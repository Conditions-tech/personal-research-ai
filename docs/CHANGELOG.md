# Changelog

## 2026-10-26 — Crossref server filters; app RAM gate

- Crossref requests now carry server-side year/type filters (start year widened by one for its earliest-date semantics); exact local filters, date precedence, storage and schema are unchanged. Crossref totals with filters are labelled as candidate counts. Live sample: 36/50 fetched entries kept versus 0/50 before.
- The review UI checks available physical RAM (4 GiB, the existing benchmark gate) before generation. Frozen Qwen3 files (`review/analysis.py`, `review/local_backend.py`, `review/quote_analysis_v5.py`) are byte-identical; the gate lives in the new `review/memory.py`.
- Full suite: **247 tests** passed (5 new). Qwen3 frozen source/ledger check passed; ledger unchanged at 7/12. No production data, schema, model, package or Git change.

## 2026-10-25 — runtime identity diagnosis

Improved recovery state to report failed runtime identity checks with endpoint, status and safe reason; clear stale digests on failed probes and preserve blocked state during offline regression runs. Added focused regression coverage. Diagnosed the empty inventory as an account/model-store context mismatch candidate; the installed nested digest still matches, but active daemon model path is unknown. A process stop failed and was not retried. No inference or download. [Details](C2_QWEN3_RUNTIME_IDENTITY_2026-10-25.md).

## 2026-10-25

Added a separate bounded Qwen3 recovery/continuation controller and twenty-two isolated tests. Serializes regressions and one-case children, preserves original budget/source identity and pending work, and refuses unknown/busy model ownership. Live readiness found no loaded model and below-gate physical RAM; no inference, unload, production write, default change or download occurred. [Continuation verification](C2_QWEN3_CONTINUATION_2026-10-25.md).

## 2026-10-24 — Interrupted pilot reconciled without replay

- Verified complete saved responses and unload evidence for all seven charged Qwen3 requests, including the seventh; same ledger 7/12, five unattempted, no unknown/retried/un-charged request.
- Added exact partial holdout adjudication and resource summary, preserving original raw artifacts and frozen source/labels. Fresh runtime metadata passed; physical RAM remained below 5.5 GiB and no new inference was sent.
- Fresh isolated regressions: **217 tests in 36.577 seconds**; 51 active files compiled. No source/default, production/schema, historical-file, model/dependency or Git change. [Report](C2_QWEN3_STATUS_2026-10-24.md).

## 2026-10-21 — Approved Qwen3 downloaded; RAM blocks inference

- Downloaded exactly the approved additional 4B Q4_K_M model, retaining Qwen2.5; pinned digest and installed nonthinking metadata verified without a runtime/package upgrade.
- Added separate bounded pilot/audit tools, frozen public/synthetic evidence and alternatives, and ten isolated tests. First controller blocked before backend use at the unchanged 5.5 GiB gate; ledger 0/12 and no Qwen3 quality claim.
- Full suite: **217 tests in 35.970 seconds**, 51 active Python files compiled. Existing app routing, production data/schema, historical files and old evidence/ledgers remain unchanged. [Report](C2_QWEN3_PILOT_2026-10-21.md).

## 2026-10-21 — One-role trial failed; review import strengthened

- Restored conservative v3 default while retaining saved v1–v5 compatibility. Added unpromoted v6 independent-role diagnostic and offline support/archive audits; completed exactly 12 approved local requests, without new model/download.
- V6 matched 4/6 development and 2/6 holdout roles despite exact source copying. Preserved all failed outputs, frozen labels and original evidence; no scientific-quality or synthesis claim.
- Added a reproduced oversized-review warning while preserving complete JSON downloads and the existing 10 MiB reopening cap; no notes are truncated.
- Fixed reproduced duplicate-JSON note replacement and missing required action/root timestamps. Valid exports, pending/missing null times, reviewer notes and original evidence remain intact. Added the review guide. Full suite: 207 tests in 35.786 seconds; 47 active files compiled. [Report](C2_SINGLE_ROLE_EVALUATION_2026-10-21.md).

## 2026-10-21 — Public prose reachable; field quality remains partial

