# Phase C — Literature Review and Paper Analysis

## Runtime identity repaired; resource gate remains — 2026-10-25

The previous empty-model-inventory condition was repaired by restarting the same approved daemon with a process-scoped path to the existing store. Current PID 11528 reports the exact approved digest and an empty loaded-model list. The controller remains `waiting_memory`: latest available RAM is 4.13 GiB, below the original 5.5 GiB gate. Keep all five cases pending and do not load the model until a fresh controller run qualifies. [Repair evidence](C2_QWEN3_RUNTIME_REPAIR_2026-10-25.md).

## Resource continuation — 2026-10-25

The approved recovery layer is separate from frozen inference. Automatic supervision can recheck and run one original uncharged Qwen3 case when RAM qualifies; temporary low RAM preserves the queue without repeated ready questions. Ledger remains 7/12 after live readiness. No quality/default promotion or Phase C completion. [Current evidence](C2_QWEN3_CONTINUATION_2026-10-25.md).

## Current bounded pilot state — 2026-10-24

Resume only the five unattempted frozen Qwen3 cases when physical RAM actually reaches the unchanged 5.5 GiB gate. Seven charged cases have complete saved responses, no ambiguous/retried request, and the same ledger remains 7/12. Do not replace the default or start synthesis: source copying passed while clear role failures remain. [Current acceptance evidence](C2_QWEN3_STATUS_2026-10-24.md).

The user approved the exact [Qwen3 plan](C2_NEXT_MODEL_PILOT_PLAN.md). Download/metadata checks are complete, but the first loading gate failed at about 5.015 GiB available versus 5.5 GiB required. That first checkpoint sent no inference (ledger then 0/12). The [current live pilot](C2_QWEN3_LIVE_PILOT_2026-10-21.md) subsequently began after RAM qualified. Finish the frozen bounded pilot only when resources qualify; no app-default/model-option change or scientific-quality claim follows from installation. [Current pilot handover](C2_QWEN3_PILOT_2026-10-21.md).

Started 2026-10-20 after the user approved moving beyond the completed A/B re-audits. The user explicitly selected the default paper summary fields: objective, method, dataset, results, limitations and conclusion. [A/B handover](PHASE_C_HANDOVER.md) remains the discovery evidence contract.

## Current quality follow-up — 2026-10-21

The no-download single-role pilot completed **12/12 new local requests**: development matched 4/6 roles with two false fills; fresh holdout matched 2/6 with three wrong-role selections and one false fill. All quotes copied source text exactly, but field-quality acceptance failed. The app default is restored to **`abstract-quotes-v3`**; v4/v5 remain readable and v6 is an unpromoted diagnostic. No further inference or new model was used. [Full current report](C2_SINGLE_ROLE_EVALUATION_2026-10-21.md).

The separate bounded Qwen3 pilot currently has seven complete, reconciled responses and five original cases pending under its independent 12-request cap. A second-pass non-blinded review found multiple material role/coverage problems and verified identity binding to the captured records; this is not independent scientific validation and does not alter frozen labels. Current inference remains memory-gated. [Review addendum](C2_QWEN3_DEVELOPER_REVIEW_ADDENDUM_2026-10-25.md), [current runtime/pilot status](C2_QWEN3_RUNTIME_REPAIR_2026-10-25.md).

Continue useful backend-independent correctness/evidence work rather than cosmetic prompt versions. Current follow-through reproduced/fixed JSON-import ambiguity and missing action metadata, added exact archive replay with explicit limitations, and documented reviewer support judgments. Final suite: 207 tests in 35.786 seconds. No synthesis or scientific-quality promotion is justified. Valid v1–v5 reviews remain supported; v6 reports are re-audited as diagnostics, not imported as an invented app proposal format. [Review guide](ABSTRACT_REVIEW_GUIDE.md).

## C2 — Quote-first abstract analysis (operational; quality acceptance partial)

The user approved improvements after the original failed benchmark. That prior follow-up used `abstract-quotes-v2`: explicit field definitions, conservative English sentence eligibility, whole-source quote selection, abstention and pre-inference refusal of obvious instructions. Saved v1 drafts and mixed-version JSON still reopen with original prompts/claims. Eight real local generations were evaluated with fresh/original synthetic cases and temporary review UI: selected quotes improved, but available information was omitted. Final regression: 150 tests. The [v2 report](QUOTE_FIRST_C2_2026-10-20.md) records exact outcomes, compatibility and limitations. No runtime/model/package change or synthesis was introduced.

The current workspace adds strict six-field generated-proposal validation, paper/run/evidence binding, model/digest/runtime/prompt/settings provenance, exact excerpts and conservative numeric-literal checks. Statements, interpretations and missing information remain explicit. AI proposals stay separate from reviewer notes, start pending and require human checking and a reviewer note before acceptance. JSON preserves all proposals; separate comparison `ai_` columns include only the latest accepted proposal. AI reviews use format version 2; existing version-one C1 reviews still reopen. No SQLite/schema changes.

The loopback-only CPU adapter is wired into explicit review-tab actions, with no app-managed downloads/startup, external model URL or automatic generation. Missing/oversize abstracts and invalid/model-failure responses preserve existing work. The user approved installing Ollama 0.40.6 CLI and one Qwen model. Six real synthetic generations and temporary review-UI checks now verify actual operation and sampled resource use. **Model-quality acceptance failed: field misassignment and an injected false claim were observed.** See [C2 handover](PHASE_C_C2_HANDOVER.md), [setup](LOCAL_MODEL_SETUP.md) and [real benchmark](LOCAL_ANALYSIS_BENCHMARK_2026-10-20.md). C2 quality gates and full Phase C remain incomplete; no prompt change or additional model was introduced during the setup/benchmark.

