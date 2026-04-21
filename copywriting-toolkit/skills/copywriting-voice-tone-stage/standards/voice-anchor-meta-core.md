---
title: Voice Anchor Meta — Core (hot path)
tier: 2
---

# Voice Anchor Meta — Core

**Load scope**: Phase 6 Pass 3 (any branch). Hot-path meta — always needed when Pass 3 is processing a voice reference.

**Content**: schema definition + 4-condition selection rubric + over-mimic mitigation index. Detailed lineage map / cross-reference registry / cross-cultural label rubric / corrections catalog live in [voice-anchor-meta-detail.md](voice-anchor-meta-detail.md).

## Purpose

This file provides the minimum operational metadata Pass 3 needs to correctly read and apply ANY voice anchor (whether from craft-gate per-master `anchor-{jp,zh-tw}-{master}-*.md` via `JP/ZH_CRAFT_MASTER_MAP`, register-signal `{lang}-q{N}-anchors.md` router → `anchor-{slug}.md` body, or axis `axis-extreme-anchors.md`). Cross-master attribution / era / comparison audit content lives in `voice-anchor-meta-detail.md §Cross-Master Context` (conditional Pass 3a/3b load + always-on Pass 3d load). Schema + rubric + mitigation are "hot path" because they are consulted on every anchor invocation.

## Schema version selector (v1.5.0)

Anchor entries now exist in two schemas. Pass 3 must detect schema version before field extraction.

**Detection rule**:
- If anchor file frontmatter contains `schema_version: 2.0` → use **Layer 1 v2 schema** (below, §v2 schema)
- Otherwise (no `schema_version` OR `schema_version: 1.x`) → use **v1 schema** (original, below)

Both schemas coexist during migration window. v2 entries are individually re-researched per `docs/anchor-schema-v2.md` inclusion criterion. Entries without individual-creator authorship have been moved to `docs/format-templates/` (institutional/platform) or `docs/register-references/` (documented movements/campaigns) — those are NOT voice anchors and are NOT loaded by Pass 3.

## v2 schema (Layer 1 purpose-centric, preferred going forward)

Source of truth spec: `docs/anchor-schema-v2.md`. Fields Pass 3 reads:

```
### {anchor name} ({culture} | {quadrant} {landmark position})

## Voice direction
**What this register achieves**: {one-line register intent}

**Native critical read** (≥3):
- 「{verbatim term}」({source: critic/author/trade-press})
- ...

## Prose mechanics (≥5, actionable)
- {Rule 1 — sentence-level, concrete}
- ...

## Examples (≥5 verbatim)
- 「{verbatim line}」({work, year, context})
- ...

## Don't / Over-mimic
- **Failure mode**: {LLM-default-drift specific to this anchor}
- **Mitigation** (≤15 words): "{injectable clause}"

## Metadata
- Trigger slug: {culture}-{kebab}-{style-label}
- Over-mimic risk: LOW / MEDIUM / HIGH / HIGH+
- Pairs with form: [form1, form2, ...]
- Cross-reference-valid-for (optional): {other-lang}: STRONG / MEDIUM / WEAK
```

**v2 validation** (anchor passes iff ALL 5 hold):
1. Voice direction present (1 line, substantive)
2. Native critical read has ≥3 attributed phrases
3. Prose mechanics has ≥5 actionable rules
4. Examples has ≥5 verbatim with source
5. Don't / Over-mimic has failure mode + ≤15-word mitigation

