# C2 public abstract evaluation — completed 2026-10-21

**Ordinary public prose is now reachable, but field-quality acceptance failed. Phase C is incomplete.** V4 removes English cue gates; v5 additionally replaces numeric sentence-ID output with literal whole-source quote choices. Both retained protocols are implemented, and v5 is the current experimental proposal path. All outputs remain pending and require human review before acceptance. The UI explicitly warns about observed wrong field assignments and unsupported fills.

## Fixed evidence and budget

Four public tuning abstracts and four reserved public holdouts were prelabelled before implementation. Two observed v3 failures are explicitly reused as tuning; six new publisher abstracts add cognitive psychology, archaeology, quantitative linguistics, ecology and metascience. No synthetic field prefixes were added. The developer read/curated the holdout before tuning but did not use its labels/outcomes to choose rules; this is **developer-reviewed convenience evidence, not independent or blinded annotation**. All eight sources come from one publisher, so cross-publisher/domain representativeness is unverified.

[Capture](C2_V4_PUBLIC_CAPTURE_2026-10-20.json), [tuning](C2_V4_TUNING_2026-10-20.json), [holdout](C2_V4_HOLDOUT_2026-10-20.json) and [split freeze](C2_V4_SPLIT_FREEZE_2026-10-20.json) retain complete text, attribution, DOI/URL, licence evidence, hashes and developer ambiguity notes. Five newly captured pages explicitly link CC BY 4.0; the sixth states Creative Commons Attribution reuse without a version/link. No version was invented. Prior captured sources retain their original attribution/licence. No full-text analysis, private research transfer or scientific source-authentication claim is made.

The new [follow-up ledger](C2_V4_BUDGET_2026-10-20.json) is **12/12**: four v4 tuning, four v5 tuning, four v5 holdout. The earlier v3 ledger remains 10/12 and was not reset. All actual generations were serial on the installed loopback/cloud-disabled Ollama 0.40.6 and unchanged Qwen2.5 1.5B Q4_K_M model/digest/options. RAM initially blocked inference at about 2.54 GiB; after the user freed memory, the existing daemon was restarted hidden. Blocked resource/health reports are retained and consumed no generation call. No package/runtime/model download or upgrade occurred.

## Results: keep three questions separate

| Protocol/partition | Proposals / abstracts | Literal source copying | Frozen six-field agreement | Correctly selected expected nonmissing fields |
| --- | --- | --- | --- | --- |
| v4 tuning | 4/4 | 24/24 nonmissing quotes | 3/24 | 3/17 |
| v5 tuning | 4/4 | 22/22 nonmissing quotes | 15/24 | 13/17 |
| v5 public holdout | 4/4 | 21/21 nonmissing quotes | 15/24 | 12/20 |

Workflow refusal was zero during these twelve completed generations; no saved proposal was auto-accepted. V4 greatly broadened access but filled seven expected-missing fields and selected fourteen different field quotes. V5 tuning still filled five expected-missing fields and chose four different quotes; holdout filled one expected-missing field and chose eight different quotes. Across v5, **43/43 selected quotes were literal source excerpts**, yet six expected-missing fields were filled and twelve nonmissing field choices differed from frozen labels. There were no empty-field omissions where the labels expected a quote; that does not mean completeness was solved: only **25/37 expected nonmissing field supports** were selected across the eight v5 papers.

Exact copying preserves wording, uncertainty, negation and numeric literals; it does **not** establish the correct role, entailment or scientific support. This evaluation observed real background-as-objective, result-as-dataset and finding-as-limitation errors. It does not demonstrate comprehensive prompt-injection resistance. No new adversarial live generation was spent in this public-only batch; prior deterministic quarantine behavior remains covered by isolated tests.

Strict exact-quote disagreement is not identical to a scientific error. [Developer review](C2_V4_V5_DEVELOPER_REVIEW_2026-10-20.json) records plausible alternatives without changing frozen gold or scores: corpus selection can be a method, a scanned-vessel sentence identifies less-specific materials, and a cutoff-stability finding can be an author takeaway. Theory/proof descriptions can overlap method and results. Conversely, assigning a photobleaching application as a study limitation or a background statement as the objective is a substantive field problem. Some labels are debatable; no adjusted accuracy estimate or independent quality guarantee is manufactured.

Raw reports and offline counts remain retained:

- [V4 tuning responses](C2_V4_TUNING_RESUMED_2026-10-20.json), [frozen-label scoring](C2_V4_TUNING_ADJUDICATION_2026-10-20.json).
- [V5 tuning responses](C2_V5_TUNING_RESULTS_2026-10-20.json), [scoring](C2_V5_TUNING_ADJUDICATION_2026-10-20.json).
- [V5 holdout responses](C2_V5_HOLDOUT_RESULTS_2026-10-20.json), [scoring](C2_V5_HOLDOUT_ADJUDICATION_2026-10-20.json).

## Implementation and preservation

`review/quote_analysis_v4.py` offers every safe short source sentence for each role, with model judgment rather than vocabulary gates. Its frozen tuning failure is preserved. `review/quote_analysis_v5.py` uses the same source spans but returns a complete literal sentence or empty string per field. Unsupported/free paraphrases, fragments, wrong identities, withheld sentences and oversized sentences are rejected mechanically. Empty roles remain empty; the application does not fill them from keywords or another response.

V3 segmentation and instruction-pattern quarantine remain unchanged. Original abstracts, citations, source observations, run/record keys, fingerprints, model/runtime settings, full requests/responses and reviewer notes are retained. Flagged sentences stay in original context but are withheld from inference/selection with an explicit partial-evidence warning. Unknown attacks may pass and legitimate evidence may be hidden. Source-presence validation cannot reject every semantically wrong-role quote; tests explicitly demonstrate that limitation.

