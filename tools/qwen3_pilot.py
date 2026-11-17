"""Explicit, bounded Qwen3 diagnostic; never changes application model routing."""

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import time
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
MODEL = "qwen3:4b-q4_K_M"
DIGEST = "2bfd38a7daaf4b1037efe517ccb73d1a3bbd4822cf89f1a82be1569050a114e0"
VERSION = "qwen3-abstract-quotes-pilot-v1"
RUNTIME = "0.40.6"
ENDPOINT = "http://127.0.0.1:11434"
MIN_AVAILABLE = 11 * 1024 ** 3 // 2
OPTIONS = {"temperature": 0, "seed": 42, "num_ctx": 6144, "num_predict": 1024,
           "num_gpu": 0, "num_thread": 4}


def build(context):
    from review.quote_analysis_v5 import build as quote_request
    abstract = context["record"]["abstract"]
    if not isinstance(abstract, str) or not abstract.strip() or len(abstract) > 4000:
        raise ValueError("A nonempty abstract of at most 4,000 characters is required.")
    return {**quote_request(context, OPTIONS), "think": False}


class PilotBlocked(ValueError):
    """Resource, identity or compatibility boundary; no further load attempts."""


class Backend:
    def __init__(self, ledger, case):
        self.ledger, self.case = ledger, case
        self.events = []

    def request(self, path, body=None):
        import requests
        from review.analysis import strict_json
        if path not in ("/api/version", "/api/tags", "/api/show", "/api/ps", "/api/generate"):
            raise PilotBlocked("Unapproved local endpoint.")
        event = {"method": "GET" if body is None else "POST", "path": path}
        if path == "/api/generate":
            from coverage_evaluation import debit
            from local_analysis_benchmark import available_memory
            if not isinstance(body, dict) or body.get("model") != MODEL or body.get("think") is not False or body.get("options") != OPTIONS or body.get("keep_alive") != 0 or body.get("stream") is not False:
                raise PilotBlocked("Unapproved generation settings.")
            if available_memory() < MIN_AVAILABLE:
                raise PilotBlocked("Available memory below the unchanged 5.5 GiB Qwen3 loading gate.")
            budget = json.loads(self.ledger.read_text(encoding="utf-8"))
            if any(e.get("case") == self.case for e in budget.get("entries", [])):
                raise PilotBlocked("This case already consumed a generation attempt; no duplicate trial.")
            debit(self.ledger, self.case, VERSION)
        self.events.append(event)
        try:
            with requests.Session() as session:
                session.trust_env = False
                with session.request(event["method"], ENDPOINT + path, json=body,
                                     timeout=(2, 120 if path == "/api/generate" else 3),
                                     allow_redirects=False, stream=True) as response:
                    event["http_status"] = response.status_code
                    data = bytearray()
                    for part in response.iter_content(chunk_size=4096):
                        data.extend(part)
                        if len(data) > 32 * 1024:
                            event["raw_body"] = data[:32 * 1024].decode("utf-8", errors="replace")
                            raise PilotBlocked("Local response exceeded 32 KiB; preserved bounded body.")
                    event["raw_body"] = data.decode("utf-8", errors="replace")
                    if response.status_code != 200:
                        raise PilotBlocked("Local HTTP failure; no silent retry.")
                    return strict_json(data.decode("utf-8"))
        except (requests.RequestException, UnicodeError, ValueError, RecursionError) as error:
            if isinstance(error, PilotBlocked):
                raise
            event["error_type"] = type(error).__name__
            raise PilotBlocked("Local transport or JSON failure; no silent retry.") from error

    def inventory(self):
        tags = self.request("/api/tags")
        models = tags.get("models") if isinstance(tags, dict) else None
        if not isinstance(models, list):
            raise PilotBlocked("Invalid local inventory.")
        matches = [m for m in models if isinstance(m, dict) and m.get("name") == MODEL]
        if len(matches) != 1 or matches[0].get("digest") != DIGEST or any(
                matches[0].get(k) for k in ("remote_host", "remote_model")):
            raise PilotBlocked("Approved local model/digest unavailable; no fallback or download.")
        return matches[0]

    def inspect(self):
        runtime = self.request("/api/version")
        if not isinstance(runtime, dict) or runtime.get("version") != RUNTIME:
            raise PilotBlocked("Runtime differs from the approved existing version.")
        model = self.inventory()
        show = self.request("/api/show", {"model": MODEL})
        if not isinstance(show, dict) or any(show.get(k) for k in ("remote_host", "remote_model")):
            raise PilotBlocked("Local model details required.")
        details = show.get("details", {})
        if not isinstance(details, dict) or details.get("format") != "gguf" or details.get("quantization_level") != "Q4_K_M" or details.get("family") != "qwen3":
            raise PilotBlocked("Qwen3 GGUF Q4_K_M details required.")
        controls = show.get("thinking", {}).get("values", []) if isinstance(show.get("thinking", {}), dict) else []
        capabilities = show.get("capabilities")
        if not isinstance(capabilities, list) or "thinking" not in capabilities or not isinstance(controls, list) or not any(v is False for v in controls):
            raise PilotBlocked("Explicit model support for think:false has not been verified.")
        return {"model": MODEL, "model_digest": DIGEST, "runtime_version": RUNTIME,
                "endpoint": ENDPOINT, "size_bytes": model.get("size"), "details": details,
                "thinking_controls": show["thinking"], "capabilities": show["capabilities"]}

    def unloaded(self, seconds=10):
        deadline = time.monotonic() + seconds
        while True:
            state = self.request("/api/ps")
            if not isinstance(state, dict) or not isinstance(state.get("models"), list):
                raise PilotBlocked("Cannot verify unloaded state.")
            if not state["models"]:
                return
            if time.monotonic() >= deadline:
                raise PilotBlocked("A model is still loaded; no new load or application closure.")
            time.sleep(0.25)

    def generate(self, request):
        from local_analysis_benchmark import available_memory
        identity = self.inspect()
        if request.get("options") != OPTIONS or request.get("think") is not False or request.get("stream") is not False or request.get("keep_alive") != 0:
            raise PilotBlocked("Request differs from the frozen CPU/nonthinking/unload configuration.")
        self.unloaded()
        free = available_memory()
        if free < MIN_AVAILABLE:
            raise PilotBlocked("Available memory below the unchanged 5.5 GiB Qwen3 loading gate.")
        identity["immediate_pre_load_available_bytes"] = free
        try:
            result = self.request("/api/generate", {**request, "model": MODEL})
        finally:
            # Verify requested immediate unload, including transport/output failures.
            self.unloaded()
        if self.inventory()["digest"] != identity["model_digest"]:
            raise PilotBlocked("Model identity changed during generation.")
        if not isinstance(result, dict) or result.get("model") != MODEL or result.get("done") is not True or result.get("done_reason") != "stop" or not isinstance(result.get("response"), str):
            raise PilotBlocked("Incomplete or mismatched generation; raw response retained.")
        count = result.get("prompt_eval_count")
        if type(count) is not int or not 0 < count < OPTIONS["num_ctx"] - OPTIONS["num_predict"]:
            raise PilotBlocked("Prompt completion/context budget was not verified.")
        if result.get("thinking"):
            raise PilotBlocked("Unexpected thinking output with think:false; raw response retained.")
        return {**identity, "response": result["response"], "wire_response": result}


