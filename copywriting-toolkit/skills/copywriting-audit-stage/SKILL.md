---
name: copywriting-audit-stage
description: Audit existing external copy you did not draft — competitor / legacy / A/B variant — through voice positioning, tone, ethics, and form checks. Use when you have pre-existing copy text (not a new brief) and want review / critique / rewrite suggestions. Not for new copy creation — use using-copywriting-toolkit to start a fresh pipeline. 文案審查・既存コピー監査。
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

Formal schema used by `using-copywriting-toolkit` router for bounce-back routing. On violation, router emits the bounce-back envelope defined in `../../CLAUDE.md §Envelope Violation`. Audit-stage is an alternate entry; it does NOT require the full intake envelope.

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
Phase 5 — Voice Positioning  reuse copywriting-voice-quadrant-stage
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

If Phase 3 emits rewrite variants (optional output, 1-3 variants typical), each variant undergoes an **independent sub-pipeline** through Phase 7 + Phase 8. This is a divergent fan-out from the main audit flow.

**Variant re-gating loop — formal contract:**

For each `rewrite_variants[i]`:

1. **Construct per-variant envelope** — clone the main envelope, replace `draft` with `rewrite_variants[i].text`, reset `retries.revise_round_count` to 0 (each variant has its own revision budget), preserve all other fields (voice_quadrant from main Phase 5 result, tone_notes from Phase 6, brief unchanged).
2. **Run Phase 7 ethics-check** on the variant draft. Verdict → `rewrite_variants[i].ethics_verdict`.
3. **If ethics PASS** → run Phase 8 form-check. Verdict → `rewrite_variants[i].form_verdict`.
4. **If ethics NEEDS_REVISION** → skip Phase 8 for this variant; record ethics findings; variant is reported as "gate-blocked" but not auto-revised (audit does not re-draft — it reports).
5. **Per-variant revise budget**: `revise_round_count < 2` → allow auto-revise for FIXABLE at Phase 7 or 8; `>= 2` → stop for that variant.
6. **Aggregate total_retries**: sum across main + all variants. If `total_retries >= 4` at ANY point (main audit + variant gates combined), HALT entire audit and ask user — do not silently keep re-gating.

**Execution strategy** — serial by default. Parallel execution is permitted if the orchestrator supports isolated variant sub-envelopes AND guarantees `retries.total_retries` aggregation atomicity. Default to serial to keep the counter coherent.

**Voice Consistency SHOULD gate runs cross-variant** — once after all variants are evaluated, the Phase 6 voice-consistency rubric checks that the variants collectively deliver a stable voice. This is one gate per audit run, not per variant.

**Rewrites follow 谷山 「なんかいいよね禁止」** — each variant must justify with 3 concrete reasons covering (a) what benefit / to whom, (b) why new vs existing copy, (c) why resonant in the given context. Description-type rationale ("it reads better" / "it's punchier") is rejected; the reason must name a concrete audience / benefit / rhetorical mechanism. This rule is applied locally here; audit does not delegate to `copywriting-ideation`.

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
  "voice_quadrant": { "primary": "Q1 | Q2 | Q3 | Q4", "edge": "...", "rationale": "...", "schwartz_alignment": "..." },
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
