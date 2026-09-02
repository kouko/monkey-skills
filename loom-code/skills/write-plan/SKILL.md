---
name: write-plan
description: |
  Turn a confirmed intent into a task plan at docs/loom/<change-id>/plan.md. Use when someone asks to plan, start, or implement a change; when an intent file exists but is not confirmed yet; or when there is no intent yet and the work is about to begin. This is the entry station for engineering changes, and the entry station for every change when loom-design is not installed.
version: 1.0.0
---

## What this station does

You take one intent — a short document saying what the user wants and how
they will know it is done — and produce `docs/loom/<change-id>/plan.md`: a
graph of tasks, grouped into waves, each with its files, its one failing
test, and its risk. You do **not** implement anything, and you do not ask
the user to approve the plan: how the work is split is your decision, and
you write down why.

When `loom-design` is installed, an upstream station (`capture-intent`)
has already interviewed the user and confirmed the intent. When it is not
installed, **you also run that confirmation yourself** — step 3 below.

Two names for the same command, because the checker lives in different
places on the two hosts:

| Host | Command prefix |
|---|---|
| Claude Code | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/loom_checker.py` |
| Codex CLI | `python3 .codex/hooks/loom_checker.py` (written into the repo by the scaffold, step 0b) |

Below, the Claude Code form is written out. On Codex, substitute the other
prefix; nothing else changes.

**Vocabulary you need.** `kind: product` means the user-visible behaviour
of a product changes — what someone using it reads, types, or sees
happen. `kind: engineering` is everything else: refactors, internal
plumbing, tooling, tests, docs. `<change-id>` is `<YYYY-MM-DD>-<slug>`,
where the date is the day the work starts and the slug is the intent's
title in kebab-case — for "six scripts share a git helper" started on
2026-09-02, `2026-09-02-scripts-share-git-helper`.

## What you will be asked, in plain words

Give the user this list if they ask what is coming. It is the whole list:
there are no other **decision points**. On Codex there is also one
non-decision authorisation stop, the first time this repo is used (step
0b) — it asks for permission to run, not for a decision about the work.

1. **"Is this what you want?"** — I restate the problem and what you will
   be able to do when it is done. You say yes, or you correct me.
2. **Any choice that is expensive to undo** — asked in the same message,
   as consequences ("from then on it only runs on ___, ___ per month"),
   never as jargon.
3. **Once per change, if a second AI command-line tool is installed here** —
   whether to use it as a second reviewer. Your answer is remembered and
   never asked again.
4. **If this is a product change and this repo has no product principles
   yet** — about ten minutes of questions, in the same conversation as
   question 1, confirmed together with it.
5. **Nothing about the plan itself** — the task split, the wave sizes and
   the review timing are mine to decide; each judgement call gets a written
   reason.
6. **At the end, acceptance** — you read a report that says, for every line
   of your Acceptance list, how it was tried and what happened, and you say
   OK or not OK.

## The whole station order

Read this table before answering any question about who does what. It
covers the change end to end, upstream stations included, for both install
shapes.

| Station | Artifact produced (path) | Who decides | Checker rules that can block, and when | Checkpoint |
|---|---|---|---|---|
| capture-intent | `docs/loom/intent/<change-id>.md` | User — **decision point ①** ("is this what you want?"). Absent `loom-design`: step 3 of this file does it | `intent.schema`, `intent.product-no-identifiers`, `intent.needs-design-reason`, `intent.needs-design-recompute` — when the intent is committed | none |
| write-spec | `docs/loom/<change-id>/spec.md` (only when `needs-design: yes`) | User — **decision point ②**, product only ("you type X and see Y"). Engineering: agent-decided. Absent `loom-design`: step 4 of this file writes a minimal spec and runs ② | `standing.product-principles-reject` blocks a product change with no ratified `PRINCIPLES.md`, when the spec is started | spec review (read + adversarial) must PASS before any plan is written |
| **write-plan** (here) | `docs/loom/<change-id>/plan.md` | Agent, always. Every judgement call carries a one-line reason | step 2, every change, before ①: `standing.warn` and `standing.silence` are notice-only and never block, `standing.product-principles-reject` blocks. Step 4, before the plan: `intake.confirmed`, `intake.spec-pass`, `intake.confirmed-behavior` | none of its own |
| build | commits (the diff); one commit per task carrying a `Task: <id>` trailer | Agent | none | end of a wave when the unreviewed change exceeds 8 files or 400 lines; immediately after any task the plan marked `review: after-task`; a wave containing an after-task task always ends with a checkpoint too, and that one reviews only the delta after the after-task review plus cross-task consistency |
| review | `docs/loom/<change-id>/review.json` — created here, at the first checkpoint (the spec review, or the first wave end); never written by write-plan | Agent — two or more fresh reviewers; their disagreement is recorded, not averaged | none directly; it writes the record the push rules read | every checkpoint; the end of the branch always; at most 5 during build |
| ship | pull request and merge (git) | User — **decision point ③**: they read the blind-run report, not the diff | `push.review-only-head`, `push.reviewed-sha`, `push.open-findings-closed`, `push.probes-package-tests`, `push.verdicts-ge-2`, `push.reviewer-ne-implementer`, `push.dismissed-by-reviewer`, `push.review-schema` — on `git push`, `gh pr create`, `gh pr merge` | the end-of-branch checkpoint must have passed first |
| maintain | a new or updated `docs/loom/intent/<change-id>.md` | Agent turns an incident into an intent; the user then answers ① for that new change | `intent.schema` and the rest of the `intent.*` family, when that intent is committed | none |

Two install shapes, one table: with `loom-design` the first two rows are
run by its stations; without it, rows 1 and 2 are steps 3 and 4 of this
file, and the user sees exactly the same questions.

---

## Step 0 — Check the contract version

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/loom_checker.py contract --require 1.0
```

