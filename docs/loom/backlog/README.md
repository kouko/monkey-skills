# loom family backlog store

> Repo-native home for open items, debts, and re-trigger conditions
> that span the loom-* plugins — one entry per file. This is the
> format SSOT: derive the entry format from this file alone, without
> opening any other file.

## Frontmatter contract

Every entry (live or archived) carries this frontmatter, transcribed
verbatim from the plan that created this store:

```
---
name: <YYYY-MM-DD-slug — identical to the filename without .md>
description: <one line; what the item is>
status: <COMMITTED-NEXT | OPEN | PARKED | UPSTREAM | SHIPPED | CLOSED — SUPERSEDED | archived>
origin: <optional; where the item came from>
start: <optional; the start / re-trigger condition>
archived: <optional; required when status is archived — YYYY-MM-DD the entry was archived>
---
```

`archived` is stamped when an entry is closed (see the Archive rule
below) and is what the generated index's compact `## Archived` line
(`- <name> (archived <date>)`) reads its date from. It carries no
meaning on a live entry and must not be set on one.

Live entries — those directly under `docs/loom/backlog/`, excluding
`archive/` — carry any status **except** `archived`. Entries under
`docs/loom/backlog/archive/` carry `status: archived` and no other value.

**`description` never restates the status.** Write `description: the CI
lane drops coverage for foreign carrier files`, never `… (OPEN)`. The
status lives in the `status` field and nowhere else: a copy in the
description is a second source of truth that drifts the moment the entry
is reclassified, and the generated index already renders each entry under
its status heading. The same applies to the `name` slug — no `-open`,
no `-shipped` suffix.

## Closed status vocabulary

The `status` field is a closed enum — exactly these seven values, no
others:

- `COMMITTED-NEXT`
- `OPEN`
- `PARKED`
- `UPSTREAM`
- `SHIPPED`
- `CLOSED — SUPERSEDED`
- `archived`

The first six are live statuses. `archived` is reserved for entries
that have been closed and moved to `archive/` (see below) — a live
entry must never carry `status: archived`, and an archived entry must
never carry any other status.

## Filename rule

Each entry's filename is `YYYY-MM-DD-<slug>.md`, where the date is the
entry's creation date. **The filename is assigned once, when the entry
is created, and is never changed afterward** — not on a status change,
not on a description edit, and not when the entry is archived.
Archiving **moves** the file (see below); it does not rename it. The
filename is the entry's permanent identity, and the frontmatter `name`
field must always equal the filename with `.md` stripped.

## `docs/loom/BACKLOG.md` is generated — never hand-edit it

`docs/loom/BACKLOG.md` is **generated output**, produced by scanning
every entry file in this store and grouping them by status. It must
never be hand-edited: any change belongs in the entry file it was
generated from, followed by regenerating the index. A hand-edit to
`docs/loom/BACKLOG.md` is drift and will be overwritten (and is
detected as drift by the store's `--check` mode).

## Archive rule

Closing an entry means:

1. Move the entry file from `docs/loom/backlog/<name>.md` to
   `docs/loom/backlog/archive/<name>.md`.
2. Stamp `status: archived` into the moved file's frontmatter.
3. Stamp `archived: <YYYY-MM-DD>` (the archive date) into the same
   frontmatter — the generated index's `## Archived` line needs it and
   has no other source for it.

Archiving **never renames** the file (the filename rule above still
applies) and **never deletes** the file. The entry's full body and
history remain readable at its new path indefinitely.

### This differs deliberately from the memory store's policy

`docs/loom/memory/` (the loom family practice-memory store) deletes
stale facts outright and relies on git history as the archive — see
`docs/loom/memory/README.md`. **This backlog store does the opposite
on purpose**: it archives (moves + stamps), and never deletes. The two
stores answer different questions — memory asks "what do we currently
believe", where a superseded fact should stop being read at all, while
this backlog asks "what did we decide to do, and when did we close
it", where the closed item itself is the record. A reader of one
store's charter should not assume the other store's policy applies —
they are different, and that is intentional.
