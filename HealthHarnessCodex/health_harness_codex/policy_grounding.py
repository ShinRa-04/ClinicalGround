"""Verify decision-source provenance, never choose a clinical outcome."""
from __future__ import annotations

from copy import deepcopy
import hashlib
from .working_set import business, canonical, pointer
from .completion_contracts import _tool_matches


POLICY_ACTIONS = frozenset({
    'cases.create_from_order',
    'docs.create_submission_bundle','auth.finalize_provider_determination','auth.submit_authorization',
    'review.save_criteria_evaluation','review.submit_nurse_case_recommendation','review.save_md_review',
    'review.submit_md_case_decision','determination.finalize',
    'cm_intake.disenroll_case',
})


# The requested service fields committed when a provider case is created; every later
# review depends on them, so they are bound and grounded like a determination.
REQUEST_FIELDS = ('procedure_code', 'diagnosis_codes', 'site_of_service', 'service_type')

# Coverage/clinical determinations need a clinical policy source; other
# operations (routing, intake, notices, CM workflow) may rest on the governing
# operational procedure alone.
DETERMINATION_ACTIONS = POLICY_ACTIONS - {'cm_intake.disenroll_case'}


class PolicyGroundingError(ValueError):
    def __init__(self,message,**feedback):
        super().__init__(message)
        self.feedback=feedback


def operation_name(name):
    # MCP aliases truncate long method names before hashing. Do not let that
    # truncation bypass a known policy-dependent action.
    return next((op for op in POLICY_ACTIONS if _tool_matches(name,[op])),canonical(name))


def _cited_path(data, text_pointer):
    """Best-effort file location behind a citation, for rejection feedback only."""
    parts=[p for p in str(text_pointer).split('/') if p]
    try:
        if len(parts)>=2 and parts[0] in {'items','matches','documents'} and parts[1].isdigit():
            node=data[parts[0]][int(parts[1])]
            node=node.get('result',node.get('source',node)) if isinstance(node,dict) else {}
            return node.get('path') if isinstance(node,dict) else None
        return data.get('path') if isinstance(data,dict) else None
    except (KeyError,IndexError,TypeError):
        return None


def _source(state, source_id):
    item=next((e for e in state.get('evidence',[]) if e.get('id')==source_id),None)
    if item is None or item.get('outcome')!='success' or item.get('scope')!=state.get('scope'):
        from .planning import _source_error
        detail=_source_error(state,source_id,item).partition(': ')[2]
        raise ValueError('decision sources must be successful observations in this exact case'+(': '+detail if detail else ''))
    return item


