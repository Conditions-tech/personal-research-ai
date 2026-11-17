"""Bounded, serial literature retrieval; no Streamlit, SQLite, or credential access."""

import json
import math
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any

import requests

from .providers import SourceAdapter
from .metadata import PUBLICATION_TYPE_LABELS


@dataclass(frozen=True)
class RetrievalBudget:
    """Hard request/record caps; the time budget is checked between requests.

    Each request keeps the same page size, including Crossref cursor requests.
    Stop before requesting a page that could exceed the raw record cap.
    The transport uses 45-second connect/read inactivity timeouts, not a total
    wall-clock cancellation deadline for an in-flight request.
    """

    max_records: int = 10
    page_size: int = 50
    max_pages: int = 5
    max_seconds: float = 120

    def __post_init__(self):
        for name, maximum in (("max_records", 250), ("page_size", 50), ("max_pages", 5)):
            value = getattr(self, name)
            if type(value) is not int or not 1 <= value <= maximum:
                raise ValueError(f"{name} must be an integer from 1 to {maximum}.")
        if (isinstance(self.max_seconds, bool)
                or not isinstance(self.max_seconds, (int, float))
                or not 0 < self.max_seconds <= 120):
            raise ValueError("max_seconds must be greater than zero and at most 120.")

    @property
    def request_size(self):
        return min(self.page_size, self.max_records)


def search_settings(budget, year_from=None, year_to=None, work_types=None):
    for year in (year_from, year_to):
        if year is not None and (type(year) is not int or not 1 <= year <= 9999):
            raise ValueError("Year bounds must be CE integers from 1 to 9999 or unset.")
    if year_from is not None and year_to is not None and year_from > year_to:
        raise ValueError("The starting year cannot be later than the ending year.")
    if isinstance(work_types, (str, bytes)):
        raise ValueError("Publication types must be a collection of supported categories.")
    try:
        selected = list(work_types) if work_types is not None else []
    except TypeError as exc:
        raise ValueError("Publication types must be a collection of supported categories.") from exc
    if any(not isinstance(category, str) or category not in PUBLICATION_TYPE_LABELS for category in selected):
        raise ValueError("Unsupported publication category.")
    return {
        "year_from": year_from, "year_to": year_to,
        "publication_types": sorted(set(selected)),
        "raw_record_budget": budget.max_records, "page_size": budget.request_size,
        "max_pages": budget.max_pages, "max_seconds": budget.max_seconds,
    }


STOP_LABELS = {
    "source_exhausted": "The source returned its final page for this query.",
    "record_budget": "Stopped at the raw record budget; more matches may exist.",
    "page_budget": "Stopped at the page budget; more matches may exist.",
    "time_budget": "Stopped at the time budget; more matches may exist.",
    "provider_error": "The source request failed; any earlier pages were kept.",
    "invalid_response": "The source returned an invalid response; earlier pages were kept.",
    "cursor_missing": "The source did not provide a cursor for the next full page.",
    "cursor_repeated": "The source repeated a cursor; stopped to avoid repeating pages.",
    "inconsistent_response": "The source's final page and reported totals disagree.",
    "rate_limited": "The source is rate limited; wait before searching it again. Earlier pages were kept.",
}


@dataclass
class RetrievalResult:
    provider: str
    reported_total: int | None = None
    total_scope: str = "unknown"
    fetched_count: int = 0
    pages_completed: int = 0
    requests_attempted: int = 0
    records: list[dict[str, Any]] = field(default_factory=list)
    status: str = "partial"
    stop_reason: str = "record_budget"
    error: str = ""
    total_changed: bool = False
    retry_after_seconds: int | None = None
    started_utc: str = ""
    finished_utc: str = ""
    provenance: list[dict[str, Any]] = field(default_factory=list)
    query: str = ""
    settings_snapshot: dict[str, Any] | None = field(default=None, repr=False)

    @property
    def filtered_count(self):
        return len(self.records)

    @property
    def unique_count(self):
        return len({record["record_key"] for record in self.records})

    @property
    def explanation(self):
        return STOP_LABELS[self.stop_reason]

    def history_note(self, budget, year_from, year_to, work_types):
        """Use the existing note column; never include payloads, URLs, or cursors."""
        settings = search_settings(budget, year_from, year_to, work_types)
        if self.settings_snapshot is not None and self.settings_snapshot != settings:
            raise ValueError("History settings do not match the actual retrieval.")
        return json.dumps({
            "version": 1,
            "settings": settings,
            "retrieval": {
                "total_scope": self.total_scope, "total_changed": self.total_changed,
                "raw_fetched": self.fetched_count, "filtered": self.filtered_count,
                "unique_in_source_run": self.unique_count,
                "pages_completed": self.pages_completed,
                "requests_attempted": self.requests_attempted,
                "stop_reason": self.stop_reason, "error": self.error,
                "retry_after_seconds": self.retry_after_seconds,
            },
        }, ensure_ascii=False)


