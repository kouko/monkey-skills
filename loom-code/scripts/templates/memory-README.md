# loom family practice-memory store

> The scaffold stamp above records which loom-code version minted
> this document. From that moment it is THIS repo's own file —
> it never syncs back to the plugin; edit it freely.

> Repo-native home for distilled loom-* practices, habits, processes,
> and recurring gotchas — knowledge not bound to a single commit that
> must travel with the repo (any machine, any host, headless agents).
> One fact per file, one file per entry. Stale facts should be
> deleted, not archived — git history is the archive.

## What belongs here, and what does not

Record a **distilled practice, habit, process, or recurring gotcha** —
something learned the hard way that should change how future work in
this repo is done. Do NOT record here:

- An open item, debt, or re-trigger condition — that belongs in
  `docs/loom/backlog/` (its own charter defines the entry format).
- A decision bound to a single commit — that belongs in the commit's
  own memory trailer (`Decision:` / `Learning:` / `Gotcha:`), not here.
- A one-off event artifact (a spec, a plan, an audit) — those live
  under `docs/loom/{specs,plans,audits}/`.

This store answers "what do we currently believe about how to work in
this repo" — a superseded fact should stop being read at all, which is
why it is deleted rather than archived.

## Format — one fact per file

Each entry is `<store>/<kebab-slug>.md`, with `---`-delimited
frontmatter:

```markdown
---
name: <kebab-slug — identical to the filename without .md>
description: <one line; the durable rule, used for relevance decisions
  at recall time before the file is opened>
type: practice | gotcha | process
origin: <PR / session / audit reference>
---

<the fact>

**Why:** <why the behavior matters>

**How to apply:** <the operative rule, readable standalone by a future
agent who never saw the work that produced it>
```

## §Index invariant

`## Index` below is a **generated section** — one line per entry,
`[<name>](<file>.md) — <description>`, where `<description>` must be
byte-identical to that entry's frontmatter `description` field. Never
hand-edit it. This invariant — plus "every body file has an index
line", "every index line points to an existing file", and "no
duplicate index lines" — is machine-enforced; run the checker from the
repo root:

```
python3 scripts/check_loom_memory_integrity.py           # validate every invariant
python3 scripts/check_loom_memory_integrity.py --write    # regenerate ## Index from body-file frontmatter
python3 scripts/check_loom_memory_integrity.py --check    # diff the committed index against a fresh regeneration
```

A hand-edit to `## Index` is drift and will be overwritten by
`--write`, and is detected as drift by `--check`. If the repo has no
repo-root `scripts/check_loom_memory_integrity.py` yet, the copy
shipped inside the loom-code plugin (beside this scaffold's own
`loom_init.py`) applies the same invariants.

## Index

_(empty — no entries yet)_