def _policy_text_source(item,path,value,*,allow_workflow=False):
    """Recognize reference content, rather than metadata or patient opinions."""
    name=canonical(item.get('tool',''));data=business(item['observed_result'])
    if name.startswith(('chart.','case.','workspace.write')) or operation_name(item.get('tool','')) in POLICY_ACTIONS:
        return False
    method=name.partition('.')[2]
    if name not in {'workspace.read_file','workspace.read_pdf','workspace.hybrid_search','workspace.read_many'} and not method.startswith(('get','read','list','search')):
        return False
    parts=[p.casefold() for p in path.split('/') if p]
    if not isinstance(value,str) or not value.strip():return False
    if not parts or parts[-1] in {'id','title','name','path','filename','url','policy_id','policy_name'}:return False
    if name=='workspace.hybrid_search':
        if len(parts)<3 or parts[0] not in {'matches','documents'} or not parts[1].isdigit() or parts[-1]!='text':return False
        try:source=data[parts[0]][int(parts[1])]['source']
        except (KeyError,IndexError,TypeError):return False
        source_path=source.get('path','')
        return (source_path.startswith('/workspace/skills/managed-care-operations-handbook/references/') and
                (allow_workflow or any(x in source_path for x in ('/medical-library/','/pa-requirements/'))) and
                isinstance(source.get('sha256'),str) and len(source['sha256'])==64)
    if name=='workspace.read_many':
        # A batch does not elevate search snippets, errors or arbitrary files
        # into policy. Validate the original child reader and approved path.
        if len(parts)<4 or parts[0]!='items' or not parts[1].isdigit() or parts[2]!='result':return False
        try:child=data['items'][int(parts[1])]
        except (KeyError,IndexError,TypeError):return False
        if child.get('operation') not in {'read_file','read_pdf'} or 'error' in child.get('result',{}):return False
        return _policy_text_source({'tool':'workspace.'+child['operation'],'observed_result':child['result']},
            '/'+ '/'.join(path.split('/')[4:]),value,allow_workflow=allow_workflow)
    if name in {'workspace.read_file','workspace.read_pdf'}:
        source_path=str(data.get('path','')) if isinstance(data,dict) else ''
        return (source_path.startswith('/workspace/skills/managed-care-operations-handbook/references/') and
                (allow_workflow or any(x in source_path for x in ('/medical-library/','/pa-requirements/'))) and
                ('text' in parts or 'pages' in parts))
    if name.startswith(('payer_policy_library.','payer.policy_library','policy.','policies.')):return True
    if any(part in {'policy','policy_text','criteria','criteria_text','guideline','guideline_text',
                    'coverage_policy','policy_reference'} for part in parts):
        return not name.startswith('workspace.write')
    if isinstance(data,dict):
        nodes=[data]
        for key in ('document','policy','result'):
            if isinstance(data.get(key),dict):nodes.append(data[key])
        return any(n.get('kind',n.get('source_type',n.get('document_type'))) in
                   {'policy','medical_policy','coverage_policy','policy_reference','clinical_guideline'} for n in nodes)
    return False


REFERENCE_ROOT='/workspace/skills/managed-care-operations-handbook/references/'


def _reference_source(item):
    """A retrieved policy, requirement or handbook reference, as opposed to a case record."""
    name=canonical(item.get('tool',''));data=business(item.get('observed_result'))
    if name.startswith(('payer_policy_library.','payer.policy_library','policy.','policies.')):return True
    if not name.startswith('workspace.') or not isinstance(data,dict):return False
    paths=[data.get('path')]
    for key in ('items','matches','documents'):
        for node in data.get(key,[]) if isinstance(data.get(key),list) else []:
            if isinstance(node,dict):
                paths+=[node.get('path')]+[node[k].get('path') for k in ('source','result') if isinstance(node.get(k),dict)]
    return any(isinstance(path,str) and path.startswith(REFERENCE_ROOT) for path in paths)


