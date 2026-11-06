import io
import threading
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timezone

from health_harness_codex.console_logs import format_event, log_event


class ConsoleLogTests(unittest.TestCase):
    def test_retrieval_status_reports_work_without_query_or_source_text(self):
        line=format_event('retrieval_progress',tool_name='workspace.hybrid_search',stage='indexing',current=512,total=1024,
                          query='private query',source_text='private source')
        self.assertIn('RETRIEVAL Local retrieval progress',line)
        self.assertIn('stage=indexing',line)
        self.assertIn('tool_name=workspace.hybrid_search',line)
        self.assertIn('current=512',line);self.assertIn('total=1024',line)
        self.assertNotIn('private',line);self.assertNotIn('UNKNOWN',line)

    def test_internal_tool_events_include_tool_and_outcome(self):
        start=format_event('local_tool_started',tool_name='case.retrieve_evidence')
        end=format_event('local_tool_finished',tool_name='case.retrieve_evidence',result_status='error')
        self.assertIn('LOCAL_TOOL_START',start)
        self.assertIn('tool_name=case.retrieve_evidence',start)
        self.assertIn('LOCAL_TOOL_END',end);self.assertIn('result_status=error',end)

    def test_identity_investigation_has_operational_labels_without_patient_data(self):
        start=format_event('identity_investigation_started',candidate_count=2,patient='private')
        end=format_event('identity_investigation_finished',candidate_count=2,resolved=True)
        model=format_event('model_call_started',model_role='identity_investigation')
        self.assertIn('IDENTITY_INVESTIGATION_START',start)
        self.assertIn('candidate_count=2',end)
        self.assertIn('resolved=true',end)
        self.assertIn('model_role=identity_investigation',model)
        self.assertNotIn('private',start)

    def test_task_context_ist_timestamp_and_allowlisted_fields(self):
        line = format_event(
            "model_call_started", task_id="pa_t012_01", domain="pa_provider", attempt=3,
            timestamp=datetime(2026, 10, 21, 8, 40, tzinfo=timezone.utc),
            call_number=3, model="provider/model-v1", prompt="private patient details",
            tool_arguments={"name": "private"},
        )
        self.assertTrue(line.startswith("[14:10:00 IST] INFO [pa_provider/pa_t012_01/a3] MODEL_START"))
        self.assertIn("call_number=3", line)
        self.assertNotIn("private", line)

    def test_batch_context_and_unknown_event_are_bounded_single_lines(self):
        batch = format_event("batch_progress", settled=3, active=2, pending=70)
        self.assertIn("[BATCH] BATCH_PROGRESS", batch)
        unknown = format_event("unexpected\nINFO [forged]", task_id="task\r\nX")
        self.assertEqual(0, unknown.count("\n"))
        self.assertIn("UNKNOWN unexpected INFO [forged]", unknown)

    def test_fresh_and_resumed_batches_are_distinct_and_report_ungraded_attempts(self):
        fresh = format_event("resume_state", status="started", selected_tasks=75)
        resumed = format_event("resume_state", status="resumed", settled=3, pending=72)
        finished = format_event("batch_finished", ungraded_attempts=4, failed_attempts=1)
        self.assertIn("Fresh batch; no earlier task progress", fresh)
        self.assertIn("Batch resume state loaded", resumed)
        self.assertIn("ungraded_attempts=4", finished)
        self.assertIn("failed_attempts=1", finished)

    def test_concurrent_lines_remain_whole_and_correlated(self):
        output = io.StringIO()
        events = [(f"pa_t{i:03d}", i) for i in range(40)]
        with redirect_stdout(output):
            threads = [threading.Thread(target=log_event, args=("task_started",),
                                        kwargs={"task_id": task, "task_index": idx})
                       for task, idx in events]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
        lines = output.getvalue().splitlines()
        self.assertEqual(40, len(lines))
        for task, idx in events:
            matching = [line for line in lines if f"[{task}]" in line]
            self.assertEqual(1, len(matching))
            self.assertIn(f"task_index={idx}", matching[0])


if __name__ == "__main__":
    unittest.main()
