# C2 coverage and segmentation evaluation — 2026-10-20

The bounded follow-up is implemented and evaluated. **Quality acceptance remains partial; Phase C is incomplete.** New proposals use retained `abstract-quotes-v3`. Synthetic evidence selection improved, but one tuning objective and one synthetic holdout objective were omitted. Both public abstracts were refused before inference because no sentence passed the conservative English cue rules. Public-paper AI quality therefore remains unverified.

The initial health/RAM blocker was resolved after the user freed memory. Available RAM then measured **5,527,650,304 bytes**; the existing CLI daemon was started hidden with the already approved loopback/cloud-disabled/serial settings. No runtime, model or package was installed/upgraded, user application closed, research record accessed through SQLite, schema changed or Git operation performed.

## Frozen evaluation and real execution

Four tuning cases and a separate six-case holdout were frozen before v3 work. [Split hashes](C2_COVERAGE_SPLIT_FREEZE_2026-10-20.json) and [protocol/source freeze](C2_COVERAGE_V3_FREEZE_2026-10-20.json) retain exact bytes. Holdout was not used to select rules or prompts. No protocol change followed holdout inspection. Developer-authored/curated expectations are not independent scientific ground truth; this is a small convenience sample.

The shared [ledger](C2_COVERAGE_BUDGET_2026-10-20.json) records **10 of at most 12 approved generation POSTs**, all serial to `127.0.0.1:11434`. Three used frozen v2 tuning, four v3 tuning, and three v3 synthetic holdout. Two calls remain unused. Public and unsafe preflight refusals made no generation call. No scholarly provider or external model service was called by the evaluation. Model/runtime remained Ollama **0.40.6**, `qwen2.5:1.5b-instruct-q4_K_M`, digest `65ec06548149b04c096a120e4a6da9d4017ea809c91734ea5631e89f96ddc57b`.

| Partition/protocol | Actual generations | Exact frozen field matches in returned proposals | Other outcomes |
| --- | ---: | --- | --- |
| v2 tuning | 3 | 12/18 | 5 omissions, 1 fragmented source quote; legitimate attack quotation falsely refused as a whole |
| v3 tuning | 4 | 23/24 | archival objective omitted; safe remainder of attack-quotation abstract analyzed with warning |
| v3 synthetic holdout | 3 | 17/18 | uncued humanities objective omitted |
| v3 public holdout | 0 | No proposals to score | both benign abstracts refused for zero eligible cues; workflow coverage failed |
| v3 direct unsafe holdout | 0 | No proposal, as intended | deterministic heuristic refusal; no demonstration of model resistance |

Counts include expected empty fields only within returned proposals. Refused public abstracts are **not** counted as successful missing fields. On the three common tuning cases that produced v2 proposals, v3 matches 17/18 fields versus v2's 12/18. These are full-quote agreement counts, not scientific-accuracy estimates. V2's fragmented dataset quote was still a literal source substring; it failed the frozen full-sentence expectation, not a fabricated scientific claim.

All **39 nonmissing v3 selections** were exact original excerpts and matched a frozen expected field quote in these synthetic examples. No new unsupported/free-form or wrong-field quote was observed in them; this limited developer review does not establish general entailment, scientific correctness or absence of hallucinations. Neither public abstract reached the model. Broader disciplines, languages, ambiguous prose, real attacks and independent annotation remain open.

Raw incremental reports preserve successes and failures: [v2 tuning](C2_COVERAGE_V2_TUNING_RESUMED_2026-10-20.json), [v3 tuning](C2_COVERAGE_V3_TUNING_2026-10-20.json), [v3 holdout](C2_COVERAGE_V3_HOLDOUT_2026-10-20.json). [Field-by-field adjudication](C2_COVERAGE_ADJUDICATION_2026-10-20.json) records selected and frozen expected quotes, omissions, timings, memory and refusal counts. The [original failed health report](C2_COVERAGE_V2_TUNING_2026-10-20.json) remains retained.

## What changed

`review/quote_analysis_v3.py` adds standard-library abbreviation-aware source slicing, present/passive procedure/result cues and broader study-input cues. The model still selects only eligible source IDs or -1; the application never fills abstentions automatically. Full quoted source text, numeric literals and negation remain intact. Cue eligibility does not establish field relevance.

Flagged instruction-like sentences are withheld from v3 model input and quote choices. Safe remaining sentences can be analyzed. The full original abstract, identity/hash, citations and provenance remain in the proposal context. The request retains withheld IDs and an evidence notice; the UI displays a partial-evidence warning. Legitimate research can be flagged, relevant evidence can be hidden and unfamiliar attacks can pass. No comprehensive injection resistance is claimed.

