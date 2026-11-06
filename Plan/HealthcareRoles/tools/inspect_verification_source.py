"""Inspect bounded primary-source passages without opening a browser."""
import argparse
import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

parser=argparse.ArgumentParser()
parser.add_argument('source')
parser.add_argument('terms',nargs='*')
parser.add_argument('--limit',type=int,default=12)
parser.add_argument('--chars',type=int,default=1300)
args=parser.parse_args()
root=Path(__file__).resolve().parents[3]
record=json.loads((root/'Runner/.cache/role-verification'/(args.source+'.json')).read_text(encoding='utf-8'))
print(args.source,record['retrieval_status'],record['url'])
terms=[t.casefold() for t in args.terms]
rows=[p for p in record['paragraphs'] if not terms or any(t in p['text'].casefold() for t in terms)]
for paragraph in rows[:args.limit]:
    print(paragraph['locator']+': '+paragraph['text'][:args.chars])
print('Matching paragraphs:',len(rows))
