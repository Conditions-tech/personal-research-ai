# Testing

## Runtime identity diagnostic — 2026-10-25

The recovery suite now contains **25 focused tests**; the final full suite is recorded in [continuation verification](C2_QWEN3_CONTINUATION_VERIFY_2026-10-25.json). Tests verify fresh runtime identity, useful endpoint/status error reporting and removal of stale identities while preserving blocked diagnostics through an offline regression. No tests call model generation or use production SQLite. The prior empty-inventory diagnosis was superseded by the [runtime repair](C2_QWEN3_RUNTIME_REPAIR_2026-10-25.md).

The live repair metadata check verified one loopback listener, the exact pinned Qwen3 digest, GGUF/Q4_K_M identity, `thinking=false` support, no connected client and an empty loaded-model list. A fresh `--run-approved` check then stopped at `waiting_memory` after three below-gate samples. No generation, unload, search or database access occurred. This is an operational metadata check, not an inference-quality test.

Final recovery regression: **242 tests passed in 37.760 seconds**; the 25 recovery tests use isolated state and mocked/blocked model HTTP.

## Resource-controller verification — 2026-10-25

Twenty-two isolated controller tests add bounded memory recovery/resume, OS lease exclusion, owned unload checks, failure/interruption handling, immutable charged attempts and corrupt-state preservation. Full-suite results and protected-file checks are in [continuation verification](C2_QWEN3_CONTINUATION_VERIFY_2026-10-25.json). Use `python tools/qwen3_recovery.py --regression` to serialize regressions with bounded pilot jobs. The live readiness check sent no generation or unload; successful unload and failure handling are mocked, not live-tested. [Commands, actual coverage and limitations](C2_QWEN3_RECOVERY_2026-10-25.md).

## Qwen3 reconciliation checkpoint — 2026-10-24

Fresh `python -m unittest discover -s tests -v`: **217 passed in 36.577 seconds**; all **51 active Python files** compiled. The seven charged actual responses reconstruct with original snapshots, model identity, frozen requests/fields and recorded unload checks; no charged request is unknown or repeated. Development replay is identical. Current RAM blocked further loading; zero new inference was sent during this audit. Five unattempted cases remain outside success/missingness counts, including all four new synthetic robustness cases. These are not independent scientific labels or live failure/injection-resistance tests. [Current report](C2_QWEN3_STATUS_2026-10-24.md).

## Qwen3 pilot preparation — 2026-10-21

`python -m unittest discover -s tests -v` passed **217 tests in 35.970 seconds** on stable source/fixtures; all **51 active Python files** compiled. Ten new isolated Qwen3 pilot/audit tests passed in 0.042 seconds, covering pinned model/capabilities, independent settings, unchanged RAM gate, opt-in/new reports, duplicate metering, failure retention, first-case selection, reconstruction and missingness counters. An intermediate full run passed 216 tests in 37.011 seconds.

The separately approved model download and read-only metadata checks are real. The first live controller stopped **before backend use** at the 5.5 GiB gate; no Qwen3 generation, latency, sampled inference memory, field accuracy or model injection resistance is verified. The ledger is **0/12**. All twelve frozen cases build offline and the synthetic directive is quarantined. Historical tests/evidence below remain dated milestones, not a Qwen3 integration claim. [Current report](C2_QWEN3_PILOT_2026-10-21.md).

## Single-role pilot and import integrity — 2026-10-21

Intermediate regression after restoring v3 default: **195 tests in 35.544 seconds**. Final `python -m unittest discover -s tests -v` passed **207 tests in 35.786 seconds**; all **47 active Python files** compiled on a stable source/fixture snapshot. New tests cover one-role independent full-safe-context requests, exact source/role/identity/type/fragment/quarantine limits, no auto-fill, conservative default, mixed v1–v5 reopening, memory-before-backend and failure preservation, opt-in/report protection, support versus valid alternatives/false fills/omissions, and archive scope/tamper rejection. V6 is diagnostic only; `generate_analysis` rejects its unsupported app protocol and normal review import rejects its artifact shape.

Isolated acceptance-gap checks reproduced duplicate-key note replacement and missing required action/root times. The five new `test_review_integrity.py` methods initially produced **8 failing assertions**; all five pass after strict JSON/timestamp validation. Untouched pending/missing null times, normally authored work and cleared-note exports still round-trip. The first archive-audit approach was correctly rejected by the snapshot hash guard; the tool now uses the complete original review when available and explicitly limits draft-only checks, with no fabricated replacement run or bypass.

