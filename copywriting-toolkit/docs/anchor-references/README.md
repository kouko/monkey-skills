---
title: Anchor References — non-Layer-1 registers (format templates + register references)
schema_version: v2.0
status: consolidated in v1.13.1 (merged from former docs/format-templates/ + docs/register-references/)
date: 2026-04-22
---

# Anchor References

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

**Purpose**: hold register / format / movement descriptions that do NOT qualify as Layer 1 voice anchors under v2 inclusion criterion (individual creator with identifiable sentence-level register). These remain valuable — Pass 3 over-mimic registry cites some as mitigation-only; Phase 8 form-check may consult others as format conventions — but they are NOT loaded as voice anchors.

**Consolidated in v1.13.1** from former `docs/format-templates/` + `docs/register-references/`. Both folders held non-Layer-1 references with overlapping purposes; single folder reduces navigation overhead.

## Two categories of entries

### Format templates (`jp-*`, `en-*`, `zh-tw-*-platforms-*`, `zh-tw-*-institutional-*`)

Institutional / platform / IP entities producing a reusable structural format. Examples:
- **Magazines / newspapers / wire services** with rotating authors (天声人語 / 東洋経済 / Reuters JP / 日経社説)
- **Institutional platforms / SNS / IP mascots** (研之有物 / 故宮粉絲團 / 全聯 SNS / クックパッド つくれぽ / ワークマン SNS)
- **E-commerce platforms** with distributed authorship (Shopee 雙11 / PChome / MOMO / Pinkoi)
- **Brand institutional voices** without a single named author at the register-defining moment (Amazon product copy / REI expert-advice / IKEA assembly voice)

Voice emerges from a consistent sentence-level sensibility exercised repeatedly by one hand. These entities produce **a FORMAT, a PROTOCOL, or a TEMPLATE** — rotating authors converge on house-style rules rather than expressing a single author's voice.

### Register references (movement-level / campaign-level / publication-era)

Documented movements / famous campaigns / editorial voices that are influential enough to leak into drafts as anti-patterns but have no single author-voice to load. Examples:
- **Documented movements** with civic-declarative or manifesto registers (XR Declaration / Occupy declarations)
- **Publication institutional voices** where house style functions as mitigation reference despite rotating editors (Economist brand voice / 天下雜誌 / 商業周刊 / 報導者)
- **Campaign-level entries** where register emerged from team consensus (certain Nike "Dream Crazy" executions with rotating CWs)

The distinction between format-template and register-reference is soft — both are non-Layer-1, both serve downstream gates rather than Pass 3 voice selection. Entries are filed by primary lens (structural format vs documented movement) but the folder as a whole is a single "non-anchor references" bucket.

## How Pass 3 and gates use this folder

- **Pass 3 does NOT load these files as voice anchors.** Voice Consistency (Dimension 6) and Thesis Alignment (Dimension 7) of `voice-consistency-gate.md` operate only over Layer 1 entries in `standards/anchor-*.md`.
- **Over-mimic registry in `voice-anchor-meta.md §Over-mimic mitigation fallback registry`** cites some entries here as mitigation sources — e.g., "XR Declaration civic-declarative register ONLY; NOT for commercial product copy".
- **Phase 8 form-check (8a)** may reference format templates for platform-specific conventions (e-commerce product copy beats / wire-service headline length / SNS IP mascot register).
- **Audit / evaluator** may cite these as "the draft is imitating a platform-format template or a civic-movement cadence, not a voice register — re-anchor or re-direct" style rationale.

## Relationship to other skill layers

- **Voice library proper** (`standards/anchor-*.md`) — Layer 1 individual-creator voice anchors (80+ entries). Pass 3 loads from here.
- **Anchor references** (this folder) — non-Layer-1: format templates + register references. Mitigation-only / form-convention-only.
- **Voice anchor notes** (`../voice-anchor-notes/`) — Layer 2/3 research artifacts for Layer 1 entries + rejected-candidate research trails.

## Important: not a voice register source

If a brief lands in this folder's territory, the skill routes to:
1. **Form appropriateness** (Phase 8 8a) — the template's structural conventions, if format-template
2. **Over-mimic mitigation** (Dimension 6) — cite as anti-pattern if register-reference
3. **Tone** — derived from the brand's brief or a named-individual voice anchor selected separately from Layer 1

Never "apply Amazon product copy as voice register" — Amazon's register IS the product copy template. Use the template for structure; choose a voice anchor separately from Layer 1. Same for "apply XR Declaration as voice" — that's a mitigation warning, not a source.

## Migration status

Phase C (v1.5.0) originally created `docs/format-templates/` + `docs/register-references/` as separate folders. v1.13.1 consolidates both into `docs/anchor-references/` — same content, single navigation target.

**Entry-by-entry migration from v1 `standards/*-anchors.md` to this folder**: progressive per `docs/voice-library-recast-audit.md`. Entries that clearly map to format-template (rotating authors producing a house style) or register-reference (movement or publication-era) land here; entries that represent an individual creator's sentence-level register go to `standards/anchor-{slug}.md` as Layer 1.
