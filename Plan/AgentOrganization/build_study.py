"""Publish authored design hypotheses and mechanical coverage screens; no model/network calls."""
from __future__ import annotations
import csv
import hashlib
import io
import itertools
import json
import sys
from collections import Counter,defaultdict
from pathlib import Path

sys.dont_write_bytecode=True
from definitions import PACKAGES,ROLE_NOTES
from decision_basis import DECISIONS,AUTHORITY_EFFECTS,SCENARIOS

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
OLD=ROOT/'Plan/HealthcareRoles'
DATE='2026-10-18'


def read(path):return json.loads(path.read_text(encoding='utf-8'))


def write(name,text):
    p=BASE/name;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text('\n'.join(x.rstrip() for x in text.splitlines()).rstrip()+'\n',encoding='utf-8',newline='\n')


def dump(name,value):write(name,json.dumps(value,ensure_ascii=False,indent=2))


def csv_write(name,rows,fields):
    out=io.StringIO();writer=csv.DictWriter(out,fieldnames=fields,lineterminator='\n')
    writer.writeheader();writer.writerows(rows);write(name,out.getvalue())


def refs(ids):
    return ', '.join('[Prior audited reference](../HealthcareRoles/README.md)' if id=='prior-reference' else f'[{id}](SOURCES.md#{id.lower()})' for id in ids)


FORMS={
 'external_route_adapter':'Share routing/transport machinery where permitted, while retaining actual forum eligibility and external decision ownership.',
 'external_actor':'Keep a separately attributed participant/evidence interface when this information belongs to an external party; use an acting role mode only where the actual task explicitly assigns it.',
 'external_review_actor':'Preserve the actual external forum, route and observed outcome; an internal critic is a different function.',
 'external_service_actor':'Coordinate the service through permitted interfaces; require observed acceptance/fulfillment rather than an internal persona’s promise.',
 'composite_external_functions':'Decompose the profile’s multiple functions before assigning worker identities or decision ownership.',
 'communication_adapter':'Prefer a bounded language/communication capability; retain speaker, content and understanding distinctions.',
 'task_scoped_worker':'Candidate workflow-owner function when the actual task assigns it; retain explicit role modes and observed completion obligations.',
 'task_scoped_review_mode':'Keep a distinct review-stage/permission contract; test separate reasoning context if it improves a defined review task.',
 'protected_review':'Preserve applicable uninvolved-review accountability; a fresh model context is only an internal error-checking experiment.',
 'delegation_boundary':'Establish the actual delegated scope and retained plan functions; do not infer it from a reviewer title.',
 'bounded_specialist':'Candidate on-demand specialist with a specific question and bounded evidence view; proposal by default, not assumed case-finalization authority.',
 'bounded_capability':'Candidate reusable evidence/checking capability; autonomous persistence needs a measured reason.',
 'role_mode':'Candidate explicit mode of a shared workflow owner, conditional on scope and measured context/coordination behavior.',
 'tool_supported_mode':'Prefer explicit identifiers/validation plus a scoped operation; a distinct persona is not inherently necessary.',
 'controlled_operation':'Candidate controlled operation derived from authoritative state, not an open-ended decision-making persona.',
 'configuration_or_escalation':'Represent assignment/routing rules explicitly; interpret/escalate only when the actual task requires it.',
 'governance_interface':'Retain the approved mandate/version and external approval identity; retrieval/analysis may be shared without creating governance authority.',
 'development_capability':'Primarily a development/quality-analysis function unless a task explicitly requires it at runtime; keep official grading separate.',
 'infrastructure':'Prefer explicit access/configuration/tool machinery; role text alone is not enforcement.'
}


