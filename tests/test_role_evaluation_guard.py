"""No live inference: one-role runner I/O isolation and failure preservation."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from role_analysis_evaluation import evaluate
from test_analysis import model_metadata


class FakeMemory:
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def report(self):return {'mocked':True}


class RoleEvaluationGuardTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory(prefix='single-role-tests-');self.addCleanup(temp.cleanup);self.root=Path(temp.name)
        self.ledger=self.root/'budget.json';self.ledger.write_text(json.dumps({'kind':'c2-coverage-budget-v1','cap':12,'used':0,'entries':[]}))
        self.case={'id':'synthetic','kind':'synthetic','title':'Synthetic','authors':'Synthetic','year':None,'doi':'','source_url':'','license':'Synthetic fixture','capture_date':'2026-10-21','abstract':'Here a model is developed. Results are uncertain.'}
        self.manifest=self.root/'manifest.json';self.manifest.write_text(json.dumps({'partition':'development','cases':[self.case]}))
        self.enterContext(patch('requests.sessions.Session.request',side_effect=AssertionError('HTTP blocked')))
        self.enterContext(patch('sqlite3.connect',side_effect=AssertionError('SQLite blocked')))

    def test_low_memory_refuses_before_backend_or_budget_use(self):
        output=self.root/'low.json'
        with patch('local_analysis_benchmark.wait_for_memory_gate',return_value=1),patch('review.local_backend.OllamaLocal.inspect') as inspect:
            evaluate(self.manifest,self.ledger,output)
        inspect.assert_not_called();self.assertEqual(json.loads(output.read_text())['state'],'blocked')
        self.assertEqual(json.loads(self.ledger.read_text())['used'],0)

    def test_backend_failure_is_retained_before_any_generation(self):
        output=self.root/'backend.json'
        with patch('local_analysis_benchmark.wait_for_memory_gate',return_value=5*1024**3),patch('review.local_backend.OllamaLocal.inspect',side_effect=ValueError('Local failure')):
            evaluate(self.manifest,self.ledger,output)
        self.assertEqual(json.loads(output.read_text())['blocker']['reason'],'Local failure')
        self.assertEqual(json.loads(self.ledger.read_text())['used'],0)

    def test_six_mock_requests_are_independent_and_error_does_not_destroy_source(self):
        output=self.root/'six.json';requests=[]
        def generate(request):
            requests.append(request);data=json.loads(request['prompt'].split('\n',1)[1])
            if data['role']=='dataset':raise ValueError('Simulated generation failure')
            value={k:data[k] for k in ('run_id','record_key','evidence_sha256','role')};value['quote']=''
            return {**model_metadata(),'response':json.dumps(value)}
        with patch('local_analysis_benchmark.wait_for_memory_gate',return_value=5*1024**3),patch('local_analysis_benchmark.MemoryMonitor',FakeMemory),patch('review.local_backend.OllamaLocal.inspect',return_value=model_metadata()),patch('review.local_backend.OllamaLocal.generate',side_effect=generate):
            evaluate(self.manifest,self.ledger,output)
        saved=json.loads(output.read_text());item=saved['cases'][0]
        self.assertEqual(len(requests),6);self.assertEqual(len(item['roles']),6)
        self.assertEqual(item['roles']['dataset']['error'],'Simulated generation failure')
        self.assertNotIn('field',item['roles']['dataset'])
        self.assertTrue(item['original_review_unchanged']);self.assertTrue(item['original_review_roundtrip'])
        self.assertEqual(item['review_snapshot']['run']['manifest']['provenance'][0]['captured_date'],'2026-10-21')
        for request in requests:
            data=json.loads(request['prompt'].split('\n',1)[1]);self.assertNotIn('expected',data)
            self.assertNotIn('previous_response',data);self.assertEqual(' '.join(data['source_sentences']),self.case['abstract'])

    def test_cli_requires_opt_in_and_preserves_existing_report(self):
        tool=Path(__file__).resolve().parents[1]/'tools/role_analysis_evaluation.py'
        result=subprocess.run([sys.executable,'-B',str(tool)],capture_output=True,text=True,timeout=30)
        self.assertEqual(result.returncode,2);self.assertIn('--live-local',result.stderr)
        existing=self.root/'existing.json';existing.write_text('preserve')
        result=subprocess.run([sys.executable,'-B',str(tool),'--live-local','--report',str(existing)],capture_output=True,text=True,timeout=30)
        self.assertEqual(result.returncode,2);self.assertEqual(existing.read_text(),'preserve')


if __name__=='__main__':unittest.main()
