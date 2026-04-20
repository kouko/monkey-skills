---
name: copywriting-ethics-check-stage
description: Check draft copy for 景品表示法 / FTC Endorsement / 優良誤認 / 不實廣告 / Cialdini dark-pattern compliance. Use when auditing a draft for legal + ethics risk, or called by the pipeline as Phase 7 MUST gate (evaluator-only; NEEDS_REVISION blocks delivery). 倫理ゲート・広告表示法チェック。倫理審查・不實廣告。
---

# copywriting-ethics-check-stage

Phase 7 — **evaluator-only ethics MUST gate**. Non-negotiable. This skill
does not draft, rewrite, or "soften" copy. It only launches the
evaluator against a fixed checklist, receives a verdict, and decides
whether Phase 8 (form gate) may run.

> Position in pipeline: … → `copywriting-voice-tone-stage` → **this
> skill (Phase 7)** → `copywriting-form-check-stage` (Phase 8) →
> delivery.

## Role Constraint (read first)

- **Evaluator-only** — this skill MUST NOT produce, edit, or paraphrase
  any draft content. Behavioral contract from `../../agents/copywriter-evaluator.md`
  §Rules: "Do NOT fix problems or produce revised artifacts. Your job
  is to judge, not to do."
- **MUST gate** — the verdict is binding. `NEEDS_REVISION` here halts
  the pipeline regardless of how well later gates would score. Do not
  forward-run Phase 8 to "check anyway."
- **Non-negotiable** — legal (景品表示法 / FTC Endorsement Guides /
  ステマ告示) and ethical (Brignull dark patterns / Cialdini misuse /
  小霜「嘘をつかない」) boundaries are not subject to user override.
  The user may edit the draft and re-submit, but cannot waive a
  `FAIL_FATAL`.

## Input — Envelope Shape

