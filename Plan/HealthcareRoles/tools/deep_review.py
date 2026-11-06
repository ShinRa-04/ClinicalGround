"""Publish scoped, authored evidence judgments; never infer truth from selector matches."""
from __future__ import annotations
import json
import os
import re
from collections import Counter
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]


def read(name):
    return json.loads((BASE/'verification'/name).read_text(encoding='utf-8'))


def evidence_lines(evidence):
    result=[]
    for e in evidence:
        locations='; '.join(x['locator'] for x in e['locations'])
        result.append(f"- [{e['source']}]({e['url']}) — {locations}; access: {e['retrieval_status']}. Passage anchor: `{e['selector']}`.")
    return result


def relocated(text,origin,destination):
    """Keep links in frozen quotations pointing to their original document context."""
    original=(BASE.parents[1]/origin) if origin.startswith('Plan/') else BASE/origin
    def replace(match):
        target=match.group(1)
        if re.match(r'https?://',target):return match.group(0)
        file,marker,anchor=target.partition('#')
        resolved=(original.parent/file).resolve() if file else original.resolve()
        link=Path(os.path.relpath(resolved,destination.parent)).as_posix()
        return ']('+link+('#'+anchor if marker else '')+')'
    return re.sub(r'\]\(([^)]+)\)',replace,text)


def apply(roles,decisions,sources):
    role_basis=read('role_evidence_bindings.json');decision_basis=read('decision_evidence_bindings.json')
    receipt=read('audit_receipt.json')
    assert receipt['pending_units']==0 and not read('missing_selectors.json')
    for r in roles:
        basis=role_basis[r['id']]
        r['claim_audit_status']='REVIEWED within the frozen assertion inventory: scoped evidence judgments, alternatives and unresolved facts recorded; not universal certification.'
        r['evidence_review_basis']=basis
        r['field_evidence'].update(
            duties=basis['duty_verdict']+': '+basis['rationale']+' Individual exceptions are in the assertion audit.',
            limits='INTERPRETIVE BOUNDARY: not an exhaustive legal prohibition; another qualification or appointment can change scope.',
            condition='SCOPED CONDITIONS / UNRESOLVED LOCAL FACTS: '+basis['complexity'])
    for d in decisions:
        basis=decision_basis[d['id']]
        d['evidence_review_basis']=basis
        d['evidence_status']=basis['verdict']+': '+basis['rationale']
    provenance={s['id']:s for s in read('source_provenance.json')}
    for id,s in sources.items():
        p=provenance[id]
        s['retrieval_status']=p['retrieval_status']
        s['retrieval_provenance']=p
        s['evidence_status']=p['retrieval_status']+': access/provenance only; use the authored assertion judgment and source edition/scope.'
        if id in ['R03','R23','V06','V20']:
            s['evidence_status']='UNAVAILABLE IN THIS AUDIT: not used as current supporting passage evidence. '+str(p.get('error') or '')
        if id in ['R09','R12']:
            s['evidence_status']='EARLIER RETRIEVED EXCERPT ONLY: fresh retrieval failed; historical/source-specific example, current unchanged enforcement unconfirmed.'
        if id=='R19':s['evidence_status']='ALIAS OF A09: same HHS source, not independent corroboration.'


def review_blocks(review):
    return ['**Review reasoning:** '+review['rationale'], '',
            '**Other documented possibilities:** '+review['alternatives'], '',
            '**Complexity / unresolved facts:** '+review['complexity'], '',
            '**Captured supporting passage locations:**', '',*evidence_lines(review['evidence'])]


