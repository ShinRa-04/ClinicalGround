"""Build traceable Markdown, JSON, DOT and a portable HTML reference; no network/Docker."""
from __future__ import annotations

import csv
import html
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
from role_definitions import ROLES
from decision_definitions import DECISIONS, FLOWS
from custom_graphs import create as create_custom_graphs
from evidence_labels import apply_labels
from deep_review import apply as apply_deep_review, report as generate_deep_report, review_blocks
from review_revision_delta import main as review_revisions

BASE = Path(__file__).resolve().parents[1]
PROJECT = BASE.parents[1]
DATE = '2026-10-17'
sys.path.insert(0,str(BASE/'verification'))
from apply_reviewed_corrections import apply as apply_corrections
apply_corrections(ROLES,DECISIONS)
BY_ID = {r['id']: r for r in ROLES}


def write(path, text):
    target = BASE / path
    target.parent.mkdir(parents=True, exist_ok=True)
    normalized = '\n'.join(line.rstrip() for line in text.splitlines()).rstrip() + '\n'
    target.write_text(normalized, encoding='utf-8', newline='\n')


def dump(path, obj):
    write(path, json.dumps(obj, ensure_ascii=False, indent=2))


def source_catalog():
    old = (PROJECT / 'Plan/Source/04-workflow-people-sources.md').read_text(encoding='utf-8')
    sources = []
    for match in re.finditer(r'^- \*\*(R\d+) — \[([^\]]+)\]\(([^)]+)\)\.\*\* (.+)$', old, re.M):
        id, title, url, note = match.groups()
        sources.append(dict(id=id, title=title, url=url, kind='Public primary-source role example/guidance',
            scope='Use stated organization/program; not universal legal authority', access='Prior research in this conversation, October 17, 2026; see note', locator='Relevant passages described in prior ledger', note=note))
    sources.extend(json.loads((BASE / 'data/additional_sources.json').read_text(encoding='utf-8')))
    for path in sorted((BASE/'verification').glob('additional_sources*.json')):
        sources.extend(json.loads(path.read_text(encoding='utf-8')))
    return {s['id']: s for s in sources}


SOURCES = source_catalog()
apply_labels(ROLES, DECISIONS, FLOWS, SOURCES)
apply_deep_review(ROLES,DECISIONS,SOURCES)


def refs(ids):
    return ', '.join(f"[{i}: {SOURCES[i]['title']}]({SOURCES[i]['url']})" for i in ids)


def role_link(id, prefix='roles/'):
    return f"[{id} {BY_ID[id]['title']}]({prefix}{id}.md)"


def text_list(items):
    return '\n'.join('- ' + item.rstrip('.') + '.' for item in items)


def relations():
    result = []
    for r in ROLES:
        for predecessor in r['upstream']:
            result.append(dict(id=f"DEP{len(result)+1:03}", sender=predecessor, receiver=r['id'],
                type='coordination_dependency', artifact='Relevant information/service context; see role inputs',
                available_work_products=BY_ID[predecessor]['outputs'], recipient_context_needs=r['inputs'],
                condition='Only when this role and pathway participate; not a universal mandatory predecessor',
                hard_gate=False, evidence='Operational synthesis from role responsibilities', sources=r['sources']))
            result[-1]['evidence_status']='SYNTHESIZED MODEL: this dependency is NOT CONFIRMED as an actual institutional relationship.'
    for f in FLOWS:
        result.append(dict(id=f['id'], sender=f['sender'], receiver=f['receiver'], type='information_handoff',
            artifact=f['artifact'], condition=f['condition'], hard_gate=False,
            evidence=f['evidence'], sources=f['sources']))
        result[-1]['evidence_status']=f['evidence_status']
    return result


RELATIONS = relations()

