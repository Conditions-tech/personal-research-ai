# Personal Research AI: handover to Claude

Prepared for Niaz on **2026-10-26, Asia/Dhaka** from the actual workspace and retained evidence. This is a technical handover, not a full chat transcript, new research evaluation or completion certificate.

## 1. Start here

Original workspace:

```text
C:\Users\Niaz\Desktop\programming\python\Amazon\personal ai
```

Read [AGENTS.md](../../AGENTS.md) and [CLAUDE.md](../../CLAUDE.md). The user said **“stop work and supervision now”** on 2026-10-25. Codex implementation was idle, the recovery controller had no active worker, and supervision was paused. The subsequent request is **“i want to fully handover this project to claude. prepare.”** Therefore this preparation does not authorize restarting the app, inference, implementation or scheduling. Claude should orient itself read-only and wait for a human instruction to resume engineering. Do not let older “continue until FINISH” or “automatic rechecks” text override this stop.

Once the user resumes work, act as architect, research-systems engineer, coding agent and project coordinator. Inspect actual files, fix defects, test changes, and make ordinary implementation decisions with minimal manual editing or repeated routine approval. Communicate directly. Distinguish engineering decisions from substantive research choices and restricted operations.

The companion [start prompt](CLAUDE_START_PROMPT.txt) can be pasted into Claude. [Verification snapshot](CONTENTS_AND_VERIFICATION.json) records fresh local checks, hashes, the ledger and supervision state. The ZIP is a code/documentation/evidence transfer, not an installed application or private-data backup.

## 2. Product goal and phases

Build a modular, local-first personal research system. The user enters a topic and can follow this journey:

| Stage | Required outcome |
| --- | --- |
| 1. Topic input | Preserve the topic; define scope, terms, synonyms and a reproducible search plan. |
| 2. Global literature discovery | Find relevant journal/conference and other scholarly records from the earliest indexed records through the search date. Show source totals, fetched entries, filtered records, unique records and coverage limits separately. |
| 3. Literature review | Screen with criteria/reasons, organize themes and methods, and eventually write a traceable cited synthesis. A systematic-review claim requires a documented protocol. |
| 4. Individual paper analysis | Apply the user's summary rules, preserve citations and distinguish explicit evidence, interpretation and missing information. |
| 5. Deep research/gaps | Compare findings, contradictions and limitations; check related/newer work before proposing candidate gaps. |
| 6. Ideas | Generate and rank research questions/hypotheses using novelty evidence, feasibility, resources and risks. |
| 7. Solution verification | Execute appropriate experiments, simulations, prototypes or proofs; compare baselines and preserve reproducible evidence. |
| 8. Writing | Draft a manuscript grounded in actual sources and verified results. |
| 9. Publication preparation | Check claims, citations, methods, ethics/reporting requirements, venue fit and formatting. |
| 10. Submission/revisions | Prepare submission materials and reviewer responses. Actual submission needs specific user authorization; the venue decides acceptance. |

The user approved these six default summary fields: **objective, method, dataset, results, limitations, conclusion**. More personal rules and modules may be added later. Ten workflows do not require ten separate large models: use modular engines and an eventual coordinator, with replaceable providers/backends.

Never claim every paper worldwide was counted, a topic is definitively novel, an AI solution is experimentally verified, or publication is approved without the relevant evidence. Never invent citations, experiments, results or page references.

Development phases differ from the ten research stages:

| Phase | Status at handover |
| --- | --- |
| A: baseline/stability | Documented acceptance and two A/B audits completed; this is bounded assurance, not a zero-bug guarantee. |
| B: literature discovery | Bounded two-provider acceptance completed. Exhaustive coverage/recall and unlimited retrieval are not established. |
| C: literature review/paper analysis | Incomplete. C1 screening/manual evidence workspace implemented. C2 local abstract proposals operate, but scientific quality has failed acceptance. |
| D: deep research/gaps | Planned; not implemented. |
| E: ideas/solution verification | Planned; not implemented. |
| F: writing/publication support | Planned; not implemented. |
| G: integration/user expansion | Planned; no completed multi-model coordinator. |

