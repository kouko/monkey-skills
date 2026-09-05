---
name: ship
description: |
  Closes a development branch out: confirms the branch-end checkpoint passed, presents the blind-run report to the user for acceptance, writes the memory, runs the deterministic push gate, opens the pull request from the review record, verifies the merge and closes the intent. Use when the last checkpoint returned PASS, or on "finish the branch", "open the PR", "ready to merge", "ship it".
version: 1.0.0
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

On Codex, if `.codex/hooks/loom_checker.py` does not exist, **stop**: run
`loom-code:write-plan` step 0b (the scaffold and its trust probe; that station
writes the procedure out in `codex-first-contact.md`, under its `references/`)
first. Do not produce any
artifact without the checker. The file existing is not proof the hook runs:
an untrusted Codex hook is skipped in silence, and step 0b's trust probe is
what tells the two apart.

## 1. Preconditions — recompute them, do not trust the hand-off

Read `docs/loom/<change-id>/review.json` and the git state yourself. Four
facts, in this order:

1. **The latest round is a branch-end pass.** Its `scope` is `branch-end`
   and its outcome is `PASS` or `PASS_WITH_NOTES`. If the last checkpoint
   was any other scope — or the branch grew a commit after it — call
   `loom-code:review` with scope `branch-end` now and come back with its
   verdict.

   One case does not need a second run: when the last wave-end checkpoint
   ran at the commit that is still `HEAD^` and nothing has changed since,
   there is no delta for a branch-end round to look at, and re-reviewing an
   unchanged tree buys nothing. That round **is** the branch-end
   checkpoint — the review station records `scope: branch-end` on it rather
   than adding an empty round, and this precondition is met. Anything
   committed after it, review.json aside, and the exemption is gone.
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

The memory trailers and any store entry under `docs/loom/memory/` are
written in English regardless of the change's own language, while the
blind-run report and the pull-request body stay in the user's language,
since those two are what the user reads at decision point ③ and afterward.

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

Amending is allowed **for this commit only**. Two things may change in it:
the message (the trailers above) and `review.json` itself, to append the
`questions[]` entries step 2 recorded. Nothing else — the parent does not
move, the commit still touches only `review.json`, so `reviewed_sha` still
equals `HEAD^` and step 1's fourth fact still holds, and the checker
permits exactly this shape:

```
git add docs/loom/<change-id>/review.json
git commit --amend --no-edit --trailer "Learning: <one fact>"
```

Amending any other file, or an earlier commit, invalidates the review and
sends you back to `loom-code:review`.

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

Before the push, copy this change's pytest probes under `evidence/probes/`
into the repo's permanent test directory as byte copies, adjusting only
their path lines and keeping the evidence originals, whenever no existing
test in that directory shares a probe's test-function name; commit them
with a `Task:` trailer. Cold-read reports for docs or skill deltas never
graduate.

A permanent test that shares a probe's function name but not its body is
a name collision, not a duplicate — rename the probe copy rather than
dropping it.

Like a store entry, this graduation commit lands before the review-only
commit; commit it separately and re-run the `branch-end` checkpoint,
because step 1's fourth fact is now false.

The intent's `status` is **not** touched yet. It becomes `closed` after the
merge (step 6), because that is when it is true.

## 3.5 The nit batch

Before the push, collect every `nit`-severity finding recorded in
`review.json` since the last passing round and fix all of them in **one**
commit, docs/records only — never a behaviour change; a code change is not
a nit and goes back to `build`. That commit necessarily touches files other
than `review.json`, so `HEAD` is no longer review-only and the push gate
would block on `push.review-only-head` if pushed as-is. Three more steps
close the gap:

