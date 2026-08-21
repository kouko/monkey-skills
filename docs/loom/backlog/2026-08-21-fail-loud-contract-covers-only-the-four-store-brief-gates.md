---
name: 2026-08-21-fail-loud-contract-covers-only-the-four-store-brief-gates
description: the unreadable-input fail-loud contract binds only the four store/brief gates; twenty other modules in loom-code/scripts/ are EXEMPT, and three of them are leaky by the contract's own metric today
status: open
origin: 2026-08-21 dissolve-direction-layer round-7 review — the EXEMPT block claimed this widening was already filed as backlog work when no such entry existed; the reviewer caught the overclaim and this entry is the filing that comment now points at
start: the next time a non-gate script in loom-code/scripts/ dies on a raw traceback in front of a user, or the next arc that touches archive_change_folder.py, loom_init.py, or plan_card.py for any other reason
---

- Start: the next time a non-gate script in loom-code/scripts/ dies on a
  raw traceback in front of a user, or the next arc that touches
  archive_change_folder.py, loom_init.py, or plan_card.py for any other
  reason

- Origin: 2026-08-21 dissolve-direction-layer round-7 review — the EXEMPT
  block claimed this widening was already filed as backlog work when no
  such entry existed; the reviewer caught the overclaim and this entry is
  the filing that comment now points at

- What: `test_gate_scripts_fail_loud_on_unreadable_input.py` binds four
  scripts — `backlog_index.py`, `check_onramp_choice.py`,
  `check_queue_relation.py`, `check_north_star_link.py` — to a contract:
  an unreadable input produces a nonzero exit, no traceback, and the path
  named. Every other module in that directory sits in `EXEMPT` with a
  stated reason. Exempt means "outside the contract", not "checked and
  safe", and the difference is measurable: running the file's own
  `leaky_scopes()` over the exempt set shows `archive_change_folder.py`,
  `loom_init.py` and `plan_card.py` leaky today. `plan_card.py` is the
  one a user meets most often — it renders the progress card at every
  station of the close-out.

- Why not now: the arc that built this contract was dissolving the
  direction layer, and widening it to twenty more scripts is a different
  piece of work with a different blast radius. Doing it at that arc's
  close-out would have been scope creep dressed as diligence.

- Shape when it happens: the machinery already exists and is the cheap
  half. Move a script from `EXEMPT` to `FAMILY`, add its unreadable-input
  cases, and let `test_no_recognised_oserror_escape_reaches_main` name
  what leaks. The expensive half is deciding, per script, what an
  actionable failure line should SAY — which is judgment, not mechanism,
  and is why this is worth doing deliberately rather than in a sweep.

- Known limit to carry forward: the contract's completeness leg
  recognises filesystem calls by callee NAME. A call reached through a
  variable holding a bound method, or an I/O entry point whose name is
  not in `_FS_CALLS`, still escapes it. That limit is stated in the
  leg's own docstring; two review rounds caught earlier revisions
  claiming more than they delivered, so keep the claim sized to the
  mechanism when this is widened.
