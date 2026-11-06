# Role prompt baseline — Phase 0

Offline measurement on 2026-11-03. No model, Docker, dataset trial or judge was invoked. Saved database opened read-only; only lengths/counts are exported, with no dialogue or handbook text.

Command from `C:\Projects\BigData`:

```powershell
python -B -X utf8 HealthHarnessCodex/evaluations/prompt_metrics.py --report Progress/ROLE_PROMPT_BASELINE.md
```

| Domain | Combined chars | Helpers chars |
| --- | ---: | ---: |
| PA | 22195 | 16529 |
| UM | 21992 | 16331 |
| CM | 27613 | 21469 |

| CM phase | Guidance | Role packet | Full packet |
| --- | ---: | ---: | ---: |
| intake | 1360 | 743 | 2423 |
| outreach | 2516 | 1102 | 3940 |
| assessment | 1360 | 744 | 2428 |
| plan | 1360 | 811 | 2489 |
| closure | 1550 | 427 | 2298 |

| Saved CM-04 message | Chars | PROGRAM_DESCRIPTION | CAPABILITY_LIMITS |
| --- | ---: | ---: | ---: |
| system [0] | 6572 | 1 | 1 |
| user [1] | 24771 | 1 | 2 |
| question [1/question (subset)] | 4408 | 1 | 1 |

| Caution family (rendered surfaces) | Lexical matches | Matching statements |
| --- | ---: | ---: |
| unsupported_facts_authority | 86 | 86 |
| completed_effects_delivery | 109 | 75 |
| guarantees_immediacy | 61 | 42 |
| pressure_participation | 21 | 12 |
| consent_privacy_identity | 109 | 80 |
| unavailable_capability | 94 | 54 |
| stop_decline | 62 | 55 |
| provenance_isolation | 75 | 75 |

Caution counts cover the six owner prompts, five stage packets and two saved worker messages. Families overlap and include positive statements; these are reproducible lexical indicators, not a claim to classify every semantic caution in every possible runtime path. Synthetic stage fixtures follow the successful same-scope evidence pattern in tests/test_goal_planning.py. Packet serialization is defined by this script; caller formatting can change delivered size. Source hashes pin this baseline; no patient identifiers or saved content are exported.

A separate AST inventory covers candidate model-facing literals in nine runtime modules, including reviewer text; its counts include diagnostic/docstring false positives and do not expand imported constants. This is supplementary static evidence, not delivered-message size.

## Complete sanitized results

