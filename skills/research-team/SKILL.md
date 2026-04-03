---
name: research-team
description: Execute the research pipeline with citation checking and quality evaluation gates. Requires using-research-team for task routing.
---

# Research Team

Generate → Checklist → Quality Gate → Edit loop.
Uses hybrid evaluation: binary citation checklist first, then qualitative flag gate.

## Language

Detect the user's language and pass it as `output_language` to all agent launch prompts.

## Step 1 — Generate (Protocol-Guided)

Load the appropriate protocol BEFORE generating research output. Route by task type:

| Task | Protocol to load |
|------|-----------------|
| General research / analysis | `skills/domain-research/protocols/research.md` |
| Market / industry analysis | `skills/domain-research/protocols/market-analysis.md` |
| Competitive / competitor analysis | `skills/domain-research/protocols/competitive-analysis.md` |
| Academic / theoretical research | `skills/domain-research/protocols/academic-research.md` |
| Investment / stock / macro | `skills/domain-research/protocols/investment.md` |
| Tech stack / library / OSS evaluation | `skills/domain-research/protocols/stack-evaluation.md` |

Launch `worker` with:
- Protocol: the matched protocol from the table above
- Standards: Read `skills/domain-research/standards/citation-standards.md`
  (also `skills/domain-research/standards/oss-safety.md` for OSS evaluation)
- Input: research question + context

Include protocol and standards content in the worker's launch prompt.

## Step 2a — Source Citation Checklist (binary gate)

Launch `evaluator` with:
- Checklist: Read `skills/domain-research/checklists/source-citation-checklist.md`
- Standards: Read `skills/domain-research/standards/citation-standards.md`
- Artifact: research draft from Step 1

- All `PASS` → proceed to Step 2b
- Any `FAIL` → `NEEDS_REVISION`, re-dispatch worker with specific fix instructions

## Step 2b — Research Quality Gate (flag gate)

Launch `evaluator` with:
- Rubric: Read `skills/domain-research/rubrics/research-quality-gate.md`
- Standards: Read `skills/domain-research/standards/citation-standards.md`
- Artifact: research draft from Step 1

## Step 3 — Iterate based on verdict

- **PASS** → Done, deliver to user
- **PASS_WITH_NOTES** → Main conversation edits based on feedback
  (formatting, clarity, structure only) → re-run Step 2b
- **NEEDS_REVISION** → Stop, present issues to user
  (user may choose to re-dispatch worker with feedback)

## Context Isolation

Each agent launch starts fresh. Pass only:
- To worker: the protocol + standards + research question (no prior conversation history)
- To evaluator: the checklist/rubric + standards + research draft + original requirements

Use `context-compressor` to compress large artifacts before passing between phases if needed.

## Auto-Revise Loop (Context-Clean Retry)

When a gate returns `PASS_WITH_NOTES` or a checklist returns `FAIL_FIXABLE`:

1. Use `context-compressor` to compress the current draft + feedback into a brief
2. Launch a **fresh** worker with ONLY: original question + current draft + evaluator feedback
3. Discard all prior retry history — the new worker should NOT see previous failed drafts
4. Re-run from Step 2a (citation checklist first)

## Worker BLOCKED Handling

If a worker outputs `BLOCKED` status (e.g., no sources found, contradictory requirements):
- Do NOT proceed to evaluation gates
- Present the BLOCKED reason and suggested next steps to the user
- Wait for user input before re-dispatching

## Guard Rails

- Max 2 auto-edit rounds before escalating to user
- Main conversation edits only what evaluator flagged
- Factual accuracy or data freshness issues → always NEEDS_REVISION
  (main conversation cannot verify facts without web search)
- Each retry launches a fresh agent (no accumulated context from failed attempts)
