---
title: Codebase Overview
type: overview
last_updated: TBD
seeded_from: TBD
---

# Codebase Overview

> This file is maintained by `/repo-wiki:init` and updated by
> `/repo-wiki:ingest` when architecture-level changes land.
> Do not edit by hand.

## Repository

<!-- one paragraph: pulled from README.md if present, otherwise derived
     from top-level directory structure during /repo-wiki:init -->

## All Modules

<!-- entity stubs created during /repo-wiki:init Phase 1 (src/ scan).
     Every detected module gets a stub. Listed in two groups by
     activity in the Phase 2 scan window (default 90d). -->

### Recently active (touched in scan window)

<!-- entries for modules that appeared in Phase 2 batches -->

### Stable (older history, still present in src/)

<!-- entries for modules that exist in src/ but had no commits in
     the Phase 2 scan window -->

## Recent Themes

<!-- 2-4 themes synthesized from Phase 2 source pages — what kinds of
     changes have been happening in the scan window -->

## What Lives Where

- `.repo-wiki/sources/` — change history (with WHY)
  - `YYYY-MM-DD-*.md` — Phase 2 batch pages (recent cross-module changes)
  - `era-YYYY-HX.md` — Phase 3 era pages (only if `init full-history` ran)
  - `*-manual-*.md` — captured via `/repo-wiki:ingest "<context>"`
  - `*-doc-*.md` — imported via `/repo-wiki:ingest "import doc: <path>"`
- `.repo-wiki/entities/` — module knowledge (skeletal stubs after init; fills via ingest)
- `.repo-wiki/concepts/` — patterns / ADRs (empty after init; grows via ingest)
- `.repo-wiki/syntheses/` — saved query answers (empty after init; grows via query)
