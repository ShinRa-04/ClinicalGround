"""Offline regression of goal linkage and precommit effects, not benchmark scores."""
import copy
import json
import unittest
from contextlib import closing

from health_harness_codex.models import Scope, ToolCall, ToolSpec, ModelReply, Limits
from health_harness_codex.store import CaseStore
from health_harness_codex.engine import Harness
from health_harness_codex.completion_contracts import build_completion_contract, contract_hash
from health_harness_codex.goal_state import requested_outcome, view, action_impact
from health_harness_codex.planning import record_blocker, working_record_view
from health_harness_codex.terminal_review import before_action
from health_harness_codex.closure import assess_closure
from health_harness_codex.context import project_context
from health_harness_codex.evaluation import classify_result
from health_harness_codex.policy_grounding import record_decision


SCOPE=Scope('synthetic','goal-task','org','actor','patient','case')
INSTRUCTION='Complete intake, outreach, assessment and a finalized care plan.'
EXIT='cm_intake.disenroll_case'


def base():
    c=build_completion_contract(SCOPE.task,'cm',INSTRUCTION,SCOPE.to_dict())
    return {'scope':SCOPE.to_dict(),'instruction':INSTRUCTION,'domain':'CM','composition':'helpers',
        'completion_contract':c,'completion_contract_sha256':contract_hash(c),'goal_planning_enabled':True,
        'model_calls':1,'tool_calls':0,'evidence':[],'obligations':[],'status':'running',
        'messages':[{'role':'system','content':'Source rules'},{'role':'user','content':INSTRUCTION}]}


def ev(s,name,result,effect='write',key=None):
    e={'id':key or 'ev:'+str(len(s['evidence'])),'scope':SCOPE.to_dict(),'outcome':'success',
       'tool':name,'effect':effect,'observed_result':result,'action_id':'action-'+str(len(s['evidence']))}
    s['evidence'].append(e)
    return e


def decline(s):
    ev(s,'cm_intake.open_case',{'case_id':'case'})
    ev(s,'cm_chart.submit_chart_review',{'case_id':'case'})
    ev(s,'cm_outreach.end_outreach_call',{'case_id':'case','engagement_status':'refused',
        'consent_obtained':False,'notes':'Synthetic documented choice.'})
    ev(s,EXIT,{'case_id':'case','status':'disenrolled'})


def decision(s):
    source=ev(s,'cm_chart.get_chart_data',{'case_id':'case','status':'outreach_complete'},'read')
    args={'case_id':'case','reason':'Synthetic policy-supported exit'}
    s['policy_decisions']=[{'id':'decision-1','applies_to':[EXIT],'provenance_verified':True,
        'case_evidence_ids':[source['id']],'policy_sources':[],
        'bound_arguments':{EXIT:args},'assessment':'Source-based interpretation, not clinical ground truth.',
        'remaining_actions_considered':['Review the supported communication path.'],
        'why_act_now':'Synthetic terminal-action justification.'}]
    return ToolCall('terminal',EXIT,args)


class Tools:
    def __init__(self):self.calls=[]
    def list_tools(self):
        return [ToolSpec(EXIT,'Synthetic terminal operation',{'type':'object'},effect='write'),
                ToolSpec('cm_chart.get_chart_data','Scoped read',{'type':'object'},effect='read')]
    def call(self,name,args):
        self.calls.append(name)
        return {'case_id':'case','status':'disenrolled' if name==EXIT else 'outreach_complete'}


class Reviewer:
    def __init__(self):self.calls=0;self.specs=[]
    def complete(self,messages,tools,**kw):
        self.calls+=1;self.specs.append(tools)
        return ModelReply(content=json.dumps({'status':'complete',
            'conclusion':'Owner must compare the proposed exit with remaining permitted work.',
            'evidence_ids':[],'open_questions':[]}))