`test_review_export_limit.py` uses the guarded temporary AppTest harness and synthetic oversized manual work. It first failed because no warning explained that the download exceeded the existing 10 MiB reopening cap. After the UI fix it passed in **0.650 seconds**, verifying the warning, byte-complete JSON, unchanged notes/session, refused oversized import and zero HTTP calls. This does not verify browser download transfer or add large-file reopening. The preceding intermediate suite passed 206 tests in 38.393 seconds before this final regression was added.

Separately authorized live pilot used exactly **12/12 serial localhost generations**: six development roles, six fresh holdout roles. Development 4/6 supported with two false fills; holdout 2/6 supported with one false fill and three manually confirmed wrong roles. Literal copying was 12/12, no predeclared alternatives selected, no abstentions or backend/contract failures. Source/role correctness remains unverified beyond these developer labels; the hypothesis failed its promotion gate. Exact copying is not semantic accuracy. The fresh holdout has no same-paper v5 baseline.

The archive audit observed 37 proposal occurrences: six complete-review validations, 27 context-only checks and four raw v1 occurrences unreplayed without the original complete review. These are not unique independent scientific judgments. V1 complete fixtures remain reopenable; v6 snapshots/requests/responses are independently reconstructed by its report auditor. Ordinary tests block/mock HTTP and isolate SQLite; no production database is opened. No new inference UI or model download was introduced. [Report](C2_SINGLE_ROLE_EVALUATION_2026-10-21.md), [verification](C2_V6_VERIFY_2026-10-21.json), [review guide](ABSTRACT_REVIEW_GUIDE.md).

## Public-prose v4/v5 — completed 2026-10-21

Baseline: **168 tests in 35.434 seconds**. Final `python -m unittest discover -s tests -v` passed **184 tests in 35.350 seconds** on stable source/fixtures after the final UI warning; all **37 active Python files** compiled. An earlier full run passed 184 tests in 45.290 seconds. Focused quote cases passed 34 tests in 0.140 seconds and four offline adjudication tests passed in 0.108 seconds. New contracts cover cue-independent availability, exact literal quote responses, wrong-paper/fragment/withheld/type rejection, preserved abstention/manual notes, mixed reopening and explicit demonstrations that source presence can accept a wrong role. Existing v3/v4 tests now explicitly retain their protocols; a new mocked v1/v2/v3 compatibility fixture leaves original fixture bytes intact.

Separately opted-in live public evaluation used **12/12** calls: v4 tuning 4, v5 tuning 4, v5 reserved holdout 4. Workflow proposals were 4/4 in each partition. V4 field agreement was 3/24, v5 tuning 15/24 and v5 holdout 15/24. V5 copied 43/43 selected original quotes exactly, yet filled six expected-missing roles and selected twelve other quotes differing from frozen role labels. Some alternatives are defensible; clear background/outcome/limitation misassignments also remain. Gold labels and scores were not changed after model output. The evaluation is developer-reviewed, not independent scientific validation; no actual new adversarial test was included in the twelve public-only calls.

The UI now discloses observed role/fill failures. All ordinary tests mock/block HTTP and isolate SQLite to temporary data. Actual new generation was programmatic; UI generation is mocked. Browser transfer/layout, broad languages/publishers, independent scientific support and comprehensive injection resistance are unverified. Prior benchmark evidence and production records remain untouched. [Public report](C2_PUBLIC_ABSTRACT_EVALUATION_2026-10-21.md), [verification](C2_V4_V5_VERIFY_2026-10-21.json), [optional next-model approval plan](C2_NEXT_MODEL_PILOT_PLAN.md).

## C2 coverage/segmentation v3 — 2026-10-20

Baseline: 150 tests in 34.720 seconds; evaluator preparation checkpoint: 158 tests in 42.306 seconds. Final `python -m unittest discover -s tests -v` passed **168 tests in 35.410 seconds** on a stable source/compatibility-fixture snapshot; **31 active Python files** compiled in memory. Focused quote tests passed 21 tests in 0.088 seconds before the additional multibyte case; four AI UI tests passed in 2.517 seconds. No production SQLite is opened by tests, and ordinary HTTP is blocked/mocked.

