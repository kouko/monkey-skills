# Layer-0 Literary / Screen Voice Register Primers — Research

**Branch**: `research/copywriting-voice-anchor-expansion`
**Date**: 2026-04-21
**Status**: Research complete; layers with earlier `voice-anchor-research.md` (brand-era + persona)

## Why Layer-0

Existing anchor library (copywriter-centric: 糸井 / 許舜英 / David Abbott etc.) suffers a **training-corpus depth asymmetry**:

| Anchor type | LLM training corpus | Trigger token cost | Style recall strength |
|---|---|---|---|
| Copywriter persona | 10-30 pieces | 400-800 token lineage file | WEAK (LLMs document reproduction gap) |
| Brand-era | 100+ pieces | brand-entry + era | MEDIUM |
| **Literary author (Murakami / Hemingway / 張愛玲)** | **1000+ pieces + translations + criticism + academic sub-field** | **2-3 words** | **STRONG (LLM pre-trained to pastiche them)** |
| **Screenwriter / playwright (Chekhov / Sorkin / 王家衛 / 坂元裕二)** | **scripts + film criticism + dialogue-scene citations** | **2-3 words** | **STRONG** |

Literary / screen anchors should be **Layer-0 register primer** (tonal filter applied before brand-era + persona layers). Copywriter persona drops to **craft-depth mitigation gate** (how the literary voice was shaped into selling discipline).

## Key risk — pastiche without selling discipline

Literary voice alone produces "poetic but doesn't sell" output. Layer-0 must pair with Layer-1 brand-era to inherit selling discipline:

- ❌ "Murakami style for a coffee ad" → atmospheric description, no CTA
- ✅ Layer-0 `Murakami-detached-domestic` + Layer-1 `左岸咖啡館 brand-era` + mitigation `no jazz / no cats / no wells / no whisky`

## Verified advertising-literary lineage map (6 primary sources)

Only **6 copywriter → literary-author lineages** are primary-source verifiable. All other claimed connections ("許舜英 ← 張愛玲", "糸井 ← 宮沢賢治") are stylistic parallel, NOT documented influence. Toolkit must not claim undocumented citation.

| Copywriter | Literary anchor | Primary source | Confidence |
|---|---|---|---|
| **李欣頻** | 寺山修司 | 《誠品副作用》+《拋開書本到街上去》系列，作者自述 | HIGH |
| **李欣頻** | 阿莫多瓦 Almodóvar | 《拋開電影到街上去》系列 | HIGH |
| **李欣頻** | 徐四金 Patrick Süskind | 同系列 | HIGH |
| **李欣頻** | 村上春樹 | 《拋開書本到街上去》 | HIGH |
| **糸井重里** | 谷川俊太郎 | ほぼ日刊イトイ新聞 repeated collaborations; 共著『ぼく』(2013) | HIGH |
| **葉明桂 / 台灣奧美** | Peter Altenberg | 已 documented in repo zh-lineage drift Z1 | HIGH |
| **David Ogilvy** | Strunk & White | *Ogilvy on Advertising* (1983) "How to Write Potent Copy" 章 explicit 推薦 | HIGH |
| **George Orwell** (不是 copywriter but 廣告 canon 吸收) | "Politics and the English Language" (1946) | 直接影響 Strunk & White tradition 及 Anglo copy craft | HIGH (as canonical substrate) |
| **박웅현 Park Woong-hyun** | 김훈 / Milan Kundera / Kazantzakis / Dostoevsky / Oscar Wilde | 《책은 도끼다》(2011) 書名 from Kafka「書は凍れる海を割る斧でなければならない」 | HIGH (requires book ToC verification) |

**Drift protection**: inferred parallels MUST be marked `[stylistic parallel — NOT documented citation]`. Examples:

- 糸井重里 ← 宮沢賢治：stylistic resonance（「生きろ。」/「このへんないきもの」）但 **NO primary source**
- 許舜英 ← 張愛玲：aphoristic-density parallel 極強但 **NO primary source**
- 許舜英 ← Roland Barthes《神話作用》：意識形態時代結構語言學討論但 **NO primary source**
- 秋山晶 ← 松尾芭蕉：haiku resonance（「時は流れない」）但 **NO primary source**
- 岩崎俊一 ← 佐野洋子：rumored but **NO primary source**

## Consolidated Top-24 Layer-0 anchors (cross-cultural)

Ranked by composite score: LLM corpus depth × register transferability × over-mimic control × label clarity × documented-lineage bonus.

### Tier A — HIGH priority (12 primary anchors)

