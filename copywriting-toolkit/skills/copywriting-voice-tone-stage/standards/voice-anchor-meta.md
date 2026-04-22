---
title: Voice Anchor Meta
tier: 2
---

# Voice Anchor Meta

**Load scope**: Phase 6 Pass 3 — any branch. Always-on metadata for anchor operations.

**Content**: schema spec → selection rubric → over-mimic fallback registry → verified lineage map → cross-reference registry → cross-cultural label rubric → drift corrections → cross-master context → axis extreme candidates → quick reference flow.

**Consolidated in v1.13.0** from former `voice-anchor-meta-core.md` + `voice-anchor-meta-detail.md` + `axis-extreme-anchors.md`. The former split (hot-path vs deep-path) produced token-budget optimization at the cost of mental overhead tracking which file held which rule; v1.13.0 collapses into a single SSOT meta file.

## Purpose

This file provides the operational metadata Pass 3 needs to correctly read and apply ANY voice anchor — whether from craft-gate per-master `anchor-{slug}.md`, register-signal `{lang}-q{N}-anchors.md` router → `anchor-{slug}.md` body, or axis-extreme candidates. Schema + selection rubric + over-mimic mitigation + lineage map + cross-reference rules + cross-cultural mappings + drift corrections + cross-master context are ALL here.

## Schema (v2 — single active schema)

Source of truth spec: `docs/anchor-schema-v2.md`. Fields Pass 3 reads from each `anchor-{slug}.md`:

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

**Schema validation** (anchor passes iff ALL 5 hold):
1. Voice direction present (1 line, substantive)
2. Native critical read has ≥3 attributed phrases
3. Prose mechanics has ≥5 actionable rules
4. Examples has ≥5 verbatim with source
5. Don't / Over-mimic has failure mode + ≤15-word mitigation

**Dimension 6 consumer rule**: the over-mimic mitigation clause is read directly from the anchor's own `Don't / Over-mimic` block. This is the single source of truth for mitigation; the fallback registry (§Over-mimic mitigation fallback registry below) applies ONLY to the 9 no-anchor-file authors and 3 movement/campaign entries.

**v1 schema removed (v1.13.0)**: all 81 anchor files carry `schema_version: 2.0` frontmatter. Prior v1 schema documentation removed as dead code. The former §Schema version selector is also removed — Pass 3 assumes v2.

## Anchor selection rubric — 5 conditions

An anchor is valid for a given brief IF AND ONLY IF all 5 hold. **Note (v1.13.0 migration)**: starting v1.13.0, conditions 1-4 are enforced at library-entry CI lint time (`scripts/lint-anchor-library.py`), not at runtime. Runtime Pass 3 trusts that any anchor in the library has already passed 1-4. Condition 5 remains runtime-enforced.

### Condition 1: Corpus-depth floor

Anchor's LLM training corpus is DEEP or MEDIUM-DEEP. Proxy signals (any one):
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

Anchor with **documented advertising-craft lineage** to a verified copywriter citation (primary source = author's own book / verified interview / TCC 年鑑 / 宣伝会議 / Brain magazine) gets +1 tier. See §Verified lineage map below.

### Condition 5: Negation-of-axis rule (runtime-enforced)

When `brief.tone_cue` contains an **explicit negation of an axis or an axis-adjacent cluster** — e.g., "not corporate", "not artisan-snob", "not funny", "not preachy", "not aspirational" — Pass 3 auto-selector MUST:

1. Forbid the negated axis/cluster from consideration. Example: "not corporate" → Authority axis forbidden → Q1/Q2 candidates downgraded.
2. Record the forbidden axis in `voice_quadrant.rationale` so Phase 6 gates can verify the rewrite does not drift back.
3. If no anchor satisfies the negation (all candidates fail), emit a `violation` envelope to intake requesting tone_cue clarification.

Example from v1.9.x E2E (JP meditation app): `tone_cue: "calming, not corporate"` → Authority axis forbidden → Q1/Q2 craft-gate masters (糸井 / 岩崎 state-proposal) eliminated → Q3 private-space register selected (吉本ばなな).

### Safe-substitute lookup (broadened v1.11.1)

When `brief.voice_reference` names any master, Pass 3 MAY auto-suggest a safer alternative by querying anchor frontmatter:

```
candidates = [anchor for anchor in standards/anchor-*.md
              if named-master ∈ anchor.frontmatter.safe_substitute_for]
