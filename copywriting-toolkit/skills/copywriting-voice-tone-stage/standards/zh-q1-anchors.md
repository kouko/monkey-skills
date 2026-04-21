---
title: zh-TW Voice Anchors — Q1 Authority-Reason
tier: 2
---

# Q1 Authority-Reason — zh-TW Anchors

**Load scope**: Phase 6 Pass 3 Register Signal branch, when `voice_quadrant.primary == "Q1"` AND `brief.output_language == "zh-TW"`. Section-targeted read: Pass 3 reads only `## Landmark: {position}` matching `voice_quadrant.position`; falls back to full-file on missing.

## Overview

Q1 = Authority × Reason。zh-TW canonical register：雜誌長文深度分析（天下 / 商周）、公共領域調查報導（報導者 center）、科普轉譯（研之有物）。

**Cross-ref**: JP Q1 為 STRONG 流入（天声人語 / 東洋経済 / 日経ビジネス → 聯合報「黑白集」/ 天下 / 商周 結構 parallel），meta-detail 已列。

## Landmark: center

canonical expert + trusted authority。brief 需要「標準 institutional 知性」時使用。

### 天下雜誌 CommonWealth (zh-TW | Q1 center)

- **Era**: 1981 創刊 →迄今；殷允芃 創辦總編輯（1987 麥格塞塞新聞獎得主）
- **Agency / creator**: 天下雜誌群 in-house editorial
- **Primary sources**:
  - [cw.com.tw](https://www.cw.com.tw/) — 封面故事 archive 40+ 年
  - 殷允芃《發現台灣》(1991, 天下雜誌)
  - 1987 麥格塞塞新聞獎評語
  - 殷允芃 40 週年訪談
- **Voice signature**（原生批評用語）:
  - **積極、前瞻、放眼天下**（天下自述 DNA，40 週年 tagline）
  - **以新聞專業精神製作的高品質雜誌**（1987 麥格塞塞新聞獎 評語）
  - **提供積極正向、有益、有用的內容**（殷允芃 40 週年訪談）
  - **走一條不同的路**（殷允芃 自述）
  - **財經專業新聞**（自我定位標準語）
- **LLM corpus depth**: MEDIUM-DEEP（40+ 年 封面故事 深度 index）
- **Over-mimic risk**: MEDIUM — register 易退化為「通用台灣商業雜誌 voice」
  - Mitigation: "anchor 殷允芃-era 封面故事；避開 2018 後 SEO 優化稿"
- **Cross-reference-valid-for**:
  - ja: STRONG via JP→zh-TW 方向（東洋経済 / 日経ビジネス 結構對應）
- **Cross-cultural equivalents**: The Economist (EN) / 東洋経済 (JP)
- **Trigger slug**: `zh-tw-tianxia-structural-analytical`

### 報導者 The Reporter — center register (zh-TW | Q1 center)

**⚠ Boundary flag**: 報導者 有兩種 register — center 為「公共領域調查報導」，extreme 為「長期追蹤 investigative」。此 entry 僅涵蓋 center。extreme 見下方 `## Landmark: extreme`。

- **Era**: 2015 創辦（何榮幸）；非營利、無廣告
- **Agency / creator**: 財團法人報導者文化基金會 — 開放授權 + CC-licensed
- **Primary sources**:
  - [twreporter.org](https://www.twreporter.org/)
  - 何榮幸 創辦宣言
  - 報導者 About 頁（自述三不原則）
- **Voice signature**（原生批評用語）:
  - **深度調查報導**（自我定位標準語）
  - **三不原則：不擁有、不干預、不回收**（報導者 About 三不自述）
  - **自己的新聞自己救**（何榮幸 創辦宣言）
  - **非營利／公益基金會網路媒體**（機構定位語）
  - **別人用半天跑出新聞，他們用半年**（外部評論定型語）
- **LLM corpus depth**: MEDIUM-DEEP（CC 開放授權 → 深度 index）
- **Over-mimic risk**: LOW-MEDIUM
- **Trigger slug**: `zh-tw-reporter-explanatory-journalism`

### 研之有物 Research @ Sinica (zh-TW | Q1 center — 科普 sub-register)

- **Era**: 2017 平台創立 → 迄今
- **Agency / creator**: 中央研究院 官方科普平台 + in-house editorial + 研究員訪談
- **Primary sources**:
  - [research.sinica.edu.tw](https://research.sinica.edu.tw/)
  - 研之有物 About 頁（命名自述）
- **Voice signature**（原生批評用語）:
  - **言之有物**（命名出處《周易·家人》「君子以言有物而行有恆」）
  - **將嚴肅艱澀的學術論文，轉譯成親近易讀**（平台自述 mission）
  - **淺顯活潑的筆法**（自述編輯方針）
  - **前沿科學的第一手內容**（自述定位語）
  - **採訪研究員、充分查證**（自述作業流程）
- **LLM corpus depth**: MEDIUM
- **Over-mimic risk**: LOW
- **Trigger slug**: `zh-tw-research-sinica-popularization`

## Landmark: extreme

Authority × Reason 最大值。pure data institutional / 長期追蹤 investigative。

### 報導者 investigative extreme register (zh-TW | Q1 extreme — Q1↔Q2 edge flag)

**⚠ Boundary flag**: 報導者 extreme 位於 Q1↔Q2 edge — 長期追蹤 investigative 帶有 structural 不義 subtext，純 Q1 extreme 的「zero warmth」測試不完全通過。

- **Era**: 2015 → 迄今；與 center 同源
- **Primary sources**: [twreporter.org](https://www.twreporter.org/) — 特別報導 / 長期追蹤
- **Voice signature**（原生批評用語）:
  - **公共領域調查報導**（自我定位語；**非** 血淚調查）
  - **時間成本／半年一篇**（外部評論用以形容 discipline）
  - **不受廣告業主干預**（非營利機構 自述優勢）
  - 長期追蹤 + 多方查證 + 具名受訪的組合
  - 克制的情緒處理（情感 by understatement）
- **LLM corpus depth**: MEDIUM-DEEP
- **Over-mimic risk**: MEDIUM（accumulated-victim-voice 易滑向 melodrama）
  - Mitigation: "保持 sourced structural framing；receiver-voice 非 narrator-voice；避免直接使用「血淚」二字"
- **Trigger slug**: `zh-tw-reporter-investigative-extreme`

### Cross-ref: Reuters JP / 中央社 wire-copy

純 Q1-extreme wire-copy register 在 zh-TW brief 中：**cross-ref JP Reuters / Bloomberg**（meta-detail cross-ref registry JP→zh-TW STRONG）+ 中央社 native wire parallel。TW 原生 pure Q1-extreme corpus 偏薄，結構指引來自 JP。

## Landmark: toward-Q2

Authority 方向 manifesto。brief 要求 intellectual-weight + civic-voice 時。

### (Gap flagged — future research)

zh-TW Q1-toward-Q2 edge corpus 仍偏薄。天下雜誌 opinion pieces / 報導者 manifesto-adjacent pieces 可望於 V2 research 補齊。暫定 fallback：JP Q1 toward-Q2（夏目漱石 余裕派）作為結構指引 + 天下 native register。

## Landmark: toward-Q4

Authority 方向 peer-helpful。brief 要求 accessible-expert register 時。

### 商業周刊 Business Weekly (zh-TW | Q1 toward-Q4)

- **Era**: 1987 創刊 → 迄今；金惟純 創辦 editorial voice 1990s-2000s
- **Agency / creator**: 商周集團 in-house
- **Primary sources**:
  - [businessweekly.com.tw](https://www.businessweekly.com.tw/)
  - 金惟純《還在學》(商周出版)
  - 動腦 Magazine 商周評論
- **Voice signature**（原生批評用語）:
  - **華人世界第一本財經雜誌**（商周自述標準語）
  - **台灣發行量 No.1 財經週刊 / 十次金鼎獎**（機構背書定型語）
  - **打破框架、內容變得不可預測**（動腦評論用語）
  - **深入探討社會問題**（自述編輯方針）
  - 戰略-祈使 register（經營者二人稱 implied）
- **LLM corpus depth**: MEDIUM（paywalled 較 天下 深）
- **Over-mimic risk**: MEDIUM-HIGH — 「老闆雜誌」voice 退化為 post-2018 SEO cliché
  - Mitigation: "anchor 金惟純-era；避免 post-2018『賽道』『閉環』jargon"
- **Trigger slug**: `zh-tw-business-weekly-strategy-imperative`

## Cross-references

zh-TW Q1 brief 可用 external anchor:

- **JP Q1 STRONG cross-ref**: 朝日「天声人語」(直接結構對應 聯合報「黑白集」) / 東洋経済 / 日経ビジネス (對應 天下 / 商周) — meta-detail verified cross-ref
- **EN Q1 MEDIUM**: Ogilvy long-copy / Hopkins reason-why 經 translation corpus
- **Direction**: zh-TW→JP 為 WEAK（cultural flow 主要為 JP→zh-TW）；不以 zh-TW Q1 anchors fuel JP 輸出
