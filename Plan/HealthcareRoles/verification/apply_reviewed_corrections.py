"""Apply specific source-reviewed corrections/clarifications, preserving the baseline inventory."""

CORRECTIONS = [
 {'id':'FIX01','targets':['C05'],'change':'Recognize physician assistant/associate terminology and jurisdiction-specific collaboration rather than a universal supervision model.','sources':['V03','B02']},
 {'id':'FIX02','targets':['M02'],'change':'Remove the misleading medical/nonclinical binary; distinguish job title, supervised pre-licensure work and independent clinical licensure.','sources':['R25','B09']},
 {'id':'FIX03','targets':['U01','U02','D11'],'change':'Add limited delegated nonclinical approvals/benefit-only decisions as a published program alternative; keep medical-necessity denials distinct.','sources':['R13']},
 {'id':'FIX04','targets':['U08'],'change':'Make retained health-plan appeals explicit in the AZPC delegation example.','sources':['R13']},
 {'id':'FIX05','targets':['C04'],'change':'Separate NP practice category, furnishing authority and employer conditions; flag prospective/stale availability wording.','sources':['V02']},
 {'id':'FIX06','targets':['M04','D25'],'change':'Clarify separately authorized pharmacist therapy activity and avoid implying a new physician instruction for every protocol-authorized action.','sources':['V13','B07']},
 {'id':'FIX07','targets':['M07','D26'],'change':'Add New Mexico additional prescribing-certification example without implying general psychologist prescribing rights.','sources':['V04']},
 {'id':'FIX08','targets':['M28','D33','S-M28'],'change':'Use official 2025 codification to distinguish interdisciplinary planning, designated RN coordination, attending, certification and admission; retain edition limit.','sources':['V11','V16','V17','R34']},
 {'id':'FIX09','targets':['D16','commercial-appeals'],'change':'Show eligible urgent internal/external review concurrently and qualify applicable plan/process scope.','sources':['V19','R17','A12']},
 {'id':'FIX10','targets':['D27','G10','O06'],'change':'Add applicable Part 2 protections to prevent treating the HIPAA minimum-necessary treatment exception as unrestricted sharing.','sources':['V15','A10']},
 {'id':'FIX11','targets':['reporting-examples'],'change':'Distinguish documented associate-director direction from manager/supervisor collaboration; do not imply an unsupported direct reporting chain.','sources':['R32']},
 {'id':'FIX12','targets':['R03','R23','WORKFLOW_PEOPLE'],'change':'Stop using expired/unavailable sources as current proof; replace relevant examples with accessible Noyes/Michigan and care-program sources.','sources':['R04','R05','R24','R25','R32']},
 {'id':'FIX13','targets':['M23','M24','M31','G14','G15','G17'],'change':'Add specific public context for transport, protection, access-control, billing and legal functions while keeping composite/local mandate limits.','sources':['V05','V14','V12','V08','V18','V07']},
 {'id':'FIX14','targets':['U03','U04','U06','U07'],'change':'Record tension between a program\'s professional categories and medical-director final responsibility; do not infer a case signatory without clarification.','sources':['R13']},
 {'id':'FIX15','targets':['ma-appeals'],'change':'Place an explicit product/integrated-plan route check before applying the standard MA path; detailed integrated rules remain outside verified scope.','sources':['A02','A03']}
]