- Added retained cue-independent v4 and literal-quote v5 protocols, versioned reopening, observed-quality UI warnings and a pure offline adjudication utility.
- Froze 4 public tuning and 4 holdout examples with source/licence provenance before tuning. Used 12/12 actual localhost calls; v5 matched 15/24 fields in each partition while copying every selected quote exactly. Preserved failed v4 outputs and original gold; no scientific/injection guarantee.
- Added 16 isolated tests and a mocked v1–v3 compatibility fixture. Final suite: 184 tests in 35.350 seconds; 37 active Python files compiled. Production/historical/legacy evidence/dependencies remain preserved. [Report](C2_PUBLIC_ABSTRACT_EVALUATION_2026-10-21.md).

## 2026-10-20 — Resumed C2 evaluation and retained v3

- Added `review/quote_analysis_v3.py`, version/format dispatch and a UI warning for instruction-flagged sentences withheld from model input/quote choices. Original evidence and reviewer work remain intact; legacy v1/v2 reconstruction and fixtures are preserved.
- Ran 10/12 approved actual generations on the existing local runtime/model after RAM qualified. V3 matched 23/24 tuning and 17/18 synthetic holdout fields. Both public abstracts were refused before inference; public-paper output quality remains unverified. No rules changed after holdout inspection.
- Added nine v3 tests and one UI case alongside eight evaluator guards; final suite passed 168 tests in 35.410 seconds and 31 active files compiled. Full raw results, failures, hashes and developer-adjudication limits are in the [evaluation](C2_COVERAGE_FOLLOWUP_2026-10-20.md).
- No production schema/records, historical scripts, dependencies, runtime/model installation or Git operation changed. Quality acceptance stays partial; synthesis and full Phase C completion remain separate.

## 2026-10-20 — Earlier evaluation preparation checkpoint; resource blocker later resolved

- Froze four tuning and six separate holdout examples with abbreviations, passive/uncued evidence, participants, null results, safe/unsafe instructions and two attributed CC BY 4.0 public abstracts. Recorded offline v2 segmentation/candidate failures; no holdout tuning or new model result.
- Added an opt-in serial evaluator with shared 12-request ledger, concurrent lock, incremental reports, resource-before-backend checks and gold-label isolation. Eight new isolated guards pass; full suite passed 158 tests in 42.306 seconds.
- Live health timed out and available RAM remained below the unchanged 4 GiB gate. Budget remains 0/12. No v3 extraction change, installation, model loading, user application closure, production data/schema change or Git action. [Resume plan/blocker](C2_COVERAGE_FOLLOWUP_2026-10-20.md).
## 2026-10-20 — Approved quote-first C2 follow-up

- Added `abstract-quotes-v2` with independent field definitions, conservative English eligibility, full source-span selections, abstention and pre-inference instruction-pattern refusal. New AI text is extractive; manual interpretations and old v1 drafts remain unchanged.
- Preserved exact v1 request/response validation and added version-matched reopening with frozen v1/mixed compatibility fixtures. Model/digest, citations, original evidence, reviewer notes and previous benchmark files are preserved.
- Added 13 isolated regressions plus four fresh evaluation cases. Final suite: 150 tests in 34.427 seconds. Eight actual local generations improved selected-field fidelity but left omissions; no runtime/model/package/schema/Git change or Phase C completion.
- See [v2 report](QUOTE_FIRST_C2_2026-10-20.md) for actual metrics, omissions, deterministic-refusal limits and next validation work.

## 2026-10-20 — Approved local runtime/model setup and real benchmark

- Installed the approved Ollama 0.40.6 runtime using its verified official CLI archive to avoid the desktop updater; configured loopback/cloud-disabled single-model operation and downloaded only the specified Qwen2.5 1.5B Q4_K_M model. No Python dependency, production data/schema, historical file or Git change.
- Added an explicitly opted-in synthetic benchmark with guarded temporary app/storage, bounded memory waiting and sampled Windows runtime memory counters; four isolated guard tests prevent accidental inference/overwrite or relaxing the memory gate.
- Executed six real local generations and review integration checks. Technical integration passed; model-quality acceptance failed because of field assignment and injected-instruction behavior. No prompt/model change was made to hide failures. See [benchmark](LOCAL_ANALYSIS_BENCHMARK_2026-10-20.md).
- Final ordinary regression: 137 tests passed in 34.485 seconds. Phase C remains incomplete; the next bounded proposal is field-specific prompt/evidence handling with backward-compatible versioning.

## 2026-10-20 — Phase C2 analysis contracts and conditional local adapter

