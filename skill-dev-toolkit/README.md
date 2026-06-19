# skill-dev-toolkit

A **self-contained** toolkit for authoring Claude Agent Skills end-to-end. Zero
cross-plugin dependencies — install it alone and it works.

Extracted from `dev-workflow` (2026-06-20) so the skill-authoring lifecycle can be
distributed independently of dev-workflow's session/git/critique tools.

## Skills (the lifecycle)

| Skill | Role |
|---|---|
| `skill-creator-advance` | Create new skills, do major redesigns, run eval-driven development, optimize a description's triggering. |
| `skill-judge` | Score a skill's design quality on an 8-dimension rubric (0–120 + grade). |
| `dogfood-skill-testing` | Blind behavioral test of a drafted SKILL.md — does it fire when expected, does its workflow meet its contract. |
| `skill-refactor` | Token / structure refactor of a skill, preserving output behavior. |
| `skill-tuning` | Output-quality A/B for a skill — human-judged variant selection. |

Typical flow: **create** (`skill-creator-advance`) → **score** (`skill-judge`) /
**behavioral-test** (`dogfood-skill-testing`) → **refactor** (`skill-refactor`) /
**tune output** (`skill-tuning`).

## Self-contained

These skills carry their own worth-it / smallest-skill checks inline rather than
delegating to other plugins, so the toolkit has **no `plugin:skill` references to
other plugins**. (Generic code-change critique — `complexity-critique` /
`proposal-critique` — and session-log mining — `distill-sessions` — remain in
`dev-workflow`, which this toolkit does not depend on.)

## License

MIT — see repository root `LICENSE`.
