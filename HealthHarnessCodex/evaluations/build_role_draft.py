"""Export approved role text and review provenance from the blueprint source.

Historical filename retained for reproducible Phase 1/2 verification. This
command exports documentation only; build_blueprint.py regenerates catalogs.
"""
from __future__ import annotations
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
BASELINE_REVISION='514a890f7d1f03537de7c1b5f87ec149ceba9306'
sys.path.insert(0,str(ROOT/'HealthHarnessBlueprint'))
from micro_roles import ROLES

# Only the explicitly requested redefinitions; CM-17/18/19 retain current contracts.
REDEFINITIONS = {
 'CM-01': ('Orient coordination around the referral and member context rather than only identifying forms.', {
   'decision_scope': 'Interpret the referral and current episode using observed chart context and applicable care-management intake policy; identify coordination priorities and unresolved needs.'}),
 'CM-03': ('Name the governing policy family without inventing a universal outreach sequence.', {
   'decision_scope': 'Plan outreach from applicable care-management outreach and enrollment policy, observed contact permissions and current member questions; retain required information and exit/handoff duties.'}),
 'CM-04': ('Own informed engagement and accurate program representation, with actual consent before any permitted interview.', {
   'name': 'Member-engagement lead',
   'decision_scope': 'Represent the program accurately under retrieved policy and observed eligibility conditions; learn member priorities, connect them to supported services and answer questions plainly. Invite an informed decision, respect decline and conduct a permitted interview only after actual consent.',
   'output': 'Source-linked engagement handoff with consent status, member priorities and open questions; accurate program information and permitted post-consent interview findings.',
   'completion_check': 'An informed decision is observed or the member ended contact; each question is answered or noted as unanswerable. Consent status, member priorities and open questions are preserved.'}),
 'CM-09': ('Make goal elicitation relevant during permitted outreach and include CM-09 in its responsibility packet.', {
   'decision_scope': 'Elicit the member\'s own priorities during permitted outreach and clarify goals for care planning under the applicable consent conditions; preserve acceptance, disagreement and unknown status.'}),
 'CM-11': ('Make support options actionable as proposed plan interventions without claiming delivery.', {
   'output': 'Proposed care-plan interventions linked to member goals and support needs, with responsible recipients and eligibility/availability uncertainty.',
   'decision_scope': 'Translate supported psychosocial and resource options into proposed care-plan interventions within assigned scope.'}),
 'CM-13': ('Name general care-plan elements while leaving exact requirements to retrieved policy.', {
   'output': 'Versioned care plan connecting supported problems, member goals and interventions with escalation conditions, follow-up cadence, responsibilities and unresolved items.',
   'decision_scope': 'Compose the requested plan using applicable care-plan standards; distinguish sourced problems and goals from proposed interventions and their execution status.'}),
 'CM-14': ('Preserve a useful referral intervention where the world supplies no execution tool.', {
   'decision_scope': 'Coordinate a permitted referral through an actual available tool; when no execution tool exists, include the proposed referral intervention and responsible recipient in the care plan.',
   'output': 'Actual referral receipt/failure/unknown where performed, otherwise a clearly planned care-plan referral intervention.',
   'completion_check': 'Record observed receipt and next owner if executed; otherwise record the planned intervention, execution limit and responsible recipient without claiming a sent referral.'}),
 'CM-15': ('Do not demand an acknowledgement operation that the world cannot perform.', {
   'decision_scope': 'Track the recipient\'s actual acceptance or status when observable; when no receiving-status tool exists, plan the acknowledgement follow-up intervention in the care plan.',
   'output': 'Sourced receiver status and next obligation, or a clearly planned acknowledgement follow-up intervention.',
   'completion_check': 'Each claimed receiving status has a fresh actual source; an unexecuted acknowledgement check remains a planned intervention with an owner.'}),
 'CM-16': ('Keep access coordination useful without inventing a booking capability.', {
   'decision_scope': 'Coordinate an available permitted access step; when no execution tool exists, plan the access intervention and responsible recipient in the care plan.',
   'output': 'Observed booking/support status where performed, otherwise a planned care-plan access intervention with unresolved barriers.',
   'completion_check': 'Claimed bookings have supplied observations; unavailable execution is represented as planned coordination with an owner and outstanding barriers.'}),
 'CM-20': ('A decline or ended contact requires the applicable closure path, not an inferred successful care outcome.', {
   'decision_scope': 'Choose the episode completion, decline or exception path under retrieved care-management closure policy and observed participation; distinguish an ended contact from consent or refusal.',
   'output': 'Source-supported episode disposition with remaining permitted documentation/communication duties, return-path information where required and unmet goals.',
   'completion_check': 'Disposition follows the retrieved policy and observed participation; remaining duties and unmet assigned outcomes remain explicit without claiming downstream care.'}),
 'PA-09': ('Clarification routing may represent the documented provider position but does not impersonate its clinical author.', {
   'decision_scope': 'Choose the clarification question and recipient under provider procedure; represent documented provider facts, with any new clinical opinion restricted to separately assigned professional authority.'}),
 'PA-14': ('Give the response function an operational next-step mandate while retaining the payer as decision source.', {
   'decision_scope': 'Classify the actual payer response and choose the supported provider operational next step under applicable procedure; preserve the authoritative response and outstanding deadlines.'}),
 'PA-15': ('Represent a supported response without inventing clinical support or new counterparty requests.', {
   'decision_scope': 'Choose and represent the supported provider response to the actual request under applicable procedure; obtain new clinical clarification from its authorized source where required.'}),
 'PA-16': ('Distinguish procedural route selection from separately assigned clinical representation and external adjudication.', {
   'decision_scope': 'Select the supported correction, peer exchange or dispute route under established standing and procedure; clinical representation requires assigned professional authority and external outcomes require actual observations.'}),
 'UM-08': ('Reflect U03 delegated approval latitude without granting automatic final denial or reconsideration.', {
   'decision_scope': 'Apply governing criteria to observed evidence; approve only under documented delegation when criteria and program permit, otherwise recommend or escalate within the assigned initial-review function.'}),
 'UM-13': ('Reflect U04 clinical determination latitude and preserve recommendation versus finalization.', {
   'decision_scope': 'Issue or recommend the clinical coverage determination actually assigned under documented authority and governing criteria; preserve the difference between recommendation, recorded decision and finalized determination.'}),
 'UM-14': ('Represent the recorded outcome and procedural rights accurately without creating a new decision.', {
   'decision_scope': 'Represent the authoritative determination and applicable procedural information under notice policy; resolve missing rationale through the responsible decision source rather than changing the outcome.'}),
 'UM-17': ('Reflect U13 affirm/reverse latitude conditional on actual reconsideration assignment and required independence.', {
   'decision_scope': 'Affirm or reverse within assigned reconsideration authority using the disputed record and governing criteria; verify applicable review separation rather than infer independence from a changed prompt.'}),
}


