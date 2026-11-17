"""Bounded resource recovery around the unchanged, opt-in Qwen3 pilot.

No daemon restarts, process termination, global cache clearing or model downloads.
One invocation runs at most one frozen case. The external supervisor schedules
later checks; this process never respawns itself or lowers the RAM gate.
"""

import argparse
import ctypes
from datetime import datetime, timezone
import gc
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import qwen3_pilot as pilot
from local_analysis_benchmark import available_memory

REMAINING = ("public-0020753", "holdout-ecology-abbrev", "holdout-letters",
             "holdout-safe-task-instruction", "qwen3-synthetic-mixed-injection")
BASELINE_ENTRIES_SHA = "a755946612bce60765df43f6fdfa10f060ed89a52d7806dedb26ceb128be7e98"
FREEZE_SHA = "a55bacfa0af41fe4d29fc2d14dea3ce54eec4f91261d2080466620c4d442e521"
LEDGER = ROOT / "docs/C2_QWEN3_BUDGET_2026-10-21.json"
MANIFEST = ROOT / "docs/C2_QWEN3_HOLDOUT_2026-10-21.json"
STATE_DIR = ROOT / ".pilot_state/qwen3"


def now():
    return datetime.now(timezone.utc).isoformat()


def read(path):
    from review.analysis import strict_json
    return strict_json(path.read_text(encoding="utf-8"))


def save(path, value):
    pending = path.with_name(path.name + ".pending")
    with pending.open("w", encoding="utf-8") as file:
        json.dump(value, file, indent=2, allow_nan=False)
        file.flush()
        os.fsync(file.fileno())
    pending.replace(path)


class Busy(RuntimeError):
    pass


