---
name: copywriting-intake
description: |
  Clarify and confirm copywriting requirements (product, audience, goal, form, awareness level), hard gate on missing info. Use at the start of a new copy task with an incomplete brief, before drafting. External-copy → copywriting-audit-stage.
---

# copywriting-intake

Phase 0 (brief intake) + Phase 1 (message confirmation) — the mandatory
entry gate for every `copywriting-toolkit` pipeline run (drafting, ideation,
audit). No downstream phase loads until this skill produces a confirmed
Understanding Summary AND the `intake-completeness-checklist.md` MUST gate
returns PASS / PASS_WITH_NOTES.

## When to Use

Invoke this skill:

- As the first step of any `using-copywriting-toolkit` pipeline when the
  brief is incomplete or unconfirmed.
- When switching form type mid-conversation (short → long, etc.) — re-intake
  Level 1 fields rather than carrying stale assumptions forward.
- Before `copywriting-audit-stage` if the audit target's metadata (form,
  channel, review focus) is ambiguous.

Skip only when a prior run already produced a valid Understanding Summary
envelope within the same session and the request has not changed.

## What This Skill Owns

- **Protocol**: `protocols/copywriting-brainstorming.md` — Q1-Q10 checklist
  (request / form type / product / audience / form-specific fields / voice /
  framework / neta opt-in / grill / Understanding Summary / user confirmation).
- **Handoff format**: `protocols/copywriting-handoff-format.md` — candidate
  output template + progress reporting + mid-pipeline checkpoint rules. This
  skill uses §Section 2 (progress reporting) for Phase 0-1 transparency;
  downstream skills use the rest.
- **Gate**: `checklists/intake-completeness-checklist.md` — MUST gate run
  by `copywriting-toolkit/agents/copywriter-evaluator.md` against the Understanding
  Summary before this skill returns.

## Execution Paths — Q1-Q10 vs Express Mode

This skill has two execution paths for producing the Understanding Summary:

| Path | Protocol | When used | Elicitation |
|---|---|---|---|
| **Q1-Q10 (default)** | `protocols/copywriting-brainstorming.md` | Brief is rough / missing Level 1 fields / user requested full intake / re-entry after a downstream bounce-back | 10 questions, one per turn |
| **Express Mode** | `protocols/express-mode.md` | Router's Express Qualification Check (phase-decision-tree.md §Step 0.5) declared the raw brief Level-1-complete | Synthesis + single-turn confirmation |

Both paths produce the same output envelope shape and both run the same Intake Completeness MUST gate. Express Mode is a fast-path, not a relaxed-rigor path — rigor lives in the gate, not in the number of questions.

Route selection is driven by the router; this skill accepts whichever protocol the router dispatches and honours abort/fallback signals (Express → Q1-Q10 fallback on grill FATAL, synthesis Level 1 gap, or gate NEEDS_REVISION).

### Grill resolution strategy differs by path (by design)

The two paths handle Q8 grill FATAL candidates differently — this bifurcation is intentional, mirrors `superpowers:brainstorming` (interactive) vs `superpowers:subagent-driven-development` (status-coded return), and is NOT a protocol drift to be reconciled:

**Q1-Q10 path — inline probe-and-resolve** (interactive)

When Q8 grill surfaces a FATAL candidate (景表法 / FTC / ステマ / dark-pattern / unsubstantiated claim), the agent resolves it INLINE before emitting the Understanding Summary:

1. Agent probe: surface the specific concern to the user in plain language, cite the legal / ethical surface (e.g., 景表法 §5-2 有利誤認).
2. Agent offers 3 structured options:
   - **(A) Supply substantiation** — user provides benchmark / third-party data / certification.
   - **(B) Rewrite to avoid** — drop the claim and replace with experiential / factual framing the writer can defend.
   - **(C) Drop the claim** — remove entirely; brief proceeds without it.
3. User picks → agent records decision in `Confirmed Assumptions` → continues to Q9 Summary.
4. If user cannot decide after one probe round (replies vague, off-topic, or asks agent to decide) → agent BLOCKED status, halt and ask human partner per `superpowers:executing-plans §When to Stop and Ask for Help`.

**Q1-Q10 has NO tier concept** (T1/T2/T3). Tier classification is an Express Mode output contract (see `protocols/express-mode.md §Tiered FATAL handling §Scope note`). In Q1-Q10, every FATAL candidate is resolved interactively — there is no "carry to Phase 7 with benchmark-required flag" because Q8 probe-and-resolve already surfaced the benchmark requirement to the user in the same session.

**Express path — structured tier return** (non-interactive)

When Phase 0.5-B grill (run by `copywriter-evaluator` in single-shot mode) surfaces a FATAL candidate, it cannot probe — it classifies the finding into T1 / T2 / T3 per `protocols/express-mode.md §Tiered FATAL handling`. Router routes based on the tier:

- T1 (AI-inferred) → ABORT Express → fall back to Q1-Q10 (interactive mode can probe).
- T2 (user-stated + benchmark-missing) → CARRY to Phase 7 with `benchmark_required_before_phase_7` flag in `Confirmed Assumptions`. User sees the flag in Phase 0.5-C single-turn confirmation and can pre-resolve, OR Phase 7 adjudicates.
- T3 (user-stated + outright violation) → ABORT Express → fall back to Q1-Q10 (the claim itself needs discussion, not benchmark).

Tier logic exists ONLY for Express because Express lacks the interactive probe option. Q1-Q10 has no need for it.

### Rationale for not unifying

Following `superpowers` precedent: `brainstorming` and `subagent-driven-development` are treated as two distinct skills with different return contracts, not one unified process. Interactive and non-interactive modes legitimately have different resolution strategies — unifying them would force Q1-Q10 to adopt tier labels it doesn't need, or force Express to leave questions open for a probe turn it cannot execute.

Each path is clean within its own context. The rhetoric divergence (tier vs probe) is a feature, not a bug.

## Phase 0 — Brief Intake (Q1-Q10 path)

Drive the Q1-Q10 sequence in `protocols/copywriting-brainstorming.md`.
One question per message, multiple-choice first, always attach a recommended
answer. Render each question in the user's `output_language` (ja / en /
zh-TW per §Template Rendering Rule).

### Field tiers

Mirror the protocol:

**Level 1 (Must — BLOCKED if missing)**

- `form_type` — long / mid / short / ideation / audit (Q2)
- `product` + 1-sentence `value_proposition` (Q3)
- `target_audience` — at least 1 concrete demographic / persona (Q4)
- **Form-specific must fields** (Q5, branching):
  - long → word-count range + Schwartz awareness level
  - mid → 3+ concrete benefits + channel (Rakuten / Amazon / POP / briefing)
  - short → target emotion/pain + intended channel + char-limit band
  - ideation → candidate count + value-prop source
  - audit → existing copy **full text** (not summary) + review focus

**Level 2 (Should — AI recommends, user approves, defaults disclosed)**

- `voice_reference` — 糸井 / 岩崎 / 眞木 / 谷山 / Ogilvy / 龔大中 / 許舜英 /
  default (Q6). Optional `voice_quadrant` Q1-Q4 macro positioning.
- `framework` / `approach` — form-scoped choices (Q7): 旧/新 PASONA /
  PASBECONA / BEAF / 5-approach / PREP / CREMA / Mandal-Art, etc.

**Level 3 (May — off by default, opt-in)**

- `neta_opt_in: Yes | No` (default No; Q7.5)
- `neta_source_type_preference: all | sns-meme | literary | mixed` (only
  when opt-in Yes)

### Grill (Q8)

Mandatory. Minimum one ethics-boundary question even when the brief is
clean (景品表示法 / FTC / ステマ告示 risk scan). Additional probes on
premises / dependencies / voice-conflict per protocol §Task 4b adaptation.

## Phase 1 — Message Confirmation

After Q8 grill resolves, produce the **Understanding Summary** (Q9) in the
exact 10-subsection structure defined in the protocol (Request / Form Type /
Product / Target Audience / Form-Specific Spec / Voice Reference / Framework /
Confirmed Assumptions / Resolved Ambiguities / Level 2/3 Defaults Accepted).

### Decision tree — LOOSE coupling to planning-team

Before presenting the Summary to the user (Q10 confirmation gate), run:

```
Is the problem thesis-level?
  (unclear product positioning / audience-thesis mismatch / goal absent /
   value proposition cannot be verbalized in 1 sentence)

  YES → RECOMMEND (not enforce):
        "Consider running planning-team first for thesis clarification
         (PRODUCT-SPEC.md / JTBD / audience anchor). You may also
         proceed here — I will record the thesis as user-supplied
         and flag Level 2 defaults accordingly."
        User decides: [run planning-team first] / [proceed anyway] / [abort]
        No hard block. No auto-delegation.

  NO  → Proceed to Q10 user confirmation gate with the Summary.
```

Signals that trigger the RECOMMEND branch:

- Q3 value proposition cannot be written in 1 concrete sentence.
- Q4 audience is "general consumers" / "everyone" with no narrowing after
  one grill round.
- User explicitly asks "what should this product even be saying?" (goal
  ambiguity) rather than "how do I phrase this message?" (copy ambiguity).

Cross-plugin reference: `planning-team` lives in the `domain-teams` plugin
(`domain-teams:planning-team`). This skill does not load it, does not pass
paths to it, and does not wait on its verdict. The recommendation is a
plain-English suggestion the user acts on or ignores.

## Hard Gate — MUST

After Q9 Summary is drafted AND before Q10 user confirmation, dispatch the
evaluator:

- **Agent**: `copywriting-toolkit/agents/copywriter-evaluator.md`
- **Checklist**: `checklists/intake-completeness-checklist.md`
- **Input**: the Understanding Summary artifact + form_type
- **Output**: verdict JSON (see checklist §Output Format)

Verdict handling:

