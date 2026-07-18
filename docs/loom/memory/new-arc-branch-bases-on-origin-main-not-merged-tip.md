---
name: new-arc-branch-bases-on-origin-main-not-merged-tip
description: After a squash-merged arc, cut the NEXT arc's branch from origin/main — not from the previous arc's local branch tip; a tip-cut branch carries a stale base whose diff-vs-main is polluted by the old arc's commits and any content main gained since, and the pollution only surfaces at finishing
type: practice
origin: 52/53-week filer arc finishing (feat-52-53-week-filer-support, 2026-07-19)
---

This repo squash-merges PRs, so a merged arc's local branch tip is
content-similar to main but history-divergent from it — and main keeps
moving. Cutting the next arc's branch from that tip (convenient when the
worktree is still parked there) builds the whole arc on a stale base:
`git log origin/main..HEAD` lists BOTH arcs' commits, the three-dot diff
re-shows the shipped arc's files, and any content main gained in between
shows up as phantom reverts. In the 52/53-week arc this surfaced only at
finishing — a 47-file direct diff against origin/main for a 19-file arc —
and cost a 17-commit `git rebase --onto origin/main <old-tip>` before the
whole-branch review could run against a truthful diff.

**Why:** a polluted base corrupts every base-relative surface at once —
whole-branch review scope, PR files-changed, merge conflicts — and the
longer the arc, the later and more expensively it surfaces. The rebase is
cheap when caught, but review verdicts minted before the rebase reviewed
the wrong diff.

**How to apply:** when opening a new arc branch, cut from origin/main
after a fetch (`git fetch origin && git checkout -b <branch> origin/main`
— note the repo guard blocks `checkout -b` FROM origin/main in one
compound line with pushes; branch from a fetched, fast-forwarded local
ref if the guard complains). If the worktree is parked on a merged
branch, that convenience is the trap. At finishing, ALWAYS verify base
freshness before dispatching the whole-branch reviewer:
`git log --oneline origin/main..HEAD | wc -l` must equal this arc's
commit count, and `git diff origin/main HEAD --stat` must list only this
arc's files; a mismatch → `git rebase --onto origin/main <old-base>`
first (never-pushed branches rebase freely), then re-run the suite at the
rebased HEAD before review.
