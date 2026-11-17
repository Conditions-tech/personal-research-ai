# Personal Research AI

Current runtime status (2026-10-25): the approved local Ollama daemon is PID 11528, serves the exact pinned Qwen3 digest, and has no model loaded. The latest controller sample was about 4.13 GiB, below the unchanged 5.5 GiB gate; ledger remains 7/12 with five pending and no new inference. [Repair evidence and limits](docs/C2_QWEN3_RUNTIME_REPAIR_2026-10-25.md).

Final recovery regression: **242 tests passed in 37.760 seconds**; the 25 recovery tests use isolated state and mocked/blocked model HTTP.

Current continuation (2026-10-25): a tested bounded recovery controller now preserves the five pending Qwen3 cases for automatic supervision, without repeated ready replies. The live check remained below the unchanged 5.5 GiB gate; ledger stays **7/12**, with no new inference. [Current continuation, commands and limits](docs/C2_QWEN3_CONTINUATION_2026-10-25.md).

Prior resumption checkpoint (2026-10-24): **seven charged Qwen3 requests are reconciled with complete saved responses; five remain unattempted**. The unchanged 5.5 GiB RAM gate currently blocks loading. No request was repeated or uncharged, and Qwen2.5/v3 remains the app default. Fresh suite: **217 tests in 36.577 seconds**. [Current outcome and boundaries](docs/C2_QWEN3_STATUS_2026-10-24.md).

The separately approved [Qwen3 pilot](docs/C2_QWEN3_PILOT_2026-10-21.md) has downloaded the one additional model and verified runtime metadata. Actual generations have now resumed under the unchanged 5.5 GiB gate; the [live report](docs/C2_QWEN3_LIVE_PILOT_2026-10-21.md) separates outcomes from prior blocked checkpoints. No default change or scientific-quality promotion has occurred. At that checkpoint the regression suite passed **217 tests**; production data and historical files remain preserved.

The current Literature Discovery foundation for Personal Research AI searches and organizes scholarly metadata from OpenAlex and Crossref through a local Streamlit application. It stores results and search history in SQLite. Phase C adds screening, reviewer-authored evidence notes, exports and JSON reopening. Local C2 now uses versioned quote-first selection with the installed Ollama/Qwen backend and separate human-reviewed proposals. **Experimental public-abstract trials reached the installed model, but field accuracy remains unreliable; the conservative v3 selector is the app default.** Full-text analysis, synthesis and multi-model orchestration remain unimplemented.

The [single-role pilot](docs/C2_SINGLE_ROLE_EVALUATION_2026-10-21.md) failed field-quality acceptance despite exact source copying. The default is restored to conservative **v3**; saved v1–v5 work remains supported and v6 is diagnostic only. Offline follow-through fixed ambiguous review-JSON imports and missing action timestamps. That milestone passed **207 isolated tests**. See the [review guide](docs/ABSTRACT_REVIEW_GUIDE.md) for current screening, notes, proposal checking and save/reopen behavior. Phase C remains incomplete. The [acceptance-gap audit](docs/PHASE_C_ACCEPTANCE_GAPS.md) separates verified software from unresolved scientific-quality work.

Phase B has an importable `discovery` package: metadata normalization, source adapters and bounded retrieval run without Streamlit or SQLite. The interface and storage remain in `app.py`. Keep `app.py`, `discovery/` and `review/` together when copying or launching the project. Searches now paginate within explicit entry/page/time budgets and retain successful pages if a later request fails.

The full [ten-stage research goal](docs/MISSION.md) runs from topic input and discovery through literature review, paper analysis, research gaps, ideas, solution verification, writing and publication support. The current app implements the discovery foundation, basic topic entry and the first Phase C review workspace; later analysis and research stages remain in progress or planned. [Roadmap](docs/ROADMAP.md) records the development order and working agreement. See [Retrieval Design](docs/RETRIEVAL_DESIGN.md) for implemented budgets, statuses, provider access and coverage limits.

Before Phase C, read the [Phase A/B re-audit](docs/AB_AUDIT_2026-10-20.md) and [Phase C knowledge handover](docs/PHASE_C_HANDOVER.md). The audit corrected duplicate-title selection, NULL metadata enrichment and malformed evidence types. Library CSV includes the stable `record_key`; consumers should use column names. The [C2 handover](docs/PHASE_C_C2_HANDOVER.md), [original failed benchmark](docs/LOCAL_ANALYSIS_BENCHMARK_2026-10-20.md) and [quote-first follow-up](docs/QUOTE_FIRST_C2_2026-10-20.md) separate technical operation, selected-quote fidelity and remaining omissions.

The subsequent [second A/B audit](docs/AB_AUDIT_2_2026-10-20.md) verifies stricter optional metadata validation and actual search-context attribution for run/history exports. Passing the same query/settings to retrieval and run construction is now enforced; old history is preserved. Its final isolated suite passed 92 tests.

