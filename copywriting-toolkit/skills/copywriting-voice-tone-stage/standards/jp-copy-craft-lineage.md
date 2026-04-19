---
title: JP Copy Craft Lineage — 糸井重里 / 岩崎俊一 / 眞木準 Voice Deep Dives
tier: 3
---

# JP Copy Craft Lineage — 糸井 / 岩崎 / 眞木

Tier 3 standard: fully self-contained. Deepens the voice master
references introduced in `short-form-catchcopy-canon.md` §Voice
Master References. Where the short-form canon provides 2-3 line
summaries per master, this standard provides full voice analysis:
representative works corpus, voice signature identification, stylistic
grammar patterns, generational context, and — critically — the
specific LLM reproduction gap for each master.

Three masters, one generation: 糸井重里 (1948–), 岩崎俊一
(1947–2014), 眞木準 (1948–2009). All active during the 1980s
"copywriter boom" (コピーライターブーム). Together they define three
distinct poles of Japanese short-copy voice that remain the primary
reference points for キャッチコピー craft.

## Primary Sources

- **糸井重里**: ほぼ日刊イトイ新聞 (ほぼ日) author's own copy
  selection; 2024 コピー10 series (10 landmark copies discussed
  with 谷山雅計); TCC コピー年鑑. 13+ representative works confirmed.
- **岩崎俊一**: 『幸福を見つめるコピー』(東急エージェンシー, 2009;
  restored edition 2015). Wikipedia 岩崎俊一 article. TCC コピー年鑑.
  宣伝会議 memorial articles. 11+ representative works confirmed.
- **眞木準**: TCC コピー年鑑. 宣伝会議賞 眞木準賞 (~2010 established,
  48th edition, still active). Wikipedia article. 15+ representative
  works confirmed.
- **Cross-reference JP sources**: TCC official site, iso-labo.com,
  kai-story.com, AdverTimes, EDIMAG.

## Critical Attribution Corrections

- **Drift #8: リゲイン「24時間戦えますか？」is NOT 岩崎俊一.**
  This copy is frequently misattributed to 岩崎 in secondary
  sources. Re-confirmed during v4.14.0 grounding research — the
  attribution is incorrect. Do not list it among 岩崎's works.

## Generational Context

All three masters were born 1947–1948 and rose to prominence during
the 1980s Japanese advertising golden age. This era's key features:

- Mass media dominance (TV CM + print + 交通広告)
- Copywriter as cultural celebrity (コピーライターブーム)
- Copy judged by artistic merit, not click-through rate
- TCC (東京コピーライターズクラブ) annual as the industry's canon

The generational context matters because their voice styles emerged
from a media environment where **a single line needed to work across
millions of viewers with no targeting, no A/B testing, and no
retargeting**. This constraint produced copy that prioritized
universality, ambiguity, and cultural resonance over specificity
and conversion optimization.

## 糸井重里 (1948–)

### Career arc

Copywriter → ほぼ日 founder (1998 transition from client copywriting
to media ownership). TCC Hall of Fame **2012**.

### Representative works (13+ confirmed)

Ghibli series: 「生きろ。」(もののけ姫 1997), 「おちこんだりもした
けれど、私はげんきです。」(魔女の宅急便 1989), 「このへんないきもの
は、まだ日本にいるのです。たぶん。」(となりのトトロ 1988).
西武百貨店:「おいしい生活。」(1982),「不思議、大好き。」(1981).
Others: 「くうねるあそぶ。」(日産セフィーロ 1988), 「ほしいものが、
ほしいわ。」(西武百貨店 1988).

### Voice signature

| Dimension | Characteristic | Example |
|-----------|---------------|---------|
| Semantic openness | 意図的な曖昧さ — deliberately leaves interpretation to the reader | 「おいしい生活。」— "delicious life" means nothing specific and everything at once |
| Register | 日常語の詩化 — everyday words elevated to poetic register | 「くうねるあそぶ。」— three basic verbs, zero adjectives, infinite lifestyle projection |
| Function | おまじない性 — copy works as an incantation, not an argument | 「生きろ。」— two mora, imperative, no reasoning attached |
| Stance | 状態提案型 — proposes a state of being, not an action to take | 「ほしいものが、ほしいわ。」— names a desire-state without pointing to a product |

