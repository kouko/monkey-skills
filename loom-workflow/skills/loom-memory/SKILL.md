---
name: loom-memory
description: |
  Recall, Record, Reconcile, or Retire a durable repository lesson in the OKF v0.2-compatible loom-memory store. Use only when the user explicitly asks to remember, recall, forget, or reconcile repository knowledge ("記得這個坑", "之前是怎麼解的", "把這個教訓記下來", "這條還準嗎", "remember this", "what did we learn about X", "忘れないで"), or when you independently judge the current task needs a prior repository lesson. Works standalone or alongside loom-code / loom-design; neither requires it. For commit- or PR-bound decisions, learnings, and gotchas, use loom-workflow's git-memory instead.
---

# loom-memory

`loom-memory` is the one public surface over an OKF v0.2-compatible
repository memory store: a directory of Markdown concept files plus a
generated `index.md`, holding durable repository lessons that outlive any
single change. It exposes four operations — **Recall**, **Record**,
**Reconcile**, **Retire** — and nothing else. Validation and index
generation are implemented in
`${CLAUDE_PLUGIN_ROOT}/skills/loom-memory/scripts/loom_memory.py` (the
`skills/loom-memory/scripts/loom_memory.py` file inside this skill's own
directory); this skill is the only place that decides *when* and *how* to
call them.

This skill runs identically wherever agent skills and repository file
access are available. Nothing in this file or in the store schema depends
on a specific host's private path or API — Recall, Record, Reconcile,
Retire, and validation work the same whether or not any other plugin is
installed.

## Boundary against git-memory

`git-memory` owns commit- and pull-request-bound Decision, Learning, and
Gotcha carriers — captured at the moment of one change, retrieved through
`git log` and PR history. `loom-memory` owns repository lessons that
outlive a change: durable practices, habits, and recurring gotchas that
stay true after the commit that taught them is long gone. Neither skill is
a runtime dependency of the other, and content does not move automatically
between them — a commit-bound `Gotcha:` trailer is not itself a
`loom-memory` concept until someone deliberately records it as one.

## When this skill activates

Two triggers only, both passive:

1. **Explicit user request** — the user asks to remember, recall,
   reconcile, or retire repository knowledge, in any language.
2. **Independent agent judgement** — mid-task, the agent identifies a
   concrete need for prior repository experience (not a hunch, not a
   completeness ritual).

No other condition activates this skill. Reaching any particular point in
a workflow is not, by itself, a reason to invoke it — this skill has no
fixed-station calling convention and installs no gate on anyone else's
process.

## The four operations

### Recall

**Trigger:** explicit request, or the agent judges prior repository
experience is needed for the task at hand.

**Steps:**
1. Read `index.md` first. Never open every concept file — the index
   exists so an agent chooses without loading bodies.
2. Open only the bounded set of concept files whose index entry matches
   the need.
3. For each matching lesson, verify that any file, flag, skill, or command
   it names still exists before acting on it. A lesson that names a
   vanished file is stale evidence, not a fact to act on — say so.
4. An absent store or an empty result is a normal no-memory result, not an
   error. Report it plainly and continue the task.
5. A store with concept files but no `index.md` is structural corruption,
   not an empty result. Fail this recall explicitly and point the user at
   `${CLAUDE_PLUGIN_ROOT}/skills/loom-memory/scripts/loom_memory.py validate`
   (the `skills/loom-memory/scripts/loom_memory.py` file inside this
   skill's own directory) or the explicit migration operation — never read
   the concept files directly to work around a missing index.

### Record

**Trigger:** explicit request, or the agent judges a discovery is worth
keeping past this change.

**When:** before the branch closes. A fact already known while the branch
is still open — one that did not require the merge to observe — belongs in
that same branch, never a separate post-merge branch: a branch and a pull
request opened only to write down something already known is pure overhead
the close-out should have absorbed. The one exception is a fact only
confirmable by observing real post-merge or installed behavior; that
genuinely needs a follow-up branch, and those are batched rather than one
pull request per discovery. A lesson that surfaces only after a closing
review has spent its last reviewed content is the same case: it rides the
next change's branch batched, which is still not a branch opened to record.

**How much:** almost nothing qualifies. Most of what a change surfaces is
not a durable lesson — a one-off implementation slip belongs in its commit
message, a verification result belongs in the change's evidence, an
unfinished item belongs in an intent or a backlog entry. Zero to one
durable lesson per change is the normal outcome. The filter below judges
one candidate at a time, so it cannot see the other signal: wanting to
record eight things at once means the filter has not been applied yet.

**Steps:**
1. Classify the candidate first. It qualifies only as a durable repository
   lesson — not an open task, a change narrative, a verification record, a
   commit-bound decision (that belongs in `git-memory`), or a personal
   preference. When it fails this classification, do not record it; say
   why.
2. Read `index.md` and search for an equivalent or contradictory live
   entry before creating anything. A match routes to Reconcile instead.
3. Author exactly one concept file: frontmatter (`type`, `name` equal to
   the filename stem, `description`, at least one `sources[].resource`),
   followed by a body of `Trigger`, `Correct path`, `Why`, and `Limits`
   only when a real non-applicability boundary exists — see
   `references/okf-profile.md`.
4. Regenerate and validate the index with
   `${CLAUDE_PLUGIN_ROOT}/skills/loom-memory/scripts/loom_memory.py
   regenerate-index <store>` and `validate <store>` (that script is
   `skills/loom-memory/scripts/loom_memory.py` inside this skill's own
   directory).

### Reconcile

**Trigger:** a new lesson contradicts or narrows a current entry.

**Steps:**
1. Locate the current entry through `index.md`, never by guessing a
   filename.
2. Update that entry in place, or replace it with one current concept.
   Never create a second, contradictory sibling for the same subject.
3. Preserve every existing `sources[].resource` and add the new source
   rather than discarding provenance.
4. Regenerate and validate the index.

### Retire

**Trigger:** an entry is no longer true and has no current replacement
value.

**Steps:**
1. Name the entry and why it no longer holds.
2. Require explicit user approval before deleting anything — Retire never
   deletes on the agent's own judgement alone, unlike the other three
   operations.
3. On approval, delete the concept file. Git history is the archive; this
   store keeps no separate `log.md` change log.
4. Regenerate and validate the index after deletion.

## Failure behavior

A requested operation that finds malformed frontmatter, a missing
required field, duplicate concept identity, index drift, or a broken
index target stops with every offender named — never a first-match-only
report — and never installs another plugin or blocks unrelated work.

A store that turns out to be a legacy README-indexed store (no generated
`index.md`; concept files still shaped by the pre-OKF format) is reported
as needing an explicit migration, without modifying any file. This skill
never reads or writes that legacy format itself; migration is a separate,
explicit operation, never an implicit side effect of installation, session
start, Recall, or any other station.

## Resource map

- `references/okf-profile.md` — the OKF v0.2 compatibility clauses this
  store profile pins, the Loom minimum concept schema, the lesson body
  contract, and why `log.md` is omitted.
- `references/operations.md` — the full step-by-step procedure behind each
  operation above, including the Record classification filter and the
  Reconcile merge rule in detail.
- `${CLAUDE_PLUGIN_ROOT}/skills/loom-memory/scripts/loom_memory.py` (the
  `skills/loom-memory/scripts/loom_memory.py` file inside this skill's own
  directory) — `validate <store>` and `regenerate-index <store>`.
- `templates/memory-store-README.md` and `templates/memory-store-index.md`
  — the starting shape for a new store, instantiated as that store's
  `README.md` and `index.md`.

## License

MIT — see repository root `LICENSE`.
