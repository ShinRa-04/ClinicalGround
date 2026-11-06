"""Bounded deterministic retrieval over original case evidence; no model calls."""
from __future__ import annotations

import re

from .models import IsolationError
from .working_set import business, inspect_source, packed, pointer


def field_overview(value, max_chars=4500):
    """Keep document locations discoverable even when their bodies are omitted."""
    documents=value.get('documents') if isinstance(value,dict) else None
    if not isinstance(documents,list) or max_chars<1200:
        return _field_overview(value,max_chars)
    index={'items':[],'total_items':len(documents),'partial':False,
           'instruction':'Original metadata only; retrieve content by its pointer. Titles are not clinical evidence.'}
    budget=min(1400,max_chars//3)
    for i,document in enumerate(documents):
        if not isinstance(document,dict):continue
        entry={'path':f'/documents/{i}'}
        for key in ('title','date','document_date'):
            text=document.get(key)
            if isinstance(text,str):
                entry[key]=text[:140]
                if len(text)>140:entry[key+'_partial']=True
        if 'content' in document:entry['content_path']=entry['path']+'/content'
        if len(packed({**index,'items':[*index['items'],entry]}))>budget:break
        index['items'].append(entry)
    index['partial']=len(index['items'])<len(documents)
    result={'document_index':index,**_field_overview(value,max_chars-len(packed(index))-30)}
    return result


def _field_overview(value, max_chars):
    """Expose useful child fields together, with explicit partial/omission markers."""
    from .working_set import preview
    if len(packed(value))<=min(2200,max_chars-150):return {'value':value,'partial':False}
    if not isinstance(value,dict):return preview(value,min(2200,max_chars-200))
    from .working_set import _PRIORITY
    priority=(*_PRIORITY,'summaries','encounters','orders','documents','providers','notes')
    keys=sorted(value,key=lambda k:(priority.index(k) if k in priority else len(priority),k))
    fields=[];omitted=[]
    for key in keys:
        path='/'+key.replace('~','~0').replace('/','~1')
        child=value[key]
        # Give large strings and collections an attributed first passage,
        # rather than only saying that an entire field was omitted.
        view=inspect_source(value,path,0,900 if isinstance(child,str) else 2,max_chars=1600)
        if view.get('child_path'):
            child_path=view['child_path'];first=pointer(value,child_path)
            view['first_child']=inspect_source(value,child_path,0,700 if isinstance(first,str) else 1,max_chars=1000)
        candidate={'field_readouts':[*fields,view],'partial':True,'omitted_fields':omitted}
        if len(packed(candidate))<=max_chars-700:fields.append(view)
        else:omitted.append({'path':path,'type':type(child).__name__})
    # The exact field index lives in the original observation. Bound metadata
    # too; a payload with many tiny keys must not fill the model context.
    result={'field_readouts':fields,'partial':True,'omitted_fields':omitted[:8],
            'omitted_field_count':len(omitted),
            'instruction':'Historical attributed fields; partial fields have continuation pointers. '
                          'Use case.retrieve_evidence to request several fields/phrases together; no new evidence is created.'}
    while len(packed(result))>max_chars and result['omitted_fields']:result['omitted_fields'].pop()
    while len(packed(result))>max_chars and result['field_readouts']:
        result['field_readouts'].pop();result['omitted_field_count']+=1
    return result


def _strings(value,path='',depth=0,work=None):
    if work is None:work={'visited':0,'partial':False}
    work['visited']+=1
    if depth>30 or work['visited']>20000:
        work['partial']=True;return
    if isinstance(value,str):yield path,value
    elif isinstance(value,dict):
        for key,child in value.items():
            yield from _strings(child,path+'/'+str(key).replace('~','~0').replace('/','~1'),depth+1,work)
            if work['visited']>20000:return
    elif isinstance(value,list):
        for i,child in enumerate(value):
            yield from _strings(child,path+'/'+str(i),depth+1,work)
            if work['visited']>20000:return


def retrieve_evidence(state,requests,*,max_chars=16000,request_offset=0):
    """Return several fields and phrase passages without serial model navigation.

    Each result cites its ORIGINAL evidence ID and business JSON pointer.
    Search offsets address actual text fields, not serialized/escaped JSON.
    All scope checks happen before emitting any source; mixed-case batches fail.
    """
    if not 4000<=max_chars<=24000:raise ValueError('retrieval output budget must be 4000..24000 characters')
    if not 0<=request_offset<=len(requests):raise ValueError('request_offset is outside this batch')
    sources={e['id']:e for e in state.get('evidence',[])}
    for req in requests:
        item=sources.get(req['id'])
        if item is None or item.get('scope')!=state.get('scope') or item.get('outcome')!='success':
            raise IsolationError('batch retrieval requires successful original evidence from this exact case')
    result={'creates_evidence':False,'results':[],'next_request':None,
            'instruction':'Historical evidence views. Cite original id and text_pointer; start/end are relative to that text field. '
                          'An empty literal search does not prove a clinical fact or policy is absent. No semantic search is performed.'}
    remaining=len(requests)-request_offset
    share=max(1800,min(6500,(max_chars-900)//max(1,min(remaining,6))))
    for index in range(request_offset,len(requests)):
        req=requests[index];item=sources[req['id']];data=business(item['observed_result'])
        entry={'request_index':index,'id':item['id'],'fields':[],'passages':[],
               'unprocessed_paths':[],'unprocessed_queries':[],'search_partial':False,'next_match':None}
        paths=list(dict.fromkeys(req.get('paths',[])));queries=list(dict.fromkeys(req.get('queries',[])))
        if not paths and not queries:
            entry['overview']=field_overview(data,share-400)
        for path_index,path in enumerate(paths):
            try:
                view=inspect_source(data,path,req.get('offset',0),req.get('limit',1200),max_chars=max(400,share//2))
            except (KeyError,TypeError):
                from .working_set import missing_path_feedback
                view=missing_path_feedback(data,path)
            except ValueError:view={'path':path,'error':'invalid_source_pointer'}
            if len(packed({**entry,'fields':[*entry['fields'],view]}))>share:
                entry['unprocessed_paths']=paths[path_index:];break
            entry['fields'].append(view)
        seen=set();scanned=0;max_scan=2_000_000;max_nodes=20000;nodes=0;match_index=0
        # One traversal searches all requested phrases; matches retain their
        # original text field and exact character slices, not a generated answer.
        work={'visited':0,'partial':False}
        for path,text in _strings(data,work=work):
            if not queries:break
            nodes+=1
            if scanned+len(text)>max_scan or nodes>max_nodes:
                entry['search_partial']=True;break
            scanned+=len(text)
            for query in queries:
                for match in re.finditer(re.escape(query),text,flags=re.IGNORECASE):
                    start=max(0,match.start()-180);end=min(len(text),match.end()+260)
                    key=(path,start,end)
                    if key in seen:continue
                    seen.add(key)
                    current_match=match_index;match_index+=1
                    if current_match<req.get('search_offset',0):continue
                    passage={'text_pointer':path,'start':start,'end':end,'text':text[start:end],'matched_query':query}
                    if len(entry['passages'])>=req.get('max_passages',8) or len(packed({**entry,'passages':[*entry['passages'],passage]}))>share:
                        entry['search_partial']=True;entry['next_match']=current_match;break
                    entry['passages'].append(passage)
                if entry['search_partial']:break
            if entry['search_partial']:break
        entry['search_partial']=entry['search_partial'] or (bool(queries) and work['partial'])
        if entry['search_partial']:entry['unprocessed_queries']=queries
        candidate={**result,'results':[*result['results'],entry]}
        if len(packed(candidate))>max_chars:
            result['next_request']=index;break
        result['results'].append(entry)
    return result
