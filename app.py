import math
import sqlite3
import time
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import streamlit as st

from discovery.metadata import PUBLICATION_TYPE_LABELS
from discovery.providers import CrossrefAdapter, OpenAlexAdapter
from discovery.retrieval import RetrievalBudget, RetrievalResult, retrieve
from discovery.runs import history_note_for_run, make_run, run_bundle
from review.ui import render_review


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
EXPORT_DIR = ROOT / "exports"
DB_PATH = DATA_DIR / "research.db"

DATA_DIR.mkdir(exist_ok=True)
EXPORT_DIR.mkdir(exist_ok=True)


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


def save_search(query, source, count, retrieved, status, note=""):
    with closing(connect_db()) as conn, conn:
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

    with closing(connect_db()) as conn, conn:
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
                        work_type = CASE WHEN work_type = '' OR work_type IS NULL THEN ? ELSE work_type END,
                        abstract = CASE WHEN abstract = '' OR abstract IS NULL THEN ? ELSE abstract END,
                        authors = CASE WHEN authors = '' OR authors IS NULL THEN ? ELSE authors END,
                        source = ?,
                        url = CASE WHEN url = '' OR url IS NULL THEN ? ELSE url END,
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
    with closing(connect_db()) as conn, conn:
        return pd.read_sql_query("""
            SELECT record_key, title, authors, year, work_type, doi, source,
                   abstract, url, first_saved_utc
            FROM papers
            ORDER BY year DESC, title COLLATE NOCASE
        """, conn)


def load_searches():
    with closing(connect_db()) as conn, conn:
        return pd.read_sql_query("""
            SELECT searched_utc, query, source, reported_count,
                   retrieved_count, status, note
            FROM searches
            ORDER BY id DESC
            LIMIT 100
        """, conn)


def filter_papers(papers, filter_text):
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

    return view


def papers_to_csv(papers):
    return papers.to_csv(index=False).encode("utf-8-sig")


st.set_page_config(
    page_title="Personal Research AI",
    page_icon="🔬",
    layout="wide",
)

st.title("🔬 Personal Research AI")
st.caption(
    "Literature discovery · Review workspace · Metadata and abstract evidence"
)

with st.sidebar:
    st.header("Search settings")
    query = st.text_input(
        "Research topic",
        placeholder="e.g. machine learning for power system fault detection",
    )
    limit = st.select_slider(
        "Maximum fetched records per database",
        options=[5, 10, 25, 50, 100, 250],
        value=10,
        help="Raw metadata entries before filtering and deduplication; up to five pages of 50.",
    )
    st.caption("Filtering can leave fewer papers. Retrieval is bounded and may be partial.")

use_year_from = st.checkbox("Apply start year", value=True, key="apply_start_year")
year_from = st.number_input(
    "From publication year",
    min_value=1,
    max_value=9999,
    value=2015,
    step=1,
    disabled=not use_year_from,
)

use_year_to = st.checkbox("Apply end year", value=True, key="apply_end_year")
year_to = st.number_input(
    "To publication year",
    min_value=1,
    max_value=9999,
    value=datetime.now().year,
    step=1,
    disabled=not use_year_to,
)
if not use_year_from:
    year_from = None
if not use_year_to:
    year_to = None
st.caption(
    "Clear either year checkbox to remove that bound. With both bounds off, "
    "unknown years are included; provider historical coverage is still limited."
)

publication_types = st.multiselect(
    "Publication types",
    options=list(PUBLICATION_TYPE_LABELS),
    default=["journal-paper", "conference-paper"],
    format_func=PUBLICATION_TYPE_LABELS.get,
    help=(
        "Journal papers include articles and reviews together; Crossref does "
        "not distinguish them or reliably separate other journal content. "
        "OpenAlex uses explicit work and venue metadata. "
        "Clear the selection to include unclassified records."
    ),
)

st.info(
        "Searches are sent to public academic metadata services. "
        "Do not enter confidential research or personal data."
    )

run_search = st.button(
        "Search literature",
        type="primary",
        width="stretch",
    )

st.caption("Local database: data/research.db")


