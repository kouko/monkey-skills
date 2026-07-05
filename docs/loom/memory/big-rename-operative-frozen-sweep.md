---
name: big-rename-operative-frozen-sweep
description: Big-rename recipe — split operative vs frozen references, regex look-behind guards for path collisions, git mv to preserve history, closing grep-guard for zero operative survivors
type: process
origin: PR #440 (loom suite rename, 2026-06-21)
---

Recipe for a large identifier/path rename across a repo, proven on
the 4-plugin loom suite rename (344 renames, CI 13/13):

1. **Split references into operative vs frozen.** Operative
   (README / SPEC / ROADMAP — anything a reader acts on today) gets
   repointed to the new name. Frozen (docs archive, CHANGELOG,
   research / ADR / announcement records) KEEPS the old ids — they
   are history, and rewriting them falsifies it.
2. **Guard path collisions with regex look-behinds.** Example: a
   `(?<!docs/)` look-behind protected the `docs/<plugin>` archive
   paths while the live plugin directories were being renamed.
3. **Move with `git mv`** so file history survives the rename.
4. **Close with a grep-guard:** search for the old name and require
   zero operative survivors (frozen hits are expected and fine).

Watch: an automated sweep can rewrite prose ABOUT the rename into
self-contradiction — one CHANGELOG line saying the docs archive "is
NOT renamed" got itself rewritten and had to be restored.

**Why:** without the operative/frozen split you either rewrite
history or leave live docs stale; without the closing grep-guard,
stragglers ship.

**How to apply:** before any repo-wide rename, classify reference
sites into the two buckets first, then sweep with guards, then run
the closing grep. Estimate the sweep cost by grepping the old name
BEFORE committing to the rename.
