import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sqlite3
import sys
import tempfile
import unittest
import multiprocessing
import time
from contextlib import closing
from unittest.mock import patch

from health_harness_codex.hybrid_search import HybridIndex,DockerEmbedder,CorpusCoverageError,_sections
from health_harness_codex.docker_bridge import _CORPUS_SCRIPT,DockerWorkspaceTools
from health_harness_codex.models import Scope,IsolationError,ToolCall
from health_harness_codex.engine import Harness
from health_harness_codex.store import CaseStore
from health_harness_codex.working_set import packed
from health_harness_codex.policy_grounding import record_decision,check_decision
from health_harness_codex.context import project_context
from health_harness_codex.batch import _evaluation_matches_frozen


class FakeEmbedder:
    """Synthetic vectors test the algorithm, not real embedding relevance."""
    identity={'model':'synthetic-test-vectorizer'}
    def __init__(self):self.calls=[]
    def embed(self,texts,query=False):
        self.calls.append((list(texts),query))
        return [[1.,0.] if any(w in t.casefold() for w in ('cardiac','heart')) else [0.,1.] for t in texts]


def doc(name,text):
    return {'id':name,'title':name,'text':text,'source':{'path':'/approved/'+name,
            'sha256':hashlib.sha256(text.encode()).hexdigest()}}


def _parallel_reference_worker(cache,start,output):
    class SlowEmbedder(FakeEmbedder):
        def embed(self,texts,query=False):
            if not query:time.sleep(.3)
            return super().embed(texts,query=query)
    d=doc('policy','Heart disease assessment by a specialist.')
    d['source'].update(path='/workspace/skills/managed-care-operations-handbook/references/policy.md',trusted_fixed_reference=True)
    encoder=SlowEmbedder();index=HybridIndex('independent-case',encoder,reference_cache=True,cache_path=cache)
    start.wait(10)
    try:
        result=index.search([d],'cardiac',namespace='independent-case')
        output.put({'documents_embedded':sum(len(t) for t,q in encoder.calls if not q),
                    'matches':len(result['matches'])})
    except Exception as exc:output.put({'error':type(exc).__name__})


