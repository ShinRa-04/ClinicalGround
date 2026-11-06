"""Resolve an owner's explicit commit request to its stored, source-bound payload."""
from copy import deepcopy
import hashlib

from .assignment import resolve_tool
from .policy_grounding import operation_name
from .schema import validate_arguments
from .models import IsolationError


def resolve(harness, scope, state, arguments, remote):
    record=next((r for r in state.get('policy_decisions',[]) if r.get('id')==arguments['record_id']),None)
    actual=harness._identity_scope(scope,state)
    if (not record or record.get('scope')!=scope.to_dict() or record.get('actual_scope')!=actual.to_dict()
            or record.get('provenance_verified') is not True):
        raise IsolationError('prepared action requires a current source-backed decision in this exact case')
    op=operation_name(arguments['operation'])
    payload=record.get('bound_arguments',{}).get(op)
    if op not in record.get('applies_to',[]) or not isinstance(payload,dict):
        raise ValueError('the decision does not contain bound arguments for this operation')
    spec=resolve_tool(list(remote.values()),op)
    if spec.effect!='write':
        raise ValueError('use the actual read tool for reads; prepared commits resolve only remote writes')
    if harness._helper_channel:
        job=next((j for j in state.get('helper_jobs',[]) if j['id']==harness._helper_channel['id']),None)
        if not job or not job.get('allow_writes') or spec.name not in job.get('tool_names',[]):
            raise IsolationError('prepared commit cannot expand the helper delegated tool permissions')
    payload=deepcopy(payload)
    validate_arguments(spec,payload,actual)
    key=hashlib.sha256((scope.key+'\0'+record['id']+'\0'+op).encode()).hexdigest()
    return spec,payload,'prepared:'+key,{'record_id':record['id'],'operation':op}
