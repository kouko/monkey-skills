---
name: research-team
description: Research with quality checkpoints. Agent controls execution; gates enforce citation and analysis quality.
---

# Research Team

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
| Source Citation | Output makes factual claims or cites sources | `evaluator` + `skills/domain-research/checklists/source-citation-checklist.md` |

### SHOULD Gates (auto-trigger, skippable with stated reason)

| Gate | Trigger | File |
|------|---------|------|
| Research Quality | Output is a deep research or analysis report | `evaluator` + `skills/domain-research/rubrics/research-quality-gate.md` |

### MAY Gates (user-requested only)

| Gate | File |
|------|------|
| OSS Due Diligence | `skills/domain-research/checklists/oss-due-diligence.md` |

## Gate Protocol

For MUST and SHOULD gates, launch `evaluator` with:
- The gate file (checklist or rubric)
- Standards: `skills/domain-research/standards/citation-standards.md`
  (also `skills/domain-research/standards/oss-safety.md` for OSS evaluation)
- The artifact to evaluate
- Original requirements

Handle verdict:
- **PASS** → gate cleared
- **PASS_WITH_NOTES** → auto-fix based on feedback → re-run from MUST gate
- **NEEDS_REVISION** → stop, present issues to user

Guard rails:
- Max 2 auto-edit rounds before escalating
- Factual accuracy or data freshness issues → always NEEDS_REVISION
  (main conversation cannot verify facts without web search)
- Each retry launches a fresh evaluator (no accumulated context)
- Use `context-compressor` if artifact is large before passing to evaluator

## Available Resources

Agent loads these as needed. No obligation to use all of them.

### Domain Knowledge (`skills/domain-research/`)

All files are available to any agent as reference.

| Directory | Content | Typical Use |
|-----------|---------|-------------|
| `protocols/` | Research methodology SOPs | Execution guidance |
| `checklists/` | Binary pass/fail criteria | Gate evaluation, preventive self-check |
| `rubrics/` | Qualitative flag criteria | Gate evaluation, preventive self-check |
| `standards/` | Baseline rules (SSOT) | Universal reference |

Files:
| File | Content |
|------|---------|
| `protocols/research.md` | General research methodology SOP (fallback) |
| `protocols/market-analysis.md` | Market & industry analysis SOP |
| `protocols/competitive-analysis.md` | Competitive & competitor analysis SOP |
| `protocols/academic-research.md` | Academic & theoretical research SOP |
| `protocols/investment.md` | Investment & macro analysis framework |
| `protocols/stack-evaluation.md` | Tech stack & OSS evaluation SOP |
| `checklists/source-citation-checklist.md` | Citation gate criteria |
| `checklists/oss-due-diligence.md` | OSS compliance gate criteria |
| `rubrics/research-quality-gate.md` | Research quality flags |
| `standards/citation-standards.md` | Shared citation & output rules (SSOT) |
| `standards/oss-safety.md` | OSS licensing & production-readiness rules (SSOT) |

### Agents

| Agent | Role | Model |
|-------|------|-------|
| `worker` | Execute research tasks with protocol guidance | sonnet |
| `evaluator` | Run quality gates | opus |
| `context-compressor` | Compress context between phases | haiku |

## Recommended Flows

Suggested approaches, not mandates. Agent adapts based on task.

### Deep Research / Analysis
1. Load matching protocol (research, market, competitive, academic, investment, or stack)
2. Dispatch `worker` with protocol + standards
3. SELF check → MUST gate (Citation) → SHOULD gate (Quality)
4. Deliver

### Quick Lookup / Fact-Check
1. Search and answer directly
2. SELF check
3. Deliver (no formal citations → no MUST gate trigger)

### Research Summary (from existing sources)
1. Load relevant protocol
2. Write summary in main conversation
3. SELF check → MUST gate (Citation, if sources cited)
4. Deliver

### Tech Stack / OSS Evaluation
1. Load `stack-evaluation.md` protocol
2. Dispatch `worker` with protocol + `citation-standards.md` + `oss-safety.md`
3. SELF check → MUST gate (Citation) → SHOULD gate (Quality)
4. Optionally run OSS Due Diligence (MAY gate)
5. Deliver

## Context Isolation

Each agent launch starts fresh. Pass only:
- To evaluator: gate file + standards + artifact + original requirements
- To worker: protocol + standards + research question + context
Use `context-compressor` for large artifacts.

## Worker BLOCKED Handling

If a worker outputs `BLOCKED` (e.g., no sources found, contradictory requirements):
- Do NOT proceed to gates
- Present BLOCKED reason to user
- Wait for user input