- Added six-field abstract proposal validation, exact paper/evidence binding, excerpts, numeric guards and complete model/prompt/source traceability.
- Added separate pending/accepted/rejected AI proposals, human review controls, accepted-only comparison columns and validated version-two JSON reopening while retaining C1 support.
- Added a loopback-only Ollama CPU adapter with bounded/sanitized errors and no automatic downloads or generation; existing manual notes/discovery/storage remain intact.
- No usable local backend/model was found. [C2 handover](PHASE_C_C2_HANDOVER.md) separates mocked validation from unverified inference; [setup proposal](LOCAL_MODEL_SETUP.md) gives the download/memory/licence details and required approval. Phase C is not complete.

## 2026-10-20 — Phase C C1 review workspace

- Started the approved Literature Review and Paper Analysis phase using the user's selected six-field default summary format.
- Added a copied discovery-run snapshot, required screening protocol, candidate decisions/reasons, reviewer-authored abstract notes, exact-excerpt validation and metadata-only controls.
- Added comparison CSV and full-workspace JSON downloads/reopening. Reviews are session-local; no SQLite/schema change or model integration.
- Added ten pure review tests and three isolated UI cases. See [Phase C plan](PHASE_C_PLAN.md) for limits and remaining work.

## 2026-10-20 - Second Phase A/B re-audit

- Added stricter provider text/abstract-position handling, preserved nullable author-name parts, and normalized OpenAlex DOI record links.
- Captured actual retrieval query/settings, validated bounded inputs before network requests, and prevented run/history mislabelling, duplicate provider results and impossible insertion counts. Manifest/note shapes and versions remain unchanged.
- Added 12 isolated regression/integration cases; the full suite passed 92 tests. Corrected earlier misleading settings fixtures, preserved the first audit, and updated the Phase C handover. No app entry-point, provider request, production data/schema, historical file, package or Git changes.

## 2026-10-20 - Phase A/B re-audit and Phase C handover

- Reproduced and corrected identical-title paper selection, NULL metadata enrichment, malformed title/year acceptance and zero-versus-unknown fallback identity. Library CSV now includes the existing stable record key; no schema migration or production rewrite.
- Added isolated regressions and transaction-rollback verification; reviewed the existing live evidence without new provider calls. Preserve failed sample assertions and distinguish them from successful traversal/classification checks.
- Added a detailed A/B audit and Phase C knowledge contract; corrected obsolete current-risk statements and linked the handover across maintained documentation. Phase C implementation remains unstarted.

## 2026-10-20 - Phase B bounded discovery acceptance

- Built on the existing pagination controller and 57-test baseline; added optional historical year bounds, early-CE date formatting and explicit unknown-year behavior.
- Added native source/page provenance, shared run IDs and count/settings manifests through the existing history note field, latest-run ZIP and displayed-history JSON exports. No schema migration; legacy notes preserved; library CSV now includes record_key.
- Added 429 session cooldowns using sanitized Retry-After, two-way final-total consistency checks and exclusion of untitled records from saveable counts. Preserved existing budgets. Reviewed newer malformed title/year validation, zero-year keys, NULL metadata enrichment, rollback tests and identical-title selection fixes.
- Full isolated suite passed 80 tests. Seventeen controlled HTTP 200 responses supplied pagination/historical/empty/replay evidence; strict Crossref query-window sampling failures and a successful known-conference DOI check are documented separately.
- Added explicit Phase B acceptance and live evidence reports; kept Literature Review and Paper Analysis separate. Production data/schema, historical scripts, requirements and Git state were preserved.

## 2026-10-20 - Bounded discovery and persistent mission

- Preserved the user-confirmed three-workflow goal, incremental engineering authorization and FINISH agreement in `docs/MISSION.md`.
- Added a UI/storage-independent retrieval controller and provider page methods: keyless OpenAlex basic pages and latest Crossref cursors, bounded to 250 raw entries/five requests per source with a between-request time budget.
- Added complete/partial/error states, stop reasons, earlier-page preservation, unknown/changing total handling, raw/filtered/run-unique counts and sanitized errors. New history notes retain settings/counts in the existing schema.
- Extended the UI budgets, distinguished current-run unique keys from new library insertions, and replaced deprecated Streamlit width arguments.
- Added isolated pagination/failure/budget tests and UI cases for later matching pages, duplicate merging and interrupted retrieval. Updated the current design and roadmap. No production data/schema, historical scripts, packages, paid services or Git operations were changed.

## 2026-10-20 - Reusable Literature Discovery boundary

