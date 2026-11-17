# C2 follow-up — versioned quote-first analysis

The user approved focused improvements on the installed model after the first benchmark failed. No installation/download, model/runtime change, external inference, Git operation or production data/schema change was made. **Version two improves selected-field fidelity on the small synthetic evaluation, but still omits available information. Full quality acceptance and Phase C remain incomplete.**

## Changed behavior

`abstract-quotes-v2` asks the model to select an original source span independently for each approved field. Deterministic English cues restrict eligible sentence-sized spans; explicit field definitions distinguish objective, procedure, dataset/participants/materials, observed findings, study limitations and author conclusions. A result cannot be offered as a dataset simply because it occurs third. Titles/citation metadata, reviewer notes and other papers are omitted from model input; full citations, original evidence, run/record identities and source observations remain in the saved proposal context.

The response contains only bound run/record/evidence identities and six integer selections. It cannot introduce a new paraphrase, number, shortened quote or interpretation. The application derives each nonmissing `text` and `excerpt` from the same complete selected source span, retaining wording and negation. Wrong identity, unknown fields, Boolean/noninteger IDs and out-of-role/range selections are refused before state changes. Model `-1` becomes an empty missing field; the UI explains that **no quote selected does not prove information absent**. Reviewer-authored interpretations and existing notes remain independent.

Obvious instruction-like abstract text is refused before inference, with manual review still available. This is a conservative pattern check: legitimate prompt-injection research can be falsely blocked, and unfamiliar/obfuscated instructions can pass. Sentence segmentation and role cues are English heuristics, not semantic entailment or scientific verification. Abbreviations can fragment spans; long sentences stay in the bounded evidence input but are not eligible as oversized claims. Evidence without qualifying cues is refused rather than summarized from guesses. These restrictions reduce coverage and do not establish reliable extraction across languages/disciplines.

No automatic post-fill was added when the model abstains. A keyword cue alone does not justify filling a field the model declined. Human review remains required before acceptance.

## Compatibility and provenance

- New generation defaults to prompt `abstract-quotes-v2` and proposal format 2. The review workspace container stays version 2. The six normalized field names/kinds and comparison/manual-note separation remain compatible.
- Saved `abstract-analysis-v1` proposals retain format 1 and their exact original system prompt, options, schema, raw response and claims. Their previous validation path remains available. Neither historical requests nor old analysis are rewritten or silently reclassified.
- `build_request` and `validate_response` retain their legacy version-one defaults for direct callers; pass `prompt_version=CURRENT_PROMPT_VERSION` for v2. `generate_analysis` defaults to the active v2 protocol. Validation/reopening dispatches using each saved proposal's explicit prompt version and checks the matching proposal format/request/response.
- The new `review/quote_analysis.py` owns the v2 prompt, segmentation and eligibility rules. **Keep version-two rules stable**; future changed rules/prompts require a new version plus retained old reconstruction. Frozen synthetic v1 and mixed v1/v2 JSON fixtures guard reopening compatibility. Those fixtures use mocked generation only; they are compatibility evidence, not live AI evidence.
- Both protocols preserve original discovery evidence, citations, model/digest/runtime details, exact request settings, raw model output and fingerprints. Review decisions remain pending until explicit checking/note acceptance. No SQLite review persistence or schema changes were introduced.

## Real evaluation on the unchanged installed model

Ollama 0.40.6 and model digest `65ec06548149b04c096a120e4a6da9d4017ea809c91734ea5631e89f96ddc57b` were rechecked. Loopback/cloud-disabled settings and the 4 GiB pre-load memory gate remained in effect; no user applications were closed. The same CPU/context/options were used. Original failed v1 benchmark/adjudication files are preserved unchanged.

Nine fixed synthetic cases were attempted: the five earlier cases plus four fresh cases, including reordered structured fields, a nonempirical mathematical proof, uncertainty/participants, and an instruction variant. Case texts and expected field selections were fixed before output inspection; source/rules were frozen before inference. The eligibility rules were refined during **offline preflight**, not after seeing live answers. These are agent-authored examples, not independent/blinded scientific validation.