| # | Culture | Anchor | Trigger | Quadrant | Corpus | Over-mimic | Documented lineage |
|---|---|---|---|---|---|---|---|
| L1 | JP | **谷川俊太郎 Tanikawa Shuntaro** | `tanikawa-clear-child-cosmic` | Q1/Q3 | DEEP | LOW | ✅ 糸井 ほぼ日 |
| L2 | ZH | **張愛玲 Eileen Chang** | `eileen-chang-aphoristic-observation` | Q2 | DEEP++ | MEDIUM | [parallel only] 許舜英 |
| L3 | EN | **E.B. White / Strunk & White** | `white-limpid` | all Q | DEEP | LOW | ✅ Ogilvy cite |
| L4 | EN | **Joan Didion** | `didion-observational` | Q2/Q3 | DEEP | MED-HIGH | [inferred] |
| L5 | JP | **谷崎潤一郎《陰翳礼讃》** | `tanizaki-inei-shadow-aesthetic` | Q4 craft | DEEP | LOW | [inferred] 原研哉 |
| L6 | JP | **川端康成 Kawabata** | `kawabata-sensory-ellipsis` | Q3/Q4 | DEEP | LOW-MED | [inferred] JR東海 |
| L7 | EN | **Phoebe Waller-Bridge** (Fleabag) | `pwb-fourth-wall` | Q3 | MEDIUM-DEEP | MEDIUM | — contemporary DTC dominant |
| L8 | EN | **George Orwell** (Politics & English) | `orwell-plain-style` | all Q | DEEP | LOW | ✅ Anglo copy canon |
| L9 | JP | **寺山修司 Terayama** | `terayama-poetic-provocative-street` | Q2 | MED-DEEP | MEDIUM | ✅ 李欣頻 cite |
| L10 | ZH | **阿城 A Cheng** | `a-cheng-iceberg-laconic` | Q1 | MED-DEEP | LOW | [parallel] Hemingway |
| L11 | JP | **向田邦子 Mukoda Kuniko** | `mukoda-domestic-intimacy-with-bite` | Q3 | MED-DEEP | LOW | Source node (TV+CM 脚本家) |
| L12 | EN | **Nora Ephron** | `ephron-warm-wit` | Q3 | DEEP | LOW-MED | [inferred] |

### Tier B — MEDIUM priority (12 supporting anchors)

| # | Culture | Anchor | Trigger | Quadrant | Notes |
|---|---|---|---|---|---|
| L13 | JP | 宮沢賢治 Miyazawa Kenji | `miyazawa-childlike-cosmic-animism` | Q3 | [parallel] 糸井 — DO NOT claim cite |
| L14 | JP | 吉本ばなな Banana Yoshimoto | `yoshimoto-gentle-domestic-grief` | Q3 | safer Murakami alt |
| L15 | ZH | 王家衛 Wong Kar-wai | `wkw-monologue-fragment-temporal` | Q2/Q3 | HIGH over-mimic, strong mitigation required |
| L16 | ZH | 朱天文 Chu Tien-wen | `chu-tien-wen-temporal-slowness` | Q3/Q4 | TW premium nostalgia |
| L17 | ZH | 王小波 Wang Xiaobo | `wangxiaobo-irreverent-rational-wit` | Q1/Q2 | CN intellectual-populist |
| L18 | EN | Raymond Carver | `carver-minimal-precision` | Q3/Q4 | safer Hemingway alt |
| L19 | EN | George Saunders | `saunders-compassionate-absurd` | Q3 | contemporary DTC |
| L20 | EN | John McPhee | `mcphee-detail-dense` | Q4 heritage | heritage longform, under-used |
| L21 | EN | Raymond Chandler | `chandler-hard-boiled` | Q4 | metaphor cap required |
| L22 | EN | Aaron Sorkin | `sorkin-walk-and-talk` | Q1/Q4 | dialogic brand film |
| L23 | KR | 한강 Han Kang | `hankang-restrained-visceral` | Q2 | post-Nobel 2024 corpus boost |
| L24 | KR | 봉준호 Bong Joon-ho | `bong-class-satire` | Q4 | post-Oscar corpus |

### Tier C — SKIP (reasons vary)

| Anchor | Reason |
|---|---|
| 三島由紀夫 | Ornate-violent-nationalist; HIGH over-mimic (seppuku leak) |
| 莫言 | Hallucinatory-baroque-rural; content overrides style |
| 殘雪 | Experimental; near-zero commercial transfer |
| 金庸 | HIGH+++ over-mimic (江湖/內功 auto-leak); niche wuxia only |
| Hemingway | Over-prompted; prefer Carver/Hempel |
| Virginia Woolf | Interior register too literary |
| Beckett | Stripped to blank output |
| DFW | Runaway maximalism; Layer-1 only |
| Ellroy | Telegraph brittle; over-mimic extreme |
| 이상 Yi Sang | LLM corpus too thin |
| 顧城 / 海子 | Biographical-tragic weight overpowers |
| Cormac McCarthy | Polysyndeton auto-leak; niche-only |