```

**Qualifying rule**: a candidate qualifies as a substitute IFF its over-mimic risk is **strictly lower** than the named master's. Risk order: `LOW < MEDIUM < MEDIUM-HIGH < HIGH < HIGH+`. Read the named master's risk from its own anchor frontmatter's `Over-mimic risk:` line; if the named master has no anchor file, fall back to §Over-mimic mitigation fallback registry below; if not in either, treat as `MEDIUM` (permissive default — substitute emits if substitute is LOW).

If a candidate exists AND is strictly lower-risk, Pass 3 emits `register_signal_applied.substitute_suggested = {slug, rationale}` alongside the primary selection. The user-specified master remains the default primary unless user confirms substitute in a follow-up turn.

**tone_cue contamination upgrade (v1.11.1)**: if `brief.tone_cue` contains tokens that match the substitute anchor's `Don't / Failure mode` warning about the named-master contamination, upgrade `substitute_suggested` to `substitute_recommended_strong` in the envelope — signals to Phase 6 that substitute isn't just safer but likely necessary to avoid the failure mode the user's own cue is invoking.

Current documented substitutes (from v1.10.0-v1.11.1 sweeps + v1.12.0 additions):
- `anchor-jp-yoshimoto-banana-j-bungaku.md`: `safe_substitute_for: [村上春樹]`
- `anchor-en-carver-working-class-precision.md`: `safe_substitute_for: [Hemingway]`
- `anchor-en-ephron-warm-wit.md`: `safe_substitute_for: [Didion, Joan Didion]`
- `anchor-en-hammett-terse-procedural.md`: `safe_substitute_for: [Chandler, Raymond Chandler]`
- `anchor-jp-tanikawa-shi-no-kotoba.md`: `safe_substitute_for: [糸井重里]`
- `anchor-zh-tw-pai-hsien-yung-elegiac-diaspora.md`: `safe_substitute_for: [張愛玲]`
- `anchor-zh-qianzhongshu-erudite-sardonic-metaphor.md`: `safe_substitute_for: [David Foster Wallace, DFW]`
- `anchor-jp-yoro-takeshi-baka-no-kabe.md`: `safe_substitute_for: [原研哉]`
- `anchor-jp-toyama-shigehiko-shikou-seiri.md`: `safe_substitute_for: [伊丹十三]`

### Automatic rejection

- Voice inseparable from ideological/traumatic content (三島 nationalist / 莫言 magical-realist-rural / 余華 death-content)
- Biographical-tragic weight overpowers style on bare name (顧城 / 海子 / Sylvia Plath)
- Corpus deep but LLM latent-space illegible (殘雪 experimental, certain avant-garde)
- Register non-transferable to commercial frame (Virginia Woolf interior, Beckett stripped)
- Register requires >800-token context to stabilise (DFW)
- Corpus THIN in target language (Yi Sang, heritage-only poets)

## Over-mimic mitigation fallback registry

When the listed anchor is invoked and no `anchor-{slug}.md` file exists, the corresponding mitigation clause MUST appear inline in the prompt or be enforced by the Voice Consistency gate.

### Source of truth (v1.13.0)

**Primary**: anchor file's own `Don't / Over-mimic` block (single source of truth). Pass 3 reads mitigation from the anchor file directly for ALL v2-migrated anchors.

**Fallback**: this registry covers TWO categories:

1. **9 authors with no anchor file** — registry-row entries only (anchor name + auto-leaked tropes + mitigation clause), NOT full anchor bodies. These authors are referenced by users but haven't been built out as full anchors.
2. **3 movement / campaign / brand-category entries** — rotating authorship / team-coauthored / generic category. Fail v2 inclusion criterion (individual-creator authorship); mitigation stays here as the only home.

### Registry table

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

### Usage rule

Pass 3 agent consults mitigation as follows:

1. **Anchor has `anchor-{slug}.md` file**: read mitigation from the anchor's own `Don't / Over-mimic` block. Do NOT look in this registry.
2. **Anchor is v1-only (no anchor file) OR movement/campaign/category entry**: read mitigation from this registry.
3. If anchor NOT listed in either place, Pass 3 applies anchor without mitigation (LOW risk default).

Voice Consistency gate (Dimension 6) applies the same precedence — anchor file is authoritative; registry is fallback for no-anchor-file entries.

## Verified lineage map

