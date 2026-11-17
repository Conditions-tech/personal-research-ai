# Live pagination and classification evidence - 2026-10-20

The live check used the current source adapters, bounded retrieval controller, actual normalizers, unchanged application storage functions extracted without UI execution, and guarded temporary SQLite storage. The production database was never connected. Requests were public, unauthenticated, serial, and separated by at least two seconds in each traversal. No paid service, package, schema, production record or historical script was changed.

The first sandbox attempt failed without receiving an HTTP response. The approved network-enabled checks then received **17 HTTP 200 responses** in total. No live 401/403/429, timeout or server failure occurred or was intentionally induced. Failure and cooldown behavior was tested separately with mocks.

Live queries preceded the final shared-workspace title/year, NULL-enrichment and identical-title-selection hardening. Those later fixes were verified offline; provider query parameters, category mappings, paging/budgets and transport were preserved. No additional live calls were made for those defensive changes.

## Primary traversal - 11 requests

The primary check ran at 11:58:47-11:59:10 Bangladesh time (05:58:47-05:59:10 UTC). Each page requested two entries. Journal/conference runs used a four-entry/two-page budget per source; historical/empty runs used one page. These are small programmatic budgets, not changes to the UI's existing options.

| Query / selection | Source | Reported total | Pages | Raw / filtered / unique | Result |
| --- | --- | ---: | ---: | --- | --- |
| The Hallmarks of Cancer / journal | OpenAlex | 375,492 | 2 | 4 / 3 / 3 | partial, record budget |
| Same / journal | Crossref | 3,182,702 | 2 | 4 / 4 / 4 | partial, record budget |
| Deep Residual Learning for Image Recognition / conference | OpenAlex | 240,756 | 2 | 4 / 2 / 2 | partial, record budget |
| Same / conference | Crossref | 4,671,020 | 2 | 4 / 0 / 0 | partial, record budget |
| Philosophical Transactions / types cleared, no lower year, upper 1800 | OpenAlex | 457 | 1 | 2 / 2 / 2 | partial, record budget |
| zzqvx8f7c4b2dphasebnaturalempty / no year/type bounds | OpenAlex | 0 | 1 | 0 / 0 / 0 | complete, source exhausted |
| Same / no year/type bounds | Crossref | 0 | 1 | 0 / 0 / 0 | complete, source exhausted |

OpenAlex advanced page 1 to page 2. Crossref followed the newest cursor with the same query/rows. Raw counts matched accepted payload sizes, and first totals matched provider payload fields. Retained journal records had explicit OpenAlex journal venue evidence or native Crossref journal-article types; OpenAlex retained native conference-paper records. Historical retained years were **1735 and 1791**.

The primary harness exited **1** because its stronger sampling assertion expected at least one retained Crossref conference record in four raw entries. All four were journal-article, correctly excluded. Traversal, count, budget, cursor, filtering-evidence and natural-empty checks passed. This was an unmet sample-content assertion, not a request or classifier exception. The original failed result is preserved in [primary JSON](LIVE_PAGINATION_2026-10-20.json).

## Additional checks - six requests

| Check | Requests / entries | Observed outcome |
| --- | --- | --- |
| Crossref two-page conference supplement: IEEE International Conference on Robotics and Automation | 2 / 4 | Four journal-article entries; zero conference records retained; positive-sample assertion failed. |
| Crossref explicit score-descending cursor diagnostic for the ResNet title | 1 / 2 | posted-content and journal-article; no production sort change was made. |
| Crossref two-page full-citation query: Deep Residual Learning for Image Recognition Kaiming He Xiangyu Zhang Shaoqing Ren Jian Sun 2016 | 2 / 4 | Four journal-article entries; zero conference records retained; positive-sample assertion failed. |
| Crossref public known-work lookup: DOI 10.1109/CVPR.2016.90 | 1 / 1 | Native proceedings-article; the real normalizer/filter retained conference selection and excluded journal selection. |

The known-work check positively verifies Crossref conference classification against live metadata; **it is not a paginated query result**. The two-page query checks establish actual cursor traversal and correct exclusion of other types. They do not establish recall for conference queries, nor absence of relevant conference works. The known DOI exists while these small query windows exclude it; larger budgets and relevance behavior were not evaluated live. Broad bibliographic queries and differing source rankings are important discovery limitations.

Unsuccessful sample probes are preserved, not relabelled as passing: [venue supplement](LIVE_PAGINATION_2026-10-20_SUPPLEMENT.json), [ordering diagnostic](CROSSREF_ORDER_DIAGNOSTIC_2026-10-20.json), [citation supplement](LIVE_PAGINATION_2026-10-20_CITATION.json), and [known-work classification](CROSSREF_KNOWN_WORK_2026-10-20.json).

## Storage, deduplication and export

Primary journal runs produced seven filtered/unique records; conference runs two; historical runs two. All were inserted only into temporary storage. Replaying each accepted batch inserted **zero** new rows. No natural cross-provider duplicate appeared in these tiny samples; cross-provider merging is verified with isolated synthetic tests, and exact live-record replay is verified here. The primary temporary database ended with 11 papers and seven source attempts; it was removed. Supplemental temporary storage was also removed.

Each run's shared ID, settings, provider-scoped counts/status, native identifiers/page evidence and actual insertion count were serialized through the existing note column. Run ZIP manifests round-tripped exactly. Counts describe accepted pages and metadata keys, not an independently audited worldwide paper total. All payloads, cursors and disposable databases were discarded; JSON artifacts contain aggregates and public test queries only.

## Reproduction and limits

Live calls require fresh authorization; they never run during unittest discovery. From the project root:

```powershell
python tools/live_discovery_smoke.py --live --report smoke-results.json
python tools/live_discovery_smoke.py --live --conference-supplement --report supplement-results.json
python tools/live_discovery_smoke.py --live --known-conference --report known-work-results.json
```

The primary/supplement script intentionally exits nonzero if its small window lacks a positive category sample; inspect individual checks before interpreting that as an application failure. A test verifies that omitting --live refuses before network/database I/O. Future rankings/counts may differ.

Not verified live: larger UI budgets/page sizes, independent total accuracy, broad discipline/language/historical recall, missing-year prevalence, real outages/429 headers, concurrent sessions, browser layout or file transfer. Do not generalize the biomedical/computer-vision/conference-name/historical query intents into a validated discipline coverage matrix.

Provider contracts were rechecked against official [OpenAlex paging](https://help.openalex.org/api/paging/), [OpenAlex access limits](https://help.openalex.org/api/authentication/), [Crossref cursor guidance](https://www.crossref.org/documentation/retrieve-metadata/rest-api/tips-for-using-the-crossref-rest-api/), [Crossref cursor changes](https://community.crossref.org/t/changes-to-cursors-filtering-and-sorting-in-the-rest-api/16246), [Crossref rate limits](https://www.crossref.org/blog/announcing-changes-to-rest-api-rate-limits/), and [Crossref query/sort fields](https://github.com/CrossRef/rest-api-doc). See [Phase B acceptance](PHASE_B_ACCEPTANCE.md) for the implementation gates and remaining limitations.
