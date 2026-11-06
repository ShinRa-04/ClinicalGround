"""Freeze assertion units and explicit models without claiming automated truth verification."""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parents[1]
OUT=BASE/'verification'


def load(name):return json.loads((BASE/'data'/name).read_text(encoding='utf-8'))


def main():
    OUT.mkdir(exist_ok=True)
    target=OUT/'baseline_inventory.json'
    if target.exists():
        data=json.loads(target.read_text(encoding='utf-8'));print(json.dumps(dict(existing_inventory=True,assertion_units=len(data['items']),counts=data['counts']),indent=2));return
    items=[];covered_files=[]
    def add(id,kind,text,origin,sources,field=None,parent=None):
        items.append(dict(id=id,kind=kind,text=text,origin=origin,sources=sources,field=field,parent=parent,
            original_sha256=hashlib.sha256(text.encode()).hexdigest(),adjudication='pending'))
    for r in load('roles.json'):
        for field in ['mission','duties','decisions','limits','inputs','outputs','escalation','condition']:
            values=r[field] if isinstance(r[field],list) else [r[field]]
            for n,text in enumerate(values,1):add(f"ROLE:{r['id']}:{field}:{n:02}",'role_assertion' if field not in ['inputs','outputs','escalation'] else 'explicit_operational_model',text,'roles/'+r['id']+'.md',r['sources'],field,r['id'])
    for d in load('decisions.json'):
        for field in ['rule','cannot','review','condition']:
            add(f"DECISION:{d['id']}:{field}",'decision_assertion',d[field],'DECISIONS.md',d['sources'],field,d['id'])
    for f in load('information_flows.json'):
        for field in ['artifact','fields','acknowledgement','failure','condition']:
            text='; '.join(f[field]) if isinstance(f[field],list) else f[field]
            add(f"FLOW:{f['id']}:{field}",'explicit_operational_model',text,'INFORMATION_FLOWS.md',f['sources'],field,f['id'])
    for e in load('relations.json'):
        if e['type']!='coordination_dependency':continue
        add('EDGE:'+e['id'],'explicit_operational_model',f"{e['sender']} -> {e['receiver']}: {e['condition']}",'DEPENDENCIES.md',e['sources'],'relationship',e['id'])
    for s in load('service_interfaces.json'):
        add('INTERFACE:'+s['id'],'explicit_operational_model',f"{s['primary_contact']} <-> {s['role']}: {s['request']}",'SERVICE_INTERFACES.md',s['sources'],'primary_contact',s['role'])
    # Generated prose is covered by authored canonical units. Narrative blocks are separately inventoried.
    files=[BASE/'AUTHORITY.md',BASE/'WORKFLOWS.md',ROOT/'Plan/WORKFLOW_PEOPLE.md',ROOT/'Plan/MEDICAL_WORKFLOW.md']
    for file in files:
        text=file.read_text(encoding='utf-8');heading='';number=0;code=False
        for paragraph in re.split(r'\n\s*\n',text):
            paragraph=paragraph.strip()
            if not paragraph:continue
            if paragraph.startswith('#'):
                heading=paragraph.splitlines()[0].lstrip('# ');continue
            if paragraph.startswith('```'):continue
            number+=1
            refs=sorted(set(re.findall(r'\b(?:R|A|B)\d{2}\b',paragraph)))
            relative=file.relative_to(ROOT).as_posix()
            add(f'NARRATIVE:{file.stem}:{number:03}','narrative_block',paragraph,relative,refs,heading,file.stem)
        covered_files.append(dict(path=file.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(text.encode()).hexdigest()))
    # DOT labels for the authored authority/reporting diagrams are not generated from the role fields.
    for graph in ['authority-domains','ma-appeals','commercial-appeals','reporting-examples']:
        text=(BASE/'graphs'/f'{graph}.dot').read_text(encoding='utf-8')
        number=0
        for line in text.splitlines():
            if 'label=' not in line:continue
            number+=1
            match=re.search(r'label=("(?:[^"\\]|\\.)*")',line)
            if not match:continue
            label=json.loads(match[1]);ref=sorted(set(re.findall(r'\b(?:R|A|B)\d{2}\b',label)))
            add(f'GRAPH:{graph}:{number:02}','authored_graph_label',label,'graphs/'+graph+'.dot',ref,'label',graph)
    counts={k:sum(x['kind']==k for x in items) for k in sorted({x['kind'] for x in items})}
    data=dict(schema='role-evidence-inventory/v1',date='2026-10-17',purpose='Frozen assertion/model units; no unit is declared true automatically. Generated repetitions map to canonical fields.',items=items,counts=counts,narrative_baselines=covered_files)
    target.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(assertion_units=len(items),counts=counts),indent=2))


if __name__=='__main__':main()
