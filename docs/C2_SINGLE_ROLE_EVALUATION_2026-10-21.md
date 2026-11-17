# C2 single-role experiment and review integrity — 2026-10-21

**The one-role hypothesis failed its field-quality gate. Phase C remains incomplete.** Twelve serial local requests were completed on the already installed Qwen2.5 1.5B model. No model/runtime/package download or upgrade, external inference, production data/schema change or Git operation occurred. The app default is restored to conservative **`abstract-quotes-v3`**. Saved v4/v5 drafts still reopen; v6 is an experimental diagnostic artifact, not an app proposal/default.

## Predeclared experiment

The hypothesis was that asking one explicitly defined role at a time, while repeating the whole safe abstract independently, would reduce cross-role interference and position-based fills. Each request returns one complete source quote or an empty string. It receives no earlier model answer, reviewer note or other paper. Definitions and source/identity validation are fixed in `review/role_analysis_v6.py`; resource/model settings are unchanged.

One previously observed theoretical-paper failure was frozen as development, and one newly captured public metascience abstract was reserved as holdout. Six independent roles per paper consume the new [12/12 ledger](C2_V6_BUDGET_2026-10-21.json). Previous v3 and v4/v5 ledgers remain 10/12 and 12/12, respectively. No completed ledger was reset/extended. Evidence and strict/acceptable-alternative labels were written before implementation and inference; no prompt, definition or selection rule changed after holdout inspection. Adjudication is developer-authored, not independent or blinded. Two papers cannot establish general quality.

- Development: Ghosh A, Marquez-Lago TT (2015), [Simulating Stochastic Reaction-Diffusion Systems on and within Moving Boundaries](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0133401), DOI `10.1371/journal.pone.0133401`; original source/CC BY 4.0 attribution retained. Previously observed v5 result: 3/6 frozen fields, with ambiguous alternatives noted in the original review.
- Holdout: Ivan Stelmakh; Charvi Rastogi; Nihar B. Shah; Aarti Singh; Hal Daumé III (2023), [A large scale randomized controlled trial on herding in peer-review discussions](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0287443), DOI `10.1371/journal.pone.0287443`. Complete public abstract captured from publisher metadata; its page explicitly links CC BY 4.0. No private conference/reviewer data was requested. This paper was not previously used for inference.

[Development](C2_V6_DEVELOPMENT_2026-10-21.json), [holdout](C2_V6_HOLDOUT_2026-10-21.json), [publisher capture](C2_V6_PUBLIC_CAPTURE_2026-10-21.json), [evidence freeze](C2_V6_EVIDENCE_FREEZE_2026-10-21.json), [protocol freeze](C2_V6_PROTOCOL_FREEZE_2026-10-21.json).

## Outcomes, without conflating presence and support

| Measure | Development | Fresh holdout |
| --- | ---: | ---: |
| Requests / validated mechanical responses | 6/6 | 6/6 |
| Literal original source quotes | 6/6 | 6/6 |
| Strict supported-role selections | 4/6 roles | 2/6 roles |
| Predeclared valid alternative selected | 0 | 0 |
| Fills against predeclared missingness | 2 | 1 |
| Other quotes needing support review | 0 | 3 |
| Empty omissions / correct missing roles | 0 / 0 | 0 / 0 |
| Backend/contract failures | 0 | 0 |

Development recovered the objective and correctly selected method/results/conclusion support, but labelled a benchmark/result sentence as dataset and general cellular dynamics as a study limitation. The abstract does not identify an empirical dataset or explicitly state those as this study's limitations; this does not prove that the complete paper lacks such information.

On holdout, the model repeated the null finding as objective, method and dataset. That sentence supplies no experimental procedure or sampled inputs, while the abstract separately describes its randomized trial and sample. Results and conclusion matched support; the policy implication was incorrectly assigned as a study limitation. The three other quotes were inspected and are clear role errors here, not merely valid alternatives excluded by exact gold. Negative wording was preserved, but correct wording did not imply correct placement.

The pilot selected support for **6/9 roles prelabelled as supported**, filled **all 3 roles prelabelled missing**, and produced no abstentions. No generated result was accepted into a review or comparison CSV. The fresh holdout has no v5 baseline, so this is not a controlled claim that v6 is better/worse than v5 on that paper. The small development gain does not establish reliable general improvement.

Raw requests, source context, normalized fields, model/runtime identity, responses, memory/latency and preserved original review snapshots are in [development results](C2_V6_DEVELOPMENT_RESULTS_2026-10-21.json) and [holdout results](C2_V6_HOLDOUT_RESULTS_2026-10-21.json). Offline [development scoring](C2_V6_DEVELOPMENT_ADJUDICATION_2026-10-21.json) and [holdout scoring](C2_V6_HOLDOUT_ADJUDICATION_2026-10-21.json) separate strict gold, predeclared valid alternatives, omissions, missingness fills and unclassified support. No label was changed after inference.

