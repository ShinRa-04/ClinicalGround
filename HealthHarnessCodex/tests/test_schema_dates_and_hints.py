import unittest
from health_harness_codex.models import Scope,ToolSpec
from health_harness_codex.schema import validate_arguments

SCOPE=Scope('synthetic','task','org','principal','patient','case')


class SchemaDatesAndHintsTests(unittest.TestCase):
    def test_date_format_checks_calendar_and_exact_date_shape(self):
        spec=ToolSpec('records.save','Save.',{'type':'object','properties':{'date':{'type':'string','format':'date'}},'required':['date']})
        for value in ['2024-02-29','2026-10-25']:validate_arguments(spec,{'date':value},SCOPE)
        for value in ['2023-02-29','2024-13-01','2024-2-9','2024-01-01T00:00:00Z','0000-01-01']:
            with self.subTest(value=value),self.assertRaises(ValueError):validate_arguments(spec,{'date':value},SCOPE)

    def test_nullable_date_remains_optional_and_nonstring_dates_are_not_accepted(self):
        spec=ToolSpec('records.save','Save.',{'type':'object','properties':{'date':{'anyOf':[
            {'type':'string','format':'date'},{'type':'null'}]}}})
        for value in [{},{'date':None},{'date':'2026-10-25'}]:validate_arguments(spec,value,SCOPE)
        with self.assertRaises(ValueError):validate_arguments(spec,{'date':20261025},SCOPE)

    def test_malformed_discriminator_is_rejected_without_using_it_to_select_a_branch(self):
        for hint in [None,{}, {'propertyName':''},{'propertyName':'kind','mapping':{'a':4}}]:
            spec=ToolSpec('records.save','Save.',{'type':'object','discriminator':hint})
            with self.subTest(hint=hint),self.assertRaises(ValueError):validate_arguments(spec,{},SCOPE)


if __name__=='__main__':unittest.main()
