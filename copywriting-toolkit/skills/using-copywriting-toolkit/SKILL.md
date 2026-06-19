---
name: using-copywriting-toolkit
description: |
  Router for copywriting — use BEFORE any draft, ideation, audit, or tagline/headline work on a raw brief (landing page / email / sales letter / SNS / voice guide / audit). Routes new briefs, audits, or resumed pipelines via a 9-phase decision tree.
---

# using-copywriting-toolkit

Entry router + validator for the `copywriting-toolkit` plugin. Three responsibilities:

1. **Route** — inspect the user's raw request, place it on the 9-phase pipeline (plus audit alt-entry), hand off to the correct skill with a structured envelope.
2. **Validate** — before every skill launch, load the target skill's `## Preconditions` schema and check the envelope. On violation, emit a bounce-back envelope (see `../../CLAUDE.md §Envelope Violation`) and route upstream instead of launching.
3. **Qualify for Express Mode** — on a raw new brief, check whether Level 1 fields are all present (`protocols/phase-decision-tree.md §Step 0.5`). If yes, dispatch `copywriting-intake` in Express Mode; otherwise default to Q1-Q10 full intake.

This skill does NOT draft copy, run gates, or produce verdicts. It only routes, validates, and packages the handoff envelope. Each downstream skill owns its own SKILL.md, standards, and (where applicable) gates.

## When to Use

- User arrives with a copywriting request but has not chosen a specific skill (raw intent: "write an LP", "headline options", "audit this email").
- A previous skill finished its phase and the envelope needs to be routed to the next stage.
- The user has pre-existing external copy and wants it evaluated (audit alt-entry).

## When NOT to Use

- You already know the exact target skill (e.g. user explicitly says "run the form gate"). Invoke that skill directly.
- Task is outside copywriting scope — see the "Out of scope" section below and hand off to the correct team.

## Out of Scope — Hand Off to Another Team

| Need | Target |
|---|---|
| Technical docs / API references | `domain-teams:docs-team` |
| Product strategy / PRODUCT-SPEC authoring | `domain-teams:planning-team` |
| In-screen UX microcopy (buttons, errors, empty states) | `domain-teams:design-team` |
| Market / competitive / audience research | `domain-teams:research-team` |
| Source code or template implementation of copy | `domain-teams:code-team` |

Boundary with `planning-team`: planning writes the value-proposition thesis; this toolkit writes the expression of that thesis. If the brief reveals thesis-level ambiguity during Phase 1, see "Loose Coupling to planning-team" below.

## 9-Phase Pipeline (Primary Path)

```
Phase 0  Intake                    copywriting-intake              mandatory
Phase 1  Message Confirmation      copywriting-intake (inline)     mandatory, loose recommend planning-team
Phase 2  Ideation                  copywriting-ideation            skippable if brief is concrete
Phase 3  Neta Decision             copywriting-neta-injection      skippable; hybrid pre-draft or post-draft
Phase 4  Form-Specific Draft       one of 5 workflow skills        mandatory — form selection tree below
Phase 5  Voice Quadrant Position   copywriting-voice-quadrant-stage   mandatory
Phase 6  Voice Tone Tuning         copywriting-voice-tone-stage    mandatory
Phase 7  Ethics Gate               copywriting-ethics-check-stage  mandatory, evaluator-only
Phase 8  Form Gate                 copywriting-form-check-stage    mandatory, evaluator-only
```

**Alt entry**: `copywriting-audit-stage` accepts pre-existing external copy and runs phases 5-8 against it (no ideation / draft). See "Audit Alt-Entry" below.

## Phase Decision Tree (Routing Questions)

Walk the user's request top-down. Stop at the first match and hand off. Detailed questioning script lives in `protocols/phase-decision-tree.md` — read and execute that protocol when routing.

