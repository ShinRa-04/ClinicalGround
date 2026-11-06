// Documentation inspection only: isolated headless browser, no visible window or user profile.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),base=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const {chromium}=require('C:/Users/prath/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const output=path.join(base,'_cache/qa');fs.mkdirSync(output,{recursive:true});let browser;
try{
 browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const page=await browser.newPage({viewport:{width:1500,height:1050}}),errors=[],results=[];
 page.on('pageerror',error=>errors.push(String(error)));
 for(const name of ['organization','composite-roles','case-execution','patient-isolation','memory-context']){
  const raw=fs.readFileSync(path.join(base,'graphs',name+'.svg'),'utf8'),svg=raw.slice(raw.indexOf('<svg'));
  await page.setContent('<!doctype html><html><head><meta charset="utf-8"><style>body{margin:16px;background:white}svg{display:block;width:100%;height:auto}</style></head><body>'+svg+'</body></html>');
  const geometry=await page.locator('svg').evaluate(s=>({width:s.viewBox.baseVal.width,height:s.viewBox.baseVal.height,nodes:s.querySelectorAll('.node').length}));
  if(!geometry.width||!geometry.nodes)throw new Error('Empty diagram '+name);
  await page.screenshot({path:path.join(output,name+'.png'),fullPage:true,timeout:15000});results.push({name,...geometry});
 }
 if(errors.length)throw new Error(errors.join('\n'));
 const receipt={headless:true,visible_windows_requested:false,diagrams_loaded:results,javascript_errors:errors,screenshot_folder:'HealthHarnessBlueprint/_cache/qa',scope:'Diagram loading only, not runtime isolation, task compatibility or benchmark verification.'};
 fs.writeFileSync(path.join(base,'verification/headless_receipt.json'),JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify(receipt,null,2));
}finally{if(browser)await browser.close();}
