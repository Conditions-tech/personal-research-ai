# Project Status

## Project resumed; Phase C still open — 2026-11-16

Resumed in the original workspace after the Claude handover. Fresh isolated regression: `python -m unittest discover -s tests -q` passed **247 tests in 40.136 seconds**. The frozen Qwen3 ledger verified at **7/12**, with five unattempted cases. Available physical RAM sampled at **2.30 GiB**, below the 5.5 GiB Qwen3 loading gate; no inference was started. The next Phase C task is to validate paper-summary field accuracy and completeness. Bounded discovery remains accepted; synthesis has not started.

## Claude takeover; Crossref server filters and app RAM gate — 2026-10-26

Claude took over from Codex. Read-only audit: all 211 handover manifest hashes matched, production database and pilot state unchanged, 242 tests passed; no Ollama daemon was running and available RAM was about 0.97 GiB. On the user's instruction, Crossref now receives server-side year/type filters and the review UI refuses generation below 4 GiB available RAM. **247 tests passed**; Qwen3 frozen files and ledger (7/12, five pending) are unchanged. See [changelog](CHANGELOG.md). Known handover-archive defect: `tests/fixtures/*.json` were not packaged in the 2026-10-26 ZIP, so an extracted copy cannot pass the full suite; the original workspace is unaffected.

## Runtime identity repaired; memory gate remains — 2026-10-25

The existing Ollama daemon was restarted under `Niaz` with a process-scoped path to the existing model store; current PID 11528 serves the approved Qwen3 name/digest. The model remains unloaded. The latest controller state is `waiting_memory` at about 4.13 GiB versus the unchanged 5.5 GiB gate. No inference/unload request was sent. Ledger remains 7/12; five cases pending. The seven completed outputs now have a non-blinded second-pass usefulness review; no labels or prompts changed. [Runtime repair](C2_QWEN3_RUNTIME_REPAIR_2026-10-25.md), [review addendum](C2_QWEN3_DEVELOPER_REVIEW_ADDENDUM_2026-10-25.md).

Final recovery regression: **242 tests passed in 37.760 seconds**; the 25 recovery tests use isolated state and mocked/blocked model HTTP.

## Current continuation — 2026-10-25

The approved resource controller serializes full regressions and one-case pilot jobs, checks frozen source/ledger identity, preserves unknown charged outcomes and leaves low-memory work resumable for the existing automatic supervisor. No model was loaded during the live check; RAM remained below 5.5 GiB and the ledger remained 7/12. [Current verification and pending work](C2_QWEN3_CONTINUATION_2026-10-25.md).

## Prior resumption checkpoint — 2026-10-24

The interrupted Qwen3 pilot has seven reconciled completed responses, including the charged seventh case; there are **no ambiguous outcomes and five unattempted cases**. Ledger remains 7/12. At that checkpoint RAM was below the unchanged 5.5 GiB load gate, with no new inference sent during reconciliation. Completed outputs matched 21/24 development and 16/18 returned holdout decisions, but clear field-role failures remain despite literal copying. **217 tests passed in 36.577 seconds; 51 active files compiled.** [Current report](C2_QWEN3_STATUS_2026-10-24.md). No source/default change, data/schema change, installation or budget reset was needed.

Earlier approved Qwen3 pilot checkpoint: the additional 4B Q4_K_M model is downloaded; installed digest and nonthinking control metadata are verified. The original first controller stopped before backend use; actual generations subsequently resumed after RAM qualified. See the [live report](C2_QWEN3_LIVE_PILOT_2026-10-21.md) for current counts and outcomes. Qwen2.5/v3 remains the app default; no general quality or app-integration claim is made. **217 tests passed in 35.970 seconds; 51 files compiled.** [Current report](C2_QWEN3_PILOT_2026-10-21.md).

## Current update — 2026-10-21: single-role hypothesis failed; offline integrity improved

