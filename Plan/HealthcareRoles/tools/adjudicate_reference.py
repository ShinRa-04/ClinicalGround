"""Materialize authored evidence judgments for all frozen units; not automated fact checking."""
from __future__ import annotations
import copy
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode=True
sys.stdout.reconfigure(encoding='utf-8')
BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parents[1]
sys.path.insert(0,str(BASE/'verification'))
from role_definitions import ROLES
from decision_definitions import DECISIONS,FLOWS
from apply_reviewed_corrections import apply,CORRECTIONS


def read(name):return json.loads((BASE/'verification'/name).read_text(encoding='utf-8'))
def write(name,obj):
    (BASE/'verification'/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')


def main():
    baseline=read('baseline_inventory.json')['items']
    titles=read('supplemental_title_inventory.json')
    role_basis=read('role_evidence_bindings.json');decision_basis=read('decision_evidence_bindings.json');narrative_basis=read('narrative_evidence_bindings.json')
    missing=read('missing_selectors.json')
    if missing:raise ValueError('Unresolved authored evidence selectors; inspect missing_selectors.json')
    roles=copy.deepcopy(ROLES);decisions=copy.deepcopy(DECISIONS);apply(roles,decisions)
    role_by={r['id']:r for r in roles};decision_by={d['id']:d for d in decisions}
    coverage=json.loads((BASE/'data/coverage.json').read_text(encoding='utf-8'))
    for role,basis in role_basis.items():
        assert role in role_by and basis['evidence'],role
    ledger=[]
    for unit in [*baseline,*titles]:
        result={k:v for k,v in unit.items() if k!='adjudication'}
        id=unit['id'];kind=unit['kind'];parent=unit.get('parent');field=unit.get('field')
        result.update(review_completed=True,review_date='2026-10-17',all_contexts_or_local_cases_confirmed=False)
        if kind in ['role_assertion','role_taxonomy']:
            review=role_basis[parent];current=role_by[parent]
            result['evidence']=review['evidence'];result['alternatives']=review['alternatives'];result['complexity_or_unresolved']=review['complexity']
            if field=='title':
                result['verdict']='FUNCTIONAL_TAXONOMY_WITH_SOURCE_CONTEXT'
                result['reason']='This is a functional label, not proof of a single nationally standardized occupation, staffed position or credential. '+review['rationale']
                result['current_text']=current['title']
            elif field=='duties':
                n=int(id.rsplit(':',1)[-1]);exception=review.get('duty_exceptions',{}).get(str(n))
                result['verdict']=exception.split(':',1)[0] if exception else review['duty_verdict']
                result['reason']=(exception+' ' if exception else '')+review['rationale']
                result['current_text']=current[field][n-1]
                result['support_limit']='Support is for the described general/source-example function, not proof of an actual employee\'s permission, observed performance or a nationwide mandatory duty.'
            elif field=='decisions':
                result['verdict']='CONDITIONAL_CAPABILITY_LOCAL_AUTHORITY_NOT_ESTABLISHED'
                result['reason']='Role title alone does not settle license, jurisdiction, product, delegation or actual case power. '+review['rationale']
                result['current_text']=current[field][int(id.rsplit(':',1)[-1])-1]
            elif field=='limits':
                result['verdict']='INTERPRETIVE_BOUNDARY_NOT_EXHAUSTIVE_LEGAL_RULE'
                result['reason']='Retain as a conservative role/domain boundary, not a universal claim that the same person can never hold another qualification or appointment. '+review['rationale']
                result['current_text']=current[field][int(id.rsplit(':',1)[-1])-1]
            elif field=='mission':
                result['verdict']='INTERPRETIVE_FUNCTION_SUMMARY'
                result['reason']='The mission summarizes a modeled function from the evidence and does not create an official occupation or grant authority. '+review['rationale']
                result['current_text']=current[field]
            else:
                result['verdict']='SCOPED_CONDITION_OR_EXPLICIT_UNRESOLVED_LOCAL_FACT'
                result['reason']='Conditions are limitations on use, not assertions that an unidentified local case satisfies them. '+review['complexity']
                result['current_text']=current[field]
            fixes=[c for c in CORRECTIONS if parent in c['targets']]
            result['corrections']=[c['id'] for c in fixes]
        elif kind=='decision_assertion':
            review=decision_basis[parent]
            result['verdict']=review['verdict'] if field in ['rule','cannot'] else ('RECOMMENDED_OR_SCOPED_REVIEW_ROUTE' if field=='review' else 'APPLICABILITY_CONDITION_OR_UNRESOLVED_CASE_FACT')
            result['reason']=review['rationale']
            result['evidence']=review['evidence'];result['alternatives']=review['alternatives'];result['complexity_or_unresolved']=review['complexity']
            result['current_text']=decision_by[parent][field]
            result['corrections']=[c['id'] for c in CORRECTIONS if parent in c['targets']]
        elif kind=='explicit_operational_model':
            result['verdict']='MODEL_NOT_CONFIRMED_EMPIRICAL_OR_INSTITUTIONAL_FACT'
            result['reason']='This is an explicit proposed field, contact, service boundary, condition or workflow-control choice. Sources inform its context but do not establish the exact design as actual or mandatory practice.'
            related=[]
            if parent in role_basis:related=[parent]
            elif parent and parent.startswith('DEP'):
                # Stable DEP numbering follows roles/upstream order; current modeling can narrow an edge.
                edges=[(r['id'],u) for r in roles for u in r['upstream']]
                index=int(parent[3:])-1
                if index<len(edges):
                    receiver,sender=edges[index];related=[receiver,sender]
                    result['current_text']=f'{sender} -> {receiver}: Only when this role and pathway participate; not a universal mandatory predecessor'
            elif parent and parent.startswith('F'):
                flow=next((f for f in FLOWS if f['id']==parent),None)
                if flow:
                    related=[flow['sender'],flow['receiver']]
                    value=flow[field]
                    result['current_text']='; '.join(value) if isinstance(value,list) else value
            result['context_role_reviews']=related
            result['evidence']=[e for r in related if r in role_basis for e in role_basis[r]['evidence']][:10]
            result['evidence_limit']='Contextual support only: not direct passage proof of this model or arrow.'
            result['alternatives']='Local forms, contacts, staffing combinations and procedures may differ; the model does not select an institution-specific one.'
            result['complexity_or_unresolved']='Actual institution procedure, delegation, acknowledgement and closure rules are not supplied and remain unconfirmed.'
            if parent in role_by:
                value=role_by[parent].get(field)
                if isinstance(value,list):result['current_text']=value[int(id.rsplit(':',1)[-1])-1]
                elif isinstance(value,str):result['current_text']=value
                elif field=='primary_contact':
                    contact='C06' if parent=='M28' else unit['text'].split(' <-> ',1)[0]
                    result['current_text']=f'{contact} <-> {parent}: Question/referral/task and available relevant context for: '+role_by[parent]['mission']
            result['corrections']=[c['id'] for c in CORRECTIONS if parent in c['targets'] or (result.get('current_text')!=unit['text'] and any(x in c['targets'] for x in related))]
        else:
            if id not in narrative_basis:raise ValueError('Unreviewed narrative/graph unit: '+id)
            review=narrative_basis[id]
            result.update(verdict=review['verdict'],reason=review['reason'],evidence=review['evidence'])
            if review['verdict']=='COMPOSITE_TABLE_TRACEABLE_TO_ROLE_REVIEWS':
                linked=sorted({r for row in coverage if row['earlier_label'] in unit['text'] for r in row['canonical_ids']})
                result['context_role_reviews']=linked
                result['reason']+=' Matched canonical role reviews: '+', '.join(linked)+'.'
                result['evidence']=[e for r in linked for e in role_basis[r]['evidence']][:20]
            result['alternatives']='Read the cited scope and associated role/decision alternatives; this does not verify an unidentified institution.'
            result['complexity_or_unresolved']='Real local assignments and all unprovided jurisdiction/product/case facts remain unresolved.'
            result['corrections']=[c['id'] for c in CORRECTIONS if parent in c['targets'] or (parent=='commercial-appeals' and c['id']=='FIX09') or (parent=='reporting-examples' and c['id']=='FIX11')]
        if result.get('current_text') is not None:
            result['wording_changed']=result['current_text']!=result['text']
        assert result.get('verdict') and result.get('reason'),id
        ledger.append(result)
    assert len(ledger)==2218
    assert len({x['id'] for x in ledger})==2218
    counts=dict(sorted(Counter(x['verdict'] for x in ledger).items()))
    write('claim_adjudications.json',ledger)
    write('corrections.json',CORRECTIONS)
    receipt=dict(schema='deep-reference-audit/v1',date='2026-10-17',baseline_units=2121,supplemental_title_units=97,
        total_units=2218,reviewed_units=2218,pending_units=0,role_reviews=97,decision_reviews=34,narrative_graph_reviews=143,
        authored_passage_selectors=495,unresolved_selectors=0,verdict_counts=counts,
        corrections=len(CORRECTIONS),changed_role_or_decision_wording=sum(x.get('wording_changed',False) for x in ledger if x['kind']!='explicit_operational_model'),
        changed_model_units=sum(x.get('wording_changed',False) for x in ledger if x['kind']=='explicit_operational_model'),
        coverage_adjudication_complete=True,every_finding_confirmed_true=False,actual_institutional_authority_verified=False,
        evidence_method='Authored source/role/decision judgments with captured paragraph/page locators; code expands and checks coverage, not automatic truth/entailment scoring.',
        limitation='Assertion units can be source-scoped summaries or composite narrative blocks. Models remain models; unknown local facts and listed ambiguities remain unknown. Not independent legal/clinical certification.')
    write('audit_receipt.json',receipt)
    print(json.dumps(receipt,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