class Lease:
    """Kernel-held job lease, shared by controller and regression invocations.

    A leftover filename is harmless. Never delete a file to break a live lease.
    It coordinates these tools, not arbitrary external clients of Ollama.
    """
    def __init__(self, directory):
        self.directory = directory

    def __enter__(self):
        self.directory.mkdir(parents=True, exist_ok=True)
        self.file = (self.directory / "job.lock").open("a+b")
        try:
            if os.name == "nt":
                import msvcrt
                if self.file.seek(0, 2) == 0:
                    self.file.write(b"0"); self.file.flush()
                self.file.seek(0)
                msvcrt.locking(self.file.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            self.file.close()
            raise Busy("Another controlled job still owns the lease.") from error
        return self

    def __exit__(self, *_):
        self.file.close()  # Closing the handle releases the OS lease.


def process_birth(pid):
    """Creation token for a live Windows PID; None only if proven exited.

    Access denial/unknown state raises: neither is evidence of termination.
    """
    from ctypes import wintypes
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
    kernel.WaitForSingleObject.argtypes = (wintypes.HANDLE, wintypes.DWORD)
    kernel.GetProcessTimes.argtypes = (wintypes.HANDLE,) + (ctypes.POINTER(wintypes.FILETIME),) * 4
    handle = kernel.OpenProcess(0x1000 | 0x100000, False, pid)
    if not handle:
        if ctypes.get_last_error() == 87:  # ERROR_INVALID_PARAMETER: PID absent
            return None
        raise OSError("Cannot prove worker liveness.")
    try:
        state = kernel.WaitForSingleObject(handle, 0)
        if state == 0:
            return None
        if state != 258:
            raise OSError("Unknown worker wait status.")
        times = [wintypes.FILETIME() for _ in range(4)]
        if not kernel.GetProcessTimes(handle, *(ctypes.byref(t) for t in times)):
            raise OSError("Cannot identify worker creation time.")
        return str(times[0].dwHighDateTime << 32 | times[0].dwLowDateTime)
    finally:
        kernel.CloseHandle(handle)


def no_runtime_clients():
    """Conservative IPv4 connection check for the pinned IPv4 loopback port.

    This is a momentary check, not a server-side exclusion guarantee. Do not
    use the app/CLI against this runtime concurrently with this bounded pilot.
    """
    from ctypes import wintypes
    size = wintypes.DWORD()
    api = ctypes.WinDLL("iphlpapi").GetExtendedTcpTable
    api.argtypes = (ctypes.c_void_p, ctypes.POINTER(wintypes.DWORD), wintypes.BOOL,
                    wintypes.ULONG, ctypes.c_int, wintypes.ULONG)
    result = api(None, ctypes.byref(size), False, 2, 5, 0)
    if result not in (0, 122):
        raise OSError("Cannot inspect local runtime connections.")
    buffer = ctypes.create_string_buffer(size.value)
    if api(buffer, ctypes.byref(size), False, 2, 5, 0):
        raise OSError("Runtime connections changed during inspection.")
    count = int.from_bytes(buffer.raw[:4], "little")
    for i in range(count):
        values = (wintypes.DWORD * 6).from_buffer_copy(buffer.raw[4 + i*24:28 + i*24])
        ports = [int.from_bytes(int(values[n]).to_bytes(4, "little")[:2], "big") for n in (2, 4)]
        if values[0] in (3, 4, 5, 8) and 11434 in ports:
            return False
    return True


def unload_owned_model():
    """Documented control request, never an analysis request or ledger debit."""
    import requests
    from review.analysis import strict_json
    with requests.Session() as session:
        session.trust_env = False
        with session.post(pilot.ENDPOINT + "/api/generate",
                          json={"model": pilot.MODEL, "keep_alive": 0},
                          timeout=(2, 3), allow_redirects=False, stream=True) as response:
            data = bytearray()
            for part in response.iter_content(4096):
                data.extend(part)
                if len(data) > 32768:
                    raise ValueError("Oversized unload response.")
            value = strict_json(data.decode("utf-8"))
            if response.status_code != 200 or not isinstance(value, dict) or value.get("done") is not True or value.get("response") or value.get("thinking"):
                raise ValueError("Unload control did not confirm an empty completed response.")


def verified_budget(root=ROOT):
    """Validate original seven entries and frozen source before any runtime use."""
    freeze_path = root / "docs/C2_QWEN3_PROTOCOL_FREEZE_2026-10-21.json"
    if hashlib.sha256(freeze_path.read_bytes()).hexdigest() != FREEZE_SHA:
        raise ValueError("Frozen protocol file changed.")
    freeze = read(freeze_path)
    for relative, expected in freeze["source_and_evidence_sha256"].items():
        if hashlib.sha256((root / relative).read_bytes()).hexdigest() != expected:
            raise ValueError("Frozen source/evidence changed: " + relative)
    ledger = read(root / "docs/C2_QWEN3_BUDGET_2026-10-21.json")
    entries = ledger.get("entries", [])
    raw = json.dumps(entries[:7], sort_keys=True, separators=(",", ":")).encode()
    if hashlib.sha256(raw).hexdigest() != BASELINE_ENTRIES_SHA:
        raise ValueError("Original seven charged entries changed.")
    ids = [e.get("case") for e in entries]
    if (ledger.get("kind") != "c2-coverage-budget-v1" or ledger.get("cap") != 12
            or type(ledger.get("used")) is not int or not 7 <= ledger["used"] <= 12
            or ledger["used"] != len(entries) or len(set(ids)) != len(ids)
            or any(e.get("protocol") != pilot.VERSION for e in entries)
            or set(ids[7:]) - set(REMAINING)):
        raise ValueError("Invalid or expanded pilot ledger.")
    return ledger


class Controller:
    def __init__(self, directory=STATE_DIR, budget=verified_budget, memory=available_memory,
                 backend_factory=None, sleep=time.sleep, birth=process_birth,
                 clients=no_runtime_clients, unload=unload_owned_model, popen=subprocess.Popen):
        self.directory, self.budget, self.memory = directory, budget, memory
        self.backend_factory = backend_factory or (lambda: pilot.Backend(LEDGER, "recovery-control-only"))
        self.sleep, self.birth, self.clients, self.unload, self.popen = sleep, birth, clients, unload, popen
        self.path = directory / "state.json"

    def checkpoint(self, state, status):
        state.update(status=status, checked_utc=now())
        save(self.path, state)
        return state

    def idle(self, state):
        backend = self.backend_factory()
        state["runtime_check"] = {"status": "checking", "stage": "runtime_metadata_and_model_identity", "started_utc": now()}
        try:
            identity = backend.inspect()
        except Exception as error:
            self.record_runtime_failure(state, backend, error)
            raise
        state["runtime_identity"] = identity
        state["runtime_check"] = {"status": "checking", "stage": "loaded_model_inventory", "checked_utc": now()}
        try:
            response = backend.request("/api/ps")
            models = response.get("models") if isinstance(response, dict) else None
        except Exception as error:
            self.record_runtime_failure(state, backend, error)
            raise
        if not isinstance(models, list):
            error = ValueError("Invalid loaded-model inventory.")
            self.record_runtime_failure(state, backend, error)
            raise error
        state["loaded_model_count"] = len(models)
        state["runtime_check"] = {"status": "checking", "stage": "pre_control_loopback_client_check", "checked_utc": now()}
        try:
            client_free = self.clients()
        except Exception as error:
            self.record_runtime_failure(state, backend, error)
            raise
        if not client_free:
            state["runtime_check"] = {"status": "blocked", "stage": "active_loopback_client", "checked_utc": now()}
            return False
        if models:
            owned = state.get("owned_finished_case")
            if (not owned or len(models) != 1 or models[0].get("name") != pilot.MODEL
                    or models[0].get("digest") != pilot.DIGEST):
                state["runtime_check"] = {"status": "blocked", "stage": "loaded_model_not_proven_owned", "checked_utc": now()}
                return False
            state["runtime_check"] = {"status": "checking", "stage": "owned_model_unload", "checked_utc": now()}
            self.unload()
            state.setdefault("recovery_controls", []).append({"utc": now(), "case": owned,
                                                             "action": "empty-request-unload"})
            # The request returning alone is not proof that memory is released.
            for attempt in range(3):
                if backend.request("/api/ps").get("models") == []:
                    state["loaded_model_count"] = 0
                    break
                if attempt == 2:
                    state["runtime_check"] = {"status": "blocked", "stage": "unload_not_verified", "checked_utc": now()}
                    return False
                self.sleep(1)
        state.pop("owned_finished_case", None)
        state["runtime_check"] = {"status": "checking", "stage": "post_control_loopback_client_check", "checked_utc": now()}
        try:
            idle = self.clients()
        except Exception as error:
            self.record_runtime_failure(state, backend, error)
            raise
        if not idle:
            state["runtime_check"] = {"status": "blocked", "stage": "active_loopback_client", "checked_utc": now()}
            return False
        state["runtime_check"] = {"status": "ready", "stage": "idle_verified", "checked_utc": now()}
        return True

    @staticmethod
    def record_runtime_failure(state, backend, error):
        """Persist a useful, bounded readiness diagnosis without response bodies."""
        check = state.setdefault("runtime_check", {})
        check.update(status="blocked", checked_utc=now())
        state["runtime_identity"] = None
        state.pop("loaded_model_count", None)
        event = next((e for e in reversed(getattr(backend, "events", []))
                      if e.get("path") in ("/api/version", "/api/tags", "/api/show", "/api/ps")), None)
        problem = {"type": type(error).__name__, "stage": check.get("stage")}
        if event:
            problem["endpoint"] = event["path"]
            for field in ("http_status", "error_type"):
                if field in event:
                    problem[field] = event[field]
        if isinstance(error, pilot.PilotBlocked):
            problem["reason"] = str(error)[:240]
        else:
            problem["reason"] = "Runtime check failed; response details were withheld."
        state["last_check_error"] = problem

    def reconcile(self, state):
        job = state.get("active_job")
        if not job:
            return True
        if not job.get("pid") or not job.get("birth"):
            return False  # Crash during launch: do not guess that nothing started.
        token = self.birth(job["pid"])
        if token == job["birth"]:
            return False
        # Absent or reused PID proves the tracked worker has finished, not success.
        state.setdefault("finished_jobs", []).append({**job, "outcome": "exited-reconcile-report-and-ledger"})
        self.confirm_finished_owner(state, job)
        del state["active_job"]
        return True

    def confirm_finished_owner(self, state, job):
        """A dead HTTP client is not proof a server-side generation finished.

        Only a saved completed wire response can authorize owned-model unload.
        Missing/ambiguous reports stay charged and cannot authorize recovery.
        """
        if not job.get("case") or not job.get("report"):
            return
        try:
            report = read(Path(job["report"]))
            for item in report.get("cases", []):
                if item.get("case", {}).get("id") != job["case"]:
                    continue
                for event in item.get("events", []):
                    if event.get("path") != "/api/generate" or event.get("http_status") != 200:
                        continue
                    from review.analysis import strict_json
                    wire = strict_json(event.get("raw_body", ""))
                    if wire.get("model") == pilot.MODEL and wire.get("done") is True and wire.get("done_reason") == "stop":
                        state["owned_finished_case"] = job["case"]
        except (OSError, ValueError, AttributeError):
            return

    def run(self, generate=False, regression=False):
        try:
            with Lease(self.directory):
                try:
                    state = read(self.path) if self.path.exists() else {"version": 1}
                    if not isinstance(state, dict) or state.get("version") != 1:
                        raise ValueError("Unrecognized controller state.")
                except (OSError, ValueError):
                    # Preserve the suspect state for reconciliation, not overwrite.
                    return {"status": "waiting_state_reconciliation", "checked_utc": now()}
                if not regression:
                    state["memory_samples"] = []
                    state.pop("runtime_identity", None)
                    state.pop("loaded_model_count", None)
                    state.pop("last_check_error", None)
                    state.pop("error_type", None)
                    state["runtime_check"] = {"status": "not_checked", "stage": "not_started", "checked_utc": now()}
                try:
                    if not self.reconcile(state):
                        return self.checkpoint(state, "waiting_worker_reconciliation")
                    budget = self.budget()
                    state["charged"] = budget["used"]
                    state["pending"] = [c for c in REMAINING if c not in {e["case"] for e in budget["entries"]}]
                    if regression:
                        return self.worker(state, None, regression=True)
                    state["available_before_recovery_bytes"] = self.memory()
                    state["collected_python_objects"] = gc.collect()
                    if not self.idle(state):
                        return self.checkpoint(state, "waiting_runtime_idle")
                    for attempt in range(3):
                        free = self.memory()
                        state["memory_samples"].append({"utc": now(), "available_bytes": free})
                        if free >= pilot.MIN_AVAILABLE:
                            break
                        if attempt < 2:
                            self.sleep(5)
                    if not state["pending"]:
                        return self.checkpoint(state, "allocation_finished")
                    if free < pilot.MIN_AVAILABLE:
                        return self.checkpoint(state, "waiting_memory")
                    if not generate:
                        return self.checkpoint(state, "ready_no_generation_requested")
                    # Repeat runtime/client checks immediately before launching; the
                    # frozen child independently checks RAM/settings before debit.
                    if not self.idle(state):
                        return self.checkpoint(state, "waiting_runtime_idle")
                    return self.worker(state, state["pending"][0])
                except Exception as error:
                    # No raw research, HTTP response, environment or command text.
                    state["error_type"] = type(error).__name__
                    if state.get("runtime_check", {}).get("status") == "blocked":
                        status = "waiting_runtime_identity" if state["runtime_check"].get("stage") == "runtime_metadata_and_model_identity" else "waiting_check_failure"
                        return self.checkpoint(state, status)
                    return self.checkpoint(state, "waiting_check_failure")
        except Busy:
            return {"status": "busy", "checked_utc": now()}

    def worker(self, state, case, regression=False):
        prior_status = state.get("status") if regression else None
        tag = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "_" + uuid.uuid4().hex[:8]
        report = ROOT / "docs" / ("C2_QWEN3_RESUME_" + tag + "_RESULT.json")
        command = ([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"] if regression else
                   [sys.executable, str(ROOT / "tools/qwen3_pilot.py"), "--live-local",
                    "--manifest", str(MANIFEST), "--ledger", str(LEDGER),
                    "--report", str(report), "--case-id", case])
        job = {"case": case, "kind": "regression" if regression else "one-frozen-case",
               "report": None if regression else str(report), "started_utc": now(), "phase": "launching"}
        state["active_job"] = job
        self.checkpoint(state, "running")  # Durable before process creation.
        log = self.directory / (tag + ".log")
        with log.open("xb") as output:
            try:
                child = self.popen(command, cwd=ROOT, stdout=output, stderr=subprocess.STDOUT)
            except OSError:
                del state["active_job"]  # Popen failed: no child was created.
                raise
            job.update(pid=child.pid, phase="running", log=str(log))
            try:
                try:
                    job["birth"] = self.birth(child.pid)
                except OSError:
                    job["birth"] = None  # Still wait on the live Popen handle.
                self.checkpoint(state, "running")
            finally:
                # Even a metadata/checkpoint failure must not orphan our handle.
                # A caller/tool timeout is NOT evidence of process exit.
                job["exit_code"] = child.wait()
        state.setdefault("finished_jobs", []).append(dict(job))
        del state["active_job"]
        self.confirm_finished_owner(state, job)
        gc.collect()
        budget = self.budget()
        state["charged"] = budget["used"]
        state["pending"] = [c for c in REMAINING if c not in {e["case"] for e in budget["entries"]}]
        self.checkpoint(state, "worker_finished")
        if not regression and not self.idle(state):
            return self.checkpoint(state, "waiting_runtime_idle")
        if job["exit_code"] != 0:
            return self.checkpoint(state, "regression_failed" if regression else "case_process_failed_reconcile")
        if regression and prior_status:
            state["last_regression_exit_code"] = job["exit_code"]
            return self.checkpoint(state, prior_status)
        return self.checkpoint(state, "regression_finished" if regression else "case_finished_recheck_next_invocation")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--run-approved", action="store_true", help="At most one original uncharged case.")
    mode.add_argument("--regression", action="store_true", help="Run isolated suite under the same job lease.")
    args = parser.parse_args()
    result = Controller().run(args.run_approved, args.regression)
    print(json.dumps({k: result[k] for k in ("status", "charged", "pending", "memory_samples", "error_type") if k in result}))
    regression_failed = args.regression and result.get("last_regression_exit_code") not in (None, 0)
    operation_failed = not args.regression and result["status"] in ("waiting_runtime_identity", "waiting_check_failure", "case_process_failed_reconcile")
    if regression_failed or operation_failed or result["status"] == "regression_failed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
