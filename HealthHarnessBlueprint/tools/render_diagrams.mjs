// Render hypothetical documentation only; no healthcare runtime/provider calls.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),base=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),root=path.resolve(base,'..');
const modulePath=path.join(root,'Runner/.cache/role-docs-toolchain/node_modules/@viz-js/viz/dist/viz.cjs');
const {instance}=require(modulePath),viz=await instance();
const common='graph [rankdir=TB,fontname="Arial",fontsize=15,labelloc=t,pad=0.35,nodesep=0.45,ranksep=0.65,bgcolor="white"];node [shape=box,style="rounded,filled",fillcolor="#edf3f6",color="#8396a2",fontname="Arial",fontsize=11,margin="0.15,0.12"];edge [fontname="Arial",fontsize=9,color="#526e80",arrowsize=0.7];';
const diagrams={
'organization':`${common}
graph [label="PROPOSED WORKING ORGANIZATION | one supplied environment, not a second world"];
work [label="Actual χ-Bench task / current stage\nSupplied instruction and tool scope"];
board [label="Work routing and ownership board\nScoped task references\nNo global patient chart in every prompt"];
pa [label="Provider PA composite job\n18 responsibility contracts",URL="../COMPOSITION.md"];
um [label="Payer UM composite job\n18 responsibility contracts\nSeparate principal / review stages",URL="../COMPOSITION.md"];
cm [label="CM composite job\n20 responsibility contracts",URL="../COMPOSITION.md"];
support [label="Scoped capabilities and interfaces\nEvidence / policy / coding / artifacts\nDialogue / referral / discipline support"];
kernel [label="Shared kernel: 10 support responsibilities\nPatient barrier / context / provenance\nTools / actions / budgets / checkpoints"];
env [label="χ-Bench supplied records and tools\nActual counterparties and observations\nOfficial evaluation stays outside acting inputs"];
work -> board [label="assigned work, not all stages"];
board -> pa;board -> um;board -> cm;
pa -> support [label="needed contributions"];um -> support;cm -> support;
support -> kernel [label="scoped request / result"];
kernel -> env [label="actual permitted operations"];
env -> kernel [label="observed outcome / unknown"];
`,
'composite-roles':`${common}
graph [label="PROPOSED DECOMPOSITION | responsibility does not imply a separate person or model call"];
owner [label="PA specialist: composite job owner\nOwn the assigned outcome and pending work"];
orient [label="PA-01–05\nRequest / identity / coverage\nRequirement / policy applicability",URL="../MICRO_ROLES.md#pa-01"];
evidence [label="PA-06–09\nEvidence / criteria links\nGaps / clinical clarification",URL="../MICRO_ROLES.md#pa-06"];
packet [label="PA-10–13\nCoding / packet / preflight\nActual submission",URL="../MICRO_ROLES.md#pa-10"];
response [label="PA-14–18\nActual response / RFI / dispute\nAccess handoff / closure",URL="../MICRO_ROLES.md#pa-14"];
forms [label="Choose execution arrangement\nCombined owner / bounded helpers\nSelected role workers",URL="../COMPOSITION.md"];
support [label="SH-01–10 shared mechanisms\nDeterministic functions where sufficient\nCase-scoped reasoning where useful",URL="../MICRO_ROLES.md#sh-01"];
owner -> orient [label="only needed outputs"];owner -> evidence;owner -> packet;owner -> response;
orient -> forms;evidence -> forms;packet -> forms;response -> forms;
forms -> support [label="same contract / scope / evidence obligations"];
`,
'case-execution':`${common}
graph [label="PROPOSED CASE FLOW | no mandatory PA→UM→CM tour"];
task [label="Actual task and observed starting stage"];
scope [label="Resolve principal / patient / case\nProtected request and obligations"];
job [label="Assign composite job\nSelect required responsibility outputs"];
reason [label="Combined reasoning or scoped helpers\nNo other patient data / learned habits"];
gate [shape=diamond,label="Actual scope / evidence / arguments\nready for the requested operation?"];
clarify [label="Clarify / retrieve / retain unknown\nBounded next step, not fabricated evidence"];
tool [label="Actual tool dispatch / intent identity\nObserve result and permitted readback"];
state [label="Update case-local obligations\nUnknown external effect stays unknown"];
done [shape=diamond,label="What does observed evidence\nestablish for the assigned work?"];
close [label="Truthful completion / exception\nRemaining work and owner explicit"];
task -> scope -> job -> reason -> gate;
job -> done [style=dashed,label="existing evidence may already suffice"];
gate -> clarify [label="no / unknown"];clarify -> reason [style=dashed,label="if required and permitted"];
clarify -> close [style=dashed,label="bounded unresolved / exception report"];
gate -> tool [label="yes"];tool -> state -> done;
done -> job [label="more work within scope / budget"];done -> close [label="completion / exception / explicit unresolved report"];
`,
'patient-isolation':`${common}
graph [label="DESIGN REQUIREMENT, NOT IMPLEMENTED | no patient-derived influence across patients"];
general [label="Approved reusable job definitions\nGeneral procedures / applicable reference versions\nRead-only to patient-runtime work"];
subgraph cluster_a {label="Patient A / task A namespace";color="#afc8d5";
dataA [label="A records / answers / source references"];
jobA [label="A composite owner and bounded helpers"];
memA [label="A notes / summaries / episodes\nCheckpoint / actions / artifacts"];
dataA -> jobA;jobA -> memA;memA -> jobA [label="same allowed case scope"];
}
subgraph cluster_b {label="Patient B / task B namespace";color="#afc8d5";
dataB [label="B records / answers / source references"];
jobB [label="B composite owner and bounded helpers"];
memB [label="B notes / summaries / episodes\nCheckpoint / actions / artifacts"];
dataB -> jobB;jobB -> memB;memB -> jobB [label="same allowed case scope"];
}
stop [shape=octagon,fillcolor="#fff0ed",label="No cross-patient retrieval/context\nNo automatic patient-derived shared\nprofiles, habits, procedures or learning"];
general -> jobA [label="general definitions only"];general -> jobB [label="general definitions only"];
memA -> stop [style=dashed,color="#a94534",arrowhead=tee];memB -> stop [style=dashed,color="#a94534",arrowhead=tee];
`,
'memory-context':`${common}
graph [label="PROPOSED CASE MEMORY | authoritative observations and derived working views stay distinct"];
env [label="Supplied case records / tool responses"];
caseview [label="Source-linked case working view\nTask / stage / obligations / unknowns"];
episodes [label="Case-local dialogue and episodes\nActual speakers / answers / refusals"];
checkpoint [label="Case checkpoint / action journal\nSource versions / pending and unknown effects"];
approved [label="Approved general knowledge\nNo patient-derived automatic updates"];
builder [label="Scoped context builder\nActive request / role / relevant evidence\nCoherent exchanges and bounded recall"];
model [label="One scoped model request\nActual provider budget/state contract"];
env -> caseview [label="observed facts / provenance"];
env -> episodes [label="actual interaction"];
caseview -> checkpoint;episodes -> checkpoint;
caseview -> builder;episodes -> builder;checkpoint -> builder;approved -> builder;
builder -> model [label="filter / render / measure / reserve"];
`};
fs.mkdirSync(path.join(base,'graphs'),{recursive:true});const results=[];
for(const [name,body] of Object.entries(diagrams)){
 const normalized=body.replaceAll('χ-Bench','CHI-Bench').replaceAll('–','-').replaceAll('→',' -> ');
 const dot='digraph '+name.replaceAll('-','_')+' {\n'+normalized+'\n}\n';
 fs.writeFileSync(path.join(base,'graphs',name+'.dot'),dot);
 const result=viz.render(dot,{format:'svg',engine:'dot'});
 if(result.status!=='success'||result.output.includes('NaN'))throw new Error(JSON.stringify({name,errors:result.errors}));
 fs.writeFileSync(path.join(base,'graphs',name+'.svg'),result.output);
 results.push({name,warnings:result.errors||[],bytes:Buffer.byteLength(result.output)});
}
const receipt={date:'2026-10-18',renderer:'@viz-js/viz',version:JSON.parse(fs.readFileSync(path.join(path.dirname(modulePath),'../package.json'),'utf8')).version,diagrams:results.length,results,scope:'Hypothetical documentation only; no agent runtime, actual task mapping, isolation enforcement or benchmark result.'};
fs.mkdirSync(path.join(base,'verification'),{recursive:true});fs.writeFileSync(path.join(base,'verification/render_receipt.json'),JSON.stringify(receipt,null,2)+'\n');
console.log(JSON.stringify({diagrams:results.length,warnings:results.reduce((n,r)=>n+r.warnings.length,0)},null,2));
