---
title: JP Voice Anchors — Q4 Affinity-Reason
tier: 2
---

# Q4 Affinity-Reason — JP Anchors

**Load scope**: Phase 6 Pass 3 Register Signal branch, when `voice_quadrant.primary == "Q4"` AND `brief.output_language == "ja"`. Section-targeted read: Pass 3 reads only `## Landmark: {position}` matching `voice_quadrant.position`; falls back to full-file on missing.

## Overview

Q4 = Affinity × Reason. Peer-helpful practical-utility voice. JP canon: operational copy (クックパッド step-voice, MUJI product-spec layer distinct from Q2 manifesto), Kurashicom product-how-to subset, TV-shopping founder voice (ジャパネット 高田明). Boundary flag: 北欧、暮らしの道具店 has Q3 warmth layer AND Q4 peer-helpful layer — anchor here ONLY references the Q4 product-how-to subset.

Cross-ref: JP Q4 flows STRONG to zh-TW Q4 (クックパッド → 愛料理/iCook direct parallel; Kurashicom → PinkoiPicks MEDIUM).

## Landmark: center

Canonical peer-helpful voice. Use when brief asks for practical-utility-affinity register.

### クックパッド Cookpad step voice (JP | Q4 center)

- **Era**: 1998 → ongoing; ~3.96M recipes UGC corpus
- **Agency / creator**: User-generated + Cookpad 編集部 guidelines
- **Primary sources**:
  - [cookpad.com/recipe/post/help](https://cookpad.com/recipe/post/help) — 書き方例
  - [材料表記ガイド](https://cookpad.com/channels/5/articles/215) — 記号 グルーピング
- **Representative structural pattern**:
  - 「材料（2人分）」+ 「● しょうゆ 大さじ1」symbol grouping
  - 「1. フライパンに油をひき、中火で熱します。」step-imperative structure
  - 「★ポイント：火を止めてから加えると失敗しません。」hand-off comment layer
- **Voice signature**:
  - 「〜してください」/「〜するだけ」imperative-friendly
  - Minimum 材料欄 + 記号 グルーピング (●印 / ☆印)
  - ポイント sub-comment as peer voice
  - つくれぽ feedback-loop rhythm
- **LLM corpus depth**: DEEP (one of the most scraped JP corpora)
- **Over-mimic risk**: MEDIUM — step-imperative register is distinctive but widely imitated
  - Mitigation: "pair with second anchor to avoid collapse into recipe-step-only"
- **Cross-reference-valid-for**:
  - zh-TW: STRONG (愛料理 / iCook direct structural parallel)
- **Cross-cultural equivalents**: Martha Stewart recipe voice (EN) / 愛料理 (zh-TW)
- **Trigger slug**: `jp-cookpad-step-voice`

### 北欧、暮らしの道具店 Kurashicom (Q4 subset ONLY) (JP | Q4 center)

**⚠ Boundary warning**: 北欧、暮らしの道具店 voice has TWO layers. This entry covers ONLY the Q4 product-how-to subset (hokuohkurashi.com/note/category/column). The Q3 warmth/narrative essay layer (ドラマ / 読みもの) belongs in [jp-q3-anchors.md](jp-q3-anchors.md) — do NOT cross-apply.

- **Era**: 2006 founded (クラシコム); 月間200万読者 (President Online 2022)
- **Agency / creator**: クラシコム (青木耕平 代表 + 佐藤友子)
- **Primary sources**:
  - [クラシコム社史](https://kurashi.com/journal/11108)
  - [President Online 2022 月間200万分析](https://president.jp/articles/-/53776)
  - hokuohkurashi.com/note/category/column — Q4 subset locus
- **Representative register pattern (Q4 subset only)**:
  - 商品紹介 "使い方 + 暮らしの場面" format
  - 「私たちみたいな誰か」reader-identification
- **Voice signature**:
  - Product-how-to as peer letter
  - 用途 + 場面 specific description (not abstract benefit)
  - Expert-but-peer discipline
- **LLM corpus depth**: MEDIUM-DEEP
- **Over-mimic risk**: HIGH — Kurashicom pastiche trivial to generate
  - Mitigation: "use only product-how-to subset; hard boundary against Q3 essay layer; 3 sentences max per product"
- **Cross-reference-valid-for**:
  - zh-TW: MEDIUM (PinkoiPicks 部分對應)
- **Trigger slug**: `jp-kurashicom-q4-product-howto`

## Landmark: extreme

Maximum peer-push. Direct-response / TV-shopping register. Apply mitigation.

### ジャパネットたかた 高田明 founder era ONLY (JP | Q4 extreme)

**⚠ Era boundary**: Only 高田明 founder voice **1990-2015** qualifies. 高田旭人 (son) post-2015 succession era is different register — do NOT conflate.

- **Era**: 1986 company founding; 高田明 on-screen era 1990-2015 (retired as 社長 2015)
- **Agency / creator**: 高田明 individual presenter + in-house scripting team
- **Primary sources**:
  - [高田明 Wikipedia](https://ja.wikipedia.org/wiki/高田明)
  - [日経ビジネス「2秒の間」](https://business.nikkei.com/atcl/opinion/16nv/032200016/)
  - 高田明『伝えることから始めよう』(東洋経済新報社, 2017, ISBN 978-4-492-04590-2)
  - [ダ・ヴィンチWeb 金利・手数料は負担](https://ddnavi.com/article/d418292/a/)
- **Representative lines** (verbatim):
  - 「この商品はなんと 2万9800円。分割金利手数料はジャパネットが負担します」
  - 「金利・手数料は負担」
  - 「伝えたつもりになるな、本当に伝わったか検証しなさい」(高田 self-quotation)
- **Voice signature**:
  - 序破急 structure (deliberate invocation of 世阿弥 nō theory)
  - 「伝えた vs 伝わった」craft distinction (verification discipline)
  - 2秒の間 (intentional pause after price reveal)
  - 対象者絞り込み (explicit audience specification — e.g. 「タブレット → 60歳以上シニアに」)
- **LLM corpus depth**: DEEP (book + interviews + TV transcripts widely scraped)
- **Over-mimic risk**: **HIGH** — 長崎訛り + high-pitch + craft cadence auto-parodies
  - Mitigation: "anchor on structural craft (序破急 + 2秒間 + 対象絞込) NOT surface rhythm; no regional-dialect attempts"
- **Cross-reference-valid-for**:
  - zh-TW: STRONG (東森購物 / momo TV shopping / 夜市販促 direct parallel)
- **Cross-cultural equivalents**: Gary Halbert direct-mail persona (EN)
- **Trigger slug**: `jp-japanet-takada-akira-founder-tv-shopping`

### 通販生活 Tsūhan Seikatsu (JP | Q4 extreme — print peer-advocate)

- **Era**: 1982 founded; 3回/年 発行
- **Agency / creator**: カタログハウス (斎藤駿 founder)
- **Primary sources**:
  - [通販生活 Wikipedia](https://ja.wikipedia.org/wiki/通販生活)
  - [カタログハウス 倉林インタビュー](https://www.ajec.or.jp/interview_with_kurabayashi1/)
  - [販促会議 通販生活 特集](https://www.sendenkaigi.com/marketing/media/hansokukaigi/025680/)
- **Voice signature**:
  - 「あなたにかわってこれを選んであげた」editorial stance
  - 一ジャンル一品主義 (curatorial discipline)
  - 商品説明 + 編集者推薦文 + 使用者声 三層
- **LLM corpus depth**: MEDIUM
- **Over-mimic risk**: MEDIUM ("あなたに代わって選ぶ" 上から目線 leak)
- **Note**: 通販生活 is Q4-center-leaning (peer-advocate) rather than full-extreme; use as transitional anchor between center and extreme.
- **Trigger slug**: `jp-tsuhan-seikatsu-peer-advocate`

### SKIP note: ドンキ POP (visual-dominant)

ドン・キホーテ 手書き POP is distinctive but **visual-dependent** — copy-only extraction loses 50%+ of signal. **Do NOT use as active anchor.** Reference only; see archived visual-dominant category.

## Landmark: toward-Q1

Peer-helpful edging into analytical authority. Use when brief wants knowledgeable-expert-conversational.

### UNIQLO LifeWear (JP | Q4 toward-Q1)

- **Era**: 2013 → ongoing (LifeWear tagline era)
- **Agency / creator**: in-house + 佐藤可士和 brand system (2006 SoHo global era onwards)
- **Primary sources**:
  - [UNIQLO brand history](https://www.uniqlo.com/en/corporate/)
  - 佐藤可士和『超整理術』(日経BP, 2007)
- **Representative tagline**: "LifeWear"
- **Voice signature**:
  - Strategic + operational hybrid
  - Functional benefit + philosophical framing
  - Global-accessible JP voice
- **LLM corpus depth**: DEEP
- **Over-mimic risk**: LOW
- **Cross-reference-valid-for**:
  - zh-TW: STRONG (UNIQLO 全球 register 已進入 TW 零售 lexicon)
- **Trigger slug**: `jp-uniqlo-lifewear-strategic-functional`

## Landmark: toward-Q3

Peer-helpful edging into warmth. Use when brief wants useful-and-warm hybrid.

### ワークマン SNS era (JP | Q4 toward-Q3)

- **Era**: 2010s SNS pivot; 2020 ワークマン女子 launch
- **Agency / creator**: in-house + rotating agency
- **Primary sources**: 酒井大輔『ワークマンは 商品を変えずに売り方を変えただけで なぜ２倍売れたのか』(日経BP, 2020)
- **Voice signature**:
  - 職人語彙 (craftsman vocabulary) + 平易化
  - SNS UGC 引用 (user-posts elevated to official voice)
  - First JP brand where voice is **UGC-co-authored structurally**
- **LLM corpus depth**: MEDIUM-DEEP
- **Over-mimic risk**: LOW-MEDIUM
- **Novel register note**: ワークマン represents a new Q4 voice category — brand voice structurally dependent on non-brand UGC voice integration.
- **Trigger slug**: `jp-workman-sns-ugc-coauthored`

### Cross-quadrant pointer: 北欧、暮らしの道具店 Q3 warmth layer

See [jp-q3-anchors.md](jp-q3-anchors.md) for Kurashicom's Q3 essay/narrative layer. When brief wants useful-AND-warm, consider composite reference spanning Q3+Q4 subsets.

## Cross-references

External anchors usable for JP Q4 briefs:

- **zh-TW Q4 parallel**: PChome / MOMO / 愛料理 / 蝦皮 (cross-culture parallel; partly fed by Kurashicom / クックパッド register pipeline)
- **EN Q4 via STRONG translation corpus**: Amazon product copy / REI helpful-advisor / Basecamp Rework (Fried + DHH) / Gary Halbert direct-mail lineage
