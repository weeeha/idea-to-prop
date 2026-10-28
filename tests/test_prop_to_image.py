import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from PIL import Image


CLI = Path(__file__).resolve().parents[1] / 'skills/prop-to-image/scripts/prop_to_image.py'


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = self.root / 'asset with spaces'
        self.source = self.root / 'original photo.png'
        Image.new('RGB', (32, 24), '#496875').save(self.source)
        self.output = self.root / 'output.png'
        Image.new('RGB', (32, 24), '#946338').save(self.output)
        self.brief = self.root / 'brief.json'
        self.brief.write_text(json.dumps({'fixed_features': ['Keep the handle opening'],
                                         'allowed_changes': ['Color and finish'],
                                         'unknowns': ['Reverse side', 'physical size']}))

    def run_cli(self, command, *args, ok=True):
        p = subprocess.run([sys.executable, str(CLI), command, str(self.project),
                            *map(str, args)], capture_output=True, text=True)
        if ok:
            self.assertEqual(p.returncode, 0, p.stderr)
            return json.loads(p.stdout)
        self.assertNotEqual(p.returncode, 0, p.stdout)
        self.assertNotIn('Traceback', p.stderr)
        return p.stderr

    def init(self, title='Wood study'):
        return self.run_cli('init', '--source', self.source, '--brief', self.brief,
                            '--asset-id', 'FILM-PROP-42', '--title', title,
                            '--mode', 'finish-only')

    def candidate(self):
        job = self.run_cli('prepare', '--title', 'Walnut', '--direction', 'Walnut and steel')
        return self.run_cli('complete', '--job', job['job_id'], '--image', self.output,
                            '--provider', 'built-in-imagegen')

    def record(self):
        return json.loads((self.project / 'project.json').read_text())

    def test_full_lifecycle_preserves_input_and_explicit_selection(self):
        original = self.source.read_bytes()
        self.init()
        self.source.unlink()
        job = self.run_cli('prepare', '--title', 'Walnut', '--direction', 'Warm wood')
        request = json.loads(Path(job['request_path']).read_text())
        args = request['arguments']
        self.assertIn('Keep the handle opening', args['prompt'])
        self.assertEqual(Path(args['referenced_image_paths'][0]).read_bytes(), original)
        self.assertEqual(args['transparent_background'], False)
        result = self.run_cli('complete', '--job', job['job_id'], '--image', self.output,
                              '--provider', 'built-in-imagegen')
        self.assertIsNone(self.record()['selection'])
        self.run_cli('select', '--candidate', result['candidate_id'], '--by', 'Designer')
        export = self.run_cli('handoff')
        handoff = json.loads(Path(export['handoff_path']).read_text())
        self.assertEqual(handoff['selection_status'], 'selected')
        self.assertIsNone(handoff['geometry']['dimensions'])
        self.assertFalse(handoff['model_created'])
        self.assertIsNone(handoff['source_revision_id'])
        self.assertEqual(handoff['linkage_status'], 'unlinked-tool-handoff')
        selected_file = Path(export['handoff_path']).parent / handoff['image']['path']
        self.assertEqual(selected_file.read_bytes(), self.output.read_bytes())
        self.assertEqual(handoff['image']['sha256'], hashlib.sha256(self.output.read_bytes()).hexdigest())
        self.assertEqual(handoff['source_candidate_id'], result['candidate_id'])

    def test_unselected_handoff_requires_explicit_provisional_reason(self):
        self.init()
        c = self.candidate()['candidate_id']
        self.assertIn('select', self.run_cli('handoff', ok=False).lower())
        self.run_cli('handoff', '--candidate', c, ok=False)
        out = self.run_cli('handoff', '--candidate', c, '--provisional-reason', 'Shape study only')
        data = json.loads(Path(out['handoff_path']).read_text())
        self.assertEqual(data['selection_status'], 'provisional')
        self.assertEqual(data['provisional_reason'], 'Shape study only')
        self.assertIsNone(self.record()['selection'])

    def test_source_tamper_stops_generation_request(self):
        self.init()
        source = self.project / self.record()['source']['path']
        source.write_bytes(self.output.read_bytes())
        self.assertIn('checksum', self.run_cli('prepare', '--title', 'x', '--direction', 'x', ok=False).lower())
        self.assertEqual(self.record()['jobs'], [])

    def test_output_tamper_stops_handoff(self):
        self.init()
        c = self.candidate()['candidate_id']
        self.run_cli('select', '--candidate', c, '--by', 'Designer')
        path = self.project / self.record()['candidates'][0]['image']['path']
        path.write_bytes(b'changed after selection')
        self.assertIn('checksum', self.run_cli('handoff', ok=False).lower())

    def test_bad_image_does_not_complete_job(self):
        self.init()
        job = self.run_cli('prepare', '--title', 'x', '--direction', 'x')
        bad = self.root / 'pretend.png'
        bad.write_bytes(b'not an image')
        self.run_cli('complete', '--job', job['job_id'], '--image', bad,
                     '--provider', 'built-in-imagegen', ok=False)
        record = self.record()
        self.assertEqual(record['jobs'][0]['status'], 'prepared')
        self.assertEqual(record['candidates'], [])

    def test_blocked_job_has_no_candidate_and_cannot_be_recompleted(self):
        self.init()
        job = self.run_cli('prepare', '--title', 'x', '--direction', 'x')
        self.run_cli('fail', '--job', job['job_id'], '--status', 'blocked', '--reason', 'Provider declined')
        self.assertEqual(self.record()['jobs'][0]['status'], 'blocked')
        self.assertEqual(self.record()['candidates'], [])
        self.run_cli('complete', '--job', job['job_id'], '--image', self.output,
                     '--provider', 'built-in-imagegen', ok=False)

    def test_import_keeps_unknown_provenance_and_does_not_select(self):
        self.init()
        prov = self.root / 'provenance.json'
        prov.write_text(json.dumps({'origin': 'user-provided-existing-image', 'prompt': None,
                                    'model': None, 'notes': 'Uploaded alternate finish'}))
        c = self.run_cli('import', '--image', self.output, '--title', 'Existing finish', '--provenance', prov)
        self.assertIn('candidate_id', c)
        record = self.record()
        self.assertEqual(record['jobs'], [])
        self.assertIsNone(record['selection'])
        self.assertIsNone(record['candidates'][0]['provenance']['prompt'])
        self.assertIsNone(record['candidates'][0]['provenance']['model'])

    def test_invalid_import_title_does_not_poison_next_import(self):
        self.init()
        prov = self.root / 'provenance.json'
        prov.write_text(json.dumps({'origin': 'existing-image'}))
        self.run_cli('import', '--image', self.output, '--title', ' ', '--provenance', prov, ok=False)
        self.assertEqual(self.record()['candidates'], [])
        result = self.run_cli('import', '--image', self.output, '--title', 'Valid title', '--provenance', prov)
        self.assertEqual(result['candidate_id'], 'candidate-0001')

    def test_reinit_does_not_overwrite_project(self):
        self.init()
        before = (self.project / 'project.json').read_bytes()
        self.run_cli('init', '--source', self.output, '--brief', self.brief,
                     '--asset-id', 'DIFFERENT', '--title', 'Replacement', '--mode', 'finish-only', ok=False)
        self.assertEqual((self.project / 'project.json').read_bytes(), before)

    def test_mpo_phone_photo_preserves_auxiliary_images_without_combining_views(self):
        Image.new('RGB', (32, 24), '#496875').save(
            self.source, format='MPO', save_all=True,
            append_images=[Image.new('RGB', (16, 12), '#888888')])
        original = self.source.read_bytes()
        self.init()
        copied = self.project / self.record()['source']['path']
        self.assertEqual(copied.read_bytes(), original)
        self.assertEqual(self.record()['source']['frame_count'], 2)
        self.assertEqual(self.record()['source']['primary_frame'], 0)
        job = self.run_cli('prepare', '--title', 'Finish', '--direction', 'Grey finish')
        request = json.loads(Path(job['request_path']).read_text())
        self.assertEqual(len(request['arguments']['referenced_image_paths']), 1)

    def test_gallery_escapes_metadata_and_keeps_relative_image_links(self):
        self.init(title='<script>alert(1)</script>')
        self.candidate()
        out = self.run_cli('gallery')
        page = Path(out['gallery_path']).read_text()
        self.assertNotIn('<script>alert(1)</script>', page)
        self.assertIn('&lt;script&gt;', page)
        self.assertNotIn(str(self.root), page)
        self.assertIn('source/', page)
        self.assertIn('candidates/', page)

    def test_lock_contention_refuses_mutation(self):
        self.init()
        before = (self.project / 'project.json').read_bytes()
        lock = self.project / '.write.lock'
        lock.write_text('another process')
        self.assertIn('lock', self.run_cli('prepare', '--title', 'x', '--direction', 'x', ok=False).lower())
        self.assertEqual((self.project / 'project.json').read_bytes(), before)
        self.assertEqual(lock.read_text(), 'another process')

    def test_new_candidate_does_not_replace_selected_candidate(self):
        self.init()
        first = self.candidate()['candidate_id']
        self.run_cli('select', '--candidate', first, '--by', 'Designer')
        second = self.candidate()['candidate_id']
        self.assertNotEqual(first, second)
        out = self.run_cli('handoff')
        handoff = json.loads(Path(out['handoff_path']).read_text())
        self.assertEqual(handoff['source_candidate_id'], first)


if __name__ == '__main__':
    unittest.main()
