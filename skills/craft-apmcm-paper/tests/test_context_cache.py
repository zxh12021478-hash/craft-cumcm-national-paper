import importlib.util
from pathlib import Path
import sys,tempfile,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import context_cache as cc

class ContextCacheTests(unittest.TestCase):
    def test_changed_input_or_brief_cannot_reuse_facts(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'input').write_text('A');(p/'brief').write_text('Reviewed A')
            r=cc.snapshot(p,['input'],'brief')
            self.assertEqual(cc.check(p,r,True)['facts'],'Reviewed A')
            (p/'input').write_text('B');self.assertNotIn('facts',cc.check(p,r,True))
            (p/'input').write_text('A');(p/'brief').write_text('Unreviewed edit')
            self.assertEqual(cc.check(p,r,True)['status'],'stale')
    def test_missing_input_and_outside_path_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'input').write_text('A');(p/'brief').write_text('A')
            r=cc.snapshot(p,['input'],'brief');(p/'input').unlink()
            self.assertEqual(cc.check(p,r)['status'],'stale')
            with self.assertRaises(ValueError):cc.snapshot(p,['../outside'],'brief')
    def test_unbound_brief_is_not_exposed(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'input').write_text('A');(p/'brief').write_text('A')
            r=cc.snapshot(p,['input'],'brief');r['files']=r['files'][:1]
            with self.assertRaises(ValueError):cc.check(p,r,True)

if __name__=='__main__':unittest.main()