**Only 8 copywriter → literary-anchor lineages are primary-source verifiable.** All other claimed connections are stylistic parallel, NOT documented influence. Toolkit must not claim undocumented citation in rationale outputs.

| # | Copywriter | Literary anchor | Primary source | Confidence |
|---|---|---|---|---|
| 1 | 李欣頻 Lee Hsin-ping | 寺山修司 Terayama Shūji | 《誠品副作用》(新新聞文化, 1998) + 《拋開書本到街上去》系列 — 作者自述 | HIGH |
| 2 | 李欣頻 | 阿莫多瓦 Pedro Almodóvar | 《拋開電影到街上去》系列 — 作者自述 | HIGH |
| 3 | 李欣頻 | 徐四金 Patrick Süskind | 《拋開書本到街上去》系列 — 作者自述 | HIGH |
| 4 | 李欣頻 | 村上春樹 Murakami Haruki | 《拋開書本到街上去》系列 — 作者自述 | HIGH |
| 5 | 糸井重里 Itoi Shigesato | 谷川俊太郎 Tanikawa Shuntarō | ほぼ日刊イトイ新聞 repeated collaborations; 共著『ぼく』(2013) | HIGH |
| 6 | 葉明桂 Yeh Ming-kuei / 台灣奧美 | Peter Altenberg | 左岸咖啡館「我不在咖啡館，就在去咖啡館的路上」sinicized from Altenberg Viennese saying — documented in §Drift corrections catalog §Z1 below | HIGH |
| 7 | David Ogilvy | Strunk & White | *Ogilvy on Advertising* (1983), "How to Write Potent Copy" 章 explicit 推薦 | HIGH |
| 8 | Anglo copywriting canon | George Orwell "Politics and the English Language" (1946) | 直接影響 Strunk & White tradition + 廣告 craft rules 傳承 | HIGH (as canonical substrate, not single-copywriter citation) |

### Inferred parallels (MUST be marked as "stylistic parallel, NOT documented citation")

These stylistic resonances are critical-consensus but have NO primary-source citation. Toolkit MUST NOT claim them as documented lineage:

- 糸井重里 ← 宮沢賢治（「生きろ。」/「このへんないきもの」 resonance with 『銀河鉄道』childlike cosmic register）
- 許舜英 ← 張愛玲（aphoristic-density parallel 極強）
- 許舜英 ← Roland Barthes《神話作用》（意識形態時代結構語言學討論）
- 秋山晶 ← 松尾芭蕉（haiku resonance：「時は流れない」）
- 岩崎俊一 ← 佐野洋子（rumored but NOT documented）
- 全聯經濟美學 ← 王小波 irreverent-rational-wit（TW 青年 / CN intellectual 可能 cross-pollinate）
- 朱家鼎 鐵達時 ← 侯孝賢 / 王家衛 filmic-monologue（HK-TW-filmic era 交互影響）

## Cross-reference-valid-for registry

When an anchor is cited but `output_language` ≠ anchor's native language, Phase 5 cross-lang resolver consults this table to decide whether cross-reference is safe.

### Direction: JP → zh-TW (STRONG, documented cultural flow)

| JP anchor | zh-TW target registration | Strength | Evidence |
|---|---|---|---|
| 村上春樹 Murakami | 都會都市感 Q3 | STRONG | 李欣頻 documented cite; TW 1990s-2010s 譯本爆量 |
| 寺山修司 Terayama | 文青 provocative Q2 | STRONG | 李欣頻 documented cite |
| 谷崎潤一郎《陰翳礼讃》 | 設計 / craft Q4 | STRONG | 原研哉 MUJI aesthetic 已大量進入 TW lifestyle retail 詞彙 |
| 川端康成 | 時光緩拍 seasonal Q3 | STRONG | TW 誠品文青 register 底色 |
| 向田邦子 | 家庭 peer-intimate Q3 | STRONG | 昭和 / TW 文青 aesthetic 直承 |
| 谷川俊太郎 | 童稚宇宙 Q1/Q3 | STRONG | 糸井 ほぼ日 collab 已被 TW 廣告引述 |
| 宮沢賢治 | 童話 cosmic Q3 | STRONG | TW 教科書 canon-adjacent |
| 吉本ばなな | 都會哀愁 Q3 | STRONG | 1990s J-lit boom 譯本充分 |
| 糸井重里 | 狀態提案 peer-warm Q3 | STRONG | 糸井已為 TW 廣告界通識 |
| 岩崎俊一 | 余韻 Q2-edge | MEDIUM | TW 廣告界知名度 MEDIUM |
| クックパッド recipe step voice | Q4 操作 register | STRONG | 愛料理 / iCook 直接對應 |
| 北欧、暮らしの道具店 (Q4 subset) | 生活風格 EC Q4 | MEDIUM | PinkoiPicks 部分對應 |

