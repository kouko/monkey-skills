---
name: copywriting-neta-injection
description: Phase 3 neta overlay — 4 techniques (Reversal / Substitution / Subcultural Capital / Cross-domain Mapping) via WebSearch-only pipeline. Hybrid pre-draft bake-in OR post-draft overlay. Skippable. ネタ投入。文案ネタ挿入。
---

# copywriting-neta-injection

Phase 3 of the copywriting-toolkit pipeline. Injects pop-culture,
subcultural, or literary references ("neta" / ネタ) into copy via a
**WebSearch-only** retrieval pipeline, using four academically-anchored
techniques. Supports **hybrid placement**: either **pre-draft bake-in**
(Phase 3 → Phase 4 drafts with neta integrated) or **post-draft overlay**
(Phase 4 drafts clean → Phase 3 overlays neta before Phase 5).

This skill is **skippable**. Neta is optional flair, never mandatory.
When triggered, output MUST pass the Neta Safety gate
(`rubrics/neta-safety-gate.md`) before advancing — two hard legal
vetoes on copyright and 景品表示法 ステマ.

## When to Use

Trigger when the intake envelope has `neta_opt_in: Yes` AND the brief
is compatible. See §Skip Conditions below for when to bypass.

**Typical use cases**:
- SNS campaigns riffing on a current meme / viral format
- B2C copy for subculture-native audiences (anime, game, niche fandoms)
- Campaigns that lean on a literary / quote / aphorism as rhetorical hook
- Brand copy that wants a Cross-domain Mapping metaphor (e.g. explain
  SaaS ROI via a cooking analogy)

## Skip Conditions (verbatim from source)

Mirror of `domain-teams:copywriting-team` SKILL.md §Neta Injection
Overlay:

- neta opt-in = No
- brief is >6-month evergreen AND source type is `sns-meme` only
  (literary sources are inherently evergreen-compatible)
- audience too broad for Technique 3 Subcultural Capital with SNS/Meme
  sources (literary sources may work for broader audiences via Bourdieu
  cultural capital axis)

If any skip condition fires: return `phase: phase-3-skipped` on the
envelope and hand off to Phase 4 (or Phase 5 if post-draft path and
draft already exists).

## Hybrid Placement — Decision Rule

Two modes are supported. `using-copywriting-toolkit` asks once during
routing: "Neta timing: bake-in or overlay?" The answer determines which
mode this skill runs.

### Mode 1: Pre-draft integration (bake-in)

Run Phase 3 **before** Phase 4. Output populates `neta_candidates` on
the envelope. The Phase 4 drafting skill (short-form / mid-form /
long-form-pasona / long-form-extended / light-action) consumes those
candidates and weaves the neta into the draft structure itself —
headline framing, body analogies, CTA echoes all align with the neta.

**Choose bake-in when**:
- Neta IS the campaign concept (e.g. "our whole ad is a riff on 『進撃の巨人』")
- Form is short-form / catchcopy where the neta must sit in the hook
- Cross-domain Mapping (Technique 4) is the chosen technique — the
  mapping must anchor the whole draft, not bolt on after
- Audience is subculture-native and expects the reference to permeate
  tone, word choice, and rhythm — not just appear once

### Mode 2: Post-draft overlay

Run Phase 4 **clean** (no neta awareness). Then run Phase 3 as an
overlay that mutates `draft` in-place, injecting neta at 1-3 strategic
surfaces (headline, mid-body callback, CTA). Runs **after** Phase 4,
**before** Phase 5 (voice-positioning).

**Choose overlay when**:
- Neta is optional flair layered on a messaging-first draft
- The base framework (PASONA / BEAF / QUEST etc.) must hold even if
  neta is removed in final review
- Client may A/B test with-neta vs. without-neta variants — overlay
  mode gives a clean base for free
- Technique 1 (Reversal) or Technique 2 (Substitution) is used at a
  single surface — no structural mapping needed

### Decision summary

| Situation | Mode |
|-----------|------|
| Culturally-integrated campaign; neta = concept | Pre-draft bake-in |
| Messaging-first copy; neta = flair | Post-draft overlay |
| Cross-domain Mapping (Technique 4) | Pre-draft bake-in |
| Subculture-native audience, long-form | Pre-draft bake-in |
| A/B test with vs. without neta wanted | Post-draft overlay |
| Single-surface Reversal / Substitution | Post-draft overlay |

When ambiguous, default to **post-draft overlay** (safer — base draft
survives if neta fails Safety gate).

## Preconditions

Formal schema used by `using-copywriting-toolkit` router for bounce-back routing. On violation, router emits the bounce-back envelope defined in `../../CLAUDE.md §Envelope Violation`. Two sets — one per placement mode.

### Required envelope fields (pre-draft bake-in mode)