def cell(value):
    return str(value).replace('|','&#124;').replace('\n','<br>')


def main():
    original={r['id']:r for r in json.loads(subprocess.check_output(
        ['git','show',BASELINE_REVISION+':HealthHarnessCodex/health_harness_codex/data/micro_roles.json'],cwd=ROOT))}
    previous={r['id']:r for r in json.loads((ROOT/'Progress/role_authority_draft.json').read_text(encoding='utf-8'))}
    draft=[]
    for r in ROLES:
        row={k:r[k] for k in ('id','hospital_roles','authority','approach','status_label','model_visible')}
        row['hospital_source_note']=previous[r['id']]['hospital_source_note']
        if r['id'] in REDEFINITIONS:
            row['changes']={k:{'old':original[r['id']][k],'new':r[k]}
                for k in REDEFINITIONS[r['id']][1]}
        draft.append(row)
    (ROOT/'Progress/role_authority_draft.json').write_text(json.dumps(draft,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# Role authority and professional approach','',
        '2026-11-03. Final role text approved by user-delegated Claude review. Phase 1 revisions and Phase 2 runtime delivery are implemented. Software verification is recorded below; behavioral success requires later user-run probes/trials.','',
        'Authority is an active mandate governed jointly by the assigned task and retrieved applicable policy. It never overrides boundaries, consent/privacy, identity or tool/observation requirements. Dossier mappings supply functional context, not credentials or proof of local delegation. Approaches synthesize mission/duties; no protected handbook text is embedded.','',
        '## Binding decisions and reasons','',
        '- All 66 mandates use affirmative voice; the common assignment/policy qualification is stated once per system message rather than in each role. CM-04 uses the exact reviewed authority (the sole length exception). Approaches retain the draft meaning in at most 200 characters.',
        '- CM-04 remains Member-engagement lead, with the drafted scope, output and completion check. Its role represents the program accurately and supports an informed decision under actual policy conditions and consent.',
        '- Keep CM-02 (M01/P03/P05) and CM-05 (M01/P05) composite mappings: participant/interface sources constrain representation and communication fidelity, without impersonating those participants.',
        '- Keep UM-04/05 split: select controlling policy versus interpret its criteria; neither gains policy-approval authority. UM-08 retains delegated approval, otherwise recommendation/escalation; UM-13/17 retain assigned decision authority conditions.',
        '- Keep drafted CM-14/15/16 planning contracts when tools are absent. Planning completes only that delegated responsibility, not the unperformed external effect or overall goal. CM-17/18/19 retain all previous contract fields, with authority/approach and catalog metadata added.',
        '- SH-02/04/06/07/08/09 remain cataloged code safeguards with model_visible=false; SH-01/03/05/10 remain visible. case.get_role returns any current-domain/shared contract, including hidden safeguards; hidden safeguards cannot become model helpers.',
        '- status_label is prompt_contract except CM-04/SH-10 executing_worker. This is descriptive, not a declaration of 66 running processes. SH-10 reviews readiness/stopping, not conversation content or official grading.',
        '- Existing boundaries are unchanged byte-for-byte; no execution guard, patient isolation, repeat detection or evidence/completion check was weakened.','',
        '## Source and regeneration','',
        'The source of truth is [micro_roles.py](../HealthHarnessBlueprint/micro_roles.py). [Hospital role dossiers](../Plan/HealthcareRoles/data/roles.json), [module coverage](../HealthHarnessBlueprint/data/role_coverage.json) and [work packages](../Plan/AgentOrganization/data/work_packages.json) supply mapping provenance. The machine-readable [review record](role_authority_draft.json) retains per-role mapping explanations and original/new redefinitions.',
        '', 'Run `python -X utf8 HealthHarnessBlueprint/tools/build_blueprint.py` to regenerate the blueprint JSON, MICRO_ROLES.md and runtime JSON. [runtime_overrides.py](../HealthHarnessBlueprint/runtime_overrides.py) is the explicit runtime-only override mechanism: **no overrides currently**. The previous CM-04 runtime status difference is superseded by the shared executing_worker label. Future overrides require a documented field/reason here; boundary overrides are forbidden. Tests assert generated runtime equals blueprint after only that mapping.',
        '', 'Run `python -X utf8 HealthHarnessCodex/evaluations/build_role_draft.py` to export this record; `validate_role_draft.py` checks redefinitions against the pinned pre-revision catalog at `514a890f7d1f03537de7c1b5f87ec149ceba9306` and new fields against the final catalog. [Prompt measurements](ROLE_PROMPT_BASELINE.md) retain before/after numbers.','',
        '## Approved role text and mappings','',
        '| Role | Hospital IDs | Status / visible | Authority | Approach |',
        '| --- | --- | --- | --- | --- |']
    for r in ROLES:
        lines.append('| '+' | '.join(map(cell,[r['id']+' '+r['name'],', '.join(r['hospital_roles']) or 'code-only safeguard',r['status_label']+' / '+str(r['model_visible']),r['authority'],r['approach']]))+' |')
    lines+=['','## Retained redefinitions and reasons','']
    for row in draft:
        if 'changes' not in row:continue
        lines += ['### '+row['id'],'',REDEFINITIONS[row['id']][0],'',
            '| Field | Previous | Approved |','| --- | --- | --- |']
        for k,c in row['changes'].items():
            lines.append('| '+' | '.join(map(cell,[k,c['old'],c['new']]))+' |')
    lines += ['','## Verification and continuation','',
        'See [Phase 2 verification](ROLE_AUTHORITY_VERIFICATION.md) for executed checks, counts, timings, offline probe sizes and next steps. No commit, Docker, dataset trial, judge or live inference is authorized in this implementation session. Root HANDOFF.md is reviewer-owned and was left untouched.','']
    (ROOT/'Progress/ROLE_AUTHORITY.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({'roles':len(draft),'redefinitions':len(REDEFINITIONS),'runtime_overrides':0}))


if __name__=='__main__':main()
