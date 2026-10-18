"""Availability at the actual origin, not whether a historical value exists now."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import check_information as ci


class InformationTests(unittest.TestCase):
    def setUp(self):
        self.trace={'availability_lags':{'promotion':-2,'tickets':1,'demand':0},
          'forecasts':[{'id':'o80-h2','origin':80,'target':82,
                       'features':[{'name':'promotion','source_time':82,'kind':'observed'}]}]}

    def test_known_two_steps_ahead_but_third_step_is_future_information(self):
        self.assertEqual(ci.audit(self.trace)['status'],'pass')
        self.trace['forecasts'][0].update(id='o80-h3',target=83)
        self.trace['forecasts'][0]['features'][0]['source_time']=83
        r=ci.audit(self.trace)
        self.assertEqual(r['errors'][0]['code'],'FUTURE_INFORMATION')
        self.assertEqual(r['errors'][0]['available_at'],81)

    def test_lagged_feature_may_still_be_unavailable_at_origin(self):
        f=self.trace['forecasts'][0]['features'][0]
        f.update(name='tickets',source_time=79)
        self.assertEqual(ci.audit(self.trace)['status'],'pass')
        f['source_time']=80
        self.assertEqual(ci.audit(self.trace)['status'],'fail')

    def test_assumed_scenario_is_separate_from_observation_and_posthoc_input(self):
        f=self.trace['forecasts'][0]['features'][0]
        f.update(source_time=84,kind='scenario',formed_at=80,note='Assume no promotion; not observed')
        r=ci.audit(self.trace)
        self.assertEqual(r['status'],'pass')
        self.assertEqual(len(r['non_observed_inputs']),1)
        f['formed_at']=81
        self.assertEqual(ci.audit(self.trace)['errors'][0]['code'],'POST_ORIGIN_INPUT')
        f['formed_at']=80
        f.pop('note')
        self.assertEqual(ci.audit(self.trace)['status'],'fail')

    def test_malformed_nonfinite_duplicate_and_undeclared_inputs(self):
        for edit in ('nonfinite','duplicate','undeclared','bad_kind','missing_uses'):
            m=copy.deepcopy(self.trace)
            if edit=='nonfinite':m['forecasts'][0]['origin']=float('nan')
            if edit=='duplicate':m['forecasts']*=2
            if edit=='undeclared':m['forecasts'][0]['features'][0]['name']='unknown'
            if edit=='bad_kind':m['forecasts'][0]['features'][0]['kind']='actual_future'
            if edit=='missing_uses':m['forecasts'][0].pop('features')
            self.assertEqual(ci.audit(m)['status'],'fail',edit)

    def test_cli_rejects_leakage_without_traceback(self):
        self.trace['forecasts'][0]['features'][0]['source_time']=83
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'trace.json';p.write_text(json.dumps(self.trace))
            r=subprocess.run([sys.executable,str(Path(ci.__file__)),'--trace',str(p)],capture_output=True,text=True)
            self.assertEqual(r.returncode,1)
            self.assertEqual(json.loads(r.stdout)['status'],'fail')
            self.assertNotIn('Traceback',r.stderr)

if __name__=='__main__':unittest.main()