`test_coverage_evaluation.py` adds eight isolated guards for the 12-debit hard cap, malformed ledger, concurrent lock, opt-in/report protection, low-memory-before-backend ordering, incremental health-failure reports and gold-label isolation. Nine `test_quote_analysis_v3.py` cases cover abbreviation/number/negation preservation, present/passive/record cues, unfilled abstention, quarantined inputs and original evidence, unsafe/uncued refusal, wrong identity/type/field choices, mixed v1/v2/v3 JSON/accepted CSV, long claims and multibyte limits. One additional AppTest case checks the partial-evidence warning and retained original abstract. Existing v2 regression tests now explicitly use v2; frozen compatibility fixture bytes are unchanged.

The first full v3 run passed 166 of 167 tests: the legacy multibyte test expected a token-budget message but called the new default, which safely rejected uncued evidence earlier. Pinning that legacy check to v1 plus adding an explicit v3 test for both refusal paths resolved the test-contract mismatch. No protocol/source rule was changed after the holdout freeze.

Separately opted-in live evaluation used **10/12 actual localhost generations**: three v2 tuning, four v3 tuning and three synthetic v3 holdout. V3 agreed with 23/24 tuning and 17/18 returned synthetic holdout fields; two objective omissions remain. All 39 nonmissing v3 selections exactly copied expected original quotes in those developer examples. Both CC BY public abstracts were refused for zero eligible cues before model invocation, so public-paper AI quality is untested and benign workflow coverage failed. One unsafe holdout fixture was refused deterministically. No holdout outcomes informed extraction changes. Two calls remain unused. See [full report](C2_COVERAGE_FOLLOWUP_2026-10-20.md), [adjudication](C2_COVERAGE_ADJUDICATION_2026-10-20.json) and [verification](C2_COVERAGE_VERIFY_2026-10-20.json).

These are developer-authored/curated convenience cases, not independently blinded scientific evaluation. No unsupported/wrong-field v3 quote was observed in the returned synthetic proposals; exact matching only proves textual presence, not scientific support. English cue coverage, unfamiliar instructions, broader domains/languages, full-text analysis and independent correctness remain unverified. V3 actual generation was programmatic; new UI generation checks are mocked. Browser layout/uploads/download transfer and large-workspace behavior remain unverified. Earlier reports below are dated milestones, not current readiness statements.

## Quote-first C2 v2 follow-up — 2026-10-20

Fresh baseline: **137 tests passed in 34.573 seconds**. Final `python -m unittest discover -s tests -v` passed **150 tests in 34.427 seconds** on a stable source/compatibility-fixture snapshot. All 27 active Python files compiled. Thirteen new `test_quote_analysis.py` cases cover role misassignment, complete quote/negation preservation, explicit abstention, observed/fresh instruction variants, legitimate attack-research false positives, wrong identities/types/indices/free claims, fresh reordered structured/math cases, title omission, unchanged reviewer notes, backend failure and frozen v1/mixed-version JSON. The focused new suite passed 13 tests in 0.048 seconds before the final regression; legacy/UI focused checks passed 20 tests in 2.243 seconds. Legacy tests explicitly retain the v1 generation path, while UI fixtures exercise v2 selections.

The separately opted-in [real evaluation](QUOTE_FIRST_C2_2026-10-20.md) used the installed model unchanged: seven programmatic generations, two deterministic instruction refusals and one real temporary AppTest generation. Selected quote fidelity improved in these fixed examples, but four expected programmatic fields and one UI limitation were omitted. Eight actual responses were structurally valid. This is not broad semantic/instruction-resistance acceptance: English cues are heuristic, unknown instructions may pass, legitimate evidence may be refused, and source spans may fragment at abbreviations. All original failed v1 benchmark evidence remains unchanged.

Ordinary tests still mock/block HTTP and guard temporary SQLite. Compatibility JSON fixtures use mocked generation only and contain synthetic records; they do not establish AI quality. Real generation/latency/memory evidence is isolated in [raw v2 output](QUOTE_V2_BENCHMARK_2026-10-20.json) and [adjudication](QUOTE_V2_ADJUDICATION_2026-10-20.json). Final source/fixture/protected-file/diff/link checks are in [verification](QUOTE_V2_VERIFY_2026-10-20.json). No production research, external model service, new installation, Git operation or browser transfer/layout validation occurred. No actual backend outage/timeout occurred in this live sample; simulated failures remain in regression tests.

## Approved local setup and real C2 benchmark — 2026-10-20 follow-up

