"""Offline identity/coverage/navigation checks; never imports or executes upstream systems."""
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

sys.dont_write_bytecode=True
BASE=Path(__file__).resolve().parents[1]


def read(name):return json.loads((BASE/name).read_text(encoding='utf-8-sig'))


def sha(data):return hashlib.sha256(data).hexdigest()


def anchors(text):
    found=set(re.findall(r'<a\s+id=["\']([^"\']+)',text))
    for heading in re.findall(r'^#+\s+(.+)$',text,re.M):
        value=re.sub(r'[^\w\- ]','',heading.lower().strip())
        found.add(re.sub(r'\s+','-',value))
    return found


def main():
    versions=read('source_versions.json');findings={};source_checks=0
    for repo in versions['repositories']:
        name=repo['id'];root=BASE/'_sources'/name
        actual=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()
        assert actual==repo['commit']
        assert not subprocess.check_output(['git','-C',str(root),'status','--porcelain'],text=True).strip(),name
        rows=read(name+'/evidence.json');assert len(rows)==(60 if name=='hermes' else 75)
        for r in rows:
            assert r['id'] not in findings and r['commit']==actual
            assert r['statement'] and r['limits'] and r['status'] in {'code-traced','docs-only','test-inspected'}
            raw=(root/r['source_path']).read_bytes();lines=raw.decode('utf-8-sig').splitlines()
            assert 1<=r['line_start']<=r['line_end']<=len(lines),r['id']
            payload='\n'.join(lines[r['line_start']-1:r['line_end']]).encode() if name=='hermes' else raw
            key='selected_lines_sha256' if name=='hermes' else 'source_sha256'
            assert sha(payload)==r[key],r['id']
            url=r.get('source_url') or r['url'];assert '/blob/'+actual+'/' in url
            findings[r['id']]=r;source_checks+=1
    comparative=read('comparative/evidence.json')['claims'];sources=read('comparative/sources.json')['sources']
    assert len(comparative)==35 and len(sources)==24
    source_by={s['id']:s for s in sources}
    for s in sources:
        raw=(BASE/s['cache_relative_path']).read_bytes();assert sha(raw)==s['sha256'],s['id'];source_checks+=1
        if s.get('line_count'):assert len(raw.decode('utf-8-sig').splitlines())==s['line_count'],s['id']
    for r in comparative:
        assert r['id'] not in findings and r['source_id'] in source_by and r['statement'] and r['limits']
        assert r['status'] in {'documented','code_inspected','ambiguous_documentation'}
        if r['status']=='code_inspected':
            s=source_by[r['source_id']];assert r['commit']==s['commit']
            for first,last in re.findall(r'(\d+)[–-](\d+)',r['locator']):assert 1<=int(first)<=int(last)<=s['line_count'],r['id']
        findings[r['id']]=r
    assert len(findings)==170
    foundations=read('foundation_sources.json');assert len({s['id'] for s in foundations})==18
    captures=read('verification/foundation_capture_receipt.json');assert len(captures)==18
    for c in captures:
        assert c['status']=='captured'
        assert sha((BASE/'_cache/foundations'/(c['id']+'.bin')).read_bytes())==c['sha256'];source_checks+=1
    coverage=read('verification/coverage.json');foundation_ids={s['id'] for s in foundations}
    assert len(coverage)==len({r['id'] for r in coverage})==38
    for row in coverage:
        assert (BASE/row['chapter']).exists() and set(row['foundation_ids'])<=foundation_ids
        assert set(row['finding_ids'])<=set(findings) and row['runtime_completeness_verified'] is False
    lab=read('verification/lab_receipt.json');assert lab['tests_run']==17 and lab['passed'] and lab['failures']==lab['errors']==0
    assert len(list((BASE/'general').glob('*.md')))==12
    local_links=0;local_anchors=0;documents=[]
    paths=[]
    for directory,dirs,files in os.walk(BASE):
        dirs[:]=[d for d in dirs if d not in {'_sources','_cache','__pycache__','.git'}]
        paths.extend(Path(directory)/name for name in files if name.endswith('.md'))
    for file in paths:
        documents.append(file)
        for target in re.findall(r'\]\(([^)]+)\)',file.read_text(encoding='utf-8-sig')):
            if re.match(r'https?://',target):continue
            path,separator,anchor=unquote(target.strip('<>')).partition('#')
            resolved=(file.parent/path).resolve() if path else file.resolve()
            assert resolved.exists(),(file.relative_to(BASE),target)
            local_links+=1
            if separator and anchor and resolved.suffix=='.md':
                assert anchor in anchors(resolved.read_text(encoding='utf-8-sig')),(file.relative_to(BASE),target)
                local_anchors+=1
    for path in ['general/10-construction-guide.md','general/11-data-contracts-and-failure-catalog.md','general/12-design-questions-and-learning-map.md','ARCHITECTURE_MAPS.md','VERIFICATION.md']:
        assert (BASE/path).exists()
    build=read('verification/build_receipt.json')
    assert build['upstream_runtime_executed'] is build['upstream_tests_executed'] is build['architecture_selected'] is False
    snapshot=[]
    for file in sorted(documents):
        snapshot.append(dict(path=file.relative_to(BASE).as_posix(),normalized_utf8_sha256=sha(file.read_text(encoding='utf-8-sig').encode())))
    receipt=dict(date='2026-10-18',result='passed',general_chapters=12,knowledge_topics=38,scoped_implementation_comparative_findings=170,
        foundation_sources=18,source_identity_checks=source_checks,documents_checked=len(documents),local_markdown_links_checked=local_links,
        local_markdown_anchor_targets_checked=local_anchors,synthetic_lab_tests_passed=17,upstream_checkouts_clean=True,
        upstream_runtime_executed=False,upstream_tests_executed=False,architecture_performance_verified=False,
        limits='Identity, bounds, coverage and navigation checks only; semantic support uses bounded independent review. Synthetic examples are not deployment/upstream behavior.',documents=snapshot)
    (BASE/'verification/validation_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in receipt.items() if k!='documents'},indent=2))


if __name__=='__main__':main()