# Explicit mapping to every non-header row in the preceding participant inventory.
CROSSWALK = {
1:'P01',2:'P02',3:'P03',4:'P04',5:'P05 P06',6:'M10 P07',8:'C01',9:'C04 C05',10:'C02',11:'C03',12:'C06 C07 C08',13:'O01',14:'O02',15:'O03 O04',16:'O05',17:'O06',18:'O07 O08',19:'O09 M05',20:'O10',21:'O11',22:'O12',24:'U11 U01',25:'U03',26:'U04 U05',27:'O13 C03 M14',28:'M04 M05',29:'M25 M26',30:'U14 U18',32:'U01',33:'U02',34:'U03',35:'U04',36:'U05',37:'U06',38:'U07',39:'U08',40:'U09',41:'U10',42:'U11',43:'U12',44:'U13',45:'U14 U18 U15',46:'U16',47:'U17',48:'P01 P03 P04 C01 O01',50:'P01',51:'P02 P03',52:'M01',53:'C02 C01',54:'C04 C05',55:'C03',56:'C06',57:'M02 M03',58:'M04',59:'M05',60:'M06 M07 M08',61:'M09 M10 M11',62:'M12',63:'M13',64:'M14',65:'M15',66:'M16',67:'M17',68:'M18',69:'M19 M20',70:'M21',71:'M22',72:'M23 M24',73:'M25',74:'M27 M29',75:'M28',76:'M30 O05',77:'U02 U01 O04',78:'P05 P06',79:'P07 M31',81:'G01 G02',82:'G03 U05',83:'G04 G05',84:'G06',85:'G07',86:'G08 G09',87:'G10 O06',88:'G11 G12',89:'G13 G14',90:'G15 O10',91:'U15 G16 G17'}


def crosswalk():
    old = (PROJECT / 'Plan/WORKFLOW_PEOPLE.md').read_text(encoding='utf-8')
    rows = [line.split('|')[1].strip() for line in old.splitlines() if line.startswith('| ') and not line.startswith('| ---')]
    ignored = {'Person', 'Role', 'Participant', 'People/function'}
    result = []
    for index, label in enumerate(rows):
        if label in ignored:
            continue
        if index not in CROSSWALK:
            raise ValueError(f'Unmapped earlier role row {index}: {label}')
        result.append(dict(earlier_row=index, earlier_label=label, canonical_ids=CROSSWALK[index].split()))
    return result


COVERAGE = crosswalk()

# An explicit illustrative service interface for every role, not an observed institutional protocol.
# Primary contact is one modeled requester/recipient, not the exclusive owner of every input.
CONTACTS = dict(zip(
    [r['id'] for r in ROLES],
    ('C01 M01 C01 U12 C01 U09 P01 '
     'P01 P01 C02 P01 P01 C01 C06 C01 '
     'C01 C02 P01 O03 O02 O01 G15 O07 P01 O01 O10 O01 C01 '
     'O01 U01 U01 U03 U04 U01 U01 U01 U04 P01 O01 P04 U12 U13 P04 P01 U03 U15 '
     'C02 M01 M01 M01 M04 M01 M01 M01 M01 M01 M01 M01 M01 M01 M01 M01 C01 C01 M18 M18 M19 M10 M01 M23 C01 C01 C01 C01 M27 M01 M02 '
     'C01 U17 G08 M01 M01 G04 G04 G03 G04 O06 G04 G04 G12 O01 P01 G09 P04 '
     'P04 P04 G17').split()))
CONTACTS['M28']='C06'


def interfaces():
    assert len(CONTACTS)==len(ROLES) and all(x in BY_ID for x in CONTACTS.values())
    result=[]
    for r in ROLES:
        result.append(dict(id='S-'+r['id'], role=r['id'], primary_contact=CONTACTS[r['id']],
            request='Question/referral/task and available relevant context for: '+r['mission'],
            needs=r['inputs'], response=r['outputs'], decisions=r['decisions'], exclusions=r['limits'],
            acknowledgement='Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.',
            failure=r['escalation'], condition=r['condition'], sources=r['sources'],
            evidence_status='SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.',
            evidence='Illustrative synthesis, not a required sequence, exclusive contact, established employer protocol or additional decision authority.'))
    return result


