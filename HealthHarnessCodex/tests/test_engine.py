from __future__ import annotations

import json
import tempfile
import threading
import time
from contextlib import closing
import unittest
from pathlib import Path
from typing import Any
from closure_fixtures import stop_record

from health_harness_codex.engine import Harness, _completion_contract_hash, _safe_validation_feedback, _LOCAL_SPECS
from health_harness_codex.schema import validate_arguments
from health_harness_codex.completion_contracts import build_completion_contract, validate_completion_contract
from health_harness_codex.models import ConflictError, Limits, ModelReply, Scope, ToolCall, ToolSpec
from health_harness_codex.providers import ModelResponseFormatError, ProviderError
from health_harness_codex.store import CaseStore
from health_harness_codex.tools import ToolRegistry, WorkspaceTools


def make_scope(patient: str = "p-1", case: str = "c-1") -> Scope:
    return Scope("env", "task", "org", "principal", patient, case)


def _test_completion_contract(scope: Scope, tool: str, path: str, *, phase: str = "final_readback",
                             op: str = "present", value: Any = None) -> dict[str, Any]:
    """A synthetic contract for tests whose task ends at one observed tool postcondition."""
    proof_kind = "terminal_write_response" if phase == "terminal_write_response" else "fresh_case_readback"
    return {
        "version": 1, "task_id": scope.task, "mapping_status": "mapped", "verified_task_goal": True,
        "scope": scope.to_dict(),
        "branches": [{"id": "synthetic_tool_postcondition", "proof_kind": proof_kind, "requirements": [
            {"id": "tool_postcondition", "tools": [tool], "phase": phase,
             "predicate": {"path": path, "op": op, "value": value}},
        ]}],
    }


class FakeModel:
    def __init__(self, replies: list[ModelReply]):
        self.replies = list(replies)
        self.seen: list[list[dict[str, Any]]] = []
        self.seen_tools: list[list[ToolSpec]] = []

    def complete(self, messages, tools, *, max_output_tokens):
        self.seen.append(json.loads(json.dumps(messages)))
        self.seen_tools.append(list(tools))
        if not self.replies:
            raise AssertionError("unexpected model request")
        return self.replies.pop(0)


class FailedModel:
    def complete(self, messages, tools, *, max_output_tokens):
        raise ProviderError("Codex turn reported a failure [failure_category=error:failed:rateLimitExceeded]",
                            failure_category="error:failed:rateLimitExceeded",
                            proposal_dispatch_safe=True, transient_retry_eligible=True)


class FormatErrorThenProseModel:
    def __init__(self):
        self.calls = 0

    def complete(self, messages, tools, *, max_output_tokens):
        self.calls += 1
        if self.calls == 1:
            raise ModelResponseFormatError("outer_json", {"input_tokens": 10})
        return ModelReply(content="A plain prose final.")


class FakeTools:
    def __init__(self, result: Any, *, effect: str = "read"):
        self.result = result
        self.effect = effect
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def list_tools(self):
        return [ToolSpec("records.lookup", "lookup a case record", {
            "type": "object", "required": ["patient_id"], "properties": {"patient_id": {"type": "string"}},
            "additionalProperties": False,
        }, effect=self.effect, identity_fields=("patient_id",))]

    def call(self, name, arguments):
        self.calls.append((name, arguments))
        if isinstance(self.result, Exception):
            raise self.result
        return self.result(arguments) if callable(self.result) else self.result


class ChangingCaseReadbackTools:
    def __init__(self):
        self.statuses = iter(("draft", "docs_needed"))

    def list_tools(self):
        return [ToolSpec("cases.get_case", "Read the current case state.", {
            "type": "object", "required": ["case_id"],
            "properties": {"case_id": {"type": "string"}}, "additionalProperties": False,
        }, effect="read", identity_fields=("case_id",))]

    def call(self, name, arguments):
        return {"case_id": arguments["case_id"], "case": {"id": arguments["case_id"],
                                                              "status": next(self.statuses)}}


class ProviderContractTools:
    def __init__(self, status: str = "docs_needed"):
        self.status = status
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def list_tools(self):
        return [
            ToolSpec("cases.create_from_order", "Create the patient case.", {
                "type": "object", "required": ["patient_id", "procedure_code", "requested_date"],
                "properties": {"patient_id": {"type": "string"}, "procedure_code": {"type": "string"},
                               "requested_date": {"type": "string"}}, "additionalProperties": False,
            }, effect="write", identity_fields=("patient_id",)),
            ToolSpec("auth.finalize_provider_determination", "Record the provider disposition.", {
                "type": "object", "required": ["case_id"],
                "properties": {"case_id": {"type": "string"}}, "additionalProperties": False,
            }, effect="write", identity_fields=("case_id",)),
            ToolSpec("cases.get_case", "Read the current case.", {
                "type": "object", "required": ["case_id"],
                "properties": {"case_id": {"type": "string"}}, "additionalProperties": False,
            }, effect="read", identity_fields=("case_id",)),
        ]

    def call(self, name, arguments):
        self.calls.append((name, arguments))
        if name == "cases.create_from_order":
            return {"case": {"id": "actual-case-7", "patient_id": arguments["patient_id"]}}
        if name == "auth.finalize_provider_determination":
            return {"case": {"id": "actual-case-7", "status": self.status}}
        return {"case": {"id": "actual-case-7", "status": self.status},
                "workflow_state": {"stage_detail": self.status}}


class PrincipalBindingTools:
    def __init__(self, review_case_id: str | None = "c-1", actors: list[Any] | None = None):
        self.review_case_id = review_case_id
        self.actors = list(actors or ["actor-1"])
        self.review_calls = 0
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def list_tools(self):
        return [
            ToolSpec("review.get_nurse_review_data", "Read the selected case review.", {
                "type": "object", "required": ["case_id"],
                "properties": {"case_id": {"type": "string"}}, "additionalProperties": False,
            }, effect="read", identity_fields=("case_id",)),
            ToolSpec("determination.finalize", "Finalize for the selected actor.", {
                "type": "object", "required": ["actor"],
                "properties": {"actor": {"type": "string"}}, "additionalProperties": False,
            }, effect="read", identity_fields=("actor",)),
        ]

    def call(self, name, arguments):
        self.calls.append((name, arguments))
        if name == "review.get_nurse_review_data":
            actor = self.actors[min(self.review_calls, len(self.actors) - 1)]
            self.review_calls += 1
            return {"structuredContent": {"triage": {
                "case_id": self.review_case_id, "actor": actor,
            }}}
        return {"accepted": True}


class RequestDateTools:
    def __init__(self):
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def list_tools(self):
        return [
            ToolSpec("cases.create_from_order", "Create the selected patient's prior authorization case.", {
                "type": "object",
                "required": ["patient_id", "procedure_code", "requested_date"],
                "properties": {
                    "patient_id": {"type": "string"},
                    "procedure_code": {"type": "string"},
                    "requested_date": {"anyOf": [
                        {"type": "string", "format": "date-time"}, {"type": "null"},
                    ]},
                },
                "additionalProperties": False,
            }, effect="write", identity_fields=("patient_id",)),
            ToolSpec("records.notify", "Send a side-effecting notice.", {
                "type": "object", "required": ["patient_id"],
                "properties": {"patient_id": {"type": "string"}}, "additionalProperties": False,
            }, effect="write", identity_fields=("patient_id",)),
        ]

    def call(self, name, arguments):
        self.calls.append((name, arguments))
        return {"receipt": "recorded"}