def apply(roles,decisions):
    r={x['id']:x for x in roles};d={x['id']:x for x in decisions}
    for x in roles:
        x['sources']=[s for s in x['sources'] if s not in ['R03','R23']]
    for x in decisions:
        x['sources']=[s for s in x['sources'] if s not in ['R03','R23']]
    def add(id,*sources):
        for source in sources:
            if source not in r[id]['sources']:r[id]['sources'].append(source)
    r['C05']['title']='Physician assistant / associate (jurisdiction-specific title)';add('C05','V03')
    r['C04']['condition']+=' California examples separate practice category, furnishing authority and employer requirements. Prospective 104-availability wording is not proof of present individual certification or application availability.';add('C04','V02')
    add('C08','B02')
    add('O01','R05')
    r['U01']['decisions'][0]='Make operational decisions and only explicitly delegated limited nonclinical/benefit decisions under the applicable program criteria'
    r['U01']['condition']+=' R13 describes some limited nonclinical approvals and assigned benefit-only decisions; it is not a national permission or medical-necessity-denial grant.'
    r['U02']['condition']+=' R13 permits some assigned benefit-only decisions; actual signatory authority still requires the plan/delegation.'
    r['U08']['condition']+=' In R13, AZPC explicitly retains no delegation to process, decide or notify appeals; the plan handles that review.'
    for id in ['U03','U04','U06','U07']:
        r[id]['condition']+=' R13 has both a wider professional-category list and medical-director final-responsibility language. Specific case review/signoff must be clarified, not inferred from either statement alone.'
    r['M01']['condition']+=' Published staffing examples differ; this is not evidence of national role prevalence.';add('M01','R24')
    r['M02']['title']='Medical social worker (credential-dependent practice)'
    r['M02']['condition']+=' UCLA describes a pre-licensure Clinical Social Worker II assignment; clinical job wording does not establish independent clinical licensure.'
    add('M04','V13');r['M04']['condition']+=' Washington CDTA is one documented pathway for specified therapy activity; no universal requirement for a new physician instruction on each authorized action is inferred.'
    add('M07','V04');r['M07']['condition']+=' New Mexico documents additional conditional/full prescribing certification; ordinary psychology licensure alone does not establish it.'
    r['M14']['condition']+=' No particular state direct-access rule was established in this audit; attempted V20 was unavailable and is not used as proof.'
    for id in ['M23','M24']:add(id,'V05','V14')
    r['M28']['title']='Hospice interdisciplinary group and attending functions (distinct roles)'
    r['M28']['mission']='Coordinate hospice care while distinguishing interdisciplinary, RN coordination, attending and certifying/admission functions.'
    r['M28']['duties']=[
        'Prepare and review an interdisciplinary written care plan as specified in the cited hospice edition',
        'Use the designated interdisciplinary-group RN coordination function described in that edition',
        'Keep attending, terminal-illness certification and admission recommendation responsibilities distinct']
    r['M28']['upstream']=['P01','C01','C06']
    r['M28']['condition']='V11, V16 and V17 are the official October 2025 codification, not a complete current-2026 update check. They distinguish IDG/designated RN coordination, physician certification and admission. A patient-designated attending may have a different allowed credential; that does not grant every attending terminal-illness certification authority.'
    add('M28','V11','V16','V17')
    add('M31','V12');r['M31']['condition']+=' The cited 2024 APS fact sheet has a 2028 full-compliance date; it does not prove uniform present implementation in every state or child-protection setting.'
    for id,source in [('G14','V08'),('G15','V18'),('G17','V07'),('O06','V15'),('G10','V15')]:add(id,source)
    d['D05']['sources'].append('V02');d['D06']['sources'].append('V03')
    d['D07']['sources'].append('V10')
    d['D11']['actors']=['U01','U02','U03','U04','U06','U07']
    d['D11']['rule']='Published programs may permit limited nonclinical approvals under explicit criteria and assigned benefit decisions, alongside licensed clinical review and escalation; authority is delegation- and product-specific.'
    d['D11']['condition']+=' R13 also states medical-director final responsibility and wider professional categories; exact case signoff needs clarification.'
    d['D16']['sources']+=['V19']
    d['D16']['condition']+=' Check the applicable ACA/non-grandfathered context and actual external-review eligibility. Eligible urgent external review may be requested concurrently with internal appeal.'
    d['D21']['sources']+=['R24','R32']
    d['D25']['sources'].append('V13');d['D26']['sources'].append('V04')
    d['D27']['sources'].append('V15')
    d['D27']['condition']+=' Applicable Part 2 records and separate SUD counseling notes illustrate additional consent distinctions; a HIPAA minimum-necessary exception is not blanket disclosure permission.'
    d['D33']['rule']='The official October 2025 hospice codification distinguishes the interdisciplinary group/designated RN coordination from attending, physician certification and admission responsibilities.'
    d['D33']['condition']='V11/V16/V17 establish that codified edition; a complete current-2026 update audit and actual hospice assignment are not established.'
    d['D33']['sources']+=['V11','V16','V17','R34']
    for x in [*roles,*decisions]:x['sources']=list(dict.fromkeys(x['sources']))