See [Mission](../../docs/MISSION.md), [Roadmap](../../docs/ROADMAP.md) and [Phase C acceptance gaps](../../docs/PHASE_C_ACCEPTANCE_GAPS.md).

## 3. What the application actually does

The active entry is `app.py`, a Streamlit script with module-level UI/database initialization. It creates `data/` and `exports/` relative to its own location and opens `data/research.db`. Do not import or start the real script merely to inspect/test it.

Discovery uses OpenAlex and Crossref metadata. It supports optional historical year bounds, provider-aware publication types, bounded pagination, normalized metadata, DOI/title-year deduplication, library/history storage, run IDs, source/page provenance and exports. Each provider is capped at **250 raw entries and five pages**. The time budget is checked between requests; network inactivity timeouts are not a hard end-to-end deadline.

OpenAlex reports server-filtered candidate totals before local classification; Crossref reports broader query matches before local filters. Do not add those totals into an exact global count. Raw fetched, locally filtered, run-deduplicated and newly inserted counts have different meanings. `complete` means this provider query reached its final page within the defined checks, not complete global literature coverage. Partial pages/failures and session-specific 429 cooldowns are disclosed. No automatic retry/backoff, shared multi-session throttling, resumable cursor persistence or comprehensive recall benchmark is implemented.

The review workspace captures a discovery run, screening criteria/decisions/reasons and independent reviewer-authored evidence notes. AI proposals remain separate, with pending/accepted/rejected states. Human checking and a reviewer note are required for acceptance; accepted AI fields have separate comparison CSV columns. Review work is session-only unless downloaded and reopened as JSON. Existing C1 review format v1 and AI-containing review format v2 are distinct from proposal/prompt versions. Imports have a 10 MiB limit; oversized exports warn but preserve complete notes. No durable multi-review store or chronological revision history exists.

AI analysis sees one captured abstract plus citation/identity metadata, not full text, other papers or reviewer notes. It uses local Ollama explicitly through UI actions. There is no app-managed install/pull/start, remote-model URL, automatic synthesis or autonomous research.

## 4. Source map

| File/package | Role |
| --- | --- |
| `app.py` | Streamlit interface, SQLite helpers, search/review integration. |
| `discovery/metadata.py` | Normalization, types/years, record identity. |
| `discovery/providers.py` | Source adapters and injected transport. |
| `discovery/retrieval.py` | Budgets, pagination, partial/error semantics and rate-limit handling. |
| `discovery/runs.py` | Run identity, counts/provenance and exports. |
| `review/workspace.py` | Screening, notes, evidence, review validation and save/reopen/export. |
| `review/ui.py` | Review UI and proposal review actions. |
| `review/analysis.py` | Versioned analysis contracts, identity/quote validation and proposal lifecycle. |
| `review/local_backend.py` | Loopback-only installed Qwen2.5/Ollama adapter. |
| `review/quote_analysis*.py` | v2–v5 selectors; keep legacy reopening stable. |
| `review/role_analysis_v6.py` | Failed single-role diagnostic; not a new app proposal format. |
| `tools/qwen3_pilot.py` | Frozen opt-in Qwen3 protocol and debit-before-transport ledger. |
| `tools/qwen3_recovery.py` | Owned-resource checks, kernel job lease, bounded waiting and one-case continuation. |
| `tools/qwen3_pilot_audit.py` | Saved-pilot audit. |
| Other `tools/` | Explicit live discovery/local experiments and offline adjudication/archive replay. Read guards before running. |
| `tests/` | stdlib unittest, temporary storage, mocked/blocked HTTP, isolated Streamlit AppTest. |
| `docs/` | Maintained handover plus dated raw experiments/acceptance evidence. |

