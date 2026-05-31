# Brief — git-memory squash-merge retrieval caveat (doc-note)

Date: 2026-05-31 · Stage: brainstorming output → `writing-plans`
Target: `dev-workflow:git-memory` SKILL.md (Pillar 2). Doc-only, no behavior/config/workflow change.

## Problem (Axis 1 — JTBD)

git-memory's Pillar 2 **overclaims** trailer retrievability: it says trailers are
"Machine-readable: `git log --pretty='%(trailers)'` … retrieval trivial" (SKILL.md:72-73)
and "Every git hosting platform **preserves** trailers as raw text" (SKILL.md:76-78). But
in a **squash-merge repo** (this one), squash concatenates per-commit messages into the
squash commit's **mid-body**, so per-commit `Decision:`/`Learning:` trailers are NO LONGER
in the footer → `%(trailers)` / `git interpret-trailers --parse` return **0 on the default
branch** (confirmed live on squash commit `8ad4c3fe`). The job: make the retrievability
claim **honest** and point at the path that actually works on main — not "preserve trailers
at all costs." (Same defect class as the depth-grounding overclaim fixed in code-toolkit
PR #357: an accurate-sounding claim that doesn't hold in the actual environment.)

## Users (Axis 2)

- A future developer / agent doing `git log` decision-recall on **main** in a squash-merge
  repo — they'll reach for `%(trailers)` per Pillar 2 and get nothing, not realizing
  `git log --grep` is the path that works.
- The skill author trusting Pillar 2's "machine-readable / every platform preserves" claim.

## Smallest End State (Axis 3)

Add a **squash-merge caveat** to git-memory SKILL.md Pillar 2 (a short note/bullet):
- In a **squash-merge** repo, per-commit trailers land mid-body of the squash commit →
  `%(trailers)` / `git interpret-trailers --parse` are **unreliable on the default branch**
  (they read only the footer). `git log --grep='^Decision:'` (TEXT match) still works on
  main. So on squash repos, the retrieval path is **`git log --grep` + the PR `## Memory`
  section** (GitHub-hosted, survives squash); `%(trailers)` structured parse is reliable
  on the **feature branch** and in **merge-commit / rebase-merge** repos.
- Name two **opt-in escape hatches** for teams that need parseable trailers on main:
  (a) set `squash_merge_commit_message = PR_BODY` and end the PR body with the raw trailer
  footer; (b) use **merge-commit** (not squash) for memory-worthy PRs.
- Lightly qualify the "every git hosting platform preserves trailers" line (true for
  rendering / non-squash; squash relocates them).

Plus a patch version bump (dev-workflow 2.14.0 → 2.14.1) + CHANGELOG.

## Current State Evidence

- `dev-workflow/skills/git-memory/SKILL.md:72-73` — "Machine-readable: `%(trailers)` …
  retrieval trivial" (the overclaim).
- `:76-78` — "Every git hosting platform preserves trailers as raw text" (squash relocates,
  doesn't preserve-in-footer).
- `:9` — "`git log --grep='Decision:'` retrieves across sessions…" — this one is FINE
  (text-grep survives squash); the caveat should reinforce grep as the squash-robust path.
- Live: squash commit `8ad4c3fe` (PR #359) — `git interpret-trailers --parse` → 0 trailers;
  `git log --grep='^Decision:'` → still matches (text mid-body).
- Repo settings (`gh api`): `allow_merge_commit/squash/rebase` all true;
  `squash_merge_commit_message = COMMIT_MESSAGES` (the concatenation that buries trailers).

## Decision

Add a squash-merge caveat to Pillar 2 correcting the `%(trailers)` overclaim and stating
the squash-robust retrieval path (`git log --grep` + PR `## Memory`), with the two escape
hatches named as opt-in. **No repo-setting change, no per-PR merge-strategy mandate, no new
mechanism.** Honest doc correction only — the actual recall use case ("why did we X?") is
already served by `git log --grep`, which works on main post-squash.

## Alternatives Considered (Axis 4 — research-grounded, EN + JA)

- **Config: `squash_merge_commit_message = PR_BODY`** ([GitHub since 2022](https://github.blog/changelog/2022-08-23-new-options-for-controlling-the-default-commit-message-when-merging-a-pull-request/))
  + PR-body trailer footer → parseable on main. Rejected as the default: repo-wide setting
  affecting ALL PRs + PR-body discipline; surfaced as escape hatch (a).
- **Per-PR merge-commit for memory-worthy PRs** (already allowed) → trailers survive verbatim.
  Rejected as default: messier history + per-PR merge-strategy discipline; surfaced as
  escape hatch (b).
- **git notes (git-adr)** — survives squash independently. Rejected: not fetched/pushed by
  default, poor GitHub UI, a whole new mechanism (over-engineering for a low-impact problem).
EN+JA agree: trailers must be in the footer; squash discards/relocates original commits;
use PR-description-as-squash-message or a real merge to preserve. Sources: GitHub Docs
"Configuring commit squashing"; git-interpret-trailers(1); JA git-style guides.

## What Becomes Obsolete (Axis 5)

Nothing removed. The Pillar-2 "machine-readable / every platform preserves" claim is
**qualified** (not deleted) with the squash caveat. A tightening, not a removal.

## Out of Scope

- Changing the repo's merge settings or `squash_merge_commit_message` (escape hatch, user's call).
- Mandating a per-PR merge strategy.
- git notes.
- The git-memory Phase-2 pre-commit validate hook (separate concern — and if `%(trailers)`
  is branch-only on squash repos, that hook's value needs its own re-evaluation).

## Open Questions

1. Version: dev-workflow patch 2.14.0 → 2.14.1 (doc correction, no behavior change).
2. Placement: the caveat belongs in SKILL.md Pillar 2; confirm whether a one-line cross-ref
   in `memory-conventions.md` retrieval area is also warranted (lean SKILL.md-only — keep
   it where the overclaim is).
