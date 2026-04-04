---
name: code-team
description: Code development with quality checkpoints. Agent controls execution; gates enforce quality.
---

# Code Team

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
| Security | Output contains code changes | `evaluator` + `skills/domain-code/checklists/security-checklist.md` |
| Architecture | Output changes public API or system structure | `evaluator` + `skills/domain-code/rubrics/arch-gate.md` |

### SHOULD Gates (auto-trigger, skippable with stated reason)

| Gate | Trigger | File |
|------|---------|------|
| Quality | Code changes span >3 files or introduce new module | `evaluator` + `skills/domain-code/rubrics/quality-gate.md` |

### MAY Gates (user-requested only)

| Gate | File |
|------|------|
| QA Verification | `skills/domain-code/rubrics/qa-gate.md` |
| Tech Debt Audit | `skills/domain-code/checklists/tech-debt-checklist.md` |

## Gate Protocol

For MUST and SHOULD gates, launch `evaluator` with:
- The gate file (checklist or rubric)
- Standards: `skills/domain-code/standards/code-conventions.md`
- The artifact to evaluate
- Original requirements

Handle verdict:
- **PASS** → gate cleared
- **PASS_WITH_NOTES** → auto-fix based on feedback → re-run from MUST gates
- **NEEDS_REVISION** → stop, present issues to user

Guard rails:
- Max 3 auto-revision rounds before escalating
- Run tests after each revision if test suite exists
- Each retry launches a fresh evaluator (no accumulated context)
- After fixing one gate's issues, re-check other triggered gates
- Use `context-compressor` if artifact is large before passing to evaluator

## Available Resources

Agent loads these as needed. No obligation to use all of them.

### Domain Knowledge (`skills/domain-code/`)

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
| `protocols/brainstorming.md` | Feature brainstorming & approach exploration |
| `protocols/refactoring.md` | Mechanical refactoring SOP |
| `protocols/codebase-assessment.md` | Health assessment SOP |
| `protocols/doc-writing.md` | Documentation SOP |
| `protocols/test-writing.md` | Test generation SOP |
| `checklists/security-checklist.md` | Security gate criteria |
| `checklists/tech-debt-checklist.md` | Tech debt gate criteria |
| `rubrics/arch-gate.md` | Architecture fitness flags |
| `rubrics/quality-gate.md` | Code quality flags |
| `rubrics/qa-gate.md` | Final QA flags |
| `standards/code-conventions.md` | Shared coding rules (SSOT) |

### Agents

| Agent | Role | Model |
|-------|------|-------|
| `worker` | Execute large tasks with protocol guidance | sonnet |
| `evaluator` | Run quality gates | opus |
| `context-compressor` | Compress context between phases | haiku |

### External Plugins

| Plugin | When useful |
|--------|------------|
| `feature-dev:code-architect` | Complex features needing detailed architecture planning |

## Recommended Flows

Suggested approaches, not mandates. Agent adapts based on task.

### New Feature / Significant Change
1. Load `brainstorming.md` → explore approaches
2. Optionally use `feature-dev:code-architect` for planning
3. Implement (main conversation or `worker`)
4. Run tests if suite exists
5. SELF check → MUST gates → SHOULD gates (if triggered)
6. Deliver

### Documentation
1. Load `doc-writing.md` protocol
2. Reference `code-conventions.md` for style
3. Write
4. SELF check
5. Deliver (no MUST/SHOULD gates trigger — no code changes)

### Refactoring
1. Load `refactoring.md` protocol
2. Implement → run tests
3. SELF check → MUST gates → SHOULD gates (if triggered)
4. Deliver

### Bug Fix
1. Investigate → fix → run tests
2. SELF check → MUST gates
3. Deliver

### Standalone Test Writing
1. Load `test-writing.md` protocol
2. Write tests → verify they pass
3. SELF check → MUST gates
4. Deliver

### Codebase Assessment
1. Load `codebase-assessment.md` protocol
2. Analyze
3. SELF check
4. Deliver (no code changes — no MUST gates trigger)

## Context Isolation

Each agent launch starts fresh. Pass only:
- To evaluator: gate file + standards + artifact + original requirements
- To worker: protocol + standards + task description + relevant input
Use `context-compressor` for large artifacts.

## Worker BLOCKED Handling

If a worker outputs `BLOCKED`:
- Do NOT proceed to gates
- Present BLOCKED reason to user
- Wait for user input
