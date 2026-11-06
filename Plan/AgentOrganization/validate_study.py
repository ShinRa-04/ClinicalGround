"""Check design-study coverage/provenance/links; never evaluate clinical truth or runtime benefit."""
import csv
import hashlib
import itertools
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote

sys.dont_write_bytecode=True
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[1]


def load(name):return json.loads((BASE/name).read_text(encoding='utf-8'))


def main():
    baseline=load('baseline.json')
    for f in baseline['files']:
        assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256'],f['path']
    prior=json.loads((ROOT/'Plan/HealthcareRoles/data/roles.json').read_text(encoding='utf-8'))
    role_ids={r['id'] for r in prior}
    roles=load('data/role_analysis.json');packages=load('data/work_packages.json');decisions=load('data/decisions.json')
    authorities=load('data/authority_implications.json');scenarios=load('data/stress_cases.json');sources=load('sources.json')
    assert len(roles)==len({r['id'] for r in roles})==97 and {r['id'] for r in roles}==role_ids
    assert len(packages)==len({p['id'] for p in packages})==23
    package_map={p['id']:p for p in packages}
    assigned=[r for p in packages for r in p['roles']]
    assert len(assigned)==len(set(assigned))==97 and set(assigned)==role_ids
    for r in roles:
        assert r['id'] in package_map[r['package']]['roles']
        assert all(r[k] for k in ['key_question','distinction','counterexample','conclusion','merge_condition','retained_package_boundary','split_trigger','original_scope','original_evidence_limit'])
        assert r['actual_task_assignment_verified'] is False
        assert r['status']=='PROPOSED_DESIGN_INFERENCE_NOT_RUNTIME_VALIDATED'
        assert (ROOT/r['evidence_role']).exists()
        assert (BASE/'roles'/f'{r["id"]}.md').exists()
    assert len(list((BASE/'roles').glob('*.md')))==97
    assert len({r['key_question'] for r in roles})==97
    assert len(decisions)==16 and {d['id'] for d in decisions}=={f'AD{i:02}' for i in range(1,17)}
    source_ids={s['id'] for s in sources}
    assert len(sources)==len(source_ids)==11
    for d in decisions:
        assert all(d[k] for k in ['question','conclusion','rationale','alternatives','evidence','uncertainty','reconsider_if'])
        assert set(d['evidence'])<=source_ids|{'prior-reference'}
        assert d['status']=='PROVISIONAL_DESIGN_JUDGMENT_NOT_RUNTIME_VALIDATED'
    assert {a['id'] for a in authorities}=={f'D{i:02}' for i in range(1,35)} and len(authorities)==34
    assert len(scenarios)==20 and len({s['id'] for s in scenarios})==20
    assert all(set(s['roles'])<=role_ids and s['status']=='PROPOSED_NOT_EXECUTED' for s in scenarios)
    for name,expected in [('data/pair_screen.csv',4656),('data/package_dependencies.csv',None)]:
        with (BASE/name).open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
        if expected:
            assert len(rows)==expected
            assert {(r['role_a'],r['role_b']) for r in rows}==set(itertools.combinations(sorted(role_ids),2))
            assert all(r['method']=='mechanical_design_screen_not_individual_factual_review' for r in rows)
        else:
            assert sum(int(r['modeled_edge_count']) for r in rows)==219
            edges=[e for r in rows for e in r['edge_ids'].split()]
            assert len(edges)==len(set(edges))==219
            assert all(r['sender'] in package_map and r['receiver'] in package_map for r in rows)
    flows=load('data/handoff_implications.json')
    assert len(flows)==46 and {f['id'] for f in flows}=={f'F{i:02}' for i in range(1,47)}
    examples=load('data/considered_merge_examples.json')
    assert len(examples)==20 and all(x['a'] in role_ids and x['b'] in role_ids and x['reason'] for x in examples)
    # Local links and explicit anchors are checked in the new study and linked baseline documents.
    links=0;anchors=0
    def slugs(text):
        headings=set()
        for title in re.findall(r'^#+\s+(.+)$',text,re.M):
            clean=re.sub(r'[^\w\- ]','',title.strip().lower());headings.add(re.sub(r'\s+','-',clean))
        return headings|set(re.findall(r'<a\s+id="([^"]+)"',text))
    for file in BASE.rglob('*.md'):
        text=file.read_text(encoding='utf-8')
        for raw in re.findall(r'\]\(([^)]+)\)',text):
            if re.match(r'https?://',raw):continue
            target,separator,anchor=unquote(raw).partition('#')
            p=(file.parent/target).resolve() if target else file.resolve()
            assert p.exists(),(file.relative_to(BASE),raw)
            links+=1
            if separator and p.suffix=='.md':
                assert anchor in slugs(p.read_text(encoding='utf-8')),(file.relative_to(BASE),raw)
                anchors+=1
    graph_files=sorted((BASE/'graphs').glob('*.svg'))
    assert len(graph_files)==3
    for file in graph_files:
        svg=ET.parse(file).getroot();assert svg.tag.endswith('svg') and svg.get('viewBox')
        assert (file.with_suffix('.dot')).exists()
        for a in svg.iter('{http://www.w3.org/2000/svg}a'):
            href=a.get('{http://www.w3.org/1999/xlink}href')
            if href:
                path,_,anchor=href.partition('#');p=(file.parent/path).resolve()
                assert p.exists() and anchor in slugs(p.read_text(encoding='utf-8'))
    render=load('data/render_receipt.json');assert render['graphs']==3 and all(not x['warnings'] for x in render['results'])
    questions=(BASE/'QUESTIONS.md').read_text(encoding='utf-8')
    assert set(re.findall(r'\| (Q\d{2}) \|',questions))=={f'Q{i:02}' for i in range(1,27)}
    # Important representation boundaries, not tests of healthcare law.
    by={r['id']:r for r in roles}
    assert by['M28']['representation']=='composite_external_functions'
    assert by['U13']['representation']=='protected_review'
    assert by['M24']['representation']=='external_service_actor'
    analysis=(BASE/'ANALYSIS.md').read_text(encoding='utf-8')
    assert 'must not invent an extra real-person approval requirement' in analysis
    assert 'not an optimized partition' in analysis
    build=load('data/build_receipt.json')
    assert build['runtime_implemented'] is build['benchmarks_executed'] is build['architecture_performance_verified'] is False
    result=dict(date='2026-10-18',result='passed',baseline_hashes_unchanged=True,roles=97,packages=23,design_decisions=16,
        authority_implications=34,stress_cases_proposed_not_run=20,mechanically_screened_pairs=4656,authored_pair_examples=20,
        cross_cutting_questions=26,inherited_dependency_edges_accounted_for=219,inherited_handoffs_accounted_for=46,
        source_entries=11,rendered_diagrams=3,local_markdown_links_checked=links,markdown_anchor_targets_checked=anchors,
        checks='Coverage, preserved baseline hashes, explicit hypothesis status, record consistency, link/anchor validity and SVG structure.',
        clinical_or_institutional_validity_verified=False,task_assignments_verified=False,architecture_performance_verified=False)
    (BASE/'data/validation_receipt.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