def retry_after_seconds(response, now=None):
    """Interpret only a numeric/date Retry-After; never expose a raw header."""
    value = str(getattr(response, "headers", {}).get("Retry-After", "")).strip()
    try:
        seconds = int(value) if value.isascii() and value.isdigit() else None
        if seconds is None:
            date = parsedate_to_datetime(value)
            if date.tzinfo is None:
                date = date.replace(tzinfo=timezone.utc)
            seconds = math.ceil((date - (now or datetime.now(timezone.utc))).total_seconds())
        return min(31536000, max(1, seconds))
    except (ValueError, TypeError, OverflowError):
        return 60


def _safe_error(exc):
    # Exception messages can embed a private query or a future credential in a URL.
    if isinstance(exc, requests.exceptions.JSONDecodeError):
        return "Invalid provider response"
    if isinstance(exc, requests.HTTPError):
        code = getattr(exc.response, "status_code", None)
        return f"HTTP {code}" if isinstance(code, int) else "HTTP request failed"
    if isinstance(exc, requests.Timeout):
        return "Request timed out"
    if isinstance(exc, requests.RequestException):
        return "Network request failed"
    return "Invalid provider response"


def retrieve(
    adapter: SourceAdapter, query: str, budget: RetrievalBudget,
    year_from=None, year_to=None, work_types=None,
    *, sleep_fn=time.sleep, clock_fn=time.monotonic,
) -> RetrievalResult:
    """Keep successful pages on failure, and never equate a budget stop with coverage.

    No automatic retries: 401/403/429 and other failures stop this provider.
    A one-second gap follows each successful page before another request starts.
    Totals are the first response's value, with later changes disclosed.
    """
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Enter a research topic first.")
    settings = search_settings(budget, year_from, year_to, work_types)
    work_types = tuple(settings["publication_types"]) or None
    if adapter.pagination not in ("page", "cursor"):
        raise ValueError("Unsupported provider pagination.")
    result = RetrievalResult(provider=adapter.name, query=query.strip(), settings_snapshot=settings)
    result.started_utc = datetime.now(timezone.utc).isoformat()
    started = clock_fn()
    cursor = "*"
    used_cursors = {cursor}
    size = budget.request_size

    while True:
        if result.fetched_count + size > budget.max_records:
            result.stop_reason = "record_budget"
            break
        if result.requests_attempted >= budget.max_pages:
            result.stop_reason = "page_budget"
            break
        if clock_fn() - started >= budget.max_seconds:
            result.stop_reason = "time_budget"
            break
        if result.pages_completed:
            sleep_fn(min(1.0, max(0, budget.max_seconds - (clock_fn() - started))))
            if clock_fn() - started >= budget.max_seconds:
                result.stop_reason = "time_budget"
                break

        result.requests_attempted += 1
        try:
            batch = adapter.search_page(
                query.strip(), size, year_from, year_to, work_types,
                page=result.requests_attempted, cursor=cursor,
            )
            if batch.fetched_count > size:
                raise ValueError("Provider exceeded the requested page size.")
        except (requests.RequestException, ValueError, KeyError, TypeError, AttributeError) as exc:
            result.stop_reason = (
                "provider_error" if isinstance(exc, requests.RequestException)
                and not isinstance(exc, requests.exceptions.JSONDecodeError)
                else "invalid_response"
            )
            result.error = _safe_error(exc)
            if isinstance(exc, requests.HTTPError) and getattr(exc.response, "status_code", None) == 429:
                result.stop_reason = "rate_limited"
                result.retry_after_seconds = retry_after_seconds(exc.response)
            result.status = "partial" if result.pages_completed else "error"
            break

        if result.pages_completed == 0:
            result.reported_total = batch.reported_total
            result.total_scope = batch.total_scope
        elif batch.reported_total != result.reported_total:
            result.total_changed = True
        result.pages_completed += 1
        result.fetched_count += batch.fetched_count
        result.records.extend(batch.records)
        result.provenance.extend({
            "record_key": record["record_key"], "provider": adapter.name,
            "source_id": record.get("source_id", ""),
            "source_url": record.get("source_url", ""),
            "raw_type": record.get("work_type", ""),
            "publication_type": record.get("publication_type", ""),
            "year": record.get("year"), "venue": record.get("venue", ""),
            "source_type": record.get("source_type", ""),
            "page": result.pages_completed,
        } for record in batch.records)

        if batch.fetched_count < size:
            if result.total_changed or (
                result.reported_total is not None
                and result.fetched_count != result.reported_total
            ):
                result.stop_reason = "inconsistent_response"
            else:
                result.status = "complete"
                result.stop_reason = "source_exhausted"
            break
        if adapter.pagination == "cursor":
            if not batch.next_cursor:
                result.stop_reason = "cursor_missing"
                break
            if batch.next_cursor in used_cursors:
                result.stop_reason = "cursor_repeated"
                break
            cursor = batch.next_cursor
            used_cursors.add(cursor)

    result.finished_utc = datetime.now(timezone.utc).isoformat()
    return result
