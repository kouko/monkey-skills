---
name: skill-tuning
description: |
  Output-quality A/B for an existing skill: generate variants, run blind on the same prompts, human picks the winner. Use to tune a skill's output style/voice/tone. For redesign use skill-creator-advance; for token refactor use skill-refactor.
---

# Skill Tuning

A user-invoked gate skill: forces variant exploration of an
existing skill's output quality through **human-judged blind A/B
comparison**, accumulating a preference log that serves as both the
decision basis for current iteration and a future RLHF-lite
dataset.

This skill is the **feature hat** counterpart to `skill-refactor`'s
refactor hat: where refactor preserves behavior, tuning deliberately
explores behavior changes to find better outputs. Where refactor
uses LLM-as-judge (reliable for binary equivalence), tuning uses
human judgment (necessary because taste cannot be reliably
LLM-judged).

## Overview

Skill outputs have **taste-sensitive dimensions** that
LLM-as-judge cannot reliably evaluate: writing style, voice, tone,
choice of metaphors, persuasive force, design feel. A skill that
"works" can still produce outputs that are flat, off-tone, or just
not what the user wanted.

Improving such skills requires **human preference signal**, not
more rule-following. This skill captures that signal in a
structured way: generate variants, run them blind, ask the user to
pick, log the choice. Over iterations, the preference log becomes
a dataset; eventually (H4 horizon) a small judge can be trained on
it that approximates the user's taste better than any general LLM
judge.

This skill is **runtime self-contained** — `dev-workflow` is the
only plugin needed. No cross-plugin dependency.

## The Iron Law

```
NO VARIANT SHIPS WITHOUT (1) CONSTITUTION HONORED
                         (2) HUMAN PREFERENCE CAPTURED
                         (3) PREFERENCE LOG UPDATED
```

Constitution is the floor — variants violating MUST clauses are
auto-rejected before the human sees them. Taste is the ceiling —
which variant is better is the human's call, not the skill's.
Preference log is the durable record — one A/B without log entry
is wasted signal.

## Before You Begin

Before generating variants, the target skill needs:

1. **`test-prompts.json`** — at least 3 representative prompts.
   Schema: `references/test-prompts-schema.md`. Same convention as
   skill-refactor; if test-prompts.json was created during a
   skill-refactor session, reuse it here.
2. **`constitution.md`** *(strongly recommended)* — MUST / MUST NOT
   list for the skill. Variants violating any MUST are filtered
   before the human sees them. If the skill has no constitution,
   ask the user whether to write one (high-value for taste-sensitive
   work) or proceed without (variants un-floored; user does
   constitutional check manually). Schema:
   `references/constitution-schema.md`.
3. **`golden/` directory** *(optional)* — human-curated reference
   outputs. If present, variants are scored against goldens for
   "closeness to anchor" as a tie-breaker / direction check.
   Schema: `references/golden-anchor-protocol.md`.
4. **A baseline run** — execute each test prompt against the
   *current* SKILL.md, capture outputs to `<workspace>/baseline/`.
   This is variant A (or B; randomized per blind protocol).
5. **Preference log location** — typically
   `<skill>/preference-log.jsonl`. Schema:
   `references/preference-log-schema.md`. If absent, create on
   first session.

**Do not generate variants until baseline is captured.**

## The Gate Function (per round)

### Phase 1: Variant Generation (editor agent)

Spawn an editor subagent with the **feature hat** prompt:

> You are exploring variant outputs for skill `<name>`. The current
> skill produces `<baseline output>` for the prompt `<test prompt>`.
> Generate 1 variant SKILL.md modification that produces a *different
> output* — different tone / structure / level of detail / phrasing.
> The variant must:
> - Honor every MUST clause in `constitution.md`
> - Not violate any MUST NOT clause
> - Produce semantically valid output for the prompt (not gibberish)
> - Differ from baseline in at least one *named* dimension (state
>   what's different)
>
> Generate the variant SKILL.md edit; explain the dimension being
> explored.

For each round, generate **2-3 variants** (not 5+; user judgment
fatigue caps the useful ensemble at small N). See
`references/ab-harness-protocol.md` for the full variant-generation
protocol.

### Phase 2: Constitutional pre-filter

Before showing variants to the human, run constitutional check
against each variant:

```
For each variant:
    For each MUST in constitution.md:
        Test variant against MUST condition (run on a representative prompt)
        If violated: variant rejected, do not show to user
    For each MUST NOT in constitution.md:
        Test variant against MUST NOT condition
        If triggered: variant rejected, do not show to user
```

A variant that fails constitutional check gets a 1-line "rejected:
violates MUST X" entry in the preference log; the user is informed
the variant was filtered (not silently dropped). See
`references/constitutional-judging.md`.

If all variants fail constitution → no candidates remain → report
to user; recommend either (a) loosening constitution if too strict,
or (b) refining variant generation prompt.

### Phase 3: Blind A/B harness

Surviving variants + baseline are presented to the human in
random label assignment (A / B / C):

> Three variants of `<skill>` were tested on this prompt:
>
> ```
> User prompt: <prompt>
> ```
>
> ## Variant A
> <output>
>
> ## Variant B
> <output>
>
> ## Variant C
> <output>
>
> Which output do you prefer? You can pick:
> - One of A / B / C
> - "Both A and C" (multi-pick)
> - "None" (all variants worse than current state)
> - "Need more info" (request different test prompt or different variants)

The user's identity (which variant was the baseline, which were
new) is **withheld** until after the user picks. Reveal only after
the choice is locked.

For multi-evaluator setups (rare; only when multiple humans review
together), each evaluator picks independently; aggregate via
inter-rater agreement; if agreement <70%, escalate as
`dev-workflow:skill-refactor`-style "uncertain" → don't ratchet
without resolution.

See `references/ab-harness-protocol.md` for the full harness flow.

### Phase 4: Verdict + log

| User pick | Verdict | Action |
|---|---|---|
| User picks variant ≠ baseline | **ADOPT** | Apply the picked variant's SKILL.md edit; commit; log preference |
| User picks baseline | **DROP** (variants drop) | Discard variant edits; log "no preference for variants this round" |
| User picks "Both" | **DEFER** | No immediate change; record both as candidates for future rounds |
| User picks "None" | **DROP** | Discard all variants; log "all variants worse"; consider this a signal that the variant-generation prompt may be too narrow |
| User picks "Need more info" | **REFINE** | Don't decide; gather what the user requested (different prompt / different variants); re-run |

Preference log entry per round:

```jsonl
{"timestamp": "...", "skill": "...", "round": N, "test_prompt_id": M, "variants_shown": ["baseline", "variant_a", "variant_b"], "user_pick": "variant_a", "rejected_by_constitution": [], "evaluator": "human-1", "notes": "..."}
```

See `references/preference-log-schema.md`.

## Verdict Vocabulary

Parallel to other dev-workflow critique skills:

| Verdict | When | Action |
|---|---|---|
| **ADOPT** | User prefers a non-baseline variant | Apply edit; ratchet to new baseline; log |
| **DROP** | User prefers baseline OR all variants worse | Variants discarded; baseline preserved |
| **DEFER** | Multiple variants preferred (no single winner) | Record candidates; no immediate change |
| **REFINE** | User needs different test inputs / variants | Re-run with revised generation; no decision yet |
| **ESCALATE** | Multi-evaluator disagreement >30% | Block decision; resolve human-to-human first |

Note: skill-tuning **does not auto-revert** the way skill-refactor
does. There is no LLM judge that can reliably say "this variant is
worse" — only the human can. Without a human pick, no variant ships,
period.

## Constitutional Judging (the floor)

A skill's `constitution.md` lists MUST / MUST NOT clauses. These
are **non-negotiable** — taste does not override constitution. A
variant that violates a MUST is rejected even if a user might
"prefer" the violating output.

This is the difference between *taste* and *negligence*. Tuning
explores legitimate quality variation within the skill's contract.
Constitutional violation is contract breach, not taste — it gets
caught before it ever reaches user judgment.

See `references/constitutional-judging.md` for full protocol
including: how to test MUST clauses against variants, what counts
as "violated", how to handle MUST clauses that are themselves
ambiguous, and how to evolve constitution when tuning reveals
implicit constraints.

