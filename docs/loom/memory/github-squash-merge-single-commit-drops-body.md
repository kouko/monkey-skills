---
name: github-squash-merge-single-commit-drops-body
description: GitHub's default squash-merge message for a single-commit PR keeps only the PR/commit title — the full body (including git-memory Decision/Learning/Gotcha trailers) is silently dropped from main's git history; a multi-commit PR concatenates all bodies instead
type: gotcha
origin: PR #520 (loom-code mechanical-exemption sync-script category, 2026-07-08)
---

Verifying `git-memory`'s commit-carrier survival on `main` after PR #520
merged (`memory-grep.sh --verify <merge-sha>`) returned exit 4 — no
trailer found — even though the branch's single close-out commit had a
full `Decision:`/`Learning:`/`Gotcha:` body. `git log -1 --format=%B` on
the merge commit showed only the PR title line, nothing else. Comparing
against PR #519 (same session, same day), whose branch had 2 commits,
showed the opposite: the squash merge concatenated BOTH commits' full
messages into the merge commit body, and `--verify` passed cleanly.

**Why:** GitHub's squash-merge default commit-message behavior differs
by commit count on the source branch — a single-commit PR's default
squash message is just `<title> (#N)`, while a multi-commit PR's default
is the title plus a bulleted list of every commit's subject+body. This
is a GitHub UI default, not a repo setting or something the merging user
did wrong; it fires even when the single commit's body is rich and
memory-worthy. The PR page itself (title + body, including any
`## Memory` section) survives merge either way — only the git-log-visible
copy on `main` is at risk for single-commit PRs.

**How to apply:** for a memory-worthy PR, don't assume the commit
carrier survived squash-merge just because you verified it pre-merge —
pre-merge verification only confirms the trailer exists on the *branch*
commit, not what the squash message will look like. After merge,
re-run `memory-grep.sh --verify <merge-sha>` against the actual `main`
history. If it exits 4 and the branch had only one commit, the PR
`## Memory` section (both-carrier policy) is the only surviving copy —
that's expected and acceptable, but note it rather than assuming
`git log --grep` alone can find it later. If structured `%(trailers)`
footer-parsing on `main` matters for a given repo, either force a
merge-commit (not squash) for memory-worthy PRs, or set
`squash_merge_commit_message = PR_BODY` in the repo's merge settings so
the PR body (which the both-carrier policy already writes trailers
into) becomes the squash message.

**Status (2026-07-08, this repo): mitigated at the repo-settings level.**
`kouko/monkey-skills` now has `squash_merge_commit_title=PR_TITLE` +
`squash_merge_commit_message=PR_BODY` set (via `gh api -X PATCH
repos/<owner>/<repo> -f squash_merge_commit_title=PR_TITLE -f
squash_merge_commit_message=PR_BODY` — note GitHub only accepts specific
title/message combos, `COMMIT_OR_PR_TITLE` does NOT pair with `PR_BODY`,
use `PR_TITLE`). Every future squash-merge in this repo now carries the
full PR body (including `## Memory`) into the squash commit regardless
of source-branch commit count — the single-commit-drops-body failure
mode described above should no longer occur here. Still worth the
post-merge `--verify` habit as a safety net, and still fully applicable
knowledge for any OTHER repo that hasn't made this settings change.
