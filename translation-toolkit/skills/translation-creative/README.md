# translation-creative

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Translate ad copy / headline / tagline / catchphrase via faithful or transcreation mode.

Part of the [translation-toolkit](../..) plugin. Operational spec
Claude loads is [`SKILL.md`](SKILL.md); this README is for humans.

## Why a dedicated creative skill

Ad copy fails in ways prose translation does not detect. A back-translation
similarity score may pass while the target loses the source's persuasion
intent — wrong CTA strength, dead pun, alien cultural reference, silent
taboo. A faithful render of "Just do it." into Japanese is grammatical
and useless as a tagline.

`translation-creative` adds two pieces the other format specialists
don't have: a **5th critique axis** (Effectiveness, in transcreation
mode) judging whether the target preserves persuasion intent in target
culture, and a **mode-conditional S1 tier flip** that promotes
back-translation to HARD when the WRITER is licensed to deviate from
the source surface. Variants are also a first-class output mode —
A/B candidates instead of paraphrase noise.

## Two modes

Mode is declared in the intake-spec and controls REFLECT axis count
+ S1 gate tier:

| Mode | REFLECT | S1 tier | Threshold | Use when |
|---|---|---|---|---|
| **faithful** | 4D (Accuracy / Fluency / Style / Terminology) | SHOULD (WARN below) | 0.85 | Source structure + sentence boundaries should hold; only phrasing adapts |
| **transcreation** | 5D (4D + Effectiveness) | **MUST** (FAIL below) | 0.70 | Source surface can be left behind to land equivalent persuasion in target culture |

If intake-spec doesn't specify mode, the upstream `translation-intake`
defaults ad-shaped genres to `transcreation` and prose-leaning marketing
brief content to `faithful`, recording the resolved mode + reason.

The full mode-entry contract — the 5th Effectiveness axis, how variants
differ, the S1 MUST contract, the glossary leeway rule — is in
[`protocols/transcreation-mode.md`](protocols/transcreation-mode.md).

## Pipeline

```
intake-spec (from translation-intake)
        │
Layer 2 — Preparation
        ├── brand brief intake (recommended for transcreation; optional for faithful)
        ├── protect-pass: mask URLs / HTML / brand tokens as ⟦P:NN⟧
        ├── source analysis: cultural references, wordplay, CTA verbs,
        │   untranslatability candidates
        └── glossary resolve (4-tier)
        │
Layer 3 — Core loop (DRAFT → REFLECT 4D-or-5D → IMPROVE)
        │   └── WRITER receives brand-brief context; honors signature
        │       phrases + do-not-say list
        │
Layer 4 — Verification (M1 + M2 HARD; S1 mode-conditional;
        │   S2 SHOULD; I1 INFO)
        │
Layer 5 — Output
        ├── default: 1 translation
        ├── --variants=N: N independent core-loop runs with
        │   axis-differentiated prompts (NOT paraphrases)
        └── emit audit-trail.json (with variant_index when applicable)
```

## Brand brief

Captured per [`protocols/brand-brief-intake.md`](protocols/brand-brief-intake.md).
Recommended for transcreation, optional for faithful (which falls back
to intake-spec `register` + `intent` if no brief is provided).

The brief captures: brand archetype (Hero / Sage / Outlaw / etc.),
tone-of-voice axes (authoritative ↔ playful, formal ↔ casual,
warm ↔ cool), do-not-say list, signature phrases (verbatim-preserve
vs locale-transcreate), target persona, CTA style, and per-locale
brand-name handling (preserve / transliterate / locale-substitute).
Outputs land in the audit-trail `brand_brief` block.

## Verification gate matrix

The defining trait vs the other format specialists: **mode-conditional
S1 tier flip** — back-translation is SHOULD in faithful but promoted
to MUST in transcreation. This is the only place in the toolkit where
a tier flip drives a HARD gate.

| Gate | Tier | Action |
|---|---|---|
| **M1** | HARD | Placeholder integrity — count + ID set parity |
| **M2** | HARD | Project glossary compliance. In transcreation, see [`protocols/transcreation-mode.md`](protocols/transcreation-mode.md) §"Glossary leeway" — culturally-driven violations are auditable but allowed. |
| **S1** | **MUST in transcreation, SHOULD in faithful** | Back-translation similarity. Threshold = **0.85** in faithful (WARN), **0.70** in transcreation (FAIL below blocks output). |
| **S2** | SHOULD | Register preservation — JUDGE classifies source vs target register; mismatch surfaces a WARN. |
| **I1** | INFO | Untranslatability flagging — particularly active in transcreation. Non-interactive: records borrow / explain / approximate decisions. |

**Why S1 promotes to MUST in transcreation** (spec Decision #4): when
the WRITER is licensed to deviate substantially from the source surface,
M1 (placeholder count) and S2 (register) are insufficient guards
against outright topic drift — S1 is the only gate that catches
"the v2 is well-written copy about a different product".

## Variants

`--variants=N` is opt-in. When set, the skill emits N **genuinely
different** alternatives — each variant is a full, independent
DRAFT → REFLECT → IMPROVE run with the WRITER prompt instructed to
vary on a tactical axis (preserve source structure / restructure for
target rhythm / substitute culturally equivalent metaphor / etc).

Variants are NOT paraphrases of a single draft — that pattern is
explicitly forbidden because it produces synonym-swap noise. The
`variant_index` field in the audit trail attributes issues to the
specific variant. If a variant fails S1 in transcreation mode it is
dropped; if all N fail, the run halts rather than silently emitting
fewer than N.

## Web search policy

ON by default — creative work benefits from current cultural / campaign
context. Override to OFF (`--web-search=off`) when an established brand
voice risks contamination from competitor copy. Effectiveness-axis
critique still works from training-time knowledge with web off;
transcreation does not require web search but loses freshness on recent
slogans / memes / campaign references.

## Cross-plugin composition

`copywriting-toolkit` can be invoked **after** creative translation for
voice / form / ethics polish. Composition is **user-explicit only** —
`translation-creative` does NOT auto-invoke `copywriting-toolkit`. Run
the two as a sequential pair when desired; the skills are complementary.

## What this skill does NOT do

- **Does not run intake.** Hand off to [`translation-intake`](../translation-intake)
- **Does not generate brand strategy.** Missing brief in transcreation
  mode produces a WARN, not a generated strategy.
- **Does not translate brand names** without explicit intake instruction —
  default is verbatim-preserve.
- **Does not auto-invoke `copywriting-toolkit`** — composition is explicit.
- **Does not paraphrase a single draft into variants** — `--variants=N`
  runs N independent core loops.
- **Does not bypass S1 in transcreation mode.** When S1 is MUST, a
  sub-threshold v2 blocks output; revise or escalate to a human, NOT
  flip the gate off.
- **Does not replace human creative review.** The audit trail + variant
  index are designed to make downstream review fast.

## See also

- [`SKILL.md`](SKILL.md) — operational spec
- [`protocols/brand-brief-intake.md`](protocols/brand-brief-intake.md) ·
  [`protocols/transcreation-mode.md`](protocols/transcreation-mode.md)
  (5D Effectiveness, variant strategy, S1 MUST contract, glossary leeway)
- [`checklists/creative-checklist.md`](checklists/creative-checklist.md) ·
  [`references/5d-effectiveness.md`](references/5d-effectiveness.md)
- Plugin: [`../../README.md`](../../README.md) ·
  Router: [`../using-translation-toolkit`](../using-translation-toolkit) ·
  Layer 1: [`../translation-intake`](../translation-intake)
