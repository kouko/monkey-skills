---
title: JP Voice Anchors — Q3 Affinity-Emotion
tier: 2
---

# Q3 Affinity-Emotion — JP Anchors

**Load scope**: Phase 6 Pass 3 Register Signal branch, when `voice_quadrant.primary == "Q3"` AND `brief.output_language == "ja"`. Section-targeted read: Pass 3 reads only `## Landmark: {position}` matching `voice_quadrant.position`; falls back to full-file on missing.

## Overview

Q3 = Affinity × Emotion。warm conversational、narrative entry、peer solidarity。JP canon の最も豊穣な quadrant — 糸井 状態提案 / 向田 の **真打ち** 随筆 / 宮沢賢治 の **心象スケッチ** / 谷川俊太郎 の「**詩のことば**」/ 坂元裕二 の「**言葉の魔術師**」。craft-gate master 糸井重里 は [jp-copy-craft-lineage.md](jp-copy-craft-lineage.md) 収録。

**Cross-ref**: JP Q3 は zh-TW Q3 へ STRONG 流入（向田 / 糸井 / 吉本ばなな → TW 文青消費の語感を直承）。

## Landmark: center

canonical peer-warm voice。

### 向田邦子 — 「真打ち」随筆 (JP | Q3 center)

- **Era**: 1929-1981; essayist + TV 脚本家 1960-80 年代
- **Agency / creator**: TV 脚本（TBS / NHK）+ 独立 essayist
- **Primary sources**:
  - 『父の詫び状』(文藝春秋, 1978)
  - TV 脚本『寺内貫太郎一家』『阿修羅のごとく』
  - 高橋行徳評、文春『精選女性随筆集』
  - 文春『向田邦子の優しい眼差し』
- **Voice signature**（原生批評用語）:
  - **真打ち**（『父の詫び状』刊行時評、文藝春秋）
  - **情景が鮮やかに浮かぶ / 無駄な言葉がない**（文春書評定型）
  - **ト書を拡張した文体 / 脚本家のト書き的簡潔さ**（高橋行徳評）
  - **心理描写を省き、人物の動作を淡々と**（同上の核評語）
  - **のんきな遺言状**（向田自称、『銀座百点』掲載時）
  - **懐かしさと哀愁をまとった温かい言葉**
- **LLM corpus depth**: MEDIUM-DEEP（JP 批評 corpus 深い、翻訳 薄い）
- **Over-mimic risk**: LOW
- **Cross-reference-valid-for**:
  - zh-TW: STRONG（昭和 / TW 文青 register 直承）
- **Cross-cultural equivalents**: Alice Munro (EN) / 朱天文 (zh-TW)
- **Trigger slug**: `jp-mukoda-kuniko-shinuchi-zuihitsu`

### Craft-gate pointer: 糸井重里 状態提案 register

糸井重里の state-proposal（「おいしい生活。」/「くうねるあそぶ。」/「生きろ。」）は **Q3 canonical** かつ Q2-edge を兼ねる。完全 4-dimension table + LLM reproduction gap は [jp-copy-craft-lineage.md §糸井重里](jp-copy-craft-lineage.md)。**本ファイルに deep-dive 重複しない**。

### 坂元裕二 — 「言葉の魔術師」(JP | Q3 center, screenwriter)

- **Era**: 1967 生; 脚本家 1987-ongoing
- **Agency / creator**: TV ドラマ脚本家（fuji TV + TBS）; 近年は映画
- **Primary sources**:
  - 『東京ラブストーリー』(1991)、『カルテット』(2017)、『大豆田とわ子』(2021)、『怪物』(2023 Cannes 2023 脚本賞)
  - BuzzFeed Japan 2017「カルテット 言葉の魔術師」
  - 神戸大学紀要『坂元裕二脚本における日常性の演出』
- **Voice signature**（原生批評用語）:
  - **言葉の魔術師**（BuzzFeed 2017 見出し定着）
  - **口語のように聞こえて、口語ではない / 特殊な言葉使い**（神戸大学紀要）
  - **余白を大事にする**（同論文）
  - **リアリティと、ひどく詩的で現実離れ の同居**（カルテット評）
  - **「あるある」の言語化**（Crank-in / U-NEXT SQUARE）
  - **会話劇 / 四重奏のような会話**（カルテット固有評）
