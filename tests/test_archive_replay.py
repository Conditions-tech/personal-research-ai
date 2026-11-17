"""Offline compatibility audit must not rewrite evidence or mask tampering."""

import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from replay_analysis_archive import audit,find_drafts,replay_draft


class ArchiveReplayTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch('requests.sessions.Session.request',side_effect=AssertionError('HTTP blocked')))
        self.enterContext(patch('sqlite3.connect',side_effect=AssertionError('SQLite blocked')))
        self.path=Path(__file__).parent/'fixtures/review_ai_v1_v2_v3_synthetic.json'

    def test_frozen_legacy_requests_claims_decisions_and_bytes_remain_unchanged(self):
        before=self.path.read_bytes();result=audit([self.path])
        self.assertEqual(result['drafts_replayed'],3)
        self.assertEqual([r['format_version'] for r in result['archives'][0]['drafts']],[1,2,3])
        self.assertEqual(self.path.read_bytes(),before)

    def test_tampered_requests_and_claims_are_rejected_without_mutating_input(self):
        review=json.loads(self.path.read_bytes());draft=list(find_drafts(review))[0]
        for change in [lambda d:d['generation']['request'].update(system='changed'),lambda d:d['fields']['method'].update(text='changed')]:
            bad=copy.deepcopy(draft);change(bad);before=copy.deepcopy(bad)
            with self.assertRaises(ValueError):replay_draft(bad,review)
            self.assertEqual(bad,before)

    def test_raw_context_audit_does_not_claim_to_restore_missing_history(self):
        drafts=list(find_drafts(json.loads(self.path.read_bytes())))
        self.assertEqual(replay_draft(drafts[0])['validation_level'],'unreplayed-no-complete-review')
        self.assertEqual(replay_draft(drafts[-1])['validation_level'],'context-protocol-only')
        bad=copy.deepcopy(drafts[-1]);bad['generation']['request']['system']='changed'
        with self.assertRaises(ValueError):replay_draft(bad)


if __name__=='__main__':unittest.main()
