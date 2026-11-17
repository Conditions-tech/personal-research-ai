# Roadmap

Current continuation (2026-10-25): finish only the five original unattempted Qwen3 cases using the tested recovery controller and existing automatic supervisor when the unchanged physical-RAM gate passes. Low memory leaves a resumable waiting state, with no repeated ready coordination. Ledger remains 7/12. [Current evidence and boundaries](C2_QWEN3_CONTINUATION_2026-10-25.md).

Current 2026-10-24 boundary: five frozen Qwen3 cases remain unattempted under the original 12-attempt cap. The seven existing charged responses were reconciled without retries or fabricated outcomes. RAM below 5.5 GiB blocks loading; use the [current evidence report](C2_QWEN3_STATUS_2026-10-24.md), preserve Qwen2.5/v3, and keep scientific adjudication/full text/synthesis separate.

Current bounded next step: complete the already approved frozen Qwen3 pilot only after actual available RAM reaches 5.5 GiB. Download and installed metadata are verified; actual generations resumed after the original pre-load block. The [live report](C2_QWEN3_LIVE_PILOT_2026-10-21.md) records current progress. Preserve Qwen2.5/v3 default and do not infer scientific quality from installation or test success. [Resume evidence](C2_QWEN3_PILOT_2026-10-21.md).

The user's master directive authorizes incremental work toward the roadmap, with small, tested changes and persistent status. It does not authorize destructive data operations, unapproved schema changes, package installation, paid services, significant architecture replacement, or unnecessary live API calls. Do not treat a completed milestone as completion of the product.

The target is the full [ten-stage research pipeline](MISSION.md): topic input, discovery, literature review, individual analysis, deep research/gaps, ideas, solution verification, writing, quality/publication preparation, and submission/revision support. This expands the earlier three-workflow direction. Complete and verify discovery first, then build the dependent workflows incrementally. The stage numbers describe the user's research journey; the phases below describe implementation order, not ten required model deployments.

## Master phases and current position

1. **Phase A - Baseline and stability:** audit actual source/tests, filtering, errors, deduplication and storage; preserve production records. The inspected baseline had 57 tests, and current acceptance passed 74. Known gaps remain documented.
2. **Phase B - Topic and Literature Discovery (bounded acceptance complete; stages 1-2):** basic topic entry, source adapters, bounded pagination, optional historical bounds, count/status reporting, local filters, deduplication/storage, run settings/provenance/exports and conservative failure/cooldown handling are verified. [Acceptance](PHASE_B_ACCEPTANCE.md) separates those gates from unverified recall/coverage. Topic expansion, resumable bulk search and comprehensive coverage evaluation remain optional future enhancements.
3. **Phase C - Literature Review and Paper Analysis (in progress; stages 3-4):** define summary rules and evidence/output contracts; add screening records, abstract-first individual analysis, comparison tables and cited synthesis. Clearly label evidence depth; accessible licensed full text follows. Literature review and individual analysis feed each other. Evaluate suitable model backends as needed here.
4. **Phase D - Deep Research and Gaps (stage 5):** evidence-backed limitations/questions, contradictions, candidate gaps, related-work checks and uncertainty. Candidate gaps are not verified novelty.
5. **Phase E - Ideas and Solution Verification (stages 6-7):** rank ideas by supporting evidence, novelty checks, feasibility and resources; develop appropriate methods/experiments and reproducible baseline comparisons or proofs. Separate planned, executed and independently checked evidence. The user retains control of the research direction and substantive claims.
6. **Phase F - Writing and Publication Support (stages 8-10):** draft from actual evidence/results, validate citations and manuscript consistency, prepare for the target venue, support the user's final review and authorized submission, and assist with revisions. Never fabricate results or guarantee acceptance.
7. **Phase G - Integration and User-Directed Expansion:** integrate independently tested engines through a coordinator with shared provenance, decisions, configuration, history and exports. Keep backends swappable, evaluate quality/resources/licences throughout development, and support future user-defined modules. The inherited target is i3-8100/8 GB/integrated graphics; no paid compute, package installation or training without applicable approval.

## Next candidates

