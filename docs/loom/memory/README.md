---
name: README
description: This store's charter: one distilled loom-family lesson per file, the test for whether a fact belongs here rather than in an open intent, a commit trailer, or a one-off evidence record, and how to record, recall, and reconcile an entry; read before adding, editing, or retiring any concept in this store.
type: Memory Store Guide
sources:
  - resource: introducing commit 03d8312cbd557b6e8dfac69e551773ba228c770b
---

# loom family practice-memory store

> Repo-native home for distilled loom-* practices, habits, processes,
> and recurring gotchas — knowledge not bound to a single commit that
> must travel with the repo (any machine, any host, headless agents).
> One fact per file. Machine-local Claude memory keeps only pointers
> here — this folder is the durable truth (versioned, host-agnostic,
> greppable). Stale facts are deleted, not archived — git history is
> the archive.

## Charter — jurisdiction

| Knowledge shape | Home |
|---|---|
| Open item / debt / re-trigger | an intent file in `docs/loom/intent/` (the maintain station opens one, or appends evidence to the same-subject open intent) |
| Decision bound to a commit | git-memory trailers (`Decision:`) |
| Distilled practice / habit / process / recurring gotcha | **`docs/loom/memory/`** (this store) |
| One-off event artifact (audit, dogfood, measurement, review record) | `docs/loom/<change-id>/evidence/` when it belongs to one change; `docs/loom/evidence/` when it outlives the change |
| Harness/dcg friction (plugin-shipped) | `loom-code/.../environment-gotchas.md` — stays, NOT migrated |

> `docs/loom/backlog/` and `docs/loom/{plans,specs,design}/` are frozen at
> loom 1.0 (see `docs/loom/README.md` §Frozen stores). Nothing is written
> into them any more; a recurring open item comes back as a new intent.

> Durable lessons live in the repo's committed memory store
> (`docs/loom/memory/` here) — the authoritative carrier. Commit trailers are
> commit-bound capture: best-effort, secondary, and never the retrieval path
> a durable lesson depends on. This is why the "Decision bound to a commit"
> row above points at git-memory trailers for commit-bound capture only —
> not as a durable retrieval path.

## When to record

A fact already known before the branch closes (not merge-required to
observe) MUST land in that same branch/PR, never a separate post-merge
branch — a post-merge branch+PR just to record something you already
knew is pure overhead the close-out flow should have absorbed. The one
exception: a fact only confirmable by observing real post-merge/
installed behavior genuinely needs a follow-up branch — but even those
should be batched, not one-PR-per-discovery.

**Pull, not push.** Nothing auto-loads this folder. Retrieval = read
the index below / grep on demand. This preserves the documented
anti-preload decision (`dev-workflow/skills/git-memory/SKILL.md:193-197`);
evidence: a 2026 ETH Zurich study found always-loaded auto-generated
context files reduced agent task success by ~3% and raised inference
cost by ~20% (`dev-workflow/skills/git-memory/standards/memory-conventions.md`
§Pull retrieval).

Before acting on a recalled entry, verify any file/flag/skill it names
still exists — a memory reflects what was true when written, and a
named path may have been renamed or removed since.

Before recording, grep the store for entries the new fact contradicts —
on a hit, update or replace that entry (git history is the archive);
never add a contradicting sibling.

## Format — one fact per file

The file is named `<name>.md` — the frontmatter `name` slug IS the
filename, so index links never diverge from filenames.

```markdown
---
name: <kebab-slug>
description: <one-line — used for relevance decisions at pull time>
type: <free-text label, e.g. practice | gotcha | process | reference>
sources:
  - resource: <PR / session / audit reference, or "introducing commit <sha>">
---

<the fact>

**Why:** <why the behavior matters>

**How to apply:** <the operative rule, readable standalone>
```

`name`, `description`, `type`, and at least one `sources[].resource` are
required (the OKF v0.2-compatible Loom profile checked by
`loom-workflow/skills/loom-memory/scripts/loom_memory.py`); any other frontmatter key is
preserved as-is and never rejected.

**The `description` states the durable rule; it never states which tools
currently exist.**

**The test** — one question, applied clause by clause: *would this clause
become false if someone shipped, removed, or reconfigured a tool?* If yes,
it is body content. If no, it may stay.

- Fails the test, so belongs in the body: "X is not yet mechanised",
  "no script covers Z", "the check runs in CI but not in pytest",
  "mechanized in `<some-tool>`".
- Passes, so may stay: a permanent property of the method itself — "a
  proposition restated in synonyms is invisible to any string search" is
  true of string search, not of any particular script.

**Why the description and not the body.** The body can be corrected in the
same commit that changes the tooling, and the reader meets the correction
in context. The description cannot: `index.md` is generated from it
(`python3 loom-workflow/skills/loom-memory/scripts/loom_memory.py regenerate-index docs/loom/memory`),
it is the only text a pull-time grep surfaces before the file is opened, and
nothing mechanically compares it against the body. A
description asserting an open leak therefore outlives the commit that
closes the leak, and the recall surface goes on reporting the old world.

Recorded instance: an entry whose description presented a hard-wrap leak
as open while its own body stated the leak was mechanised — the store's
integrity checker exited 0 throughout, because byte-identity to the index
is the invariant it enforces, and truth against the body is not checkable
(`docs/loom/audits/2026-08-04-docs-review-convergence-experiment.md`).
`docs/loom/memory/measure-a-checks-fire-rate-before-building-it.md`
records why this is a format rule and not a detector.

**Binding: forward-only, and the store does not yet conform.** The rule
governs an entry when it is written and when its description is next
edited; it does not oblige a retrofit sweep. Fix a non-conforming
description on its next touch.

**`index.md` is generated — never hand-edit it.** Any change belongs in the
entry file's frontmatter, followed by regenerating the index (run from
the repo root):

```
python3 loom-workflow/skills/loom-memory/scripts/loom_memory.py validate docs/loom/memory            # validate every invariant, index drift included
python3 loom-workflow/skills/loom-memory/scripts/loom_memory.py regenerate-index docs/loom/memory    # rewrite index.md from every concept file's frontmatter
```

A hand-edit to `index.md` is drift: `validate` compares a fresh
regeneration against the committed file and fails on any difference, so a
lesson's frontmatter edited without regenerating the index is caught, not
silently stale.

If `regenerate-index` itself fails, its FAIL output names every offending
file and the reason (broken frontmatter, a `name` that does not match the
filename, a missing `description`) — fix those named problems first, then
repeat both commands above.
