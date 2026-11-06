"""GPU embeddings over stdin only. Public weights downloaded at build time."""
import hashlib
import json
from pathlib import Path
import sys

from fastembed import TextEmbedding

MODEL='BAAI/bge-small-en-v1.5'
prepare='--prepare' in sys.argv
model=TextEmbedding(model_name=MODEL,cache_dir='/opt/models',threads=2,
    providers=['CPUExecutionProvider'] if prepare else ['CUDAExecutionProvider','CPUExecutionProvider'],
    local_files_only=not prepare)
if prepare:
    files=[(str(p.relative_to('/opt/models')),hashlib.sha256(p.read_bytes()).hexdigest())
           for p in sorted(Path('/opt/models').rglob('*')) if p.is_file()]
    import onnxruntime
    identity={'model':MODEL,'fastembed':'0.9.0','onnxruntime':onnxruntime.__version__,'dimension':384,
              'weights_sha256':hashlib.sha256(json.dumps(files,sort_keys=True).encode()).hexdigest()}
    Path('/opt/model-manifest.json').write_text(json.dumps(identity))
    print(json.dumps(identity));sys.exit(0)

obj=model
providers=[]
for _ in range(5):
    if callable(getattr(obj,'get_providers',None)):
        providers=obj.get_providers();break
    obj=getattr(obj,'model',None)
    if obj is None:break
if 'CUDAExecutionProvider' not in providers:
    raise RuntimeError('GPU session unavailable; refusing an unreported CPU fallback')
request=json.load(sys.stdin)
texts=request.get('texts')
if not isinstance(texts,list) or not 1<=len(texts)<=512 or any(not isinstance(t,str) or len(t)>12000 for t in texts):
    raise ValueError('bounded string list required')
if sum(map(len,texts))>1500000:raise ValueError('embedding input budget exceeded')
vectors=list(model.query_embed(texts) if request.get('query') else model.passage_embed(texts,batch_size=64))
identity=json.loads(Path('/opt/model-manifest.json').read_text())
print(json.dumps({'vectors':[v.tolist() for v in vectors],'encoder':{**identity,'providers':providers,'device':'gpu'}}))