Inherits the plugin's handoff envelope (see `../../CLAUDE.md §Handoff
Envelope`). At this phase the envelope MUST already carry:

```json
{
  "phase": "phase-7-ethics",
  "form": "<short-form | mid-form | long-form-pasona | long-form-extended | light-action>",
  "brief": { "...": "from Phase 0 intake" },
  "message_thesis": "...",
  "draft": "<polished draft from Phase 6>",
  "voice_quadrant": {
    "primary": "Q1 | Q2 | Q3 | Q4",
    "edge": "Q2-Q3 | Q1-Q4 | null",
    "rationale": "<from Phase 5>",
    "schwartz_alignment": "ok | hard_rule_applied | conflict_flagged"
  },
  "tone_notes": "<from Phase 6>",
  "next_stage": "copywriting-ethics-check-stage"
}
```

If `draft`, `voice_quadrant`, or `tone_notes` are missing, stop and
return control to the orchestrator — do not launch the evaluator
against an incomplete envelope.

### Artifact scope — what the evaluator judges

The evaluator judges **both** the final `draft` text AND brief-level claims that will accompany the delivery in the real placement context. This distinction matters for borderline cases:

- **In-draft claims** are the primary artifact. Any 景表法 / FTC / dark-pattern violation present in the draft triggers a FATAL directly.
- **Brief-level claims** that a reasonable reader would understand to accompany the copy in the real channel (LP hero + sub-copy, email subject + body, product page body) are ALSO in scope. E.g., "比市售連鎖咖啡便宜 30%" stated in `brief.value_proposition` but NOT in `draft` is still subject to adjudication if the delivery context (a landing page) would print both.
- **Upstream grill findings carried forward** from Express Mode as T2 benchmark-required flags are adjudicated here. If the benchmark was supplied between intake and Phase 7, the evaluator PASSES the claim; if not, the evaluator returns FAIL_FATAL.

**Rationale**: the copywriter agent can strategically drop a FATAL-candidate claim from the draft itself (per `copywriter.md §Persona Discipline` rule 5) to slip past narrow draft-only adjudication. That is good discipline but insufficient legal protection — the brand's real-world placement will still include the brief-level value proposition in the page surrounds. Phase 7 protects against that gap by reading `brief` as context, not just `draft` as artifact.

**Limit of scope**: claims in `ideation_pool` or `neta_candidates` that were discarded at convergence are NOT in scope. The evaluator does not resurrect rejected candidates.

## Preconditions

Formal schema used by `using-copywriting-toolkit` router for bounce-back routing. On violation, router emits the bounce-back envelope defined in `../../CLAUDE.md §Envelope Violation`.

### Required envelope fields (Level 1 — BLOCKED if missing)

| Field | Type | Source | Notes |
|---|---|---|---|
| `phase` | enum | Phase 6 | must equal `phase-7-ethics` (router sets this when routing to this skill) |
| `draft` | string | Phase 4 / 6 | non-empty; polished after tone tuning |
| `voice_quadrant` | object | Phase 5 | needed as context (ethics does not judge voice but records positioning for audit trail) |
| `tone_notes` | object | Phase 6 | needed for PASS_WITH_NOTES auto-revise targeting |
| `form` | enum | intake | determines which legal / ethics dimensions apply more aggressively |
| `brief` | object | intake | original claims / testimonials / urgency framing subject to FTC / 景表法 |

### Bounce targets on violation

- `draft` missing → `copywriting-<form>` (Phase 4 drafter)
- `voice_quadrant` missing → `copywriting-voice-quadrant-stage` (Phase 5)
- `tone_notes` missing → `copywriting-voice-tone-stage` (Phase 6)
- `form` or `brief` missing → `copywriting-intake`

Ethics gate MUST NOT run on an incomplete envelope — partial artifacts yield false-positive PASS verdicts on claims the evaluator cannot see in full context.

## Gate Definition

| Layer | File | Mode |
|---|---|---|
| Standard (context) | `standards/persuasion-ethics.md` | Reference material — dual-track (legal + ethical) canon |
| Gate (checklist) | `checklists/ethics-checklist.md` | Checklist Mode (PASS / FAIL_FATAL / FAIL_FIXABLE / N/A per item) |

Coverage (see `standards/persuasion-ethics.md` for canonical
definitions):

1. **Legal hard boundaries**
   - 景品表示法 (2023 amendment, effective 2024-10-01) — 優良誤認 /
     有利誤認 / 打消し表示 / No.3 告示 (ステマ, effective
     2023-10-01)
   - FTC Endorsement Guides (16 CFR Part 255, effective 2023-07-01) —
     material connection disclosure, atypical-result disclaimer,
     employee / influencer / expert endorsement rules
2. **Ethical soft boundaries**
   - Brignull / `deceptive.design` 12 dark-pattern taxonomy — false
     urgency, confirmshaming, roach motel, forced continuity, etc.
   - Cialdini 7 influence principles **misuse** audit — scarcity and
     social-proof over-claim, authority fabrication, reciprocity
     coercion
   - 小霜和也「嘘をつかない」principle — no claim the writer cannot
     personally defend

### Evaluator hints for common TW/JP D2C patterns

**As of v1.1.0**, evaluator hints live IN the checklist itself. See `checklists/ethics-checklist.md §copywriting-toolkit evaluator hints for common TW/JP D2C patterns` for the canonical list (5 patterns: aggregate-count social-proof, first-in-industry, 市價 dual-pricing, comparative-price without benchmark, repeating false-urgency).

The evaluator agent reads the checklist directly — it will automatically apply these hints without needing to cross-reference this SKILL.md. This SKILL.md section is kept only as a navigation pointer.

(Prior to v1.1.0, hints lived here because the checklist was Tier 1 unmodifiable. The v1.1.0 Provenance & Divergence principle allows Tier 2 additive modification; hints migrated to their natural home. See `../../CLAUDE.md §Provenance & Divergence Principle`.)

## Evaluator Launch

Use `../../agents/copywriter-evaluator.md` (plugin-local evaluator, not
`domain-teams:evaluator`). Per plugin CLAUDE.md §Evaluator, launch
with the input contract from the evaluator agent's own spec:

```
### Resource Paths
- gate_file: <absolute path to>/checklists/ethics-checklist.md
- standards:
    - <absolute path to>/standards/persuasion-ethics.md

### Artifact
<envelope.draft — the polished copy text only>

