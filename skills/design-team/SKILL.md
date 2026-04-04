---
name: design-team
description: Design with accessibility and quality review. Use when designing UI, creating wireframes, planning UX strategy, auditing accessibility, reviewing visual design, implementing frontend, or writing design documentation. UI設計・UXレビュー・アクセシビリティ。介面設計・無障礙審查。
---

# Design Team

Agent-driven execution with four-level quality gates.

## When to Use

- Design brainstorming and concept development
- UI design and wireframes
- UX strategy and user journeys
- Visual design creation and specification
- Frontend implementation review
- Accessibility audits and reports
- Design documentation (style guides, pattern libraries)
- Design review and feedback

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
| Accessibility | Output contains UI elements (wireframe, spec, frontend code) | `evaluator` + `checklists/a11y-checklist.md` |

### SHOULD Gates (auto-trigger, skippable with stated reason)

| Gate | Trigger | File |
|------|---------|------|
| UX Strategy | Output contains UX strategy or user journey | `evaluator` + `rubrics/ux-strategy-gate.md` |
| UI Interaction | Output contains wireframe / UI spec / frontend code | `evaluator` + `rubrics/ui-interaction-gate.md` |

### MAY Gates (user-requested only)

| Gate | File |
|------|------|
| Visual Design | `rubrics/visual-gate.md` |

## Gate Protocol

For MUST and SHOULD gates, launch `evaluator` with:
- The gate file (checklist or rubric)
- Standards: `standards/wcag-baseline.md`
- The artifact to evaluate
- Original requirements

When multiple SHOULD gates trigger, run them in parallel. Aggregate verdicts: worst verdict wins.

Handle verdict:
- **PASS** → gate cleared
- **PASS_WITH_NOTES** → fix based on feedback → re-run from MUST gates
  - Only use: original requirements + current artifact + feedback (no retry history)
  - Max 3 rounds before escalating
- **NEEDS_REVISION** → stop, present issues to user

Guard rails:
- Visual design cannot be auto-generated — always require human input
- Only auto-revise issues evaluators flagged; do not introduce new changes
- Each retry launches fresh evaluator instances (no accumulated context)
- Use `context-compressor` if artifact is large before passing to evaluator

## Available Resources

Agent loads these as needed. No obligation to use all of them.

### Domain Knowledge

All files in this skill directory are available to any agent as reference.
Organized by subdirectory convention:

| Directory | Load when | Contains |
|-----------|-----------|----------|
| `protocols/` | Starting a task — pick the matching SOP by filename | Execution SOPs |
| `checklists/` | Running MUST gates | Binary pass/fail criteria |
| `rubrics/` | Running MUST/SHOULD gates | Qualitative flag criteria |
| `standards/` | Always available as reference | Baseline rules (SSOT) |

Files are named descriptively (e.g., `a11y-checklist.md`, `ux-strategy.md`).
Use Glob to discover available files if unsure which to load.

### Behavioral Rules

Knowledge access is open. Role boundaries are enforced by behavior:

- **worker / main agent**: Produces artifacts. Does NOT produce gate verdicts (PASS/FAIL/flags).
- **evaluator**: Produces verdicts. Does NOT modify artifacts or produce revised output.

### Agents

| Agent | Role | Model |
|-------|------|-------|
| `evaluator` | Run quality gates | opus |
| `context-compressor` | Compress context between phases | haiku |

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

## Cross-Domain Awareness

Lightweight cross-domain tasks can be handled directly without switching skills:
- Quick reference lookup for design standards or patterns
- Reading code to understand existing UI implementation
- Brief competitive analysis of design approaches

Switch to specialized team when quality gates for that domain are needed:
- `planning-team`: cross-domain product spec or scope definition
- `code-team`: any code implementation, tech spec writing, refactoring, bug fixes,
  or any task where security/architecture quality gates are needed
- `research-team`: deep analysis, multi-source investigation, tech evaluation,
  or any task where citation verification matters

## Context Isolation

Each agent launch starts fresh. Pass only:
- To evaluator: gate file + standards + artifact + original requirements
Use `context-compressor` for large artifacts.
