// Render only proposed study diagrams; no browser, network or benchmark execution.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),base=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(base,'../..');
const modulePath=path.join(root,'Runner/.cache/role-docs-toolchain/node_modules/@viz-js/viz/dist/viz.cjs');
const {instance}=require(modulePath),viz=await instance();
const common='graph [rankdir=TB,fontname="Arial",fontsize=15,labelloc=t,pad=0.35,nodesep=0.4,ranksep=0.8,bgcolor="white"];node [shape=box,style="rounded,filled",fillcolor="#edf3f6",color="#8396a2",fontname="Arial",fontsize=11,margin="0.15,0.12"];edge [fontname="Arial",fontsize=9,color="#526e80",arrowsize=0.7];';
const bodies={
'owner-specialists':`${common}
graph [label="PROPOSED / UNTESTED | one owner with explicit modes and bounded helpers"];
task [label="Actual assigned instruction\nand allowed tools / scope"];
owner [label="Accountable case owner\nNamed role modes and obligations\nProposed owner of mutable case actions"];
state [label="Case state / evidence references\nSources, versions, actual observations\nUnknowns and pending obligations"];
specialist [label="On-demand specialist contexts\nBounded evidence / policy question\nNo assumed finalization authority"];
environment [label="Supplied benchmark environment\nPatient/counterparty responses\nAuthoritative tool outcomes"];
scope [label="Actual task permissions / policy\nExplicit operation and data scope\nPrompt title does not grant authority",shape=note,fillcolor="#fff7e2"];
task -> owner [label="task / current stage"];
state -> owner [label="current evidence / obligations"];
owner -> specialist [label="bounded question + scoped references"];
specialist -> owner [label="sourced proposal + unknowns"];
scope -> owner [style=dashed,label="constrains permitted action"];
owner -> environment [label="allowed action / query"];
environment -> state [label="observed result; preserve provenance"];
owner -> state [label="proposed internal tracking / next owner"];
`,
'handoff-acceptance':`${common}
graph [label="PROPOSED / UNTESTED | message receipt is not substantive approval"];
request [label="Request\nCase, stage, evidence versions\nObjective, scope, budget, output"];
result [label="Helper result\nFacts / interpretations / proposal\nSources, missing facts, limits"];
check [shape=diamond,label="Correct case, current version\nand permitted scope?"];
stale [label="Clarify / refresh / decline proposal\nRetain named unresolved obligation"];
accepted [label="Owner acknowledges accepted work\nResolve conflicts through actual rule\nDo not invent missing authority"];
action [label="Permitted action through actual tools\nRead back authoritative outcome\nTrack remaining completion evidence"];
request -> result [label="bounded work"];
result -> check [label="proposed contribution"];
check -> stale [label="no / unknown"];
stale -> request [style=dashed,label="only if needed and budget permits"];
check -> accepted [label="yes"];
accepted -> action [label="ready under actual task contract"];
`,
};
const packages=JSON.parse(fs.readFileSync(path.join(base,'data/work_packages.json'),'utf8'));
const relations=JSON.parse(fs.readFileSync(path.join(root,'Plan/HealthcareRoles/data/relations.json'),'utf8'));
const rolePackage=new Map(packages.flatMap(p=>p.roles.map(r=>[r,p.id]))),selected=new Set(['W05','W06','W07','W08','W09','W10','W11','W12','W13','W17']);
const grouped=new Map();
for(const e of relations){
 if(e.type!=='coordination_dependency')continue;
 const a=rolePackage.get(e.sender),b=rolePackage.get(e.receiver);
 if(a===b||!selected.has(a)||!selected.has(b))continue;
 const key=a+' '+b;grouped.set(key,(grouped.get(key)||0)+1);
}
let body=common+'\ngraph [label="UNCONFIRMED INHERITED MODEL | selected package dependencies\\nEdge labels = counts of modeled context links, not measured workload or command authority"];\n';
for(const p of packages.filter(x=>selected.has(x.id))){
 const words=p.title.split(' '),lines=[];let line='';
 for(const word of words){if((line+' '+word).length>29){lines.push(line);line=word;}else line+=(line?' ':'')+word;}if(line)lines.push(line);
 body+=`${p.id} [label=${JSON.stringify(p.id+'\n'+lines.join('\n'))},URL=${JSON.stringify('../WORK_PACKAGES.md#'+p.id.toLowerCase())}];\n`;
}
for(const [key,n] of grouped){const [a,b]=key.split(' ');body+=`${a} -> ${b} [label="${n} modeled links"];\n`;}
bodies['package-dependencies']=body;
const folder=path.join(base,'graphs');fs.mkdirSync(folder,{recursive:true});const results=[];
for(const [name,content] of Object.entries(bodies)){
 const dot='digraph '+name.replaceAll('-','_')+' {\n'+content+'\n}\n';fs.writeFileSync(path.join(folder,name+'.dot'),dot);
 const result=viz.render(dot,{format:'svg',engine:'dot'});
 if(result.status!=='success'||result.output.includes('NaN'))throw new Error(JSON.stringify({name,errors:result.errors}));
 fs.writeFileSync(path.join(folder,name+'.svg'),result.output);
 results.push({name,warnings:result.errors||[],bytes:Buffer.byteLength(result.output)});
}
const receipt={date:'2026-10-18',renderer:'@viz-js/viz',version:JSON.parse(fs.readFileSync(path.join(path.dirname(modulePath),'../package.json'),'utf8')).version,graphs:results.length,results,scope:'Proposed design / inherited unconfirmed models; no empirical architecture validation.'};
fs.writeFileSync(path.join(base,'data/render_receipt.json'),JSON.stringify(receipt,null,2)+'\n');
console.log(JSON.stringify({graphs:results.length,warnings:results.reduce((n,r)=>n+r.warnings.length,0)},null,2));
