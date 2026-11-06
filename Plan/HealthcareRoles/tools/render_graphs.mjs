// Render only this reference's declared local graphs, with the pinned local-only toolchain.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
const require=createRequire(import.meta.url);
const base=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const root=path.resolve(base,'../..');
const modulePath=process.argv[2]||path.join(root,'Runner/.cache/role-docs-toolchain/node_modules/@viz-js/viz/dist/viz.cjs');
const {instance}=require(modulePath);
const viz=await instance();
const manifest=JSON.parse(fs.readFileSync(path.join(base,'data/graph_manifest.json'),'utf8'));
const results=[];
for(const item of manifest){
  const dot=fs.readFileSync(path.join(base,'graphs',item.name+'.dot'),'utf8');
  const rendered=viz.render(dot,{format:'svg',engine:item.engine});
  if(rendered.status!=='success')throw new Error(item.name+': '+JSON.stringify(rendered.errors));
  const svg=rendered.output;
  if(!svg.includes('<svg')||svg.includes('NaN'))throw new Error('Invalid SVG: '+item.name);
  fs.writeFileSync(path.join(base,'graphs',item.name+'.svg'),svg);
  results.push({name:item.name,engine:item.engine,bytes:Buffer.byteLength(svg),warnings:rendered.errors||[]});
}
const receipt={renderer:'@viz-js/viz',version:JSON.parse(fs.readFileSync(path.join(path.dirname(modulePath),'../package.json'),'utf8')).version,date:'2026-10-17',graphs:results.length,results};
fs.writeFileSync(path.join(base,'data/render_receipt.json'),JSON.stringify(receipt,null,2)+'\n');
console.log(JSON.stringify({renderer:receipt.renderer,version:receipt.version,graphs:results.length,warnings:results.reduce((n,x)=>n+x.warnings.length,0)},null,2));
