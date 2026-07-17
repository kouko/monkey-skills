---
name: github-ui-squash-appends-coauthor-and-wraps-body
description: GitHub UI squash-merge appends a divider + Co-authored-by block AFTER the PR body and hard-wraps long lines — %(trailers) on squash main cannot reliably see body-end trailer blocks even when the PR body ends with a raw footer; grep-level retrieval is the attainable bar (PR #576 live)
type: gotcha
origin: PR #576 (this repo, monkey-skills, 2026-07-17)
---

PR #576's body ended with the git-memory O2-mandated raw trailer
footer (`Decision:`/`Learning:`/`Gotcha:`, unbolded, the PR body's true
last block, nothing after it). After squash-merging via the GitHub UI,
`memory-grep.sh --verify HEAD` and `--verify-merged HEAD` both exited
`0` (grep-level retrieval, CI green) — but `--verify-strict HEAD`
(the `git interpret-trailers --parse --unfold` diagnostic) exited `4`.
`git log -1 --format=%B` on the squash commit showed why: GitHub (a)
APPENDED a `---------` divider + a `Co-authored-by:` block AFTER the
authored PR body, and (b) HARD-WRAPPED the long trailer lines across
physical lines. Both break `%(trailers)`/`git interpret-trailers` for
the body's own keys — only the GitHub-appended `Co-authored-by` block
itself parses as a trailer.

**Why:** the raw-trailer-footer mandate (`compose-pr.md` Step 4)
assumed that "PR body ends with the mandated footer" was sufficient
for `%(trailers)` to parse on squash `main`. It is not — GitHub's own
merge-commit-message UI is a second author writing content after the
PR body author has no control over, at merge time, not authoring time.
The mandate's actually-guaranteed property is that trailer KEYS stay
at line starts (grep-level retrieval via `git log --grep`); strict
`%(trailers)` structured parsing is best-effort on squash `main`, not
guaranteed, even when the footer-placement rule is followed correctly.

**How to apply:** don't claim "raw footer as last block ⇒ `%(trailers)`
parses on squash main" for GitHub-UI merges — that claim is refuted.
Keep mandating the raw trailer footer (it still prevents the #575
in-body-breakage class and secures the grep-level floor), but treat
strict `%(trailers)`/`git interpret-trailers` parsing as best-effort:
use `--verify-strict` as a diagnostic signal, never as the durable-
lesson gate. The reliable retrieval paths remain `git log --grep`, the
PR `## Memory` prose section, and the repo's committed memory store
(this folder) — never `%(trailers)` alone on a GitHub-UI squash-merged
`main`.

**Contradiction check:** this is a DIFFERENT mechanism from
[github-squash-merge-single-commit-drops-body](github-squash-merge-single-commit-drops-body.md)
— that entry is about GitHub's *default* squash-message dropping the
whole body for a single-commit PR (mitigated in this repo by the
`squash_merge_commit_message = PR_BODY` setting). This entry assumes
that setting is already in place (the body *does* survive into the
squash message) and describes a second, independent GitHub-UI
behavior on top of it: appending a trailer-like block and wrapping
lines. Do not merge or replace the other entry with this one — both
stay, cross-referenced.
