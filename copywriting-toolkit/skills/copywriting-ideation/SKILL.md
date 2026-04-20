---
name: copywriting-ideation
description: Phase 2 ideation — diverge with 曼陀羅 + Verbalized Sampling + 小霜本能分析; converge with KJ法 + 谷山 なんかいいよね禁止. Use when brief needs candidate angles before drafting. Skippable if brief is concrete. 文案發想。コピー発想。
---

# copywriting-ideation

Phase 2 of the copywriting pipeline. Take the Understanding Summary from `copywriting-intake` and produce 3-5 winning angles (each with a "なぜ良いか" 3-item rationale) that seed the downstream form-specific draft skill (`copywriting-long-form-pasona`, `copywriting-long-form-extended`, `copywriting-mid-form`, `copywriting-short-form`, `copywriting-light-action`).

散らかす（diverge）→ 選ぶ（converge）の 2 段を厳格に分離する。谷山 雅彦の「なんかいいよね禁止」ルールを選ぶ段の出口ゲートに置く。

## When to use

**As of v1.1.0, Phase 2 is MANDATORY — always runs; only its depth varies.** The prior v1.0.x behavior (skippable when brief looked concrete) violated 谷山 discipline's `散らかす → 選ぶ → 磨く` canon (`standards/ideation-taniyama-discipline.md §なんかいいよね禁止` requires every candidate to justify against other candidates, which requires multiple candidates to exist — single-draft delivery is a discipline violation).

Invoke after Phase 1 intake (Understanding Summary confirmed, Intake Completeness gate PASS).

### Depth control

Depth is set by `envelope.ideation_depth` field, populated by router per `using-copywriting-toolkit/protocols/phase-decision-tree.md §Step 3`:

| Depth | Candidates | Execution | Trigger |
|---|---|---|---|
| **scoped** | 8-12 | Single-pass, no parallel subagents; `copywriter` produces inline in one pass through 曼陀羅 center | Default for Express path — brief is Level-1-complete + concrete |
| **standard** | 40-64 | Parallel subagents × 曼陀羅 8-direction fan-out (base `copy-ideation-parallel.md`) | Default for Q1-Q10 path |
| **full** | 64-100+ | Standard + advanced overlays (小霜 instinct axis, ULSSAS seed filter, jp-lineage voice calibration) per `copy-ideation-advanced.md` | Multi-channel, SNS-native, cultural campaign, ambiguous target, innovative-positioning brief |

### Skip — rare, rationale-required

Skip is NEVER the default path in v1.1.0. Valid skip scenarios:

- Audit workflow (`copywriting-audit-stage` — audit reviews existing copy, not new ideation)
- Pre-existing approved angle from a prior session's Phase 2 output
- A/B test explicitly baselined against a known-winner variant
- External concept already approved by client; this run is a formal re-draft only

When skipping, envelope MUST carry `ideation_skip_rationale: <explicit reason>`. Silent skips are rejected by the Intake Completeness gate. If user requests skip without valid rationale, router force-upgrades to scoped depth (10-second cost, closes the canon gap).

## Input

From `copywriting-intake` handoff envelope:

- `brief` — value proposition / key message (from planning-team or user)
- `brief.target` — target audience description (persona draft or segment)
- `brief.form` — long / mid / short / light-action (affects Phase 3 handoff target)
- `message_thesis` — confirmed single-sentence thesis (Phase 1 output)

If any of the 3 required inputs (value prop / target / form) is missing, HALT and return to `copywriting-intake`. Ideation cannot substitute for intake.

## Preconditions

Formal schema used by `using-copywriting-toolkit` router for bounce-back routing. On violation, router emits the bounce-back envelope defined in `../../CLAUDE.md §Envelope Violation`.

### Required envelope fields (Level 1 — BLOCKED if missing)

| Field | Type | Source phase | Notes |
|---|---|---|---|
| `phase` | enum | intake or express | one of `phase-1-confirmed`, `phase-express-confirmed` |
| `form` | enum | intake | `long-form-pasona` / `long-form-extended` / `mid-form` / `short-form` / `light-action` — determines Phase 3 handoff target |
| `brief.product` | string | intake | non-empty |
| `brief.value_proposition` | string | intake | single-sentence |
| `brief.target_audience` | string | intake | at least one concrete demographic / persona |
| `message_thesis` | string | intake | confirmed 1-sentence core message |
| `gate_verdict` | enum | intake | `PASS` or `PASS_WITH_NOTES` (from Intake Completeness MUST gate) |

### Optional envelope fields (Level 2/3)

| Field | Type | Notes |
|---|---|---|
| `brief.voice_reference` | string | if present, activates advanced overlay voice-calibration signal |
| `brief.schwartz_level` | enum 1-5 | if present, downstream Phase 5 routing honours Schwartz × Quadrant table |
| `brief.neta_opt_in` | bool | default `false` |
| `ideation_overlay_hint` | enum | `multi-channel` / `sns-native` / `cultural` / `ambiguous-target` / `innovative-positioning` — any triggers advanced overlay |