The no-download single-role pilot completed **12/12 new local requests**: development matched 4/6 roles with two false fills; fresh holdout matched 2/6 with three wrong-role selections and one false fill. All quotes copied source text exactly, but field-quality acceptance failed. The app default is restored to **`abstract-quotes-v3`**; v4/v5 remain readable and v6 is an unpromoted diagnostic. No further inference or new model was used. [Full current report](C2_SINGLE_ROLE_EVALUATION_2026-10-21.md).

Backend-independent follow-through added a frozen-evidence role audit, archive replay with explicit full/context/unreplayed levels, and the [review guide](ABSTRACT_REVIEW_GUIDE.md). Duplicate JSON keys could silently replace notes; missing required action/root timestamps were also accepted. Both defects were reproduced in isolated tests and fixed without changing the format/schema or valid saved work. The current full suite passed **207 tests in 35.786 seconds**; **47 active files** compiled. [Verification](C2_V6_VERIFY_2026-10-21.json).

Archive audit: 37 proposal occurrences observed, 6 complete-review validations, 27 context-only replays, 4 raw v1 occurrences unreplayed without complete history. Full v1 review fixtures still reopen. Source copying, import validation and test success are not scientific support. Existing production data/schema, historical scripts, old evidence, dependencies and previous ledgers remain unchanged. No new model/runtime/package, cloud inference, Git action or synthesis. Routine offline maintenance approval continues; field relevance, missingness and independent scientific review remain unresolved.

Prior public-prose experiment: v4 tuning 3/24; v5 tuning and holdout each 15/24 with 43 exact source quotes. Its evidence is retained in the [prior report](C2_PUBLIC_ABSTRACT_EVALUATION_2026-10-21.md); the former v5 default has been withdrawn.

## Prior milestone — quote-first v2 verified; completeness partial

That prior follow-up used `abstract-quotes-v2`: field-specific definitions, conservative English quote eligibility, source-preserving selections, abstention and refusal of obvious instruction-like abstracts before inference. Saved v1 proposals retain exact original prompts/options/claims and reopen alongside v2; frozen compatibility fixtures guard this. Reviewer notes, citations, original discovery evidence and all original benchmark files remain intact. No model/runtime/package change was made.

Real evaluation attempted nine original/fresh synthetic cases: seven actual programmatic responses, two deterministic preflight refusals and one further actual UI generation. Nonmissing selections were faithful/field-relevant in these fixtures; 38 of 42 expected programmatic fields matched, with four omissions, and the UI omitted one limitation. Unknown instructions, false-positive refusals, segmentation/English cue limitations and broader scientific reliability remain open. **Quality acceptance is partial; Phase C is incomplete.** See [v2 report](QUOTE_FIRST_C2_2026-10-20.md) and [adjudication](QUOTE_V2_ADJUDICATION_2026-10-20.json).

Final regression: **150 isolated tests passed in 34.427 seconds**, all 27 active Python files compile. Existing production data/schema, historical files, requirements, application/storage/provider code and original benchmark evidence are unchanged. [Verification](QUOTE_V2_VERIFY_2026-10-20.json) records source/fixture stability, compatibility, protected-file hashes, diff and links. Next recommended validation addresses omissions, segmentation and broader independent samples, with retained new protocol versions for changed rules. No silent filling or premature synthesis.

## Prior C2 setup milestone — v1 quality failed

The user approved the concrete setup/benchmark. Ollama 0.40.6 CLI and only Qwen2.5 1.5B Q4_K_M are installed, with the official archive checksum/executable signature verified and loopback/cloud-disabled configuration applied. Six real synthetic generations ran, including temporary review-UI generation, acceptance/rejection and JSON reopening. Model outputs exposed field misassignment and a malicious cure claim: **model-quality acceptance FAILED**. Two malformed outputs were safely refused; quote/number matching does not establish scientific support or instruction resistance. See [real benchmark](LOCAL_ANALYSIS_BENCHMARK_2026-10-20.md), [installation evidence](LOCAL_MODEL_INSTALL_2026-10-20.json) and [adjudication](LOCAL_ANALYSIS_ADJUDICATION_2026-10-20.json).