def screen(a,b):
    x,y=ROLE_NOTES[a],ROLE_NOTES[b]
    forms={x['representation'],y['representation']}
    if 'protected_review' in forms or 'external_review_actor' in forms:
        return 'preserve_review_accountability','Keep review provenance, applicable independence and forum identity; shared software is not the same as merged decision authority.','AD05 AD06 AD10'
    if forms & {'external_actor','external_service_actor','composite_external_functions','delegation_boundary'}:
        return 'preserve_participant_or_delegation_boundary','A common adapter may coordinate these functions, but external statements/fulfillment, composite functions and delegation cannot be collapsed by a shared persona.','AD02 AD03 AD05'
    if x['package']==y['package']:
        p=PACKAGES[x['package']]
        if p['mode']=='merge_candidate':
            return 'candidate_function_merger','Shared primary work package suggests a merger to test, conditional on actual tools, authority, state distinctions and workload; not a verified permission.','AD04 AD05 AD13'
        return 'shared_plumbing_distinct_function','Shared package is an analysis grouping; preserve distinct expertise/output/approval conditions and evaluate whether separate contexts help.','AD03 AD08 AD15'
    if (forms & {'infrastructure','configuration_or_escalation','governance_interface','development_capability'}):
        return 'shared_support_preserve_permissions','Shared configuration/support can serve the case worker without acquiring its substantive authority or official grading powers.','AD05 AD07 AD15'
    return 'no_merge_evidence_yet','Different work packages: a merger is possible but not justified by this mechanical screen; examine actual task/data/tool overlap first.','AD03 AD04 AD13'


EXAMPLES=[
 ('O01','O02','candidate','Share provider packet/referral tracking; retain referral receipt/acceptance and authorization outcome as distinct observations.'),
 ('O01','O03','candidate','Share the case owner, but make identity matching explicit before attaching evidence.'),
 ('O01','O04','candidate','Share benefits lookup and packet preparation; never equate verified benefits with authorization or payment.'),
 ('O01','O05','candidate','Share administrative tracking and scheduling where permitted; booked, cleared and performed remain distinct.'),
 ('O06','O08','conditional','Share evidence retrieval/consistency review, but use the actual release purpose and clarification/authorship process.'),
 ('O07','O08','conditional','Common documentation support is plausible; code selection and clinical fact clarification remain different work.'),
 ('U01','U02','candidate','Share payer intake/benefit state; apply only explicitly delegated limited nonclinical decisions.'),
 ('U01','U09','conditional_cross_package','The payer owner may invoke notice preparation/delivery, but the notice must derive from the authorized decision and cannot create it.'),
 ('U03','U04','conditional','Share criteria/evidence infrastructure; retain the actual initial-review stage, expertise, escalation and signoff rules.'),
 ('U04','U13','protected','Do not rename the initial author to claim uninvolved reconsideration. Internal critic and actual reconsideration are distinct.'),
 ('M01','M10','candidate','Navigation and coordination can share case obligations; external resource availability still needs evidence.'),
 ('M01','M18','conditional','Shared transition coordination may improve continuity, but administrative readiness and clinical discharge authority differ.'),
 ('M04','M05','conditional','Share medication/access information; technician/access activity must not acquire therapy-change authority.'),
 ('M23','M24','external_boundary','Dispatcher coordination is not physical driving, pickup or attendance; only the actual environment response can establish completion.'),
 ('P01','P02','participant_boundary','Shared family-case context must retain separate speakers, wishes and representative facts.'),
 ('P05','P06','conditional','A language service can offer both operations while preserving oral interaction versus written fidelity and actual qualification limits.'),
 ('P05','M16','expertise_boundary','Interpreting a conversation is not a clinical speech/swallowing assessment; similar language-related words do not make the functions equivalent.'),
 ('M28','M29','composite_boundary','Common support coordination is possible, but hospice IDG/RN/attending/certification and spiritual support are distinct functions.'),
 ('G08','G03','approval_boundary','A policy-analysis capability can serve governance; its draft cannot approve its own controlling policy.'),
 ('G06','U13','review_boundary','An internal quality critic is not the applicable physician reconsiderer or official benchmark grader.')
]


