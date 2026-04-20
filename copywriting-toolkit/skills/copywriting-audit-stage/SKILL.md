---
name: copywriting-audit-stage
description: Alternate pipeline entry — audit existing external copy through Phases 5-8 (voice positioning, tone, ethics, form). Use when reviewing copy you did not draft (competitor, legacy, A/B variant). 文案審查・既存コピー監査。
---

# copywriting-audit-stage

Alternate entry point for the `copywriting-toolkit` pipeline. Accepts pre-existing external copy (a draft you did NOT produce — competitor copy, legacy campaigns, A/B variants, client-supplied content) and runs it through **Phases 5-8** of the standard pipeline. Skips Phase 0-4 (no intake, no ideation, no neta injection, no draft) because the draft already exists.

Output: issue list by severity + suggested improvements (+ optional rewrites), with all the same gate verdicts the drafting pipeline would produce.

## When to Use

- Review competitor campaigns for benchmarking
- Audit legacy copy inherited from prior agency / internal team
- Analyse A/B variants to diagnose underperformance
- Client hands you existing LP / email / banner and asks "what's wrong?"
- Pre-launch QA on copy the user produced outside this toolkit

Skip when:

- You need to generate new copy → use `using-copywriting-toolkit` router → full pipeline
- Audit target is technical docs / UX microcopy / PRODUCT-SPEC → out of scope (see `using-copywriting-toolkit` §Out of Scope)
- You need translation / localisation judgement rather than persuasion audit → research-team / design-team

## Input Envelope

Accepts a compact envelope emitted by `using-copywriting-toolkit` audit branch:

```json
{
  "phase": "phase-audit-entry",
  "form": "long-form-pasona | long-form-extended | mid-form | short-form | light-action | unknown",
  "brief": {
    "product": "... optional ...",
    "audience": "... optional ...",
    "voice_reference": "... optional ...",
    "review_focus": "structure | ethics | voice | all"
  },
  "external_copy": "<FULL TEXT of the copy under review — not a summary>",
  "next_stage": "copywriting-audit-stage"
}
```

Hard rule: `external_copy` must be the full original text. Audit on summaries collapses the form-adherence + voice-consistency checks.

If `form` is `unknown`, the audit protocol's Phase 1 (Type ID) determines it before downstream gates run.

## Preconditions

Formal schema used by `using-copywriting-toolkit` router for bounce-back routing. Audit-stage is an alternate entry; it does NOT require the full intake envelope.

### Required envelope fields (Level 1 — BLOCKED if missing)

| Field | Type | Source | Notes |
|---|---|---|---|
| `phase` | enum | router | must equal `phase-audit-entry` |
| `external_copy` | string | user | FULL TEXT of copy under review — summaries rejected |
| `brief.review_focus` | enum | user OR default | `structure` / `ethics` / `voice` / `all` (default `all`) |

### Optional fields (fill via defaults if absent)

| Field | Type | Notes |
|---|---|---|
| `form` | enum | if `unknown`, protocol Step 1 Type ID resolves it before Phase 5-8 |
| `brief.product` | string | helpful for context; not strictly required for detection |
| `brief.target_audience` | string | helpful for voice-consistency gate |
| `brief.voice_reference` | string | if supplied, gates judge fidelity; if absent, audit marks voice as "declared-by-artifact" |

### Upstream bounce target on violation

- `external_copy` missing / summary-only → bounce to `using-copywriting-toolkit` to re-collect full text from user
- `external_copy` empty / placeholder → do NOT proceed; audit has nothing to judge

Audit-stage reuses Phase 5-8 gates. If any downstream gate bounces (e.g. `voice_quadrant` not determinable because copy is non-prose), audit-stage halts and surfaces the block — it does NOT paper over with placeholder data.

## Workflow