## LLM over-mimic mitigation registry (load-bearing)

Without these mitigation clauses, bare name-mention triggers runaway pastiche. Each MUST appear inline when the corresponding trigger is used.

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
| Hemingway | "He was tired. The whisky was cold." + he-said/she-said | "pair with Carver/Didion; forbid dialogue-tag chains >2" |
| Didion | "It meant nothing. It meant everything." antithesis tic | "cap rhetorical-antithesis to 1 per 150 words" |
| Chandler | "Her eyes were like [noun]" simile cascade | "cap similes to 1 per 50 words" |
| McCarthy | "and X and Y and Z" polysyndeton | "forbid triple-conjunction chains" |
| Sorkin | "You want X? Let me tell you about X" rhetorical-Q-then-A | "forbid rhetorical-question-plus-answer pattern" |
| DFW | Nested footnotes/parentheticals | "Layer-1 only, never Layer-0" |
| Ellroy | Telegraph fragments | "avoid for Layer-0 entirely" |

## Cross-cultural unified style-label rubric

Layer-0 labels unify across JP/ZH/EN/KR. Copywriter can pick one axis across cultures, producing consistent voice direction with culture-appropriate anchors.

| Unified label | JP | ZH | EN | KR |
|---|---|---|---|---|
| **iceberg-minimalism** | 太宰治 (compression) / 川端康成 (restraint) | 阿城 | Hemingway / Carver / Hempel | 김훈 Kim Hoon |
| **aphoristic-observation** | 向田邦子 | 張愛玲 | Didion | (한강 *White Book* partial) |
| **plain-style-editorial** | 村上春樹 (early) | 白先勇 | E.B. White / Orwell | 김영하 Kim Young-ha |
| **compassionate-absurd** | 吉本ばなな (warm) | 駱以軍 | Saunders / Waititi | 박민규 / 정세랑 |
| **fourth-wall-confessional** | 酒井順子 | 李欣頻 (partial) | Waller-Bridge / Ephron | — |
| **heritage-detail-dense** | 司馬遼太郎 | — | McPhee | 김훈 |
| **hard-boiled-metaphor** | 大藪春彦 | gap | Chandler / Hammett | 편혜영 Pyun Hye-young |
| **dialogic-walk-and-talk** | 三谷幸喜 | gap | Sorkin | 봉준호 Bong |
| **childlike-cosmic-animism** | 宮沢賢治 | — | Saint-Exupéry | — |
| **clear-child-cosmic-poet** | 谷川俊太郎 | — | Mary Oliver | — |
| **shadow-aesthetic-craft** | 谷崎潤一郎《陰翳礼讃》 | 蔣勳 | John Berger | — |
| **poetic-provocative-street** | 寺山修司 | 王小波 | Allen Ginsberg | — |
| **monologue-fragment-temporal** | — | 王家衛 | — | — |
| **humane-vernacular-compassion** | — | 黃春明 / 吳念真 | Carver | — |
| **distant-everyday-uncanny** | 村上春樹 | — | Paul Auster | — |
| **elegiac-diaspora-memory** | — | 白先勇 | W.G. Sebald | — |
| **erudite-sardonic-metaphor** | 夏目漱石《猫》 | 錢鍾書《圍城》 | DFW (light) | — |
| **zen-minimal-meditation** | 松尾芭蕉 | 周夢蝶 | — | — |
| **irreverent-rational-wit** | — | 王小波 | Kurt Vonnegut | — |

**Gaps to flag for future research**: fourth-wall-confessional (KR), hard-boiled-metaphor (ZH), dialogic-walk-and-talk (ZH).

## Candidate-selection rubric

**To qualify as Layer-0 register primer, an author must meet ALL 4:**

1. **Corpus-depth floor**: DEEP or MEDIUM-DEEP in LLM training. Proxy: (a) translated to ≥3 languages, OR (b) school-textbook canon in ≥1 major market (JP/TW/HK/CN/KR/EN), OR (c) dedicated academic sub-field (張學 / 村上學 / Joyce studies).
2. **Style-label specificity**: expressible in 1-3 words + ONE memorable formal feature. If paragraph-level description needed → REJECT.
3. **Transferability ≥ MEDIUM**: at least one Q1/Q2/Q3/Q4 explicitly gains from the voice.
4. **Over-mimic risk < HIGH** natively, OR mitigation clause fits in ≤15 words.

