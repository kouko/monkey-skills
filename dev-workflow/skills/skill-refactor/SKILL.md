---
name: skill-refactor
description: >-
  Token / structure refactor for an existing skill, **preserving
  output behavior**. Three checks per round: output equivalence
  (multi-judge ensemble + structured comparison), token reduction
  (≥10% threshold), invariant preservation (frontmatter / dependencies
  / contract). Emits PROCEED / RESHAPE / REJECT verdict with git
  ratchet (auto-revert if score drops or equivalence fails). Use when
  the user wants to shrink a skill's SKILL.md, tidy structure, dedupe
  prose, or optimize token cost without changing what the skill does.
  Triggers: shorten skill / reduce tokens / 縮減 SKILL.md / 整理結構
  / refactor skill / behavior unchanged / 保留行為的前提下 / リファクタ
  with output preservation. Do NOT use for output quality A/B (use
  dev-workflow:skill-tuning), structural redesign / phase changes
  (use dev-workflow:skill-creator-advance), creating a new skill (use
  dev-workflow:skill-creator-advance), or single-line cosmetic edits
  (just edit directly). スキル refactor・トークン削減・等価保証。
  技能精簡・Token 縮減・行為保留。
---

# Skill Refactor

A user-invoked gate skill: forces any proposed refactor of an
existing skill — token reduction, structure cleanup, dedupe, prose
tightening — through a deletion-first design pass with **automated
output equivalence verification** before the change is committed.

## Overview

Skills accumulate tokens. SKILL.md files grow over rounds of
edits. Most edits are additive — fixing a corner case here, adding
an example there. The result: skills that take more tokens to load
than they need to, with output behavior that's the same as before
(or worse, since longer prompts can degrade focus).

**This skill is the refactor hat applied to skills**: improve
internal structure without changing external behavior. Output
equivalence is enforced by a multi-judge ensemble + structured
comparison; behavior changes are out of scope (route to
`dev-workflow:skill-tuning` for output quality work or
`dev-workflow:skill-creator-advance` for structural redesign).

This skill is **runtime self-contained** — `dev-workflow` is the
only plugin needed. No cross-plugin dependency.

## The Iron Law

```
NO REFACTOR SHIPS WITHOUT (1) EQUIVALENCE PROVEN
                          (2) TOKEN REDUCTION ≥10%
                          (3) INVARIANTS PRESERVED
```

If any of three fails, the round is rolled back via `git revert`.
This is the ratchet — only refactors that **measurably preserve
behavior while measurably shrinking the file** survive.

## Before You Begin — Establish Baseline

Before proposing any refactor, the target skill needs:

1. **`test-prompts.json`** — at least 3 representative prompts that
   cover the skill's documented use cases. Schema:
   `references/test-prompts-schema.md`. If the skill doesn't have
   one, create it (with user confirmation) before any refactor.
2. **A baseline run** — execute each test prompt against the
   *current* SKILL.md via subagent; capture outputs to
   `<workspace>/baseline/`. This is what "equivalence" is checked
   against.
3. **Baseline token count** — `wc -w` of the current SKILL.md. Used
   for Q2's threshold check.
4. **Invariant snapshot** — record current frontmatter `name`,
   non-description fields, declared dependencies, file structure
   (subdirectories, key bundled files). This is what Q3 protects.

**Do not propose Q1's refactor moves until baseline is captured.**

If any of (1)-(4) cannot be obtained (e.g., skill has no
deterministic test prompts because output is purely creative), the
gate cannot run safely. Report the blocker to the user and suggest
`dev-workflow:skill-tuning` if the underlying intent was quality
improvement, or manual edit if only cosmetic.

## The Gate Function (per round)

Each refactor round runs three independent checks against the
candidate (post-edit) SKILL.md.

### Q1. Output equivalence (multi-judge ensemble)

For each test prompt:
- Run candidate SKILL.md via subagent → capture output
- Compare to baseline output via:
  - **Structural check** (cheap, deterministic): same key sections /
    headings / file paths / tool calls present
  - **LLM-judge ensemble** (3 independent calls with varied prompt
    framing, see `references/multi-judge-ensemble.md`): is the
    semantic content equivalent?