`review/analysis.py` dispatches retained v1–v5 builders/validators and corresponding proposal formats 1–5 inside unchanged root review format 2. V1–v3 fixtures and prior evidence remain unchanged. A new mocked v1/v2/v3 fixture and tests guard exact reopening; seven prior actual v3 proposals were reconstructed unchanged. Existing v4 response reconstruction remains versioned after v5; unknown/tampered version/format combinations fail reopening. The UI keeps AI separate, requires review/note before acceptance and exports only accepted claims into separate CSV columns. SQLite schema/data and historical application scripts are unchanged.

`tools/analysis_adjudication.py` is a pure offline comparison utility. It verifies manifest hash/case/label integrity, separates source presence from field agreement, retains refused/unattempted cases in coverage denominators and never scores them as correct missing fields. A missing saved proposal is not automatically classified as preflight resistance: backend errors are preserved. New tests distinguish source-literal but wrong-role choices, false fills, omissions and coverage loss.

No inference protocol changed after holdout evaluation. The final UI copy was strengthened to disclose the observed failures and remove stale installation-approval wording; that status-text change affects no request or model setting. [Protocol freezes](C2_V5_PROTOCOL_FREEZE_2026-10-20.json) retain the inference source used for the trial.

## Resources and verification

Observed v4 generation latency was 22.012–26.578 seconds; v5 tuning 32.691–36.862 seconds; v5 holdout 29.634–32.835 seconds. [Resource summary](C2_V4_V5_RESOURCE_SUMMARY_2026-10-20.json) reports a sampled aggregate runtime working-set peak of **1,467,129,856 bytes**, no sampler errors and every pre-load sample above the unchanged **4,294,967,296-byte gate** (minimum 4,398,448,640 bytes). The gate is pre-load, not a continuous free-RAM floor. Some holdout inference overlapped isolated regression work; these are development-load observations, not a controlled speed comparison or total-private-memory guarantee. Models unload with `keep_alive=0`.

The unchanged baseline passed **168 tests in 35.434 seconds**. Focused quote checks passed 34 tests in 0.140 seconds; four offline scoring tests passed in 0.108 seconds. Final `python -m unittest discover -s tests -v` passed **184 tests in 35.350 seconds** after the final UI status warning (an earlier full run also passed in 45.290 seconds). All **37 active Python files** compiled in memory. Ordinary tests mock/block HTTP and use isolated temporary data; no production database is opened. V5 UI generation is mocked in AppTest; actual new model generation was programmatic. Browser layout/upload/download transfer and independent scientific correctness remain unverified. [Final verification and changed files](C2_V4_V5_VERIFY_2026-10-21.json).

## Next boundary

The twelve-call follow-up is exhausted, and none of these results authorizes synthesis or full Phase C completion. The next useful quality experiment needs a **new bounded inference allocation**; a larger-model comparison additionally needs explicit new model-download approval. Current evidence does not prove that either further prompting or a larger model will succeed. [Concrete optional next-model plan](C2_NEXT_MODEL_PILOT_PLAN.md) specifies an Apache-2.0 Qwen3 4B Q4_K_M candidate (~2.6 GB), estimated memory/headroom, versioned compatibility and the exact new authorization. No download or runtime change is made by that plan. Existing approval for routine code/testing remains valid; no repeat approval for the installed model or completed work is requested.

## Source attribution

- tuning: Atiyo Ghosh; Tatiana T. Marquez-Lago (2015), [Simulating Stochastic Reaction-Diffusion Systems on and within Moving Boundaries](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0133401); DOI `10.1371/journal.pone.0133401`. CC BY 4.0.
- tuning: Andreas Carlson; L. Mahadevan (2015), [Elastohydrodynamics and Kinetics of Protein Patterning in the Immunological Synapse](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1004481); DOI `10.1371/journal.pcbi.1004481`. CC BY 4.0.
- tuning: Marta Reyes; Mª Julia Morales; Mª Teresa Bajo (2023), [Judgments of learning in bilinguals: Does studying in a L2 hinder learning monitoring?](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0286516); DOI `10.1371/journal.pone.0286516`. CC BY 4.0.
- tuning: Ortal Harush; Leore Grosman (2021), [Toward the identification of social signatures in ceramic production – An archaeological case study](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0254766); DOI `10.1371/journal.pone.0254766`. CC BY 4.0.
- holdout: Álvaro Corral; Gemma Boleda; Ramon Ferrer-i-Cancho (2015), [Zipf’s Law for Word Frequencies: Word Forms versus Lemmas in Long Texts](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0129031); DOI `10.1371/journal.pone.0129031`. CC BY 4.0.
- holdout: H. Eden W. Cottee-Jones; Thomas J. Matthews; Tom P. Bregman; Maan Barua; Jatin Tamuly; Robert J. Whittaker (2015), [Are Protected Areas Required to Maintain Functional Diversity in Human-Modified Landscapes?](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0123952); DOI `10.1371/journal.pone.0123952`. CC BY 4.0.
- holdout: Matthias Steinfath; Silvia Vogl; Norman Violet; Franziska Schwarz; Hans Mielke; Thomas Selhorst; Matthias Greiner; Gilbert Schönfelder (2018), [Simple changes of individual studies can improve the reproducibility of the biomedical scientific process as a whole](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0202762); DOI `10.1371/journal.pone.0202762`. CC BY 4.0.
- holdout: Alan C.-N. Wong; Cindy M. Bukach; Crystal Yuen; Lizhuang Yang; Shirley Leung; Emma Greenspon (2011), [Holistic Processing of Words Modulated by Reading Experience](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0020753); DOI `10.1371/journal.pone.0020753`. Creative Commons Attribution License; version unspecified on publisher page.