1. **The nit-batch commit.** Records/docs/wording only, as above.
2. **A confirmation round.** Resume each reader of the last passing round
   (same agent) and have each confirm, in one line, that the nit batch
   fixes its nits and nothing else changed. Record that confirmation as a
   verdict of a new round with `sha` equal to the nit-batch commit — one
   verdict in the small lane (the lane's one reader), both readers'
   verdicts in the full lane. No fresh reader, no blind run, no adversary
   for this round; the floor from the last passing round still holds
   because nothing but wording moved.
3. **A review-only commit.** Touching only `review.json`, moving
   `reviewed_sha` to the nit-batch commit — the same shape as step 7's
   commit above, so `HEAD` is review-only again and `reviewed_sha` again
   equals `HEAD^`.
4. **Push**, as usual, from this new `HEAD`.

The checker still re-runs the recorded probes at push regardless of the
nit batch — fixing wording never substitutes for a passing probe run.

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
| `push.probes-package-tests` | the recorded test run does not reproduce, or is not this repo's own test command | `loom-code:build` — the suite is red, or `docs/loom/KICKOFF-DEFAULTS.md` never said what the command is |
| `push.probes-adversarial` | fewer than 3 usable adversarial probes for this change's artifact types, or one exited non-zero when the checker ran it | back to `loom-code:review`, dispatch an adversary |
| `push.dispatch-covers-tasks` | (i) a commit touching code/skill/gate carries no `Task:` trailer (spec/intent/plan/docs commits owe none); or (ii) a `Task:` trailer on this branch names a task no implementer entry claims | (i) `loom-code:build` — the task that owns the work amends or re-commits with the trailer; (ii) `loom-code:review` — the dispatch record lost a writer |
| `push.second-vendor-honoured` | KICKOFF-DEFAULTS names a second vendor the round neither used nor recorded a `fallback` for | `loom-code:review` |
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
Vendors: <vendors[]>, plus any `fallback` a round recorded.
Findings: <n> raised, <n> resolved, <n> dismissed (each dismissal with its
reason and the reviewer who made it).

Probes — one line each, from `probes[]`, `<kind> — <command> — <result>`:
<every probe, verbatim; the command is the point of the line, because a
reader can re-type it, and a command that plainly runs nothing is visible
here before it is visible in production>

## Questions I asked you
<every `questions[]` entry, verbatim: `<decision point> — <text>`. A reader
who cannot recognise one of these as a question they could have answered
has found a leak of agent judgement into the user's lap.>

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

## 6. Close the intent, then merge, then verify

Close the intent on the branch, before the merge — the pull request
already has a number (§5), so the status line can be written now:

```
git commit -m "docs(loom): close intent <change-id>" \
  -- docs/loom/intent/<change-id>.md
```

The commit changes exactly one line, `status:`, from `confirmed <date>` to
`closed <YYYY-MM-DD> — PR #<N>`; nothing else in the file moves.

That commit needs its own checkpoint before it can be pushed. Call
`loom-code:review` again, scope `branch-end`, delta
`<reviewed_sha>..<close commit>`: two fresh reviewers under the docs and
user-judgment-leak lenses, each stating the delta is that one status line
and nothing else; every verdict carries `sha: <close commit>`; package
tests and adversarial probes are re-pinned there. No blind run is owed —
an intent-typed delta has no Acceptance line to walk, and the branch-end
blind-run report already covers the change. Then the review-only commit,
`reviewed_sha` set to the close commit, and push again.

Consequence: the commit right before a review-only commit may not touch
any intent file for a reason other than closing it — not decision point
①'s confirmation commit, not a new intent from `maintain`, not an
amendment; each of those goes in its own, earlier commit.
`push.review-only-head` blocks any other shape there and says so. Merging
before this sequence finishes leaves the intent looking unfinished on
`main`; say so in the final report if the session ends first.

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
git log -1 --format=%B <squash sha> | grep -E '^(Decision|Learning|Gotcha):'
```

Exit 0 — the footer survived, and the matched lines are what survived. Exit
1 — the merge dropped it: say so, and recover the memory from the
pull-request page into a follow-up commit. Do not treat a red post-merge
check as noise. When the memory was an honest "nothing", there is no footer
to find and this step is skipped, said out loud rather than silently.

When loom-workflow is installed, `loom-workflow:git-memory --verify-merged`
runs the same check with the trailer grammar it owns; prefer it, and fall
back to the grep above when it is not there.

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
| capture-intent | intent — `docs/loom/intent/<change-id>.md`; `PRINCIPLES.md` and `DESIGN.md` at the repo root are side outputs of the tools it calls | user — decision point ① | `intent.schema`, `intent.product-no-identifiers`, `intent.needs-design-reason`, `intent.needs-design-recompute` | N/A |
| write-spec | spec — `docs/loom/<change-id>/spec.md` | user — decision point ②, product only | `intake.confirmed`, `standing.product-principles-reject` | spec lens must pass before a plan exists |
| write-plan | plan — `docs/loom/<change-id>/plan.md` | agent-decided (runs ① itself when loom-design is absent) | `intake.confirmed`, `intake.confirmed-behavior`, `intake.spec-pass`, `intake.after-task-budget` | calls review with scope `spec` |
| build | diff — commits on the change branch, one `Task: <id>` trailer each | agent-decided | none during build; writes the `dispatch[]` the push rules read; a full-lane `code`- or `gate`-typed task is adversary-first, the adversary dispatched before the implementer | wave end when the unreviewed delta exceeds 8 files or 400 lines; immediately after an `after-task` task; ≤5 checkpoints during build, NEEDS_REVISION fix rounds not counted; branch end always |
| review | review — `docs/loom/<change-id>/review.json`, and `docs/loom/<change-id>/blind-run-report.md` from the blind run | fresh-context reviewers, one in the small lane, two or more in the full lane (§1); no averaging | `push.verdicts-ge-2`, `push.reviewer-ne-implementer`, `push.dismissed-by-reviewer`, `push.open-findings-closed`, `push.second-vendor-honoured` | `branch-end` always runs |
| ship | diff / PR — the pushed change branch and its pull request | user — decision point ③, reads the blind-run report | `push.review-only-head`, `push.reviewed-sha`, `push.review-schema`, `push.probes-package-tests`, `push.probes-adversarial`, `push.dispatch-covers-tasks`, and every review rule above, re-run at push | before push; a missing `branch-end` pass sends the change back to review |
| maintain | intent — a fresh `docs/loom/intent/<change-id>.md` | agent (dedupe is mechanical) | `intent.schema`, `intent.needs-design-reason`, `intent.needs-design-recompute`, `intent.product-no-identifiers` on a new intent | before hand-off to write-plan |

