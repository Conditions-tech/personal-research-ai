# Bounded literature retrieval

Implemented 2026-10-20 under the user's instruction to advance Personal Research AI. This is an incremental Literature Discovery feature; it does not establish worldwide coverage or implement Paper Analyst/Research Strategist.

## Budgets and source access

The UI selects a **raw entry budget per provider**: 5, 10, 25, 50, 100, or 250 (default 10). A request asks for `min(50, budget)` entries; later requests keep that page size. Every provider has at most five requests and a 120-second budget checked between requests. The controller checks the deadline again after its one-second delay between pages. The transport's 45-second connect/read inactivity timeouts are not a hard wall-clock request deadline; slow activity can exceed the between-request budget. Provider searches remain serial.

Raw entries consume the budget even if local filters exclude them, they lack a usable key, or they duplicate earlier entries. The limit is not a promise to find that many selected or unique papers. Higher budgets allow later pages to contain matching papers when the first page does not. For programmatic budgets not divisible by the request size, stop before a further full page could exceed the cap; unused budget is possible. No retries or extra count probes are sent.

- **OpenAlex:** basic numbered pages, retaining search/select/year/native candidate-type parameters. At most 250 entries are requested, comfortably below the documented 10,000-result basic paging depth. This avoids introducing credentials or relying on cursor access, which requires a free key beyond the first page. No API key is read, created, logged, or requested by the application.
- **Crossref:** `cursor=*` on the first request; follow the latest `next-cursor` and retain the exact bibliographic query, row size and server filter. Stop on a short page. A full page without a usable next cursor, or with a cursor already seen during this traversal, stops as partial. A one-second gap between pages respects the documented public list-query rate in this serial local application; it is not a process-wide or multi-user rate limiter.

## Counts and completion

Start/end years are independently optional. The UI defaults remain 2015/current local year, while bounded input accepts CE 1-9999. Disabled bounds are recorded as JSON null and omitted from OpenAlex request filters. Both disabled admits unknown years; any enabled bound excludes them. OpenAlex formats early CE date years with four digits. Crossref's existing print/online/published date precedence and local filtering are retained. Crossref also receives server-side `from-pub-date`/`until-pub-date`/`type` filters (2026-10-26). Crossref dates by the earliest online/print date while local years prefer print, so the start bound is widened by one year; the exact local filter still decides which records are kept. Records printed more than a year after first online publication can be excluded by the server; a 2026-10-26 live sample (one query, 50-record budget, 2015–2026, journal+conference) kept 36/50 fetched entries versus 0/50 without server filters, the 14 drops all being 2014 records admitted by the margin. Removing a bound does not establish historical index completeness.

`RetrievalResult` separates the first response's provider total/scope, raw entries in successfully parsed pages, locally filtered records, unique keys within that source run, successful pages, and attempted requests. A later total change is flagged; a missing total remains unknown. A malformed page is rejected as a unit, so its entries are not included in accepted-page counts.

The A/B re-audit added title-shape checks (OpenAlex string, Crossref list of strings) and integer-or-null source-year checks within SQLite's signed 64-bit storage range. Boolean/string/fractional/oversized year values are rejected, not coerced into evidence. Unbounded metadata is not restricted to the UI's CE year inputs; this validates representation/storage, not the scientific correctness of a date. Source integer zero remains distinct from a missing year in new fallback keys. See [Phase C Handover](PHASE_C_HANDOVER.md) for downstream interpretation.

Raw counts include records without a usable title/key; those entries are excluded from filtered/saveable records. Duplicate filtered observations remain counted before deduplication. On a final page, either direction of mismatch between known stable total and fetched raw count prevents complete status. Run manifests separately record summed raw/filtered entries, cross-source unique keys, duplicate filtered entries and actual new library insertions; provider totals are never summed.

