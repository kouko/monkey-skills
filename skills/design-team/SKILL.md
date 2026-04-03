---
name: design-team
description: Execute the design review pipeline with accessibility checks and parallel quality gates. Requires using-design-team for task routing.
---

# Design Team

Semi-automatic Generate → Checklist → Review → Revise loop.
Uses hybrid evaluation: binary a11y checklist first, then qualitative flag gates in parallel.

## Language

Detect the user's language and pass it as `output_language` to all agent launch prompts.

## Step 1 — Generate (Protocol-Guided)

Load the appropriate protocol BEFORE generating any design output.
Route by task type:

| Task | Protocol to load |
|------|-----------------|
| Design brainstorming / concept | `skills/domain-design/protocols/design-brainstorming.md` |
| UX strategy / user journey | `skills/domain-design/protocols/ux-strategy.md` |
| Visual design / color / typography | `skills/domain-design/protocols/visual-design.md` |
| UI spec / wireframe / frontend code | `skills/domain-design/protocols/ui-interaction.md` |
| Full design (end-to-end) | `design-brainstorming.md` first, then task-specific protocol |

Worker reads the protocol, then generates design output
(strategy doc, UI spec, Object Map, or frontend code).
Worker should also reference `skills/domain-design/standards/wcag-baseline.md` during creation.

## Step 2a — A11y Checklist (binary gate, always runs for UI output)

Launch `evaluator` with:
- Checklist: Read `skills/domain-design/checklists/a11y-checklist.md`
- Standards: Read `skills/domain-design/standards/wcag-baseline.md`
- Artifact: design output from Step 1

- All `PASS` → proceed to Step 2b
- Any `FAIL` → `NEEDS_REVISION`, auto-fix → re-run Step 2a

## Step 2b — Qualitative Review (parallel flag gates)

Dispatch multiple `evaluator` instances in parallel by output type.
For each, read the corresponding rubric and include its content in the launch prompt.

- Strategy / journey / value proposition →
  `evaluator` + Read `skills/domain-design/rubrics/ux-strategy-gate.md`
- Wireframe / UI spec / Object Map / IA / frontend code →
  `evaluator` + Read `skills/domain-design/rubrics/ui-interaction-gate.md`
- Visual design (user-provided asset) →
  `evaluator` + Read `skills/domain-design/rubrics/visual-gate.md`
  Skip if: no visual asset provided (wireframe/text only)
- Full design → all three in parallel

Aggregate verdicts: worst verdict wins.

## Step 3 — Iterate based on verdict

- **PASS** → Done, report to user
- **PASS_WITH_NOTES** → Auto-revise based on evaluator feedback → go to Step 2a
- **NEEDS_REVISION** → Stop, present issues to user, await direction

## Context Isolation

Each evaluator launch starts fresh. Pass only:
- The checklist/rubric content (from the domain file)
- Standards content (from `standards/wcag-baseline.md`)
- The design artifact to evaluate
- The original requirements

Use `context-compressor` to compress large artifacts before passing between phases if needed.

## Auto-Revise Loop (Context-Clean Retry)

When a gate returns `PASS_WITH_NOTES` or a checklist returns `FAIL_FIXABLE`:

1. Use `context-compressor` to compress the current artifact + feedback into a brief
2. Revise in main conversation with ONLY: original requirements + current artifact + evaluator feedback
3. Discard all prior retry history from the evaluator's view
4. Re-run from Step 2a (a11y checklist first)

## Guard Rails

- Max 3 auto-revision rounds before escalating to user
- Visual design cannot be auto-generated — always require human input
- Only auto-revise issues evaluators flagged; do not introduce new changes
- Each retry launches fresh evaluator instances (no accumulated context)
