---
name: 2026-09-01-adversarial-audit-surfaced-preexisting-gate-holes
description: The prose-edit self-sweep arc's close-out adversarial audit reproduced four pre-existing holes in loom's own gate machinery (signal new-gate self-exemption blindness, Safety-bearing absent-header dodges the exit-3 STOP, forged empty-test pin, non-recursive fail-loud classification glob) — none introduced by that branch, all needing a RED test + fix before they can land in ATTACK-CATALOGUE ## Instances
status: open
origin: 2026-09-01 — finishing Step 3.5 adversarial audit (opus) of docs/loom/plans/2026-09-01-prose-edit-self-sweep.md at HEAD 5e6169b3; four reproduced vectors the audit itself marks as predating the branch; recorded here rather than in ATTACK-CATALOGUE ## Instances because that section requires `pinned by <test>` and these are unpinned pending fix
start: event — the next arc that touches check_attack_catalogue.py signal, test_gate_scripts_fail_loud_on_unreadable_input.py, or the ATTACK-CATALOGUE pin-checker, or a dedicated gate-hardening arc
---

Four reproduced vectors, each with the audit's own command (run in a
scratch clone, never against the repo):

1. **signal blind to a new gate that self-exempts.** A commit adding a
   brand-new gate script AND its own `EXEMPT` entry in
   `test_gate_scripts_fail_loud_on_unreadable_input.py` draws
   `adversarial audit: N/A … guarded-hits=0` — `check_attack_catalogue.py
   signal` never flags the self-exemption because the new script is not
   in `## Guarded paths` yet. (This arc's own `prose_selfsweep_tally.py`
   is the exercising case; its fail-loud behavior was separately fixed,
   but signal's blindness remains.)

2. **Safety-bearing ABSENT dodges the exit-3 STOP.** A plan with a
   guarded-path hit and `Safety-bearing: no` correctly STOPs (exit 3),
   but a plan that simply OMITS the header renders
   `safety-bearing: N/A — header absent` (exit 0) — omitting the header
   is strictly safer for the author than declaring it honestly. Distinct
   from the existing `Safety-bearing: no + gutted store` instance.

3. **Forged pin: an empty test closes a reproduced finding.** The store's
   `pinned by <test>` check is name-existence only:
   `def test_x(): pass` satisfies it, and
   `check_attack_catalogue.py <store>` exits 0. A `reproduced` finding can
   be "closed" by a test that asserts nothing.

4. **Non-recursive classification glob.** `test_every_script_here_is_
   classified` globs `SCRIPTS.glob("*.py")` (non-recursive), so a
   store-reading gate at `loom-code/scripts/nested/rogue_gate.py` escapes
   the "no script joins this directory silently" leg — 20 passed with the
   nested rogue present.

Each needs the normal TDD flow (RED test pinning the hole → fix →
`## Instances` entry) before it can be marked reproduced-and-pinned.
Bounded deliberately: fixing loom's gate infrastructure is a separate
arc, not the prose-edit self-sweep deliverable.