`python -m unittest discover -s tests -v` passed **137 tests in 34.485 seconds** after the setup/benchmark diagnostic was added. All 25 active Python files compiled; source/test hashes were stable and protected files remained unchanged. Four new `test_local_benchmark_guard.py` cases cover explicit live opt-in, non-JSON/existing-report refusal, refusing low-memory loads and bounded waiting for asynchronous unload without lowering the 4 GiB gate. The focused command passed **four tests in 0.558 seconds**. Ordinary tests still block/mock HTTP and isolate SQLite; they do not perform inference.

The separately opted-in [real local benchmark](LOCAL_ANALYSIS_BENCHMARK_2026-10-20.md) executed five fixed synthetic cases and one additional actual model generation from a temporary AppTest copy, with HTTP limited to loopback and SQLite to temporary storage. It records full model/digest/prompt/evidence context, raw successful/rejected responses, latency and Windows process-memory counters. Three of five programmatic outputs passed mechanical contracts; two were rejected for nonempty missing fields. Original review work remained intact. Real UI pending-generation, manual-note/evidence preservation, synthetic acceptance/rejection and JSON reopening passed. No production research was used.

**Model-quality acceptance failed.** Field misassignment occurred, and the model repeated an injected cure claim. Rejection was caused by unrelated malformed missing fields. An offline replay clearing those malformed fields accepted the poisoned claim lexically. This demonstrates a limit rather than successful semantic/injection validation. The separate [adjudication](LOCAL_ANALYSIS_ADJUDICATION_2026-10-20.json) preserves that finding. Scientific correctness, real-paper generalization, broader language/discipline performance, actual backend outage/timeout behavior and browser transfer/layout remain unverified. Simulated backend failures remain covered by ordinary tests. [Execution verification](LOCAL_MODEL_EXECUTION_VERIFY_2026-10-20.json) records the final checks.

## Phase C2 pre-install verification milestone — 2026-10-20

Fresh C1 baseline: **105 tests passed in 32.819 seconds**. Final `python -m unittest discover -s tests -v`: **133 tests passed in 34.176 seconds** on Python 3.14.7 / Streamlit 1.66.0. All 23 active Python files compiled in memory. Source/test hashes were compared before/after this run; protected files and existing application helpers remain unchanged. Final details are in [C2 verification](PHASE_C_C2_2026-10-20.json) and [handover](PHASE_C_C2_HANDOVER.md).

New coverage consists of 17 pure analysis tests, eight mocked local-backend wire tests and three isolated AppTest workflows. Focused `python -m unittest discover -s tests -p 'test_analysis*.py' -v` passed **20 tests in 2.222 seconds**. `python -m unittest discover -s tests -p 'test_local_backend.py' -v` passed **eight tests in 0.031 seconds** before the final full regression. Context-limit expectations were subsequently updated and passed in the full suite.

The tests verify six-field schema/missingness, exact excerpts, wrong run/paper/fingerprint rejection, malformed/duplicate/nonfinite JSON, numeric-literal guards, source/citation/model/prompt preservation, independent manual notes, pending/accepted/rejected proposals, regeneration, version-one/two JSON, comparison export and context/storage caps. A deliberate semantically unsupported claim passes lexical validation in a regression: excerpt presence does **not** establish scientific support. Injection-shaped fixtures verify the contract/data boundary only. The wire tests mock documented Ollama responses and check loopback/proxy/redirect restrictions, missing/cloud/wrong models, HTTP failures/timeouts, oversized responses, model changes and incomplete/context-limit generation. UI tests exercise disabled controls, failures preserving work, mocked generation, human approval/rejection and reopening without a runtime. Existing discovery/backup/C1 coverage remains in the full suite.

All HTTP in tests is mocked or blocked; AppTest uses the existing guarded temporary database harness. No live scholarly API/model generation, production database connection, package/model installation, Git action or historical-script change occurred. Outside tests, read-only local port/path/process/dependency/hardware checks and official documentation browsing established the setup proposal. **No usable backend exists in the inspected locations, so actual AI integration, latency/memory, scientific quality and real prompt-injection resistance remain unverified.** Browser layout and actual file transfers also remain unverified; AppTest emits existing bare-mode context warnings. See [runtime/model approval plan](LOCAL_MODEL_SETUP.md).

## Phase C C1 verification — 2026-10-20

Final C1 verification: `python -m unittest discover -s tests -v` passed **105 tests in 33.131 seconds** on a stable source/test snapshot. All 18 active Python files compiled; existing app helper/storage ASTs and protected-file hashes matched the baseline. Production data, historical scripts, requirements and repository instructions were preserved. No installation, Git action or live request was performed. Browser transfer/layout remains unverified.

