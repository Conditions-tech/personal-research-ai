
import json
import re
import sqlite3
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests
import streamlit as st


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
EXPORT_DIR = ROOT / "exports"
DB_PATH = DATA_DIR / "research.db"

DATA_DIR.mkdir(exist_ok=True)
EXPORT_DIR.mkdir(exist_ok=True)

OPENALEX_URL = "https://api.openalex.org/works"
CROSSREF_URL = "https://api.crossref.org/works"

HEADERS = {
    "User-Agent": "PersonalResearchAI/0.1 (personal research metadata client)"
}


def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS papers (
            record_key TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            doi TEXT,
            year INTEGER,
            work_type TEXT,
            abstract TEXT,
            authors TEXT,
            source TEXT NOT NULL,
            url TEXT,
            first_saved_utc TEXT NOT NULL,
            last_seen_utc TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS searches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            searched_utc TEXT NOT NULL,
            source TEXT NOT NULL,
            reported_count INTEGER,
            retrieved_count INTEGER,
            status TEXT NOT NULL,
            note TEXT
        )
    """)
    conn.commit()
    return conn


def now_utc():
    return datetime.now(timezone.utc).isoformat()


def clean_text(value):
    if not value:
        return ""
    if isinstance(value, list):
        value = " ".join(str(x) for x in value if x)
    return re.sub(r"\s+", " ", str(value)).strip()


def normalize_doi(doi):
    doi = clean_text(doi).lower()
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi)
    doi = re.sub(r"^doi:\s*", "", doi)
    return doi.strip()


def normalize_title(title):
    title = unicodedata.normalize("NFKC", clean_text(title)).lower()
    return re.sub(r"[^\w]+", " ", title).strip()


def make_key(doi, title, year):
    doi = normalize_doi(doi)
    if doi:
        return "doi:" + doi

    normalized = normalize_title(title)
    if not normalized:
        return ""

    return f"title:{normalized}|year:{year or 'unknown'}"


def abstract_from_openalex(index):
    if not isinstance(index, dict):
        return ""

    positions = {}
    for word, indexes in index.items():
        for position in indexes:
            positions[position] = word

    return " ".join(
        positions[position] for position in sorted(positions)
    )


def authors_from_openalex(authorships):
    names = []
    for item in authorships or []:
        author = item.get("author") or {}
        name = author.get("display_name")
        if name:
            names.append(name)
    return "; ".join(names)


def normalize_openalex(item):
    title = clean_text(item.get("title"))
    doi = normalize_doi(item.get("doi"))
    year = item.get("publication_year")
    key = make_key(doi, title, year)

    location = item.get("primary_location") or {}
    source = location.get("source") or {}

    return {
        "record_key": key,
        "title": title,
        "doi": doi,
        "year": year,
        "work_type": item.get("type") or "",
        "abstract": abstract_from_openalex(
            item.get("abstract_inverted_index")
        ),
        "authors": authors_from_openalex(item.get("authorships")),
        "source": "OpenAlex",
        "url": (
            item.get("doi")
            or item.get("id")
            or ""
        ),
        "venue": source.get("display_name") or "",
    }


def normalize_crossref(item):
    titles = item.get("title") or []
    title = clean_text(titles[0] if titles else "")
    doi = normalize_doi(item.get("DOI"))
    date_parts = (
        (item.get("published-print") or {}).get("date-parts")
        or (item.get("published-online") or {}).get("date-parts")
        or (item.get("published") or {}).get("date-parts")
        or []
    )
    year = date_parts[0][0] if date_parts and date_parts[0] else None

    authors = []
    for author in item.get("author") or []:
        name = clean_text(
            " ".join([
                author.get("given", ""),
                author.get("family", "")
            ])
        )
        if name:
            authors.append(name)

    key = make_key(doi, title, year)
    abstract = clean_text(item.get("abstract", ""))
    abstract = re.sub(r"<[^>]+>", " ", abstract)

    return {
        "record_key": key,
        "title": title,
        "doi": doi,
        "year": year,
        "work_type": item.get("type") or "",
        "abstract": abstract,
        "authors": "; ".join(authors),
        "source": "Crossref",
        "url": (
            "https://doi.org/" + doi if doi else item.get("URL", "")
        ),
        "venue": clean_text(item.get("container-title") or []),
    }


def request_json(url, params):
    response = requests.get(
        url,
        params=params,
        headers=HEADERS,
        timeout=45,
    )
    response.raise_for_status()
    return response.json()


def search_openalex(query, limit):
    payload = request_json(
        OPENALEX_URL,
        {
            "search": query,
            "per_page": limit,
            "select": (
                "id,doi,title,publication_year,type,authorships,"
                "primary_location,abstract_inverted_index"
            ),
        },
    )

    meta = payload.get("meta") or {}
    papers = [
        normalize_openalex(item)
        for item in payload.get("results", [])
    ]
    papers = [p for p in papers if p["record_key"]]

    return meta.get("count"), papers


def search_crossref(query, limit):
    payload = request_json(
        CROSSREF_URL,
        {
            "query.bibliographic": query,
            "rows": limit,
        },
    )

    message = payload.get("message") or {}
    papers = [
        normalize_crossref(item)
        for item in message.get("items", [])
    ]
    papers = [p for p in papers if p["record_key"]]

    return message.get("total-results"), papers


def save_search(query, source, count, retrieved, status, note=""):
    with connect_db() as conn:
        conn.execute("""
            INSERT INTO searches (
                query, searched_utc, source, reported_count,
                retrieved_count, status, note
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            query,
            now_utc(),
            source,
            count,
            retrieved,
            status,
            note,
        ))