### Direction: zh-TW → JP (WEAK — generally not used)

文化流向主要是 JP→TW 單向；zh-TW anchor 反向 fuel JP output 基本不建議（台湾ブーム 僅 tourism-adjacent，未到 copy 語感水準）。

### Direction: EN ↔ zh-TW (MEDIUM-STRONG via translation corpus)

| EN anchor | zh-TW target Q | Strength |
|---|---|---|
| Hemingway iceberg | Q1/Q4 | MEDIUM-STRONG (阿城 parallel via 中式 Hemingway critical consensus) |
| Joan Didion | Q2 | MEDIUM-STRONG (張愛玲 aphoristic parallel) |
| E.B. White / Strunk & White | all Q | STRONG (plain-style canon) |
| George Orwell "Politics and English" | all Q | STRONG (plain-style canon) |
| Raymond Carver | Q3/Q4 | MEDIUM (較少直接 TW 反映) |
| John McPhee | Q4 heritage | MEDIUM |
| Phoebe Waller-Bridge Fleabag | Q3 | MEDIUM (TW 年輕 SNS 詞彙少受直接影響) |
| Raymond Chandler | Q4 | MEDIUM (TW noir 傳統薄) |

### Direction: EN ↔ JP (MEDIUM via translation corpus)

| EN anchor | JP target Q | Strength |
|---|---|---|
| Hemingway | Q1/Q4 | MEDIUM-STRONG (日譯本爆量，阿城同一 iceberg lineage 亦 cross) |
| Didion | Q2 | MEDIUM |
| E.B. White / Orwell | all Q | STRONG (plain-style 廣告通識) |
| Raymond Chandler | Q4 | STRONG (日本 hardboiled 傳承充分，大藪春彦 等 direct descendant) |

## Cross-cultural unified label rubric (19 labels × 4 cultures)

When Pass 3 agent needs "find equivalent anchor in target culture", this matrix provides canonical mappings.

| Unified label | JP | ZH | EN |
|---|---|---|---|
| **iceberg-minimalism** | 太宰治 (compression) / 川端康成 (restraint) | 阿城 | Hemingway / Carver / Hempel |
| **aphoristic-observation** | 向田邦子 | 張愛玲 | Didion |
| **plain-style-editorial** | 村上春樹 (early) | 白先勇 | E.B. White / Orwell |
| **compassionate-absurd** | 吉本ばなな (warm) | 駱以軍 | Saunders / Waititi |
| **fourth-wall-confessional** | 酒井順子 | 李欣頻 (partial) | Waller-Bridge / Ephron |
| **heritage-detail-dense** | 司馬遼太郎 | — | McPhee |
| **hard-boiled-metaphor** | 大藪春彦 | (gap) | Chandler / Hammett |
| **dialogic-walk-and-talk** | 三谷幸喜 | (gap) | Sorkin |
| **childlike-cosmic-animism** | 宮沢賢治 | — | Saint-Exupéry |
| **clear-child-cosmic-poet** | 谷川俊太郎 | — | Mary Oliver |
| **shadow-aesthetic-craft** | 谷崎潤一郎《陰翳礼讃》 | 蔣勳 (adjacent) | John Berger |
| **poetic-provocative-street** | 寺山修司 | 王小波 (adjacent) | Allen Ginsberg |
| **monologue-fragment-temporal** | — | 王家衛 | — |
| **humane-vernacular-compassion** | — | 黃春明 / 吳念真 | Carver |
| **distant-everyday-uncanny** | 村上春樹 | — | Paul Auster |
| **elegiac-diaspora-memory** | — | 白先勇 | W.G. Sebald |
| **erudite-sardonic-metaphor** | 夏目漱石《猫》 | 錢鍾書《圍城》 | DFW (light only, Layer-1) |
| **zen-minimal-meditation** | 松尾芭蕉 | 周夢蝶 | — |
| **irreverent-rational-wit** | — | 王小波 | Kurt Vonnegut |

### Gap flags for future research