The latest [single-role pilot](C2_SINGLE_ROLE_EVALUATION_2026-10-21.md) exhausted its separate 12-call allocation and failed field-quality acceptance (4/6 development, 2/6 holdout). Conservative v3 is restored as default; v4/v5 remain readable and v6 remains diagnostic. Backend-independent work fixed reproduced review-import ambiguity/traceability defects and added archive/support audits plus the review guide. Keep future quality work distinct from synthesis; no automatic prompt-version promotion or extra inference/model download is implied.

Phase C is active after the user's approval. [Phase C plan](PHASE_C_PLAN.md) describes the implemented C1 screening/evidence workspace and the user-approved summary fields. A/B acceptance and its limitations remain preserved.

1. Validate/improve C2 field coverage, segmentation and abstention on broader/independent samples. The approved [quote-first follow-up](QUOTE_FIRST_C2_2026-10-20.md) is implemented with saved-v1 compatibility and real original/fresh evaluations; selected quotes improved but completeness remains partial. Do not automatically replace abstentions or infer broad scientific accuracy. Keep protocol versions stable; no extra model download is included.
2. Build cited synthesis of screened included papers and comparison of themes/methods; follow with legally accessible full text and real passage references.
3. Optional discovery/persistence improvements remain separate: wider recall benchmarks, shared throttling/resumption, multiple saved reviews and revision history. Schema changes still require migration/backup approval.

## Completed approved task

- Completed [bounded Phase B acceptance](PHASE_B_ACCEPTANCE.md): optional historical scope, real small page/cursor checks, explicit count semantics, native source/page evidence and shared run exports through existing notes, plus 429 cooldowns and preservation of earlier pages/legacy data. All 80 automated tests passed; live sample failures and positive known-work classification are disclosed. No production schema/data, historical-script, package or Git change.

- Implemented [bounded pagination and retrieval status](RETRIEVAL_DESIGN.md) under the user's renewed master goal: OpenAlex basic pages, Crossref cursors, up to 250 raw entries/five pages per source, explicit complete/partial/error statuses, earlier-page preservation, raw/filtered/run-unique count distinctions and reproducible settings in the existing history note. Replaced deprecated Streamlit width arguments. No dependencies or schema changes.

- Extracted a reusable discovery package with OpenAlex/Crossref adapters, injected transport, and a common single-batch count contract. Existing request/filter/UI/storage behavior is preserved. Eight new adapter tests and all 39 tests passed; no live calls, schema changes, dependencies, or pagination were added.

- Completed a [controlled live smoke check](LIVE_SMOKE_2026-10-20.md) with seven public requests and temporary storage. Sampled journal/conference filtering, count pass-through, natural empty responses, and one cross-provider duplicate passed. UI replay and simulated error checks were separate from live requests. Coverage, exhaustive retrieval, and real outage behavior remain unverified.

- Corrected provider-aware journal/conference categories and default selection, retained raw stored types and request limits, replaced unrealistic type fixtures, and clarified candidate counts. The subsequent live check above adds sampled evidence; corpus coverage remains unverified.
- Added seven isolated Streamlit UI smoke tests for initialization, validation, mocked searches, persistence/history/deduplication, browsing, CSV payloads, and provider failure/empty states. They use unchanged temporary app copies and reject external database connections and unmocked HTTP. Browser rendering and actual download transfer remain untested.
- Documented the [schema-version and migration policy](SCHEMA_MIGRATIONS.md), including adoption criteria, isolated testing, staged upgrades, approval, and rollback. No runner, schema change, or database version assignment was implemented.
- Verified the documented SQLite backup, staged restore, and rollback procedure against disposable app-schema databases, including committed WAL data and refusal cases. No production backup or restore was performed.
- The publication end-year default follows the app host's local calendar year, with an isolated year-rollover test. The 1900â€“2100 bounds and 2015 start-year default remain unchanged.
- Added shared year/type filtering with bounded requests; the initial type-equivalence assumptions in those fixtures were subsequently corrected by the provider-aware category task above. No pagination was added.

## Deferred implementation

Bounded discovery acceptance is complete; exhaustive/resumable retrieval and comprehensive historical coverage are not claimed. Literature review, AI paper analysis, gap synthesis, idea generation, solution verification, manuscript writing, quality/publication preparation and submission support are planned, not implemented. Local abstract-only model integration is present; quality acceptance remains partial. Keep the next phase separately scoped and tested; production schema/data changes retain explicit migration/backup approval. The user's [Mission](MISSION.md) remains active until FINISH.