class GoalPlanningTests(unittest.TestCase):
    def test_supported_decline_does_not_claim_requested_plan_achieved(self):
        s=base();decline(s)
        gate=assess_closure(s)
        self.assertTrue(gate['accepted'])
        self.assertEqual('unmet',gate['requested_outcome']['status'])
        self.assertTrue(gate['requires_stop_assessment'])
        self.assertEqual('cm_documented_refusal_and_disenrollment',gate['branch_id'])
        self.assertIn('finalized_care_plan',gate['requested_outcome']['missing_milestones'])

    def test_generic_workflow_choice_does_not_invent_an_explicit_plan_goal(self):
        s=base();s['instruction']='Complete intake and outreach; proceed according to the care management workflow.'
        s['completion_contract']=build_completion_contract(SCOPE.task,'cm',s['instruction'],SCOPE.to_dict())
        s['completion_contract_sha256']=contract_hash(s['completion_contract']);decline(s)
        self.assertEqual('achieved',requested_outcome(s)['status'])

    def test_pinned_instruction_contract_and_case_sources_cannot_be_replaced(self):
        for mutation in ('instruction','contract','foreign_source'):
            s=base();decline(s)
            if mutation=='instruction':s['instruction']='Different request'
            if mutation=='contract':s['completion_contract']['requested_branch_ids']=[]
            if mutation=='foreign_source':
                for e in s['evidence']:e['scope']={**SCOPE.to_dict(),'patient':'another-patient'}
            with self.subTest(mutation=mutation):
                self.assertNotEqual('achieved',requested_outcome(s)['status'])

    def test_one_blocker_leaves_unrelated_work_visible_without_granting_permission(self):
        s=base();s['obligations']=[{'id':'assessment','status':'open','description':'Assess'},
            {'id':'answer-question','status':'open','description':'Investigate the stated program question.'}]
        record_blocker(s,{'id':'consent','blocked_action':'assessment','claim':'Consent needed for assessment',
            'basis_kind':'hypothesis','affected_obligation_ids':['assessment'],
            'next_investigation':'Check the actual participation question.'},[])
        v=view(s)
        self.assertEqual(['assessment'],v['blockers'][0]['affected_obligation_ids'])
        self.assertEqual(['answer-question'],[o['id'] for o in v['other_open_work']])
        self.assertFalse(v['other_open_work'][0]['permission_to_execute_verified'])
        self.assertFalse(v['blockers'][0]['semantic_necessity_verified'])
        with self.assertRaises(ValueError):
            record_blocker(s,{'id':'bad','blocked_action':'work','claim':'unsupported','basis_kind':'hypothesis',
                             'affected_obligation_ids':['foreign-work']},[])

    def test_projection_does_not_expand_with_closed_history_and_originals_stay_available(self):
        s=base();before=json.dumps(view(s),sort_keys=True)
        s['prerequisite_records']=[{'id':f'history-{i}','status':'resolved','claim':'long '*5000} for i in range(100)]
        s['obligations']=[{'id':f'closed-{i}','status':'closed','description':'long '*5000} for i in range(100)]
        self.assertEqual(before,json.dumps(view(s),sort_keys=True))
        self.assertEqual(100,len(s['prerequisite_records']))
        for i in range(25):
            record_blocker(s,{'id':f'open-{i}','blocked_action':'Investigate '+str(i),
                'claim':'A bounded hypothesis. '*20,'basis_kind':'hypothesis','next_investigation':'Check its source.'},[])
        v=view(s)
        self.assertLessEqual(len(json.dumps(v,ensure_ascii=False)),3200)
        self.assertTrue(v['projection_partial'])
        self.assertEqual('open-24',v['blockers'][0]['id'])
        self.assertEqual(125,len(s['prerequisite_records']))
        detail=view(s,blocker_id='open-0',max_chars=10000)
        self.assertEqual('open-0',detail['blockers'][0]['id'])

    def test_current_goal_slice_replaces_duplicate_records_in_projected_context(self):
        s=base();s['prerequisite_records']=[]
        projected=project_context(s['messages'],s,[],0)
        ledger=json.loads(projected[0]['content'].split('Current case working set:\n')[1])
        self.assertIn('goal_state',ledger)
        self.assertNotIn('prerequisite_records',ledger)
        self.assertNotIn('outstanding_work',ledger)
        self.assertIn('PRIMARY TASK GOAL',ledger['goal_state']['primary_goal']['marker'])

    def test_terminal_helper_runs_before_write_once_then_owner_must_repropose(self):
        with closing(CaseStore(':memory:')) as store:
            s=store.open_case(SCOPE,INSTRUCTION,'CM');s.update({k:v for k,v in base().items() if k!='version'})
            call=decision(s);reviewer=Reviewer();tools=Tools()
            h=Harness(store,reviewer,tools,composition='helpers',recovery_helper_policy='auto')
            owner='owner';fence=store.claim(SCOPE,owner);h._save(SCOPE,s,owner,fence)
            updated,feedback=before_action(h,SCOPE,s,call,owner,fence)
            self.assertEqual('terminal_review_returned_to_owner',feedback['error'])
            self.assertEqual([],tools.calls)
            self.assertEqual(1,reviewer.calls)
            self.assertEqual(2,updated['model_calls'])
            self.assertTrue(all(t.effect=='read' for t in reviewer.specs[0]))
            self.assertEqual([],store.actions(SCOPE))
            updated['model_calls']+=1;h._save(SCOPE,updated,owner,fence)
            updated,again=before_action(h,SCOPE,updated,call,owner,fence)
            self.assertIsNone(again)
            self.assertEqual(1,reviewer.calls)
            changed=ToolCall('changed',EXIT,{**call.arguments,'reason':'Different proposal'})
            updated,rejected=before_action(h,SCOPE,updated,changed,owner,fence)
            self.assertTrue(rejected['known_not_dispatched'])

    def test_ordinary_action_and_legacy_state_do_not_spawn_review(self):
        s=base();self.assertIsNone(action_impact(s,'cm_chart.get_chart_data'))
        self.assertIsNotNone(action_impact(s,EXIT))
        s.pop('goal_planning_enabled');self.assertIsNone(action_impact(s,EXIT))

    def test_finished_unmet_is_not_classified_as_goal_achieved(self):
        s=base();decline(s);s['status']='complete'
        result=Harness._result(s)
        self.assertEqual('finished',result['execution_assessment']['execution_state'])
        self.assertEqual('unmet',result['execution_assessment']['requested_outcome']['status'])
        self.assertEqual('finished_goal_unmet',classify_result(result))

    def test_terminal_decision_needs_goal_impact_justification_before_recording(self):
        s=base()
        case=ev(s,'cm_outreach.end_outreach_call',{'case_id':'case','engagement_status':'refused','consent_obtained':False})
        policy=ev(s,'workspace.read_file',{'path':'/workspace/skills/managed-care-operations-handbook/references/care-management/synthetic.md',
            'text':'Synthetic terminal policy requires an informed supported choice.'},'read')
        args={'policy_name':'Synthetic','applicability':'Synthetic source scope','assessment':'Compare the evidence.',
            'unresolved_questions':[],'decision':'Supported terminal decision','closure_basis':'patient_refusal',
            'policy_sources':[{'evidence_id':policy['id'],'text_pointer':'/text'}],
            'case_evidence_ids':[case['id']],'applies_to':[EXIT],
            'bound_arguments':{EXIT:{'case_id':'case','reason':'Synthetic supported reason'}}}
        with self.assertRaisesRegex(ValueError,'remaining_actions_considered'):
            record_decision(s,args,{EXIT},SCOPE.to_dict())
        self.assertFalse(s.get('policy_decisions'))
        args.update(remaining_actions_considered=['Consider other permitted work.'],why_act_now='Explain the source-supported reason to stop now.')
        r=record_decision(s,args,{EXIT},SCOPE.to_dict())
        self.assertTrue(r['provenance_verified'])
        self.assertEqual('not_assessed',r['semantic_correctness'])

    def test_dispatcher_waits_for_owner_after_review_and_does_not_replay_siblings(self):
        with closing(CaseStore(':memory:')) as store:
            s=store.open_case(SCOPE,INSTRUCTION,'CM');s.update({k:v for k,v in base().items() if k!='version'})
            first=decision(s);tools=Tools();reviewer=Reviewer()
            h=Harness(store,reviewer,tools,composition='helpers',recovery_helper_policy='auto')
            owner='owner';fence=store.claim(SCOPE,owner)
            calls=[h._call_dict(first),h._call_dict(ToolCall('sibling','cm_chart.get_chart_data',{}))]
            s['messages'].append({'role':'assistant','content':'Review proposed action.','tool_calls':calls})
            h._save(SCOPE,s,owner,fence)
            updated,fence=h._execute_calls(SCOPE,s,calls,h._tool_map(),owner,fence)
            self.assertEqual([],tools.calls)
            self.assertEqual([],store.actions(SCOPE))
            self.assertEqual([],h._pending_tool_calls(updated))
            self.assertTrue(any('not_dispatched_after_terminal_review' in m.get('content','') for m in updated['messages']))
            updated['model_calls']+=1
            retry=h._call_dict(ToolCall('owner-reproposal',EXIT,first.arguments))
            updated['messages'].append({'role':'assistant','content':'Reconsidered sources.','tool_calls':[retry]})
            h._save(SCOPE,updated,owner,fence)
            updated,fence=h._execute_calls(SCOPE,updated,[retry],h._tool_map(),owner,fence)
            self.assertEqual([EXIT],tools.calls)
            self.assertEqual(1,reviewer.calls)
            self.assertEqual(1,len(store.actions(SCOPE)))
            self.assertEqual('completed',store.actions(SCOPE)[0]['status'])

    def test_supported_stop_preserves_blocked_work_unfinished_and_requires_acknowledgement(self):
        s=base();decline(s)
        read=ev(s,'records.read',{'reason':'Synthetic external choice documented.'},'read')
        s['obligations']=[{'id':'assessment','status':'open','description':'Perform the assigned assessment.'}]
        record_blocker(s,{'id':'chosen-exit','blocked_action':'assessment','claim':'Source-supported constraint.',
            'basis_kind':'observed_gap','affected_obligation_ids':['assessment'],
            'sources':[{'evidence_id':read['id'],'path':'/reason'}]},[])
        gate=assess_closure(s)
        self.assertTrue(gate['accepted'])
        self.assertEqual(['assessment'],gate['blocked_obligation_ids'])
        self.assertFalse(gate['blocked_work_necessity_verified'])
        extra=copy.deepcopy(s)
        extra['obligations'].append({'id':'other-work','status':'open','description':'Uninvestigated work.'})
        self.assertFalse(assess_closure(extra)['accepted'])
        payload={'status':'complete','claim':'Execution stopped with the requested goal unmet.',
            'evidence_ids':[read['id']], 'stop_assessment':{'no_further_permitted_action':True,
                'reason':'Explain the remaining work and supported constraint.', 'evidence_ids':[read['id']],
                'investigations_performed':[read['id']], 'other_work_considered':['Remaining assessment and coordination.'],
                'waiting_on_obligation_ids':[], 'blocked_obligation_ids':['assessment']}}
        with closing(CaseStore(':memory:')) as store:
            h=Harness(store,None,Tools())
            bad=copy.deepcopy(payload);bad['stop_assessment'].pop('blocked_obligation_ids')
            self.assertNotEqual('complete',h._accept_final(copy.deepcopy(s),json.dumps(bad))['status'])
            result=h._accept_final(s,json.dumps(payload))
            self.assertEqual('complete',result['status'])
            self.assertEqual('unmet',result['completion_gate']['requested_outcome']['status'])
            self.assertEqual('open',result['obligations'][0]['status'])
            self.assertFalse(result['stop_assessment_validation']['semantic_actionability_verified'])

    def test_helpers_disabled_or_last_owner_budget_are_honored_and_reported(self):
        for composition,policy,cap in [('combined','auto',20),('helpers','off',20),('helpers','auto',3)]:
            with self.subTest(composition=composition,policy=policy,cap=cap),closing(CaseStore(':memory:')) as store:
                s=store.open_case(SCOPE,INSTRUCTION,'CM');s.update({k:v for k,v in base().items() if k!='version'})
                call=decision(s);reviewer=Reviewer()
                h=Harness(store,reviewer,Tools(),composition=composition,recovery_helper_policy=policy,limits=Limits(max_model_calls=cap))
                owner='owner';fence=store.claim(SCOPE,owner);h._save(SCOPE,s,owner,fence)
                updated,feedback=before_action(h,SCOPE,s,call,owner,fence)
                self.assertIsNone(feedback)
                self.assertEqual(0,reviewer.calls)
                self.assertEqual('owner_only',next(iter(updated['terminal_reviews'].values()))['status'])

    def test_same_justification_with_new_source_id_does_not_trigger_duplicate_review(self):
        with closing(CaseStore(':memory:')) as store:
            s=store.open_case(SCOPE,INSTRUCTION,'CM');s.update({k:v for k,v in base().items() if k!='version'})
            call=decision(s);reviewer=Reviewer();h=Harness(store,reviewer,Tools(),composition='helpers',recovery_helper_policy='auto')
            owner='owner';fence=store.claim(SCOPE,owner);h._save(SCOPE,s,owner,fence)
            updated,_=before_action(h,SCOPE,s,call,owner,fence)
            duplicate=copy.deepcopy(updated['evidence'][-1]);duplicate['id']='same-observation-new-id';updated['evidence'].append(duplicate)
            updated['policy_decisions'][-1]['case_evidence_ids']=[duplicate['id']]
            updated['model_calls']+=1;h._save(SCOPE,updated,owner,fence)
            updated,feedback=before_action(h,SCOPE,updated,call,owner,fence)
            self.assertIsNone(feedback)
            self.assertEqual(1,reviewer.calls)

    def test_first_premature_stop_gets_one_read_only_challenge_before_owner_continues(self):
        from health_harness_codex.synthetic_contracts import operator_observation_contract
        read='cm_chart.get_chart_data'
        c=operator_observation_contract(SCOPE,'CM',read,[{'id':'observed','path':'status','op':'eq','value':'outreach_complete'}])
        c['domain']='cm';c['requested_branch_ids']=[c['branches'][0]['id']]
        class Model:
            calls=0
            def complete(self,messages,tools,**kw):
                self.calls+=1
                if self.calls==1:
                    return ModelReply(content=json.dumps({'status':'incomplete','claim':'A supposed registry blocks all work.','evidence_ids':[]}))
                if self.calls==2:
                    self_test.assertTrue(all(t.effect=='read' for t in tools))
                    return ModelReply(content=json.dumps({'status':'complete','conclusion':'Inspect the actual available source before stopping.',
                                                         'evidence_ids':[],'open_questions':[]}))
                if self.calls==3:
                    return ModelReply(tool_calls=(ToolCall('read',read,{}),))
                evidence_id=next(json.loads(m['content'])['evidence_id'] for m in reversed(messages)
                    if m.get('role')=='tool' and 'evidence_id' in json.loads(m['content']))
                return ModelReply(content=json.dumps({'status':'complete','claim':'Observed the assigned source.',
                                                     'evidence_ids':[evidence_id]}))
        self_test=self;model=Model();tools=Tools()
        with closing(CaseStore(':memory:')) as store:
            result=Harness(store,model,tools,composition='helpers',recovery_helper_policy='auto').run(
                SCOPE,'Observe the assigned source.','CM',completion_contract=c)
        self.assertEqual('complete',result['status'])
        self.assertEqual('achieved',result['execution_assessment']['requested_outcome']['status'])
        self.assertEqual('proposed_stop',result['recovery_audit']['trigger'])
        self.assertEqual(1,len(result['helper_jobs']))
        self.assertEqual([read],tools.calls)
        self.assertEqual(4,result['model_calls'])

    def test_omitted_work_and_original_instruction_remain_retrievable(self):
        s=base()
        s['obligations']=[{'id':f'work-{i}','status':'open','description':'Original work description. '*100}
                          for i in range(8)]
        first=view(s,limit=1)
        self.assertEqual(1,first['next_work_offset'])
        second=view(s,limit=1,work_offset=first['next_work_offset'])
        self.assertEqual('work-1',second['other_open_work'][0]['id'])
        detail=working_record_view(s,{'kind':'work','id':'work-7'})
        self.assertEqual(s['obligations'][7]['description'],detail['items'][0]['description'])
        self.assertFalse(detail['creates_evidence'])
        s['instruction']=INSTRUCTION+'\n'+'Additional public instructions. '*250
        s['completion_contract']=build_completion_contract(SCOPE.task,'cm',s['instruction'],SCOPE.to_dict())
        s['completion_contract_sha256']=contract_hash(s['completion_contract'])
        with closing(CaseStore(':memory:')) as store:
            h=Harness(store,None,Tools())
            result=h._local_call(SCOPE,s,ToolCall('goal','case.get_goal_state',
                {'instruction_offset':600,'instruction_limit':4000}),None,None)
        self.assertEqual(s['instruction'][600:4600],result['original_instruction']['text'])
        self.assertTrue(result['original_instruction']['has_more'])

    def test_workflow_phrase_cannot_replace_an_explicit_final_plan_request(self):
        s=base()
        s['instruction']=INSTRUCTION+' Proceed according to the care management workflow.'
        c=build_completion_contract(SCOPE.task,'cm',s['instruction'],SCOPE.to_dict())
        s['completion_contract']=c;s['completion_contract_sha256']=contract_hash(c)
        decline(s)
        self.assertEqual(['cm_finalized_care_plan'],c['requested_branch_ids'])
        self.assertEqual('unmet',requested_outcome(s)['status'])

    def test_batch_and_console_show_goal_unmet_even_when_execution_finishes(self):
        import tempfile
        import threading
        from pathlib import Path
        from health_harness_codex.batch import _append_batch_event
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'events.jsonl'
            line=_append_batch_event(path,threading.RLock(),'actor_finished',task_id='synthetic-task',
                harness_status='complete',status='finished',execution_state='finished',goal_status='unmet')
            event=json.loads(path.read_text())
        self.assertIn('WARNING',line)
        self.assertIn('execution_state=finished',line)
        self.assertIn('goal_status=unmet',line)
        self.assertEqual('unmet',event['goal_status'])

    def test_goal_reporting_uses_validated_actor_case_binding_not_internal_namespace(self):
        from health_harness_codex.synthetic_contracts import operator_observation_contract
        scope=Scope('synthetic','bound-goal','org','actor','patient','case-subject:patient')
        task='Observe the actual bound case.'
        c=operator_observation_contract(scope,'PA','cases.get_case',
            [{'id':'case_observed','path':'case_id','op':'eq','value':'actual-case'}])
        c['domain']='pa_provider';c['requested_branch_ids']=[c['branches'][0]['id']]
        c['branches'][0]['requirements'][0]['predicate']={'path':'case_id','op':'matches_scope_case','value':None}
        with closing(CaseStore(':memory:')) as store:
            s=store.open_case(scope,task,'PA')
            s.update(goal_planning_enabled=True,completion_contract=c,completion_contract_sha256=contract_hash(c),
                case_bindings={'case_namespace':scope.case,'case_id':'actual-case','patient_id':scope.patient,
                    'source_tool':'cases.create_from_order','source_evidence_id':'ev:created'},
                evidence=[{'id':'ev:read','scope':scope.to_dict(),'effect':'read','outcome':'success',
                    'tool':'cases.get_case','observed_result':{'case_id':'actual-case'}}])
            h=Harness(store,None,Tools(),case_identity_tools=('cases.create_from_order',))
            owner='owner';fence=store.claim(scope,owner);h._save(scope,s,owner,fence)
            self.assertEqual('actual-case',s['goal_actual_scope']['case'])
            self.assertEqual('achieved',requested_outcome(s)['status'])
            self.assertEqual('achieved',Harness._result(s)['execution_assessment']['requested_outcome']['status'])

    def test_actual_standalone_prompt_wrappers_preserve_the_pinned_public_goal(self):
        from health_harness_codex.standalone import _profile_instruction
        from health_harness_codex.domain_profiles import DOMAIN_PROFILES
        examples={'cm':INSTRUCTION,
                  'pa_um':'Triage Routing. Pick the review lane, then work clinical review, MD decision and any P2P to final determination yourself.',
                  'pa_provider':'Clinical intake. Prepare the supported referral.'}
        class Model:
            def complete(self,*a,**kw):
                return ModelReply(content=json.dumps({'status':'incomplete','claim':'Boundary check only.','evidence_ids':[]}))
        for domain,raw in examples.items():
            with self.subTest(domain=domain),closing(CaseStore(':memory:')) as store:
                profile=DOMAIN_PROFILES[domain]
                wrapped=_profile_instruction(profile,SCOPE.task,{'case_id':SCOPE.case,'patient_id':SCOPE.patient},
                    SCOPE,SCOPE.patient,'/synthetic/workspace',raw)
                self.assertNotEqual(raw,wrapped)
                c=build_completion_contract(SCOPE.task,domain,raw,SCOPE.to_dict())
                result=Harness(store,Model(),Tools(),limits=Limits(max_model_calls=1)).run(
                    SCOPE,wrapped,profile.engine_domain,completion_contract=c)
                saved=store.load_case(SCOPE)
                self.assertEqual(wrapped,saved['instruction'])
                self.assertEqual(raw,saved['completion_contract']['public_instruction'])
                self.assertEqual(raw,view(saved)['primary_goal']['excerpt'])
                self.assertEqual('unmet',result['execution_assessment']['requested_outcome']['status'])

    def test_mismatched_pinned_public_text_is_not_accepted_even_when_contract_is_rehashed(self):
        s=base();s['completion_contract']['public_instruction']='Different public assignment'
        s['completion_contract_sha256']=contract_hash(s['completion_contract'])
        self.assertEqual('unverified',requested_outcome(s)['status'])

    def test_review_is_not_repeated_for_reworded_rationale_or_audit_reason(self):
        with closing(CaseStore(':memory:')) as store:
            s=store.open_case(SCOPE,INSTRUCTION,'CM');s.update({k:v for k,v in base().items() if k!='version'})
            call=decision(s);reviewer=Reviewer();h=Harness(store,reviewer,Tools(),composition='helpers',recovery_helper_policy='auto')
            owner='owner';fence=store.claim(SCOPE,owner);h._save(SCOPE,s,owner,fence)
            updated,_=before_action(h,SCOPE,s,call,owner,fence)
            d=copy.deepcopy(updated['policy_decisions'][-1]);d.update(id='new-words',assessment='A revised explanation.',
                why_act_now='A reworded explanation of the same facts.',decision='Same proposed state transition.')
            d['bound_arguments'][EXIT]['reason']='Reworded audit reason for the same exit'
            updated['policy_decisions'].append(d);updated['model_calls']+=1;h._save(SCOPE,updated,owner,fence)
            revised=ToolCall('revised',EXIT,d['bound_arguments'][EXIT])
            updated,feedback=before_action(h,SCOPE,updated,revised,owner,fence)
            self.assertIsNone(feedback)
            self.assertEqual(1,reviewer.calls)
            self.assertEqual(1,len(updated['terminal_reviews']))
            self.assertFalse(next(iter(updated['terminal_reviews'].values()))['current_wording_independently_reviewed'])
            fresh=copy.deepcopy(updated['evidence'][-1]);fresh.update(id='new-facts',observed_result={'case_id':'case','status':'changed-source'})
            updated['evidence'].append(fresh);d['case_evidence_ids']=['new-facts'];updated['policy_decisions'][-1]=d
            updated['model_calls']+=1;h._save(SCOPE,updated,owner,fence)
            updated,feedback=before_action(h,SCOPE,updated,revised,owner,fence)
            self.assertEqual('terminal_review_returned_to_owner',feedback['error'])
            self.assertEqual(2,reviewer.calls)

    def test_conversation_response_precedes_later_writes_but_not_independent_reads(self):
        for send in ('cm_outreach.send_message','p2p_session.send_turn'):
            with self.subTest(send=send),closing(CaseStore(':memory:')) as store:
                s=store.open_case(SCOPE,INSTRUCTION,'CM');s.update({k:v for k,v in base().items() if k!='version'})
                class ConversationTools:
                    calls=[]
                    def list_tools(self):
                        return [ToolSpec(send,'Interactive response',{'type':'object'},effect='write'),
                            ToolSpec('cm_outreach.end_outreach_call','Save summary',{'type':'object'},effect='write'),
                            ToolSpec('records.read','Independent source',{'type':'object'},effect='read')]
                    def call(self,name,args):
                        self.calls.append((name,args))
                        return {'case_id':'case','patient_response':'Yes, I agree.'} if name==send else {'case_id':'case','saved':args}
                tools=ConversationTools();h=Harness(store,None,tools);owner='owner';fence=store.claim(SCOPE,owner)
                calls=[{'id':'send','journal_id':'m1:send','name':send,'arguments':{}},
                    {'id':'read','journal_id':'m1:read','name':'records.read','arguments':{}},
                    {'id':'stale','journal_id':'m1:stale','name':'cm_outreach.end_outreach_call','arguments':{'consent_obtained':False}}]
                h._save(SCOPE,s,owner,fence)
                updated,fence=h._execute_calls(SCOPE,s,calls,h._tool_map(),owner,fence)
                self.assertEqual([send,'records.read'],[n for n,a in tools.calls])
                self.assertEqual(2,len(store.actions(SCOPE)))
                self.assertTrue(any('conversation_response_must_be_observed_first' in m.get('content','') for m in updated['messages']))
                # A durable readback after interruption still blocks a stale
                # sibling carrying the old proposal round.
                resumed=store.load_case(SCOPE)
                stale=[{**calls[-1],'id':'stale-after-resume','journal_id':'m1:stale-after-resume'}]
                resumed,fence=h._execute_calls(SCOPE,resumed,stale,h._tool_map(),owner,fence)
                self.assertEqual(2,len(tools.calls))
                resumed['model_calls']=2;h._save(SCOPE,resumed,owner,fence)
                fresh=[{'id':'fresh','journal_id':'m2:fresh','name':'cm_outreach.end_outreach_call',
                        'arguments':{'consent_obtained':True}}]
                resumed,fence=h._execute_calls(SCOPE,resumed,fresh,h._tool_map(),owner,fence)
                self.assertEqual(True,tools.calls[-1][1]['consent_obtained'])
                self.assertEqual(3,len(store.actions(SCOPE)))

    def test_dialogue_is_investigation_and_incomplete_stop_gets_one_precise_reference_correction(self):
        from health_harness_codex.closure import assess_stop_record
        s=base();ev(s,'cm_intake.open_case',{'case_id':'case'});ev(s,'cm_chart.submit_chart_review',{'case_id':'case'})
        reply=ev(s,'cm_outreach.send_message',{'patient_response':'I do not agree.','session_status':'ended'})
        summary=ev(s,'cm_outreach.end_outreach_call',{'case_id':'case','engagement_status':'refused',
            'consent_obtained':False,'notes':'Synthetic refusal observed.'})
        ev(s,EXIT,{'case_id':'case','status':'disenrolled'})
        record={'no_further_permitted_action':True,'reason':'Actual observed stopping condition.',
            'evidence_ids':[reply['id']],'investigations_performed':[reply['id']],
            'other_work_considered':['Further permitted contact and assigned work.'],'waiting_on_obligation_ids':[]}
        self.assertTrue(assess_stop_record(s,{'stop_assessment':record},assess_closure(s))['accepted'])
        record['investigations_performed'].append(summary['id'])
        payload={'status':'incomplete','claim':'Requested goal unmet; no useful permitted work remains.',
                 'evidence_ids':[reply['id']],'stop_assessment':record}
        s['pre_dispatch_validation_retry_count']=1
        with closing(CaseStore(':memory:')) as store:
            h=Harness(store,None,Tools())
            result=h._accept_final(s,json.dumps(payload))
            self.assertEqual('running',result['status'])
            self.assertTrue(result['final_format_retry_pending'])
            self.assertIn('investigation_eligible',result['messages'][-1]['content'])
            record['investigations_performed']=[reply['id']]
            result=h._accept_final(result,json.dumps(payload))
            self.assertEqual('complete',result['status'])
            self.assertEqual('unmet',result['completion_gate']['requested_outcome']['status'])

    def test_cm_responsibility_packet_and_observed_terminal_phase_are_consistent(self):
        from health_harness_codex.assignment import stage_guidance
        from health_harness_codex.working_set import stage,select_tools
        s=base();ev(s,'cm_intake.open_case',{'case_id':'case'})
        guidance=stage_guidance(s)
        self.assertEqual('outreach',stage(s))
        self.assertEqual({'CM-03','CM-04','CM-05','CM-09'},{r['role_id'] for r in guidance['responsibility_packet']})
        self.assertTrue(all('inputs' in r and 'output' in r for r in guidance['responsibility_packet']))
        ev(s,EXIT,{'case_id':'case','status':'disenrolled'})
        self.assertEqual('closure',stage(s))
        self.assertEqual('closure',stage_guidance(s)['current_responsibility'])
        self.assertEqual(['CM-20'],[r['role_id'] for r in stage_guidance(s)['responsibility_packet']])
        self.assertTrue(select_tools(Tools().list_tools(),s))


