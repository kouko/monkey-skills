---
name: research-team
description: Conduct research with citation verification. Use when researching, analyzing, evaluating tech stacks, comparing libraries, checking OSS licenses, doing investment/market analysis, writing research summaries, or quick fact-checking. 研究・分析・技術評估・開源調查。調査・技術評価。
---

# Research Team

Agent-driven execution with four-level quality gates.

## When to Use

- Deep research and analysis
- Investment and macro analysis
- Market / competitive research
- Technology evaluation
- Research summaries from existing sources
- Quick fact-check / single-question lookup
- OSS license and compliance checks

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
| Source Citation | Output makes factual claims or cites sources | `evaluator` + `checklists/source-citation-checklist.md` |

### SHOULD Gates (auto-trigger, skippable with stated reason)

| Gate | Trigger | File |
|------|---------|------|
| Research Quality | Output is a deep research or analysis report | `evaluator` + `rubrics/research-quality-gate.md` |

### MAY Gates (user-requested only)

| Gate | File |
|------|------|
| OSS Due Diligence | `checklists/oss-due-diligence.md` |

## Gate Protocol

For MUST and SHOULD gates, launch `evaluator` with:
- The gate file (checklist or rubric)
- Standards: `standards/citation-standards.md`
  (also `standards/oss-safety.md` for OSS evaluation)
- The artifact to evaluate
- Original requirements

Handle verdict:
- **PASS** → gate cleared
- **PASS_WITH_NOTES** → fix based on feedback → re-run from MUST gates
  - Only use: original requirements + current artifact + feedback (no retry history)
  - Max 2 rounds before escalating
- **NEEDS_REVISION** → stop, present issues to user

Guard rails:
- Factual accuracy or data freshness issues → always NEEDS_REVISION
  (main conversation cannot verify facts without web search)
- Each retry launches a fresh evaluator (no accumulated context)
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

Files are named descriptively (e.g., `source-citation-checklist.md`, `market-analysis.md`).
Use Glob to discover available files if unsure which to load.
| `standards/oss-safety.md` | OSS licensing & production-readiness rules (SSOT) |

### Behavioral Rules

Knowledge access is open. Role boundaries are enforced by behavior:

- **worker / main agent**: Produces artifacts. Does NOT produce gate verdicts (PASS/FAIL/flags).
- **evaluator**: Produces verdicts. Does NOT modify artifacts or produce revised output.

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
