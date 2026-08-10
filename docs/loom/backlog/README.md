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

## The body below the frontmatter is freeform — with one exception

Below the frontmatter, write whatever the item needs — prose,
headings, bullets, a quoted excerpt — with no required sections and no
fixed order. This is deliberate: the store holds heterogeneous items
(a pointer to a fix that lives elsewhere, a self-contained debt, a
re-trigger condition), and a fixed section schema would over-constrain
content that legitimately varies.

**The one exception, machine-enforced by `scripts/backlog_index.py
--validate`:** if the body repeats `Origin` or `Start` as a top-level
bullet — the *label* may vary (`- Origin: …`, `- **Origin**: …`,
`- Start (re-trigger): …`, or a similar parenthetical-qualifier on the
label) — **and** the frontmatter also carries the matching
`origin`/`start` field, the two must agree after whitespace
normalization (line wraps and indentation collapsed to single
spaces). A qualifier written *after* the colon is part of the value,
not the label, and is compared as part of it.

The captured value runs from after the label to the first of: a blank
line, a line starting with `- ` at column 0, or end of text. A wrapped
bullet — indented continuation lines, no blank line before the next
bullet — still captures in full. Prose or a heading placed directly
after the bullet with **no** blank line between them is captured too,
which means it is compared against the frontmatter field as if it were
part of the value — so a bullet that agrees with its twin word for word
still fails. Put a blank line between the bullet and whatever follows.

A bullet that disagrees with its frontmatter twin fails `--validate`
with a `[field-agreement]` violation. This fires **only when both
copies exist**: a body with no such bullet is untouched by this rule,
and so is a bullet naming any field other than `Origin`/`Start`. If an
entry doesn't need the constraint, don't restate `Origin`/`Start` as a
labelled bullet at all — fold the same information into ordinary
prose instead.

The one standard the body must meet otherwise is a **retrieval**
standard, not a shape one: a future agent who finds this entry by grep,
has never seen the work that produced it, and has no access to any plan
must be able to act on it. State what the item is, why it matters, and
what the next step is, inside the entry itself. Do not write a body
that only makes sense to someone who already knows the context.

## Closed status vocabulary

The `status` field is a closed enum — exactly these seven values, no
others. Pick by what is *blocking the item*, not by how important it
feels:

- `COMMITTED-NEXT` — decided, scheduled, and active/claimed for the
  parallel set. Nothing is blocking it but our own turn to start. When
  `docs/loom/DIRECTION.md` exists, this queue is mirrored into its
  generated `## Now` section by `scripts/backlog_index.py
  --direction-write` (see §Verbs' Bet flow). This is a PARALLEL ACTIVE
  SET, not a serial queue: one entry typically maps to one
  worktree/lane, and the ≤5 cap is parallel-steering capacity. See
  `docs/loom/DIRECTION.md`'s charter header — the convention's SSOT.
- `OPEN` — agreed to be worth doing, not yet scheduled. Anyone may
  pick it up.
- `PARKED` — deliberately not being done for now, with the reason
  recorded in the body. Distinct from `OPEN`: a parked item needs a
  condition to change before it is eligible again, which is what
  `start:` records.
- `UPSTREAM` — the fix belongs to something this repo does not own (an
  external tool, another project, a file outside this repo). We can
  describe and track it here; we cannot land it here.
- `SHIPPED` — the work is done and merged, but the entry is being kept
  live deliberately, usually because a follow-up or measurement is
  still attached to it. An entry with nothing left attached should be
  archived instead.
- `CLOSED — SUPERSEDED` — no longer applicable because a later
  decision replaced it. The body should name what superseded it.
- `archived` — closed and moved to `archive/`; see the Archive rule
  below. Never used on a live entry.

The first six are live statuses. `archived` is reserved for entries
that have been closed and moved to `archive/` (see below) — a live
entry must never carry `status: archived`, and an archived entry must
never carry any other status.

## Verbs

Four flows read, close, or promote items in this store; everything
else only writes it.

- **Ready query** — `python3 scripts/backlog_index.py --ready` is the
  store's read surface: it prints the `COMMITTED-NEXT` queue (the
  "now" queue, file-date order — a listing order, not an execution
  order; store policy — not enforced by the tool — keep it to ≤5
  entries: a sixth commitment means re-judging the queue) followed by
  `OPEN` candidates with their `start:` conditions. The script path
  resolves per the generated-index section below (repo-root first,
  else the loom-code plugin copy).
- **Close duty** — `finishing-a-development-branch`'s Step 8
  Backlog-close check flips a shipped or superseded entry's status at
  branch close-out. The procedure lives in that skill, not here —
  follow it there rather than reconstructing it from this charter.
  The flip is a way-station, not the terminus — entries with nothing
  left attached still batch into the Archive rule's physical move
  later.
- **Kickoff read** — `brainstorming`'s Axis 0 Backlog ready check runs
  the ready query at arc kickoff, so the queue informs new work.
