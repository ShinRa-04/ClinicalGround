"""Controller-owned clean episodes; quarantined state never becomes a prompt."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sqlite3
from typing import Callable
from .models import Limits
from .console_logs import log_event


_ACTOR_FILES = {'events.jsonl','evaluation.json','run.result.json','result.private.json','run.live.md',
                'state.sqlite','state.sqlite-wal','state.sqlite-shm','.setup-exception.private.json'}


def _write(path, value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')


def write_requires_reconciliation(tool, effect, status, result):
    if effect!='write':return False
    if status!='completed':return True
    if tool=='workspace.write_file':return False
    # Only the explicit trusted pre-dispatch rejection is known effect-free.
    # An ordinary application error or timeout is not an undo receipt.
    return not (isinstance(result,dict) and result.get('isError') is True
                and result.get('known_not_dispatched') is True)


def _barriers(root):
    path=root/'state.sqlite'
    if not path.is_file() or path.is_symlink():return ['journal_unavailable']
    connection=sqlite3.connect(path.resolve().as_uri()+'?mode=ro',uri=True)
    try:
        rows=connection.execute("SELECT action_id,tool,effect,status,result_json FROM actions").fetchall()
        return [row[0] for row in rows if write_requires_reconciliation(row[1],row[2],row[3],
                                                                       json.loads(row[4]) if row[4] else None)]
    finally:connection.close()


def _archive(root, number):
    root=root.resolve();target=root/'quarantine'/f'episode-{number:03d}'
    if not target.resolve().is_relative_to(root):raise ValueError('quarantine escaped the attempt directory')
    target.mkdir(parents=True,exist_ok=False)
    inventory={}
    for path in list(root.iterdir()):
        if path.name not in _ACTOR_FILES and not (path.name.startswith('identity-comparison-') and path.name.endswith('.private.json')):
            continue
        if path.is_symlink() or not path.resolve().is_relative_to(root):raise ValueError('unsafe actor archive path')
        if not path.is_file():raise ValueError('actor artifact must be a regular file')
        inventory[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
        path.rename(target/path.name)
    _write(target/'integrity.json',inventory)
    return {'archive':str(target.relative_to(root)),'sha256':inventory}


def run_identity_episodes(run_episode: Callable, parameters: dict, max_resets: int = 2):
    """Restart only after a model request, before external effects, with budgets carried."""
    if isinstance(max_resets,bool) or not isinstance(max_resets,int) or not 0<=max_resets<=4:
        raise ValueError('max_identity_resets must be between zero and four')
    Limits(max_model_calls=parameters['max_model_calls'],max_tool_calls=parameters['max_tool_calls'],
           max_context_chars=parameters['max_context_chars'])
    root=Path(parameters['run_dir']).resolve()
    control=root/'identity-resets.private.json'
    if control.exists():raise ValueError('identity reset history already exists; preserve and reconcile this attempt')
    model_cap=parameters['max_model_calls'];tool_cap=parameters['max_tool_calls']
    spent_model=spent_tools=spent_actor=spent_bootstrap=0;usage={};observed_usage={};history=[];patients=[];cases=[]
    while True:
        episode=dict(parameters)
        episode['max_model_calls']=model_cap-spent_model
        episode['max_tool_calls']=tool_cap-spent_tools
        if history:
            episode['_excluded_patient_ids']=tuple(patients)
            episode['_excluded_case_ids']=tuple(cases)
        try:
            report=run_episode(**episode)
        except Exception:
            if history:
                _write(control,{'status':'restart_failed','episodes':history,'spent_model_calls_before_failure':spent_model,
                                'spent_tool_calls_before_failure':spent_tools})
            raise
        local=report['local_harness'];request=local.get('identity_reselection') or {}
        evaluation_path=root/'evaluation.json'
        episode_evaluation=json.loads(evaluation_path.read_text()) if evaluation_path.is_file() else {}
        for name,value in episode_evaluation.get('metrics',{}).get('reported_usage_this_segment',{}).items():
            if isinstance(value,int) and not isinstance(value,bool):observed_usage[name]=observed_usage.get(name,0)+value
        spent_model+=report.get('model_calls_total_observed',local.get('model_calls',0))
        spent_actor+=local.get('model_calls',0);spent_bootstrap+=report.get('bootstrap_model_calls',0)
        spent_tools+=local.get('tool_calls',0)
        for name,value in local.get('usage',{}).items():
            if isinstance(value,int) and not isinstance(value,bool):usage[name]=usage.get(name,0)+value
        if request.get('requested') and request.get('reset_allowed'):
            barriers=_barriers(root)
            if barriers:
                local['status']='blocked';request.update(reset_allowed=False,requires_reconciliation=True)
                request['controller_barriers']=barriers
            elif len(history)>=max_resets or spent_model>=model_cap or spent_tools>=tool_cap:
                local['status']='unresolved'
                local['workflow_stop_reason']='identity_reset_limit_or_budget_exhausted'
                request['reset_allowed']=False
            else:
                scope=report['scope']
                patients.append(scope['patient']);cases.append(scope['case'])
                _write(control,{'status':'archiving','episodes':history,'spent_model_calls':spent_model,'spent_tool_calls':spent_tools})
                archived=_archive(root,len(history)+1)
                history.append({**archived,'model_calls':report.get('model_calls_total_observed',local.get('model_calls',0)),
                                'tool_calls':local.get('tool_calls',0),'scope_fingerprint':hashlib.sha256(
                                    json.dumps(scope,sort_keys=True).encode()).hexdigest()})
                _write(control,{'status':'rediscovering','episodes':history,'spent_model_calls':spent_model,'spent_tool_calls':spent_tools})
                log_event('identity_reset_started',task_id=scope['task'],domain=parameters.get('domain'),
                          count=len(history),model_calls=spent_model,tool_calls=spent_tools)
                continue
        if request.get('requested') and not request.get('reset_allowed'):
            log_event('identity_reset_blocked',task_id=report['scope']['task'],domain=parameters.get('domain'),
                      model_calls=spent_model,tool_calls=spent_tools,status=local['status'])
        if not history and not request:return report
        report['identity_reset_history']=history
        report['model_calls_total_observed']=spent_model;report['bootstrap_model_calls']=spent_bootstrap
        report['model_call_budget_total']=model_cap
        report['reported_usage_all_episodes']=observed_usage
        local.update(model_calls=spent_actor,tool_calls=spent_tools,usage=usage)
        local['identity_reset_count']=len(history)
        _write(root/'run.result.json',report)
        _write(root/'result.private.json',local)
        evaluation=root/'evaluation.json'
        if evaluation.is_file():
            data=json.loads(evaluation.read_text());data['identity_reset_history']=history
            data['harness_status']=local['status'];data['metrics']['model_calls']=spent_model
            data['metrics']['tool_calls']=spent_tools;data['metrics']['reported_usage']=usage
            data['metrics']['reported_usage_all_episodes']=observed_usage
            _write(evaluation,data)
        _write(control,{'status':'finished','episodes':history,'spent_model_calls':spent_model,'spent_tool_calls':spent_tools})
        return report
