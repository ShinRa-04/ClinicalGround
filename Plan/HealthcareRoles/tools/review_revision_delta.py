"""Reconcile revised narrative/graph units to explicit authored review routes.

Exact unchanged text reuses a frozen judgment. Changed units require a declared
review below; matching a prefix only identifies that judgment, never judges truth.
"""
import hashlib
import json
import re
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parents[1]


def load(name):return json.loads((BASE/'verification'/name).read_text(encoding='utf-8'))


# Authored disposition of revised paragraphs/labels; evidence refers to existing reviewed bundles.
REVISIONS=[
 ('**Evidence status:** this framework','AUTHORITY','DOCUMENTATION_SCOPE',[],[],'Coverage metadata, not expanded legal authority.'),
 ('The pathway need not be strictly sequential.','AUTHORITY','SUPPORTED_CONDITIONAL_WITH_ALTERNATIVES',[],['D16'],'V19 permits concurrent eligible urgent review; R17 limits plan/process scope.'),
 ('R32 describes associate-director direction','AUTHORITY','SUPPORTED_EXAMPLE_WITH_UNRESOLVED_SIGNOFF',['G04','G05','U01','U08'],['D11'],'Reporting and collaboration are distinct; R13 signoff remains unresolved.'),
 ('Applicable Part 2 records add further distinctions','AUTHORITY','SUPPORTED_PRIVACY_COMPLEXITY',[],['D27'],'V15 additional consent distinctions; no blanket permission is inferred.'),
 ('**Alternative and ambiguity:**','WORKFLOWS','SCOPED_ALTERNATIVES_AND_UNRESOLVED_FACTS',['U08'],['D11','D12','D16'],'Nonclinical limited decisions, appeals retained by plan, urgent concurrency and route check are conditional.'),
 ('**Hospice nuance:**','WORKFLOWS','SUPPORTED_DATED_DISTINCTIONS',['M28'],['D33'],'Official 2025 edition establishes distinct functions; current-2026 update/actual assignments remain unconfirmed.'),
 ('**Evidence caution:**','WORKFLOW_PEOPLE','DOCUMENTATION_SCOPE',[],[],'Evidence-review metadata; no new clinical claim.'),
 ('Noyes describes a specialist','WORKFLOW_PEOPLE','SUPPORTED_ORGANIZATION_EXAMPLES',['O01','O02'],[],'Accessible Noyes/Michigan replace expired Mayo dependence; no national staffing inference.'),
 ('R12 is an earlier captured excerpt','WORKFLOW_PEOPLE','SOURCE_LIMIT_AND_UNRESOLVED_PROGRAM_SCOPE',['U01','U04','U08'],['D11'],'Earlier excerpt and fresh failure are distinct; limited nonclinical activity and retained appeals are scoped.'),
 ('The cited care-program examples','WORKFLOW_PEOPLE','SUPPORTED_DIFFERENT_PROGRAM_EXAMPLES',['M01','M02','G04'],['D21'],'Program variation is supported, national prevalence is not.'),
 ('**Evidence caution:**','MEDICAL_WORKFLOW','DOCUMENTATION_SCOPE',[],[],'Evidence metadata; illustrations/hypotheses and unknown local facts retain that status.'),
 ('REVIEWED SCOPED SUMMARY:','authority-domains','DOCUMENTATION_SCOPE',[],[],'Review legend, no new authority.'),
 ('REVIEWED SCOPED SUMMARY:','ma-appeals','DOCUMENTATION_SCOPE',[],[],'Review legend; route and eligibility remain conditional.'),
 ('REVIEWED SCOPED SUMMARY:','commercial-appeals','DOCUMENTATION_SCOPE',[],[],'Review legend; route and eligibility remain conditional.'),
 ('Identify product / decision category','ma-appeals','SUPPORTED_ROUTE_QUALIFICATION',[],['D12','D13'],'A02(a) contains the applicable integrated-plan route distinction; detailed integrated rules were not audited.'),
 ('If applicable: identify integrated-plan process','ma-appeals','EXPLICIT_UNVERIFIED_ROUTE_LIMIT',[],['D12'],'Statement of unverified detail and required route check, not a claim to verify the integrated process.'),
 ('standard MA route applies','ma-appeals','CONDITIONAL_GRAPH_ROUTE_MODEL',[],['D12'],'Conditional routing illustration, not automatic eligibility.'),
 ('different applicable route','ma-appeals','CONDITIONAL_GRAPH_ROUTE_MODEL',[],['D12'],'Separate route must be identified; no specific unverified procedure is invented.'),
 ('Identify applicable plan / issue / process','commercial-appeals','SUPPORTED_APPLICABILITY_CONDITION',[],['D16'],'R17 scope/eligibility condition; does not certify every plan or denial.'),
 ('identified applicable process','commercial-appeals','CONDITIONAL_GRAPH_ROUTE_MODEL',[],['D16'],'Applicability gate is a modeling expression of the reviewed scope limits.'),
 ('eligible urgent review may be requested','commercial-appeals','SUPPORTED_CONCURRENT_ALTERNATIVE',[],['D16'],'V19 supports same-time urgent requests under eligible circumstances.'),
 ('described direction','reporting-examples','SUPPORTED_ORGANIZATION_EXAMPLE',['G04','G05'],[],'R32 describes associate-director direction of supervisors.'),
 ('collaborates in oversight','reporting-examples','CORRECTED_RELATIONSHIP_EXAMPLE',['G04','G05'],[],'R32 collaboration is shown dashed, not an invented direct reporting relation.'),
]


