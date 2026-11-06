from pathlib import Path, PurePosixPath
from contextlib import redirect_stdout
from io import StringIO
import json
import tempfile
from unittest import TestCase
from unittest.mock import patch

from health_harness_codex.models import ModelReply, ToolSpec, ToolCall, ConflictError
from health_harness_codex import standalone
from health_harness_codex.completion_contracts import validate_completion_contract
from health_harness_codex.tools import ToolRegistry


_QUEUE = ToolSpec("payer_queue", "list current queue", {"type": "object", "properties": {}})
_GET = ToolSpec("payer_case", "get observed case", {
    "type": "object", "required": ["case_id"], "additionalProperties": False,
    "properties": {"case_id": {"type": "string"}},
})
_SUMMARY = ToolSpec("payer_summary", "read determination summary", {
    "type": "object", "required": ["case_id"], "additionalProperties": False,
    "properties": {"case_id": {"type": "string"}},
})


class _FakeMCP:
    def __init__(self, container, port, timeout, executor):
        self._actual_names = {"queue_alias": "payer_intake_hub.list_intake_queue",
                              "case_alias": "payer_intake_hub.get_intake_case",
                              "review_alias": "review.get_nurse_review_data",
                              "md_decision_alias": "review.submit_md_case_decision",
                              "summary_alias": "determination.get_summary"}
        self._specs = [
            ToolSpec("queue_alias", _QUEUE.description, _QUEUE.input_schema),
            ToolSpec("case_alias", _GET.description, _GET.input_schema),
            ToolSpec("review_alias", "review data", _GET.input_schema),
            ToolSpec("md_decision_alias", "submit MD case decision", _GET.input_schema),
            ToolSpec("summary_alias", _SUMMARY.description, _SUMMARY.input_schema),
        ]
        self.queue = [{"patient_id": "patient-live-77", "case_id": "case-live-99", "intake_id": "intake-live-42"}]
        self.calls = []

    def list_tools(self):
        return self._specs

    def call(self, name, arguments):
        self.calls.append((name, arguments))
        if name == "queue_alias":
            return {"structuredContent": {"items": self.queue}}
        if name == "case_alias":
            requested_case_id = arguments.get("case_id")
            match = next((record for record in self.queue
                          if standalone._find_identifier(record, "case") == requested_case_id), None)
            if match is not None:
                return match
            return {"patient_id": "patient-live-77", "case_id": "case-live-99", "intake_id": "intake-live-42"}
        if name == "summary_alias":
            return {"terminal": True, "status": "finalized"}
        if name == "review_alias":
            return {"patient_id": "patient-live-77", "case_id": "case-live-99"}
        raise KeyError(name)


class _FakeStore:
    def __init__(self, path):
        self.path = path

    def close(self):
        pass

    def actions(self, scope):
        return []


class _FakeExecutor:
    def __init__(self, *args, **kwargs):
        pass

    def validate_owned_trial(self, task_id):
        self.task_id = task_id


class _FakeRecorder:
    last_instance = None

    def __init__(self, run_dir, metadata):
        self.metadata = dict(metadata)
        type(self).last_instance = self

    def emit(self, kind, **fields):
        pass

    def finish(self, result, elapsed_seconds, environment_observations=None):
        self.finished = (result, elapsed_seconds, environment_observations)


class _FakeWorkspace:
    last_instance = None

    def __init__(self, container, root, scope, **kwargs):
        self.case_root = f"{root}/{scope.key}"
        self.root = root
        self.read_roots = kwargs.get("read_roots", ())
        self.calls = []
        type(self).last_instance = self

    def list_tools(self):
        return [ToolSpec("workspace.write_file", "write current case artifact", {
            "type": "object", "required": ["path", "content"],
            "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
            "additionalProperties": False,
        }, effect="write")]

    def call(self, name, arguments):
        self.calls.append((name, dict(arguments)))
        return {"path": arguments.get("path"), "bytes_written": len(arguments.get("content", ""))}


class _IdentityRecordingWrapper:
    def __new__(cls, value, recorder):
        return value


class _FakeHarness:
    seen_scope = None
    last_limits = None
    last_patient_identity_result_paths = None
    last_principal_identity_result_paths = None
    last_completion_contract = None
    last_instruction = None
    def __init__(self, store, model, tools, limits, composition, patient_identity_tools=(),
                 case_identity_tools=(), case_binding_callback=None, patient_identity_result_paths=None,
                 principal_identity_result_paths=None, require_policy_grounding=False, progress=None,recovery_helper_policy='off',
                 runtime_guard=None):
        self.tools = tools
        type(self).last_limits = limits
        type(self).last_patient_identity_result_paths = patient_identity_result_paths
        type(self).last_principal_identity_result_paths = principal_identity_result_paths
        type(self).last_require_policy_grounding = require_policy_grounding
        type(self).last_recovery_helper_policy=recovery_helper_policy

    def run(self, scope, instruction, domain, completion_contract=None):
        type(self).seen_scope = scope
        type(self).last_instruction = instruction
        type(self).last_completion_contract = completion_contract
        gate = validate_completion_contract(completion_contract, [], scope=scope.to_dict())
        status = "complete" if gate["accepted"] else "unresolved"
        return {"status": status, "message": "local synthetic claim", "model_calls": 2,
                "tool_calls": 3, "usage": {}, "evidence": [], "obligations": [],
                "completion_gate": gate}


