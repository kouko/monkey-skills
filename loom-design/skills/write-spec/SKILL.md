---
name: write-spec
description: |
  Turn a confirmed intent into docs/loom/<change-id>/spec.md, confirm the visible behaviour with the user when the change is a product change, and hand the spec to loom-code's review station before any plan exists. Use when an intent says needs-design: yes and no spec exists yet, or when someone asks for a spec or a design of a change.
version: 1.0.0
---

## What this station does

Relative paths in this document are relative to this skill's own directory.

An intent already exists and the user has already said yes to it. You turn
it into one file — `docs/loom/<change-id>/spec.md` — that says what the
change must do, what you decided and why, and, when there is an interface,
what the user will see. For a product change you read two of its sections
back to the user in plain words and get a yes. Then the machines review it.
You never ask the user to grade the spec, and you never plan the work.

**Vocabulary you need.** `kind: product` means the user-visible behaviour
of a product changes — what someone using it reads, types, or sees happen;
`kind: engineering` is everything else. A **decision point** is one of the
few places the flow stops for the user: ① at the intent, ② here, ③ at
acceptance. `<change-id>` is `<YYYY-MM-DD>-<slug>`, and the intent file is
`docs/loom/intent/<change-id>.md`.

The file formats and the checker belong to `loom-code`; this station is one
good way to produce them. The shapes below are not negotiable.

## Station summary

| station | artifact | who decides | checker | checkpoint |
|---|---|---|---|---|
| capture-intent | intent | user — decision point ① | `intent.schema`, `intent.product-no-identifiers`, `intent.needs-design-reason`, `intent.needs-design-recompute` | N/A |
| write-spec | spec | user — decision point ②, product only | `intake.confirmed`, `standing.product-principles-reject` | spec lens must pass before a plan exists |
| write-plan | plan | agent-decided (runs ① itself when loom-design is absent) | `intake.confirmed`, `intake.confirmed-behavior`, `intake.spec-pass`, `intake.after-task-budget` | calls review with scope `spec` |
| build | diff (commits, one `Task: <id>` trailer each) | agent-decided | none during build; writes the `dispatch[]` the push rules read | wave end when the unreviewed delta exceeds 8 files or 400 lines; immediately after an `after-task` task; ≤5 checkpoints during build, NEEDS_REVISION fix rounds not counted; branch end always |
| review | review | two or more fresh-context reviewers; no averaging | `push.verdicts-ge-2`, `push.reviewer-ne-implementer`, `push.dismissed-by-reviewer`, `push.open-findings-closed`, `push.second-vendor-honoured` | `branch-end` always runs |
| ship | diff / PR | user — decision point ③, reads the blind-run report | `push.review-only-head`, `push.reviewed-sha`, `push.review-schema`, `push.probes-package-tests`, `push.probes-adversarial`, `push.dispatch-covers-tasks`, and every review rule above, re-run at push | before push; a missing `branch-end` pass sends the change back to review |
| maintain | intent | agent (dedupe is mechanical) | `intent.schema`, `intent.needs-design-reason`, `intent.needs-design-recompute`, `intent.product-no-identifiers` on a new intent | before hand-off to write-plan |

## What you will be asked, in plain words

This station makes **one** stop, and only for a product change:

1. **"You type ___ and you see ___"** — decision point ②. I read back the
   Requirements and the UI flows in your own words, one sentence per
   operation, and you say yes or correct me. There is no limit on how many
   sentences; there is a limit on what they may be about.
2. **Any choice that is expensive to undo**, folded into that same message
   as a consequence — never as jargon, never as an extra stop.

An engineering change is not stopped here at all: everything below the
Requirements is decided by me, with the reason written down, and you can
overturn any of it later. Nothing about how the work is split, reviewed or
verified is ever put to you, at this station or any other.

## Step 0 — Check the contract version

This station's artifacts are defined by `loom-code`'s contract package, so
refuse to run against a version that does not declare them.

Plugins cannot read each other's files, so there is no
`${CLAUDE_PLUGIN_ROOT}` path that reaches `loom-code` from here. Find its
checkout on this host:

| Host | Where `loom-code` lives |
|---|---|
| Claude Code | the plugin cache — `~/.claude/plugins/cache/<marketplace>/loom-code/<version>/`, one directory per installed version; take the newest |
| Codex CLI | `.codex/hooks/loom_checker.py` inside this repo, written by `loom-code`'s `write-plan` when it first met this repo |

Then run, with that directory in place of `<loom-code>`:

```
python3 <loom-code>/scripts/loom_checker.py contract --require 1.0
```