- Extracted metadata, category mappings, keys, and shared filters into `discovery/metadata.py`; introduced OpenAlex/Crossref source adapters and an explicit single-batch count contract in `discovery/providers.py`.
- Preserved the app's tuple search interface and all existing UI/storage behavior, requests, limits, schema, and records. Added no pagination, retry, model integration, packages, or live calls.
- Added eight isolated adapter tests and switched helper tests to direct discovery imports with blocked unmocked HTTP. The baseline 31 tests and final 39-test suite passed; UI/backup tests remained unchanged.
- Updated architecture, testing, decisions, status, and roadmap to connect the extraction to the three-workflow goal and target hardware.

## 2026-10-20 - Provider-aware journal and conference discovery

- Replaced raw provider-style type choices with shared journal-paper, conference-paper, book-chapter, dissertation, and posted-content categories. Default searches now include Crossref journal-article records without guessing article/review subtypes.
- Added explicit OpenAlex native-type/venue classification and native candidate request filters, including conference venue evidence for older article/review records. Unclassified records remain eligible only when categories are cleared.
- Preserved raw provider types, saved data/schema, deduplication, year controls, and per-provider limits; added no pagination or extra requests.
- Replaced unrealistic provider fixtures, expanded journal/unknown/clear-selection coverage, and relabelled OpenAlex totals as candidates before local filtering. Documented coarse classification and live-coverage limits.

## 2026-10-20 - Isolated Streamlit UI smoke tests

- Added seven AppTest smoke tests using unchanged temporary app copies, temporary SQLite data, blocked unmocked HTTP, and synthetic provider responses.
- Covered startup/validation, UI filter forwarding, saved literature/history/deduplication, metadata browsing, filtered CSV payloads, a provider timeout, and empty results.
- Documented headless coverage limits and existing Streamlit `use_container_width` deprecation warnings. No application, schema, production-data, historical-script, or dependency changes were made.

## 2026-10-20 - Schema migration policy

- Added a documentation-only policy for version adoption, schema recognition, compatibility checks, staged atomic upgrades, isolated testing, production approval, and backup-based recovery.
- Linked the policy from setup, architecture, backup, status, roadmap, and decisions documentation, distinguishing current behavior from future implementation requirements.
- No application, test, dependency, database metadata, schema, or record changes were made.

## 2026-10-20 - Backup and restore rehearsal

- Replaced the untested backup snippet with definitions that validate an existing read-only source, refuse destination overwrite, and verify the copied database.
- Documented staging, pre-restore preservation, offline replacement, rollback, sidecar handling, and verification limits.
- Added five isolated tests of the exact documented workflow using the active app's schema and synthetic records, including committed WAL data and refusal cases. The full suite passed 21 tests.
- Preserved application code, production data, schema, historical scripts, and dependencies; no production backup or restore was performed.

## 2026-10-20 - Current publication year default

- Replaced the fixed 2026 publication end-year default with the app host's current local calendar year.
- Preserved year bounds, the start-year default, provider filters, and UTC storage timestamps.
- Added an isolated widget-assignment test with a mocked clock spanning New Year.

## 2026-10-20 - Consistent provider filters

- Applied inclusive year and selected publication-type filters to normalized OpenAlex and Crossref results.
- Kept the per-provider request limit and added no pagination; Crossref may return fewer records after local filtering.
- Verified the explicit Crossref type map against its published type list and removed unsupported `article`/`review` aliases; ambiguous and missing types are not inferred. Raw provider types remain unchanged in saved metadata.
- Expanded mocked provider tests for inclusive and single year bounds, multiple types, absent metadata, date precedence, empty responses, and one bounded request per provider. No live API calls occur in tests.
- Clarified filter/count behavior and Crossref's default journal-article exclusion in the UI and handover; corrected the stale README troubleshooting claim that Crossref was unfiltered.

## 2026-10-20 - Phase 1 handover and safe stabilization

- Added repository instructions, Windows setup/usage documentation, architecture/status/decision/roadmap/data/testing notes, and a changelog.
- Added a minimal runtime dependency manifest and ignore rules for local data, exports, secrets, environments, and caches.
- Extracted the existing saved-record filter and CSV serialization into helpers without intending to change behavior.
- Closed SQLite connections after transaction handling to avoid retaining database file handles.
- Added isolated tests using temporary SQLite databases; see the test run reported with this phase for actual results.
- Preserved all historical app scripts and production research data; no database schema or production records were changed.
