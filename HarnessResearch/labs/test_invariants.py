"""Offline fault/boundary examples; not upstream behavior or semantic-quality tests."""
import tempfile
import unittest
from pathlib import Path
from invariants import Message,Unit,project,BudgetError,Memory,SimulatedReceiver,Actions,StaleOwner


class ContextTests(unittest.TestCase):
    def test_protected_request_survives_recent_selection(self):
        units=(Unit('request',(Message('user','Preserve the unresolved goal'),),4,True),Unit('old',(Message('assistant','old'),),4),Unit('recent',(Message('user','new evidence'),),4))
        self.assertEqual([u.id for u in project(units,10,2)],['request','recent'])
        self.assertEqual(len(units),3) # canonical input not mutated

    def test_mandatory_context_overflow_is_explicit(self):
        with self.assertRaises(BudgetError):project((Unit('request',(Message('user','goal'),),9,True),),10,2)

    def test_tool_exchange_is_kept_or_removed_whole(self):
        tool=Unit('tool',(Message('call','lookup','a'),Message('result','found','a')),6)
        required=Unit('request',(Message('user','goal'),),4,True)
        self.assertEqual(project((tool,required),10,2),(required,))
        self.assertEqual(project((tool,required),12,2),(tool,required))

    def test_orphan_result_rejected(self):
        with self.assertRaises(ValueError):project((Unit('bad',(Message('result','missing request','x'),),1),),10,2)

    def test_duplicate_call_identity_rejected(self):
        pair=(Message('call','x','a'),Message('result','y','a'))
        with self.assertRaises(ValueError):project((Unit('one',pair,2),Unit('two',pair,2)),10,2)


class MemoryTests(unittest.TestCase):
    def test_scope_filter_does_not_mix_principals_or_cases(self):
        m=Memory();self.addCleanup(m.close)
        m.add('a','user-a','case-1','a','user');m.add('b','user-b','case-1','b','user');m.add('c','user-a','case-2','c','user')
        self.assertEqual([x['id'] for x in m.injectable('user-a','case-1')],['a'])

    def test_untrusted_derivation_is_not_auto_promoted(self):
        m=Memory();self.addCleanup(m.close)
        m.add('external','u','p','untrusted content')
        m.add('summary','u','p','rewritten content','reviewed',parent='external')
        self.assertEqual(m.injectable('u','p'),[])

    def test_known_derived_entries_tombstoned(self):
        m=Memory();self.addCleanup(m.close)
        m.add('a','u','p','source','user');m.add('b','u','p','summary','reviewed','a');m.add('c','u','p','summary2','reviewed','b')
        m.forget('a');self.assertEqual(m.injectable('u','p'),[])

    def test_deleted_origin_cannot_create_known_child(self):
        m=Memory();self.addCleanup(m.close)
        m.add('a','u','p','source','user');m.forget('a')
        with self.assertRaises(ValueError):m.add('b','u','p','new summary','reviewed','a')

    def test_out_of_scope_origin_rejected(self):
        m=Memory();self.addCleanup(m.close);m.add('a','one','p','fact','user')
        with self.assertRaises(ValueError):m.add('b','two','p','copied','reviewed','a')

    def test_optimistic_version_rejects_stale_amendment(self):
        m=Memory();self.addCleanup(m.close);m.add('a','u','p','v1','user')
        self.assertTrue(m.amend('a',1,'v2'));self.assertFalse(m.amend('a',1,'stale'))
        self.assertEqual(m.injectable('u','p')[0]['text'],'v2')

    def test_committed_local_memory_survives_connection_restart(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'memory.sqlite';m=Memory(path);m.add('a','u','p','fact','user');m.close()
            restored=Memory(path)
            try:self.assertEqual(restored.injectable('u','p')[0]['text'],'fact')
            finally:restored.close()


class EffectTests(unittest.TestCase):
    def test_lost_ack_retry_with_supported_receiver_contract(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'journal.sqlite';j=Actions(path);receiver=SimulatedReceiver();epoch=j.claim('s');payload={'quantity':1}
            j.prepare('s','action-1',payload,epoch);original=receiver.perform('action-1',payload)
            j.unknown('s','action-1',epoch);j.close() # receiver success was not recorded locally
            resumed=Actions(path)
            try:
                self.assertEqual(resumed.state('action-1'),'outcome-unknown')
                result=receiver.perform('action-1',payload)
                resumed.confirm('s','action-1',result,epoch)
                self.assertEqual(result,original);self.assertEqual(receiver.effects,1)
                self.assertEqual(resumed.state('action-1'),'confirmed')
            finally:resumed.close()

    def test_receiver_rejects_same_key_changed_intent(self):
        r=SimulatedReceiver();r.perform('k',{'x':1})
        with self.assertRaises(ValueError):r.perform('k',{'x':2})

    def test_journal_rejects_action_scope_or_intent_reuse(self):
        j=Actions();self.addCleanup(j.close);e=j.claim('s');j.prepare('s','k',{'x':1},e)
        with self.assertRaises(ValueError):j.prepare('s','k',{'x':2},e)

    def test_superseded_owner_cannot_publish_current_result(self):
        j=Actions();self.addCleanup(j.close);old=j.claim('s');j.prepare('s','k',{'x':1},old);new=j.claim('s')
        with self.assertRaises(StaleOwner):j.confirm('s','k',{'receipt':'late'},old)
        j.confirm('s','k',{'receipt':'reconciled'},new)
        self.assertEqual(j.state('k'),'confirmed')

    def test_local_checkpoint_does_not_dedupe_uncooperative_receiver(self):
        j=Actions();self.addCleanup(j.close);e=j.claim('s');j.prepare('s','k',{'x':1},e)
        external_effects=[]
        def receiver_ignoring_keys():external_effects.append('effect')
        receiver_ignoring_keys();j.unknown('s','k',e);receiver_ignoring_keys()
        self.assertEqual(len(external_effects),2) # intended counterexample: no exactly-once guarantee


if __name__=='__main__':unittest.main()