```
Q0. Does the user supply existing external copy and ask for review / critique / A/B suggestions?
    YES → Route to audit alt-entry: copywriting-audit-stage
    NO  → continue

Q0.5 (Shape A only). Does the raw brief carry all Level 1 fields for the predicted form?
     (Run Express Qualification Check per `protocols/phase-decision-tree.md §Step 0.5`)
    YES → Route to copywriting-intake with mode=express → single-turn confirmation
    NO  → Route to copywriting-intake with mode=full-q1-q10

Q1. Has Phase 0 Intake been completed (is there a confirmed Understanding Summary)?
    NO  → Route to copywriting-intake (Q0.5 decides Express vs Q1-Q10)
    YES → continue

Q2. Is the message thesis clear (product / audience / goal / awareness level defined)?
    NO  → Re-enter copywriting-intake Phase 1; if thesis-level, surface planning-team recommendation (loose)
    YES → continue

Q3. Did the user request candidate angles / headline options / ideation before drafting?
     OR is this a complex brief (multi-channel, ambiguous target, SNS-native, cultural)?
    YES → Route to copywriting-ideation (Phase 2)
    NO  → continue (skip Phase 2 if brief already concrete)

Q4. Did intake set neta opt-in = Yes AND neta timing = bake-in (pre-draft)?
    YES → Route to copywriting-neta-injection (Phase 3 pre-draft)
    NO  → continue

Q5. Route to the correct Phase 4 form skill — see "Form Selection Tree" below.

(after Phase 4 draft returns)

Q6. Neta opt-in = Yes AND neta timing = overlay (post-draft)?
    YES → Route to copywriting-neta-injection (Phase 3 overlay)
    NO  → continue

Q7. → copywriting-voice-quadrant-stage (Phase 5)
Q8. → copywriting-voice-tone-stage       (Phase 6)
Q9. → copywriting-ethics-check-stage     (Phase 7, evaluator-only gate)
Q10.→ copywriting-form-check-stage       (Phase 8, evaluator-only gate)
```

Hand off to `copywriting-intake` with envelope `{ "phase": "phase-0-intake", "raw_request": "...", "next_stage": "copywriting-intake" }` when Q1 fails.

## Form Selection Tree (Phase 4)

Phase 4 chooses ONE of five workflow skills. Decision axis: form size × action weight × framework family. Mirror the original `copywriting-team` triggers.

```
Q-F1. Is the brief a review / critique of existing copy?
      YES → audit alt-entry (not Phase 4)
      NO  → continue

Q-F2. Headline / tagline / SNS post / banner / CM title (7-15 char target)?
      YES → copywriting-short-form         [AIDMA A+I + 5 切入點 + 谷山 なんかいいよね禁止]
      NO  → continue

Q-F3. EC product description (Rakuten / Amazon JP / in-store POP / presentation)?
      YES → copywriting-mid-form           [BEAF — Benefit → Evidence → Advantage → Feature]
      NO  → continue

Q-F4. Light action target — email opt-in, newsletter, free download, LINE 登録,
      SNS post with light CTA, or any micro-conversion (Kaushik 2007)?
      YES → copywriting-light-action       [PREP for no-CTA logical payload;
                                            CREMA for explicit Action conversions]
      NO  → continue

Q-F5. Long-form JP-leaning LP, sales letter, 記事広告, email campaign?
      YES → copywriting-long-form-pasona   [PASONA / 新 PASONA / PASBECONA — 神田 canon]
      NO  → continue

Q-F6. Long-form EN / international LP, coaching/consulting sales page, story-driven
      sales letter, education-first or shepherd-guide positioning?
      YES → copywriting-long-form-extended [QUEST Fortin 2005 / PASTOR Edwards 2016]
      NO  → re-enter intake — form indeterminate
```

Selection heuristics:

- **short-form**: 3-秒ルール readable, 7-15 chars, single-point compression.
- **mid-form**: 100-600 chars, product-centric, Benefit-first discipline.
- **long-form-pasona**: JP audience, high-emotion positioning, Problem→Affinity→Solution arc, heavy-action (purchase) macro-conversion.
- **long-form-extended**: non-JP audience OR expertise-based positioning (QUEST) OR personal-story shepherd positioning (PASTOR). Cross-pollination with PASONA documented inside that skill's standard.
- **light-action**: NEVER for high-ticket purchase — route back to pasona / extended if brief turns macro-conversion. CREMA is the default; PREP only when no CTA or share-triggering logical content.

