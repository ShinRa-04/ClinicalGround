"""Authored scoped diagrams; edges state their meaning explicitly."""
import re

COMMON = '''graph [rankdir=TB, bgcolor="white", fontname="Arial", fontsize=16, labelloc=t, pad=0.4, nodesep=0.4, ranksep=0.65];
node [shape=box, style="rounded,filled", fillcolor="#f0f5f8", fontname="Arial", fontsize=12, color="#8396a2", margin="0.18,0.14"];
edge [fontname="Arial", fontsize=10, color="#526e80", arrowsize=0.7];'''

GRAPHS = {
'authority-domains': COMMON + '''
graph [label="Separate authority domains | arrows assign a function, not universal rank"];
consent [label="Patient / lawful representative\nConsent and participation\nP01 / P03 | A01, A09"];
treatment [label="Authorized treating professional\nClinical recommendation / order\nC01-C05 | B01-B03, A15"];
coverage [label="Authorized payer reviewer\nCoverage determination\nU03-U07 | A02, A17; delegation"];
appeal [label="Applicable appeal decision-maker\nScoped review/reversal\nU13/U14/U18/J01-J03 | A03-A04, A11-A12"];
scope [label="Law + license + competence + privileges\nProfessional scope constraint\nA13-A15; not a job-rank ladder"];
policy [label="Applicable policy-governance body\nCriteria within governing coverage rules\nG03 | MA A05/A17"];
manager [label="Assigned operational manager\nWorkload and process\nO12/U17/G04/G05 | local mandate"];
case [shape=ellipse,fillcolor="#e2edf2",label="Case actions require the applicable\nauthorities together; one domain\ndoes not erase the others"];
consent -> case [label="participation decision"];
treatment -> case [label="clinical instruction"];
coverage -> case [label="benefit/authorization outcome"];
appeal -> coverage [label="may supersede disputed outcome\nONLY under applicable review route",style=dashed];
scope -> treatment [label="constrains permitted activity"];
scope -> coverage [label="constrains reviewer qualification"];
policy -> coverage [label="approved applicable criteria"];
manager -> case [label="operational allocation\nnot clinical/consent override"];
''',
'ma-appeals': COMMON + '''
graph [label="Medicare Advantage Part C review path | process review, not employment hierarchy\nA02-A04, A11, A16 | check integrated-plan route and actual eligibility"];
route [shape=diamond,label="Identify product / decision category\nApplicable integrated-plan route?\nA02(a) route check first"];
integrated [shape=note,label="If applicable: identify integrated-plan process\nDetailed integrated rules not audited here\nDo not apply this standard ladder blindly"];
U04 [label="Initial organization determination\nAppropriate authorized review\nA02: anticipated adverse medical necessity\nphysician OR other appropriate licensed expert"];
U13 [label="Plan reconsideration\nUninvolved decision-maker\nMedical-necessity denial: expert physician\nA03 / 422.590(h)"];
U14 [label="CMS-contracted independent entity\nRemaining disputed issues\nA04 / 422.592"];
J01 [label="Eligible ALJ / applicable adjudication"];
J02 [label="Eligible Medicare Appeals Council review"];
J03 [label="Eligible federal district court review"];
implementation [label="Plan implements applicable reversal\nA16 / 422.618\nDecision type and further-review exceptions matter"];
route -> U04 [label="standard MA route applies"];
route -> integrated [style=dashed,label="different applicable route"];
U04 -> U13 [label="proper reconsideration challenge"];
U13 -> U14 [label="remaining adverse issues under MA rules"];
U14 -> J01 [label="only if further appeal eligible/proper"];
J01 -> J02 [label="only if eligible/proper request"];
J02 -> J03 [label="only if legal prerequisites met"];
U13 -> implementation [style=dashed,label="applicable plan reversal"];
U14 -> implementation [style=dashed,label="applicable independent reversal"];
J01 -> implementation [style=dashed,label="applicable reversal; Council exception"];
J02 -> implementation [style=dashed,label="applicable higher decision"];
J03 -> implementation [style=dashed,label="applicable judicial disposition"];
''',
'commercial-appeals': COMMON + '''
graph [label="Applicable commercial external-review route | not the MA IRE ladder\nA12 / HealthCare.gov; R17 | determine plan, issue and state/federal process"];
eligibility [shape=diamond,label="Identify applicable plan / issue / process\nCheck ACA / non-grandfathered context\nR17; external eligibility is conditional"];
initial [label="Insurer adverse determination"];
internal [label="Applicable internal review / appeal\nQualification and procedure depend on product"];
U18 [label="Eligible independent external review\nU18: appropriate IRO route"];
implement [label="Insurer accepts applicable external outcome\nA12 describes binding acceptance\nNo treatment-consent or prescribing authority"];
eligibility -> initial [label="identified applicable process"];
initial -> internal [label="proper internal challenge / applicable process"];
internal -> U18 [label="only under applicable eligibility/rules\nexpedited routes require separate check"];
initial -> U18 [style=dashed,label="eligible urgent review may be requested\nconcurrently with internal appeal | V19\nnot required to finish all internal steps"];
U18 -> implement [label="external disposition under identified route"];
''',
'reporting-examples': COMMON + '''
graph [label="Documented reporting examples only | not a national organization chart\nSolid arrows = described supervision/management, never universal clinical override"];
subgraph cluster_ucsd {
label="UC San Diego role-description example | R14";color="#c3d0d8";
um [label="UM Manager (U17)"];
ncm [label="Assigned nurse case managers\nUM duties in this example\nM01/U03 function"];
ref [label="Assigned referral coordinators\nO02 function"];
um -> ncm [label="described supervision"];
um -> ref [label="described supervision"];
}
subgraph cluster_partnership {
label="Partnership HealthPlan role-description example | R32 pp.12-16";color="#c3d0d8";
director [label="Director of Care Coordination\nG04 leadership function"];
associate [label="Associate director\nG04 leadership function"];
managers [label="Department managers\nG04 function"];
supervisors [label="Assigned supervisors (G05)\nRN / LVN / nonclinical / social work\nDifferent scopes despite supervision titles"];
assigned [label="Assigned team members\nCase managers / social workers / guides\nActual assignment controls"];
director -> associate [label="under director direction"];
associate -> managers [label="manages / provides direction"];
associate -> supervisors [label="described direction"];
managers -> supervisors [style=dashed,label="collaborates in oversight\nnot a documented direct reporting edge"];
supervisors -> assigned [label="assigned supervision\nwithin actual scope"];
}
note [shape=note,fillcolor="#fff8e5",label="No physician-over-all-nurses or insurer-over-treating-doctor\nreporting edge is inferred. Obtain actual institution organogram,\nbylaws, privileges, delegation and service/product rules."];
'''
}


def create(write):
    result=[]
    for name, body in GRAPHS.items():
        status = ('SOURCE-SPECIFIC EXAMPLE: not confirmed for other institutions' if name=='reporting-examples'
                  else 'REVIEWED SCOPED SUMMARY: conditions and unresolved routes remain explicit')
        body = body.replace('graph [label="', 'graph [label="'+status+'\n', 1)
        body = re.sub(r'"(?:[^"\\]|\\.)*"', lambda m: m.group(0).replace('\n', r'\n'), body)
        write('graphs/'+name+'.dot', 'digraph '+name.replace('-','_')+' {\n'+body+'\n}')
        result.append(dict(name=name,title=name.replace('-',' ').title(),engine='dot',scope='See diagram labels and AUTHORITY.md',evidence_status=status))
    return result
