---
name: 2026-08-21-fail-loud-contract-covers-only-the-four-store-brief-gates
description: the unreadable-input fail-loud contract binds only the four store/brief gates; 24 other modules in loom-code/scripts/ are EXEMPT, and 15 of them are leaky by the contract's own metric today (measured, not estimated — the count is pinned by test_exempt_leak_count_matches_the_filed_ledger)
status: open
origin: 2026-08-21 dissolve-direction-layer round-7 review — the EXEMPT block claimed this widening was already filed as backlog work when no such entry existed; the reviewer caught the overclaim and this entry is the filing that comment now points at
start: the next time a non-gate script in loom-code/scripts/ dies on a raw traceback in front of a user, or the next arc that touches ANY of the 15 leaky modules the pinned metric names for any other reason
---

- Start: the next time a non-gate script in loom-code/scripts/ dies on a
  raw traceback in front of a user, or the next arc that touches ANY of the
  15 leaky modules the pinned metric names for any other reason

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
  `leaky_scopes()` over the 24 exempt modules returns **15 leaky** —
  adjudication_lint / _render / _split, archive_change_folder,
  check-living-spec-index, check-skill-crossrefs, check_contract_citations,
  check_doc_citations, check_field_microstructure, check_open_questions,
  check_scenario_coverage, distribute, loom_init, plan_card, verify-drift.
  `plan_card.py` is the one a user meets most often — it renders the
  progress card at every station of the close-out.

  That number is PINNED by `test_exempt_leak_count_matches_the_filed_ledger`,
  which recomputes it and refuses to let this entry and the metric drift
  apart. It is pinned because the first version of this entry said "three",
  written from a measurement taken before the recogniser was widened and
  never re-run — the same overclaim, in the entry filed to be the honest
  ledger for it. Two independent reviewers caught it by running the metric
  the entry cites.

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

- Known limits to carry forward, all four disclosed in the leg's own
  docstring rather than closed. Recognition limits: a call reached
  through a variable holding a bound method, an I/O entry point whose
  name is not in `_FS_CALLS`, or I/O performed by a C extension.
  REACHABILITY limits, both found by round-8 reviewers and both latent
  today (no FAMILY script contains a `yield`, none has a module-level
  `try`): I/O deferred past its call site — a generator constructed
  inside a guarded `try` runs its body where it is CONSUMED, and the leg
  credits the guard at construction — and a `def` nested inside a
  module-level `try`, whose body inherits that guard's line range though
  the `try` only runs at definition time. Whoever widens this contract
  should decide whether to close the reachability pair or keep disclosing
  it; the cheap predicate for the first is "a scope containing
  `ast.Yield` can never be guarded by its call site". That limit is stated in the
  leg's own docstring; two review rounds caught earlier revisions
  claiming more than they delivered, so keep the claim sized to the
  mechanism when this is widened.
