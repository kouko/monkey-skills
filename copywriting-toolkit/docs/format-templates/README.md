---
title: Format Templates — institutional / platform / IP registers
schema_version: v2.0
status: Phase C holding folder (v1.5.0)
date: 2026-04-21
---

# Format Templates

**Purpose**: hold register / format / protocol descriptions for entities that do NOT qualify as Layer 1 voice anchors under v2 inclusion criterion (individual creator with identifiable sentence-level register). These are still valuable references — Pass 3 and Phase 8 form-check may consult them — but they are NOT loaded as voice anchors.

## Why these entries are here, not in the voice library

Per `docs/anchor-schema-v2.md` §Inclusion criterion:

> An entity qualifies as a voice anchor IF AND ONLY IF it is an individual creator whose sentence-level register is identifiable across a body of work.

The entries in this folder are:
- **Magazines / newspapers / wire services** with rotating authors (天声人語, 東洋経済, 日経ビジネス, Reuters JP, 日経社説, 通販生活)
- **Institutional platforms / SNS / IP mascots** (研之有物, 故宮粉絲團「朕知道了」小編, 7-ELEVEN OPEN 將, 全聯 SNS post-2020, ワークマン SNS, クックパッド つくれぽ)
- **E-commerce platforms** with distributed copy authorship (PChome, MOMO, Shopee 蝦皮, Pinkoi)
- **Brand institutional voices** without a single named author at the register-defining moment (Amazon product copy, REI expert-advice, IKEA assembly voice)

Voice emerges from a consistent sentence-level sensibility exercised repeatedly by one hand. Institutional / platform / IP entities produce **a FORMAT, a PROTOCOL, or a TEMPLATE** — rotating authors converge on house-style rules rather than expressing a single author's voice.

## How to use this folder

- **Pass 3 does NOT load these files as voice anchors.** Voice consistency (Dimension 6) and Thesis alignment (Dimension 7) of `voice-consistency-gate.md` operate only over Layer 1 entries.
- **Phase 8 form-check (8a) may reference these as format templates** for platform-specific conventions (e-commerce product copy beats / wire-service headline length / SNS IP mascot register).
- **Audit / evaluator may cite these** for "this piece is imitating a platform-format template, not a voice register — re-direct to platform-copy skill" style rationale.

## Relationship to existing Phase 8 form standards

Phase 8's `form-appropriate-standards.md` covers abstract form conventions (long-form PASONA vs mid-form vs short-form catchcopy). This folder is **narrower**: specific platform / publication / IP templates with their own conventions.

## Migration status

Phase C (v1.5.0) creates this folder. Entry-by-entry migration from v1 `standards/*-anchors.md` is progressive — entries move here as Phase D refactors each `-anchors.md` file to v2 schema.

**Entries slated to move here** (per `docs/voice-library-recast-audit.md`):
- 朝日新聞「天声人語」, 東洋経済, 日経ビジネス, Reuters JP, 日経新聞社説 / 春秋, 通販生活 (JP magazine/wire institutional)
- クックパッド つくれぽ文化, ワークマン SNS era (JP platform)
- 研之有物, 故宮粉絲團「朕知道了」小編 (zh-TW institutional SNS/platform)
- PChome / MOMO 購物專家, 7-ELEVEN OPEN 將, 全聯 SNS post-2020, Shopee 雙11, Pinkoi 商品故事 (zh-TW platform/IP)
- WebMD / Reuters / Bloomberg wire institutional, Amazon product copy, REI expert-advice, IKEA assembly voice (EN institutional)

## Important: not a voice register source

If a brief lands in this folder's territory, the skill routes to:
1. **Form appropriateness** (Phase 8 8a) — the template's structural conventions
2. **Tone** — derived from the brand's brief or a named-individual voice anchor selected separately

Never "apply Amazon product copy as voice register" — Amazon's register IS the product copy template. Use the template for structure; choose a voice anchor separately from Layer 1.
