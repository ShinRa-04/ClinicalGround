import unittest

from health_harness_codex.cm_guidance import PROGRAM_DESCRIPTION, CAPABILITY_LIMITS, STOP_REVIEW
from health_harness_codex.roles import system_prompt, SCOPED_CAUTION
from health_harness_codex.assignment import stage_guidance
from health_harness_codex.dialogue_worker import stage_handoff
from test_goal_planning import base, SCOPE


class ProgramGuidanceTests(unittest.TestCase):
    def test_owner_supplies_shared_guidance_and_stage_keeps_only_stage_context(self):
        text=system_prompt('CM',SCOPE,'helpers')
        self.assertIn(PROGRAM_DESCRIPTION,text)
        self.assertIn(CAPABILITY_LIMITS,text)
        self.assertIn(SCOPED_CAUTION,text)
        self.assertIn('retrieved program or care-plan policy',text)
        guidance=stage_guidance(base())['guidance']
        self.assertNotIn(PROGRAM_DESCRIPTION,guidance)
        self.assertNotIn(CAPABILITY_LIMITS,guidance)

    def test_handoff_limits_do_not_negate_program_services_or_grant_authority(self):
        handoff=stage_handoff(base(),[])
        self.assertIn('system capability rule',handoff['capability_rule'])
        self.assertFalse(handoff['grants_permissions'])
        self.assertIn('owner/delegate boundaries',CAPABILITY_LIMITS)

    def test_stop_review_preserves_goal_and_evidence_checks(self):
        self.assertIn('counterparty decision',STOP_REVIEW)
        self.assertIn('owner chooses and cites the policy path',STOP_REVIEW)
        self.assertIn('does not establish that the requested goal was met',STOP_REVIEW)
        self.assertIn('all completion and evidence checks',STOP_REVIEW)
