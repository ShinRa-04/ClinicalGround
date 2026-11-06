import copy
import hashlib
import unittest

from health_harness_codex.attachment_sources import attachment_receipts, AttachmentSourceError
from health_harness_codex.policy_grounding import record_decision, check_decision, PolicyGroundingError
import test_policy_grounding as policy_tests


class AttachmentSourceTests(unittest.TestCase):
    def setUp(self):
        base = policy_tests.PolicyGroundingTests()
        base.setUp()
        self.state = copy.deepcopy(base.state)
        self.args = copy.deepcopy(base.args)
        self.scope = base.scope.to_dict()
        self.operations = base.operations
        self.doc = {'id': 'doc-observed', 'case_id': 'case', 'artifact_type': 'document',
                    'relative_path': 'case/shared/intake/observed.pdf'}
        self.listing = {'id': 'listing', 'tool': 'review.get_nurse_review_data', 'scope': self.scope,
                        'outcome': 'success', 'observed_result': {'documents': [self.doc]}}
        self.file = {'id': 'pdf', 'tool': 'workspace.read_pdf', 'scope': self.scope, 'outcome': 'success',
                     'observed_result': {'path': '/logs/artifacts/workspaces/case/shared/intake/observed.pdf',
                                        'sha256': hashlib.sha256(b'synthetic-pdf').hexdigest(),
                                        'pages': [{'page': 1, 'text': 'Synthetic observed case text.'}]}}
        self.state['evidence'].extend([self.listing, self.file])
        self.args['case_evidence_ids'].append('pdf')

    def test_exact_actor_listed_attachment_can_support_decision_and_is_revalidated(self):
        record = record_decision(self.state, self.args, self.operations, self.scope)
        receipt = record['case_attachment_sources'][0]
        self.assertEqual('listing', receipt['listing_source_id'])
        self.assertEqual('doc-observed', receipt['document_id'])
        self.assertIsNone(check_decision(self.state, 'auth.submit_authorization', {}, self.scope))
        self.file['observed_result']['pages'][0]['text'] += ' Tampered.'
        self.assertEqual('policy_decision_source_changed',
                         check_decision(self.state, 'auth.submit_authorization', {}, self.scope))

    def test_unlisted_alias_foreign_case_draft_and_authored_file_are_rejected(self):
        for kind in ['alias', 'foreign_case', 'foreign_patient', 'draft', 'authored', 'no_text', 'no_hash']:
            state = copy.deepcopy(self.state)
            listing, file = state['evidence'][-2:]
            doc = listing['observed_result']['documents'][0]
            if kind == 'alias': file['observed_result']['path'] = '/logs/artifacts/workspaces/case/copied/observed.pdf'
            elif kind == 'foreign_case': doc['case_id'] = 'different-case'
            elif kind == 'foreign_patient': doc['patient_id'] = 'different-patient'
            elif kind == 'draft': doc['artifact_type'] = 'draft'
            elif kind == 'authored':
                state['evidence'].append({'id': 'write', 'scope': self.scope, 'outcome': 'success',
                    'tool': 'workspace.write_file', 'observed_result': {'path': file['observed_result']['path']}})
            elif kind == 'no_text': file['observed_result']['pages'] = []
            else: file['observed_result'].pop('sha256')
            with self.subTest(kind=kind), self.assertRaises(PolicyGroundingError) as raised:
                record_decision(state, self.args, self.operations, self.scope)
            self.assertEqual('unverified_case_attachment', raised.exception.feedback['reason'])
            self.assertFalse(state.get('policy_decisions'))

    def test_listing_hash_mismatch_and_mutation_cannot_be_silently_accepted(self):
        self.doc['sha256'] = '0' * 64
        with self.assertRaises(AttachmentSourceError): attachment_receipts(self.state, self.file, self.scope)
        self.doc.pop('sha256')
        record_decision(self.state, self.args, self.operations, self.scope)
        self.doc['relative_path'] = 'case/shared/intake/changed.pdf'
        self.assertEqual('policy_decision_source_unavailable',
                         check_decision(self.state, 'auth.submit_authorization', {}, self.scope))

    def test_batched_policy_and_case_attachment_keep_individual_receipts(self):
        self.file['tool'] = 'workspace.read_many'
        self.file['observed_result'] = {'items': [
            {'operation': 'read_file', 'result': copy.deepcopy(self.state['evidence'][0]['observed_result'])},
            {'operation': 'read_pdf', 'result': {'path': '/logs/artifacts/workspaces/case/shared/intake/observed.pdf',
                'sha256': hashlib.sha256(b'pdf').hexdigest(), 'pages': [{'text': 'Observed text'}]}}]}
        record = record_decision(self.state, self.args, self.operations, self.scope)
        self.assertEqual('/items/1/result', record['case_attachment_sources'][0]['result_pointer'])
        self.assertEqual(1, len(record['case_attachment_sources']))

    def test_listing_must_be_an_original_successful_same_case_actor_read(self):
        for kind in ['workspace_listing', 'authored_tool', 'failed', 'other_scope']:
            state = copy.deepcopy(self.state)
            listing = state['evidence'][-2]
            if kind == 'workspace_listing': listing['tool'] = 'workspace.list_files'
            elif kind == 'authored_tool': listing['tool'] = 'docs.generate_draft'
            elif kind == 'failed': listing['outcome'] = 'error'
            else: listing['scope'] = {**self.scope, 'case': 'different'}
            with self.subTest(kind=kind), self.assertRaises(PolicyGroundingError):
                record_decision(state, self.args, self.operations, self.scope)


if __name__ == '__main__': unittest.main()
