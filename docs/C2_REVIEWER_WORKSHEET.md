# Phase C2 reviewer worksheet

Use one copy per case per reviewer. Apply the [acceptance rubric](C2_ACCEPTANCE_RUBRIC.md). The evaluation coordinator supplies the case, frozen abstract with stable sentence IDs, source locator and capture hash. The coordinator keeps the output files and reviewer submissions separate during source annotation.

## 1. Annotate the source independently

| Case ID | Reviewer ID | Date | Source locator | Frozen abstract hash | Evidence availability |
| --- | --- | --- | --- | --- | --- |
| | | | | | abstract available / unavailable |

Complete every field. Use **present** when the abstract explicitly supports it, **absent** when an available abstract contains no support, **ambiguous** when there is a genuine role or evidence dispute, and **unavailable** when there is no usable abstract. Record a short reason for absent or ambiguous decisions. For available evidence, record the sentence ID and exact text span. Multiple spans may support one field. A shared sentence can support two fields if you identify what it supports in each.

| Field | Source status | Acceptable evidence spans | Reason |
| --- | --- | --- | --- |
| objective | | | |
| method | | | |
| dataset | | | |
| results | | | |
| limitations | | | |
| conclusion | | | |

List the distinct facts a short summary should retain. Use one row per fact and preserve qualifiers that change its meaning. Assign each fact one primary field for coverage scoring. Use temporary IDs such as `R1-F1` in your copy. The adjudicator assigns canonical IDs after aligning both inventories by meaning.

| Fact ID | Primary field | Essential fact in your own words | Exact evidence span and sentence ID | Meaning-changing qualifiers |
| --- | --- | --- | --- | --- |
| | | | | |

Submit this section before receiving outputs or seeing another reviewer's labels. Two reviewers with relevant subject expertise complete it separately.

## 2. Reconcile source annotations before opening outputs

Preserve the two original worksheets. Compare field status, accepted spans and essential fact lists. Align facts by meaning before comparing their IDs. Record agreements as well as disagreements, and let a third reviewer resolve disagreements against the source. Record the reason, original entries and final decision. If a material dispute remains unresolved, retain it as unresolved and report its effect separately. The coordinator records the applicable scoring rule before reading outputs.

| Case and field | Issue (status, span, fact or role) | Reviewer 1 entry | Reviewer 2 entry | Final status, span or canonical fact ID | Adjudicator ID and rationale |
| --- | --- | --- | --- | --- | --- |
| | | | | | |

The coordinator freezes the reconciled reference, case eligibility, thresholds and scoring rules before output review. Record the reference version or hash, freeze date and reviewers. Keep the rubric's numerical thresholds as proposals until the evaluation plan is agreed.

## 3. Review masked outputs against the frozen reference

The coordinator assigns a draft code and keeps the model mapping private until scoring is frozen. Use randomized order where practical. A coordinator with access to provenance checks identity and records pass/fail before handing the masked draft to reviewers. Reviewers record any unmasking.

| Case ID | Draft code | Reviewer ID | Outcome | Outcome reason | Identity and provenance | Unmasking |
| --- | --- | --- | --- | --- | --- | --- |
| | | | valid / invalid / refused / failed / unattempted | | pass / fail / not applicable | |

For a valid draft, make one row per field. A populated field can contain relevant material and a wrong-role component. Record **relevant**, **wrong role**, **mixed** or **unresolved** and flag a mixed row in the wrong-role count. Only entirely relevant rows earn relevance credit. Give coverage credit only for a faithful essential fact in its assigned field. A blank in an answerable field is a blank omission. A blank in an explicitly absent field is a correct blank. Populating an absent field is a false fill. Preserve ambiguous or unavailable source statuses separately. For invalid, failed, refused or unattempted cases, record the outcome and leave field scores unassigned. Keep eligible cases in the assigned fact denominator.

| Field | Filled or blank | Source status | Role verdict | Missingness decision | Covered canonical fact IDs | Material error and reason |
| --- | --- | --- | --- | --- | --- | --- |
| | | | | | | |

Split each filled field into atomic assertions. Record the excerpt or its sentence ID and exact span. A literal match and a wrong role can coexist with claim support. Mark **supported** for a faithful claim, **contradicted** when the evidence conflicts with it, **unsupported** when the cited text and context do not justify it, and **unresolved** when support cannot be settled. Check attribution, negation, quantities, scope and qualifications. Mark explicit interpretations separately from paper statements.

| Field and claim ID | Atomic assertion and kind | Cited span | Literal traceability | Support verdict | Material error and reason |
| --- | --- | --- | --- | --- | --- |
| | | | pass / fail | | |

Reconcile output verdicts using the disagreement table from section 2 with the draft code and claim ID added to each issue. Preserve original scores. Record outcome totals, per-field numerators and denominators, unique covered fact IDs, claim totals and material errors before unmasking. Follow the rubric for aggregate reporting and zero denominators.

For coordinator practice using invented examples, use the [synthetic dry run](C2_REVIEWER_DRY_RUN.md). Withhold its worked answers until trainees submit the practice source worksheet.
