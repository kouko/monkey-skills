---
title: Register References — movement / documented-campaign / publication registers
schema_version: v2.0
status: Phase C holding folder (v1.5.0)
date: 2026-04-21
---

# Register References

**Purpose**: hold register / campaign / movement descriptions that do NOT qualify as Layer 1 voice anchors under v2 inclusion criterion (individual creator with identifiable sentence-level register), but remain valuable as **mitigation references** — "what NOT to copy" signals for Dimension 6 (voice-consistency-gate) and Dimension 7 (thesis-alignment-gate).

## Why these entries are here, not in the voice library

Per `docs/anchor-schema-v2.md` §Boundary: documented movements:

> These remain cited in meta-core over-mimic registry as mitigation references but are NOT voice anchors. They inform what NOT to copy; they don't qualify as what TO copy.

Register references differ from format templates (`../format-templates/`):
- **Format templates** = institutional / platform / IP producing a reusable structural format (Reuters headlines, Amazon product copy, 天声人語 column beats)
- **Register references** = documented movements / famous campaigns / editorial voices that are influential enough to leak into drafts as anti-patterns but have no single author-voice to load

## What belongs here

- **Documented movements** with civic-declarative or manifesto registers (XR Declaration / Extinction Rebellion, Occupy Wall Street declarations) — influence-rich but rotating authors, and the register is the movement's, not any individual's
- **Magazine institutional voices** where the publication's house style is so specific it functions as a mitigation reference even though individual editors have rotated (Economist brand voice, 天下雜誌 CommonWealth era-voice, 商業周刊, 報導者 investigative register)
- **Campaign-level entries** where a single creator genuinely cannot be isolated because the register emerged from team consensus (certain Nike "Dream Crazy / Crazier" executions where multiple CWs rotated)

## How to use this folder

- **Pass 3 does NOT load these files as voice anchors.** Dimension 6 operates only over Layer 1 entries in `standards/*-anchors.md`.
- **Over-mimic registry may cite these as mitigation sources** — "the draft is drifting toward XR-Declaration civic-declarative cadence; re-anchor to {selected Layer 1 voice anchor}".
- **Phase 6 Pass 3 lineage load** may optionally reference these as "neighboring registers to distinguish against".

## Migration status

Phase C (v1.5.0) creates this folder. Entry-by-entry migration from v1 `standards/*-anchors.md` is progressive.

**Entries slated to move here** (per `docs/voice-library-recast-audit.md`):
- XR Declaration / Extinction Rebellion civic-declarative (EN Q2 mitigation-only)
- Economist brand voice (EN Q1 institutional)
- 天下雜誌 CommonWealth (zh-TW Q1 institutional — 殷允芃 era note preserved)
- 商業周刊 Business Weekly (zh-TW Q1 institutional — 金惟純 era note preserved)
- 報導者 The Reporter investigative / center (zh-TW Q1 institutional)
- Nike "Dream Crazy / Crazier" (EN Q2 — campaign register with no isolable single CW)

## Relationship to other skill layers

- **Voice library proper** (`standards/*-anchors.md`) = Layer 1 individual creators
- **Register references** (this folder) = influence-rich documented registers that rotate authorship
- **Format templates** (`../format-templates/`) = institutional / platform / IP producing structural formats
- **Voice anchor deep dives** (`../voice-anchor-deep-dives/`) = Layer 2/3 research artifacts for Layer 1 entries

## Important: mitigation-only

If a brief sounds XR-Declaration-like, Economist-like, or 報導者-like, the skill MUST:
1. Select a Layer 1 individual-creator voice anchor whose register is adjacent
2. Cite the register-reference as anti-pattern mitigation ("avoid collapsing into XR-Declaration cadence")
3. NOT attempt to "apply the register-reference" as if it were a voice

Loading a register-reference as voice anchor would pull the draft toward a movement-cadence with no verifiable individual voice underneath — the drift LLM over-mimic registry is designed to catch.