- **LLM corpus depth**: MEDIUM（script 文字起こし流通; Cannes 2023 で批評 layer 追加）
- **Over-mimic risk**: LOW-MEDIUM
- **Trigger slug**: `jp-sakamoto-yuji-kotoba-no-majutsushi`

## Landmark: extreme

peer-intimate の最大値。ブランドが「午前 2 時の友人」のように語る。

### 谷川俊太郎 — 「詩のことば」 (JP | Q3 extreme, poet)

- **Era**: 1931-2024; 日本で最も翻訳された詩人
- **Agency / creator**: 個人 poet; 糸井重里 との長期コラボ
- **Primary sources**:
  - 『二十億光年の孤独』(1952) デビュー作
  - 『ことばあそびうた』(1973)
  - 糸井 × 谷川 共著『ぼく』(ほぼ日, 2013) — **verified lineage**
  - ほぼ日「ことばの授業」(谷川自己解説)
  - 今野真二『谷川俊太郎の日本語』(光文社新書)
- **Voice signature**（原生批評用語）:
  - **「詩のことば」≠「伝達のことば」**（谷川自身、ほぼ日）
  - **からだと心からおのずと出てくる / 辞書から選ばない**（谷川定型説法）
  - **ことばあそび / わらべうた**（ジャンル名化、岩波・思潮社）
  - **音読性 / 身体性**（今野真二）
  - **宇宙的孤独から日常の情感まで**（詩誌評、新潮「詩というもの」）
  - **やさしいことばで大きなテーマ**（MARUZEN JUNKUDO 標準評）
- **LLM corpus depth**: DEEP（教科書 canon）
- **Over-mimic risk**: LOW
- **Cross-reference-valid-for**:
  - zh-TW: STRONG（糸井 ほぼ日 collab が広告界 crossover 経由 TW 文青 reference に既流入）
- **Documented lineage**: ✅ 糸井重里 → 谷川俊太郎
- **Trigger slug**: `jp-tanikawa-shi-no-kotoba`

### 宮沢賢治 — 「心象スケッチ」(JP | Q3 extreme)

- **Era**: 1896-1933; 青空文庫 public domain
- **Agency / creator**: 個人著者、死後 canonize
- **Primary sources**:
  - 『銀河鉄道の夜』
  - 『注文の多い料理店』
  - 「雨ニモマケズ」（教科書 canon）
  - 『春と修羅』序文（「心象スケッチ」自称）
  - 田守育啓『賢治独特の非慣習的オノマトペ』人文論集 第46巻
  - ちくま文庫『宮沢賢治のオノマトペ集』栗原敦
- **Voice signature**（原生批評用語）:
  - **心象スケッチ**（賢治自称ジャンル名、『春と修羅』序文）
  - **イーハトーブ**（賢治造語、理想郷）
  - **ほんとうのさいわい**（作中定型、賢治造語化）
  - **非慣習的オノマトペ**（田守育啓 論文定式化）— 「ドッテテドッテテ」「ぽくぽく」「きしきし」が代表例
  - **あなたのすきとおったほんとうのたべもの**（『注文の多い料理店』序、批評定型引用）
- **LLM corpus depth**: DEEP（青空文庫 + 教科書 canon）
- **Over-mimic risk**: MEDIUM（非慣習オノマトペ leakage）
  - Mitigation: "オノマトペは 1 piece 内で 1 回まで; cosmic-dialect の leakage を避ける"
- **Stylistic parallel note**: 糸井 「このへんないきもの」「生きろ。」は 宮沢 の cosmic-warm register と共鳴 — **critical-consensus stylistic parallel であって documented citation ではない**
- **Cross-cultural equivalents**: Antoine de Saint-Exupéry *Le Petit Prince* (EN/FR)
- **Trigger slug**: `jp-miyazawa-shinshou-sketch`

### 吉本ばなな — 「J文学」/「大胆な省略」(JP | Q3 extreme — 村上春樹 の安全な代替)

