# Qwen3 resource recovery and automatic continuation

The approved continuation adds `tools/qwen3_recovery.py` around the frozen pilot. It does not change the model, context, quantization, prompts, validation, generation timeout or **5,905,580,032-byte (5.5 GiB)** physical-RAM gate. The existing ledger remains authoritative: the original seven entries are pinned, only the five previously unattempted case IDs can follow them, and the cap remains twelve. The frozen helper still charges before transport; failures and unknown outcomes stay charged.

## Running and supervision

Run these commands sequentially from the project root with the existing selected Python interpreter:

```powershell
python tools/qwen3_recovery.py --regression
python tools/qwen3_recovery.py
python tools/qwen3_recovery.py --run-approved
```

`--regression` runs the full isolated suite under the same OS job lease as the controller. No flag performs readiness/recovery checks without analysis. `--run-approved` runs **at most one** original uncharged frozen case in a separate child process. The frozen child independently rechecks resources, model identity and request settings immediately before charging. Release the child process and its file handles before the next invocation. Test jobs and generation jobs must use this controller serially; unrelated/manual invocations do not participate in its lease.

State and owned logs are in `.pilot_state/qwen3/`; uniquely named raw case reports are in `docs/C2_QWEN3_RESUME_*_RESULT.json`. Never delete the job lock to bypass a busy job. The OS lock, not the existence of the filename, determines whether it is held. Do not edit/reset state or the ledger to repeat a charged case.

The existing external supervisor's five-minute heartbeat may invoke a later bounded check when this worker is idle. No new scheduler, startup registration, background self-respawn or repeated ready prompt is added here. Each low-memory invocation samples at most three times, five seconds apart, and leaves `waiting_memory` with the pending queue intact. Temporary low memory is a waiting state for automatic supervision. It is not permission to bypass the gate or an instruction for the user to coordinate another ready reply.

## What recovery can safely do

- Collect controller-owned temporary Python objects and close owned HTTP/log/process handles. One case per child avoids retaining earlier review copies and response trees in the next generation process.
- Recheck the pinned runtime/model metadata, loaded-model inventory and physical RAM. Before/after availability is observational; an increase is not proof that this code freed that memory.
- Unload a residual **owned, completed** Qwen3 model with the documented empty request `{"model":"qwen3:4b-q4_K_M","keep_alive":0}`. This is a separate control path with no prompt, schema or inference settings, and no ledger debit. Verify `/api/ps` becomes empty using bounded checks.
- Refuse unload if ownership/completion is unknown, another model is loaded or an IPv4 connection to the pinned runtime port is active. A dead/timed-out client does not prove server-side generation finished; a saved completed wire response is needed for ownership recovery.

The empty unload control follows [Ollama's FAQ](https://docs.ollama.com/faq#how-do-i-keep-a-model-loaded-in-memory-or-make-it-unload-immediately), [generate API](https://docs.ollama.com/api/generate) and [running-model inventory](https://docs.ollama.com/api/ps), checked against official documentation during implementation. No residual owned model was assumed merely because the daemon existed.

The controller does **not** restart the daemon: the observed idle daemon was already small, so a restart had no demonstrated benefit. It never kills processes, closes other applications, changes OS/page-file settings, clears global caches, installs/downloads anything or changes app routing. Much of system RAM may belong to unrelated applications or the OS and is outside this recovery scope.

## Interruption and concurrency limits

The active job is recorded before launch, then bound to its PID and Windows creation token. The parent retains and waits on the actual child handle. A tool timeout does not imply exit. A later invocation with a live/reused/absent PID distinguishes liveness from success; an unknown launch or inaccessible process remains `waiting_worker_reconciliation`. A charged case with a missing or failed report is skipped, never retried or uncharged. Its scientific result still needs explicit reconciliation.

The lease covers cooperating project tools only. A momentary TCP check and `/api/ps` cannot provide server-side exclusion against an unrelated client racing immediately afterward, nor authenticate who loaded a model. Keep the app's model actions and unrelated Ollama clients idle during this bounded pilot. If ownership or idleness is uncertain, the controller leaves the model alone. Windows PID/TCP inspection is platform-specific; other operating systems have not been verified.

Recovery controls do not establish model quality or make low-memory inference safe on arbitrary hardware. Earlier samples fell to about 0.51 GiB during generation despite passing the pre-load gate. Keep that observed headroom limitation visible when evaluating whether Qwen3 fits this machine. Exact quote matching still proves source presence only, not field relevance, entailment, authorship or scientific support. No app-default promotion or Phase C completion follows from this controller.

## Verification scope

`tests/test_qwen3_recovery.py` adds twenty-five isolated tests with temporary state, mocked runtime/memory/worker responses and blocked provider/model HTTP and SQLite. They exercise bounded low-memory waiting/resume, recovery-only defaults, ownership/client checks, verified unload and failures, active/unknown/exited/reused workers, one-child serialization, interrupted waits, spawn/metadata failures, queue/budget preservation, original-entry/frozen-source tampering, corrupt-state preservation, allocation exhaustion, precise runtime identity failure reporting and clearing stale runtime details. A real small subprocess verifies OS lease exclusion; it performs no inference. Regression mode and failure reporting are also checked without runtime calls.

The initial empty-inventory blocker was repaired outside the controller by restarting the same installed Ollama executable under `Niaz` with a process-scoped model-store path. Current PID 11528 lists the exact approved digest, and `/api/ps` is empty. Current status is `waiting_memory`; the latest controller sample is about 4.13 GiB, below the original gate. The controller itself never restarts the daemon. See [runtime repair evidence](C2_QWEN3_RUNTIME_REPAIR_2026-10-25.md). A regression run preserves runtime state because it does not recheck Ollama.

Live execution results, actual suite duration, protected-file hashes and remaining cases are recorded in the dated continuation verification. A mocked unload success does not claim an actual live unload was needed or executed.
