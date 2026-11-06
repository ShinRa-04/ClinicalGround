import json
from pathlib import Path
import tempfile
import unittest

from health_harness_codex.batch import _save_stage_diagnostic


class StageDiagnosticTests(unittest.TestCase):
    def test_filesystem_code_and_frames_are_saved_without_exception_message_or_locals(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            try:
                exc=PermissionError(13,'DO_NOT_SAVE_THIS_PAYLOAD','locked-export.json')
                exc.winerror=32
                raise exc
            except PermissionError as error:
                self.assertTrue(_save_stage_diagnostic(root,'snapshot',error))
            text=(root/'stage-error.private.json').read_text(encoding='utf-8');record=json.loads(text)
            self.assertEqual(32,record['winerror'])
            self.assertEqual('locked-export.json',record['filename'])
            self.assertTrue(record['frames'])
            self.assertNotIn('DO_NOT_SAVE_THIS_PAYLOAD',text)
            self.assertFalse(_save_stage_diagnostic(root,'second',RuntimeError('secret')))
            self.assertEqual(text,(root/'stage-error.private.json').read_text(encoding='utf-8'))

    def test_unavailable_diagnostic_directory_cannot_mask_original_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            self.assertFalse(_save_stage_diagnostic(Path(temp)/'missing','snapshot',PermissionError('secret')))


if __name__ == '__main__':unittest.main()
