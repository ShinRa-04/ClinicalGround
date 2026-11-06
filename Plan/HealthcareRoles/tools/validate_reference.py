"""Check reference integrity and graph semantics; not clinical validation."""
from __future__ import annotations
import json
import hashlib
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote

sys.dont_write_bytecode=True
BASE=Path(__file__).resolve().parents[1]


def load(name):
    return json.loads((BASE/'data'/name).read_text(encoding='utf-8'))


def main():
    roles=load('roles.json'); sources=load('sources.json'); decisions=load('decisions.json')
    flows=load('information_flows.json'); interfaces=load('service_interfaces.json')
    relations=load('relations.json'); coverage=load('coverage.json'); graphs=load('graph_manifest.json')
    role_ids={x['id'] for x in roles}; source_ids={x['id'] for x in sources}
    assert len(role_ids)==len(roles)==97
    assert len(source_ids)==len(sources)==95
    assert len({s['url'] for s in sources})==94
    assert all(r['field_evidence'] and r['local_authority_confirmed'] is False for r in roles)
    assert all('REVIEWED' in r['claim_audit_status'] and r['evidence_review_basis']['evidence'] for r in roles)
    assert all(r['evidence_review_basis']['alternatives'] and r['evidence_review_basis']['complexity'] for r in roles)
    assert all('SYNTHESIZED MODEL' in f['evidence_status'] for f in flows)
    assert all('SYNTHESIZED MODEL' in s['evidence_status'] for s in interfaces)
    assert all('evidence_status' in d for d in decisions)
    review=load('evidence_review.json')
    assert review['defined_inventory_adjudication_completed'] is True
    assert review['every_finding_confirmed_true'] is False
    assert {d['id'] for d in review['checked_core_rules']}=={'D12','D13','D22','D23'}
    assert len(decisions)==34 and len(flows)==46 and len(interfaces)==97
    assert len(coverage)==86
    assert {x for c in coverage for x in c['canonical_ids']}==role_ids-{'J01','J02','J03'}
    assert {s['role'] for s in interfaces}==role_ids
    assert all(s['role']!=s['primary_contact'] for s in interfaces)
    for collection in [roles,decisions,flows,interfaces,relations]:
        for record in collection:
            assert record['sources'] and set(record['sources'])<=source_ids, record['id']
    assert all(not x['hard_gate'] for x in relations)
    assert all(x['type'] in ['coordination_dependency','information_handoff'] for x in relations)
    assert all(x['sender'] in role_ids and x['receiver'] in role_ids for x in relations)
    assert all((BASE/'roles'/f'{id}.md').is_file() for id in role_ids)
    assert len(list((BASE/'roles').glob('*.md')))==97
    local_links=0
    for document in BASE.rglob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)',document.read_text(encoding='utf-8')):
            if re.match(r'https?://',target):
                continue
            target=unquote(target.split('#',1)[0])
            if not target:
                continue
            assert (document.parent/target).resolve().exists(), (document.relative_to(BASE),target)
            local_links+=1
    svg_nodes=0
    for graph in graphs:
        assert (BASE/'graphs'/f"{graph['name']}.dot").is_file()
        root=ET.parse(BASE/'graphs'/f"{graph['name']}.svg").getroot()
        assert root.tag.endswith('svg')
        assert 'viewBox' in root.attrib
        for g in root.iter('{http://www.w3.org/2000/svg}g'):
            if g.get('class')=='node':
                svg_nodes+=1
        for a in root.iter('{http://www.w3.org/2000/svg}a'):
            href=a.get('{http://www.w3.org/1999/xlink}href','')
            if href:
                assert href.startswith('../index.html#') and href.split('#')[1] in role_ids
    assert len(graphs)==112
    assert all(not r['warnings'] for r in load('render_receipt.json')['results'])
    # Semantic sentinels: no dependency is presented as an override, and review routes stay distinct.
    d={x['id']:x for x in decisions}
    assert 'OR' in d['D12']['rule'] and 'physician' in d['D13']['rule']
    assert 'not involved' in d['D13']['rule']
    assert 'A02' in d['D12']['sources'] and 'A03' in d['D13']['sources']
    assert 'A12' in d['D16']['sources'] and 'A04' in d['D15']['sources']
    assert '2025' in d['D33']['rule'] and '2026' in d['D33']['condition']
    assert 'V19' in d['D16']['sources'] and 'concurrently' in d['D16']['condition']
    assert 'U01' in d['D11']['actors'] and 'nonclinical' in d['D11']['rule']
    assert 'V15' in d['D27']['sources']
    hospice=next(x for x in roles if x['id']=='M28')
    assert hospice['upstream']==['P01','C01','C06']
    assert next(x for x in interfaces if x['role']=='M28')['primary_contact']=='C06'
    ledger=json.loads((BASE/'verification/claim_adjudications.json').read_text(encoding='utf-8'))
    baseline=json.loads((BASE/'verification/baseline_inventory.json').read_text(encoding='utf-8'))['items']
    titles=json.loads((BASE/'verification/supplemental_title_inventory.json').read_text(encoding='utf-8'))
    frozen={x['id']:x for x in baseline+titles}
    assert len(frozen)==len(ledger)==2218 and len({x['id'] for x in ledger})==2218
    for unit in ledger:
        assert unit['text']==frozen[unit['id']]['text']
        assert hashlib.sha256(unit['text'].encode()).hexdigest()==unit['original_sha256']
        assert unit['review_completed'] and unit['verdict'] and unit['reason']
        assert unit['all_contexts_or_local_cases_confirmed'] is False
        for e in unit['evidence']:
            assert e['source'] in source_ids and e['locations'] and e['source_text_sha256']
            assert e['retrieval_status']!='failed'
        if unit['kind'] in ['role_assertion','role_taxonomy','decision_assertion']:
            current=next(x for x in (roles if unit['parent'] in role_ids else decisions) if x['id']==unit['parent'])
            value=current[unit['field']]
            if isinstance(value,list):value=value[int(unit['id'].rsplit(':',1)[-1])-1]
            assert unit['current_text']==value,(unit['id'],value)
    audit=json.loads((BASE/'verification/audit_receipt.json').read_text(encoding='utf-8'))
    assert audit['reviewed_units']==2218 and audit['pending_units']==audit['unresolved_selectors']==0
    revisions=json.loads((BASE/'verification/current_revision_review.json').read_text(encoding='utf-8'))
    assert revisions['pending_units']==0 and revisions['current_units']==len(revisions['items'])
    assert len(revisions['artifacts'])==8
    for artifact in revisions['artifacts']:
        assert hashlib.sha256((BASE.parents[1]/artifact['path']).read_text(encoding='utf-8').encode()).hexdigest()==artifact['normalized_utf8_sha256'],artifact['path']
    assert all(u['verdict'] and u['reason'] and hashlib.sha256(u['text'].encode()).hexdigest()==u['sha256'] for u in revisions['items'])
    assert all(x['evidence_review_basis']['evidence'] and x['evidence_review_basis']['alternatives'] and x['evidence_review_basis']['complexity'] for x in decisions)
    # Verify semantic changes survive generation (not a test of underlying law).
    reporting=(BASE/'graphs/reporting-examples.dot').read_text(encoding='utf-8')
    assert 'associate -> supervisors' in reporting and 'managers -> supervisors [style=dashed' in reporting
    assert 'concurrently' in (BASE/'graphs/commercial-appeals.dot').read_text(encoding='utf-8')
    assert 'route -> integrated' in (BASE/'graphs/ma-appeals.dot').read_text(encoding='utf-8')
    result=dict(result='passed',roles=97,source_entries=95,distinct_source_urls=94,earlier_rows=86,decision_questions=34,
        explicit_handoffs=46,service_interfaces=97,dependency_edges=219,rendered_graphs=112,
        checked_local_markdown_links=local_links,checked_svg_node_instances=svg_nodes,
        consistency_checks='Frozen inventory/hash coverage, recorded verdicts/passages, applied corrections, labels, links, SVGs and semantic sentinels; not automatic factual entailment verification.',
        defined_inventory_adjudication_completed=True,reviewed_assertion_units=2218,pending_assertion_units=0,
        current_narrative_graph_units_reconciled=revisions['current_units'],revised_added_units_reviewed=revisions['revised_or_added_units'],
        every_finding_confirmed_true=False,actual_institutional_authority_verified=False,
        limitations='Reference consistency and rendering only; no institution-specific approval, interviews, clinical validation or live clinical workflow')
    (BASE/'data/validation_receipt.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__': main()