## Preference Log → Self-Trained Judge (H4 horizon)

The preference log is **durable signal**. Every round adds an
entry; over time, hundreds to thousands of entries accumulate.

At ≥1000 entries, the log becomes training data for a
domain-specific preference model:

```
Train: log[i].variants → predict log[i].user_pick
Eval: held-out log entries
Deploy: use trained model as a Tier-1 pre-filter to rank variants
        before showing to user; user still has final say
```

This is RLHF-lite: human-judged data → trained reward model →
cheaper iteration over time. The trained model **does not replace**
the user's final pick — it's a pre-filter that ranks variants by
predicted user preference, so the user sees the most-promising
variants first.

**This skill ships with the pipeline scaffolded** but the trained
model itself is out-of-scope until the log accumulates. See
`references/self-trained-judge-pipeline.md` for the schema and
training methodology.

## Red Flags — STOP

| Flag | Why STOP |
|---|---|
| User wants behavior preserved (not different) | This is `skill-refactor` territory |
| Output is deterministic / mechanical (file transform, JSON spec) | No taste dimension; tuning is overkill |
| User wants to skip blind labeling ("just show me which is the new one") | Blind protocol exists for position-bias reasons; honoring user request would compromise the data |
| Constitution is missing AND skill has taste-sensitive output | Strongly recommend writing constitution first; without floor, variants drift unpredictably |
| Variants are too similar (cosmetic phrasing changes) | Wasted A/B; user can't distinguish; widen variant generation |
| Multi-evaluator <70% agreement | Don't ratchet on disagreement; resolve human-to-human first |
| Round 5+ with no clear preference signal | The skill's quality dimensions may not be tasteable from output alone — consider going to skill-creator-advance for redesign |

## Rationalization Prevention

| Excuse | Reality |
|---|---|
| "I can tell which is the new variant from style alone." | Maybe — but blind labeling captures bias-free signal. Your hunch is not the data. |
| "Let me skip the constitution check this round." | A variant that violates MUST is not a taste variant. Skipping = shipping behavior change as taste. |
| "User picked 'both' — I'll just keep both." | DEFER means *no immediate change*. Multi-pick is not a multi-keep license. |
| "Variants are similar enough; I'll merge their best parts." | Don't. That creates a 4th variant the user didn't pick. Re-run if needed. |
| "1 round was enough; I'll skip the log entry." | The log is the durable signal. One unlogged round wastes the human's judgment. |

## Composes With

- **`dev-workflow:skill-creator-advance`** — when tuning reveals a
  structural problem (no variant in the same shape gets preferred,
  user wants fundamentally different shape), hand off to redesign
- **`dev-workflow:skill-refactor`** — when the variant the user
  picks happens to be longer (token cost up), can chain to
  refactor afterwards to compress without losing the chosen
  qualities
- **`dev-workflow:skill-judge`** — optional advisory check on each
  variant; advisory only (skill-judge does not understand taste);
  useful as a sanity check on structural dimensions of variants
- **`copywriting-toolkit:voice-anchors`** — analogous concept at
  the copywriting level; the goldens / constitution patterns in
  this skill borrow from voice-anchor curation discipline

## Worked Example — improving a status-report skill's tone

**Input**: User says "the status-report skill produces dry, formal
prose. I want warmer, more direct outputs without losing the
information density."

**Phase 0**:
- `test-prompts.json`: 3 prompts (weekly update / blocker post /
  shipping announcement)
- `constitution.md`: includes MUSTs like "include the 3 facts:
  what shipped / what's in flight / what's blocked"; MUST NOT
  "fabricate metrics not in input"
- Baseline run: dry, formal outputs as expected

**Phase 1 (variants)**:
- Variant A: same content, conversational tone (contractions,
  shorter sentences)
- Variant B: bulleted-up list-first, less prose
- Variant C: lead with the human story, then facts

**Phase 2 (constitutional pre-filter)**:
- All 3 variants honor MUST (3-fact coverage); all honor MUST NOT
  (no fabrication)
- All 3 pass to user