INTERFACES=interfaces()


def generate_role_cards():
    index = ['# Role index', '', 'All roles are functions; multiple cards can describe one person. Read [scope and authority](AUTHORITY.md) before interpreting decision rights.', '', '| ID | Role | Domain |', '| --- | --- | --- |']
    for r in ROLES:
        id = r['id']
        downstream = sorted({e['receiver'] for e in RELATIONS if e['sender'] == id})
        handoffs = [f for f in FLOWS if id in (f['sender'], f['receiver'])]
        decisions = [d for d in DECISIONS if id in d['actors']]
        index.append(f"| {id} | [{r['title']}](roles/{id}.md) | {r['group']} |")
        blocks = [f"# {id} — {r['title']}", '', f"Domain: **{r['group']}**. Research date: {DATE}. [Role index](../ROLE_INDEX.md) · [Decision framework](../AUTHORITY.md)",
            '', '**Evidence warning:** '+r['claim_audit_status']+' Actual local authority: **NOT CONFIRMED**. See [evidence register](../EVIDENCE_REGISTER.md).',
            '', '## Purpose', '', '**Status:** '+r['field_evidence']['mission'], '', r['mission'],
            '', '## Responsibilities', '', '**Status:** '+r['field_evidence']['duties'], '', text_list(r['duties']),
            '', '## Decisions potentially within scope', '', '**Status:** '+r['field_evidence']['decisions'], '', text_list(r['decisions']),
            '', '## Authority not conferred merely by the title', '', '**Status:** '+r['field_evidence']['limits'], '', text_list(r['limits']),
            '', '## Incoming information and service context', '', '**Status:** '+r['field_evidence']['inputs'], '', text_list(r['inputs']),
            '', '## Outputs and responsibility for the work', '', '**Status:** '+r['field_evidence']['outputs'], '', text_list(r['outputs']),
            '', 'The role holder is responsible for the accuracy/provenance of their own work within the assignment. This is a functional responsibility statement, not a legal allocation of all institutional liability.',
            '', '## Dependencies and handoffs', '', '**Status:** '+r['field_evidence']['dependencies'], '', 'Upstream contacts (conditional; not necessarily approval gates):', '',
            '\n'.join('- ' + role_link(x, '') for x in r['upstream']),
            '', 'Downstream contacts receiving a dependency or handoff:', '',
            '\n'.join('- ' + role_link(x, '') for x in downstream) or '- None individually modeled; see outputs and actual local service owner.',
            '', f"[Dependency neighborhood](../graphs/role-{id}.svg) · [All-role network](../graphs/all-role-dependencies.svg)",
            '', '## Escalation', '', '**Status:** '+r['field_evidence']['escalation'], '', r['escalation'],
            '', '## Scope, reporting and authority conditions', '', '**Status:** '+r['field_evidence']['condition'], '', r['condition'],
            '', 'A reporting supervisor is not invented from this title. See the explicitly scoped [reporting examples](../graphs/reporting-examples.svg). Reporting rank does not itself decide consent, clinical scope, coverage or appeal authority.',
            '', '## Decision questions linked to this role', '',
            '\n'.join(f"- [{d['id']} — {d['question']}](../DECISIONS.md#{d['id'].lower()})" for d in decisions) or '- Apply the domain boundaries in AUTHORITY.md and the explicit rights above; no additional authority is implied.',
            '', '## Explicit handoff records', '',
            '\n'.join(f"- [{f['id']} — {f['artifact']}](../INFORMATION_FLOWS.md#{f['id'].lower()})" for f in handoffs) or '- No separately specified transaction contract. Upstream/downstream edges describe coordination context, not a mandatory institutional procedure.',
            '', f"An illustrative request/response interface is documented for this role in [S-{id}](../SERVICE_INTERFACES.md#s-{id.lower()}). It identifies a primary modeled contact and output without claiming every organization follows that sequence.",
            '', '## Evidence and interpretation', '', refs(r['sources']),
            '', *review_blocks(r['evidence_review_basis']),
            '', f"[Every inventoried assertion and its verdict](../verification/assertions/{id}.md). Inputs, outputs, dependency contacts and completion checks remain models and unconfirmed locally. Evidence supports the stated source scope; it does not certify actual local permission.",
            '', '## Completion / exception check', '',
            '- Confirm the correct person/case and applicable role permissions.',
            '- Preserve the author, version and status of the relevant output.',
            '- Communicate unresolved needs to the named appropriate role; do not silently convert uncertainty into a clinical decision or completed service.']
        write(f'roles/{id}.md', '\n'.join(blocks))
    write('ROLE_INDEX.md', '\n'.join(index))