Hand off to `copywriting-<form>` with envelope:

```json
{
  "phase": "phase-4-draft",
  "form": "<short-form | mid-form | long-form-pasona | long-form-extended | light-action>",
  "brief": { "...": "from intake" },
  "message_thesis": "...",
  "ideation_pool": ["... if Phase 2 ran ..."],
  "neta_candidates": ["... if Phase 3 ran pre-draft ..."],
  "next_stage": "copywriting-<form>"
}
```

## Neta Timing Decision (Hybrid)

`copywriting-neta-injection` supports two placements. The router asks once during intake handoff which the user wants:

- **bake-in (pre-draft)**: run Phase 3 BEFORE Phase 4. Draft absorbs neta candidates as raw material. Good when the neta IS the angle (meme-driven campaign, parody-rooted KV).
- **overlay (post-draft)**: run Phase 4 FIRST (clean framework-adherent draft), then Phase 3 rewrites 2-3 variants with neta swapped in. Good when neta is decorative rather than load-bearing, or when testing A/B with/without neta.

If the user is undecided, default to **overlay** — it keeps the base draft's framework integrity intact and makes neta safety easier to isolate at Phase 3's own gate.

Hand off to `copywriting-neta-injection` with envelope containing `"neta_timing": "bake-in" | "overlay"` and the current phase context.

## Loose Coupling to planning-team

Inside Phase 1 (Message Confirmation) the intake skill may detect thesis-level ambiguity. This router surfaces the same hint when the raw request shows:

- Product positioning not yet defined ("we're launching something, help us figure out how to pitch it").
- Target audience undefined AND cannot be inferred from brief.
- Goal is strategic rather than expressive ("what should our brand voice be across all channels?").

**Action**: RECOMMEND (not enforce):

> "This looks thesis-level rather than expression-level. Consider running `domain-teams:planning-team` first to clarify the value proposition, then return here for expression. You may proceed in copywriting-toolkit anyway — no hard block."

User decides. No auto-delegation. No forced invocation. Record the recommendation in the envelope's `notes` field so downstream skills know it was raised.

## Audit Alt-Entry

When user arrives with pre-existing external copy to evaluate:

Hand off to `copywriting-audit-stage` with envelope:

```json
{
  "phase": "audit",
  "existing_copy": "...",
  "audit_focus": "<framework | ethics | voice | form | all>",
  "form_hint": "<if known>",
  "next_stage": "copywriting-audit-stage"
}
```

The audit skill runs its own Phase 0 intake (light — review focus), identifies form + framework, diagnoses issues by severity, and may chain into Phases 5-8 gate skills to produce verdicts on the external copy. Rewrite variants (if requested) route through the ethics gate before delivery.

## Handoff Envelope Schema

Canonical between-skill artifact. Every downstream skill reads this envelope, appends its layer, updates `next_stage`, and returns. Envelope is the single source of truth — no side-channel state.

```json
{
  "phase": "phase-N-<name>",
  "form": "short-form | mid-form | long-form-pasona | long-form-extended | light-action | null",
  "brief": {
    "product": "...",
    "audience": "...",
    "channel": "...",
    "output_language": "ja | en | zh-TW | ...",
    "awareness_level": "unaware | problem-aware | solution-aware | product-aware | most-aware",
    "action_weight": "light | heavy",
    "voice_reference": "... optional ...",
    "neta_opt_in": true,
    "neta_timing": "bake-in | overlay | null",
    "level_1_fields": { "...": "..." },
    "level_2_fields": { "...": "..." },
    "level_3_fields": { "...": "..." }
  },
  "message_thesis": "...",
  "ideation_pool": ["... optional if Phase 2 ran ..."],
  "neta_candidates": ["... optional if Phase 3 ran pre-draft ..."],
  "draft": "... populated from Phase 4 onward ...",
  "voice_quadrant": "... populated from Phase 5 ...",
  "voice_tone": "... populated from Phase 6 ...",
  "gate_verdicts": {
    "intake_completeness": "PASS | PASS_WITH_NOTES | NEEDS_REVISION | null",
    "framework_adherence": "...",
    "ethics": "...",
    "voice_consistency": "...",
    "form_appropriate": "...",
    "neta_safety": "..."
  },
  "notes": ["loose-coupling recommendations, reroute hints, etc."],
  "next_stage": "copywriting-<skill-name>"
}
```

