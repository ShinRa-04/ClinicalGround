import unittest
from pathlib import Path

from health_harness_codex.domain_profiles import (
    DOMAIN_PROFILES,
    DomainSpec,
    discover_domain_case,
    domain_for_task,
    readback_domain_case,
)


class DomainProfileTests(unittest.TestCase):
    def test_profiles_are_immutable_and_have_expected_actor_runtime_contracts(self):
        self.assertIsInstance(DOMAIN_PROFILES["pa_provider"], DomainSpec)
        self.assertEqual(("PA", 8020, "provider"), (
            DOMAIN_PROFILES["pa_provider"].engine_domain,
            DOMAIN_PROFILES["pa_provider"].port,
            DOMAIN_PROFILES["pa_provider"].workspace_role,
        ))
        self.assertEqual(
            ("chart", "cases", "inbox", "docs", "forms", "auth", "people", "p2p_session"),
            DOMAIN_PROFILES["pa_provider"].namespaces,
        )
        self.assertEqual(("UM", 8100, "payer"), (
            DOMAIN_PROFILES["pa_um"].engine_domain,
            DOMAIN_PROFILES["pa_um"].port,
            DOMAIN_PROFILES["pa_um"].workspace_role,
        ))
        self.assertEqual(("CM", 8200, "care-manager"), (
            DOMAIN_PROFILES["cm"].engine_domain,
            DOMAIN_PROFILES["cm"].port,
            DOMAIN_PROFILES["cm"].workspace_role,
        ))
        self.assertEqual(
            ("cm_intake", "cm_chart", "cm_outreach", "cm_assessment", "cm_care_plan"),
            DOMAIN_PROFILES["cm"].namespaces,
        )
        self.assertEqual("cases.get_case", DOMAIN_PROFILES["pa_provider"].readback_tool)
        self.assertEqual("cm_chart.get_chart_data", DOMAIN_PROFILES["cm"].readback_tool)
        self.assertEqual(("cases.create_from_order",), DOMAIN_PROFILES["pa_provider"].case_identity_tools)
        self.assertEqual((), DOMAIN_PROFILES["pa_um"].case_identity_tools)
        self.assertEqual(("inbox.list_messages",), DOMAIN_PROFILES["pa_provider"].case_scoped_tools)
        self.assertNotIn("inbox.list_messages", DOMAIN_PROFILES["pa_provider"].discovery_only_tools)
        self.assertEqual(("chart.get_patient_chart_by_patient",), DOMAIN_PROFILES["pa_provider"].patient_scoped_tools)
        self.assertIn("payer_letter_center", DOMAIN_PROFILES["pa_um"].namespaces)
        self.assertIn("p2p_session", DOMAIN_PROFILES["pa_um"].namespaces)
        with self.assertRaises(TypeError):
            DOMAIN_PROFILES["new"] = DOMAIN_PROFILES["cm"]

    def test_domain_comes_from_dataset_ancestor_not_task_name(self):
        cases = (
            (r"C:\data\chi-bench\prior_auth_provider\tasks\pa_um_named_folder", "pa_provider"),
            (r"/data/chi-bench/prior_auth_um/tasks/cm_named_folder", "pa_um"),
            (r"C:\data\chi-bench\care_management\tasks\pa_t012", "cm"),
        )
        for path, expected in cases:
            with self.subTest(path=path):
                self.assertEqual(expected, domain_for_task(Path(path)).name)

    def test_legacy_synthetic_path_requires_an_explicit_validated_override(self):
        task = Path("/tmp/pa_public_task")
        with self.assertRaisesRegex(ValueError, "explicit domain override"):
            domain_for_task(task)
        self.assertEqual("pa_um", domain_for_task(task, "pa_um").name)
        for invalid in ("PA", "payer", "", None):
            if invalid is None:
                continue
            with self.subTest(override=invalid), self.assertRaisesRegex(ValueError, "domain override"):
                domain_for_task(task, invalid)

    def test_multiple_dataset_boundaries_are_rejected(self):
        task = Path("/data/prior_auth_provider/tasks/nested/care_management/tasks/task")
        with self.assertRaisesRegex(ValueError, "multiple χ-Bench dataset boundaries"):
            domain_for_task(task)

    def test_override_cannot_route_a_recognized_dataset_into_another_domain(self):
        task = Path("/data/chi-bench/care_management/tasks/cm_example")
        with self.assertRaisesRegex(ValueError, "conflicts with the task path"):
            domain_for_task(task, "pa_um")

    def test_um_discovery_delegates_public_instruction_and_identity_policy(self):
        instruction = "Review for Dr Jane Example requesting laparoscopic sleeve gastrectomy."
        actor = _UMActor([{
            "case_id": "case-observed-1",
            "requesting_provider": {"provider_name": "Dr Jane Example"},
            "line_items": [{"procedures": [{"name": "laparoscopic sleeve gastrectomy"}]}],
        }])
        captured = {}

        def legacy_discover(actual_actor, **kwargs):
            captured["actor"] = actual_actor
            captured.update(kwargs)
            return {
                "case_id": "case-observed-1",
                "patient_id": "patient-observed-1",
                "case_payload_sha256": "a" * 64,
                "selection_method": "public_instruction_provider_procedure",
            }

        result = discover_domain_case(
            actor,
            DOMAIN_PROFILES["pa_um"],
            instruction,
            case_id=None,
            allow_case_subject_namespace=False,
            legacy_um_discover=legacy_discover,
        )
        self.assertEqual("case-observed-1", result["case_id"])
        self.assertEqual("a" * 64, result["case_payload_sha256"])
        self.assertIs(actor, captured["actor"])
        self.assertEqual(instruction, captured["task_instruction"])
        self.assertEqual("case-observed-1", captured["case_id"])
        self.assertFalse(captured["allow_case_subject_namespace"])

    def test_um_empty_header_uses_one_isolated_intake_form_candidate(self):
        procedure = "Magnetic resonance imaging of brain with contrast"
        actor = _UMActor([
            {"case_id": "case-empty", "requesting_provider": None, "diagnoses": [],
             "line_items": [{"procedures": [{"name": procedure}]}]},
            {"case_id": "case-other", "requesting_provider": None, "diagnoses": [],
             "line_items": [{"procedures": [{"name": "Unrelated outpatient procedure"}]}]},
        ])
        instruction = "Please review Magnetic resonance imaging of brain with contrast."
        reads = []

        def reader(case_id, metadata):
            reads.append((case_id, metadata["case_id"]))
            return {"text": "Original request names Dr Jane Example.", "source_sha256": "c" * 64,
                    "truncated": True}

        seen = []
        progress_events = []
        def matcher(public_instruction, one_case_context):
            self.assertEqual(instruction, public_instruction)
            self.assertEqual({"queue_record", "intake_form_text", "intake_form_truncated"}, set(one_case_context))
            self.assertEqual("case-empty", one_case_context["queue_record"]["case_id"])
            self.assertNotIn("case-other", repr(one_case_context))
            self.assertTrue(one_case_context["intake_form_truncated"])
            seen.append(one_case_context["intake_form_text"])
            return "Dr Jane Example" in one_case_context["intake_form_text"]

        def legacy(_actor, **kwargs):
            self.assertEqual("case-empty", kwargs["case_id"])
            return {"case_id": "case-empty", "patient_id": "patient-1",
                    "case_payload_sha256": "a" * 64, "selection_method": "explicit_case_id"}

        result = discover_domain_case(
            actor, DOMAIN_PROFILES["pa_um"], instruction,
            legacy_um_discover=legacy, semantic_patient_matcher=matcher,
            intake_context_reader=reader,
            progress=lambda event, **fields: progress_events.append((event, fields)),
        )
        self.assertEqual("case-empty", result["case_id"])
        self.assertEqual("public_instruction_isolated_semantic_match", result["selection_method"])
        self.assertEqual("c" * 64, result["intake_source_sha256"])
        self.assertEqual(1, result["semantic_matcher_invocations"])
        self.assertEqual([("case-empty", "case-empty")], reads)
        self.assertEqual(1, len(seen))
        self.assertNotIn("intake_form_text", repr(result))
        self.assertNotIn("case-other", repr(result))
        self.assertEqual(["discovery_started", "discovery_roster_loaded",
                          "discovery_source_progress", "discovery_source_progress",
                          "discovery_finished"], [event for event, _fields in progress_events])
        self.assertEqual([(0, 1), (1, 1)], [
            (fields["current"], fields["total"])
            for event, fields in progress_events if event == "discovery_source_progress"
        ])
        self.assertTrue(all("case_id" not in fields and "patient_id" not in fields
                            for _event, fields in progress_events))

    def test_um_semantic_multiple_positive_candidates_fail_before_case_readback(self):
        procedure = "Magnetic resonance imaging of brain with contrast"
        actor = _UMActor([
            {"case_id": f"case-{index}", "requesting_provider": None, "diagnoses": [],
             "line_items": [{"procedures": [{"name": procedure}]}]}
            for index in (1, 2)
        ])
        reader_calls = []
        matcher_calls = []
        legacy_calls = []
        with self.assertRaisesRegex(ValueError, "2 positive candidates"):
            discover_domain_case(
                actor, DOMAIN_PROFILES["pa_um"], "Review MRI brain with contrast request.",
                legacy_um_discover=lambda *args, **kwargs: legacy_calls.append(kwargs),
                semantic_patient_matcher=lambda text, context: matcher_calls.append(context) or True,
                intake_context_reader=lambda case_id, metadata: reader_calls.append(case_id) or {
                    "text": f"Synthetic form for {case_id}", "source_sha256": "d" * 64,
                },
            )
        self.assertEqual(["case-1", "case-2"], reader_calls)
        self.assertEqual(2, len(matcher_calls))
        self.assertEqual([], legacy_calls)

    def test_um_shared_boilerplate_phrase_never_selects_without_isolated_matcher(self):
        procedure = "Magnetic resonance imaging of brain with contrast"
        actor = _UMActor([
            {"case_id": f"case-{index}", "requesting_provider": None,
             "line_items": [{"procedures": [{"name": procedure}]}]}
            for index in (1, 2)
        ])
        calls = []
        result = discover_domain_case(
            actor, DOMAIN_PROFILES["pa_um"],
            "Review Magnetic resonance imaging of brain with contrast prior authorization.",
            legacy_um_discover=lambda _actor, **kwargs: {
                "case_id": kwargs["case_id"], "patient_id": "patient-1",
                "case_payload_sha256": "f" * 64, "selection_method": "explicit_case_id",
            },
            semantic_patient_matcher=lambda _instruction, context: (
                calls.append(context) or context["queue_record"]["case_id"] == "case-2"
            ),
            intake_context_reader=lambda case_id, _metadata: {
                "text": "Please review this standard prior authorization request form.",
                "source_sha256": "b" * 64,
            },
        )
        self.assertEqual("case-2", result["case_id"])
        self.assertEqual(2, result["semantic_matcher_invocations"])
        self.assertEqual(2, len(calls))
        self.assertEqual("public_instruction_isolated_semantic_match", result["selection_method"])

    def test_um_unique_exact_provider_procedure_path_does_not_read_intake_forms(self):
        actor = _UMActor([
            {"case_id": "case-exact", "requesting_provider": {"provider_name": "Dr Jane Example"},
             "line_items": [{"procedures": [{"name": "Laparoscopic sleeve gastrectomy"}]}]},
            {"case_id": "case-other", "requesting_provider": {"provider_name": "Dr Other Person"},
             "line_items": [{"procedures": [{"name": "Laparoscopic sleeve gastrectomy"}]}]},
        ])
        legacy_calls = []
        result = discover_domain_case(
            actor, DOMAIN_PROFILES["pa_um"],
            "Review the request from Dr Jane Example for laparoscopic sleeve gastrectomy.",
            legacy_um_discover=lambda _actor, **kwargs: legacy_calls.append(kwargs) or {
                "case_id": "case-exact", "patient_id": "patient-1", "case_payload_sha256": "e" * 64,
                "selection_method": "explicit_case_id",
            },
            intake_context_reader=lambda *args: self.fail("exact unique public cue should skip PDF access"),
        )
        self.assertEqual("case-exact", result["case_id"])
        self.assertEqual("public_instruction_provider_procedure", result["selection_method"])
        self.assertEqual(0, result["semantic_matcher_invocations"])
        self.assertEqual("case-exact", legacy_calls[0]["case_id"])

    def test_provider_discovery_uses_public_name_and_never_creates_a_case(self):
        actor = _PublicActor({
            "chart.search_patients": {"items": [
                {"id": "pat-1", "patient_name": "Alex Rivera"},
                {"id": "pat-2", "patient_name": "Taylor Smith"},
            ], "total": 2},
            "chart.get_patient_chart_by_patient": {"patient": {"id": "pat-1"}, "diagnoses": ["selected chart"]},
        })
        observed = discover_domain_case(
            actor, DOMAIN_PROFILES["pa_provider"], "Prepare the request for Alex Rivera."
        )
        self.assertEqual("pat-1", observed["patient_id"])
        self.assertEqual("case-subject:pat-1", observed["case_id"])
        self.assertEqual("patient_subject_namespace", observed["case_namespace_kind"])
        self.assertEqual(["chart.search_patients", "chart.get_patient_chart_by_patient"],
                         [name for name, _ in actor.calls])
        self.assertNotIn("patient_name", observed)

    def test_provider_discovery_finds_named_patient_after_first_25_in_complete_65_patient_roster(self):
        records = [
            {"id": f"pat-{index:03d}", "patient_name": f"Patient {index:03d}"}
            for index in range(1, 66)
        ]
        actor = _PublicActor({
            "chart.search_patients": {"items": records, "total": 65},
            "chart.get_patient_chart_by_patient": {
                "pat-065": {"patient": {"id": "pat-065"}, "diagnoses": ["selected chart"]},
            },
        })

        observed = discover_domain_case(
            actor, DOMAIN_PROFILES["pa_provider"], "Prepare the request for Patient 065."
        )

        self.assertEqual("pat-065", observed["patient_id"])
        self.assertEqual(("chart.search_patients", {"limit": 256}), actor.calls[0])
        self.assertEqual(["chart.search_patients", "chart.get_patient_chart_by_patient"],
                         [name for name, _ in actor.calls])
        self.assertEqual({"patient_id": "pat-065"}, actor.calls[1][1])

    def test_provider_discovery_fails_closed_on_truncated_or_inconsistent_roster(self):
        records = [{"id": f"pat-{index:03d}", "patient_name": f"Patient {index:03d}"}
                   for index in range(1, 66)]
        for label, total in (("truncated", 300), ("inconsistent", 64), ("missing", None),
                             ("invalid_total", True)):
            with self.subTest(roster=label):
                payload = {"items": records}
                if total is not None:
                    payload["total"] = total
                actor = _PublicActor({"chart.search_patients": payload})
                with self.assertRaisesRegex(ValueError, "roster|total count"):
                    discover_domain_case(actor, DOMAIN_PROFILES["pa_provider"],
                                         "Prepare the request for Patient 065.")
                self.assertEqual(["chart.search_patients"], [name for name, _ in actor.calls])

    def test_provider_discovery_fails_closed_on_duplicate_or_invalid_roster_ids(self):
        base = [{"id": "pat-1", "patient_name": "Alex Rivera"},
                {"id": "pat-2", "patient_name": "Taylor Smith"}]
        duplicate = [base[0], {"id": "pat-1", "patient_name": "Taylor Smith"}]
        invalid = [base[0], {"id": "pat-\u0001bad", "patient_name": "Taylor Smith"}]
        for label, records in (("duplicate", duplicate), ("invalid", invalid)):
            with self.subTest(roster=label):
                actor = _PublicActor({"chart.search_patients": {"items": records, "total": 2}})
                with self.assertRaisesRegex(ValueError, "duplicate patient IDs|invalid patient ID"):
                    discover_domain_case(actor, DOMAIN_PROFILES["pa_provider"],
                                         "Prepare the request for Alex Rivera.")
                self.assertEqual(["chart.search_patients"], [name for name, _ in actor.calls])

    def test_provider_unique_diagnosis_is_not_identity_without_source_comparison(self):
        actor = _PublicActor({
            "chart.search_patients": {"items": [
                {"id": "pat-1", "patient_name": "Alex Rivera"},
                {"id": "pat-2", "patient_name": "Taylor Smith"},
            ], "total": 2},
            "chart.get_patient_chart_by_patient": {
                "pat-1": {"patient": {"id": "pat-1"}, "conditions": [{"display": "Chronic obstructive pulmonary disease"}]},
                "pat-2": {"patient": {"id": "pat-2"}, "conditions": [{"display": "Type 2 diabetes mellitus"}]},
            },
        })
        with self.assertRaisesRegex(ValueError, "identity requires"):
            discover_domain_case(actor, DOMAIN_PROFILES["pa_provider"], "Review the type 2 diabetes mellitus history.")
        self.assertEqual(3, len(actor.calls))

        ambiguous = _PublicActor({
            "chart.search_patients": {"items": [
                {"id": "pat-1", "patient_name": "Alex Rivera"},
                {"id": "pat-2", "patient_name": "Taylor Smith"},
            ], "total": 2},
            "chart.get_patient_chart_by_patient": {
                "pat-1": {"patient": {"id": "pat-1"}, "conditions": [{"display": "Type 2 diabetes mellitus"}]},
                "pat-2": {"patient": {"id": "pat-2"}, "conditions": [{"display": "Type 2 diabetes mellitus"}]},
            },
        })
        with self.assertRaisesRegex(ValueError, "no exact actor-visible chart cue"):
            discover_domain_case(
                ambiguous, DOMAIN_PROFILES["pa_provider"], "Review the type 2 diabetes mellitus history."
            )

    def test_provider_semantic_matcher_receives_one_candidate_chart_and_requires_one_positive(self):
        records = [
            {"id": "pat-a", "patient_name": "Alex Rivera"},
            {"id": "pat-b", "patient_name": "Taylor Smith"},
        ]
        charts = {
            "pat-a": {"patient": {"id": "pat-a"}, "conditions": [{"display": "Chronic obstructive pulmonary disease"}]},
            "pat-b": {"patient": {"id": "pat-b"}, "conditions": [{"display": "Type 2 diabetes mellitus"}]},
        }
        instruction = (
            "# Clinical Intake — Chronic obstructive pulmonary disease\n\n"
            "Compare chronic obstructive pulmonary disease with type 2 diabetes mellitus."
        )
        actor = _PublicActor({
            "chart.search_patients": {"items": records, "total": 2},
            "chart.get_patient_chart_by_patient": charts,
        })
        seen = []
        progress_events = []

        def matcher(public_instruction, candidate_chart):
            self.assertEqual(instruction, public_instruction)
            self.assertIsInstance(candidate_chart, dict)
            self.assertEqual({"patient", "conditions"}, set(candidate_chart))
            seen.append(candidate_chart["conditions"][0]["display"])
            return "Type 2 diabetes mellitus" in candidate_chart["conditions"][0]["display"]

        observed = discover_domain_case(
            actor, DOMAIN_PROFILES["pa_provider"], instruction,
            semantic_patient_matcher=matcher,
            progress=lambda event, **fields: progress_events.append((event, fields)),
        )
        self.assertEqual("pat-b", observed["patient_id"])
        self.assertEqual("public_instruction_isolated_semantic_match", observed["selection_method"])
        self.assertEqual(2, observed["semantic_matcher_invocations"])
        self.assertEqual(2, len(seen))
        self.assertNotIn("patient_name", observed)
        self.assertEqual(["discovery_started", "discovery_roster_loaded",
                          "discovery_chart_progress", "discovery_chart_progress",
                          "discovery_finished"],
                         [event for event, _fields in progress_events])
        self.assertEqual([(0, 2), (2, 2)], [
            (fields["current"], fields["total"])
            for event, fields in progress_events if event == "discovery_chart_progress"
        ])
        self.assertTrue(all("patient_id" not in fields and "case_id" not in fields
                            for _event, fields in progress_events))

        ambiguous_actor = _PublicActor({
            "chart.search_patients": {"items": records, "total": 2},
            "chart.get_patient_chart_by_patient": charts,
        })
        calls = []
        with self.assertRaisesRegex(ValueError, "0 positive candidates|2 positive candidates"):
            discover_domain_case(
                ambiguous_actor, DOMAIN_PROFILES["pa_provider"], instruction,
                semantic_patient_matcher=lambda public_text, one_chart: calls.append(one_chart) or True,
            )
        self.assertEqual(2, len(calls))

    def test_provider_semantic_matcher_is_not_called_when_public_exact_name_is_unique(self):
        actor = _PublicActor({
            "chart.search_patients": {"items": [{"id": "pat-1", "patient_name": "Alex Rivera"}], "total": 1},
            "chart.get_patient_chart_by_patient": {"patient": {"id": "pat-1"}, "diagnoses": ["selected chart"]},
        })
        observed = discover_domain_case(
            actor, DOMAIN_PROFILES["pa_provider"], "Prepare the request for Alex Rivera.",
            semantic_patient_matcher=lambda *args: self.fail("semantic matcher must not run for unique public name"),
        )
        self.assertEqual(0, observed["semantic_matcher_invocations"])

    def test_provider_ambiguous_surname_is_resolved_by_unique_chart_cue(self):
        actor = _PublicActor({
            "chart.search_patients": {"items": [
                {"id": "pat-1", "patient_name": "Alex Smith", "last_name": "Smith"},
                {"id": "pat-2", "patient_name": "Taylor Smith", "last_name": "Smith"},
                {"id": "pat-3", "patient_name": "Jordan Rivera"},
            ], "total": 3},
            "chart.get_patient_chart_by_patient": {
                "pat-1": {"patient": {"id": "pat-1"}, "conditions": [{"display": "Obstructive sleep apnea"}]},
                "pat-2": {"patient": {"id": "pat-2"}, "conditions": [{"display": "Type 2 diabetes mellitus"}]},
                "pat-3": {"patient": {"id": "pat-3"}, "conditions": [{"display": "Pulmonary arterial hypertension"}]},
            },
        })
        instruction = (
            "# Clinical Intake — Dr Smith request\n\n"
            "Review the pulmonary arterial hypertension history for this authorization."
        )

        observed = discover_domain_case(actor, DOMAIN_PROFILES["pa_provider"], instruction,
                                       semantic_patient_matcher=lambda _text, chart: chart['patient']['id'] == 'pat-3')

        self.assertEqual("pat-3", observed["patient_id"])
        self.assertEqual("public_instruction_isolated_semantic_match", observed["selection_method"])
        self.assertNotIn("patient_name", observed)

    def test_provider_full_name_remains_a_hard_constraint_when_chart_cue_conflicts(self):
        actor = _PublicActor({
            "chart.search_patients": {"items": [
                {"id": "pat-1", "patient_name": "Alex Smith", "last_name": "Smith"},
                {"id": "pat-2", "patient_name": "Taylor Smith", "last_name": "Smith"},
                {"id": "pat-3", "patient_name": "Jordan Rivera"},
            ], "total": 3},
            "chart.get_patient_chart_by_patient": {
                "pat-1": {"patient": {"id": "pat-1"}, "conditions": [{"display": "Obstructive sleep apnea"}]},
                "pat-2": {"patient": {"id": "pat-2"}, "conditions": [{"display": "Type 2 diabetes mellitus"}]},
                "pat-3": {"patient": {"id": "pat-3"}, "conditions": [{"display": "Pulmonary arterial hypertension"}]},
            },
        })
        instruction = (
            "# Clinical Intake — Alex Smith\n\n"
            "Dr Smith requests review of the pulmonary arterial hypertension history for this authorization."
        )

        with self.assertRaisesRegex(ValueError, "name and chart cue did not identify"):
            discover_domain_case(actor, DOMAIN_PROFILES["pa_provider"], instruction,
                                 semantic_patient_matcher=lambda _text, chart: chart['patient']['id'] == 'pat-3')

    def test_provider_diagnosis_distractor_never_excludes_paraphrased_correct_candidate(self):
        records=[{'id':'distractor','patient_name':'Alex Rivera'}, {'id':'correct','patient_name':'Taylor Smith'}]
        actor=_PublicActor({'chart.search_patients':{'items':records,'total':2},
            'chart.get_patient_chart_by_patient':{
                'distractor':{'patient':{'id':'distractor'},'conditions':[{'display':'Complete right shoulder tendon rupture'}]},
                'correct':{'patient':{'id':'correct'},'summaries':[{'text':'Retraction on imaging after twelve weeks of rehabilitation.'}]}}})
        seen=[]
        def matcher(text,chart):
            seen.append(chart['patient']['id']);return 'summaries' in chart
        result=discover_domain_case(actor,DOMAIN_PROFILES['pa_provider'],
            '# Complete right shoulder tendon rupture\n\nFailed rehabilitation with retracted tendons on imaging.',
            semantic_patient_matcher=matcher)
        self.assertEqual(['distractor','correct'],seen)
        self.assertEqual('correct',result['patient_id'])

    def test_provider_screen_excludes_demographic_contradictions_but_retains_unknowns(self):
        from health_harness_codex.domain_profiles import _provider_demographic_compatible
        intro='A 54-year-old male has persistent weakness.'
        chart={'patient':{'sex':'male','dob':'1971-01-01'},'encounters':[{'occurred_at':'2025-06-01'}]}
        self.assertTrue(_provider_demographic_compatible({},chart,intro))
        self.assertFalse(_provider_demographic_compatible({},dict(chart,patient={'sex':'female'}),intro))
        self.assertFalse(_provider_demographic_compatible({},dict(chart,patient={'sex':'male','dob':'1991-01-01'}),intro))
        self.assertTrue(_provider_demographic_compatible({}, {'patient':{}},intro))
        self.assertTrue(_provider_demographic_compatible({},dict(chart,patient={'sex':'male','dob':'1970-01-01'}),intro))

    def test_provider_comparison_capacity_checked_before_any_model_call(self):
        from health_harness_codex.domain_profiles import _select_provider_patient
        records=[{'id':f'p{i}','patient_name':f'Person {i}'} for i in range(5)]
        charts={x['id']:{'patient':{'id':x['id']}} for x in records}
        def matcher(*args):self.fail('oversized candidate pool must not consume model budget')
        matcher.max_candidate_calls=2
        with self.assertRaisesRegex(ValueError,'reserved setup budget'):
            _select_provider_patient(records,charts,'An unnamed clinical intake.',matcher)

    def test_rejected_provider_identity_is_not_read_or_sent_to_new_comparisons(self):
        actor=_PublicActor({'chart.search_patients':{'items':[
            {'id':'old','patient_name':'Old Person'},{'id':'new','patient_name':'New Person'}],'total':2},
            'chart.get_patient_chart_by_patient':{'new':{'patient':{'id':'new'},'content':'NEW_SOURCE'}}})
        seen=[]
        result=discover_domain_case(actor,DOMAIN_PROFILES['pa_provider'],'An unnamed clinical intake.',
            excluded_patient_ids=('old',),semantic_patient_matcher=lambda text,chart:seen.append(chart) or True)
        self.assertEqual('new',result['patient_id']);self.assertEqual(1,len(seen))
        self.assertEqual([{'patient_id':'new'}],[args for name,args in actor.calls if name=='chart.get_patient_chart_by_patient'])

    def test_rejected_cm_referral_is_excluded_before_selecting_and_reading(self):
        old={'case_id':'old-case','patient_id':'old','referral_id':'old-ref','patient_name':'Mei Zhang'}
        new={'case_id':'new-case','patient_id':'new','referral_id':'new-ref','patient_name':'Mei Zhang'}
        actor=_PublicActor({'cm_intake.list_referral_queue':{'result':[old,new]},'cm_intake.get_referral':new})
        result=discover_domain_case(actor,DOMAIN_PROFILES['cm'],'Complete intake for Mei Zhang.',
                                   excluded_patient_ids=('old',),excluded_case_ids=('old-case',))
        self.assertEqual('new',result['patient_id'])
        self.assertEqual({'referral_id':'new-ref'},actor.calls[-1][1])

    def test_provider_chart_readback_cannot_bind_another_roster_patient(self):
        actor = _PublicActor({
            "chart.search_patients": {"items": [{"id": "pat-1", "patient_name": "Alex Rivera"}], "total": 1},
            "chart.get_patient_chart_by_patient": {"patient": {"id": "pat-2"}, "diagnoses": ["wrong patient"]},
        })
        with self.assertRaisesRegex(ValueError, "patient identity disagreed"):
            discover_domain_case(actor, DOMAIN_PROFILES["pa_provider"], "Prepare the request for Alex Rivera.")

    def test_cm_discovery_requires_unique_public_cue_and_verifies_referral_readback(self):
        queue = [
            {"case_id": "cm-case-1", "referral_id": "ref-1", "patient_id": "pat-1",
             "patient_name": "Mei Zhang", "reason": "Medication coordination"},
            {"case_id": "cm-case-2", "referral_id": "ref-2", "patient_id": "pat-2",
             "patient_name": "Sam Jones", "reason": "Transportation assistance"},
        ]
        actor = _PublicActor({
            "cm_intake.list_referral_queue": {"result": queue},
            "cm_intake.get_referral": {"case_id": "cm-case-1", "referral_id": "ref-1", "patient_id": "pat-1"},
        })
        progress_events = []
        observed = discover_domain_case(actor, DOMAIN_PROFILES["cm"], "Complete intake for Mei Zhang.",
                                        progress=lambda event, **fields: progress_events.append((event, fields)))
        self.assertEqual("cm-case-1", observed["case_id"])
        self.assertEqual("ref-1", observed["referral_id"])
        self.assertEqual("pat-1", observed["patient_id"])
        self.assertEqual(["cm_intake.list_referral_queue", "cm_intake.get_referral"],
                         [name for name, _ in actor.calls])
        self.assertEqual(["discovery_started", "discovery_roster_loaded", "discovery_finished"],
                         [event for event, _fields in progress_events])
        self.assertEqual(2, progress_events[1][1]["total"])
        self.assertEqual("cm_chart.get_chart_data", DOMAIN_PROFILES["cm"].readback_tool)

    def test_cm_discovery_initializes_a_lazy_actor_catalogue_once(self):
        queue_record = {
            "case_id": "cm-case-1", "referral_id": "ref-1", "patient_id": "pat-1",
            "patient_name": "Mei Zhang", "reason": "Medication coordination",
        }
        actor = _LazyPublicActor({
            "cm_intake.list_referral_queue": {"result": [queue_record]},
            "cm_intake.get_referral": queue_record,
        })
        observed = discover_domain_case(actor, DOMAIN_PROFILES["cm"], "Complete intake for Mei Zhang.")
        self.assertEqual("cm-case-1", observed["case_id"])
        self.assertEqual(1, actor.list_tools_calls)
        self.assertEqual(["cm_intake.list_referral_queue", "cm_intake.get_referral"],
                         [name for name, _ in actor.calls])

    def test_cm_ambiguous_cue_and_disagreeing_readback_fail_closed(self):
        queue = [
            {"case_id": "cm-case-1", "referral_id": "ref-1", "patient_id": "pat-1",
             "patient_name": "Mei Zhang", "reason": "Medication coordination"},
            {"case_id": "cm-case-2", "referral_id": "ref-2", "patient_id": "pat-2",
             "patient_name": "Mei Zhang", "reason": "Medication coordination"},
        ]
        actor = _PublicActor({"cm_intake.list_referral_queue": {"result": queue}})
        with self.assertRaisesRegex(ValueError, "did not uniquely identify"):
            discover_domain_case(actor, DOMAIN_PROFILES["cm"], "Complete intake for Mei Zhang.")

        actor = _PublicActor({
            "cm_intake.list_referral_queue": {"result": [queue[0]]},
            "cm_intake.get_referral": {"case_id": "wrong-case", "referral_id": "ref-1", "patient_id": "pat-1"},
        })
        with self.assertRaisesRegex(ValueError, "did not match"):
            discover_domain_case(actor, DOMAIN_PROFILES["cm"], "Complete intake for Mei Zhang.")

        actor = _PublicActor({
            "cm_intake.list_referral_queue": {"result": [queue[0]]},
            "cm_intake.get_referral": {"case_id": "cm-case-1", "referral_id": "ref-1", "patient_id": "pat-other"},
        })
        with self.assertRaisesRegex(ValueError, "patient identity disagreed"):
            discover_domain_case(actor, DOMAIN_PROFILES["cm"], "Complete intake for Mei Zhang.")

    def test_profile_readback_envelopes_label_patient_chart_without_claiming_case_finalization(self):
        actor = _PublicActor({
            "chart.get_patient_chart_by_patient": {"patient": {"id": "pat-1"}},
            "cm_chart.get_chart_data": {"case_id": "cm-case-1", "status": "assessment_in_progress"},
        })
        pa_readback = readback_domain_case(actor, DOMAIN_PROFILES["pa_provider"], {
            "case_id": "case-subject:pat-1", "case_namespace_kind": "patient_subject_namespace",
            "patient_id": "pat-1",
        })
        self.assertEqual("observed", pa_readback["status"])
        self.assertEqual("chart.get_patient_chart_by_patient", pa_readback["tool"])
        self.assertEqual("patient_chart_state_not_case_finalization", pa_readback["observation_kind"])
        cm_readback = readback_domain_case(actor, DOMAIN_PROFILES["cm"], {"case_id": "cm-case-1"})
        self.assertEqual("cm_chart.get_chart_data", cm_readback["tool"])
        self.assertEqual("assessment_in_progress", cm_readback["result"]["structuredContent"]["status"])