- **Bet (promote)** — promoting a backlog entry into `COMMITTED-NEXT`
  is **user-only**; agents never promote. Triggered by
  `finishing-a-development-branch`'s close-out when that close-out
  flips a backlog entry (the duty lives in its Backlog-close row), the
  `COMMITTED-NEXT` queue is empty after the flip, and the repo has
  `docs/loom/DIRECTION.md` — or manually at any time. Candidates: the
  active roadmap entries' next arcs first (same-lane first — when an
  arc of theme X just closed, theme X's next arc leads the list), then
  the ready query's `OPEN` output. To promote, the user edits the
  chosen entry's `status:` to `COMMITTED-NEXT`; `--write` and
  `--direction-write` then regenerate `BACKLOG.md` and DIRECTION.md's
  `## Now` from it. Those flags belong to the same script, resolved per
  the generated-index section below (repo-root first, else the
  loom-code plugin copy).

## Roadmap entries — a named pattern, not a new file type

A **roadmap entry** is an ordinary backlog entry whose body is an
ordered arc list with dependency notes, serving one DIRECTION theme —
not a new file type, not a DIRECTION section. `docs/loom/DIRECTION.md`'s
`## Next` lines may point at one by filename (the filename's date
prefix is a file identifier, exempt from DIRECTION.md's no-dates
rule). As each arc ships, its evidence line accumulates in the entry's
body rather than opening a new entry per arc. Precedent for the shape
(not the cadence — per-arc
evidence accumulation is the prescription going forward):
`2026-08-07-execute-complexity-audit-keep-lanes.md` held one theme's
ordered arc list with dependency notes across five PRs, its body
revised arc by arc as the plan reshaped, with the SHIPPED evidence for
all five arcs recorded together at close.

## Filename rule

Each entry's filename is `YYYY-MM-DD-<slug>.md`, where the date is the
entry's creation date. **The filename is assigned once, when the entry
is created, and is never changed afterward** — not on a status change,
not on a description edit, and not when the entry is archived.
Archiving **moves** the file (see below); it does not rename it. The
filename is the entry's permanent identity, and the frontmatter `name`
field must always equal the filename with `.md` stripped.

**`<slug>` derivation (ONE-WAY DOOR — nothing validates this, the
author is the only check):** lowercase; replace each run of
non-alphanumeric characters with a single `-`; strip any leading or
trailing `-`; ASCII only, no CJK or other non-ASCII characters; cap the
result at **72 characters**. Because the filename can never change,
getting the slug wrong (too long, wrong casing, non-ASCII) is an
unrecoverable identity defect on that entry — there is no script that
rejects a malformed slug, so authoring it correctly is entirely on the
author.

## `docs/loom/BACKLOG.md` is generated — never hand-edit it

`docs/loom/BACKLOG.md` is **generated output**, produced by scanning
every entry file in this store and grouping them by status. It must
never be hand-edited: any change belongs in the entry file it was
generated from, followed by regenerating the index with
`scripts/backlog_index.py`, the store's generator/validator script
(run from the repo root). The script resolves two-tier: use the
repo-root `scripts/backlog_index.py` when it exists; otherwise run the
copy shipped inside the loom-code plugin
(`loom-code/scripts/backlog_index.py` in this repo). The commands:

```
python3 scripts/backlog_index.py --validate   # check every entry's frontmatter invariants
python3 scripts/backlog_index.py --write      # regenerate docs/loom/BACKLOG.md from the entry files
python3 scripts/backlog_index.py --check      # regenerate in memory and diff against the committed index; exits 1 on drift
```

A hand-edit to `docs/loom/BACKLOG.md` is drift and will be overwritten
by `--write`, and is detected as drift by `--check` (the mode CI runs).

## Archive rule

Close an entry with `loom-code/scripts/archive_change_folder.py`, not a
hand `mv` — the script validates every path before touching the
filesystem and rolls back on a stamp failure, which a manual move does
not:

```
python3 loom-code/scripts/archive_change_folder.py <identifier> [root] [--date YYYY-MM-DD] [--unit folder|file]
```

For a backlog entry, `--unit file` and `<identifier>` is the entry's
filename including `.md` (e.g. `2026-08-01-example-entry.md`).

Under the hood, closing an entry means:

1. Move the entry file from `docs/loom/backlog/<name>.md` to
   `docs/loom/backlog/archive/<name>.md`.
2. Stamp `status: archived` into the moved file's frontmatter.
3. Stamp `archived: <YYYY-MM-DD>` (the archive date) into the same
   frontmatter — the generated index's `## Archived` line needs it and
   has no other source for it.

Knowing these three steps lets you verify the script's result; it is
not an invitation to perform them by hand. Archiving **never renames**
the file (the filename rule above still applies) and **never deletes**
the file. The entry's full body and history remain readable at its new
path indefinitely.

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