Exit 0: continue. Anything else, the rule is `contract.requires`: print
what the checker printed, tell the user to update `loom-code`, and
**stop**. Do not work around it.

On Codex the checker copy this command runs does not exist until step 0b
has written it, so on Codex do step 0b first and then this step; on Claude
Code the order is as written.

## Step 0b — Codex only: first contact with this repo

Skip this entirely on Claude Code, where the plugin supplies the checker
and nothing is installed into the repo.

On Codex CLI, the checker has to live inside the repo and be trusted once.
From the loom-code checkout — wherever the user installed it; there is no
plugin root variable on this host:

```
python3 <loom-code>/scripts/codex_scaffold.py --repo .
```

If it wrote or changed files, commit them with the message
`chore(loom): scaffold hooks <version>`, using the version the script
printed. Then prove the belt is actually live:

```
python3 <loom-code>/scripts/codex_scaffold.py --probe
```

The probe fires a command that **must** be blocked. If it was blocked,
continue to step 1. If it was not, an untrusted hook is being skipped
silently — print the script's BLOCK message and **stop**, in these words:

> 我已幫這個 repo 裝好 loom 的檢查；請在 Codex 裡輸入 `/hooks` 按一次授
> 權，我才會繼續。
>
> (I have installed loom's checks for this repo; please type `/hooks` in
> Codex and approve them once, then I will carry on.)

The user approves once, and the next command continues from step 1. This
is an authorisation, not a decision about the work — it is not a decision
point, and it happens once per repo, not once per change.

## Step 1 — Find the intent

The intent lives at `docs/loom/intent/<change-id>.md`. Look there first; if
the user named a change, match the slug.

**If an intent exists**, read it and go to step 2.

**If none exists**, there are two cases:

- `loom-design` is installed → this is not your station. Tell the user the
  change starts at `capture-intent`, and stop.
- `loom-design` is not installed → hand the user the template path,
  `contract/templates/intent.md` inside the `loom-code` plugin, and stop
  there **unless** the user wants to describe the change now. If they do,
  run step 3's restate-and-confirm as a short interview instead: ask what
  the problem is, who it hurts, and what they will be able to do when it
  is done; write the file yourself from their answers. Keep it short — an
  engineering intent is normally three to five lines, and writing it by
  hand beats interviewing. The user never hand-writes the file.

<!-- gate: write-plan.no-plan-without-confirmed-intent -->
**No plan is written without a confirmed intent.** If `status:` is not
`confirmed <date>` by the end of step 3, you stop; you do not draft a plan
"provisionally" and you do not confirm on the user's behalf. The checker
enforces the same rule at step 4 (`intake.confirmed`), so a plan written
early cannot be shipped anyway.

## Step 2 — Standing documents

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/loom_checker.py standing docs/loom/intent/<change-id>.md
```

Run this on **every** change, before decision point ①. Print its WARN lines
to the user **verbatim** — do not summarise them, do not add to them, and
do not act on them. `standing.warn` and `standing.silence` are notices;
they never block.

One outcome does block, `standing.product-principles-reject`: `kind:
product` in a repo with no ratified `PRINCIPLES.md` (ratified = the file
carries a `ratified-by: <name> <date>` line and a `## Non-negotiables`
section with at least three items). Then, if `loom-design` is not
installed, you run the interview in
`contract/templates/PRINCIPLES-interview.md` — **inside the same
conversation as step 3**, not as a separate stop. Open with the line that
template gives you, ask its questions until the answers are clear, write
`PRINCIPLES.md`, and restate it together with the intent in step 3. When
the user says yes, write the `ratified-by:` line. If `loom-design` **is**
installed, hand this to its `product-principles` tool instead.

