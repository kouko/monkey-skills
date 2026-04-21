---
title: Voice Anchor Deep Dives — Layer 2/3 research artifacts
status: restored v1.6.1 (post-v1.6.0 undo-accidental-delete)
date: 2026-04-21
---

# Voice Anchor Deep Dives

**Purpose**: Layer 2/3 research artifacts per `docs/anchor-schema-v2.md`. Pass 3 does NOT load these files; they exist for audit / provenance / future deep-dive research expansion.

## Layer separation (per `anchor-schema-v2.md`)

| Layer | Location | Consumed by | Content |
|---|---|---|---|
| **Layer 1** (voice body) | `skills/copywriting-voice-tone-stage/standards/anchor-{slug}.md` | Pass 3 (hot path) | Voice direction / Native critical read / Prose mechanics / Examples / Don't / Metadata — the fields Pass 3 needs to rewrite a draft in this voice |
| **Layer 2/3** (research) | `docs/voice-anchor-deep-dives/{slug}.md` (this folder) | Audit / evaluator rationale (optional) / future researchers | Full research notes / primary source URLs & ISBNs / biographical & era context / awards timeline / critical history / documented lineage influences |

## Current state (v1.6.1)

All 64 files in this folder are **frozen snapshots** of the Layer 1 v2 entries at the time of v1.6.0 migration (commit `b9b1c39`, post-scaffolding-cleanup). They're identical in content to the corresponding `anchor-{slug}.md` files in `standards/` — but are **allowed to diverge over time** as Layer 2/3 research expands each entry:

- Biographical timeline
- Era context (surrounding cultural / political / market conditions)
- Full primary source bibliography beyond the critic citations already in `Native critical read`
- Awards / recognition history
- Documented lineage (who influenced whom, with specific interview / letter / academic citations)
- Critical-history debates (scholarly disputes about the register's boundary)

## Filename convention

Current (v1.6.1): `pilot-layer1-v2-{creator-slug}.md` (historical, preserved from v1.4-v1.5 pilot era).

Future (v1.7.0+): rename to `{trigger-slug}.md` (matching the Layer 1 anchor slug) as deep-dive research expands each entry — at that point the filename alignment makes audit tooling simpler.

## How to use this folder

- **Pass 3**: MUST NOT load. Layer 1 at `standards/anchor-{slug}.md` is the only Pass 3 source.
- **Dimension 6 evaluator** (voice-consistency-gate): MAY optionally cite a deep-dive entry in rationale when over-mimic judgment requires biographical / era / lineage context that Layer 1 does not carry.
- **Human researchers**: expand any entry with new biographical / era / lineage findings as research progresses. Keep the filename stable even if Layer 1 slug changes (or sync — pick one discipline).
- **Commit discipline**: Layer 1 anchor updates and Layer 2/3 deep-dive updates are **independent commits** — do not conflate them. Layer 1 changes are production-facing (Pass 3 behavior); Layer 2/3 changes are audit-facing.

## Accidental delete history (v1.6.0 → v1.6.1)

v1.6.0 migration accidentally removed this folder (and 64 files) when the pilot files were `git mv`'d into `standards/`. The intent was to move Layer 1 bodies out of pilot location, but the Layer 2/3 **seed material** and the folder itself were meant to stay. v1.6.1 restores all 64 files verbatim from commit `b9b1c39` (pre-delete snapshot).

The files are now **seed material** for future Layer 2/3 research. No deep-dive research has been done yet — every file currently holds only the Layer 1 schema. That's the starting point; not the end state.