Baseline: 92 tests in 26.795 seconds. New `test_review.py` has ten pure contract tests using synthetic discovery fixtures and blocked HTTP. Three added `test_ui.py` cases cover protocol/reason validation, screening/annotation/export behavior, distinct paper form state, missing-abstract controls, isolation from a later search and rendering reopened JSON in a fresh headless session. Existing UI expectations now include the fourth tab. Review files are in memory; all SQLite remains guarded temporary storage. No live API, browser or production database connection is part of this check. A test initially assumed keyword download data while the UI passed it positionally; the UI now consistently supplies `data=` and the focused case passes.

## Second Phase A/B re-audit: 2026-10-20

Fresh baseline: 80 tests in 25.371 seconds. The final full command passed **92 tests in 26.534 seconds**: 19 helper/widget, eight adapter, 30 retrieval, 18 UI, ten run-evidence, two live-guard and five backup tests. New regressions initially failed for malformed optional text, nullable author names, invalid input bounds/categories and query/settings relabelling. Further cases cover abstract-position conflicts, DOI resolver links, defensive selection snapshots, duplicate providers, impossible insertion counts, missing retrieval context, mismatched history attempts and malformed-field UI isolation. An older fixture was corrected to retrieve using the date scope asserted in its manifest.

Source hashes were stable during the final suite; syntax, snapshot diff, local-link and protected-file checks passed. No live provider call or production SQLite connection was made. See the [second audit](AB_AUDIT_2_2026-10-20.md) and [Phase C contract](PHASE_C_HANDOVER.md). Earlier test counts below are preserved milestones. A passing audit does not certify scientific accuracy or all untested scenarios.

## Phase A/B re-audit: 2026-10-20

The user requested another review before Phase C. [Audit evidence](AB_AUDIT_2026-10-20.md) records the baseline, reproduced regression failures, final results and unchanged production-file checks. New cases cover identical-title paper selection by stable key, NULL metadata enrichment, rollback of a mixed update/insert batch, malformed title/year rejection, preservation of source integer years outside the UI input range, and zero-versus-unknown key identity. The existing suite still covers provider/filter/count/budget/error/cooldown/history/provenance/export and backup behavior. All new data is synthetic and temporary; no production SQLite connection or live query is needed.

The next phase's input and interpretation contract is [Phase C Handover](PHASE_C_HANDOVER.md). Test success is not proof of bug-free behavior, worldwide coverage or independent scientific accuracy. Earlier counts and live evidence below remain dated milestones.

Final re-audit: **80 tests passed in 25.521 seconds** on Python 3.14.7/Streamlit 1.66.0, with source hashes stable during the run. All 14 active Python files compiled in memory; schema AST, local document links, source snapshot diff and protected-file hashes passed. The audit added five cases to its 74-test baseline; a concurrently completed and reviewed live-report guard added one more. No new live calls or production SQLite connections were made.

## Phase B acceptance: 2026-10-20

The current workspace baseline was **57 tests in 16.658 seconds**, including already-implemented pagination/history settings. The final full command `python -m unittest discover -s tests -v` passed **80 tests in 26.302 seconds** on Python 3.14.7 and Streamlit 1.66.0: 19 helper/widget, eight adapter, 24 retrieval, 17 UI, five run-evidence, two live-opt-in guards, and five backup tests. Earlier counts below are dated milestones.

New coverage verifies independently optional years, pre-1900/early-CE request formatting, missing-year handling, native source/page evidence, over- and under-reported final totals, exclusion of untitled records from saveable counts, Retry-After dates/numbers/defaults, later-page 429 preservation, UI session cooldowns, shared run IDs/settings, source-specific history provenance, ZIP/CSV/JSON round trips, unique-versus-new counts with existing library records, legacy note preservation, and refusing live diagnostics without --live. Helper/adapter/retrieval/run/UI requests are mocked or injected, with unmocked HTTP blocked; all storage is temporary and guarded.

Focused commands used `-p test_retrieval.py`, `-p test_ui.py`, `-p test_runs.py`, `-p test_app.py`, and `-p test_live_guard.py` with unittest discovery. Syntax, unchanged schema initialization, reviewed AST changes limited to NULL enrichment/library key loading, protected hashes, links and snapshot diffs were checked. Newer workspace tests/fixes were preserved: malformed title/year rejection, SQLite-safe integer years, zero-year keys, NULL enrichment, rollback and identical-title evidence selection. An intermediate mixed-version run failed; final acceptance uses source/test hashes before and after the stable suite. The backup suite remains unchanged. Bare-mode AppTest context warnings remain; no browser/server was launched.

