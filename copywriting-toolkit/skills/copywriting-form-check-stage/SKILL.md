---
name: copywriting-form-check-stage
description: Phase 8 form gate (evaluator-only) — framework adherence + length discipline + CTA appropriateness. MUST gate after ethics clears. 形式ゲート・フレームワーク適合。形式審查。
---

# copywriting-form-check-stage

Phase 8 — **evaluator-only form MUST gate**. This is the **last gate
before delivery**. It runs only after `copywriting-ethics-check-stage`
(Phase 7) returns `PASS`.

> Position in pipeline: … → `copywriting-ethics-check-stage` → **this
> skill (Phase 8)** → delivery to user.

## Role Constraint (read first)

- **Evaluator-only** — this skill MUST NOT edit the draft. Per plugin
  CLAUDE.md (Agent Behavioral Rules): evaluators produce verdicts,
  do NOT modify artifacts.
- **MUST gate** — verdict is binding on delivery. `NEEDS_REVISION`
  loops the envelope back to the Phase 4 drafter skill with the
  evaluator's findings attached.
- **Preconditions** — `envelope.ethics_verdict == "PASS"`. If this
  field is missing or not `PASS`, stop and return to the orchestrator;
  the pipeline MUST pass Phase 7 first.

## Preconditions

Formal schema used by `using-copywriting-toolkit` router for bounce-back routing. On violation, router emits the bounce-back envelope defined in `../../CLAUDE.md §Envelope Violation`.

### Required envelope fields (Level 1 — BLOCKED if missing)

| Field | Type | Source | Notes |
|---|---|---|---|
| `phase` | enum | Phase 7 | must equal `phase-8-form` |
| `ethics_verdict` | enum | Phase 7 | must equal `PASS` — `NEEDS_REVISION` blocks, `PASS_WITH_NOTES` must have FIXABLE notes applied first |
| `draft` | string | Phase 4 / 6 / 7 | non-empty; final polished version |
| `form` | enum | intake | determines which framework-adherence branch applies (PASONA / BEAF / QUEST-PASTOR / PREP-CREMA / AIDMA short) |
| `voice_quadrant` | object | Phase 5 | context for 8b form-appropriate rubric (voice-register vs form-register consistency) |
| `tone_notes` | object | Phase 6 | context for 8b |

### Bounce targets on violation

- `ethics_verdict` missing OR `NEEDS_REVISION` → `copywriting-ethics-check-stage` (Phase 7 must complete first)
- `ethics_verdict == "PASS_WITH_NOTES"` with unapplied notes → bounce to Phase 7 FIXABLE auto-revise loop
- `draft` missing → `copywriting-<form>` (Phase 4 drafter)
- `form` missing → `using-copywriting-toolkit` (mis-routed)
- `voice_quadrant` / `tone_notes` missing → `copywriting-voice-positioning-stage` / `copywriting-voice-tone-stage`

## Input — Envelope Shape

```json
{
  "phase": "phase-8-form",
  "form": "<short-form | mid-form | long-form-pasona | long-form-extended | light-action>",
  "brief": { "...": "from Phase 0 intake" },
  "message_thesis": "...",
  "draft": "<Phase 7-cleared draft>",
  "voice_quadrant": { "primary": "Q1 | Q2 | Q3 | Q4", "edge": "...", "rationale": "...", "schwartz_alignment": "..." },
  "tone_notes": "...",
  "ethics_verdict": "PASS",
  "next_stage": "copywriting-form-check-stage"
}
```

## Gate Definition

Two evaluator passes run in order. Both use `../../agents/copywriter-evaluator.md`.

| # | Layer | File | Mode | Tier |
|---|---|---|---|---|
| 8a | Gate (checklist) | `checklists/persuasion-framework-adherence-checklist.md` | Checklist Mode (PASS / FAIL_FATAL / FAIL_FIXABLE / N/A) | **MUST** |
| 8b | Gate (rubric) | `rubrics/form-appropriate-gate.md` | Flag Mode (🔴 / 🟡 / 🟢) | **SHOULD** |

