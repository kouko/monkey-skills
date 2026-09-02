---
name: ship
description: |
  Closes a development branch out: confirms the branch-end checkpoint passed, presents the blind-run report to the user for acceptance, writes the memory, runs the deterministic push gate, opens the pull request from the review record, verifies the merge and closes the intent. Use when the last checkpoint returned PASS, or on "finish the branch", "open the PR", "ready to merge", "ship it".
version: 0.1.0
---

## What this station does

Everything the change has learned lands here or is lost here. This is the
only station that exercises the deterministic push gate, the only one that
writes memory, and the only one where the user is asked "is this what you
wanted" — decision point ③, answered off the blind-run report, never off
the diff.

It produces no new code. If something is missing, it goes back: to
`loom-code:review` for a checkpoint, to `loom-code:build` for a fix, to
`loom-code:write-plan` when what changed is the intent itself.

| Host | Command prefix |
|---|---|
| Claude Code | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/loom_checker.py` |
| Codex CLI | `python3 .codex/hooks/loom_checker.py` |

The Claude Code form is written out below; on Codex substitute the other
prefix and nothing else changes.

## 0. Contract check

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/loom_checker.py contract --require 1.0
```

Exit 0 continue; non-zero stop and report the mismatch (`contract.requires`)
— do not work around a contract that does not fit.

## 1. Preconditions — recompute them, do not trust the hand-off

Read `docs/loom/<change-id>/review.json` and the git state yourself. Four
facts, in this order:

1. **The latest round is a branch-end pass.** Its `scope` is `branch-end`
   and its outcome is `PASS` or `PASS_WITH_NOTES`. A wave-end pass is not a
   branch-end pass, however recent. If the last checkpoint was any other
   scope — or the branch grew a commit after it — call `loom-code:review`
   with scope `branch-end` now and come back with its verdict.
2. **The blind-run report exists** at
   `docs/loom/<change-id>/blind-run-report.md`. Without it there is nothing
   to accept, and step 2 has no material.
3. **The tree is clean.** `git status --short` prints nothing. An
   uncommitted file is work that was never reviewed.
4. **HEAD is the review-only commit** and `reviewed_sha` equals `HEAD^`:

   ```
   git show --name-only --pretty=format: HEAD
   git rev-parse HEAD^
   ```

   The first must print exactly `docs/loom/<change-id>/review.json`; the
   second must equal the `reviewed_sha` in that file. This is what makes
   the reviewed tree and the pushed tree the same object. If they differ,
   the branch moved after the review — go back to `loom-code:review`.

Also read `docs/loom/intent/<change-id>.md`: its `Acceptance` lines are what
step 2 is about, and its `status` must be `confirmed <date>`.

## 2. Decision point ③ — acceptance

<!-- gate: ship.no-push-before-acceptance -->
Nothing leaves the machine before the user has accepted. Present the
blind-run report first; push, pull request and merge all come after. A
branch pushed "so it is ready" and accepted afterwards has inverted the one
decision this station exists to carry.
<!-- /gate -->

Present `docs/loom/<change-id>/blind-run-report.md` in the user's own
language — the report's own structure, not a summary of it, and never the
diff:

- **Per Acceptance line**, in the intent's order: how I tried it, what
  happened, the evidence (the screenshot, the command output). "Line 1 of
  what you asked for: I did ___ in a clean checkout, and got ___ — here."
- **The fixed line about existing data**: what this change did to data the
  user already had. If it touched none, that sentence says so explicitly.
- **"I decided for you"**: every fork the agent settled on its own, marked
  `agent-decided`, plus every dismissed finding of severity `important` or
  worse. Each one in consequence form — what it means for them, not which
  mechanism produced it.
- **Open questions**: everything the run left uncertain.

Then wait. Three answers are possible:

| Answer | Where it goes |
|---|---|
| OK | continue to step 3 |
| Not OK, or a fix | back to `loom-code:build` as a new task, then a fresh `branch-end` checkpoint |
| The intent was wrong | back to `loom-code:write-plan`; the intent is re-confirmed at decision point ① before anything else |

Record what the user actually said. Append one entry per question asked to
`questions[]` in `review.json`, with `type: done` — this decision point asks
the "is it done" question and no other:

```json
{"decision_point": 3, "text": "Acceptance #2 — the export keeps your old file; OK?", "type": "done"}
```

A question that fits no type (`what` / `behaviour` / `done`, or the
consequence form of a one-way door) is a question the user cannot answer;
the review lens `user-judgment-leak` fails a station that asks one. Write
these entries into the review-only commit at step 3 — never into a commit
of its own.