Exit 0: continue. Anything else, the rule is `contract.requires`: print
what the checker printed, tell the user to update `loom-code`, and
**stop**. Do not work around it and do not guess a path — if you cannot
find the checkout, say so and ask the user where `loom-code` is installed.

## Step 1 — Intake

```
python3 <loom-code>/scripts/loom_checker.py intake write-spec <change-id>
```

Exit 0 and you may write. Non-zero and you may not — fix what it names and
re-run:

- `intake.confirmed` — the intent's status line does not read
  `confirmed <date>`. An intent nobody has agreed to is not yours to spec;
  send it back to `loom-design:capture-intent`.
- `standing.product-principles-reject` — the change is `kind: product` and
  this repo has no ratified `PRINCIPLES.md` (a `ratified-by: <name> <date>`
  line and at least three `## Non-negotiables` items). This is the one
  standing-document outcome that blocks. It is not yours to fix here
  either: the principles interview belongs to decision point ①, so hand
  the change back to `capture-intent`, which runs the interview inside the
  same conversation and confirms it together with the intent. Never open a
  second stop for it, and never write `ratified-by:` on the user's behalf.

Then read what exists, because each one changes what you write:

- **`PRINCIPLES.md`** — its `## Non-negotiables` are constraints, not
  advice. They order the Requirements: a requirement that serves a
  non-negotiable comes first, and any Design decision that would breach
  one is not a fork you get to pick — say which line pinned it.
- **`DESIGN.md`** — the vocabulary and components the UI flows are written
  in. Name the components it names; do not invent a second word for a
  thing it already calls something.

Missing files print WARN lines from the checker's `standing` command. Pass
them through verbatim; they never block, and only a product change without
principles ever does.

## Step 2 — Write the spec

Write `docs/loom/<change-id>/spec.md` from `spec-minimal.md` in
`loom-code`'s `contract/templates/` directory. Every section is required —
`N/A — <reason>` is an answer, silence is not.

- **`intent: <change-id>@<sha>`** — the sha of the commit that confirmed
  the intent, not of HEAD. It is the version of the ask this spec answers.
- **`## Requirements`** — `REQ-<n> — <name>`, then one sentence of
  obligation ending `→ Acceptance #<n>`. One requirement per Acceptance
  line, in that order; do not merge two. Each must be provable by someone
  who has never seen the change: "the list shows the due date next to each
  task" is provable, "due dates are handled correctly" is not. The
  identifier rules — authored, never renumbered, never reused — are in
  `references/spec-forms.md`. One line of the worked example:

  ```
  REQ-2 — Due date on the list
    The list shows each task's due date beside its title → Acceptance #2
  ```

- **`## Design decision`** — what you are doing, what you are not, and
  why. Every fork you resolved yourself carries one sentence of reason and
  the tag `agent-decided`; every one-way door the user answered carries
  their answer and the tag `user-decided`. Never shown to the user.
- **`## Alternatives considered`** — what you rejected, one line of reason
  each. A spec with no rejected alternative usually means you found one
  design and stopped.
- **`## Current state evidence`** — five lines, each with a path and an
  anchor in this repo: Forward (where the flow starts today), Reverse (who
  calls it), Error (how it fails today), Data (what shape the data has),
  Boundary (where this change stops). For greenfield, say so on the line —
  `Forward: N/A — nothing exists yet` — rather than deleting it.
- **`## UI flows`** — every operation and the system's reaction, in the
  user's words. Grammar, the four variants every surface owes, and the
  `N/A` form are in `references/ui-flows.md`.

Forms: reference `references/spec-forms.md` before reaching for a table, a
state list or a diagram — it says which shape carries which content, and
carries the ten completeness questions the review station's
design-conformance lens will ask you anyway.

## Step 3 — Decision point ②, product changes only

Engineering changes skip this step entirely: no stop, everything
`agent-decided`, reasons written down. For `kind: product`, compose **one**
message.

<!-- gate: write-spec.no-design-decision-shown-to-user -->
**Nothing from `## Design decision` down is ever shown to the user.**
Requirements and UI flows only. Alternatives, evidence and the mechanism
of the change are not theirs to judge, and putting them in the message
turns a behaviour confirmation into a quality review the user cannot do.
<!-- /gate -->

1. **The behaviour, one sentence per operation**, from the UI flows:

   > 你下 ___ 會看到 ___；___ 的情況會 ___。對嗎？
   >
   > (You type ___ and you see ___; when ___ happens it will ___. Is that
   > right?)

   Then the Requirements in the same plain register — what they will be
   able to do, not what the code will contain.

