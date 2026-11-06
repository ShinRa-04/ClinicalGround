// Visual checks use a private headless browser only. No user profile or visible window.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),base=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(base,'../..');
const {chromium}=require('C:/Users/prath/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const output=path.join(root,'Runner/.cache/agent-organization/qa');fs.mkdirSync(output,{recursive:true});
let browser;
try{
 browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const page=await browser.newPage({viewport:{width:1500,height:1050}}),errors=[],results=[];
 page.on('pageerror',e=>errors.push(String(e)));
 for(const name of ['owner-specialists','handoff-acceptance','package-dependencies']){
  const content=fs.readFileSync(path.join(base,'graphs',name+'.svg'),'utf8');
  const svg=content.slice(content.indexOf('<svg'));
  await page.setContent('<!doctype html><html><head><meta charset="utf-8"><style>body{margin:16px;background:white}svg{display:block;width:100%;height:auto}</style></head><body>'+svg+'</body></html>');
  const dimensions=await page.locator('svg').evaluate(svg=>({width:svg.viewBox.baseVal.width,height:svg.viewBox.baseVal.height,nodes:svg.querySelectorAll('.node').length}));
  if(!dimensions.width||!dimensions.nodes)throw new Error('Empty SVG '+name);
  await page.screenshot({path:path.join(output,name+'.png'),fullPage:true,timeout:15000});results.push({name,...dimensions});
 }
 if(errors.length)throw new Error(errors.join('\n'));
 const result={headless:true,visible_windows_requested:false,svg_loads:results,javascript_errors:errors,screenshot_folder:'Runner/.cache/agent-organization/qa',limitation:'Loading/screenshots are representation checks, not empirical architecture validation.'};
 fs.writeFileSync(path.join(base,'data/headless_receipt.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
}finally{if(browser)await browser.close();}
