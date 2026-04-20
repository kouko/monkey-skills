# Protocol — Express Mode (Phase 0-1 fast path)

Alternate execution path for `copywriting-intake`. Used when the user's raw brief already carries every Level 1 field this toolkit needs; the router (`using-copywriting-toolkit`) qualifies the input and dispatches intake into Express Mode instead of the full Q1-Q10 brainstorming sequence.

Express Mode does NOT relax rigor — the Intake Completeness MUST gate still runs. It replaces the **elicitation** step (asking the user 10 questions) with a **synthesis + single-turn confirmation** step (restating the user's brief in the toolkit's vocabulary and having the user confirm or adjust item-by-item).

## When to Use

Express Mode activates only when ALL of the following hold:

1. Router's Express Qualification Check (phase-decision-tree.md §Step 0.5) declares the raw input Level-1-complete.
2. No `violation` envelope was emitted against this intake (not a bounce-back retry from downstream — bounce-backs must go through full Q&A).
3. User did not explicitly request `[full Q&A intake instead]` at any prior turn.

If any condition fails → fall back to `protocols/copywriting-brainstorming.md` Q1-Q10 sequence.

## Phases

### Phase 0.5-A — Synthesis

Launch `copywriter` agent with:

- Protocol: this file
- Standards to read:
  - `../protocols/copywriting-brainstorming.md` — Level 1/2/3 field taxonomy + form-specific branches
  - `../../copywriting-voice-positioning-stage/standards/voice-quadrant-positioning.md` — quadrant pre-diagnosis (read-only)
  - `../../copywriting-ideation/standards/kosimo-instinct-analysis.md` — Level 2 approach hint
- Input: raw user brief + user's `output_language`

Worker produces an **Understanding Summary draft envelope** in the Q9 10-subsection shape defined by `copywriting-brainstorming.md`, populated as follows:

| Level | Policy | Label |
|---|---|---|
| **Level 1** | MUST be sourced directly from user's words. Never infer. If a Level 1 field cannot be quoted from the brief → ABORT Express Mode, fall back to Q1-Q10 | no label |
| **Level 2** | MAY be AI-inferred from brief + toolkit standards. MUST be explicitly labelled `AI-recommend — user-adjustable`. Include the 1-line rationale | `[AI-recommend]` |
| **Level 3** | Apply defaults (neta opt-in = No, etc.). Label as `default accepted — opt in if needed` | `[default]` |

Worker also pre-computes:

- **Predicted Phase 4 form** (short / mid / long-pasona / long-extended / light-action) from brief channel + length + action weight — labelled `[form detected]`
- **Predicted Phase 5 voice quadrant** from audience register + brief language + message_thesis — labelled `[AI-recommend]`
- **Predicted framework** (新 PASONA / BEAF / QUEST / CREMA / AIDMA short etc.) from form + Schwartz level — labelled `[AI-recommend]`
- **Predicted pipeline route** — enumerate which phases will run (Phase 2 ideation? Phase 3 neta?) and which will skip, with one-line rationale each

### Phase 0.5-B — Automated Grill (mandatory)

Mirror `copywriting-brainstorming.md §Task 4b` grill, but run by `copywriter-evaluator` (not `copywriter`) against the synthesised envelope:

1. Ethics boundary scan — 景品表示法 優良誤認 / 有利誤認 / ステマ告示 + FTC Endorsement red flags surfaced from the user's brief
2. Premise / dependency check — hidden assumptions in the brief
3. Voice-conflict check — audience register vs declared voice reference
4. Form-brief mismatch check — e.g. "7-15 chars brief" while user supplied paragraph-length narrative

Grill findings attach to the summary under `Confirmed Assumptions` (explicit) and `Resolved Ambiguities` (AI-resolved).

If any grill finding escalates to `FAIL_FATAL` (e.g. brief contains a claim violating 景表法) → ABORT Express Mode, route the user to full Q1-Q10 intake so the question can be interactively resolved.

### Phase 0.5-C — Single-turn Confirmation

Render the Understanding Summary to the user in the following fixed shape (output_language honoured):

