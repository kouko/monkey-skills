---
name: git-memory
description: >-
  MANDATORY invocation gate before every `git commit` and `gh pr create` —
  the skill itself decides whether memory trailers (`Decision:` / `Learning:`
  / `Gotcha:`) are warranted. Do NOT pre-decide "this commit is routine" and
  skip the skill; that decision belongs to the skill, not the caller. Without
  this gate, the git history loses the "why" archive that
  `git log --grep='Decision:'` retrieves across sessions, machine changes,
  and tool switches. Also use to recall past decisions (user asks "why did
  we...", 為什麼, references an old branch, revisits earlier work). Triggers:
  about-to-`git commit`, about-to-`gh pr create`, about-to-merge, "why did
  we", 為什麼, "decision", "rationale", "commit メモ", "決定記録".
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

- Machine-readable: `git log --pretty='%(trailers)'` and
  `git log --grep='^Decision:'` make retrieval trivial.
- Coexists with prose: the commit body reads naturally for humans;
  trailers carry the structured signal for machines.
- Git-native: trailer format is part of core git, not a Claude Code
  convention. Every git hosting platform preserves trailers as raw
  text even when they don't render them specially.
- Minimum viable schema — three trailers cover ~80% of value:
  - `Decision:` — why this approach was chosen
  - `Learning:` — what was discovered during the work
  - `Gotcha:` — a trap for future self or other readers

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
