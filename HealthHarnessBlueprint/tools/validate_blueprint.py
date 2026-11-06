"""Check hypothetical specification structure, scope and navigation, not runtime behavior."""
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from urllib.parse import unquote

sys.dont_write_bytecode=True
BASE=Path(__file__).resolve().parents[1];ROOT=BASE.parent


def read(path):return json.loads((BASE/path).read_text(encoding='utf-8'))


def anchors(text):
    result=set(re.findall(r'<a\s+id="([^"]+)"',text))
    for heading in re.findall(r'^#+\s+(.+)$',text,re.M):
        value=re.sub(r'[^\w\- ]','',heading.lower().strip());result.add(re.sub(r'\s+','-',value))
    return result


def main():
    for record in read('baseline.json')['files']:
        assert hashlib.sha256((ROOT/record['path']).read_bytes()).hexdigest()==record['sha256'],record['path']
    modules=read('data/modules.json');micro=read('data/micro_roles.json');services=read('data/services.json')
    memories=read('data/memory_layers.json');coverage=read('data/role_coverage.json');policy=read('data/patient_isolation_policy.json')
    assert len(modules)==len({x['id'] for x in modules})==29
    assert len(micro)==len({x['id'] for x in micro})==66
    assert Counter(r['domain'] for r in micro)==dict(PA=18,UM=18,CM=20,SH=10)
    for r in micro:
        assert all(r[k] for k in ['inputs','output','decision_scope','boundary','completion_check','execution_form','activation'])
        assert 'status' not in r
        assert r['status_label'] == ('executing_worker' if r['id'] in {'CM-04','SH-10'} else 'prompt_contract')
        assert isinstance(r['model_visible'],bool)
        assert r['model_visible'] == (r['id'] not in {'SH-02','SH-04','SH-06','SH-07','SH-08','SH-09'})
        assert isinstance(r['hospital_roles'],list)
        assert r['authority'] and (len(r['authority'])<=160 or r['id']=='CM-04')
        assert r['approach'] and len(r['approach'])<=200
        assert 'no patient-derived cross-patient learning' in r['memory_policy']
    service_ids={s['id'] for s in services};assert len(service_ids)==len(services)==20
    assert all(set(m['service_ids'])<=service_ids for m in modules)
    assert len(memories)==10 and all(m['implemented'] is False for m in memories)
    assert all(s['actual_tool_mapping']=='NOT_YET_PERFORMED' and s['implemented'] is False for s in services)
    original=json.loads((ROOT/'Plan/HealthcareRoles/data/roles.json').read_text(encoding='utf-8'))
    assert all(set(r['hospital_roles']) <= {h['id'] for h in original} for r in micro)
    assert all(bool(r['hospital_roles']) == (r['domain']!='SH') for r in micro)
    assert len(coverage)==len({r['role_id'] for r in coverage})==97 and {r['role_id'] for r in coverage}=={r['id'] for r in original}
    assert all((ROOT/r['prior_evidence']).is_file() for r in coverage)
    assert len(read('data/composition_variants.json'))==3
    assert policy['automatic_patient_derived_shared_learning'] is policy['cross_patient_retrieval'] is policy['actual_isolation_enforced_or_tested'] is False
    receipt=read('verification/build_receipt.json')
    assert receipt['supplied_environment_is_authoritative'] is True
    assert receipt['separate_hospital_world_in_scope'] is receipt['runtime_implemented'] is receipt['actual_tool_mapping_completed'] is False
    assert receipt['patient_isolation_enforced_or_tested'] is receipt['benchmark_or_clinical_performance_verified'] is False
    # Scope sentinels enforce the user's corrections in the published proposal.
    composition=(BASE/'COMPOSITION.md').read_text(encoding='utf-8')
    isolation=(BASE/'PATIENT_ISOLATION.md').read_text(encoding='utf-8')
    vision=(BASE/'VISION_AND_SCOPE.md').read_text(encoding='utf-8')
    assert '66 functional contracts' in composition and 'Single combined agent' in composition
    assert 'job definitions and approved general knowledge' in isolation
    assert 'a separate patient, physiology or hospital-world simulator' in vision
    assert len(set(re.findall(r'\| (V\d{2}) \|',(BASE/'EVALUATION_AND_FAILURES.md').read_text(encoding='utf-8'))))==20
    assert len(set(re.findall(r'\| (D\d{2}) \|',(BASE/'DECISIONS_AND_OPEN_QUESTIONS.md').read_text(encoding='utf-8'))))==18
    paths=[p for p in BASE.rglob('*.md') if '_cache' not in p.relative_to(BASE).parts]
    links=0;anchor_count=0
    for file in paths:
        for raw in re.findall(r'\]\(([^)]+)\)',file.read_text(encoding='utf-8')):
            if re.match(r'https?://',raw):continue
            target,separator,anchor=unquote(raw).partition('#');path=(file.parent/target).resolve() if target else file.resolve()
            assert path.exists(),(file.name,raw);links+=1
            if separator and anchor and path.suffix=='.md':
                assert anchor in anchors(path.read_text(encoding='utf-8')),(file.name,raw);anchor_count+=1
    svgs=list((BASE/'graphs').glob('*.svg'));assert len(svgs)==5
    for file in svgs:
        svg=ET.parse(file).getroot();assert svg.tag.endswith('svg') and svg.get('viewBox')
        assert file.with_suffix('.dot').exists()
        for a in svg.iter('{http://www.w3.org/2000/svg}a'):
            href=a.get('{http://www.w3.org/1999/xlink}href')
            if href:
                path,_,anchor=href.partition('#');target=(file.parent/path).resolve()
                assert target.exists() and (not anchor or anchor in anchors(target.read_text(encoding='utf-8')))
    assert all(not r['warnings'] for r in read('verification/render_receipt.json')['results'])
    result=dict(date='2026-10-18',result='passed',organizational_modules=29,micro_role_contracts=66,domain_counts=dict(Counter(r['domain'] for r in micro)),
        service_contracts=20,memory_layers=10,prior_function_mappings=97,composition_variants=3,design_decisions=18,proposed_acceptance_cases=20,
        diagrams=5,markdown_documents=len(paths),local_links_checked=links,local_anchors_checked=anchor_count,baseline_hashes_unchanged=True,
        checks='Structural coverage, user-scope/isolation requirement labels, links, anchors and SVG integrity; not implementation enforcement.',
        runtime_implemented=False,actual_tool_mapping_completed=False,patient_isolation_enforced_or_tested=False,benchmark_or_clinical_performance_verified=False)
    (BASE/'verification/validation_receipt.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
