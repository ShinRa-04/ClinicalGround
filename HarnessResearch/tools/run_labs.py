"""Run only this research's stdlib synthetic tests and record exact results."""
import io
import json
import platform
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode=True
BASE=Path(__file__).resolve().parents[1]
suite=unittest.TestLoader().discover(str(BASE/'labs'),pattern='test_*.py')
buffer=io.StringIO();result=unittest.TextTestRunner(stream=buffer,verbosity=2).run(suite)
receipt=dict(date='2026-10-18',python=platform.python_version(),tests_run=result.testsRun,
    failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),passed=result.wasSuccessful(),
    output=buffer.getvalue(),scope='Synthetic stdlib teaching invariants only; no upstream runtime, provider calls, semantic-quality or production concurrency validation.')
out=BASE/'verification/lab_receipt.json';out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({k:v for k,v in receipt.items() if k!='output'},indent=2))
raise SystemExit(0 if result.wasSuccessful() else 1)