def generate_tables():
    lines = ['# Decision matrix', '', 'A decision is scoped to a domain and process. The actors column does not mean every listed actor has identical authority.', '']
    for d in DECISIONS:
        lines += [f"<a id=\"{d['id'].lower()}\"></a>", f"## {d['id']} — {d['question']}", '',
            '**Evidence status:** '+d['evidence_status'], '',
            '**Domain:** ' + d['domain'], '', '**Actors:** ' + ', '.join(role_link(x) for x in d['actors']),
            '', '**Decision rule:** ' + d['rule'], '', '**Does not establish:** ' + d['cannot'],
            '', '**Review/escalation:** ' + d['review'], '', '**Applicability:** ' + d['condition'],
            '', '**Evidence:** ' + refs(d['sources']), '', *review_blocks(d['evidence_review_basis']),
            '', f"[Assertion review](verification/assertions/{d['id']}.md)", '']
    write('DECISIONS.md', '\n'.join(lines))
    lines = ['# Information-flow contracts', '', 'These are explicit illustrative handoff contracts, not a claim that each organization uses these forms or that every field is legally mandated. A cited regulation controls only its stated setting. Select a flow by ID in the diagrams.', '']
    for f in FLOWS:
        lines += [f"<a id=\"{f['id'].lower()}\"></a>", f"## {f['id']} — {f['artifact']}", '',
            '**Evidence status:** '+f['evidence_status'], '',
            f"**From → to:** {role_link(f['sender'])} → {role_link(f['receiver'])}",
            '', '**Condition:** ' + f['condition'], '', '**Suggested identifying/content fields:**', '', text_list(f['fields']),
            '', '**Acknowledgement/completion evidence:** ' + f['acknowledgement'],
            '', '**If missing, rejected or inconsistent:** ' + f['failure'],
            '', '**Evidence:** ' + refs(f['sources']), '']
    write('INFORMATION_FLOWS.md', '\n'.join(lines))
    lines=['# Illustrative service interfaces for every role', '', 'These request/response models make input/output responsibilities explicit for all roles. They are synthesized examples, not observed local protocols. A primary contact is one modeled requester/recipient, not a supervisor or the exclusive source of all information. Fields are suggested modeling fields, not universal legal mandates.', '']
    for s in INTERFACES:
        lines += [f'<a id="{s["id"].lower()}"></a>', f'## {s["id"]} — {BY_ID[s["role"]]["title"]}', '',
            '**Evidence status:** '+s['evidence_status'], '',
            '**Modeled contact ↔ role:** '+role_link(s['primary_contact'])+' ↔ '+role_link(s['role']),
            '', '**Request/context:** '+s['request'], '', '**Additional information needed:**', '',text_list(s['needs']),
            '', '**Response/work product:**', '',text_list(s['response']), '', '**Permitted decision domain:**', '',text_list(s['decisions']),
            '', '**Not granted by this interaction:**', '',text_list(s['exclusions']), '', '**Acknowledgement:** '+s['acknowledgement'],
            '', '**If unresolved:** '+s['failure'], '', '**Applicability:** '+s['condition'], '', '**Evidence:** '+refs(s['sources']), '']
    write('SERVICE_INTERFACES.md','\n'.join(lines))
    lines=['# Conditional dependency register', '', '**All 219 edges: SYNTHESIZED MODEL — NOT CONFIRMED actual institutional relationships.** Source context does not directly prove each arrow. Each DEP arrow identifies possible information/service context, not a required order, compulsory approval or command relationship. Sender work products do not imply the sender supplies every recipient input.', '', '| Edge / status | From | To | Available sender work product | Recipient context needs |', '| --- | --- | --- | --- | --- |']
    for e in RELATIONS:
        if e['type']!='coordination_dependency': continue
        lines.append(f"| {e['id']} — model / unconfirmed locally | {role_link(e['sender'])} | {role_link(e['receiver'])} | {'; '.join(e['available_work_products'])} | {'; '.join(e['recipient_context_needs'])} |")
    write('DEPENDENCIES.md','\n'.join(lines))
    lines = ['# Coverage of the earlier participant map', '', f'All {len(COVERAGE)} non-header rows in the previous map have explicit mappings below. These are not unique-person counts. Later MA adjudication roles J01–J03 are added to explain the requested appeal hierarchy.', '', '| Earlier role/function | Current dossiers |', '| --- | --- |']
    lines += [f"| {c['earlier_label']} | {', '.join(role_link(x) for x in c['canonical_ids'])} |" for c in COVERAGE]
    write('COVERAGE.md', '\n'.join(lines))
    lines = ['# Source catalogue', '', f'There are {len(SOURCES)} reference entries covering {len({s["url"] for s in SOURCES.values()})} distinct source URLs, including failed attempts. R19 and A09 identify the same HHS guidance; they are not independent sources. See [capture provenance](SOURCE_PROVENANCE.md).', '', 'Read the access note and scope before applying a source. Government occupational descriptions are not state practice acts. Organization-specific policies are examples. Current eCFR pages displayed Title 42 through October 15, 2026; hospice V11/V16/V17 establish the official 2025 codification, not a full 2026 update audit. A08 remains a dated fallback.', '']
    for s in sorted(SOURCES.values(), key=lambda x:x['id']):
        lines += [f"## {s['id']} — {s['title']}", '', f"[Primary source]({s['url']})", '',
            f"- Type: {s['kind']}", f"- Scope: {s['scope']}", f"- Access: {s['access']}",
            f"- Evidence status: {s['evidence_status']}",
            f"- Locator: {s['locator']}", f"- Note: {s['note']}", '']
    lines += ['## Access and evidence limits', '', 'Some direct eCFR requests and the advertised API failed (automated-access notice / HTTP 406). Already retrieved current sections remain documented. A08 uses an explicitly dated CMS manual transmittal rather than pretending the current full hospice rule was checked. Prior NCQA draft/inaccessible requirements remain excluded. Older sources and indexed-only evidence are marked in the prior ledger. No protected handbook, verifier expectations, interviews or clinical validation were used.']
    write('SOURCES.md', '\n'.join(lines))