```
我將你的 brief 用 copywriting-toolkit 的 9-phase 架構重新理解如下 —
請確認或逐項調整：

【Phase 4 選型 / form detected】<form>
  理由：<1-line rationale>

【產品 / Level 1】<user's exact words>
【價值主張 / Level 1】<1-sentence from brief>
【受眾 / Level 1】<user's exact words>
【Schwartz Level / Level 1 or AI-recommend】<level + rationale>
【切入 / Level 2 AI-recommend】<approach>
  依據：<rationale>
【聲音參照 / Level 2 AI-recommend】<maestro or default>
【Voice Quadrant / Phase 5 預判】<Q1-Q4> (<Schwartz × Quadrant rule applied>)
【框架 / Phase 4】<framework>
【Neta / Level 3 default】opt-in = <Yes|No>
  <1-line rationale>
【SNS behavior model / if applicable】<AISAS|SIPS|ULSSAS|N/A>
【Grill findings】
  - <ethics / premise / voice / form finding 1>
  - <...>

【Confirmed Assumptions】
  - <assumption 1 the AI made explicit>
  - <...>

【Resolved Ambiguities】
  - <brief wording X interpreted as Y because Z>
  - <...>

【預計 Pipeline】
  Phase 0   → Express confirm (current step)
  Phase 2   → <run | skip> — <rationale>
  Phase 3   → <run bake-in | run overlay | skip> — <rationale>
  Phase 4   → copywriting-<form>
  Phase 5   → copywriting-voice-positioning-stage
  Phase 6   → copywriting-voice-tone-stage
  Phase 7   → copywriting-ethics-check-stage (MUST)
  Phase 8   → copywriting-form-check-stage (MUST)

Options:
  [1] confirm — start writing
  [2] adjust item: <pick by number>
  [3] switch to full Q1-Q10 intake
  [4] start over
```

Accept one of the 4 responses. Do NOT proceed on silence or on "looks good" variants — require explicit `confirm` or equivalent.

### Phase 0.5-D — Intake Completeness MUST Gate

Once user confirms, run the standard Intake Completeness gate via `copywriter-evaluator`:

- Gate file: `../checklists/intake-completeness-checklist.md`
- Artifact: the confirmed Understanding Summary envelope
- Mode: binary checklist (per evaluator.md §Mode 1)

Verdict rules are unchanged from Q1-Q10 path:

- `PASS` → emit handoff envelope with `phase: phase-express-confirmed`
- `PASS_WITH_NOTES` → auto-revise ONCE (apply evaluator FIXABLE notes to the synthesised summary, re-run this gate, then emit on re-PASS)
- `NEEDS_REVISION` → ABORT Express Mode, fall back to Q1-Q10 full intake (the gate found Level 1 gaps the synthesis missed)

## Output

On PASS, emit the Phase 0-1 handoff envelope per plugin CLAUDE.md §Handoff Envelope, with:

```json
{
  "phase": "phase-express-confirmed",
  "form": "<form>",
  "brief": { "...": "synthesised + user-confirmed fields" },
  "message_thesis": "...",
  "gate_verdict": "PASS",
  "planning_team_recommended": false,
  "express_mode_used": true,
  "next_stage": "<copywriting-ideation | copywriting-<form> | copywriting-neta-injection>"
}
```

`express_mode_used: true` lets downstream skills (especially `copywriting-form-check-stage`) note in their findings that the brief was synthesised by AI — useful if a later NEEDS_REVISION turns out to be caused by a Level 2 mis-inference.

## Adjust-Item Sub-Flow

When the user picks `[2] adjust item: <N>`:

1. Echo the current value of item N and ask for the correction
2. Update ONLY that item — do NOT re-synthesise the whole envelope
3. If the adjusted item is Level 1 and the new value invalidates a Level 2 inference (e.g. user changes form from short-form to long-form-pasona → Schwartz-level inference may need re-running), re-run synthesis for JUST the dependent Level 2 fields, mark them `[AI-recommend — re-inferred]`, show diff to user, loop to Phase 0.5-C confirmation
4. Do NOT loop adjust-item more than 3 times in a single session — on the 4th request, auto-escalate to `[3] switch to full Q1-Q10 intake`

## Anti-Patterns

- **Inferring Level 1 fields** — violates the rule. If user didn't say it, ask Q1-Q10; don't guess.
- **Skipping the grill** — Phase 0.5-B is not optional. Express Mode's speed comes from eliding elicitation, not elision of rigor.
- **Silent-confirm on partial response** — if user says "looks ok" without explicit `confirm`, treat as unclear and re-prompt.
- **Bypassing Intake Completeness gate** — the MUST gate runs regardless of Express / Q&A path. The verdict is the same contract.
- **Running Express on bounce-back** — a downstream violation returning to intake indicates the synthesis (or user confirmation) was insufficient; force full Q1-Q10 on re-entry to surface the actual gap.