The [acceptance-gap audit](PHASE_C_ACCEPTANCE_GAPS.md) records verified software behavior, reproduced defects and unresolved scientific/research boundaries.

## Backend-independent follow-through

`tools/role_adjudication.py` verifies the frozen manifest and original snapshot/context, reconstructs each role request and normalized response, and keeps failed/unattempted roles out of correct-missing counts. Its counters are developer-label comparisons, not scientific verification. `tools/role_analysis_evaluation.py` blocks SQLite/non-loopback HTTP, checks the unchanged memory gate before every role, meters POSTs in the owned separate ledger, retains failures incrementally and never mutates the review snapshot. Whole original snapshots are retained in these v6 artifacts. Normal review reopening intentionally rejects the diagnostic report as an unsupported workspace shape.

`tools/replay_analysis_archive.py` audits explicit historical JSON inputs without inference or mutation. The [audit](C2_V6_ARCHIVE_AUDIT_2026-10-21.json) observed **37 proposal occurrences** (including repeated fixtures): **6 complete-review validations**, **27 context/protocol-only replays**, and **4 raw v1 occurrences explicitly unreplayed** because the complete original review was absent. Complete saved v1 reviews still reopen through the normal fixture tests. Context-only replay cannot authenticate the original run, reconstruct absent history or validate a review decision. The first audit implementation was correctly rejected by the existing snapshot guard; the audit was changed to report these levels instead of bypassing the guard or inventing a run.

A concrete acceptance-gap audit then reproduced two importer defects using synthetic workspaces: duplicate JSON `text` keys silently replaced a reviewer note, and completed review actions/root metadata were accepted with missing timestamps. New regressions failed with **8 failing assertions across 5 test methods** before the fix. `restore_review` now rejects duplicate/nonfinite JSON and requires timezone-aware root creation/update and completed screening/authored-note timestamps. Untouched pending decisions/missing notes may retain null action times. Valid exports and cleared-note round trips remain supported. Errors remain generic without echoing note content. No timestamp is fabricated and no existing file is rewritten.

The [abstract review guide](ABSTRACT_REVIEW_GUIDE.md) explains field roles, source support versus copying, rejection/manual correction, accepted-only CSV semantics, save/reopen limits and diagnostic-versus-review formats. It uses the current workflow rather than adding product features. No additional cosmetic prompt version was introduced after v6 failed.

A guarded UI regression also reproduced a missing warning: valid manually authored work could exceed the existing 10 MiB reopening limit while the app still recommended its JSON download without explaining that limit. The focused test failed before the fix and passed in 0.650 seconds afterward. The UI now warns explicitly and retains the complete original download and session notes. No truncation or import-limit change was introduced; oversized-file reopening remains unsupported.

## Verification and remaining boundaries

The first full regression after restoring the default passed **195 tests in 35.544 seconds**. After offline audits and the reproduced importer fixes, final `python -m unittest discover -s tests -v` passed **207 tests in 35.786 seconds**. All **47 active Python files** compiled in memory. Tests use synthetic/temporary data and mocked/blocked HTTP; no production database is opened. Saved v1–v5 version/format pairing and unchanged existing proposals are tested. V6 compatibility means re-auditing the standalone report and its original snapshot/requests/responses, not importing an invented proposal format 6 into the app.

[Resource summary](C2_V6_RESOURCE_SUMMARY_2026-10-21.json): development role requests took 15.319–17.970 seconds (102.674 seconds summed); holdout 16.937–19.777 seconds (107.704 seconds summed). Every pre-load sample exceeded the unchanged 4 GiB gate (minimum **4,950,958,080 bytes**). Sampled aggregate runtime working-set peak was **1,417,420,800 bytes**, with no sampler errors. This is 250 ms development sampling, not total private memory, exact peak or a performance guarantee. `keep_alive=0` was retained. The app does not expose this six-call pilot as a generation default. A later read-only `/api/ps` health probe timed out, so current runtime readiness/loaded-model state is not claimed from earlier success. No generation, download or runtime restart was performed for that offline check.

[Final verification](C2_V6_VERIFY_2026-10-21.json) records stable source/fixtures, protected data/historical files, preserved old evidence and ledgers, diff review and local-link checks. Browser transfer/layout, independent scientific annotation, wider corpus performance and comprehensive injection resistance remain unverified.

The installed-model pilot has exhausted its separate inference allocation and did not establish a reliable field-analysis method. No inference/model/download is authorized by the offline follow-through. Useful progress here was safer import, exact archive scope and reproducible evaluation, not AI synthesis. Routine maintenance approval remains valid; scientific-quality acceptance, independent adjudication, any different model and synthesis remain distinct unresolved boundaries. Phase C is not declared complete.