def save_papers(papers):
    saved = 0
    stamp = now_utc()

    with connect_db() as conn:
        for paper in papers:
            key = paper["record_key"]
            if not key or not paper["title"]:
                continue

            existing = conn.execute(
                "SELECT source FROM papers WHERE record_key = ?",
                (key,),
            ).fetchone()

            if existing:
                old_sources = set(existing[0].split(";"))
                old_sources.update(paper["source"].split(";"))
                sources = ";".join(sorted(old_sources))

                conn.execute("""
                    UPDATE papers SET
                        title = CASE WHEN title = '' THEN ? ELSE title END,
                        doi = CASE WHEN doi = '' OR doi IS NULL THEN ? ELSE doi END,
                        year = COALESCE(year, ?),
                        work_type = CASE WHEN work_type = '' THEN ? ELSE work_type END,
                        abstract = CASE WHEN abstract = '' THEN ? ELSE abstract END,
                        authors = CASE WHEN authors = '' THEN ? ELSE authors END,
                        source = ?,
                        url = CASE WHEN url = '' THEN ? ELSE url END,
                        last_seen_utc = ?
                    WHERE record_key = ?
                """, (
                    paper["title"], paper["doi"], paper["year"],
                    paper["work_type"], paper["abstract"],
                    paper["authors"], sources, paper["url"],
                    stamp, key,
                ))
            else:
                conn.execute("""
                    INSERT INTO papers (
                        record_key, title, doi, year, work_type,
                        abstract, authors, source, url,
                        first_saved_utc, last_seen_utc
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    key, paper["title"], paper["doi"], paper["year"],
                    paper["work_type"], paper["abstract"],
                    paper["authors"], paper["source"], paper["url"],
                    stamp, stamp,
                ))
                saved += 1

        conn.commit()

    return saved


def load_papers():
    with connect_db() as conn:
        return pd.read_sql_query("""
            SELECT title, authors, year, work_type, doi, source,
                   abstract, url, first_saved_utc
            FROM papers
            ORDER BY year DESC, title COLLATE NOCASE
        """, conn)


def load_searches():
    with connect_db() as conn:
        return pd.read_sql_query("""
            SELECT searched_utc, query, source, reported_count,
                   retrieved_count, status, note
            FROM searches
            ORDER BY id DESC
            LIMIT 100
        """, conn)


st.set_page_config(
    page_title="Personal Research AI",
    page_icon="🔬",
    layout="wide",
)

st.title("🔬 Personal Research AI")
st.caption(
    "Milestone 1 · Literature Discovery · Scholarly metadata only"
)

with st.sidebar:
    st.header("Search settings")
    query = st.text_input(
        "Research topic",
        placeholder="e.g. machine learning for power system fault detection",
    )
    limit = st.select_slider(
        "Maximum records per database",
        options=[5, 10, 25, 50],
        value=10,
    )

    st.info(
        "Searches are sent to public academic metadata services. "
        "Do not enter confidential research or personal data."
    )

    run_search = st.button(
        "Search literature",
        type="primary",
        use_container_width=True,
    )

    st.caption("Local database: data/research.db")

if run_search:
    if not query.strip():
        st.warning("Enter a research topic first.")
    else:
        combined = []

        for name, search_fn in [
            ("OpenAlex", search_openalex),
            ("Crossref", search_crossref),
        ]:
            with st.spinner(f"Searching {name}..."):
                try:
                    count, records = search_fn(query.strip(), limit)
                    combined.extend(records)
                    save_search(
                        query.strip(), name, count, len(records),
                        "success",
                        "Reported count is database-specific; "
                        "retrieved records are bounded by the selected limit."
                    )
                    st.success(
                        f"{name}: database reports "
                        f"{count:,} matches; retrieved {len(records)}."
                        if isinstance(count, int)
                        else f"{name}: retrieved {len(records)} records."
                    )
                except (requests.RequestException, ValueError, KeyError) as exc:
                    save_search(
                        query.strip(), name, None, 0, "error", str(exc)
                    )
                    st.error(f"{name} search failed: {exc}")

            # Avoid hammering public services.
            time.sleep(0.5)

        if combined:
            added = save_papers(combined)
            st.success(
                f"Saved results. {added} new unique records added; "
                "existing records were updated or deduplicated."
            )
            st.session_state["last_query"] = query.strip()

st.divider()

papers = load_papers()
searches = load_searches()

m1, m2, m3 = st.columns(3)
m1.metric("Unique saved records", len(papers))
m2.metric(
    "Records with abstracts",
    int(papers["abstract"].fillna("").str.len().gt(0).sum())
    if not papers.empty else 0,
)
m3.metric(
    "Searches recorded",
    len(searches),
)

tab1, tab2, tab3 = st.tabs([
    "Saved literature",
    "Search history",
    "Coverage & limitations",
])

with tab1:
    if papers.empty:
        st.info("No records saved yet. Run your first search in the sidebar.")
    else:
        filter_text = st.text_input(
            "Filter saved titles and abstracts",
            key="local_filter",
        )
        view = papers.copy()

        if filter_text.strip():
            mask = (
                view["title"].fillna("").str.contains(
                    filter_text, case=False, regex=False
                )
                | view["abstract"].fillna("").str.contains(
                    filter_text, case=False, regex=False
                )
            )
            view = view[mask]

        st.dataframe(
            view[[
                "title", "year", "work_type", "authors",
                "doi", "source", "url"
            ]],
            use_container_width=True,
            hide_index=True,
        )

        csv_bytes = view.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "Download filtered CSV",
            data=csv_bytes,
            file_name="personal_research_literature.csv",
            mime="text/csv",
        )

        with st.expander("Read abstract and metadata"):
            titles = view["title"].fillna("").tolist()
            if titles:
                selected = st.selectbox("Choose a paper", titles)
                row = view[view["title"] == selected].iloc[0]
                st.write("**Authors:**", row["authors"] or "Not available")
                st.write("**Year:**", row["year"])
                st.write("**Type:**", row["work_type"] or "Not classified")
                st.write("**DOI:**", row["doi"] or "Not available")
                st.write("**Sources:**", row["source"])
                st.write("**Abstract:**", row["abstract"] or "Not available")
                if row["url"]:
                    st.markdown(f"[Open source record]({row['url']})")

with tab2:
    if searches.empty:
        st.info("Search history will appear here.")
    else:
        st.dataframe(searches, use_container_width=True, hide_index=True)

with tab3:
    st.markdown("""
    **What the counts mean**

    - Reported matches are the counts returned by each individual database.
    - Retrieved records are limited by the per-database result setting.
    - Unique saved records are locally deduplicated by normalized DOI, or
      by normalized title and year when a DOI is unavailable.
    - The two database counts must not be added to estimate a global total.

    **Coverage limitations**

    - OpenAlex and Crossref do not index every publication ever produced.
    - Historical coverage, language coverage and conference metadata vary.
    - A missing abstract does not mean a paper does not exist.
    - Work-type labels come from source metadata and may be incomplete.
    - A title/year match is a practical duplicate heuristic, not proof
      that two records describe the same publication.
    - This milestone does not yet perform citation chaining, systematic
      query expansion, full-text retrieval or exhaustive pagination.
    - Search results can change over time. The history records the query,
      timestamp and counts to help with reproducibility.
    - Metadata access does not automatically grant rights to reuse
      abstracts or full-text papers. Respect the relevant terms and licenses.
    """)
