"""Offline contracts, rendering, guard text, source sync and size regression checks."""
from contextlib import closing
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from health_harness_codex import roles
from health_harness_codex.assignment import stage_guidance
from health_harness_codex.dialogue_worker import outreach_question, QUESTION_CAP
from health_harness_codex.models import ToolCall
from health_harness_codex.engine import Harness
from health_harness_codex.store import CaseStore
from test_goal_planning import base, ev, SCOPE

ROOT=Path(__file__).resolve().parents[2]
HIDDEN=set('SH-02 SH-04 SH-06 SH-07 SH-08 SH-09'.split())
CM04_AUTHORITY=("Speaks for the program to the member: may state the program's purpose, services, cost and participation "
    "terms as the retrieved policy states them, once the policy's conditions are checked against the member's records; "
    "may explain what care planning could include, ask for enrollment consent, and conduct the permitted interview after consent. "
    "It speaks as the member's health plan: the member's observed active coverage with the plan operating the program is "
    "the plan information that participation statements rely on.")
BEFORE={'PA':(22195,16529),'UM':(21992,16331),'CM':(27613,21469)}


def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


class RoleAuthorityTests(TestCase):
    def test_all_66_fields_mappings_status_and_affirmative_text(self):
        catalog=roles._catalogue()
        hospital={r['id'] for r in json.loads((ROOT/'Plan/HealthcareRoles/data/roles.json').read_text(encoding='utf-8'))}
        self.assertEqual(66,len(catalog))
        for r in catalog:
            with self.subTest(role=r['id']):
                self.assertNotIn('status',r)
                self.assertEqual(r['id'] not in HIDDEN,r['model_visible'])
                self.assertEqual('executing_worker' if r['id'] in {'CM-04','SH-10'} else 'prompt_contract',r['status_label'])
                self.assertIsInstance(r['hospital_roles'],list)
                self.assertTrue(set(r['hospital_roles'])<=hospital)
                self.assertEqual(r['domain']!='SH',bool(r['hospital_roles']))
                self.assertRegex(r['authority'],r'^[A-Z][a-z]+(?:s|es)\b')
                self.assertNotIn('Accountable for',r['authority'])
                self.assertNotIn('within the assigned task and retrieved policy',r['authority'])
                if r['id']!='CM-04':self.assertLessEqual(len(r['authority']),160)
                self.assertLessEqual(len(r['approach']),200)
                self.assertTrue(r['approach'].strip())
                self.assertLessEqual(len(re.split(r'(?<=[.!?])\s+',r['approach'])),2)
                # Check all prompt-facing contract text, not provenance notes or saved dialogue.
                text=' '.join(r[k] for k in ('name','decision_scope','authority','approach','boundary','output','completion_check'))
                self.assertNotRegex(text,r'(?i)\b(?:cm|um|pa)_[a-z0-9_]+|CM-(?:CASE|PAT)|\b(?:patient|member)\s+(?:named|name\s*:)|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}')

    def test_cm04_exact_text_and_unchanged_cm17_18_19_contracts(self):
        current={r['id']:r for r in roles._catalogue()}
        self.assertEqual(CM04_AUTHORITY,current['CM-04']['authority'])
        self.assertEqual('Member-engagement lead',current['CM-04']['name'])
        previous=json.loads(subprocess.check_output(['git','show',
            'HEAD:HealthHarnessCodex/health_harness_codex/data/micro_roles.json'],cwd=ROOT))
        for r in previous:
            self.assertEqual(r['boundary'].encode('utf-8'),current[r['id']]['boundary'].encode('utf-8'))
            if r['id'] in {'CM-17','CM-18','CM-19'}:
                for k,v in r.items():
                    if k!='status':self.assertEqual(v,current[r['id']][k])

    def test_runtime_matches_generated_blueprint_except_documented_overrides(self):
        blueprint=load_module('authority_blueprint',ROOT/'HealthHarnessBlueprint/micro_roles.py')
        overrides=load_module('authority_overrides',ROOT/'HealthHarnessBlueprint/runtime_overrides.py')
        generated=json.loads((ROOT/'HealthHarnessBlueprint/data/micro_roles.json').read_text(encoding='utf-8'))
        self.assertEqual(blueprint.ROLES,generated)
        self.assertEqual(overrides.runtime_catalogue(generated),list(roles._catalogue()))

    def test_hidden_safeguards_excluded_from_all_owner_compositions(self):
        for domain in BEFORE:
            for composition in ('combined','helpers','team'):
                text=roles.system_prompt(domain,SCOPE,composition)
                for r in roles.roles_for(domain):
                    if r['model_visible']:
                        self.assertIn(f"{r['id']} {r['name']}: {r['decision_scope']} Authority: {r['authority']}",text)
                    else:
                        self.assertNotIn(r['id'],text)
                        with self.assertRaises(ValueError):roles.helper_prompt(r)

    def test_case_get_role_returns_hidden_contract_without_delegating_it(self):
        from health_harness_codex.helper_jobs import run_helper
        class NoTools:
            def list_tools(self):return []
        with closing(CaseStore(':memory:')) as store:
            harness=Harness(store,None,NoTools(),composition='helpers')
            for rid in HIDDEN:
                role=harness._local_call(SCOPE,base(),ToolCall('get','case.get_role',{'role_id':rid}),None,None)
                self.assertEqual(rid,role['id'])
                self.assertFalse(role['model_visible'])
                with self.assertRaises(ValueError):
                    run_helper(harness,SCOPE,base(),ToolCall('delegate','case.request_helper',{'role_id':rid}),None,None)

    def test_precedence_and_each_caution_protection_once_per_system_message(self):
        protections=('completed or immediate actions without tool/observation support',
            'specific facts absent from records or policy', 'schedules, names or availability',
            'guarantee outcomes or downstream benefits','pressure or manipulate participation',
            'bypass consent/privacy rules')
        texts=[roles.system_prompt(d,SCOPE,c) for d in BEFORE for c in ('combined','helpers','team')]
        texts += [roles.helper_prompt(r) for r in roles._catalogue() if r['model_visible']]
        for text in texts:
            self.assertEqual(1,text.count(roles.ROLE_PRECEDENCE))
            self.assertEqual(1,text.count(roles.SCOPED_CAUTION))
            self.assertIn('Authority never overrides a role boundary, consent/privacy rules, identity, or tool/observation requirements',text)
            for protection in protections:self.assertEqual(1,text.count(protection))
        for domain in ('PA','UM'):
            text=roles.system_prompt(domain,SCOPE,'helpers')
            self.assertNotIn('member decision',text)
            self.assertNotIn('program services after enrollment',text)

    def test_active_role_delivery_and_cm_outreach_packet(self):
        r=next(r for r in roles.roles_for('CM') if r['id']=='CM-04')
        text=roles.helper_prompt(r)
        for k in ('authority','approach','boundary'):self.assertIn(json.dumps(r[k]),text)
        for k in ('memory_policy','activation','execution_form','status_label','hospital_roles'):
            self.assertNotIn('"'+k+'":',text)
        state=base();ev(state,'cm_intake.open_case',{'case_id':'case'})
        packet=stage_guidance(state)['responsibility_packet']
        self.assertIn('CM-09',{r['role_id'] for r in packet})
        for r in packet:
            for k in ('decision_scope','authority','approach','boundary'):self.assertTrue(r[k])

    def test_question_cap_on_real_size_and_escaping_heavy_assignments(self):
        for instruction in ('Review coordination needs. '*200,'"\\\n\t'*10000,'λ'*12000):
            question=outreach_question(instruction,'ev:original','observed-session')
            self.assertLessEqual(len(question),QUESTION_CAP)
            context,excerpt=question.split('\n',1)
            value=json.loads(excerpt)
            self.assertTrue(value['assignment_excerpted'])
            self.assertTrue(instruction.startswith(value['public_assignment_excerpt']))
            self.assertIn('Only the owner saves and verifies',context)
            self.assertNotIn(roles.SCOPED_CAUTION,question)
        with self.assertRaises(ValueError):outreach_question('', 'x'*3000,'session')

    def test_owner_budget_and_cm04_system_plus_question_budget(self):
        for domain,before in BEFORE.items():
            for composition,old in zip(('combined','helpers'),before):
                self.assertLessEqual(len(roles.system_prompt(domain,SCOPE,composition)),old*1.15)
        role=next(r for r in roles._catalogue() if r['id']=='CM-04')
        # Worst capped question, not a tiny fixture with an accidental size margin.
        self.assertLessEqual(len(roles.helper_prompt(role,tool_access=True,allow_writes=True))+QUESTION_CAP,6572+4408)

    def test_catalogue_rejects_missing_or_malformed_new_fields(self):
        original=deepcopy(list(roles._catalogue()))
        mutations=[(k,None) for k in ('authority','approach','hospital_roles','status_label','model_visible')]
        mutations += [('model_visible','false'),('hospital_roles','M01'),('authority',''),('approach','x'*201),('status_label',[])]
        try:
            with TemporaryDirectory() as temp:
                root=Path(temp);(root/'data').mkdir()
                for field,value in mutations:
                    data=deepcopy(original);data[0][field]=value
                    (root/'data/micro_roles.json').write_text(json.dumps(data),encoding='utf-8')
                    roles._catalogue.cache_clear()
                    with patch.object(roles,'files',return_value=root),self.assertRaises(RuntimeError):roles._catalogue()
        finally:roles._catalogue.cache_clear()

    def test_roles_for_detaches_nested_mapping(self):
        first=roles.roles_for('CM');first[0]['hospital_roles'].append('tampered')
        self.assertNotIn('tampered',roles.roles_for('CM')[0]['hospital_roles'])