**Phase 3 (blind A/B)**:
- User sees baseline + A + B + C in random label order
- User picks "A or C, both feel right; B is too sparse"

**Phase 4 (verdict)**:
- DEFER (multi-pick) — record A and C as candidates
- Round 2 generates A/C-style variants; user picks A
- Round 3 confirms A as preferred; ADOPT

After 3 rounds: skill outputs warm-but-dense status reports;
preference log has 9 entries (3 prompts × 3 rounds); user
satisfied; durable record of what "warm" means in this context.

## Worked Example — variant rejected by constitution

**Input**: User wants variants for an inventory-snapshot skill.

**Phase 1**: variant generation produces:
- Variant A: list inventory by category (organized)
- Variant B: list inventory by SKU number (sortable)
- Variant C: summarize inventory in narrative prose ("we have
  approximately 200 widgets and a few dozen sprockets...")

**Phase 2 (constitutional pre-filter)**:
- Variant C violates MUST: "All quantities MUST be exact integers
  from input; no approximation". Rejected before user sees.
- User informed: "Variant C was generated but rejected because it
  approximates quantities ('approximately 200', 'a few dozen'),
  violating the skill's exactness requirement."
- A and B proceed to A/B.

**Phase 3**: User picks A (category organization).

**Verdict**: ADOPT variant A.

This is the constitution as floor: a variant that **the user might
have actually preferred** ("we have approximately 200 widgets" is
warmer / friendlier prose) is filtered because it breaks a
non-negotiable accuracy contract. Taste does not override
contract.

## When To Apply

**Primary triggers**:
- "Improve this skill's output style"
- "Try different phrasings"
- "A/B test variants"
- "改善 skill 輸出 / 風格優化 / 跑 A/B 測試"
- "出力品質を改善" / "リライト試したい"
- "the output feels off — let me try alternatives"

**Shape**: An existing skill where output has *taste-sensitive
dimensions* — writing style, voice, tone, persuasive force, design
feel, structural choices that aren't load-bearing. Skill must have
≥3 documented test prompts; preferably has a constitution.

**Not-triggers** — do NOT invoke for:

- **Token / structure refactor with output preserved** — use
  `skill-refactor` (Phase A; output equivalence is the goal there)
- **Structural redesign / phase changes** — use
  `skill-creator-advance`
- **New skill creation** — use `skill-creator-advance`
- **Deterministic / mechanical skills** (file transforms, JSON
  spec generation, fixed-format report) — output is binary
  correct/incorrect; taste doesn't apply; tuning is overkill
- **Single-iteration vibes-check** — don't create a preference log
  for a one-off "does this look right?"; just edit
- **Skill with no constitution AND no goldens AND no test prompts**
  — gate cannot run safely; recommend foundation work first

## Bundled Resources

This skill is fully self-contained at runtime. References:

- `references/ab-harness-protocol.md` — variant generation +
  side-by-side presentation + 4-option capture protocol
- `references/constitutional-judging.md` — how MUST clauses
  filter variants before user judgment; constitution evolution
- `references/preference-log-schema.md` — JSONL format,
  per-entry fields, retention / privacy considerations
- `references/self-trained-judge-pipeline.md` — H4 horizon scaffold
  for training a domain-specific preference model from log;
  not-yet-active, schema for future
- `references/golden-anchor-protocol.md` — *bundled functional copy*
  of the shared convention also living in `skill-refactor`'s
  references; same-PR drift rule
- `references/test-prompts-schema.md` — *bundled functional copy*;
  same convention as skill-refactor
- `references/constitution-schema.md` — *bundled functional copy*;
  same convention as skill-refactor

Scripts:

- `scripts/ab_harness.py` — orchestrates variant collection,
  random labeling, side-by-side rendering for terminal display
- `scripts/preference_log.py` — append / query / aggregate
  preference log entries
- `scripts/judge_train_stub.py` — H4 stub: documents training
  pipeline, fails with "log too small" until ≥1000 entries

## Bottom Line

```
Constitution is the floor. Taste is the ceiling.
Variants the user picks ship. Variants the user doesn't pick log
the signal anyway.
The ratchet here is the preference log — it only grows.
```
