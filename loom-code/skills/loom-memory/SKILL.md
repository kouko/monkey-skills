---
name: loom-memory
# firing-evidence: 2026-07-14 baseline 4/4 EXACT (docs/skill-dogfood/2026-07-14-description-token-economy/baseline.md)
description: >-
  Record, recall, or prune the repo-native loom practice-memory store
  (`docs/loom/memory/`) — save a distilled lesson/gotcha, check prior
  experience before loom work, or propose keep/merge/retire cleanup
  (never auto-deletes). CONDITIONAL: fires only when the repo has
  `docs/loom/memory/README.md` — otherwise `loom-memory: N/A` with the
  reason, loudly. NOT for git commit trailers (loom-workflow:git-memory)
  nor Claude auto-memory. Triggers: "有沒有相關經驗", "記住這個做法",
  "記憶整理", "この教訓を残して", "過去の知見はある？".
version: 0.2.1
---

# loom-memory — record / recall / prune for the practice-memory store

Three verbs over one store; execute its charter, never redefine it.

## When it fires — N/A-loud gate

Fire only when the target repo has the store charter,
`docs/loom/memory/README.md`. If missing, emit **`loom-memory: N/A (no
docs/loom/memory/README.md in this repo)`** and stop. Never silently
skip, never scaffold a store, and never substitute machine-local
memory. Store creation is a separate user decision.

The target repo is the user's current project repository, never the
plugin installation or skill directory.

## SSOT — point, never copy

The charter owns the jurisdiction table, one-fact-per-file and index
formats, and pull-not-push policy. Every verb **reads the charter at
execution time**. Do not reproduce its rows or format block in this
skill, prompts, or dispatch payloads. If this summary differs, the
charter wins.

## record

1. **Classify against the charter's jurisdiction table.** A
   backlog-shaped open item/debt/re-trigger becomes an entry under
   `docs/loom/backlog/` per `docs/loom/backlog/README.md`; harness/dcg
   friction routes to the plugin-shipped gotchas reference. Classify
   everything else by the charter. Not every useful fact belongs in
   practice memory: do not blur these destinations. Tell the user the
   chosen route and why, including when the fact is rejected from this
   store.
2. **Check the store for contradictions.** First grep both index and bodies
   before writing. On a hit, update or replace the entry (git history
   is the archive), never add a contradicting sibling. Note replacement
   in its frontmatter `description`, which the regenerated index carries.
   Follow `loom-workflow:git-memory`'s backward-pointing `Supersedes:`
   doctrine by reference; do not copy it.
3. **Write `<slug>.md`** to `docs/loom/memory/<slug>.md`, following the
   charter's format block exactly, including frontmatter and body sections.
4. Run `python3 scripts/check_loom_memory_integrity.py --write`; it
   generates `## Index` from entry frontmatter, so never append a line
   manually. If it refuses, its FAIL output identifies the offending
   file and cause, such as broken frontmatter or unexpected index prose;
   fix that named file before rerunning.
5. Before declaring done, `python3 scripts/check_loom_memory_integrity.py`
   must exit 0, independently checking the validator docstring's five
   invariants. Also run `--check` for committed-index drift; because it
   regenerates, it is not the certification. Any nonzero exit is
   fail-loud and fix-now.

## recall

1. **Grep the index first** for topic keywords, then bodies for terms
   index lines may omit.
2. **Read ONLY the hit files.** Never preload the store; recall is
   pull-based by charter policy.
3. Surface applicable rules in the user's conversation language,
   especially their operative "how to apply" content, quoting text
   verbatim with a file citation per rule
   (`docs/loom/memory/<file>.md`). Before acting, verify any
   file/flag/skill it names still exists; memories can become stale.
4. **No hits → say "no hits" honestly.** Never fabricate or stretch a
   near-match; label adjacent material clearly, if offered.

## prune

Invoked explicitly, never ambient: no cron or hook-driven pruning. For
**each** file, check:

- **origin age**: compare frontmatter `origin` with git log for shipped
  work on cited paths;
- **superseded by a repo artifact**: a skill, hook, script, or standard
  encodes it; cite that artifact;
- **no plausible future trigger**: the guarded situation cannot recur.

Output one **keep / merge / retire** table; every file gets a row and
one-line reason, including keeps:

| file | verdict | reason |
|---|---|---|

- **keep**: operative with a plausible trigger.
- **merge**: duplicate/near-duplicate; propose combined file and index.
- **retire**: propose deletion; git history is the archive, not a folder.

**NEVER delete without explicit user approval.** Merge and retire are
proposals. After approval, execute and regenerate the index in the same
pass with `python3 scripts/check_loom_memory_integrity.py --write`, then
run `--check` for merged files.

## Red flags — refuse these

| Impulse | Refusal |
|---|---|
| "Load all memories at session start" | Pull, not push: grep, then read hits only. |
| "Copy the charter table/spec into a prompt" | Point at `docs/loom/memory/README.md`; copies drift. |
| "This entry is obviously dead — just delete it" | Prune outputs a proposal. Deletion is user-approved only. |
| "A near hit is close enough" | Report "no hits"; label it adjacent or omit it. |
| "The repo has no store — create one so the verb can run" | `loom-memory: N/A`, loudly. Store creation is the user's deliberate act. |
