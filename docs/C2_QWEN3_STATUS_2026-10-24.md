# Qwen3 pilot — seven results reconciled; remaining work resource-blocked

This is the October 24 checkpoint. The [October 25 continuation](C2_QWEN3_CONTINUATION_2026-10-25.md) supersedes its manual ready-request workflow with bounded automatic resource supervision; the seven-case results below remain unchanged.

Fresh authorization on 2026-10-24 resumed the interrupted task, not the inference budget. The ledger remains **7/12**, with **five authorized unattempted cases**. All seven charged cases have complete saved responses, exact reconstruction and recorded post-generation empty `/api/ps` checks. The seventh case, `public-0202762`, completed in 92.619 seconds; it is not an unknown outcome and was not repeated. No inference was sent during this reconciliation. [Evidence/ledger reconciliation](C2_QWEN3_RECONCILIATION_2026-10-24.json).

The existing Ollama 0.40.6 daemon was stopped. Only that approved daemon was restored hidden with loopback, cloud disabled, serial requests and one loaded model. Installed Qwen3 digest/thinking controls and retained Qwen2.5 digest were verified. No model was loaded. Available RAM was **5,341,868,032 bytes (about 4.98 GiB)**, below the unchanged **5,905,580,032-byte (5.5 GiB)** gate. Disk headroom was adequate. No application was closed and no OS/page-file setting, download, installation, upgrade, startup registration or inference budget was changed. [Fresh preflight](C2_QWEN3_PREFLIGHT_2026-10-24.json).

The later [resource check](C2_QWEN3_RESOURCE_CHECK_2026-10-24.json) remained below the gate at **5,092,646,912 bytes (about 4.74 GiB)**, with no loaded model and ledger still 7/12. No further load was attempted after the insufficient-memory observation.

After the user replied ready, a [fresh identity/readiness check](C2_QWEN3_READY_CHECK_2026-10-24.json) again verified the pinned model and empty loaded-model inventory. Eleven physical-memory samples across ten seconds all remained below 5.5 GiB; the last was **5,546,061,824 bytes (about 5.17 GiB)**. No generation was sent and the ledger remained 7/12. A ready reply does not replace the measured load gate.

## Actual outcomes, without treating copying as support

| Partition | Frozen cases | Completed | Unattempted | Supported quote selections | Correct missing fields | Fills against declared missingness | Other quotes needing support review |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Public development | 4 | 4 | 0 | 16 | 5 | 2 | 1 |
| Holdout | 8 | 3 | 5 | 14 | 2 | 1 | 1 |

Across the **42 returned field decisions**, 30 selected frozen support and seven matched missingness: **37/42 strict decisions**. All **35 nonmissing quotations** occurred literally in their original abstracts. No predeclared alternative was selected and no empty omission was observed in the completed outputs. These counts do not assign correct missing fields or successful coverage to unattempted cases. Five cases remain unattempted: `public-0020753`, `holdout-ecology-abbrev`, `holdout-letters`, `holdout-safe-task-instruction`, `qwen3-synthetic-mixed-injection`.

[Development reconstruction](C2_QWEN3_DEVELOPMENT_AUDIT_2026-10-21.json), [three-case holdout reconstruction](C2_QWEN3_HOLDOUT_RECONCILED_AUDIT_2026-10-24.json), [derived holdout evidence with original-input hashes](C2_QWEN3_HOLDOUT_RECONCILED_RESULTS_2026-10-24.json). Original reports, prompts, responses, contexts, labels, reviewer work and earlier evidence were not overwritten. The partial composite does not manufacture completion of the frozen eight-case holdout.

Clear role failures remain: the bird-conservation paper's dataset selection is global background rather than its separately identified survey sample, and its limitation selection is an ecological result rather than a study/inference constraint. The bilingual-study dataset selection is also a result. The algorithm-contribution sentence selected as a conclusion is a less definite gold mismatch requiring support review, not automatically hallucination. [Post-output developer review](C2_QWEN3_DEVELOPER_REVIEW_2026-10-21.json) remains separate from frozen labels.

The development comparison improved from archived v5's 15/24 strict decisions to 21/24, with two predeclared defensible alternatives in the older output; one paper became worse. Context size and thinking controls also differ. These are previously developer-inspected, single-publisher public examples, not independent/blinded domain-expert gold, representative scientific validation or an isolated causal estimate of model size. [Descriptive comparison](C2_QWEN3_DEVELOPMENT_COMPARISON_2026-10-21.json). No default promotion or automatic acceptance is justified. Phase C remains incomplete.

## Resources and operational limits

All seven recorded immediate pre-load samples passed 5.5 GiB (minimum **5,943,414,784 bytes**). End-to-end case latency was **84.549–102.731 seconds**, median 95.598 seconds; summed case time was 670.871 seconds, excluding manual memory coordination. Sampled aggregate runtime working-set peak was **3,762,552,832 bytes**. Minimum sampled system availability was **545,505,280 bytes**, and one process-measurement error occurred. These are incomplete sampled working-set observations, not an exact private-memory peak or a performance/resource-fit guarantee. Repeated between-case gate failures prevented unattended completion. [Resource summary](C2_QWEN3_RESOURCE_SUMMARY_2026-10-24.json).

The prior [placement observation](C2_QWEN3_PLACEMENT_OBSERVATION_2026-10-21.json) showed one pinned Qwen3 model, 6,144 context and zero VRAM allocation during a running generation. Every request used the frozen CPU/nonthinking/immediate-unload settings. No thinking output was observed in saved successful responses; this does not prove anything about internal computation. There were no recorded live transport/schema failures in the seven completed requests. Live timeout/rate-limit behavior and Qwen3 injection resistance remain unverified; ordinary failure/contract tests are isolated mocks. The new synthetic robustness cases have not run.

## Verification and next boundary

`python -m unittest discover -s tests -v` passed **217 tests in 36.577 seconds** on 2026-10-24. All **51 active Python files** compiled in memory. Tests use synthetic/temporary work and mocked/blocked HTTP; no production SQLite is opened. Frozen source/protocol/evidence hashes match, original development adjudication is identical on replay, and normal saved v1–v5 compatibility remains covered by the full suite. No source change was needed to reconcile the actual completed request.

The app remains Qwen2.5/conservative v3. Qwen3 outputs are programmatic diagnostics, not app proposals or accepted review notes; original manual notes and saved formats remain separate. Full text, synthesis, independent scientific adjudication and the rest of Phase C are not complete.

If actual available RAM qualifies, continue only the five listed unattempted cases using the same frozen protocol and existing ledger, with a new report path and per-load resource checks. Never repeat/uncharge a completed, failed or ambiguous charged request, reset/extend the ledger, download another model or weaken the gate. While RAM is insufficient, no load attempt is authorized by successful offline tests. The user was asked once on this resumption to free memory; no application was closed by the agent. Current acceptance evidence supports preserving failures and human review, not a cosmetic prompt revision or automatic promotion.
