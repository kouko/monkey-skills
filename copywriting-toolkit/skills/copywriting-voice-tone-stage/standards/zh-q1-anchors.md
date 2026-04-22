---
title: zh-TW Voice Anchors — Q1 Authority-Reason (Router Index)
tier: 2
schema_version: router-v1
migrated_date: 2026-04-21
---

# Q1 Authority-Reason — zh-TW Anchor Router

**Load scope**: Phase 6 Pass 3 Register Signal branch, when `voice_quadrant.primary == "Q1"` AND `brief.output_language == "zh-TW"`. Router index.

## Overview

Q1 = Authority × Reason. **zh-TW Q1 individual-creator pool is currently thin** — all v1 entries (天下 / 報導者 / 研之有物 / 商業周刊) are institutional publications with rotating editorial teams, so none qualify as v2 voice anchors. Brief resolution uses format-templates + register-references + JP/EN cross-reference.

**Gap flagged**: individual zh-TW Q1 essayists / long-form authors (e.g. 龍應台, 南方朔, 楊照) await Layer 1 v2 research in v1.7.0+.

## Landmark: center

All v1 entries moved out (v1.6.0):

- **天下雜誌 CommonWealth** (殷允芃-era institutional register) → [../../../../docs/anchor-references/zh-tw-tianxia-structural-analytical.md](../../../../docs/anchor-references/zh-tw-tianxia-structural-analytical.md)
- **報導者 The Reporter** (center + investigative-extreme registers, non-profit journalism) → [../../../../docs/anchor-references/zh-tw-reporter-explanatory-journalism.md](../../../../docs/anchor-references/zh-tw-reporter-explanatory-journalism.md)
- **研之有物 Research @ Sinica** (institutional 科普 platform) → [../../../../docs/anchor-references/zh-tw-research-sinica-popularization.md](../../../../docs/anchor-references/zh-tw-research-sinica-popularization.md)

Strategy: select individual voice anchor from the v1.8.0 additions below, or cross-load from JP/EN Q1 + use institutional register reference for structural layer.

### zh-TW Q1 individual-creator pool (v1.8.0 gap-fill)

- **南方朔 — lexical archaeology** (essayist / cultural critic) — [anchor-zh-tw-nan-fang-shuo-lexical-archaeology.md](anchor-zh-tw-nan-fang-shuo-lexical-archaeology.md)
  - Slug: `zh-tw-nan-fang-shuo-lexical-archaeology`
  - Register: 單一詞為入口 + 字源追溯 + 跨文化並舉 + 古典當代對照; 詞語考古學 register

## Landmark: extreme

Moved out: 報導者 investigative-extreme register (consolidated with center entry above).

## Landmark: toward-Q2

- **龍應台 — public intellectual address** (essayist / 野火集 1985-) — [anchor-zh-tw-lung-ying-tai-public-intellectual.md](anchor-zh-tw-lung-ying-tai-public-intellectual.md)
  - Slug: `zh-tw-lung-ying-tai-public-intellectual`
  - Register: 「你」作為讀者-公民的直接呼告 + 短句排比 + 歷史敘事 + 道德反問 + 具名田調感
  - ⚠ Over-mimic MEDIUM: 道德反問 tic + 演講腔 drift

## Landmark: toward-Q4

**商業周刊 Business Weekly** (金惟純-era institutional strategy-imperative) → [../../../../docs/anchor-references/zh-tw-business-weekly-strategy-imperative.md](../../../../docs/anchor-references/zh-tw-business-weekly-strategy-imperative.md)

- **楊照 — lecture-hall essay** (essayist / 誠品講堂 + podcast host) — [anchor-zh-tw-yang-zhao-lecture-hall-essay.md](anchor-zh-tw-yang-zhao-lecture-hall-essay.md)
  - Slug: `zh-tw-yang-zhao-lecture-hall-essay`
  - Register: 口語講堂 register 書面化 + 歷史現場具象 + 「其實」反轉連接詞 + 古典文本現代化解讀
  - ⚠ Over-mimic MEDIUM: 「其實」tic

## Cross-references

Primary cross-load targets for Q1 zh-TW briefs:

- **JP Q1 STRONG** (direction-dominant): route to `anchor-jp-soseki-yoyu-ha-dry-observer.md` / `anchor-jp-itami-juzo-keimyou-shadatsu.md` + jp-q1 format-templates (天声人語 / 東洋経済) for structural register parallel
- **EN Q1 STRONG**: David Ogilvy (`anchor-en-david-ogilvy-*`) / Claude Hopkins (`anchor-en-claude-hopkins-*`) / George Orwell (`anchor-en-george-orwell-*`) / Amy Hempel spare-authority (`anchor-en-amy-hempel-*`) / Hemingway (`anchor-en-hemingway-*`)
- **Wire cross-ref**: Reuters JP + 中央社 wire-copy — format-templates layer for wire-service structural register

## Migration history

- **v1.0-v1.5.x**: aggregate with 5 inline entries (天下 + 報導者 x2 + 研之有物 + 商業周刊), all institutional
- **v1.6.0** (this file): all 5 moved to register-references/ + format-templates/; zh-TW Q1 individual-creator pool gap-flagged for v1.7.0+ research
