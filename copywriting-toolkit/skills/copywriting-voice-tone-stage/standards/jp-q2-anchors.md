---
title: JP Voice Anchors — Q2 Authority-Emotion (Router Index)
tier: 2
schema_version: router-v1
migrated_date: 2026-04-21
---

# Q2 Authority-Emotion — JP Anchor Router

**Load scope**: Phase 6 Pass 3 Register Signal branch, when `voice_quadrant.primary == "Q2"` AND `brief.output_language == "ja"`. Router index.

## Overview

Q2 = Authority × Emotion. Manifesto / 文学 / 陰翳 / brand-philosophy register. JP canonical: 寺山修司 (extreme), 谷崎 (toward-Q1), 川端 (toward-Q3).

## Landmark: center

- **原研哉 (MUJI era)** — RECAST pending research (v1.7.0+). v1 entry 「empty vessel / 空 / 透明性」register tracks to 原研哉 as design director but Layer 1 v2 research not yet completed. See `docs/voice-library-recast-audit.md`.
- **太田恵美 (JR東海「そうだ 京都、行こう。」)** — RECAST pending research (v1.7.0+). CD: 佐々木宏, CW: 太田恵美 (v1.3.3 attribution correction preserved).

## Landmark: extreme

- **寺山修司 — 言葉の錬金術師** (poet / playwright, 1935-1983) — [anchor-jp-terayama-kotoba-no-renkinjutsushi.md](anchor-jp-terayama-kotoba-no-renkinjutsushi.md)
  - Slug: `jp-terayama-kotoba-no-renkinjutsushi`

Craft-gate pointers (Q2 extreme): 糸井重里 Q2-edge + 秋山晶 — load [jp-copy-craft-lineage.md](jp-copy-craft-lineage.md) when trigger matches.

## Landmark: toward-Q1

- **谷崎潤一郎『陰翳礼讃』** (novelist, 1886-1965) — [anchor-jp-tanizaki-inei.md](anchor-jp-tanizaki-inei.md)
  - Slug: `jp-tanizaki-inei`

Craft-gate pointer: 秋山晶 aphoristic time-philosophy — load [jp-copy-craft-lineage.md](jp-copy-craft-lineage.md).

## Landmark: toward-Q3

- **川端康成『雪国』— 新感覚派** (novelist, 1899-1972) — [anchor-jp-kawabata-shinkankaku-ha.md](anchor-jp-kawabata-shinkankaku-ha.md)
  - Slug: `jp-kawabata-shinkankaku-ha`

Craft-gate pointer: 糸井重里 「おいしい生活」Q2-edge — load [jp-copy-craft-lineage.md](jp-copy-craft-lineage.md).

## Cross-references

- **zh Q2 STRONG**: 中興百貨 (許舜英) / 誠品書店 (李欣頻) / 左岸咖啡館 (葉明桂) — load [zh-copy-craft-lineage.md](zh-copy-craft-lineage.md)
- **EN Q2**: Apple Lee Clow `anchor-en-lee-clow-visionary-manifesto.md`, Nike Dan Wieden `anchor-en-dan-wieden-*`, Patek Philippe Tim Delaney `anchor-en-tim-delaney-patek-philippe-stewardship.md`, Yvon Chouinard `anchor-en-yvon-chouinard-patagonia-conscience.md`

## Migration history

- **v1.0-v1.5.x**: aggregate file with 5 inline entries + brand-era duplicates (原研哉 MUJI era + JR東海 + 寺山 + 谷崎 + 川端)
- **v1.6.0** (this file): 3 individual-creator entries moved to flat `anchor-*.md`; 原研哉 / 太田恵美 recast deferred (pending research, gap flagged)
