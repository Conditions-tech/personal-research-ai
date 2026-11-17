# Qwen3 continuation — automatic resource recovery

The approved recovery controller and isolated tests are implemented separately from the frozen inference source. The original pilot still has **seven charged requests with complete saved responses and five unattempted cases**. No generation was sent during this continuation's initial live readiness check. No ledger reset, repeated case, extra download or model change occurred. Qwen2.5/conservative v3 remains the app default; Qwen3 remains a programmatic diagnostic. Phase C is incomplete.

## Live check and pending work

On 2026-10-25 local date (the retained raw timestamps are UTC on 2026-10-24), the controller verified Ollama 0.40.6, the exact approved Qwen3 digest/GGUF/thinking capabilities and an empty loaded-model inventory. No active runtime client was observed at the connection check. Three physical-memory samples over ten seconds were **5,321,252,864**, **5,341,806,592** and **5,344,673,792 bytes** (last about **4.98 GiB**). Each was below the unchanged **5,905,580,032-byte / 5.5 GiB** gate. The live state was `waiting_memory`; no inference or unload request was needed/sent and the ledger stayed **7/12**.

Pending cases are `public-0020753`, `holdout-ecology-abbrev`, `holdout-letters`, `holdout-safe-task-instruction` and `qwen3-synthetic-mixed-injection`. They receive no success or correct-missing credit. All four new synthetic robustness cases remain unattempted. The prior seven-result reconciliation, role failures and resource observations remain in the [October 24 report](C2_QWEN3_STATUS_2026-10-24.md); its manual ready-request workflow is superseded by this continuation.

The [recovery controller guide](C2_QWEN3_RECOVERY_2026-10-25.md) documents the tested commands, state, ownership and concurrency boundaries. For the existing supervisor's later idle heartbeat, use `python tools/qwen3_recovery.py --run-approved`: one original uncharged case per invocation, after fresh checks. The controller has no self-respawn or scheduler. Below-gate checks quietly preserve the queue for automatic supervision, without another ready question. No additional automation was created. Do not run a separate manual benchmark, model action or regression job concurrently.

A later `--run-approved` check also returned `waiting_memory`, with samples **5,311,787,008**, **5,312,663,552** and **5,323,309,056 bytes** (last about **4.96 GiB**). No child generation started, no unload control was sent and all five cases remain pending. [Retained latest readiness state](C2_QWEN3_RECOVERY_CHECK_2026-10-25.json).


## Previous runtime identity checkpoint — superseded 2026-10-25

The later live recovery probe then returned `waiting_runtime_identity`: the local 0.40.6 daemon answered `/api/tags` with HTTP 200 and an empty list. Its executable and listener were confirmed, but the process owner was `CodexSandboxOffline`; the approved model store belonged to `Niaz`. The nested 859-byte model-manifest blob hash equaled the pinned digest. The daemon's `OLLAMA_MODELS` environment could not be read, so the account mismatch was a plausible explanation rather than a proven root cause. This checkpoint was superseded by the [runtime repair](C2_QWEN3_RUNTIME_REPAIR_2026-10-25.md).

A targeted stop of the exact idle, empty PID failed with a PowerShell error and a follow-up confirmed the daemon remains running. No alternative termination or replacement daemon was attempted. The ledger remains 7/12; available RAM was 1,679,548,416 bytes, below the unchanged gate. The next safe repair is to launch the existing daemon under Niaz with its current model directory explicit, then require the exact pinned digest in `/api/tags` before any inference.

## Verification and boundaries

**242 tests passed in 37.760 seconds** using `python tools/qwen3_recovery.py --regression` (the child runs `python -m unittest discover -s tests -v`). Twenty-five are recovery tests. Active-file compilation, reviewed differences, source and protected-file hashes are recorded in [continuation verification](C2_QWEN3_CONTINUATION_VERIFY_2026-10-25.json). Tests use isolated files/data and blocked or mocked HTTP; they do not exercise live provider/model failures or use production SQLite. The full suite covers retained C1/C2 review imports/exports and app behavior as well as the new controller.

The controller cannot safely reclaim memory owned by unrelated applications or the OS. No residual project model was loaded, so pretending a forced daemon restart would recover enough RAM is unjustified. Owned child processes, handles and temporary references are released; the remaining resource condition is left for bounded automatic rechecks. Unload-path success is isolated/mocked coverage, not an actual observed recovery of a loaded model. Windows process/TCP checks are momentary observations and do not provide server-side exclusion against arbitrary external clients.

## Runtime identity repair and current gate — 2026-10-25

The same installed Ollama executable now runs under `Niaz` with a child-only model path to the existing store. The sole loopback daemon reports the exact approved Qwen3 digest and `thinking=false` support; no model is loaded or connected. Controller state records the current identity. The repair-time physical-memory samples were 1,316,044,800, 1,307,320,320 and 1,301,250,048 bytes; a subsequent `--run-approved` check sampled 1,110,786,048, 1,130,930,176 and 993,452,032 bytes. Both checks are far below the unchanged 5,905,580,032-byte gate. Status remains `waiting_memory`; the controller sent no inference or unload. Ledger remains 7/12 with five pending. See [runtime repair evidence](C2_QWEN3_RUNTIME_REPAIR_2026-10-25.md).

After a later app/host interruption the supervisor restarted the same daemon (PID 11528). A fresh read-only check confirmed its executable, API version, exact approved model digest and empty loaded-model list. Latest controller memory is 4,430,458,880 bytes (about 4.13 GiB), still below the gate. No inference occurred; the original budget and pending queue are unchanged.

The seven earlier generations establish actual model transport and exact source copying, not reliable field support. Clear dataset/limitation role errors remain. Exact excerpt presence alone does not establish entailment or scientific support; no proposal is auto-accepted. The unchanged RAM gate previously admitted generations whose sampled system availability fell to roughly 0.51 GiB, so passing it is not a general resource-fit guarantee. The remaining frozen outcomes and resource samples must be audited before any quality/default recommendation. Literature synthesis, full-text analysis, scientific validation and the rest of Phase C remain separate.
