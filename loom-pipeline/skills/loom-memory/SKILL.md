---
name: loom-memory
# firing-evidence: 2026-07-14 baseline 4/4 EXACT (docs/skill-dogfood/2026-07-14-description-token-economy/baseline.md)
description: >-
  Record, recall, or prune the repo-native loom practice-memory store
  (`docs/loom/memory/`) — save a distilled lesson/gotcha, check prior
  experience before loom work, or propose keep/merge/retire cleanup
  (never auto-deletes). CONDITIONAL: fires only when the repo has
  `docs/loom/memory/README.md` — otherwise `loom-memory: N/A` with the
  reason, loudly. NOT for git commit trailers (dev-workflow:git-memory)
  nor Claude auto-memory. Triggers: "有沒有相關經驗", "記住這個做法",
  "記憶整理", "この教訓を残して", "過去の知見はある？".
version: 0.2.0
---

# loom-memory — record / recall / prune for the practice-memory store

Three verbs over one store. This skill executes the store's charter —
it never redefines it.

## When it fires — N/A-loud gate

**Condition: the target repo has `docs/loom/memory/README.md`** (the
store charter).

Missing → emit **`loom-memory: N/A (no docs/loom/memory/README.md in
this repo)`** and stop. N/A is a first-class honest outcome — never
silently skip, never scaffold a store on the fly to make the verb
"work", and never improvise an equivalent from machine-local memory.
Creating a store is a deliberate, separate act by the user.

## SSOT — point, never copy

The charter (`docs/loom/memory/README.md`) owns the jurisdiction
table, the one-fact-per-file format spec, the index-line format, and
the pull-not-push retrieval policy. Every verb below **reads the
charter at execution time** and follows what it finds there. Do not
reproduce the charter's table rows or format fence in this skill, in
prompts, or in dispatch payloads — a copy drifts; the pointer never
does. If this skill's summary ever disagrees with the charter, the
charter wins.

## record

Given a fact worth keeping:

1. **Classify against the charter's jurisdiction table** (read it
   first). Not everything belongs in the store — e.g. a backlog-shaped
   item (open item / debt / re-trigger) routes to `docs/loom/BACKLOG.md`,
   and harness/dcg friction routes to the loom-code plugin-shipped
   gotchas reference. Everything else: classify per the charter's
   jurisdiction table (read it — it wins). Tell the user where you
   routed the fact and why.
2. **Check the store for contradictions.** Before writing, grep the
   store — the index and the file bodies — for entries the new fact
   contradicts. On a hit, update or replace that entry (delete and
   rewrite it; git history is the archive) instead of adding a
   contradicting sibling, and note the replacement in the index line.
   This mirrors git-memory's backward-pointing `Supersedes:` doctrine
   (`dev-workflow/skills/git-memory/standards/memory-conventions.md`)
   — point at it, don't copy its table (SSOT above).
3. **Write `<slug>.md`** in `docs/loom/memory/` following the
   charter's format block exactly (frontmatter fields, body sections).
4. **Append the index line** in the charter's index format, with the
   description copied **byte-identical** from the file's frontmatter
   `description`.
5. **Re-verify the two invariants** before declaring done:
   - filename (minus `.md`) equals the frontmatter `name` slug;
   - the index line's description equals the frontmatter
     `description`, byte for byte.

   A mismatch is a fail-loud fix-now, not a note.

## recall

Given a topic or task description:

1. **Grep the index first** (the charter's Index section) for the
   topic's keywords; then grep the store file bodies for terms the
   index lines may not carry.
2. **Read ONLY the hit files.** Never read the whole store — retrieval
   is pull-based by charter policy (the anti-preload decision lives
   there; respect it).
3. **Surface the operative rules** — the "how to apply" content — with
   a file citation per rule (`docs/loom/memory/<file>.md`) —
   conversational surfacing in the user's conversation language,
   quoted file text verbatim. Before acting on a recalled entry, verify
   any file/flag/skill it names still exists — a memory reflects what
   was true when written, and a named path may have been renamed or
   removed since.
4. **No hits → say "no hits" honestly.** Never fabricate a memory and
   never stretch a loosely related one to look relevant; a clean miss
   is useful information.

## prune

Invoked explicitly, never ambient (no cron, no hook-driven pruning).
For **each** file in the store, check the expiry signals:

- **origin age** — the frontmatter `origin` predates the most recent
  shipped work touching the same area (check via git log on the cited
  paths), so the practice may already have been absorbed;
- **superseded by a repo artifact** — a skill, hook, script, or
  standard now encodes the rule; **cite that artifact** in the verdict;
- **no plausible future trigger** — the situation the memory guards
  against can no longer occur (tool removed, workflow retired).

Output one **keep / merge / retire** table — every file gets a row and
a one-line reason (keep-rows included; silence is not a verdict):

| file | verdict | reason |
|---|---|---|

- **keep** — still operative, trigger still plausible.
- **merge** — duplicates or near-duplicates; propose the combined file
  and the index update.
- **retire** — propose deletion (git history is the archive, per the
  charter — no archive folder).

**NEVER delete without explicit user approval.** Merge and retire are
proposals; execute them only after the user approves, then update the
index in the same pass and re-verify the record invariants for any
merged file.

## Red flags — refuse these

| Impulse | Refusal |
|---|---|
| "Load all memories at session start so they're handy" | Pull, not push — grep, then read hits only. The charter's anti-preload decision is evidence-backed; don't relitigate it per session. |
| "Copy the charter's jurisdiction table / format spec here or into a prompt for convenience" | Point at `docs/loom/memory/README.md`. Copies drift; the family anti-copy convention is test-pinned. |
| "This entry is obviously dead — just delete it" | Prune outputs a proposal. Deletion is user-approved only. |
| "No exact hit, but this memory is close enough — present it as the answer" | Report "no hits" and offer the near-miss as clearly labeled adjacent material, or not at all. |
| "The repo has no store — create one so the verb can run" | `loom-memory: N/A`, loudly. Store creation is the user's deliberate act. |