if run_search:
    if not query.strip():
        st.warning("Enter a research topic first.")
    elif year_from is not None and year_to is not None and year_from > year_to:
        st.warning("The starting year cannot be later than the ending year.")
    else:
        combined = []
        results = []
        budget = RetrievalBudget(max_records=limit)
        cooldowns = st.session_state.setdefault("provider_retry_at", {})

        for adapter in (OpenAlexAdapter(), CrossrefAdapter()):
            name = adapter.name
            with st.spinner(f"Searching {name}..."):
                remaining = math.ceil(cooldowns.get(name, 0) - time.time())
                if remaining > 0:
                    result = RetrievalResult(
                        provider=name, status="error", stop_reason="rate_limited",
                        error="Waiting before retrying this provider",
                        retry_after_seconds=remaining,
                        started_utc=now_utc(), finished_utc=now_utc(),
                    )
                else:
                    result = retrieve(
                        adapter, query.strip(), budget,
                        year_from=year_from, year_to=year_to,
                        work_types=publication_types or None,
                    )
                    if result.retry_after_seconds is not None:
                        cooldowns[name] = time.time() + result.retry_after_seconds
                results.append(result)
                combined.extend(result.records)
                count_label = (
                    "candidate matches before local filters"
                    if result.total_scope == "server-filtered-candidates"
                    else "query matches before local filters"
                )
                total_label = (
                    f"database reports {result.reported_total:,} {count_label}"
                    if result.reported_total is not None else "database total unavailable"
                )
                message = (
                    f"{name}: {total_label}; fetched {result.fetched_count} raw entries "
                    f"in {result.pages_completed} pages; retrieved {result.filtered_count} "
                    f"after selected filters. Status: {result.status}. {result.explanation}"
                )
                if result.error:
                    message += f" {result.error}."
                if result.retry_after_seconds is not None:
                    message += f" Retry in at least {result.retry_after_seconds} seconds."
                if result.total_changed:
                    message += " The reported total changed during retrieval."
                if result.status == "error":
                    st.error(message)
                elif result.status == "partial":
                    st.warning(message)
                else:
                    st.success(message)

            # Avoid making requests too quickly.
            time.sleep(0.5)

        added = 0
        if combined:
            unique_this_run = len({paper["record_key"] for paper in combined})
            added = save_papers(combined)
            st.success(
                f"This search retrieved {unique_this_run} unique records across sources. "
                f"Saved results. {added} new unique records added; "
                "existing records were updated or deduplicated."
            )
            st.session_state["last_query"] = query.strip()
        else:
            st.warning(
                "No records were retrieved. Check the messages above "
                "for search errors or try another query."
            )
        run = make_run(
            query.strip(), budget, results, year_from, year_to, publication_types,
            new_records=added,
        )
        for result in results:
            save_search(
                query.strip(), result.provider, result.reported_total,
                result.filtered_count, result.status, history_note_for_run(result, run),
            )
        st.session_state["last_run"] = run
        st.caption(
            f"Run {run['manifest']['run_id']}: {run['manifest']['counts']['raw_fetched']} raw; "
            f"{run['manifest']['counts']['filtered']} filtered; "
            f"{run['manifest']['counts']['unique_in_run']} unique. "
            f"Overall status: {run['manifest']['status']}."
        )


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

tab1, tab2, tab3, tab4 = st.tabs([
    "Saved literature",
    "Search history",
    "Coverage & limitations",
    "Literature review",
])