Observed programmatic latency was 24.727–33.959 seconds; sampled peak aggregate runtime working set was about 1.44 GB. The unchanged 4 GiB pre-load gate was enforced; a bounded wait resolved asynchronous unloading between cases. No user application was closed. The CLI daemon remains available locally; no model remained loaded at the end. No automatic updater/startup registration or extra model was introduced.

Final isolated regression: **137 tests passed in 34.485 seconds**; all 25 active Python files compile. Source/test stability, protected-file hashes, diff and local-link review are recorded in [execution verification](LOCAL_MODEL_EXECUTION_VERIFY_2026-10-20.json). Production data/schema, historical scripts, requirements and existing application/review implementation are unchanged in this setup task. New source is limited to the opt-in benchmark diagnostic and its four guards.

Next proposed task: field-specific, quote-first analysis rules and instruction-handling evaluation, retaining compatibility with saved prompt-version-one proposals. Wait for approval before that task. No additional model download, synthesis or full Phase C completion is authorized/claimed by the benchmark.

## Initial C2 milestone — contracts verified before installation

Reverified the C1 baseline: 105 tests passed in 32.819 seconds. C2 adds strict abstract-analysis proposals under the six approved fields, identity/evidence/model/prompt provenance, separate pending/reviewed AI output, accepted-only comparison columns, version-two JSON support and a conditional loopback Ollama adapter. Reviewer notes, screening, discovery evidence and production storage remain intact. **No usable local backend/model was found: actual AI generation, performance and scientific quality are unverified.** The final isolated suite passed **133 tests in 34.176 seconds**; all 23 active Python files compiled. See [C2 handover](PHASE_C_C2_HANDOVER.md), [verification](PHASE_C_C2_2026-10-20.json) and [concrete setup approval plan](LOCAL_MODEL_SETUP.md).

Next: obtain approval for only the specified free local runtime/model downloads/setup and a small isolated public/synthetic abstract benchmark. No installation, model download, external research transfer, production data/schema change or Git action was performed. Full text, synthesis and the rest of Phase C remain separate and incomplete. The dated statements below preserve previous milestones.

## C1 milestone — Phase C started

Final C1 verification: `python -m unittest discover -s tests -v` passed **105 tests in 33.131 seconds** on a stable source/test snapshot. All 18 active Python files compiled; existing app helper/storage ASTs and protected-file hashes matched the baseline. Production data, historical scripts, requirements and repository instructions were preserved. No installation, Git action or live request was performed. Browser transfer/layout remains unverified.

The user approved moving to Phase C and selected objective, method, dataset, results, limitations and conclusion as the default summary format. C1 implements a session-local review workspace, explicit screening protocol/decisions, abstract evidence notes with exact-excerpt checks, comparison CSV and complete JSON export/reopening. Original discovery runs remain copied and independently traceable; later searches do not change review evidence. No AI model, generated summaries, full text or synthesis is implemented yet. [Phase C plan](PHASE_C_PLAN.md) records the implemented slice and remaining work. Earlier statements that Phase C was unimplemented describe the dated A/B audits below.

Last repository audit: 2026-10-20.

Latest audit: the user's [second Phase A/B re-audit](AB_AUDIT_2_2026-10-20.md) passed **92 tests in 26.534 seconds**, with source fingerprints stable throughout verification. Additional fixes protect optional metadata shapes, nullable author names, abstract positions, record URLs, input validation and actual query/settings attribution in run/history exports. `app.py`, provider request code, production data/schema, historical scripts, requirements and instructions were unchanged in this pass. The [Phase C Handover](PHASE_C_HANDOVER.md) is updated; Phase C remains unimplemented. Earlier audit/milestone counts below are dated evidence.