def q(value):
    return json.dumps(value, ensure_ascii=False)


def dot_graph(name, title, ids, edges, engine='dot'):
    title='MODEL: NOT CONFIRMED institutional workflow\n'+title
    lines = [f'digraph {q(name)} {{', 'graph [rankdir=LR, overlap=false, splines=true, pad=0.35, nodesep=0.35, ranksep=0.8, bgcolor="white", fontname="Arial", fontsize=16, label='+q(title)+', labelloc=t];',
        'node [shape=box, style="rounded,filled", fillcolor="#f2f5f7", color="#94a3b8", fontname="Arial", fontsize=11, margin="0.14,0.1"];',
        'edge [color="#718096", fontname="Arial", fontsize=9, arrowsize=0.65];']
    for id in sorted(ids):
        r = BY_ID[id]
        title_lines = '\n'.join(re.findall(r'.{1,29}(?:\s|$)', r['title'])) or r['title']
        lines.append(f'{id} [label={q(id+chr(10)+title_lines)}, URL={q("../index.html#"+id)}, target="_top"];')
    if engine == 'sfdp':
        lines[1] = lines[1].replace('overlap=false', 'overlap=scale')
    for e in edges:
        label = e['id'] + (' | ' + e['artifact'] if e['type']=='information_handoff' else '')
        lines.append(f"{e['sender']} -> {e['receiver']} [label={q(label)}, tooltip={q(e['condition'])}];")
    lines.append('}')
    write('graphs/'+name+'.dot', '\n'.join(lines))
    return dict(name=name, title=title, engine=engine, nodes=len(ids), edges=len(edges),evidence_status='SYNTHESIZED MODEL / NOT CONFIRMED institutional workflow')