### Stylistic grammar patterns

- Sentence-final 。 on fragments (not full sentences)
- Hiragana preference over kanji for common words
- Omission of logical connectives — juxtaposition carries the meaning
- First-person perspective rare; third-person or impersonal default

### LLM reproduction gap

LLM output attempting 糸井 voice typically **over-explains metaphors**
and **closes interpretive openness**. The signature 意図的な曖昧さ
is the hardest dimension to reproduce — LLMs default to clarity and
completeness, which is antithetical to 糸井's method.

Specific failure modes:
- Adding a subordinate clause that explains why the metaphor matters
- Producing full sentences where 糸井 would use a fragment
- Using adjectives where 糸井 would use bare nouns or verbs
- Resolving ambiguity into a single reading

**Mitigation**: instruct the LLM to "delete the explanation" after
drafting — write the full thought, then strip it back to the
fragment. Review by checking if the copy has multiple valid
interpretations.

## 岩崎俊一 (1947–2014)

### Career arc

Copywriter active from 1970s through 2000s. Passed away 2014.
TCC Hall of Fame **2020** (posthumous).
『幸福を見つめるコピー』(2009, restored 2015) is the canonical
collection of his philosophy.

### Representative works (11+ confirmed)

ミツカン:「やがて、いのちに変わるもの。」(2004).
新潮文庫:「想像力と数百円。」(1984).
日産:「21世紀に間に合いました。」(プリメーラ).
Others: multiple TCC award-winning works across food, automotive,
publishing verticals.

### Voice signature

| Dimension | Characteristic | Example |
|-----------|---------------|---------|
| Temporal awareness | 人生の有限性 — consciousness of life's finiteness | 「やがて、いのちに変わるもの。」— food becomes life, and life is finite |
| Philosophical register | 仏教的無常観 — Buddhist impermanence undertone | The "やがて" (eventually) carries temporal weight beyond its literal meaning |
| Structural technique | 具体と抽象の架橋 — bridging concrete and abstract | 「想像力と数百円。」— imagination (abstract) + a few hundred yen (concrete) |
| Reframing | 行為の意味変換 — transforms the meaning of an everyday act | Eating → becoming life. Reading → imagination for pocket change. |
| Tone | 穏やかな断定 — gentle assertion, not argument | Declarative sentences that feel like observations, not persuasion |

### Core philosophy

「コピーは、作るものではなく、見つけるもの」— copy is not fabricated
but discovered. The copywriter's role is to find the truth that
already exists in the relationship between the product and the
human, not to invent clever wordplay.

### LLM reproduction gap

LLM output attempting 岩崎 voice typically **produces generic
inspirational copy** and **misses the specific binding moment**.
岩崎's signature is anchoring abstract philosophy to a concrete,
specific instant — "this food becoming this life" — not
"life is beautiful."

Specific failure modes:
- Producing motivational-poster copy (vague uplift without specificity)
- Missing the "bridge" — abstract without concrete, or concrete without abstract
- Using emotional vocabulary where 岩崎 would use observational vocabulary
- Creating urgency where 岩崎 would create stillness

**Mitigation**: after drafting, check — "does this copy name a
specific moment or object?" If it could apply to any product, it
has missed 岩崎's voice. The copy should be inseparable from its
product.

## 眞木準 (1948–2009)

### Career arc

Copywriter active from 1970s through 2000s. Passed away 2009.
TCC Hall of Fame **2013** (posthumous).
宣伝会議賞 眞木準賞 established ~2010 (48th edition), still active
— one of the few named awards in the industry.

### Representative works (15+ confirmed)

Extensive 掛詞 (double-meaning / wordplay) portfolio across fashion,
lifestyle, and consumer goods verticals. Known for the density and
elegance of phonetic and semantic wordplay in every piece.

### Voice signature

| Dimension | Characteristic | Example |
|-----------|---------------|---------|
| Core technique | 同音異義 — homophone exploitation | Words that sound identical but carry dual meanings, both relevant to the product |
| Structural method | 和製英語再分解 — decomposing Japanese-English loanwords | Breaking apart wasei-eigo to reveal hidden meanings in the component parts |
| Thematic universe | 恋 / 愛 / 服 三角 — love / affection / fashion triangle | Fashion copy that reads as love poetry and vice versa |
| Lineage | 和歌の掛詞伝統の現代継承 — modern inheritance of waka kakekotoba | The classical Japanese poetic technique of pivot-words, updated for advertising |