class HarnessTests(unittest.TestCase):
    def test_slow_provider_timeout_preserves_lease_and_failure_record(self):
        class ShortLeaseStore(CaseStore):
            def claim(self,scope,owner,ttl_seconds=60):return super().claim(scope,owner,ttl_seconds=.5)
            def maintained_claim(self,scope,owner,fence,**kwargs):
                return super().maintained_claim(scope,owner,fence,ttl_seconds=.5,interval_seconds=.05)
        class SlowFailure:
            def complete(self,*args,**kwargs):
                time.sleep(1.)
                raise ProviderError('synthetic request timed out',failure_category='transport:timeout')
        with closing(ShortLeaseStore(Path(self.temp.name)/'short-lease.sqlite')) as store:
            result=Harness(store,SlowFailure(),FakeTools({})).run(make_scope(),'Synthetic task','PA')
            self.assertEqual('error',result['status'])
            self.assertEqual(1,result['model_calls']);self.assertEqual(0,result['tool_calls'])
            self.assertEqual('ProviderError',result['model_failure']['error_type'])
            self.assertEqual('transport:timeout',result['model_failure']['failure_category'])

    def test_principal_binding_uses_only_explicit_same_case_review_path(self):
        model = FakeModel([
            ModelReply(tool_calls=(ToolCall("review", "review.get_nurse_review_data", {"case_id": "c-1"}),)),
            ModelReply(tool_calls=(ToolCall("finalize", "determination.finalize", {"actor": "actor-1"}),)),
            ModelReply(content=json.dumps({"status": "complete", "claim": "The case action completed.",
                                           "evidence_ids": ["ev:m1:review", "ev:m2:finalize"]})),
        ])
        tools = PrincipalBindingTools()
        harness = Harness(self.store, model, tools, principal_identity_result_paths={
            "review.get_nurse_review_data": ("structuredContent", "triage"),
        })
        result = harness.run(make_scope(), "Review and finalize the case", "UM")
        self.assertEqual("unresolved", result["status"])
        self.assertEqual("actor-1", result["principal_bindings"]["principal_id"])
        self.assertEqual("ev:m1:review", result["principal_bindings"]["source_evidence_id"])
        self.assertEqual("actor-1", tools.calls[1][1]["actor"])

    def test_principal_binding_quarantines_a_cross_case_review_record(self):
        model = FakeModel([
            ModelReply(tool_calls=(ToolCall("review", "review.get_nurse_review_data", {"case_id": "c-1"}),)),
        ])
        tools = PrincipalBindingTools(review_case_id="other-case")
        harness = Harness(self.store, model, tools, principal_identity_result_paths={
            "review.get_nurse_review_data": ("structuredContent", "triage"),
        })
        result = harness.run(make_scope(), "Review the case", "UM")
        self.assertEqual("blocked", result["status"])
        self.assertEqual({}, result["principal_bindings"])
        self.assertEqual("result_identity_mismatch", result["evidence"][0]["observed_result"]["error"])
        self.assertEqual(1, len(tools.calls))

    def test_principal_binding_quarantines_a_conflicting_later_actor(self):
        model = FakeModel([
            ModelReply(tool_calls=(ToolCall("review-1", "review.get_nurse_review_data", {"case_id": "c-1"}),)),
            ModelReply(tool_calls=(ToolCall("review-2", "review.get_nurse_review_data", {"case_id": "c-1"}),)),
        ])
        tools = PrincipalBindingTools(actors=["actor-1", "actor-2"])
        harness = Harness(self.store, model, tools, principal_identity_result_paths={
            "review.get_nurse_review_data": ("structuredContent", "triage"),
        })
        result = harness.run(make_scope(), "Review the case", "UM")
        self.assertEqual("blocked", result["status"])
        self.assertEqual("actor-1", result["principal_bindings"]["principal_id"])
        self.assertEqual("result_identity_mismatch", result["evidence"][-1]["observed_result"]["error"])
        self.assertEqual(2, len(tools.calls))

    def test_principal_actor_without_matching_case_id_does_not_bind(self):
        model = FakeModel([
            ModelReply(tool_calls=(ToolCall("review", "review.get_nurse_review_data", {"case_id": "c-1"}),)),
            ModelReply(tool_calls=(ToolCall("finalize", "determination.finalize", {"actor": "actor-1"}),)),
        ])
        tools = PrincipalBindingTools(review_case_id=None)
        harness = Harness(self.store, model, tools, principal_identity_result_paths={
            "review.get_nurse_review_data": ("structuredContent", "triage"),
        })
        result = harness.run(make_scope(), "Review and finalize the case", "UM")
        self.assertEqual("error", result["status"])
        self.assertEqual({}, result["principal_bindings"])
        self.assertEqual(1, len(tools.calls))

    def test_principal_binding_rejects_malformed_actor_value(self):
        model = FakeModel([
            ModelReply(tool_calls=(ToolCall("review", "review.get_nurse_review_data", {"case_id": "c-1"}),)),
        ])
        tools = PrincipalBindingTools(actors=[123])
        harness = Harness(self.store, model, tools, principal_identity_result_paths={
            "review.get_nurse_review_data": ("structuredContent", "triage"),
        })
        result = harness.run(make_scope(), "Review the case", "UM")
        self.assertEqual("blocked", result["status"])
        self.assertEqual({}, result["principal_bindings"])
        self.assertEqual("result_identity_mismatch", result["evidence"][0]["observed_result"]["error"])

    def test_review_actor_does_not_bind_without_explicit_trusted_path(self):
        model = FakeModel([
            ModelReply(tool_calls=(ToolCall("review", "review.get_nurse_review_data", {"case_id": "c-1"}),)),
            ModelReply(tool_calls=(ToolCall("finalize", "determination.finalize", {"actor": "actor-1"}),)),
        ])
        tools = PrincipalBindingTools()
        result = Harness(self.store, model, tools).run(make_scope(), "Review and finalize the case", "UM")
        self.assertEqual("error", result["status"])
        self.assertEqual({}, result["principal_bindings"])
        self.assertEqual(1, len(tools.calls))

    def test_plain_prose_gets_one_charged_tool_free_format_correction(self):
        model = FakeModel([
            ModelReply(tool_calls=(ToolCall("read", "records.lookup", {"patient_id": "p-1"}),)),
            ModelReply(content="I completed the assigned lookup."),
            ModelReply(content=json.dumps({"status": "complete", "claim": "The lookup completed.",
                                           "evidence_ids": ["ev:m1:read"]})),
        ])
        tools = FakeTools({"patient_id": "p-1"})
        result = Harness(self.store, model, tools, limits=Limits(max_model_calls=3)).run(
            make_scope(), "Read the source", "UM",
            completion_contract=_test_completion_contract(make_scope(), "records.lookup", "patient_id"))
        self.assertEqual("complete", result["status"], result.get("completion_gate"))
        self.assertEqual(3, result["model_calls"])
        self.assertEqual(1, result["final_format_retry_count"])
        self.assertEqual(0, result["model_response_format_retry_count"])
        self.assertEqual([], model.seen_tools[-1])
        self.assertEqual([("records.lookup", {"patient_id": "p-1"})], tools.calls)

    def test_final_format_correction_never_dispatches_proposed_tools(self):
        model = FakeModel([
            ModelReply(tool_calls=(ToolCall("read", "records.lookup", {"patient_id": "p-1"}),)),
            ModelReply(content="I completed the assigned lookup."),
            ModelReply(tool_calls=(ToolCall("again", "records.lookup", {"patient_id": "p-1"}),)),
        ])
        tools = FakeTools({"patient_id": "p-1"})
        result = Harness(self.store, model, tools, limits=Limits(max_model_calls=3)).run(
            make_scope(), "Read the source", "UM")
        self.assertEqual("error", result["status"])
        self.assertIn("was not dispatched", result["message"])
        self.assertEqual(1, result["final_format_retry_count"])
        self.assertEqual(1, len(tools.calls))

    def test_plain_prose_at_model_call_limit_does_not_make_extra_call(self):
        model = FakeModel([
            ModelReply(tool_calls=(ToolCall("read", "records.lookup", {"patient_id": "p-1"}),)),
            ModelReply(content="I completed the assigned lookup."),
        ])
        result = Harness(self.store, model, FakeTools({"patient_id": "p-1"}),
                         limits=Limits(max_model_calls=2)).run(make_scope(), "Read the source", "UM")
        self.assertEqual("unresolved", result["status"])
        self.assertEqual(2, result["model_calls"])
        self.assertEqual(0, result["final_format_retry_count"])

    def test_malformed_format_correction_does_not_trigger_another_retry(self):
        model = FakeModel([
            ModelReply(tool_calls=(ToolCall("read", "records.lookup", {"patient_id": "p-1"}),)),
            ModelReply(content="I completed the assigned lookup."),
            ModelReply(content="Still prose."),
        ])
        result = Harness(self.store, model, FakeTools({"patient_id": "p-1"}),
                         limits=Limits(max_model_calls=4)).run(make_scope(), "Read the source", "UM")
        self.assertEqual("unresolved", result["status"])
        self.assertEqual(3, result["model_calls"])
        self.assertEqual(1, result["final_format_retry_count"])

    def test_provider_and_final_format_corrections_share_one_retry_budget(self):
        model = FormatErrorThenProseModel()
        result = Harness(self.store, model, FakeTools({})).run(make_scope(), "Read the source", "UM")
        self.assertEqual("unresolved", result["status"])
        self.assertEqual(2, model.calls)
        self.assertEqual(1, result["model_response_format_retry_count"])
        self.assertEqual(0, result["final_format_retry_count"])

    def test_pre_dispatch_schema_rejection_retries_one_tool_without_siblings(self):
        model = FakeModel([
            ModelReply(tool_calls=(
                ToolCall("create", "cases.create_from_order", {
                    "patient_id": "p-1", "procedure_code": "A123", "requested_date": "2026-10-21",
                }),
                ToolCall("notify", "records.notify", {"patient_id": "p-1"}),
            )),
            ModelReply(tool_calls=(ToolCall("create-corrected", "cases.create_from_order", {
                "patient_id": "p-1", "procedure_code": "A123", "requested_date": "2026-10-21T00:00:00Z",
            }),)),
            ModelReply(content=json.dumps({"status": "complete", "claim": "The case was created.",
                                           "evidence_ids": ["ev:m1:create"]})),
        ])
        tools = RequestDateTools()
        result = Harness(self.store, model, tools, limits=Limits(max_model_calls=3)).run(
            make_scope(), "Create the assigned case", "PA",
            completion_contract=_test_completion_contract(make_scope(), "cases.create_from_order", "receipt",
                                                          phase="terminal_write_response"))
        self.assertEqual("complete", result["status"])
        self.assertEqual(3, result["model_calls"])
        self.assertEqual(1, result["tool_calls"])
        self.assertEqual(1, result["pre_dispatch_validation_retry_count"])
        self.assertEqual([("cases.create_from_order", {
            "patient_id": "p-1", "procedure_code": "A123", "requested_date": "2026-10-21T00:00:00Z",
        })], tools.calls)
        self.assertEqual(["cases.create_from_order"], [spec.name for spec in model.seen_tools[1]])
        error_results = [json.loads(m["content"]) for m in model.seen[1] if m.get("role") == "tool"]
        self.assertIn({"error": "arguments_rejected_before_dispatch", "category": "schema_any_of",
                       "path": "$.requested_date"}, error_results)
        self.assertIn({"error": "not_dispatched_after_validation_rejection",
                       "category": "schema_any_of"}, error_results)
        self.assertNotIn("2026-10-21", json.dumps(error_results))

    def test_nested_retrieval_array_error_supplies_actionable_constraints_without_values(self):
        spec=next(s for s in _LOCAL_SPECS if s.name=='case.retrieve_evidence')
        args={'requests':[{'id':'private-source','queries':['private phrase '+str(i) for i in range(9)]}]}
        try:validate_arguments(spec,args,make_scope())
        except ValueError as exc:feedback=_safe_validation_feedback(exc,spec)
        else:self.fail('nine queries must fail the declared maximum')
        self.assertEqual({'category':'schema_array_bounds','path':'$.requests[0].queries',
                          'constraints':{'maxItems':8}},feedback)
        self.assertNotIn('private',json.dumps(feedback))
        self.assertEqual({'category':'schema_array_bounds'},_safe_validation_feedback(
            ValueError('array length at $.unknown[0].secret is out of bounds'),spec))

    def test_nested_retrieval_correction_dispatches_all_queries_without_replaying_reads(self):
        source='Original source text contains a detailed synthetic clinical narrative.'
        queries=['synthetic question '+str(i) for i in range(9)]
        invalid={'requests':[{'id':'ev:m1:read','queries':queries}]}
        corrected={'requests':[{'id':'ev:m1:read','queries':queries[:8]},
                               {'id':'ev:m1:read','queries':queries[8:]}]}
        tools=FakeTools({'text':source})
        model=FakeModel([
            ModelReply(tool_calls=(ToolCall('read','records.lookup',{'patient_id':'p-1'}),)),
            ModelReply(tool_calls=(ToolCall('search','case.retrieve_evidence',invalid),)),
            ModelReply(tool_calls=(ToolCall('search-corrected','case.retrieve_evidence',corrected),)),
            ModelReply(content=json.dumps({'status':'incomplete','claim':'Synthetic retrieval check only.',
                                          'evidence_ids':['ev:m1:read']})),
        ])
        result=Harness(self.store,model,tools,limits=Limits(max_model_calls=4)).run(
            make_scope(),'Read original evidence','PA')
        self.assertNotEqual('error',result['status'])
        feedback=[json.loads(m['content']) for m in model.seen[2] if m.get('role')=='tool'
                  and 'arguments_rejected_before_dispatch' in m.get('content','')]
        self.assertEqual(8,feedback[0]['constraints']['maxItems'])
        self.assertEqual('$.requests[0].queries',feedback[0]['path'])
        self.assertEqual(1,len(tools.calls))
        self.assertEqual(1,result['pre_dispatch_validation_retry_count'])

    def test_pre_dispatch_identity_rejection_without_observed_identity_is_not_retried(self):
        model = FakeModel([
            ModelReply(tool_calls=(ToolCall("finalize", "determination.finalize", {"actor": "unobserved-actor"}),)),
            ModelReply(content=json.dumps({"status": "complete", "claim": "Invented identity used.",
                                           "evidence_ids": ["ev:m1:finalize"]})),
        ])
        tools = PrincipalBindingTools()
        result = Harness(self.store, model, tools).run(make_scope(), "Finalize the case", "UM")
        self.assertEqual("error", result["status"])
        self.assertEqual(1, result["model_calls"])
        self.assertEqual(0, result["pre_dispatch_validation_retry_count"])
        self.assertEqual([], tools.calls)

    def test_resume_does_not_replay_calls_already_answered_as_skipped(self):
        scope = make_scope()
        self.store.open_case(scope, "Read then apply", "PA")
        state = self.store.load_case(scope)
        state.update({"status": "running", "model_calls": 1, "tool_calls": 2,
                      "processed_tool_calls": ["m1:invalid", "m1:skipped"]})
        state["messages"] = [
            {"role": "system", "content": "system"},
            {"role": "user", "content": "Read then apply"},
            {"role": "assistant", "content": "", "tool_calls": [
                {"id": "invalid", "journal_id": "m1:invalid", "name": "records.lookup",
                 "arguments": {"patient_id": "wrong-patient"}},
                {"id": "skipped", "journal_id": "m1:skipped", "name": "records.lookup",
                 "arguments": {"patient_id": "p-1"}},
            ]},
            {"role": "tool", "tool_call_id": "invalid", "name": "records.lookup",
             "content": json.dumps({"error": "arguments_rejected_before_dispatch",
                                    "category": "identity_scope", "path": "$.patient_id"})},
            {"role": "tool", "tool_call_id": "skipped", "name": "records.lookup",
             "content": json.dumps({"error": "not_dispatched_after_validation_rejection",
                                    "category": "identity_scope"})},
        ]
        self.store.save_case(scope, state, 0)
        model = FakeModel([ModelReply(content=json.dumps({"status": "incomplete",
                                                          "claim": "One read was rejected before dispatch.",
                                                          "evidence_ids": []}))])
        tools = FakeTools({"patient_id": "p-1"})

        result = Harness(self.store, model, tools).run(scope, "Read then apply", "PA", resume=True)

        self.assertEqual("unresolved", result["status"])
        self.assertEqual([], tools.calls)
        self.assertEqual(2, result["model_calls"])
        self.assertEqual([], Harness._pending_tool_calls(self.store.load_case(scope)))

    def test_failed_pre_dispatch_correction_is_not_retried_again(self):
        model = FakeModel([
            ModelReply(tool_calls=(ToolCall("create", "cases.create_from_order", {
                "patient_id": "p-1", "procedure_code": "A123", "requested_date": "2026-10-21",
            }),)),
            ModelReply(tool_calls=(ToolCall("create-corrected", "cases.create_from_order", {
                "patient_id": "p-1", "procedure_code": "A123", "requested_date": "still-invalid",
            }),)),
        ])
        tools = RequestDateTools()
        result = Harness(self.store, model, tools, limits=Limits(max_model_calls=4)).run(
            make_scope(), "Create the assigned case", "PA")
        self.assertEqual("error", result["status"])
        self.assertEqual(2, result["model_calls"])
        self.assertEqual(1, result["pre_dispatch_validation_retry_count"])
        self.assertEqual([], tools.calls)

    def test_pre_dispatch_correction_uses_shared_retry_budget_with_final_prose(self):
        model = FakeModel([
            ModelReply(tool_calls=(ToolCall("create", "cases.create_from_order", {
                "patient_id": "p-1", "procedure_code": "A123", "requested_date": "2026-10-21",
            }),)),
            ModelReply(content="The date format is unclear, so I cannot create the case."),
        ])
        result = Harness(self.store, model, RequestDateTools(), limits=Limits(max_model_calls=4)).run(
            make_scope(), "Create the assigned case", "PA")
        self.assertEqual("unresolved", result["status"])
        self.assertEqual(2, result["model_calls"])
        self.assertEqual(1, result["pre_dispatch_validation_retry_count"])
        self.assertEqual(0, result["final_format_retry_count"])

    def test_model_failure_result_preserves_only_safe_retry_metadata(self):
        tools = FakeTools({})
        result = Harness(self.store, FailedModel(), tools).run(make_scope(), "Read the source", "UM")
        self.assertEqual("error", result["status"])
        self.assertEqual({
            "error_type": "ProviderError",
            "failure_category": "error:failed:rateLimitExceeded",
            "proposal_dispatch_safe": True,
            "transient_retry_eligible": True,
        }, result["model_failure"])
        self.assertEqual([], tools.calls)

    def test_disconnected_generation_retries_once_without_replaying_completed_write(self):
        failure=ProviderError('disconnected',failure_category='error:unknown:responseStreamDisconnected',
            proposal_dispatch_safe=True,transient_retry_eligible=True,
            diagnostics={'cleanup_confirmed':True,'request_timed_out':False},usage={'input_tokens':7})
        class Model:
            calls=0
            def complete(self,messages,tools,**kwargs):
                self.calls+=1
                if self.calls==1:return ModelReply(tool_calls=(ToolCall('saved','records.lookup',{'patient_id':'p-1'}),))
                if self.calls==2:raise failure
                return ModelReply(content=json.dumps({'status':'complete','claim':'Observed saved record.',
                    'evidence_ids':['ev:m1:saved']}))
        tools=FakeTools({'patient_id':'p-1'},effect='write')
        result=Harness(self.store,Model(),tools,limits=Limits(max_model_calls=3)).run(
            make_scope(),'Save once','UM',completion_contract=_test_completion_contract(
                make_scope(),'records.lookup','patient_id',phase='terminal_write_response'))
        self.assertEqual('complete',result['status'],result.get('message'))
        self.assertEqual(3,result['model_calls'])
        self.assertEqual(1,len(tools.calls))
        self.assertEqual(7,result['usage']['input_tokens'])
        self.assertEqual([{'failed_model_call':2,'retry_model_call':3,
            'failure_category':'error:unknown:responseStreamDisconnected','proposal_dispatched':False}],
            result['model_transport_retries'])

    def test_disconnection_retry_is_bounded_and_requires_cleanup_and_remaining_budget(self):
        for cleanup,budget,expected_calls in ((True,5,2),(False,5,1),(True,1,1)):
            with self.subTest(cleanup=cleanup,budget=budget),closing(CaseStore(':memory:')) as store:
                class Model:
                    calls=0
                    def complete(self,*args,**kwargs):
                        self.calls+=1
                        raise ProviderError('disconnected',failure_category='error:unknown:responseStreamDisconnected',
                            proposal_dispatch_safe=True,transient_retry_eligible=True,
                            diagnostics={'cleanup_confirmed':cleanup,'request_timed_out':False})
                model=Model();tools=FakeTools({})
                result=Harness(store,model,tools,limits=Limits(max_model_calls=budget)).run(
                    make_scope(),'Read','UM')
                self.assertEqual('error',result['status'])
                self.assertEqual(expected_calls,model.calls)
                self.assertEqual([],tools.calls)
                self.assertEqual(expected_calls-1,len(result['model_transport_retries']))

    def test_rehydration_keeps_original_source_id_and_cannot_support_invented_citation(self):
        for citation, expected in (("ev:m1:source", "complete"), ("ev:m2:rehydrate", "unresolved")):
            with self.subTest(citation=citation):
                store = CaseStore(":memory:")
                try:
                    responses = [
                        ModelReply(tool_calls=(ToolCall("source", "records.lookup", {"patient_id": "p-1"}),)),
                        ModelReply(tool_calls=(ToolCall("rehydrate", "case.read_evidence",
                                                       {"id": "ev:m1:source", "offset": 0, "length": 1000}),)),
                        ModelReply(content=json.dumps({"status": "complete", "claim": "Source was read",
                                                       "evidence_ids": [citation]})),
                    ]
                    if expected=='unresolved':
                        responses.append(ModelReply(content=json.dumps({'status':'complete','claim':'Source was read',
                                                                        'evidence_ids':[citation]})))
                    model=FakeModel(responses)
                    result = Harness(store, model, FakeTools({"patient_id": "p-1"})).run(
                        make_scope(), "Read the source", "UM",
                        completion_contract=_test_completion_contract(make_scope(), "records.lookup", "patient_id"))
                    self.assertEqual(expected, result["status"])
                    self.assertEqual(["ev:m1:source"], [e["id"] for e in result["evidence"]])
                    rehydrated = json.loads(model.seen[2][-1]["content"])
                    self.assertEqual("ev:m1:source", rehydrated["id"])
                    if expected=='unresolved':self.assertEqual(1,result['final_format_retry_count'])
                finally:
                    store.close()

    def test_search_evidence_returns_source_offsets_roundtrips_and_creates_no_evidence(self):
        source = {"patient_id": "p-1", "body": ("x" * 12000) +
                 " Original Policy Phrase appears here. " + ("y" * 500) + " ORIGINAL policy phrase again."}
        serialized = json.dumps(source, ensure_ascii=False, sort_keys=True, default=str)
        match_offset = serialized.index("Original Policy Phrase")
        snippet_offset = max(0, match_offset - 150)
        snippet_end = min(len(serialized), snippet_offset + 400)
        snippet_length = snippet_end - snippet_offset
        model = FakeModel([
            ModelReply(tool_calls=(ToolCall("source", "records.lookup", {"patient_id": "p-1"}),)),
            ModelReply(tool_calls=(ToolCall("search", "case.search_evidence", {
                "id": "ev:m1:source", "query": "original policy phrase", "max_results": 1}),)),
            ModelReply(tool_calls=(ToolCall("read", "case.read_evidence", {
                "id": "ev:m1:source", "offset": snippet_offset, "length": snippet_length}),)),
            ModelReply(content=json.dumps({"status": "complete", "claim": "The original observation was searched and re-read.",
                                          "evidence_ids": ["ev:m1:source"]})),
        ])
        tools = FakeTools(source)

        result = Harness(self.store, model, tools).run(
            make_scope(), "Read the source", "UM",
            completion_contract=_test_completion_contract(make_scope(), "records.lookup", "patient_id"))

        self.assertEqual("complete", result["status"])
        self.assertEqual(1, len(result["evidence"]))
        self.assertEqual("ev:m1:source", result["evidence"][0]["id"])
        search_reply = json.loads(model.seen[2][-1]["content"])
        self.assertEqual("ev:m1:source", search_reply["id"])
        self.assertEqual(len(serialized), search_reply["total_chars"])
        self.assertTrue(search_reply["has_more"])
        self.assertEqual(1, len(search_reply["matches"]))
        match = search_reply["matches"][0]
        self.assertEqual(snippet_offset, match["offset"])
        self.assertEqual(snippet_length, match["length"])
        self.assertEqual(match_offset, match["match_offset"])
        self.assertIn("Original Policy Phrase", match["text"])
        read_reply = json.loads(model.seen[3][-1]["content"])
        self.assertEqual("ev:m1:source", read_reply["id"])
        self.assertEqual(snippet_offset, read_reply["offset"])
        self.assertEqual(match["text"], read_reply["text"])
        self.assertEqual([("records.lookup", {"patient_id": "p-1"})], tools.calls)

    def test_search_evidence_rejects_invented_and_failed_sources(self):
        cases = (
            ("invented", "ev:m9:invented", [], "not present"),
            ("failed", "ev:m1:read", [ModelReply(tool_calls=(ToolCall(
                "read", "records.lookup", {"patient_id": "p-1"}),))], "only successful evidence"),
        )
        for name, source_id, prefix, expected_error in cases:
            with self.subTest(source=name):
                store = CaseStore(":memory:")
                try:
                    model = FakeModel([
                        *prefix,
                        ModelReply(tool_calls=(ToolCall("search", "case.search_evidence", {
                            "id": source_id, "query": "needle"}),)),
                        ModelReply(content="The source search could not be completed."),
                    ])
                    tools = FakeTools({"error": "source read failed"})
                    result = Harness(store, model, tools, limits=Limits(max_model_calls=2 + len(prefix))).run(
                        make_scope(), "Search source", "UM")
                    self.assertNotEqual("complete", result["status"])
                    self.assertEqual(1 if prefix else 0, len(result["evidence"]))
                    self.assertEqual(1 if prefix else 0, len(tools.calls))
                    error_message = model.seen[-1][-1]["content"]
                    self.assertIn(expected_error, error_message)
                    if prefix:
                        self.assertEqual("failure", result["evidence"][0]["outcome"])
                finally:
                    store.close()

    def test_search_evidence_treats_regex_metacharacters_as_literal_text(self):
        model = FakeModel([
            ModelReply(tool_calls=(ToolCall("source", "records.lookup", {"patient_id": "p-1"}),)),
            ModelReply(tool_calls=(ToolCall("search", "case.search_evidence", {
                "id": "ev:m1:source", "query": ".*[]"}),)),
            ModelReply(content="No further claim."),
        ])
        tools = FakeTools({"patient_id": "p-1", "text": "literal .*[] only"})

        Harness(self.store, model, tools, limits=Limits(max_model_calls=3)).run(
            make_scope(), "Literal search", "UM")

        search_reply = json.loads(model.seen[-1][-1]["content"])
        self.assertEqual(1, len(search_reply["matches"]))
        self.assertIn("literal .*[] only", search_reply["matches"][0]["text"])
        self.assertFalse(search_reply["has_more"])

    def test_search_evidence_cannot_access_another_case_source_id(self):
        secret_body = "UNIQUE_CROSS_CASE_SOURCE_BODY"
        tools = FakeTools({"patient_id": "patient-A", "private": secret_body})
        source_model = FakeModel([ModelReply(tool_calls=(ToolCall(
            "read-a", "records.lookup", {"patient_id": "patient-A"}),)), ModelReply(content="Source recorded.")])
        first_scope = make_scope("patient-A", "case-A")
        first = Harness(self.store, source_model, tools).run(first_scope, "Record A", "UM")
        self.assertEqual("ev:m1:read-a", first["evidence"][0]["id"])

        second_model = FakeModel([
            ModelReply(tool_calls=(ToolCall("search-b", "case.search_evidence", {
                "id": "ev:m1:read-a", "query": "cross case"}),)),
            ModelReply(content="No source from another case is available."),
        ])
        second_scope = make_scope("patient-B", "case-B")
        second = Harness(self.store, second_model, tools, limits=Limits(max_model_calls=2)).run(
            second_scope, "Search B", "UM")

        self.assertEqual([], second["evidence"])
        self.assertNotIn(secret_body, json.dumps(second_model.seen))
        self.assertIn("not present in this case", second_model.seen[-1][-1]["content"])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = CaseStore(Path(self.temp.name) / "state.sqlite")

    def tearDown(self):
        self.store.close()
        self.temp.cleanup()

    def test_scoped_completion_requires_successful_observation_and_closed_obligation(self):
        model = FakeModel([
            ModelReply(tool_calls=(ToolCall("read", "records.lookup", {"patient_id": "p-1"}),)),
            ModelReply(tool_calls=(ToolCall("ob1", "case.add_obligation", {"id": "review", "description": "Review the observed response"}),)),
            ModelReply(tool_calls=(ToolCall("close1", "case.close_obligation", {"id": "review", "evidence_ids": ["ev:m1:read"]}),)),
            ModelReply(content=json.dumps({"status": "complete", "claim": "The assigned lookup returned a case-scoped result.", "evidence_ids": ["ev:m1:read"]})),
        ])
        tools = FakeTools({"patient_id": "p-1", "record_status": "present"})
        harness = Harness(self.store, model, tools)
        result = harness.run(make_scope(), "Check this record", "PA",
                             completion_contract=_test_completion_contract(make_scope(), "records.lookup", "record_status"))
        self.assertEqual("complete", result["status"])
        self.assertEqual("closed", result["obligations"][0]["status"])
        self.assertEqual("success", result["evidence"][0]["outcome"])
        self.assertEqual("task-contract verified local workflow; not official benchmark success",
                         result["completion"]["kind"])

    def test_completion_claim_without_trusted_task_contract_is_unresolved(self):
        model = FakeModel([
            ModelReply(tool_calls=(ToolCall("read", "records.lookup", {"patient_id": "p-1"}),)),
            ModelReply(content=json.dumps({"status": "complete", "claim": "The lookup succeeded.",
                                          "evidence_ids": ["ev:m1:read"]})),
        ])
        result = Harness(self.store, model, FakeTools({"patient_id": "p-1", "record_status": "draft"})).run(
            make_scope(), "Complete the assigned workflow", "PA")
        self.assertEqual("unresolved", result["status"])
        self.assertIsNone(result["completion"])
        self.assertEqual("completion_contract_missing", result["completion_gate"]["reason_code"])
        self.assertEqual(0, result["completion_gate_corrections"])

    def test_unverified_public_goal_cannot_become_complete_from_a_successful_lookup(self):
        model = FakeModel([
            ModelReply(tool_calls=(ToolCall("read", "records.lookup", {"patient_id": "p-1"}),)),
            ModelReply(content=json.dumps({"status": "complete", "claim": "The referral is finished.",
                                          "evidence_ids": ["ev:m1:read"]})),
        ])
        contract = {"version": 1, "task_id": "task", "mapping_status": "unverified", "branches": []}
        result = Harness(self.store, model, FakeTools({"patient_id": "p-1", "record_status": "draft"})).run(
            make_scope(), "Clinical intake", "PA", completion_contract=contract)
        self.assertEqual("unresolved", result["status"])
        self.assertEqual("goal_unverified", result["completion_gate"]["reason_code"])
        self.assertIsNone(result["completion"])

    def test_completion_contract_cannot_change_when_resuming_a_case(self):
        model = FakeModel([ModelReply(content=json.dumps({"status": "incomplete",
                                                           "claim": "Work remains.",
                                                           "evidence_ids": []}))])
        first_contract = {"version": 1, "task_id": "task", "status": "mapped", "branches": []}
        second_contract = {**first_contract, "instruction_sha256": "different-public-instruction"}
        harness = Harness(self.store, model, FakeTools({"patient_id": "p-1"}))
        first = harness.run(make_scope(), "Review this case", "PA", completion_contract=first_contract)
        self.assertEqual("unresolved", first["status"])
        with self.assertRaisesRegex(ConflictError, "completion contract cannot change"):
            harness.run(make_scope(), "Review this case", "PA", resume=True,
                        completion_contract=second_contract)

    def test_persisted_completion_contract_content_must_match_its_pin(self):
        scope = make_scope()
        contract = _test_completion_contract(scope, "records.lookup", "patient_id")
        model = FakeModel([ModelReply(content=json.dumps({"status": "incomplete",
                                                           "claim": "Work remains.",
                                                           "evidence_ids": []}))])
        harness = Harness(self.store, model, FakeTools({"patient_id": "p-1"}))
        first = harness.run(scope, "Review this case", "PA", completion_contract=contract)
        self.assertEqual("unresolved", first["status"])
        state = self.store.load_case(scope)
        state["completion_contract"]["branches"][0]["id"] = "changed_after_pin"
        self.store.save_case(scope, state, state["version"])
        with self.assertRaisesRegex(ConflictError, "failed integrity validation"):
            harness.run(scope, "Review this case", "PA", resume=True)

        final_state = {
            "scope": scope.to_dict(), "completion_contract": contract,
            "completion_contract_sha256": "incorrect-pin", "evidence": [{
                "id": "ev:observed", "scope": scope.to_dict(), "tool": "records.lookup",
                "effect": "read", "outcome": "success", "observed_result": {"patient_id": "p-1"},
            }],
            "obligations": [], "messages": [], "model_calls": 1,
        }
        final = harness._accept_final(final_state, json.dumps({
            "status": "complete", "claim": "The task is complete.", "evidence_ids": ["ev:observed"],
        }))
        self.assertEqual("unresolved", final["status"])
        self.assertEqual("completion_contract_integrity_error", final["completion_gate"]["reason_code"])

    def test_completion_contract_requires_fresh_same_case_terminal_readback(self):
        scope = make_scope().to_dict()
        contract = {
            "version": 1, "task_id": "task", "mapping_status": "mapped", "verified_task_goal": True,
            "scope": scope,
            "branches": [{"id": "docs_needed", "proof_kind": "fresh_case_readback", "requirements": [
                {"id": "disposition", "tools": ["auth.finalize_provider_determination"], "phase": "any",
                 "predicate": {"path": "case.status", "op": "eq", "value": "docs_needed"}},
                {"id": "final_readback", "tools": ["cases.get_case"], "phase": "final_readback",
                 "predicate": {"path": "case.status", "op": "eq", "value": "docs_needed"}},
                {"id": "case_scope", "tools": ["cases.get_case"], "phase": "final_readback",
                 "predicate": {"path": "case.id", "op": "matches_scope_case", "value": None}},
            ]}],
        }
        evidence = [
            {"id": "ev:write", "scope": scope, "tool": "auth.finalize_provider_determination",
             "effect": "write", "outcome": "success",
             "observed_result": {"case": {"id": "c-1", "status": "docs_needed"}}},
            {"id": "ev:read", "scope": scope, "tool": "cases.get_case", "effect": "read",
             "outcome": "success", "observed_result": {"case": {"id": "c-1", "status": "draft"}}},
        ]
        stale = validate_completion_contract(contract, evidence, scope)
        self.assertFalse(stale["accepted"])
        self.assertIn("final_readback", stale["missing_milestones"])

        evidence[1]["observed_result"]["case"]["status"] = "docs_needed"
        fresh = validate_completion_contract(contract, evidence, scope)
        self.assertTrue(fresh["accepted"])
        self.assertEqual("docs_needed", fresh["branch_id"])
        evidence.append({"id": "ev:later-write", "scope": scope, "tool": "records.update",
                         "effect": "write", "outcome": "success", "observed_result": {"ok": True}})
        stale_after_write = validate_completion_contract(contract, evidence, scope)
        self.assertFalse(stale_after_write["accepted"])

        wrong_case = [dict(item, scope={**scope, "case": "other-case"}) for item in evidence[:2]]
        wrong_scope = validate_completion_contract(contract, wrong_case, scope)
        self.assertFalse(wrong_scope["accepted"])

    def test_late_bound_provider_case_verifies_without_changing_durable_scope(self):
        durable_scope = Scope("env", "task", "org", "principal",
                              "patient-placeholder", "case-subject:patient-placeholder")
        scope_dict = durable_scope.to_dict()
        contract = {
            "version": 1, "task_id": "task", "mapping_status": "mapped", "verified_task_goal": True,
            "scope": scope_dict,
            "branches": [{"id": "docs_needed", "proof_kind": "fresh_case_readback", "requirements": [
                {"id": "disposition", "tools": ["auth.finalize_provider_determination"], "phase": "any",
                 "predicate": {"path": "case.status", "op": "eq", "value": "docs_needed"}},
                {"id": "readback", "tools": ["cases.get_case"], "phase": "final_readback",
                 "predicate": {"path": "case.status", "op": "eq", "value": "docs_needed"}},
                {"id": "actual_case_identity", "tools": ["cases.get_case"], "phase": "final_readback",
                 "predicate": {"path": "case.id", "op": "matches_evidence", "value": {
                     "tool": "cases.create_from_order", "path": "case.id"}}},
            ]}],
        }
        evidence = [
            {"id": "ev:create", "scope": scope_dict, "tool": "cases.create_from_order", "effect": "write",
             "outcome": "success", "observed_result": {"case": {"id": "actual-case-7"}}},
            {"id": "ev:disposition", "scope": scope_dict, "tool": "auth.finalize_provider_determination",
             "effect": "write", "outcome": "success", "observed_result": {"case": {"status": "docs_needed"}}},
            {"id": "ev:readback", "scope": scope_dict, "tool": "cases.get_case", "effect": "read",
             "outcome": "success", "observed_result": {"case": {"id": "actual-case-7", "status": "docs_needed"}}},
        ]
        state = {
            "scope": scope_dict, "completion_contract": contract, "evidence": evidence,
            "obligations": [], "model_calls": 1,
            "messages": [],
            "completion_contract_sha256": _completion_contract_hash(contract),
            "case_bindings": {"case_namespace": scope_dict["case"], "case_id": "actual-case-7",
                              "patient_id": scope_dict["patient"], "source_tool": "cases.create_from_order",
                              "source_evidence_id": "ev:create", "method": "same_case_provider_creation_result"},
        }
        harness = Harness(self.store, FakeModel([]), FakeTools({}),
                          case_identity_tools=("cases.create_from_order",))
        self.assertEqual("actual-case-7", harness._identity_scope(durable_scope, state).case)
        result = harness._accept_final(state, json.dumps({"status": "complete", "claim": "Disposition verified.",
                                                          "evidence_ids": ["ev:disposition", "ev:readback"]}))
        self.assertEqual("complete", result["status"], result.get("completion_gate"))
        self.assertEqual("actual-case-7", harness._identity_scope(durable_scope, result).case)
        self.assertEqual("case-subject:patient-placeholder", result["completion"]["scope"]["case"])

    def test_premature_claim_on_draft_gets_bounded_readback_correction(self):
        contract = {
            "version": 1, "task_id": "task", "mapping_status": "mapped", "verified_task_goal": True,
            "scope": make_scope().to_dict(),
            "branches": [{"id": "docs_needed", "proof_kind": "fresh_case_readback", "requirements": [
                {"id": "case_status_docs_needed", "tools": ["cases.get_case"], "phase": "final_readback",
                 "predicate": {"path": "case.status", "op": "eq", "value": "docs_needed"}},
            ]}],
        }
        model = FakeModel([
            ModelReply(tool_calls=(ToolCall("read1", "cases.get_case", {"case_id": "c-1"}),)),
            ModelReply(content=json.dumps({"status": "complete", "claim": "The case is complete.",
                                          "evidence_ids": ["ev:m1:read1"]})),
            ModelReply(tool_calls=(ToolCall("read2", "cases.get_case", {"case_id": "c-1"}),)),
            ModelReply(content=json.dumps({"status": "complete", "claim": "The case is awaiting documents.",
                                          "evidence_ids": ["ev:m3:read2"]})),
        ])
        result = Harness(self.store, model, ChangingCaseReadbackTools()).run(
            make_scope(), "Prepare the case", "PA", completion_contract=contract)
        self.assertEqual("complete", result["status"])
        self.assertEqual("docs_needed", result["completion"]["branch_id"])
        self.assertEqual(1, result["completion_gate_corrections"])
        self.assertEqual("draft", result["evidence"][0]["observed_result"]["case"]["status"])
        self.assertEqual("docs_needed", result["evidence"][1]["observed_result"]["case"]["status"])

    def test_real_builder_contract_runs_through_harness_for_verified_and_incomplete_paths(self):
        instruction = "Please gather more evidence and finalize the provider determination."

        complete_scope = Scope("env", "task", "org", "principal", "p-1", "case-subject:p-1")
        complete_contract = build_completion_contract("task", "pa_provider", instruction,
                                                      scope=complete_scope.to_dict())
        self.assertEqual("mapped", complete_contract["mapping_status"])
        self.assertIs(complete_contract.get("verified_task_goal"), True)
        complete_model = FakeModel([
            ModelReply(tool_calls=(ToolCall("create", "cases.create_from_order", {
                "patient_id": "p-1", "procedure_code": "A123", "requested_date": "2026-10-22"}),)),
            ModelReply(tool_calls=(ToolCall("inspect-requirements", "cases.get_case", {"case_id": "actual-case-7"}),)),
            ModelReply(tool_calls=(ToolCall("disposition", "auth.finalize_provider_determination",
                                            {"case_id": "actual-case-7"}),)),
            ModelReply(tool_calls=(ToolCall("readback", "cases.get_case", {"case_id": "actual-case-7"}),)),
            ModelReply(content=json.dumps({"status": "complete", "claim": "The provider disposition was verified.",
                                           "stop_assessment":stop_record(['ev:m3:disposition','ev:m4:readback']),
                                           "evidence_ids": ["ev:m3:disposition", "ev:m4:readback"]})),
        ])
        complete_result = Harness(self.store, complete_model,
                                  ProviderContractTools("docs_needed"),
                                  case_identity_tools=("cases.create_from_order",)).run(
                                      complete_scope, instruction, "PA",
                                      completion_contract=complete_contract)
        self.assertEqual("complete", complete_result["status"], complete_result.get("completion_gate"))
        self.assertEqual("provider_more_evidence_required", complete_result["completion"]["branch_id"])
        self.assertEqual("fresh_case_readback", complete_result["completion"]["proof_kind"])
        self.assertEqual("case-subject:p-1", complete_result["completion"]["scope"]["case"])

        incomplete_scope = Scope("env", "task", "org", "principal", "p-2", "case-subject:p-2")
        incomplete_contract = build_completion_contract("task", "pa_provider", instruction,
                                                        scope=incomplete_scope.to_dict())
        incomplete_model = FakeModel([
            ModelReply(tool_calls=(ToolCall("create", "cases.create_from_order", {
                "patient_id": "p-2", "procedure_code": "A123", "requested_date": "2026-10-22"}),)),
            ModelReply(content=json.dumps({"status": "complete", "claim": "The provider disposition was verified.",
                                           "evidence_ids": ["ev:m1:create"]})),
        ])
        incomplete = Harness(self.store, incomplete_model, ProviderContractTools("draft"),
                             limits=Limits(max_model_calls=2),
                             case_identity_tools=("cases.create_from_order",)).run(
                                 incomplete_scope, instruction, "PA",
                                 completion_contract=incomplete_contract)
        self.assertEqual("unresolved", incomplete["status"])
        self.assertFalse(incomplete["completion_gate"]["accepted"])
        self.assertIn("provider_gather_more_disposition", incomplete["completion_gate"]["missing_milestones"])

    def test_foreign_patient_result_is_quarantined_before_any_later_model_call(self):
        model = FakeModel([
            ModelReply(tool_calls=(ToolCall("read", "records.lookup", {"patient_id": "p-1"}),)),
            ModelReply(content='{"status":"complete","claim":"bad","evidence_ids":["ev:m1:read"]}'),
        ])
        tools = FakeTools({"structuredContent": None, "content": [{"type": "text",
                           "text": '{"patient_id":"p-2","secret":"other patient details"}',
                           "parsed_json": {"patient_id": "p-2", "secret": "other patient details"}}], "isError": False})
        result = Harness(self.store, model, tools).run(make_scope(), "Read this record", "PA")
        self.assertEqual("blocked", result["status"])
        self.assertEqual(1, len(model.seen))
        self.assertNotIn("other patient details", json.dumps(model.seen))
        self.assertNotIn("other patient details", json.dumps(result))
        self.assertEqual("result_identity_mismatch", result["evidence"][0]["observed_result"]["error"])

    def test_bound_workspace_rejects_different_scope_before_model_or_file_access(self):
        scope_a, scope_b = make_scope("p-a", "c-a"), make_scope("p-b", "c-b")
        workspace = WorkspaceTools(Path(self.temp.name) / "work", scope_a)
        workspace.call("workspace.write_file", {"path": "marker.txt", "content": "patient A private"})
        model = FakeModel([])
        harness = Harness(self.store, model, ToolRegistry(workspace))
        with self.assertRaisesRegex(ValueError, "different case scope"):
            harness.run(scope_b, "Read case files", "PA")
        self.assertEqual([], model.seen)
        self.assertEqual("patient A private", workspace.call("workspace.read_file", {"path": "marker.txt"})["text"])

    def test_same_harness_rejects_overlapping_run(self):
        entered_model = threading.Event()
        release_model = threading.Event()

        class BlockingModel:
            def complete(self, messages, tools, *, max_output_tokens):
                entered_model.set()
                if not release_model.wait(3):
                    raise TimeoutError("test model release timed out")
                return ModelReply(content="not a completion record")

        harness = Harness(self.store, BlockingModel(), FakeTools({"patient_id": "p-1"}))
        worker_errors = []

        def first_run():
            try:
                harness.run(make_scope(), "first run", "PA")
            except Exception as exc:
                worker_errors.append(exc)

        worker = threading.Thread(target=first_run)
        worker.start()
        self.assertTrue(entered_model.wait(2), "first run did not reach the model")
        try:
            with self.assertRaisesRegex(ConflictError, "already has a run in progress"):
                harness.run(make_scope("p-2", "c-2"), "second run", "PA")
        finally:
            release_model.set()
            worker.join(3)
        self.assertFalse(worker.is_alive())
        self.assertEqual([], worker_errors)

    def test_failed_tool_output_cannot_support_completion_claim(self):
        model = FakeModel([
            ModelReply(tool_calls=(ToolCall("read", "records.lookup", {"patient_id": "p-1"}),)),
            ModelReply(content=json.dumps({"status": "complete", "claim": "done", "evidence_ids": ["ev:m1:read"]})),
        ])
        result = Harness(self.store, model, FakeTools({"error": "not found"})).run(make_scope(), "Read", "PA")
        self.assertEqual("unresolved", result["status"])
        self.assertEqual("failure", result["evidence"][0]["outcome"])

    def test_unknown_write_is_not_retried_on_resume(self):
        model = FakeModel([
            ModelReply(tool_calls=(ToolCall("write", "records.lookup", {"patient_id": "p-1"}),)),
        ])
        tools = FakeTools(RuntimeError("connection dropped after dispatch"), effect="write")
        harness = Harness(self.store, model, tools)
        first = harness.run(make_scope(), "Make the assigned change", "PA")
        self.assertEqual("blocked", first["status"])
        self.assertEqual(1, len(tools.calls))
        second = harness.run(make_scope(), "Make the assigned change", "PA", resume=True)
        self.assertEqual("blocked", second["status"])
        self.assertEqual(1, len(tools.calls))

    def test_resume_retries_transient_model_failure_and_executes_effect_once(self):
        class FailThenReplyModel:
            def __init__(self):
                self.calls = 0

            def complete(self, messages, tools, *, max_output_tokens):
                self.calls += 1
                if self.calls == 1:
                    raise OSError("temporary provider interruption")
                if self.calls == 2:
                    return ModelReply(tool_calls=(ToolCall("apply", "records.lookup", {"patient_id": "p-1"}),))
                return ModelReply(content=json.dumps({"status": "complete", "claim": "effect observed",
                                                      "evidence_ids": ["ev:m2:apply"]}))

        model = FailThenReplyModel()
        tools = FakeTools({"patient_id": "p-1", "receipt": "once"}, effect="write")
        harness = Harness(self.store, model, tools, limits=Limits(max_model_calls=3, max_tool_calls=4))
        scope = make_scope()
        contract = _test_completion_contract(scope, "records.lookup", "receipt", phase="terminal_write_response")
        first = harness.run(scope, "Perform the requested effect", "PA", completion_contract=contract)
        self.assertEqual("error", first["status"])
        second = harness.run(scope, "Perform the requested effect", "PA", resume=True,
                             completion_contract=contract)
        self.assertEqual("complete", second["status"])
        self.assertEqual(3, second["model_calls"])
        self.assertEqual(1, second["tool_calls"])
        self.assertEqual(1, len(tools.calls))
        self.assertEqual(3, self.store.load_case(make_scope())["budgets"]["max_model_calls"])

    def test_helper_and_write_in_same_model_turn_keep_stable_journal_identity(self):
        model = FakeModel([
            ModelReply(tool_calls=(
                ToolCall("helper", "case.request_helper", {"role_id": "PA-01", "question": "Check the request framing"}),
                ToolCall("write", "records.lookup", {"patient_id": "p-1"}),
            )),
            ModelReply(content="bounded proposal"),
            ModelReply(content='{"status":"complete","claim":"change observed","evidence_ids":["ev:m1:write"]}'),
        ])
        tools = FakeTools({"patient_id": "p-1", "receipt": "r-1"}, effect="write")
        scope = make_scope()
        result = Harness(self.store, model, tools, composition="helpers").run(
            scope, "Do task", "PA",
            completion_contract=_test_completion_contract(scope, "records.lookup", "receipt",
                                                          phase="terminal_write_response"))
        self.assertEqual("complete", result["status"])
        self.assertEqual("m1:write", self.store.actions(make_scope())[0]["id"])
        self.assertEqual(1, len(tools.calls))

    def test_completed_write_receipt_recovers_without_replaying_after_crash_boundary(self):
        scope = make_scope()
        self.store.open_case(scope, "Do task", "PA")
        state = self.store.load_case(scope)
        state.update({"status": "running", "model_calls": 1, "tool_calls": 1,
                      "processed_tool_calls": ["m1:write"]})
        state["messages"] = [
            {"role": "system", "content": "system"}, {"role": "user", "content": "Do task"},
            {"role": "assistant", "content": "", "tool_calls": [{"id": "write", "journal_id": "m1:write",
             "name": "records.lookup", "arguments": {"patient_id": "p-1"}}]},
        ]
        self.store.save_case(scope, state, 0)
        self.store.reserve_action(scope, "m1:write", "records.lookup", {"patient_id": "p-1"}, "write")
        self.store.finish_action(scope, "m1:write", {"patient_id": "p-1", "receipt": "stored-r"})
        model = FakeModel([ModelReply(content=json.dumps({"status": "complete", "claim": "receipt recovered",
                                                          "evidence_ids": ["ev:m1:write"]}))])
        tools = FakeTools({"patient_id": "p-1", "receipt": "should-not-run"}, effect="write")
        result = Harness(self.store, model, tools).run(scope, "Do task", "PA", resume=True)
        self.assertEqual("unresolved", result["status"])
        self.assertEqual("stored-r", result["evidence"][0]["observed_result"]["receipt"])
        self.assertEqual([], tools.calls)

    def test_pending_write_at_resume_is_quarantined_and_not_dispatched(self):
        scope = make_scope()
        self.store.open_case(scope, "Do task", "PA")
        state = self.store.load_case(scope)
        state.update({"status": "running", "model_calls": 1, "tool_calls": 1,
                      "processed_tool_calls": ["m1:write"]})
        state["messages"] = [
            {"role": "system", "content": "system"}, {"role": "user", "content": "Do task"},
            {"role": "assistant", "content": "", "tool_calls": [{"id": "write", "journal_id": "m1:write",
             "name": "records.lookup", "arguments": {"patient_id": "p-1"}}]},
        ]
        self.store.save_case(scope, state, 0)
        self.store.reserve_action(scope, "m1:write", "records.lookup", {"patient_id": "p-1"}, "write")
        model = FakeModel([])
        tools = FakeTools({"patient_id": "p-1"}, effect="write")
        result = Harness(self.store, model, tools).run(scope, "Do task", "PA", resume=True)
        self.assertEqual("blocked", result["status"])
        self.assertEqual("unknown", self.store.actions(scope)[0]["status"])
        self.assertEqual([], tools.calls)

    def test_same_harness_and_model_instance_do_not_carry_patient_a_context_to_b(self):
        model = FakeModel([
            ModelReply(tool_calls=(ToolCall("read-a", "records.lookup", {"patient_id": "p-1"}),)),
            ModelReply(content=json.dumps({"status": "complete", "claim": "A lookup completed", "evidence_ids": ["ev:m1:read-a"]})),
            ModelReply(content=json.dumps({"status": "incomplete", "claim": "B remains unresolved", "evidence_ids": []})),
        ])
        tools = FakeTools(lambda args: {"patient_id": args["patient_id"], "marker": "only-A" if args["patient_id"] == "p-1" else "only-B"})
        harness = Harness(self.store, model, tools)
        scope_a, scope_b = make_scope("p-1", "c-1"), make_scope("p-2", "c-2")
        result_a = harness.run(scope_a, "Review", "PA",
                               completion_contract=_test_completion_contract(scope_a, "records.lookup", "patient_id"))
        result_b = harness.run(scope_b, "Review", "PA",
                               completion_contract=_test_completion_contract(scope_b, "records.lookup", "patient_id"))
        self.assertEqual("complete", result_a["status"])
        self.assertEqual("unresolved", result_b["status"])
        self.assertNotIn("only-A", json.dumps(model.seen[2]))
        self.assertIn("p-2", str(model.seen[2]))

    def test_schema_and_context_budget_stop_before_provider_execution(self):
        model = FakeModel([ModelReply(content="unused")])
        tools = FakeTools({"patient_id": "p-1"})
        result = Harness(self.store, model, tools, limits=Limits(max_context_chars=32)).run(make_scope(), "Do task", "PA")
        self.assertEqual("exhausted", result["status"])
        self.assertEqual([], model.seen)
        self.assertEqual([], tools.calls)


