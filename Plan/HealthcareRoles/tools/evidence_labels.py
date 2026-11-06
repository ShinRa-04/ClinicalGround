"""Baseline field labels and historical core checks; deep_review overrides publication statuses."""

CHECKED_RULES = {
 'D12': {'source':'A02','locator':'42 CFR 422.566(d)',
  'checked_claim':'Anticipated adverse MA medical-necessity determinations require appropriate physician or other licensed professional review with relevant expertise.',
  'scope':'Core qualification requirement only; integrated-plan exception and actual case applicability must still be checked.'},
 'D13': {'source':'A03','locator':'42 CFR 422.590(h)(1)-(2)',
  'checked_claim':'MA reconsiderers were not involved in the initial determination; medical-necessity denial reconsideration is made by an appropriately expert physician.',
  'scope':'Specified MA reconsideration rule; not every product or dispute type.'},
 'D22': {'source':'A06','locator':'42 CFR 482.43(a)(5)',
  'checked_claim':'Hospital discharge planning/evaluation is developed by or under an RN, social worker or other appropriately qualified personnel.',
  'scope':'Hospital discharge-planning qualification requirement only; not sole medical discharge authority.'},
 'D23': {'source':'A07','locator':'42 CFR 484.60(a)(1)',
  'checked_claim':'The specified home-health plan is established, reviewed and signed by a physician or allowed practitioner within scope; applicable additions are approved by the referring professional.',
  'scope':'Core plan/signature and evaluation-addition rule; other order/revision statements retain their separate scope.'}
}

FIELD_LABELS = {
 'mission':'INTERPRETATION: functional summary, not an independently verified occupational classification.',
 'duties':'SOURCE-LINKED SUMMARY: not individually passage-verified sentence by sentence; no blanket factual certification.',
 'decisions':'CONDITIONAL INTERPRETATION: actual license, delegation and local decision permission are NOT CONFIRMED.',
 'limits':'BOUNDARY INTERPRETATION: avoid assuming title grants authority; not a complete, claim-verified legal scope statement.',
 'inputs':'SYNTHESIZED MODEL: suggested information needs, NOT CONFIRMED institutional requirements.',
 'outputs':'SYNTHESIZED MODEL: suggested work products, NOT CONFIRMED mandatory records/forms.',
 'dependencies':'SYNTHESIZED MODEL: possible contacts/arrows, NOT CONFIRMED as actual organizational workflow.',
 'escalation':'SYNTHESIZED MODEL: suggested routing, NOT CONFIRMED local escalation procedure.',
 'condition':'UNCONFIRMED LOCAL FACTS: resolve the stated jurisdiction, credential, product and institution conditions.'
}


def apply_labels(roles,decisions,flows,sources):
    for s in sources.values():
        note=s.get('note','').lower()
        if s['id']=='A08':
            status='DATED SOURCE: June 2024 snapshot; current complete hospice requirements NOT CONFIRMED.'
        elif 'indexed' in note and 'opened' in note:
            status='MIXED OPENED / INDEXED EVIDENCE: full-text support for every paraphrase NOT CONFIRMED.'
        elif 'indexed' in note:
            status='INDEXED EXCERPT: full page/passage support NOT CONFIRMED.'
        elif s['id'].startswith('R'):
            status='PRIOR SOURCE RECORD: access described in note; each downstream statement NOT individually reverified.'
        else:
            status='SOURCE ACCESSED: access does not establish every linked statement is entailed or independently validated.'
        s['evidence_status']=status
    for r in roles:
        r['field_evidence']=dict(FIELD_LABELS)
        r['claim_audit_status']='NOT COMPLETED: no comprehensive sentence-by-sentence entailment audit of this dossier.'
        r['local_authority_confirmed']=False
    for d in decisions:
        if d['id'] in CHECKED_RULES:
            d['evidence_status']='CORE RULE PASSAGE-CHECKED WITHIN STATED SCOPE; other interpretation/local applicability not certified.'
            d['checked_core_rule']=dict(CHECKED_RULES[d['id']],checked_date='2026-10-17',displayed_edition='Title 42 through 2026-10-15')
        elif d['id']=='D33':
            d['evidence_status']='DATED EXAMPLE: current complete hospice requirements NOT CONFIRMED.'
        elif d['id'] in ['D11','D14']:
            d['evidence_status']='ORGANIZATION / PROCESS EXAMPLE: NOT CONFIRMED as a universal rule.'
        elif d['id'] in ['D24','D31']:
            d['evidence_status']='SYNTHESIZED INTERPRETATION / MODEL: NOT CONFIRMED as a required institutional procedure.'
        else:
            d['evidence_status']='SOURCE-LINKED INTERPRETATION: full claim-by-claim passage verification NOT COMPLETED; apply scope conditions.'
    for f in flows:
        f['evidence_status']='SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution\'s procedure.'
