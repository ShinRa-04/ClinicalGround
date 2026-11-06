import json
import unittest

from health_harness_codex.identity import (
    IdentityResolutionError,
    resolve_actual_case_id,
    resolve_patient_identity,
    resolve_patient_identity_at_path,
    validate_patient_identity_result,
)
from health_harness_codex.models import Scope


class PatientIdentityResolutionTests(unittest.TestCase):
    def setUp(self):
        self.scope = Scope(environment="test", task="task", organization="org",
                            principal="actor", patient="case-subject:case-42", case="case-42")

    def test_late_case_bound_identity_is_returned_without_mutating_scope_namespace(self):
        result = {"case_id": "case-42", "patient_id": "patient-900"}
        self.assertEqual("patient-900", resolve_patient_identity(result, self.scope))
        self.assertEqual("case-subject:case-42", self.scope.patient)
        self.assertEqual("patient-900", validate_patient_identity_result(result, self.scope, "patient-900"))

    def test_mcp_structured_and_duplicate_json_content_normalizations_are_supported(self):
        identity = {"case": {"id": "case-42"}, "patient": {"id": "patient-900"}}
        result = {
            "structuredContent": {"data": [identity]},
            "content": [{"type": "text", "text": json.dumps({"data": [identity]})}],
        }
        self.assertEqual("patient-900", resolve_patient_identity(result, self.scope))

    def test_case_envelope_object_binds_its_sibling_patient_id(self):
        result = {"case": {"id": "case-42", "patient_id": "patient-900", "status": "in_review"}}
        self.assertEqual("patient-900", resolve_patient_identity(result, self.scope))

    def test_case_envelope_rejects_conflicting_case_ids(self):
        result = {"case_id": "case-other",
                  "case": {"id": "case-42", "patient_id": "patient-900"}}
        with self.assertRaisesRegex(IdentityResolutionError, "case ID outside"):
            resolve_patient_identity(result, self.scope)

    def test_arbitrary_nested_object_id_is_not_interpreted_as_case_id(self):
        result = {"record": {"id": "case-42", "patient_id": "patient-900"}}
        self.assertIsNone(resolve_patient_identity(result, self.scope))

    def test_nested_unbound_sibling_identity_cannot_be_combined(self):
        result = {"record": {"case_id": "case-42", "patient": {"patient_id": "patient-900"}}}
        self.assertIsNone(resolve_patient_identity(result, self.scope))

    def test_unrelated_patient_object_does_not_supply_binding(self):
        result = {"case_id": "case-42", "related_records": [{"patient_id": "patient-900"}]}
        self.assertIsNone(resolve_patient_identity(result, self.scope))

    def test_foreign_case_id_rejects_entire_payload(self):
        result = {"structuredContent": {"case_id": "case-42", "patient_id": "patient-900"},
                  "content": [{"type": "text", "text": json.dumps({"case_id": "case-other"})}]}
        with self.assertRaisesRegex(IdentityResolutionError, "case ID outside"):
            resolve_patient_identity(result, self.scope)

    def test_conflicting_patient_ids_reject_entire_payload(self):
        result = {"case_id": "case-42", "patient_id": "patient-900",
                  "secondary": {"patient_id": "patient-other"}}
        with self.assertRaisesRegex(IdentityResolutionError, "conflicting patient IDs"):
            resolve_patient_identity(result, self.scope)

    def test_multiple_case_bound_patient_ids_reject_entire_payload(self):
        result = {"items": [{"case_id": "case-42", "patient_id": "patient-900"},
                            {"case_id": "case-42", "patient_id": "patient-other"}]}
        with self.assertRaisesRegex(IdentityResolutionError, "conflicting patient IDs"):
            resolve_patient_identity(result, self.scope)

    def test_late_identity_must_match_existing_separate_mapping(self):
        with self.assertRaisesRegex(IdentityResolutionError, "conflicts with the resolved"):
            resolve_patient_identity({"case_id": "case-42", "patient_id": "patient-other"},
                                     self.scope, existing_patient_id="patient-900")
        self.assertEqual("patient-900", resolve_patient_identity({"status": "no identity"},
                                                                  self.scope, existing_patient_id="patient-900"))

    def test_internal_namespace_is_never_adopted_as_patient_id(self):
        with self.assertRaisesRegex(IdentityResolutionError, "namespace cannot be adopted"):
            resolve_patient_identity({"case_id": "case-42", "patient_id": "case-subject:case-42"},
                                     self.scope)

    def test_um_md_decision_patient_binding_uses_only_authoritative_nested_case_path(self):
        result = {"structuredContent": {"missing_information": {
            "case": {"id": "case-42", "patient_id": "patient-900", "notes": "untrusted narrative"},
            "notes": {"patient_id": "patient-unrelated"},
        }, "patient_id": "patient-top-level-unrelated"}}
        path = ("structuredContent", "missing_information", "case")
        self.assertEqual("patient-900", resolve_patient_identity_at_path(result, self.scope, path))

    def test_um_md_decision_patient_binding_rejects_fake_case_and_ignores_unrelated_descriptors(self):
        path = ("structuredContent", "missing_information", "case")
        fake_case = {"structuredContent": {"missing_information": {
            "case": {"id": "case-other", "patient_id": "patient-900"}}}}
        with self.assertRaisesRegex(IdentityResolutionError, "does not match the active case"):
            resolve_patient_identity_at_path(fake_case, self.scope, path)
        for result in (
            {"structuredContent": {"missing_information": {"case": {"patient_id": "patient-900"}}}},
            {"structuredContent": {"missing_information": {"descriptor": {"id": "case-42"}}},
             "patient_id": "patient-900"},
        ):
            self.assertIsNone(resolve_patient_identity_at_path(result, self.scope, path))

    def test_validation_requires_same_object_case_binding(self):
        with self.assertRaisesRegex(IdentityResolutionError, "does not bind"):
            validate_patient_identity_result({"case_id": "case-42", "data": {"patient_id": "patient-900"}},
                                             self.scope, "patient-900")

    def test_existing_real_patient_scope_is_supported(self):
        actual_scope = Scope(environment="test", task="task", organization="org", principal="actor",
                             patient="patient-900", case="case-42")
        self.assertEqual("patient-900", resolve_patient_identity(
            {"case_id": "case-42", "patient_id": "patient-900"}, actual_scope))

    def test_provider_case_binding_requires_same_case_and_active_patient_object(self):
        provider_scope = Scope(environment="test", task="task", organization="provider", principal="actor",
                               patient="patient-900", case="case-subject:patient-900")
        result = {"structuredContent": {"case": {"id": "provider-case-7", "patient_id": "patient-900"}}}
        self.assertEqual("provider-case-7", resolve_actual_case_id(result, provider_scope))

    def test_provider_case_binding_rejects_missing_foreign_or_internal_ids(self):
        provider_scope = Scope(environment="test", task="task", organization="provider", principal="actor",
                               patient="patient-900", case="case-subject:patient-900")
        invalid = (
            ({"case_id": "provider-case-7"}, "missing or conflicting patient"),
            ({"case_id": "provider-case-7", "patient_id": "patient-other"}, "missing or conflicting patient"),
            ({"case_id": "case-subject:patient-900", "patient_id": "patient-900"}, "internal case-subject"),
            ({"case_id": "case-a", "patient_id": "patient-900", "other": {"case_id": "case-b"}}, "conflicting case IDs"),
            ({"case_id": "provider-case-7", "related": {"patient_id": "patient-900"}}, "does not bind"),
        )
        for result, message in invalid:
            with self.subTest(result=result), self.assertRaisesRegex(IdentityResolutionError, message):
                resolve_actual_case_id(result, provider_scope)


if __name__ == "__main__":
    unittest.main()
