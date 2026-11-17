"""Reproduced review-import ambiguity and lost action-timestamp defects."""

import copy
import json
import unittest
from unittest.mock import patch

from review.workspace import annotate_paper,create_review,export_review,restore_review,screen_paper
from test_review import fixture_run


class ReviewImportIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch('requests.sessions.Session.request',side_effect=AssertionError('HTTP blocked')))
        self.enterContext(patch('sqlite3.connect',side_effect=AssertionError('SQLite blocked')))
        self.review=create_review(fixture_run(),'Synthetic question','Synthetic include','Exclude real research')
        self.key=next(iter(self.review['papers']))

    def test_duplicate_note_keys_refuse_instead_of_silently_replacing_review_work(self):
        review=annotate_paper(self.review,self.key,'method','paper-statement','Original reviewer note','tested a method.')
        before=copy.deepcopy(review);raw=export_review(review).decode()
        needle='"text": "Original reviewer note"';self.assertEqual(raw.count(needle),1)
        ambiguous=raw.replace(needle,needle+', "text": "Replacement private note"')
        with self.assertRaisesRegex(ValueError,'Invalid review JSON') as caught:restore_review(ambiguous.encode())
        self.assertNotIn('Replacement private note',str(caught.exception))
        self.assertEqual(review,before)

    def test_duplicate_top_level_keys_and_nonfinite_json_are_refused(self):
        raw=export_review(self.review).decode()
        for malformed in [raw.replace('"format_version": 1','"format_version": 1, "format_version": 1',1),
                          raw[:-1]+', "unexpected": NaN}',raw[:-1]+', "unexpected": Infinity}']:
            with self.subTest(case=malformed[-35:]),self.assertRaisesRegex(ValueError,'Invalid review JSON'):restore_review(malformed.encode())

    def test_required_root_screening_and_authored_note_timestamps_cannot_be_missing(self):
        screened=screen_paper(self.review,self.key,'include','Synthetic relevance')
        annotated=annotate_paper(self.review,self.key,'method','interpretation','Synthetic interpretation','tested a method.')
        cases=[]
        for name in ('created_utc','updated_utc'):
            bad=copy.deepcopy(self.review);bad[name]=None;cases.append(bad)
        bad=copy.deepcopy(screened);bad['papers'][self.key]['screened_utc']=None;cases.append(bad)
        bad=copy.deepcopy(annotated);bad['papers'][self.key]['analysis']['method']['updated_utc']=None;cases.append(bad)
        for bad in cases:
            with self.subTest(root_created=bad['created_utc']),self.assertRaisesRegex(ValueError,'Invalid review JSON'):restore_review(json.dumps(bad).encode())

    def test_untouched_pending_and_missing_timestamps_remain_reopenable(self):
        self.assertEqual(restore_review(export_review(self.review)),self.review)
        paper=self.review['papers'][self.key]
        self.assertIsNone(paper['screened_utc']);self.assertIsNone(paper['analysis']['method']['updated_utc'])

    def test_normally_authored_screening_notes_and_cleared_notes_roundtrip(self):
        review=screen_paper(self.review,self.key,'include','Synthetic relevance')
        review=annotate_paper(review,self.key,'method','interpretation','Synthetic interpretation','tested a method.')
        self.assertEqual(restore_review(export_review(review)),review)
        review=annotate_paper(review,self.key,'method','missing')
        self.assertIsNotNone(review['papers'][self.key]['analysis']['method']['updated_utc'])
        self.assertEqual(restore_review(export_review(review)),review)


if __name__=='__main__':unittest.main()