def record_decision(state,args,allowed_operations,actual_scope):
    operations=list(dict.fromkeys(operation_name(name) for name in args['applies_to']))
    cm_exit = 'cm_intake.disenroll_case' in operations
    determinations = [op for op in operations if op in DETERMINATION_ACTIONS]
    clinical_cited = False
    if cm_exit and operations != ['cm_intake.disenroll_case']:
        raise ValueError('record CM terminal closure separately from other policy actions')
    if not operations or any(op not in allowed_operations for op in operations):
        raise PolicyGroundingError('decision operations must be canonical names from the available actor registry',
            reason='operation_not_available',unavailable_operations=[op for op in operations if op not in allowed_operations],
            available_policy_operations=sorted(POLICY_ACTIONS.intersection(allowed_operations)))
    policies=[]
    for citation_index,citation in enumerate(args['policy_sources']):
        item=_source(state,citation['evidence_id']);data=business(item['observed_result'])
        path=citation.get('text_pointer',citation.get('path'))
        file_source=canonical(item.get('tool',''))=='workspace.read_file' and isinstance(data,dict)
        # Resolve only an exact already-observed file location. Never open a
        # path supplied by the model or guess which external file it intended.
        if file_source and not citation.get('text_pointer') and (path is None or path==data.get('path')):
            path='/text'
        if path is None:
            raise ValueError('supply text_pointer as a JSON field pointer, for example /policy_text; it is not a filesystem path')
        try:value=pointer(data,path)
        except (ValueError,KeyError,TypeError):
            raise PolicyGroundingError('policy text field not found: use text_pointer relative to the stored business result, e.g. /text for file reads or /policy_text for a tool response; filesystem paths must exactly match the retrieved file',
                reason='text_pointer_not_found',citation_index=citation_index,evidence_id=citation['evidence_id'],
                available_top_level_fields=list(data) if isinstance(data,dict) else [],
                file_text_pointer='/text' if file_source else None) from None
        if _policy_text_source(item,path,value,allow_workflow=False):
            clinical_cited = True
        elif not _policy_text_source(item,path,value,allow_workflow=True):
            raise PolicyGroundingError('a policy citation must identify retrieved policy text, not metadata, a chart opinion or authored draft',
                reason='not_retrieved_policy_text',citation_index=citation_index,evidence_id=citation['evidence_id'],
                text_pointer=path,source_tool=canonical(item.get('tool','')),source_path=_cited_path(data,path))
        # Coordinates refer to this stored text field, not the original file's
        # absolute offsets. Omitting them cites the entire returned passage.
        # Legacy exact quotes remain readable for existing callers/receipts.
        ranged='start' in citation or 'end' in citation
        if ranged and 'quote' in citation:
            raise ValueError('use passage coordinates or a legacy quotation, not both')
        if ranged or 'quote' not in citation:
            start=citation.get('start',0);end=citation.get('end',len(value))
            if type(start) is not int or type(end) is not int or not 0<=start<end<=len(value):
                raise PolicyGroundingError('passage offsets must satisfy 0 <= start < end <= source_text_characters; omit both to cite the entire returned text field',
                    reason='invalid_passage_range',citation_index=citation_index,evidence_id=citation['evidence_id'],
                    text_pointer=path,source_text_characters=len(value))
            quote=value[start:end]
        else:
            quote=citation['quote'];start=value.find(quote) if isinstance(quote,str) else -1
            end=start+len(quote) if isinstance(quote,str) else -1
        if not isinstance(quote,str) or len(quote.strip())<8 or quote not in value:
            raise PolicyGroundingError('policy quotation must be copied exactly from the referenced source field',
                reason='quotation_not_verbatim',citation_index=citation_index,evidence_id=citation['evidence_id'],
                text_pointer=path,source_text_characters=len(value),
                inspect_source={'tool':'case.inspect_evidence','arguments':{'id':citation['evidence_id'],
                                'path':path,'offset':0,'limit':4000}},
                instruction='A paraphrase or joined sentences are not an exact quotation. Inspect the original text and cite only the exact returned wording.')
        policies.append({'evidence_id':citation['evidence_id'],'path':path,
                         'start':start,'end':end,'quote':quote,
                         'source_text_sha256':hashlib.sha256(value.encode()).hexdigest()})
    if not policies:raise ValueError('retrieve governing policy text before recording a policy-dependent decision')
    if determinations and not clinical_cited:
        raise PolicyGroundingError('a coverage or clinical determination must also cite retrieved clinical policy or requirement text',
            reason='clinical_source_required_for_determination',determination_operations=determinations)
    clinical=[];attachments=[]
    for source_id in args['case_evidence_ids']:
        item=_source(state,source_id)
        if canonical(item.get('tool','')).startswith('workspace.'):
            from .attachment_sources import attachment_receipts, AttachmentSourceError
            try:attachments.extend(attachment_receipts(state,item,actual_scope))
            except AttachmentSourceError as exc:
                raise PolicyGroundingError(str(exc),reason='unverified_case_attachment',evidence_id=source_id,
                    instruction='Use a same-case actor listing and read its exact relative_path with workspace.read_pdf/read_file. '
                    'Filename similarity is insufficient; generated drafts and fixed policies are not clinical attachments.') from None
        clinical.append(source_id)
    if not clinical:raise ValueError('a policy-dependent decision requires observed case evidence')
    bindings={}
    for k,v in args.get('bound_arguments',{}).items():
        key=operation_name(k)
        if key in bindings:raise ValueError('duplicate canonical operation in bound arguments')
        bindings[key]=v
    if not isinstance(bindings,dict) or any(op not in operations or not isinstance(v,dict) for op,v in bindings.items()):
        raise ValueError('bound arguments must map decision operations to argument objects')
    if 'auth.finalize_provider_determination' in operations and not isinstance(
            bindings.get('auth.finalize_provider_determination',{}).get('final_action'),str):
        raise ValueError('bind the intended final_action before recording a provider disposition')
    field_basis=[]
    if 'cases.create_from_order' in operations:
        bound=[k for k in REQUEST_FIELDS if k in bindings.get('cases.create_from_order',{})]
        if not bound:
            raise ValueError('bind the requested service fields you will send ('+', '.join(REQUEST_FIELDS)+
                             ') under cases.create_from_order before recording the request decision')
        given={}
        for entry in args.get('field_basis',[]):
            if entry['field'] in given:raise ValueError('give one field_basis entry per requested field')
            for source_id in entry['source_evidence_ids']:_source(state,source_id)
            given[entry['field']]=entry
        missing=[k for k in bound if k not in given]
        unreferenced=[k for k in bound if k in given and given[k]['basis_kind']=='inferred'
                      and not any(_reference_source(_source(state,i)) for i in given[k]['source_evidence_ids'])]
        if unreferenced and not missing:
            # An inference applies a rule to case facts; the rule must be retrieved, not assumed.
            raise PolicyGroundingError('an inferred request field must also cite the retrieved reference it relies on',
                reason='inferred_field_needs_reference_source',fields=unreferenced,
                instruction='For each inferred value, also cite the retrieved policy, requirement or handbook passage whose '
                    'rule your inference applies (for example a setting or coding rule), alongside the case records; search '
                    'for one if none is retrieved yet. The request still needs a value: when no source states it, choose the '
                    'best-supported value from those rules and the case facts, keep it marked inferred, name the uncertainty '
                    'in unresolved_questions and proceed. Do not leave a required request field blocking creation.')
        if missing:
            # Coverage and provenance only: which value is right stays the actor's judgment.
            raise PolicyGroundingError('each requested service field needs its own field_basis citing retrieved sources',
                reason='request_field_basis_missing',missing_fields=missing,
                instruction='For each missing field, cite the retrieved chart, order, provider or policy record it comes from '
                    'and say whether that source states the value (documented) or you derived it (inferred). If no '
                    'retrieved source settles a field, investigate the records that would before creating the request.')
        field_basis=[deepcopy(given[k]) for k in bound]
    if cm_exit:
        bound = bindings.get('cm_intake.disenroll_case', {})
        if bound.get('case_id') != actual_scope.get('case') or not isinstance(bound.get('reason'), str) or not bound['reason'].strip():
            raise ValueError('bind the actual case_id and exact proposed disenrollment reason before terminal closure')
        if args.get('closure_basis') not in {'patient_refusal','other_policy_basis'}:
            raise ValueError('declare closure_basis as patient_refusal or other_policy_basis; you choose and justify the policy basis')
        outreach = _latest_outreach(state)
        if outreach and outreach['id'] not in clinical:
            raise ValueError('include the latest recorded outreach as case evidence before irreversible closure')
        if args['closure_basis'] == 'patient_refusal' and (not outreach or
                business(outreach['observed_result']).get('engagement_status') != 'refused' or
                business(outreach['observed_result']).get('consent_obtained') is not False):
            raise PolicyGroundingError('the current outreach record does not establish patient refusal',
                reason='refusal_not_recorded',
                instruction='Tentative engagement, missing consent and a conversation stop do not establish refusal. '
                    'Investigate remaining permitted outreach and coordination; do not change the record merely to bypass this check. '
                    'A different terminal reason requires its own supported policy basis. Code does not decide that basis.')
    records=state.setdefault('policy_decisions',[])
    record={'id':f'policy-decision:{len(records)+1}','scope':deepcopy(state['scope']),
            'actual_scope':deepcopy(actual_scope),'applies_to':operations,'bound_arguments':deepcopy(bindings),
            'policy_name':args['policy_name'],'applicability':args['applicability'],
            'policy_sources':policies,'case_evidence_ids':list(dict.fromkeys(clinical)),
            'case_attachment_sources':attachments,
            'assessment':args['assessment'],'unresolved_questions':args['unresolved_questions'],
            'decision':args['decision'],'provenance_verified':True,'semantic_correctness':'not_assessed'}
    if field_basis:
        record['field_basis']=field_basis
    if cm_exit:
        record['closure_basis'] = args['closure_basis']
        record['outreach_evidence_id'] = outreach['id'] if outreach else None
    if state.get('goal_planning_enabled'):
        from .goal_state import action_impact
        valid_ids = {'primary'} | {o['id'] for o in state.get('obligations',[])}
        unmet = list(dict.fromkeys(args.get('unmet_goal_ids',[])))
        if not set(unmet) <= valid_ids:
            raise ValueError('unmet_goal_ids must name primary or existing work in this case')
        if 'primary' in unmet or any(action_impact(state, op, actual_scope) for op in operations):
            if not args.get('remaining_actions_considered') or not str(args.get('why_act_now','')).strip():
                raise ValueError('a terminal action leaving the requested goal unmet requires remaining_actions_considered and why_act_now; investigate useful permitted work before closing')
        record.update(unmet_goal_ids=unmet,remaining_actions_considered=args.get('remaining_actions_considered',[]),
                      why_act_now=args.get('why_act_now',''))
    records.append(record)
    return record