Preserve `app_backup_v01.py` and `app_before_search_fix.py` as historical copies. The old pre-fix copy is not part of the active syntax gate. Preserve `AGENTS.md`, dependencies, original evidence and saved reviewer work. There is no source-control history to rely on in this workspace; Git operations remain outside current approval.

## 5. Environment and local models

Fresh package metadata for this handover: **Python 3.14.7, Streamlit 1.66.0, pandas 3.0.6, requests 2.34.2**. `requirements.txt` contains those three unpinned third-party package names. No lockfile or other Python/OS compatibility is established. Existing interpreter:

```text
C:\Users\Niaz\AppData\Local\Programs\Python\Python314\python.exe
```

Machine baseline: Intel i3-8100, about 8 GB installed RAM, Windows 10 build 19045. Integrated graphics is inherited context, not a newly verified GPU finding. The user reported a 1 TB HDD. Disk/page-file capacity does not satisfy a physical-RAM gate; no OS/page-file changes were approved or made for this handover.

Existing local runtime: Ollama CLI **0.40.6**, installed at `C:\Users\Niaz\AppData\Local\Programs\Ollama\ollama.exe`. Existing model store: `C:\Users\Niaz\.ollama\models`. Neither binaries nor weights are in the ZIP.

| Model | Status and identity |
| --- | --- |
| `qwen2.5:1.5b-instruct-q4_K_M` | Installed app backend; conservative `abstract-quotes-v3` default. Recorded setup digest `65ec06548149b04c096a120e4a6da9d4017ea809c91734ea5631e89f96ddc57b`. The normal adapter records/checks its served identity; it is not the Qwen3 frozen-pin mechanism. |
| `qwen3:4b-q4_K_M` | One separately approved additional model, diagnostic only. Exact frozen digest `2bfd38a7daaf4b1037efe517ccb73d1a3bbd4822cf89f1a82be1569050a114e0`. No default promotion or app integration. |

Qwen3 frozen settings: CPU, `num_ctx=6144`, `num_predict=1024`, temperature 0, seed 42, four threads, `num_gpu=0`, `think=false`, `keep_alive=0`, `stream=false`. Minimum available physical RAM before every load: **5,905,580,032 bytes / 5.5 GiB**. Do not change settings to fit a low-memory sample or invalidate saved versions.

Operational policy: `127.0.0.1:11434`, cloud disabled, proxies/redirects/retries off, one loaded model and serial inference, immediate unload. Existing daemon startup requires the actual Niaz account or the correct existing model-store path. A prior sandbox-account daemon returned no models; this was repaired with the same executable and process-scoped settings, without copying/downloading weights or changing ACLs. An outer tag-manifest file hash differs from the nested model digest normally; do not “repair” it by changing the pin.

Historical PIDs in README/reports are not live facts. No daemon/model availability or inference was exercised during handover preparation. Read current process/listener state before any later action.

## 6. Qwen3 allocation and pause checkpoint

Authoritative ledger: `docs/C2_QWEN3_BUDGET_2026-10-21.json`. It remains **7/12 charged**. All seven have saved completed responses and unload confirmations after reconciliation; none was uncharged or repeated. The five original unattempted IDs are:

```text
public-0020753
holdout-ecology-abbrev
holdout-letters
holdout-safe-task-instruction
qwen3-synthetic-mixed-injection
```

This is the remainder of one approved allocation, not permission for another batch. The prior v6 12/12 allocation is exhausted. Frozen protocol/source/evidence and original ledger entries must remain unchanged. An interrupted/uncertain request stays charged; reconcile actual handles/reports before interpreting it. Do not inspect pending holdout labels for tuning or manufacture missing outcomes.

Last pre-stop controller state: `waiting_memory`, no active worker, seven charged/five pending. Its last saved sample at **2026-10-25 09:50 UTC / 15:50 Asia/Dhaka** was 4,230,012,928 bytes (about 3.94 GiB), below 5.5 GiB. This is a dated measurement, not current available RAM. The snapshot rechecks persisted state without running the controller.