def generate_graphs():
    graphs=[]
    dependencies=[e for e in RELATIONS if e['type']=='coordination_dependency']
    graphs.append(dot_graph('all-role-dependencies','All-role coordination dependencies | conditional, not command or mandatory approval',set(BY_ID),dependencies,'dot'))
    interface_edges=[]
    for s in INTERFACES:
        for sender,receiver,direction in [(s['primary_contact'],s['role'],'request'),(s['role'],s['primary_contact'],'response')]:
            interface_edges.append(dict(id=s['id']+' '+direction,sender=sender,receiver=receiver,type='model_interface',artifact=direction,condition=s['condition']))
    graphs.append(dot_graph('all-role-information','All-role illustrative request/response interfaces | not an institutional protocol',set(BY_ID),interface_edges,'dot'))
    for group in ['provider','payer','care','governance','appeal']:
        selected={r['id'] for r in ROLES if r['group']==group}
        edges=[e for e in dependencies if e['receiver'] in selected]
        ids=selected|{e['sender'] for e in edges}
        graphs.append(dot_graph(group+'-dependencies',group.title()+' dependencies | arrow = conditional information/service context',ids,edges))
    flow_groups={'provider-information':range(1,16),'payer-appeal-information':range(7,21),'care-information':range(21,37),'governance-information':range(36,47)}
    for name, seq in flow_groups.items():
        edges=[e for e in RELATIONS if e['type']=='information_handoff' and int(e['id'][1:]) in seq]
        ids={x for e in edges for x in [e['sender'],e['receiver']]}
        graphs.append(dot_graph(name,name.replace('-',' ').title()+' | arrow = named information handoff; F ID links to contract',ids,edges))
    for r in ROLES:
        edges=[e for e in dependencies if r['id'] in [e['sender'],e['receiver']]]
        edges += [e for e in interface_edges if e['id'].startswith('S-'+r['id']+' ')]
        ids={r['id']}|{x for e in edges for x in [e['sender'],e['receiver']]}
        graphs.append(dot_graph('role-'+r['id'],r['id']+' dependency neighborhood | conditional contacts, not supervisors',ids,edges))
    graphs += create_custom_graphs(write)
    dump('data/graph_manifest.json', graphs)
    return graphs


def h(value):
    return html.escape(value, quote=True)