- `PASS` → present Summary to user for Q10 explicit confirmation.
- `PASS_WITH_NOTES` (≤2 FIXABLE, no FATAL) → auto-revise once; disclose the
  diff via handoff-format §Section 3 PASS_WITH_NOTES report; then present
  to user.
- `NEEDS_REVISION` (any FATAL, or ≥3 FIXABLE) → **BLOCKED**. Return to the
  specific Q-task the evaluator's `next_action` field names. Do NOT present
  Summary. Do NOT proceed.

Second PASS_WITH_NOTES round → escalate to NEEDS_REVISION (max-2-rounds
rule from handoff-format §Section 3).

## User Confirmation (Q10) — Silent-proceed Prohibited

Only after gate PASS / PASS_WITH_NOTES AND explicit user reply of
"confirm — start writing" does this skill emit the handoff envelope and
return. "Adjust item" routes back to the named Q-task; "Start over" restarts
at Q1.

## Handoff Envelope (this skill's output)

Schema mirrors `copywriting-toolkit/CLAUDE.md §Handoff Envelope`:

```json
{
  "phase": "phase-1-confirmed",
  "form": "long-form-pasona | long-form-extended | mid-form | short-form | light-action | ideation | audit",
  "brief": {
    "request": "user's paraphrased Q1 request",
    "product": "...",
    "value_proposition": "1-sentence",
    "target_audience": "demographic + Schwartz-level (long) or emotion (short)",
    "form_specific": { "word_count_range | benefits | channel | char_limit | ...": "..." },
    "voice_reference": "糸井 | 岩崎 | 眞木 | 谷山 | Ogilvy | 龔大中 | 許舜英 | default",
    "voice_quadrant": "Q1 | Q2 | Q3 | Q4 | not-declared",
    "framework": "新 PASONA | BEAF | 5-approach | CREMA | ...",
    "neta_opt_in": "Yes | No",
    "neta_source_type_preference": "all | sns-meme | literary | mixed | null",
    "level_2_3_defaults_accepted": ["voice=default (AI-recommended, user-approved)", "..."]
  },
  "message_thesis": "1-2 sentence core message derived from value prop + audience + framework",
  "planning_team_recommended": false,
  "gate_verdict": "PASS | PASS_WITH_NOTES",
  "next_stage": "copywriting-ideation | copywriting-neta-injection | copywriting-long-form-pasona | copywriting-long-form-extended | copywriting-mid-form | copywriting-short-form | copywriting-light-action | copywriting-audit-stage"
}
```

Downstream skills read `brief` + `message_thesis`, add their layer
(ideation_pool / neta_candidates / draft), update `next_stage`, return.

## Next-Step Hints

The router `using-copywriting-toolkit` reads `next_stage` and dispatches.
Default routing from this skill:

- Brief is divergent / angle space unclear → `copywriting-ideation` (Phase 2)
- Brief is concrete + user opted neta=Yes with pre-draft bake-in →
  `copywriting-neta-injection` (Phase 3 pre-draft)
- Brief is concrete + direct-to-draft → skip to Phase 4 workflow skill
  matching `form`:
  - long-form-pasona → `copywriting-long-form-pasona`
  - long-form-extended (QUEST / PASTOR) → `copywriting-long-form-extended`
  - mid-form → `copywriting-mid-form`
  - short-form → `copywriting-short-form`
  - light-action (PREP / CREMA) → `copywriting-light-action`
- form = audit → `copywriting-audit-stage` (bypasses Phase 2-4, runs 5-8
  against existing copy)

When unsure, default `next_stage` to `copywriting-ideation` for long/short
(divergence reduces backtracking) and to the Phase 4 workflow for mid/audit.

## Rules (condensed — see protocol for full text)

- One question per message. Multiple choice first. Recommendation attached.
- "Don't ask what you can look up" — parse request / PRODUCT-SPEC / brand
  guide before asking the user.
- Understanding Summary is a hard gate. No next-phase load without user
  confirmation.
- Silent Level 2 default adoption is prohibited — disclose in Summary
  §Level 2/3 Defaults Accepted.
- Voice guide > framework. If brand voice guide conflicts with Q6, voice
  wins.
- Q8 grill minimum 1 question (ethics boundary) even for clean briefs.
- `planning-team` recommendation is LOOSE — never auto-delegate, never hard
  block.

## Anti-Patterns (see protocol §Anti-Patterns for examples)

- Batch questioning (Q2+Q3+Q4 in one message)
- Skipping Q8 grill
- Loading next protocol without Q10 confirmation
- Open-ended voice question ("what voice should we use?") instead of
  multi-choice with representative samples
- Silent default adoption without Summary disclosure
- Re-asking what's already in the request text

## Files

- `protocols/copywriting-brainstorming.md` — full Q1-Q10 checklist (verbatim
  copy from `domain-teams:copywriting-team`)
- `protocols/copywriting-handoff-format.md` — output format + progress
  reporting (verbatim copy)
- `checklists/intake-completeness-checklist.md` — MUST gate (verbatim copy)
