import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from closure_fixtures import stop_record

from health_harness_codex.completion_contracts import build_completion_contract
from health_harness_codex.docker_bridge import DockerMCPClient
from health_harness_codex.engine import Harness
from health_harness_codex.models import Limits, ModelReply, Scope, ToolCall, ToolSpec
from health_harness_codex.store import CaseStore
from health_harness_codex.workflow import (execution_capabilities, validate_dependencies,
    recovery_diagnostics, recovery_prompt, evidence_fingerprint, request_stop_recovery)


class WorkflowTools:
    def __init__(self, disposition_status="closed", forms_complete=False):
        self.calls = []
        self.created = False
        self.closed = False
        self.disposition_status = disposition_status
        self.forms_complete = forms_complete

    def list_tools(self):
        return [
            ToolSpec("chart.list_candidate_orders", "List existing requests", {
                "type": "object", "properties": {"patient_id": {"type": "string"}},
                "required": ["patient_id"], "additionalProperties": False}, "read", ("patient_id",)),
            ToolSpec("cases.create_from_order", "Create a new request, optionally adopt an existing one", {
                "type": "object", "properties": {"patient_id": {"type": "string"},
                    "source_order_id": {"type": "string"}}, "required": ["patient_id"],
                "additionalProperties": False}, "write", ("patient_id",)),
            ToolSpec("auth.finalize_provider_determination", "Record a supported disposition", {
                "type": "object", "properties": {}, "additionalProperties": False}, "write"),
            ToolSpec("cases.get_case", "Read case state", {
                "type": "object", "properties": {}, "additionalProperties": False}, "read"),
        ]

    def call(self, name, arguments):
        self.calls.append(name)
        if name == "chart.list_candidate_orders":
            return {"items": []}
        if name == "cases.create_from_order":
            self.created = True
            return {"case": {"id": "case-1", "status": "draft"}}
        if name == "auth.finalize_provider_determination":
            assert self.created
            self.closed = True
        return {"case": {"id": "case-1", "status": self.disposition_status if self.closed else "draft"},
                "form_validation": {"complete": self.forms_complete},
                "workflow_state": {"stage_detail": "no_submit" if self.disposition_status == "closed" else "docs_needed"}}