def main(quiet=False):
    old=load('claim_adjudications.json')
    original={(u.get('parent'),u['text']):u for u in old if u['kind'] in ['narrative_block','authored_graph_label']}
    roles=load('role_evidence_bindings.json');decisions=load('decision_evidence_bindings.json')
    coverage=json.loads((BASE/'data/coverage.json').read_text(encoding='utf-8'))
    current=[]
    for file in [BASE/'AUTHORITY.md',BASE/'WORKFLOWS.md',ROOT/'Plan/WORKFLOW_PEOPLE.md',ROOT/'Plan/MEDICAL_WORKFLOW.md']:
        for paragraph in re.split(r'\n\s*\n',file.read_text(encoding='utf-8')):
            text=paragraph.strip()
            if not text or text.startswith(('#','```')):continue
            current.append(dict(parent=file.stem,text=text,kind='current_narrative_block',origin=file.relative_to(ROOT).as_posix()))
    for name in ['authority-domains','ma-appeals','commercial-appeals','reporting-examples']:
        file=BASE/'graphs'/f'{name}.dot'
        for line in file.read_text(encoding='utf-8').splitlines():
            match=re.search(r'label=("(?:[^"\\]|\\.)*")',line)
            if match:current.append(dict(parent=name,text=json.loads(match[1]),kind='current_graph_label',origin=file.relative_to(ROOT).as_posix()))
    missing=[];changed=0
    for i,u in enumerate(current,1):
        u['id']=f'CURRENT:{i:03}';u['sha256']=hashlib.sha256(u['text'].encode()).hexdigest()
        previous=original.get((u['parent'],u['text']))
        if previous:
            u.update(review_route='Unchanged frozen unit',baseline_id=previous['id'],verdict=previous['verdict'],reason=previous['reason'],evidence=previous['evidence'])
            continue
        changed+=1
        if u['parent']=='WORKFLOW_PEOPLE' and u['text'].startswith('|'):
            related=sorted({r for row in coverage if row['earlier_label'] in u['text'] for r in row['canonical_ids']})
            u.update(review_route='Revised composite table; reviewed canonical role mapping',verdict='COMPOSITE_MODEL_AND_SCOPED_ROLE_CONTEXT',
                reason='Corrected source references and qualified title/staffing examples. Each role has its own verdict; this does not certify all table cells as empirical facts.',
                context_role_reviews=related,evidence=[e for r in related for e in roles[r]['evidence']])
            if not related:missing.append(u)
            continue
        review=next((r for r in REVISIONS if r[1]==u['parent'] and u['text'].startswith(r[0])),None)
        if review:
            prefix,parent,verdict,rs,ds,reason=review
            evidence=[e for r in rs for e in roles[r]['evidence']]+[e for d in ds for e in decisions[d]['evidence']]
            u.update(review_route='Explicit authored revision disposition',verdict=verdict,reason=reason,context_role_reviews=rs,context_decision_reviews=ds,evidence=evidence)
        else:missing.append(u)
    if missing:
        print(json.dumps(dict(unassigned_revisions=missing),ensure_ascii=False,indent=2));raise SystemExit(1)
    paths=sorted({u['origin'] for u in current})
    artifacts=[dict(path=p,normalized_utf8_sha256=hashlib.sha256((ROOT/p).read_text(encoding='utf-8').encode()).hexdigest()) for p in paths]
    result=dict(date='2026-10-17',current_units=len(current),unchanged_units=len(current)-changed,revised_or_added_units=changed,pending_units=0,artifacts=artifacts,
        method='Explicit authored revision dispositions and links to existing reviewed source bundles; no automatic entailment judgment.',
        all_contexts_confirmed=False,items=current)
    (BASE/'verification/current_revision_review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    if not quiet:print(json.dumps({k:v for k,v in result.items() if k not in ['items','artifacts']},indent=2))


if __name__=='__main__':main()