- **fourth-wall-confessional** KR — no anchor identified (scope-excluded anyway)
- **hard-boiled-metaphor** ZH — TW noir tradition thin
- **dialogic-walk-and-talk** ZH — no clear anchor; 王家衛 is monologue-type not dialogue-type

## Drift corrections catalog (pointer index)

All Z# attribution drifts except Z6 are **inlined in corresponding anchor files** per v2 SSOT rule. This catalog keeps Z6 full text (no anchor home for 孫大偉) + pointer index for discoverability.

| # | Drift | Authoritative source |
|---|---|---|
| Z1 | Altenberg sinicized (NOT 葉明桂 original) | `anchor-zh-tw-ye-mingui-strategic-aphorism.md §Don't / Over-mimic` |
| Z2 | 「拋開書本到街上去」李欣頻 ref 寺山修司 1967 | `anchor-zh-tw-lee-hsin-ping-literary-consumption.md §Metadata` |
| Z3 | 意識形態 founded 1987 (not 1988); canonical window 1988-1999 | `anchor-zh-tw-xu-shunying-ideological-definitional.md §Metadata` |
| Z4 | Content-farm "中興百貨 文案" source discipline | `anchor-zh-tw-xu-shunying-ideological-definitional.md §Metadata` |
| Z5 | 多喝水 NOT 吳念真 (奧美台灣 in-house) | `anchor-zh-tw-wu-nien-jen-taiyu-peer-intimate.md` |
| **Z6** | **孫大偉 agency: 台灣奧美 → 偉太 (NOT JWT)** | **(kept here — no dedicated 孫大偉 anchor)** |
| Z7 | 長榮〈I SEE YOU〉VO is 金城武, NOT 吳念真 | `anchor-zh-tw-wu-nien-jen-taiyu-peer-intimate.md` |
| Z8 | 全聯經濟美學 creative lead = 龔大中 (not 林敬凱 / 邱彥翔) | `anchor-zh-tw-gong-dazhong-quanlian-economics-aesthetics.md` + `zh-q3-anchors.md` |
| Z9 | KC Tsang (NOT Calvin Choy); agency path: Ogilvy → Bozell → BBDO HK → 陳曾黃朱梅 | `anchor-zh-hk-kc-tsang-cantonese-vernacular-pun.md` |
| Z10 | 全聯 2006-2014 TV-era is **Q3-CENTER** (aphoristic), NOT Q3-extreme | `anchor-zh-tw-gong-dazhong-quanlian-economics-aesthetics.md` + `zh-q3-anchors.md` |
| Z11 | 意識形態廣告 co-founded 許舜英 + 鄭松茂 (1987) — not 許舜英 alone | `anchor-zh-tw-xu-shunying-ideological-definitional.md` |
| JP-8 | リゲイン「24時間戦えますか？」NOT 岩崎俊一 | `anchor-jp-iwasaki-shunichi-yonin.md §Don't / Over-mimic` + Metadata |

### Z6 — 孫大偉 agency (only drift with no anchor home)

**Drift**: 孫大偉 sometimes cited as 智威湯遜 (J. Walter Thompson) affiliated.

**Correct**: 台灣奧美 創意總監 (1980s-2000s) → 汎太廣告 → 偉太廣告 (1991+ 創辦人). NOT JWT.

**Why here not inline**: 孫大偉 has no dedicated `anchor-{slug}.md` file (not in the 81-anchor v2 inventory). If a future brief references 孫大偉, Pass 3 conditional load triggers this section for the correction. If a 孫大偉 anchor is created in a future version, this entry migrates to the anchor's Metadata.

## Cross-Master Context