def generate_html(graphs):
    sections=[]
    for r in ROLES:
        id=r['id']
        parts=[f'<article id="{id}" class="role" data-search="{h((id+" "+r["title"]+" "+r["group"]).lower())}"><h2>{id} · {h(r["title"])}</h2><p class="tag">{h(r["group"])}</p><p><strong>Defined assertion inventory reviewed. Actual local authority NOT CONFIRMED.</strong></p><p>{h(r["mission"])}</p>']
        for key,title in [('duties','Responsibilities'),('decisions','Decisions potentially within scope'),('limits','Authority not conferred by this title'),('inputs','Inputs'),('outputs','Outputs')]:
            parts.append(f'<h3>{title}</h3><p><strong>Status:</strong> {h(r["field_evidence"][key])}</p><ul>'+''.join('<li>'+h(x)+'</li>' for x in r[key])+'</ul>')
        parts += ['<h3>Reviewed evidence and limits</h3><p>'+h(r['evidence_review_basis']['rationale'])+'</p><h3>Other documented possibilities</h3><p>'+h(r['evidence_review_basis']['alternatives'])+'</p><h3>Complexity and unresolved facts</h3><p>'+h(r['evidence_review_basis']['complexity'])+'</p>',
            f'<p><a href="verification/assertions/{id}.md">Assertion-by-assertion verdicts and passage locations</a></p>',
            '<h3>Escalation</h3><p><strong>Synthesized routing; NOT CONFIRMED local procedure.</strong></p><p>'+h(r['escalation'])+'</p><h3>Applicability and local permissions</h3><p>'+h(r['condition'])+'</p>',
            '<p>Reporting rank is not inferred. Source links are not blanket confirmation; proposed contracts and dependency relationships are unconfirmed models.</p>',
            '<p>Upstream: '+', '.join(f'<a href="#{x}">{x} {h(BY_ID[x]["title"])}</a>' for x in r['upstream'])+'</p>',
            f'<p><a href="roles/{id}.md">Full Markdown dossier</a> · <a href="graphs/role-{id}.svg">Dependency graph</a></p>',
            '<p>Sources: '+', '.join(f'<a href="{h(SOURCES[x]["url"])}" target="_blank" rel="noopener">{x}</a>' for x in r['sources'])+'</p></article>']
        sections.append(''.join(parts))
    graph_items=''.join(f'<li><a href="graphs/{g["name"]}.svg">{h(g["title"])}</a></li>' for g in graphs if not g['name'].startswith('role-'))
    page='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Healthcare roles and authority reference</title><style>