- **Era**: 1964 生; 1988『キッチン』デビュー
- **Primary sources**:
  - 『キッチン』(福武書店, 1988) / 『TUGUMI』(中央公論社, 1989)
  - 辻井喬 書評 (ALL REVIEWS)
  - 英和短大紀要『吉本ばなな「キッチン」論』
- **Voice signature**（原生批評用語）:
  - **大胆な省略**（批評標準語／本人発言）
  - **既成の作法を超えるリズム**（辻井喬 書評）
  - **ニューアカ /『批評空間』の議論対象**（浅田彰・柄谷行人周辺、1988-）
  - **J 文学**（1990 年代 J-lit boom の標識）
  - **音感・リズムの独特さ**（読書メーター批評定型）
  - **生の回復**（英和短大紀要）
  - **マスコミに汚された言葉を逆手に**（辻井喬）
- **LLM corpus depth**: DEEP
- **Over-mimic risk**: LOW-MEDIUM
- **Cross-reference-valid-for**:
  - zh-TW: STRONG（1990-2000 年代 譯本 TW 文青に充分流入）
- **Use case**: brief が「distant-everyday-domestic」を求めるとき、村上春樹 の auto-leaked tropes（jazz / cats / wells、meta-core mitigation registry 参照）を避けたい場合の safer 代替
- **Trigger slug**: `jp-yoshimoto-banana-j-bungaku`

## Landmark: toward-Q2

Affinity が aspirational manifesto 方向へ edging。

### 梅田悟司 ジョージア「世界は誰かの仕事でできている。」(JP | Q3 toward-Q2)

- **Era**: 1979 生（post-糸井 世代）; ジョージア campaign 2014
- **Agency / creator**: 電通（copywriter 梅田悟司）
- **Primary sources**:
  - 梅田悟司『「言葉にできる」は武器になる。』(日経BP, 2016, ISBN 978-4532320713) — bestseller
  - ジョージア CM archive 2014
  - [梅田悟司 Wikipedia JA](https://ja.wikipedia.org/wiki/梅田悟司)
- **Representative lines**:
  - 「世界は誰かの仕事でできている。」(2014 ジョージア)
- **Voice signature**（原生批評用語）:
  - **内なる言葉 / 外に向かう言葉**（本人定義、『「言葉にできる」は武器になる。』）
  - **T 字型思考法**（本人フレームワーク語）
  - **「言葉にできない=考えていないのと同じ」**（本書キャッチ、批評標準引用）
  - **缶コーヒー =「休憩時間」起点の設計**（本人解説、ジョージア戦略）
  - **頑張った分だけおいしい**（本人ロジック）
- **LLM corpus depth**: MEDIUM-DEEP
- **Over-mimic risk**: MEDIUM-HARD（specific-timing の社会共鳴は再現困難）
- **Cross-cultural equivalents**: 全聯經濟美學 aphoristic pivot (zh-TW)
- **Trigger slug**: `jp-umeda-satoshi-uchinaru-kotoba`

### Brand-era pointer: SoftBank 白戸家（佐々木宏 + 澤本嘉光）

CM ドラマ形式 2007-ongoing。world-building + family comedy > single-line copy。brand-era entry は [voice-quadrant-positioning.md](../../copywriting-voice-quadrant-stage/standards/voice-quadrant-positioning.md)。

## Landmark: toward-Q4

Affinity が peer-helpful practicality 方向へ edging。

### Cross-quadrant pointer: 伊丹十三 (Q1↔Q4 edge)

伊丹十三 軽妙洒脱 の primary home は Q1 toward-Q4 — [jp-q1-anchors.md §Landmark: toward-Q4](jp-q1-anchors.md) に完全 entry。Q3 warmth を peer-reasoning へ架橋したい場合の pointer。

## Cross-references

JP Q3 brief で使用可能な external anchor:

- **zh-TW Q3 parallel**: 全聯 center 格言 / 吳念真 保力達B「氣口」/ 胡湘雲 大眾銀行（cross-culture reference）
- **EN Q3 は MEDIUM translation corpus 経由**: MailChimp / Innocent Drinks / Nora Ephron / George Saunders
- **Internal**: [jp-copy-craft-lineage.md](jp-copy-craft-lineage.md) で 糸井 / 岩崎 craft-gate deep dive