```json
{
  "measurement": "Unicode chars; compact JSON packets; exact guidance substring repetitions",
  "synthetic_scope": {
    "environment": "synthetic",
    "task": "goal-task",
    "organization": "org",
    "principal": "actor",
    "patient": "patient",
    "case": "case"
  },
  "owner_prompts": [
    {
      "domain": "PA",
      "composition": "combined",
      "chars": 22195
    },
    {
      "domain": "PA",
      "composition": "helpers",
      "chars": 16529
    },
    {
      "domain": "UM",
      "composition": "combined",
      "chars": 21992
    },
    {
      "domain": "UM",
      "composition": "helpers",
      "chars": 16331
    },
    {
      "domain": "CM",
      "composition": "combined",
      "chars": 27613
    },
    {
      "domain": "CM",
      "composition": "helpers",
      "chars": 21469
    }
  ],
  "cm_stages": [
    {
      "phase": "intake",
      "guidance_chars": 1360,
      "responsibility_packet_chars": 743,
      "full_packet_chars": 2423
    },
    {
      "phase": "outreach",
      "guidance_chars": 2516,
      "responsibility_packet_chars": 1102,
      "full_packet_chars": 3940
    },
    {
      "phase": "assessment",
      "guidance_chars": 1360,
      "responsibility_packet_chars": 744,
      "full_packet_chars": 2428
    },
    {
      "phase": "plan",
      "guidance_chars": 1360,
      "responsibility_packet_chars": 811,
      "full_packet_chars": 2489
    },
    {
      "phase": "closure",
      "guidance_chars": 1550,
      "responsibility_packet_chars": 427,
      "full_packet_chars": 2298
    }
  ],
  "saved_messages": [
    {
      "message_index": 0,
      "role": "system",
      "chars": 6572,
      "PROGRAM_DESCRIPTION": 1,
      "CAPABILITY_LIMITS": 1
    },
    {
      "message_index": 1,
      "role": "user",
      "chars": 24771,
      "PROGRAM_DESCRIPTION": 1,
      "CAPABILITY_LIMITS": 2
    },
    {
      "message_index": "1/question (subset)",
      "role": "question",
      "chars": 4408,
      "PROGRAM_DESCRIPTION": 1,
      "CAPABILITY_LIMITS": 1
    }
  ],
  "saved_database": "HealthHarnessCodex\\runs\\20261103-cm-dm-low-coop-luna-03\\cm\\cm_dm_low_coop_001\\attempt-1\\state.sqlite",
  "source_sha256": {
    "HealthHarnessCodex/health_harness_codex/roles.py": "c87602c3a759d7ff84a85218bf08bb6b9cdabf7ed078489081df5861abc56fba",
    "HealthHarnessCodex/health_harness_codex/assignment.py": "a8d81d0f38125a22f387a3a996573d05ba04309eaede7c18353ede52824ee59a",
    "HealthHarnessCodex/health_harness_codex/cm_guidance.py": "720196b4df7529575e6db6c60d5c2b22029a25d5db4b48b476e179a395a73a86",
    "HealthHarnessCodex/health_harness_codex/working_set.py": "6e9940d96c23fea6f7605d773b0ce173377226a177b6e1db6ff35f09454e64c3",
    "HealthHarnessCodex/health_harness_codex/planning.py": "1f3a0e85e193cfb065f510c5a30eb7ff1b1f1be6144cd056ef765fda38ffb541",
    "HealthHarnessCodex/health_harness_codex/dialogue_worker.py": "ea94b3c46608316e1ecac9f2a699df53c85e290db623b887824dfccd9a590104",
    "HealthHarnessCodex/health_harness_codex/closure.py": "01eb7d4b473c955b7de66164284a584a0b61d0a7adff253972da205aef5e6da5",
    "HealthHarnessCodex/health_harness_codex/recovery_audit.py": "0c45e3c2932a7010dec5a4f7e4d2db5ebdbc6acc94443242655c73662743e115",
    "HealthHarnessCodex/health_harness_codex/terminal_review.py": "72a32bb06145253bc19b77681619d8d8d0f83a26c3e41b5d712824ea35c91da9"
  },
  "caution_method": "Overlapping lexical families; matches plus sentence/newline units containing each family. Positive duties also match. Rendered surfaces are counted separately, not one conversation; other dynamic paths and tool schemas are not covered. No semantic deduplication claim.",
  "caution_patterns": {
    "unsupported_facts_authority": "\\b(?:invent\\w*|fabricat\\w*|unsupported)\\b",
    "completed_effects_delivery": "\\b(?:receipt\\w*|deliver\\w*|completed action\\w*|observed effect\\w*)\\b",
    "guarantees_immediacy": "\\b(?:guarantee\\w*|promis\\w*|immediate\\w*)\\b",
    "pressure_participation": "\\b(?:pressur\\w*|manipulat\\w*|coerc\\w*)\\b",
    "consent_privacy_identity": "\\b(?:consent|privacy|identit\\w*|permission\\w*)\\b",
    "unavailable_capability": "\\b(?:unavailable|absent|capability|capabilities|execution limit\\w*)\\b",
    "stop_decline": "\\b(?:stop|refus\\w*|declin\\w*|ended conversation)\\b",
    "provenance_isolation": "\\b(?:provenance|cross.patient|source.backed|source.linked|case.local)\\b"
  },
  "caution_by_surface": {
    "owner/PA/combined": {
      "unsupported_facts_authority": {
        "matches": 12,
        "matching_statements": 12
      },
      "completed_effects_delivery": {
        "matches": 11,
        "matching_statements": 9
      },
      "guarantees_immediacy": {
        "matches": 1,
        "matching_statements": 1
      },
      "pressure_participation": {
        "matches": 0,
        "matching_statements": 0
      },
      "consent_privacy_identity": {
        "matches": 7,
        "matching_statements": 7
      },
      "unavailable_capability": {
        "matches": 5,
        "matching_statements": 5
      },
      "stop_decline": {
        "matches": 6,
        "matching_statements": 6
      },
      "provenance_isolation": {
        "matches": 12,
        "matching_statements": 12
      }
    },
    "owner/PA/helpers": {
      "unsupported_facts_authority": {
        "matches": 9,
        "matching_statements": 9
      },
      "completed_effects_delivery": {
        "matches": 6,
        "matching_statements": 4
      },
      "guarantees_immediacy": {
        "matches": 1,
        "matching_statements": 1
      },
      "pressure_participation": {
        "matches": 0,
        "matching_statements": 0
      },
      "consent_privacy_identity": {
        "matches": 6,
        "matching_statements": 6
      },
      "unavailable_capability": {
        "matches": 4,
        "matching_statements": 4
      },
      "stop_decline": {
        "matches": 5,
        "matching_statements": 5
      },
      "provenance_isolation": {
        "matches": 10,
        "matching_statements": 10
      }
    },
    "owner/UM/combined": {
      "unsupported_facts_authority": {
        "matches": 12,
        "matching_statements": 12
      },
      "completed_effects_delivery": {
        "matches": 16,
        "matching_statements": 12
      },
      "guarantees_immediacy": {
        "matches": 1,
        "matching_statements": 1
      },
      "pressure_participation": {
        "matches": 0,
        "matching_statements": 0
      },
      "consent_privacy_identity": {
        "matches": 8,
        "matching_statements": 8
      },
      "unavailable_capability": {
        "matches": 5,
        "matching_statements": 5
      },
      "stop_decline": {
        "matches": 6,
        "matching_statements": 6
      },
      "provenance_isolation": {
        "matches": 13,
        "matching_statements": 13
      }
    },
    "owner/UM/helpers": {
      "unsupported_facts_authority": {
        "matches": 9,
        "matching_statements": 9
      },
      "completed_effects_delivery": {
        "matches": 8,
        "matching_statements": 5
      },
      "guarantees_immediacy": {
        "matches": 1,
        "matching_statements": 1
      },
      "pressure_participation": {
        "matches": 0,
        "matching_statements": 0
      },
      "consent_privacy_identity": {
        "matches": 4,
        "matching_statements": 4
      },
      "unavailable_capability": {
        "matches": 4,
        "matching_statements": 4
      },
      "stop_decline": {
        "matches": 5,
        "matching_statements": 5
      },
      "provenance_isolation": {
        "matches": 10,
        "matching_statements": 10
      }
    },
    "owner/CM/combined": {
      "unsupported_facts_authority": {
        "matches": 14,
        "matching_statements": 14
      },
      "completed_effects_delivery": {
        "matches": 17,
        "matching_statements": 13
      },
      "guarantees_immediacy": {
        "matches": 8,
        "matching_statements": 6
      },
      "pressure_participation": {
        "matches": 3,
        "matching_statements": 2
      },
      "consent_privacy_identity": {
        "matches": 19,
        "matching_statements": 14
      },
      "unavailable_capability": {
        "matches": 12,
        "matching_statements": 8
      },
      "stop_decline": {
        "matches": 16,
        "matching_statements": 13
      },
      "provenance_isolation": {
        "matches": 15,
        "matching_statements": 15
      }
    },
    "owner/CM/helpers": {
      "unsupported_facts_authority": {
        "matches": 12,
        "matching_statements": 12
      },
      "completed_effects_delivery": {
        "matches": 11,
        "matching_statements": 7
      },
      "guarantees_immediacy": {
        "matches": 8,
        "matching_statements": 6
      },
      "pressure_participation": {
        "matches": 3,
        "matching_statements": 2
      },
      "consent_privacy_identity": {
        "matches": 17,
        "matching_statements": 12
      },
      "unavailable_capability": {
        "matches": 12,
        "matching_statements": 8
      },
      "stop_decline": {
        "matches": 13,
        "matching_statements": 10
      },
      "provenance_isolation": {
        "matches": 11,
        "matching_statements": 11
      }
    },
    "stage/intake": {
      "unsupported_facts_authority": {
        "matches": 2,
        "matching_statements": 2
      },
      "completed_effects_delivery": {
        "matches": 5,
        "matching_statements": 3
      },
      "guarantees_immediacy": {
        "matches": 5,
        "matching_statements": 3
      },
      "pressure_participation": {
        "matches": 2,
        "matching_statements": 1
      },
      "consent_privacy_identity": {
        "matches": 3,
        "matching_statements": 2
      },
      "unavailable_capability": {
        "matches": 6,
        "matching_statements": 2
      },
      "stop_decline": {
        "matches": 0,
        "matching_statements": 0
      },
      "provenance_isolation": {
        "matches": 1,
        "matching_statements": 1
      }
    },
    "stage/outreach": {
      "unsupported_facts_authority": {
        "matches": 3,
        "matching_statements": 3
      },
      "completed_effects_delivery": {
        "matches": 6,
        "matching_statements": 4
      },
      "guarantees_immediacy": {
        "matches": 5,
        "matching_statements": 3
      },
      "pressure_participation": {
        "matches": 2,
        "matching_statements": 1
      },
      "consent_privacy_identity": {
        "matches": 7,
        "matching_statements": 4
      },
      "unavailable_capability": {
        "matches": 7,
        "matching_statements": 3
      },
      "stop_decline": {
        "matches": 1,
        "matching_statements": 1
      },
      "provenance_isolation": {
        "matches": 0,
        "matching_statements": 0
      }
    },
    "stage/assessment": {
      "unsupported_facts_authority": {
        "matches": 2,
        "matching_statements": 2
      },
      "completed_effects_delivery": {
        "matches": 5,
        "matching_statements": 3
      },
      "guarantees_immediacy": {
        "matches": 5,
        "matching_statements": 3
      },
      "pressure_participation": {
        "matches": 2,
        "matching_statements": 1
      },
      "consent_privacy_identity": {
        "matches": 2,
        "matching_statements": 1
      },
      "unavailable_capability": {
        "matches": 6,
        "matching_statements": 2
      },
      "stop_decline": {
        "matches": 1,
        "matching_statements": 1
      },
      "provenance_isolation": {
        "matches": 0,
        "matching_statements": 0
      }
    },
    "stage/plan": {
      "unsupported_facts_authority": {
        "matches": 2,
        "matching_statements": 2
      },
      "completed_effects_delivery": {
        "matches": 5,
        "matching_statements": 3
      },
      "guarantees_immediacy": {
        "matches": 5,
        "matching_statements": 3
      },
      "pressure_participation": {
        "matches": 2,
        "matching_statements": 1
      },
      "consent_privacy_identity": {
        "matches": 2,
        "matching_statements": 1
      },
      "unavailable_capability": {
        "matches": 6,
        "matching_statements": 2
      },
      "stop_decline": {
        "matches": 0,
        "matching_statements": 0
      },
      "provenance_isolation": {
        "matches": 0,
        "matching_statements": 0
      }
    },
    "stage/closure": {
      "unsupported_facts_authority": {
        "matches": 2,
        "matching_statements": 2
      },
      "completed_effects_delivery": {
        "matches": 5,
        "matching_statements": 3
      },
      "guarantees_immediacy": {
        "matches": 5,
        "matching_statements": 3
      },
      "pressure_participation": {
        "matches": 2,
        "matching_statements": 1
      },
      "consent_privacy_identity": {
        "matches": 2,
        "matching_statements": 1
      },
      "unavailable_capability": {
        "matches": 6,
        "matching_statements": 2
      },
      "stop_decline": {
        "matches": 0,
        "matching_statements": 0
      },
      "provenance_isolation": {
        "matches": 0,
        "matching_statements": 0
      }
    },
    "saved/CM-04/0": {
      "unsupported_facts_authority": {
        "matches": 3,
        "matching_statements": 3
      },
      "completed_effects_delivery": {
        "matches": 6,
        "matching_statements": 4
      },
      "guarantees_immediacy": {
        "matches": 7,
        "matching_statements": 5
      },
      "pressure_participation": {
        "matches": 3,
        "matching_statements": 2
      },
      "consent_privacy_identity": {
        "matches": 11,
        "matching_statements": 6
      },
      "unavailable_capability": {
        "matches": 8,
        "matching_statements": 4
      },
      "stop_decline": {
        "matches": 3,
        "matching_statements": 2
      },
      "provenance_isolation": {
        "matches": 3,
        "matching_statements": 3
      }
    },
    "saved/CM-04/1": {
      "unsupported_facts_authority": {
        "matches": 4,
        "matching_statements": 4
      },
      "completed_effects_delivery": {
        "matches": 8,
        "matching_statements": 5
      },
      "guarantees_immediacy": {
        "matches": 9,
        "matching_statements": 6
      },
      "pressure_participation": {
        "matches": 2,
        "matching_statements": 1
      },
      "consent_privacy_identity": {
        "matches": 21,
        "matching_statements": 14
      },
      "unavailable_capability": {
        "matches": 13,
        "matching_statements": 5
      },
      "stop_decline": {
        "matches": 6,
        "matching_statements": 6
      },
      "provenance_isolation": {
        "matches": 0,
        "matching_statements": 0
      }
    }
  },
  "caution_rendered_totals": {
    "unsupported_facts_authority": {
      "matches": 86,
      "matching_statements": 86
    },
    "completed_effects_delivery": {
      "matches": 109,
      "matching_statements": 75
    },
    "guarantees_immediacy": {
      "matches": 61,
      "matching_statements": 42
    },
    "pressure_participation": {
      "matches": 21,
      "matching_statements": 12
    },
    "consent_privacy_identity": {
      "matches": 109,
      "matching_statements": 80
    },
    "unavailable_capability": {
      "matches": 94,
      "matching_statements": 54
    },
    "stop_decline": {
      "matches": 62,
      "matching_statements": 55
    },
    "provenance_isolation": {
      "matches": 75,
      "matching_statements": 75
    }
  },
  "source_literal_inventory_method": "AST string constants longer than 40 chars containing a space, counted once per syntax occurrence. Candidate model-facing text includes diagnostics/docstrings; not all is delivered in one call. Concatenated references are not expanded. This separate static inventory is not added to rendered counts.",
  "caution_source_literal_inventory": {
    "HealthHarnessCodex/health_harness_codex/roles.py": {
      "unsupported_facts_authority": {
        "matches": 8,
        "matching_statements": 8
      },
      "completed_effects_delivery": {
        "matches": 7,
        "matching_statements": 5
      },
      "guarantees_immediacy": {
        "matches": 3,
        "matching_statements": 3
      },
      "pressure_participation": {
        "matches": 1,
        "matching_statements": 1
      },
      "consent_privacy_identity": {
        "matches": 16,
        "matching_statements": 12
      },
      "unavailable_capability": {
        "matches": 6,
        "matching_statements": 6
      },
      "stop_decline": {
        "matches": 12,
        "matching_statements": 9
      },
      "provenance_isolation": {
        "matches": 9,
        "matching_statements": 9
      }
    },
    "HealthHarnessCodex/health_harness_codex/assignment.py": {
      "unsupported_facts_authority": {
        "matches": 5,
        "matching_statements": 5
      },
      "completed_effects_delivery": {
        "matches": 5,
        "matching_statements": 5
      },
      "guarantees_immediacy": {
        "matches": 0,
        "matching_statements": 0
      },
      "pressure_participation": {
        "matches": 0,
        "matching_statements": 0
      },
      "consent_privacy_identity": {
        "matches": 5,
        "matching_statements": 3
      },
      "unavailable_capability": {
        "matches": 1,
        "matching_statements": 1
      },
      "stop_decline": {
        "matches": 1,
        "matching_statements": 1
      },
      "provenance_isolation": {
        "matches": 2,
        "matching_statements": 2
      }
    },
    "HealthHarnessCodex/health_harness_codex/cm_guidance.py": {
      "unsupported_facts_authority": {
        "matches": 2,
        "matching_statements": 2
      },
      "completed_effects_delivery": {
        "matches": 4,
        "matching_statements": 2
      },
      "guarantees_immediacy": {
        "matches": 5,
        "matching_statements": 3
      },
      "pressure_participation": {
        "matches": 3,
        "matching_statements": 2
      },
      "consent_privacy_identity": {
        "matches": 4,
        "matching_statements": 3
      },
      "unavailable_capability": {
        "matches": 10,
        "matching_statements": 4
      },
      "stop_decline": {
        "matches": 0,
        "matching_statements": 0
      },
      "provenance_isolation": {
        "matches": 0,
        "matching_statements": 0
      }
    },
    "HealthHarnessCodex/health_harness_codex/working_set.py": {
      "unsupported_facts_authority": {
        "matches": 0,
        "matching_statements": 0
      },
      "completed_effects_delivery": {
        "matches": 0,
        "matching_statements": 0
      },
      "guarantees_immediacy": {
        "matches": 0,
        "matching_statements": 0
      },
      "pressure_participation": {
        "matches": 0,
        "matching_statements": 0
      },
      "consent_privacy_identity": {
        "matches": 0,
        "matching_statements": 0
      },
      "unavailable_capability": {
        "matches": 4,
        "matching_statements": 4
      },
      "stop_decline": {
        "matches": 0,
        "matching_statements": 0
      },
      "provenance_isolation": {
        "matches": 1,
        "matching_statements": 1
      }
    },
    "HealthHarnessCodex/health_harness_codex/planning.py": {
      "unsupported_facts_authority": {
        "matches": 1,
        "matching_statements": 1
      },
      "completed_effects_delivery": {
        "matches": 0,
        "matching_statements": 0
      },
      "guarantees_immediacy": {
        "matches": 0,
        "matching_statements": 0
      },
      "pressure_participation": {
        "matches": 0,
        "matching_statements": 0
      },
      "consent_privacy_identity": {
        "matches": 0,
        "matching_statements": 0
      },
      "unavailable_capability": {
        "matches": 3,
        "matching_statements": 2
      },
      "stop_decline": {
        "matches": 1,
        "matching_statements": 1
      },
      "provenance_isolation": {
        "matches": 4,
        "matching_statements": 4
      }
    },
    "HealthHarnessCodex/health_harness_codex/dialogue_worker.py": {
      "unsupported_facts_authority": {
        "matches": 0,
        "matching_statements": 0
      },
      "completed_effects_delivery": {
        "matches": 3,
        "matching_statements": 3
      },
      "guarantees_immediacy": {
        "matches": 2,
        "matching_statements": 2
      },
      "pressure_participation": {
        "matches": 0,
        "matching_statements": 0
      },
      "consent_privacy_identity": {
        "matches": 16,
        "matching_statements": 11
      },
      "unavailable_capability": {
        "matches": 2,
        "matching_statements": 2
      },
      "stop_decline": {
        "matches": 3,
        "matching_statements": 3
      },
      "provenance_isolation": {
        "matches": 0,
        "matching_statements": 0
      }
    },
    "HealthHarnessCodex/health_harness_codex/closure.py": {
      "unsupported_facts_authority": {
        "matches": 1,
        "matching_statements": 1
      },
      "completed_effects_delivery": {
        "matches": 1,
        "matching_statements": 1
      },
      "guarantees_immediacy": {
        "matches": 0,
        "matching_statements": 0
      },
      "pressure_participation": {
        "matches": 0,
        "matching_statements": 0
      },
      "consent_privacy_identity": {
        "matches": 0,
        "matching_statements": 0
      },
      "unavailable_capability": {
        "matches": 0,
        "matching_statements": 0
      },
      "stop_decline": {
        "matches": 0,
        "matching_statements": 0
      },
      "provenance_isolation": {
        "matches": 2,
        "matching_statements": 2
      }
    },
    "HealthHarnessCodex/health_harness_codex/recovery_audit.py": {
      "unsupported_facts_authority": {
        "matches": 1,
        "matching_statements": 1
      },
      "completed_effects_delivery": {
        "matches": 0,
        "matching_statements": 0
      },
      "guarantees_immediacy": {
        "matches": 0,
        "matching_statements": 0
      },
      "pressure_participation": {
        "matches": 0,
        "matching_statements": 0
      },
      "consent_privacy_identity": {
        "matches": 1,
        "matching_statements": 1
      },
      "unavailable_capability": {
        "matches": 0,
        "matching_statements": 0
      },
      "stop_decline": {
        "matches": 1,
        "matching_statements": 1
      },
      "provenance_isolation": {
        "matches": 1,
        "matching_statements": 1
      }
    },
    "HealthHarnessCodex/health_harness_codex/terminal_review.py": {
      "unsupported_facts_authority": {
        "matches": 1,
        "matching_statements": 1
      },
      "completed_effects_delivery": {
        "matches": 0,
        "matching_statements": 0
      },
      "guarantees_immediacy": {
        "matches": 0,
        "matching_statements": 0
      },
      "pressure_participation": {
        "matches": 0,
        "matching_statements": 0
      },
      "consent_privacy_identity": {
        "matches": 1,
        "matching_statements": 1
      },
      "unavailable_capability": {
        "matches": 0,
        "matching_statements": 0
      },
      "stop_decline": {
        "matches": 2,
        "matching_statements": 2
      },
      "provenance_isolation": {
        "matches": 2,
        "matching_statements": 2
      }
    }
  }
}
```