The target is local-first personal use on an i3-8100 with 8 GB RAM and integrated graphics. Keep models/providers swappable and evidence/resource/licence requirements explicit. The approved [local setup](docs/LOCAL_MODEL_SETUP.md) installed only Ollama 0.40.6 CLI and Qwen2.5 1.5B Q4_K_M, with cloud disabled and a loopback listener. The app never installs, pulls or starts a runtime/model itself and has no remote model-service option. Other installations/downloads still require approval.

## Prerequisites

- Windows with PowerShell.
- Python 3.14 is the interpreter currently selected by VS Code/Pylance in this workspace. No Python support range is declared by the project; other versions have not been verified here.
- Network access to the public OpenAlex and Crossref APIs when searching.

The selected interpreter is currently the system installation at `C:\Users\Niaz\AppData\Local\Programs\Python\Python314\python.exe`; no project virtual environment was detected during the audit. A local virtual environment is recommended for repeatable setup.

## Setup and launch (PowerShell)

From the project root:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

If the Python launcher does not recognize `-3.14`, create the environment with the full path to the verified interpreter:

```powershell
& 'C:\Users\Niaz\AppData\Local\Programs\Python\Python314\python.exe' -m venv .venv
```

Then activate and install as above. In VS Code, select `.venv\Scripts\python.exe` as the workspace interpreter. Running Streamlit with `python -m streamlit` ensures it uses the interpreter associated with the active shell.

## Usage

1. Enter a research topic and select the maximum fetched entries per service: 5, 10, 25, 50, 100 or 250 (default 10). This is a raw metadata budget before filtering and deduplication, not a target number of matching papers.
2. Set publication year bounds and publication types. The defaults remain 2015 to the current local year. Either year checkbox can remove its bound; both off searches without year bounds and includes missing-year metadata. Bounded controls accept CE years 1-9999. OpenAlex date parameters use four-digit years. Both providers' normalized results honor the enabled bounds and selected categories.
3. Start the search. OpenAlex receives year/native candidate-type filters and numbered pages; Crossref uses a bibliographic query, cursors and server-side year/type filters (start year widened by one; see below). Both apply exact local year/category checks. Retrieval stops at the raw budget, five pages, the between-request time budget, a final page, or a provider problem. Each source shows raw fetched entries, filtered records, status and stop reason; later-page failures retain earlier valid pages. A higher budget can reach matching papers on later pages, but does not guarantee more selected papers.
4. Browse or filter saved titles and abstracts, inspect available metadata, and download the current filtered view as CSV.
5. In Search history, download the displayed attempts/settings as JSON or the session's latest run bundle: manifest, deduplicated records CSV, and per-source/page provenance CSV. The bundle records run ID, query, settings, timestamps, counts, statuses, native source identifiers and observed metadata. It describes that run, separately from the accumulated library view.
6. Open Literature review, enter a review question and screening inclusion/exclusion criteria, then start a review of that captured run. Record decisions and reviewer-authored notes under the six default fields with exact abstract excerpts. AI proposals are separate: check the local backend, generate, inspect every field/excerpt, then accept or reject with a reviewer note. New proposals select source quotes using conservative English field cues; missing means no quote selected, not absent paper information. Obvious instruction-like abstracts are refused before inference. Unknown attacks, valid evidence omissions and heuristic errors remain possible. Saved v1 proposals retain their original interpretation/paraphrase behavior and reopen unchanged. Excerpt matching alone does not verify scientific support.
7. Download review JSON to save the workspace and comparison CSV for the worksheet. Only accepted AI claims enter separate `ai_` comparison columns; JSON retains pending/rejected proposals too. Work is session-only; reopen downloaded JSON in a fresh session to continue. C1 reviews remain version 1; AI work uses version 2 and requires the current app to reopen. See [Phase C guide](docs/PHASE_C_PLAN.md) for limits.

The library CSV includes record_key for traceability. Papers with identical titles are selected by their unique key and labelled with DOI/key evidence. New retrieval can fill previously NULL metadata without replacing existing nonempty values. New title/year keys distinguish year zero from missing year; existing saved keys are not rewritten.

The defaults are **Journal papers (articles and reviews)** and **Conference papers**. Categories translate provider metadata rather than assuming identical type labels:

| Selection | OpenAlex evidence | Crossref type |
| --- | --- | --- |
| Journal papers (articles and reviews) | `article` or `review` with primary source type `journal` | `journal-article` |
| Conference papers | Native `conference-paper`, or `article`/`review` with primary source type `conference` | `proceedings-article` |
| Book chapters | `book-chapter` | `book-chapter` |
| Dissertations | `dissertation` | `dissertation` |
| Preprints / posted content | `preprint` | `posted-content` |

