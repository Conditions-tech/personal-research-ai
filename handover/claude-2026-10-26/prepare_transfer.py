"""Prepare a source/evidence handover; never launches the app or model runtime."""

from datetime import datetime, timedelta, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tomllib
import zipfile


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = HERE.parent / "Personal_Research_AI_Claude_2026-10-26.zip"
AUTOMATION_ID = "supervise-personal-research-ai-until-usage-limit"


def digest(path):
    with path.open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


def sources():
    paths = [ROOT / name for name in (
        "AGENTS.md", "CLAUDE.md", "README.md", "requirements.txt", ".gitignore",
        "app.py", "app_backup_v01.py", "app_before_search_fix.py",
    )]
    for folder in ("discovery", "review", "tests", "tools", "docs"):
        suffixes = {".md", ".json"} if folder == "docs" else {".py"}
        paths.extend(p for p in (ROOT / folder).rglob("*")
                     if p.is_file() and p.suffix in suffixes)
    for path in paths:
        if path.is_symlink() or not path.resolve().is_relative_to(ROOT):
            raise RuntimeError("Transfer source must stay inside the project.")
    return sorted(set(paths))


def hashes(paths):
    return {p.relative_to(ROOT).as_posix(): digest(p) for p in paths}


def prepare():
    if ARCHIVE.exists() or (HERE / "CONTENTS_AND_VERIFICATION.json").exists():
        raise RuntimeError("Refusing to overwrite an existing dated handover.")
    automation_file = Path(os.environ.get("CODEX_HOME", r"C:\Users\Niaz\.codex")) / "automations" / AUTOMATION_ID / "automation.toml"
    automation = tomllib.loads(automation_file.read_text(encoding="utf-8"))
    if automation.get("status") != "PAUSED":
        raise RuntimeError("Supervision must remain paused for this handover.")
    state_path = ROOT / ".pilot_state/qwen3/state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    if state.get("active_job"):
        raise RuntimeError("A controlled job must be reconciled before preparation.")
    base = sources()
    watched = base + [ROOT / "data/research.db", state_path]
    before = hashes(watched)
    versions = {name: importlib.metadata.version(name)
                for name in ("streamlit", "pandas", "requests")}
    started = datetime.now(timezone.utc)
    log = HERE / "TEST_RESULTS.txt"
    command = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]
    with log.open("xb") as output:
        result = subprocess.run(command, cwd=ROOT, stdout=output,
                                stderr=subprocess.STDOUT,
                                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    finished = datetime.now(timezone.utc)
    after = hashes(watched)
    if before != after:
        raise RuntimeError("A source, evidence, controller or protected file changed during verification.")
    text = log.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"Ran (\d+) tests? in ([0-9.]+)s", text)
    if result.returncode != 0 or not match:
        raise RuntimeError("Tests did not pass; retain the log and resolve before transfer.")
    active = [ROOT / "app.py"]
    for folder in ("discovery", "review", "tests", "tools"):
        active.extend((ROOT / folder).rglob("*.py"))
    for path in active:
        compile(path.read_bytes(), str(path), "exec")
    json_reports = list((ROOT / "docs").glob("*.json"))
    for path in json_reports:
        json.loads(path.read_text(encoding="utf-8"))
    ledger_path = ROOT / "docs/C2_QWEN3_BUDGET_2026-10-21.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    sys.path.insert(0, str(ROOT / "tools"))
    from qwen3_recovery import verified_budget
    verified_budget()  # Pure file/hash checks, no backend construction or I/O.
    snapshot = {
        "kind": "claude-handover-source-snapshot-v1",
        "prepared_local_date": "2026-10-26",
        "client_timezone": "Asia/Dhaka",
        "verified_utc": finished.isoformat(),
        "verified_dhaka": finished.astimezone(timezone(timedelta(hours=6))).isoformat(),
        "original_workspace": str(ROOT),
        "scope": "Handover preparation and isolated offline verification only; implementation and supervision remain stopped.",
        "python": sys.version.split()[0], "interpreter": sys.executable,
        "installed_packages": versions,
        "tests": {"command": "python -m unittest discover -s tests -v",
                  "count": int(match[1]), "reported_seconds": float(match[2]),
                  "elapsed_seconds": round((finished-started).total_seconds(), 3),
                  "exit_code": result.returncode, "log": "TEST_RESULTS.txt",
                  "log_sha256": digest(log),
                  "scope": "Temporary/synthetic isolated tests; no live inference/provider validation."},
        "active_python_compilation": {"count": len(active), "success": True,
                                      "historical_scripts_excluded": True},
        "existing_json_reports_parsed": len(json_reports),
        "watched_files_unchanged": before == after,
        "original_files_sha256": after,
        "production_database": {"included_in_archive": False,
                                "opened_with_sqlite": False,
                                "hash_only": after["data/research.db"],
                                "backup_performed": False},
        "supervision": {"automation_id": AUTOMATION_ID,
                        "status": automation["status"],
                        "resumed_during_preparation": False},
        "saved_controller_state": {k: state.get(k) for k in
                                   ("status", "checked_utc", "charged", "pending", "active_job", "memory_samples")},
        "qwen3_ledger": {"used": ledger["used"], "cap": ledger["cap"],
                         "charged_case_ids": [e["case"] for e in ledger["entries"]],
                         "sha256": digest(ledger_path)},
        "live_runtime_or_memory_rechecked": False,
        "app_or_daemon_started": False, "inference_requests": 0,
        "archive_exclusions": ["data/", "exports/", ".pilot_state/", ".git/",
                               ".env and secrets", "Python environments/caches",
                               "installed runtimes and model weights", "unknown top-level folders"],
        "archive_disclosure": "Includes existing docs/ public/synthetic captured evaluation evidence and dated local path metadata; no production database/export or external upload.",
    }
    (HERE / "CONTENTS_AND_VERIFICATION.json").write_text(
        json.dumps(snapshot, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    package = base + [HERE / name for name in
                      ("HANDOVER.md", "CLAUDE_START_PROMPT.txt", "prepare_transfer.py",
                       "CONTENTS_AND_VERIFICATION.json", "TEST_RESULTS.txt")]
    manifest = HERE / "MANIFEST.sha256"
    manifest.write_text("".join(f"{digest(p)}  {p.relative_to(ROOT).as_posix()}\n"
                                for p in sorted(set(package))), encoding="utf-8")
    package.append(manifest)
    with zipfile.ZipFile(ARCHIVE, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(set(package)):
            archive.write(path, path.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(ARCHIVE) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("Archive CRC check failed.")
        names = archive.namelist()
        for path in set(package):
            if hashlib.sha256(archive.read(path.relative_to(ROOT).as_posix())).hexdigest() != digest(path):
                raise RuntimeError("Archive contents differ from source.")
        if any(n.startswith(("data/", "exports/", ".pilot_state/", ".git/")) for n in names):
            raise RuntimeError("Private/operational files must not be packaged.")
    print(json.dumps({"archive": str(ARCHIVE), "bytes": ARCHIVE.stat().st_size,
                      "files": len(names), "sha256": digest(ARCHIVE),
                      "tests": snapshot["tests"],
                      "compiled": len(active), "all_watched_files_unchanged": True,
                      "supervision": automation["status"]}, indent=2))


if __name__ == "__main__":
    prepare()