## Phase 2 after measurements

Offline current-code measurement, 2026-11-03. The Phase 0 tables above remain historical. Saved message sizes in the script output are historical; the current worker sizes below come from prepare_probe, without inference or dispatch.

| Domain / composition | Before | After | Growth |
| --- | ---: | ---: | ---: |
| PA / combined | 22195 | 23284 | +4.91% |
| PA / helpers | 16529 | 18742 | +13.39% |
| UM / combined | 21992 | 23313 | +6.01% |
| UM / helpers | 16331 | 18776 | +14.97% |
| CM / combined | 27613 | 30196 | +9.35% |
| CM / helpers | 21469 | 24107 | +12.29% |

| Offline current probe | Turn | System | Question | Sum | Exact authority / DB unchanged |
| --- | ---: | ---: | ---: | ---: | --- |
| 20261103-cm-dm-low-coop-luna-03 | 4 | 7884 | 2633 | 10517 | True / True |
| 20261103-cm-dm-low-coop-luna-01 | 7 | 7884 | 2633 | 10517 | True / True |

Command: `python -X utf8 HealthHarnessCodex/evaluations/prompt_metrics.py --after-report Progress/ROLE_PROMPT_BASELINE.md`. Character counts are Unicode, not tokens. Full sanitized results stay in local runs/; no saved record, dialogue or protected policy text is exported.

Dedicated preparation verification (2026-11-03): owner text and fixed worker
system/question sizes are unchanged by this turn. The shared preparation instruction
is a separate worker-only user message, outside owner prompts. Additional selected
source observations and recorded statements are variable input and are not measured
by these fixed prompt counts. Both saved boundaries were rebuilt offline without
inference; source database hashes stayed unchanged.