Live tests are separate and explicitly opt-in: [live pagination evidence](LIVE_PAGINATION_2026-10-20.md). Seventeen HTTP 200 responses established small page/cursor traversal, positive journal and OpenAlex conference examples, historical dates, natural empties and exact duplicate replay in disposable storage. Three strict Crossref positive-conference-in-window probes failed because their windows contained journal types; a separate public DOI lookup positively verified Crossref conference classification. Those failed sample assertions remain in their JSON artifacts. No real outage/429 was induced; actual fault behavior, broad recall, larger budgets, concurrency, process recovery and browser downloads remain unverified.

The [acceptance matrix](PHASE_B_ACCEPTANCE.md) distinguishes these implementation gates from research coverage claims. No live API calls are part of the 80-test automated suite, and no production database/schema or historical script was changed.

## Bounded retrieval verification: 2026-10-20

The pre-change baseline passed 39 tests in 10.405 seconds. New `test_retrieval.py` cases inject synthetic provider pages, a fake monotonic clock and fake sleep while blocking live HTTP. They cover OpenAlex page numbers, latest Crossref cursors with stable query/rows, final-page exhaustion, raw/page/time budgets, locally excluded records and duplicate counts, non-multiple budgets, unknown/changing totals, contradictory totals, missing/cyclic cursors, access/rate/transport/JSON failures, malformed envelopes, oversized pages, earlier-page preservation, error sanitization and structured history notes.

UI tests continue to use byte-for-byte temporary copies of the active app with temporary SQLite files. Additional cases traverse two pages from both providers after first-page local filtering excludes all entries, merge a cross-provider duplicate, and preserve the first page when the second times out. Updated assertions distinguish raw/filtered/run-unique counts and complete/partial/error history statuses. The fresh-interpreter import audit now includes the retrieval module.

Commands: `python -m unittest discover -s tests -p test_retrieval.py -v`, `python -m unittest discover -s tests -p test_discovery.py -v`, `python -m unittest discover -s tests -p test_ui.py -v`, and the full-suite command below. The final full suite passed **57 tests in 16.158 seconds** (16 retrieval, eight adapter, 11 UI, 17 helper/widget and five backup tests). In-memory compilation, AST checks of unchanged storage/export helpers, metadata byte comparison, protected-file hashes and a snapshot diff review passed. See [Retrieval Design](RETRIEVAL_DESIGN.md) for completion semantics and provider documentation. Existing dated reports below describe earlier milestones. Live pagination, real rate-limit behavior, corpus coverage, concurrent sessions, browser layout/download transfer and process-crash recovery remain unverified. This task removes the deprecated width arguments; bare-mode AppTest `ScriptRunContext` warnings can still appear.

## Run focused tests

With the project environment activated and runtime dependencies installed, run:

```powershell
python -m unittest discover -s tests -v
```

The suite uses Python's standard-library `unittest` and temporary directories. It does not require pytest or make live API calls.

## Isolation design

`app.py` executes the Streamlit interface at module scope and creates data/output directories during initialization. Helper tests import the UI/storage-free `discovery` modules normally and compile only the remaining storage/export helpers from `app.py`. The end-year default test separately executes only that widget assignment with a mocked clock and mocked Streamlit object. For helper persistence coverage, the test namespace's database path is set to a temporary file before `connect_db` is called. UI tests use the separate isolation boundary below. The production `data/research.db` must never be opened by the test suite.

## Source adapter contract tests

`python -m unittest discover -s tests -p test_discovery.py -v` runs eight tests without live APIs. Injected synthetic responses distinguish reported totals, raw batches, filtered records, keyless exclusions, and duplicates retained for storage. Cases preserve unknown totals, tuple compatibility, independent requesters, HTTP/JSON/transport error propagation, and the existing headers/45-second timeout without retries or cursor traversal. Helper and adapter tests also block unmocked HTTP sessions.

A fresh-interpreter test imports discovery from an empty temporary working directory with audit guards rejecting writes, directory creation, SQLite connections, DNS lookup, and socket connection attempts. It checks that Streamlit, pandas, SQLite, and the app were not imported. UI tests still execute a temporary unchanged script, importing the real workspace discovery package. These checks do not validate concurrency, static types, malformed payload recovery, retry policy, pagination, or live behavior after the extraction.

