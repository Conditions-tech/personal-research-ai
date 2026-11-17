"""Explicitly opt-in, small public-query smoke check. Never opens production data."""

import argparse
import ast
from collections import Counter
from contextlib import closing
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import time
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import requests

from discovery.providers import CrossrefAdapter, HEADERS, OpenAlexAdapter
from discovery.metadata import filter_search_results, normalize_crossref
from discovery.retrieval import RetrievalBudget, retrieve
from discovery.runs import history_note_for_run, make_run, run_bundle


def run_smoke(conference_supplement=False, supplement_query=None):
    report = {"started_utc": datetime.now(timezone.utc).isoformat(),
              "request_cap": 11, "page_size": 2, "cases": [], "requests": []}
    last_start = None
    storage_tree = ast.parse((ROOT / "app.py").read_text(encoding="utf-8"))
    storage_names = {"connect_db", "now_utc", "save_papers", "save_search"}
    definitions = [n for n in storage_tree.body if isinstance(n, ast.FunctionDef) and n.name in storage_names]
    assert {n.name for n in definitions} == storage_names
    cases = [
        ("journal-pages", "The Hallmarks of Cancer", ["journal-paper"], None, None, 2),
        ("conference-pages", "Deep Residual Learning for Image Recognition", ["conference-paper"], None, None, 2),
        ("historical", "Philosophical Transactions", [], None, 1800, 1),
        ("natural-empty", "zzqvx8f7c4b2dphasebnaturalempty", [], None, None, 1),
    ]
    if conference_supplement:
        report["request_cap"] = 2
        cases = [("conference-supplement", supplement_query or "IEEE International Conference on Robotics and Automation",
                  ["conference-paper"], None, None, 2)]
    real_connect = sqlite3.connect
    stop_live = False
    with tempfile.TemporaryDirectory(prefix="pra-phaseb-live-") as directory:
        temporary_root = Path(directory).resolve()

        def guarded_connect(database, *args, **kwargs):
            if kwargs.get("uri") or not Path(database).resolve().is_relative_to(temporary_root):
                raise AssertionError("Live smoke storage outside temporary root blocked.")
            return real_connect(database, *args, **kwargs)

        storage = {"sqlite3": sqlite3, "DB_PATH": temporary_root / "research.db",
                   "closing": closing, "datetime": datetime, "timezone": timezone}
        exec(compile(ast.Module(body=definitions, type_ignores=[]), "app.py", "exec"), storage)
        with patch("sqlite3.connect", side_effect=guarded_connect):
            storage["connect_db"]().close()
            for label, query, categories, start, end, pages in cases:
                if stop_live:
                    break
                budget = RetrievalBudget(max_records=2 * pages, page_size=2, max_pages=pages, max_seconds=90)
                results = []
                for factory in (OpenAlexAdapter, CrossrefAdapter):
                    if conference_supplement and factory is OpenAlexAdapter:
                        continue
                    if label == "historical" and factory is CrossrefAdapter:
                        continue
                    expected_cursor = "*"
                    provider_steps = []

                    def observed_request(url, params):
                        nonlocal last_start, expected_cursor
                        if len(report["requests"]) >= report["request_cap"]:
                            raise AssertionError("Live request cap exceeded.")
                        if last_start is not None:
                            time.sleep(max(0, 2 - (time.monotonic() - last_start)))
                        last_start = time.monotonic()
                        step = {"case": label, "provider": factory.name,
                                "sequence": len(provider_steps) + 1,
                                "page_size": params.get("per_page", params.get("rows")),
                                "page": params.get("page"),
                                "year_filter": params.get("filter", ""),
                                "started_utc": datetime.now(timezone.utc).isoformat(),
                                "cursor_follows_previous": (params.get("cursor") == expected_cursor
                                                            if factory is CrossrefAdapter else None)}
                        report["requests"].append(step)
                        provider_steps.append(step)
                        try:
                            with requests.get(url, params=params, headers=HEADERS, timeout=45) as response:
                                step["http_status"] = response.status_code
                                response.raise_for_status()
                                payload = response.json()
                        except requests.RequestException:
                            step["request_failed"] = True
                            raise
                        container = payload.get("meta", {}) if factory is OpenAlexAdapter else payload.get("message", {})
                        items = payload.get("results", []) if factory is OpenAlexAdapter else container.get("items", [])
                        step["raw_fetched"] = len(items)
                        step["raw_types"] = dict(Counter(i.get("type", "") for i in items))
                        step["reported_total"] = container.get("count" if factory is OpenAlexAdapter else "total-results")
                        expected_cursor = container.get("next-cursor")
                        return payload

                    result = retrieve(factory(observed_request), query, budget, start, end, categories)
                    results.append(result)
                    evidence_valid = all(
                        (not categories or (
                            p["raw_type"] == ("journal-article" if categories == ["journal-paper"] else "proceedings-article")
                            if factory is CrossrefAdapter else (
                                p["raw_type"] in ("article", "review") and p["source_type"] == "journal"
                                if categories == ["journal-paper"] else
                                p["raw_type"] == "conference-paper" or
                                p["raw_type"] in ("article", "review") and p["source_type"] == "conference"
                            )
                        )) and (end is None or p["year"] is not None and p["year"] <= end)
                        for p in result.provenance
                    )
                    observed_totals = [s.get("reported_total") for s in provider_steps if "raw_fetched" in s]
                    checks = {
                        "pages_traversed": result.pages_completed == pages,
                        "raw_count_matches_pages": result.fetched_count == sum(s.get("raw_fetched", 0) for s in provider_steps),
                        "first_total_preserved": bool(observed_totals) and result.reported_total == observed_totals[0],
                        "within_budget": result.fetched_count <= budget.max_records and result.requests_attempted <= pages,
                        "cursor_sequence": all(s["cursor_follows_previous"] is not False for s in provider_steps),
                        "filter_evidence": evidence_valid,
                        "positive_type_or_historical_evidence": bool(result.records) if label != "natural-empty" else True,
                        "natural_empty": (result.reported_total == result.fetched_count == result.filtered_count == 0
                                          and result.status == "complete") if label == "natural-empty" else True,
                        "no_error": not result.error,
                    }
                    report["cases"].append({
                        "case": label, "query": query, "provider": factory.name,
                        "years": [start, end], "categories": categories,
                        "reported_total": result.reported_total, "total_scope": result.total_scope,
                        "fetched": result.fetched_count, "filtered": result.filtered_count,
                        "unique": result.unique_count, "pages": result.pages_completed,
                        "status": result.status, "stop_reason": result.stop_reason,
                        "error": result.error,
                        "retained_types": dict(Counter(r["work_type"] for r in result.records)),
                        "retained_years": sorted({r["year"] for r in result.records if r["year"] is not None}),
                        "checks": checks,
                    })
                    print(json.dumps(report["cases"][-1]), flush=True)
                    if result.error:
                        stop_live = True
                        break  # No more live calls after a service/transport error.

                records = [p for result in results for p in result.records]
                added = storage["save_papers"](records)
                replay_added = storage["save_papers"](records)
                run = make_run(query, budget, results, start, end, categories, new_records=added)
                for result in results:
                    storage["save_search"](query, result.provider, result.reported_total,
                                           result.filtered_count, result.status, history_note_for_run(result, run))
                with zipfile.ZipFile(io.BytesIO(run_bundle(run))) as bundle:
                    exported = json.loads(bundle.read("manifest.json"))
                    assert exported == run["manifest"]
                report.setdefault("runs", []).append({
                    "case": label, "run_id": run["manifest"]["run_id"],
                    "counts": run["manifest"]["counts"], "replay_insertions": replay_added,
                    "export_round_trip": exported == run["manifest"],
                })
                assert replay_added == 0
            with closing(guarded_connect(storage["DB_PATH"])) as connection:
                report["temporary_counts"] = {
                    table: connection.execute("SELECT COUNT(*) FROM " + table).fetchone()[0]
                    for table in ("papers", "searches")
                }
    report["temporary_storage_removed"] = not temporary_root.exists()
    report["finished_utc"] = datetime.now(timezone.utc).isoformat()
    report["passed"] = (len(report["cases"]) == (1 if conference_supplement else 7) and
                        all(all(c["checks"].values()) for c in report["cases"]) and
                        report["temporary_storage_removed"])
    return report


