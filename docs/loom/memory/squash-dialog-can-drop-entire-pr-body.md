---
name: squash-dialog-can-drop-entire-pr-body
description: The GitHub merge dialog can ship a title-only squash commit even when repo settings are correctly PR_TITLE+PR_BODY (#578 live) — a heading-based memory-worthiness detector goes green-blind when the whole body vanishes, so post-merge verify must treat title-only "(#N)" commits as suspicious (mechanized in memory-grep --verify-merged)
type: gotcha
origin: PR #578 (this repo, monkey-skills, 2026-07-17)
---

PR #578's squash commit on `main` (`2c147cd7`) has a body of exactly
ONE line — the title, ending `(#578)`. This happened even though the
repo's squash settings were verified correct
(`squash_merge_commit_title=PR_TITLE`,
`squash_merge_commit_message=PR_BODY`, checked via `gh api`), and two
other PRs merged the same day (#576, #577) carried their full bodies
through squash normally. Consequence: `memory-grep.sh --verify-merged`
exited `0` — no `## Memory` heading was found, so the heading-based
detector judged the commit not memory-worthy — when the true state was
unknowable, because the entire body had vanished before the heading
check ever ran. `--verify` (the plain trailer-text-match mode)
correctly caught the emptiness and exited `4`, which is what surfaced
the bug.

**Why:** repo-level squash settings (`PR_TITLE`+`PR_BODY`) determine
the *template* GitHub uses to compose a squash message, but the
merge-time UI dialog is still editable by the person clicking merge —
if that editable textarea gets cleared (accidentally or via some
client/extension interaction) before confirming, the squash commit
ships title-only regardless of what the repo settings say. A
heading-based memory-worthiness check (`grep for '## Memory'`) is
blind to this failure mode by construction: an absent heading is
supposed to mean "this PR never claimed to carry memory," but it
cannot distinguish that from "the memory section existed and got
wiped along with everything else."

**How to apply:** any post-merge verify step that gates on "does the
body contain marker X" must first rule out "does the body exist at
all." For `memory-grep.sh --verify-merged`, this is mechanized: before
the heading check, if the commit message is title-only (exactly one
non-empty line) AND that title matches the squash-of-PR signature
`\(#[0-9]+\)$`, exit `4` immediately with a stderr message naming the
suspicious-empty-body case — never fall through to "no heading ⇒ not
memory-worthy." A title-only body WITHOUT a `(#N)` suffix is a routine
direct commit (not a squash-of-PR shape at all) and stays exit `0`.
Generalize this pattern to any other heading/marker-based detector
gating on PR-sourced squash bodies.

**Contradiction check:** this is a DIFFERENT mechanism from both
[github-squash-merge-single-commit-drops-body](github-squash-merge-single-commit-drops-body.md)
(GitHub's *default* squash-message template drops the body for a
single-commit PR — mitigated here by the `PR_BODY` setting, and this
entry's incident happened with that mitigation already correctly in
place) and
[github-ui-squash-appends-coauthor-and-wraps-body](github-ui-squash-appends-coauthor-and-wraps-body.md)
(GitHub's merge UI appends a trailer-like block and hard-wraps lines
AFTER a body that did survive — a parse-level problem, not an
existence problem). This entry's incident is the body being emptied
entirely at merge time despite correct settings, with no known
mechanism yet identified that would predict it. All three entries
stay, cross-referenced — do not merge or replace one with another.