def report(write,roles,decisions,sources):
    receipt=read('audit_receipt.json');ledger=read('claim_adjudications.json')
    fixes=read('corrections.json');provenance=read('source_provenance.json')
    lines=['# Evidence review and unresolved facts','',
        'The defined inventory has **2,218 reviewed assertion units and zero pending dispositions**: 2,121 frozen baseline units plus 97 role-title units. Every unit has an explicit verdict and reason in the [assertion ledger](verification/claim_adjudications.json). This means review coverage, not that every assertion is confirmed true. Some units are composite paragraphs or table blocks rather than atomic sentences. Generated repetitions are not counted as independent findings.','',
        'The review was authored by the research agent against public primary-source passages. Scripts bind 495 authored selectors to captured paragraph/page/line locations and check inventory coverage; finding a selector is not automatic entailment verification. This is not an independent human clinical/legal review.','',
        'The 1,031 explicitly modeled units remain models. Actual institution workflows, permissions, staffing, delegation, case applicability and unprovided jurisdiction facts remain **unconfirmed**. No interviews, observed workflow study or institutional signoff occurred. No zero-hallucination guarantee is justified.','',
        'Read the reasoning, alternatives and complexity in each role dossier and decision entry. Per-assertion records are also published as [readable audit files](verification/README.md). [Corrections and consequential nuances](FINDINGS.md) identify the changes. [Source provenance](SOURCE_PROVENANCE.md) preserves access failures, edition limits, aliases and capture hashes.','',
        '## Coverage','', '| Category | Reviewed units |','| --- | --- |']
    for kind,count in sorted(Counter(x['kind'] for x in ledger).items()):lines.append(f'| {kind} | {count} |')
    lines+=['','## Verdicts','', '| Verdict | Units |','| --- | --- |']
    lines += [f'| {k} | {v} |' for k,v in receipt['verdict_counts'].items()]
    lines+=['','## Remaining boundaries','',
        '- A published job description establishes a described organizational example, not nationwide prevalence, actual current staffing or every employee’s permission.',
        '- Professional descriptions are context; state law, license, competence, privileges and practice arrangements still determine clinical permission.',
        '- Hospice V11/V16/V17 establish the official 2025 codification; a complete current-2026 amendment audit was not performed.',
        '- Four inaccessible sources remain in the catalogue as failed attempts, not positive evidence. R09/R12 use earlier excerpts with fresh-access failure. R19/A09 are aliases.',
        '- R13 contains wider professional categories alongside medical-director final-responsibility wording. Exact case signoff needs clarification; this review does not resolve that tension by guessing.',
        '- The inventory is a reproducible defined study scope. It does not establish all states, every insurance product, every possible exception, or task-by-task benchmark coverage.']
    write('EVIDENCE_REGISTER.md','\n'.join(lines))
    lines=['# Source access and capture provenance','',
        f'There are {len(sources)} catalogue entries across {len({s["url"] for s in sources.values()})} distinct URLs. This includes failed attempts and aliases; it is not a count of independently verified authorities. Captured source text remains local-only under ignored Runner/.cache/role-verification/. Tracked records preserve hashes and locators, not complete copyrighted source text. Tool-line locators refer to the captured tool response, not stable publisher line numbers.','',
        '| Source | Retrieval status | Paragraphs | Error / qualification |','| --- | --- | --- | --- |']
    for p in provenance:
        lines.append(f'| [{p["id"]}]({p["url"]}) | {p["retrieval_status"]} | {p.get("paragraphs",0)} | {str(p.get("error") or "See source edition/scope and assertion judgment").replace("|","/")} |')
    lines+=['','Machine-readable hashes: [source_provenance.json](verification/source_provenance.json). Passage locations and paragraph hashes: role/decision/narrative evidence bindings in verification/. A failed fresh fetch does not establish that a previously captured source was false, and an accessible page does not prove every linked claim.']
    write('SOURCE_PROVENANCE.md','\n'.join(lines))
    index=['# Assertion-by-assertion review','',
        'Frozen original wording, explicit verdict, reasoning, alternatives, scope limits and captured passage locations. The JSON ledger additionally preserves hashes. A shared source bundle supports a role-level judgment; its repetition on individual units does not claim that every passage independently proves every clause. Models are explicitly non-empirical. New corrected wording is shown where recorded.','',
        '[Evidence review](../EVIDENCE_REGISTER.md) · [Corrections](../FINDINGS.md) · [Full JSON ledger](claim_adjudications.json)','']
    grouped={}
    for unit in ledger:
        key=unit.get('parent') or unit['kind']
        if unit['kind'] in ['narrative_block','authored_graph_label']:key='narrative-and-graphs'
        grouped.setdefault(key,[]).append(unit)
    for key,units in sorted(grouped.items()):
        safe=''.join(c if c.isalnum() or c in '-_' else '-' for c in key)
        filename='assertions/'+safe+'.md'
        index.append(f'- [{key} — {len(units)} units]({filename})')
        body=[f'# {key} assertion review','', '[Audit index](../README.md)','']
        for u in units:
            body += [f'## {u["id"]}', '', '**Original:** '+relocated(u['text'],u['origin'],BASE/'verification'/filename), '', '**Verdict:** '+u['verdict'], '', '**Reason:** '+u['reason']]
            if u.get('wording_changed'):body += ['', '**Corrected wording:** '+u['current_text']]
            body += ['', '**Alternatives:** '+u['alternatives'], '', '**Complexity / unresolved:** '+u['complexity_or_unresolved'], '',*evidence_lines(u.get('evidence',[])), '']
        write('verification/'+filename,'\n'.join(body))
    index += ['', '[Revised narrative/graph units](revisions.md) supplement the frozen original ledger; they do not silently replace its original wording.']
    write('verification/README.md','\n'.join(index))
    revision_file=BASE/'verification/current_revision_review.json'
    if revision_file.exists():
        revisions=read('current_revision_review.json')
        body=['# Reviewed revision delta','',
            f"{revisions['current_units']} current narrative/graph units reconciled: {revisions['unchanged_units']} unchanged and {revisions['revised_or_added_units']} revised/added, zero pending dispositions. These overlap the original inventory; they are not all additional independent findings.", '',
            '[Machine-readable revision review](current_revision_review.json) · [Original assertion audit](README.md)', '']
        for u in revisions['items']:
            if u['review_route']=='Unchanged frozen unit':continue
            body += [f"## {u['id']} — {u['parent']}", '',
                relocated(u['text'],u['origin'],BASE/'verification/revisions.md'), '',
                '**Verdict:** '+u['verdict'], '', '**Reason:** '+u['reason'], '',*evidence_lines(u['evidence']), '']
        write('verification/revisions.md','\n'.join(body))
    findings=['# Corrections, alternatives and complexities','',
        'These are consequential findings from the defined evidence review, with detailed reasons and passage locations in the linked dossiers/decisions and assertion ledger. They are scoped findings, not new universal clinical rules.','']
    for fix in fixes:
        findings += [f'## {fix["id"]} — '+', '.join(fix['targets']), '', fix['change'], '',
            'Source context: '+', '.join(f'[{s}]({sources[s]["url"]})' for s in fix['sources'])+'.','']
    findings += ['## Further limits that matter','',
        '- **Job title versus credential:** a clinical job title can include supervised pre-licensure work (M02/R25). Additional credentials can change a psychologist’s prescribing scope (M07/V04). Neither title alone settles permission.',
        '- **Review versus implementation:** a favorable decision is distinct from authorization, service delivery or payment. MA effectuation depends on decision type and further-review exceptions (D15/A16).',
        '- **Peer review timing:** source presentations differ; no universal filing deadline is inferred. Use the actual product and notice (D14/R15).',
        '- **Protection and transport:** APS implementation timing, state programs, eligibility and service arrangements vary; no uniform child-protection mandate or national dispatch protocol is inferred (M23/M24/M31).',
        '- **Unavailable sources:** the expired Mayo page R03 and unavailable guide R23 no longer support current role assertions. V06/V20 are failed source attempts. Accessible alternatives support narrower examples.',
        '- **Prior authorization versus pre-claim review:** the CMS initiative overview distinguishes pre-service prior authorization from pre-claim review that can occur after service; do not extend one timing rule to all payment processes (V21).',
        '', 'Detailed unresolved facts and alternative pathways appear in every one of the 97 role reviews and all 34 decision reviews. The 219 dependencies, 46 handoffs and 97 interfaces continue to be explicitly proposed models.']
    write('FINDINGS.md','\n'.join(findings))
