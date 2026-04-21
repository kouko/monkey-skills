---
title: zh-TW Voice Anchors — Q3 Affinity-Emotion (Router Index)
tier: 2
schema_version: router-v1
migrated_date: 2026-04-21
---

# Q3 Affinity-Emotion — zh-TW Anchor Router

**Load scope**: Phase 6 Pass 3 Register Signal branch, when `voice_quadrant.primary == "Q3"` AND `brief.output_language == "zh-TW"`. This file is a **router index** — Pass 3 reads the landmark section matching `voice_quadrant.position`, then loads the named `anchor-*.md` file for full voice body.

## Two-step read protocol (v1.6.0)

1. **This file (router)**: lists anchors in each landmark group with one-line voice direction + slug + relative path (single-folder flat)
2. **Per-anchor file** `anchor-{slug}.md`: full Layer 1 v2 entry (Voice direction / Native critical read / Prose mechanics / Examples / Don't / Metadata)

Pass 3 consumes router to select candidate → loads the named anchor file(s) for body. See `voice-anchor-meta-core.md §v2 schema` for field schema and selection rubric.

## Overview

Q3 = Affinity × Emotion。zh-TW canonical:
- **center**: 龔大中 全聯格言體 / 吳念真 台語氣口 / 胡湘雲 大眾銀行 long-form TVC
- **extreme**: 金鵬遠 杜蕾斯借勢文案 (CN cross-pollination reference)
- **toward-Q2**: 黃春明 humane-vernacular / 三毛 lyrical-travel-romantic

**Cross-ref**: JP Q3 STRONG 流入 — 向田 / 糸井 aesthetic 直接 feed TW 文青消費 / 家庭 intimate registers.

**⚠ Z10 correction**: 全聯 TV-era 2006-2014 為 Q3-**center** (格言 / aphorism register) NOT Q3-extreme; Q3-extreme reserves for peer-intimate voices (午夜兩點的朋友 聲口).

## Landmark: center

Canonical peer-warm voice. Use when brief requires standard affinity-emotional.

- **龔大中 — 全聯格言體** (奧美 ECD craft-gate) — [anchor-zh-tw-gong-dazhong-quanlian-economics-aesthetics.md](anchor-zh-tw-gong-dazhong-quanlian-economics-aesthetics.md)
  - Slug: `zh-tw-gong-dazhong-quanlian-economics-aesthetics`
  - Register: 對仗格言 + 台式自嘲 + 素人第一人稱；時尚街拍視覺 × 庶民語言 mismatch

- **吳念真 — 保力達B 台語氣口** (named CW + VO) — [anchor-zh-tw-wu-nien-jen-taiyu-peer-intimate.md](anchor-zh-tw-wu-nien-jen-taiyu-peer-intimate.md)
  - Slug: `zh-tw-wu-nien-jen-taiyu-peer-intimate`
  - Register: 台語氣口 + 講古式敘事 + 庶民聲口；勞動階級肉身感
  - ⚠ Z5/Z7 preserved: 多喝水 非吳念真 (奧美 in-house); 長榮〈I SEE YOU〉VO 為金城武

- **胡湘雲 — 大眾銀行 long-form TVC** (named CD) — [anchor-zh-tw-hu-xiang-yun-narrative-tvc.md](anchor-zh-tw-hu-xiang-yun-narrative-tvc.md)
  - Slug: `zh-tw-hu-xiang-yun-narrative-tvc`
  - Register: 不平凡的平凡大眾 tagline; 真人真事改編 + 3-min TVC 敘事 + 留白多

## Landmark: extreme

Peer-intimate 最大值 / cross-pollination registers. Apply mitigation per anchor file's Don't block.

- **金鵬遠 — 杜蕾斯借勢文案** (zh-CN, named CD + 環時互動 operator, STRICT era lock 2011-2017) — [anchor-zh-cn-jin-pengyuan-durex-borrowed-timing.md](anchor-zh-cn-jin-pengyuan-durex-borrowed-timing.md)
  - Slug: `zh-cn-jin-pengyuan-durex-borrowed-timing`
  - Register: 借勢文案 + 擦邊球分寸 + 小杜擬人化 + 實時熱點
  - Cross-ref note: CN anchor; zh-TW registry 用作 register-pattern reference 不作 fuel (TW 商業文化 ≠ CN 微博 ecosystem)

**Moved out of voice library** (per audit, v1.6.0):
- 故宮粉絲團「朕知道了」era → rotating 6-10-person 小編 team, no isolable creator → see [../../../../docs/format-templates/zh-tw-npm-zhen-zhidaole-institutional-meme.md](../../../../docs/format-templates/zh-tw-npm-zhen-zhidaole-institutional-meme.md) (format template, NOT voice anchor)
- 台灣吧 Taiwan Bar → dual-founder team register → see [../../../../docs/register-references/zh-tw-taiwan-bar-educational-comedy.md](../../../../docs/register-references/zh-tw-taiwan-bar-educational-comedy.md) (register reference, NOT voice anchor)

## Landmark: toward-Q2

Affinity 方向 manifesto. Use when brief requires warm-but-aspirational.

- **黃春明 — 鄉土文學 humane-vernacular** (author) — [anchor-zh-tw-huang-chun-ming-humane-vernacular.md](anchor-zh-tw-huang-chun-ming-humane-vernacular.md)
  - Slug: `zh-tw-huang-chun-ming-humane-vernacular`
  - Register: 鄉土文學 + 小人物書寫 + 悲憫人道關懷
  - Cross-ref: Raymond Carver working-class precision (EN) / 向田邦子 domestic (JP) / documented co-generation with 吳念真 (《兒子的大玩偶》侯孝賢 1983 nexus)

- **三毛 — lyrical-travel-romantic** (author) — [anchor-zh-tw-san-mao-lyrical-travel-romantic.md](anchor-zh-tw-san-mao-lyrical-travel-romantic.md)
  - Slug: `zh-tw-san-mao-lyrical-travel-romantic`
  - Register: 流浪文學 + 漂泊抒情 + 散文化小說體；Sahara/Jose 母題 ⚠ mitigation required (MEDIUM over-mimic)

## Landmark: toward-Q4

Affinity 方向 peer-helpful reasoning. Use when brief requires warm-and-useful hybrid.

### Thin native corpus — cross-load zh-q4

zh-TW Q3 toward-Q4 edge 在 active library 偏薄。Brief 需要 Q3-warmth bridged into peer-reasoning 時，cross-load [zh-q4-anchors.md](zh-q4-anchors.md) center landmark.

## Cross-references (non-zh-TW anchors reachable from this quadrant)

- **JP Q3 STRONG cross-ref** (meta-detail verified map):
  - 向田邦子 domestic-intimacy-with-bite → TW 家庭 register 直承
  - 糸井重里 state-proposal → TW 文青消費 底色
  - 吉本ばなな gentle-grief-domestic → safer alt
  - 坂元裕二 conversational-aphorism → drama-dialogue template
  - 谷川俊太郎 clear-child-cosmic → poetic compression template
- **HK cross-ref**: 金庸 武俠 niche only — 須搭配 **HIGH+++ over-mimic mitigation** (meta-core registry)
- **EN Q3 MEDIUM via translation**: Kate Kiefer Lee (`anchor-en-kate-kiefer-lee-*`) / Richard Reed (`anchor-en-richard-reed-*`) / Nora Ephron warm-wit (`anchor-en-nora-ephron-*`) / George Saunders compassionate-absurd (`anchor-en-george-saunders-*`)

## Migration history (audit trail)

- **v1.0-v1.4.x**: aggregate `zh-q3-anchors.md` with 7 entries inline (龔大中 + 吳念真 + 胡湘雲 + 故宮 + 台灣吧 + 杜蕾斯 + 黃春明 + 三毛)
- **v1.5.0**: Phase B recasts — 龔大中 / 金鵬遠 individual-creator recasts added to `docs/voice-anchor-deep-dives/pilot-layer1-v2-*.md`; schema v2 spec added to meta-core
- **v1.6.0 (this file)**: 6 v2 entries moved to standards/ as `anchor-*.md` per-entry files; 故宮 + 台灣吧 moved out of voice library to `format-templates/` + `register-references/`; this file becomes router index
