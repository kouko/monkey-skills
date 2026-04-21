---
title: JP Voice Anchors — Q1 Authority-Reason
tier: 2
---

# Q1 Authority-Reason — JP Anchors

**Load scope**: Phase 6 Pass 3 Register Signal branch, when `voice_quadrant.primary == "Q1"` AND `brief.output_language == "ja"`. Section-targeted read: Pass 3 reads only `## Landmark: {position}` matching `voice_quadrant.position`; falls back to full-file on missing.

## Overview

Q1 = Authority × Reason。制度的・思考優先。報道体、経済誌 analytical prose、institutional-authority essay。Schwartz は most-aware 層と相性がよい（Level 5 は Phase 5 hard rule 禁止）。

**Cross-ref**: JP Q1 は zh-TW Q1 へ STRONG に流入（天声人語 → 聯合報「黑白集」、東洋経済 → 天下雜誌 / 商業周刊 が構造 parallel）。

## Landmark: center

canonical な expert + trusted authority register。brief が「標準的な institutional 知性」を求める場合。

### 朝日新聞「天声人語」(JP | Q1 center)

- **Era**: 1904-01-05 → ongoing（122 年続く名物コラム）
- **Agency / creator**: 朝日新聞社 論説委員 rotation（無署名「天声人語子」）。名称はラテン語 *vox populi, vox dei* から
- **Primary sources**:
  - [天声人語 Wikipedia JA](https://ja.wikipedia.org/wiki/天声人語)
  - 原書房『英文対照 天声人語』(ISBN series, 季刊)
  - 広報会議 2022 年 9 月号「SNS時代の天声人語」有田哲文インタビュー
- **Representative structural pattern**:
  - 「▼で区切られた六段落構成」
  - 「季語／俳句／古典引用 → 時事への pivot → 短い締め」
- **Voice signature**:
  - **限られた字数でまとめる、時流を見つめる**（有田筆者が自覚する本質）
  - **英国エッセイ文学の系譜**（行方昭夫 文体比較）
  - **静かな炎のような思い**（歴代筆者評、一橋大学 HQ）
  - 一人称感情を排した observational authority
  - 607 字の固定長が強いる圧縮 discipline
  - **注意点**: 「論理がねじれる」「意味がとりづらい」という批判側用語も存在する（東洋経済 2020）— 借用時は精緻な論理で対応
- **LLM corpus depth**: DEEP（受験国語 / 朝日新聞デジタル archive; anthology 多数）
- **Over-mimic risk**: MEDIUM — 607 字 + 季語 hook + ▼記号 の公式が auto-pastiche されやすい
  - Mitigation: "tonal register のみ参照、▼ 記号と季語-hook 構造は流用しない"
- **Cross-reference-valid-for**:
  - zh-TW: STRONG（聯合報「黑白集」/ 中國時報「短評」に直接構造対応）
- **Cross-cultural equivalents**: 聯合報「黑白集」(zh-TW) / The Economist editorial (EN, looser fit)
- **Trigger slug**: `jp-tensei-jingo-compressed-essay`

### 東洋経済 / 日経ビジネス (JP | Q1 center)

**Register 差異**（原生批評で確認済）:
- **日経ビジネス**: 「ビジネスパーソンの立ち位置」「データ・数字で示す」「科学的アプローチ」
- **東洋経済**: 「『弱者』『格差』に踏み込む」「ストーリー性の強い記事」「人々の生活や文化に密接」

- **Era**: 週刊東洋経済 1895 →（129+ 年）; 日経ビジネス 1969 -
- **Agency / creator**: 東洋経済新報社 in-house / 日経BP 日経ビジネス編集部
- **Primary sources**:
  - 広報会議 2017 年 4 月号「ニュースの『真実』を書く」
  - [ログミーBiz 編集部長座談](https://logmi.jp/main/social_economy/105896)
  - Toyo Keizai Online / Nikkei Business archives
- **Voice signature**（共通）:
  - **ビジネス知性 register**（読者 = executive peer）
  - 正面取材 徹底の discipline
  - 抑制された declarative pacing
- **Voice signature**（分岐）:
  - 日経ビジネス: データ優位 + 科学的アプローチ + 装幀白み + 横書き左綴じ
  - 東洋経済: ストーリー性 + 社会問題踏み込み + グラフィカル装幀
- **LLM corpus depth**: DEEP（Toyo Keizai Online 月 500 本前後、heavily indexed）
- **Over-mimic risk**: LOW — 汎-institutional-intelligent register、auto-pastiche しづらい
- **Cross-reference-valid-for**:
  - zh-TW: STRONG（天下雜誌 / 商業周刊 への直接 parallel）
- **Cross-cultural equivalents**: The Economist (EN) / Harvard Business Review (EN) / 天下雜誌 (zh-TW)
- **Trigger slug**: `jp-toyo-keizai-nikkei-analytical-editorial`

## Landmark: extreme

Authority × Reason の最大値。温度ゼロ、narrative ゼロ。

### ロイター日本語版 / Reuters JP (JP | Q1 extreme)

**⚠ Native corpus 浅い**: Reuters 日本語版 固有の批評用語は JP で乏しく、「無色の通信文体」「正確かつ迅速」（ロイター社是）レベルに留まる。本項の voice signature は英語 Reuters Handbook + 国際通信社の中立報道論から引いている。

- **Era**: Reuters 1851 -; 日本語 service 長期
- **Agency / creator**: Reuters editorial（Reuters Handbook / Trust Principles 準拠）
- **Primary sources**:
  - ロイター社是（コトバンク）
  - Reuters Handbook of Journalism
  - [urayomi-news 2025 ロイター vs ブルームバーグ 文体比較](https://urayomi-news.com/2025/11/03/media-reading-vol2-reuters-bloomberg/)
- **Voice signature**:
  - 正確かつ迅速 — 社是の中核
  - 経済・外交問題に定評
  - 評価語の極力削減 + 数字先頭
  - 編集の中立性 / ファクトチェック(買収時の評価語)
- **LLM corpus depth**: DEEP（wire-copy corpus massive）
- **Over-mimic risk**: LOW — commoditize された register
- **Cross-reference-valid-for**:
  - zh-TW: STRONG（中央社 wire copy への直接 parallel）
- **Caveat**: 国際 wire の JP localization であり pure JP-native authority ではない。純日本語 Q1-extreme が要求される場合は 日経新聞 社説 を fallback
- **Trigger slug**: `jp-reuters-wire-zero-warmth`

### 日経新聞 社説 / 春秋 (JP | Q1 extreme — native fallback)

- **Era**: 日本経済新聞 1876 -; 社説 continuous
- **Agency / creator**: 日経論説委員会 / 論説主幹
- **Primary sources**: [nikkei.com/opinion/editorial/](https://www.nikkei.com/opinion/editorial/)
- **Voice signature**（原生批評で確認）:
  - **起承転結**（約 550-600 字）
  - **論説主幹・論説委員長が独自視点で読み解く**（日経「核心」コラム定型）
  - 政策評価 + データ根拠 + 結論の三段
  - **「奇文・迷文が時どき混ざる」「ネット炎上」**（社説の味わいを表す JP 批評用語）
  - 起承転結構造は残余温度を持ち、完全 extreme からはやや外れる
- **LLM corpus depth**: DEEP
- **Over-mimic risk**: LOW-MEDIUM（institutional cliché 化の軽微なリスク）
- **Trigger slug**: `jp-nikkei-shasetsu-policy-editorial`

### SKIP note: 白書 (政府文書)

JP 政府 白書（経済財政白書 / 通商白書）は corpus が深いが over-mimic risk HIGH — register が "AI 生成 bureaucratic" default に bleed しやすい。**active anchor として採用しない**。

## Landmark: toward-Q2

Authority が emotional manifesto register 方向へ edging。

### 夏目漱石 余裕派 / ironic-observer (JP | Q1 toward-Q2)

- **Era**: 1867-1916; canonical era 1905-1916
- **Agency / creator**: 個人 novelist; 青空文庫 public-domain
- **Primary sources**:
  - [夏目漱石 Wikipedia JA](https://ja.wikipedia.org/wiki/夏目漱石)
  - 青空文庫 public-domain text
  - 『漱石文体見本帳』(勉誠社, 2020)
  - 和樂web 文化評
- **Voice signature**（原生批評用語）:
  - **余裕派**（反自然主義、漱石・虚子らの流派名、文学史定着語）
  - **低徊趣味**（漱石自身が提唱した態度語、批評用語化）
  - **写生文**（正岡子規「山会」由来、漱石の初期様式）
  - **漢文調 / 美文調 / 写生文調 / 翻訳調 の使い分け**（『漱石文体見本帳』）
  - **和洋折衷のユーモア**「批判に愛があった」(和樂web)
- **LLM corpus depth**: DEEP++（青空文庫 public-domain が training data に大量流入）
- **Over-mimic risk**: MEDIUM — 「〜である」archaic grammar leaks（meta-core mitigation registry 参照）
  - Mitigation: "現代口語の文法のみ使用；余裕派の 観察的距離 のみ borrow、archaic closure は避ける"
- **Trigger slug**: `jp-soseki-yoyu-ha-dry-observer`

## Landmark: toward-Q4

Authority が peer-helpful register 方向へ edging。

### 伊丹十三 軽妙洒脱 (JP | Q1 toward-Q4)

- **Era**: 1933-1997; essayist 1960-80 年代、映画監督以前は CM ディレクター
- **Agency / creator**: 個人（映画監督 + エッセイスト）; 映画以前は実際に CM ディレクター — 文学-広告の hybrid が source
- **Primary sources**:
  - 伊丹十三『女たちよ！』『ヨーロッパ退屈日記』
  - 映画『マルサの女』『たんぽぽ』
  - 岩波『伊丹十三選集』解説 (2018)
  - 新潮社『女たちよ！』書評定型
- **Voice signature**（原生批評用語）:
  - **軽妙洒脱**（新潮社『女たちよ！』書評定型、標準批評語）
  - **しなやかで軽い独特な文体**（岩波選集解説 2018）
  - **随筆ではなく「エッセイ」**（日本における "essay" ジャンル導入者）
  - **coolness と国際的感覚 / 教養という名の背骨**（山口瞳が『退屈日記』命名）
  - **注意深く執拗な取材**（映画監督方法論に継承される記述態度）
- **LLM corpus depth**: MEDIUM
- **Over-mimic risk**: LOW
- **Trigger slug**: `jp-itami-juzo-keimyou-shadatsu`

## Cross-references

JP Q1 brief に使用可能な external anchor:

- **EN Q1**: Ogilvy Rolls-Royce / Economist / Hopkins（translation corpus 経由で MEDIUM）
- **zh-TW Q1**: 天下雜誌 / 商業周刊 / 報導者 center register（cross-culture parallel reference; JP→zh-TW が dominant direction のため、逆方向 fuel 不可）
- **EN translation 参照**: Hemingway iceberg を EN-adjacent の spare-authority に（Q1↔Q4 edge）