2. **The one-way doors of this change**, in consequence form, in this same
   message. A one-way door is a choice that is expensive or impossible to
   undo. The reference that defines them lives in `loom-code`'s
   `write-plan` station — the file `one-way-door.md` in that skill's own
   references directory, which you cannot read from here; the classes are:
   **(a)** hard to swap later — framework, language, database,
   authentication, hosting, package manager; **(b)** creates money or a
   standing obligation — paid services, third-party APIs needing an
   account, infrastructure to maintain; **(c)** limits what the user can do
   later — data formats, export, platform lock-in; **(d)** sets the ceiling
   on output quality — model, algorithm or data source, when candidates
   differ on an axis the user feels (accuracy, speed, cost per run,
   coverage, privacy); **(e)** an irreversible action on the user's
   existing state — rewriting or deleting their data in place, changing a
   file format with no backup, sending their data off their machine, which
   is asked **even when there is no fork at all**.

   Four gates, in order: **check** the intent's Acceptance and Constraints
   and `PRINCIPLES.md` first — an axis already pinned there is not asked,
   you pick what complies and say which line pinned it; **measure** first
   when the candidates can be compared quickly on the user's own samples,
   then ask about the result, never about assumptions; **threshold** — for
   class (d), any axis differing by at least 20%, or the presence versus
   absence of money, privacy or coverage; **merge** — every one-way door of
   this change is asked once, inside this message. Never open an extra stop.

   The shape is fixed and carries no mechanism vocabulary:

   > Option A: from then on it only runs on ___, it costs ___ per month,
   > and swapping it out means rewriting ___. Option B: ___. I suggest A,
   > because ___.

   With no fork — class (e) — the same shape states the consequence and the
   safeguard, as UI flow 4's second sentence does: "this will rewrite your
   ___ into a new format and the old program will not read it; I will keep
   a backup at ___ first. Is that OK?"

**Every question in this message must be one of three types, or a one-way
door in consequence form**: what do you want, what will you see (this
station's own type), did it work. A question fitting none of them is a
question the user cannot answer — "should the state live in the store or
the component?" is not a behaviour question however it is phrased. The
review station has a dimension for exactly this, `user-judgment-leak`, and
returns NEEDS_REVISION when it finds one.

A one-way door that surfaces **after** this message is not a new stop: pick
a default, tag it `agent-decided`, and let the blind-run report disclose
it at decision point ③. For classes (b), (c) and (e) the default is not
free — take the option with zero obligation, that is reversible, and that
does not touch the user's existing data, and record
`agent-decided — no authorisation, conservative option`. If no such option
exists, that piece of work stops and is reported as not done.

<!-- gate: write-spec.product-visible-behaviour-confirmed-before-review -->
**A product spec does not reach the review station before the user has
confirmed its visible behaviour.** On "yes", write
`confirmed-behavior: <date>` into the spec frontmatter. On a correction,
rewrite the spec and present it again — there is no limit on rounds, and
you never write that line on the user's behalf.
<!-- /gate -->

**Record every question you asked**, as `{decision_point, text, type}` with
`type` one of `what` / `behaviour` / `done` / `consequence`. The spec has
no section for this list and inventing one would put a second schema next
to the contract's. The canonical carrier is the plan's `## Questions asked`
section, from which the review station copies it into `questions[]` in
`review.json`. So carry the list forward **verbatim in your hand-off
message** in step 4, together with anything `capture-intent` handed you,
and say it belongs in that section.

## Step 4 — Commit, review, hand off

1. Commit the spec with the message `docs(loom): spec <change-id>`.
2. Hand it to **`loom-code:review`** with scope `spec`. That lens is read
   plus adversarial: at least two fresh-context reviewers on the read,
   and a red-team pass over the spec itself. You are not one of them, and
   you do not review your own file.
3. **NEEDS_REVISION** — close each finding, commit, and send it round
   again as a new round. Nothing about this is negotiable by argument: the
   verdict moves when the file does.
4. **PASS or PASS_WITH_NOTES** — the spec part of the next station's
   intake is now satisfied, which you can see for yourself:

   ```
   python3 <loom-code>/scripts/loom_checker.py intake write-plan <change-id>
   ```

   `intake.spec-pass` reads the latest review round; for a product change
   `intake.confirmed-behavior` reads the line step 3 wrote.
5. Hand the change to **`loom-code:write-plan`**, naming the change-id and
   pasting the question list. Say that decision point ② has happened and
   is not to be run again, and that the plan itself is agent-decided —
   the user is not asked to approve it. The next stop the user sees is
   acceptance.

## On Codex CLI

Every step above is the same. Only the checker prefix differs:
`python3 .codex/hooks/loom_checker.py` — a copy that lives inside the repo
because Codex has no plugin root. If it is not there, `loom-code`'s
`write-plan` station writes it on first contact with a repo and asks the
user once to trust it; do not install anything from here.
