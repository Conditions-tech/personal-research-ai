# Reviewing abstract-based analysis

The current app default is conservative `abstract-quotes-v3`. It may omit uncued prose or refuse a public abstract. V4/v5 remain readable but failed public field-quality checks; v6 is a separate experimental report format, not an app proposal. None provides reliable autonomous scientific analysis. Use the captured source and your own judgment; a copied sentence can still be placed under the wrong role.

## Work from the captured paper

Start with the source run, record key, DOI/authors and captured abstract shown in Literature review. Search filters are candidate retrieval settings, not inclusion decisions. Record your screening decision and reason against your question/criteria. Metadata-only papers can be screened but cannot acquire abstract content claims. An incomplete discovery run contains only its retrieved candidates and does not establish comprehensive literature coverage.

For each of the six approved fields, ask what this study explicitly states:

| Field | What to look for | Common error seen in the experiments |
| --- | --- | --- |
| Objective | This work's purpose or research question | General background or a reported result substituted for its aim |
| Method | What was done: design, procedure, derivation or analysis | A finding substituted for a procedure |
| Dataset | Identified studied data, materials, corpus or sampled population | A model, prediction or outcome called a dataset |
| Results | Observed/computed/proved findings, retaining null results and qualifications | A purpose or policy implication substituted for a finding |
| Limitations | An explicit boundary or inability of this study/inference | Background difficulties, a procedure or a negative finding called a study limitation |
| Conclusion | The authors' takeaway or qualified implication | A procedure treated as a takeaway |

Roles may overlap in compound sentences. A sentence describing corpus selection can support a method; a direct result may also be an author takeaway. Record a defensible alternative with an explanation, rather than treating one developer label as unique scientific truth. Keep uncertainty and negation intact. Missing in the captured abstract does not establish that the paper lacks the feature, and an unsupported AI selection is not evidence for it.

## Keep reviewer notes separate from model output

The reviewer-authored section lets you save a paper-statement, a clearly labelled interpretation, or missing information for each field. Nonmissing notes require an exact excerpt from this paper's captured abstract. The excerpt check establishes text presence only; you assess whether it supports your note and whether interpretation is justified. Save the evidence note before moving to another paper or action. Missing notes contain no claim/excerpt; clearing a note is an explicit saved action.

Generated proposals remain separate. Check the model/protocol details, original context and any withheld-sentence warning. Reject a proposal with a reason when a role is wrong or the abstract does not support a fill; retain your corrected work in reviewer-authored notes. Do not accept a wrong field merely because the sentence was copied exactly. Acceptance requires checking every field and a review note. No source, screening decision or manual note is replaced by acceptance.

The comparison CSV has separate manual and `ai_` columns. Pending/rejected AI claims do not become comparison findings. If an earlier proposal was accepted and a newer one rejected, the earlier accepted proposal remains in the AI columns; inspect `ai_latest_status`, accepted draft ID, protocol and reviewer note. CSV is a worksheet, not a synthesis or independent scientific verification.

## Preserve and reopen work

Review work is session-only: download the complete review JSON before closing/restarting. CSV does not contain all the original work. The current UI holds one review at a time; save before opening a fresh session to work on another review. Reopening does not repeat discovery or model calls. Source hashes detect accidental changes, not authorship, source authenticity or scientific truth.

If manually authored work exceeds the existing 10 MiB reopening limit, the app warns that its JSON cannot be reopened. The download still preserves the complete work without truncating notes. Keep that backup; use a smaller review for reopening. The warning does not provide large-file import or durable storage.

Use the intact exported JSON. Duplicate object keys and nonfinite JSON values are rejected instead of silently replacing notes. Root creation/update times and completed screening/authored-note timestamps must be timezone-aware and present. Untouched pending decisions and missing notes may retain null action times. Hand-edited files that remove required metadata are rejected; do not invent timestamps or overwrite the original file to conceal lost history. Invalid imports leave existing work intact. The normal import limit remains 10 MiB; legacy proposal versions 1–5 remain supported. V6 diagnostic reports must not be passed off as a review JSON workspace.

## What remains outside this workflow

Abstract excerpts do not supply full-text page/section citations. Do not infer causal or scientific validity from a hash, exact match, successful test or model confidence. Independent domain review, broader scientific validation, full-text analysis and literature synthesis remain unfinished. [Current evaluation](C2_SINGLE_ROLE_EVALUATION_2026-10-21.md) records the failed v6 hypothesis and the [Phase C handover](PHASE_C_C2_HANDOVER.md) records the current boundary.