## Step 3 — Decision point ①: restate and confirm

Run this only when the intent's `status:` is not already `confirmed`.

Compose **one message**. Everything below goes in it; you do not stop
twice.

1. **The restatement.** Problem and Acceptance in the user's own plain
   words — no file paths, no identifiers, no mechanism names:

   > You want ___, and when it is done you will be able to ___, ___ and
   > ___. Is that right?

2. **The one-way doors found so far**, in consequence form, per
   `references/one-way-door.md` — load that file before deciding whether a
   fork is one; the five classes and the four gates (check, measure,
   threshold, merge) are there, and a class (e) action — anything
   irreversible to the user's existing data — is asked even when there is
   no fork.

3. **The second-reviewer suggestion, at most once per change.** A second
   reviewer only counts if it is a non-interactive command-line tool from a
   **different model vendor than the host you are running on**: on Claude
   Code look for `codex` or `gemini`, on Codex look for `claude` or
   `gemini` (`which codex gemini` / `which claude gemini`). Never suggest
   the host itself. Include the suggestion only if
   `docs/loom/KICKOFF-DEFAULTS.md` has no `second-vendor:` line and such a
   tool is present. Say it in one plain sentence with the number in it:
   reviewing with a second vendor costs a few minutes and some quota, and
   when this system's own spec was reviewed, five of the seven serious
   problems were found by only one of the two vendors. Whatever the answer,
   record it in `docs/loom/KICKOFF-DEFAULTS.md` as
   `- second-vendor: <cli> | none — <reason> (<date>)` and never ask again;
   if that file does not exist yet, create it first from
   `contract/templates/KICKOFF-DEFAULTS.md`. If the line already exists,
   say nothing about it.

4. **The principles interview**, if step 2 demanded it.

**Every question in this message must be one of four kinds**, and you check
the list before sending:

- what do you want (the restatement),
- what will you see (visible behaviour — product only, and it belongs to
  decision point ②),
- did it work (acceptance — decision point ③),
- a one-way door in consequence form.

A question that fits none of them is a question the user cannot answer.
The review station has a dimension for exactly this, `user-judgment-leak`,
and it returns NEEDS_REVISION when it finds one. Ask nothing about spec
quality, task splitting, or review verdicts.

**On "yes":**

1. Write `status: confirmed <date>` into the intent.
2. Commit it. The message is `docs(loom): intent <change-id> confirmed`,
   and its body **must contain the `needs-design:` line verbatim** — the
   checker compares the two strings character for character.
3. Verify: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/loom_checker.py intent docs/loom/intent/<change-id>.md`
   Fix what it names and re-run until it exits 0.

**On "no" or a correction:** rewrite the intent, restate again. There is no
limit on rounds here; there is on guessing.

## Step 4 — Does this need a spec?

Read the intent's `needs-design:` line. It is `yes` when either holds:

- **(a)** the change touches a surface the user reads or types into — a
  GUI, a TUI, CLI arguments and output, an external API — and no
  `DESIGN.md` or ui-flows document already covers that surface; or
- **(b)** the behaviour is multi-state or multi-object, and there is no
  spec for it.

Otherwise it is `no`. The same rule applies to every `kind`; product and
engineering are not judged differently here.

You do not get the last word on `no`: the checker recomputes it
(`intent.needs-design-recompute`) against this repo's declared
interface-surface globs, and a diff that touches one of them while the
intent says `no` is blocked.

Worked example — Task A, "six scripts share a git helper": nothing the
user reads or types into changes, and it is one object with no states, so
neither (a) nor (b) holds → `needs-design: no — internal refactor, no
surface the user reads or types into`.

**`no`** — go to step 5. The plan carries the Current State Evidence
section instead of a spec.

**`yes`, and `docs/loom/<change-id>/spec.md` already exists** — go to the
intake check below.

**`yes`, spec missing, `loom-design` installed** — hand the change to its
`write-spec` station and stop.

**`yes`, spec missing, `loom-design` not installed** — you write a minimal
spec yourself, from `contract/templates/spec-minimal.md`:

- **Frontmatter** — `intent: <change-id>@<sha>`, where the sha is the
  commit you made in step 3 confirming the intent.
- **Requirements** — one `REQ-<n> — <name>` per line of the intent's
  Acceptance list, each ending `→ Acceptance #<n>`. One-to-one; do not
  merge two Acceptance lines into one requirement.