This section consolidates cross-master attribution corrections, generational context, and inter-master comparison tables previously maintained in `jp-copy-craft-lineage.md` + `zh-copy-craft-lineage.md`. Per-master voice bodies (register, prose mechanics, examples, Don't blocks) already live in each `anchor-{slug}.md`; this section covers what IS genuinely cross-master.

**Load scope**: Pass 3 conditional (attribution risk / cross-master comparison / era context triggers) + Pass 3d register-signal (always loaded with this file).

### Primary Sources (aggregate)

**JP craft-gate masters**:
- **糸井重里**: ほぼ日刊イトイ新聞 archive; 2024 コピー10 series (landmark copies discussed with 谷山雅計); TCC コピー年鑑.
- **岩崎俊一**: 『幸福を見つめるコピー』(東急エージェンシー, 2009; restored 2015). 宣伝会議 memorial articles. TCC コピー年鑑.
- **眞木準**: TCC コピー年鑑. 宣伝会議賞 眞木準賞.
- **谷山雅計**: 『広告コピーってこう書くんだ！読本』『人の心を動かす「伝える」技術』. TCC コピー年鑑.
- **Cross-reference JP sources**: TCC official site, iso-labo.com, kai-story.com, AdverTimes, EDIMAG.

**ZH craft-gate masters**:
- **許舜英**: 《許舜英購物日記》(漫遊者文化, 2011); 《我不是一本型錄》文集; 中興百貨 1988–1999 campaign archive (意識形態廣告公司作品集, 數英 / 壹讀 / Brain 340 期 2004).
- **李欣頻**: 《誠品副作用》(新新聞文化, 1998); 《廣告副作用．藝文篇》; 《李欣頻的廣告四庫全書》(時報 2016, 1991-2016 典藏); 《李欣頻的寫作之道》(2019).
- **葉明桂**: 《品牌的技術和藝術：向廣告鬼才葉明桂學洞察力與故事力》(天下文化, 2017; ISBN 9789864792375); 左岸咖啡館 1998– campaign archive (台灣奧美作品集, 數英 / 廣告雜誌 122 期); 奧美官方簡歷.
- **Cross-reference ZH sources**: 動腦 Brain magazine archive (brain.com.tw), 天下雜誌, 經理人月刊, 數英 digitaling.com, 壹讀 read01.com, 設計之家 sj33.cn.

### Critical Attribution Corrections

See §Drift corrections catalog (pointer index) above for the complete list (Z1-Z11 + JP-8). All drifts except Z6 are inlined at their authoritative per-anchor source; Z6 (孫大偉) is kept in full above since no 孫大偉 anchor exists.

### Generational Context

#### JP (1947-1948 cohort, 1980s copywriter boom)

糸井重里 (1948–), 岩崎俊一 (1947–2014), 眞木準 (1948–2009), 谷山雅計 (1961–, later cohort). All active during the 1980s "コピーライターブーム":

- Mass media dominance (TV CM + print + 交通広告)
- Copywriter as cultural celebrity
- Copy judged by artistic merit, not click-through rate
- TCC (東京コピーライターズクラブ) annual as the industry's canon

These voices emerged from a media environment where **a single line needed to work across millions of viewers with no targeting, no A/B testing, and no retargeting**. This constraint produced copy that prioritized universality, ambiguity, and cultural resonance over specificity and conversion optimization.

#### ZH (1980s-1990s TW 解嚴後新都會消費主義覺醒)

許舜英 / 李欣頻 / 葉明桂 — all three masters emerged from 1980s–1990s 台灣解嚴後新都會消費主義覺醒:

- 1987 解嚴 → 1990s 文化開放 + 消費升級 + 女性經濟獨立
- 意識形態廣告公司 (1987–2008) as cultural focal point for "有態度的消費" — advertising as cultural criticism, not product description
- 誠品書店 1989 敦南店 → 1995 遷址 → 2000s 全島連鎖, anchoring "書店 = 生活提案" category that did not exist before
- 台灣奧美 under 莊淑芬 / 葉明桂 leadership institutionalizing strategic-planning-first advertising

These voices emerged from a media environment where **a full-page 報紙廣告 or one-minute TVC had to carry an entire cultural thesis**. Reader hailed as **literate cultural peer**, not conversion target. Produces copy privileging aphoristic density, cross-domain vocabulary transplant, cultural-reference-dense hooks over specificity and call-to-action clarity.

**Warning**: applying these voices uncritically to 2020s performance-marketing contexts produces beautiful copy that does not convert. Use as voice reference, not targeting strategy.

### LLM Reproduction Gap — Cross-master Summary (ZH craft-gate)

| Master | Hardest dimension to reproduce | Canonical failure mode | Single best mitigation gate |
|--------|-------------------------------|------------------------|-----------------------------|
| 許舜英 | 文化批判 payload underneath definitional inversion | Hollow 「X 是一種 Y」without power-disparity word | Require a power-disparity word (政治/殖民/失敗/禁慾/危險) in the sentence |
| 李欣頻 | Named-reference specificity in enumeration | Generic-list rhythm without load-bearing names | Require 4 specific named cultural figures; confirm removing one breaks the rhythm |
| 葉明桂 / 左岸 | Strategic category-reframe underneath atmospheric prose | Pretty scene without brand thesis | Require answering "what are we actually selling that competitor is not?" before drafting scene |

All three masters share a common LLM-failure pattern: **surface grammar is easy to copy; the cultural / strategic / critical payload underneath is not**. ZH Q2 literary voice is defined by payload + grammar in tension; reproducing grammar alone produces what Chinese copywriting critics call 「文青腔」— a voice that sounds like the canon but means nothing.

### Voice selection guidance (cross-master)

| Voice reference | Best fit | Avoid when |
|-----------------|----------|------------|
| 許舜英 | Fashion / luxury retail / cultural-criticism-tolerant brands; audiences comfortable with provocation | Mass-market FMCG; youth-targeted short-form; any context where power-disparity vocabulary reads as alienating |
| 李欣頻 | Bookstores / lifestyle retail / cultural institutions; audiences who read named references | Utility products; price-sensitive campaigns; audiences without literary-reference capital |
| 葉明桂 / 左岸 | Long-arc brand-building for premium consumer goods with strategic category-reframe potential | Performance-marketing contexts requiring measurable CTR; short-term promotional windows |

### Cross-master Anti-Patterns

- **Mixing two ZH masters' voices in one piece** — registers conflict: 許舜英's aphoristic density overwhelms 李欣頻's breathing rhythm; 葉明桂 / 左岸's first-person intimacy collapses 許舜英's impersonal critique stance. One voice per piece.
- **Using 許舜英's definitional inversion for products without cultural-critique capacity** — 民生用品 ad as "X 就是一種 Y" reads pretentious, not insightful. Inversion requires cultural tension to inversely mirror; if product category has no such tension, form does not apply.
- **Applying 李欣頻's named-reference enumeration to audiences without literary-reference capital** — voice assumes reader recognizes 寺山修司 / 阿莫多瓦 / 徐四金. For audiences outside that reference set, copy reads as cultural gatekeeping rather than invitation.
- **Reproducing 左岸 atmospheric prose without the strategic category-reframe underneath** — atmosphere without brand thesis produces interchangeable café copy. 葉明桂's method is explicit: strategy first, copy second.
- **Ignoring generational context** — these voices emerged from 1990s–2000s pre-digital media. Applying to 2020s performance-marketing contexts produces beautiful copy that does not convert.
- **Claiming LLM can "寫出 許舜英 / 李欣頻 / 左岸 style" or "岩崎 / 糸井 / 眞木 style"** — LLM reproduces grammar but consistently fails on payload. Use the mitigation gates per master (via each anchor's `Don't / Over-mimic` block + this cross-master summary), not the naive claim.

### Cross-tradition transplant forbidden

Never force JP lineage patterns onto ZH output (or vice versa); never force either onto Anglo output. Each culture's voice tradition emerged from distinct media ecology, critical apparatus, and reader-register expectations. Cross-reference-valid-for registry (see above) documents where cross-fertilization is safe; outside those documented links, **do not transplant**.

## Axis Extreme candidates (cross-language)

**Status**: **MVP PLACEHOLDER — V2 research pending**. Content is structural stub + candidate list; full corpus, primary sources, verbatim lines, voice signature dimensions to be populated in V2 research wave.

### Overview

Axis extremes are voices that sit **extreme on one axis while neutral on the other**. They genuinely don't fit any Q1-Q4 quadrant because they deliberately refuse one axis entirely. Uncommon (~5-10% of briefs) but valuable for edge cases.

Four axis extremes:

1. **Authority-extreme / Reason-Emotion neutral** — pure institutional voice that refuses both argumentation AND emotion (BBC News, Supreme Court decisions)
2. **Affinity-extreme / Reason-Emotion neutral** — pure peer voice that refuses both argumentation AND emotion (Mailchimp help center neutral mode, Reddit r/askhistorians)
3. **Reason-extreme / Authority-Affinity neutral** — pure analytical voice that refuses both institutional AND peer framing (Wikipedia, Stratechery analytical)
4. **Emotion-extreme / Authority-Affinity neutral** — pure emotional voice that refuses both institutional AND peer framing (Hallmark greeting cards, 昭和 CM お袋の味, cinematic MV VO)

Use case triggers: brief needs news reportage / documentation / emotional film voice / neutral documentation — where standard Q1-Q4 quadrant feels wrong-shaped.

### Landmark: axis-authority-extreme

Extreme institutional authority, Reason/Emotion neutral. Pure reportage / statement.

Candidate anchors (V2 research):
- **EN**: BBC News VO register / Supreme Court decisions / FT Pink Paper / GOV.UK style
- **JP**: NHK ニュース9 reportage / 官邸声明 / 最高裁判決書
- **zh-TW**: 中央社 wire / 行政院聲明 / 最高法院判決

`<!-- V2 research needed: primary sources + verbatim lines + voice signature dimensions + over-mimic assessment -->`

### Landmark: axis-affinity-extreme

Extreme peer voice, Reason/Emotion neutral. Pure peer-information / neutral help.

Candidate anchors (V2 research):
- **EN**: Mailchimp help center neutral mode / Reddit r/askhistorians peer-expert / StackOverflow top-answer voice
- **JP**: (gap — research candidate: 楽天 seller neutral Q&A / はてな知識系)
- **zh-TW**: (gap — research candidate: 批踢踢 資料串 / Dcard 冷知識小編)

`<!-- V2 research needed -->`

### Landmark: axis-reason-extreme

Extreme analytical, Authority/Affinity neutral. Pure logic / documentation register.

Candidate anchors (V2 research):
- **EN**: Wikipedia article voice / Stratechery analytical mode / The Atlantic analytical essay
- **JP**: はてな科学 / ニコニコ大百科 / Wikipedia-ja formal entry
- **zh-TW**: 科學人雜誌 / 天下雜誌 analytical feature / 得到 App 知識產品 (CN 但 zh 通用)

`<!-- V2 research needed -->`

### Landmark: axis-emotion-extreme

Extreme emotion, Authority/Affinity neutral. Pure emotional / cinematic register.

Candidate anchors (V2 research):
- **EN**: Hallmark greeting cards / Pixar opening-sequence VO / cinematic MV narration
- **JP**: 昭和 CM お袋の味 情感派 VO / TV ドキュメント涙誘い narration
- **zh-TW**: 電影 MV VO (侯孝賢-school) / 紀錄片情感旁白

`<!-- V2 research needed -->`

### V2 research triggers

Populate these sections when any of:
1. Real brief triggers `voice_quadrant.position = axis-*` and fallback to Q1-Q4 quadrant produces wrong-shaped output
2. User explicitly requests BBC-news-voice / Hallmark-voice / Wikipedia-voice type anchors
3. Dedicated research cycle scheduled for axis-extreme expansion

## Quick reference — anchor lookup flow

```
voice_reference = user-supplied string (or "default")
      ↓
Is voice_reference a craft-gate master?
  {糸井重里, 岩崎俊一, 眞木準, 谷山雅計, 仲畑貴志,
   許舜英, 李欣頻, 葉明桂}
      ├── YES → Pass 3 Craft Gate: load anchor-{slug}.md + this file
      │
      └── NO → Is voice_quadrant.position = "axis-*"?
           ├── YES → Pass 3 Axis Extreme: load this file §Axis Extreme
           │
           └── NO → Pass 3 Register Signal:
                    - Load this file (schema + rubric + mitigation + lineage + cross-ref)
                    - Load {output_language}-q{voice_quadrant.primary}-anchors.md
                      (section-targeted if position provided)
                    - Cross-lang STRONG? Also load {cross-lang}-q{N}-anchors.md section
```

## Cross-references

- Per-quadrant anchor files: `{jp,zh,en}-q{1,2,3,4}-anchors.md` — register-signal inventory
- Per-master biographical arc + campaign detail: see `docs/voice-anchor-notes/pilot-layer1-v2-{slug}.md` files (Layer 2/3 research artifacts, Pass 3 does NOT load)
- Anchor schema spec: `docs/anchor-schema-v2.md`

## Migration history

- **v1.5.0 - v1.9.2**: split as `voice-anchor-meta-core.md` (hot path — schema + rubric + mitigation) + `voice-anchor-meta-detail.md` (deep path — lineage / cross-ref / label rubric / corrections / cross-master context)
- **v1.13.0** (this file): merged into single `voice-anchor-meta.md`; `axis-extreme-anchors.md` content absorbed as §Axis Extreme section; v1 schema references removed as dead code; 4-condition rubric still documented here but runtime enforcement moves to `scripts/lint-anchor-library.py` at library-entry CI time