Latest follow-up: the user requested a full Phase A/B recheck before advancing. See [A/B Audit](AB_AUDIT_2026-10-20.md) for reproduced defects, fixes and verification, and [Phase C Handover](PHASE_C_HANDOVER.md) for the evidence/data contract. This audit changes paper identity selection, NULL enrichment and metadata validation, while preserving schema and production data. The milestone evidence below describes the earlier bounded acceptance; Phase C implementation has not started.

Re-audit result: **80 isolated tests passed in 25.521 seconds**; all 14 active Python files compiled, source fingerprints remained stable during tests, schema initialization was unchanged, local links resolved and protected-file hashes matched. Confirmed defects were fixed and the knowledge handover is prepared for the bounded implementation. Known coverage, browser/concurrency, crash persistence and metadata-depth limits remain explicit in the audit.

## Verified baseline

- The active entry point is root `app.py`; UI and SQLite remain there, with metadata/providers now in the importable `discovery` package.
- It queries OpenAlex and Crossref and persists scholarly metadata and search history in `data/research.db`.
- At the audit, the database existed and contained 25 `papers` rows and 4 `searches` rows. Only schema and counts were inspected; research text was not read.
- `exports/` was empty. The current CSV control downloads data through Streamlit rather than writing into that directory.
- The active app and `app_backup_v01.py` had no syntax errors. `app_before_search_fix.py` had parser errors around its search control flow and is not runnable as written.
- The selected VS Code/Pylance interpreter was `C:\Users\Niaz\AppData\Local\Programs\Python\Python314\python.exe`; no project virtual environment was detected. The only discovered interpreter was this Python 3.14 installation.
- The selected interpreter had Streamlit 1.66.0, pandas 3.0.6, and requests 2.34.2 installed. These are observations, not a supported-version policy.
- No Git repository, external README, dependency manifest, or tests existed at the beginning of the documentation audit. The root README, requirements, and tests now exist; Git remains uninitialized.

## Current phase

**Phase B - bounded Literature Discovery: acceptance complete on 2026-10-20.** The current workspace was inspected before changes: retrieval.py, OpenAlex pages, Crossref cursors, statuses and JSON history settings already existed. The older 39-test/no-pagination description was stale. The [acceptance matrix](PHASE_B_ACCEPTANCE.md) records the implemented scope and remaining limitations; it does not certify exhaustive worldwide literature coverage.

Added independently optional historical year bounds (CE 1-9999 for enabled inputs), native source/page provenance, shared run IDs/settings/counts in version-two existing history notes, latest-session run ZIP and displayed-history JSON exports. Counts distinguish raw, saveable filtered, source/run unique and actual new library insertions. Final-count contradictions stay partial in either direction. Rate limits preserve prior pages and apply sanitized Retry-After session cooldowns, with no automatic retries or budget expansion. The database schema is unchanged.

Newer workspace fixes were preserved and reviewed during verification: reject malformed titles/non-integer or SQLite-overflow years; retain unbounded source integer years; distinguish zero from missing year in new keys; fill NULL metadata without replacing nonempty evidence; and select identical-title papers by record_key. Library CSV now includes that key. Old stored keys are not rewritten. A mixed-version intermediate run failed while files changed; the final 80-test run passed in 26.302 seconds with unchanged source/test hashes across the run.

Baseline: 57 tests passed in 16.658 seconds. Acceptance: 80 isolated tests passed (19 helper/widget, eight adapter, 24 retrieval, 17 UI, five run, two opt-in guards, five backup). Syntax, AST, local-link, diff and protected-file checks passed. All data tests/live storage were temporary; the production database hash is unchanged and its private records/counts were not re-read. Historical scripts, requirements and AGENTS.md were preserved; no packages, paid services or Git operations were used.

[Live evidence](LIVE_PAGINATION_2026-10-20.md) records 17 HTTP 200 responses: real two-page traversal on both sources, historical OpenAlex years 1735/1791, natural empties, exact duplicate replay and export round trips. Three strict Crossref positive-conference-in-window probes failed because those windows contained journal entries; the JSON artifacts preserve those failures. A separate known CVPR DOI returned proceedings-article and passed the real conference filter. This validates metadata classification and traversal, not query recall. No actual outage or 429 was provoked; those paths were tested with mocks.

