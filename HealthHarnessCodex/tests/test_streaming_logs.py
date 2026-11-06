import json
import tempfile
import time
import threading
import unittest
from pathlib import Path

from health_harness_codex.evaluation import RecordingModel,RunRecorder,_Heartbeat
from health_harness_codex.providers import safe_request_diagnostics
from health_harness_codex.models import ModelReply
from health_harness_codex.console_logs import format_event


class StreamingLogTests(unittest.TestCase):
    def test_activity_sampling_switches_wait_receiving_wait_and_keeps_estimate_distinct(self):
        class Model:
            def __init__(self):self.chars=0
            def request_diagnostics(self):return {'reply_chars_received':self.chars,'estimated_reply_tokens':(self.chars+3)//4,
                'token_estimate_method':'characters_div4','private':'PRIVATE_TEXT'}
        with tempfile.TemporaryDirectory() as tmp:
            recorder=RunRecorder(Path(tmp)/'runs'/'test',{'task_id':'synthetic'})
            model=Model();wrapped=RecordingModel(model,recorder)
            self.assertEqual('model_waiting',wrapped._wait_fields()['_event'])
            model.chars=12;receiving=wrapped._wait_fields()
            self.assertEqual('model_receiving',receiving['_event'])
            self.assertEqual(3,receiving['estimated_reply_tokens'])
            self.assertNotIn('reported_output_tokens',receiving)
            self.assertEqual('model_waiting',wrapped._wait_fields()['_event'])
            model.chars=16;self.assertEqual('model_receiving',wrapped._wait_fields()['_event'])
            self.assertNotIn('PRIVATE_TEXT',json.dumps(receiving))

    def test_actual_heartbeat_logs_stream_progress_without_inventing_usage_or_call_counts(self):
        waiting=threading.Event();first=threading.Event();second=threading.Event();paused=threading.Event()
        class Recorder(RunRecorder):
            def emit(self,kind,**fields):
                super().emit(kind,**fields)
                count=fields.get('reply_chars_received')
                if kind=='model_waiting' and count==0:waiting.set()
                if kind=='model_receiving' and count==12:first.set()
                if kind=='model_receiving' and count==24:second.set()
                if kind=='model_waiting' and count==24:paused.set()
        class Model:
            def __init__(self):self.chars=0
            def request_diagnostics(self):return {'reply_chars_received':self.chars,'estimated_reply_tokens':(self.chars+3)//4,
                'token_estimate_method':'characters_div4'}
            def complete(self,*args,**kwargs):
                if not waiting.wait(2):raise AssertionError('missing initial wait heartbeat')
                self.chars=12
                if not first.wait(2):raise AssertionError('missing first receiving heartbeat')
                self.chars=24
                if not second.wait(2) or not paused.wait(2):raise AssertionError('missing receiving/pause transition')
                return ModelReply(content='ok',usage={'input_tokens':5,'output_tokens':2,'total_tokens':7})
        old=_Heartbeat.INTERVAL_SECONDS;_Heartbeat.INTERVAL_SECONDS=.005
        try:
            with tempfile.TemporaryDirectory() as tmp:
                recorder=Recorder(Path(tmp)/'runs'/'test',{'task_id':'synthetic'})
                RecordingModel(Model(),recorder).complete([],[],max_output_tokens=10)
                events=recorder._read_events();count=len(events);time.sleep(.02)
                self.assertEqual(count,len(recorder._read_events()))
                receiving=[e for e in events if e['kind']=='model_receiving']
                self.assertEqual([12,24],[e['reply_chars_received'] for e in receiving])
                self.assertTrue(any(e['kind']=='model_waiting' and e.get('reply_chars_received')==24 for e in events))
                self.assertEqual(1,len([e for e in events if e['kind']=='model_call_started']))
                self.assertEqual(2,recorder._usage['output_tokens'])
        finally:_Heartbeat.INTERVAL_SECONDS=old

    def test_console_distinguishes_estimates_and_provider_counts(self):
        line=format_event('model_receiving',task_id='synthetic',reply_chars_received=120,
            estimated_reply_tokens=30,token_estimate_method='characters_div4',reported_output_tokens=41)
        self.assertIn('MODEL_RECEIVING',line)
        self.assertNotIn('MODEL_WAIT',line)
        self.assertIn('estimated_reply_tokens=30',line)
        self.assertIn('reported_output_tokens=41',line)
        self.assertIn('token_estimate_method=characters_div4',line)

    def test_stream_diagnostics_allow_only_numeric_counters_and_known_estimation_method(self):
        d=safe_request_diagnostics({'reply_chars_received':True,'reply_bytes_received':float('nan'),
            'estimated_reply_tokens':7,'reply_idle_seconds':-1,'token_estimate_method':'PRIVATE_TEXT',
            'raw_delta':'PRIVATE_CONTENT','reported_output_tokens':9})
        self.assertEqual({'estimated_reply_tokens':7,'reported_output_tokens':9},d)


if __name__=='__main__':unittest.main()