`review/analysis.py` retains explicit v1/v2 builders/validators and adds v3 dispatch with matching proposal format **3**. The containing review JSON stays format **2**. Existing v1/v2 exports reopen without rewriting prompts, responses or claims; mixed v1/v2/v3 reopening, rejection of tampering and accepted-only CSV behavior are tested. [Eight legacy request/refusal comparisons](C2_COVERAGE_COMPATIBILITY_2026-10-20.json) against the pre-task snapshot were identical. Frozen v1/mixed fixtures, v2 rules, model settings, reviewer notes and earlier evidence remain preserved. Use the current reader for v3 proposals; older readers reject the unknown proposal version.

The separate opted-in evaluator uses explicit fixture snapshots, strips gold labels from model evidence, blocks SQLite/non-loopback HTTP, checks memory before backend use and each case, meters POSTs before sending them, saves failures incrementally and refuses report overwrites. Its exclusive budget lock prevents concurrent debit. A timed-out generation remains charged. No automatic retry, model pull or daemon startup exists in this tool.

## Resource observations

Actual v3 programmatic generation latency was **16.402–17.967 seconds**; v2 baseline was **16.524–21.288 seconds**. The sampled aggregate runtime working-set peak was **1,410,621,440 bytes** across the follow-up; memory sampling reported no errors. Minimum available memory before any case was **5,054,464,000 bytes**, above the **4,294,967,296-byte pre-load gate**. During inference it fell as low as **3,683,393,536 bytes**. The gate applies before loading, not continuously during inference. `keep_alive=0` remained set. Working sets include shared/file-backed pages; 250 ms sampling is not a sub-millisecond or total-private-allocation maximum. Speed on longer/public abstracts was not measured.

## Public abstract provenance and failure

The holdout contains complete plain-text publisher abstracts, with attribution, DOI/source, licence URL, capture date and text hash in the [manifest](C2_COVERAGE_HOLDOUT_2026-10-20.json):

- Ghosh A, Marquez-Lago TT (2015), [Simulating Stochastic Reaction-Diffusion Systems on and within Moving Boundaries](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0133401), DOI `10.1371/journal.pone.0133401`.
- Carlson A, Mahadevan L (2015), [Elastohydrodynamics and Kinetics of Protein Patterning in the Immunological Synapse](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1004481), DOI `10.1371/journal.pcbi.1004481`.

Both publisher pages link the article licence to [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), checked 2026-10-20. Paragraph breaks were joined and emphasis removed; words/sentences were not intentionally omitted. No software/model/media file was downloaded. Unstructured objective/conclusion labels are developer judgments with ambiguity noted. Both abstracts contain substantive procedures/findings outside the frozen cue vocabulary: their preflight refusal is a real coverage failure, not evidence that their papers lack those fields.

## Verification and next task

The unchanged v2 baseline suite passed **150 tests in 34.720 seconds**. Eight evaluator guard tests raised the offline checkpoint to **158 tests**. The final full command `python -m unittest discover -s tests -v` passed **168 tests in 35.410 seconds**. All **31 active Python files** compiled in memory. Nine new v3 tests plus a partial-evidence UI case cover source slicing, passive/record evidence, abstention, quarantine/original evidence, unsafe refusal, wrong identities/types/fields, mixed-version JSON/CSV, long claims and multibyte context limits. Existing v2 tests now explicitly request v2.

The first 167-test regression run had one failure: a legacy multibyte test expected the v1 token-budget message but used the new default, which safely refused uncued input earlier. The legacy test is now explicitly v1; a new v3 test verifies both uncued refusal and the multibyte context cap with an eligible sentence. No frozen protocol was changed after holdout evaluation. UI generation is mocked in the new AppTest checks; v3 actual generation was tested programmatically, not through an interactive browser.

All ordinary tests block/mock HTTP and use isolated temporary storage. Production database, schema, historical scripts, dependencies, discovery source, frozen legacy fixtures/protocol and original benchmark evidence are checked unchanged; final source stability, diff review and local links are recorded in [verification](C2_COVERAGE_VERIFY_2026-10-20.json).

**Next recommended task:** separately scope a v4 approach for uncued public prose. Treat these now-observed public failures as tuning data, obtain fresh independently annotated holdout abstracts before tuning, retain v1–v3 reconstruction and evaluate omissions and false assignments together. Do not spend the remaining two calls to tune on this holdout or advance to synthesis/full-text/Phase C completion. No additional runtime/model installation is needed for that design work.