### Core philosophy

「ダジャレではなく、オシャレです」— "It's not a bad pun, it's
elegant wordplay." The line between ダジャレ (groan-inducing pun) and
オシャレ (elegant wit) is whether the wordplay **adds meaning relevant
to the product and the reader's emotion**, not just phonetic
coincidence.

### LLM reproduction gap

LLM output attempting 眞木 voice **produces bad puns (ダジャレ)
rather than elegant wordplay (オシャレ)**. The puns lack product
relevance — they exploit phonetic coincidence without carrying
meaning.

Specific failure modes:
- Phonetic puns with no semantic relevance to the product
- Wordplay that works in isolation but doesn't deepen the product's appeal
- Over-density of puns (眞木 used one per piece, not three)
- Missing the emotional undertone — 眞木's wordplay always carried
  feeling (love, longing, delight), not just cleverness

**Mitigation**: after generating wordplay candidates, apply a
two-gate test:
1. Remove the wordplay — does the copy still relate to the product?
   (If not, the pun is load-bearing but empty.)
2. Remove the product — does the wordplay still carry an emotion?
   (If not, the pun is product-relevant but emotionally dead.)
Only candidates passing both gates qualify as オシャレ.

## TCC Hall of Fame timeline

| Master | Birth | Death | Hall of Fame | Active peak |
|--------|-------|-------|-------------|-------------|
| 糸井重里 | 1948 | — | 2012 | 1980s–1990s |
| 岩崎俊一 | 1947 | 2014 | 2020 (posthumous) | 1980s–2000s |
| 眞木準 | 1948 | 2009 | 2013 (posthumous) | 1980s–2000s |

## Voice selection guidance

When `short-form-catchcopy-canon.md` or `write-short-form-copy.md`
references a voice master, use this standard to calibrate the voice:

| Voice reference | Best fit | Avoid when |
|-----------------|----------|------------|
| 糸井 | Lifestyle branding, state-proposal copy, cultural campaigns | Direct-response, conversion-optimized, feature-heavy products |
| 岩崎 | Food, life-stage products, philosophical branding | Fast-paced, urgency-driven, youth-targeted campaigns |
| 眞木 | Fashion, lifestyle accessories, campaigns where wordplay adds meaning | Technical products, B2B, contexts where wordplay reads as frivolous |

For copy audit (`copy-audit.md`): when diagnosing voice inconsistency,
check against these signatures. A piece claiming 糸井 voice but using
argumentative structure is misaligned. A piece claiming 眞木 voice but
containing only phonetic puns without emotional undertone is ダジャレ,
not オシャレ.

## Anti-Patterns

- **Attributing リゲイン「24時間戦えますか？」to 岩崎俊一**.
  This is a confirmed misattribution (drift #8).
- **Treating the three masters as interchangeable**. Each has a
  distinct voice signature, philosophical stance, and structural
  method. "Write in the style of a Japanese copywriting master"
  is not actionable — specify which master and why.
- **Reproducing 糸井 voice by adding "。" to the end of fragments**.
  The punctuation is a surface marker, not the voice. The voice is
  in the semantic openness and register elevation.
- **Claiming LLM can "write like 糸井/岩崎/眞木"**. LLM can
  approximate structural patterns but consistently fails on the
  specific dimensions documented in each master's LLM reproduction
  gap section. Use the mitigation strategies, not the claim.
- **Mixing two masters' voices in one piece**. Their voices are
  structurally incompatible — 糸井's ambiguity conflicts with
  眞木's precision; 岩崎's stillness conflicts with 眞木's
  playfulness. One voice per piece.
- **Using 眞木-style wordplay in non-Japanese copy**. The 掛詞
  tradition is Japanese-language-specific (homophone density,
  和製英語 decomposition). English copy can use puns, but the
  structural technique is different.
- **Ignoring the generational context**. These voices emerged from
  mass-media, no-targeting environments. Applying them uncritically
  to micro-targeted digital ads may produce beautiful copy that
  doesn't convert. Use them as voice reference, not as targeting
  strategy.
