# Personal Research AI status and next steps — 2026-11-20

## Current position

The project is a local Streamlit literature discovery and review foundation. It searches OpenAlex and Crossref, stores records locally in SQLite, and supports screening and abstract based evidence notes. Full text review, cited synthesis, deep research, gap verification, idea development, solution experiments, and manuscript preparation are not implemented.

The uploaded snapshot passed 247 isolated tests in 41.031 seconds. This was the latest recorded verification of that snapshot, not a new test run on November 20. The production database and local pilot state were excluded from the public repository.

| Phase | Status | What exists and what remains |
| --- | --- | --- |
| A — Baseline and stability | Audits completed with bounded assurance | Two documented A/B audits and isolated regression coverage, including fixes for verified filtering, identity, validation, and export issues. Teammate should verify the claims against source and evidence. |
| B — Literature discovery | Bounded acceptance complete | OpenAlex and Crossref retrieval, filters, pagination budgets, deduplication, local storage, provenance, exports, and status reporting. Exhaustive recall and global counts are not established. |
| C — Literature review and paper analysis | In progress. AI quality not accepted | Manual screening and abstract evidence notes are implemented. AI proposals remain experimental with role accuracy, missingness, and completeness gaps. Conservative v3 is the default. Latest pilot checkpoint records 7 of 12 Qwen3 responses and five unattempted. Full text and synthesis are not implemented. |
| D — Deep research and research gaps | Planned | Compare supported findings, contradictions, limitations, and candidate gaps, with citations, counterevidence, search scope, and uncertainty. Novelty must remain a candidate until checked. |
| E — Ideas and solution verification | Planned | Rank ideas against evidence, feasibility, resources, and risks. Verify solutions through reproducible experiments, simulations, prototypes, or proofs. |
| F — Writing and publication support | Planned | Draft from cited sources and verified results, check claims and citations, prepare venue materials, and support revisions. |
| G — Integration and expansion | Planned | Integrate independently tested modules with shared provenance, decisions, history, exports, and replaceable backends. |

## Recommended next steps

1. Have the teammate audit Phases A–C against current source, tests, and dated evidence. Run the isolated test suite and report unsupported or stale claims.
2. Resolve the C2 evaluation question before presenting AI analysis as reliable. Use `docs/C2_ACCEPTANCE_RUBRIC.md` to freeze a fresh expert-reviewed plan and holdout before generation. Measure record binding, role relevance, missingness, essential fact coverage, claim support, failures, and reviewer disagreement. Do not repurpose the old pilot as a fresh holdout. Finishing its five unattempted cases alone will not meet the broader proposed evaluation.
3. Define Phase D's inputs and outputs using captured discovery runs and reviewer-checked evidence. Each candidate gap should link to supporting and conflicting claims, source identifiers, search dates/settings, coverage limits, and uncertainty.
4. Implement Phase D incrementally after reviewing its design. Test with synthetic or temporary data, preserve Phase C behavior, and avoid unverified novelty claims.

## Later work

After Phase D evaluation, proceed to Phase E, then Phase F, then integration in Phase G. Broader discovery recall, resumable/shared retrieval, multiple durable reviews, and revision history are separate optional enhancements.

## Handover links

- [Mission](https://github.com/Conditions-tech/personal-research-ai/blob/main/docs/MISSION.md)
- [Roadmap](https://github.com/Conditions-tech/personal-research-ai/blob/main/docs/ROADMAP.md)
- [Project status chronology](https://github.com/Conditions-tech/personal-research-ai/blob/main/docs/PROJECT_STATUS.md)
- [Phase A/B audit 1](https://github.com/Conditions-tech/personal-research-ai/blob/main/docs/AB_AUDIT_2026-10-20.md)
- [Phase A/B audit 2](https://github.com/Conditions-tech/personal-research-ai/blob/main/docs/AB_AUDIT_2_2026-10-20.md)
- [Phase B acceptance](https://github.com/Conditions-tech/personal-research-ai/blob/main/docs/PHASE_B_ACCEPTANCE.md)
- [Phase C plan](https://github.com/Conditions-tech/personal-research-ai/blob/main/docs/PHASE_C_PLAN.md)
- [Phase C acceptance gaps](https://github.com/Conditions-tech/personal-research-ai/blob/main/docs/PHASE_C_ACCEPTANCE_GAPS.md)
- [C2 acceptance rubric](https://github.com/Conditions-tech/personal-research-ai/blob/main/docs/C2_ACCEPTANCE_RUBRIC.md)
- [Usage guide](https://github.com/Conditions-tech/personal-research-ai/blob/main/docs/USAGE_GUIDE.md)
- [Testing guide](https://github.com/Conditions-tech/personal-research-ai/blob/main/docs/TESTING.md)
