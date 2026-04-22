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

- **原研哉 — design manifesto register** (named designer recast, MUJI AD 2001-) — [anchor-jp-hara-kenya-design-manifesto.md](anchor-jp-hara-kenya-design-manifesto.md)
  - Slug: `jp-hara-kenya-design-manifesto`
  - Register: design-as-sensory-awakening essay; 白 / 虚 / 間 conceptual vocabulary; 「ではなく」転倒 + 具体物→感覚→世界観 三段跳躍
  - Recast from: MUJI 無印良品 原研哉 era brand anchor (v1.3.x) → named designer 原研哉 (v1.8.0)

- **太田恵美 — JR東海「そうだ 京都、行こう。」** (named CW recast; CD 佐々木宏) — [anchor-jp-jr-central-souda-kyoto-discovery.md](anchor-jp-jr-central-souda-kyoto-discovery.md)
  - Slug: `jp-jr-central-souda-kyoto-discovery`
  - Register: 口語開口 + 独白体 + 季語ドライブ + 最小単位コピー; 30 年持続 campaign register
  - ⚠ v1.3.3 attribution correction preserved — CW = 太田恵美 (not 一倉宏), CD = 佐々木宏

## Landmark: extreme

- **寺山修司 — 言葉の錬金術師** (poet / playwright, 1935-1983) — [anchor-jp-terayama-kotoba-no-renkinjutsushi.md](anchor-jp-terayama-kotoba-no-renkinjutsushi.md)
  - Slug: `jp-terayama-kotoba-no-renkinjutsushi`

Craft-gate pointers (Q2 extreme): 糸井重里 Q2-edge + 秋山晶 — load `voice-anchor-meta.md §Cross-Master Context` when trigger matches.

## Landmark: toward-Q1

- **谷崎潤一郎『陰翳礼讃』** (novelist, 1886-1965) — [anchor-jp-tanizaki-inei.md](anchor-jp-tanizaki-inei.md)
  - Slug: `jp-tanizaki-inei`

- **三谷幸喜 — 群像会話劇・軽妙コメディ** (playwright + screenwriter) — [anchor-jp-mitani-koki-group-scene-dialogue-comedy.md](anchor-jp-mitani-koki-group-scene-dialogue-comedy.md) (v1.12.0)
  - Slug: `jp-mitani-koki-group-scene-dialogue-comedy`
  - Register: 群像会話リレー + 遮り (えっ/あの/ちょっと待って) + 敬語ズレ + ビリー・ワイルダー系譜 JP 適応;『古畑任三郎』『12 人の優しい日本人』『鎌倉殿の 13 人』
  - ⚠ Over-mimic MEDIUM: 遮り乱発 / キメ台詞飽和 / 敬語ズレ誤用は検知しやすい. Mitigation: 遮りは 3 発話に 1 回まで、キメ台詞は 1 シーン 1 回、敬語ズレは意味のある時だけ
  - Sorkin substitute として不適 (rhetorical Q-plus-self-answer / moral verdict / walk-and-talk の 3 核心技法すべて欠落)

Craft-gate pointer: 秋山晶 aphoristic time-philosophy — load `voice-anchor-meta.md §Cross-Master Context`.

## Landmark: toward-Q3

- **川端康成『雪国』— 新感覚派** (novelist, 1899-1972) — [anchor-jp-kawabata-shinkankaku-ha.md](anchor-jp-kawabata-shinkankaku-ha.md)
  - Slug: `jp-kawabata-shinkankaku-ha`

Craft-gate pointer: 糸井重里 「おいしい生活」Q2-edge — load `voice-anchor-meta.md §Cross-Master Context`.

## Cross-references

- **zh Q2 STRONG**: 中興百貨 (許舜英) / 誠品書店 (李欣頻) / 左岸咖啡館 (葉明桂) — load `voice-anchor-meta.md §Cross-Master Context`
- **EN Q2**: Apple Lee Clow `anchor-en-lee-clow-visionary-manifesto.md`, Nike Dan Wieden `anchor-en-dan-wieden-*`, Patek Philippe Tim Delaney `anchor-en-tim-delaney-patek-philippe-stewardship.md`, Yvon Chouinard `anchor-en-yvon-chouinard-patagonia-conscience.md`

## Migration history

- **v1.0-v1.5.x**: aggregate file with 5 inline entries + brand-era duplicates (原研哉 MUJI era + JR東海 + 寺山 + 谷崎 + 川端)
- **v1.6.0** (this file): 3 individual-creator entries moved to flat `anchor-*.md`; 原研哉 / 太田恵美 recast deferred (pending research, gap flagged)
