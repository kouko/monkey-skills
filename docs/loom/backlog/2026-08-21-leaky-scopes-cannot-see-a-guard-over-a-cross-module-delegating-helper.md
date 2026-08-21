---
name: 2026-08-21-leaky-scopes-cannot-see-a-guard-over-a-cross-module-delegating-helper
description: leaky_scopes in test_gate_scripts_fail_loud_on_unreadable_input.py parses one file at a time, so it cannot see a guard around a top-level helper whose own body delegates the filesystem read to a symbol imported from another module
status: open
origin: 2026-08-21 code-as-spec-writing-rule arc, Task 5's mutation run over test_oracle_capability_claims.py
---

- The gap: `leaky_scopes` (in
  `loom-code/scripts/test_gate_scripts_fail_loud_on_unreadable_input.py`)
  builds its leaky-scope fixpoint from a single file's AST. A guard around
  a call to a top-level helper is only recognised as protecting a
  filesystem read when that helper's own body is visible in the same
  file. When the helper instead delegates the read to a symbol imported
  from another module, the call is neither in `_FS_CALLS` nor a locally
  tracked leaky scope inside the guarded file — the oracle cannot see
  past the import boundary, and a mutant of that guard survives a full
  oracle run undetected.

- Two call sites carry this shape today, both correct and both needed:
  - `check_queue_relation.py`'s `main` guards a call to the top-level
    helper `live_bet_names`, defined in the same file.
  - `check_north_star_link.py`'s `main` guards a call to the top-level
    helper `find_bet_entries`, defined in the same file.

  Both helpers delegate their actual filesystem read to `live_entries`,
  imported from `backlog_index`. Removing either guard would let an
  OSError reach `main` unguarded, and the oracle would not notice —
  the guards are correct, but the oracle cannot prove they are needed.

- These two survive as a named, reasoned exception in
  `loom-code/scripts/test_oracle_capability_claims.py`
  (`_CROSS_MODULE_BLIND_SPOT_SURVIVORS`), the same pattern the file
  already uses for its by-design `subprocess.run`-only exemptions — a
  survivor set that fails loudly (`test_the_family_has_no_survivor_outside_the_two_named_reasons`)
  if a new, unreasoned survivor appears.

- Next step, when picked up: extend `leaky_scopes` (or the surrounding
  discovery in the same file) to follow a same-repo `from X import Y`
  one hop — resolve `Y`'s definition in module `X` and fold its body
  into the guarded file's fixpoint before deciding leakiness. Re-run
  `test_oracle_capability_claims.py`'s cross-module cases after the
  change; they should flip from "survives by design" to "caught", at
  which point `_CROSS_MODULE_BLIND_SPOT_SURVIVORS` in that test file
  should be emptied and this entry closed.
