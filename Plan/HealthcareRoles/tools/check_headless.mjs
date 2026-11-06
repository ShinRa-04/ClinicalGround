// Headless-only visual/interaction check. Serves only this public reference on loopback.
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),base=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),root=path.resolve(base,'../..');
const moduleFile=process.argv[2];
if(!moduleFile)throw new Error('Pass an absolute installed Playwright module path; no package installation is performed.');
const {chromium}=require(moduleFile);
const screenshots=path.join(root,'Runner/.cache/role-docs-toolchain/qa');fs.mkdirSync(screenshots,{recursive:true});
const server=http.createServer((req,res)=>{
 const requested=new URL(req.url,'http://localhost').pathname;
 if(requested.startsWith('/_preview/')&&/^\/_preview\/[A-Za-z0-9-]+$/.test(requested)){
  const name=requested.slice('/_preview/'.length);
  res.writeHead(200,{'Content-Type':'text/html; charset=utf-8'});
  res.end('<!doctype html><html><head><meta charset="utf-8"><title>Diagram check</title></head><body style="margin:16px;background:white"><img alt="'+name+'" style="display:block;max-width:1400px;width:100%;height:auto" src="/graphs/'+name+'.svg"></body></html>');return;
 }
 const target=path.resolve(base,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));
 if(!target.startsWith(base+path.sep)||!fs.existsSync(target)||fs.statSync(target).isDirectory()){res.writeHead(404);res.end();return;}
 const ext=path.extname(target),mime={'.html':'text/html','.svg':'image/svg+xml','.md':'text/plain','.json':'application/json'}[ext]||'application/octet-stream';
 res.writeHead(200,{'Content-Type':mime+'; charset=utf-8'});res.end(fs.readFileSync(target));
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const origin='http://127.0.0.1:'+server.address().port;
let browser;
try{
 browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[];
 page.on('pageerror',e=>errors.push(String(e)));
 await page.goto(origin+'/index.html');
 if(await page.locator('.role').count()!==97)throw new Error('Missing HTML profiles');
 await page.screenshot({path:path.join(screenshots,'index.png')});
 await page.locator('#search').fill('U13');
 if(await page.locator('.role:visible').count()!==1)throw new Error('ID filter failed');
 await page.screenshot({path:path.join(screenshots,'role-U13.png')});
 await page.locator('#search').fill('');await page.locator('#group').selectOption('payer');
 const expected=JSON.parse(fs.readFileSync(path.join(base,'data/roles.json'),'utf8')).filter(x=>x.group==='payer').length;
 if(await page.locator('.role:visible').count()!==expected)throw new Error('Domain filter failed');
 await page.goto(origin+'/index.html#M04');
 if(await page.locator('.role:visible').count()!==97)throw new Error('Hash navigation did not reset filters');
 const inspected=[];
 for(const name of ['authority-domains','ma-appeals','commercial-appeals','reporting-examples','role-M28','role-U13','provider-information']){
  await page.goto(origin+'/_preview/'+name);
  const geometry=await page.locator('img').evaluate(image=>({width:image.naturalWidth,height:image.naturalHeight,loaded:image.complete}));
  if(!geometry.width||!geometry.height||!geometry.loaded)throw new Error('Empty graph '+name);
  await page.screenshot({path:path.join(screenshots,name+'.png'),fullPage:true});
  inspected.push({name,...geometry});
 }
 if(errors.length)throw new Error(errors.join('\n'));
 const result={headless:true,visible_windows_requested:false,profile_count:97,id_filter:'passed',domain_filter:'passed',hash_navigation:'passed',javascript_errors:errors,graphs_inspected:inspected,screenshot_folder:'Runner/.cache/role-docs-toolchain/qa'};
 fs.writeFileSync(path.join(base,'data/headless_receipt.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
}finally{if(browser)await browser.close();await new Promise(resolve=>server.close(resolve));}