body{margin:0;font:16px/1.6 system-ui,sans-serif;color:#19252c;background:#f4f6f7}header,main{max-width:1050px;margin:auto;padding:24px}header{background:#e7eef1}h1{line-height:1.2}h2{line-height:1.3}a{color:#155779}input,select{font:inherit;padding:10px;border:1px solid #81939b;border-radius:4px;max-width:100%}.filters{position:sticky;top:0;padding:12px;background:#e7eef1;display:flex;gap:12px;flex-wrap:wrap;z-index:1}.role{background:white;padding:24px;margin:24px 0;border:1px solid #c9d4d9;border-radius:6px;scroll-margin-top:100px}.role[hidden]{display:none}.tag{font-weight:600;color:#48616d}h3{font-size:1rem;margin-bottom:0}ul{margin-top:6px}small{color:#49616c}summary{cursor:pointer;font-weight:600}li{margin:4px 0}@media print{.filters{position:static}article{break-inside:avoid}a{color:inherit}}</style></head><body><header><h1>Healthcare roles, decisions and information flow</h1>
<p>US workflow reference · October 17, 2026 · 97 role/function profiles. Roles can overlap in one person. Conditional connections do not mean command authority or mandatory approval.</p>
<p><strong>2,218 defined assertion units reviewed, with scoped verdicts and explicit uncertainties.</strong> This does not mean every assertion is confirmed true. Workflow arrows, fields and contacts remain synthesized models. <a href="EVIDENCE_REGISTER.md">Evidence review</a> · <a href="FINDINGS.md">Corrections and complexities</a> · <a href="verification/README.md">Assertion ledger</a>.</p>
<p><a href="README.md">Reading guide</a> · <a href="AUTHORITY.md">Authority and scope</a> · <a href="DECISIONS.md">34 decision questions</a> · <a href="INFORMATION_FLOWS.md">46 handoffs</a> · <a href="SOURCES.md">Evidence and access limits</a> · <a href="COVERAGE.md">Earlier-map coverage</a></p>
<details><summary>Open a diagram</summary><ul>'''+graph_items+'''</ul></details></header><main><div class="filters"><label>Find role <input id="search" type="search" placeholder="e.g. U13, pharmacist, caregiver"></label><label>Domain <select id="group"><option value="">All</option><option>shared</option><option>provider</option><option>payer</option><option>care</option><option>governance</option><option>appeal</option></select></label><span id="count" role="status"></span></div>'''+''.join(sections)+'''</main><script>
const search=document.getElementById('search'),group=document.getElementById('group'),cards=[...document.querySelectorAll('.role')];function filter(){const query=search.value.trim().toLowerCase();let n=0;for(const card of cards){const show=card.dataset.search.includes(query)&&(!group.value||card.querySelector('.tag').textContent===group.value);card.hidden=!show;if(show)n++;}document.getElementById('count').textContent=n+' roles shown';}search.addEventListener('input',filter);group.addEventListener('change',filter);function reveal(){if(location.hash){search.value='';group.value='';filter();document.getElementById(location.hash.slice(1))?.scrollIntoView();}}window.addEventListener('hashchange',reveal);filter();reveal();</script></body></html>'''
    write('index.html', page)


def validate_data():
    assert len(BY_ID)==len(ROLES)==97
    assert len(SOURCES)==95, len(SOURCES)
    for r in ROLES:
        for field in ['mission','duties','decisions','limits','inputs','outputs','escalation','sources','upstream','condition']:
            assert r[field], (r['id'],field)
    for record in [*ROLES,*DECISIONS,*FLOWS,*RELATIONS]:
        assert all(x in SOURCES for x in record['sources']), record
    for e in RELATIONS:
        assert e['sender'] in BY_ID and e['receiver'] in BY_ID
        assert e['sender']!=e['receiver']
        assert e['type'] in ['coordination_dependency','information_handoff']
        assert e['hard_gate'] is False
    assert all(id in BY_ID for c in COVERAGE for id in c['canonical_ids'])
    mapped={x for c in COVERAGE for x in c['canonical_ids']}
    assert set(BY_ID)-mapped=={'J01','J02','J03'}, set(BY_ID)-mapped


def main():
    validate_data()
    dump('data/sources.json',list(SOURCES.values()))
    dump('data/roles.json',ROLES)
    dump('data/decisions.json',DECISIONS)
    dump('data/information_flows.json',FLOWS)
    dump('data/relations.json',RELATIONS)
    dump('data/coverage.json',COVERAGE)
    dump('data/service_interfaces.json',INTERFACES)
    dump('data/evidence_review.json',dict(date=DATE,defined_inventory_adjudication_completed=True,
        reviewed_assertion_units=2218,pending_assertion_units=0,every_finding_confirmed_true=False,
        local_institutional_authority_confirmed=False,
        source_access_is_not_claim_verification=True,
        checked_core_rules=[dict(id=d['id'],**d['checked_core_rule'],url=SOURCES[d['checked_core_rule']['source']]['url']) for d in DECISIONS if 'checked_core_rule' in d],
        unconfirmed_models=dict(dependency_edges=219,handoff_contracts=46,service_interfaces=97),
        limitation='All defined assertion units have scoped authored judgments, with alternatives and unresolved facts. Composite units and explicit models are included; not independent clinical/legal certification.'))
    generate_role_cards()
    generate_tables()
    graphs=generate_graphs()
    review_revisions(quiet=True)
    generate_deep_report(write,ROLES,DECISIONS,SOURCES)
    generate_html(graphs)
    summary=dict(date=DATE,roles=len(ROLES),source_entries=len(SOURCES),distinct_source_urls=len({s['url'] for s in SOURCES.values()}),decisions=len(DECISIONS),
        handoffs=len(FLOWS),dependencies=sum(e['type']=='coordination_dependency' for e in RELATIONS),
        legacy_rows=len(COVERAGE),interfaces=len(INTERFACES),generated_graphs=len(graphs),schema_checks='passed',
        defined_inventory_adjudication_completed=True,reviewed_assertion_units=2218,pending_assertion_units=0,
        every_finding_confirmed_true=False,actual_institutional_authority_verified=False,
        interpretation='Authored evidence dispositions for the frozen inventory; models and unresolved facts remain explicit. Not independent clinical/legal validation.')
    dump('data/build_receipt.json',summary)
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    main()