For this extraction, the baseline full suite passed **31 tests in 10.738 seconds**. Focused checks passed **17 helper/widget tests** and **8 adapter tests**; the final full suite passed **39 tests in 10.534 seconds**, including nine unchanged UI tests and five unchanged backup tests, on Python 3.14.7/Streamlit 1.66.0. In-memory compilation passed for eight active source/test files. AST comparisons confirmed unchanged UI, initialization, storage, metadata/key/filter mappings, and HTTP transport. Protected-file hashes and local documentation links were checked. No live APIs were called; the earlier [live report](LIVE_SMOKE_2026-10-20.md) remains dated pre-extraction evidence. Existing Streamlit warnings remain.

The helper suite covers DOI/title normalization, source payload normalization, OpenAlex abstract reconstruction, duplicate merging and persistence, local title/abstract filtering, CSV encoding/content, provider-aware publication categories, and provider request/filter behavior with mocked responses. Cases cover inclusive/single year bounds, missing years/types/locations/sources, empty selections, all five shared categories, multiple selections, original type preservation, explicit venue evidence, peer reviews, conference abstracts, editorials, existing Crossref date precedence, empty responses, and one bounded request per provider. OpenAlex fixtures use native types and venue metadata; Crossref fixtures use its distinct type vocabulary. Tests verify that OpenAlex requests use native candidate types, never raw Crossref labels. Helper provider tests replace `request_json`; UI provider requests are mocked at the HTTP session boundary. No tests call live APIs or use the production database.

`tests/test_backup.py` extracts only `connect_db` to initialize the app's schema under a temporary directory. It executes the marked Python definitions in [Data and Backup](DATA_AND_BACKUP.md), so changes to the documented procedure are tested directly. It checks exact synthetic schema/data/ID-sequence snapshots through backup, replacement, and rollback; source preservation; committed WAL changes with an open writer connection; and refusal of missing/invalid sources, unrelated databases, existing targets, and self-overwrite. It does not simulate writes occurring during backup, process crashes, or disk exhaustion.

To run just this rehearsal:

```powershell
python -m unittest discover -s tests -p test_backup.py -v
```

## Isolated Streamlit UI smoke tests

Run the headless UI tests with the already installed Streamlit testing utility:

```powershell
python -m unittest discover -s tests -p test_ui.py -v
```

`tests/test_ui.py` uses `streamlit.testing.v1.AppTest.from_file` on a byte-for-byte copy of the active `app.py` inside a fresh temporary directory for each test. No application code is rewritten. Since the application derives its root from `__file__`, all initialization, data, and export paths resolve under that temporary root. A patched `sqlite3.connect` rejects connections outside that root and URI-style paths before opening anything. An explicit guard test exercises rejection without opening an external database.

The HTTP session request method is patched for the lifetime of each test. An unconfigured request raises an assertion; search tests return synthetic `requests.Response` mocks for the two exact provider URLs. The guard test verifies unmocked HTTP is blocked. Real normalization, filtering, persistence, UI code, and request construction still execute. Cleanup restores patches and removes disposable app/data files. These tests run serially because patches affect process-wide modules; do not run them concurrently in the same process.

UI smoke-test coverage includes:

- Empty-database startup, search controls, tabs, default year/limit, empty-state messages, and zero metrics.
- Blank-query and inverted-year validation without provider requests or saved searches.
- Search-button forwarding of topic, years, type selection, and limit; provider-specific count messages; saved literature/history; DOI deduplication and repeated searches.
- Saved-title/abstract filtering, paper selection, metadata and source-link output, and an empty filtered view.
- CSV filename/MIME, UTF-8 BOM, and filtered rows by inspecting the bytes passed to the real download widget, including a header-only CSV for an empty view.
- A mocked OpenAlex timeout while Crossref succeeds, with both attempts recorded and successful records saved.
- Empty provider batches, the no-results warning, and successful search-history entries with zero retrieved rows.
- Journal-only selection includes journal metadata from both providers, excludes conference/unclassified records, and preserves raw stored types.
- Clearing categories admits unclassified records, retains year bounds, and omits the OpenAlex native type filter. Default labels combine journal articles and reviews alongside conference papers.

The provider-category correction replaced the former unrealistic OpenAlex `proceedings-article`/`posted-content` fixtures and their false cross-provider equivalence assumption. The earlier passing suite did not establish correct live provider type semantics. Current mocks follow documented native vocabularies and explicit venue evidence. UI tests check candidate-count wording rather than claiming exact selected-category totals.