**Pass rule**: structural OK *and* ≥2 of 3 ensemble judges report
equivalent. Disagreement among judges → flag as **uncertain** →
auto-escalate to human Tier 2 (do not auto-keep).

**Pass = output is functionally the same as before.** This is the
load-bearing guarantee of refactor work.

### Q2. Token reduction ≥10%

`wc -w` on candidate SKILL.md compared to baseline:

| Reduction | Verdict |
|---|---|
| ≥10% reduction | OK |
| 5–10% reduction | OK only if Q1 + Q3 also strictly pass; weak win |
| <5% reduction (or no reduction) | **REJECT** — refactor cost not worth it |
| **Increase** | **REJECT** — this isn't a refactor; route elsewhere |

The 10% threshold prevents cosmetic micro-edits from accumulating
ratchet credit. Each refactor round must be a real win.

### Q3. Invariant preservation

Compare candidate against the snapshot captured in §Before You
Begin:

| Invariant | Allowed change |
|---|---|
| `name` (frontmatter) | Never change |
| `description` (frontmatter) | Allowed; this is often the target of token reduction |
| Other frontmatter fields (e.g., `compatibility`) | Never change |
| Declared dependencies (scripts called, references referenced) | Never change without going to skill-creator-advance |
| Subdirectory structure (`agents/`, `references/`, `scripts/`) | Allowed to add files (e.g. extract content); never to remove without skill-creator-advance |
| Bundled file *contents* | Allowed (refactor cascades) but each cascade is its own round |

**Pass rule**: all "never change" items unchanged; "allowed" items
verified to still serve the skill's documented behavior.

## Verdict

After Q1, Q2, Q3:

- **PROCEED** — all three pass strictly. `git commit` the candidate;
  ratchet advances.
- **RESHAPE** — Q1 or Q3 passes, Q2 marginal (5–10% reduction). Show
  user the candidate + which dimension is weak; user decides keep
  or further-refactor. Do not auto-merge.
- **REJECT** — Q1 fails (output not equivalent), or Q2 shows
  increase / no reduction, or Q3 violated. `git revert` the
  candidate; record the failed move in `results.tsv`; move to next
  round (or skill, if this skill has hit its bound).

## Ablation mode — find bloat without a baseline