Schema rules:

1. **Single-source truth**: downstream skills mutate `envelope.draft`, append to `envelope.gate_verdicts`, push to `envelope.notes` — never create side channels.
2. **next_stage is always present**: null only after final gate passes (pipeline done).
3. **Gate verdicts bubble up**: if any MUST gate returns `NEEDS_REVISION`, `next_stage` returns to the appropriate earlier phase and a note records the revision loop count.
4. **Evaluator-only phases (7, 8, audit)**: produce verdicts, do NOT mutate `envelope.draft`.
5. **Schema fidelity**: each skill validates incoming envelope against this shape before executing; malformed envelopes return a structured error, not a best-effort mutation.

## Routing Outputs — Quick Reference

| User Signal | Route | Envelope `next_stage` |
|---|---|---|
| Raw request, no prior intake | `copywriting-intake` | `copywriting-intake` |
| Intake done, need candidate angles | `copywriting-ideation` | `copywriting-ideation` |
| Intake done, neta bake-in | `copywriting-neta-injection` | `copywriting-neta-injection` |
| Draft phase, short form | `copywriting-short-form` | `copywriting-short-form` |
| Draft phase, mid form | `copywriting-mid-form` | `copywriting-mid-form` |
| Draft phase, long PASONA | `copywriting-long-form-pasona` | `copywriting-long-form-pasona` |
| Draft phase, long QUEST/PASTOR | `copywriting-long-form-extended` | `copywriting-long-form-extended` |
| Draft phase, light action | `copywriting-light-action` | `copywriting-light-action` |
| Draft done, neta overlay | `copywriting-neta-injection` | `copywriting-neta-injection` |
| Draft done, position voice | `copywriting-voice-quadrant-stage` | `copywriting-voice-quadrant-stage` |
| Voice positioned, tune tone | `copywriting-voice-tone-stage` | `copywriting-voice-tone-stage` |
| Tone tuned, run ethics | `copywriting-ethics-check-stage` | `copywriting-ethics-check-stage` |
| Ethics passed, run form gate | `copywriting-form-check-stage` | `copywriting-form-check-stage` |
| Existing external copy | `copywriting-audit-stage` | `copywriting-audit-stage` |
| Thesis-level ambiguity | (still `copywriting-intake`) with planning-team recommend note | `copywriting-intake` |

## Resource Manifest

- Protocol: `protocols/phase-decision-tree.md` — detailed questioning script + branching logic.
- Research archive: `research/grounding-v4.*.md` — evolution history of the original `copywriting-team` (plugin-level archive, verbatim copies from source).

## Behavioral Rules

- Router **does not draft copy, run gates, or produce verdicts**. It only routes and packages envelopes.
- Every outbound handoff ends with an explicit envelope — no implicit state.
- If routing is ambiguous, ask the user exactly one clarifying question (from `protocols/phase-decision-tree.md`) rather than guessing.
- Preserve envelope shape strictly — downstream skills rely on schema fidelity.
- Never short-circuit Phase 0 Intake. A seemingly-complete request may still lack Schwartz awareness level, voice reference, or action weight.

## Empty Invocation Fallback

If the router is invoked with no clear signal:

1. Summarize the 9-phase pipeline + audit alt-entry in one paragraph for orientation.
2. Ask: "What is the raw request? (LP / email / headline / audit / something else)"
3. Route once answered — hand off to `copywriting-intake` as the safe default when still unclear.

## Cross-Plugin Delegation Note

- `planning-team` — loose recommend on thesis-level ambiguity (Phase 1). No auto-invoke.
- `design-team` — recommend when UX microcopy is the actual need.
- `docs-team` — recommend when technical documentation is dressed as "copy".

No other cross-plugin delegation is wired in v1.0.0.
