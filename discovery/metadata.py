"""Provider metadata normalization and shared filters, without UI or storage."""

import re
import unicodedata


PUBLICATION_TYPE_LABELS = {
    "journal-paper": "Journal papers (articles and reviews)",
    "conference-paper": "Conference papers",
    "book-chapter": "Book chapters",
    "dissertation": "Dissertations",
    "posted-content": "Preprints / posted content",
}
CROSSREF_TYPE_MAP = {
    "journal-article": "journal-paper",
    "proceedings-article": "conference-paper",
    "book-chapter": "book-chapter",
    "dissertation": "dissertation",
    "posted-content": "posted-content",
}
CROSSREF_QUERY_TYPES = {
    category: tuple(sorted(raw for raw, mapped in CROSSREF_TYPE_MAP.items() if mapped == category))
    for category in PUBLICATION_TYPE_LABELS
}
OPENALEX_TYPE_MAP = {
    "conference-paper": "conference-paper",
    "book-chapter": "book-chapter",
    "dissertation": "dissertation",
    "preprint": "posted-content",
}
OPENALEX_QUERY_TYPES = {
    "journal-paper": ("article", "review"),
    "conference-paper": ("article", "review", "conference-paper"),
    "book-chapter": ("book-chapter",),
    "dissertation": ("dissertation",),
    "posted-content": ("preprint",),
}


def clean_text(value):
    if not value:
        return ""
    if isinstance(value, list):
        value = " ".join(str(x) for x in value if x)
    return re.sub(r"\s+", " ", str(value)).strip()


def optional_text(value):
    """Missing provider text is empty; structured values are not invented text."""
    if value is not None and not isinstance(value, str):
        raise ValueError("Invalid provider text field.")
    return clean_text(value)


def text_or_list(value):
    if isinstance(value, list):
        if any(not isinstance(item, str) for item in value):
            raise ValueError("Invalid provider text list.")
        return clean_text(value)
    return optional_text(value)


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

    return f"title:{normalized}|year:{year if year is not None else 'unknown'}"


def abstract_from_openalex(index):
    if not isinstance(index, dict):
        return ""

    positions = {}
    for word, indexes in index.items():
        if not isinstance(word, str) or not isinstance(indexes, list):
            raise ValueError("Invalid abstract index.")
        for position in indexes:
            if type(position) is not int or position < 0 or position in positions:
                raise ValueError("Invalid abstract position.")
            positions[position] = word

    return " ".join(
        positions[position] for position in sorted(positions)
    )


def authors_from_openalex(authorships):
    names = []
    for item in authorships or []:
        author = item.get("author") or {}
        name = optional_text(author.get("display_name"))
        if name:
            names.append(name)
    return "; ".join(names)


def validate_year(year):
    """Retain source integer years or missing values without coercing evidence.

    Do not impose the UI's CE input range on unbounded provider metadata.
    Booleans, floating point values and strings are not publication years.
    """
    if year is not None and (type(year) is not int or not -(2**63) <= year < 2**63):
        raise ValueError("Invalid publication year.")
    return year


def normalize_openalex(item):
    if item.get("title") is not None and not isinstance(item["title"], str):
        raise ValueError("Invalid OpenAlex title.")
    title = clean_text(item.get("title"))
    doi = normalize_doi(optional_text(item.get("doi")))
    year = validate_year(item.get("publication_year"))
    key = make_key(doi, title, year)

    location = item.get("primary_location") or {}
    source = location.get("source") or {}
    source_id = optional_text(item.get("id"))
    work_type = optional_text(item.get("type"))
    venue = optional_text(source.get("display_name"))
    source_type = optional_text(source.get("type"))
    abstract_index = item.get("abstract_inverted_index")
    if abstract_index is not None and not isinstance(abstract_index, dict):
        raise ValueError("Invalid abstract index.")
    url = "https://doi.org/" + doi if doi else source_id

    return {
        "record_key": key,
        "title": title,
        "doi": doi,
        "year": year,
        "work_type": work_type,
        "publication_type": openalex_publication_type(item),
        "abstract": abstract_from_openalex(abstract_index),
        "authors": authors_from_openalex(item.get("authorships")),
        "source": "OpenAlex",
        "source_id": source_id,
        "source_url": source_id or url,
        "source_type": source_type,
        "url": url,
        "venue": venue,
    }


def normalize_crossref(item):
    titles = item.get("title") or []
    if not isinstance(titles, list) or any(not isinstance(title, str) for title in titles):
        raise ValueError("Invalid Crossref title list.")
    title = clean_text(titles[0] if titles else "")
    doi = normalize_doi(optional_text(item.get("DOI")))
    date_parts = (
        (item.get("published-print") or {}).get("date-parts")
        or (item.get("published-online") or {}).get("date-parts")
        or (item.get("published") or {}).get("date-parts")
        or []
    )
    year = validate_year(date_parts[0][0] if date_parts and date_parts[0] else None)

    authors = []
    for author in item.get("author") or []:
        name = clean_text(
            " ".join([
                optional_text(author.get("given")),
                optional_text(author.get("family")),
            ])
        )
        if name:
            authors.append(name)

    key = make_key(doi, title, year)
    abstract = optional_text(item.get("abstract"))
    abstract = re.sub(r"<[^>]+>", " ", abstract)
    source_url = optional_text(item.get("URL"))
    work_type = optional_text(item.get("type"))
    venue = text_or_list(item.get("container-title"))

    return {
        "record_key": key,
        "title": title,
        "doi": doi,
        "year": year,
        "work_type": work_type,
        "publication_type": crossref_publication_type(item),
        "abstract": abstract,
        "authors": "; ".join(authors),
        "source": "Crossref",
        "source_id": doi,
        "source_url": source_url or ("https://doi.org/" + doi if doi else ""),
        "source_type": "",
        "url": (
            "https://doi.org/" + doi if doi else source_url
        ),
        "venue": venue,
    }


def openalex_publication_type(item):
    """Use native specific types or explicit venue evidence, never title guesses."""
    raw_type = clean_text(item.get("type")).lower()
    if raw_type in ("article", "review"):
        location = item.get("primary_location") or {}
        source = location.get("source") or {}
        source_type = clean_text(source.get("type")).lower()
        return {"journal": "journal-paper", "conference": "conference-paper"}.get(source_type, "")
    return OPENALEX_TYPE_MAP.get(raw_type, "")


def crossref_publication_type(item):
    """Return a supported filter type without inferring ambiguous categories."""
    raw_type = clean_text(item.get("type")).lower()
    return CROSSREF_TYPE_MAP.get(raw_type, "")


def filter_search_results(papers, year_from=None, year_to=None, work_types=None):
    """Apply inclusive bounds and optional types to either provider's records."""
    selected_types = set(work_types or [])
    filtered = []

    for paper in papers:
        year = paper.get("year")
        if year_from is not None and (year is None or year < year_from):
            continue
        if year_to is not None and (year is None or year > year_to):
            continue
        if selected_types and paper.get("publication_type") not in selected_types:
            continue
        filtered.append(paper)

    return filtered
