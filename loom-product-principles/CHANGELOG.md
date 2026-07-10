# Changelog

All notable changes to the `loom-product-principles` plugin (formerly `product-principles-toolkit`) are documented in this file.

Format: [Keep a Changelog](https://keepachangelog.com/).
Versioning: [Semantic Versioning](https://semver.org/).

> This file was reconstructed on 2026-07-02 from the git history — the plugin
> shipped its first two versions without a CHANGELOG.

## [0.5.1] — 2026-07-10

### Fixed

- **`§Headless/seeded mode` gains the seed-traceability invariant + a
  post-draft seed walk** (the headless mirror of the interactive coverage
  self-check): every seed item — each individual stance, named canon,
  tech-stack choice, or deferred marker, even when several share one
  bullet — must land in at least one of a carrying principle, an
  `## Anchors` row, an Open Question with a re-trigger, a
  `## Deviation Ledger` entry, or (for North-Star-bound facts) the
  `## North Star` section; out-of-jurisdiction seed content is noted, not
  silently skipped — no silent drops. Evidence: an n=4
  weak-model headless seeded replay of the construction flow
  (`docs/loom/dogfood/2026-07-10-principles-flow-cold-operator/seed.md`)
  showed the seed's deferred stance dropped 4/4, seed-named canons
  dropped from Anchors (Apple Design Language 0/4, Core ML 0/4,
  JTBD 1/4), and stance coverage compressed 7→4-5 — one root cause: the
  mode had no rule for seed content that is neither an answer nor a gap.
- Oracle calibration in the cold-operator dogfood seed: the 「恰 7 條」
  count assertion replaced with the coverage form (count is not the
  invariant — merging is legitimate); the C9 negative pattern narrowed
  to development-team-as-decision-actor phrasings.
- The invariant's Open Question landing spot now has a defined format
  home: `references/principles-rules.md` gains an optional
  `## Open Questions` section (ordered list, one physical line per entry,
  literal `— re-trigger:` marker stating when to revisit) plus validator
  contract rule 8, and `validate_principles_output.py` enforces it when
  present (absent stays valid).

### Verified

- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest loom-product-principles/scripts/ -q`
  → 169 passed (146 baseline + 23 seed-traceability pins/checks across
  two review rounds, RED-then-GREEN).

## [0.5.0] — 2026-07-10

### Added

- **Construction-flow rewrite of `product-principles` SKILL.md's elicitation
  core**: user-states-first → question-set probing → same-axis canon
  candidates (with considered-but-rejected recorded per round) → the user
  decides the mix or goes bespoke → version-pinned `## Anchors` +
  `## Deviation Ledger` + falsifiable principles → per-section and final
  read-backs. New `§Headless/seeded mode` covers unattended runs, including
  a thin-seed `BLOCKED` refusal and greppable `(agent-decided)` markers for
  choices made without a human in the loop.
- New reference files: `references/question-sets.md` and four canon base
  lists — `references/canon-product.md`, `references/canon-design-interaction.md`,
  `references/canon-design-visual.md`, `references/canon-engineering.md` —
  supplying the same-axis candidates the construction flow proposes.
- `references/principles-rules.md` gains `## Anchors` and `## Deviation
  Ledger` format rules (enforce-when-present) plus validator contract
  rules 6–7 describing how `validate_principles_output.py` checks them.
- `scripts/validate_principles_output.py`: enforce-when-present checks for
  both the `## Anchors` and `## Deviation Ledger` sections.

### Verified

- Cold-operator dogfood
  (`docs/loom/dogfood/2026-07-10-principles-flow-cold-operator/`): 4 PASS +
  1 PARTIAL; findings F1–F3 folded back into the construction flow (see
  the `fix(loom-product-principles)` commit above).
- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest loom-product-principles/scripts/ --collect-only -q`
  → 145 tests collected.

## [0.4.1] — 2026-07-07

### Changed

- **`using-loom-product-principles` §Intake points at the family relay
  discipline**: the entry skill's intake now cites
  `loom-pipeline/hooks/family-relay.md` as the shared reference for
  how it talks to the user, rather than restating relay rules locally.
  Verification: `test_family_relay.py::test_design_side_pointers[product-principles]`
  passed.

## [0.4.0] — 2026-07-04

### Added

- **New `using-loom-product-principles` entry skill**: a thin family-entry
  router (§Intake — 前站檢查 / 對站檢查 / handoff to `product-principles`)
  for users who aren't sure where to start. Its description is
  entry-framed and deliberately avoids `product-principles`' own
  direct-ask triggers (產品原則 / north star / 憲章) so the entry never
  steals the member's direct pull (#456 positive-specificity).
- `product-principles` SKILL.md gains a **Next station** close-out line:
  once `PRINCIPLES.md` is shipped, hand off to `using-loom-interface-design`
  for UI-bearing products, or to `using-loom-spec` to expand a feature
  directly for headless / CLI-only products.

Both changes are part of the loom-family connective-tissue pass wiring the
`using-loom-*` entry-skill convention across the pipeline.

## [0.3.0] — 2026-07-03

### Changed

- **Three-jurisdiction sections**: the required section renamed
  `## Principles` → `## Product Principles` (legacy `## Principles` files
  are detected and migrated with a one-line message, not silently
  rejected). Two new optional sections, `## Design Principles` and
  `## Engineering Principles`, each 1–7 falsifiable principles and never
  emitted empty — jurisdiction-appropriate content is elicited only when
  the product warrants it. `references/principles-rules.md` gained the
  Jurisdictions table and the posture-elicitation steps (does this product
  need a Design jurisdiction? an Engineering jurisdiction?) that decide
  whether each optional section is generated.
- Unqualified "product-level" claims in `SKILL.md` / `principles-rules.md`
  / `README.md` widened to project-constitution framing; the `## Product
  Principles` jurisdiction itself is unchanged in scope (product design
  principles + target user, not business/market/strategy).

- §Downstream updated to reflect the wired reality: named per-station intake
  sections (design generators, `loom-spec:spec-expansion` §Governing
  constraint, both critics' principles lenses) and the **live** loom-code
  `code-reviewer` D8 principles-conformance gate — replacing the stale "a
  future conformance gate may check artifacts" forward-reference.

### Fixed

- Skill description restored to the proactive, trilingual-trigger form: fires
  BEFORE design/spec/build (not only when asked), carries 產品原則 / 產品憲章 /
  プロダクト指針 triggers and the "north star" phrasing the test suite encodes,
  and states a when-NOT boundary. #456's rewrite had dropped the CJK triggers
  and made the description reactive-only, silently breaking 2 tests (no CI ran
  them) and likely re-opening the pre-#456 under-firing this plugin was known
  for.

- `product-principles` SKILL.md now states the correct skill-dir-relative
  validator path (`../../scripts/validate_principles_output.py`); the
  previously claimed `scripts/…` form did not resolve from the skill directory
  in an installed plugin.
- Earlier unversioned post-0.2.0 changes: trigger-description rewrite (#456),
  reply-honesty prose fixes (#465).

## [0.2.0] — 2026-06-21

### Changed

- **BREAKING**: plugin renamed `product-principles-toolkit` →
  `loom-product-principles`; artifact path unified to
  `docs/loom/PRINCIPLES.md` (#440).

## [0.1.0] — 2026-06-14

### Added

- MVP: `product-principles` skill — turn a sparse product idea into a
  `PRINCIPLES.md` constitution (north-star + 3–7 falsifiable principles) —
  plus `validate_principles_output.py` structure validator (#398).
