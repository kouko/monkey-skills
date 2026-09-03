# loom post-merge seams — task W0-04 — what I tried and what happened

Tried on 2026-09-03, in a clean copy of the project at `58b8f514` (branch
`loom-post-merge-seams`). This is a narrow, after-task blind run: it walks
only the part of Acceptance #1 that task W0-04 (commit `942ced9e`) claims
to deliver — the check that a "close the intent" commit has the right
shape before the push gate lets it through. It does not walk the rest of
Acceptance #1 (the review round on the close commit, the "already closed"
message from `intake write-plan`), because those pieces are not in this
commit yet.

I never wrote any of this code. I built five small, throwaway practice
repositories — none of them the real project — and pointed the project's
own gate-checking program (`loom_checker.py push`) at each one, exactly
the way the real ship process would.

## What you asked for, one line at a time

### 1. Acceptance #1 (the push-gate part): a well-formed "close the
intent" commit should let the push through with no manual override and no
new rule; each of four specific mistakes around it should be caught and
blocked, by name.

**Positive case — the good sequence goes through**
- **How I tried it**: built a practice repo with a normal checkpoint
  commit (a code commit + its review record), then a commit that changes
  only the intent file's status line from `confirmed …` to
  `closed 2026-09-03 — PR #999`, then a second checkpoint whose review
  record points at that close commit and whose reviewer sign-offs are all
  stamped with that same commit's id. Ran:
  `python3 loom_checker.py push` (from inside the practice repo).
- **What happened**: exit code 0. The tool printed only its normal
  test-replay lines ("package-tests … observed exit code 0", three
  "adversarial … observed exit code 0" lines) and no `BLOCK` lines at all.
- **Evidence**: captured stdout/stderr of the run; `blocked rules: set()`.
- **Verdict**: works.

**Negative A — the close commit also touches an unrelated file**
- **How I tried it**: same setup, but the close commit also edits a second
  file (`docs/loom/notes.md`) alongside the status line. Ran the same push
  check.
- **What happened**: exit code 1, blocked with:
  `push.review-only-head: HEAD^ turns \`status:\` closed on
  docs/loom/intent/….md but also touches docs/loom/notes.md; a close
  commit must touch only the intent file.`
- **Evidence**: captured stderr line above.
- **Verdict**: works.

**Negative B — the close commit changes a second line in the same file**
- **How I tried it**: same setup, but besides the status line the close
  commit also edits another line inside the intent file (a line under
  "## Problem"). Ran the push check.
- **What happened**: exit code 1, blocked with:
  `push.review-only-head: HEAD^'s diff on docs/loom/intent/….md must be
  exactly one removed and one added \`status:\` line, the added one
  matching the \`closed\` grammar; got 2 removed / 2 added line(s).`
- **Evidence**: captured stderr line above.
- **Verdict**: works.

**Negative C — an unrelated commit sits between the checkpoint and the
close commit**
- **How I tried it**: same setup, but a plain docs commit was inserted
  right after the checkpoint and right before the close commit (so the
  close commit's parent is that stray commit, not the checkpoint). Ran the
  push check.
- **What happened**: exit code 1, blocked with:
  `push.review-only-head: HEAD^^ is not itself a checkpoint (touches
  something other than review.json), so no checkpoint sits between the
  last review and the close commit.`
- **Evidence**: captured stderr line above.
- **Verdict**: works.

**Negative D (the task's own instruction) — the review pointer is moved by
hand to the close commit, but the reviewers' individual sign-offs still
name the older commit**
- **How I tried it**: built the close commit properly (well-formed, parent
  is a real checkpoint), then wrote the second checkpoint's review record
  by hand so its top-level "which commit did we review" field says the
  close commit, but each individual reviewer's sign-off still carries the
  older commit's id (the one the first checkpoint reviewed). Ran the push
  check.
- **What happened**: exit code 1, blocked with three separate lines —
  `push.reviewed-sha: agent-rev's verdict sha resolves to …, not
  reviewed_sha ….`, the same for the second reviewer, plus two more lines
  (`push.probes-package-tests`, `push.probes-adversarial`) saying the
  recorded test run and abuse-case runs were against the older commit too.
  The task's own rule (`push.reviewed-sha`) fires exactly as described,
  and composes cleanly with the pre-existing rules that check the test
  evidence — nothing here weakens or bypasses anything.
- **Evidence**: captured stderr, four `BLOCK` lines.
- **Verdict**: works (the specific rule named in the task, `push.
  reviewed-sha`, is present; two additional and unrelated rules also fire
  on this same malformed record, which is expected and not a problem).

**Not walked in this after-task pass** (out of scope for W0-04 alone,
belongs to the rest of Acceptance #1): the two-fresh-reviewer round that
must actually happen on the close commit before the review-only commit is
written; the `intake write-plan` message on an already-closed intent; the
carry-over of `2026-09-02-simple-loom-flow`'s own status to `closed`. — not-yet, out of scope for this commit.

## What the package tests say

Ran the project's own declared test command from the clean checkout:
`python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/ -q`, at sha
`58b8f514`.

- **Summary line**: `1024 passed in 155.03s (0:02:35)`

## 對你既有的資料做了什麼 (what this did to data you already had)

Nothing — every repository I tested in was one I built from scratch in a
scratch folder outside the project, and I removed it when I was done. I
never touched the real project's files, git history, or any of your data.

## I decided for you

- **Which parts of Acceptance #1 to walk.** The task that dispatched me
  named a specific commit and said to walk only the part of Acceptance #1
  that commit claims to deliver — the shape-check on the close commit. I
  did not attempt the review-round or the "already closed" messaging,
  because those are not in this commit; I labeled that scope narrowing
  explicitly above rather than silently skipping it.
- **Building throwaway practice repos instead of the real project.** The
  gate being tested is a piece of logic about git commit shapes, not a
  product feature with a UI; the fastest and safest way to prove it works
  is a disposable repo with the exact shapes described, not the real
  history (which does not yet contain a close commit to test against).

## Things I am not sure you want

- The task asked me to also confirm the two rules "compose" for negative
  case D. They do — but the malformed record I built also trips two other,
  older rules about test evidence at the same time. That is expected
  (an obviously fabricated record fails several checks at once), not a
  new finding, but flagging it since the task specifically asked about
  composition.
- Nothing else.