## C1 — Review workspace and evidence contracts (implemented)

The Literature review tab starts from the latest nonempty captured discovery run, rather than the accumulated library. It requires a review question and explicit inclusion/exclusion criteria. Search filters do not count as screening decisions. All candidates start pending, including those without abstracts.

The review copies the run manifest, settings, query, timestamps, provider statuses, coverage limits, records and provenance. It keeps the run ID, record keys, DOI, authors and source observations. A subsequent search cannot replace that snapshot. A SHA-256 comparison detects accidental changes to the captured evidence; it is not an authenticity signature or proof of source truth. The original merged metadata still has unresolved per-field attribution/conflict limitations.

Screening choices are pending, include, exclude and uncertain. Include/exclude/uncertain require reasons. Each paper has six reviewer-authored summary fields, initially marked missing; C2-generated proposals are separate. A nonmissing note must be labelled paper-statement or interpretation and have an exact excerpt present in that paper's captured abstract. A match proves text presence only: a human still evaluates whether the excerpt supports the note. Metadata-only candidates cannot acquire abstract content claims. Missing means not recorded in available evidence, not that the study lacks a method/result.

The comparison table contains all candidates, their individual screening decisions, bibliographic identifiers, evidence depth, field notes, claim kinds and excerpts. It is a worksheet, not an automated literature synthesis or a completed systematic review. No full-text page or section citations are manufactured.

## Saving and reopening

Work stays in Streamlit session memory. Download review JSON before closing/restarting; there is no automatic save. JSON includes the original run, protocol, current decisions, current notes and timestamps. It can be reopened through the uploader when no review is active, without repeating searches. Reopening validates format, snapshot hash, candidate keys, screening reasons and exact-excerpt notes; invalid imports produce a generic error without echoing research text. Limit: 10 MiB. Imported work is data, not executable instructions. Extra unrecognized fields are discarded and current limitation/default-rule labels are regenerated.

Comparison CSV is a derived, portable worksheet; JSON is the complete workspace. The CSV uses run/record IDs to join the captured manifest and source observations in JSON. JSON import does not authenticate scientific content or its author. A deliberately edited file with a recalculated digest cannot be detected as a forgery. One review is active per session; starting another currently requires a fresh session after saving the first. Current decisions replace previous decisions; a chronological revision/audit trail and simultaneous reviews are not implemented.

No review data is written to SQLite. Discovery retains its existing normal application behavior. No production schema change, dependency installation or new model service is part of C1.

## Verification

Final C1 verification: `python -m unittest discover -s tests -v` passed **105 tests in 33.131 seconds** on a stable source/test snapshot. All 18 active Python files compiled; existing app helper/storage ASTs and protected-file hashes matched the baseline. Production data, historical scripts, requirements and repository instructions were preserved. No installation, Git action or live request was performed. Browser transfer/layout remains unverified. Machine-readable evidence: [C1 verification](PHASE_C_C1_2026-10-20.json).

- Baseline: `python -m unittest discover -s tests -v` passed 92 tests in 26.795 seconds.
- Ten pure review tests cover deep snapshots, partial runs, identical titles, protocol requirements, candidate identity/provenance, reason requirements, abstract-only evidence, invalid claims, mutation detection, Unicode JSON reopening/CSV, malformed inputs and import size limits.
- Three additional isolated AppTest cases exercise protocol validation, screening reasons, evidence-note exports, paper-specific form state, missing-abstract controls, later-search isolation and rendering a restored workspace in a new session.
- UI tests retain temporary application copies, guarded temporary SQLite and blocked live HTTP. No production database is opened by tests.
- Full-suite result and protected-file/syntax checks are recorded in [Project Status](PROJECT_STATUS.md) and [Testing](TESTING.md).

Browser upload/download transfer, live layout, maximum-size workspace performance and independent scientific correctness have not been verified. The headless tests verify the bytes passed to downloads, pure reopening validation and restored-session rendering; they do not simulate an actual browser file upload.

## Remaining Phase C work

1. Improve/evaluate field coverage and abstention on broader independent samples; handle segmentation/uncued evidence conservatively. V5 reaches public prose but wrongly assigns source sentences to roles and fills unsupported fields; its public quality gate remains unmet. Retain old protocol builders for saved work; no automatic filling from keyword cues.
2. Expand adjudicated actual summaries for field relevance, claim support, missingness, wrong-paper evidence, numerical distortions and contradiction/injection behavior. Existing lexical contracts cannot establish semantic support or general research quality.
3. Build cited synthesis of included studies, comparison by theme/method, uncertainty and contradictions. Evaluate citation and claim support separately from textual excerpt matching. Do not call this a systematic review without the relevant protocol and documented screening.
4. Add legally accessible full text with access/licence metadata, document identity, extraction quality and real passage locations. Abstract analysis must never be relabelled full-text analysis.
5. Evaluate resumable work, revision history and multiple reviews. Persistent database changes remain separately gated by the migration/backup policy.

Phase C is in progress. C1 does not complete AI analysis, synthesis, full-text support or the broader research mission.
