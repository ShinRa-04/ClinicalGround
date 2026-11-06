from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from typing import Any

from health_harness_codex.engine import Harness
from health_harness_codex.models import Limits, ModelReply, Scope, ToolCall, ToolSpec
from health_harness_codex.store import CaseStore
from health_harness_codex.synthetic_contracts import operator_observation_contract


def make_scope(case: str = "case-42") -> Scope:
    return Scope("env", "task", "org", "actor", f"case-subject:{case}", case)


def _patient_read_contract(scope: Scope) -> dict[str, Any]:
    return operator_observation_contract(
        scope, "UM", "records.by_patient", [
            {"id": "current_patient_record", "path": "record_status", "op": "eq", "value": "observed"},
            {"id": "same_patient_result", "path": "patient_id", "op": "eq", "value": "patient-900"},
        ])


class SequenceModel:
    def __init__(self, replies: list[ModelReply | Exception]):
        self.replies = list(replies)
        self.seen: list[list[dict[str, Any]]] = []

    def complete(self, messages, tools, *, max_output_tokens):
        self.seen.append(json.loads(json.dumps(messages)))
        if not self.replies:
            raise AssertionError("unexpected model call")
        reply = self.replies.pop(0)
        if isinstance(reply, Exception):
            raise reply
        return reply


class IdentityTools:
    def __init__(self, results: dict[str, Any]):
        self.results = results
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def list_tools(self):
        return [
            ToolSpec("payer.route_case", "Route the observed case", {
                "type": "object", "required": ["case_id"], "additionalProperties": False,
                "properties": {"case_id": {"type": "string"}},
            }, effect="write", identity_fields=("case_id",)),
            ToolSpec("records.by_patient", "Read a patient record", {
                "type": "object", "required": ["patient_id"], "additionalProperties": False,
                "properties": {"patient_id": {"type": "string"}},
            }, identity_fields=("patient_id",)),
            ToolSpec("workspace.read_file", "Read current workspace artifact", {
                "type": "object", "required": ["path"], "additionalProperties": False,
                "properties": {"path": {"type": "string"}},
            }),
        ]

    def call(self, name, arguments):
        self.calls.append((name, dict(arguments)))
        value = self.results[name]
        if isinstance(value, Exception):
            raise value
        return value(arguments) if callable(value) else value


class ProviderCaseTools:
    def __init__(self, create_result):
        self.create_result = create_result
        self.calls = []

    def list_tools(self):
        return [
            ToolSpec("cases.create_from_order", "Create the assigned provider case", {
                "type": "object", "required": ["patient_id", "clinical_choice"],
                "properties": {"patient_id": {"type": "string"}, "clinical_choice": {"type": "string"}},
                "additionalProperties": False,
            }, effect="write", identity_fields=("patient_id",)),
            ToolSpec("cases.get_case", "Read the bound provider case", {
                "type": "object", "required": ["case_id"],
                "properties": {"case_id": {"type": "string"}}, "additionalProperties": False,
            }, identity_fields=("case_id",)),
        ]

    def call(self, name, arguments):
        self.calls.append((name, dict(arguments)))
        if name == "cases.create_from_order":
            return self.create_result
        if name == "cases.get_case":
            return {"case_id": arguments["case_id"], "patient_id": "patient-900", "status": "observed"}
        raise KeyError(name)


class MDDecisionTools:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def list_tools(self):
        return [ToolSpec("review.submit_md_case_decision", "Submit the reviewed case decision", {
            "type": "object", "required": ["case_id", "decision"],
            "properties": {"case_id": {"type": "string"}, "decision": {"type": "string"}},
            "additionalProperties": False,
        }, effect="write", identity_fields=("case_id",))]

    def call(self, name, arguments):
        self.calls.append((name, dict(arguments)))
        return self.result


class IdentityEngineIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp.name) / "state.sqlite"
        self.store = CaseStore(self.db_path)

    def tearDown(self):
        self.store.close()
        self.temp.cleanup()

    @staticmethod
    def case_patient_result(case_id="case-42", patient_id="patient-900"):
        return {"case": {"id": case_id, "patient_id": patient_id, "status": "routed"}}

    def test_trusted_late_binding_allows_patient_tool_and_evidence_linked_completion(self):
        scope = make_scope()
        route = self.case_patient_result()
        tools = IdentityTools({
            "payer.route_case": route,
            "records.by_patient": lambda args: {"patient_id": args["patient_id"], "record_status": "observed"},
            "workspace.read_file": {},
        })
        model = SequenceModel([
            ModelReply(tool_calls=(ToolCall("route", "payer.route_case", {"case_id": scope.case}),)),
            ModelReply(tool_calls=(ToolCall("lookup", "records.by_patient", {"patient_id": "patient-900"}),)),
            ModelReply(tool_calls=(ToolCall("ob", "case.add_obligation", {
                "id": "verify", "description": "Verify the routed case record"}),)),
            ModelReply(tool_calls=(ToolCall("close", "case.close_obligation", {
                "id": "verify", "evidence_ids": ["ev:m1:route", "ev:m2:lookup"]}),)),
            ModelReply(content=json.dumps({"status": "complete", "claim": "Routed identity and patient record were observed.",
                                          "evidence_ids": ["ev:m1:route", "ev:m2:lookup"]})),
        ])
        harness = Harness(self.store, model, tools, limits=Limits(max_model_calls=6, max_tool_calls=12),
                          patient_identity_tools=("payer.route_case",))

        result = harness.run(scope, "Complete the synthetic case work", "UM",
                             completion_contract=_patient_read_contract(scope))

        self.assertEqual("complete", result["status"])
        self.assertEqual("closed", result["obligations"][0]["status"])
        self.assertEqual("patient-900", result["identity_bindings"]["patient_id"])
        self.assertEqual(scope.case, result["identity_bindings"]["case_id"])
        self.assertEqual(scope.patient, result["completion"]["scope"]["patient"])
        self.assertEqual(("records.by_patient", {"patient_id": "patient-900"}), tools.calls[1])
        self.assertTrue(any(item.get("observed_result", {}).get("record_status") == "observed"
                            for item in result["evidence"]))

    def test_workspace_result_cannot_establish_patient_identity(self):
        scope = make_scope()
        tools = IdentityTools({
            "payer.route_case": self.case_patient_result(),
            "records.by_patient": {},
            "workspace.read_file": self.case_patient_result(),
        })
        model = SequenceModel([ModelReply(tool_calls=(ToolCall(
            "workspace", "workspace.read_file", {"path": "incoming/request.json"}),))])
        harness = Harness(self.store, model, tools,
                          patient_identity_tools=("payer.route_case",))

        result = harness.run(scope, "Read the workspace", "UM")

        self.assertEqual("blocked", result["status"])
        self.assertEqual({}, result["identity_bindings"])
        self.assertEqual("result_identity_mismatch", result["evidence"][0]["observed_result"]["error"])
        self.assertEqual(1, len(model.seen), "the quarantined result must stop before another model call")

    def test_conflicting_later_patient_id_is_quarantined_before_model(self):
        scope = make_scope()
        tools = IdentityTools({
            "payer.route_case": self.case_patient_result(),
            "records.by_patient": {"patient_id": "patient-other", "record_status": "foreign"},
            "workspace.read_file": {},
        })
        model = SequenceModel([
            ModelReply(tool_calls=(ToolCall("route", "payer.route_case", {"case_id": scope.case}),)),
            ModelReply(tool_calls=(ToolCall("lookup", "records.by_patient", {"patient_id": "patient-900"}),)),
        ])
        harness = Harness(self.store, model, tools, patient_identity_tools=("payer.route_case",))

        result = harness.run(scope, "Route and read", "UM")

        self.assertEqual("blocked", result["status"])
        self.assertEqual(2, len(model.seen))
        self.assertEqual("patient-900", result["identity_bindings"]["patient_id"])
        self.assertEqual("case-subject:case-42", self.store.load_case(scope)["scope"]["patient"])
        last = result["evidence"][-1]["observed_result"]
        self.assertEqual("result_identity_mismatch", last["error"])
        self.assertNotIn("foreign", json.dumps(model.seen[-1]))

    def test_patient_binding_is_per_case_and_not_injected_into_next_case_context(self):
        scope_a, scope_b = make_scope("case-A"), make_scope("case-B")
        tools_a = IdentityTools({"payer.route_case": self.case_patient_result("case-A", "patient-A"),
                                 "records.by_patient": {}, "workspace.read_file": {}})
        model_a = SequenceModel([
            ModelReply(tool_calls=(ToolCall("route-a", "payer.route_case", {"case_id": scope_a.case}),)),
            ModelReply(content="Case A remains unresolved."),
        ])
        result_a = Harness(self.store, model_a, tools_a,
                           patient_identity_tools=("payer.route_case",)).run(scope_a, "Case A", "UM")
        self.assertEqual("patient-A", result_a["identity_bindings"]["patient_id"])

        tools_b = IdentityTools({"payer.route_case": self.case_patient_result("case-B", "patient-B"),
                                 "records.by_patient": {}, "workspace.read_file": {}})
        model_b = SequenceModel([ModelReply(content="Case B remains unresolved.")])
        result_b = Harness(self.store, model_b, tools_b,
                           patient_identity_tools=("payer.route_case",)).run(scope_b, "Case B", "UM")

        self.assertEqual({}, result_b["identity_bindings"])
        self.assertNotIn("patient-A", json.dumps(model_b.seen[0]))
        self.assertEqual("patient-A", self.store.load_case(scope_a)["identity_bindings"]["patient_id"])
        self.assertNotIn("identity_bindings", self.store.load_case(scope_b))

    def test_binding_survives_model_error_and_resume_without_changing_scope_key(self):
        scope = make_scope()
        original_key = scope.key
        tools = IdentityTools({
            "payer.route_case": self.case_patient_result(),
            "records.by_patient": lambda args: {"patient_id": args["patient_id"], "record_status": "observed"},
            "workspace.read_file": {},
        })
        first_model = SequenceModel([
            ModelReply(tool_calls=(ToolCall("route", "payer.route_case", {"case_id": scope.case}),)),
            OSError("synthetic transient model failure"),
        ])
        first = Harness(self.store, first_model, tools, patient_identity_tools=("payer.route_case",))
        contract = _patient_read_contract(scope)
        first_result = first.run(scope, "Route and inspect", "UM", completion_contract=contract)
        self.assertEqual("error", first_result["status"])
        self.assertEqual("patient-900", first_result["identity_bindings"]["patient_id"])
        self.assertEqual("case-subject:case-42", self.store.load_case(scope)["scope"]["patient"])
        self.assertEqual(original_key, scope.key)

        self.store.close()
        self.store = CaseStore(self.db_path)
        resume_model = SequenceModel([
            ModelReply(tool_calls=(ToolCall("lookup", "records.by_patient", {"patient_id": "patient-900"}),)),
            ModelReply(content=json.dumps({"status": "complete", "claim": "Resumed patient read was observed.",
                                          "evidence_ids": ["ev:m3:lookup"]})),
        ])
        resumed = Harness(self.store, resume_model, tools, patient_identity_tools=("payer.route_case",))
        result = resumed.run(scope, "Route and inspect", "UM", resume=True,
                             completion_contract=contract)

        self.assertEqual("complete", result["status"])
        self.assertEqual("patient-900", result["identity_bindings"]["patient_id"])
        self.assertEqual(scope.patient, result["completion"]["scope"]["patient"])
        self.assertEqual(original_key, scope.key)
        self.assertEqual(("records.by_patient", {"patient_id": "patient-900"}), tools.calls[-1])

    def test_same_case_sibling_patient_id_without_binding_is_denied(self):
        scope = make_scope()
        unbound = {"case_id": scope.case, "related": {"patient_id": "patient-900"}}
        tools = IdentityTools({"payer.route_case": unbound,
                               "records.by_patient": {}, "workspace.read_file": {}})
        model = SequenceModel([ModelReply(tool_calls=(ToolCall(
            "route", "payer.route_case", {"case_id": scope.case}),))])
        harness = Harness(self.store, model, tools, patient_identity_tools=("payer.route_case",))

        result = harness.run(scope, "Route only", "UM")

        self.assertEqual("blocked", result["status"])
        self.assertEqual({}, result["identity_bindings"])
        self.assertEqual("result_identity_mismatch", result["evidence"][0]["observed_result"]["error"])
        self.assertEqual(1, len(model.seen))

    def test_provider_case_binds_only_after_trusted_create_and_keeps_original_scope_key(self):
        scope = Scope("env", "provider-task", "provider", "actor", "patient-900",
                      "case-subject:patient-900")
        original_key = scope.key
        tools = ProviderCaseTools({"structuredContent": {"case": {
            "id": "provider-case-7", "patient_id": "patient-900", "status": "created"}}})
        model = SequenceModel([
            ModelReply(tool_calls=(ToolCall("create", "cases.create_from_order", {
                "patient_id": "patient-900", "clinical_choice": "evidence-backed choice"}),)),
            ModelReply(tool_calls=(ToolCall("read", "cases.get_case", {"case_id": "provider-case-7"}),)),
            ModelReply(content="The case readback was observed."),
        ])
        rebound = []
        harness = Harness(self.store, model, tools, case_identity_tools=("cases.create_from_order",),
                          case_binding_callback=lambda binding: rebound.append(binding))

        result = harness.run(scope, "Create the assigned provider case", "PA")

        binding = result["case_bindings"]
        self.assertEqual("provider-case-7", binding["case_id"])
        self.assertEqual("case-subject:patient-900", binding["case_namespace"])
        self.assertEqual("cases.create_from_order", binding["source_tool"])
        self.assertEqual("ev:m1:create", binding["source_evidence_id"])
        self.assertEqual("provider-case-7", rebound[0]["case_id"])
        self.assertEqual("case-subject:patient-900", self.store.load_case(scope)["scope"]["case"])
        self.assertEqual(original_key, scope.key)
        self.assertEqual("cases.get_case", tools.calls[-1][0])
        self.assertIn("provider-case-7", json.dumps(model.seen[1]))
        self.assertIn("case-subject:patient-900", json.dumps(model.seen[1]))

    def test_provider_case_creation_result_with_foreign_patient_is_quarantined(self):
        scope = Scope("env", "provider-task", "provider", "actor", "patient-900",
                      "case-subject:patient-900")
        tools = ProviderCaseTools({"structuredContent": {"case": {
            "id": "provider-case-7", "patient_id": "patient-other", "status": "created"}}})
        model = SequenceModel([ModelReply(tool_calls=(ToolCall(
            "create", "cases.create_from_order", {"patient_id": "patient-900",
                                                   "clinical_choice": "evidence-backed choice"}),))])
        result = Harness(self.store, model, tools,
                         case_identity_tools=("cases.create_from_order",)).run(
                             scope, "Create the assigned provider case", "PA")
        self.assertEqual("blocked", result["status"])
        self.assertEqual({}, result["case_bindings"])
        self.assertEqual("result_identity_mismatch", result["evidence"][0]["observed_result"]["error"])
        self.assertNotIn("patient-other", json.dumps(model.seen[-1]))

    def test_provider_internal_case_namespace_is_rejected_before_remote_call(self):
        scope = Scope("env", "provider-task", "provider", "actor", "patient-900",
                      "case-subject:patient-900")
        tools = ProviderCaseTools({})
        model = SequenceModel([ModelReply(tool_calls=(ToolCall(
            "read", "cases.get_case", {"case_id": scope.case}),))])
        result = Harness(self.store, model, tools,
                         case_identity_tools=("cases.create_from_order",)).run(
                             scope, "Read provider case", "PA")
        self.assertEqual("error", result["status"])
        self.assertEqual([], tools.calls)

    def test_um_md_decision_binds_patient_only_from_authoritative_case_path_without_replay(self):
        scope = make_scope()
        raw_result = {"structuredContent": {"missing_information": {
            "case": {"id": scope.case, "patient_id": "patient-900",
                     "case_status": "pended_action_required"},
            "message": "Additional records are needed."}}}
        tools = MDDecisionTools(raw_result)
        model = SequenceModel([
            ModelReply(tool_calls=(ToolCall("decision", "review.submit_md_case_decision", {
                "case_id": scope.case, "decision": "request_information"}),)),
            ModelReply(content="The saved case identity was read from the authoritative decision result."),
        ])
        path = ("structuredContent", "missing_information", "case")
        result = Harness(self.store, model, tools,
                         patient_identity_tools=("review.submit_md_case_decision",),
                         patient_identity_result_paths={"review.submit_md_case_decision": path}).run(
                             scope, "Handle the case decision", "UM")
        self.assertEqual("patient-900", result["identity_bindings"]["patient_id"])
        self.assertEqual(scope.case, result["identity_bindings"]["case_id"])
        self.assertEqual([("review.submit_md_case_decision", {
            "case_id": scope.case, "decision": "request_information"})], tools.calls)
        self.assertEqual("completed", self.store.actions(scope)[0]["status"])
        self.assertEqual(raw_result["structuredContent"], result["evidence"][0]["observed_result"]["structuredContent"])

    def test_um_md_decision_does_not_bind_from_fake_case_or_generic_patient_echo(self):
        path = ("structuredContent", "missing_information", "case")
        for index in range(2):
            scope = make_scope(f"case-negative-{index}")
            raw_result = ({"structuredContent": {"missing_information": {
                "case": {"id": "case-other", "patient_id": "patient-900"}}}}
                if index == 0 else
                {"structuredContent": {"case_id": scope.case, "notes": {"patient_id": "patient-900"},
                                       "missing_information": {"case": {"patient_id": "patient-900"}}}})
            with self.subTest(raw_result=raw_result):
                tools = MDDecisionTools(raw_result)
                model = SequenceModel([ModelReply(tool_calls=(ToolCall(
                    "decision", "review.submit_md_case_decision", {
                        "case_id": scope.case, "decision": "request_information"}),))])
                result = Harness(self.store, model, tools,
                                 patient_identity_tools=("review.submit_md_case_decision",),
                                 patient_identity_result_paths={"review.submit_md_case_decision": path}).run(
                                     scope, "Handle the case decision", "UM")
                self.assertEqual("blocked", result["status"])
                self.assertEqual({}, result["identity_bindings"])
                self.assertEqual("result_identity_mismatch", result["evidence"][0]["observed_result"]["error"])
                self.assertEqual(1, len(tools.calls))


if __name__ == "__main__":
    unittest.main()
