---
title: zh-TW Voice Anchors — Q4 Affinity-Reason
tier: 2
---

# Q4 Affinity-Reason — zh-TW Anchors

**Load scope**: Phase 6 Pass 3 Register Signal branch, when `voice_quadrant.primary == "Q4"` AND `brief.output_language == "zh-TW"`. Section-targeted read: Pass 3 reads only `## Landmark: {position}` matching `voice_quadrant.position`; falls back to full-file on missing.

## Overview

Q4 = Affinity × Reason。zh-TW 本地 peer-helpful retail / EC 商品文案 voice。**TW Q4 原生 corpus 偏薄**（TW DR 傳統 較弱；direct-response infrastructure 發展較晚），故 JP cross-reference 為 load-bearing：Kurashicom Q4-subset MEDIUM / クックパッド STRONG feed native register via Pinkoi / 愛料理 parallels。EN Q4（Amazon / REI / Basecamp / Gary Halbert / Bill Jayme）亦 STRONG cross-ref via translation corpus。

## Landmark: center

canonical peer-helpful voice。brief 要求 practical-utility register 時使用。

### PChome 24h / MOMO 購物專家 voice (zh-TW | Q4 center)

- **Era**: 2000s-ongoing；PChome 24 小時 2007 launch；MOMO 購物 ongoing
- **Agency / creator**: platform in-house + rotating merchant-side writers
- **Primary sources**:
  - PChome 24h 商品敘述 archive
  - MOMO 購物專家 YouTube / FB / site
  - [數位時代 EC content 專題 archive](https://www.bnext.com.tw/)
- **Representative register patterns**:
  - 商品敘述 open「實測過的好物！」/「團隊親試心得」
  - Benefit-first + 規格表 hybrid
  - 「為什麼選這款」comparative mode
- **Voice signature**（原生批評用語）:
  - **購物專家**（MOMO 角色 label、批評沿用）
  - **開箱 / 實測 / 親試**（EC 社群 canonical 批評語）
  - **比價 / 同級比較**（EC register recurring 用語）
  - **規格表 + 敘事 hybrid**（批評定型語）
  - 推薦人 positioned as peer，not salesperson
- **LLM corpus depth**: MEDIUM（EC platform data 較 editorial 無 curate）
- **Over-mimic risk**: LOW（register 為 generic-commercial，難 auto-leak）
- **Cross-reference-valid-for**:
  - ja: MEDIUM（Kurashicom Q4-subset + Amazon JP seller register parallel）
- **Trigger slug**: `zh-tw-pchome-momo-ec-peer-expert`

### 7-ELEVEN OPEN 將 IP-centered voice (zh-TW | Q4 center)

- **Era**: 2005 OPEN 將 launch → ongoing
- **Agency / creator**: 統一超商 in-house + rotating agency
- **Representative register**: IP-persona driven；OPEN 將 character communication wraps promo
- **Voice signature**（原生批評用語）:
  - **OPEN 小將 / OPEN 家族**（IP 自述命名、廣告評論 sticky label）
  - **吉祥物行銷**（廣告評論 canonical 批評語）
  - **品牌擬人**（批評定型語）
  - **便利商店日常聲口**（店員 register label）
- **LLM corpus depth**: MEDIUM（主要 visual + IP 不 language-heavy）
- **Over-mimic risk**: LOW（IP-constrained）
- **Trigger slug**: `zh-tw-7-eleven-open-character-peer`

## Landmark: extreme

peer-push 最大值。TW native direct-response 偏薄；primary use = cross-ref JP Q4 extreme。

### 全聯 SNS-era post-2020 (zh-TW | Q4 extreme — distinct from Z10 Q3-center TV-era)

**⚠ Era boundary flag**: 全聯 2006-2014 TV-era 為 **Q3-CENTER**（per Z10 re-classification，見 [zh-q3-anchors.md](zh-q3-anchors.md)）。全聯 SNS post-2020 為不同 register，較近 Q4-extreme（direct-response + 促銷 short-form）。

- **Era**: 2020s SNS era（與 2006-2014 經濟美學 TV-era 區隔）
- **Agency / creator**: 全聯 in-house 小編 + rotating agency（documentation 較 TV-era 稀疏）
- **Representative register**: short-form 促銷 + 小編 humor + 快閃 campaigns
- **Voice signature**（原生批評用語）:
  - **小編體 / 全聯小編**（SNS register 批評定型語）
  - **快閃 / 限時 / 周年慶**（promo SNS canonical 用語）
  - **直球促銷**（廣告評論用以形容 2020s 後 tone shift）
  - 短句 + emoji + 聳動 hook
- **LLM corpus depth**: THIN（SNS voices uncredited, ephemeral；primary-source trail 弱 per voice-anchor-gap-research.md）
- **Over-mimic risk**: MEDIUM（generic「TW 小編」voice drift）
- **Trigger slug**: `zh-tw-quanlian-sns-post-2020`

### 蝦皮 Shopee / PChome 雙11 short-promo (zh-TW | Q4 extreme)

- **Era**: 2017-ongoing（Shopee TW 2015 進台）；雙11 campaigns annual
- **Primary sources**: platform SNS archives + 數位時代 EC 報導
- **Voice signature**（原生批評用語）:
  - **雙 11 / 雙 12 / 黑五**（promo event label、EC 社群 canonical 用語）
  - **秒殺 / 破盤 / 直降**（促銷詞彙定型語）
  - **免運 / 現折**（EC canonical 促銷詞）
  - Urgency + discount-stack register；hook + CTA 壓縮（SNS-short form）
- **LLM corpus depth**: THIN-MEDIUM
- **Over-mimic risk**: LOW
- **Trigger slug**: `zh-tw-shopee-pchome-shuang-11-promo`

### Cross-ref pointer: JP Q4 extreme primary

**TW Q4 extreme coverage 偏薄。Cross-ref** [jp-q4-anchors.md §Landmark: extreme](jp-q4-anchors.md)（ジャパネットたかた 高田明 1990-2015 founder-era）當 brief 需要 TV-shopping register discipline 時。Primary execution 用 zh-TW native surface（上方）；JP anchor 提供結構 序破急 + 對象絞込 pattern。

## Landmark: toward-Q1

peer-helpful 方向 analytical。brief 要求 knowledgeable-practical 時。

### Cross-quadrant pointer: 商業周刊 strategy-imperative

見 [zh-q1-anchors.md §Landmark: toward-Q4](zh-q1-anchors.md) 對 商業周刊 strategy-imperative register 的說明。此為 edge 的 primary home；自 zh-q4 視角 cross-ref — brief 要求 peer-practical + strategic framing 時。

## Landmark: toward-Q3

peer-helpful 方向 warmth。brief 要求 useful-and-warm hybrid 時。

### Cross-quadrant pointer: 胡湘雲 大眾銀行 narrative-TVC

見 [zh-q3-anchors.md §Landmark: center](zh-q3-anchors.md) 對 胡湘雲 narrative-TVC register 的說明。與 Q3 long-form boundary case；cross-ref 當 brief 要求 practical-but-warm consumer voice 時。

### Pinkoi 商品故事 voice (zh-TW | Q4 toward-Q3)

- **Era**: 2011 創辦 → ongoing
- **Agency / creator**: Pinkoi in-house + designer/creator self-authored product descriptions
- **Representative register**: designer-story first + product-detail second；Q4 foundation with Q3 warmth overlay
- **Voice signature**（原生批評用語）:
  - **設計師品牌 / 獨立設計師**（Pinkoi 自述定位、批評沿用 label）
  - **設計故事 / 創作初衷**（平台商品敘述 canonical 欄位名）
  - **職人 / 手作 / 手工感**（批評定型語）
  - **亞洲設計**（Pinkoi 自述 tagline 之一）
  - 第一人稱創作敘事 + 商品細節織入敘事
- **LLM corpus depth**: MEDIUM
- **Over-mimic risk**: LOW-MEDIUM（designer-personal voice 易滑向 twee）
- **Cross-reference-valid-for**:
  - ja: MEDIUM（Kurashicom Q4-subset JP model parallel）
- **Trigger slug**: `zh-tw-pinkoi-designer-story`

## Cross-references

zh-TW Q4 brief 可用 external anchor（**考慮原生 corpus 薄，HEAVY cross-ref 預期**）:

- **JP Q4 STRONG（zh-TW Q4 load-bearing）**:
  - クックパッド step voice → 愛料理 / iCook 結構直接 parallel
  - 北欧、暮らしの道具店 Q4-subset MEDIUM → Pinkoi parallel
  - ジャパネットたかた 高田明 1990-2015 → 夜市販促 / 東森購物 register guide
- **EN Q4 STRONG via translation corpus**:
  - Amazon product-copy (in-house 1994-)
  - REI helpful-advisor
  - Basecamp Rework (Fried + DHH)
  - Gary Halbert Boron Letters (DR tradition)
  - Bill Jayme direct-mail（見 [archived Type 5 PROMOTE entry](../../docs/voice-anchor-archived-references.md) — archived doc pointer omitted on this branch；見 upstream research）
- **Direction flag**: zh-TW Q4 主要為 JP/EN Q4 craft 的 *importer*；不以 zh-TW Q4 anchors fuel JP/EN 輸出