class HybridSearchTests(unittest.TestCase):
    def test_mixed_corpus_only_persists_verified_reference_vectors(self):
        with tempfile.TemporaryDirectory() as folder:
            ref=doc('policy','Heart assessment and documented criteria.')
            ref['source'].update(path='/workspace/skills/managed-care-operations-handbook/references/policy.md',trusted_fixed_reference=True)
            private=doc('patient','Private patient heart history marker.')
            cache=Path(folder)/'shared.sqlite'
            first=HybridIndex('one',FakeEmbedder(),reference_cache=True,cache_path=cache)
            first.search([ref,private],'cardiac',namespace='one')
            e=FakeEmbedder();second=HybridIndex('two',e,reference_cache=True,cache_path=cache)
            result=second.search([ref,private],'cardiac',namespace='two')
            self.assertEqual(1,result['reference_cache']['disk_hits'])
            self.assertEqual(1,result['reference_cache']['eligible_chunks'])
            embedded=[s for texts,q in e.calls if not q for s in texts]
            self.assertEqual(1,len(embedded));self.assertIn('Private patient',embedded[0])
            with closing(sqlite3.connect(cache)) as c:self.assertEqual(1,c.execute('SELECT count(*) FROM vectors').fetchone()[0])

    def test_concurrent_processes_embed_shared_chunk_only_once(self):
        with tempfile.TemporaryDirectory() as folder:
            ctx=multiprocessing.get_context('spawn');start=ctx.Event();out=ctx.Queue()
            workers=[ctx.Process(target=_parallel_reference_worker,args=(str(Path(folder)/'shared.sqlite'),start,out)) for _ in range(2)]
            try:
                for worker in workers:worker.start()
                start.set();results=[out.get(timeout=30) for _ in workers]
                self.assertTrue(all('error' not in r for r in results),results)
                self.assertEqual(1,sum(r['documents_embedded'] for r in results))
                self.assertTrue(all(r['matches']==1 for r in results))
            finally:
                for worker in workers:
                    worker.join(10)
                    if worker.is_alive():worker.terminate();worker.join(5)
                out.close();out.join_thread()

    def test_case_query_cache_exact_reuse_similarity_and_state_invalidation(self):
        from health_harness_codex.retrieval_cache import CaseQueryCache
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'case.sqlite';e=FakeEmbedder()
            index=HybridIndex('one',e,query_cache=True,query_cache_path=path,relevance_floor=.5)
            documents=[doc('heart','Heart assessment by a specialist.')]
            first=index.search(documents,'cardiac',namespace='one');calls=len(e.calls)
            second=index.search(documents,'cardiac',namespace='one')
            self.assertEqual(calls,len(e.calls));self.assertEqual('exact_hit',second['query_cache']['status'])
            self.assertFalse(second['semantic_executed']);self.assertTrue(second['semantic_result_cached'])
            self.assertEqual(0,second['reference_cache']['disk_hits'])
            self.assertEqual(first['matches'],second['matches'])
            similar=index.search(documents,'heart',namespace='one')
            self.assertEqual('miss',similar['query_cache']['status'])
            self.assertAlmostEqual(1.,similar['query_cache']['nearest_similarity'])
            self.assertFalse(similar['query_cache']['similar_result_reused'])
            changed=copy.deepcopy(documents);changed[0]['source']['evidence_id']='new-original-source'
            result=index.search(changed,'cardiac',namespace='one')
            self.assertEqual('miss',result['query_cache']['status'])
            self.assertEqual('new-original-source',result['matches'][0]['source']['evidence_id'])
            index.relevance_floor=.8
            self.assertEqual('miss',index.search(changed,'cardiac',namespace='one')['query_cache']['status'])
            self.assertEqual('miss',index.search(changed,'cardiac',namespace='one',limit=1)['query_cache']['status'])
            with self.assertRaises(IsolationError):CaseQueryCache('another-case',e.identity,path)
            with self.assertRaises(IsolationError):index.search(changed,'cardiac',namespace='another-case')

    def test_query_cache_keeps_alternating_corpora_and_bounded_results(self):
        with tempfile.TemporaryDirectory() as folder:
            e=FakeEmbedder();index=HybridIndex('one',e,query_cache=True,query_cache_path=Path(folder)/'query.sqlite')
            first=[doc('a','# Policy\n'+('Heart assessment. '*100))]
            second=[doc('b','Heart assessment and evidence of prior treatment.')]
            result=index.search(first,'cardiac',namespace='one',max_chars=4000)
            self.assertTrue(result['matches']);self.assertLessEqual(len(packed(result)),4000)
            index.search(second,'cardiac',namespace='one');count=len(e.calls)
            cached=index.search(first,'cardiac',namespace='one',max_chars=4000)
            self.assertEqual(count,len(e.calls));self.assertEqual('exact_hit',cached['query_cache']['status'])
            self.assertLessEqual(len(packed(cached)),4000)

    def test_reference_lease_releases_after_embedding_failure_and_stale_owner_expires(self):
        from health_harness_codex.hybrid_search import ReferenceVectorCache
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'reference.sqlite';cache=ReferenceVectorCache(FakeEmbedder.identity,path)
            self.assertEqual(['x'],cache.claim(['x'],'crashed',seconds=-1))
            self.assertEqual(['x'],cache.claim(['x'],'new'))
            cache.release('new')
            class Fails(FakeEmbedder):
                def embed(self,*args,**kwargs):raise RuntimeError('synthetic failure')
            d=doc('policy','Heart assessment.')
            d['source'].update(path='/workspace/skills/managed-care-operations-handbook/references/policy.md',trusted_fixed_reference=True)
            with self.assertRaises(RuntimeError):
                HybridIndex('one',Fails(),reference_cache=True,cache_path=path).search([d],'cardiac',namespace='one')
            with closing(sqlite3.connect(path)) as c:self.assertEqual(0,c.execute('SELECT count(*) FROM leases').fetchone()[0])
            self.assertTrue(HybridIndex('two',FakeEmbedder(),reference_cache=True,cache_path=path).search([d],'cardiac',namespace='two')['matches'])

    def test_internal_tool_logging_preserves_results_and_marks_exceptions(self):
        events=[];h=object.__new__(Harness)
        h.progress=lambda event,**fields:events.append((event,fields))
        call=ToolCall('local-1','case.retrieve_evidence',{})
        h._local_call=lambda *args:{'value':'private'}
        self.assertEqual({'value':'private'},h._observed_local_call(None,None,call,None,None))
        self.assertEqual(['local_tool_started','local_tool_finished'],[e for e,_ in events])
        self.assertEqual('success',events[-1][1]['result_status'])
        self.assertNotIn('private',json.dumps(events))
        events.clear()
        def fail(*args):raise ValueError('private')
        h._local_call=fail
        with self.assertRaises(ValueError):h._observed_local_call(None,None,call,None,None)
        self.assertEqual('error',events[-1][1]['result_status'])
        self.assertNotIn('private',json.dumps(events))

    def test_relevance_gate_filters_before_fusion_and_returns_empty_without_leaking_text(self):
        index=HybridIndex('one',FakeEmbedder(),relevance_floor=.665)
        docs=[doc('heart','Heart disease assessment.'),doc('other','Unrelated confidential dental detail.')]
        result=index.search(docs,'cardiac',namespace='one')
        self.assertEqual(['heart'],[m['document_id'] for m in result['matches']])
        self.assertNotIn('confidential',json.dumps(result))
        self.assertEqual(1,result['relevance_gate']['rejected_chunks'])
        empty=index.search([docs[1]],'cardiac',namespace='one')
        self.assertEqual([],empty['matches']);self.assertEqual([],empty['documents'])
        self.assertEqual('no_candidate_above_floor',empty['relevance_gate']['status'])
        self.assertTrue(empty['coverage_complete']);self.assertTrue(empty['semantic_executed'])
        self.assertNotIn('confidential',json.dumps(empty))

    def test_relevance_floor_boundary_is_inclusive_and_invalid_values_rejected(self):
        result=HybridIndex('one',FakeEmbedder(),relevance_floor=1.).search(
            [doc('heart','Heart assessment.')],'cardiac',namespace='one')
        self.assertEqual(1,len(result['matches']))
        for floor in (True,float('nan'),float('inf'),-1.1,1.1,'0.7'):
            with self.subTest(floor=floor),self.assertRaises(ValueError):
                HybridIndex('one',FakeEmbedder(),relevance_floor=floor)

    def test_progress_is_out_of_band_and_warm_index_does_not_claim_reindexing(self):
        events=[];encoder=FakeEmbedder()
        index=HybridIndex('one',encoder,progress=lambda event,**fields:events.append((event,fields)))
        docs=[doc('heart','Heart assessment.')]
        index.search(docs,'cardiac',namespace='one')
        self.assertIn('indexing',[f['stage'] for _,f in events])
        events.clear();before=len(encoder.calls)
        index.search(docs,'cardiac',namespace='one')
        self.assertEqual(before+1,len(encoder.calls))
        self.assertEqual(['checking_vector_cache','cache_ready','indexed','indexed_retrieving','retrieval_finished'],
                         [f['stage'] for _,f in events])
        self.assertTrue(all(set(f)<= {'stage','total','current','count','file_count','cache_hits','cache_misses'} for _,f in events))

    def test_calibration_is_bound_to_embedding_runtime(self):
        from health_harness_codex.hybrid_search import relevance_settings
        with patch('health_harness_codex.hybrid_search.runtime_config',return_value={'configured':False}):
            self.assertEqual(.665,relevance_settings('policy')['minimum_cosine'])
            self.assertEqual(.587,relevance_settings('narrative')['minimum_cosine'])
        with patch('health_harness_codex.hybrid_search.runtime_config',return_value={
            'configured':True,'model':'another','image':'sha256:changed'}):
            with self.assertRaisesRegex(ValueError,'recalibration'):relevance_settings('policy')

    def test_dense_branch_finds_synthetic_semantic_match_without_keyword_overlap(self):
        encoder=FakeEmbedder();index=HybridIndex('one',encoder)
        documents=[doc('dental.md','Dental screening and tooth restoration.'),
                   doc('heart.md','Heart disease assessment and specialist consultation.')]
        result=index.search(documents,'cardiac',namespace='one')
        self.assertEqual('heart.md',result['matches'][0]['document_id'])
        self.assertEqual(0,result['matches'][0]['scores']['bm25'])
        self.assertTrue(result['semantic_executed'])
        self.assertEqual('hybrid_bm25_dense_rrf',result['mode'])

    def test_bm25_preserves_exact_code_candidate_when_dense_vectors_are_equal(self):
        result=HybridIndex('one',FakeEmbedder()).search([
            doc('other.md','Procedure CODE-999 is described.'),doc('target.md','Procedure CODE-123 is described.')],
            'CODE-123',namespace='one')
        self.assertEqual('target.md',result['matches'][0]['document_id'])
        self.assertGreater(result['matches'][0]['scores']['bm25'],0)

    def test_exact_spans_headers_and_exclusions_remain_source_backed(self):
        text='# Synthetic policy\nEffective: a synthetic date.\n## Eligibility\n'+('Heart assessment requires evidence. '*50)+\
             '\n## Exclusions\nA specific exception does not apply.\n## Definitions\nA term is defined here.\n'
        before=doc('policy.md',text);saved=copy.deepcopy(before)
        result=HybridIndex('one',FakeEmbedder()).search([before],'cardiac assessment',namespace='one')
        for h in result['matches']:self.assertEqual(text[h['start']:h['end']],h['text'])
        meta=result['documents'][0]
        for s in [meta['header'],*meta['qualifying_sections']]:self.assertEqual(text[s['start']:s['end']],s['text'])
        self.assertTrue(any('Exclusions' in s['heading'] for s in meta['qualifying_sections']))
        self.assertFalse(meta['qualifications_complete']);self.assertEqual(saved,before)

    def test_scope_mismatch_is_rejected_before_embedding_and_changed_text_is_reembedded(self):
        e=FakeEmbedder();index=HybridIndex('one',e)
        with self.assertRaises(IsolationError):index.search([doc('x','Heart assessment')],'cardiac',namespace='two')
        self.assertEqual([],e.calls)
        index.search([doc('x','Heart assessment')],'cardiac',namespace='one')
        calls=len(e.calls);index.search([doc('x','Heart assessment')],'cardiac',namespace='one')
        self.assertEqual(calls+1,len(e.calls)) # unchanged corpus only re-embeds query
        index.search([doc('x','Different heart assessment')],'cardiac',namespace='one')
        self.assertEqual(calls+3,len(e.calls));self.assertEqual(1,len(index.cache))

    def test_output_budget_and_missing_backend_are_explicit(self):
        text='# Policy\n'+('Heart assessment. '*100)+'\n## Exclusions\n'+('Not eligible. '*200)
        result=HybridIndex('one',FakeEmbedder()).search([doc('x',text)],'cardiac',namespace='one',max_chars=4000)
        self.assertLessEqual(len(packed(result)),4000);self.assertTrue(result['matches'])
        with self.assertRaisesRegex(RuntimeError,'not configured'):
            HybridIndex('one',DockerEmbedder({'configured':False})).search([doc('x',text)],'cardiac',namespace='one')

    def test_output_budget_stops_packing_instead_of_walking_all_lower_ranked_chunks(self):
        text='# Policy\n'+('Heart assessment. '*100)+'\n## Exclusions\n'+('Not eligible. '*100)
        documents=[doc(str(i),text) for i in range(100)]
        with patch('health_harness_codex.hybrid_search._sections',wraps=_sections) as sections:
            result=HybridIndex('one',FakeEmbedder()).search(documents,'cardiac',namespace='one',max_chars=4000)
            self.assertTrue(result['output_partial'])
            self.assertLessEqual(sections.call_count,len(documents)+12)

    def test_entire_corpus_is_indexed_beyond_the_old_prefix_limit(self):
        source=doc('large.md','Heart assessment evidence. '*50000);source['source']['file_index']=4
        result=HybridIndex('one',FakeEmbedder()).search([source],'cardiac',namespace='one')
        self.assertFalse(result['corpus_partial']);self.assertTrue(result['coverage_complete'])
        self.assertGreater(result['indexed_chunks'],1024)

    def test_oversized_corpus_fails_before_ranking_instead_of_returning_a_prefix(self):
        encoder=FakeEmbedder()
        with self.assertRaises(CorpusCoverageError):HybridIndex('one',encoder).search(
            [doc('small','A text.')]*10001,'cardiac',namespace='one')
        self.assertEqual([],encoder.calls)

    def test_fixed_reference_vectors_are_reused_across_cases_but_queries_and_patients_are_not_cached(self):
        with tempfile.TemporaryDirectory(prefix='reference-vector-cache-') as folder:
            cache=Path(folder)/'vectors.sqlite';reference=doc('policy','Heart assessment and its documented criteria.')
            reference['source'].update(path='/workspace/skills/managed-care-operations-handbook/references/medical-library/policy.md',trusted_fixed_reference=True)
            first=HybridIndex('one',FakeEmbedder(),reference_cache=True,cache_path=cache)
            first.search([reference],'cardiac',namespace='one')
            second_encoder=FakeEmbedder();second=HybridIndex('two',second_encoder,reference_cache=True,cache_path=cache)
            result=second.search([reference],'different clinical query',namespace='two')
            self.assertEqual(1,result['reference_cache']['disk_hits'])
            self.assertEqual([True],[query for texts,query in second_encoder.calls])
            with closing(sqlite3.connect(cache)) as c:self.assertEqual(1,c.execute('select count(*) from vectors').fetchone()[0])
            private=doc('private','PRIVATE_PATIENT_MARKER '+('Heart narrative. '*20))
            third=HybridIndex('three',FakeEmbedder(),reference_cache=True,cache_path=cache)
            r=third.search([private],'cardiac',namespace='three')
            self.assertFalse(r['reference_cache']['eligible'])
            self.assertNotIn(b'PRIVATE_PATIENT_MARKER',cache.read_bytes())
            with closing(sqlite3.connect(cache)) as c:self.assertEqual(1,c.execute('select count(*) from vectors').fetchone()[0])

    def test_fixed_source_changes_and_encoder_changes_cannot_reuse_stale_vectors(self):
        with tempfile.TemporaryDirectory(prefix='reference-version-') as folder:
            cache=Path(folder)/'vectors.sqlite';source=doc('policy','Heart assessment original criteria.')
            source['source'].update(path='/workspace/skills/managed-care-operations-handbook/references/policy.md',trusted_fixed_reference=True)
            HybridIndex('one',FakeEmbedder(),True,cache).search([source],'cardiac',namespace='one')
            source['text']+=' An updated clause.';encoder=FakeEmbedder()
            result=HybridIndex('two',encoder,True,cache).search([source],'cardiac',namespace='two')
            self.assertEqual(0,result['reference_cache']['disk_hits']);self.assertEqual(2,len(encoder.calls))
            encoder=FakeEmbedder();encoder.identity={'model':'other-encoder'}
            with self.assertRaisesRegex(ValueError,'encoder mismatch'):
                HybridIndex('three',encoder,True,cache).search([source],'cardiac',namespace='three')

    def test_corpus_transport_pages_are_assembled_before_search_and_manifest_changes_invalidate_memory(self):
        source={'path':'/reference/policy.md','sha256':'a'*64,'page':None,'offset_chars':0,'has_more':True,'total_chars':6}
        first={'id':'policy','title':'policy','text':'abc','source':source}
        second={**first,'text':'def','source':{**source,'offset_chars':3,'has_more':False}}
        class Executor:
            def __init__(self):self.parts=0;self.manifest='one'
            def python_json(self,script,data):
                if data.get('manifest_only'):return {'manifest_sha256':self.manifest,'files':1}
                self.parts+=1
                return {'documents':[second if data.get('cursor') else first],
                    'manifest_sha256':self.manifest,'excluded_sources':[],
                    'next_cursor':None if data.get('cursor') else {'file_index':0,'page_index':0,'text_offset':3}}
        scope=Scope('world','task','org','actor','patient','case');executor=Executor()
        tools=DockerWorkspaceTools('container','/tmp',scope,executor=executor)
        result=tools._collect_hybrid_corpus('/reference')
        self.assertEqual('abcdef',result['documents'][0]['text']);self.assertTrue(result['coverage_complete'])
        tools._collect_hybrid_corpus('/reference');self.assertEqual(2,executor.parts)
        executor.manifest='two';again=tools._collect_hybrid_corpus('/reference');self.assertEqual(4,executor.parts)
        self.assertEqual('abcdef',again['documents'][0]['text'])

    def test_actual_complete_reader_can_rank_a_late_alphabetical_file_after_the_old_256_limit(self):
        with tempfile.TemporaryDirectory(prefix='complete-corpus-') as folder:
            root=Path(folder)
            for i in range(299):(root/f'{i:03d}.md').write_text('Dental screening and followup. '*4,encoding='utf-8')
            target=root/'z-target.md';target.write_text('Heart assessment by a specialist. '*4,encoding='utf-8')
            class Executor:
                def python_json(self,script,data):
                    data={**data,'case_root':str(root),'read_roots':[],'path':str(root)}
                    r=subprocess.run([sys.executable,'-X','utf8','-c',script],input=json.dumps(data),
                        text=True,capture_output=True,timeout=10)
                    if r.returncode:raise RuntimeError(r.stderr)
                    return json.loads(r.stdout)
            scope=Scope('world','task','org','actor','patient','case')
            tools=DockerWorkspaceTools('container','/tmp',scope,executor=Executor())
            tools._hybrid_index=HybridIndex(scope.key,FakeEmbedder())
            result=tools.call('workspace.hybrid_search',{'query':'cardiac'})
            self.assertEqual(300,result['source_documents']);self.assertTrue(result['coverage_complete'])
            self.assertEqual(target.resolve(),Path(result['matches'][0]['source']['path']).resolve())

    def test_embedding_transport_has_gpu_network_isolation_and_cleanup(self):
        config={'configured':True,'image':'sha256:'+'a'*64,'model':'BAAI/bge-small-en-v1.5','device':'gpu'}
        success=subprocess.CompletedProcess([],0,json.dumps({'vectors':[[1.,0.]],'encoder':{
            'providers':['CUDAExecutionProvider','CPUExecutionProvider'],'device':'gpu'}}),'')
        with patch('health_harness_codex.hybrid_search.subprocess.run',return_value=success) as run:
            e=DockerEmbedder(config);self.assertEqual([[1.,0.]],e.embed(['synthetic']))
            command=run.call_args_list[0].args[0]
            self.assertIn('--gpus',command);self.assertIn('--network',command)
            self.assertEqual('none',command[command.index('--network')+1]);self.assertNotIn('--mount',command)
            self.assertEqual(config['image'],command[-1]);self.assertIn('rm',run.call_args_list[-1].args[0])
        success.stdout=json.dumps({'vectors':[[1.,0.]],'encoder':{'providers':['CPUExecutionProvider'],'device':'cpu'}})
        with patch('health_harness_codex.hybrid_search.subprocess.run',return_value=success),self.assertRaisesRegex(RuntimeError,'confirm CUDA'):
            DockerEmbedder(config).embed(['synthetic'])

    def test_fixed_corpus_reader_rejects_foreign_hidden_and_symlink_material(self):
        with tempfile.TemporaryDirectory(prefix='hybrid-boundary-') as folder:
            base=Path(folder);owned=base/'owned';refs=base/'refs';foreign=base/'foreign'
            for p in (owned,refs,foreign):p.mkdir()
            (refs/'policy.md').write_text('Allowed original policy text.',encoding='utf-8')
            (refs/'expectations.json').write_text('HIDDEN_SENTINEL',encoding='utf-8')
            (foreign/'chart.md').write_text('FOREIGN_SENTINEL',encoding='utf-8')
            args={'operation':'corpus','case_root':str(owned),'read_roots':[str(refs)],'path':str(refs)}
            def read(a):
                r=subprocess.run([sys.executable,'-X','utf8','-c',_CORPUS_SCRIPT],input=json.dumps(a),
                    text=True,capture_output=True,timeout=10)
                self.assertEqual(0,r.returncode,r.stderr);return json.loads(r.stdout)
            result=read(args);self.assertEqual(1,len(result['documents']))
            self.assertNotIn('HIDDEN_SENTINEL',packed(result));self.assertNotIn('FOREIGN_SENTINEL',packed(result))
            self.assertIn('error',read({**args,'path':str(foreign)}))
            try:(refs/'linked.md').symlink_to(foreign/'chart.md')
            except OSError:pass
            self.assertNotIn('FOREIGN_SENTINEL',packed(read(args)))

    def test_local_narrative_search_rejects_foreign_source_before_any_embedding(self):
        scope=Scope('world','task','org','actor','patient','case')
        with tempfile.TemporaryDirectory(prefix='hybrid-engine-') as folder:
            store=CaseStore(Path(folder)/'state.sqlite')
            try:
                state=store.open_case(scope,'task','PA');fence=store.claim(scope,'worker',120)
                state['evidence']=[{'id':'original','scope':scope.to_dict(),'outcome':'success','tool':'records.read',
                    'observed_result':{'notes':'Heart assessment and treatment. '*20}},
                    {'id':'foreign','scope':{'patient':'other'},'outcome':'success','observed_result':{}}]
                h=Harness(store,None,None);e=FakeEmbedder();h._narrative_index=HybridIndex(packed(scope.to_dict()),e)
                with self.assertRaises(IsolationError):h._local_call(scope,state,ToolCall('search','case.search_narrative',
                    {'ids':['original','foreign'],'query':'cardiac'}),'worker',fence)
                self.assertEqual([],e.calls)
                result=h._local_call(scope,state,ToolCall('search','case.search_narrative',
                    {'ids':['original'],'query':'cardiac'}),'worker',fence)
                self.assertEqual('original',result['matches'][0]['source']['evidence_id'])
                self.assertEqual('/notes',result['matches'][0]['source']['text_pointer'])
                h._narrative_index=HybridIndex(packed(scope.to_dict()),DockerEmbedder({'configured':False}))
                unavailable=h._local_call(scope,state,ToolCall('search','case.search_narrative',
                    {'ids':['original'],'query':'cardiac'}),'worker',fence)
                self.assertEqual('semantic_backend_unavailable',unavailable['error'])
                self.assertFalse(unavailable['semantic_executed'])
            finally:store.close()

    def test_hybrid_policy_citation_requires_original_reference_not_case_narrative(self):
        scope=Scope('world','task','org','actor','patient','case')
        source={'id':'policy','scope':scope.to_dict(),'outcome':'success','tool':'workspace.hybrid_search',
            'observed_result':{'matches':[{'text':'Synthetic criteria with a qualifying exclusion.',
                'source':{'path':'/workspace/skills/managed-care-operations-handbook/references/medical-library/medical-policies/synthetic.md','sha256':'a'*64}}]}}
        case={'id':'case','scope':scope.to_dict(),'outcome':'success','tool':'cases.get_case','observed_result':{}}
        state={'scope':scope.to_dict(),'policy_grounding_required':True,'evidence':[source,case]}
        args={'policy_name':'Synthetic','applicability':'Synthetic','policy_sources':[{
            'evidence_id':'policy','text_pointer':'/matches/0/text'}],'case_evidence_ids':['case'],
            'assessment':'Compare facts','unresolved_questions':[],'decision':'Model choice','applies_to':['auth.submit_authorization']}
        record_decision(state,args,{'auth.submit_authorization'},scope.to_dict())
        self.assertIsNone(check_decision(state,'auth.submit_authorization',{},scope.to_dict()))
        source['observed_result']['matches'][0]['source']['path']='/logs/workspaces/case/opinion.md'
        with self.assertRaises(ValueError):record_decision(state,args,{'auth.submit_authorization'},scope.to_dict())

    def test_pdf_corpus_has_original_page_and_file_digest_without_ocr(self):
        from tests.test_docker_bridge import DockerBridgeTests
        with tempfile.TemporaryDirectory(prefix='hybrid-pdf-') as folder:
            root=Path(folder);pdf=root/'narrative.pdf'
            DockerBridgeTests._write_synthetic_pdf(pdf,['Original narrative text layer'])
            p=subprocess.run([sys.executable,'-X','utf8','-c',_CORPUS_SCRIPT],input=json.dumps({
                'operation':'corpus','case_root':str(root),'read_roots':[],'path':str(pdf)}),
                text=True,capture_output=True,timeout=10)
            d=json.loads(p.stdout)['documents'][0]
            self.assertEqual(1,d['source']['page']);self.assertTrue(d['source']['text_layer_only'])
            self.assertEqual(hashlib.sha256(pdf.read_bytes()).hexdigest(),d['source']['sha256'])
            self.assertIn('Original narrative',d['text'])

    def test_hybrid_reference_passage_survives_projection_with_exact_citation_pointer(self):
        scope=Scope('world','task','org','actor','patient','case')
        text='ORIGINAL_POLICY_PASSAGE '+('original text '*300)
        source={'id':'policy','scope':scope.to_dict(),'outcome':'success','tool':'workspace.hybrid_search',
            'observed_result':{'matches':[{'document_id':'doc','start':100,'end':100+len(text),'text':text,
                'source':{'path':'/approved/policy.md','sha256':'a'*64}}],'documents':[]}}
        state={'scope':scope.to_dict(),'completion_contract':{'domain':'pa_provider'},'evidence':[source],
               'obligations':[],'domain':'PA'}
        messages=[{'role':'system','content':'rules'},{'role':'user','content':'task'}]
        projected=project_context(messages,state,[],100000)
        self.assertIn(text,projected[0]['content']);self.assertIn('/matches/0/text',projected[0]['content'])

    def test_embedding_identity_is_part_of_frozen_execution_provenance(self):
        with tempfile.TemporaryDirectory(prefix='hybrid-provenance-') as folder:
            root=Path(folder);metadata={'source_fingerprint':'a','source_commit':'b',
                'retrieval_runtime':{'image':'sha256:one'}}
            (root/'evaluation.json').write_text(json.dumps({'metadata':metadata}),encoding='utf-8')
            self.assertTrue(_evaluation_matches_frozen(root,metadata))
            other={**metadata,'retrieval_runtime':{'image':'sha256:two'}}
            self.assertFalse(_evaluation_matches_frozen(root,other))


if __name__=='__main__':unittest.main()