**v2 Dimension 6 consumer change**: the over-mimic mitigation clause is now read directly from the anchor's own `Don't / Over-mimic` block, not from the legacy registry table in §Over-mimic mitigation registry. For v2 entries, the anchor file IS the single source of truth for mitigation. For v1 entries, the registry table still applies.

## v1 schema (legacy — registry-row entries only)

As of v1.9.2, **no anchor files use v1 schema body** — all 81 `anchor-{slug}.md` carry `schema_version: 2.0` frontmatter and v2 body structure. The full v1 body spec has been removed (was obsolete; no writer / consumer).

v1-era remnants still present:
- **9 v1-only authors in §Over-mimic mitigation registry below** (村上春樹 / 金庸 / 三島 / 莫言 / 太宰 / 余華 / McCarthy / DFW / Ellroy) — registry-row entries only (anchor name + auto-leaked tropes + mitigation clause), NOT full v1 anchor bodies.

§Schema version selector above still detects `schema_version` frontmatter; anything without it falls back to "treat as registry-row reference only, not as standalone anchor body".

## Anchor selection rubric — 4 conditions

An anchor is valid for a given brief IF AND ONLY IF all 4 hold:

### Condition 1: Corpus-depth floor

Anchor's LLM training corpus is **DEEP or MEDIUM-DEEP**. Proxy signals (any one):
- Translated into ≥3 languages
- School-textbook canon in ≥1 major market (JP/TW/HK/CN/EN)
- Dedicated academic sub-field (張學 / 村上學 / Joyce studies)
- Wikipedia article word count ≥ 2000

If depth is MEDIUM or THIN without specific-brief justification → REJECT the anchor selection.

### Condition 2: Label-density specificity

Anchor's style must be expressible in **1-3 words + ONE memorable formal feature**. If paragraph-level description required → REJECT.

Pass test examples:
- ✅ "iceberg-minimalism + short declaratives" (Hemingway)
- ✅ "aphoristic-observation + antithesis" (Didion)
- ❌ "a complex hybrid of multiple rhetorical patterns" (too vague)

### Condition 3: Commercial-register bridge

At least ONE of {Q1, Q2, Q3, Q4} explicitly gains from the voice. Confirmed by anchor entry's `quadrant` field.

If anchor is "literary only, non-commercial register" → REJECT for Layer-0 (may remain as long-form narrative reference only).

### Condition 4: Over-mimic control

Over-mimic risk is LOW or MEDIUM natively, OR the mitigation clause fits in ≤15 words. If mitigation requires paragraph-level guardrails → DOWNGRADE to "niche-only, experienced-user tier" (still allowed but flagged in usage).

### Priority boost (+1 tier)

Anchor with **documented advertising-craft lineage** to a verified copywriter citation (primary source = author's own book / verified interview / TCC 年鑑 / 宣伝会議 / Brain magazine) gets +1 tier. See [verified lineage map in meta-detail](voice-anchor-meta-detail.md#verified-lineage-map).

### Condition 5: Negation-of-axis rule (v1.10.0)

When `brief.tone_cue` contains an **explicit negation of an axis or an axis-adjacent cluster** — e.g., "not corporate", "not artisan-snob", "not funny", "not preachy", "not aspirational" — Pass 3 auto-selector MUST:

1. Forbid the negated axis/cluster from consideration. Example: "not corporate" → Authority axis forbidden → Q1/Q2 candidates downgraded.
2. Record the forbidden axis in `voice_quadrant.rationale` so Phase 6 gates can verify the rewrite does not drift back.
3. If no anchor satisfies the negation (all candidates fail), emit a `violation` envelope to intake requesting tone_cue clarification.

Example from v1.9.x E2E (JP meditation app): `tone_cue: "calming, not corporate"` → Authority axis forbidden → Q1/Q2 craft-gate masters (糸井 / 岩崎 state-proposal) eliminated → Q3 private-space register selected (吉本ばなな).

### Safe-substitute lookup (v1.10.0)

When `brief.voice_reference` names a master with **HIGH over-mimic risk** in the registry (村上春樹 / Hemingway / Didion / Chandler / Sorkin / Duolingo-Parvez / etc.), Pass 3 MAY auto-suggest a safer alternative by querying anchor frontmatter:

```
candidates = [anchor for anchor in standards/*.md
              if named-master ∈ anchor.frontmatter.safe_substitute_for]
```

If a candidate exists AND its over-mimic risk is LOWER than the named master's, Pass 3 emits `register_signal_applied.substitute_suggested = {slug, rationale}` alongside the primary selection. The user-specified master remains the default primary unless user confirms substitute in a follow-up turn.

Current documented substitutes (expand as research surfaces more):
- 吉本ばなな `anchor-jp-yoshimoto-banana-j-bungaku.md` has `safe_substitute_for: [村上春樹]` — same peer-intimate cadence, LOWER over-mimic risk (no jazz/cats/wells tropes).

### Automatic rejection

- Voice inseparable from ideological/traumatic content (三島 nationalist / 莫言 magical-realist-rural / 余華 death-content)
- Biographical-tragic weight overpowers style on bare name (顧城 / 海子 / Sylvia Plath)
- Corpus deep but LLM latent-space illegible (殘雪 experimental, certain avant-garde)
- Register non-transferable to commercial frame (Virginia Woolf interior, Beckett stripped)
- Register requires >800-token context to stabilise (DFW)
- Corpus THIN in target language (Yi Sang, heritage-only poets)

## Over-mimic mitigation registry (index)

When the listed anchor is invoked, the corresponding mitigation clause MUST appear inline in the prompt or be enforced by the Voice Consistency gate. Omitting mitigation → pastiche leak.

### Source of truth (v1.7.1)

This registry covers TWO categories:

1. **v1-only anchors** (no v2 migration yet) — mitigation lives in this table; Pass 3 consumes directly.
2. **Movement / campaign / brand-category entries** (not individual-creator anchors) — these have no v2 anchor file because they fail the inclusion criterion (rotating authorship / team-coauthored / generic category). Mitigation stays here as the only home.

**For v2-migrated anchors**: mitigation lives in the anchor's own `Don't / Over-mimic` block (single source of truth). Pass 3 reads it from the anchor file directly, NOT from this registry. See §v2 anchors with inline mitigation (below) for the index.

### Registry table (v1-only anchors + movement / campaign / category)

| Anchor | Auto-leaked tropes | Required mitigation clause (≤15 words) |
|---|---|---|
| 村上春樹 Murakami | jazz, cats, wells, whisky, pasta-boiling-while-phone-rings | "no jazz / no cats / no wells / no whisky / no cooking-phone-ring" |
| 金庸 Jin Yong | 江湖, 內功, 俠氣, 前輩晚輩 | "no wuxia vocabulary; 只借節奏不借詞彙" |
| 三島由紀夫 Mishima | sword, seppuku, 金閣, nationalist pathos | "avoid violent-aesthetic imagery" |
| 莫言 Mo Yan | red sorghum, 高密東北鄉, magical-realist hallucination | "no rural-surrealist imagery" |
| 太宰治 Dazai | "恥の多い生涯", 人間失格 opening register | "no confessional-failure framing" |
| 余華 Yu Hua | death, blood-selling, famine | "sentence architecture only, no content" |
| Cormac McCarthy | "and X and Y and Z" polysyndeton | "forbid triple-conjunction chains" |
| David Foster Wallace | Nested footnotes/parentheticals | "Layer-1 only, never Layer-0 / flatten nesting" |
| James Ellroy | Telegraph staccato fragments | "avoid for Layer-0; paragraph-level integration required" |
| Extinction Rebellion Declaration | US-Declaration-of-Independence pastiche on any manifesto | "civic-declarative register ONLY; NOT for commercial product copy" |
| Nike "Dream Crazy" | "Believe in something. Even if it means sacrificing everything." anaphora | "anaphora limited to 1 series per piece; sacrifice-stake clause reserved" |
| Extreme luxury manifesto brands (generic) | Ralph Lauren / Gucci aspirational-heritage auto-drift | "no nostalgia clichés (old-world / heritage / craftsmanship) without specific signifier" |

### v2 anchors with inline mitigation (SSOT in anchor file, NOT here)

The following v2-migrated anchors carry their own `Don't / Over-mimic` block in their `anchor-{slug}.md` file. Pass 3 reads mitigation from the anchor file directly (per v2 schema §Dimension 6 consumer change). These are listed here for **discoverability only** — do NOT duplicate their mitigation clauses into the registry table above.

| Anchor | Mitigation source |
|---|---|
| 王家衛 Wong Kar-wai | `anchor-zh-hk-wong-kar-wai-monologue-fragment-temporal.md §Don't / Over-mimic` |
| 夏目漱石 Soseki | `anchor-jp-soseki-yoyu-ha-dry-observer.md §Don't / Over-mimic` |
| Hemingway | `anchor-en-hemingway-iceberg.md §Don't / Over-mimic` |
| Joan Didion | `anchor-en-didion-observational-essay.md §Don't / Over-mimic` |
| Raymond Chandler | `anchor-en-chandler-hard-boiled-metaphor.md §Don't / Over-mimic` |
| Aaron Sorkin | `anchor-en-sorkin-rhetorical-rapid-fire.md §Don't / Over-mimic` |
| Zaria Parvez (Duolingo 2021-2022 era) | `anchor-en-duolingo-parvez-2021-formative.md §Don't / Over-mimic` |
| 許舜英 | `anchor-zh-tw-xu-shunying-ideological-definitional.md §Don't / Over-mimic` |

Additional v2-migrated anchors with inline mitigation (not flagged for drift in v1 registry historically, but follow the same SSOT rule): all other `anchor-{slug}.md` files under `standards/` carry their own `Don't / Over-mimic` block.

### Usage rule

Pass 3 agent consults mitigation as follows:

1. **Anchor is v2-migrated** (has `schema_version: 2.0` frontmatter and corresponding `anchor-{slug}.md`): read mitigation from the anchor's own `Don't / Over-mimic` block. Do NOT look in this registry table.
2. **Anchor is v1-only** (no v2 migration yet): read mitigation from the registry table above.
3. **Entry is movement / campaign / brand-category** (XR Declaration / Nike Dream Crazy / Extreme luxury manifesto brands): read mitigation from the registry table above (these have no v2 anchor by design).

Voice Consistency gate (Dimension 6) applies the same precedence — v2 anchor file is authoritative; registry is fallback for v1 / movement / category entries.

If anchor NOT listed in either place, Pass 3 applies anchor without mitigation (LOW risk default).

## Quick reference — anchor lookup flow

```
voice_reference = user-supplied string (or "default")
      ↓
Is it in craft-gate masters?
  {糸井重里, 岩崎俊一, 眞木準, 谷山雅計,
   許舜英, 李欣頻, 葉明桂}
      ├── YES → Tier 1: load voice-anchor-meta-detail.md §Cross-Master Context
      │        + this file (for over-mimic mitigation)
      │
      └── NO → Is voice_quadrant.position = "axis-*"?
           ├── YES → Tier 3: load axis-extreme-anchors.md + this file
           │
           └── NO → Tier 2: REGISTER SIGNAL path
                    - Load this file (schema + rubric + mitigation)
                    - Load voice-anchor-meta-detail.md (lineage + cross-ref)
                    - Load {output_language}-q{voice_quadrant.primary}-anchors.md
                      (section-targeted if position provided)
                    - Cross-lang STRONG? Also load jp-q{N}-anchors.md section
```

## Cross-references

- [voice-anchor-meta-detail.md](voice-anchor-meta-detail.md) — verified lineage map / cross-reference registry / cross-cultural label rubric / corrections catalog (loaded for register-signal path)
- `voice-anchor-meta-detail.md §Cross-Master Context` — craft-gate target for JP canonical masters
- `voice-anchor-meta-detail.md §Cross-Master Context` — craft-gate target for ZH canonical masters
- Per-quadrant anchor files: `{jp,zh,en}-q{1,2,3,4}-anchors.md` — register-signal inventory
- [axis-extreme-anchors.md](axis-extreme-anchors.md) — axis-extreme landmarks (V2 expansion)
