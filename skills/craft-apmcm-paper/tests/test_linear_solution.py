"""Check physical feasibility independently of solver labels and sign transforms."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import check_linear_solution as cls

class LinearSolutionTests(unittest.TestCase):
    def setUp(self):
        self.m={'model':{'sense':'max','c':[3,1],'bounds':[[0,2],[0,2]],
                        'A_ub':[[1,1]],'b_ub':[3],'integer_indices':[0,1]},
                'candidate':{'x':[2,1],'reported_objective':7}}

    def test_feasible_value_does_not_prove_optimality(self):
        r=cls.audit(self.m)
        self.assertEqual(r['status'],'pass')
        self.assertTrue(r['linear_feasible'])
        self.assertFalse(r['optimality_verified'])
        self.m['candidate'].update(x=[1,1],reported_objective=4)
        self.assertEqual(cls.audit(self.m)['status'],'pass') # also feasible, not optimal

    def test_solver_optimal_label_cannot_hide_constraint_violation(self):
        self.m['candidate'].update(x=[2,2],reported_objective=8,solver_status='optimal')
        r=cls.audit(self.m)
        self.assertEqual(r['status'],'fail')
        self.assertFalse(r['linear_feasible'])
        self.assertEqual([r['checks'][0]['lhs'],r['checks'][0]['rhs']],[4,3])

    def test_original_max_objective_not_negated_solver_value(self):
        self.m['candidate']['reported_objective']=-7
        r=cls.audit(self.m)
        self.assertTrue(r['linear_feasible'])
        self.assertEqual(r['status'],'fail')
        self.assertEqual(r['checks'][-1]['id'],'objective')

    def test_integrality_never_uses_relative_tolerance(self):
        self.m={'model':{'sense':'min','c':[1],'bounds':[[None,None]],'integer_indices':[0]},
                'candidate':{'x':[1e9+.25],'reported_objective':1e9+.25},
                'tolerances':{'relative':.01}}
        r=cls.audit(self.m)
        self.assertFalse(r['linear_feasible'])
        self.assertEqual(r['checks'][0]['tolerance'],1e-7)

    def test_free_negative_variable_and_equality(self):
        self.m={'model':{'sense':'min','c':[1],'offset':3,'bounds':[[None,None]],
                         'A_eq':[[2]],'b_eq':[-4]},
                'candidate':{'x':[-2],'reported_objective':1}}
        self.assertEqual(cls.audit(self.m)['status'],'pass')
        self.m['model']['bounds']=[[0,None]]
        self.assertFalse(cls.audit(self.m)['linear_feasible'])

    def test_malformed_numeric_inputs_fail(self):
        mutations=[('bad-shape',lambda m:m['model'].update(A_ub=[[1]])),
                   ('missing-bounds',lambda m:m['model'].pop('bounds')),
                   ('nan',lambda m:m['candidate'].update(x=[float('nan'),1])),
                   ('bool',lambda m:m['candidate'].update(x=[True,1])),
                   ('negative-tolerance',lambda m:m.update(tolerances={'integer':-1})),
                   ('vacuous-integer-tolerance',lambda m:m.update(tolerances={'integer':.5})),
                   ('duplicate-index',lambda m:m['model'].update(integer_indices=[0,0])),
                   ('missing-rhs',lambda m:m['model'].pop('b_ub')),
                   ('missing-objective',lambda m:m['candidate'].pop('reported_objective'))]
        for name,mutate in mutations:
            m=copy.deepcopy(self.m);mutate(m)
            self.assertEqual(cls.audit(m)['status'],'fail',name)

    def test_overflow_rejected(self):
        self.m['model'].update(c=[1e308,1e308],A_ub=[[1e308,1e308]])
        self.assertEqual(cls.audit(self.m)['status'],'fail')

    def test_cli_reports_failed_candidate(self):
        self.m['candidate'].update(x=[2,2],reported_objective=8)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'case.json';p.write_text(json.dumps(self.m))
            r=subprocess.run([sys.executable,str(Path(cls.__file__)),'--input',str(p)],capture_output=True,text=True)
            self.assertEqual(r.returncode,1)
            self.assertNotIn('Traceback',r.stderr)
            self.assertEqual(json.loads(r.stdout)['status'],'fail')

if __name__=='__main__':unittest.main()
