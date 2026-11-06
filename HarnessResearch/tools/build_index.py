"""Publish research indexes and coverage metadata; no upstream imports/model calls."""
from collections import Counter
import json
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]


def read(path):return json.loads((BASE/path).read_text(encoding='utf-8'))


def write(path,text):
    p=BASE/path;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text('\n'.join(line.rstrip() for line in text.splitlines()).rstrip()+'\n',encoding='utf-8',newline='\n')


TOPICS=[
 ('01','Harness/model/agent/workflow boundaries','general/01-anatomy-and-control.md','G03 G07','H001 OC-003 C01 C02'),
 ('02','Task state, obligations and completion','general/01-anatomy-and-control.md','G08 G10 G14','H001 OC-006'),
 ('03','Provider adapters and native context ownership','general/08-providers-streaming-and-performance.md','G03 G04 G05 G07','H004 OC-003 OC-072'),
 ('04','Streaming and incomplete tool calls','general/08-providers-streaming-and-performance.md','G03','OC-006 C30 C31'),
 ('05','Tool contracts, discovery and response design','general/05-tools-execution-and-trust.md','G03 G11 G12 G13','OC-062'),
 ('06','Permissions, approval and execution authority','general/05-tools-execution-and-trust.md','G01 G02','H048 H049 H050 OC-063 OC-064'),
 ('07','Sandbox and deployment trust boundaries','general/05-tools-execution-and-trust.md','G01 G02','OC-065 OC-066 OC-067'),
 ('08','Prompt construction and instruction tiers','general/03-context-budget-and-compaction.md','G06 G09','H006 H008 H009'),
 ('09','Token accounting, reserves and effective triggers','general/03-context-budget-and-compaction.md','G05 G06','H012 H013 H014'),
 ('10','Prompt cache versus durable memory','general/08-providers-streaming-and-performance.md','G06 G08','H011'),
 ('11','Pruning, compaction and persisted projections','general/03-context-budget-and-compaction.md','G05 G09','H016 H018 OC-023 OC-024 OC-025 C04'),
 ('12','Tool-pair and provider protocol preservation','general/03-context-budget-and-compaction.md','G03 G05','C35'),
 ('13','Lossy summaries versus retained evidence','general/03-context-budget-and-compaction.md','G05 G08 G09','H016 C20'),
 ('14','Event logs, episodes and transcript recall','general/02-state-memory-and-sessions.md','G04 G08','H030 C03 C04'),
 ('15','Semantic facts/profile memory','general/04-memory-retrieval-and-learning.md','G08 G09','H019 H020 C15'),
 ('16','Procedural memory, skills and self-improvement','general/10-construction-guide.md','G08 G10','H042 H043 H044 H045'),
 ('17','Retrieval: exact/lexical/vector/hybrid/file alternatives','general/04-memory-retrieval-and-learning.md','G09','H030 C16 C17 C18'),
 ('18','Admission, consolidation and trust provenance','general/04-memory-retrieval-and-learning.md','G01 G02','OC-042 OC-045 OC-046'),
 ('19','Correction, deletion and derived lineage','general/04-memory-retrieval-and-learning.md','G16','OC-050 OC-051 OC-052'),
 ('20','Index freshness and source/version consistency','general/04-memory-retrieval-and-learning.md','G16 G17','H032 OC-038'),
 ('21','Session identity, branching, reset and resume','general/02-state-memory-and-sessions.md','G04','H033 H034 C03 C04'),
 ('22','Checkpoints and replay semantics','general/06-durability-replay-and-recovery.md','G15 G16 G17','C06 C07 C08 C09 C10 C11 C12'),
 ('23','External effects, idempotency and unknown outcomes','general/06-durability-replay-and-recovery.md','G15 G18','H002 H034 C11 C13'),
 ('24','Failure recovery, cancellation and restart','general/06-durability-replay-and-recovery.md','G15 G16','H017 OC-061 C13 C33 C34'),
 ('25','Writer ownership, fences and concurrent state','general/06-durability-replay-and-recovery.md','G16 G17','H003 OC-019 OC-020 OC-073'),
 ('26','Worker/mode/handoff/team alternatives','general/07-orchestration-concurrency-and-delegation.md','G09 G10','H038 OC-059 C01 C02'),
 ('27','Admission, queues, aggregate budgets and stops','general/07-orchestration-concurrency-and-delegation.md','G14 G15','H039 OC-057 OC-058'),
 ('28','Gateway, cron, heartbeat and background work','general/07-orchestration-concurrency-and-delegation.md','G15','H044 H045 H047 H060 OC-069 OC-070'),
 ('29','Tracing, privacy and actual resource accounting','general/09-observability-evaluation-and-maintenance.md','G06 G14','OC-071'),
 ('30','Evaluation, ablations and reserved evidence','general/09-observability-evaluation-and-maintenance.md','G14','H054 H055 H056 OC-074 OC-075'),
 ('31','Plugins, configuration and replaceable engines','general/10-construction-guide.md','G01 G07','H018 H059 OC-003'),
 ('32','Versioning, migration and documentation drift','general/09-observability-evaluation-and-maintenance.md','G04 G07','H006 H014 OC-024 OC-025 C21 C22'),
 ('33','Construction sequence and explicit contracts','general/10-construction-guide.md','G03 G08 G10 G15','H002 C11'),
 ('34','Failure catalog and executable teaching invariants','general/11-data-contracts-and-failure-catalog.md','G03 G15 G16 G18','H002 OC-073'),
 ('35','Local/hosted/managed runtime alternatives','general/08-providers-streaming-and-performance.md','G07','OC-003 OC-072'),
 ('36','Independent requirements rather than copied products','general/12-design-questions-and-learning-map.md','G10 G14','C01 C02 C16'),
 ('37','Error classification and bounded fallbacks','general/08-providers-streaming-and-performance.md','G05 G15','H017 H058'),
 ('38','Principal/case/agent scopes and memory ownership','general/02-state-memory-and-sessions.md','G01 G02 G04','H023 H037 H038 OC-067 C06')
]


