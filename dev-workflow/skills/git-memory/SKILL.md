---
name: git-memory
description: |
  Mandatory gate before every git commit / gh pr create — the skill decides whether memory trailers (Decision/Learning/Gotcha) apply; don't pre-judge a commit 'routine'. Also recalls past decisions: 'why did we…', '為什麼', an old branch.
---

# Git Memory

Portable, tool-agnostic project memory using git commit messages and
PR body as the durable substrate.

## Invocation policy

> **The skill is an invocation gate, not a trailer gate.**

Two distinct decisions must not be conflated:

| Decision | Who decides | When |
|----------|-------------|------|
| **Should this skill be invoked?** | The caller | Before `git commit` / `gh pr create` — answer is **always yes** in a Claude session |
| **Should this commit carry memory trailers?** | The skill | Inside the skill — routine commits exit cleanly with no trailers |

Pre-deciding "this commit is routine, I'll skip the skill" is the bug.
The skill's classification logic (routine vs non-routine, see *When not to
use* below) belongs **inside** the skill, not in the caller's head. Skipping
the skill loses the audit trail of "we considered memory and decided no",
and biases toward under-recording over time.

**Concretely**: even when the skill outputs *"no trailers needed for this
commit"*, the invocation itself ensures consistent decision-making and
catches the cases where the caller would have wrongly classified a
non-trivial commit as routine.

## Core thesis

Write the **why** of a decision into commit messages and PR bodies so
that any future session — Claude Code, Cursor, Codex, aider, or a human
reader — can reconstruct project knowledge from `git log` alone.
The git repository itself becomes the memory store; no separate
database, embedding index, or vendor-specific memory file is required.

## Three pillars

### Pillar 1 — Carrier: git artifacts themselves

Memory lives in commit messages and PR descriptions, not in a
separate file. Consequences:

- Any tool that can read git can read the memory (Claude / Cursor /
  Codex / aider / `cat` / a human).
- `git clone` brings the memory with it. Switching machines requires
  no sync step.
- Zero infrastructure dependency. No server, no embedding store, no
  vendor lock-in.
- The memory is versioned automatically by git history. `git blame`
  and `git log` are the audit trail.

### Pillar 2 — Structure: commit trailers

Structured facts ride in **git trailers** — the same mechanism as
`Co-Authored-By:` and `Signed-off-by:` (see `git-interpret-trailers(1)`).

- Machine-readable: `git log --grep='^Decision:'` (reliable everywhere)
  and `git log --pretty='%(trailers)'` (feature branch / merge-commit
  repos — see squash caveat below) make retrieval trivial.
- Coexists with prose: the commit body reads naturally for humans;
  trailers carry the structured signal for machines.
- Git-native: trailer format is part of core git, not a Claude Code
  convention. Every git hosting platform preserves trailers as raw
  text — true for rendering and non-squash merges; a squash merge
  relocates them mid-body (see caveat below).
- Minimum viable schema — three trailers cover ~80% of value:
  - `Decision:` — why this approach was chosen
  - `Learning:` — what was discovered during the work
  - `Gotcha:` — a trap for future self or other readers

> **Squash-merge caveat — `%(trailers)` is unreliable on the default branch.**
> A squash merge concatenates every per-commit message into one squash
> commit, so the original trailers land in the **mid-body**, not the
> footer. `git log --pretty='%(trailers)'` and `git interpret-trailers
> --parse` read **only the footer**, so on a squash-merge `main` they
> miss the buried trailers. `git log --grep='^Decision:'` is a **text**
> match, so it still finds them on `main`.

Retrieval path by repo style:

| Repo merge style | Reliable retrieval |
|---|---|
| **Squash merge** (default branch) | `git log --grep` + the PR `## Memory` section (GitHub-hosted, survives squash) |
| **Feature branch** (pre-squash) | `%(trailers)` structured parse is reliable |
| **Merge-commit / rebase-merge** | `%(trailers)` structured parse is reliable |

Two opt-in escape hatches for parseable trailers on a squash `main`:

- Set `squash_merge_commit_message = PR_BODY` and end the PR body with
  the raw trailer footer, so the squash commit's footer carries them.
- Use a **merge-commit** (not squash) for memory-worthy PRs, preserving
  each commit's footer.

See `standards/memory-conventions.md` for the full schema, line-length
rules, and examples.