- **UI flows** — derived from the surfaces the intent says the user sees
  or types into: for each, the action and the system's response. `N/A` when
  the change has no such surface.
- **Design decision**, **Alternatives considered**, **Current state
  evidence** (Forward, Reverse, Error, Data, Boundary, each with a path and
  an anchor) — you fill these in. They are never shown to the user.

Print one line for the user: installing `loom-design` gets them a fuller
spec than this one. Then hand the spec to the **review** station under the
spec lens (read + adversarial). It must come back PASS or PASS_WITH_NOTES
before you write a plan; on NEEDS_REVISION, fix and send it round again.

<!-- gate: write-plan.product-spec-needs-confirmed-behavior -->
**A product spec needs `confirmed-behavior:` before it becomes a plan.**
When `kind: product`, decision point ② belongs to whoever wrote the spec:
if you wrote it, you run it. Present the Requirements and the UI flows in
plain words — "you type ___ and you see ___; when ___ happens it will
___" — and nothing from `## Design decision` down, ever. On "yes", write
`confirmed-behavior: <date>` into the spec frontmatter. On a correction,
rewrite and present again. Engineering changes skip this entirely.

Then let the checker confirm all of it:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/loom_checker.py intake write-plan <change-id>
```

Fix and re-run until it exits 0. It checks `intake.confirmed`,
`intake.spec-pass` and `intake.confirmed-behavior` — the three ways a plan
can be started too early. When `needs-design: no` there is no spec, and
the last two rules have nothing to check and pass; only `intake.confirmed`
can block.

## Step 5 — Write the plan

Write `docs/loom/<change-id>/plan.md` from `contract/templates/plan.md`.

**Task size.** A task is right-sized when all three hold: you can name the
first test — one that fails today and passes when the task is done — so the
implementer has a concrete RED to start from; it touches one module
boundary; and it can be done in isolation given only the dependencies it
declares. That first test is the starting point, not a ceiling: the
implementer writes as many tests as the behaviour has faces. If the task
needs tests for three unrelated behaviours, it is three tasks. Never size
a task by how long it will take.

**Shape.**

- Group tasks into **waves**. The hard limit is on reviews, not waves:
  **at most 5 checkpoints during build**, counting wave-end checkpoints and
  after-task ones together, with the fix rounds after a NEEDS_REVISION not
  counted. Derive the wave count from that budget; as a rough guide that
  leaves about five waves, and needing more usually means the change is too
  big — say so rather than nesting further.
- Task ids are `W<n>-<nn>` and are **stable**: once written, an id is never
  renumbered, because commits refer to it in their `Task: <id>` trailer.
- Dependencies go on the task line as `after: <ids>`. Tasks in one wave
  with no dependency between them run in parallel — but disjoint files are
  not enough: a shared symbol, a doc that mirrors code, or a
  producer/consumer pair stays sequential.
- Each task lists **files it will touch**, **the test written failing
  first**, and **its risk**.
- `review: after-task` marks a task that gets its own review immediately
  after its commit. Budget **2 per plan**; more is allowed, and each extra
  one carries a one-line reason on that task. A wave holding one still ends
  with its own wave-end checkpoint, and both count against the 5.

**Sections.**

- When `needs-design: no`, the plan opens with **Current State Evidence** —
  Forward, Reverse, Error, Data, Boundary, each with a path and an anchor.
  With a spec, that section lives there instead and the plan cites the spec.
- A closing **Risks** section for risks that span the whole plan. When
  there is no spec, this section is also where the answers to one-way-door
  questions live: one `user-decided — <what they chose and why>` line each,
  because with no spec there is no `## Design decision` to hold them.

**Forks you decided yourself.** Every one gets a one-line reason on its
task: what you chose and why. Any one-way door that surfaces now — after
decision point ① closed — is not a reason to go back to the user: take the
default, mark it `agent-decided`, and list it so the blind-run report can
show it at decision point ③.

<!-- gate: write-plan.post-decision-conservative-default -->
**After the decision point, classes (b), (c) and (e) have no free
default.** For those three classes in `references/one-way-door.md` — money
or a standing obligation, a limit on what the user can do later, and any
irreversible action on the user's existing data — you must take the
zero-obligation, reversible option that touches no existing data, and
record it as `agent-decided — not authorised, took the conservative
option`. Choosing a committing option unasked is never allowed, however
obvious it looks.

## Step 6 — Commit and hand off

Commit the plan with the message `docs(loom): plan <change-id>`. Then hand
the change to the build station — `loom-code:build` — which dispatches one
implementer per task and calls the review station at each checkpoint.
