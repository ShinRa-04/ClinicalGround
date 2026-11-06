"""Synthetic offline source coverage regressions; no benchmark policy/fixtures."""
import copy
import unittest

from health_harness_codex.planning import observe_progress, progress_recovery


def read(path='/synthetic/a.md', text='abcdefghij', offset=0, version='v1'):
    return {'path':path, 'sha256':version, 'offset_chars':offset, 'text':text}


def search(path='/synthetic/a.md', text='abcdefghij', start=0, version='v1', score=1):
    return {'documents':[], 'matches':[{'document_id':'doc',
        'source':{'path':path, 'sha256':version}, 'start':start,
        'end':start+len(text), 'text':text, 'scores':{'rrf':score}}],
        'embedding_metrics':{'elapsed_seconds':score}, 'query_cache':{'status':str(score)}}


class RetrievalProgressTests(unittest.TestCase):
    def setUp(self):
        self.state={'model_calls':1,'status':'running','messages':[]}

    def observe(self, name, result, args=None, outcome='success'):
        s=self.state
        feedback=observe_progress(s,name,args or {},result,f'ev:{s["model_calls"]}',outcome)
        s['model_calls']+=1
        return feedback

    def test_reworded_searches_ignore_size_ranking_and_cache_metadata(self):
        original=search();saved=copy.deepcopy(original)
        self.assertIsNone(self.observe('workspace.hybrid_search',original,{'query':'first','max_chars':2000}))
        feedback=self.observe('workspace.hybrid_search',search(score=2),{'query':'reworded','max_results':9,'max_chars':4000})
        self.assertFalse(feedback['new_source_information'])
        self.assertEqual('ev:1',feedback['first_matching_evidence_id'])
        self.assertEqual(saved,original)  # No filtering/mutation of source results.

    def test_new_document_is_progress(self):
        self.observe('workspace.hybrid_search',search())
        self.assertIsNone(self.observe('workspace.hybrid_search',search(path='/synthetic/b.md',score=2)))
        self.assertEqual(2,self.state['last_information_progress_call'])

    def test_new_passage_in_same_document_is_progress(self):
        self.observe('workspace.hybrid_search',search())
        self.assertIsNone(self.observe('workspace.hybrid_search',search(text='unread',start=10)))

    def test_exact_repeats_remain_detected(self):
        for name,result in [('workspace.hybrid_search',search()),('workspace.read_file',read()),('records.read',{'value':1})]:
            with self.subTest(name=name):
                self.setUp()
                self.assertIsNone(self.observe(name,result))
                self.assertFalse(self.observe(name,result)['new_source_information'])

    def test_reread_with_new_size_and_same_offset_is_detected(self):
        self.observe('workspace.read_file',read(),{'max_bytes':10})
        self.assertFalse(self.observe('workspace.read_file',read(text='abcde'),{'max_bytes':5})['new_source_information'])

    def test_read_many_and_read_file_share_case_coverage(self):
        self.observe('workspace.read_many',{'items':[{'operation':'read_file','result':read()}]})
        self.assertFalse(self.observe('workspace.read_file',read())['new_source_information'])
        self.assertFalse(self.observe('workspace.read_many',{'items':[{'operation':'read_file','result':read()}]})['new_source_information'])

    def test_new_offset_extended_page_and_changed_file_are_progress(self):
        self.observe('workspace.read_file',read())
        self.assertIsNone(self.observe('workspace.read_file',read(text='next',offset=10)))
        self.assertIsNone(self.observe('workspace.read_file',read(text='abcdefghijklmnop')))
        self.assertIsNone(self.observe('workspace.read_file',read(text='changed',version='v2')))

    def test_full_read_covers_search_but_unread_header_or_qualification_is_progress(self):
        self.observe('workspace.read_file',read())
        self.assertFalse(self.observe('workspace.hybrid_search',search(text='cde',start=2))['new_source_information'])
        result=search(text='cde',start=2)
        result['documents']=[{'source':{'path':'/synthetic/a.md','sha256':'v1'},
            'header':{'start':0,'text':'abc'},'qualifying_sections':[{'start':10,'text':'unread qualification'}]}]
        self.assertIsNone(self.observe('workspace.hybrid_search',result))

    def test_subset_of_previously_seen_results_and_order_are_not_progress(self):
        first=search();second=search(path='/synthetic/b.md')
        first['matches']+=second['matches']
        self.observe('workspace.hybrid_search',first)
        self.assertFalse(self.observe('workspace.hybrid_search',second)['new_source_information'])
        first['matches'].reverse()
        self.assertFalse(self.observe('workspace.hybrid_search',first)['new_source_information'])

    def test_reworded_repeats_trigger_existing_replanning_nudge(self):
        for i in range(4):
            self.observe('workspace.hybrid_search',search(score=i),{'query':str(i)})
        self.assertTrue(progress_recovery(self.state))
        self.assertEqual('running',self.state['status'])
        self.assertIn('apply the system capability rule',self.state['messages'][-1]['content'])

    def test_unknown_shapes_and_failures_do_not_add_source_coverage(self):
        self.observe('workspace.read_file',read(),outcome='error')
        self.assertNotIn('retrieval_source_progress',self.state)
        self.observe('workspace.read_many',{'items':[{'operation':'other','result':read()}]})
        self.assertNotIn('retrieval_source_progress',self.state)

    def test_unversioned_changed_passage_is_progress(self):
        self.observe('workspace.read_file',read(version=None))
        self.assertIsNone(self.observe('workspace.read_file',read(text='new content',version=None)))

    def test_coverage_does_not_cross_case_state(self):
        self.observe('workspace.read_file',read())
        other={'model_calls':1}
        self.assertIsNone(observe_progress(other,'workspace.read_file',{},read(),'ev:other','success'))


if __name__=='__main__':unittest.main()
