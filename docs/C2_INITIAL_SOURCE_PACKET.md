# Phase C2 initial source packet

Three source snapshots for preparing independent review. Selection follows the [initial sample plan](C2_INITIAL_SAMPLE_PLAN.md). Source versions, licence URLs, SHA-256 hashes and stable span ranges are recorded in the [snapshot manifest](c2_initial_snapshots/manifest.json), captured on 2026-11-16. Annotate the linked reviewer text so both reviewers work from the same bytes.

| Case ID | Publisher and year | Article and DOI | Abstract locator and rights |
| --- | --- | --- | --- |
| C2-INIT-01 | PLOS ONE, 2024 | Enders et al. [Evidence of elevated situational awareness for active duty soldiers during navigation of a virtual environment](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0298867). DOI `10.1371/journal.pone.0298867`. | **Abstract** on publisher HTML. The article carries a CC0 public domain dedication. |
| C2-INIT-02 | Frontiers in Education, 2024 | Lechuga, Ortega-Tudela and Gómez-Ariza. [Retrieval-based concept mapping makes a difference as a retrieval practice activity: a study with high school students](https://www.frontiersin.org/journals/education/articles/10.3389/feduc.2024.1287744/full). DOI `10.3389/feduc.2024.1287744`. | **Abstract** on publisher HTML. Article copyright statement specifies CC BY with attribution. |
| C2-INIT-03 | Astronomy & Astrophysics, 2025 | Geraldía-González et al. [Discovery of a transiting hot water-world candidate orbiting Ross 176 with TESS and CARMENES](https://www.aanda.org/articles/aa/pdf/2025/08/aa53719-25.pdf). DOI `10.1051/0004-6361/202553719`. | **Abstract** from the [EDP Sciences deposit in Crossref](https://api.crossref.org/works/10.1051/0004-6361/202553719). The publisher record and deposit specify CC BY 4.0. The deposit is the source of record for this exercise. |

## Coordinator handoff

Give both reviewers the same files with the manifest, publisher citations and licences. The HTML captures decode entities and normalize layout whitespace. Frontiers section headings are retained. The astronomy snapshot uses `_{...}` and `^{...}` to preserve JATS subscript and superscript notation. Both the original deposited fragment and the reviewer rendering are frozen and hashed. Direct requests to the A&A HTML and PDF returned 403, so equivalence to the rendered PDF remains unverified. Use the deposited version consistently for this exercise. If the evaluation requires the rendered publisher version, mark that version unverified and exclude the astronomy case from that evaluation.

| Case ID | Frozen reviewer text | Source version | Span IDs |
| --- | --- | --- | --- |
| C2-INIT-01 | [PLOS abstract](c2_initial_snapshots/C2-INIT-01.txt) | Publisher HTML | P1 |
| C2-INIT-02 | [Frontiers abstract](c2_initial_snapshots/C2-INIT-02.txt) | Publisher HTML | P1–P4 |
| C2-INIT-03 | [Astronomy abstract](c2_initial_snapshots/C2-INIT-03.txt) | [Publisher's deposited JATS fragment](c2_initial_snapshots/C2-INIT-03.jats-fragment.txt) | P1 |

For each excerpt, record the span ID and exact excerpt. When needed to disambiguate repeated wording, add a zero-based Unicode character range with an exclusive end position relative to the full reviewer text. Use the manifest's hash for the worksheet's frozen abstract hash.

Give each reviewer a separate copy of section 1 of the [reviewer worksheet](C2_REVIEWER_WORKSHEET.md). Collect all six source statuses, exact evidence spans and essential findings from each reviewer before either sees another submission. Preserve both submissions. Use section 2 to align equivalent facts and have a third reviewer reconcile disagreements. Record both entries, the decision, its reason and unresolved items. Keep this practice packet outside acceptance scoring. See the [acceptance rubric](C2_ACCEPTANCE_RUBRIC.md).

## Sampling record

The searches used the dates and topics in the plan. The frame below preserves publisher hits in order within each query. Alternate file formats of the same DOI were collapsed into one entry. Stop screening when a slot has an eligible selection. These were scoped original studies with English abstracts and publication dates within 2024–2025.

| Slot | Rank | Publisher candidate | Outcome |
| --- | --- | --- | --- |
| C2-INIT-01 | 1 | [PLOS e0298867](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0298867) | Selected |
| C2-INIT-01 | 2 | [PLOS e0317026](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0317026) | Later candidate, not screened |
| C2-INIT-01 | 3 | [PLOS e0333039](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0333039) | Later candidate, not screened |
| C2-INIT-02 | 1 | [Frontiers 1287744](https://www.frontiersin.org/journals/education/articles/10.3389/feduc.2024.1287744/full) | Selected |
| C2-INIT-02 | 2 | [Frontiers 1632206](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2025.1632206/full) | Later candidate, not screened |
| C2-INIT-02 | 3 | [Frontiers 1457504](https://www.frontiersin.org/journals/education/articles/10.3389/feduc.2024.1457504/full) | Later candidate, not screened |
| C2-INIT-03 | 1 | [A&A 693 A235](https://www.aanda.org/articles/aa/pdf/2025/01/aa51057-24.pdf) | Excluded because HTML and PDF checks returned 403 and eligibility could not be verified |
| C2-INIT-03 | 2 | [A&A 700 A216](https://www.aanda.org/articles/aa/pdf/2025/08/aa53719-25.pdf) | Selected via indexed publisher PDF after rerunning the same scoped search |
| C2-INIT-03 | 3 | [A&A 696 A86](https://www.aanda.org/articles/aa/pdf/2025/04/aa52969-24.pdf) | Later candidate from same rerun, not screened |

The identity check indexed case IDs, normalized titles, DOI fields, record keys and source URLs from 114 local documentation and test-fixture JSON files. It excluded expected answers, annotation fields and abstract text from comparison. No selected identity matched that index or another selected paper. This check cannot rule out an undocumented previous evaluation or a paper published under an unrelated title and DOI. Search ranking, topic choice and access affected selection. The packet cannot estimate performance across disciplines or languages.

The rejected A&A 693 A235 entry remains excluded. For the selected A&A 700 A216 entry, the EDP Sciences alternate route also returned 403. The publisher mirror and the author institution's direct routes could not be verified because TLS validation failed. The public Crossref record returned HTTP 200 and supplied the EDP Sciences abstract, matching DOI and title, and the version-of-record licence. This changes the capture route for the selected DOI. It adds no replacement paper.