The Gate Function proves a *rewrite* preserves behavior. **Ablation mode** answers
a different question with the same infra — *which sections add words without adding
capability* — and needs **no external baseline** (the skill is its own control; you
don't need an ancestor or sibling to compare against).

**Procedure** (reuses `test-prompts.json` + the Q1 judge ensemble):

1. Run the test prompts through the FULL skill → baseline outputs.
2. For each section, generate a variant with **that one section removed**; re-run the prompts.
3. Judge ensemble compares full-vs-ablated per section:
   - behavior **unchanged** on removal → **BLOAT candidate** (compress / cut);
   - behavior **degraded** (weaker refusal, dropped step, wrong decision) → **LOAD-BEARING** (keep).

**Three caveats — ship them with every ablation report:**

1. **Redundancy trap.** Two overlapping sections each read as removable (the other
   covers for it), but you cannot remove both → the verdict is **merge the pair**,
   not delete either. A SPLIT ensemble verdict across two related sections is the tell.
2. **Coverage boundary.** A section reads as bloat if no test prompt exercises its
   purpose. Navigational sections (`See also`, cross-skill tables) carry discoverability
   value that behavioral ablation cannot measure — judge those by hand.
3. **Candidate-finder, not auto-deleter.** Ablation ranks refactor *targets*; the actual
   cut still passes the Q1/Q2/Q3 gate.

Grounded in ablation-study methodology (generic prompt additions are non-monotonic —
validate each component against task evals, not intuition) and the context-rot finding
that surplus tokens measurably *degrade* output, so a confirmed-bloat cut is often
net-positive, not neutral. See `references/ablation-mode.md` for the section-splitter +
worked example.

## Refactor Moves Catalog

Refactor-hat-safe transformations only. See
`references/refactor-moves-catalog.md` for full list with examples.
Quick reference:

| Move | Effect | Equivalence risk |
|---|---|---|
| Dedupe prose | Same content stated once | Low |
| Extract to `references/` | Move detail out of SKILL.md body | Low (if reference loaded on-demand correctly) |
| Compress lists / tables | Replace bullet duplication with concise table | Low |
| Inline single-use definition | Remove indirection | Low |
| Tighten verbose phrasing | "in order to" → "to" | Low |
| Remove "ALWAYS / NEVER" caps where the prose can carry meaning | Reduce noise | Low–medium (test for behavior change) |
| Move worked examples to companion file | If 3+ examples, extract per skill-team companion-file pattern | Medium (load discipline matters) |

**Out-of-scope moves** (these are not refactor; route elsewhere):
- Adding new behavior or capability → `skill-creator-advance`
- Changing input/output format → `skill-creator-advance`
- Different prompt phrasing aimed at *different* output → `skill-tuning`
- Removing a fallback / edge case handler → `skill-creator-advance`

## Tier Cascade (when Q1's ensemble disagrees)

The multi-judge ensemble in Q1 might return mixed signals. The Tier
cascade governs how to handle disagreement:

| Tier | Trigger | Action |
|---|---|---|
| **Tier 1** | All 3 judges agree (equivalent or not) | Auto verdict |
| **Tier 2** | 2-of-3 agree | Auto verdict but flag as "uncertain", show user |
| **Tier 3** | Judges all disagree, or >50% probability of taste-call | Hand off to `dev-workflow:skill-tuning` (the equivalence question is masking a taste question; skill-refactor is the wrong tool) |

Tier 3 is the safety valve: when "is the output the same?" turns
into "which output is better?", we've left refactor territory.

## Red Flags — STOP

| Flag | Why STOP |
|---|---|
| User wants the output to *improve*, not preserve | This is `skill-tuning` territory |
| Refactor adds new sections that change behavior | Two Hats violation — feature smuggled into refactor |
| Q1 says equivalent but token reduction <5% | The refactor cost exceeds the gain; reject |
| Q1's ensemble disagrees and you want to "majority-rules" anyway | Don't — that's how taste creep enters via judge bias |
| Skill has no `test-prompts.json` and user is unwilling to write any | The gate cannot run; revert to `skill-creator-advance` |
| Refactor would touch SKILL.md and bundled files in same round | Cascade-refactor — split into separate rounds (one file per round) |

## Rationalization Prevention

| Excuse | Reality |
|---|---|
| "It's just a small reorg." | Small reorgs accumulate. Run the gate anyway. |
| "Output is *probably* the same." | "Probably" isn't a verdict. Run the equivalence check. |
| "Token reduction is only 7% but it reads better." | "Reads better" is a `skill-tuning` claim, not a refactor claim. |
| "I'll skip the baseline this once." | Without baseline, Q1 cannot run. The skill self-aborts. |
| "The judge is wrong, my refactor is fine." | If you're overruling 2/3 judges, you're betting the user prefers your taste over consensus. Don't. |

## Composes With

- **`dev-workflow:skill-creator-advance`** — when refactor reveals a
  structural problem that needs redesign (not equivalence-preserving
  cleanup), hand off here.
- **`dev-workflow:skill-tuning`** — when the
  question turns from "are the outputs equivalent" to "which output
  is better", hand off here.
- **`dev-workflow:skill-judge`** — optional advisory check before /
  after refactor; if score drops by ≥1σ across rounds while
  equivalence keeps passing, this is a signal of subtle taste-drift
  that the equivalence check missed.
- **`domain-teams:code-team/standards/refactoring-standard.md`** —
  philosophical anchor (Fowler Two Hats, behavior-preserving
  discipline). Bundled-copy pattern not used; this skill references
  the canonical code-team version for human reading. Skill is still
  runtime self-contained — no runtime dependency on `domain-teams`.

## Worked Example — token bloat in skill-creator-advance

**Input**: User says "skill-creator-advance is at 5627 words, way
over the soft cap. Let's refactor."

**Phase 0 (baseline)**:
- Capture `test-prompts.json` if absent — 3 prompts covering
  creation / improvement / description optimization
- Run baseline: each prompt × current skill → outputs
- Token count: 5627 words

**Phase 1 (Q1+Q2+Q3)**:
- Candidate move: extract "Description Optimization" section (§
  lines 430-501, ~700 words) to `references/description-optimization.md`
- Re-run test prompts on candidate
- Q1 ensemble: 3/3 say outputs equivalent (the description-opt
  use case still works because the section is loaded on demand
  via reference)
- Q2: 5627 → 4927 words = 12.4% reduction ✓
- Q3: name unchanged, dependencies unchanged, structure adds one
  reference file (allowed) ✓

**Verdict**: PROCEED. `git commit` the candidate.

**Phase 2 (next round)**:
- Look for next-largest extraction candidate
- Repeat...

After 3 rounds: 5627 → 4927 → 4400 → 4100. Skill is back under
soft cap. Output behavior unchanged. Each round individually
verified.

## Worked Example — refactor that should be REJECT

**Input**: User says "let me try this rewording — it's clearer".

**Q1 result**: 2/3 judges say outputs equivalent; 1 says the
candidate's output is "less specific about edge cases". Tier 2.
- This is the warning sign — judge disagreement on a rewording move.

**Q2 result**: 5% reduction.

**Q3 result**: clean.

**Verdict**: RESHAPE → user examines the dissenting judge's
reasoning. Turns out the "clearer" rewording dropped a phrase that
nudged Claude to handle a specific edge case. The candidate is
**not actually equivalent** — it's a subtle behavior change masked
as refactor.

→ Reject this round; do not commit.

This is what the multi-judge ensemble is for: catching subtle
behavior changes that single-judge or pure structural check would
miss.

## When To Apply

**Primary triggers**:
- "Shorten this skill" / "reduce token count" / "縮減 SKILL.md"
- "Skill is too long; tidy it up without changing behavior"
- "Refactor SKILL.md keeping outputs the same"
- "リファクタ skill / トークン削減"
- "整理 skill 結構"

**Shape**: A single existing skill with ≥3 documented use cases
(needed for `test-prompts.json`). Token bloat or structural mess is
the symptom; output behavior is the invariant.

**Not-triggers** — do NOT invoke for:

- **Skill output is bad / wrong** → use `skill-tuning` (taste
  improvement, not equivalence-preserving)
- **Want to add a phase / change agent / restructure workflow** →
  use `skill-creator-advance` (structural rewrite)
- **Creating a new skill** → use `skill-creator-advance`
- **Single-line cosmetic edits** — just edit directly; the gate
  cost exceeds the change cost
- **Skill has no `test-prompts.json` and user won't write one** —
  the gate cannot run; either provide test prompts or use
  `skill-creator-advance` to redesign with proper test infra
- **Skill output is creative / non-deterministic** (writing style,
  prose, design feel) — equivalence check unreliable; use
  `skill-tuning`

## Bundled Resources

This skill is fully self-contained at runtime. References:

- `references/equivalence-check-protocol.md` — Q1's structural +
  semantic check details
- `references/multi-judge-ensemble.md` — how to spawn 3 independent
  judges with varied framing; consensus rules
- `references/refactor-moves-catalog.md` — full catalog of
  refactor-hat-safe moves with examples
- `references/golden-anchor-protocol.md` — golden anchor schema and
  curation policy (shared convention with `skill-tuning`; same-PR
  drift rule)
- `references/test-prompts-schema.md` — `test-prompts.json` schema
  (shared convention with `skill-tuning`; same-PR drift rule)
- `references/constitution-schema.md` — `constitution.md` schema
  used as Q3 invariant input (shared convention with `skill-tuning`;
  same-PR drift rule)

Scripts:

- `scripts/equivalence_check.py` — orchestrates Q1's structural
  comparison
- `scripts/multi_judge.py` — runs 3-judge ensemble, returns consensus
- `scripts/golden_compare.py` — compares candidate output to a
  golden reference (used in Tier 2 escalation)

Optional Tier 3 hand-off path: if golden anchors exist for the
target skill (in `<skill>/golden/`), Q1's pass criterion can be
strengthened to "equivalence check passes AND candidate output
matches golden anchor pattern"; see `golden-anchor-protocol.md`.

## Bottom Line

```
Output preserved. Tokens shrunk. Invariants intact. Or revert.
Refactor is structure, not feature. Prove equivalence; don't promise it.
```
