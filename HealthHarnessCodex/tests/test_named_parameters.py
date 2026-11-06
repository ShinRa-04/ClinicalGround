"""Prevent optional payloads disappearing under unrecognized parameter names."""
import json
import unittest
from contextlib import closing

from health_harness_codex.codex_provider import _reply_schema
from health_harness_codex.engine import Harness, _safe_validation_feedback
from health_harness_codex.models import Scope, ToolSpec, ToolCall, ModelReply, Limits
from health_harness_codex.schema import validate_arguments, UnexpectedParameterError, tool_parameter_schema
from health_harness_codex.store import CaseStore
from health_harness_codex.synthetic_contracts import operator_observation_contract


SCOPE = Scope("synthetic", "task", "org", "principal", "patient", "case")


def save_spec():
    # Mirrors the general signature pattern: required identifier plus an optional
    # list, no additionalProperties assertion on the published parameter root.
    return ToolSpec("records.save", "Save supplied synthetic evaluations", {
        "type": "object", "properties": {
            "record_id": {"type": "string"},
            "evaluations": {"anyOf": [{"type": "array", "items": {"type": "string"}},
                                         {"type": "null"}]},
            "metadata": {"type": "object"}}, "required": ["record_id"]}, effect="write")


class NamedParameterTests(unittest.TestCase):
    def test_unknown_names_are_rejected_without_echoing_arguments_or_renaming(self):
        spec = save_spec()
        for key in ("evaluations_defer", "evaluations data", "evaluations\u201d", "private member name"):
            arguments = {"record_id": "synthetic", key: ["private source text"]}
            with self.subTest(key=key), self.assertRaises(UnexpectedParameterError) as raised:
                validate_arguments(spec, arguments, SCOPE)
            feedback = _safe_validation_feedback(raised.exception, spec)
            self.assertEqual({"category": "schema_unexpected_field", "path": "$",
                              "allowed_fields": ["evaluations", "metadata", "record_id"]}, feedback)
            self.assertNotIn(key, str(raised.exception))
            self.assertNotIn("private source text", json.dumps(feedback))
            self.assertNotIn("evaluations", arguments)

    def test_valid_optional_values_and_nested_data_maps_remain_supported(self):
        spec = save_spec()
        for value in ({"record_id": "synthetic"},
                      {"record_id": "synthetic", "evaluations": None},
                      {"record_id": "synthetic", "evaluations": []},
                      {"record_id": "synthetic", "evaluations": ["one"],
                       "metadata": {"arbitrary map key": {"free": True}}}):
            validate_arguments(spec, value, SCOPE)
        self.assertNotIn("additionalProperties", spec.input_schema)

    def test_explicit_open_and_typed_maps_are_preserved(self):
        for extra in (True, {"type": "string"}):
            schema = {"type": "object", "properties": {"known": {"type": "string"}},
                      "additionalProperties": extra}
            spec = ToolSpec("dynamic", "explicit dynamic parameters", schema)
            validate_arguments(spec, {"known": "x", "extension": "y"}, SCOPE)
            self.assertEqual(extra, tool_parameter_schema(schema)["additionalProperties"])
        validate_arguments(ToolSpec("map", "unstructured map", {"type": "object"}),
                           {"arbitrary key": [1]}, SCOPE)

    def test_closed_schema_still_rejects_unknown_parameters(self):
        spec = save_spec()
        spec = ToolSpec(spec.name, spec.description, {**spec.input_schema, "additionalProperties": False})
        with self.assertRaises(UnexpectedParameterError):
            validate_arguments(spec, {"record_id": "synthetic", "extra": 1}, SCOPE)

    def test_decoder_closes_only_parameter_root_without_mutating_published_contract(self):
        spec = save_spec()
        projected = _reply_schema([spec])["$defs"]["tool_0"]
        self.assertFalse(projected["additionalProperties"])
        self.assertNotIn("additionalProperties", projected["properties"]["metadata"])
        self.assertEqual(["record_id"], projected["required"])
        self.assertNotIn("additionalProperties", spec.input_schema)

    def test_root_local_reference_is_checked_after_resolution(self):
        spec = ToolSpec("referenced", "parameters", {"$ref": "#/$defs/Params", "$defs": {
            "Params": {"type": "object", "properties": {"known": {"type": "string"}}}}})
        # The validator resolves root references before applying the parameter rule.
        with self.assertRaises(ValueError):
            validate_arguments(spec, {"typo": "ignored otherwise"}, SCOPE)

    def test_unknown_payload_is_corrected_before_first_dispatch_and_saved_once(self):
        class Model:
            def __init__(self): self.messages = []
            def complete(self, messages, tools, **kwargs):
                self.messages.append(json.loads(json.dumps(messages)))
                if len(self.messages) == 1:
                    return ModelReply(tool_calls=(ToolCall("bad", "records.save", {
                        "record_id": "synthetic", "evaluations\u201d": ["one"]}),))
                if len(self.messages) == 2:
                    return ModelReply(tool_calls=(ToolCall("corrected", "records.save", {
                        "record_id": "synthetic", "evaluations": ["one"]}),))
                return ModelReply(content=json.dumps({"status": "complete", "claim": "Observed one saved value.",
                                                       "evidence_ids": ["ev:m1:bad"]}))
        class Tools:
            def __init__(self): self.calls = []
            def list_tools(self): return [save_spec()]
            def call(self, name, arguments):
                self.calls.append(arguments)
                # An API silently ignores unrecognized parameters and defaults
                # the optional list to empty, as in the actual failure pattern.
                return {"saved_count": len(arguments.get("evaluations") or [])}
        tools = Tools(); model = Model()
        contract = operator_observation_contract(SCOPE, "UM", "records.save", [
            {"id": "saved", "path": "saved_count", "op": "eq", "value": 1}], phase="terminal_write_response")
        with closing(CaseStore(":memory:")) as store:
            result = Harness(store, model, tools, limits=Limits(max_model_calls=4)).run(
                SCOPE, "Save the one synthetic evaluation.", "UM", completion_contract=contract)
        self.assertEqual("complete", result["status"])
        self.assertEqual(1, result["pre_dispatch_validation_retry_count"])
        self.assertEqual([{"record_id": "synthetic", "evaluations": ["one"]}], tools.calls)
        feedback = [json.loads(m["content"]) for m in model.messages[1] if m.get("role") == "tool"]
        self.assertIn(["evaluations", "metadata", "record_id"], [f.get("allowed_fields") for f in feedback])


if __name__ == "__main__":
    unittest.main()