Uses `protocols/copy-audit.md` (cp'd verbatim from `domain-teams/skills/copywriting-team/`).

```
Phase 1 — Type ID            protocol Step 1   form type + framework detected
Phase 2 — Diagnose           protocol Step 2   issue list by severity
Phase 3 — Suggest            protocol Step 3   improvement recommendations
                                               (+ optional rewrites)
Phase 5 — Voice Positioning  reuse copywriting-voice-positioning-stage
                                               assign voice_quadrant
Phase 6 — Voice Tone         reuse copywriting-voice-tone-stage
                                               tone_notes + voice-consistency
                                               SHOULD gate
Phase 7 — Ethics Gate        reuse copywriting-ethics-check-stage
                                               MUST gate (non-negotiable)
Phase 8 — Form Gate          reuse copywriting-form-check-stage
                                               MUST gate (framework adherence,
                                               length, CTA)
```

Phases 5-8 run on the `external_copy` as if it were a Phase 4 draft. They use the same evaluator (`../../agents/copywriter-evaluator.md`) and the same gate files — no duplicated checklists / rubrics in this skill directory.

### When rewrites are produced

If Phase 3 emits rewrite variants (optional output), those rewrites trigger:

- Additional ethics re-gate on each rewrite (Phase 7)
- Additional form re-gate on each rewrite (Phase 8)
- Voice consistency SHOULD gate across all variants (Phase 6 rubric)

Rewrites follow 谷山 「なんかいいよね禁止」 — each variant must justify with 3 concrete reasons covering (a) what benefit / to whom, (b) why new vs existing copy, (c) why resonant in the given context. Description-type rationale ("it reads better" / "it's punchier") is rejected; the reason must name a concrete audience / benefit / rhetorical mechanism. This rule is applied locally here; audit does not delegate to `copywriting-ideation`.

## Output

Audit report envelope:

```json
{
  "phase": "audit-complete",
  "form_detected": "long-form-pasona | ...",
  "framework_detected": "pasona | bf | quest | crema | ...",
  "issues": [
    {
      "severity": "critical | high | medium | low",
      "category": "structure | ethics | voice | length | cta",
      "location": "<stage / line / section>",
      "finding": "...",
      "suggestion": "..."
    }
  ],
  "rewrite_variants": [
    {
      "variant_id": "A",
      "text": "...",
      "three_reasons": ["...", "...", "..."],
      "ethics_verdict": "PASS | PASS_WITH_NOTES | NEEDS_REVISION",
      "form_verdict": "PASS | PASS_WITH_NOTES | NEEDS_REVISION"
    }
  ],
  "voice_quadrant": "Q1-Q4",
  "tone_notes": "...",
  "ethics_verdict_on_original": "PASS | PASS_WITH_NOTES | NEEDS_REVISION",
  "form_verdict_on_original": "PASS | PASS_WITH_NOTES | NEEDS_REVISION",
  "next_stage": null
}
```

## Loop-back

If the user asks for revised rewrites (not just findings):

- Route rewrites to `copywriting-voice-tone-stage` → `copywriting-ethics-check-stage` → `copywriting-form-check-stage` (reuse the main pipeline's loop-back cap: 2 revise rounds per variant, then human escalation).
- Do NOT re-enter Phase 4 drafter skills from audit — if the user wants a full rewrite from scratch, exit audit and use `using-copywriting-toolkit` to enter the standard pipeline.

## Hard Rules

- **Full text, not summary** — audit on summaries is invalid.
- **Original copy is never modified** — audit produces reports + optional variants; the original survives unchanged in the envelope.
- **Ethics gate verdict on original is reported even if NEEDS_REVISION** — a failing audit is a valid audit; the user needs to know the legal / ethical exposure.
- **Framework detection before gates** — form-check-stage cannot run without knowing the framework. If the copy resists classification, the protocol's Phase 1 returns "framework_detected: unknown" and form-check-stage runs in exploratory mode per its own §Unknown-form handling.
- **Do NOT duplicate gate files here** — this skill reuses `copywriting-ethics-check-stage/` + `copywriting-form-check-stage/` + `copywriting-voice-tone-stage/` gates via the orchestrator. Drift-sync risk avoided.

## Next Stage

- On completion: return audit report to user. No downstream stage.
- On user request for revised variants: enter the Phase 6 → 7 → 8 sub-loop described above.
