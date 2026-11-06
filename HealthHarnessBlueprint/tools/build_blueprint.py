"""Publish hypothetical design contracts; never creates/runs a healthcare agent."""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode=True
BASE=Path(__file__).resolve().parents[1];ROOT=BASE.parent
sys.path.insert(0,str(BASE))
from catalog import MODULES,SERVICES,MEMORY_LAYERS
from micro_roles import ROLES
from runtime_overrides import runtime_catalogue


def write(name,text):
    p=BASE/name;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text('\n'.join(line.rstrip() for line in text.splitlines()).rstrip()+'\n',encoding='utf-8',newline='\n')


def dump(name,data):write(name,json.dumps(data,ensure_ascii=False,indent=2))


def main():
    baseline=json.loads((BASE/'baseline.json').read_text(encoding='utf-8'))
    for f in baseline['files']:assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256'],f['path']
    prior=json.loads((ROOT/'Plan/HealthcareRoles/data/roles.json').read_text(encoding='utf-8'))
    role_by={r['id']:r for r in prior};assigned=[r for m in MODULES for r in m['source_roles']]
    assert len(assigned)==len(set(assigned))==97 and set(assigned)==set(role_by)
    assert len(MODULES)==29 and len(SERVICES)==20 and len(MEMORY_LAYERS)==10
    assert len(ROLES)==len({r['id'] for r in ROLES})==66
    assert Counter(r['domain'] for r in ROLES)==dict(PA=18,UM=18,CM=20,SH=10)
    service_ids={s[0] for s in SERVICES}
    assert all(set(m['service_ids'])<=service_ids for m in MODULES)
    dump('data/modules.json',MODULES);dump('data/micro_roles.json',ROLES)
    (ROOT/'HealthHarnessCodex/health_harness_codex/data/micro_roles.json').write_text(
        json.dumps(runtime_catalogue(ROLES),ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    service_data=[dict(id=id,name=name,information=info,contract=contract,actual_tool_mapping='NOT_YET_PERFORMED',implemented=False) for id,name,info,contract in SERVICES]
    memory_data=[dict(id=id,name=name,scope=scope,contents=contents,boundary=boundary,implemented=False) for id,name,scope,contents,boundary in MEMORY_LAYERS]
    dump('data/services.json',service_data);dump('data/memory_layers.json',memory_data)
    policy=dict(status='DESIGN_REQUIREMENT_NOT_IMPLEMENTED',origin='User explicitly requires that patient data not influence another patient’s role behavior.',
        reusable=['approved job definitions','approved general procedures','applicable approved policy/reference versions'],
        case_local=['patient records and evidence','dialogue answers/refusal','derived facts and summaries','episodic recall','checkpoints','helper outputs','tool handles/results'],
        automatic_patient_derived_shared_learning=False,cross_patient_retrieval=False,reassign_provider_thread_without_verified_reset=False,
        actual_isolation_enforced_or_tested=False,operational_state='Only actual permitted operational facts, separately sourced; no other patient chart/context injection.',
        verification_property='Hold B allowed inputs/general versions/operational facts fixed; changes to A must not change B constructed context, source set or permitted operation scope.')
    dump('data/patient_isolation_policy.json',policy)
    variants=[dict(id='C1',name='Single combined agent',behavior='The composite owner performs needed reasoning responsibilities together, retaining deterministic gates and functional output obligations.'),
        dict(id='C2',name='Owner plus bounded helpers',behavior='Only selected work with a useful separate context is delegated; results are case/source/version-linked proposals.'),
        dict(id='C3',name='Selected role-worker team',behavior='Task-relevant responsibilities use separate bounded workers; no blanket activation of every role.')]
    for v in variants:v.update(status='HYPOTHETICAL_NOT_EVALUATED',patient_isolation_required=True,micro_role_count_is_not_call_count=True)
    dump('data/composition_variants.json',variants)
    lines=['# Organizational modules and composite workspaces','',
        '29 logical modules organize the work. Some are composite jobs, some capabilities/services or external interfaces. This is not 29 running agents and is not the deepest decomposition: the three main jobs are built from the [66 smaller responsibility contracts](MICRO_ROLES.md). All names and boundaries are proposed, not actual benchmark API assignments.','']
    for m in MODULES:
        lines += [f'<a id="{m["id"].lower()}"></a>',f'## {m["id"]} — {m["name"]}','',
            '**Kind / principal:** '+m['kind']+' / '+m['principal'],'','**Trigger:** '+m['trigger'],'',
            '**Responsibility:** '+m['responsibility'],'','**Write intent:** '+m['allowed_write_intent'],'',
            '**Boundary:** '+m['retained_boundary'],'','**Instantiation:** '+m['instances'],'',
            '**Service contracts:** '+', '.join(f'[{s}](SERVICE_CONTRACTS.md#{s.lower()})' for s in m['service_ids']), '',
            '**Prior healthcare context:** '+(', '.join(f'[{r} {role_by[r]["title"]}](../Plan/HealthcareRoles/roles/{r}.md)' for r in m['source_roles']) if m['source_roles'] else 'New technical/design responsibility; not an asserted existing healthcare occupation.'), '']
    write('MODULE_CATALOG.md','\n'.join(lines))
    lines=['# Micro-role responsibility contracts','',
        'These 66 proposed responsibilities may or may not correspond to separate real-world people. They compose PA/UM/CM jobs and shared support. A responsibility can be ordinary code, a tool operation, in-context reasoning, a bounded call or a worker; the recommended form below is a starting hypothesis. No role is required on a case unless its output is actually needed.','',
        '[Composition model](COMPOSITION.md) · [Patient isolation](PATIENT_ISOLATION.md) · [Workflows](WORKFLOWS.md)','']
    for family in ['PA','UM','CM','SH']:
        lines += [f'# {family} responsibilities','']
        for r in [r for r in ROLES if r['domain']==family]:
            lines += [f'<a id="{r["id"].lower()}"></a>',f'## {r["id"]} — {r["name"]}','',
                '**Candidate execution form:** '+r['execution_form'],'','**Inputs:** '+r['inputs'],'','**Output:** '+r['output'],'',
                '**Decision scope:** '+r['decision_scope'],'','**Must not assume/do:** '+r['boundary'],'',
                '**Authority:** '+r['authority'],'','**Approach:** '+r['approach'],'',
                '**Hospital roles:** '+(', '.join(r['hospital_roles']) or 'code-only safeguard'),'',
                '**Status label:** '+r['status_label'],'','**Model visible:** '+str(r['model_visible']),'',
                '**Completion check:** '+r['completion_check'],'','**Activation:** '+r['activation'],'',
                '**Memory:** '+r['memory_policy'],'']
    write('MICRO_ROLES.md','\n'.join(lines))
    lines=['# Logical service contracts','',
        'These 20 internal contracts are proposed boundaries, not verified MCP names/endpoints or a one-to-one copy of the benchmark’s apps. Actual task/tool mapping is unperformed. No service is implemented by this document. Unavailable operations must be disabled or remain explicit gaps; there is no second world engine supplying convenient outcomes.','']
    for s in service_data:
        lines += [f'<a id="{s["id"].lower()}"></a>',f'## {s["id"]} — {s["name"]}','',s['information'],'','**Contract:** '+s['contract'],'','**Actual mapping:** not performed; implementation absent.','']
    write('SERVICE_CONTRACTS.md','\n'.join(lines))
    lines=['# Proposed memory layers','',
        'Ten logical surfaces with separate ownership and meaning. They are not ten databases or a selected storage stack. Patient-derived material remains in the current permitted patient/case/task boundary; shared job/procedure knowledge is approved and read-only.','',
        '| ID | Layer | Scope / owner | Contents | Boundary |','| --- | --- | --- | --- | --- |']
    for m in memory_data:lines.append(f'| {m["id"]} | {m["name"]} | {m["scope"]} | {m["contents"]} | {m["boundary"]} |')
    write('MEMORY_LAYERS.md','\n'.join(lines))
    coverage=[];lines=['# Coverage of prior real-world functions','',
        'All 97 prior functional profiles have one primary organizational/interface mapping. This preserves context; it does not mean all are simulated separately, used in every task or merged into identical permissions. The finer computational decomposition is independently proposed in MICRO_ROLES.md, so it is not limited to these professions.','',
        '| Prior function | Primary module | Design interpretation |','| --- | --- | --- |']
    for m in MODULES:
        for id in m['source_roles']:
            r=role_by[id]
            row=dict(role_id=id,title=r['title'],module_id=m['id'],module_name=m['name'],prior_scope=r['condition'],
                prior_evidence=f'Plan/HealthcareRoles/roles/{id}.md',status='PROPOSED_PRIMARY_MAPPING_NOT_VERIFIED_BENCHMARK_ASSIGNMENT')
            coverage.append(row)
            lines.append(f'| [{id} {r["title"]}](../Plan/HealthcareRoles/roles/{id}.md) | [{m["id"]} {m["name"]}](MODULE_CATALOG.md#{m["id"].lower()}) | {m["retained_boundary"]} |')
    write('ROLE_COVERAGE.md','\n'.join(lines));dump('data/role_coverage.json',coverage)
    summary=dict(date='2026-10-18',organizational_modules=29,micro_responsibilities=66,micro_families=dict(Counter(r['domain'] for r in ROLES)),
        service_contracts=20,memory_layers=10,prior_role_mappings=97,composition_variants=3,
        supplied_environment_is_authoritative=True,separate_hospital_world_in_scope=False,
        patient_derived_cross_patient_learning=False,actual_tool_mapping_completed=False,runtime_implemented=False,
        patient_isolation_enforced_or_tested=False,benchmark_or_clinical_performance_verified=False,baseline_hashes_unchanged=True)
    dump('verification/build_receipt.json',summary);print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