### Pillar 3 — Content: decision context, not code

The git diff already shows **what** changed. Memory records the **why**.

- Record: the reason behind a non-obvious choice, alternatives
  considered and rejected, surprising behavior discovered,
  gotchas to avoid.
- Don't record: what the diff already makes obvious ("added function
  foo"), implementation details, routine fixes, typo corrections.
- Aim for entries that stay valuable six months later when the
  original context is gone — not entries that are redundant with
  the code itself.

## When to use

- Recording a non-trivial design decision (why this approach, not
  the alternatives)
- Capturing a gotcha or surprising constraint discovered mid-implementation
- Surfacing relevant past decisions when starting new work in a repo
- Making project knowledge survive a machine change or a tool switch
- Complementing Claude Code's native `~/.claude/.../MEMORY.md`
  (user-level preferences) with repo-level project knowledge

## When not to use

> The lines below describe when the skill **outputs no trailers**, not
> when to skip invoking the skill. See *Invocation policy* above — the
> skill is always invoked; only the trailer outcome varies.

- **Routine commits → skill exits with no trailers.** Typo fixes, version
  bumps, formatting changes — memory trailers would be pure noise. The
  skill itself recognises these and outputs an empty trailer set.
- **User-level preferences not tied to a repo** (e.g. "user prefers
  concise responses") — those belong in Claude Code's native memory,
  not in git. The skill does not write these as git-memory trailers.
- **Secrets or sensitive context** — git is public-by-default; use
  `.gitignore`d notes or secret managers instead. The skill refuses
  to embed secrets in commit trailers.
- **Replacing Claude Code's memory wholesale** — git-memory complements
  it, does not substitute for it. Both layers coexist; see the
  *Relationship to Claude Code native memory* table below.

## Relationship to Claude Code native memory

| Layer | Substrate | Scope | Owner |
|---|---|---|---|
| Claude Code native | `~/.claude/projects/{slug}/memory/MEMORY.md` | User-level preferences, cross-project | The individual user |
| git-memory | commit messages + PR bodies in-repo | Project decisions, shared knowledge | The repo (team or solo) |

The two are complementary. A user preference ("kouko prefers
terse replies") stays in Claude native memory. A project decision
("we adopted two-layer i18n because API surface is English but
user-facing design needs trilingual") belongs in git-memory.

In later phases, a rebuild script can distill git-memory into
`MEMORY.md`-shaped entries so Claude Code's auto-loaded memory
reflects project decisions without manual transcription.

## Phased rollout

- **Phase 1 (MVP, this version)** — conventions + a retrieval
  primitive. Claude helps compose commit trailers and the PR
  `## Memory` section when prompted.
- **Phase 2** — install script for `attribution.commit` integration,
  optional pre-commit validate hook. (A static PR template under
  `.github/` is deferred until humans-opening-PRs-via-GitHub-UI
  becomes a real use case in this repo — Claude-authored PRs
  bypass the template entirely via `gh pr create --body`.)
- **Phase 3** — rebuild pipeline: `git log --trailer` + PR body
  extraction → distilled `MEMORY.md` entries.

## Resources

- `standards/memory-conventions.md` — trailer schema, PR body section
  layout, diagram venue rules
- `protocols/compose-commit.md` — guidance for writing commit messages
  with memory trailers
- `protocols/compose-pr.md` — guidance for writing PR bodies with a
  `## Memory` section
- `scripts/memory-grep.sh` — retrieval primitive; run from any repo to
  dump all memory trailers + PR `## Memory` sections as a digest

## Prior art

The approach is closest to **Lore** (Stetsenko, arXiv:2603.15566,
2026) — a git-trailer-based decision protocol with an associated
CLI. `git-memory` deliberately starts with a leaner three-trailer
subset (`Decision:` / `Learning:` / `Gotcha:`) rather than Lore's
full 12-trailer schema, to keep the per-commit cognitive load low.
If Lore's schema becomes a de-facto standard, the upgrade path is
additive (introduce more trailers on top of the existing three).

Related prior art:

- **Letta Context Repositories** (2026-01) — git-backed agent memory
  with markdown files committed to the repo; auto-commit on memory
  change
- **Git Context Controller** (arXiv:2508.00031, 2025-08) — COMMIT /
  BRANCH / MERGE as agent-memory primitives

## License

MIT — see repository root `LICENSE`.