def _latest_outreach(state):
    return next((e for e in reversed(state.get('evidence', []))
                 if e.get('outcome') == 'success' and e.get('scope') == state.get('scope')
                 and canonical(e.get('tool', '')) == 'cm_outreach.end_outreach_call'), None)


def check_decision(state,tool,arguments,actual_scope):
    op=operation_name(tool)
    if not state.get('policy_grounding_required') or op not in POLICY_ACTIONS:return None
    record=next((r for r in reversed(state.get('policy_decisions',[])) if op in r.get('applies_to',[])),None)
    if record is None:return 'no_source_backed_policy_decision'
    if record.get('scope')!=state.get('scope') or record.get('actual_scope')!=actual_scope:
        return 'policy_decision_scope_changed'
    bound=record.get('bound_arguments',{}).get(op,{})
    if any(arguments.get(k)!=v for k,v in bound.items()):
        return 'policy_decision_action_changed'
    if op=='cases.create_from_order' and any(k in arguments and k not in bound for k in REQUEST_FIELDS):
        return 'request_fields_not_bound'
    if op == 'cm_intake.disenroll_case':
        outreach = _latest_outreach(state)
        if record.get('outreach_evidence_id') != (outreach['id'] if outreach else None):
            return 'policy_decision_source_changed'
    try:
        for p in record['policy_sources']:
            item=_source(state,p['evidence_id']);value=pointer(business(item['observed_result']),p['path'])
            if not isinstance(value,str) or p['quote'] not in value or hashlib.sha256(value.encode()).hexdigest()!=p['source_text_sha256']:
                return 'policy_decision_source_changed'
            if 'start' in p and value[p['start']:p['end']]!=p['quote']:
                return 'policy_decision_source_changed'
        for source_id in record['case_evidence_ids']:_source(state,source_id)
        if record.get('case_attachment_sources'):
            from .attachment_sources import attachment_receipts
            receipts=[]
            for source_id in record['case_evidence_ids']:
                item=_source(state,source_id)
                if canonical(item.get('tool','')).startswith('workspace.'):
                    receipts.extend(attachment_receipts(state,item,actual_scope))
            if receipts!=record['case_attachment_sources']:return 'policy_decision_source_changed'
    except (KeyError,ValueError,TypeError):return 'policy_decision_source_unavailable'
    return None


def decision_view(state):
    records=state.get('policy_decisions',[])
    if not records:return {'required':state.get('policy_grounding_required',False),'latest':None}
    latest=deepcopy(records[-1])
    for source in latest['policy_sources']:source.pop('quote',None)
    return {'required':state.get('policy_grounding_required',False),'latest':latest,
            'instruction':'Provenance is checked; policy applicability and judgment remain your responsibility. Reuse this analysis when unchanged; update it when action, evidence or interpretation changes. Administrative readiness is not policy eligibility.'}
