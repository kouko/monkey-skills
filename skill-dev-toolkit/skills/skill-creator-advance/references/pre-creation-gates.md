# Pre-Creation Gates Reference

Purpose: Extracted from SKILL.md for token efficiency. The main skill file keeps only routing pointers; this reference holds the full protocol.

---

## Do NOT Load Guards

**SKILL.md embedding instructions include explicit guards at these points:**

- **After Step 0 (Evaluation-First)**: Do NOT load this reference if you selected the quick eval path
- **Before Capture Intent section**: Load only when starting a full skill creation workflow

---

## Phase 1/3: Initial Validation

Before intake / interview / drafting, run two lightweight gates against the user's request — one or two focused questions each; they prevent shipping a skill that should not have been built.

### Gate 1 — Worth-it check

Applicable when the user proposes ≥2 skills at once, or one skill with multiple supporting claims ("we need this because A, B, and C"). Triage each proposed item into KEEP / DEFER / DROP, judging it on evidence grounding (is the need real and recurring, not speculative?) and YAGNI (would you build it now?).

A single skill with a single load-bearing reason keeps this gate cheap — confirm the reason holds, then move to Gate 2.

### Gate 2 — Smallest-end-state check

Applicable to **every** new skill proposal, single or multi. The three questions:

1. What's the smallest end state that solves this? (Could it be 0 functions — not really a skill, just a one-off prompt? One existing skill plus a new section instead of a new skill?)
2. Does this result in less total skill-ecosystem code than not building it? (A new skill adds surface area; default "no" unless it subtracts other artifacts or replaces ad-hoc prompts.)
3. What does this skill make obsolete? (If nothing, the rationale is purely additive — apply deletion-first skepticism as for any feature add.)

Skip explicitly if the user has already done the equivalent analysis ("we discussed this last week and concluded we need a dedicated skill"). Do NOT skip just to move faster — the cost of building the wrong skill is permanent.

If a gate verdict is DROP / REJECT / RESHAPE, surface it and ask the user how to proceed (drop, defer, or reshape smaller) before continuing to intake.

### Gate 3 — User-input check (after intake, before drafting)

Does this skill have any user-input branching? If yes, plan to apply the hardened `AskUserQuestion` pattern from `references/asking-user-questions.md` when drafting the relevant STEP — without it, the skill is highly likely to inline-fallback or silently default in production. If no user input is needed, this gate is N/A.