Command:

```powershell
python tools/local_analysis_benchmark.py --live-local --fresh --report docs/QUOTE_V2_BENCHMARK_2026-10-20.json
```

There were **eight actual model generations**: seven programmatic cases and one guarded temporary AppTest generation. Two instruction-like cases were refused without a model request. This demonstrates deterministic refusal, not learned model attack resistance. Every actual response passed identity/schema/selection checks; no backend outage or timeout occurred.

| Case | Field assessment against the fixed synthetic source |
| --- | --- |
| Explicit findings | All six expected fields selected; named Toy dataset retained instead of a limitation. |
| Missing information | Objective selected; five intentionally unavailable fields abstained. |
| Negative result | Negative finding preserved. Method, dataset and conclusion were unnecessarily omitted. |
| Contradictory title | Actual negative abstract finding selected; title was not supplied to the model. |
| Instruction fixture | Refused before inference. |
| Fresh reordered structured abstract | All six expected fields selected despite changed source order. |
| Fresh mathematical proof | Five expected quotes and missing empirical dataset selected correctly. |
| Fresh uncertainty/participants | Uncertainty and negation retained; available participant evidence omitted from dataset. |
| Fresh instruction variant | Refused before inference. |

The seven programmatic cases matched **38 of 42** predetermined field expectations; four mismatches were omissions. Five cases had complete expected coverage. Agent inspection found the nonmissing selected quotes faithful and field-relevant within these fixtures; this is not a population accuracy estimate. The real UI example preserved notes/source evidence and passed pending generation, acceptance/rejection and JSON reopening checks, but omitted its available limitation (five of six expected fields). Automated synthetic acceptance actions are not substantive user/scientific approval.

Programmatic real-generation latency was **16.718–17.851 seconds**, mean **17.286 seconds**; UI generation/render was **18.977 seconds**. Peak sampled aggregate runtime working set was **1,401,036,800 bytes** (about 1.40 GB / 1.30 GiB), with no sampler errors. These are normal-desktop observations on short synthetic inputs; 250 ms working-set sampling includes shared/file-backed pages and is not a hard/private-memory maximum or controlled performance benchmark.

Evidence: [reviewed preflight](QUOTE_V2_PREFLIGHT_REVIEWED_2026-10-20.json), [fixed expectations](QUOTE_V2_EXPECTED_2026-10-20.json), [unchanged raw responses](QUOTE_V2_BENCHMARK_2026-10-20.json), [adjudication and omissions](QUOTE_V2_ADJUDICATION_2026-10-20.json). The earlier [offline design preflight](QUOTE_V2_PREFLIGHT_2026-10-20.json) remains available. The live source/rules hash still matches the evaluated source; no new protocol tuning was performed after inspecting this run.

## Regression checks and remaining work

Fresh baseline: 137 tests passed in 34.573 seconds. Thirteen new isolated tests cover field-role failures, negation, abstention, blocked instructions/false positives, fresh structured/math cases, identity/type rejection, exact source preservation, backend failure and fixed v1/mixed-version reopening. Existing legacy tests explicitly exercise v1; UI fixtures now supply v2 selections. All ordinary HTTP remains mocked/blocked and SQLite isolated.

Final suite and protected-file/source-stability/diff/link checks are recorded in [v2 verification](QUOTE_V2_VERIFY_2026-10-20.json). No actual user research was used. Existing app/storage/provider code, production database, historical scripts, requirements and original benchmark evidence remain unchanged.

Next recommended work is broader field-coverage/abstention evaluation and careful handling of abbreviations/uncued evidence, with a new retained protocol version for changed rules. Real-paper, multilingual and independent quality evaluation remain open. Do not silently fill omissions or claim comprehensive instruction resistance, scientific support, full-text analysis, synthesis or all of Phase C complete.
