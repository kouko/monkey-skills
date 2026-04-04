---
name: design-team
description: Design with quality checkpoints. Agent controls execution; gates enforce accessibility and design quality.
---

# Design Team

Agent-driven execution with four-level quality gates.

## Language

Detect the user's language and pass it as `output_language` to all agent launch prompts.

## Quality Gates

### SELF Check (every delivery)

Before delivering output, verify your own work:
1. Re-read the user's original request
2. List 3-5 things that would make this output unacceptable
3. Check each one against your output
4. Fix any issues found before delivering

You may reference any domain file (rubrics, checklists, standards) during self-check.

### MUST Gates (auto-trigger, non-skippable)

| Gate | Trigger | File |
|------|---------|------|
| Accessibility | Output contains UI elements (wireframe, spec, frontend code) | `evaluator` + `skills/domain-design/checklists/a11y-checklist.md` |

### SHOULD Gates (auto-trigger, skippable with stated reason)

| Gate | Trigger | File |
|------|---------|------|
| UX Strategy | Output contains UX strategy or user journey | `evaluator` + `skills/domain-design/rubrics/ux-strategy-gate.md` |
| UI Interaction | Output contains wireframe / UI spec / frontend code | `evaluator` + `skills/domain-design/rubrics/ui-interaction-gate.md` |

### MAY Gates (user-requested only)

| Gate | File |
|------|------|
| Visual Design | `skills/domain-design/rubrics/visual-gate.md` |

## Gate Protocol

For MUST and SHOULD gates, launch `evaluator` with:
- The gate file (checklist or rubric)
- Standards: `skills/domain-design/standards/wcag-baseline.md`
- The artifact to evaluate
- Original requirements

When multiple SHOULD gates trigger, run them in parallel. Aggregate verdicts: worst verdict wins.

Handle verdict:
- **PASS** → gate cleared
- **PASS_WITH_NOTES** → auto-fix based on feedback → re-run from MUST gate
- **NEEDS_REVISION** → stop, present issues to user

Guard rails:
- Max 3 auto-revision rounds before escalating
- Visual design cannot be auto-generated — always require human input
- Only auto-revise issues evaluators flagged; do not introduce new changes
- Each retry launches fresh evaluator instances (no accumulated context)
- Use `context-compressor` if artifact is large before passing to evaluator

## Available Resources

Agent loads these as needed. No obligation to use all of them.

### Domain Knowledge (`skills/domain-design/`)

All files are available to any agent as reference.

| Directory | Content | Typical Use |
|-----------|---------|-------------|
| `protocols/` | Step-by-step SOPs | Execution guidance |
| `checklists/` | Binary pass/fail criteria | Gate evaluation, preventive self-check |
| `rubrics/` | Qualitative flag criteria | Gate evaluation, preventive self-check |
| `standards/` | Baseline rules (SSOT) | Universal reference |

Files:
| File | Content |
|------|---------|
| `protocols/design-brainstorming.md` | Integrated design thinking (Kansei x Meaning x Affordance) |
| `protocols/ux-strategy.md` | UX strategy creation (Ando temporal model x Garrett) |
| `protocols/visual-design.md` | Visual design (Kansei Engineering) |
| `protocols/ui-interaction.md` | UI & interaction design (Without Thought x OOUI) |
| `checklists/a11y-checklist.md` | Accessibility gate criteria |
| `rubrics/ux-strategy-gate.md` | UX strategy flags (Ando temporal model) |
| `rubrics/ui-interaction-gate.md` | UI structure & interaction flags |
| `rubrics/visual-gate.md` | Visual design flags (Kansei) |
| `standards/wcag-baseline.md` | Shared WCAG 2.2 AA rules (SSOT) |

### Agents

| Agent | Role | Model |
|-------|------|-------|
| `evaluator` | Run quality gates | opus |
| `context-compressor` | Compress context between phases | haiku |

## Context Isolation

Each agent launch starts fresh. Pass only:
- To evaluator: gate file + standards + artifact + original requirements
Use `context-compressor` for large artifacts.

## Recommended Flows

Suggested approaches, not mandates. Agent adapts based on task.

### Full Design (end-to-end)
1. Load `design-brainstorming.md` → explore concepts
2. Load task-specific protocol (UX, UI, or visual)
3. Generate design output
4. SELF check → MUST gates → SHOULD gates (if triggered)
5. Deliver

### UX Strategy / User Journey
1. Load `ux-strategy.md` protocol
2. Generate strategy doc
3. SELF check → SHOULD gate (UX Strategy)
4. Deliver

### UI Spec / Wireframe / Frontend Code
1. Load `ui-interaction.md` protocol
2. Reference `wcag-baseline.md`
3. Generate UI output
4. SELF check → MUST gate (A11y) → SHOULD gate (UI Interaction)
5. Deliver

### Design Documentation (style guide, pattern library)
1. Load relevant protocol for reference
2. Write documentation
3. SELF check
4. Deliver (no MUST gates trigger if no UI elements produced)

### Minor Update to Existing Design Spec
1. Make changes directly
2. SELF check
3. Deliver