if __name__=='__main__':unittest.main()


def finalized(s):
    ev(s,'cm_intake.open_case',{'case_id':'case'})
    ev(s,'cm_chart.submit_chart_review',{'case_id':'case'})
    ev(s,'cm_outreach.end_outreach_call',{'case_id':'case','consent_obtained':True,'engagement_status':'engaged'})
    ev(s,'cm_assessment.complete_assessment',{'case_id':'case','status':'complete'})
    ev(s,'cm_care_plan.finalize',{'case_id':'case','status':'finalized','problems':['Synthetic problem'],
        'escalation_conditions':['Synthetic condition'],'follow_up_cadence_kind':'monthly'})


class OutstandingDutyTests(unittest.TestCase):
    """-08/-13: requested plan verified, an actor-added duty has no executable tool."""

    def state(self,blocked):
        s=base();finalized(s)
        s['obligations']=[{'id':'summary-duty','description':'Synthetic follow-up duty','status':'open','evidence_ids':[]}]
        if blocked:
            source=ev(s,'records.read',{'operations':[]},'read')
            s['prerequisite_records']=[{'id':'blocker-1','status':'open','basis_kind':'observed_gap',
                'support':'observation_referenced_necessity_unverified','affected_obligation_ids':['summary-duty'],
                'blocked_action':'Synthetic send','facts':{'source_references':[{'evidence_id':source['id']}]}}]
        return s

    def test_verified_outcome_with_source_linked_blocked_duty_is_accepted_and_acknowledged(self):
        s=self.state(True);gate=assess_closure(s)
        self.assertEqual('achieved',gate['requested_outcome']['status'])
        self.assertTrue(gate['accepted'])
        self.assertEqual(['summary-duty'],gate['outstanding_obligation_ids'])
        self.assertEqual(['summary-duty'],gate['blocked_obligation_ids'])
        self.assertTrue(gate['requires_stop_assessment'])
        self.assertIn('completion_note',view(s))

    def test_unlinked_open_duty_still_blocks_completion(self):
        gate=assess_closure(self.state(False))
        self.assertFalse(gate['accepted']);self.assertEqual('open_obligations',gate['reason_code'])
        self.assertNotIn('outstanding_obligation_ids',gate)

    def test_unmet_outcome_is_unchanged(self):
        s=base();s['obligations']=[{'id':'x','status':'open','description':'d','evidence_ids':[]}]
        self.assertNotIn('completion_note',view(s))
        self.assertNotIn('outstanding_obligation_ids',assess_closure(s))
