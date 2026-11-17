"""Evidence/screening contracts using synthetic provider fixtures and no storage."""

import copy
import csv
import io
import json
import unittest
from unittest.mock import Mock, patch

from discovery.providers import OpenAlexAdapter
from discovery.retrieval import RetrievalBudget, retrieve
from discovery.runs import make_run
from review.workspace import (
    SUMMARY_FIELDS, annotate_paper, comparison_csv, comparison_rows, create_review,
    export_review, restore_review, screen_paper,
)


def fixture_run():
    budget = RetrievalBudget(5)
    result = retrieve(OpenAlexAdapter(Mock(return_value={"meta": {"count": 99}, "results": [
        {"id": "https://openalex.org/W1", "doi": "10.1234/one", "title": "Identical café title",
         "abstract_inverted_index": {"We": [0], "tested": [1], "a": [2], "method.": [3]}},
        {"id": "https://openalex.org/W2", "doi": "10.1234/two", "title": "Identical café title"},
    ]})), "synthetic question", budget)
    return make_run("synthetic question", budget, [result])


class ReviewWorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch("requests.sessions.Session.request", side_effect=AssertionError("Live HTTP blocked.")))
        self.run = fixture_run()
        self.review = create_review(self.run, "  Research question  ", "Relevant methods", "Unrelated populations")
        self.first, self.second = [r["record_key"] for r in self.run["records"]]

    def test_snapshot_keeps_identity_context_and_missing_evidence_without_inventing_claims(self):
        self.assertEqual(self.review["protocol"]["question"], "Research question")
        self.assertEqual(self.review["run"], self.run)
        self.assertEqual(self.review["summary_fields"], list(SUMMARY_FIELDS))
        self.assertEqual(len(self.review["papers"]), 2)  # Identical titles are separate.
        rows = comparison_rows(self.review)
        self.assertEqual([r["evidence_depth"] for r in rows], ["abstract-based", "metadata-only"])
        self.assertTrue(all(r["decision"] == "pending" for r in rows))
        self.assertTrue(all(r["results_kind"] == "missing" for r in rows))
        self.run["records"][0]["abstract"] = "A later search changed this."
        self.run["manifest"]["settings"]["year_from"] = 2000
        self.assertEqual(self.review["run"]["records"][0]["abstract"], "We tested a method.")
        self.assertIsNone(self.review["run"]["manifest"]["settings"]["year_from"])

    def test_protocol_requires_explicit_question_and_both_screening_criteria(self):
        for values in [("", "in", "out"), ("q", " ", "out"), ("q", "in", None)]:
            with self.subTest(values=values), self.assertRaises(ValueError):
                create_review(self.run, *values)

    def test_invalid_candidate_identity_counts_and_missing_provenance_rejected(self):
        for change in (lambda r: r["manifest"]["counts"].update(unique_in_run=3),
                       lambda r: r["records"][1].update(record_key=self.first),
                       lambda r: r["manifest"].update(provenance=[]),
                       lambda r: r["manifest"].update(coverage_limits="invalid")):
            run = copy.deepcopy(self.run)
            change(run)
            with self.assertRaises(ValueError):
                create_review(run, "q", "in", "out")

    def test_screening_requires_reason_and_does_not_change_original_or_other_paper(self):
        before = copy.deepcopy(self.review)
        for decision in ("include", "exclude", "uncertain"):
            with self.subTest(decision=decision), self.assertRaises(ValueError):
                screen_paper(self.review, self.first, decision, " ")
        updated = screen_paper(self.review, self.second, "exclude", "  Unrelated population  ")
        self.assertEqual(self.review, before)
        self.assertEqual(updated["papers"][self.second]["reason"], "Unrelated population")
        self.assertEqual(updated["papers"][self.first]["decision"], "pending")
        self.assertIsNotNone(updated["papers"][self.second]["screened_utc"])

    def test_unknown_paper_decision_field_and_claim_kind_rejected(self):
        for action in (
            lambda: screen_paper(self.review, "unknown", "include", "Relevant"),
            lambda: screen_paper(self.review, self.first, "verified", "Relevant"),
            lambda: annotate_paper(self.review, self.first, "novelty", "missing"),
            lambda: annotate_paper(self.review, self.first, "method", "verified"),
        ):
            with self.assertRaises(ValueError):
                action()

    def test_claims_require_this_abstract_and_missing_cannot_hide_a_claim(self):
        for key, kind, text, excerpt in [
            (self.first, "paper-statement", "Method was tested", ""),
            (self.first, "paper-statement", "", "tested a method."),
            (self.first, "paper-statement", "Unsupported numerical result", "Accuracy was 99%"),
            (self.second, "interpretation", "Wrong paper", "tested a method."),
            (self.first, "missing", "Hidden claim", ""),
        ]:
            with self.subTest(key=key, kind=kind, text=text), self.assertRaises(ValueError):
                annotate_paper(self.review, key, "method", kind, text, excerpt)
        self.assertEqual(self.review["papers"][self.first]["analysis"]["method"]["kind"], "missing")

    def test_explicit_and_interpretive_notes_preserve_quotes_and_citations(self):
        updated = annotate_paper(self.review, self.first, "method", "paper-statement", "A method was tested.", "tested a method.")
        updated = annotate_paper(updated, self.first, "conclusion", "interpretation", "The method needs further evaluation.", "tested a method.")
        row = comparison_rows(updated)[0]
        self.assertEqual(row["doi"], "10.1234/one")
        self.assertEqual(row["method_kind"], "paper-statement")
        self.assertEqual(row["conclusion_kind"], "interpretation")
        self.assertEqual(row["method_excerpt"], "tested a method.")
        cleared = annotate_paper(updated, self.first, "method", "missing")
        self.assertEqual(cleared["papers"][self.first]["analysis"]["method"]["text"], "")

    def test_snapshot_mutation_rejected_by_updates_and_exports(self):
        self.review["run"]["manifest"]["query"] = "Misattributed query"
        for action in (lambda: screen_paper(self.review, self.first, "include", "Relevant"),
                       lambda: annotate_paper(self.review, self.first, "method", "missing"),
                       lambda: export_review(self.review), lambda: comparison_csv(self.review)):
            with self.assertRaises(ValueError):
                action()

    def test_json_reopen_and_csv_preserve_unicode_decisions_and_complete_evidence(self):
        updated = screen_paper(self.review, self.first, "include", "Relevant to café methods")
        updated = annotate_paper(updated, self.first, "method", "paper-statement", "Tested method", "tested a method.")
        data = export_review(updated)
        self.assertEqual(restore_review(data), updated)
        self.assertEqual(json.loads(data)["run"], self.run)
        rows = list(csv.DictReader(io.StringIO(comparison_csv(updated).decode("utf-8-sig"))))
        self.assertEqual(rows[0]["title"], "Identical café title")
        self.assertEqual(rows[0]["decision"], "include")
        self.assertEqual(rows[0]["method_excerpt"], "tested a method.")
        self.assertEqual(rows[0]["run_id"], self.run["manifest"]["run_id"])

    def test_restore_rejects_changed_evidence_unsupported_claims_and_bad_formats(self):
        changes = (
            lambda r: r["run"]["records"][0].update(abstract="Changed abstract"),
            lambda r: r["papers"][self.first]["analysis"]["results"].update(kind="paper-statement", text="Invented", excerpt="99%"),
            lambda r: r["papers"][self.first].update(decision="include", reason=""),
            lambda r: r.update(format_version=2),
            lambda r: r.update(review_id="../unsafe"),
            lambda r: r.update(created_utc="yesterday"),
            lambda r: r["papers"].pop(self.second),
            lambda r: r["papers"][self.first]["analysis"].pop("results"),
        )
        for change in changes:
            saved = copy.deepcopy(self.review)
            change(saved)
            with self.assertRaisesRegex(ValueError, "Invalid review JSON"):
                restore_review(json.dumps(saved).encode())
        for data in (b"private text: not JSON", b"null", b"[]", b'{}', b'\xff'):
            with self.assertRaisesRegex(ValueError, "Invalid review JSON"):
                restore_review(data)
        with self.assertRaises(ValueError):
            restore_review(b" " * (10 * 1024 * 1024 + 1))


if __name__ == "__main__":
    unittest.main()