## 3. Memory — what the repo must keep

Ask one question: what did this change teach that the next change here
would otherwise learn the hard way? An honest "nothing" is an answer;
inventing a lesson costs the next reader more than it saves.

Two carriers, both written now, before the push:

**Git trailers**, on the review-only commit at HEAD. Invoke
`loom-workflow:git-memory`, which owns the trailer format and composes them
from the diff and the branch's commits. When loom-workflow is not
installed, write them by hand in the format
`contract/templates/memory-README.md` states — one `Decision:` /
`Learning:` / `Gotcha:` line per fact, as the last block of the message,
with no prose after it:

```
git commit --amend --no-edit --trailer "Learning: <one fact>"
```

Amending is allowed **for this commit only**, and only for the message. The
parent does not change, so `reviewed_sha` still equals `HEAD^` and step 1's
fourth fact still holds. Amending anything else — a file, an earlier commit
— invalidates the review and sends you back to `loom-code:review`.

**Store entries**, when the lesson is durable rather than bound to this one
commit: a file under `docs/loom/memory/`, one fact per file, in the format
that store's own README defines (scaffolded from
`contract/templates/memory-README.md`). A durable practice, habit or
recurring gotcha belongs there; a decision about this change alone belongs
only in the trailer. Adding a store entry means the tree is dirty again:
commit it separately **before** the review-only commit, and re-run the
`branch-end` checkpoint, because step 1's fourth fact is now false.
Trailers cost nothing here; a store entry costs a checkpoint. Decide which
one the fact deserves.

The intent's `status` is **not** touched yet. It becomes `closed` after the
merge (step 6), because that is when it is true.

## 4. Push

Run the checker explicitly, then push:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/loom_checker.py push
```

It re-runs the package tests and the adversarial probes recorded in
`review.json` itself, in a clean tree at `reviewed_sha`, and believes only
the exit codes it observes. Expect it to take minutes; that wait is the
point of it. The same command runs again, unasked, from the host's
PreToolUse hook the moment the push command is issued — running it here
first only means you see the block before the tool call does.

Exit 0 → push the branch, by name, never bare:

```
git push -u origin <branch>
```

Any exit 1 prints `BLOCK <rule.id>: <reason>` on stderr. **Print that line
verbatim to the user and stop.** Do not re-run with flags, do not
`--no-verify`, do not adjust `review.json` to satisfy the rule — every rule
recomputes its fact, so the only way past it is to make the fact true at
the station that owns it:

| BLOCK | What is actually wrong | Go back to |
|---|---|---|
| `push.review-only-head` | HEAD touches more than `review.json` | `loom-code:review` — a new checkpoint |
| `push.reviewed-sha` | the branch moved after the review | `loom-code:review` |
| `push.review-schema` | `review.json` lost a declared key | `loom-code:review` |
| `push.open-findings-closed` | a finding is neither resolved nor dismissed | `loom-code:build` for the fix, then `loom-code:review` |
| `push.probes-package-tests` | the recorded test run does not reproduce | `loom-code:build` — the suite is red |
| `push.verdicts-ge-2` | one reviewer is not a review | `loom-code:review` |
| `push.reviewer-ne-implementer` | someone reviewed their own work | `loom-code:review` — dispatch an independent agent |
| `push.dismissed-by-reviewer` | an implementer waved away a finding | `loom-code:review` |

A rule that blocks twice means the plan is wrong, not the rule.

## 5. The pull request

Compose the body into a file and pass the file. Never paste a body inline:
a shell-quoted body loses the trailer footer, which is the one part of it a
machine reads.

Sources, in order — intent for what and why, `review.json` for how it was
checked, the blind-run report for what was observed:

<!-- pr-body-template -->
```
## Problem
<the intent's Problem, in the user's words>

## Acceptance
<the intent's Acceptance lines, each with the blind-run result: how it was
tried, what happened, the evidence>

## Review
Rounds: <n>. Reviewers: <agent ids and models from verdicts[]>.
Vendors: <vendors[]>. Probes: <package tests, blind run, adversarial cases —
kind and result, from probes[]>.
Findings: <n> raised, <n> resolved, <n> dismissed (each dismissal with its
reason and the reviewer who made it).

## What this did to existing data
<the report's fixed line>

## I decided for you
<the agent-decided forks and the important-or-worse dismissals, in
consequence form>

## Memory

