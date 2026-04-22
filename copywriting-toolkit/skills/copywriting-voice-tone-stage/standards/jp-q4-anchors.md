---
title: JP Voice Anchors — Q4 Affinity-Reason (Router Index)
tier: 2
schema_version: router-v1
migrated_date: 2026-04-21
---

# Q4 Affinity-Reason — JP Anchor Router

**Load scope**: Phase 6 Pass 3 Register Signal branch, when `voice_quadrant.primary == "Q4"` AND `brief.output_language == "ja"`. Router index.

## Overview

Q4 = Affinity × Reason. Peer-advocate + peer-helpful register. JP canonical: 高田明 (extreme, ジャパネット 2 秒の間). Platform / UGC registers are institutional (クックパッド / 通販生活 / ワークマン / 北欧、暮らしの道具店) — migrated out to `format-templates/` per v2 inclusion criterion.

## Landmark: center

- **青木耕平 — クラシコム 北欧、暮らしの道具店** (named founder recast; 青木耕平 + 佐藤友子 共同) — [anchor-jp-kurashicom-aoki-kohei-lifestyle-narrative.md](anchor-jp-kurashicom-aoki-kohei-lifestyle-narrative.md)
  - Slug: `jp-kurashicom-aoki-kohei-lifestyle-narrative`
  - Register: 商品説明を 暮らしの随筆 へ転調; 一人称「私」固定 + 生活情景冒頭 + 丁寧体淡々 + 形容詞禁 (具体シーン代わる)
  - Landmark: Q4 toward-Q3 (peer-practical with narrative warmth)

**Moved out to format templates** (v1.6.0):
- クックパッド「つくれぽ」文化 UGC → [../../../../docs/anchor-references/jp-cookpad-tsukurepo.md](../../../../docs/anchor-references/jp-cookpad-tsukurepo.md)

Cross-load: 伊丹十三 `anchor-jp-itami-juzo-keimyou-shadatsu.md` (Q1 toward-Q4 edge) for individual-voice substitute.

## Landmark: extreme

- **高田明 — ジャパネットたかた「2 秒の間」** (founder era のみ, 1974-2015) — [anchor-jp-japanet-takada-ni-byou-no-ma.md](anchor-jp-japanet-takada-ni-byou-no-ma.md)
  - Slug: `jp-japanet-takada-ni-byou-no-ma`
  - ⚠ Era lock: 高田明 founder era のみ canonical; post-2015 後継者 era 不採用.

**Moved out to format templates** (v1.6.0):
- 通販生活「カテゴリーにつき一点主義」→ [../../../../docs/anchor-references/jp-tsuhan-seikatsu-ipponshugi.md](../../../../docs/anchor-references/jp-tsuhan-seikatsu-ipponshugi.md)

**SKIP note preserved**: ドンキ POP visual-dominant — copy alone loses 50%+ signal; not an active anchor.

## Landmark: toward-Q1

- **佐藤可士和 — UNIQLO LifeWear** (named AD recast, SAMURAI 2000- / UNIQLO global CD 2006-) — [anchor-jp-uniqlo-sato-kashiwa-lifewear.md](anchor-jp-uniqlo-sato-kashiwa-lifewear.md)
  - Slug: `jp-uniqlo-sato-kashiwa-lifewear`
  - Register: 視覚先行 + コピー最小; 体言止め+句点 記号化; 「〜ではなく〜」 転倒レトリック; LifeWear 固有名化; グローバル機能 minimalism (vs 原研哉 和的 minimalism 区別要注意)

- **外山滋比古 — 思考エッセイ / 英文学者的随筆** (scholar-essayist, お茶の水女子大学名誉教授, 1923-2020) — [anchor-jp-toyama-shigehiko-shikou-seiri.md](anchor-jp-toyama-shigehiko-shikou-seiri.md) (v1.11.0)
  - Slug: `jp-toyama-shigehiko-shikou-seiri`
  - Register: 『思考の整理学』系思考エッセイ; 比喩先行・抽象後追い + 日常ことわざを論証の骨に + 「〜ではないか」dialogic 語尾 + Charles Lamb / Chesterton familiar essay 系譜
  - ⚠ Over-mimic MEDIUM: 比喩の骨格化 + dialogic 語尾 surface mimic. Mitigation: 比喩は章の骨、語尾は 〜ではないか、原語は一度だけ
  - Differentiation vs 池上彰: 池上は「わかる」ゴール(解説ジャーナリズム), 外山は「考える」プロセス(思考エッセイ)

## Landmark: toward-Q3

**Moved out to format templates** (v1.6.0):
- ワークマン SNS era アンバサダーマーケティング → [../../../../docs/anchor-references/jp-workman-ambassador-marketing.md](../../../../docs/anchor-references/jp-workman-ambassador-marketing.md)

Cross-load: 北欧、暮らしの道具店 Q3 warmth layer → see [jp-q3-anchors.md](jp-q3-anchors.md) for Q4+Q3 composite.

## Cross-references

- **zh-TW Q4**: 7-ELEVEN OPEN 將 / PChome / Shopee / 全聯 SNS-era post-2020 — all moved out to format-templates per audit. Individual-creator pool thin. Cross-load [zh-q4-anchors.md](zh-q4-anchors.md).
- **EN Q4**: Claude Hopkins `anchor-en-claude-hopkins-*`, Gary Halbert `anchor-en-gary-halbert-*`, Bill Jayme `anchor-en-bill-jayme-*`, Ben Thompson Stratechery `anchor-en-ben-thompson-*`, Basecamp Fried+DHH `anchor-en-basecamp-*` (if exists), Dashiell Hammett `anchor-en-dashiell-hammett-*`, Anton Chekhov `anchor-en-anton-chekhov-*`

## Migration history

- **v1.0-v1.5.x**: aggregate with 6 inline entries (クックパッド + 北欧 + 高田 + 通販生活 + UNIQLO + ワークマン)
- **v1.6.0** (this file): 高田明 moved to flat anchor-*.md; クックパッド / 通販生活 / ワークマン moved to format-templates/; 青木耕平 / 佐藤可士和 recast deferred to v1.7.0+