class StandaloneTests(TestCase):
    def test_setup_error_codes_use_only_exact_known_messages(self):
        cases = (
            ("provider patient name and chart cue did not identify the same roster entry",
             "patient_identity_conflict"),
            ("provider chart readback patient identity disagreed with the actor-visible roster",
             "patient_identity_conflict"),
            ("provider public patient roster is not complete within the bounded discovery limit",
             "incomplete_public_roster"),
            ("Codex executable does not exist or is not a file", "native_executable_missing"),
        )
        for message, code in cases:
            with self.subTest(message=message):
                self.assertEqual(code, standalone._setup_error_code(ValueError(message)))
        self.assertEqual("setup_error", standalone._setup_error_code(
            ValueError("patient private-name-do-not-log had an unknown setup issue")))

    def test_standalone_instruction_defines_isolated_simulation_without_real_credentials_or_outcomes(self):
        scope = standalone.Scope("docker:test", "pa_synthetic", "payer-org", "payer-actor",
                                 "case-subject:case-42", "case-42")
        public_instruction = "Original public task text naming its required workflow."

        instruction = standalone._standalone_instruction(
            "pa_synthetic", {"case_id": "case-42"}, scope, None,
            "/logs/artifacts/workspaces/case-42/payer/scope", public_instruction)

        self.assertTrue(instruction.endswith("--- Public task instruction ---\n" + public_instruction))
        self.assertIn("authorized, isolated simulation", instruction)
        self.assertIn("not a real hospital or clinical deployment", instruction)
        self.assertIn("may be performed by this same scoped actor", instruction)
        self.assertIn("public task and actor tool contracts together define simulated action authority", instruction)
        self.assertIn("an exposed tool alone does not authorize an action outside the assigned task", instruction)
        self.assertIn("Do not invent real staff, licenses, credentials, independent humans, reviewer IDs", instruction)
        self.assertIn("Preserve substantive clinical, policy, and stage prerequisites", instruction)
        self.assertIn("does not by itself prove that every conditional stage is required for this case", instruction)
        self.assertIn("existence of a clinical policy or an exposed tool alone does not establish", instruction)
        self.assertIn("evidence-linked eligibility checkpoint", instruction)
        self.assertIn("Resolve facts needed to choose a branch", instruction)
        self.assertIn("A writable triage disposition is not an input to the default route_case operation", instruction)
        self.assertIn("An explicit route override is a bypass", instruction)
        self.assertIn("only an explicit triage=null response establishes that no record exists", instruction)
        self.assertIn("The first disposition is a one-time immutable commit and must follow the observed route", instruction)
        self.assertIn("If a record already exists, do not attempt to amend it", instruction)
        self.assertIn("Do not repeat a successfully completed route", instruction)
        self.assertIn("Calculate SLA from the observed intake level_of_urgency", instruction)
        self.assertIn("recompute it from a newly observed urgency", instruction)
        self.assertIn("does not imply that every service exception was checked", instruction)
        self.assertIn("never infer an exception or absence of exclusions from missing or uncertain evidence", instruction)
        self.assertIn("only when the applicable policy or actor record supports that case-specific branch", instruction)
        self.assertIn("according to its tool-declared scope: it establishes only the fields it says it checked", instruction)
        self.assertIn("Do not narrow it to one factor or expand it into certification of unmentioned flags", instruction)
        self.assertIn("Distinguish observed contrary evidence from hypothetical or unmentioned exceptions", instruction)
        self.assertIn("Uncertainty alone does not prove an exception", instruction)
        self.assertIn("missing fields do not prove that no exception exists", instruction)
        self.assertIn("do not create mandatory negative-certification steps for possibilities the policy and tool contract do not require", instruction)
        self.assertIn("Treat each assessment according to its tool-declared scope", instruction)
        self.assertIn("it establishes only the fields it says it checked", instruction)
        self.assertIn("Resolve required facts and explicit contradictions", instruction)
        self.assertNotIn("triage_auto_approve", instruction)
        self.assertNotIn("final_decision=approved", instruction)
        self.assertNotIn("branch_alpha", instruction)
        self.assertNotIn("branch_beta", instruction)

    def test_terminal_readback_uses_current_actor_state_not_nested_historical_flags(self):
        self.assertIsNone(standalone._terminal_value({"result": {"old_record": {"terminal": True}}}))
        self.assertFalse(standalone._terminal_value({"result": {"terminal": False, "old_record": {"terminal": True}}}))
        self.assertTrue(standalone._terminal_value({"result": {"structuredContent": {
            "workflow_state": {"workflow_stage": "determination", "stage_detail": "finalized", "action_owner": "none"}}}}))
        self.assertIsNone(standalone._terminal_value({"result": {"structuredContent": {
            "workflow_state": {"workflow_stage": "payer_intake", "stage_detail": "triage", "action_owner": "payer"}}}}))

    def test_domain_selection_uses_dataset_parent_or_validated_override(self):
        root = Path("C:/data/chi-bench")
        cases = (
            (root / "prior_auth_provider" / "tasks" / "task-a", "pa_provider"),
            (root / "prior_auth_um" / "tasks" / "task-b", "pa_um"),
            (root / "care_management" / "tasks" / "task-c", "cm"),
        )
        for path, expected in cases:
            with self.subTest(path=path):
                self.assertEqual(expected, standalone.domain_for_task(path).name)
        self.assertEqual("pa_um", standalone.domain_for_task(root / "legacy" / "task", "pa_um").name)
        with self.assertRaisesRegex(ValueError, "domain override"):
            standalone.domain_for_task(root / "legacy" / "task", "task-a")

    def test_non_um_instruction_uses_public_task_without_um_routing_rules(self):
        scope = standalone.Scope("docker:test", "task-a", "pa_provider-organization",
                                 "pa_provider-actor", "patient-1", "case-1")
        public = "Preserve the full assigned workflow."
        for profile_name in ("pa_provider", "cm"):
            with self.subTest(domain=profile_name):
                profile = standalone.domain_for_task(Path("legacy-task"), profile_name)
                instruction = standalone._profile_instruction(
                    profile, "task-a", {"case_id": "case-1", "patient_id": "patient-1"},
                    scope, "patient-1", "/workspace/case-1", public)
                self.assertTrue(instruction.endswith("--- Public task instruction ---\n" + public))
                self.assertIn(profile.name, instruction)
                self.assertNotIn("route_case", instruction)
                self.assertNotIn("triage.set_disposition", instruction)

        um_profile = standalone.domain_for_task(Path("legacy-task"), "pa_um")
        um_instruction = standalone._profile_instruction(
            um_profile, "task-a", {"case_id": "case-1"}, scope, None,
            "/workspace/case-1", public)
        self.assertIn("default route_case operation", um_instruction)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=str(Path(__file__).resolve().parents[1] / "runs"))
        self.root = Path(self.temp.name)
        self.task = self.root / "pa_t012_t012_o001_p01_triage_payer"
        self.task.mkdir()
        (self.task / "instruction.md").write_text("Synthetic public task instruction.", encoding="utf-8")
        self.run_dir = self.root / "runs" / "attempt-1"
        self.run_dir.mkdir(parents=True)

    def tearDown(self):
        self.temp.cleanup()

    def _patches(self):
        return (
            patch.object(standalone, "DockerMCPClient", _FakeMCP),
            patch.object(standalone, "DockerExecutor", _FakeExecutor),
            patch.object(standalone, "DockerWorkspaceTools", _FakeWorkspace),
            patch.object(standalone, "CodexSessionModel", lambda *a, **k: object()),
            patch.object(standalone, "CaseStore", _FakeStore),
            patch.object(standalone, "Harness", _FakeHarness),
            patch.object(standalone, "RunRecorder", _FakeRecorder),
            patch.object(standalone, "RecordingModel", _IdentityRecordingWrapper),
            patch.object(standalone, "RecordingTools", _IdentityRecordingWrapper),
        )

    def test_runtime_failure_preserves_durable_call_counts(self):
        class PersistedStore(_FakeStore):
            def load_case(self,scope):return {'model_calls':6,'tool_calls':28,'status':'running',
                'usage':{'input_tokens':100},'evidence':[]}
        class BrokenHarness(_FakeHarness):
            def run(self,*args,**kwargs):raise ConflictError('synthetic lease failure')
        patches=list(self._patches())+[
            patch.object(standalone,'CaseStore',PersistedStore),patch.object(standalone,'Harness',BrokenHarness)]
        for p in patches:p.start()
        try:
            report=standalone.run_case('owned-container',self.task,self.run_dir,'C:/Codex/codex.exe',{},domain='pa_um')
        finally:
            for p in reversed(patches):p.stop()
        self.assertEqual('runtime_failure',report['local_harness']['status'])
        self.assertEqual('ConflictError',report['local_harness']['error_type'])
        self.assertEqual(6,report['model_calls_total_observed'])
        self.assertEqual(28,report['local_harness']['tool_calls'])
        self.assertEqual('running',report['local_harness']['persisted_status'])

    def test_run_uses_live_observed_ids_and_keeps_score_unknown(self):
        patches = self._patches()
        for p in patches:
            p.start()
        try:
            report = standalone.run_case("owned-container", self.task, self.run_dir, "C:/Codex/codex.exe", {},
                                         domain="pa_um", attempt_number=2)
        finally:
            for p in reversed(patches):
                p.stop()
        self.assertEqual(_FakeHarness.seen_scope.patient, "patient-live-77")
        self.assertEqual(_FakeHarness.seen_scope.case, "case-live-99")
        self.assertNotEqual(_FakeHarness.seen_scope.case, self.task.name)
        self.assertEqual(report["local_harness"]["status"], "unresolved")
        self.assertEqual(report["local_harness"]["completion_gate"]["reason_code"], "goal_unverified")
        self.assertEqual(_FakeHarness.last_completion_contract["task_id"], self.task.name)
        self.assertEqual(_FakeHarness.last_completion_contract["scope"], report["scope"])
        self.assertFalse(_FakeHarness.last_completion_contract["verified_task_goal"])
        self.assertEqual(report["official_score"], "unknown; no judge invoked")
        self.assertEqual(report["actual_determination_readback"]["status"], "observed")
        self.assertEqual(report["actual_determination_readback"]["result"]["terminal"], True)
        self.assertEqual({"md_decision_alias": ("structuredContent", "missing_information", "case")},
                         _FakeHarness.last_patient_identity_result_paths)
        self.assertEqual({"review_alias": ("structuredContent", "triage")},
                         _FakeHarness.last_principal_identity_result_paths)
        self.assertEqual(2, _FakeRecorder.last_instance.metadata["attempt"])
        self.assertEqual("payer_intake_hub.list_intake_queue",
                         _FakeRecorder.last_instance.metadata["actor_tool_names"]["queue_alias"])

    def test_selected_actor_model_reaches_native_constructor_and_actual_report(self):
        seen=[]
        def model(*args,**kwargs):seen.append(kwargs['model']);return object()
        patches=[*self._patches(),patch.object(standalone,'CodexSessionModel',model)]
        for p in patches:p.start()
        try:
            report=standalone.run_case('owned-container',self.task,self.run_dir,'C:/Codex/codex.exe',{},
                domain='pa_um',model_name='gpt-6.1-sol')
        finally:
            for p in reversed(patches):p.stop()
        self.assertEqual(['gpt-6.1-sol'],seen)
        self.assertEqual('gpt-6.1-sol',report['model'])
        self.assertEqual('gpt-6.1-sol',_FakeRecorder.last_instance.metadata['model'])

    def test_non_um_run_selects_domain_actor_workspace_and_readback(self):
        from health_harness_codex.models import ToolSpec

        class ProfileActor:
            last_instance = None

            def __init__(self, container, port, timeout, executor):
                type(self).last_instance = self
                self.port = port
                self.calls = []
                self._actual_names = {}
                self._specs = []
                self.add_tool("chart_read", "chart.get_patient_chart_by_patient", ("patient_id",))
                self.add_tool("cm_read", "cm_chart.get_chart_data", ("case_id",))
                self.add_tool("search_patients", "chart.search_patients")
                self.add_tool("queue", "cm_intake.list_referral_queue")
                self.add_tool("create_case", "cases.create_from_order", effect="write")
                self.add_tool("case_read", "cases.get_case", ("case_id",))
                self.add_tool("inbox", "inbox.list_messages", ("case_id",))
                self.add_tool("outsider", "payer_letter_center.generate_letter", effect="write")

            def add_tool(self, alias, actual, required=(), effect="read"):
                self._actual_names[alias] = actual
                self._specs.append(ToolSpec(alias, actual, {
                    "type": "object", "required": list(required),
                    "properties": {key: {"type": "string"} for key in required},
                }, effect=effect))

            def list_tools(self):
                return list(self._specs)

            def call(self, name, arguments):
                self.calls.append((name, dict(arguments)))
                actual = self._actual_names[name]
                if actual == "chart.get_patient_chart_by_patient":
                    return {"structuredContent": {"patient_id": arguments["patient_id"], "chart": []}}
                if actual == "cm_chart.get_chart_data":
                    return {"structuredContent": {"case_id": arguments["case_id"], "chart": []}}
                if actual == "cases.get_case":
                    return {"structuredContent": {"case_id": arguments["case_id"],
                                                   "patient_id": "patient-9",
                                                   "case": {"id": arguments["case_id"]}}}
                return {"structuredContent": {}}

        class ProfileHarness:
            seen = []
            last_completion_contract = None

            def __init__(self, store, model, tools, limits, composition, patient_identity_tools=(),
                 case_identity_tools=(), case_binding_callback=None, patient_identity_result_paths=None,
                 principal_identity_result_paths=None, require_policy_grounding=False, progress=None,recovery_helper_policy='off',
                 runtime_guard=None):
                if not require_policy_grounding:raise AssertionError('native run must enforce policy grounding')
                self.tools = tools
                self.case_identity_tools = case_identity_tools
                self.case_binding_callback = case_binding_callback

            def run(self, scope, instruction, domain, completion_contract=None):
                type(self).last_completion_contract = completion_contract
                self.tools.bind_scope(scope)
                visible = self.tools.list_tools()
                refusal = (self.tools.call("workspace.write_file", {"path": "draft.txt", "content": "x"})
                           if domain == "PA" else None)
                outsider = self.tools.call("outsider", {})
                patient_refusal = (self.tools.call("chart_read", {"patient_id": "patient-other"})
                                   if domain == "PA" else None)
                type(self).seen.append((domain, [spec.name for spec in visible], scope, refusal,
                                        outsider, visible, patient_refusal))
                case_bindings = {}
                if domain == "PA":
                    case_bindings = {"case_namespace": scope.case, "case_id": "actual-case-9",
                                     "patient_id": "patient-9", "source_tool": "create_case",
                                     "source_evidence_id": "ev:m1:create"}
                    self.case_binding_callback(case_bindings)
                    self.tools.call("workspace.write_file", {"path": "note.txt", "content": "after binding"})
                gate = validate_completion_contract(completion_contract, [], scope=scope.to_dict())
                return {"status": "complete" if gate["accepted"] else "unresolved",
                        "message": "synthetic domain run", "evidence": [],
                        "obligations": [], "case_bindings": case_bindings,
                        "completion_gate": gate}

        patches = self._patches()
        for p in patches:
            p.start()
        try:
            with patch.object(standalone, "DockerMCPClient", ProfileActor), \
                    patch.object(standalone, "Harness", ProfileHarness), \
                    patch.object(standalone, "discover_domain_case") as discovery:
                for domain, expected_port, patient_case in (
                    ("pa_provider", 8020, True), ("cm", 8200, False)):
                    run_dir = self.root / f"runs-{domain}"
                    run_dir.mkdir()
                    task = self.root / f"task-{domain}"
                    task.mkdir()
                    (task / "instruction.md").write_text("Public domain instruction.", encoding="utf-8")
                    if patient_case:
                        observed = {"patient_id": "patient-9", "case_id": "case-subject:patient-9",
                                    "case_namespace_kind": "patient_subject_namespace",
                                    "selection_method": "public_instruction_exact_patient_name",
                                    "case_payload_sha256": "a" * 64}
                    else:
                        observed = {"patient_id": "patient-9", "case_id": "cm-case-9", "referral_id": "ref-9",
                                    "selection_method": "public_instruction_exact_referral_cue",
                                    "case_payload_sha256": "b" * 64}
                    discovery.return_value = observed
                    profile = standalone.domain_for_task(task, domain)
                    report = standalone.run_case("owned-container", task, run_dir, "C:/Codex/codex.exe", {},
                                                 domain=domain)
                    self.assertEqual(ProfileHarness.last_completion_contract["task_id"], task.name)
                    self.assertEqual(ProfileHarness.last_completion_contract["scope"], report["scope"])
                    self.assertEqual(expected_port, ProfileActor.last_instance.port)
                    harness_domain, visible, scope, refusal, outsider, visible_specs, patient_refusal = ProfileHarness.seen[-1]
                    self.assertEqual(profile.engine_domain, harness_domain)
                    self.assertNotIn("search_patients", visible)
                    self.assertNotIn("queue", visible)
                    self.assertNotIn("outsider", visible)
                    self.assertTrue(outsider["known_not_dispatched"])
                    self.assertEqual(domain, report["domain"])
                    self.assertEqual("observed", report["actual_workflow_readback"]["status"],
                                     {"readback": report["actual_workflow_readback"],
                                      "actual_names": ProfileActor.last_instance._actual_names,
                                      "calls": ProfileActor.last_instance.calls})
                    if patient_case:
                        inbox_spec = next(spec for spec in visible_specs if spec.name == "inbox")
                        self.assertIn("case_id", inbox_spec.input_schema["required"])
                        self.assertIn("case_id", inbox_spec.identity_fields)
                        self.assertIn("only after cases.create_from_order", inbox_spec.description)
                        self.assertIn("Never use the internal case-subject namespace", inbox_spec.description)
                        self.assertEqual("case-subject:patient-9", scope.case)
                        self.assertTrue(refusal["known_not_dispatched"])
                        self.assertTrue(patient_refusal["known_not_dispatched"])
                        self.assertEqual("prior_authorization_case_state",
                                         report["actual_workflow_readback"]["observation_kind"])
                        self.assertEqual(PurePosixPath("/logs/artifacts/workspaces/actual-case-9/provider"),
                                         _FakeWorkspace.last_instance.root)
                        self.assertEqual(("workspace.write_file", {"path": "note.txt", "content": "after binding"}),
                                         _FakeWorkspace.last_instance.calls[-1])
                    else:
                        self.assertEqual("CM", harness_domain)
                        self.assertEqual("care_management_case_chart_state",
                                         report["actual_workflow_readback"]["observation_kind"])
        finally:
            for p in reversed(patches):
                p.stop()

    def test_public_provider_and_full_procedure_select_one_case_from_queue(self):
        selected = {
            "patient_id": "patient-a", "case_id": "case-a", "intake_id": "intake-a",
            "requesting_provider": {"provider_name": "North Valley Eye Center"},
            "line_items": [{"procedures": [{"name": "Phacoemulsification with Insertion of Intraocular Lens"}]}],
        }
        other = {
            "patient_id": "patient-b", "case_id": "case-b", "intake_id": "intake-b",
            "requesting_provider": {"provider_name": "North Valley Eye Center"},
            "line_items": [{"procedures": [{"name": "Retinal laser photocoagulation treatment"}]}],
        }
        client = _FakeMCP("owned-container", 8100, 30, object())
        client.queue = [other, selected]

        observed = standalone._discover_current_case(
            client, task_instruction=("North Valley Eye Center requests phacoemulsification with insertion "
                                     "of intraocular lens for the assigned case."))

        self.assertEqual("case-a", observed["case_id"])
        self.assertEqual("patient-a", observed["patient_id"])
        self.assertEqual("public_instruction_provider_procedure", observed["selection_method"])

    def test_public_instruction_bounded_six_token_procedure_prefix_selects_case(self):
        candidate = {
            "patient_id": "patient-prefix", "case_id": "case-prefix", "intake_id": "intake-prefix",
            "requesting_provider": {"provider_name": "Harbor Ophthalmology Group"},
            "line_items": [{"procedures": [{"name": "Cataract extraction by phacoemulsification with intraocular lens insertion, complex"}]}],
        }
        client = _FakeMCP("owned-container", 8100, 30, object())
        client.queue = [candidate, {
            "patient_id": "patient-other", "case_id": "case-other", "intake_id": "intake-other",
            "requesting_provider": {"provider_name": "Harbor Ophthalmology Group"},
            "line_items": [{"procedures": [{"name": "Retinal laser photocoagulation treatment"}]}],
        }]
        instruction = "Harbor Ophthalmology Group requests cataract extraction by phacoemulsification with intraocular lens replacement."

        observed = standalone._discover_current_case(client, task_instruction=instruction)

        self.assertEqual("case-prefix", observed["case_id"])
        self.assertEqual("public_instruction_provider_procedure", observed["selection_method"])

    def test_same_provider_and_procedure_matches_are_rejected_as_ambiguous(self):
        def candidate(case_id, patient_id):
            return {"case_id": case_id, "patient_id": patient_id,
                    "requesting_provider": {"provider_name": "North Valley Eye Center"},
                    "line_items": [{"procedures": [{"name": "Phacoemulsification with Insertion of Intraocular Lens"}]}]}
        client = _FakeMCP("owned-container", 8100, 30, object())
        client.queue = [candidate("case-a", "patient-a"), candidate("case-b", "patient-b")]
        instruction = "North Valley Eye Center requests phacoemulsification with insertion of intraocular lens."

        with self.assertRaisesRegex(standalone.StandaloneError, "exactly one case in actor-visible queue"):
            standalone._discover_current_case(client, task_instruction=instruction)

    def test_unmatched_public_provider_or_procedure_is_rejected(self):
        candidate = {
            "case_id": "case-a", "patient_id": "patient-a",
            "requesting_provider": {"provider_name": "North Valley Eye Center"},
            "line_items": [{"procedures": [{"name": "Phacoemulsification with Insertion of Intraocular Lens"}]}],
        }
        client = _FakeMCP("owned-container", 8100, 30, object())
        client.queue = [candidate, {**candidate, "case_id": "case-b", "patient_id": "patient-b"}]
        with self.assertRaisesRegex(standalone.StandaloneError, "exactly one case in actor-visible queue"):
            standalone._discover_current_case(
                client, task_instruction="A different provider requests retinal laser photocoagulation." )

    def test_explicit_case_must_be_in_queue_and_patient_may_come_from_review_readback(self):
        client = _FakeMCP("owned-container", 8100, 30, object())
        client.queue = [{"case_id": "case-live-99", "intake_id": "intake-live-42"}]
        original = _FakeMCP.call
        def without_patient(instance, name, arguments):
            value = original(instance, name, arguments)
            if name == "case_alias":
                return {"case_id": "case-live-99", "intake_id": "intake-live-42"}
            return value
        patches = self._patches()
        for p in patches:
            p.start()
        try:
            with patch.object(_FakeMCP, "call", without_patient):
                report = standalone.run_case("owned-container", self.task, self.run_dir, "C:/Codex/codex.exe", {},
                                             case_id="case-live-99", domain="pa_um")
            self.assertEqual(_FakeHarness.seen_scope.patient, "patient-live-77")
            self.assertEqual(report["scope"]["case"], "case-live-99")
            with self.assertRaisesRegex(standalone.StandaloneError, "explicit case_id"):
                standalone._discover_current_case(client, case_id="not-in-queue")
        finally:
            for p in reversed(patches):
                p.stop()

    def test_missing_patient_id_is_strict_by_default_and_opt_in_uses_case_namespace(self):
        client = _FakeMCP("owned-container", 8100, 30, object())
        client.queue = [{"case_id": "case-live-99", "intake_id": "intake-live-42"}]
        original = _FakeMCP.call
        def no_patient(instance, name, arguments):
            if name == "queue_alias":
                return {"items": [{"case_id": "case-live-99", "intake_id": "intake-live-42"}]}
            value = original(instance, name, arguments)
            if name in {"case_alias", "review_alias"}:
                return {"case_id": "case-live-99", "intake_id": "intake-live-42"}
            return value
        with patch.object(_FakeMCP, "call", no_patient):
            with self.assertRaisesRegex(standalone.StandaloneError, "did not provide a patient identity"):
                standalone._discover_current_case(client, case_id="case-live-99")
            observed = standalone._discover_current_case(
                client, case_id="case-live-99", allow_case_subject_namespace=True)
        self.assertNotIn("patient_id", observed)
        self.assertEqual(observed["case_id"], "case-live-99")

        patches = self._patches()
        for p in patches:
            p.start()
        try:
            with patch.object(_FakeMCP, "call", no_patient):
                report = standalone.run_case("owned-container", self.task, self.run_dir,
                                             "C:/Codex/codex.exe", {}, case_id="case-live-99",
                                             allow_case_subject_namespace=True, domain="pa_um")
            self.assertEqual(_FakeHarness.seen_scope.patient, "case-subject:case-live-99")
            self.assertEqual(report["scope"]["case"], "case-live-99")
            self.assertEqual(report["actual_determination_readback"]["status"], "observed")
            self.assertEqual(report["local_harness"]["status"], "unresolved")
            self.assertEqual(report["local_harness"]["completion_gate"]["reason_code"], "goal_unverified")
            self.assertEqual(_FakeHarness.last_completion_contract["task_id"], self.task.name)
            self.assertEqual(_FakeHarness.last_completion_contract["scope"], report["scope"])
            self.assertEqual(_FakeWorkspace.last_instance.root,
                             "/logs/artifacts/workspaces/case-live-99/payer")
            self.assertIn("/logs/artifacts/workspaces/case-live-99/shared/handoff",
                          _FakeWorkspace.last_instance.read_roots)
            self.assertIn("/logs/artifacts/workspaces/case-live-99/shared/intake",
                          _FakeWorkspace.last_instance.read_roots)
        finally:
            for p in reversed(patches):
                p.stop()

    def test_review_patient_id_from_foreign_case_is_rejected(self):
        client = _FakeMCP("owned-container", 8100, 30, object())
        client.queue = [{"case_id": "case-live-99", "intake_id": "intake-live-42"}]
        original = _FakeMCP.call
        def foreign_review(instance, name, arguments):
            if name == "queue_alias":
                return {"items": [{"case_id": "case-live-99", "intake_id": "intake-live-42"}]}
            value = original(instance, name, arguments)
            if name == "case_alias":
                return {"case_id": "case-live-99", "intake_id": "intake-live-42"}
            if name == "review_alias":
                return {"case_id": "case-other", "patient_id": "foreign-patient"}
            return value
        with patch.object(_FakeMCP, "call", foreign_review):
            with self.assertRaisesRegex(standalone.StandaloneError, "disagreed with the selected case"):
                standalone._discover_current_case(client, case_id="case-live-99",
                                                  allow_case_subject_namespace=True)

    def test_case_namespace_is_never_sent_as_remote_patient_id(self):
        class Delegate:
            def __init__(self):
                self.calls = []
            def bind_scope(self, scope):
                pass
            def list_tools(self):
                return []
            def call(self, name, arguments):
                self.calls.append((name, arguments))
                return {"ok": True}
        delegate = Delegate()
        guarded = standalone._CaseSubjectNamespaceTools(delegate, "case-subject:case-live-99", True)
        with self.assertRaisesRegex(standalone.StandaloneError, "cannot be sent"):
            guarded.call("actor.review", {"patient_id": "case-subject:case-live-99"})
        with self.assertRaisesRegex(standalone.StandaloneError, "cannot be sent"):
            guarded.call("actor.review", {"patient": {"id": "case-subject:case-live-99"}})
        self.assertEqual(delegate.calls, [])
        guarded.call("actor.review", {"case_id": "case-live-99"})
        self.assertEqual(len(delegate.calls), 1)

    def test_discovery_queue_is_hidden_and_guessed_alias_is_refused_before_dispatch(self):
        class Provider:
            def __init__(self):
                self.calls = []
                self.specs = [
                    ToolSpec("queue_alias", "list queue", {"type": "object", "properties": {}}),
                    ToolSpec("case_alias", "read bound case", {"type": "object", "properties": {}}),
                ]

            def list_tools(self):
                return list(self.specs)

            def call(self, name, arguments):
                self.calls.append((name, arguments))
                return {"ok": True}

        provider = Provider()
        registry = ToolRegistry(provider)
        guarded = standalone._CaseSubjectNamespaceTools(
            registry, "case-subject:case-live-99", False,
            {"queue_alias": "payer_intake_hub.list_intake_queue", "case_alias": "payer_intake_hub.get_intake_case"},
            discovery_only_names={"payer_intake_hub.list_intake_queue"})

        self.assertEqual(["case_alias"], [spec.name for spec in guarded.list_tools()])
        refused = guarded.call("queue_alias", {})
        self.assertTrue(refused["isError"])
        self.assertTrue(refused["known_not_dispatched"])
        self.assertEqual([], provider.calls)
        guarded.call("case_alias", {"case_id": "case-live-99"})
        self.assertEqual([("case_alias", {"case_id": "case-live-99"})], provider.calls)

    def test_provider_workspace_rebinds_only_after_trusted_actual_case(self):
        profile = standalone.domain_for_task(Path("synthetic"), "pa_provider")
        scope = standalone.Scope("docker:test", "task", "provider", "actor", "patient-9",
                                 "case-subject:patient-9")

        class Delegate:
            def __init__(self):
                self.calls = []

            def bind_scope(self, bound_scope):
                pass

            def list_tools(self):
                return []

            def call(self, name, arguments):
                self.calls.append((name, dict(arguments)))
                return {"ok": True}

        delegate = Delegate()
        names = {"create_alias": "cases.create_from_order"}
        guarded = standalone._CaseSubjectNamespaceTools(
            delegate, "patient-9", False, names, case_namespace=scope.case,
            case_identity_names={"cases.create_from_order"}, require_actual_case_for_writes=True)
        fake_workspace = type("Workspace", (), {})()
        fake_workspace.root = PurePosixPath("/logs/artifacts/workspaces/patient-9/provider")
        fake_workspace.case_root = fake_workspace.root / scope.key
        fake_workspace.read_roots = (PurePosixPath("/workspace/skills/managed-care-operations-handbook"),)

        pending_write = guarded.call("workspace.write_file", {"path": "draft.md", "content": "draft"})
        internal_case = guarded.call("create_alias", {"case_id": scope.case})
        self.assertTrue(pending_write["known_not_dispatched"])
        self.assertTrue(internal_case["known_not_dispatched"])
        self.assertEqual([], delegate.calls)

        binding = {"case_namespace": scope.case, "case_id": "actual-case-9", "patient_id": "patient-9",
                   "source_tool": "create_alias", "source_evidence_id": "ev:m1:create"}
        standalone._rebind_provider_workspace(fake_workspace, profile, scope, binding, guarded)
        self.assertEqual("actual-case-9", guarded.actual_case_id)
        self.assertEqual(PurePosixPath("/logs/artifacts/workspaces/actual-case-9/provider"),
                         fake_workspace.root)
        self.assertEqual(fake_workspace.root / scope.key, fake_workspace.case_root)
        self.assertIn(PurePosixPath("/logs/artifacts/workspaces/actual-case-9/shared"), fake_workspace.read_roots)
        self.assertNotIn(PurePosixPath("/logs/artifacts/workspaces/other-case/shared"), fake_workspace.read_roots)
        guarded.call("workspace.write_file", {"path": "draft.md", "content": "draft"})
        repeated_create = guarded.call("create_alias", {})
        self.assertTrue(repeated_create["known_not_dispatched"])
        self.assertEqual([("workspace.write_file", {"path": "draft.md", "content": "draft"})], delegate.calls)

    def test_provider_inbox_list_is_case_scoped_and_refused_until_binding(self):
        class Provider:
            def __init__(self):
                self.calls = []

            def list_tools(self):
                return [ToolSpec("inbox_alias", "list messages", {
                    "type": "object", "properties": {"case_id": {"type": "string"}},
                })]

            def call(self, name, arguments):
                self.calls.append((name, dict(arguments)))
                return {"items": []}

        provider = Provider()
        scope = standalone.Scope("docker:test", "task", "provider", "actor", "patient-9",
                                 "case-subject:patient-9")
        guarded = standalone._CaseSubjectNamespaceTools(
            provider, "patient-9", False, {"inbox_alias": "inbox.list_messages"},
            case_scoped_names={"inbox.list_messages"}, case_namespace=scope.case)

        spec = guarded.list_tools()[0]
        self.assertIn("case_id", spec.input_schema["required"])
        refusal = guarded.call("inbox_alias", {"case_id": "actual-case-9"})
        self.assertTrue(refusal["known_not_dispatched"])
        self.assertEqual([], provider.calls)

        binding = {"case_namespace": scope.case, "case_id": "actual-case-9", "patient_id": "patient-9",
                   "source_tool": "create_alias", "source_evidence_id": "ev:m1:create"}
        guarded.case_identity_aliases = {"create_alias"}
        guarded.bind_actual_case(binding)
        wrong_case = guarded.call("inbox_alias", {"case_id": "other-case"})
        self.assertTrue(wrong_case["known_not_dispatched"])
        self.assertEqual([], provider.calls)
        self.assertEqual({"items": []}, guarded.call("inbox_alias", {"case_id": "actual-case-9"}))
        self.assertEqual([("inbox_alias", {"case_id": "actual-case-9"})], provider.calls)

    def test_semantic_patient_matcher_requires_exact_two_source_quotes(self):
        task = "The assigned task names North Valley Surgical Center and cataract surgery."
        chart = '{"notes":"Cataract surgery is scheduled for next month."}'
        valid = json.dumps({"matches": True, "task_quote": "North Valley Surgical Center",
                            "context_quote": "Cataract surgery is scheduled"})
        self.assertTrue(standalone._parse_semantic_patient_match_response(valid, task, chart))
        negative = json.dumps({"matches": False, "task_quote": "", "context_quote": ""})
        self.assertFalse(standalone._parse_semantic_patient_match_response(negative, task, chart))
        invalid = (
            json.dumps({"matches": True, "task_quote": "North Valley", "context_quote": "invented chart text"}),
            json.dumps({"matches": True, "task_quote": "short", "context_quote": "Cataract surgery is scheduled"}),
            '{"matches":true,"matches":true,"task_quote":"North Valley Surgical Center","context_quote":"Cataract surgery is scheduled"}',
            json.dumps({"matches": True, "task_quote": "North Valley Surgical Center",
                        "context_quote": "Cataract surgery is scheduled", "extra": "ignored?"}),
        )
        for content in invalid:
            with self.subTest(content=content), self.assertRaises(standalone.StandaloneError):
                standalone._parse_semantic_patient_match_response(content, task, chart)

    def test_provider_identity_requires_distinct_narrative_evidence_not_diagnosis_label(self):
        task='# Shared diagnosis label\n\nPersistent weakness after rehabilitation. Imaging shows retracted tendons.'
        context=json.dumps({'note':'Persistent weakness. Retraction of tendons on imaging.'})
        valid={'matches':True,'identity_conflicts':[],'clinical_discrepancies':[],'missing_support':[],'evidence_pairs':[
            {'category':'presentation','task_quote':'Persistent weakness','context_quote':'Persistent weakness'},
            {'category':'imaging','task_quote':'Imaging shows retracted tendons','context_quote':'Retraction of tendons on imaging'}]}
        parse=lambda x: standalone._parse_semantic_identity_match_response(json.dumps(x),task,context,
                                                                           require_clinical_evidence=True)
        self.assertTrue(parse(valid))
        import copy
        wrong_case=copy.deepcopy(valid)
        wrong_case['evidence_pairs'][1]['context_quote']='retraction of tendons on imaging'
        with self.assertRaisesRegex(standalone.StandaloneError,r'evidence_pairs\[1\].context_quote.*case and punctuation'):
            parse(wrong_case)
        self.assertTrue(parse(valid)) # source spelling still validates unchanged
        invalid=[]
        x=copy.deepcopy(valid);x['evidence_pairs']=x['evidence_pairs'][:1];invalid.append(x)
        x=copy.deepcopy(valid);x['identity_conflicts']=['An explicit patient identifier contradicts the intake'];invalid.append(x)
        x=copy.deepcopy(valid);x['evidence_pairs'][0]['task_quote']='Shared diagnosis label';invalid.append(x)
        x=copy.deepcopy(valid);x['evidence_pairs'][1]['context_quote']='Invented matching image result';invalid.append(x)
        x=copy.deepcopy(valid);x['evidence_pairs'][1]['category']='presentation';invalid.append(x)
        for value in invalid:
            with self.subTest(value=value),self.assertRaises(standalone.StandaloneError):parse(value)
        self.assertFalse(parse({'matches':False,'evidence_pairs':[],'identity_conflicts':[],
                                'clinical_discrepancies':[],'missing_support':['No distinctive match']}))
        x=copy.deepcopy(valid);x['clinical_discrepancies']=['The imaging wording differs; investigate it.']
        self.assertTrue(parse(x))

    def test_identity_comparison_receipt_keeps_declared_decision_and_never_overwrites(self):
        decision={'matches':False,'identity_conflicts':[],'clinical_discrepancies':['Different imaging description'],
                  'missing_support':['Insufficient identifying anchors'],'evidence_pairs':[]}
        standalone._record_identity_comparison(self.run_dir,1,'public task','one candidate',
                                               json.dumps(decision),matched=False)
        receipt=json.loads((self.run_dir/'identity-comparison-001.private.json').read_text())
        self.assertEqual(decision,receipt['decision']);self.assertFalse(receipt['matched'])
        self.assertEqual(64,len(receipt['candidate_context_sha256']))
        with self.assertRaises(FileExistsError):
            standalone._record_identity_comparison(self.run_dir,1,'public task','other candidate','{}',matched=None)

    def test_bootstrap_matcher_uses_same_adapter_and_reduces_agent_budget(self):
        model_calls = []
        clinical_task = 'Persistent visual difficulty after treatment. Imaging confirms a focal opacity.'
        (self.task / 'instruction.md').write_text(clinical_task, encoding='utf-8')

        class BootstrapModel:
            def complete(self, messages, tools, *, max_output_tokens):
                model_calls.append((messages, tools, max_output_tokens))
                return ModelReply(content=json.dumps({
                    "matches": True, "identity_conflicts": [], "clinical_discrepancies": ["SELECTED_CASE_DISCREPANCY"], "missing_support": [],
                    "evidence_pairs": [
                        {"category":"presentation", "task_quote":"Persistent visual difficulty", "context_quote":"Cataract surgery is requested"},
                        {"category":"imaging", "task_quote":"Imaging confirms a focal opacity", "context_quote":"Imaging shows a focal opacity"}],
                }), usage={"input_tokens": 7, "output_tokens": 2})

        def discover(actor, profile, public_instruction, **kwargs):
            matcher = kwargs["semantic_patient_matcher"]
            context = {"notes": "x" * 45_000 +
                       " Cataract surgery is requested for this patient. Imaging shows a focal opacity."}
            matched = matcher(public_instruction, context)
            self.assertTrue(matched)
            return {"patient_id": "patient-9", "case_id": "case-subject:patient-9",
                    "case_namespace_kind": "patient_subject_namespace",
                    "case_payload_sha256": "c" * 64,
                    "selection_method": "public_instruction_isolated_semantic_match",
                    "semantic_matcher_invocations": 1,
                    "identity_comparison_context_sha256": standalone.hashlib.sha256(json.dumps(
                        context,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()}

        patchers = (
            patch.object(standalone, "DockerMCPClient", _FakeMCP),
            patch.object(standalone, "DockerExecutor", _FakeExecutor),
            patch.object(standalone, "DockerWorkspaceTools", _FakeWorkspace),
            patch.object(standalone, "CodexSessionModel", lambda *args, **kwargs: BootstrapModel()),
            patch.object(standalone, "CaseStore", _FakeStore),
            patch.object(standalone, "Harness", _FakeHarness),
            patch.object(standalone, "discover_domain_case", discover),
        )
        for item in patchers:
            item.start()
        try:
            report = standalone.run_case("owned-container", self.task, self.run_dir,
                                         "C:/Codex/codex.exe", {}, max_model_calls=5,
                                         domain="pa_provider")
            exhausted_run = self.root / "runs-provider-small-context"
            exhausted_run.mkdir()
            _FakeHarness.seen_scope = None
            calls_before = len(model_calls)
            with self.assertRaisesRegex(standalone.StandaloneError, "bounded matching context"):
                standalone.run_case("owned-container", self.task, exhausted_run, "C:/Codex/codex.exe", {},
                                    max_model_calls=5, max_context_chars=100, domain="pa_provider")
            self.assertEqual(calls_before, len(model_calls))
            self.assertIsNone(_FakeHarness.seen_scope)
        finally:
            for item in reversed(patchers):
                item.stop()

        self.assertEqual(1, len(model_calls))
        self.assertEqual([], model_calls[0][1])
        self.assertEqual(1024, model_calls[0][2])
        self.assertEqual(1, report["bootstrap_model_calls"])
        self.assertTrue(_FakeHarness.last_require_policy_grounding)
        self.assertEqual(3, report["model_calls_total_observed"])
        self.assertEqual(4, _FakeHarness.last_limits.max_model_calls)
        saved = json.loads((self.run_dir / "evaluation.json").read_text(encoding="utf-8"))
        self.assertEqual(1, saved["metadata"]["bootstrap_model_calls"])
        self.assertEqual(1, saved["metrics"]["model_calls_observed_this_segment"])
        self.assertEqual(7, saved["metrics"]["reported_usage_this_segment"]["input_tokens"])
        self.assertIn('SELECTED_CASE_DISCREPANCY',saved['metadata']['selected_identity_assessment']['assessment']['clinical_discrepancies'])
        self.assertIn('SELECTED_CASE_DISCREPANCY',_FakeHarness.last_instruction)
        self.assertIn('not a new clinical fact',_FakeHarness.last_instruction)

    def test_ambiguity_investigation_counts_budget_and_discards_other_candidate_context(self):
        task='Persistent visual difficulty. Imaging confirms a focal opacity.'
        (self.task/'instruction.md').write_text(task,encoding='utf-8')
        contexts=[{'notes':'Cataract surgery requested. Imaging shows focal opacity. OTHER_PATIENT_MARKER'},
                  {'notes':'Cataract surgery requested. Imaging shows focal opacity. SELECTED_PATIENT_MARKER'}]
        calls=[]
        class Model:
            def complete(self,messages,tools,**kwargs):
                calls.append(messages)
                if len(calls)<=2:
                    return ModelReply(content=json.dumps({'matches':True,'identity_conflicts':[],
                        'clinical_discrepancies':[], 'missing_support':[], 'evidence_pairs':[
                            {'category':'presentation','task_quote':'Persistent visual difficulty',
                             'context_quote':'Cataract surgery requested'},
                            {'category':'imaging','task_quote':'Imaging confirms a focal opacity',
                             'context_quote':'Imaging shows focal opacity'}]}))
                if len(calls)==3:
                    return ModelReply(tool_calls=tuple(ToolCall(str(i),'identity.inspect_candidate',
                        {'candidate_index':i,'path':'/notes','limit':4000}) for i in range(2)))
                return ModelReply(content=json.dumps({'status':'selected','candidate_index':1,
                    'uncertainties':[], 'candidate_assessments':[
                        {'candidate_index':i,'supports_selection':i==1,'reason':'Synthetic distinguishing explanation.',
                         'source_ids':[f'identity-read:{i+1}']} for i in range(2)]}))
        def discover(_actor,_profile,instruction,**kwargs):
            matcher=kwargs['semantic_patient_matcher']
            for context in contexts:self.assertTrue(matcher(instruction,context))
            self.assertEqual(1,matcher.resolve_ambiguity(instruction,contexts))
            return {'patient_id':'patient-9','case_id':'case-subject:patient-9',
                'case_namespace_kind':'patient_subject_namespace','case_payload_sha256':'c'*64,
                'selection_method':'public_instruction_investigated_match','semantic_matcher_invocations':2,
                'identity_comparison_context_sha256':standalone.hashlib.sha256(json.dumps(contexts[1],
                    ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()}
        patches=list(self._patches())+[
            patch.object(standalone,'CodexSessionModel',lambda *args,**kwargs:Model()),
            patch.object(standalone,'discover_domain_case',discover)]
        for item in patches:item.start()
        try:
            report=standalone.run_case('owned-container',self.task,self.run_dir,'C:/Codex/codex.exe',{},
                max_model_calls=15,domain='pa_provider')
        finally:
            for item in reversed(patches):item.stop()
        self.assertEqual(4,report['bootstrap_model_calls'])
        self.assertEqual(11,_FakeHarness.last_limits.max_model_calls)
        self.assertNotIn('OTHER_PATIENT_MARKER',_FakeHarness.last_instruction)
        self.assertNotIn('candidate_assessments',_FakeHarness.last_instruction)
        receipt=json.loads((self.run_dir/'identity-investigation.private.json').read_text(encoding='utf-8'))
        self.assertEqual('selected',receipt['status']);self.assertEqual(2,len(receipt['reads']))

    def test_bootstrap_matcher_corrects_one_candidate_locally_and_does_not_retry_nonmatch(self):
        model_calls = []
        test_case = self

        class BootstrapModel:
            def complete(self, messages, tools, *, max_output_tokens):
                self_outer = messages
                user_context = next(message["content"] for message in reversed(self_outer)
                                    if message.get("role") == "user" and
                                    "ONE_CANDIDATE_IDENTITY_CONTEXT_JSON" in message.get("content", ""))
                if len(model_calls) == 0:
                    test_case.assertIn("case-one", user_context)
                    content = json.dumps({
                        "matches": True,
                        "task_quote": "Synthetic public task instruction.",
                        "context_quote": "invented candidate evidence",
                    })
                elif len(model_calls) == 1:
                    test_case.assertIn("case-one", user_context)
                    test_case.assertNotIn("case-two", user_context)
                    test_case.assertIn("previous response failed exact source validation", messages[-1]["content"])
                    test_case.assertIn("Validation detail:", messages[-1]["content"])
                    content = json.dumps({
                        "matches": True,
                        "task_quote": "Synthetic public task instruction.",
                        "context_quote": "Cataract surgery is requested",
                    })
                else:
                    test_case.assertIn("case-two", user_context)
                    test_case.assertNotIn("case-one", user_context)
                    content = json.dumps({"matches": False, "task_quote": "", "context_quote": ""})
                model_calls.append(messages)
                return ModelReply(content=content, usage={"input_tokens": 5, "output_tokens": 2})

        def discover(_actor, _profile, public_instruction, **kwargs):
            matcher = kwargs["semantic_patient_matcher"]
            self.assertTrue(matcher(public_instruction, {"queue_record": {"case_id": "case-one"},
                                                         "intake_form_text": "Cataract surgery is requested"}))
            self.assertFalse(matcher(public_instruction, {"queue_record": {"case_id": "case-two"},
                                                           "intake_form_text": "Routine office visit"}))
            return {"patient_id": "patient-live-77", "case_id": "case-live-99",
                    "case_payload_sha256": "c" * 64, "selection_method": "public_instruction_isolated_semantic_match",
                    "semantic_matcher_invocations": 2}

        patches = list(self._patches()) + [
            patch.object(standalone, "CodexSessionModel", lambda *args, **kwargs: BootstrapModel()),
            patch.object(standalone, "discover_domain_case", discover),
        ]
        for item in patches:
            item.start()
        try:
            report = standalone.run_case("owned-container", self.task, self.run_dir,
                                         "C:/Codex/codex.exe", {}, max_model_calls=5, domain="pa_um")
        finally:
            for item in reversed(patches):
                item.stop()

        self.assertEqual(3, len(model_calls))
        self.assertEqual(3, report["bootstrap_model_calls"])
        self.assertEqual(2, _FakeHarness.last_limits.max_model_calls)

    def test_bootstrap_format_retry_is_counted_and_repeated_failure_stops(self):
        from health_harness_codex.providers import ModelResponseFormatError
        for budget,repeat,expected_calls in ((5,False,2),(5,True,2),(1,False,1)):
            calls=[]
            class BootstrapModel:
                def complete(model_self,messages,tools,**kwargs):
                    calls.append(messages)
                    if len(calls)==1 or repeat:raise ModelResponseFormatError('arguments_json',{'input_tokens':3})
                    self.assertIn('No proposal from that response was executed',messages[-1]['content'])
                    return ModelReply(content=json.dumps({'matches':True,'task_quote':'Synthetic public task instruction.',
                        'context_quote':'Cataract surgery is requested'}))
            def discover(_actor,_profile,public_instruction,**kwargs):
                self.assertTrue(kwargs['semantic_patient_matcher'](public_instruction,{'text':'Cataract surgery is requested'}))
                return {'patient_id':'patient-live-77','case_id':'case-live-99','case_payload_sha256':'c'*64,
                        'selection_method':'public_instruction_isolated_semantic_match','semantic_matcher_invocations':1}
            patches=list(self._patches())+[
                patch.object(standalone,'CodexSessionModel',lambda *args,**kwargs:BootstrapModel()),
                patch.object(standalone,'discover_domain_case',discover)]
            for item in patches:item.start()
            try:
                if repeat or budget==1:
                    with self.assertRaises((ModelResponseFormatError,standalone.StandaloneError)):
                        standalone.run_case('owned-container',self.task,self.run_dir,'C:/Codex/codex.exe',{},max_model_calls=budget,domain='pa_um')
                else:
                    report=standalone.run_case('owned-container',self.task,self.run_dir,'C:/Codex/codex.exe',{},max_model_calls=budget,domain='pa_um')
                    self.assertEqual(2,report['bootstrap_model_calls'])
                    self.assertEqual(3,_FakeHarness.last_limits.max_model_calls)
            finally:
                for item in reversed(patches):item.stop()
            self.assertEqual(expected_calls,len(calls))
            self.run_dir=self.root/f'format-case-{budget}-{repeat}';self.run_dir.mkdir()

    def test_bootstrap_quote_retry_is_bounded_and_respects_aggregate_budget(self):
        for model_budget, expected_calls, expected_error in (
            (5, 2, "patient matcher returned quotes that do not exactly match"),
            (1, 1, "bootstrap identity matching exhausted the aggregate model-call budget"),
        ):
            with self.subTest(model_budget=model_budget):
                model_calls = []

                class BootstrapModel:
                    def complete(self, messages, tools, *, max_output_tokens):
                        model_calls.append(messages)
                        return ModelReply(content=json.dumps({
                            "matches": True,
                            "task_quote": "Synthetic public task instruction.",
                            "context_quote": "invented candidate evidence",
                        }))

                def discover(_actor, _profile, public_instruction, **kwargs):
                    return kwargs["semantic_patient_matcher"](
                        public_instruction, {"intake_form_text": "Cataract surgery is requested"})

                patches = list(self._patches()) + [
                    patch.object(standalone, "CodexSessionModel", lambda *args, **kwargs: BootstrapModel()),
                    patch.object(standalone, "discover_domain_case", discover),
                ]
                for item in patches:
                    item.start()
                _FakeHarness.seen_scope = None
                try:
                    with self.assertRaisesRegex(standalone.StandaloneError, expected_error):
                        standalone.run_case("owned-container", self.task, self.run_dir,
                                             "C:/Codex/codex.exe", {}, max_model_calls=model_budget,
                                             domain="pa_um")
                finally:
                    for item in reversed(patches):
                        item.stop()
                self.assertEqual(expected_calls, len(model_calls))
                self.assertIsNone(_FakeHarness.seen_scope)
                receipt = json.loads((self.run_dir / ".setup-exception.private.json").read_text(encoding="utf-8"))
                self.assertIn(expected_error, receipt["message"])
                # Preserve the first attempt's receipt and evidence in each subtest.
                self.run_dir = self.root / f"runs-budget-{model_budget}"
                self.run_dir.mkdir()

    def test_um_intake_matcher_uses_shared_adapter_and_charges_every_candidate(self):
        model_calls = []
        intake_calls = []

        class BootstrapModel:
            def complete(self, messages, tools, *, max_output_tokens):
                model_calls.append((messages, tools, max_output_tokens))
                user_text = messages[-1]["content"]
                context_start = user_text.index("ONE_CANDIDATE_IDENTITY_CONTEXT_JSON\n") + len(
                    "ONE_CANDIDATE_IDENTITY_CONTEXT_JSON\n")
                context_json = user_text[context_start:]
                assert "single candidate source phrase" in context_json
                other_case = "case-two" if len(model_calls) == 1 else "case-one"
                assert other_case not in context_json
                return ModelReply(content=json.dumps({
                    "matches": True,
                    "task_quote": "Synthetic public task",
                    "context_quote": "single candidate source phrase",
                }), usage={"input_tokens": 5, "output_tokens": 2})

        def intake_reader_factory(_executor):
            def reader(case_id, metadata):
                intake_calls.append((case_id, metadata))
                return {"text": "single candidate source phrase", "source_sha256": "b" * 64,
                        "page_count": 1, "truncated": False}
            return reader

        def discover(actor, profile, public_instruction, **kwargs):
            self.assertEqual("pa_um", profile.name)
            matcher = kwargs["semantic_patient_matcher"]
            source_reader = kwargs["intake_context_reader"]
            for case_id in ("case-one", "case-two"):
                source = source_reader(case_id, {"case_id": case_id, "artifact_type": "intake_request_form"})
                self.assertTrue(matcher(public_instruction, {"queue_record": {"case_id": case_id},
                                                               "intake_form_text": source["text"]}))
            return {"patient_id": "patient-live-77", "case_id": "case-live-99",
                    "case_payload_sha256": "c" * 64,
                    "selection_method": "public_instruction_isolated_semantic_match",
                    "semantic_matcher_invocations": 2}

        patches = list(self._patches()) + [
            patch.object(standalone, "CodexSessionModel", lambda *args, **kwargs: BootstrapModel()),
            patch.object(standalone, "discover_domain_case", discover),
            patch("health_harness_codex.intake_sources.IntakeSourceReader", side_effect=intake_reader_factory),
        ]
        for item in patches:
            item.start()
        try:
            report = standalone.run_case("owned-container", self.task, self.run_dir,
                                         "C:/Codex/codex.exe", {}, max_model_calls=5, domain="pa_um")
        finally:
            for item in reversed(patches):
                item.stop()

        self.assertEqual(["case-one", "case-two"], [case for case, _metadata in intake_calls])
        self.assertEqual(2, len(model_calls))
        self.assertTrue(all(tools == [] and output_limit == 256
                            for _messages, tools, output_limit in model_calls))
        self.assertEqual(2, report["bootstrap_model_calls"])
        self.assertEqual(4, report["model_calls_total_observed"])
        self.assertEqual(3, _FakeHarness.last_limits.max_model_calls)

    def test_post_setup_run_exception_is_recorded_with_safe_reason_and_journal_statuses(self):
        patches = self._patches()
        for p in patches:
            p.start()
        try:
            with patch.object(standalone, "Harness", side_effect=RuntimeError("private clinical details")):
                report = standalone.run_case("owned-container", self.task, self.run_dir,
                                             "C:/Codex/codex.exe", {}, domain="pa_um")
            self.assertEqual(report["local_harness"]["status"], "runtime_failure")
            self.assertEqual(report["local_harness"]["error_type"], "RuntimeError")
            self.assertNotIn("private clinical details", str(report))
            self.assertEqual(report["local_harness"]["journal_statuses"], {})
            self.assertEqual(report["actual_determination_readback"]["status"], "skipped_after_run_exception")
        finally:
            for p in reversed(patches):
                p.stop()

    def test_ambiguous_live_queue_fails_before_model_or_harness(self):
        from health_harness_codex.evaluation import RunRecorder

        patches = self._patches()
        patches = (*patches, patch.object(standalone, "RunRecorder", RunRecorder))
        _FakeHarness.seen_scope = None
        console = StringIO()
        for p in patches:
            p.start()
        try:
            original = _FakeMCP.call
            def ambiguous(client, name, arguments):
                value = original(client, name, arguments)
                if name == "queue_alias":
                    items = value["structuredContent"]["items"]
                    return {"structuredContent": {"items": items + [{"patient_id": "patient-two", "case_id": "case-two"}]}}
                return value
            with patch.object(_FakeMCP, "call", ambiguous):
                with redirect_stdout(console):
                    with self.assertRaisesRegex(ValueError, "list_documents"):
                        standalone.run_case("owned-container", self.task, self.run_dir, "C:/Codex/codex.exe", {},
                                            domain="pa_um")
        finally:
            for p in reversed(patches):
                p.stop()
        receipt_path = self.run_dir / ".setup-exception.private.json"
        self.assertTrue(receipt_path.is_file())
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        self.assertEqual("actor_discovery", receipt["stage"])
        self.assertEqual("ValueError", receipt["exception_type"])
        self.assertIn("list_documents", receipt["message"])
        self.assertTrue(all(set(frame) == {"filename", "line", "function"}
                            for frame in receipt["traceback"]))
        self.assertTrue(receipt["traceback"])
        self.assertIsNone(_FakeHarness.seen_scope)
        console_text = console.getvalue()
        self.assertIn("stage=actor_discovery error_type=ValueError", console_text)
        self.assertNotIn("patient-live-77", console_text)
        self.assertNotIn("list_documents", console_text)
        events = [json.loads(line) for line in (self.run_dir / "events.jsonl").read_text(encoding="utf-8").splitlines()]
        setup_event = next(event for event in events if event["kind"] == "setup_failed")
        self.assertEqual({"time", "kind", "stage", "error_type", "error_code"}, set(setup_event))
        self.assertEqual("setup_error", setup_event["error_code"])
        self.assertFalse(any(event["kind"] in {"model_call_started", "tool_call_planned"}
                             for event in events))
        evaluation = json.loads((self.run_dir / "evaluation.json").read_text(encoding="utf-8"))
        self.assertEqual("actor_discovery", evaluation["actual_environment_observations"]["setup_stage"])
        self.assertEqual("setup_error", evaluation["actual_environment_observations"]["setup_error_code"])
        self.assertTrue(evaluation["actual_environment_observations"]["private_diagnostic_written"])
        self.assertNotIn("patient-live-77", json.dumps(evaluation))

    def test_rejects_non_public_or_unsupported_task_directories(self):
        with self.assertRaisesRegex(standalone.StandaloneError, "regular public instruction"):
            standalone.run_case("owned-container", self.root, self.run_dir, "C:/Codex/codex.exe", {},
                                domain="pa_um")

    def test_run_dir_must_stay_under_ignored_local_runs(self):
        outside = Path(__file__).resolve().parents[1] / "outside-test-run-dir"
        patches = self._patches()
        for p in patches:
            p.start()
        try:
            with self.assertRaisesRegex(standalone.StandaloneError, "ignored local run data"):
                standalone.run_case("owned-container", self.task, outside, "C:/Codex/codex.exe", {},
                                    domain="pa_um")
        finally:
            for p in reversed(patches):
                p.stop()

    def test_existing_attempt_is_preserved_before_any_actor_or_model_call(self):
        saved = self.run_dir / "events.jsonl"
        saved.write_text('original receipt\n', encoding="utf-8")
        with patch.object(standalone, "DockerExecutor") as executor:
            with self.assertRaisesRegex(standalone.StandaloneError, "already contains an attempt"):
                standalone.run_case("owned-container", self.task, self.run_dir, "C:/Codex/codex.exe", {},
                                    domain="pa_um")
            executor.assert_not_called()
        self.assertEqual(saved.read_text(encoding="utf-8"), 'original receipt\n')


if __name__ == "__main__":
    import unittest
    unittest.main()