Known boundaries: 250 raw entries/five requests per source; no hard in-flight cancellation, resumption, shared multi-session limiter or crash-atomic run persistence. Latest-run record ZIP is session-local unless downloaded; history exports show 100 attempts; old notes lack new provenance. Source ranking, dates, classifications and historical/discipline/language coverage remain incomplete. Browser transfer/layout, other runtimes and production migration behavior are not verified. The target remains i3-8100/8 GB/integrated graphics; no AI backend is integrated.

**Next, separately scoped Phase C:** define Literature Review and Paper Analysis screening, evidence-depth, configurable outputs/citations and evaluation contracts before model selection or implementation. None of Phase C was built here. The ten-stage [Mission](MISSION.md) remains active; completing this bounded milestone is not completion of the project.

The following entries retain earlier milestone evidence; their test totals and architecture descriptions refer to those stages.

The approved [controlled live smoke check](LIVE_SMOKE_2026-10-20.md) completed on 2026-10-20: seven public requests, limit five, all HTTP 200, with positive journal/conference examples from both providers and natural empty responses. Nine filtered entries from the initial requests became eight unique temporary records, including one cross-provider duplicate; replay inserted none. Seven offline AppTest runs checked captured-response count/history messages and simulated timeout/empty states. No live outage occurred. The complete isolated suite passed 31 tests. Application, production database, historical scripts, requirements, and test files were unchanged. This is sampled integration evidence; exhaustive retrieval, corpus coverage, and independent total accuracy remain unverified. The next proposed task is pagination/count-status design for approval, without implementation yet.

The active priority is to finish and verify Literature Discovery as the foundation of Personal Research AI. Paper Analyst, Research Strategist, and multi-model orchestration remain future work. UI/storage are still in one script; the new discovery boundary is reusable. Maintenance and mocked tests alone do not establish research coverage.

The approved provider-category correction now defaults to journal papers (articles and reviews together) and conference papers. It maps each provider's native metadata, uses explicit OpenAlex venue evidence for article/review records, preserves unclassified records only when categories are cleared, and labels OpenAlex totals as candidates before local filtering. Raw stored types, schema, persistence, selected limits, and year controls are unchanged; no pagination was added. The earlier exact-label assumptions in shared-filter mocks were invalid and have been replaced.

Verification on Python 3.14.7: 17 focused helper/widget tests and 9 isolated AppTest tests passed; `python -m unittest discover -s tests -v` passed all 31 tests including the 5 backup tests. Syntax checks and all 16 local documentation link targets passed. AST comparison confirmed schema initialization, persistence, DOI keys, HTTP handling, Crossref request construction, and the shared local filter were unchanged. Protected-file hashes confirmed the production database, historical scripts, and requirements were unchanged. Tests use mocks and temporary data; live provider behaviour and research coverage remain unverified.

Phase 1 handover and safe stabilization established root instructions, setup/dependency guidance, ignore rules, isolated tests, saved-record/CSV helpers, and connection cleanup. The subsequently approved search-filter task applies inclusive years and normalized publication types to both providers while retaining OpenAlex's server filters and each provider's selected request limit. Crossref uses an explicit conservative type map; there is no pagination or schema change.

The 2026-10-20 task recheck found the shared-filter implementation and nine tests already present, rather than the supplied five-test baseline. The README also still claimed Crossref was unfiltered in its troubleshooting section. The review corrected that documentation, removed unsupported Crossref `article`/`review` aliases, replaced synthetic provider labels in fixtures with verified types, and expanded boundary and request coverage. The nested `python/Amazon/personal ai/` directory is empty; the root remains the active project.

