# Controlled live discovery smoke test: 2026-10-20

This approved check exercised the existing discovery helpers against public OpenAlex and Crossref responses. It changed no application code, limits, schema, production records, historical scripts, or dependencies. It establishes sampled behavior, not research coverage or exhaustive retrieval.

## Method and request budget

Seven serial GET requests, no retries or pagination, used the application's existing user agent and 45-second timeout. Each selected limit was **5** and each year range was **1900–2026 inclusive**. Request starts were at least two seconds apart. No keys, accounts, or paid services were added. Requests ran on 2026-10-20 at 01:53:39–01:55:30 Bangladesh time (2026-10-19 at 19:53:39–19:55:30 UTC).

The initial six requests covered two research queries and a deliberately nonexistent query. Crossref returned only book chapters for the first journal query, so one additional journal query supplied positive journal-article evidence. Every request returned HTTP **200**.

The one-off harness parsed the actual app's function/constant definitions without importing its module-level UI. Database paths were explicitly temporary, with a guard rejecting connections outside the disposable root or using SQLite URIs. Real normalizers, local filters, persistence, and deduplication ran against those temporary databases. Responses were held in memory for headless UI replay; raw payloads and temporary databases were discarded. No production database connection was made.

OpenAlex requests used `search`, `per_page=5`, and the unchanged `select=id,doi,title,publication_year,type,authorships,primary_location,abstract_inverted_index`. All included `from_publication_date:1900-01-01,to_publication_date:2026-12-31`. Journal selection added `type:article|review`; conference selection added `type:article|conference-paper|review`; clearing types omitted that filter. Crossref requests used only `query.bibliographic` and `rows=5`, with year/category filtering locally.

## Live outcomes

| Provider | Public query | Category | Provider total | Raw batch | After local filters |
| --- | --- | --- | ---: | ---: | ---: |
| OpenAlex | climate change | Journal | 3,546,367 | 5 | 4 |
| Crossref | climate change | Journal | 1,408,203 | 5 | 0 |
| OpenAlex | Deep Residual Learning for Image Recognition | Conference | 240,557 | 5 | 2 |
| Crossref | Deep Residual Learning for Image Recognition | Conference | 4,670,276 | 5 | 3 |
| OpenAlex | zzqvx8f7c4b2dsmoketestnomatch | Types cleared | 0 | 0 | 0 |
| Crossref | zzqvx8f7c4b2dsmoketestnomatch | Types cleared | 0 | 0 | 0 |
| Crossref | The Hallmarks of Cancer | Journal | 3,182,511 | 5 | 4 |

Observed classification checks passed:

- OpenAlex's four retained journal records were native `article` with explicit `journal` primary-source metadata. The raw batch contained five articles; one was excluded by the selected filters.
- Crossref's first journal batch contained five `book-chapter` records, all correctly excluded. The additional query contained four `journal-article` records, all retained, and one `component`, excluded. A zero locally filtered batch does not establish that the provider has no matching journal papers.
- OpenAlex's conference batch contained two native `conference-paper` records with conference source metadata, both retained; three `article` candidates were excluded. Crossref retained three `proceedings-article` records and excluded one `posted-content` and one `journal-article`.
- All retained records had normalized years within 1900–2026. This broad range did not exercise narrow-year exclusion, date precedence, or historical boundary cases live; those remain mocked-test coverage.
- Both deliberate no-match requests returned total zero and empty batches, without errors or further requests.

## Counts, persistence, and duplicates

All seven helper-returned totals exactly matched their provider response fields (`meta.count` or `message.total-results`). This verifies pass-through, not the correctness or completeness of provider estimates. OpenAlex totals follow server year/candidate filters but precede local category checks; Crossref totals precede local year/category filters. They cannot be summed into a global selected-paper count.

The first six requests produced **9 filtered entries** and **8 unique keys**. Saving them into a fresh temporary database inserted eight rows. One key was shared across providers and its saved source became `Crossref;OpenAlex`. Saving the same entries again inserted **0** rows and left eight. The additional Crossref journal batch separately inserted four unique rows and zero on replay. This checks one natural cross-provider duplicate and exact replay; it does not establish general deduplication recall or precision.

Three AppTest runs replayed the captured live response pairs for journal, conference, and no-match searches using unchanged temporary app copies, guarded SQLite paths, and blocked live HTTP. These were **offline UI replays of live payloads**, not further live requests or browser tests. Provider success messages and saved history matched the table's totals and filtered counts. Journal search saved four unique rows; conference search saved four from five filtered entries; the no-match search saved none and recorded two successful zero-count attempts with a no-results warning. No uncaught exceptions occurred.

The UI labels OpenAlex totals as “candidate matches before local filters” and Crossref totals as “query matches before local filters.” Its “retrieved” value is after local filtering and before deduplication. Raw fetched-batch counts are **not displayed or stored**. “Unique saved records” is the accumulated local library, not an exhaustive query total. The harness measured raw batches independently for this report.

## Error and empty behavior

No live transport, HTTP, authentication, or rate-limit failure occurred; none was deliberately provoked. Real failure behavior therefore remains unverified.

Four further offline AppTest runs covered two simulated OpenAlex timeouts and two synthetic empty-response pairs. For the timeout with the captured Crossref cancer response, the UI showed the OpenAlex error, recorded that attempt as `error` with unknown total and zero retrieved, continued Crossref successfully, and saved its four rows. For the timeout with the climate response, Crossref succeeded but retained zero; the UI showed both the provider error and no-results warning. Synthetic empty pairs showed successful zero-count history and the warning. All seven UI runs completed without uncaught exceptions. Existing Streamlit context/deprecation warnings remained.

## Verification and remaining limits

- The live classification, count pass-through, bounded-request, natural-empty, temporary persistence, and sampled duplicate checks passed. No observed application check failed.
- `python .live_smoke_check.py` and its single-query `--crossref-journal` follow-up exited successfully. These were disposable audit harnesses, removed after reporting; no live calls were added to automated tests.
- `python -m unittest discover -s tests -v` passed **31 tests** in 20.261 seconds on Python 3.14.7 with Streamlit 1.66.0. Tests used temporary data and mocks, not live APIs.
- SHA-256 comparisons confirmed unchanged application, production database, historical scripts, requirements, and all three automated-test files. Documentation changes were reviewed against pre-edit snapshots; Git remains uninitialized.
- Not established: complete coverage by discipline/year/provider, independent count accuracy, relevance ranking, article/review subtype accuracy, rare/malformed metadata, older conference records classified only through venue evidence, all publication categories, unrestricted historical retrieval, real service outages/429 responses, concurrency, browser rendering, or actual downloads. Provider data and ranking can change, so these exact totals are a dated observation.

The safest next task is to design bounded pagination and count/status semantics for approval before implementation. The design should address raw versus filtered versus unique counts, stopping budgets, partial completion, provider access limits, and reproducible search settings. No pagination or schema change is authorized or implemented by this report.