### Coverage

**8a — Framework adherence (MUST, binary)**

- Stage existence / ordering per form:
  - 旧 PASONA (5) / 新 PASONA (6) / PASBECONA (9) — long-form
  - QUEST / PASTOR — long-form-extended
  - BEAF (Benefit → Evidence → Advantage → Feature) — mid-form
  - PREP / CREMA (5) — light-action
  - AIDMA short-form (A+I only) — short-form catchcopy
- **Length discipline**:
  - Short-form: 7–15 字 golden range
  - Mid-form: ~300–800 字
  - Long-form: ≥1,500 字 + stage word-count ratios
    (旧 P:A:So:N:A ≒ 2:2:3:2:1, PASBECONA ≒ 1:1:1:1:2:2:1:0.5:0.5)
- **CTA appropriateness** — stage-correct placement (e.g., Action stage
  in PASONA, C stage in CREMA); no CTA-before-Problem inversions
- **Taniyama discipline** — 「なんかいいよね禁止」 3-reason rule,
  描写 vs 解決 boundary, applied across forms

**8b — Form-appropriate qualitative assessment (SHOULD, flag mode)**

Assesses *how well* the structure is executed (not whether it exists —
that is 8a's job). Dimension set is form-specific:

- **Long-form**: inter-stage flow, drop-off prevention, B/E/C
  abstract → objective → concrete progression, Affinity thickness
- **Mid-form**: Benefit-first clarity, Evidence concreteness,
  Advantage comparison clarity
- **Short-form**: 3-second land ability, 掛詞 / phonetic technique,
  5-type 切入点 (利益 / 恐怖 / 顛覆 / 呼喚 / 提問) clarity

**Additional 8b dimensions the evaluator must raise regardless of form** (added per v1.0.0 review):

- **Word-count band adherence** — check the draft length against the framework's canonical band (per `long-form-pasona-canon.md §Three-framework applicability matrix`: 旧 PASONA ≤3000 chars / 新 PASONA 3000-10000 / PASBECONA 10000+). A boundary case (e.g., 新 PASONA at 1500 chars, below the 3000 floor) → 🟡. Far-below (≤60% of band floor) → 🔴. The gate does NOT reject boundary cases outright but surfaces them as a flag so the user can choose to downgrade the framework (e.g., 新 PASONA → 旧 PASONA) or expand the draft.
- **`schwartz_alignment: conflict_flagged` carry-forward** — when Phase 5's `voice_quadrant.schwartz_alignment == "conflict_flagged"` persists to Phase 8, the rubric checks whether the final draft delivers the claimed voice despite the Schwartz mismatch. If voice-fidelity drops (e.g., declared 許舜英 Q2 manifesto but actual copy reads Q4 direct-response), raise 🟡 for "voice-intent vs delivery mismatch in Schwartz-conflict context". This is the downstream consumer that closes the conflict_flagged loop.

Gate 8b runs in **flag mode**: it surfaces weaknesses but does not
block on a single 🟡. Verdict rules are per the rubric
(`rubrics/form-appropriate-gate.md`): 1 🔴 → `NEEDS_REVISION`;
2+ 🟡 → `NEEDS_REVISION`; 1 🟡 → `PASS_WITH_NOTES`; all 🟢 → `PASS`.

## Evaluator Launch — Pass 8a (MUST)

```
### Resource Paths
- gate_file: <absolute>/checklists/persuasion-framework-adherence-checklist.md
- standards: []   # the checklist references its own standards by relative path;
                  # evaluator resolves them from the checklist itself

### Artifact
<envelope.draft>

### Requirements
<original user brief from envelope.brief, plus envelope.form so
evaluator's form-type determination step (checklist §Form Type
Determination) can cross-check against declared form>
```

If 8a returns `NEEDS_REVISION` → skip 8b, go to loop-back handling
(below). If 8a returns `PASS` or `PASS_WITH_NOTES` → proceed to 8b.

## Evaluator Launch — Pass 8b (SHOULD)

```
### Resource Paths
- gate_file: <absolute>/rubrics/form-appropriate-gate.md
- standards: []

### Artifact
<envelope.draft (post-FIXABLE-revise if 8a returned PASS_WITH_NOTES)>

### Requirements
<envelope.form + envelope.voice_quadrant + envelope.tone_notes for
context on positioning and register>
```

## Combined Verdict

| 8a | 8b | Final | Action |
|---|---|---|---|
| `PASS` | `PASS` | `PASS` | Deliver. |
| `PASS` | `PASS_WITH_NOTES` | `PASS_WITH_NOTES` | Present findings alongside delivery. User chooses whether to iterate. |
| `PASS_WITH_NOTES` | any | auto-revise 8a FIXABLEs, re-run 8a, then 8b | Max one auto-revise round on 8a. |
| `NEEDS_REVISION` (either pass) | — | `NEEDS_REVISION` | Loop back (below). |

## Loop-Back on `NEEDS_REVISION`

Per plugin convention (see `../../CLAUDE.md`, and revise-loop cap
inherited from copywriting-team), **maximum 2 revise rounds** per
phase. Protocol:

1. Attach the evaluator's per-item findings to the envelope as
   `form_findings`.
2. Set `next_stage` back to the Phase 4 drafter skill implied by
   `envelope.form`:
   - `short-form` → `copywriting-short-form`
   - `mid-form` → `copywriting-mid-form`
   - `long-form-pasona` → `copywriting-long-form-pasona`
   - `long-form-extended` → `copywriting-long-form-extended`
   - `light-action` → `copywriting-light-action`
3. Track `revise_round_count` in the envelope. On entering a 3rd
   round, stop the loop and surface the situation to the user for a
   human decision (change `form`, change `message_thesis`, or
   accept-with-notes).

Do NOT re-run Phase 5 (positioning), Phase 6 (tone), or Phase 7
(ethics) on loop-back unless the drafter materially changes the
message thesis. Ethics re-gating is required if the drafter's rewrite
introduces new claims, testimonials, or urgency framing.

## Returned Envelope

On final `PASS` / `PASS_WITH_NOTES`:

```json
{
  "phase": "delivered",
  "form": "<unchanged>",
  "brief": { "...": "unchanged" },
  "message_thesis": "...",
  "draft": "<final copy>",
  "voice_quadrant": { "primary": "Q1 | Q2 | Q3 | Q4", "edge": "...", "rationale": "...", "schwartz_alignment": "..." },
  "tone_notes": "...",
  "ethics_verdict": "PASS",
  "form_verdict": "PASS | PASS_WITH_NOTES",
  "form_findings": "<optional 8b flag notes>",
  "next_stage": null
}
```

On `NEEDS_REVISION`: envelope returned to Phase 4 drafter with
`form_findings` and incremented `revise_round_count`.

## Do NOT

- Do NOT edit the draft directly — loop back to the Phase 4 drafter.
- Do NOT skip 8b when 8a passes — flag-level issues (weak Affinity,
  abstract Evidence, generic catchcopy) are the whole point of a
  separate SHOULD gate.
- Do NOT paraphrase `checklists/persuasion-framework-adherence-checklist.md`
  or `rubrics/form-appropriate-gate.md` — byte-identical copies from
  `domain-teams/skills/copywriting-team/`.
- Do NOT run this skill before `ethics_verdict == "PASS"`.
- Do NOT exceed 2 revise rounds silently — escalate to the user on
  round 3.

## Next Stage

- Final `PASS` / `PASS_WITH_NOTES` → delivery (no `next_stage`).
- `NEEDS_REVISION` → the Phase 4 drafter matching `envelope.form`.
