# Phase A/B knowledge handover to Phase C

Follow-on: C1 screening/manual notes and C2 reviewer approval are implemented. The installed local Ollama/Qwen backend now uses versioned quote-first analysis; saved v1 work remains compatible. The [original failed benchmark](LOCAL_ANALYSIS_BENCHMARK_2026-10-20.md) is preserved. The approved [v2 follow-up](QUOTE_FIRST_C2_2026-10-20.md) improves selected-field fidelity but retains omissions and heuristic limitations. Read [C2 handover](PHASE_C_C2_HANDOVER.md). Statements below describe the A/B starting point; Phase C remains incomplete.

Prepared 2026-10-20 during the user's requested re-audit. This is an implementation handover, not an implementation of Phase C or a certification of bug-free software. Read [Mission](MISSION.md), [A/B Audit](AB_AUDIT_2026-10-20.md), [Phase B acceptance](PHASE_B_ACCEPTANCE.md), and [Architecture](ARCHITECTURE.md) together.

Latest verification: the [second A/B re-audit](AB_AUDIT_2_2026-10-20.md) passed 92 tests and strengthened metadata shapes and run-context attribution. The first audit's 80-test evidence remains a prior milestone.

## Verified starting point

`app.py` owns the Streamlit interface and SQLite operations. `discovery.metadata` owns normalization, keys and classification; `discovery.providers` owns transport and source pages; `discovery.retrieval` owns budgets, statuses, counts, timestamps and per-page observations; `discovery.runs` owns run merging/manifests/history notes and ZIP exports. Import discovery normally. Never import `app.py` into a new workflow/test: its module-scope code creates directories and runs UI/storage operations.

No AI backend, literature screening system, generated summary, accessible-full-text retriever or research-gap evaluator exists. Existing abstracts are third-party metadata. Phase C must begin with explicit evidence-depth, screening, summary and evaluation contracts; no model has been selected or benchmarked.

## Input and identity contract

Prefer a captured run's `{manifest, records}` from `make_run`, or the downloaded ZIP containing `manifest.json`, `records.csv` and `provenance.csv`. These describe this run, while the library is an accumulated, merged collection from many searches. The latest run exists in Streamlit session state and disappears on restart unless downloaded. History notes preserve settings/counts/provenance, not record/abstract snapshots; they cannot reconstruct a lost complete run.

Use measured `RetrievalResult` objects from `retrieve`: they capture the actual query and canonical year/type/budget settings. `make_run` and history serialization reject relabelling those results with other settings/queries, duplicate provider results, impossible insertion counts, or attachment to a different provider attempt. Legacy tuple searches do not capture this context; do not manufacture contextless measured results for the handover. A skipped cooldown attempt has zero requests/accepted pages and planned settings. These in-memory checks prevent ordinary misassociation, not deliberate tampering; keep evidence read-only.

Input bounds accept CE integer years 1-9999 or null and supported category selections, validated before network I/O. Provider text fields are strings or missing values; venue lists contain strings. Structured non-text data and invalid/overlapping abstract positions reject their page as invalid. Missing author-name components remain missing without rejecting otherwise valid Crossref metadata. Unbounded source integer years retain the first audit's storage-compatible policy. OpenAlex DOI record links use normalized resolver URLs. None of this validates DOI existence or the truth of source claims.

| Input | Meaning and consumer obligations |
| --- | --- |
| `record_key` | Unique metadata key in a run/library: normalized DOI, otherwise normalized title plus year. Join records/provenance and select papers using this key; titles are not identifiers. DOI-less and DOI-bearing versions may remain separate. |
| `title`, `authors`, `doi`, `year`, `url` | Bibliographic metadata, not independent verification of a publication or its contents. Missing values are explicit; CSV readers must handle empty fields. DOI is normalized lowercase without a resolver prefix. `year` is an integer or null in normalized records; reject malformed non-integer years rather than coercing evidence. |
| `abstract` | Available abstract text, or an empty string. OpenAlex reconstruction and Crossref tag removal are metadata transformations, not a PDF/full-text extraction. Crossref entities/formatting may still require careful handling. |
| `work_type`, `publication_type`, `venue` | Provider-native type and shared classification/venue evidence. Journal papers combine articles and reviews; Crossref journal content cannot establish that a paper is an original article or a literature review. Missing classification is not proof that a paper is ineligible. |
| `source` | Providers observed for the merged record. First nonempty fields win during a run merge; source names are combined. Conflicting fields are not reconciled or scientifically adjudicated. |
| `manifest.settings` | Nullable year bounds, publication categories and raw/page/time budgets. Read these before making coverage statements. The current UI still defaults to a 2015 lower bound/current-year upper bound; a historical search requires removing/changing that lower bound. Both bounds disabled admits undated metadata and does not impose the UI's CE input range on source years. |
| `manifest.providers` | Each provider's scoped total, counts/status, timestamps and stop reason. Never sum reported provider totals as a worldwide count. Preserve unknown totals as null. |
| `manifest.counts` | Raw accepted entries, filtered observations, unique run keys, duplicate observations and new library insertions. These are different populations. New insertion count can be unknown for an unsaved programmatic run. |
| `manifest.provenance` / `provenance.csv` | Per-retained-observation key, provider, native ID/URL, types, year/venue and page. Many observations may join to one record. This is record-level provenance, not exact abstract-sentence/full-text passage or per-merged-field attribution. |