### Requirements
<original user brief from envelope.brief; include voice_quadrant +
tone_notes as context so the evaluator understands claimed positioning
and tone register when assessing truthfulness / exaggeration>
```

Resolve relative paths to absolute before launching. The evaluator
reads the gate and standard itself (per plugin convention: pass paths,
not file content).

## Output — Verdict Handling

The evaluator returns one of three verdicts (see
`../../agents/copywriter-evaluator.md §Mode 1`):

| Verdict | Meaning | Action |
|---|---|---|
| `PASS` | All items `PASS` or `N/A` | Update envelope: `phase → phase-8-form`, `next_stage → copywriting-form-check-stage`. Hand off. |
| `PASS_WITH_NOTES` | Only `FAIL_FIXABLE` items, no FATALs | Apply evaluator's deterministic notes (formatting / disclosure-wording polish) via a brief auto-revise turn, re-run this gate ONCE, then hand off on re-`PASS`. Never forward-run Phase 8 while a FIXABLE is outstanding. |
| `NEEDS_REVISION` | Any `FAIL_FATAL` | **Stop.** Present the evaluator's per-item findings to the user verbatim. Do NOT auto-rewrite. Do NOT launch Phase 8. Default re-entry: `copywriting-<form>` (Phase 4 drafter) with `ethics_findings` attached to the envelope. User may override to any of the three options below. |

### Stop rule on `NEEDS_REVISION`

Legal / dark-pattern failures require human judgement. The pipeline
MUST halt and ask. **Default re-entry** is the Phase 4 drafter named
in `envelope.form` (matching the router Step 2 table) — the drafter
applies the user's chosen fix in its framework context. **User-
overridable** to:

1. **User hand-edits the draft text directly** and re-submits to Phase 7
   (skip re-drafting). Router accepts `phase: phase-7-ethics` +
   `draft` + user-provided change rationale, re-validates
   Preconditions, re-runs ethics gate.
2. **User restarts Phase 4 drafting with a revised `message_thesis`**
   (a different claim that sidesteps the ethics issue entirely).
   Router routes to Phase 4 drafter with amended envelope.
3. **User drops the claim** — remove the offending paragraph / testimonial
   from the draft and re-enter Phase 7 with the reduced draft.

On any path, `revise_round_count` increments. Per `../../CLAUDE.md
§Envelope Violation`, `total_retries >= 4` HALTS the pipeline and
requires explicit user intervention — the evaluator may have
uncovered a systemic claim problem that no rewrite round will fix.

Unacceptable:

- Auto-rewriting a FATAL-flagged claim to "avoid" the flag.
- Treating legal issues as tone-adjustable via Phase 6.
- Skipping to Phase 8 to "see if form gate passes anyway."

## Returned Envelope

On `PASS` (or `PASS` after a FIXABLE auto-revise round):

```json
{
  "phase": "phase-8-form",
  "form": "<unchanged>",
  "brief": { "...": "unchanged" },
  "message_thesis": "...",
  "draft": "<draft text, unchanged unless FIXABLE auto-revise ran>",
  "voice_quadrant": "...",
  "tone_notes": "...",
  "ethics_verdict": "PASS",
  "ethics_findings": "<optional FIXABLE notes applied>",
  "next_stage": "copywriting-form-check-stage"
}
```

On `NEEDS_REVISION`: do NOT update `phase` / `next_stage`. Return the
unchanged envelope plus the findings block to the user, then stop.

## Do NOT

- Do NOT modify the draft beyond applying literal FIXABLE notes.
- Do NOT paraphrase `checklists/ethics-checklist.md` or
  `standards/persuasion-ethics.md` — they are byte-identical copies
  from `domain-teams/skills/copywriting-team/`. Drift is a CLAUDE.md
  violation.
- Do NOT launch `copywriting-form-check-stage` until this gate
  returns `PASS`.
- Do NOT merge this skill's evaluator logic into Phase 8 to save a
  turn — the two gates are deliberately separate so ethics failure
  cannot be masked by strong form compliance.

## Next Stage

- `PASS` → `copywriting-form-check-stage` (Phase 8, final gate).
- `NEEDS_REVISION` → halt; user decides whether to rework Phase 4
  (draft) or Phase 6 (tone) or drop the claim.