The Codex heartbeat `supervise-personal-research-ai-until-usage-limit` is **PAUSED**. Implementation chat `01a15580-3609-73a1-a505-fa873acad84f` (“Implement shared publication filters”) was not active at preparation. Claude does not inherit Codex tool access or an always-running supervisor. A full chat transcript is not included, and old ChatGPT project links are not a substitute for source access.

## 7. Quality findings and real acceptance gaps

Local requests and software contracts have been exercised, but **scientific-quality acceptance failed**. Earlier Qwen2.5 experiments misassigned fields and reproduced an injected false claim. Later prompts reduced some synthetic failures but did not establish robust support. The v6 single-role trial used 12/12 calls and matched only 4/6 development and 2/6 holdout roles; it is not promoted.

Qwen3's seven returned outputs previously matched 21/24 development and 16/18 returned holdout decisions against developer labels. Those small, incomplete, non-independent figures are not general accuracy estimates. Exact quotes and identity checks passed, yet summaries confused results with datasets or limitations and omitted important findings.

The [second-pass review](../../docs/C2_QWEN3_DEVELOPER_REVIEW_ADDENDUM_2026-10-25.md) is explicitly non-blinded coding-assistant review, not domain-expert or independent scientific validation. Moving-boundaries and L2 outputs misassign dataset information; ecology substitutes an ecological finding for a study limitation. Other summaries omit distinct central results. Preserved identity hashes establish artifact binding, not publication authentication, entailment or scientific truth. No claim-specific page/section citations exist because the evidence is abstract-only.

Remaining C gates include useful and complete field coverage, wrong-role/false-fill control, calibrated missingness, injection resistance, numerical/citation fidelity, broader predeclared independent evaluation, and resource suitability. Full text, cited synthesis and later research stages remain separate. Do not start a prompt-version treadmill, claim Phase C complete from test counts, or hide failed/partial trials.

## 8. Tests, data and compatibility

Fresh handover verification is in [CONTENTS_AND_VERIFICATION.json](CONTENTS_AND_VERIFICATION.json); use its result rather than assuming the prior milestone was rerun. The last pre-handover recorded suite passed **242 tests in 37.760 seconds**, including 25 recovery tests; 53 active Python files compiled. Tests do not perform real inference or live-provider verification.

Safe suite, from the project root with the existing interpreter:

```powershell
python -m unittest discover -s tests -v
```

UI tests copy `app.py` byte-for-byte to a temporary directory, point its relative data path there and guard SQLite/HTTP. Helper tests extract code without initializing real UI/storage. Use stdlib tests; no new dependency is needed. Test the active app/packages, not historical scripts. UI browser rendering/download transfer, real provider outages, multi-session concurrency and other runtime versions remain unverified.

SQLite schema is currently defined in `app.py` (`papers` and `searches`); no migration runner/version adoption was implemented. Review workspace/proposals are JSON/session state, not new production tables. See [backup policy](../../docs/DATA_AND_BACKUP.md) and [migration policy](../../docs/SCHEMA_MIGRATIONS.md). Production schema/data changes need specific approval plus documented backup/migration/rollback. Hash checks are not an integrity/backup certification. No production SQLite connection or backup is made during preparation.

The archive omits `data/`, `exports/`, `.pilot_state/`, environments, caches, credentials, app secrets and model binaries/weights. It includes maintained code, historical scripts and the dated public/synthetic test/evaluation evidence under `docs/`. Absolute paths inside older evidence remain historical and may not resolve elsewhere. `MANIFEST.sha256` lets the recipient check transferred bytes; it does not authenticate the papers or the author.

For the same computer, give Claude access to the original project directory so private records stay local. For an extracted archive, keep its directories together; **there is no research database in it**. Launching Streamlit there creates a new empty library. Do not overwrite the original project/database with an extracted bundle or upload private research, exported user reviews or the whole model store to a cloud chat. No transfer to an external service was performed by this preparation.