| Field | Type | Source phase | Notes |
|---|---|---|---|
| `phase` | enum | ideation OR intake | one of `phase-2-ideation-complete`, `phase-1-confirmed`, `phase-express-confirmed` |
| `brief.product` | string | intake | non-empty |
| `brief.target_audience` | string | intake | |
| `message_thesis` | string | intake | |
| `neta_opt_in` | bool | intake | must be `true` — else skip this skill |
| `neta_source_type_preference` | enum | intake | `all` / `sns-meme` / `literary` / `mixed` |

### Required envelope fields (post-draft overlay mode)

| Field | Type | Source phase | Notes |
|---|---|---|---|
| `phase` | enum | Phase 4 drafter | `phase-4-draft-complete` |
| `form` | enum | intake | one of 5 Phase-4 form types |
| `draft` | string | Phase 4 | non-empty, ≥1 sentence |
| `message_thesis` | string | intake | |
| `neta_opt_in` | bool | intake | must be `true` |

### Upstream bounce targets on violation

- `neta_opt_in` missing / `false` → skip this skill entirely (emit `phase-3-skipped`, route to Phase 4 drafter or Phase 5 positioning)
- pre-draft mode: any intake L1 missing → bounce to `copywriting-intake`
- post-draft mode: `draft` missing → bounce to `copywriting-<form>` (Phase 4 drafter named in `envelope.form`)

## Inputs & Outputs (envelope contract)

### Pre-draft bake-in mode

**Input envelope** (from `copywriting-ideation` or `copywriting-intake`):

```json
{
  "phase": "phase-2-ideation-complete",
  "brief": { "...": "..." },
  "message_thesis": "...",
  "ideation_pool": ["..."],
  "neta_opt_in": true,
  "neta_source_type_preference": "all | sns-meme | literary | mixed"
}
```

**Output envelope**:

```json
{
  "phase": "phase-3-neta-baked",
  "brief": { "...": "..." },
  "message_thesis": "...",
  "ideation_pool": ["..."],
  "neta_candidates": [
    {
      "reference": "...",
      "source_url": "...",
      "source_date": "YYYY-MM-DD",
      "technique": "Reversal | Substitution | Subcultural Capital | Cross-domain Mapping",
      "audience_recognition": "high | medium | low",
      "safety_notes": "..."
    }
  ],
  "next_stage": "copywriting-<form>"
}
```

### Post-draft overlay mode

**Input envelope** (from a Phase 4 workflow skill):

```json
{
  "phase": "phase-4-draft-complete",
  "brief": { "..." },
  "message_thesis": "...",
  "draft": "... clean base draft ...",
  "form": "short-form | mid-form | long-form-pasona | long-form-extended | light-action",
  "neta_opt_in": true
}
```

**Output envelope**:

```json
{
  "phase": "phase-3-neta-overlaid",
  "draft": "... neta-injected version replaces original ...",
  "neta_annotations": [
    {
      "surface": "headline | mid-body | cta",
      "reference": "...",
      "source_url": "...",
      "technique": "...",
      "original_text": "...",
      "injected_text": "..."
    }
  ],
  "next_stage": "copywriting-voice-positioning-stage"
}
```

In overlay mode `draft` is **replaced** (not appended). Base-draft
preservation is the client's responsibility via version control — the
envelope only carries the final neta-injected draft forward.

## Pipeline — Phases A–D (WebSearch-only)

The four techniques are delivered via a four-phase WebSearch-only
pipeline. Full specification in
`standards/neta-websearch-pipeline.md`. High-level:

| Phase | Purpose | Grounding |
|-------|---------|-----------|
| **A. Audience Context Retrieval** | Site-locked WebSearch (Path A-1: SNS/meme) or parametric-first (Path A-2: literary) to build a 5-15 candidate catalog | `standards/neta-websearch-pipeline.md` §A + `standards/neta-source-taxonomy.md` |
| **B. CoT Deconstruction** | For each candidate: extract referent, in-group context, mechanism vector (which of 4 techniques fits) | `standards/neta-injection-techniques.md` |
| **C. Strict Replacement / Injection** | Apply chosen technique(s) with literal preservation rules (no misquotation, no paraphrased "vibe" reference) | `standards/neta-injection-techniques.md` + `standards/neta-websearch-pipeline.md` §C |
| **D. Vibe / Safety Pre-check** | Self-verify against Neta Safety gate dimensions before handing to evaluator | `rubrics/neta-safety-gate.md` |

**WebSearch-only rule**: all retrieval goes through WebSearch with
`site:` operators from the source-taxonomy allow-list. No scraping, no
unofficial archives, no user-uploaded clip mirrors. Recency filter
≤6 months for SNS; attribution verify for literary.

Full flow: see `protocols/copy-neta-injection.md` (includes routing
mermaid, Path A-1 / A-2 divergence, BLOCKED handling for narrow
audiences or unverifiable attribution).

## Four Techniques (primary labels)

