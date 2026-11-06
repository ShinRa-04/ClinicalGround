"""Read-only, bounded investigation before binding an ambiguous patient identity."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json

from .models import ToolSpec, Scope
from .schema import validate_arguments
from .working_set import inspect_source, packed
from .providers import ModelResponseFormatError, FORMAT_CORRECTION


INSPECT = ToolSpec('identity.inspect_candidate',
    'Inspect one already actor-observed candidate chart. No external operations or new files. '
    'Use empty path to discover fields, then JSON field pointers and offset/limit to read passages. '
    'The returned source_id can be cited without copying text. Omitted fields are unknown.',
    {'type':'object','required':['candidate_index'],'additionalProperties':False,'properties':{
        'candidate_index':{'type':'integer','minimum':0},
        'path':{'type':'string','maxLength':1000},
        'offset':{'type':'integer','minimum':0},
        'limit':{'type':'integer','minimum':1,'maximum':4000}}},effect='read')


def _decision(content, count, reads):
    def unique(pairs):
        out={}
        for key,value in pairs:
            if key in out:raise ValueError('duplicate decision key')
            out[key]=value
        return out
    d=json.loads(content,object_pairs_hook=unique)
    if not isinstance(d,dict) or set(d)!={'status','candidate_index','candidate_assessments','uncertainties'}:
        raise ValueError('return exactly status, candidate_index, candidate_assessments, uncertainties')
    if d['status'] not in {'selected','unresolved'}:
        raise ValueError('status must be selected or unresolved')
    if not isinstance(d['uncertainties'],list) or any(not isinstance(x,str) for x in d['uncertainties']):
        raise ValueError('uncertainties must be a list of strings')
    if d['status']=='unresolved':
        if d['candidate_index'] is not None or not d['uncertainties']:
            raise ValueError('unresolved requires null candidate_index and stated uncertainties')
        return d
    selected=d['candidate_index']
    if type(selected) is not int or not 0<=selected<count:
        raise ValueError('selected candidate_index must identify a supplied candidate')
    if not isinstance(d['candidate_assessments'],list) or len(d['candidate_assessments'])!=count:
        raise ValueError('assess every competing candidate before selection')
    seen=set();supported=[]
    for a in d['candidate_assessments']:
        if not isinstance(a,dict) or set(a)!={'candidate_index','supports_selection','reason','source_ids'}:
            raise ValueError('assessment fields: candidate_index, supports_selection, reason, source_ids')
        i=a['candidate_index']
        if type(i) is not int or not 0<=i<count or i in seen:
            raise ValueError('assess each candidate once')
        seen.add(i)
        if type(a['supports_selection']) is not bool or not isinstance(a['reason'],str) or not a['reason'].strip():
            raise ValueError('each assessment requires a boolean and a distinguishing explanation')
        if not isinstance(a['source_ids'],list) or not a['source_ids']:
            raise ValueError('each candidate assessment requires inspected source references')
        for source_id in a['source_ids']:
            if not isinstance(source_id,str) or source_id not in reads or reads[source_id]['candidate_index']!=i:
                raise ValueError('source references must identify successful reads of that candidate')
        if a['supports_selection']:supported.append(i)
    if supported!=[selected]:raise ValueError('select only when your assessments justify exactly one candidate')
    return d


def investigate_identity(task, charts, assessments, complete, *, max_calls=6,
                         max_reads=16, max_context_chars=180000, audit=None):
    """Return selected index or None. Code validates provenance, not identity semantics.

    ``complete`` owns aggregate usage accounting. All records were acquired
    through actor-permitted discovery; this tool cannot query another patient,
    mutate records, inspect fixtures, or access any filesystem path.
    """
    if len(charts)<2 or len(charts)!=len(assessments):raise ValueError('competing candidates required')
    source_hashes=[hashlib.sha256(packed(c).encode()).hexdigest() for c in charts]
    messages=[{'role':'system','content':
        'Investigate patient identity before any patient is selected. Earlier independent comparisons '
        'accepted multiple candidates; those conclusions may be mistaken. Distinguish evidence that '
        'identifies the assigned person from common symptoms or treatment patterns. Consider missing '
        'support and discrepancies without assuming every clinical inconsistency disproves identity. '
        'Read the relevant underlying candidate records using identity.inspect_candidate; explain what '
        'distinguishes every competitor. Do not rank by fixed weights, assume the most detailed record '
        'wins, infer identity from IDs/filenames, force a choice, or make clinical decisions. No writes '
        'are available. Return unresolved if permitted records do not establish a defensible distinction. '
        'Final JSON keys: status (selected or unresolved), candidate_index (zero-based, or null), '
        'candidate_assessments (one per candidate: candidate_index, supports_selection boolean, reason '
        'explaining distinguishing evidence, source_ids from successful inspections of that candidate), '
        'uncertainties (list of strings). For selected, exactly one assessment supports selection. '
        'For unresolved, state the missing distinguishing information in uncertainties. '
        'Cite returned source IDs; code captures the exact observed passages. Do not copy quotations.'},
        {'role':'user','content':'PUBLIC_TASK_TEXT\n'+task+'\nCOMPETING_PRELIMINARY_ASSESSMENTS\n'+
            packed([{'candidate_index':i,'assessment':a} for i,a in enumerate(assessments)])}]
    reads={};read_count=0;format_errors=[]
    def save(status,decision=None):
        if audit:audit({'status':status,'source_hashes':source_hashes,'reads':deepcopy(reads),'decision':decision,
                        'format_errors':deepcopy(format_errors)})
    save('started')
    for _ in range(max_calls):
        if max_context_chars and len(packed(messages))>max_context_chars:
            save('context_budget_exhausted');return None
        try:reply=complete(messages,[INSPECT])
        except ModelResponseFormatError as exc:
            format_errors.append({'call':_+1,'stage':exc.stage})
            save('response_format_failed')
            if len(format_errors)>1:return None
            messages.append({'role':'user','content':FORMAT_CORRECTION})
            continue
        if reply.tool_calls:
            messages.append({'role':'assistant','content':reply.content,'tool_calls':[
                {'id':c.id,'name':c.name,'arguments':c.arguments} for c in reply.tool_calls]})
            for call in reply.tool_calls:
                if read_count>=max_reads:
                    save('read_budget_exhausted');return None
                read_count+=1
                try:
                    if call.name!=INSPECT.name:raise ValueError('only read-only candidate inspection is available')
                    validate_arguments(INSPECT,call.arguments,Scope('discovery','discovery','discovery','discovery','unbound','unbound'))
                    a=call.arguments;i=a['candidate_index']
                    if type(i) is not int or not 0<=i<len(charts):raise ValueError('candidate index not available')
                    view=inspect_source(charts[i],a.get('path',''),a.get('offset',0),a.get('limit',20),max_chars=6000)
                    source_id=f'identity-read:{read_count}'
                    reads[source_id]={'candidate_index':i,'source_sha256':source_hashes[i],
                                      'view':view}
                    result={'source_id':source_id,'candidate_index':i,**view}
                except (ValueError,KeyError,TypeError) as exc:
                    result={'error':str(exc)}
                messages.append({'role':'tool','tool_call_id':call.id,'name':call.name,'content':packed(result)})
                save('investigating')
            continue
        try:
            d=_decision(reply.content,len(charts),reads)
        except (ValueError,TypeError) as exc:
            messages.extend([{'role':'assistant','content':reply.content},
                {'role':'user','content':'Decision provenance/format validation failed: '+str(exc)+
                 '. Investigate further or report unresolved; no patient has been bound.'}])
            save('decision_validation_failed');continue
        save(d['status'],d)
        return d['candidate_index'] if d['status']=='selected' else None
    save('model_budget_exhausted');return None
