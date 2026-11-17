"""Frozen single-role support counters and tamper detection without inference."""

import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from coverage_evaluation import make_review
from role_adjudication import adjudicate
from review.analysis import OPTIONS,evidence_context
from review.role_analysis_v6 import VERSION,build,validate
from review.workspace import SUMMARY_FIELDS


class RoleAdjudicationTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch('requests.sessions.Session.request',side_effect=AssertionError('HTTP blocked')))
        self.enterContext(patch('sqlite3.connect',side_effect=AssertionError('SQLite blocked')))
        first='Here an estimator is fitted.';second='Three records were analyzed.'
        gold={f:[] for f in SUMMARY_FIELDS};gold.update(objective=[first],method=[first],dataset=[second])
        alt={f:[] for f in SUMMARY_FIELDS};alt['method']=[second]
        self.case={'id':'synthetic','kind':'synthetic','title':'Synthetic','authors':'Synthetic','year':None,'doi':'','source_url':'','license':'Synthetic fixture','abstract':first+' '+second,'expected':gold,'acceptable_alternate_quotes':alt}
        self.manifest=json.dumps({'partition':'development','cases':[self.case]}).encode()
        review=make_review([self.case],'development');key=next(iter(review['papers']));ctx=evidence_context(review,key)
        item={'case':copy.deepcopy(self.case),'review_snapshot':review,'context':ctx,'roles':{}}
        quotes={'objective':first,'method':second,'dataset':'','results':'','limitations':second,'conclusion':''}
        for role,q in quotes.items():
            value={**{k:ctx[k] for k in ('run_id','record_key','evidence_sha256')},'role':role,'quote':q};raw=json.dumps(value)
            item['roles'][role]={'request':build(ctx,role,OPTIONS),'generation':{'response':raw},'field':validate(ctx,role,raw)}
        item['roles']['results']={'error':'Simulated backend failure'}
        self.report={'protocol':VERSION,'manifest_sha256':hashlib.sha256(self.manifest).hexdigest(),'cases':[item]}

    def test_support_alternates_missing_false_fills_and_failures_are_separate(self):
        c=adjudicate(self.manifest,self.report)['counts']
        self.assertEqual(c['strict_gold_support'],1);self.assertEqual(c['predeclared_valid_alternative'],1)
        self.assertEqual(c['supported_selections'],2);self.assertEqual(c['expected_supported_roles'],3)
        self.assertEqual(c['omission'],1);self.assertEqual(c['fill_against_declared_missingness'],1)
        self.assertEqual(c['failed_roles'],1);self.assertEqual(c['correct_missing'],1)
        self.assertEqual(c['literal_original_quotes'],3)

    def test_unattempted_role_never_counts_as_correct_missing(self):
        del self.report['cases'][0]['roles']['conclusion']
        c=adjudicate(self.manifest,self.report)['counts']
        self.assertEqual(c['unattempted_roles'],1);self.assertEqual(c['correct_missing'],0)

    def test_changed_manifest_context_field_request_and_role_are_rejected(self):
        for change in [lambda r:r.update(manifest_sha256='wrong'),
                       lambda r:r['cases'][0]['context']['record'].update(abstract='wrong evidence'),
                       lambda r:r['cases'][0]['roles']['objective']['field'].update(text='changed'),
                       lambda r:r['cases'][0]['roles']['objective']['request'].update(system='changed'),
                       lambda r:r['cases'][0]['roles'].update(unknown={})]:
            r=copy.deepcopy(self.report);change(r)
            with self.subTest(change=change),self.assertRaises(ValueError):adjudicate(self.manifest,r)


if __name__=='__main__':unittest.main()
