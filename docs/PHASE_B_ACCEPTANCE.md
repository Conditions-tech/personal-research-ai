# Phase B acceptance - bounded Literature Discovery

Date: 2026-10-20. Scope: the local two-provider metadata-discovery workflow within its explicit budgets. This does not certify exhaustive retrieval, scientific relevance/recall, universal historical coverage, or any later AI workflow.

Subsequent user-requested review: [Phase A/B re-audit](AB_AUDIT_2026-10-20.md) reproduced and corrected evidence-integrity defects outside the earlier 74-test cases. Consult its newer verification and [Phase C Handover](PHASE_C_HANDOVER.md) before advancing. The matrix below preserves the earlier milestone's evidence; it is not an assertion that no bugs can remain.

## Acceptance evidence

| Requirement | Evidence | Result |
| --- | --- | --- |
| Build on existing pagination/settings | Audited actual retrieval.py/provider/UI/history implementation; baseline 57 tests passed in 16.658 s. Existing budgets/page/cursor methods retained. Reviewed newer metadata/selection/null-enrichment fixes found during final verification. | Pass |
| Historical search with optional bounds | Independently optional UI bounds, CE 1-9999 controls, early-year formatting, missing years admitted only without bounds; helper/retrieval/UI tests. Live no-lower-bound OpenAlex query retained 1735/1791. Crossref optional/local date handling is tested offline. | Pass |
| Live pagination for both sources | Two numbered pages for OpenAlex and two latest-cursor pages for Crossref, for journal and conference-oriented public queries; raw budgets stopped as partial. See the separate live report and original failed sample probes. | Pass for traversal; recall unverified |
| Publication-type filtering | Provider-native mocks and live positive journal examples; live OpenAlex conference entries; Crossref known CVPR proceedings-article retained as conference and rejected as journal. Other live query slices contained only journal types and were correctly excluded. | Pass for metadata classification; query sampling limitations disclosed |
| Accurate count semantics | Provider totals remain source-scoped/unknown when absent. Accepted raw entries, saveable filtered observations, run/source unique keys, duplicate entries, actual new insertions and accumulated library metrics are separate. Contradictory final totals in either direction remain partial. Existing-library, keyless/untitled and duplicate tests pass. | Pass |
| Traceable settings/provenance/exports | Shared run ID, timestamps, query, nullable year settings, types/budgets/statuses, native IDs/URLs and source/page evidence in version-two existing note field. ZIP/CSV/JSON round trips; library CSV now includes record_key and identical titles select their own record evidence. | Pass |
| Provider failures/timeouts/rate limits | First/later HTTP/access/network/JSON/malformed/timeouts tested; valid pages survive, other source continues, errors sanitized. 429 Retry-After dates/numbers/default and session cooldown tested; no automatic retry. No live fault was provoked. | Pass offline; real fault incidence unverified |
| Clear partial/coverage warnings | Budget/cursor/inconsistent-total/failure stops are incomplete; source exhaustion is scoped. UI, run manifests and docs disclose missing metadata, ranking, history window, dates, dedup heuristics and differing totals. | Pass |
| Preserve data, schema and boundaries | Schema initialization unchanged; storage changes only fill missing NULL metadata, preserve nonempty evidence/first timestamps, and expose record_key on read. Rollback/legacy tests and protected hashes pass. No production connection, schema change, installation, paid service, Git operation or historical-script edit. | Pass |
| Full regression and handover | 80 tests passed in 26.302 s on Python 3.14.7/Streamlit 1.66.0; syntax, local links, snapshot diff and protected-file review. | Pass |

The implemented **bounded Phase B acceptance scope is complete**. There is no unresolved operational blocker within those gates. The stronger positive-conference-in-each-tiny-query-window probes did not pass and remain explicitly failed in their live JSON artifacts; their result is not a claim of broad search relevance/recall. A separate known-work lookup established positive Crossref classification. Do not describe all live harness assertions as passing.

During final verification the shared workspace received additional metadata/selection/storage tests and fixes. An intermediate mixed-version run failed 15 assertions; it is not the accepted result. The final check re-reviewed the newer work: scalar/malformed titles and non-integer/out-of-SQLite-range years are rejected, unbounded integer years are retained, year zero is distinct from missing year in new fallback keys, NULL metadata can be filled without replacing existing evidence, failed saves roll back, and identical-title papers select by key. No Phase C analysis feature was introduced. Earlier statements that all storage/helper functions were unchanged are superseded by these explicit fixes.

## Files changed

- Application/discovery: `app.py`, `discovery/metadata.py`, `discovery/providers.py`, `discovery/retrieval.py`, new `discovery/runs.py`.
- Tests: updated `test_app.py`, `test_discovery.py`, `test_retrieval.py`, `test_ui.py`; new `test_runs.py` and `test_live_guard.py`. `test_backup.py` is unchanged.
- Live tooling/evidence: new `tools/live_discovery_smoke.py`, the live-pagination Markdown report, primary/supplement/citation aggregate JSONs, and ordering/known-work diagnostic JSONs.
- Handover: README plus Architecture, Retrieval Design, Testing, Project Status, Roadmap, Decisions, Changelog and this acceptance matrix. Mission, backup/migration policies, AGENTS.md and requirements are unchanged.

## Remaining limits

- Providers do not cover every publication. The absence of a selected type in a bounded window is not evidence of absence from the source. Crossref bibliographic query rankings and native classifications can differ substantially from OpenAlex.
- Live testing sampled two-entry pages, not every UI budget, discipline, historical period, language, metadata shape or rate-limit failure. Reported totals were checked for pass-through and consistency, not independently counted.
- Retrieval remains capped at 250 raw entries/five requests per source with a between-request time budget. There is no hard wall-clock cancellation or resumption. A full page at the cap stays partial.
- Unknown dates/types and unusable titles/keys limit filtered results. Crossref print/online date precedence is unchanged. CE-bound controls do not provide a special BCE date-entry mode; unbounded requests impose no client year floor.
- Deduplication is DOI or normalized title/year matching, not a verified record-linkage system. No natural cross-source duplicate occurred in this live sample; synthetic cross-source and live replay checks are separate evidence.
- New fallback keys distinguish integer year zero from unknown year. Existing keys are not rewritten; any old zero-year/unknown-key collision is not retroactively reconciled.
- New provenance persists in existing history notes, but no raw payload archive or restart-restored paper snapshot is created. The latest ZIP is session-local until downloaded; displayed history/export covers 100 attempts. Older notes remain unchanged. Paper/history transactions are not atomic against crashes.
- Cooldowns are session-specific; automated retry/backoff, shared concurrent-user throttling, browser rendering/download transfer, CI and other runtime versions remain unverified or unimplemented.

These are explicit limits of this bounded metadata milestone, not promises of completed research coverage. Further discovery enhancements can be pursued separately. **Phase C - Literature Review and Paper Analysis remains separate and unimplemented.** Its next task is to define screening/evidence-depth, configurable summary/output contracts and evaluation examples before selecting or integrating a model.

See [live evidence](LIVE_PAGINATION_2026-10-20.md), [Testing](TESTING.md), [Architecture](ARCHITECTURE.md), [Retrieval Design](RETRIEVAL_DESIGN.md), and [Roadmap](ROADMAP.md).
