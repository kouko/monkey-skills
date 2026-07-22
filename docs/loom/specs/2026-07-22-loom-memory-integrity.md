# Brief — loom-memory store integrity (F1 + F4)

Upstream artifact: loom-memory design review (this session; notes at `scratchpad/loom-memory-design-review.md`).
Stage: brainstorming brief → `writing-plans`. Date: 2026-07-22.

## Design-side on-ramp

N/A — hardening increment over the existing loom-memory store + skill (bug-fix/refactor class). Axis-0 negative guard applies; no product-principles/design/spec station precedes it.

## Problem

(JTBD — committed read) The loom-memory store's integrity invariants — every body file has an index line, `filename == frontmatter name`, `index-line description == frontmatter description` byte-for-byte — are **enforced only by prose** ("re-verify before done", SKILL.md:67-70 / README.md:71-75). Prose enforcement has **already drifted**: 2 body files (`ixbrl-dom-traversal-drops-nested-facts.md`, `market-canonical-must-satisfy-consumer-field-contract.md`) landed via PR #592 with no index line, and nothing caught it. Separately, recall surfaces entries verbatim with no "verify it still holds" caveat, so an agent can act on a memory that names a since-renamed file/flag/skill. This is the same "prose invariant, no mechanical guard" disease the 2026-07-20 gate-hardening branch just fixed elsewhere — applied to the memory store itself.

## Users

- The loom-family maintainer (this repo) + any agent running loom-memory record/recall.
- Failure already realized (PR #592 orphans); recall silently returns an incomplete index and gives no staleness warning.

## Smallest End State

1. **F1 — a mechanical store-integrity checker** (`scripts/check_loom_memory_integrity.py`, Python stdlib, following the `scripts/check_version_bump.py` pattern) with a test, that fails loud and NAMES the offender on any of: (a) a body file with no index line in README §Index; (b) an index line pointing to a missing file; (c) `filename != frontmatter name`; (d) `index description != frontmatter description` (byte-identical). Wired into CI as a job. **Backfill** the 2 orphan index lines so the check passes.
2. **F4 — a staleness caveat**: one line added to the loom-memory recall procedure (`loom-pipeline/skills/loom-memory/SKILL.md`) and the store charter (`docs/loom/memory/README.md`): before acting on a recalled entry, verify any file/flag/skill it names still exists (mirrors the auto-memory protocol's existing warning).

The checker is validate-only (fail-loud + name), NOT auto-fix — the same read-only-gate posture as `check_version_bump.py`.

## Current State Evidence

- **Forward (control flow / how it's checked today):** nothing — the invariants live in prose (`docs/loom/memory/README.md:71-75` "re-verify the two invariants"; `loom-pipeline/skills/loom-memory/SKILL.md:67-70` record step 5). No script or CI validates the store.
- **Reverse (SSOT):** the store `docs/loom/memory/*.md` is SSOT for the fact; the README §Index (line 70+) is a byte-copied `description` pointer to each file's frontmatter (README owns no independent description — SSOT is the file frontmatter). Index line format: `[name](name.md) — <description>`. Frontmatter fields: `name` / `description` / `type` / `origin`.
- **Error:** the checker must fail-closed (nonzero exit) and print each offending file + which invariant broke; it must not auto-mutate the store.
- **Data:** 81 body files, README index ~33.2 KB; 2 confirmed orphans (verified this session).
- **Boundary:** new `scripts/check_loom_memory_integrity.py` + its CI job; edits to `docs/loom/memory/README.md` (backfill 2 index lines + F4 caveat) and `loom-pipeline/skills/loom-memory/SKILL.md` (F4 caveat).

Evidence paths: `docs/loom/memory/README.md`, `loom-pipeline/skills/loom-memory/SKILL.md`, `scripts/check_version_bump.py` (checker+CI pattern to follow), `.github/workflows/` (job wiring).

## Decision

Build a read-only store-integrity checker (`scripts/check_loom_memory_integrity.py` + test, RED-first) validating the four invariants, wire it into CI, backfill the 2 orphan index lines, and add the F4 staleness caveat to the skill + charter. Follow `check_version_bump.py`'s validate-only-fail-loud convention (no auto-fix). `loom-pipeline/skills/loom-memory/SKILL.md` is plugin-shipped → bump loom-pipeline (0.10.0 → 0.11.0). The checker + README + CI are repo-local.

We will NOT: build size governance / graduation (F2), a semantic/embedding recall (F3), a prune trigger (F5), or mirror-hook verification (F6) — those are DEFERRED per the evaluation (slow-burn or hard-to-mechanize; F4 already covers most of F5's harm).

## Out of Scope (per the F1~F6 evaluation)

- F2 size governance, F3 semantic recall, F5 prune trigger, F6 mirror-hook verification — deferred (revisit at ~150 entries or on a real recall miss). Optionally a cheap F3 "try alternate keyword angles" recall nudge, but not this branch.

## Alternatives Considered (Axis 4)

No industry-research fork — this follows the repo's own established pattern (`check_version_bump.py`: a repo-root `scripts/` Python validator + a CI job, validate-only, fail-loud, names the offender). The one WHERE choice — checker in repo-root `scripts/` vs `loom-pipeline/scripts/` — resolved to **repo-root `scripts/`** because the store it validates (`docs/loom/memory/`) is repo-level, not inside the loom-pipeline plugin dir, matching `check_version_bump.py`'s placement.

## What Becomes Obsolete

The prose "re-verify the two invariants before done" (README.md:71-75, SKILL.md:67-70) stays as the human-readable statement but is no longer the *enforcer* — CI is. Do not delete the prose (it explains intent); the check makes it binding.

## Open Questions

None blocking. (CI wiring detail — new workflow vs a job in an existing loom workflow — resolved in planning by reading the existing workflow structure.)
