# Plan: bba proactive-trigger hardening across the loom family

Source brief: docs/loom/specs/2026-07-25-bba-proactive-trigger-hardening.md
Total tasks: 6
Critical-path depth: 1 (all tasks Independent, one wave)
Execution order: parallel-where-possible (6 disjoint plugins)
Plan-document-reviewer verdict: PASS (2026-07-25, round 2, 14/14)

## Canonical constant (copy VERBATIM into every carrier — do not paraphrase)

Trigger triple (from `loom-code/skills/brainstorming/SKILL.md:58`):
`≥3 trade-offs, ≥2 implementation paths, or architectural blast radius`

bba skill ID (reference by ID, never by path): `dev-workflow:brief-before-asking`

Imperative shape (action-moment, per
`docs/loom/memory/imperative-trigger-cards-beat-descriptive-preloads.md`):
"before you fire the ask / AskUserQuestion on a fork this complex →
run `dev-workflow:brief-before-asking` FIRST". Each carrier adapts the
sentence to its surrounding voice but MUST (a) name the skill ID, (b) carry
the triple verbatim, (c) bind to the pre-ask moment.

## Notes

- All 6 tasks touch disjoint plugins → all `Independent: true`, depth 1.
  Drift risk (each implementer writing the triple) is neutralized by the
  verbatim-copy constant above.
- **marketplace.json is NOT touched** (verified 2026-07-25): the root
  `.claude-plugin/marketplace.json` carries only name/description/source —
  **no version field** — and none of these 6 tasks changes a plugin-level
  description (Task 2 edits the bba *skill* description, not dev-workflow's
  marketplace entry). So version bumps + this work never write it. This is
  why the 6 tasks are genuinely file-disjoint and `Independent: true` holds
  (Check 14 fix vs round-1 plan, which wrongly listed marketplace.json).
- No new command surface: the new dev-workflow shell test is auto-globbed by
  the existing `for t in dev-workflow/tests/test-*.sh` CI loop; loom-code and
  the 4 design-side guards EXTEND existing test files. Nothing to declare.
- Version-bump LEVELS are a kickoff one-way-door decision (see kickoff): draft
  = loom-code MINOR + dev-workflow MINOR (both change firing behavior), 4
  design-side PATCH (additive one-line router reminder). Confirm before ship.
- Out of scope (from brief): family-reception shared-card surgery, compressed
  template, delivery-blemish fixes, live firing-harness A/B.
- Whole-branch verification (all 6 plugin suites + `loom-code/scripts/
  test_asking_user_briefing_escalation.py` + `loom-pipeline/scripts/
  test_family_relay.py` green) is finishing-a-development-branch's job, not a
  plan task.

## Task 1 — loom-code router-card proactive imperative
- Description: Add an imperative to `router-card.md` rule 5 that names
  `dev-workflow:brief-before-asking` and binds it to the pre-ask moment,
  carrying the trigger triple verbatim; extend the existing escalation guard
  to assert router-card is now a 4th carrier.
- Module: loom-code (SessionStart card + its guard)
- Files touched: loom-code/hooks/router-card.md,
  loom-code/scripts/test_asking_user_briefing_escalation.py,
  loom-code/.claude-plugin/plugin.json, loom-code/CHANGELOG.md
- Context paths:
  - loom-code/hooks/router-card.md (rule 5 at :13 — the generic paraphrase)
  - loom-code/scripts/test_asking_user_briefing_escalation.py (existing triple
    + "brief-before-asking" assertions across 3 skill bodies — add router-card)
  - loom-code/skills/brainstorming/SKILL.md:58 (canonical triple source)
- Acceptance:
  - RED: add a new assertion (e.g. `test_router_card_names_bba_with_triple`)
    to `test_asking_user_briefing_escalation.py` asserting `router-card.md`
    contains both `dev-workflow:brief-before-asking` and the triple verbatim →
    fails on current generic rule 5.
  - GREEN: rule 5 carries the imperative; the new assertion + all existing
    ones pass; loom-code version bumped + CHANGELOG entry added.
- External surfaces: none (internal prose + grep test).
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State #1 "Proactive imperative at
  session-start (loom-code) — router-card.md rule 5 gains an imperative
  naming dev-workflow:brief-before-asking, reusing the canonical trigger triple".

## Task 2 — dev-workflow bba description reactive-signal summary
- Description: Summarize the two omitted reactive signals (check-question
  guard + repeated-confusion meta-trigger) in the bba SKILL.md description
  line; add a shell guard test pinning them.
- Module: dev-workflow (bba skill description + shell test)
- Files touched: dev-workflow/skills/brief-before-asking/SKILL.md,
  dev-workflow/tests/test-bba-description.sh,
  dev-workflow/.claude-plugin/plugin.json, dev-workflow/CHANGELOG.md
- Context paths:
  - dev-workflow/skills/brief-before-asking/SKILL.md (description at :4;
    body signals at :79 repeated-confusion and :81-92 check-question)
  - dev-workflow/tests/ (existing test-*.sh pattern to mirror — grep-based,
    exit-nonzero on missing needle)
