---
title: zh Voice Anchors — Q2 Authority-Emotion (Router Index)
tier: 2
schema_version: router-v1
migrated_date: 2026-04-21
---

# Q2 Authority-Emotion — zh Anchor Router (TW + HK + canonical zh-literary)

**Load scope**: Phase 6 Pass 3 Register Signal branch, when `voice_quadrant.primary == "Q2"` AND `brief.output_language == "zh-TW"` (or zh-HK / zh canonical literary registers). Router index.

## Overview

Q2 = Authority × Emotion. zh canonical:
- **zh-TW craft-gate** (許舜英 / 李欣頻 / 葉明桂): routed via `voice-anchor-meta-detail.md §Cross-Master Context (ZH)`
- **zh-HK ECDs**: 朱家鼎 Mike Chu (extreme), KC Tsang (toward-Q1)
- **zh-HK screenwriter**: 王家衛 (extreme)
- **zh canonical authors**: 錢鍾書 (toward-Q1), 白先勇 (toward-Q1), 張愛玲 (toward-Q3), 朱天文 (toward-Q3)

## Landmark: center

### Craft-gate pointers (三位 canonical masters — route to craft-lineage)

- **中興百貨 brand-era → 許舜英** — load `voice-anchor-meta-detail.md §Cross-Master Context` §許舜英
  - Slug: `zh-tw-zhongxing-xusunying-ideology-era` (brand-era label preserved; craft-gate is the actual voice anchor)
- **誠品書店 brand-era → 李欣頻** — load `voice-anchor-meta-detail.md §Cross-Master Context` §李欣頻
  - Slug: `zh-tw-eslite-lixinping-literary-bookstore`
- **左岸咖啡館 brand-era → 葉明桂** — load `voice-anchor-meta-detail.md §Cross-Master Context` §葉明桂
  - Slug: `zh-tw-zuoan-yemingui-strategic-cafe`

## Landmark: extreme

- **朱家鼎 Mike Chu Ka-Ting — 鐵達時「天長地久三部曲」** (zh-HK named ECD) — [anchor-zh-hk-mike-chu-titus-cinematic-romance-inversion.md](anchor-zh-hk-mike-chu-titus-cinematic-romance-inversion.md)
  - Slug: `zh-hk-mike-chu-titus-cinematic-romance-inversion`
  - ⚠ Z9/Z10 preserved: 朱家鼎 ≠ 曾錦程 KC Tsang (separate entries)

- **王家衛 Wong Kar-wai** (zh-HK screenwriter) — [anchor-zh-hk-wong-kar-wai-monologue-fragment-temporal.md](anchor-zh-hk-wong-kar-wai-monologue-fragment-temporal.md)
  - Slug: `zh-hk-wong-kar-wai-monologue-fragment-temporal`
  - ⚠ Over-mimic risk HIGH: expiration dates / 1-minute / pineapple cans / step-printing leaks — meta-core registry mitigation required

## Landmark: toward-Q1

- **錢鍾書《圍城》** (zh canonical novelist) — [anchor-zh-qianzhongshu-erudite-sardonic-metaphor.md](anchor-zh-qianzhongshu-erudite-sardonic-metaphor.md)
  - Slug: `zh-qianzhongshu-erudite-sardonic-metaphor`

- **白先勇 Pai Hsien-yung** (zh-TW novelist) — [anchor-zh-tw-pai-hsien-yung-elegiac-diaspora.md](anchor-zh-tw-pai-hsien-yung-elegiac-diaspora.md)
  - Slug: `zh-tw-pai-hsien-yung-elegiac-diaspora`

- **曾錦程 KC Tsang — SUNDAY / 和記 / 眼鏡 88** (zh-HK Cantonese-vernacular-pun) — [anchor-zh-hk-kc-tsang-cantonese-vernacular-pun.md](anchor-zh-hk-kc-tsang-cantonese-vernacular-pun.md)
  - Slug: `zh-hk-kc-tsang-cantonese-vernacular-pun`

## Landmark: toward-Q3

- **張愛玲 Eileen Chang** (zh canonical novelist) — [anchor-zh-eileen-chang-aphoristic-observation.md](anchor-zh-eileen-chang-aphoristic-observation.md)
  - Slug: `zh-eileen-chang-aphoristic-observation`

- **朱天文 Chu Tien-wen** (zh-TW author / screenwriter) — [anchor-zh-tw-chu-tien-wen-temporal-slowness.md](anchor-zh-tw-chu-tien-wen-temporal-slowness.md)
  - Slug: `zh-tw-chu-tien-wen-temporal-slowness`

## Cross-references

- **JP Q2 STRONG** (craft-gate direction): 寺山修司 `anchor-jp-terayama-*`, 谷崎『陰翳礼讃』`anchor-jp-tanizaki-inei.md`, 川端『雪国』`anchor-jp-kawabata-shinkankaku-ha.md`, 糸井重里 (craft-gate)
- **EN Q2**: Apple Lee Clow `anchor-en-lee-clow-*`, Patek Philippe Tim Delaney `anchor-en-tim-delaney-*`, Yvon Chouinard `anchor-en-yvon-chouinard-*`, Toni Morrison `anchor-en-toni-morrison-*`, James Baldwin `anchor-en-james-baldwin-*`, Joan Didion `anchor-en-joan-didion-*`

## Migration history

- **v1.0-v1.5.x**: aggregate with 10 inline entries (3 brand-era pointers + 朱家鼎 + KC Tsang + 王家衛 + 錢鍾書 + 白先勇 + 張愛玲 + 朱天文)
- **v1.6.0** (this file): 7 individual-creator entries moved to flat `anchor-*.md`; 3 brand-era entries collapsed to craft-gate pointers (許舜英 / 李欣頻 / 葉明桂 already in voice-anchor-meta-detail.md §Cross-Master Context)