The filtering recheck executed `python -m unittest discover -s tests -v`: all 15 tests passed on Python 3.14.7. In-memory syntax checks passed for the active app, tests, and `app_backup_v01.py`. A separate read-only count check confirmed 25 papers and 4 searches; SHA-256 checks confirmed the database and both historical scripts were unchanged. See [Testing](TESTING.md) for verification details and remaining gaps. No packages were installed and Git was not initialized.

The approved follow-up replaced the fixed 2026 publication end-year default with the app host's current local calendar year. At that step, the complete suite passed 16 tests, including a mocked year-rollover test of the actual widget assignment; active-app/test syntax checks passed. The start-year default and 1900â€“2100 bounds are unchanged. Full Streamlit rendering remains untested.

The backup/restore follow-up replaced the untested documentation snippet with a directly tested procedure that validates the source, refuses overwrite, and verifies the copied database. Five new temporary-data tests cover backup, staged replacement, rollback, and refusal cases; the complete suite passed 21 tests on Python 3.14.7. In-memory syntax checks passed for the app and both test files. The production database was neither backed up nor restored, and protected-file hashes confirmed the application, database, historical scripts, and requirements were unchanged.

The subsequent documentation task established the [Schema Migration Policy](SCHEMA_MIGRATIONS.md). It defines future `user_version` adoption, recognition of existing schemas, compatibility requirements, staged transactional upgrades, approval, and recovery. No version was assigned and no runner or startup guard was implemented; those remain future implementation work. The production database's current version metadata was not inspected for this task.

For that documentation-only change, `python -m unittest discover -s tests -v` passed all 21 existing tests on Python 3.14.7, and local documentation link targets were checked. Protected-file hashes confirm the application, production database, historical scripts, tests, and requirements are unchanged. This verifies the existing suite, not future migration behavior.

The approved UI smoke-test task added `tests/test_ui.py` using the already installed Streamlit 1.66.0 `AppTest` utility. Seven new tests execute unchanged temporary app copies with guarded SQLite paths and mocked HTTP sessions. They cover startup, input validation, searches/filters/counts, saved literature/history/deduplication, metadata selection, CSV payloads, and provider timeout/empty states. The focused command passed seven tests and `python -m unittest discover -s tests -v` passed all 28 tests on Python 3.14.7. Syntax and local documentation link checks passed. Protected-file hashes confirm the application, production database, historical scripts, existing tests, and requirements are unchanged.

Headless UI behavior now has automated coverage. Browser visual layout, actual download transfer, live provider integration, and concurrent users remain untested. AppTest setup emits bare-mode context warnings, and the current app emits `use_container_width` deprecation warnings. Those compatibility changes were not implemented in this task.

## Open risks

- Provider coverage/ranking/classification remain incomplete. A provider total is not a count of screened, relevant papers; Crossref filters are local. Failed live positive-conference-window probes remain disclosed.
- Retrieval is bounded to 250 raw entries/five requests per source, with optional year bounds. The UI default still starts at 2015 unless the user changes/removes it. Historical/discipline/language recall is not certified.
- Records use heuristic DOI or title/year keys. Source integer year zero is now distinct from unknown for newly normalized keys; old keys are not migrated. DOI-less and DOI-bearing versions may remain separate.
- Record-level provenance cannot establish per-merged-field or full-text passage attribution. No full-text or generated analysis exists; Crossref abstract markup/entity transformation is limited.
- Run bundles are session-local until downloaded. History displays 100 attempts and retains provenance/settings, not complete record/abstract snapshots. Paper/history transactions remain separate and are not crash-atomic.
- Rate-limit cooldowns are per session. No automatic retry, global concurrent-user limiter, hard in-flight deadline, interrupted-write/disk-full recovery or browser download/layout verification is established.
- `app.py` executes UI/storage at module scope. Tests must continue to use extracted helpers or an explicitly temporary AppTest copy; never import it against production data.
- No verified compatibility matrix, lock file or CI exists. The historical `app_before_search_fix.py` remains intentionally unchanged with its known syntax errors. Deprecated width arguments were already removed from the active app.