### Upstream bounce target on violation

`copywriting-intake` — any Level 1 field missing means intake did not complete; loop back and surface the missing field to the user.

## Output

- 3-5 winning angles — each with body + Mandal-Art direction tag + "なぜ良いか" 3-item rationale
- 3-5 runner-up candidates (Phase 2b also-rans — reusable for A/B variants)
- Convergence A-type diagram (human-drawn spatial placement, or text hierarchy list as fallback)
- Method selection rationale (which overlays activated, why) — metadata for downstream evaluator
- Divergence evidence — total candidate count, VS probability distribution skew summary (proves mode-collapse mitigation held)

If advanced overlay activated, candidate pool entering Phase 2 is 88-104 candidates (base 64-80 + 小霜 instinct lens 8 + ULSSAS seed lens 8-16). Winners remain 3-5.

## Protocols

Two-layer selection — base protocol always; advanced overlay only on decision rule below.

### Base (always)

`protocols/copy-ideation-parallel.md` — 散らかす → 選ぶ 2-stage parallel ideation.

- Phase 1 発散: parallel subagents fan out 8 directions × 8 candidates = 64 candidates (Mandal-Art path), or 40-80 (VS single-agent path). No self-censorship. 80% safe + 20% unusual ratio.
- Phase 2 収束: KJ法 6 stages (theme → labels → group edit → labeling → A-type diagram → B-type narrative + winner selection). Human / evaluator checkpoint required at group-edit / labeling / A-type / winner-selection.
- Phase 2b: preserve 3-5 runner-ups as appendix.
- Phase 3: handoff with 3 mandatory blocks (winning angles / 3-item rationale / runner-ups).

Do NOT enter Phase 2 before 64-100 candidates are accumulated. Converging under the quantity threshold makes selection non-functional.

### Advanced overlay (decision rule)

Activate `protocols/copy-ideation-advanced.md` when ANY of these hold:

- Multi-channel campaign (same message must land across LP + SNS + email + OOH)
- SNS-native — UGC / retweet / snap-share triggering is explicitly required (ULSSAS seed criteria)
- Cultural campaign — brand voice development or キャッチコピー tied to cultural moment
- Ambiguous target — Understanding Summary lists multiple personas or segments without clear primary
- Innovative positioning — brief explicitly asks to break category convention

When NONE apply, stay with the base protocol. Over-activating the overlay inflates runtime without improving winner quality.

Default combination when uncertain and overlay triggered: 曼陀羅 + 小霜 instinct lens (dual-axis divergence). Pattern A+ (VS probability cap + long-tail directive) is orthogonal — activate only when tail-mode output is genuinely prized over polished mainstream.

## Standards (reference only — do NOT inline-paste)

Base:

- `standards/ideation-mandalart.md` — 今泉 浩晃 マンダラート (1987) + 輔助方向庫 16+ derivative directions. Critical attribution: OW64 / 大谷翔平 chart is 原田隆史 Method + 松村寧雄 lineage, NOT 今泉 mandalart. Do not conflate.
- `standards/ideation-kj-convergence.md` — 川喜田 二郎 KJ 6 stages (1967). Embedding assists Stage 3 initial cluster; human owns kansei-affinity final judgment and A-type spatial placement.
- `standards/ideation-taniyama-discipline.md` — 谷山 雅彦 散らかす→選ぶ→磨く 3-stage discipline + なんかいいよね禁止 ルール + 31 training exercises. Original canon is 3 stages + 31 training; NOT "What × How four-quadrant" (later misattribution).
- `standards/verbalized-sampling.md` — Zhang et al. 2025 VS probability protocol. Probability field is the triggering core. Dropping probability and ending at "list 5" reverts to mode collapse (Ablation §4).

Advanced (only when overlay activated):

- `standards/kosimo-instinct-analysis.md` — 小霜 和也 の本能軸分析。INLINE duplicate: this standard lives ONLY in this ideation skill, not duplicated elsewhere. Use as the secondary divergence axis in 曼陀羅 + 小霜 dual-axis mode.

Scope boundary — this skill is self-contained. It does NOT load standards from other skills. Concepts that belong downstream (SNS-era seed behavior per AISAS / ULSSAS, JP voice lineage signatures, form-specific approach canons) are applied by their owning skills, not here:

