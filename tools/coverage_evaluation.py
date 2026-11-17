"""Opt-in fixed-partition C2 evaluation with a shared 12-request budget.

Inputs are explicit synthetic/public licensed fixtures, never production records.
Reports are incremental; the owned ledger is debited before each generation POST.
"""

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
import time
from unittest.mock import patch
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]


def debit(ledger, case_id, version):
    lock = ledger.with_suffix(".lock")
    lock.open("x").close()
    try:
        value = json.loads(ledger.read_text(encoding="utf-8"))
        if value.get("kind") != "c2-coverage-budget-v1" or type(value.get("cap")) is not int or value["cap"] != 12 or type(value.get("used")) is not int or not isinstance(value.get("entries"), list) or value["used"] != len(value["entries"]):
            raise ValueError("Invalid evaluation budget ledger.")
        if not 0 <= value["used"] < 12:
            raise ValueError("The approved 12-generation evaluation budget is exhausted.")
        value["used"] += 1
        value["entries"].append({"case": case_id, "protocol": version,
                                 "requested_utc": datetime.now(timezone.utc).isoformat()})
        temporary = ledger.with_suffix(".pending")
        with temporary.open("x", encoding="utf-8") as output:
            json.dump(value, output, indent=2)
        os.replace(temporary, ledger)
    finally:
        lock.unlink()


def make_review(cases, partition):
    from review.workspace import create_review
    records, provenance = [], []
    for case in cases:
        key = "doi:" + case["doi"] if case["doi"] else "fixture:" + case["id"]
        record = {"record_key": key, "title": case["title"], "abstract": case["abstract"],
                  "authors": case["authors"], "year": case["year"], "doi": case["doi"],
                  "url": case["source_url"], "source": "PLOS licensed evaluation" if case["kind"] == "public-abstract" else "Developer synthetic evaluation"}
        records.append(record)
        provenance.append({"record_key": key, "provider": record["source"], "source_id": case["doi"] or case["id"],
                           "source_url": case["source_url"], "license": case["license"],
                           "license_url": case.get("license_url", ""), "captured_date": "2026-10-20"})
    stamp = datetime.now(timezone.utc).isoformat()
    run = {"manifest": {"format_version": 1, "run_id": uuid4().hex,
                        "query": "Fixed isolated field-coverage evaluation: " + partition,
                        "started_utc": stamp, "finished_utc": stamp, "status": "complete",
                        "settings": {"fixture_partition": partition, "not_a_provider_search": True},
                        "counts": {"unique_in_run": len(records)}, "provenance": provenance,
                        "coverage_limits": ["Fixed evaluation fixtures only; no provider traversal or worldwide coverage claim."]},
           "records": records}
    return create_review(run, "Fixed field-coverage evaluation", "Explicit frozen fixtures only", "Private research and production records")