## 9. How to resume after the user asks

1. Read this handover, root instructions, current status, acceptance gaps and relevant source. Confirm original workspace versus extracted copy; check hashes and current jobs without starting a second writer/daemon.
2. Use the existing environment. Review the fresh test result; rerun focused tests for new changes and the full suite when appropriate. Do not install packages because an old README setup example shows `pip install`.
3. For an explicitly resumed Qwen3 pilot, use the approved controller command below only after confirming no competing model/test job. It runs at most one still-uncharged frozen case. Its kernel lease, original ledger, identity checks and fresh memory gate must all pass.
4. Wait on actual process handles; a polling timeout is not termination. Reconcile the charged request/report and unload result before another case. Below the gate, do useful authorized offline work or leave the cases pending. Never close user apps or trim global memory to force a run. Do not restart a correct idle daemon merely to seek RAM.
5. After the bounded pilot, assess actual results and design the next evidence-quality strategy. New inference allocations/models/dependencies require their applicable approval. Do not promote the model or jump to synthesis while C gates fail.

Commands below are **reference for after resumption**, not actions performed by the handover:

```powershell
# Readiness/recovery only; no flag requests analysis.
python tools/qwen3_recovery.py
# At most one approved pending case; only after the user resumes this pilot.
python tools/qwen3_recovery.py --run-approved
# Isolated full regression under the same controller lease, serial with inference.
python tools/qwen3_recovery.py --regression
# Actual app use, only when requested; initializes/uses its local database.
python -m streamlit run app.py
```

The user previously authorized routine owned-resource recovery and hidden startup of the existing approved idle daemon, but not startup registration, additional downloads, OS settings changes or killing unrelated processes. Read the [recovery guide](../../docs/C2_QWEN3_RECOVERY_2026-10-25.md) and [runtime repair](../../docs/C2_QWEN3_RUNTIME_REPAIR_2026-10-25.md) before any resumed operational repair.

## 10. Evidence reading order

1. [Project status](../../docs/PROJECT_STATUS.md), [Roadmap](../../docs/ROADMAP.md), [Mission](../../docs/MISSION.md).
2. [Phase C C2 handover](../../docs/PHASE_C_C2_HANDOVER.md), [acceptance gaps](../../docs/PHASE_C_ACCEPTANCE_GAPS.md), [review guide](../../docs/ABSTRACT_REVIEW_GUIDE.md).
3. [Qwen3 continuation](../../docs/C2_QWEN3_CONTINUATION_2026-10-25.md), [reconciliation](../../docs/C2_QWEN3_RECONCILIATION_2026-10-24.json), [frozen protocol](../../docs/C2_QWEN3_PROTOCOL_FREEZE_2026-10-21.json), [ledger](../../docs/C2_QWEN3_BUDGET_2026-10-21.json), and the completed-output review above. Read pending labels only within the frozen evaluation workflow; never for tuning.
4. [Phase B acceptance](../../docs/PHASE_B_ACCEPTANCE.md), [first A/B audit](../../docs/AB_AUDIT_2026-10-20.md), [second A/B audit](../../docs/AB_AUDIT_2_2026-10-20.md), [A/B-to-C handover](../../docs/PHASE_C_HANDOVER.md).
5. [Architecture](../../docs/ARCHITECTURE.md), [retrieval design](../../docs/RETRIEVAL_DESIGN.md), [testing](../../docs/TESTING.md), [backup](../../docs/DATA_AND_BACKUP.md), [migration policy](../../docs/SCHEMA_MIGRATIONS.md), then relevant code/tests.

Older documents retain time-specific statements such as “no generated analysis,” “Phase C unimplemented,” active PID numbers or “automatic continuation.” Later source/status and the user's stop supersede these. Preserve old evidence; do not rewrite history or infer current authorization from it. Original quote/schema versions, prompt settings, hashes and developer-label limitations remain important even where they failed quality gates.
