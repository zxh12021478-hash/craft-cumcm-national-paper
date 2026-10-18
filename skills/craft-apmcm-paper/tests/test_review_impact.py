import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import context_cache as cc


class ReviewImpactTests(unittest.TestCase):
    def fixture(self, root):
        for name in ('data.csv', 'model.py', 'figure.svg', 'summary.md', 'other.json', 'brief.md', 'extra.txt'):
            (root / name).write_text('baseline ' + name)
        mapping = {'version': 1, 'items': [
            {'id': 'result', 'files': ['data.csv', 'model.py']},
            {'id': 'figure', 'files': ['figure.svg'], 'depends_on': ['result']},
            {'id': 'summary', 'files': ['summary.md'], 'depends_on': ['result']},
            {'id': 'independent', 'files': ['other.json']}], 'open_items': []}
        (root / 'impact.json').write_text(json.dumps(mapping))
        return cc.snapshot(root, ['data.csv'], 'brief.md', impact='impact.json')

    def test_upstream_change_reaches_figure_and_summary_only(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d); record = self.fixture(p)
            (p / 'model.py').write_text('new code')
            plan = cc.check(p, record)['review_plan']
            self.assertEqual(plan['review_items'], ['result', 'figure', 'summary'])
            self.assertEqual(plan['unaffected_items'], ['independent'])
            self.assertFalse(plan['requires_full_review'])

    def test_presentation_edit_does_not_force_independent_recalculation(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d); record = self.fixture(p)
            (p / 'summary.md').write_text('revised English')
            self.assertEqual(cc.check(p, record)['review_plan']['review_items'], ['summary'])

    def test_open_issue_remains_visible_when_every_file_is_unchanged(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d); self.fixture(p)
            data = json.loads((p / 'impact.json').read_text()); data['open_items'] = ['independent']
            (p / 'impact.json').write_text(json.dumps(data))
            record = cc.snapshot(p, ['data.csv'], 'brief.md', impact='impact.json')
            result = cc.check(p, record)
            self.assertEqual(result['status'], 'fresh')
            self.assertEqual(result['review_plan']['review_items'], ['independent'])
            self.assertNotIn('independent', result['review_plan']['unaffected_items'])

    def test_semantic_change_invalidates_even_unchanged_files_and_hides_facts(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d); record = self.fixture(p)
            result = cc.check(p, record, True, True)
            self.assertEqual(result['status'], 'stale'); self.assertNotIn('facts', result)
            self.assertTrue(result['review_plan']['requires_full_review'])
            self.assertEqual(len(result['review_plan']['review_items']), 4)

    def test_changed_map_or_brief_or_unmapped_input_requires_full_review(self):
        for target in ('impact.json', 'brief.md', 'extra.txt'):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as d:
                p = Path(d); self.fixture(p)
                record = cc.snapshot(p, ['data.csv', 'extra.txt'], 'brief.md', impact='impact.json')
                (p / target).write_text('changed')
                plan = cc.check(p, record)['review_plan']
                self.assertTrue(plan['requires_full_review']); self.assertEqual(len(plan['review_items']), 4)

    def test_missing_input_invalidates_its_dependents(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d); record = self.fixture(p); (p / 'data.csv').unlink()
            self.assertEqual(cc.check(p, record)['review_plan']['review_items'], ['result', 'figure', 'summary'])

    def test_invalid_graphs_fail_closed(self):
        good = {'version': 1, 'items': [{'id': 'a', 'files': ['a.txt']}]}
        bad = [None, {}, {'version': 1, 'items': []},
               {'version': 1, 'items': [{'id': 'a', 'files': ['../a']}]},
               {'version': 1, 'items': [{'id': 'a', 'files': ['/a']}]},
               {'version': 1, 'items': [{'id': 'a'}]},
               {'version': 1, 'items': [{'id': 'a', 'depends_on': ['missing']}]},
               {'version': 1, 'items': [{'id': 'a', 'depends_on': ['b']}, {'id': 'b', 'depends_on': ['a']}]},
               {'version': 1, 'items': [{'id': 'a', 'files': ['a']}, {'id': 'a', 'files': ['b']}]},
               dict(good, open_items=['unknown']), dict(good, open_items=[True])]
        for item in bad:
            with self.subTest(item=item), self.assertRaises(ValueError): cc.impact_map(item)

    def test_unbound_graph_records_are_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d); record = self.fixture(p)
            for removed in ('impact.json', 'model.py'):
                altered = copy.deepcopy(record)
                altered['files'] = [x for x in altered['files'] if x['path'] != removed]
                with self.assertRaises(ValueError): cc.check(p, altered)

    def test_symlink_to_outside_is_rejected_at_snapshot(self):
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as outside:
            p = Path(d); self.fixture(p); f = Path(outside) / 'secret'; f.write_text('outside')
            (p / 'model.py').unlink(); (p / 'model.py').symlink_to(f)
            with self.assertRaises(ValueError): cc.snapshot(p, ['data.csv'], 'brief.md', impact='impact.json')

    def test_cli_context_change_and_evidence_overwrite_guard(self):
        script = Path(cc.__file__)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d); self.fixture(p)
            base = [sys.executable, str(script), 'snapshot', '--root', d, '--file', 'data.csv',
                    '--facts', 'brief.md', '--impact-map', 'impact.json', '--output']
            self.assertEqual(subprocess.run(base + [str(p / 'cache.json')], capture_output=True).returncode, 0)
            run = subprocess.run([sys.executable, str(script), 'check', '--root', d, '--manifest', str(p / 'cache.json'),
                                  '--context-changed', '--show-facts'], capture_output=True, text=True)
            self.assertEqual(run.returncode, 1); self.assertNotIn('facts', json.loads(run.stdout))
            original = (p / 'impact.json').read_bytes()
            self.assertEqual(subprocess.run(base + [str(p / 'impact.json')], capture_output=True).returncode, 2)
            self.assertEqual((p / 'impact.json').read_bytes(), original)


if __name__ == '__main__': unittest.main()
