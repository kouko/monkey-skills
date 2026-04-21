---
title: Voice Anchor Meta — Core (hot path)
tier: 2
---

# Voice Anchor Meta — Core

**Load scope**: Phase 6 Pass 3 (any branch). Hot-path meta — always needed when Pass 3 is processing a voice reference.

**Content**: schema definition + 4-condition selection rubric + over-mimic mitigation index. Detailed lineage map / cross-reference registry / cross-cultural label rubric / corrections catalog live in [voice-anchor-meta-detail.md](voice-anchor-meta-detail.md).

## Purpose

This file provides the minimum operational metadata Pass 3 needs to correctly read and apply ANY voice anchor (whether from craft-gate `{jp,zh}-copy-craft-lineage.md`, register-signal `{lang}-q{N}-anchors.md`, or axis `axis-extreme-anchors.md`). Schema + rubric + mitigation are "hot path" because they are consulted on every anchor invocation.

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

## v1 schema (legacy, still supported during migration)

Every v1 anchor entry follows this structure:

```
### {anchor name} ({culture} | {quadrant} {landmark position})

- **Era**: {start-year - end-year, or "ongoing"}
- **Agency / creator**: {attribution (specific person / agency / team)}
- **Primary sources**: {2-3 verifiable — Wikipedia URL / ISBN / Brain / TCC / D&AD / Cannes / author book}
- **Representative lines** (verbatim, not paraphrase):
  - {line 1}
  - {line 2}
  - {line 3}
- **Voice signature** (3-4 dimensions):
  - Dimension 1: {characteristic}
  - Dimension 2: {characteristic}
  - Dimension 3: {characteristic}
  - Dimension 4: {characteristic}
- **LLM corpus depth**: DEEP / MEDIUM-DEEP / MEDIUM / THIN — {rationale}
- **Over-mimic risk**: LOW / MEDIUM / HIGH
  - Mitigation (required if HIGH, ≤15 words): "{clause}"
- **Cross-reference-valid-for** (optional):
  - {other lang}: STRONG / MEDIUM / WEAK
- **Cross-cultural equivalents**: {parallel anchors in other cultures}
- **Trigger slug**: `{culture}-{name-kebab-case}-{style-label}`
```

### Field semantics

| Field | Meaning | Used by |
|---|---|---|
| `era` | Canonical window when voice is citable | Phase 5 era-boundary flags |
| `primary sources` | Verifiable citations | Gate verdict rationale; drift protection |
| `representative lines` | Verbatim corpus (no paraphrase) | Pass 3 register template |
| `voice signature` | 3-4 operational dimensions | Pass 3 craft application |
| `LLM corpus depth` | Proxy for retrieval reliability | Anchor selection rubric condition 1 |
| `over-mimic risk` + mitigation | Load-bearing guardrail against pastiche | Pass 3 application + Voice Consistency gate |
| `cross-reference-valid-for` | Target-language strengths | Phase 5 cross-lang resolver + Pass 3 cross-lang load |
| `trigger slug` | Kebab-case reference token | `brief.voice_reference` matching |

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

### Automatic rejection

- Voice inseparable from ideological/traumatic content (三島 nationalist / 莫言 magical-realist-rural / 余華 death-content)
- Biographical-tragic weight overpowers style on bare name (顧城 / 海子 / Sylvia Plath)
- Corpus deep but LLM latent-space illegible (殘雪 experimental, certain avant-garde)
- Register non-transferable to commercial frame (Virginia Woolf interior, Beckett stripped)
- Register requires >800-token context to stabilise (DFW)
- Corpus THIN in target language (Yi Sang, heritage-only poets)

## Over-mimic mitigation registry (index)

When the listed anchor is invoked, the corresponding mitigation clause MUST appear inline in the prompt or be enforced by the Voice Consistency gate. Omitting mitigation → pastiche leak.