def known_conference_smoke():
    """One public singleton lookup; independent of query ranking and pagination."""
    doi = "10.1109/CVPR.2016.90"
    with requests.get("https://api.crossref.org/works/" + doi, headers=HEADERS, timeout=45) as response:
        response.raise_for_status()
        item = response.json()["message"]
        status = response.status_code
    record = normalize_crossref(item)
    report = {
        "mode": "known-work lookup, not query pagination", "doi": doi, "http_status": status,
        "raw_type": item.get("type"), "doi_matches": record["doi"] == doi.lower(),
        "conference_retained": bool(filter_search_results([record], work_types=["conference-paper"])),
        "journal_retained": bool(filter_search_results([record], work_types=["journal-paper"])),
    }
    report["passed"] = (report["doi_matches"] and report["conference_retained"] and not report["journal_retained"])
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Explicitly permit at most 11 public API requests.")
    parser.add_argument("--report", type=Path, help="Write aggregate results, never provider payloads.")
    parser.add_argument("--conference-supplement", action="store_true",
                        help="Only two Crossref pages for a conference-focused query; at most two requests.")
    parser.add_argument("--supplement-query", help="Public bibliographic query for the conference supplement.")
    parser.add_argument("--known-conference", action="store_true",
                        help="One public CVPR DOI lookup to verify native conference classification.")
    args = parser.parse_args()
    if not args.live:
        parser.error("Live API calls require the explicit --live flag and user authorization.")
    if args.known_conference and args.conference_supplement:
        parser.error("Choose a pagination supplement or known-work lookup.")
    if args.supplement_query and not args.conference_supplement:
        parser.error("--supplement-query requires --conference-supplement.")
    if args.report:
        target = args.report.resolve()
        if (target.suffix.lower() != ".json" or ":" in target.name
                or target.is_relative_to((ROOT / "data").resolve())
                or target.exists() or not target.parent.is_dir()):
            parser.error("Report must be a new .json file outside production data, in an existing directory.")
        args.report = target
    report = (known_conference_smoke() if args.known_conference else
              run_smoke(args.conference_supplement, args.supplement_query))
    if args.report:
        with args.report.open("x", encoding="utf-8") as output:
            output.write(json.dumps(report, indent=2))
    print(json.dumps({"passed": report["passed"], "requests": len(report.get("requests", [None])),
                      "temporary_storage_removed": report.get("temporary_storage_removed")}), flush=True)
    sys.exit(0 if report["passed"] else 1)
