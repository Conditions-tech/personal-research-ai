# Phase C2 synthetic annotation exercise

All sources, labels and draft text in this exercise are invented. Give trainees only the source packet below and section 1 of the [reviewer worksheet](C2_REVIEWER_WORKSHEET.md) for the first pass. Keep the worked reconciliation and draft with the coordinator until trainees submit their source annotations.

## Source packet

Case `SYN-01`, locator `synthetic:SYN-01`, source version `1`. For practice, the numbered text below is the frozen source.

| Sentence | Abstract text |
| --- | --- |
| S1 | We tested whether reflective labels improved the readability of storage bins. |
| S2 | We randomly assigned 40 bins to reflective or matte labels and measured reading time under fixed lighting. |
| S3 | Reading time was shorter with reflective labels on the first trial. |
| S4 | No difference was detected on the second trial. |

Case `SYN-02`, locator `synthetic:SYN-02`, source version `1`. The abstract is unavailable.

## Coordinator key

Two simulated reviewers agree on objective (S1), method (S2) and results (S3–S4). Reviewer 1 labels dataset present and cites the 40 bins in S2. Reviewer 2 marks it ambiguous because that sentence also describes the procedure. The simulated adjudicator records **dataset present** with S2 as an acceptable span. The studied units and the procedure are distinct despite appearing in the same sentence. Both reviewers mark limitations and conclusion absent. The second case has six unavailable fields and no essential facts.

| Fact ID | Field | Essential fact | Source |
| --- | --- | --- | --- |
| F1 | objective | Tested whether reflective labels improve bin readability. | S1 |
| F2 | method | Random assignment to reflective or matte labels with reading time measured under fixed lighting. | S2 |
| F3 | dataset | Studied 40 bins. | S2 |
| F4 | results | Reading time was shorter with reflective labels on the first trial. | S3 |
| F5 | results | No difference was detected on the second trial. | S4 |

### Invented masked draft

Draft `D-17` for `SYN-01` has matching case identity in this exercise. The table shows the sentence each assertion cites in full. Objective, dataset and results are filled. Method, limitations and conclusion are blank.

| Field | Claim ID | Atomic assertion | Cited sentence | Support verdict |
| --- | --- | --- | --- | --- |
| objective | C1 | The study tested whether reflective labels improve bin readability. | S1 | supported |
| dataset | C2 | Reading time was shorter with reflective labels on the first trial. | S3 | supported |
| results | C3 | Reading time was shorter with reflective labels on the first trial. | S3 | supported |
| results | C4 | The study detected shorter reading time with reflective labels on the second trial. | S4 | contradicted |
| results | C5 | Glare caused the difference in reading time. | S3 | unsupported |

| Field | Role verdict | Missingness decision | Covered facts |
| --- | --- | --- | --- |
| objective | relevant | filled with source support available | F1 |
| method | not applicable | blank omission | |
| dataset | wrong role | filled with source support available | |
| results | relevant | filled with source support available | F4 |
| limitations | not applicable | correct blank | |
| conclusion | not applicable | correct blank | |

The dataset claim is faithful to the abstract and still in the wrong field. The results assertions concern findings, so relevance remains separate from support. C4 is a material error because it reverses the second trial finding. F5 is uncovered even though the results field is filled. C5 has no causal evidence. Every cited sentence is literal.

For `SYN-02`, the simulated preflight refuses generation because the abstract is unavailable. Record the verified cause with the workflow outcome and leave the field and claim tables unassigned. The case contributes zero correct blanks.

Expected exercise totals for the scored draft are 5/5 literal citations, 2/3 relevant filled fields, 1/3 wrong-role fills, 2/2 correct blanks on absent fields, 1/4 blank omissions on answerable fields, 2/5 essential facts covered and 3/5 supported assertions. Separately record one contradiction and one unsupported claim. These invented outcomes demonstrate the worksheet and give no evidence about model quality or reviewer agreement.