| Anchor | Auto-leaked tropes | Required mitigation clause (≤15 words) |
|---|---|---|
| 村上春樹 Murakami | jazz, cats, wells, whisky, pasta-boiling-while-phone-rings | "no jazz / no cats / no wells / no whisky / no cooking-phone-ring" |
| 王家衛 Wong Kar-wai | expiration dates, 1-minute, pineapple cans, step-printing | "no expiration imagery / no countdowns / no cans / no step-printing" |
| 金庸 Jin Yong | 江湖, 內功, 俠氣, 前輩晚輩 | "no wuxia vocabulary; 只借節奏不借詞彙" |
| 三島由紀夫 Mishima | sword, seppuku, 金閣, nationalist pathos | "avoid violent-aesthetic imagery" |
| 莫言 Mo Yan | red sorghum, 高密東北鄉, magical-realist hallucination | "no rural-surrealist imagery" |
| 太宰治 Dazai | "恥の多い生涯", 人間失格 opening register | "no confessional-failure framing" |
| 余華 Yu Hua | death, blood-selling, famine | "sentence architecture only, no content" |
| 夏目漱石 Soseki | 「〜である」archaic grammar | "modern grammar only" |
| Hemingway | "He was tired. The whisky was cold." + he-said/she-said chains | "pair with Carver/Didion; forbid dialogue-tag chains >2" |
| Didion | "It meant nothing. It meant everything." antithesis tic | "cap rhetorical-antithesis to 1 per 150 words" |
| Raymond Chandler | "Her eyes were like [noun]" simile cascade | "cap similes to 1 per 50 words" |
| Cormac McCarthy | "and X and Y and Z" polysyndeton | "forbid triple-conjunction chains" |
| Aaron Sorkin | "You want X? Let me tell you about X" rhetorical-Q-then-A | "forbid rhetorical-question-plus-answer pattern" |
| David Foster Wallace | Nested footnotes/parentheticals | "Layer-1 only, never Layer-0 / flatten nesting" |
| James Ellroy | Telegraph staccato fragments | "avoid for Layer-0; paragraph-level integration required" |
| Extinction Rebellion Declaration | US-Declaration-of-Independence pastiche on any manifesto | "civic-declarative register ONLY; NOT for commercial product copy" |
| Nike "Dream Crazy" | "Believe in something. Even if it means sacrificing everything." anaphora | "anaphora limited to 1 series per piece; sacrifice-stake clause reserved" |
| Duolingo unhinged owl | ALL-CAPS threats / parasocial name-drops post-2023 cliché | "anchor ONLY to 2021-2022 formative window; avoid post-2023 style" |
| 許舜英 definitional inversion | Hollow 「X 是一種 Y」without cultural-critique payload | "require power-disparity word (政治/殖民/失敗/禁慾/危險)" |
| Extreme luxury manifesto brands (generic) | Ralph Lauren / Gucci aspirational-heritage auto-drift | "no nostalgia clichés (old-world / heritage / craftsmanship) without specific signifier" |

### Usage rule

Pass 3 agent reads this registry when selecting an anchor. If anchor listed here:
1. The mitigation clause becomes part of the rewrite prompt
2. Voice Consistency gate later checks the draft for leaked tropes per this clause

If anchor NOT listed here, Pass 3 applies anchor without mitigation (LOW risk default).

## Quick reference — anchor lookup flow

```
voice_reference = user-supplied string (or "default")
      ↓
Is it in craft-gate masters?
  {糸井重里, 岩崎俊一, 眞木準, 谷山雅計,
   許舜英, 李欣頻, 葉明桂}
      ├── YES → Tier 1: load jp/zh-copy-craft-lineage.md
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
- [jp-copy-craft-lineage.md](jp-copy-craft-lineage.md) — craft-gate target for JP canonical masters
- [zh-copy-craft-lineage.md](zh-copy-craft-lineage.md) — craft-gate target for ZH canonical masters
- Per-quadrant anchor files: `{jp,zh,en}-q{1,2,3,4}-anchors.md` — register-signal inventory
- [axis-extreme-anchors.md](axis-extreme-anchors.md) — axis-extreme landmarks (V2 expansion)