def evaluate(manifest_path, version, ledger, output):
    import requests
    from local_analysis_benchmark import MemoryMonitor, MIN_AVAILABLE_BYTES, wait_for_memory_gate
    from review.analysis import generate_analysis
    from review.local_backend import OllamaLocal
    from review.workspace import export_review, restore_review

    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    report = {"started_utc": datetime.now(timezone.utc).isoformat(), "partition": manifest["partition"],
              "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(), "protocol": version,
              "developer_evaluation_not_independent_scientific_review": True, "cases": [],
              "minimum_available_memory_bytes": MIN_AVAILABLE_BYTES, "requests": [], "state": "running"}
    def save():
        temporary = output.with_suffix(".pending")
        with temporary.open("x", encoding="utf-8") as file:
            json.dump(report, file, ensure_ascii=False, indent=2, allow_nan=False)
        os.replace(temporary, output)

    class MeteredBackend(OllamaLocal):
        current_case = ""
        wire = None

        def _request(self, path, body=None, generation=False):
            if generation:
                debit(ledger, self.current_case, version)
            value = super()._request(path, body, generation)
            if generation:
                self.wire = copy.deepcopy(value)
            return value

    actual_request = requests.sessions.Session.request
    def local_only(session, method, url, **kwargs):
        if not url.startswith("http://127.0.0.1:11434/api/"):
            raise AssertionError("Non-loopback evaluation request blocked.")
        report["requests"].append({"method": method, "path": url.split("11434", 1)[1]})
        return actual_request(session, method, url, **kwargs)

    with output.open("x", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=2)
    free = wait_for_memory_gate()
    if free < MIN_AVAILABLE_BYTES:
        report.update(state="blocked", blocker={"reason": "Memory below unchanged approved gate", "available_bytes": free}, finished_utc=datetime.now(timezone.utc).isoformat())
        save()
        return
    with tempfile.TemporaryDirectory(prefix="pra-field-evaluation-") as temporary:
        # Review work is pure in-memory. Even temporary SQLite is unnecessary here.
        with patch("sqlite3.connect", side_effect=AssertionError("Evaluation SQLite blocked")), patch("requests.sessions.Session.request", new=local_only):
            backend = MeteredBackend()
            try:
                report["backend"] = backend.inspect()
            except ValueError as error:
                report.update(state="blocked", blocker={"reason": str(error)}, finished_utc=datetime.now(timezone.utc).isoformat())
                save()
                return
            save()
            review = make_review(manifest["cases"], manifest["partition"])
            for case, key in zip(manifest["cases"], review["papers"]):
                free = wait_for_memory_gate()
                if free < MIN_AVAILABLE_BYTES:
                    report["blocker"] = {"reason": "Memory below unchanged approved gate", "available_bytes": free}; break
                backend.current_case = case["id"]; backend.wire = None
                before = copy.deepcopy(review); started = time.perf_counter()
                item = {"case": case, "pre_load_available_bytes": free}
                print(json.dumps({"case": case["id"], "partition": manifest["partition"], "protocol": version, "action": "analysis attempt"}), flush=True)
                with MemoryMonitor() as memory:
                    try:
                        review = generate_analysis(review, key, backend, prompt_version=version)
                    except ValueError as error:
                        assert review == before
                        item.update(status="refused-or-failed", error_type=type(error).__name__, error=str(error))
                    else:
                        item.update(status="proposal-pending", draft=review["papers"][key]["ai_drafts"][-1])
                item.update(seconds=round(time.perf_counter()-started, 3), memory=memory.report(), wire_response=backend.wire)
                report["cases"].append(item); save()
                print(json.dumps({"case": case["id"], "status": item["status"], "model_completed": item["wire_response"] is not None, "seconds": item["seconds"]}), flush=True)
                if "12-generation" in item.get("error", ""):
                    report["blocker"] = {"reason": item["error"]}; break
            report["review_roundtrip"] = restore_review(export_review(review)) == review
    report.update(state="complete" if not report.get("blocker") else "blocked", finished_utc=datetime.now(timezone.utc).isoformat())
    save()
    print(json.dumps({"report": str(output), "budget_used": json.loads(ledger.read_text())["used"], "state": report["state"]}), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live-local", action="store_true")
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--version", choices=["abstract-quotes-v2", "abstract-quotes-v3", "abstract-quotes-v4", "abstract-quotes-v5"])
    parser.add_argument("--ledger", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if not args.live_local:
        parser.error("Explicit --live-local opt-in is required")
    if not args.report or args.report.suffix.lower() != ".json" or args.report.exists() or not args.report.parent.is_dir():
        parser.error("Report must be a new .json file")
    if not args.manifest or not args.manifest.is_file() or not args.ledger or args.ledger.suffix.lower() != ".json" or not args.ledger.is_file() or not args.version:
        parser.error("Existing fixture manifest, budget ledger and protocol are required")
    if sys.platform != "win32":
        parser.error("Resource-monitored evaluation requires Windows")
    sys.path.insert(0, str(ROOT))
    evaluate(args.manifest, args.version, args.ledger, args.report)


if __name__ == "__main__":
    main()
