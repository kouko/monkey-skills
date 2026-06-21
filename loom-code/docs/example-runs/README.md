# example-runs

> Preserved test evidence from `loom-code` skill ritual runs (per ROADMAP §Cross-cutting concerns / TC-1 hybrid testing cadence).

These are real outputs from skills under live session pressure tests. They are NOT plans / briefs to execute against this repo. The absolute paths in the documents reference hypothetical project repos used during testing, not the monkey-skills worktree itself.

## Index

| File | Skill tested | Test prompt | Verdict |
|---|---|---|---|
| `2026-05-16-writing-plans-stress-test-plan.md` | `writing-plans` | `tests/writing-plans-pressure/prompts/too-big-no-split.txt` (Stripe payment system, user asks for 12-task plan) | ✅ PASS — agent refused single >5-task plan, split into 4 sequential Parts, wrote Part 1 with 5 atomic tasks, self-dispatched `plan-document-reviewer` subagent (12/12 checks), pre-emptively named Beck Child Test child-split for the at-risk Task 4 |

## Why preserve these

The hybrid testing cadence (ROADMAP TC-1) does not yet have an automated harness. Live session evidence is the only way to ground claims like *"writing-plans HARD-GATE actually refuses 12-task plans"*. These artifacts let a future maintainer reading SKILL.md confirm *"this isn't aspirational design, this is what the skill actually does in a fresh session."*

When the eval harness ships in Phase 1.5+ / 3.5, these may be reformulated as fixture inputs / expected outputs.
