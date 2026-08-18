---
name: 2026-07-06-four-deferred-items-from-the-living-spec-index-slices-paired-regex-locks
description: four deferred items from the living-spec index slices — paired-regex lockstep, drift-lane tokenization, a Rule-of-Three extraction, and ready-signal binding for both merge-boundary gates
status: OPEN
origin: living-spec index slices 1–4 + capstone G (#447–#455) deferred-debt ledger
start: next living-spec script touch (loom-code/scripts/living_spec_*.py or check-living-spec-index.py)
---

- Start: next living-spec script touch
  (loom-code/scripts/living_spec_*.py or check-living-spec-index.py)
- Origin: living-spec index slices 1–4 + capstone G (#447–#455)
  deferred-debt ledger
- What: (a) regex suffix-vocab lockstep — two regexes must move
  together when the suffix vocabulary changes; (b) drift-lane
  tokenize-ization; (c) Rule-of-Three `_matched_files` extraction;
  (d) Open-Q6 ready-signal binding for BOTH merge-boundary gates
  (verify-index + active-coverage).
- Item (a) closed by the requirement-identity-hybrid arc's Task 6
  (`_STATUS_VOCAB`, commit a62857e8) — both status regexes now derive
  from one module constant. (b)–(d) remain open.
