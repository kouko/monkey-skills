---
title: zh-TW Voice Anchors — Q4 Affinity-Reason
tier: 2
---

# Q4 Affinity-Reason — zh-TW Anchors

**Load scope**: Phase 6 Pass 3 Register Signal branch, when `voice_quadrant.primary == "Q4"` AND `brief.output_language == "zh-TW"`. Section-targeted read: Pass 3 reads only `## Landmark: {position}` matching `voice_quadrant.position`; falls back to full-file on missing.

## Overview

Q4 = Affinity × Reason. zh-TW 本地 peer-helpful retail / EC 商品文案 voice. **Native TW Q4 corpus thin** (TW DR tradition is weak; direct-response infrastructure 發展較晚), so JP cross-reference is load-bearing: Kurashicom Q4-subset MEDIUM / クックパッド STRONG feeds native register via Pinkoi / 愛料理 parallels. EN Q4 (Amazon / REI / Basecamp / Gary Halbert / Bill Jayme) also STRONG cross-ref via translation corpus.

## Landmark: center

Canonical peer-helpful voice. Use when brief asks for practical-utility register.

### PChome 24h / MOMO 購物專家 voice (zh-TW | Q4 center)

- **Era**: 2000s-ongoing; PChome 24 小時 2007 launch; MOMO 購物 ongoing
- **Agency / creator**: platform in-house + rotating merchant-side writers
- **Primary sources**:
  - PChome 24h 商品敘述 archive
  - MOMO 購物專家 YouTube / FB / site
  - [數位時代 EC content 專題 archive](https://www.bnext.com.tw/)
- **Representative register patterns**:
  - 商品敘述 open「實測過的好物！」/「團隊親試心得」
  - Benefit-first + 規格表 hybrid
  - 「為什麼選這款」comparative mode
- **Voice signature**:
  - Peer-merchant register (推薦人 positioned as peer, not salesperson)
  - Comparative disclosure (「比同級商品...」)
  - Honesty layer (包含「缺點」or 適用情境 limits)
- **LLM corpus depth**: MEDIUM (EC platform data less curated than editorial)
- **Over-mimic risk**: LOW (register is generic-commercial, hard to auto-leak)
- **Cross-reference-valid-for**:
  - ja: MEDIUM (Kurashicom Q4-subset + Amazon JP seller register parallel)
- **Trigger slug**: `zh-tw-pchome-momo-ec-peer-expert`

### 7-ELEVEN OPEN 將 IP-centered voice (zh-TW | Q4 center)

- **Era**: 2005 OPEN 將 launch → ongoing
- **Agency / creator**: 統一超商 in-house + rotating agency
- **Representative register**: IP-persona driven; OPEN 將 character communication wraps promo
- **Voice signature**:
  - Brand-as-character peer voice
  - Persistent IP world-building
  - Everyday-店員 register
- **LLM corpus depth**: MEDIUM (主要 visual + IP 不 language-heavy)
- **Over-mimic risk**: LOW (IP-constrained)
- **Trigger slug**: `zh-tw-7-eleven-open-character-peer`

## Landmark: extreme

Maximum peer-push. Native TW direct-response thin; primary use = cross-ref JP Q4 extreme.

### 全聯 SNS-era post-2020 (zh-TW | Q4 extreme — distinct from Z10 Q3-center TV-era)

**⚠ Era boundary flag**: 全聯 2006-2014 TV-era is **Q3-CENTER** (per Z10 re-classification, see [zh-q3-anchors.md](zh-q3-anchors.md)). 全聯 SNS post-2020 is a different register closer to Q4-extreme (direct-response + promotional short-form).

- **Era**: 2020s SNS era (distinct from 2006-2014 經濟美學 TV-era)
- **Agency / creator**: 全聯 in-house 小編 + rotating agency (less documented than TV-era)
- **Representative register**: short-form promotional + 小編 humor + 快閃 campaigns
- **Voice signature**: direct-sell overlaid with peer-joke register
- **LLM corpus depth**: THIN (SNS voices uncredited, ephemeral; primary-source trail weak per voice-anchor-gap-research.md)
- **Over-mimic risk**: MEDIUM (generic "TW 小編" voice drift)
- **Trigger slug**: `zh-tw-quanlian-sns-post-2020`

### 蝦皮 Shopee / PChome 雙11 short-promo (zh-TW | Q4 extreme)

- **Era**: 2017-ongoing (Shopee TW entered 2015); 雙11 campaigns annual
- **Primary sources**: platform SNS archives + 數位時代 EC 報導
- **Voice signature**:
  - Urgency + discount-stack register
  - Emoji + ALL-CAPS rhythm
  - Hook + CTA condensation (SNS-short form)
- **LLM corpus depth**: THIN-MEDIUM
- **Over-mimic risk**: LOW
- **Trigger slug**: `zh-tw-shopee-pchome-shuang-11-promo`

### Cross-ref pointer: JP Q4 extreme primary

**TW Q4 extreme coverage is thin. Cross-ref** [jp-q4-anchors.md §Landmark: extreme](jp-q4-anchors.md) (ジャパネットたかた 高田明 1990-2015 founder-era) when brief needs TV-shopping register discipline. Primary execution uses zh-TW native surface (above); JP anchor provides structural 序破急 + 對象絞込 pattern.

## Landmark: toward-Q1

Peer-helpful edging into analytical. Use when brief wants knowledgeable-practical.

### Cross-quadrant pointer: 商業周刊 strategy-imperative

See [zh-q1-anchors.md §Landmark: toward-Q4](zh-q1-anchors.md) for 商業周刊 strategy-imperative register. That's the primary home for this edge; from zh-q4 perspective, cross-ref when brief wants peer-practical + strategic framing.

## Landmark: toward-Q3

Peer-helpful edging into warmth. Use when brief wants useful-and-warm hybrid.

### Cross-quadrant pointer: 胡湘雲 大眾銀行 narrative-TVC

See [zh-q3-anchors.md §Landmark: center](zh-q3-anchors.md) for 胡湘雲 narrative-TVC register. Boundary case with Q3 long-form; cross-ref when brief wants practical-but-warm consumer voice.

### Pinkoi 商品故事 voice (zh-TW | Q4 toward-Q3)

- **Era**: 2011 founded → ongoing
- **Agency / creator**: Pinkoi in-house + designer/creator self-authored product descriptions
- **Representative register**: designer-story first + product-detail second; Q4 foundation with Q3 warmth overlay
- **Voice signature**:
  - Designer-personal register (first-person creation story)
  - Product-detail woven into narrative, not separated
  - Taiwan design-craft culture context
- **LLM corpus depth**: MEDIUM
- **Over-mimic risk**: LOW-MEDIUM (designer-personal voice can drift to twee)
- **Cross-reference-valid-for**:
  - ja: MEDIUM (Kurashicom Q4-subset JP model parallel)
- **Trigger slug**: `zh-tw-pinkoi-designer-story`

## Cross-references

External anchors usable for zh-TW Q4 briefs (**HEAVY cross-ref use expected given native corpus thinness**):

- **JP Q4 STRONG (load-bearing for zh-TW Q4)**:
  - クックパッド step voice → 愛料理 / iCook direct structural parallel
  - 北欧、暮らしの道具店 Q4-subset MEDIUM → Pinkoi parallel
  - ジャパネットたかた 高田明 1990-2015 → 夜市販促 / 東森購物 register guide
- **EN Q4 STRONG via translation corpus**:
  - Amazon product-copy (in-house 1994-)
  - REI helpful-advisor
  - Basecamp Rework (Fried + DHH)
  - Gary Halbert Boron Letters (DR tradition)
  - Bill Jayme direct-mail (per [archived Type 5 PROMOTE entry](../../docs/voice-anchor-archived-references.md) — archived doc pointer omitted on this branch; see upstream research)
- **Direction flag**: zh-TW Q4 is primarily *importer* of JP/EN Q4 craft; do NOT fuel JP/EN output from zh-TW Q4