These are metadata-based categories, not inferred research classifications. Crossref does not distinguish original articles from literature reviews in `journal-article`, which may also contain other journal content. Its `peer-review` type is not treated as a literature review. OpenAlex's newer conference types are still rolling out; explicit conference venue metadata supports older `article`/`review` records. A missing/unsupported type, or an OpenAlex article/review without journal/conference venue evidence, stays unclassified. Clear the selection to include such records. The last category includes all Crossref posted content, not only preprints. The mappings follow the providers' [work types](https://help.openalex.org/data/work-types/), [source types](https://help.openalex.org/data/source-types/), and [Crossref types](https://api.crossref.org/types), consulted on 2026-10-20; classification coverage is not guaranteed.

OpenAlex's reported total is a candidate count after its server filters but before local venue/category checks. When years or types are selected, Crossref's reported total is a candidate count after its server filters (start year widened by one) and before exact local checks; with no bounds or types it is the plain query count. Neither is an exact combined total for selected papers. Retrieved counts are after local filtering and before deduplication. The search message distinguishes unique records in this run from new library insertions; the unique-record metric describes the accumulated saved library. Missing years are excluded when a bound is active. Filters apply to new search results, not previously saved records; raw provider types remain in saved metadata.

`complete` means a final source page for this query was received without contradictory totals; it never means every relevant paper worldwide was found. Budget stops and later-page failures are `partial`; a first-page failure is `error`. The first reported total is retained and later changes are disclosed. Counts include only accepted pages; entries without a usable title/key are fetched but excluded from filtered/saveable records. No automatic retries are made. A 429 preserves earlier pages, shows a sanitized cooldown, and this session waits for Retry-After (60 seconds if unavailable) before calling that source again. Requests are serial with a one-second gap between pages. The 120-second budget is checked between requests; the 45-second connect/read inactivity timeout is not a hard total request deadline.

Search results are metadata from third-party services. Do not enter confidential or personal information in search queries.

## Data locations

- `data/research.db`: SQLite papers and search-history tables. The app creates the database and tables when needed.
- `exports/`: reserved local output directory; the current CSV feature sends a download to the browser and does not write the export here.
- The app stores no API credentials and makes direct unauthenticated requests to public endpoints.

The existing database is private working data and is excluded by `.gitignore`. See [Data and Backup](docs/DATA_AND_BACKUP.md) for the backup procedure and staged restore/rollback steps. The procedure is tested on temporary databases; replacing production data still requires explicit approval.

Future schema changes follow the [Schema Migration Policy](docs/SCHEMA_MIGRATIONS.md). This is a documented policy; the app has no migration runner or version checks, and no database change is authorized by the document itself.

## Tests

The tests use Python's standard-library `unittest` runner and temporary database files. Headless UI smoke tests use the installed Streamlit `AppTest` utility with a temporary app copy and mocked provider requests:

```powershell
python -m unittest discover -s tests -v
```

See [Testing](docs/TESTING.md) for isolation details and coverage limits.

Phase B's bounded two-provider acceptance evidence is in [Phase B acceptance](docs/PHASE_B_ACCEPTANCE.md) and the [live pagination report](docs/LIVE_PAGINATION_2026-10-20.md). Phase C is now in progress; see [Phase C plan and workspace guide](docs/PHASE_C_PLAN.md).

## Troubleshooting

- **`streamlit` or another import is missing:** activate `.venv`, then run `python -m pip install -r requirements.txt` using the same interpreter.
- **VS Code shows a different Python:** use **Python: Select Interpreter** and select `.venv\Scripts\python.exe`; compare with `python -c "import sys; print(sys.executable)"` in the terminal.
- **PowerShell blocks activation:** use the environment's executable directly, for example `.\.venv\Scripts\python.exe -m streamlit run app.py`. This avoids changing the machine's execution policy.
- **A search fails:** check network access and the displayed per-service error. Search history records service, time, status, and counts.
- **No records appear:** check the topic and enabled year bounds. Bounded pages can contain other categories or insufficient classification metadata. Clear categories/remove a year bound or use a larger raw-entry budget to inspect later pages. A broad positive provider total does not guarantee selected papers within that budget.
- **CSV opens with odd characters:** the download uses UTF-8 with a byte-order mark for spreadsheet compatibility.

## Limitations

- Coverage, metadata quality, abstracts, and counts vary by provider. Provider result counts are not a combined global estimate.
- Retrieval is bounded to 250 raw entries and five requests per provider; it is not exhaustive. Provider indexes may change between pages. OpenAlex uses basic paging within its documented depth limit; deeper cursor retrieval and credential handling are not implemented.
- Optional year bounds remove the artificial historical floor, but metadata dates and historical coverage remain incomplete. No comprehensive discipline/year coverage matrix or unrestricted bulk retrieval has been established.
- Version-two history notes share a run ID and store settings, counts, source IDs/URLs, observed year/types/venue and page evidence in the existing note column. Older rows are preserved without retroactive provenance. History displays/exports the latest 100 attempts; the full latest-run bundle is session-local unless downloaded. There are no raw-payload snapshots or resumable cursors.
- Provider-specific rate limits are handled conservatively in a single session; shared multi-session throttling, automated retry/backoff and crash-safe atomic run storage remain outside this bounded milestone.
- Deduplication uses normalized DOI, or normalized title and year when DOI is absent; title/year matches may not identify duplicates perfectly.
- The app does not perform citation chaining, systematic query expansion, full-text retrieval, or generated analysis.
- Metadata availability does not grant rights to reuse abstracts or full text. Respect provider terms and applicable licenses.
- No automated tests, Python version range, dependency lock, or Git history existed at the start of this documentation phase. See [Project Status](docs/PROJECT_STATUS.md).
