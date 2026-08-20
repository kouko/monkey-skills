---
name: 2026-08-01-institution-maintenance-backlog-pointer
description: institution-maintenance.md §1 still says BACKLOG.md's header defines the entry format, which this arc made false
status: open
blocked: waiting on a human to review and approve the institution-maintenance.md diff
origin: docs-backlog-one-entry-per-file branch — the backlog-store-split arc that made the claim false
start: a human reviews and approves the diff to institution-maintenance.md
---

## What is now incorrect

The user's global rules file `institution-maintenance.md`, §1 ("Where
does a lesson go?"), item 2, says:

> **loom-family work practice/gotcha** → the repo's committed store
> `monkey-skills/docs/loom/memory/`; open follow-up items →
> `docs/loom/BACKLOG.md` (its header defines the entry format).

The parenthetical — "its header defines the entry format" — is false
as of this arc. `docs/loom/BACKLOG.md` is now **generated output**,
produced by scanning the per-entry files under `docs/loom/backlog/`
and grouping them by status. The format SSOT moved to
`docs/loom/backlog/README.md`; `BACKLOG.md`'s header no longer defines
anything and must never be hand-edited.

## Where

`institution-maintenance.md` §1, item 2, the parenthetical quoted
above. This file is **outside this repo** — its real path is
`~/dotfiles/claude/.claude/rules/institution-maintenance.md` (per its
own §2 edit-permission table; the `~/.claude/rules/` path is a
symlink). No branch of `monkey-skills` can fix it.

## Why this is REQUIRED, not optional, and why it is human-gated

This is a **REQUIRED** follow-up: leaving §1 as written misdirects any
future session that reads it toward a stale format contract (a
generated file's header) instead of the real one
(`docs/loom/backlog/README.md`).

It cannot be applied silently by a future agent. `institution-maintenance.md`
§2's own edit-permission table classifies `rules/*.md` rewrites —
this is a semantic correction to existing rule text, not a factual-drift
fix to a dead path or a renamed enum value — as requiring the user to
see a diff first. That table's `rules/*.md` row lists, in its
"requires showing the user a diff first" column:

> Rewriting/deleting any rule, merging rules, "simplifying" wording

(The two fragments are a table cell and its column header; they are
quoted separately here rather than spliced, because a spliced quote of
a table reads as one sentence the source never wrote.)

**What a future agent may and may not do.** May: draft the corrected
text, produce the diff, and surface it to the user for approval —
that is the workflow the edit-tier row describes, not an exception to
it. May not: land the edit, or treat silence as approval. The gate is
on *landing* the change, not on preparing it.

The fix itself: update the item-2 parenthetical to point at
`docs/loom/backlog/README.md` as the format SSOT instead of
`docs/loom/BACKLOG.md`'s header, then follow §3 of that same file
(cold-reader tax on any rules-file edit) before committing.
