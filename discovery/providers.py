"""Provider batches and page requests without UI or storage side effects."""

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any, Literal, Protocol

import requests

from .metadata import (
    CROSSREF_QUERY_TYPES,
    OPENALEX_QUERY_TYPES,
    filter_search_results,
    normalize_crossref,
    normalize_openalex,
)


OPENALEX_URL = "https://api.openalex.org/works"
CROSSREF_URL = "https://api.crossref.org/works"
HEADERS = {
    "User-Agent": "PersonalResearchAI/0.1 (personal research metadata client)"
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


JsonRequester = Callable[[str, dict[str, Any]], dict[str, Any]]


@dataclass
class SearchBatch:
    """One response, locally filtered but not deduplicated or persisted.

    fetched_count includes raw entries with no usable key and entries excluded
    by local filters. reported_total is the provider's estimate in its own
    scope, never a count of globally unique or exhaustively retrieved papers.
    """

    provider: str
    reported_total: int | None
    total_scope: Literal["server-filtered-candidates", "query-matches"]
    fetched_count: int
    records: list[dict[str, Any]]
    next_cursor: str | None = None

    @property
    def filtered_count(self) -> int:
        return len(self.records)


class SourceAdapter(Protocol):
    """Common batch/page contract; errors propagate to the retrieval controller."""

    name: str
    pagination: Literal["page", "cursor"]

    def search(
        self,
        query: str,
        limit: int,
        year_from: int | None = None,
        year_to: int | None = None,
        work_types: Sequence[str] | None = None,
    ) -> SearchBatch: ...

    def search_page(
        self, query: str, limit: int, year_from: int | None = None,
        year_to: int | None = None, work_types: Sequence[str] | None = None,
        *, page: int = 1, cursor: str = "*",
    ) -> SearchBatch: ...


def validate_page(payload, container_name, items_name, total_name):
    """Reject malformed paginated responses instead of reporting an empty success."""
    if not isinstance(payload, dict):
        raise ValueError("Invalid provider response.")
    container = payload.get(container_name)
    if not isinstance(container, dict):
        raise ValueError("Invalid provider response.")
    items = payload.get(items_name) if container_name == "meta" else container.get(items_name)
    if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
        raise ValueError("Invalid provider response.")
    total = container.get(total_name)
    if total is not None and (type(total) is not int or total < 0):
        raise ValueError("Invalid provider total.")
    cursor = container.get("next-cursor")
    if cursor is not None and not isinstance(cursor, str):
        raise ValueError("Invalid provider cursor.")


class OpenAlexAdapter:
    """OpenAlex metadata search using the existing request and filter semantics."""

    name = "OpenAlex"
    pagination = "page"

    def __init__(self, request_json_fn: JsonRequester | None = None):
        self._request_json = request_json if request_json_fn is None else request_json_fn

    def search(
        self, query, limit, year_from=None, year_to=None, work_types=None,
    ) -> SearchBatch:
        return self._search(query, limit, year_from, year_to, work_types)

    def search_page(
        self, query, limit, year_from=None, year_to=None, work_types=None,
        *, page=1, cursor="*",
    ) -> SearchBatch:
        # Basic paging stays well below 10,000 results and needs no cursor key.
        return self._search(query, limit, year_from, year_to, work_types, page=page)

    def _search(
        self,
        query: str,
        limit: int,
        year_from: int | None = None,
        year_to: int | None = None,
        work_types: Sequence[str] | None = None,
        *, page: int | None = None,
    ) -> SearchBatch:
        filters = []

        if year_from is not None:
            filters.append(f"from_publication_date:{year_from:04d}-01-01")

        if year_to is not None:
            filters.append(f"to_publication_date:{year_to:04d}-12-31")

        if work_types:
            native_types = sorted({
                native_type for category in work_types
                for native_type in OPENALEX_QUERY_TYPES[category]
            })
            filters.append("type:" + "|".join(native_types))

        params = {
            "search": query,
            "per_page": limit,
            "select": (
                "id,doi,title,publication_year,type,authorships,"
                "primary_location,abstract_inverted_index"
            ),
        }

        if filters:
            params["filter"] = ",".join(filters)
        if page is not None:
            params["page"] = page

        payload = self._request_json(OPENALEX_URL, params)
        if page is not None:
            validate_page(payload, "meta", "results", "count")

        meta = payload.get("meta") or {}
        items = payload.get("results", [])
        papers = [
            normalize_openalex(item)
            for item in items
        ]
        papers = [p for p in papers if p["record_key"] and p["title"]]
        papers = filter_search_results(papers, year_from, year_to, work_types)

        return SearchBatch(
            self.name, meta.get("count"), "server-filtered-candidates", len(items), papers,
        )


class CrossrefAdapter:
    """Crossref metadata search using the existing request and filter semantics."""

    name = "Crossref"
    pagination = "cursor"

    def __init__(self, request_json_fn: JsonRequester | None = None):
        self._request_json = request_json if request_json_fn is None else request_json_fn

    def search(
        self, query, limit, year_from=None, year_to=None, work_types=None,
    ) -> SearchBatch:
        return self._search(query, limit, year_from, year_to, work_types)

    def search_page(
        self, query, limit, year_from=None, year_to=None, work_types=None,
        *, page=1, cursor="*",
    ) -> SearchBatch:
        return self._search(query, limit, year_from, year_to, work_types, cursor=cursor)

    def _search(
        self,
        query: str,
        limit: int,
        year_from: int | None = None,
        year_to: int | None = None,
        work_types: Sequence[str] | None = None,
        *, cursor: str | None = None,
    ) -> SearchBatch:
        filters = crossref_filters(year_from, year_to, work_types)
        params = {"query.bibliographic": query, "rows": limit}
        if filters:
            params["filter"] = filters
        if cursor is not None:
            params["cursor"] = cursor
        payload = self._request_json(
            CROSSREF_URL,
            params,
        )
        if cursor is not None:
            validate_page(payload, "message", "items", "total-results")

        message = payload.get("message") or {}
        items = message.get("items", [])
        papers = [
            normalize_crossref(item)
            for item in items
        ]
        papers = [p for p in papers if p["record_key"] and p["title"]]
        papers = filter_search_results(papers, year_from, year_to, work_types)

        return SearchBatch(
            self.name, message.get("total-results"),
            "server-filtered-candidates" if filters else "query-matches", len(items), papers,
            message.get("next-cursor"),
        )


def crossref_filters(year_from=None, year_to=None, work_types=None):
    """Narrow Crossref's results server-side; local filters still decide retention.

    Crossref's pub-date is the earliest print/online date, while local years
    prefer the print date, which can be later. The upper bound is therefore a
    superset of the local filter. The lower bound is widened by one year so
    records published online up to a year before their print year still
    arrive; a longer print lag can be excluded by the server.
    """
    filters = []
    if year_from is not None:
        filters.append(f"from-pub-date:{max(1, year_from - 1):04d}-01-01")
    if year_to is not None:
        filters.append(f"until-pub-date:{year_to:04d}-12-31")
    if work_types:
        filters.extend(f"type:{native_type}" for native_type in sorted({
            native_type for category in work_types
            for native_type in CROSSREF_QUERY_TYPES[category]
        }))
    return ",".join(filters)


def search_openalex(query, limit, year_from=None, year_to=None, work_types=None):
    """Keep the Streamlit caller's existing (reported total, records) interface."""
    batch = OpenAlexAdapter().search(query, limit, year_from, year_to, work_types)
    return batch.reported_total, batch.records


def search_crossref(query, limit, year_from=None, year_to=None, work_types=None):
    """Keep the Streamlit caller's existing (reported total, records) interface."""
    batch = CrossrefAdapter().search(query, limit, year_from, year_to, work_types)
    return batch.reported_total, batch.records
