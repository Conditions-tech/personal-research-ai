"""A real oversized manual review must preserve its download and warn on reopen."""

import copy
import json
import unittest

import test_ui
from review.workspace import annotate_paper,create_review,restore_review
from test_review import fixture_run


class ReviewExportLimitTests(unittest.TestCase):
    setUp=test_ui.StreamlitSmokeTests.setUp
    run_app=test_ui.StreamlitSmokeTests.run_app
    download_args=test_ui.StreamlitSmokeTests.download_args

    def test_oversized_valid_review_download_preserves_notes_and_warns_it_cannot_reopen(self):
        limit=10*1024*1024
        review=create_review(fixture_run(),'Synthetic question '+('x'*limit),'Synthetic include','Exclude real research')
        key=next(iter(review['papers']))
        review=annotate_paper(review,key,'method','paper-statement','Original reviewer note','tested a method.')
        before=copy.deepcopy(review);self.app.session_state['review_workspace']=review
        self.run_app()
        data=self.download_args('Download review JSON')['data']
        self.assertGreater(len(data),limit)
        self.assertEqual(json.loads(data),before)
        self.assertEqual(self.app.session_state['review_workspace'],before)
        with self.assertRaisesRegex(ValueError,'at most 10 MiB'):restore_review(data)
        warnings=' '.join(w.value for w in self.app.warning)
        self.assertIn('cannot be reopened',warnings)
        self.http.assert_not_called()


if __name__=='__main__':unittest.main()