| # | Primary label | Mechanism summary |
|---|---------------|-------------------|
| 1 | **Reversal** (逆転 / Culture Jamming) | Take a known message, invert its stance — subvert a meme / ad / slogan into its opposite |
| 2 | **Substitution** (置換 / Snowclone) | Keep the structural template of a known phrase, swap the content — "X is the new Y" style |
| 3 | **Subcultural Capital** (界隈消費 / Tribal Signal) | Deploy an in-group cipher only the target subculture decodes — Bourdieu cultural capital axis |
| 4 | **Cross-domain Mapping** (次元降下的比喩 / Analogy) | Map a familiar domain's structure onto an unfamiliar product to enable simplification |

Full mechanism, JP/EN vernacular aliases, worked examples, and
anti-patterns: `standards/neta-injection-techniques.md`.

## Source Taxonomy — 5 Categories

| Category | Examples | Shelf life | Retrieval path |
|----------|----------|------------|----------------|
| SNS / Meme | X / Reddit / niconico / TikTok | ≤6 mo | Path A-1 (site-locked search) |
| Classical Lit | 百人一首, 漢詩, Shakespeare | evergreen | Path A-2 (parametric → verify) |
| Modern Lit | 村上春樹, 太宰治, contemporary novels | 5-20 yr | Path A-2 |
| Quotes / Aphorisms | 名言, proverbs | evergreen | Path A-2 |
| Specialist Fandom | anime / game / niche subculture | variable | Path A-1 + subculture allow-list |

Full taxonomy, recognition heuristics, and allow-list tables:
`standards/neta-source-taxonomy.md`.

## Protocol Reference

Full Phase A–D flow, BLOCKED conditions, routing diagram, and
pre-phase opt-in verification live in
`protocols/copy-neta-injection.md`. Do not inline — reference.

## Standards Reference

- `standards/neta-injection-techniques.md` — 4 techniques with primary
  English academic anchor + EN/JP vernacular aliases + worked examples
- `standards/neta-source-taxonomy.md` — 5 source categories, shelf-life
  rules, retrieval-path routing, site allow-list
- `standards/neta-websearch-pipeline.md` — Phase A-D pipeline spec
  including Path A-1 (SNS/meme, site-locked) and Path A-2 (literary,
  parametric-first with attribution verify)

## Mandatory Gate — Neta Safety

**Every output from this skill (bake-in or overlay mode) MUST pass the
Neta Safety gate before advancing.** The gate is evaluator-only.

- Rubric: `rubrics/neta-safety-gate.md`
- Agent: `copywriting-toolkit/agents/copywriter-evaluator.md`
- Dimensions: 5 (cultural fit, attribution accuracy, freshness,
  audience recognition, legal)
- **Two hard legal vetoes** (any one = FAIL):
  1. Copyright infringement (verbatim lyric / extended quote without
     license; character-likeness without rights)
  2. 景品表示法 ステマ (undisclosed endorsement / stealth marketing
     failing to label sponsored references)

Verdict enum: `PASS` | `NEEDS_REVISION`. On `NEEDS_REVISION`, worker
addresses specific dimension feedback and re-runs Phase C-D (not A-B —
candidate catalog stays stable).

## Handoff

- **Bake-in mode**: hand off to the Phase 4 drafting skill selected in
  the router (`copywriting-<form>`). `neta_candidates` is a pool the
  drafter selects from — not every candidate must appear.
- **Overlay mode**: hand off to `copywriting-voice-positioning-stage`.
  The voice-quadrant positioning analyzes the neta-injected draft, not
  the pre-overlay base.

## BLOCKED Conditions

Return `BLOCKED` on the envelope (do not proceed to Safety gate) when:

- Phase A retrieval returns zero usable candidates after both Path A-1
  and Path A-2 (audience too narrow / topic too fresh)
- Phase A-2 attribution cannot be verified for any candidate
  (misquotation risk — never guess a quote's source)
- All candidates fail Phase D pre-check on a hard legal veto dimension
  (copyright or ステマ) — surface to user for brief revision
- Intake envelope missing `neta_opt_in` or `neta_source_type_preference`
  — do not silently default

Present BLOCKED reason to user. Do not auto-skip to Phase 4/5 —
downstream expects either neta output or explicit skip flag.

## Non-Goals

- This skill does NOT do Phase 2 ideation. If the brief needs concept
  expansion, route to `copywriting-ideation` first.
- This skill does NOT own the ethics check (景表法 optical-illusion
  claims, etc.) — that is `copywriting-ethics-check-stage` Phase 7.
  Neta Safety only covers neta-specific legal vetoes (copyright + ステマ).
- This skill does NOT run on form-specific framework adherence. Phase 4
  workflow skills own their framework; this skill only injects neta.

## Next Stage

- Bake-in mode → `copywriting-<form>` (Phase 4 drafting)
- Overlay mode → `copywriting-voice-positioning-stage` (Phase 5)
- Skipped → whichever phase the router dictates (Phase 4 or Phase 5)
