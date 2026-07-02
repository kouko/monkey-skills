# git-memory — Supersedes-liveness & on-demand pull retrieval

Design/implementation note for the two features shipped in **PR #466**
(squash `c5bad9b7`, 2026-07-02). Captures the **why** so a later
iteration doesn't revert the decisions. Operational how-to lives in the
skill itself (`skills/git-memory/SKILL.md`, `standards/memory-conventions.md`,
`protocols/recall.md`, `protocols/compose-commit.md`); this note does not
duplicate it.

## Problem

Two gaps made recorded memory hard to actually use:

1. **Decisions could never be retired.** Commit messages are immutable,
   so a `Decision:` that later turned out wrong stayed live forever;
   `git log --grep` retrieval returned the old and new (contradicting)
   decisions with no way to tell which was current.
2. **Nothing pulled memory back.** The Phase-3 plan was to *distill*
   trailers into an always-loaded `MEMORY.md` (push). Memory was written
   but only surfaced if someone remembered to grep for it.

## Feature 1 — Supersedes with computed liveness

- A retiring decision carries `Supersedes: PR #N` (or SHA) on the
  **replacement** commit. The pointer is **backward** because the
  superseded commit is immutable — you cannot edit it to mark it dead.
- Liveness is **computed, never stored**: a decision is live unless a
  *later* commit's `Supersedes:` names it. `memory-grep.sh` forward-scans
  the log to build the superseded-set; default recall shows live only,
  `--history` reveals the full chain (tagged `[SUPERSEDED by …]`).

Why not git-notes-style mutable status (edit the old record to
"superseded")? Because trailers travel *inside* the commit message —
they clone by default and survive squash-merge mid-body — whereas notes
don't clone/push by default. The immutability is the feature; the
backward pointer is how you work with it.

## Feature 2 — Pull retrieval, not push

- Phase 3 repositioned **push → pull**: recall the few decisions relevant
  to the task, on demand, instead of pre-baking an always-loaded file.
- Surface = three `memory-grep.sh` filters — `--match=<regex>` (topic),
  `--path=<pathspec>` (which decisions touched this code; commit-only),
  `--top=<n>` (display cap, suppressed count reported never silently
  dropped) — driven by `protocols/recall.md`.
- Recall triggers: ① the user asks, ② before working in an area
  (`--path`), ③ weighing an alternative (`--match`). Explicitly **not**
  broad session-start priming.

**Load-bearing invariant**: `--match` / `--path` narrow the *view* only;
the supersession index is always built over full history. A decision
retired by a commit that neither matches the topic nor touches the path
still stays hidden by default. (This is the cross-feature seam
whole-branch review is designed to catch; the match test-suite proves it.)

## Key decisions (don't revert these)

| Decision | Rationale |
|---|---|
| Backward `Supersedes:` on the replacement | Superseded commit is immutable; can't point forward from it |
| Liveness computed, not stored | No status field to keep in sync; deterministic from the log |
| **Supersedes needs an atomically-recorded target** | The old push Phase 3 lived only in SKILL.md prose, so its reversal was recorded as a fresh `Decision`, NOT a `Supersedes` — pointing at the foundational PR would over-hide its still-live memory |
| push → pull | 2026 ETH Zurich study (InfoQ): always-loaded auto-generated context files cut agent task success ~3% and raised cost ~20% — worse than no file (a small human-curated file gave only ~4%) |
| No fuzzy ranking (reverse-chronological only) | Preserves deterministic retrieval — the advantage over vector RAG |
| Keep zero-infra commit-trailer substrate | Lore's paper (arXiv:2603.15566) proposed trailers, but its shipped product `rac` (github.com/itsthelore/rac-core) moved to typed Markdown + MCP + CI status. That is the right lane at team/org scale; git-memory keeps trailers for solo/small-team and treats "graduate to Markdown+MCP" as the explicit outgrow signal |

## Validation

- 38 tests green — `test-memory-grep-{verify,supersedes,match}.sh`
  (5 / 12 / 21) — under both modern bash and system `/bin/bash` 3.2.57
  (bash-3.2-safe: collect-SHAs-first avoids empty-array-under-`set -u`).
- Malformed `--match` regex validated up front (exit 1, clean message).
- Two `loom-code:code-reviewer` whole-branch reviews, both
  PASS_WITH_NOTES with all notes addressed.
- Dogfood: post-merge `memory-grep.sh --verify c5bad9b7` exits 0 — the
  trailers survived the squash mid-body, confirming the skill's core bet
  on a real squash-merged `main`.