def evaluate(manifest_path, ledger, output, case_ids=None):
    from coverage_evaluation import make_review
    from local_analysis_benchmark import available_memory, MemoryMonitor
    from review.analysis import evidence_context, strict_json
    from review.quote_analysis_v5 import validate
    from review.workspace import create_review, export_review, restore_review
    raw = manifest_path.read_bytes()
    manifest = json.loads(raw)
    if manifest.get("protocol") != VERSION or not 1 <= len(manifest["cases"]) <= 12:
        raise ValueError("Explicit frozen Qwen3 manifest required.")
    all_ids = [c.get("id") for c in manifest["cases"]]
    if len(set(all_ids)) != len(all_ids) or (case_ids is not None and (
            not case_ids or len(set(case_ids)) != len(case_ids) or set(case_ids)-set(all_ids))):
        raise ValueError("Select unique case IDs from the exact frozen manifest.")
    selected = [c for c in manifest["cases"] if case_ids is None or c["id"] in case_ids]
    report = {"protocol": VERSION, "manifest_sha256": hashlib.sha256(raw).hexdigest(),
              "partition": manifest["partition"], "started_utc": datetime.now(timezone.utc).isoformat(),
              "experimental_not_app_proposal": True, "requested_case_ids": [c["id"] for c in selected],
              "state": "running", "cases": []}

    def save():
        pending = output.with_suffix(".pending")
        with pending.open("x", encoding="utf-8") as file:
            json.dump(report, file, ensure_ascii=False, indent=2, allow_nan=False)
        pending.replace(output)

    with output.open("x", encoding="utf-8") as file:
        json.dump(report, file)
    with patch("sqlite3.connect", side_effect=AssertionError("Pilot SQLite blocked")):
        for case in selected:
            free = available_memory()
            if free < MIN_AVAILABLE:
                report["blocker"] = {"reason": "Available memory below unchanged 5.5 GiB gate", "available_bytes": free}
                break
            if case["kind"] not in ("synthetic", "public-abstract") or not case.get("license"):
                raise ValueError("Only explicitly licensed public/synthetic fixtures allowed.")
            base = make_review([case], manifest["partition"])
            run = copy.deepcopy(base["run"])
            run["manifest"]["provenance"][0]["captured_date"] = case.get("capture_utc", case.get("accessed_date", "2026-10-21"))[:10]
            review = create_review(run, "Fixed Qwen3 pilot", "Frozen public/synthetic evidence", "Private research")
            original = copy.deepcopy(review)
            key = next(iter(review["papers"]))
            context = evidence_context(review, key)
            item = {"case": case, "context": context, "original_review": review, "pre_load_available_bytes": free}
            report["cases"].append(item)
            backend = Backend(ledger, case["id"])
            item["events"] = backend.events
            start = time.perf_counter()
            with MemoryMonitor() as memory:
                try:
                    item["request"] = build(context)
                    save()
                    item["generation"] = backend.generate(copy.deepcopy(item["request"]))
                    item["fields"] = validate(context, strict_json(item["generation"]["response"]))
                except (ValueError, OSError) as error:
                    item.update(status="refused-or-failed", error=str(error))
                    if isinstance(error, PilotBlocked):
                        report["blocker"] = {"reason": str(error)}
                else:
                    item["status"] = "validated-experimental-fields"
            item.update(seconds=round(time.perf_counter()-start, 3), memory=memory.report(),
                        original_review_unchanged=review == original,
                        original_review_roundtrip=restore_review(export_review(review)) == review)
            assert item["original_review_unchanged"] and item["original_review_roundtrip"]
            save()
            print(json.dumps({"case": case["id"], "status": item["status"], "seconds": item["seconds"]}), flush=True)
            if report.get("blocker"):
                break
    report.update(state="blocked" if report.get("blocker") else "complete", finished_utc=datetime.now(timezone.utc).isoformat())
    save()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live-local", action="store_true")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--case-id", action="append", help="Explicit frozen cases for first smoke/resume; attempted cases are never retried.")
    args = parser.parse_args()
    if not args.live_local or args.report.exists() or args.report.suffix.lower() != ".json":
        parser.error("Explicit --live-local and a new JSON report are required.")
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(ROOT / "tools"))
    evaluate(args.manifest, args.ledger, args.report, args.case_id)


if __name__ == "__main__":
    main()
