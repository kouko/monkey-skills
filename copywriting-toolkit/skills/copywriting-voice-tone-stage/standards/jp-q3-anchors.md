---
title: JP Voice Anchors — Q3 Affinity-Emotion (Router Index)
tier: 2
schema_version: router-v1
migrated_date: 2026-04-21
---

# Q3 Affinity-Emotion — JP Anchor Router

**Load scope**: Phase 6 Pass 3 Register Signal branch, when `voice_quadrant.primary == "Q3"` AND `brief.output_language == "ja"`. Router index.

## Overview

Q3 = Affinity × Emotion. JP canonical: 向田邦子 (center, 真打ち random), 坂元裕二 (center, 言葉の魔術師), 谷川俊太郎 (extreme, poet), 宮沢賢治 (extreme, 心象 sketch), 吉本ばなな (extreme, J文学 / 大胆な省略 — 村上春樹 の安全な代替), 梅田悟司 (toward-Q2, 内なる言葉).

**Cross-ref**: JP Q3 STRONG 流出 → zh-TW Q3 (糸井 → 全聯, 向田 → TW家庭 register 直承).

## Landmark: center

- **向田邦子 — 「真打ち」随筆** (essayist + screenwriter, 1929-1981) — [anchor-jp-mukoda-kuniko-shinuchi-zuihitsu.md](anchor-jp-mukoda-kuniko-shinuchi-zuihitsu.md)
  - Slug: `jp-mukoda-kuniko-shinuchi-zuihitsu`

- **坂元裕二 — 言葉の魔術師** (screenwriter, 1967-) — [anchor-jp-sakamoto-yuji-kotoba-no-majutsushi.md](anchor-jp-sakamoto-yuji-kotoba-no-majutsushi.md)
  - Slug: `jp-sakamoto-yuji-kotoba-no-majutsushi`

- **澤本嘉光 — 白戸家世界観** (named CD, SoftBank 2007- recast) — [anchor-jp-sawamoto-yoshimitsu-shiroto-family.md](anchor-jp-sawamoto-yoshimitsu-shiroto-family.md)
  - Slug: `jp-sawamoto-yoshimitsu-shiroto-family`
  - Recast from v1 「Brand-era pointer: SoftBank 白戸家（佐々木宏 + 澤本嘉光）」→ named CD 澤本嘉光 selected (Phase B v1.5.0).

Craft-gate pointer: 糸井重里 状態提案 register — load `voice-anchor-meta-detail.md §Cross-Master Context`.

## Landmark: extreme

- **谷川俊太郎 — 詩のことば** (poet, 1931-2024) — [anchor-jp-tanikawa-shi-no-kotoba.md](anchor-jp-tanikawa-shi-no-kotoba.md)
  - Slug: `jp-tanikawa-shi-no-kotoba`
  - `safe_substitute_for: [糸井重里]` (v1.11.0) — 糸井重里 documented lineage (ほぼ日『ぼく』2013 collab); 谷川 LOW vs 糸井 HIGH+ craft-gate; 谷川 mechanics 仮名過半+breath-line avoid 糸井's「。」-on-fragment surface-mimic trap.

- **宮沢賢治 — 心象スケッチ** (author, 1896-1933) — [anchor-jp-miyazawa-shinshou-sketch.md](anchor-jp-miyazawa-shinshou-sketch.md)
  - Slug: `jp-miyazawa-shinshou-sketch`

- **吉本ばなな — J文学 / 大胆な省略** (novelist, 1964-) — [anchor-jp-yoshimoto-banana-j-bungaku.md](anchor-jp-yoshimoto-banana-j-bungaku.md)
  - Slug: `jp-yoshimoto-banana-j-bungaku`
  - Note: 村上春樹 の安全な代替 (Murakami over-mimic registry HIGH; ばなな lower-risk with similar peer-intimate cadence).

## Landmark: toward-Q2

- **梅田悟司 — 内なる言葉の方法論** (named CW, ジョージア「世界は誰かの仕事でできている。」) — [anchor-jp-umeda-satoshi-uchinaru-kotoba.md](anchor-jp-umeda-satoshi-uchinaru-kotoba.md)
  - Slug: `jp-umeda-satoshi-uchinaru-kotoba`

## Landmark: toward-Q4

- **松浦弥太郎 — 「今日もていねいに」** (essayist, 元『暮しの手帖』編集長 2006-2015, COW BOOKS 代表) — [anchor-jp-matsuura-yataro-teinei-essay.md](anchor-jp-matsuura-yataro-teinei-essay.md) (v1.11.0)
  - Slug: `jp-matsuura-yataro-teinei-essay`
  - Register: ですます調基調 + 一人称「ぼく/僕」+ 句点短文+並列読点; 『100の基本』体言止めマキシム 1 章 1 回; 命令形・勧誘形禁止
  - ⚠ Over-mimic HIGH: ひらがな過多 + 体言止め濫発 → ポエム化 / 自己啓発化. Mitigation: ですます基調+句点短文;体言止めは 1 章 1 回まで
  - Cross-ref: zh-TW STRONG (繁中既有譯本廣為流通、模仿者眾)

## Cross-references

- **zh-TW Q3 STRONG** (this direction dominant): 龔大中 全聯格言 / 吳念真 台語氣口 / 胡湘雲 大眾銀行 / 黃春明 / 三毛 — see [zh-q3-anchors.md](zh-q3-anchors.md)
- **EN Q3 MEDIUM via translation**: Kate Kiefer Lee `anchor-en-kate-kiefer-lee-*` / Richard Reed `anchor-en-richard-reed-*` / Nora Ephron `anchor-en-nora-ephron-*` / George Saunders `anchor-en-george-saunders-*`

## Migration history

- **v1.0-v1.5.x**: aggregate with 7 inline entries (向田 + 坂元 + 谷川 + 宮沢 + 吉本 + 梅田 + SoftBank brand-era pointer)
- **v1.6.0** (this file): 7 entries moved to flat `anchor-*.md` incl. 澤本嘉光 recast for SoftBank 白戸家
