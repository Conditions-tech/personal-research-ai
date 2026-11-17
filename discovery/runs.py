"""Traceable run manifests and in-memory exports, without database/schema changes."""

import csv
import io
import json
import zipfile
from datetime import datetime, timezone
from uuid import uuid4

from .retrieval import search_settings


RECORD_COLUMNS = (
    "record_key", "title", "authors", "year", "work_type", "doi", "source",
    "abstract", "url", "publication_type", "venue",
)
PROVENANCE_COLUMNS = (
    "record_key", "provider", "source_id", "source_url", "raw_type",
    "publication_type", "year", "venue", "source_type", "page",
)
COVERAGE_LIMITS = [
    "Only the named provider queries within the recorded budgets were traversed.",
    "Provider totals have different scopes and are not a combined global count.",
    "Provider metadata, publication dates, languages, disciplines and classifications vary.",
    "Missing abstracts and unindexed records cannot be recovered by pagination.",
    "Completion is scoped to this traversal, not exhaustive worldwide literature coverage.",
    "DOI or title/year deduplication is a heuristic; provider indexes can change while paging.",
]


def merge_run_records(results):
    """Mirror existing first-nonempty-field merging for this run, not the library."""
    merged = {}
    for result in results:
        for record in result.records:
            key = record["record_key"]
            if key not in merged:
                merged[key] = dict(record)
            else:
                existing = merged[key]
                for field, value in record.items():
                    if existing.get(field) in (None, ""):
                        existing[field] = value
                existing["source"] = ";".join(sorted(
                    set(existing["source"].split(";")) | set(record["source"].split(";"))
                ))
    return list(merged.values())


def make_run(query, budget, results, year_from=None, year_to=None, work_types=None,
             *, new_records=None, run_id=None):
    if not isinstance(query, str) or not query.strip():
        raise ValueError("A run requires a research query.")
    query = query.strip()
    results = list(results)
    if len({result.provider for result in results}) != len(results):
        raise ValueError("A run must have one retrieval result per provider.")
    for result in results:
        if result.query and result.query != query:
            raise ValueError("Run query does not match the actual retrieval.")
        if result.settings_snapshot is None and (
            result.requests_attempted or result.pages_completed or result.records
        ):
            raise ValueError("Retrieval results are missing their search context.")
    records = merge_run_records(results)
    if new_records is not None and (type(new_records) is not int or not 0 <= new_records <= len(records)):
        raise ValueError("New insertion count must fit the run's unique record count.")
    now = datetime.now(timezone.utc).isoformat()
    notes = [json.loads(r.history_note(budget, year_from, year_to, work_types)) for r in results]
    settings = notes[0]["settings"] if notes else search_settings(budget, year_from, year_to, work_types)
    filtered = sum(r.filtered_count for r in results)
    manifest = {
        "format_version": 1, "run_id": run_id or uuid4().hex, "query": query,
        "started_utc": min((r.started_utc for r in results if r.started_utc), default=now),
        "finished_utc": max((r.finished_utc for r in results if r.finished_utc), default=now),
        "settings": settings,
        "status": ("complete" if results and all(r.status == "complete" for r in results)
                   else "partial" if any(r.pages_completed for r in results) else "error"),
        "counts": {
            "raw_fetched": sum(r.fetched_count for r in results),
            "filtered": filtered, "unique_in_run": len(records),
            "duplicate_filtered_entries": filtered - len(records),
            "new_library_records": new_records,
        },
        "providers": [{
            "provider": r.provider, "reported_total": r.reported_total, "status": r.status,
            "started_utc": r.started_utc, "finished_utc": r.finished_utc,
            **note["retrieval"],
        } for r, note in zip(results, notes)],
        "coverage_limits": list(COVERAGE_LIMITS),
        "provenance": [dict(p) for r in results for p in r.provenance],
    }
    return {"manifest": manifest, "records": records}


def history_note_for_run(result, run):
    """Version two fits the existing note column and does not rewrite old notes."""
    manifest = run["manifest"]
    source = next((p for p in manifest["providers"] if p["provider"] == result.provider), None)
    if source is None:
        raise ValueError("History provider is not part of this run.")
    if (result.query and result.query != manifest["query"]) or (
        result.settings_snapshot is not None and result.settings_snapshot != manifest["settings"]
    ):
        raise ValueError("History result does not belong to this run's search context.")
    if (result.started_utc, result.finished_utc, result.fetched_count, result.filtered_count,
        result.stop_reason) != (source["started_utc"], source["finished_utc"], source["raw_fetched"],
                                source["filtered"], source["stop_reason"]):
        raise ValueError("History result does not match the captured run.")
    return json.dumps({
        "version": 2, "run_id": manifest["run_id"], "query": manifest["query"],
        "settings": manifest["settings"], "run_counts": manifest["counts"],
        "run_status": manifest["status"],
        "run_started_utc": manifest["started_utc"], "run_finished_utc": manifest["finished_utc"],
        "retrieval": source,
        "provenance": [p for p in manifest["provenance"] if p["provider"] == result.provider],
    }, ensure_ascii=False)


def _csv_bytes(records, columns):
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=columns, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(records)
    return output.getvalue().encode("utf-8-sig")


def run_bundle(run):
    """Export a run snapshot, not a filtered view of the accumulated library."""
    manifest = run["manifest"]
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        bundle.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        bundle.writestr("records.csv", _csv_bytes(run["records"], RECORD_COLUMNS))
        bundle.writestr("provenance.csv", _csv_bytes(manifest["provenance"], PROVENANCE_COLUMNS))
    return output.getvalue()