- SNS-native seed filtering — `copywriting-long-form-pasona` / `copywriting-light-action` handle ULSSAS / AISAS routing at Phase 4 drafting time via their own `standards/sns-evolution-aisas-ulssas.md`. Ideation's SNS-native trigger (advanced overlay activation rule above) only signals that the downstream drafter should engage SNS behavior models; ideation itself does not apply them.
- JP voice lineage calibration — `copywriting-voice-tone-stage` applies 糸井 / 岩崎 / 眞木 signatures in Phase 6 via its own `standards/jp-copy-craft-lineage.md`. Ideation emits candidates free-form; voice tuning happens after Phase 4 draft.
- Form-specific approach seeds (5 切入點 for short-form, BEAF stages for mid-form) — applied by the form's own drafter skill during Phase 4. Ideation's form-aware rules (Hard rules below) operate on structural layout only, not on standard content.

## Hard rules

- Separate diverge / converge strictly. Never self-censor inside a divergence subagent (`ideation-taniyama-discipline.md` §Anti-Patterns).
- Keep the Verbalized Sampling probability field. Dropping it reverts to mode collapse.
- Human / evaluator checkpoint mandatory at KJ group-edit / labeling / A-type / winner-selection. Embedding cosine alone does NOT complete KJ.
- Winner selection gate: 3-item rationale ("what / to whom / why new / why resonates") must be concretizable. Description-type candidates rejected.
- Default winner count 3-5. Fewer than 2 = selection failed; more than 6 = convergence failed.
- Long-form Phase 0: use layered "PASONA stage × independent Mandal-Art per stage", not one 3×3 for the whole piece.
- Mid-form Phase 0: independent expansion per BEAF stage.
- Short-form Phase 0: when the brief is short-form, weight 掛詞 / 余白 / 極端化 / 意外性 heavily across the 8 directions. 5 切入點 (利益 / 恐怖 / 顛覆 / 呼喚 / 提問) routing is a downstream concern — `copywriting-short-form` applies it in Phase 4 using its own standard. Ideation emits raw candidates; it does not pre-classify them by 切入點.

## Hand-off envelope

On completion, update the envelope defined in `copywriting-toolkit/CLAUDE.md` §Handoff Envelope.

```json
{
  "phase": "phase-2-ideation",
  "form": "<long-form-pasona | long-form-extended | mid-form | short-form | light-action>",
  "brief": { "...": "from intake, pass through unchanged" },
  "message_thesis": "from intake, pass through",
  "ideation_pool": {
    "winners": [
      {
        "body": "...",
        "direction": "<mandalart auxiliary direction tag>",
        "vs_probability": 0.nn,
        "rationale": {
          "to_whom_what": "...",
          "novelty_vs_existing": "...",
          "resonance_in_context": "..."
        }
      }
    ],
    "runner_ups": [ { "body": "...", "reason_not_selected": "..." } ],
    "method_selection": {
      "base": "copy-ideation-parallel",
      "overlays": ["kosimo-instinct", "ulssas-seed"],
      "rationale": "..."
    },
    "divergence_evidence": {
      "total_candidates": 72,
      "mode_collapse_check": "passed | re-dispatched <which direction>",
      "a_type_diagram_ref": "<path or inline text hierarchy>"
    }
  },
  "next_stage": "copywriting-<form>"
}
```

`next_stage` routing:

| form | next_stage |
|---|---|
| long-form-pasona | `copywriting-long-form-pasona` |
| long-form-extended | `copywriting-long-form-extended` |
| mid-form | `copywriting-mid-form` |
| short-form | `copywriting-short-form` |
| light-action | `copywriting-light-action` |

Phase 3 neta injection (`copywriting-neta-injection`) is orthogonal — invoked by the draft skill internally when it needs neta material, not by ideation.

## Skipped-ideation envelope

When ideation is skipped (brief concrete with single clear angle):

```json
{
  "phase": "phase-2-ideation",
  "ideation_pool": null,
  "skip_reason": "brief specifies single agreed angle: <restate the angle>",
  "next_stage": "copywriting-<form>"
}
```

Downstream draft skill MUST accept `ideation_pool: null` and operate on `message_thesis` alone, but SHOULD surface a warning if drafting reveals the single angle is actually thin (signal to re-enter ideation).

## Anti-patterns

- Main worker writes all 8 directions alone (no parallel subagents) — mode collapse + thought-habit leak.
- 1-shot 5 candidates and done — breeding ground for なんかいいよね.
- Calling OW64 / 大谷翔平 chart "今泉 Mandal-Art" — lineage error.
- Pre-classifying with existing taxonomies (persona / AIDMA / 4P) during KJ group-edit — "let the chaos speak" violated.
- Labels as category names ("number-related", "price-related") — canonical labels are narratives ("number-appeal group that reassures the rational type").
- Asking LLM to draw A-type spatial diagram — spatial cognition belongs to human.
- Handoff without "なぜ良いか" 3 items — downstream writes description-type copy.
- Deleting runner-ups — they are A/B variant material; always appendix.
- Advanced overlay activated as default — bloats runtime without winner-quality gain. Overlay requires explicit trigger from the decision rule.