Library CSV now also includes `record_key`; consume CSV by column names, not positional assumptions. Its records may predate the new provenance/history format. Existing library titles and nonempty fields are preserved even when a later provider disagrees. Legacy keys/history are not migrated; the audit corrected zero-valued source-year key handling only for newly normalized records.

## Retrieval and scientific interpretation

- Default search budgets are 10 raw entries per source; UI options stop at 250, at most five requests per source. The time budget is checked between requests, and a requests timeout is an inactivity timeout, not a hard process deadline.
- `complete` means a short final source page with no changing/contradictory known total. An unknown total can remain null on a completed traversal. `partial` means a budget or interruption/inconsistency prevented establishing exhaustion; `error` means no valid first page. A complete run still cannot establish worldwide research coverage or relevance.
- Crossref totals are broad bibliographic query matches before local filters; OpenAlex totals are server-filtered candidates before local venue/category checks. Indexing, query interpretation and ranking differ. Neither number is the number of screened, relevant studies.
- Counts and provenance include successfully parsed pages only. A malformed title/year/envelope causes its page to be rejected as a unit; earlier valid pages survive. Missing years remain allowed with no bounds; an active bound excludes them. Missing abstracts never justify inventing results or limitations.
- A rate limit stops that provider, records a sanitized cooldown, preserves previous pages and lets the other provider proceed. Cooldowns are per session; no automatic retry or shared concurrency limiter is implemented.
- The dated live report verified small real traversals and some classification examples. Three positive-conference-in-window probes failed; a known DOI lookup verified classification separately. Do not treat those failures as passing or as proof that conference work is absent. No post-audit live query was made.

## Phase C behavior requirements

1. Preserve the run ID, settings, search date, record key, DOI/provider links and evidence depth with each screening decision, summary and comparison.
2. Keep screening inclusion/exclusion reasons separate from search/type filters. A candidate record is not automatically a relevant included study. A systematic-review label requires its own documented protocol and screening process.
3. Label outputs `metadata-only`, `abstract-based` or later `full-text-based` according to the material actually available. A missing abstract is an explicit analysis limitation.
4. Distinguish a paper's explicit statements from model interpretation and missing information. Never invent methods, datasets, numerical results, limitations, quotes, citations or passage locations. Metadata alone cannot validate an experiment or novelty.
5. Attach paper citations and available evidence to claims. Record-level source/page observations cannot support invented page/section attribution. Conflicting metadata and absent per-field attribution must remain disclosed.
6. Keep original records/evidence immutable during analysis; put generated outputs and screening decisions in a separately designed structure. The user's detailed personal summary rules remain to be specified; defaults must be clearly labelled.
7. Add evaluations for missing abstracts, contradictory metadata, identical titles with different IDs, incomplete retrieval, unsupported claims and source attribution before declaring an analysis workflow reliable.

## Data and test boundaries

`data/research.db` is private production data and must not be used by tests. SQLite paper updates now fill SQL NULL as well as empty metadata, preserve nonempty fields and the first-save timestamp, and merge sources. A failed paper batch rolls back its inserts/updates. Paper saving and search history saving still use separate transactions; a process failure can leave them inconsistent. No migration/version runner or crash-atomic run persistence exists.

Use pure discovery tests with blocked HTTP and injected fixtures/clocks. UI tests execute a byte-for-byte temporary app copy, reject external SQLite paths and block live HTTP. Backup/restore is rehearsed only with disposable databases. No production backup/restore, schema change, package installation, paid service or Git action is authorized by this handover. Production schema changes retain the documented explicit approval/backup/migration boundary.

Browser layout/download transfer, real failure/rate-limit incidence, multi-user races, power-loss/disk-full behavior, broad relevance/coverage, full dependency compatibility and independent scientific correctness remain unverified. These limits travel with the handover; adding Phase C cannot retroactively resolve them.