| Status | Meaning |
| --- | --- |
| `complete` | A short/final source page was received without a contradictory or changing total. Only this provider traversal and query are complete. |
| `partial` | A record/page/time budget, cursor problem, inconsistent total, or failure after an earlier valid page stopped retrieval. Valid earlier pages remain available. |
| `error` | The first request failed or its response could not be parsed/validated. No valid page was accepted. |

A full page ending exactly at the budget is partial: no extra request is sent to prove exhaustion. A zero filtered count does not terminate traversal; a full raw page may contain only excluded records. Source totals remain distinct: OpenAlex counts server-filtered candidates before local venue checks; Crossref counts server-filtered candidates (or plain query matches when no bound/type is selected) before exact local year/category filtering. Never sum those totals as a global estimate.

Deduplication still uses the existing normalized DOI or title/year key. The UI reports unique keys across sources in the current run, new library insertions, and the accumulated library size separately. Provider indexes can change while paging, causing omissions or duplicates; even a completed traversal is not a stable corpus snapshot or proof of complete research coverage.

## Failures and persistence

401/403, rate limits, timeouts, connection/HTTP errors, invalid JSON, malformed page envelopes, and normalization failures stop the affected source without automatic retry. The next source still runs. Previous valid pages are returned and saved through the existing schema; missing NULL metadata can be enriched without replacing nonempty evidence. Sanitized error categories and HTTP status codes replace raw exception strings so request URLs, future credentials, payloads, and private query text cannot leak through error messages.

429 has its own `rate_limited` stop reason and safe numeric cooldown. Numeric and HTTP-date Retry-After are supported; missing/invalid headers use 60 seconds, and extreme values are bounded to one year. The current UI session does not call that source during the cooldown, but still records the skipped attempt with zero requests and continues the other source. This is conservative stopping, not adaptive retry/backoff or a shared multi-session limiter. Actual 429 responses were not deliberately provoked live.

New history rows use the existing `status` and `note` columns. Version-two notes include shared run ID, query/settings, budgets, run and per-source counts/statuses/timestamps, stop reason/cooldown and retained per-record source/page evidence. Native OpenAlex IDs, Crossref DOIs, source record URLs, observed year/raw type/category/venue survive without schema changes. Cursor values, request URLs and response bodies are not persisted. Legacy notes are preserved without retroactive settings/evidence. There is no schema migration or production rewrite.

All accepted pages are held in memory, at most 250 entries per source, until the normal save step. The latest session run can be downloaded as manifest JSON plus deduplicated records and provenance CSVs inside a ZIP. The library CSV remains a filtered library view. History export covers the latest 100 displayed attempts; older runs have no reconstructed record/abstract snapshots after restart. Crash-safe atomic run storage, resumable cursors, raw payload archives, adaptive backoff and shared throttling remain future enhancements.

## Verification and sources

Offline tests inject synthetic pages and a fake clock. Isolated AppTest cases use temporary databases and block live HTTP. They cover successful page traversal, filters excluding the first page, cross-source duplicate merging, all budget stops, unknown/changing totals, missing/cyclic cursors, malformed responses, rate/access errors, interrupted retrieval, history notes, exports and sanitized errors. [Phase B acceptance](PHASE_B_ACCEPTANCE.md) records the current tests; the separate [live pagination report](LIVE_PAGINATION_2026-10-20.md) records real traversal and sampling limitations. Browser rendering and actual download transfer remain unverified.

Provider documentation consulted on 2026-10-20:

- [OpenAlex basic and cursor paging](https://help.openalex.org/api/paging/).
- [OpenAlex authentication and limits](https://help.openalex.org/api/authentication/).
- [Crossref rows and cursor termination](https://www.crossref.org/documentation/retrieve-metadata/rest-api/tips-for-using-the-crossref-rest-api/).
- [Crossref cursor changes released August 2026](https://community.crossref.org/t/changes-to-cursors-filtering-and-sorting-in-the-rest-api/16246).
- [Crossref public list-query limits](https://www.crossref.org/blog/announcing-changes-to-rest-api-rate-limits/).