with tab1:
    if papers.empty:
        st.info("No records saved yet. Run your first search in the sidebar.")
    else:
        filter_text = st.text_input(
            "Filter saved titles and abstracts",
            key="local_filter",
        )
        view = filter_papers(papers, filter_text)

        st.dataframe(
            view[[
                "title", "year", "work_type", "authors",
                "doi", "source", "url"
            ]],
            width="stretch",
            hide_index=True,
        )

        csv_bytes = papers_to_csv(view)
        st.download_button(
            "Download filtered CSV",
            data=csv_bytes,
            file_name="personal_research_literature.csv",
            mime="text/csv",
        )

        with st.expander("Read abstract and metadata"):
            if not view.empty:
                choices = view.set_index("record_key", drop=False)
                title_counts = view["title"].fillna("").value_counts()

                def paper_label(record_key):
                    paper = choices.loc[record_key]
                    title = paper["title"] or "Untitled"
                    if title_counts.get(title, 0) > 1:
                        return f"{title} — {paper['doi'] or record_key}"
                    return title

                selected = st.selectbox(
                    "Choose a paper", choices.index.tolist(), format_func=paper_label,
                    key="selected_paper_key",
                )
                row = choices.loc[selected]
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
        st.dataframe(searches, width="stretch", hide_index=True)
        st.download_button(
            "Download displayed search history JSON",
            data=searches.to_json(orient="records", indent=2, force_ascii=False).encode("utf-8"),
            file_name="personal_research_search_history.json", mime="application/json",
        )
    if "last_run" in st.session_state:
        st.download_button(
            "Download latest run bundle",
            data=run_bundle(st.session_state["last_run"]),
            file_name=f"research_run_{st.session_state['last_run']['manifest']['run_id']}.zip",
            mime="application/zip",
        )
        st.caption(
            "The bundle contains this session's latest run manifest, deduplicated records, "
            "and per-source/page provenance. History notes retain run settings and evidence "
            "after restart; older runs do not have retroactive provenance."
        )

with tab4:
    render_review(st.session_state.get("last_run"))

with tab3:
    st.markdown("""
    **What the counts mean**

    - Reported matches are the counts returned by each individual database.
    - Fetched entries are raw metadata before filtering or deduplication.
      The per-database budget allows up to 250 entries, five pages and 120 seconds
      between requests. The transport uses 45-second inactivity timeouts, not
      a hard total deadline for an in-flight request.
    - Partial means retrieval stopped at a budget or another interruption.
      Complete means the source returned a final page for this query, not that
      all relevant research worldwide was found. Errors keep earlier pages.
    - Crossref applies the selected types and years on its server, with the
      start year widened by one because Crossref dates by first online or print
      publication. Its reported matches are candidates before the exact local
      year/type filters, which may leave fewer records than were fetched.
      Records printed more than a year after online publication can be missed.
    - OpenAlex's reported matches are candidates after its server filters,
      before local venue classification. They are not an exact total for the
      selected journal/conference categories.
    - Retrieved counts are after local filtering and before deduplication;
      unique saved records describe the accumulated library, not this query.
    - Unique saved records are locally deduplicated by normalized DOI, or
      by normalized title and year when a DOI is unavailable.
    - The two database counts must not be added to estimate a global total.

    **Coverage limitations**

    - OpenAlex and Crossref do not index every publication ever produced.
    - Historical coverage, language coverage and conference metadata vary.
    - A missing abstract does not mean a paper does not exist.
    - Work-type labels come from source metadata and may be incomplete.
      Journal papers combine articles and reviews. Crossref peer review reports
      are not literature reviews; journal-article metadata can also include
      other journal content without a distinct subtype. OpenAlex article/review records need explicit
      journal or conference venue metadata; otherwise they stay unclassified.
      Clear the type selection to include unclassified records. Native OpenAlex
      conference-paper typing is still rolling out, so classifications and
      venue coverage can be incomplete.
    - A title/year match is a practical duplicate heuristic, not proof
      that two records describe the same publication.
    - Basic OpenAlex pages and Crossref cursors support bounded retrieval.
      Provider indexes can change between pages, causing omissions or duplicates.
      This does not perform exhaustive retrieval, citation chaining, systematic
      query expansion or full-text retrieval.
    - New search history notes include filters, budgets, count scope and stop
      reasons, a shared run ID, and source IDs/URLs for retained observations.
      Older rows may lack these settings. History shows up to 100 attempts.
    - Either year bound is optional; both off includes missing-year metadata.
      Bounded controls accept CE years 1-9999; metadata dates may be uncertain
      and historical publication coverage is not guaranteed.
    - A 429 stops that provider without automatic retries and records a cooldown
      from Retry-After (60 seconds when unavailable). The session respects it on
      subsequent searches; it is not a multi-session or process-wide limiter.
    - Metadata access does not automatically grant rights to reuse
      abstracts or full-text papers. Respect the relevant terms and licenses.
    """)
