"""Offline quality counters distinguish selection, source copying and coverage."""

import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from analysis_adjudication import FIELDS, adjudicate


class AdjudicationTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch("requests.sessions.Session.request", side_effect=AssertionError("HTTP blocked")))
        self.enterContext(patch("sqlite3.connect", side_effect=AssertionError("SQLite blocked")))
        case = {"id":"one", "kind":"public-abstract", "abstract":"Aim. Background.", "expected_refusal":False,
                "expected":{f:["Aim."] if f=="objective" else [] for f in FIELDS}}
        self.cases = [case, {**copy.deepcopy(case),"id":"refused"}, {**copy.deepcopy(case),"id":"unattempted"}]
        self.manifest = json.dumps({"partition":"tuning", "cases":self.cases}).encode()
        claims = {f:{"text":"Aim." if f=="objective" else "", "excerpt":"Aim." if f=="objective" else ""} for f in FIELDS}
        self.report = {"manifest_sha256":hashlib.sha256(self.manifest).hexdigest(),"protocol":"abstract-quotes-v4","state":"blocked",
                       "cases":[{"case":copy.deepcopy(case),"status":"proposal-pending","draft":{"fields":claims},"wire_response":{}},
                                {"case":copy.deepcopy(self.cases[1]),"status":"refused-or-failed","error":"Local backend unavailable","wire_response":None}]}

    def score(self):return adjudicate(self.manifest,self.report)

    def test_refused_and_unattempted_papers_stay_in_coverage_denominator(self):
        count=self.score()["counts"]
        self.assertEqual(count["expected_nonmissing_fields_all_benign_cases"],3)
        self.assertEqual(count["expected_nonmissing_fields_selected_all_benign_cases"],1)
        self.assertEqual(count["expected-missing"],5)
        self.assertEqual(count["returned_fields"],6)
        self.assertEqual(count["benign_cases_without_proposal"],1)
        self.assertEqual(count["unattempted_cases"],1)
        self.assertEqual(self.score()["cases"][1]["error"],"Local backend unavailable")

    def test_literal_background_can_pass_presence_but_fail_role_agreement(self):
        self.report["cases"][0]["draft"]["fields"]["objective"]={"text":"Background.","excerpt":"Background."}
        count=self.score()["counts"]
        self.assertEqual(count["selected_quotes_exactly_copied_from_original"],1)
        self.assertEqual(count["different-field-quote"],1)
        self.assertEqual(count["expected_nonmissing_fields_selected_all_benign_cases"],0)

    def test_unexpected_fill_omission_and_non_source_text_are_distinct(self):
        fields=self.report["cases"][0]["draft"]["fields"]
        fields["objective"]={"text":"","excerpt":""}
        fields["dataset"]={"text":"Fabricated.","excerpt":"Fabricated."}
        count=self.score()["counts"]
        self.assertEqual(count["omission"],1)
        self.assertEqual(count["unexpected-fill"],1)
        self.assertEqual(count["selected_quotes_exactly_copied_from_original"],0)

    def test_changed_manifest_case_labels_duplicates_and_nonliteral_gold_are_rejected(self):
        for change in [lambda r:r.update(manifest_sha256="wrong"),lambda r:r["cases"][0]["case"].update(abstract="changed"),
                       lambda r:r["cases"].append(copy.deepcopy(r["cases"][0]))]:
            bad=copy.deepcopy(self.report);change(bad)
            with self.subTest(change=change),self.assertRaises(ValueError):adjudicate(self.manifest,bad)
        cases=copy.deepcopy(self.cases);cases[0]["expected"]["objective"]=["Not in source"]
        manifest=json.dumps({"partition":"tuning","cases":cases}).encode()
        bad=copy.deepcopy(self.report);bad["cases"]=[];bad["manifest_sha256"]=hashlib.sha256(manifest).hexdigest()
        with self.assertRaises(ValueError):adjudicate(manifest,bad)


if __name__ == "__main__":unittest.main()