class Model:
    def __init__(self, replies):
        self.replies = list(replies)
        self.contexts = []

    def complete(self, messages, tools, **kwargs):
        self.contexts.append(messages)
        if not self.replies:
            raise AssertionError("unexpected extra model call")
        return self.replies.pop(0)


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.scope = Scope("test", "task", "org", "actor", "patient-1", "case-1")
        self.contract = build_completion_contract(
            "task", "pa_provider", "Task: do not submit the request when authorization is not required.",
            self.scope.to_dict())
        self.store = CaseStore(":memory:")
        self.addCleanup(self.store.close)

    def test_empty_existing_orders_replans_into_supported_new_request(self):
        tools = WorkflowTools()
        model = Model([
            ModelReply(tool_calls=(ToolCall("orders", "chart.list_candidate_orders", {"patient_id": "patient-1"}),)),
            ModelReply(content=json.dumps({"status": "incomplete", "claim": "No existing order.", "evidence_ids": ["ev:m1:orders"]})),
            ModelReply(tool_calls=(ToolCall("create", "cases.create_from_order", {"patient_id": "patient-1"}),)),
            ModelReply(tool_calls=(ToolCall("dispose", "auth.finalize_provider_determination", {}),
                                   ToolCall("verify", "cases.get_case", {}))),
            ModelReply(tool_calls=(ToolCall("dispose-after-read", "auth.finalize_provider_determination", {}),
                                   ToolCall("verify-after-write", "cases.get_case", {}))),
            ModelReply(content=json.dumps({"status": "complete", "claim": "The supported no-submit disposition is recorded.",
                                           "evidence_ids": ["ev:m5:verify-after-write"]})),
        ])
        result = Harness(self.store, model, tools, limits=Limits(max_model_calls=6)).run(
            self.scope, "Carry out the supported disposition", "PA", completion_contract=self.contract)
        self.assertEqual("complete", result["status"], result.get("message"))
        self.assertEqual(6, result["model_calls"])
        self.assertEqual(1, len(result["workflow_recoveries"]))
        self.assertEqual(1, tools.calls.count("cases.create_from_order"))
        self.assertEqual(1, tools.calls.count("auth.finalize_provider_determination"))
        self.assertEqual(1, len(result["workflow_guard_refusals"]))
        self.assertIn("source_order_id OPTIONAL", model.contexts[2][-1]["content"])
        self.assertTrue(result["completion_gate"]["accepted"])

    def test_recovery_stops_when_no_new_source_evidence_is_obtained(self):
        model = Model([
            ModelReply(tool_calls=(ToolCall("orders", "chart.list_candidate_orders", {"patient_id": "patient-1"}),)),
            ModelReply(content='{"status":"incomplete","claim":"Need information","evidence_ids":[]}'),
            ModelReply(content='{"status":"incomplete","claim":"Still need information","evidence_ids":[]}'),
        ])
        result = Harness(self.store, model, WorkflowTools()).run(
            self.scope, "Work the request", "PA", completion_contract=self.contract)
        self.assertEqual("unresolved", result["status"])
        self.assertEqual(3, result["model_calls"])
        self.assertEqual("no_new_source_evidence_after_recovery", result["workflow_stop_reason"])

    def test_recovery_never_exceeds_model_budget(self):
        model = Model([ModelReply(content='{"status":"incomplete","claim":"Need information","evidence_ids":[]}')])
        result = Harness(self.store, model, WorkflowTools(), limits=Limits(max_model_calls=1)).run(
            self.scope, "Work the request", "PA", completion_contract=self.contract)
        self.assertEqual("unresolved", result["status"])
        self.assertEqual(1, result["model_calls"])
        self.assertEqual([], result["workflow_recoveries"])

    def test_recovery_targets_saved_reference_and_missing_field_without_inventing_value(self):
        scope=self.scope.to_dict()
        state={'scope':scope,'evidence':[
            {'id':'reference','scope':scope,'tool':'workspace.read_file','outcome':'success',
             'observed_result':{'text':'Read the conditional field rules.','has_more':False}},
            {'id':'case','scope':scope,'tool':'cases.get_case','outcome':'success',
             'observed_result':{'structuredContent':{'form_validation':{'missing_required_fields':['access_reason']}}}},
            {'id':'foreign','scope':{'patient':'other'},'tool':'workspace.read_file','outcome':'success',
             'observed_result':{'text':'FOREIGN_PRIVATE_TEXT'}}]}
        checks=recovery_diagnostics(state)
        self.assertEqual('reference',checks['reference_retrieval'][0]['read_action']['arguments']['id'])
        self.assertEqual('/text',checks['reference_retrieval'][0]['read_action']['arguments']['path'])
        self.assertEqual(['access_reason'],checks['observed_gaps'][0]['reported_gap'])
        self.assertNotIn('FOREIGN_PRIVATE_TEXT',recovery_prompt(state))

    def test_inspecting_unread_source_counts_as_progress_but_duplicate_inspection_does_not(self):
        scope=self.scope.to_dict();state={'scope':scope,'evidence':[{'id':'source','scope':scope,
            'tool':'workspace.read_file','outcome':'success','observed_result':{'text':'source content'}}],
            'messages':[]}
        before=evidence_fingerprint(state)
        message={'role':'tool','name':'case.inspect_evidence','content':json.dumps({
            'id':'source','path':'/text','offset':0,'value':'source content'})}
        state['messages'].append(message);after=evidence_fingerprint(state)
        self.assertNotEqual(before,after)
        state['messages'].append(message)
        self.assertEqual(after,evidence_fingerprint(state))

    def test_recovery_continues_after_two_rounds_only_with_new_progress(self):
        scope=self.scope.to_dict();state={'scope':scope,'completion_contract':{'domain':'pa_provider'},
            'model_calls':10,'messages':[],'evidence':[]}
        for i in range(4):
            state['evidence'].append({'id':str(i),'scope':scope,'tool':'cases.get_case',
                'outcome':'success','observed_result':{'progress':i}})
            self.assertTrue(request_stop_recovery(state,max_model_calls=20))
        self.assertFalse(request_stop_recovery(state,max_model_calls=20))
        self.assertEqual('stop_recovery_limit_reached',state['workflow_stop_reason'])

    def test_optional_source_order_is_a_capability_not_a_missing_prerequisite(self):
        caps = execution_capabilities(WorkflowTools().list_tools())
        self.assertEqual(False, caps["new_request_creation"][0]["existing_order_required"])
        required_order = ToolSpec("cases.create_from_order", "Requires an existing source", {
            "properties": {"source_order_id": {}}, "required": ["source_order_id"]})
        self.assertEqual([], execution_capabilities([required_order])["new_request_creation"])

    def test_dependency_validation_rejects_unknown_and_cyclic_prerequisites(self):
        validate_dependencies([], {"id": "read", "depends_on": []})
        with self.assertRaises(ValueError):
            validate_dependencies([], {"id": "submit", "depends_on": ["missing"]})
        with self.assertRaises(ValueError):
            validate_dependencies([{"id": "read", "depends_on": ["submit"]}],
                                  {"id": "submit", "depends_on": ["read"]})

    def test_only_audited_real_actor_reads_override_missing_mcp_hints(self):
        client = DockerMCPClient("synthetic-only-container")
        client._actual_names = {"read": "cases.get_case", "write": "auth.submit_authorization",
                                "unknown": "custom.get_and_mutate"}
        specs = [ToolSpec(name, "fixture", {}, "write") for name in client._actual_names]
        with patch("health_harness_codex.tools.MCPClient.list_tools", return_value=specs):
            observed = {s.name: s.effect for s in client.list_tools()}
        self.assertEqual({"read": "read", "write": "write", "unknown": "write"}, observed)

    def _handoff_model(self, *, complete):
        return Model([
            ModelReply(tool_calls=(ToolCall("create", "cases.create_from_order", {"patient_id": "patient-1"}),
                                   ToolCall("pending-document", "case.add_obligation", {"id": "external-report", "description": "Obtain the external report"}))),
            ModelReply(tool_calls=(ToolCall("requirements", "cases.get_case", {}),)),
            ModelReply(tool_calls=(ToolCall("disposition", "auth.finalize_provider_determination", {}),
                                   ToolCall("read", "cases.get_case", {}))),
            ModelReply(tool_calls=(ToolCall("defer", "case.defer_obligation", {
                "id": "external-report", "evidence_ids": ["ev:m3:read"],
                "next_action": "Obtain the external report from the requester before further processing"}),)),
            ModelReply(content=json.dumps({"status": "complete" if complete else "incomplete",
                                           "claim": "Provider information handoff recorded; document remains outstanding.",
                                           "stop_assessment":stop_record(['ev:m3:read'],['external-report']),
                                           "evidence_ids": ["ev:m3:read"]})),
        ])

    def test_verified_document_handoff_defers_work_without_claiming_it_done(self):
        contract = build_completion_contract("task", "pa_provider", "Clinical Intake. Prepare the provider record.", self.scope.to_dict())
        result = Harness(self.store, self._handoff_model(complete=True), WorkflowTools("docs_needed", True),
                         limits=Limits(max_model_calls=5)).run(
                             self.scope, "Prepare the provider workflow", "PA", completion_contract=contract)
        self.assertEqual("complete", result["status"], result.get("message"))
        self.assertTrue(result["completion"]["has_deferred_work"])
        self.assertEqual("deferred", result["obligations"][0]["status"])
        self.assertEqual("provider_more_evidence_required", result["completion"]["branch_id"])

    def test_deferral_cannot_hide_unfinished_form_preparation(self):
        contract = build_completion_contract("task", "pa_provider", "Clinical Intake. Prepare the provider record.", self.scope.to_dict())
        result = Harness(self.store, self._handoff_model(complete=False), WorkflowTools("docs_needed", False),
                         limits=Limits(max_model_calls=5)).run(
                             self.scope, "Prepare the provider workflow", "PA", completion_contract=contract)
        self.assertEqual("unresolved", result["status"])
        self.assertEqual("open", result["obligations"][0]["status"])
        self.assertIsNone(result["completion"])

    def test_deferral_rejects_unobserved_evidence_ids(self):
        contract = build_completion_contract("task", "pa_provider", "Clinical Intake. Prepare the provider record.", self.scope.to_dict())
        model = self._handoff_model(complete=False)
        model.replies[3] = ModelReply(tool_calls=(ToolCall("defer", "case.defer_obligation", {
            "id": "external-report", "evidence_ids": ["ev:another-patient"],
            "next_action": "Obtain a report"}),))
        result = Harness(self.store, model, WorkflowTools("docs_needed", True),
                         limits=Limits(max_model_calls=5)).run(
                             self.scope, "Prepare the provider workflow", "PA", completion_contract=contract)
        self.assertEqual("unresolved", result["status"])
        self.assertEqual("open", result["obligations"][0]["status"])
