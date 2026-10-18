"""Independent AI forward tests; synthetic records are never real review approvals."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import audit_bundle as ab
import package_bundle as pb


class IndependentNegativeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        content = {'paper.md': 'The cost is 32 USD.', 'results.json': '{"cost":32}',
                   'review.md': 'SYNTHETIC TEST RECORD ONLY; no real scientific audit.'}
        for name, text in content.items():
            (self.root / name).write_text(text)
        self.m = {'event': 'APMCM', 'event_year': 2024, 'mode': 'historical-rehearsal',
                  'paper': 'paper.md', 'results': 'results.json',
                  'files': [{'path': n, 'sha256': ab.digest((self.root/n).read_bytes())} for n in content],
                  'claims': [{'id': 'cost', 'quote': content['paper.md'], 'token': '32', 'pointer': '/cost', 'unit': 'USD'}],
                  'required_outputs': [{'id': 'Q1', 'status': 'verified', 'review_note': 'Synthetic fixture', 'evidence': ['results.json']}],
                  'reviews': {n: {'status': 'pass', 'reviewer': 'SYNTHETIC TEST', 'evidence': 'review.md'} for n in ('semantic', 'figures', 'coverage', 'reproduction')}}

    def test_sentence_punctuation_and_negative_sign(self):
        # Normal sentence punctuation must not be mistaken for a decimal suffix.
        (self.root/'paper.md').write_text('The cost is 32.')
        self.m['files'][0]['sha256'] = ab.digest((self.root/'paper.md').read_bytes())
        self.m['claims'][0].update(quote='The cost is 32.', token='32')
        self.assertEqual(ab.audit(self.root,self.m)['status'],'pass')
        # The unsigned token must not silently match the digits of a negative number.
        (self.root/'paper.md').write_text('The cost is -32.')
        self.m['files'][0]['sha256'] = ab.digest((self.root/'paper.md').read_bytes())
        self.m['claims'][0]['quote'] = 'The cost is -32.'
        self.assertEqual(ab.audit(self.root,self.m)['status'],'fail')

    def test_numeric_disagreement(self):
        (self.root/'results.json').write_text('{"cost":33}')
        self.m['files'][1]['sha256'] = ab.digest((self.root/'results.json').read_bytes())
        r = ab.audit(self.root, self.m)
        self.assertIn('CLAIM', [e['code'] for e in r['errors']])

    def test_paper_only_cannot_claim_reproduction(self):
        self.m.pop('results')
        self.m['reviews'].pop('reproduction')
        r = ab.audit(self.root, self.m)
        self.assertEqual(r['status'], 'fail')
        self.assertTrue({'INPUT', 'REVIEW'} <= {e['code'] for e in r['errors']})

    def test_historical_rules_cannot_clear_current_year(self):
        self.m.update(event_year=2026, mode='live-contest')
        rules = {'event': 'APMCM', 'event_year': 2024, 'rules': {}}
        r = ab.audit(self.root, self.m, rules, final=True)
        self.assertIn('RULE_EVENT', [e['code'] for e in r['errors']])

    def test_shipped_current_rules_fail_closed(self):
        self.m.update(event_year=2026, mode='live-contest')
        rules = json.loads((SCRIPTS.parent/'assets/rules-2026.json').read_text())
        r = ab.audit(self.root, self.m, rules, final=True)
        self.assertEqual(r['status'], 'fail')
        self.assertTrue(any(e['code']=='RULE_UNRESOLVED' and e['detail']=='ai_policy' for e in r['errors']))

    def test_traversal_and_external_symlink(self):
        for name in ('../outside', '/tmp/outside'):
            m = copy.deepcopy(self.m)
            m['files'].append({'path': name, 'sha256': '0'*64})
            self.assertEqual(ab.audit(self.root,m)['status'], 'fail')
        with tempfile.TemporaryDirectory() as outside:
            dest = Path(outside)/'secret'
            dest.write_text('outside')
            (self.root/'link').symlink_to(dest)
            m = copy.deepcopy(self.m)
            m['files'].append({'path':'link', 'sha256':ab.digest(dest.read_bytes())})
            self.assertEqual(ab.audit(self.root,m)['status'], 'fail')

    def test_source_edit_between_audit_and_archive(self):
        real_audit = pb.audit
        def change_after_check(*args, **kwargs):
            report = real_audit(*args, **kwargs)
            (self.root/'paper.md').write_text('Changed after audit')
            return report
        with mock.patch.object(pb,'audit',side_effect=change_after_check):
            with self.assertRaises(ValueError):
                pb.package(self.root,self.m,self.root/'output.zip')
        self.assertFalse((self.root/'output.zip').exists())

    def test_missing_team_approval_cannot_package_final(self):
        self.m.update(event_year=2026, mode='live-contest')
        rules = {'event':'APMCM','event_year':2026,'rules':{n:{'status':'verified','value':'TEST ONLY','event_year':2026,'source_url':'https://www.apmcm.org/test-only'} for n in ab.REQUIRED_RULES}}
        self.m['rule_checks'] = {n:{'status':'pass','reviewer':'SYNTHETIC TEST','evidence':'review.md'} for n in ab.REQUIRED_RULES}
        self.m['rules_sha256'] = ab.rules_hash(rules)
        with self.assertRaisesRegex(ValueError, 'approval'):
            pb.package(self.root,self.m,self.root/'final.zip',rules,True)
        self.assertFalse((self.root/'final.zip').exists())

    def test_rule_change_invalidates_approval_and_archive_keeps_rules(self):
        import zipfile
        self.m.update(event_year=2026, mode='live-contest')
        rules = {'event':'APMCM','event_year':2026,'rules':{n:{'status':'verified','value':'TEST ONLY','event_year':2026,'source_url':'https://www.apmcm.org/test-only'} for n in ab.REQUIRED_RULES}}
        self.m['rule_checks'] = {n:{'status':'pass','reviewer':'SYNTHETIC TEST','evidence':'review.md'} for n in ab.REQUIRED_RULES}
        self.m['rules_sha256'] = ab.rules_hash(rules)
        self.m['team_approval'] = {'approved':True,'name':'SYNTHETIC TEST ONLY','timestamp':'2026-10-17T00:00:00+08:00','manifest_sha256':ab.approval_hash(self.m)}
        pb.package(self.root,self.m,self.root/'good.zip',rules,True)
        with zipfile.ZipFile(self.root/'good.zip') as z:
            self.assertEqual(json.loads(z.read('RULES.json')), rules)
        rules['rules']['page_limit']['value'] = 'Changed after approval'
        with self.assertRaisesRegex(ValueError, 'RULE_HASH'):
            pb.package(self.root,self.m,self.root/'changed.zip',rules,True)
        self.m['rules_sha256'] = ab.rules_hash(rules)
        with self.assertRaisesRegex(ValueError, 'approval'):
            pb.package(self.root,self.m,self.root/'stale-approval.zip',rules,True)
        self.assertFalse((self.root/'changed.zip').exists())
        self.assertFalse((self.root/'stale-approval.zip').exists())

    def test_malformed_cli_input_fails_without_traceback(self):
        for bad in ([], {'event':'APMCM', 'claims':[None]}, {'event':'APMCM','files':[None]}, {'reviews':None}, {'rule_checks':[]}, {'team_approval':[]} ):
            (self.root/'bad.json').write_text(json.dumps(bad))
            r = subprocess.run([sys.executable,str(SCRIPTS/'audit_bundle.py'),'--root',str(self.root),'--manifest',str(self.root/'bad.json')],capture_output=True,text=True)
            self.assertNotEqual(r.returncode,0)
            self.assertNotIn('Traceback',r.stderr)
            self.assertEqual(json.loads(r.stdout)['status'],'fail')

if __name__ == '__main__':
    unittest.main()