Decision: <the decision this change made, and what it rules out>
Learning: <what the next change here should know>
```

<!-- gate: ship.pr-body-carries-trailer-footer -->
The last block of the body is the raw trailer footer, copied byte for byte
from the commit messages — `Decision:` / `Learning:` / `Gotcha:` lines under
a `## Memory` heading, and **nothing after them**. A post-merge workflow
greps the squash commit for exactly this shape; a trailer with any line
after it stops being the message's footer and the check fires on `main`,
where nobody is watching. Prose about the memory is not the memory: the
heading and the raw lines both have to be there. Length is not the test —
a single such line qualifies; a paragraph describing it does not.
<!-- /gate -->

Then:

```
gh pr create --title "<title>" --body-file <path>
PR_URL=<the url it printed>
```

The title is the change in one line, in the same conventional form the
commits use. The type whitelist CI enforces is `feat`, `fix`, `test`,
`docs`, `chore`, `refactor` — nothing else passes, and a scope is
mandatory.

Resolve the number once and reuse it: `gh pr view "$PR_URL" --json number
--jq .number`.

## 6. Merge, verify, close the intent

Merge when the user asks and CI is green. Read the body back from the pull
request itself rather than from the file written earlier — the file may be
in a worktree that step 7 removed, while the page always survives:

```
gh pr view <N> --json body --jq .body | gh pr merge <N> --squash --body-file -
```

`--body-file` is not optional. GitHub's default squash message for a
single-commit pull request keeps the title and drops the body, and the web
merge dialog can clear the body outright. Both losses are closed by passing
the body; neither is closed by hoping.

Then verify the carrier actually landed, on the squash commit on `main`:

```
git switch main && git pull --ff-only
bash loom-workflow/skills/git-memory/scripts/memory-grep.sh --verify-merged HEAD
```

Exit 0 — the footer survived. Exit 4 — the merge dropped it: say so, and
recover the memory from the pull-request page into a follow-up commit. Do
not treat a red post-merge check as noise.

Finally, close the intent. The status line cannot be written on the branch
(the merge has not happened yet there) and this station never commits to
`main` mid-flow, so it is written **after** the merge — by whoever touches
the repo next, which is usually this session:

```
git switch main && git pull --ff-only
# edit docs/loom/intent/<change-id>.md:
#   status: closed <YYYY-MM-DD> — PR #<N>
git add docs/loom/intent/<change-id>.md
git commit -m "docs(loom): close intent <change-id>"
```

An intent left `confirmed` after its pull request merged is a change that
looks unfinished to every later station, and to the decision map that
points at it. If the merge happens later, out of session, say this
explicitly in the final report so the user or the next change can do it.

## 7. Clean-up

After `verify-merged` exits 0, and not before:

```
git worktree remove <path-to-worktree>
git branch -d <branch>
git push origin --delete <branch>          # when the remote branch remains
```

`git branch -d` refuses a branch whose work has not landed — that refusal
is information, so never force it with `-D` to get past it.

If this repository ships a plugin, the merged version is not the installed
one. Three steps, in order, and the third is not optional because the
second reports success either way: update the plugin, reload plugins, then
verify the installed cache directory carries the new version number.

## Station summary

| station | artifact | who decides | checker | checkpoint |
|---|---|---|---|---|
| capture-intent | intent | user — decision point ① | `intent.schema`, `intent.product-no-identifiers`, `intent.needs-design-reason`, `intent.needs-design-recompute` | N/A |
| write-spec | spec | user — decision point ②, product only | `intake.confirmed`, `standing.product-principles-reject` | spec lens must pass before a plan exists |
| write-plan | plan | agent-decided (runs ① itself when loom-design is absent) | `intake.confirmed`, `intake.confirmed-behavior`, `intake.spec-pass` | calls review with scope `spec` |
| build | diff (commits, one `Task: <id>` trailer each) | agent-decided | none during build; writes the `dispatch[]` the push rules read | wave end past 8 files or 400 lines; right after an `after-task` task; at most 5 per plan |
| review | review | two or more fresh-context reviewers; no averaging | `push.verdicts-ge-2`, `push.reviewer-ne-implementer`, `push.dismissed-by-reviewer`, `push.open-findings-closed` | `branch-end` always runs |
| ship | diff / PR | user — decision point ③, reads the blind-run report | `push.review-only-head`, `push.reviewed-sha`, `push.review-schema`, `push.probes-package-tests`, and every review rule above, re-run at push | before push; a missing `branch-end` pass sends the change back to review |
| maintain | intent | agent (dedupe is mechanical) | `intent.schema`, `intent.needs-design-reason`, `intent.needs-design-recompute` | before hand-off to write-plan |