def main():
    foundations=read('foundation_sources.json');hermes=read('hermes/evidence.json');claw=read('openclaw/evidence.json')
    comparative=read('comparative/evidence.json')['claims'];captured=read('comparative/sources.json')['sources']
    all_ids={x['id'] for x in [*hermes,*claw,*comparative]}
    # Topic citations are navigation references, not automated entailment judgments.
    for id,title,path,general,case in TOPICS:
        missing=set(case.split())-all_ids
        if missing:raise ValueError((id,missing))
    lines=['# Primary foundations and source status','',
        'General chapters are engineering analysis grounded in these primary sources; proposed contracts and tests are our synthesis. Product-specific behavior is recorded separately in the pinned case-study ledgers. Documentation support, static code traces, inspected tests and executed synthetic tests are different evidence categories. No exhaustive runtime or security audit is claimed.','']
    for s in foundations:
        lines += [f'<a id="{s["id"].lower()}"></a>',f'## {s["id"]} — {s["title"]}','',
            f'[{s["title"]}]({s["url"]})','', '**Status:** '+s['status']+'; checked '+s['checked_local_date'], '',
            '**Inspected location:** '+s['locator'],'','**Supported mechanism:** '+s['finding'],'','**Limit:** '+s['limit'],'']
    lines += ['## Versioned implementation evidence','',
        '[Hermes registry](hermes/evidence.json) and [OpenClaw registry](openclaw/EVIDENCE.md) link to exact commits, paths and line ranges. [Broader comparison](comparative/README.md) adds Pi, LangGraph and Letta plus scoped historical research; its [24 source receipts](comparative/sources.json) preserve hashes and current-versus-historical boundaries. [Pinned identities](source_versions.json) identify the two complete local checkouts; comparative source snapshots record their own repository pins.','',
        'Full source checkouts/public-page snapshots remain ignored. Hashes identify captured material; they do not prove factual entailment. General-source cache capture status is in verification/foundation_capture_receipt.json when run and is distinct from official web pages actually inspected during research.']
    write('SOURCES.md','\n'.join(lines))
    ledger=[]
    for system,records in [('hermes',hermes),('openclaw',claw),('comparative',comparative)]:
        for r in records:
            ledger.append(dict(id=r['id'],system=system,statement=r['statement'],status=r['status'],
                url=r.get('source_url') or r['url'],locator=(f"{r['source_path']}:{r['line_start']}-{r['line_end']}" if 'source_path' in r else r['locator']),limits=r['limits']))
    lines=['# Implementation and comparative finding index','',
        f'{len(ledger)} individually scoped findings across two deep source studies and the broader comparison. These are not {len(ledger)} executed tests or verified deployment guarantees. General construction recommendations remain engineering synthesis in the handbook.','',
        '| System | Evidence status | Findings |','| --- | --- | --- |']
    for (system,status),n in sorted(Counter((r['system'],r['status']) for r in ledger).items()):lines.append(f'| {system} | {status} | {n} |')
    for r in ledger:
        lines += ['', f'<a id="{r["id"].lower()}"></a>',f'## {r["id"]} — {r["system"]}', '',
            '**'+r['status']+'** — '+r['statement'],'',f'[Source: {r["locator"]}]({r["url"]})','', '**Limit:** '+r['limits']]
    write('FINDINGS_INDEX.md','\n'.join(lines))
    topics=[];lines=['# General knowledge coverage matrix','',
        'These 38 topics define the studied scope. “Covered” means a general mechanism, alternatives/limits and source/case navigation are documented; it does not mean every backend, model or failure mode was executed. Exact source claims are in the finding ledgers. Synthetic labs cover only their stated invariants.','',
        '| ID | Topic | General chapter | Selected primary/case evidence | Status |','| --- | --- | --- | --- | --- |']
    for id,title,path,general,case in TOPICS:
        topics.append(dict(id='K'+id,topic=title,chapter=path,foundation_ids=general.split(),finding_ids=case.split(),status='DOCUMENTED_GENERAL_ANALYSIS_WITH_SCOPED_REFERENCES',runtime_completeness_verified=False))
        links=', '.join(f'[{x}](SOURCES.md#{x.lower()})' for x in general.split())+'; '+', '.join(f'[{x}](FINDINGS_INDEX.md#{x.lower()})' for x in case.split())
        lines.append(f'| K{id} | {title} | [{Path(path).stem}]({path}) | {links} | Documented; runtime limits explicit |')
    write('COVERAGE.md','\n'.join(lines));write('verification/coverage.json',json.dumps(topics,indent=2))
    receipt=dict(date='2026-10-18',general_chapters=len(list((BASE/'general').glob('*.md'))),knowledge_topics=len(topics),
        foundation_sources=len(foundations),hermes_findings=len(hermes),openclaw_findings=len(claw),comparative_findings=len(comparative),
        implementation_and_comparative_findings=len(ledger),comparative_source_receipts=len(captured),
        statuses=dict(Counter(r['status'] for r in ledger)),upstream_runtime_executed=False,upstream_tests_executed=False,
        architecture_selected=False,scope='General engineering handbook with scoped case evidence; not literal exhaustive knowledge or proof of deployment behavior.')
    write('verification/build_receipt.json',json.dumps(receipt,indent=2));print(json.dumps(receipt,indent=2))


if __name__=='__main__':main()
