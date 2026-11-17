"""Opt-in v6 single-role pilot. Public fixtures only, no app proposal promotion."""

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def evaluate(manifest_path, ledger, output):
    import requests
    from coverage_evaluation import debit, make_review
    from local_analysis_benchmark import MemoryMonitor, MIN_AVAILABLE_BYTES, wait_for_memory_gate
    from review.analysis import OPTIONS, evidence_context
    from review.local_backend import OllamaLocal
    from review.role_analysis_v6 import VERSION, build, validate
    from review.workspace import SUMMARY_FIELDS, create_review, export_review, restore_review

    data = manifest_path.read_bytes()
    manifest = json.loads(data)
    report = {"kind": "experimental-single-role-report-v1", "protocol": VERSION,
              "manifest_sha256": hashlib.sha256(data).hexdigest(), "partition": manifest["partition"],
              "started_utc": datetime.now(timezone.utc).isoformat(), "state": "running",
              "experimental_not_an_accepted_review_proposal": True, "cases": [], "requests": []}

    def save():
        pending = output.with_suffix(".pending")
        with pending.open("x", encoding="utf-8") as file:
            json.dump(report, file, ensure_ascii=False, indent=2, allow_nan=False)
        os.replace(pending, output)

    class MeteredBackend(OllamaLocal):
        current_case_role = ""
        wire = None

        def _request(self, path, body=None, generation=False):
            if generation:
                debit(ledger, self.current_case_role, VERSION)
            value = super()._request(path, body, generation)
            if generation:
                self.wire = copy.deepcopy(value)
            return value

    real_request = requests.sessions.Session.request

    def loopback(session, method, url, **kwargs):
        if not url.startswith("http://127.0.0.1:11434/api/"):
            raise AssertionError("Non-loopback pilot request blocked.")
        report["requests"].append({"method": method, "path": url.split("11434", 1)[1]})
        return real_request(session, method, url, **kwargs)

    with output.open("x", encoding="utf-8") as file:
        json.dump(report, file)
    free = wait_for_memory_gate()
    if free < MIN_AVAILABLE_BYTES:
        report.update(state="blocked", blocker={"reason": "Memory below unchanged 4 GiB pre-load gate", "available_bytes": free})
        save(); return
    with patch("sqlite3.connect", side_effect=AssertionError("Pilot SQLite blocked")), patch("requests.sessions.Session.request", new=loopback):
        backend = MeteredBackend()
        try:
            report["backend"] = backend.inspect()
        except ValueError as error:
            report.update(state="blocked", blocker={"reason": str(error)})
            save(); return
        for case in manifest["cases"]:
            # Pure disposable public snapshot; correct provenance dates before
            # fingerprinting. Never opens a research library or an app module.
            base = make_review([case], manifest["partition"])
            run = copy.deepcopy(base["run"])
            run["manifest"]["provenance"][0]["captured_date"] = case.get("capture_date", case.get("capture_utc", "2026-10-21")[:10])
            review = create_review(run, "Single-role public pilot", "Explicit frozen public fixture", "Private research")
            before = copy.deepcopy(review)
            key = next(iter(review["papers"]))
            context = evidence_context(review, key)
            item = {"case": copy.deepcopy(case), "context": context, "roles": {}, "review_snapshot": review}
            report["cases"].append(item); save()
            for role in SUMMARY_FIELDS:
                free = wait_for_memory_gate()
                if free < MIN_AVAILABLE_BYTES:
                    report["blocker"] = {"reason": "Memory below unchanged 4 GiB pre-load gate", "available_bytes": free}; break
                backend.current_case_role = case["id"] + "/" + role
                backend.wire = None
                result = {"pre_load_available_bytes": free}
                item["roles"][role] = result
                print(json.dumps({"case": case["id"], "role": role, "action": "single-role attempt"}), flush=True)
                started = time.perf_counter()
                with MemoryMonitor() as memory:
                    try:
                        request = build(context, role, OPTIONS)
                        result["request"] = request
                        generated = backend.generate(copy.deepcopy(request))
                        result["generation"] = generated
                        if generated["model_digest"] != report["backend"]["model_digest"]:
                            raise ValueError("Model identity changed during the multi-request pilot.")
                        result["field"] = validate(context, role, generated["response"])
                    except (ValueError, OSError) as error:
                        result.update(status="refused-or-failed", error=str(error))
                    else:
                        result["status"] = "validated-experimental-field"
                result.update(seconds=round(time.perf_counter()-started, 3), memory=memory.report(), wire_response=backend.wire)
                assert review == before
                save()
                print(json.dumps({"case": case["id"], "role": role, "status": result["status"], "seconds": result["seconds"]}), flush=True)
                if "12-generation" in result.get("error", ""):
                    report["blocker"] = {"reason": result["error"]}; break
            item["original_review_unchanged"] = review == before
            item["original_review_roundtrip"] = restore_review(export_review(review)) == review
            if report.get("blocker"):
                break
    report.update(state="blocked" if report.get("blocker") else "complete", finished_utc=datetime.now(timezone.utc).isoformat())
    save()
    print(json.dumps({"state": report["state"], "budget_used": json.loads(ledger.read_text(encoding="utf-8"))["used"]}), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live-local", action="store_true")
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--ledger", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if not args.live_local:
        parser.error("Explicit --live-local opt-in is required.")
    if not args.report or args.report.exists() or args.report.suffix.lower() != ".json" or not args.report.parent.is_dir():
        parser.error("Report must be a new JSON file.")
    if not args.manifest or not args.manifest.is_file() or not args.ledger or args.ledger.suffix.lower() != ".json" or not args.ledger.is_file():
        parser.error("Existing frozen manifest and budget ledger are required.")
    if sys.platform != "win32":
        parser.error("Memory-monitored pilot requires Windows.")
    sys.path.insert(0, str(ROOT))
    evaluate(args.manifest, args.ledger, args.report)


if __name__ == "__main__": main()
