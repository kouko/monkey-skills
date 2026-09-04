---
name: a-close-commit-sits-directly-under-a-checkpoint-so-any-late-fix-buys-its-own-round
description: The push gate's final shape is strict — HEAD touches only review.json, HEAD^ is the close commit (one `status:` line), HEAD^^ is itself a checkpoint commit — so a commit that lands after the branch-end pass for any other reason (a CI-only doc fix, a citation rewording in another intent) must get its OWN review-only round before the close commit is re-created on top; it cannot sit between the last checkpoint and the close, and the close-round dispatch records go inside the review-only commit, not in a separate `chore(loom): dispatch` commit
type: process
origin: branch positioning-paragraph-cap-redesign (2026-09-04) — PR #789's first CI run failed a doc-citation check; the one-line fix inserted before the close commit tripped `push.review-only-head` ("HEAD^^ is not itself a checkpoint") and the separate close-round dispatch commit tripped it again; two reorders and one extra reader round later the shape held
---

`push.review-only-head` reads three commits, not one:

| position | must be |
|---|---|
| `HEAD` | touches only `docs/loom/<change-id>/review.json` |
| `HEAD^` | the close commit — exactly one `status:` line of the intent |
| `HEAD^^` | a checkpoint commit (touches only review.json) |

Two shapes that look harmless both fail it:

1. **A fix between the last checkpoint and the close.** After the
   branch-end pass, CI found a problem in a file this change never
   touched (an intent of a *parked* change cited `~/.codex/config.toml`
   in backticks; `check_doc_citations.py` treats any backticked token
   containing `/` as a repo path). Fixing it as one commit before the
   close made `HEAD^^` that fix, not a checkpoint.
2. **A separate dispatch-record commit for the close readers.** The
   review station's habit — `chore(loom): dispatch review <scope>` before
   the verdicts — puts a non-review commit at `HEAD^` when it is done
   after the close commit.

**Why:** the rule is what makes "the reviewed tree is the pushed tree"
true at the close: the only unreviewed delta allowed above the last
checkpoint is the one status line. Anything else above it is unreviewed
work by construction, however small.

**How to apply:** when something must change after the branch-end pass,
do it in this order — fix commit → its own review-only round (both
readers, `reviewed_sha` = the fix) → close commit → review-only round
with `reviewed_sha` = the close commit, and write the close readers'
`dispatch[]` entries into that last review-only commit with a note that
they were written before dispatch. Every re-creation of the close commit
changes its sha, so ask the readers for the verdict at the final sha,
not the first. Write paths that are not repo files (`~/...`) in prose
inside intents, never in backticks.