Each UI rerun checks that Streamlit reported no uncaught exception. This verifies headless widget interaction and emitted elements, not browser DOM, CSS/layout, responsive behavior, browser navigation, or actual file-download transfer. Live provider behavior, real network failures, multi-user/concurrent sessions, interrupted writes, and other dependency versions remain untested. The installed Streamlit emits bare-mode `ScriptRunContext` warnings during AppTest setup and deprecation warnings for existing `use_container_width` arguments. Those warnings were not suppressed; replacing deprecated layout arguments remains separate work. No browser or server process is launched, and no package was installed.

## Executed checks: 2026-10-20

- `python -m unittest discover -s tests -v`: **15 tests passed** on Python 3.14.7 after the approved filtering review; the pre-edit suite had nine tests.
- After the current-year default follow-up, the same command passed **16 tests**, including the isolated end-year widget test across the 2026/2027 local year boundary. In-memory syntax checks also passed for the active app and tests. Full Streamlit rendering remains untested.
- After adding the backup/restore rehearsal, the full suite passed **21 tests**; the focused backup command above passed all **5 tests**. In-memory syntax checks passed for `app.py` and both test files. The app, production database, historical scripts, and requirements were unchanged by this task.
- The documentation-only schema-policy task reran the complete suite: **21 tests passed**. Local Markdown link targets were checked for existence. [Schema Migration Policy](SCHEMA_MIGRATIONS.md) describes required future migration tests; those tests and a migration runner have not been implemented. No tests were added for this prose-only change.
- The UI smoke-test task passed **7 focused tests** with `python -m unittest discover -s tests -p test_ui.py -v` and **28 tests** with the full discovery command. Runs used Python 3.14.7 and Streamlit 1.66.0. In-memory syntax checks passed for the active app and all three test files; local Markdown link targets were checked. Existing Streamlit warnings described above were present. No production database, application, historical-script, dependency, or existing-test changes were made.
- The provider-category correction passed **17 helper/widget tests**, **9 isolated UI tests**, and **31 tests in the full suite** using the same discovery commands. Python 3.14.7 and Streamlit 1.66.0 were used. Syntax and 16 local documentation link checks passed. AST checks confirmed unchanged schema/persistence/key logic, HTTP handling, Crossref request construction, and shared local filtering. Database, historical-script, and requirements hashes were unchanged. Existing Streamlit warnings remained; no live research queries were made during tests.
- In-memory `compile(...)` checks passed for `app.py`, `tests/test_app.py`, and `app_backup_v01.py`, without importing or executing the Streamlit UI.
- A snapshot diff was reviewed using standard-library `difflib` because this workspace has no Git repository. AST comparison confirmed the provider request functions and persistence functions were unchanged from the task's initial snapshot.
- Separate read-only database inspection (outside the tests) confirmed 25 papers and 4 searches. SHA-256 comparison confirmed the production database and both historical app scripts were unchanged across the task.

These results describe this local run, not a compatibility guarantee or a live-provider integration test. Crossref's public type list was consulted separately to verify the mapping; it is not a network dependency of the tests.

## Controlled live smoke check: 2026-10-20

The separately approved [live smoke report](LIVE_SMOKE_2026-10-20.md) records seven serial public requests with limit five and temporary storage. Both providers returned positive journal/conference examples and natural empty results; sampled classifications, count pass-through, persistence, and duplicate replay checks passed. Three offline UI replays used captured live pairs; four additional UI runs used simulated timeout/empty cases. No actual live error occurred. These checks do not establish corpus coverage, provider-total accuracy, narrow-year boundaries, or real outage behavior. Raw fetched counts were measured by the harness but are not displayed/stored by the app.

The full isolated suite was rerun with `python -m unittest discover -s tests -v`: **31 tests passed in 20.261 seconds**, with existing Streamlit warnings. No live calls were added to the suite. Earlier references to untested live behavior describe the automated-test boundary and earlier milestones; this small dated check adds only the evidence explicitly listed in its report.

## Environment and limits

The only interpreter discovered by VS Code/Pylance during the 2026-10-20 audit was the system Python 3.14 installation. The terminal's `python` command may resolve differently; check with:

```powershell
python -c "import sys; print(sys.executable)"
```

Select `.venv\Scripts\python.exe` in VS Code and run tests through that environment for consistency. No alternate Python versions or CI environment were available for this phase.
