"""Resolve authored evidence selectors to captured source locations; never auto-judge entailment."""
from __future__ import annotations
import hashlib
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode=True
sys.stdout.reconfigure(encoding='utf-8')
BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parents[1]
sys.path.insert(0,str(BASE/'verification'))
from reviewed_role_basis import REVIEWS
from reviewed_decision_basis import REVIEWS as DECISION_REVIEWS
from reviewed_narrative_basis import REVIEWS as NARRATIVE_REVIEWS

CACHE=ROOT/'Runner/.cache/role-verification'


def folded(text):
    return re.sub(r'[^a-z0-9]','',text.casefold())


def resolve(source,anchor):
    file=CACHE/(source+'.json')
    if not file.exists():return None,'source not collected'
    record=json.loads(file.read_text(encoding='utf-8'))
    if not record.get('paragraphs'):return None,record.get('error',record.get('retrieval_status'))
    paragraphs=record['paragraphs'];needle=folded(anchor)
    hits=[i for i,p in enumerate(paragraphs) if needle in folded(p['text'])]
    if not hits:return None,'authored passage selector not found in captured text'
    locations=[]
    for i in hits[:4]:
        p=paragraphs[i]
        before=1 if record.get('format')=='tool_lines' else 0
        after=3 if record.get('format')=='tool_lines' or len(p['text'])<90 else 0
        context=paragraphs[max(0,i-before):min(len(paragraphs),i+after+1)]
        locations.append(dict(locator=p['locator'],context_locators=[x['locator'] for x in context],
            paragraph_sha256=hashlib.sha256(p['text'].encode('utf-8')).hexdigest()))
    return dict(source=source,url=record['url'],source_text_sha256=record.get('text_sha256'),
        retrieval_status=record['retrieval_status'],selector=anchor,locations=locations,
        selection_limit='Selector resolution only; authored rationale provides the evidence judgment. Match presence is not automatic verification.'),None


def main():
    bound={};missing=[]
    for role,review in REVIEWS.items():
        evidence=[]
        for source,anchor in review['evidence']:
            result,error=resolve(source,anchor)
            if result:evidence.append(result)
            else:missing.append(dict(role=role,source=source,anchor=anchor,error=error))
        bound[role]=dict(review,evidence=evidence)
    (BASE/'verification/role_evidence_bindings.json').write_text(json.dumps(bound,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    decision_bound={}
    for id,review in DECISION_REVIEWS.items():
        evidence=[]
        for source,anchor in review['evidence']:
            result,error=resolve(source,anchor)
            if result:evidence.append(result)
            else:missing.append(dict(decision=id,source=source,anchor=anchor,error=error))
        decision_bound[id]=dict(review,evidence=evidence)
    (BASE/'verification/decision_evidence_bindings.json').write_text(json.dumps(decision_bound,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    narrative_bound={}
    for id,review in NARRATIVE_REVIEWS.items():
        evidence=[]
        for source,anchor in review['evidence']:
            result,error=resolve(source,anchor)
            if result:evidence.append(result)
            else:missing.append(dict(narrative=id,source=source,anchor=anchor,error=error))
        narrative_bound[id]=dict(review,evidence=evidence)
    (BASE/'verification/narrative_evidence_bindings.json').write_text(json.dumps(narrative_bound,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    (BASE/'verification/missing_selectors.json').write_text(json.dumps(missing,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(role_reviews=len(bound),decision_reviews=len(decision_bound),narrative_graph_reviews=len(narrative_bound),evidence_selectors=sum(len(r['evidence']) for r in [*REVIEWS.values(),*DECISION_REVIEWS.values(),*NARRATIVE_REVIEWS.values()]),resolved=sum(len(r['evidence']) for r in [*bound.values(),*decision_bound.values(),*narrative_bound.values()]),missing=missing),ensure_ascii=False,indent=2))


if __name__=='__main__':main()