if __name__ == "__main__":
    unittest.main()


class NestedOptionalActorTests(unittest.TestCase):
    def test_nested_bound_actor_is_omittable_only_when_the_stripped_call_validates(self):
        from health_harness_codex.engine import _can_omit_optional_audit_actor
        scope = make_scope()
        spec = ToolSpec('case.record_policy_decision', 'Synthetic', {'type': 'object', 'additionalProperties': False,
            'properties': {'applies_to': {'type': 'array'}, 'bound_arguments': {'type': 'object'}},
            'required': ['applies_to']}, effect='write')
        nested = {'applies_to': ['triage.route_case'],
                  'bound_arguments': {'triage.route_case': {'actor': 'agent', 'case_id': scope.case}}}
        self.assertTrue(_can_omit_optional_audit_actor(spec, nested, scope, {'category': 'identity_scope'}))
        # Nothing to omit, or a non-identity category: no omission path.
        plain = {'applies_to': ['triage.route_case'], 'bound_arguments': {'triage.route_case': {'case_id': scope.case}}}
        self.assertFalse(_can_omit_optional_audit_actor(spec, plain, scope, {'category': 'identity_scope'}))
        self.assertFalse(_can_omit_optional_audit_actor(spec, nested, scope, {'category': 'schema_type'}))