class _PublicActor:
    def __init__(self, responses):
        self._actual_names = {f"tool-{index}": name for index, name in enumerate(responses)}
        self.responses = responses
        self.calls = []

    def call(self, alias, arguments):
        actual = self._actual_names[alias]
        self.calls.append((actual, dict(arguments)))
        response = self.responses[actual]
        if actual == "chart.get_patient_chart_by_patient" and isinstance(response, dict) and "patient" in response:
            return {"structuredContent": response, "content": [], "isError": False}
        if actual == "chart.get_patient_chart_by_patient" and isinstance(response, dict) and "patient_id" not in response:
            patient_id = arguments["patient_id"]
            response = response[patient_id]
        if isinstance(response, dict) and "structuredContent" in response:
            return response
        return {"structuredContent": response, "content": [], "isError": False}


class _LazyPublicActor(_PublicActor):
    def __init__(self, responses):
        super().__init__(responses)
        self._catalog = dict(self._actual_names)
        self._actual_names = {}
        self.list_tools_calls = 0

    def list_tools(self):
        self.list_tools_calls += 1
        self._actual_names.update(self._catalog)
        return []


class _UMActor:
    def __init__(self, queue):
        self.queue = queue
        self.calls = []
        self._actual_names = {
            "queue": "payer_intake_hub.list_intake_queue",
            "documents": "payer_intake_hub.list_documents",
        }

    def call(self, alias, arguments):
        actual = self._actual_names[alias]
        self.calls.append((actual, dict(arguments)))
        if actual.endswith("list_intake_queue"):
            return {"structuredContent": {"items": self.queue}, "content": [], "isError": False}
        case_id = arguments["case_id"]
        return {"structuredContent": {"items": [{
            "case_id": case_id,
            "artifact_type": "intake_request_form",
            "relative_path": f"{case_id}/shared/intake/request.pdf",
        }]}, "content": [], "isError": False}


if __name__ == "__main__":
    unittest.main()