- Acceptance:
  - RED: new `dev-workflow/tests/test-bba-description.sh` greps the description
    for a check-question / repeated-confusion reactive-signal mention and
    exits non-zero if absent → fails on current description (names only
    question/explanation/stakes).
  - GREEN: description summarizes the two signals WITHOUT dropping existing
    reactive-clause wording; the shell test exits 0; dev-workflow version
    bumped + CHANGELOG entry added.
- External surfaces: none (bash grep test, no non-stdlib deps).
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State #2 "Reactive-signal summary in the
  description (dev-workflow) — description summarizes the check-question guard
  and the repeated-confusion meta-trigger it currently omits".

## Task 3 — loom-discovery router bba imperative
- Description: Add a one-line bba imperative to the using-loom-discovery
  router body (matching using-loom-pipeline:158 pattern); pin it in the
  existing entry-skill guard.
- Module: loom-discovery (entry router + its guard)
- Files touched: loom-discovery/skills/using-loom-discovery/SKILL.md,
  loom-discovery/scripts/test_using_skill.py,
  loom-discovery/.claude-plugin/plugin.json, loom-discovery/CHANGELOG.md
- Context paths:
  - loom-discovery/skills/using-loom-discovery/SKILL.md (router body)
  - loom-discovery/scripts/test_using_skill.py (grep it for
    `using-loom-discovery` router assertions; extend this file — it is the
    confirmed router guard — else add a sibling test in the same dir)
  - loom-pipeline/skills/using-loom-pipeline/SKILL.md:158 (pattern to mirror)
- Acceptance:
  - RED: add `test_using_router_names_bba` asserting the router names
    `dev-workflow:brief-before-asking` + the triple → fails (currently zero
    bba mention).
  - GREEN: router carries the imperative; assertion passes; loom-discovery
    version bumped + CHANGELOG entry added.
- External surfaces: none.
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State #3 "bba imperative in the 4
  design-side routers — loom-discovery using-* router gains a one-line bba
  imperative".

## Task 4 — loom-interface-design router bba imperative
- Description: Add a one-line bba imperative to the
  using-loom-interface-design router body; pin it in the guard that reads
  that router.
- Module: loom-interface-design (entry router + its guard)
- Files touched:
  loom-interface-design/skills/using-loom-interface-design/SKILL.md,
  loom-interface-design/scripts/test_entry_intake.py,
  loom-interface-design/.claude-plugin/plugin.json,
  loom-interface-design/CHANGELOG.md
- Context paths:
  - loom-interface-design/skills/using-loom-interface-design/SKILL.md
  - loom-interface-design/scripts/ — FIRST grep test_*.py for
    `using-loom-interface-design` to confirm the owning router guard
    (test_entry_intake.py is the likely owner; if a different file owns it,
    edit that one — else add a sibling test)
  - loom-pipeline/skills/using-loom-pipeline/SKILL.md:158
- Acceptance:
  - RED: add `test_using_router_names_bba` (in the confirmed owning guard file)
    asserting the router names `dev-workflow:brief-before-asking` + triple →
    fails.
  - GREEN: router carries the imperative; assertion passes; version bumped +
    CHANGELOG entry added.
- External surfaces: none.
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State #3 (loom-interface-design instance).

## Task 5 — loom-product-principles router bba imperative
- Description: Add a one-line bba imperative to the
  using-loom-product-principles router body; pin it in the entry-skill guard.
- Module: loom-product-principles (entry router + its guard)
- Files touched:
  loom-product-principles/skills/using-loom-product-principles/SKILL.md,
  loom-product-principles/scripts/test_principles_entry_skill.py,
  loom-product-principles/.claude-plugin/plugin.json,
  loom-product-principles/CHANGELOG.md
- Context paths:
  - loom-product-principles/skills/using-loom-product-principles/SKILL.md
  - loom-product-principles/scripts/test_principles_entry_skill.py (grep for
    the router assertions; extend this file — else add a sibling)
  - loom-pipeline/skills/using-loom-pipeline/SKILL.md:158
- Acceptance:
  - RED: add `test_entry_router_names_bba` asserting the router names
    `dev-workflow:brief-before-asking` + triple → fails.
  - GREEN: router carries the imperative; assertion passes; version bumped +
    CHANGELOG entry added.
- External surfaces: none.
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State #3 (loom-product-principles instance).

## Task 6 — loom-spec router bba imperative
- Description: Add a one-line bba imperative to the using-loom-spec router
  body; pin it in the entry-skill guard.
- Module: loom-spec (entry router + its guard)
- Files touched: loom-spec/skills/using-loom-spec/SKILL.md,
  loom-spec/scripts/test_spec_entry_skill.py,
  loom-spec/.claude-plugin/plugin.json, loom-spec/CHANGELOG.md
- Context paths:
  - loom-spec/skills/using-loom-spec/SKILL.md
  - loom-spec/scripts/test_spec_entry_skill.py (grep for router assertions;
    extend this file — else add a sibling)
  - loom-pipeline/skills/using-loom-pipeline/SKILL.md:158
- Acceptance:
  - RED: add `test_entry_router_names_bba` asserting the router names
    `dev-workflow:brief-before-asking` + triple → fails.
  - GREEN: router carries the imperative; assertion passes; version bumped +
    CHANGELOG entry added.
- External surfaces: none.
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State #3 (loom-spec instance).