**Priority boost (+1 tier)**:
- Documented advertising-craft lineage (primary source: author's own book / verified interview / TCC 年鑑 / 宣伝会議 / Brain magazine)

**Automatic rejection**:
- Voice inseparable from ideological / traumatic content (三島, 莫言 content-mode, 余華)
- Biographical-tragic weight overpowers style on bare name (顧城, 海子, Plath)
- Corpus deep but LLM latent-space illegible (殘雪, experimental poets)
- Register non-transferable to commercial frame (Woolf interior, Beckett stripped)
- Register requires >800-token context to stabilise (DFW)
- Corpus THIN in target language (이상, heritage-only poets)

## Integration into pipeline

### Phase 0 / Phase 1 brief enhancement

Add optional field `literary_primer` in `brief.tone_notes` schema:

```json
{
  "tone_notes": {
    "literary_primer": {
      "trigger": "eileen-chang-aphoristic-observation",
      "mitigation": "no 月亮 / 華美的袍 imagery",
      "paired_brand_era": "中興百貨 1988-1999"
    }
  }
}
```

Single field captures: trigger + mitigation + pairing. ~30 tokens. Downstream consumers: Phase 4 drafter, Phase 5 voice-quadrant, Phase 6 voice-tone.

### Phase 5 voice-quadrant extension

When selecting brand-era anchor, optionally select Layer-0 primer from cross-cultural rubric. Validation: primer's quadrant must be compatible with brand-era quadrant (not diagonal).

### Phase 6 voice-tone gate

Existing Voice Consistency gate adds check: did the draft preserve the Layer-0 register without triggering over-mimic failure mode? Evaluator reads mitigation clause and checks for forbidden tropes.

### Phase 8 8b Form-Check

If primer invoked, 8b checks: (a) primer's commercial-register-bridge was achieved (selling discipline preserved), (b) no over-mimic tropes leaked.

## Proposed file structure

```
copywriting-toolkit/skills/copywriting-voice-tone-stage/standards/
├── jp-copy-craft-lineage.md          (existing — persona)
├── zh-copy-craft-lineage.md          (existing — persona)
├── kr-copy-craft-lineage.md          (NEW — persona, from Tier A research)
├── en-copy-craft-lineage.md          (NEW — persona, from Tier A research)
├── literary-register-primers.md      (NEW — Layer-0 anchors, ~24 entries + rubric + mitigation registry)
├── lineage-verified.md               (NEW — 6 primary-source-verified citations + inferred-parallel drift-protection)
└── voice-and-tone.md                 (existing)
```

`literary-register-primers.md` content split:
- §Rubric (4-condition selection + auto-reject)
- §Tier A/B/C table (all 24 anchors with trigger + quadrant + mitigation)
- §Cross-cultural unified-label rubric matrix
- §Over-mimic mitigation registry (15 entries)
- §Integration usage per Phase

## Open decisions (user input)

1. **Adopt Layer-0 framework**: YES / NO / MODIFIED
2. **File split**: one monolithic `literary-register-primers.md` vs split by culture (`jp-literary-primers.md` + `zh-literary-primers.md` + ...)
3. **Trigger lexicon standardization**: use English kebab-case (`eileen-chang-aphoristic-observation`) globally, or localize (`張愛玲-警句凝練` for zh users)?
4. **Verification of unverified lineage claims**: source-check 박웅현《책은 도끼다》ToC + Ogilvy《Confessions》 Maugham reference before committing to the "6 verified" list?
5. **Inferred-parallel handling**: document as "stylistic parallel (NOT documented citation)" with explicit language, OR omit entirely to avoid confusion?
6. **Envelope schema addition**: add `literary_primer` field to brief schema, or keep as free-form inline prompt guidance?

## Research sources

- Both Layer-0 research streams (JP/ZH + EN/KR) relied on published primary sources:
  - Author own books (李欣頻《誠品副作用》, 谷山雅計書, 梅田悟司書, 박웅현《책은 도끼다》, Ogilvy《Confessions of an Advertising Man》《Ogilvy on Advertising》, Fried & DHH《Rework》, Levenson《Bill Bernbach's Book》)
  - Copywriter memoirs / interviews (Brain magazine, 宣伝会議, 數英, 動腦)
  - Academic & literary criticism corpora (張學, 村上學, Nobel laureates)
  - Wikipedia article depth as LLM-training-proxy

- Full transcripts available at `/private/tmp/claude-501/` agent output files (session-scoped).