def main():
    baseline=read(BASE/'baseline.json')
    for f in baseline['files']:
        assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256'],f['path']
    roles=read(OLD/'data/roles.json');old_decisions=read(OLD/'data/decisions.json')
    relations=read(OLD/'data/relations.json');flows=read(OLD/'data/information_flows.json')
    sources=read(BASE/'sources.json');ids={r['id'] for r in roles}
    assignments=[r for p in PACKAGES.values() for r in p['roles']]
    assert set(assignments)==set(ROLE_NOTES)==ids and len(assignments)==len(ids)==97
    assert all(ROLE_NOTES[r]['package']==p['id'] for p in PACKAGES.values() for r in p['roles'])
    assert {d['id'] for d in old_decisions}==set(AUTHORITY_EFFECTS)
    assert all(r['representation'] in FORMS for r in ROLE_NOTES.values())
    by={r['id']:r for r in roles};analyses=[]
    index=['# Analysis of all 97 functions','',
        'These are conditional organizational-design judgments, not verified assignments for every benchmark task or permission grants. All 97 functions are accounted for once in a primary work package. A profile can be an external interface, role mode, capability or composite rather than a separate running agent. No runtime benefit is established.','',
        '[Main analysis](ANALYSIS.md) · [Work packages](WORK_PACKAGES.md) · [Questions](QUESTIONS.md) · [Original audited roles](../HealthcareRoles/ROLE_INDEX.md)','',
        '| Role | Proposed representation | Primary package | Specific question |','| --- | --- | --- | --- |']
    for r in roles:
        id=r['id'];note=ROLE_NOTES[id];p=PACKAGES[note['package']]
        linked=[d['id'] for d in old_decisions if id in d['actors']]
        analysis=dict(id=id,title=r['title'],**note,conclusion=FORMS[note['representation']],
            merge_condition=p['merge_rationale'],retained_package_boundary=p['retained_boundary'],split_trigger=p['split_trigger'],
            evidence_role=f'Plan/HealthcareRoles/roles/{id}.md',evidence_source_ids=r['sources'],
            linked_authority_questions=linked,original_scope=r['condition'],
            original_evidence_limit=r['evidence_review_basis']['complexity'],
            suggested_input_context=r['inputs'],suggested_output_context=r['outputs'],
            status='PROPOSED_DESIGN_INFERENCE_NOT_RUNTIME_VALIDATED',actual_task_assignment_verified=False)
        analyses.append(analysis)
        index.append(f'| [{id} {r["title"]}](roles/{id}.md) | {note["representation"]} | [{p["id"]}](WORK_PACKAGES.md#{p["id"].lower()}) | {note["key_question"]} |')
        body=[f'# {id} — {r["title"]}','',
            '[Role analysis index](../ROLE_ANALYSIS.md) · [Audited healthcare dossier](../../HealthcareRoles/roles/'+id+'.md)','',
            '**Status:** proposed design inference; actual task assignment and runtime benefit are unverified. The task/tool contract can assign a simulated function even where the analogous human job needs credentials; do not invent extra real-person steps.','',
            '## What function are we trying to preserve?','',r['mission'],'',
            'The linked healthcare dossier contains the responsibilities, scoped decisions and evidence. This analysis does not upgrade its conditions or model contacts into universal facts.','',
            '## Specific question','',note['key_question'],'',
            '## Provisional conclusion and reason','',analysis['conclusion'],'',note['distinction'],'',
            f'Primary grouping: [{p["id"]} — {p["title"]}](../WORK_PACKAGES.md#{p["id"].lower()}). '+p['work'],'',
            '## Can its work be merged?','',p['merge_rationale'],'',
            '**Boundary that must survive:** '+p['retained_boundary'],'',
            'A common work package is not proof that one employee may perform every activity, or that one persistent LLM is best. A shared adapter, a role mode and a separate worker are all alternatives.','',
            '## Information and output contract','',
            'Context from the prior proposed model: '+ '; '.join(r['inputs'])+'.','',
            'Potential work products from that model: '+ '; '.join(r['outputs'])+'.','',
            'For a software invocation, add case/stage, source versions, explicit unknowns, allowed operations, requested output, current owner and stop condition. These are proposed internal fields, not verified API parameters or mandatory institutional forms.','',
            '## Counterexample and reconsideration','',
            '**Failure to detect:** '+note['counterexample'],'',
            '**Reason to split/revise the package:** '+p['split_trigger'],'',
            'Test a mode-based owner and a bounded specialist/persistent-worker alternative against the same task-visible facts and declared resource constraint; preserve source, authority and completion distinctions. No such comparison has run.','',
            '## Remaining uncertainty and evidence','',
            r['evidence_review_basis']['complexity'],'', '**Prior applicability:** '+r['condition'],'',
            'Source IDs in the prior dossier: '+', '.join(r['sources'])+'. These support the scoped healthcare context, not the new software partition. See the prior [source provenance](../../HealthcareRoles/SOURCE_PROVENANCE.md) for failed/dated/example evidence.','',
            'Related authority questions: '+(', '.join(f'[{d}](../AUTHORITY_IMPLICATIONS.md#{d.lower()})' for d in linked) if linked else 'Apply the explicit package/role boundaries; no additional decision power is inferred.')+'.','',
            'Design alternatives and decision rationale: [AD01–AD16](../DECISION_LOG.md).']
        write(f'roles/{id}.md','\n'.join(body))
    write('ROLE_ANALYSIS.md','\n'.join(index));dump('data/role_analysis.json',analyses)
    dump('data/work_packages.json',list(PACKAGES.values()))
    package_lines=['# Candidate work packages','',
        'Twenty-three analysis categories account for all 97 functions. They are neither 23 required agents nor a national staffing plan. Even a merger candidate needs actual task/permission verification and empirical comparison. Profiles assigned to external/interface categories can still become acting role modes if actual task instructions assign them.','']
    for p in PACKAGES.values():
        package_lines += [f'<a id="{p["id"].lower()}"></a>',f'## {p["id"]} — {p["title"]}','',
            '**Design category:** '+p['mode']+'; proposed, untested.','',
            '**Functions:** '+', '.join(f'[{r} {by[r]["title"]}](roles/{r}.md)' for r in p['roles']), '',
            '**Work to preserve:** '+p['work'],'','**Why share some work:** '+p['merge_rationale'],'',
            '**What cannot silently collapse:** '+p['retained_boundary'],'',
            '**Evidence that would favor splitting/revision:** '+p['split_trigger'],'',
            '**Alternative implementations:** a shared adapter/tool, a named mode within a case owner, bounded specialist contexts, or persistent workers where justified. Which functions are actually assigned is unresolved until task/tool mapping.','',
            '**Evidence trail:** healthcare context is in each linked audited dossier; the grouping and split trigger are authored engineering hypotheses. [Decision framework](DECISION_LOG.md) and [experiment plan](EXPERIMENT_PLAN.md) describe how to challenge them.','']
    write('WORK_PACKAGES.md','\n'.join(package_lines))
    dump('data/decisions.json',DECISIONS)
    lines=['# Decision and rationale log','',
        'Sixteen provisional design judgments record the question, evidence, conclusion, concise reason, alternatives, uncertainty and reconsideration condition. These are reviewable reasoning summaries, not measured outcomes. The main objective is our harness inside χ-Bench; an independently built simulator remains a separate alternative.','']
    for d in DECISIONS:
        lines += [f'<a id="{d["id"].lower()}"></a>',f'## {d["id"]} — {d["question"]}','',
            '**Status:** '+d['status'],'','**Conclusion:** '+d['conclusion'],'','**Rationale:** '+d['rationale'],'',
            '**Alternatives:** '+ '; '.join(d['alternatives'])+'.','','**Evidence/context:** '+refs(d['evidence']), '',
            '**Uncertainty:** '+d['uncertainty'],'','**Reconsider if:** '+d['reconsider_if'],'']
    write('DECISION_LOG.md','\n'.join(lines))
    authority=[];lines=['# Authority implications for the software design','',
        'Every one of the 34 prior questions is mapped below. The old healthcare statement retains its original scope; the software implication is a proposed design response. This is not a new legal/clinical audit or a verified task-specific permission model.','']
    for d in old_decisions:
        row=dict(id=d['id'],question=d['question'],actors=d['actors'],packages=sorted({ROLE_NOTES[r]['package'] for r in d['actors']}),
            design_implication=AUTHORITY_EFFECTS[d['id']],original_condition=d['condition'],original_source_ids=d['sources'],status='SCOPED_PRIOR_CONTEXT_PLUS_PROPOSED_DESIGN_IMPLICATION')
        authority.append(row)
        lines += [f'<a id="{d["id"].lower()}"></a>',f'## {d["id"]} — {d["question"]}','',
            '[Prior scoped rule and passage review](../HealthcareRoles/DECISIONS.md#'+d['id'].lower()+')','',
            '**Design implication:** '+row['design_implication'],'','**Retained scope:** '+d['condition'],'',
            '**Affected packages:** '+', '.join(f'[{p}](WORK_PACKAGES.md#{p.lower()})' for p in row['packages']),'']
    write('AUTHORITY_IMPLICATIONS.md','\n'.join(lines));dump('data/authority_implications.json',authority)
    scenario_data=[];lines=['# Proposed stress cases','',
        'Twenty authored counterexamples, not executed tests or official benchmark cases. Expected behavior is conceptual and conditional on the actual task/tool contract. MAST informs the diagnostic approach; these are not reproduced MAST results. [Experiment plan](EXPERIMENT_PLAN.md).','']
    for id,title,participants,trigger,expected,failure in SCENARIOS:
        scenario_data.append(dict(id=id,title=title,roles=participants.split(),trigger=trigger,expected=expected,failure=failure,status='PROPOSED_NOT_EXECUTED'))
        lines += [f'## {id} — {title}','', '**Roles:** '+', '.join(f'[{r}](roles/{r}.md)' for r in participants.split()),'',
            '**Trigger:** '+trigger,'','**Expected design behavior:** '+expected,'','**Failure to look for:** '+failure,'','**Execution evidence:** none; requires an actual permitted task/tool realization before running.','']
    write('STRESS_CASES.md','\n'.join(lines));dump('data/stress_cases.json',scenario_data)
    pairs=[]
    for a,b in itertools.combinations(sorted(ids),2):
        verdict,reason,decisions=screen(a,b)
        pairs.append(dict(role_a=a,role_b=b,package_a=ROLE_NOTES[a]['package'],package_b=ROLE_NOTES[b]['package'],screen=verdict,reason=reason,decision_ids=decisions,method='mechanical_design_screen_not_individual_factual_review'))
    csv_write('data/pair_screen.csv',pairs,list(pairs[0]));counts=dict(Counter(x['screen'] for x in pairs))
    lines=['# Merger candidates and pair screening','',
        'All 4,656 unordered pairs of 97 functions have a **mechanical planning screen** in [pair_screen.csv](data/pair_screen.csv). These are rule-derived labels, not 4,656 independently researched compatibility/permission judgments. They cannot prove safe merger, legal authority, optimal architecture or a measured benefit.','',
        'Rules run in order: preserve review accountability; preserve participant/delegation/composite boundaries; consider compatible within-package function sharing; preserve support/permission separation; otherwise record insufficient merger evidence. No numeric compatibility score is invented.','',
        '| Screen | Pairs |','| --- | --- |']
    lines += [f'| {k} | {v} |' for k,v in sorted(counts.items())]
    lines += ['', '## Twenty explicitly considered examples','',
        'These authored examples provide more specific reasoning. The mechanical screen is deliberately conservative and may leave a cross-package merger unclassified even where the authored example proposes it conditionally. A screen is not a decision engine.','',
        '| Pair | Judgment | Retained distinction / reason |','| --- | --- | --- |']
    for a,b,status,reason in EXAMPLES:lines.append(f'| [{a}](roles/{a}.md) / [{b}](roles/{b}.md) | {status} | {reason} |')
    lines += ['', 'A merger should be revisited if actual task scopes differ, context becomes unreliable, distinct information views cannot be enforced, handoff overhead changes, or a controlled trial favors separation. Conversely, common data plumbing does not require merging substantive authorities.']
    write('MERGE_ANALYSIS.md','\n'.join(lines));dump('data/considered_merge_examples.json',[dict(a=a,b=b,status=s,reason=r) for a,b,s,r in EXAMPLES])
    grouped=defaultdict(list)
    for e in relations:
        if e['type']=='coordination_dependency':grouped[(ROLE_NOTES[e['sender']]['package'],ROLE_NOTES[e['receiver']]['package'])].append(e['id'])
    package_edges=[dict(sender=a,receiver=b,modeled_edge_count=len(edges),edge_ids=' '.join(edges),status='inherited_unconfirmed_model_not_measured_frequency') for (a,b),edges in sorted(grouped.items())]
    csv_write('data/package_dependencies.csv',package_edges,list(package_edges[0]))
    flow_rows=[];lines=['# Information, ownership and dependency implications','',
        'The 219 old dependency edges and 46 handoffs are proposed workflow models, not observed interactions. Grouping them under new packages is a mechanical crosswalk, not fresh empirical evidence. Counts cannot measure communication cost or optimize worker count. [Package dependency crosswalk](data/package_dependencies.csv).','',
        'A handoff crossing two packages does not automatically require two agents; a handoff within one package does not remove its artifact, authorship or acknowledgement obligation.','',
        '| Flow | Proposed artifact | Sender/package | Receiver/package | Design obligation |','| --- | --- | --- | --- | --- |']
    for f in flows:
        a,b=ROLE_NOTES[f['sender']]['package'],ROLE_NOTES[f['receiver']]['package']
        obligation=('Retain the explicit artifact and receipt even if one owner performs both functions.' if a==b else 'Preserve case/stage, source versions, unresolved facts and responsibility when crossing this modeled boundary.')
        flow_rows.append(dict(id=f['id'],sender=f['sender'],receiver=f['receiver'],sender_package=a,receiver_package=b,artifact=f['artifact'],design_obligation=obligation,status='INHERITED_MODEL_PLUS_DESIGN_INFERENCE'))
        lines.append(f'| [{f["id"]}](../HealthcareRoles/INFORMATION_FLOWS.md#{f["id"].lower()}) | {f["artifact"]} | [{f["sender"]}](roles/{f["sender"]}.md) / {a} | [{f["receiver"]}](roles/{f["receiver"]}.md) / {b} | {obligation} |')
    lines+=['','## Proposed task/result contract','',
        'Request: case ID, actual stage, objective, relevant evidence references/versions, known unknowns, permitted data/tools, requested output, write owner, budget/deadline and stop rule. Result: supported facts, interpretations, unresolved issues, proposed actions, evidence references and what was actually observed versus merely drafted.','',
        'The receiver checks case/version/scope before accepting the proposal. Receipt is not substantive approval. Transfer of an obligation needs a named owner and acknowledgement. If newer evidence makes a result stale, re-evaluate it rather than applying it silently. These fields are internal design proposals, not asserted official API parameters.','',
        'External participant identity, case truth and actual service outcomes remain distinct from the coordinator’s plan. See [design diagrams](DIAGRAMS.md) and [stress cases](STRESS_CASES.md).']
    write('INFORMATION_DESIGN.md','\n'.join(lines));dump('data/handoff_implications.json',flow_rows)
    source_lines=['# Source ledger and interpretation limits','',
        'Eleven primary-source entries read during this study/clarification. These establish background and scoped rules, not validation of our proposed software architecture. The prior 97-role evidence audit remains a separate baseline. No source is interpreted as proving that every profession needs an agent.','']
    for s in sources:
        source_lines += [f'<a id="{s["id"].lower()}"></a>',f'## {s["id"]} — {s["title"]}','',f'[{s["title"]}]({s["url"]})','',
            '**Edition:** '+s['edition'],'','**Checked:** '+s['checked_local_date']+'; '+s['access'], '',
            '**Locator:** '+s['locators'],'','**Finding:** '+s['finding'],'','**Limit:** '+s['limit'],'']
    source_lines += ['## Local provenance','',
        'The AHRQ communication overview was also extracted headlessly with shared Crawl4AI 0.9.5: HTTP 200, 37,901 Markdown characters. Its raw text/receipt remain local-only under ignored Runner/.cache/agent-organization/sources/. That extraction is not an additional independent source or factual validation.','',
        'S09 was inspected in the actual local official checkout at commit 4444a07fa68a4f1623f841a292a54e284fc8e7f7. No source fetch changed that checkout. Its interface and the live S06 description differ; AD14 records the unresolved compatibility issue. Full paper methods were not reproduced, no all-state/current-law re-audit occurred, and inherited healthcare ambiguities remain explicit.']
    write('SOURCES.md','\n'.join(source_lines))
    result=dict(date=DATE,baseline_commit=baseline['baseline_commit'],baseline_hashes_unchanged=True,roles=len(analyses),work_packages=len(PACKAGES),
        design_decisions=len(DECISIONS),authority_implications=len(authority),proposed_stress_cases=len(SCENARIOS),
        mechanically_screened_pairs=len(pairs),authored_pair_examples=len(EXAMPLES),pair_screen_counts=counts,
        inherited_dependencies=sum(e['type']=='coordination_dependency' for e in relations),inherited_handoffs=len(flows),source_entries=len(sources),
        runtime_implemented=False,benchmarks_executed=False,architecture_performance_verified=False,
        limitation='Publication/coverage only; labels, groupings and pair screens are design hypotheses, not legal permissions or empirical optimization.')
    dump('data/build_receipt.json',result);print(json.dumps(result,indent=2))


if __name__=='__main__':main()
