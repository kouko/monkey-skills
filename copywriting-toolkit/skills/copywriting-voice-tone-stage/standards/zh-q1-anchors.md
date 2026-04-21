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

- **天下雜誌 CommonWealth** (殷允芃-era institutional register) → [../../../../docs/register-references/zh-tw-tianxia-structural-analytical.md](../../../../docs/register-references/zh-tw-tianxia-structural-analytical.md)
- **報導者 The Reporter** (center + investigative-extreme registers, non-profit journalism) → [../../../../docs/register-references/zh-tw-reporter-explanatory-journalism.md](../../../../docs/register-references/zh-tw-reporter-explanatory-journalism.md)
- **研之有物 Research @ Sinica** (institutional 科普 platform) → [../../../../docs/format-templates/zh-tw-research-sinica-popularization.md](../../../../docs/format-templates/zh-tw-research-sinica-popularization.md)

Strategy: select individual voice anchor cross-loaded from JP/EN Q1 + use institutional register reference for structural layer.

## Landmark: extreme

Moved out: 報導者 investigative-extreme register (consolidated with center entry above).

## Landmark: toward-Q2

(Gap flagged — future research: 龍應台 / 南方朔 essayist register candidates)

## Landmark: toward-Q4

**商業周刊 Business Weekly** (金惟純-era institutional strategy-imperative) → [../../../../docs/register-references/zh-tw-business-weekly-strategy-imperative.md](../../../../docs/register-references/zh-tw-business-weekly-strategy-imperative.md)

## Cross-references

Primary cross-load targets for Q1 zh-TW briefs:

- **JP Q1 STRONG** (direction-dominant): route to `anchor-jp-soseki-yoyu-ha-dry-observer.md` / `anchor-jp-itami-juzo-keimyou-shadatsu.md` + jp-q1 format-templates (天声人語 / 東洋経済) for structural register parallel
- **EN Q1 STRONG**: David Ogilvy (`anchor-en-david-ogilvy-*`) / Claude Hopkins (`anchor-en-claude-hopkins-*`) / George Orwell (`anchor-en-george-orwell-*`) / Amy Hempel spare-authority (`anchor-en-amy-hempel-*`) / Hemingway (`anchor-en-hemingway-*`)
- **Wire cross-ref**: Reuters JP + 中央社 wire-copy — format-templates layer for wire-service structural register

## Migration history

- **v1.0-v1.5.x**: aggregate with 5 inline entries (天下 + 報導者 x2 + 研之有物 + 商業周刊), all institutional
- **v1.6.0** (this file): all 5 moved to register-references/ + format-templates/; zh-TW Q1 individual-creator pool gap-flagged for v1.7.0+ research
