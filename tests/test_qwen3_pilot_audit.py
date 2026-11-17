"""Synthetic Qwen3 counters and snapshot/response binding, without inference."""

import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from coverage_evaluation import make_review
import qwen3_pilot as pilot
from qwen3_pilot_audit import audit
from review.analysis import evidence_context
from review.quote_analysis_v5 import validate
from review.workspace import SUMMARY_FIELDS


class Qwen3AuditTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch("requests.sessions.Session.request",side_effect=AssertionError("HTTP blocked")))
        self.enterContext(patch("sqlite3.connect",side_effect=AssertionError("SQLite blocked")))
        first="Here an estimator is fitted.";second="Three records were analyzed."
        gold={f:[] for f in SUMMARY_FIELDS};gold.update(objective=[first],method=[first],dataset=[second])
        self.case={"id":"synthetic","kind":"synthetic","title":"Synthetic","authors":"Synthetic","year":None,"doi":"","source_url":"","license":"Synthetic","abstract":first+" "+second,"expected":gold}
        self.manifest=json.dumps({"partition":"test","cases":[self.case]}).encode()
        review=make_review([self.case],"test");key=next(iter(review["papers"]));ctx=evidence_context(review,key)
        value={**{k:ctx[k] for k in ("run_id","record_key","evidence_sha256")},"fields":{"objective":first,"method":second,"dataset":"","results":"","limitations":second,"conclusion":""}}
        raw=json.dumps(value)
        generation={"model":pilot.MODEL,"model_digest":pilot.DIGEST,"runtime_version":pilot.RUNTIME,"response":raw,
                    "wire_response":{"model":pilot.MODEL,"response":raw,"done":True,"done_reason":"stop"}}
        self.item={"case":self.case,"status":"validated-experimental-fields","context":ctx,"original_review":review,"request":pilot.build(ctx),"generation":generation,"fields":validate(ctx,value)}
        self.report={"protocol":pilot.VERSION,"manifest_sha256":hashlib.sha256(self.manifest).hexdigest(),"cases":[self.item]}
        self.alt={"acceptable_alternate_quotes":{"synthetic":{"method":[second]}}}

    def test_support_alternatives_omission_false_fill_and_missing_are_distinct(self):
        c=audit(self.manifest,self.report,self.alt)["counts"]
        self.assertEqual(c["strict_gold_support"],1);self.assertEqual(c["predeclared_alternative"],1)
        self.assertEqual(c["supported_selected_fields"],2);self.assertEqual(c["expected_supported_fields_all_cases"],3)
        self.assertEqual(c["omission"],1);self.assertEqual(c["false_fill"],1);self.assertEqual(c["correct_missing"],2)
        self.assertEqual(c["literal_source_quotes"],3)

    def test_failed_and_unattempted_cases_do_not_count_as_correct_missing(self):
        for cases,name in [([],"unattempted_cases"),([dict(self.item,fields=None)],"failed_or_refused_cases")]:
            report=copy.deepcopy(self.report);report["cases"]=cases
            if cases:del report["cases"][0]["fields"]
            c=audit(self.manifest,report,self.alt)["counts"]
            self.assertEqual(c[name],1);self.assertEqual(c["correct_missing"],0)

    def test_changed_paper_request_fields_raw_response_and_model_are_rejected(self):
        for change in [lambda r:r.update(manifest_sha256="wrong"),lambda r:r["cases"][0]["context"]["record"].update(abstract="Wrong evidence"),
                       lambda r:r["cases"][0]["request"].update(think=True),lambda r:r["cases"][0]["fields"]["results"].update(text="unsupported"),
                       lambda r:r["cases"][0]["generation"].update(model_digest="wrong"),lambda r:r["cases"][0]["generation"]["wire_response"].update(response="changed")]:
            report=copy.deepcopy(self.report);change(report)
            with self.assertRaises(ValueError):audit(self.manifest,report,self.alt)


if __name__=="__main__":unittest.main()
