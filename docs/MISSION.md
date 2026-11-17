# Personal Research AI mission

Confirmed directly by the user on 2026-10-20. This document preserves project direction across handovers; it does not override repository data-protection or approval instructions.

The user expanded the original three-workflow goal into a complete ten-stage research pipeline on 2026-10-20. Their typed request establishes the goal; the attached screenshots illustrate the intended stages and architecture rather than granting additional action permissions.

Build a personal, modular system that takes a topic through discovering research, reviewing evidence, developing and testing an original contribution, writing a manuscript, and preparing for publication.

## Research stages and outputs

| Stage | Responsibility | Expected output |
| --- | --- | --- |
| 1. Topic input and scope | Accept a topic, question, keywords or problem; clarify scope and propose search terms/synonyms. Keep the original topic and any accepted expansions traceable. | A scoped question and reproducible search plan. |
| 2. Global Literature Discovery | Search multiple sources for journal/conference papers and other relevant scholarly work, across disciplines and from the earliest available records through the search date. | Provider-specific reported counts, raw retrieved entries, filtered papers, deduplicated records, metadata and coverage limits. |
| 3. Literature review | Screen and organize studies by theme, problem, method, findings and historical development. Record selection criteria and inclusion/exclusion reasons. | A cited literature synthesis and screening record. A systematic-review claim requires a documented protocol and screening process. |
| 4. Individual paper analysis | Summarize each paper according to the user's configurable rules: objectives, methods, data, results, contributions, limitations and future work. | Source-linked summaries and a comparative evidence table. Detailed personal summary rules are not yet supplied. |
| 5. Deep research and research gaps | Compare evidence, contradictions, limitations and underexplored directions; check whether newer or related work already addresses a proposed gap. | Candidate gaps with supporting/counterevidence, search scope, uncertainty and citations. |
| 6. Research idea generation | Derive questions, hypotheses, methods and expected contributions from supported candidate gaps; evaluate novelty evidence, feasibility, resources and risks. | Ranked research ideas and a proposed research plan. |
| 7. Solution development and verification | Develop appropriate experiments, simulations, prototypes, methods or theoretical arguments; compare against suitable baselines and validate results. | Reproducible evidence, evaluation results, limitations and supported conclusions. A proposal or model-generated answer is not a verified solution. |
| 8. Research paper writing | Draft the title, abstract, introduction, related work, methodology, results, discussion, conclusion and references using actual sources and verified findings. | A manuscript with traceable claims, figures/tables and supporting materials. Never invent citations, experiments or results. |
| 9. Quality review and publication preparation | Review evidence, citations, methods, originality, reporting needs, venue fit and formatting; identify unresolved issues for the author. | A manuscript ready for the user's final review and a publication-readiness report. |
| 10. Submission and publication decision | Prepare a cover letter/submission package, support submission tracking, and help answer reviewer comments and revisions. Actual submission needs the user's specific authorization. | Submission materials and revision support. The user approves submission; acceptance/publication is decided by the venue and cannot be guaranteed. |

The stages form an iterative workflow: Stage 3 begins screening/organization, Stage 4 adds individual evidence, and Stage 3's synthesis is then updated. Gap checks can require new searches; experiments can change ideas and conclusions; reviewer feedback can return work to earlier stages.

## Model and evidence architecture

Ten stages do not require ten separately deployed large models. Use a research coordinator plus modular discovery, review/analysis, deep research, idea/verification, and writing/quality engines. Each engine can use a suitable swappable model or a deterministic tool. Evaluate backend quality, cost, licence and local-resource needs before selection. Future user-defined tools, models, data sources and requirements must fit without rebuilding the application.

Every stage should preserve source identifiers/citations, evidence passages where available, search settings and dates, decisions, intermediate outputs and verification status. Distinguish metadata-only evidence, abstract-based analysis and full-text analysis; use accessible full texts only with appropriate access/licence handling. Mark interpretation, missing information, candidate novelty and untested claims explicitly. No system may claim to count every relevant paper ever published or guarantee a novel result without supporting evidence and stated coverage.

Planned research checkpoints let the user select the research question/idea, assess the proposed method and findings, and approve the final manuscript/submission. These are substantive research decisions; routine reversible engineering continues within the existing delegation.

## Working relationship

The user delegates architecture, engineering, defect review, tests and project coordination, with minimal manual editing or repeated handoffs. Work incrementally on the actual workspace, communicate plainly and directly, and continue project work until the user says **FINISH**. A completed milestone is not completion of this system. Keep current verified behavior separate from planned capabilities in the handover.

Respect `AGENTS.md`: preserve historical scripts and production research data, use temporary test databases, and retain explicit approval boundaries for production schema/data changes, packages, paid services and Git operations. The master project instruction authorizes incremental product development toward these workflows; it does not authorize those separate restricted operations.

The target remains i3-8100, 8 GB RAM and integrated graphics with a free/open-source preference. CPU/RAM/Windows were rechecked during C2; GPU details remain inherited because CIM access was denied. The installed Ollama/Qwen backend has an [original failed benchmark](LOCAL_ANALYSIS_BENCHMARK_2026-10-20.md) and an approved [quote-first follow-up](QUOTE_FIRST_C2_2026-10-20.md). The latter improves selected-field fidelity on synthetic data but still omits available information. This does not establish general scientific reliability or authorize moving to synthesis.

Current implementation and next steps are in [Project Status](PROJECT_STATUS.md) and [Roadmap](ROADMAP.md).
