# Changelog

All notable changes to the `skill-dev-toolkit` plugin are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] — 2026-07-13

### Changed — skill-creator-advance token refactor (equivalence-gated, first 0.2.0-machinery run)

- `skill-creator-advance/SKILL.md` 6,069 → 4,497 words (−25.9%), back under the
  4,500 CHK-SKL-010 cap. First real-world run of 0.2.0's taxonomy-guided
  candidate pre-pass (ranked 16 moves; estimates within ±20% of actuals) +
  the skill-refactor Q1/Q2/Q3 gate (4 test prompts, sonnet runners, 3-judge
  opus ensemble: P1/P3/P4 equivalent 3/3, P2 pass at moderate confidence —
  2 equivalent + 1 uncertain on a pre-existing doc ambiguity both versions
  carry, now BACKLOG'd).
- Extractions absorbed into existing references (no new files):
  `description-design.md` +479w (§Trigger eval query design, §triggering
  mechanism), `asking-user-questions.md` +328w (§Empty-Prompt Onboarding).
- User-approved sediment removals: §Description Best Practices → ~70w pointer
  (killed the items-6/7 contradiction with §House standard), "make
  descriptions a little 'pushy'" sentence deleted (contradicted the
  anti-over-trigger MUST).
- `test-prompts.json`: +P4 (description-optimization coverage, added
  pre-baseline so both gate sides ran identical prompts).

## [0.2.0] — 2026-07-13

### Added — Pocock compression-philosophy candidate-generation techniques

- `skill-refactor`'s `refactor-moves-catalog`: new **Leading-Word Substitution**
  move, gated by a mandatory weakest-tier equivalence guard.
- `skill-refactor`'s `ablation-mode`: a taxonomy-guided candidate pre-pass that
  ranks sections by bloat-taxonomy hits before the leave-one-out runs.
- `skill-creator-advance`: new `references/writing-lean.md` authoring reference,
  plus a net-negative pointer edit to its `SKILL.md` (6,085 → 6,069 words).

Rationale: [mattpocock/skills](https://github.com/mattpocock/skills)
`writing-great-skills` (MIT, © 2026 Matt Pocock — license verified in-session
against mattpocock/skills' own `LICENSE` file) contributes candidate-generation
techniques; `skill-refactor`'s existing equivalence gate verifies them — he
generates, our gate verifies.

## [0.1.0] — 2026-06-20

### Added — extracted from dev-workflow as a self-contained plugin

The skill-authoring lifecycle was extracted from `dev-workflow` into this
standalone, **zero-cross-plugin-dependency** plugin so it can be distributed on
its own. Skills: `skill-creator-advance`, `skill-judge`, `dogfood-skill-testing`,
`skill-refactor`, `skill-tuning`.

Self-sufficiency was achieved by **inlining** the worth-it / smallest-skill check
(previously delegated to dev-workflow's complexity-critique / proposal-critique gates,
which are general coding gates that stay in dev-workflow) and **genericizing**
documentation references (e.g. skill-judge's boundary notes vs domain-team
convention gates) — no `plugin:skill` reference to any other plugin remains.

Skill behavior is unchanged from their dev-workflow versions; only
dependency-severing edits + the `dev-workflow:` → `skill-dev-toolkit:` self-rename
were applied. The intra-set CI gates (description-standard grep guard;
skill-refactor↔skill-tuning shared-conventions drift) moved in with the skills.
