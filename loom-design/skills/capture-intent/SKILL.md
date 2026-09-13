---
name: capture-intent
description: |
  Capture and confirm a change intent. Use when someone wants a feature or change and no intent file exists yet.
version: 1.0.0
---

## What this station does

Relative paths in this document are relative to this skill's own directory.

Someone tells you what they want. You ask until you understand it, write
one short document — `docs/loom/intent/<change-id>.md` — restate it back
in their own words, and once they say yes, hand the change to the station
that plans it. You do not design anything, you do not plan anything, and
you never ask the user to judge the quality of your work.

## Artifact vocabulary

**Vocabulary you need.** `kind: product` means the user-visible behaviour
of a product changes — what someone using it reads, types, or sees happen.
`kind: engineering` is everything else: refactors, internal plumbing,
tooling, tests, docs. `<change-id>` is `<today YYYY-MM-DD>-<slug>`, where
the date is the day the work starts and the slug is the intent's title in
kebab-case — for "CLI todo gains a due date" started on 2026-09-02,
`2026-09-02-cli-todo-due-date` (the date is today's date, not the
example's).

The file formats and the checker belong to `loom-code`; this station is
one good way to produce them. Everything it writes is read back by
`loom-code`'s stations, so the shapes below are not negotiable.

## Station summary

| station | artifact | who decides | checker | checkpoint |
|---|---|---|---|---|
| capture-intent | intent — `docs/loom/intent/<change-id>.md`; `PRINCIPLES.md` and `DESIGN.md` at the repo root are side outputs of the tools it calls | user — decision point ① | `intent.schema`, `intent.product-no-identifiers`, `intent.needs-design-reason`, `intent.needs-design-recompute` | N/A |
| write-spec | spec — `docs/loom/<change-id>/spec.md` | user — decision point ②, product only; agent declares pre-build risk | `intake.confirmed`, `standing.product-principles-reject` | `required`: one independent `spec+adversarial` reviewer, no blind run; `not-required`: none |
| write-plan | plan — `docs/loom/<change-id>/plan.md` | agent-decided (runs ① itself when loom-design is absent) | `intake.confirmed`, `intake.confirmed-behavior`, `intake.spec-ready`, `intake.test-case-pair` | no formal plan review; invokes the required spec review only when it authored the spec |
| build | diff — commits on the change branch | agent-decided | task and integration tests | no formal review during Build; one closing review follows completed functional work |
| review | generated `docs/loom/<change-id>/attestation.json`, plus a blind-run report when needed | fresh-context reviewers; reviewer count comes from the installed Review policy | package suite and adversarial programs execute once during `finalize-review` | branch end, or again only after functional content changes |
| ship | diff / PR — the pushed change branch and its pull request | automatic for canonical intent authorization; one user decision for a legacy intent; merge is separate | `push.attestation` plus fast publication safety; no functional replay | before push; publication-only fixes reuse matching evidence |
| maintain | intent — a fresh `docs/loom/intent/<change-id>.md` | agent (dedupe is mechanical) | `intent.schema`, `intent.needs-design-reason`, `intent.needs-design-recompute`, `intent.product-no-identifiers` on a new intent | before hand-off to write-plan |

## What you will be asked, in plain words

Give the user this list if they ask what is coming. It is the whole list;
nothing else in the change stops for them.

1. **Here:** one message confirms the restated intent, every expensive-to-undo
   choice in consequence form, a product's new principles when needed, and —
   only for full-lane `second-vendor: ask` — whether to use another vendor.
   `suggest` adds no question at capture-intent; write-plan owns its post-plan
   notice.
2. **At `write-spec`, product only:** confirm visible behaviour ("you type
   ___ and see ___"). Engineering changes skip this.
3. **At the end:** accept or reject the report showing how each Acceptance
   line was tried and what happened.

Nothing about task splitting, review mechanics, or verification is put to the
user. With `loom-code` alone, `write-plan` performs this station's questions;
Codex may also need one first-use repository authorisation stop.

## Step 0 — Check the contract version

This station's artifacts are defined by `loom-code`'s contract package, so
refuse to run against a version that does not declare them.

Plugins cannot read each other's files, so there is no
`${CLAUDE_PLUGIN_ROOT}` path that reaches `loom-code` from here. Find its
checkout on this host:

| Host | Where `loom-code` lives |
|---|---|
| Claude Code | the plugin cache — `~/.claude/plugins/cache/<marketplace>/loom-code/<version>/`, one directory per installed version; take the newest |
| Codex CLI | the installed `loom-code` plugin directory; use its checker script |

Then run, with that directory in place of `<loom-code>`:

```
python3 <loom-code>/scripts/loom_checker.py contract --require 2.1
```

Exit 0: continue. Anything else, the rule is `contract.requires`: print
what the checker printed, tell the user to update `loom-code`, and
**stop**. Do not work around it and do not guess a path — if you cannot
find the checkout, say so and ask the user where `loom-code` is installed.

If the installed checker cannot be found on Codex, stop and ask the user to
install or update `loom-code`; do not create a repository-local copy.

## Step 1 — Interview

Read `references/interview.md`; ask only for missing required-field content.
Draft directly when already sufficient. No intake question quota applies.
Problems/outcomes are valid before choosing features or implementation.
Existing decision points remain unchanged.

Cover affected people and their current workaround; observable "when finished
I can ___" outcomes provable by a stranger in a clean environment; fixed
constraints; and explicit exclusions. For product, also cover why now, why not
an existing tool, and what loses the time. End with GO or NO-GO and one reason;
write a NO-GO as `status: withdrawn — <reason>` and stop.

**Every question you ask must be of type `what`** — what do you want, what
happens today, what would you be able to do. Nothing about how it should
be built. The test is concrete: if the user would have to read code to
answer, it is not a question for them — decide it yourself later and write
down why. Keep going until Problem, Proposed outcome, Acceptance,
Constraints and Out of scope can all be filled in without guessing.

Keep every field at intent altitude:

- **Problem** — present pain, affected people, and consequence; no diagnosis,
  file list, or fix. Put missing current behaviour, workaround, or consequence
  in Open questions; do not infer it.
- **Proposed outcome** — wanted capability or state; no complete scenarios,
  UI reactions, state transitions, or implementation design.
- **Acceptance** — numbered observable delivery outcomes with external
  pass/fail evidence a blind run can produce; no value claim, scenario, test step, UI placement,
  architecture, or task split.
- **Constraints** — already-fixed boundaries; no agent preference or
  speculative guardrail.
- **Value case** — for a product intent: beneficiary, urgency, existing alternative,
  displaced work, and GO/NO-GO. Count each missing answer separately;
  confirmation of other fields is not evidence. Omit for an engineering intent
  with obvious value.
- **Out of scope** — excluded capabilities, actors, systems, or data; no
  deferred implementation list.
- **Open questions** — only unresolved outcome/scope choices or missing required
  content; both block confirmation. Carry downstream spec/engineering questions
  in the hand-off, not this section.

## Step 2 — Write the intent

Write the intent and decision-point dialogue in the user's language; plans,
specs, reviews, evidence, tests, and commits are English; blind-run reports
and PR bodies use the user's language.

Write `docs/loom/intent/<change-id>.md` from the `intent.md` template in
`loom-code`'s `contract/templates/` directory. Fill in:

- `originator: <the user's name>` — or `map:<id>` when a decision map
  raised it.
- `kind:` — `product` when the product's user-visible behaviour changes,
  `engineering` otherwise.
- `needs-design:` — `yes` when either holds, and the line always carries
  the reason:
  - **(a)** the change touches a surface the user reads or types into — a
    GUI, a TUI, CLI arguments and output, an external API, or a file artifact a
    user or external system depends on — and no `DESIGN.md` or ui-flows
    document already covers that surface; or
  - **(b)** the behaviour is multi-state or multi-object and there is no
    spec for it.

  Otherwise `no — <reason>`. This applies to both kinds. The checker recomputes
  `no` (`intent.needs-design-recompute`) against the repo's interface-surface
  globs and blocks a mismatch.

  Example: a new uncovered CLI due-date surface is
  `needs-design: yes — CLI surface changes, no ui-flows cover due dates`.

- `status: open` for now; step 4 turns it into `confirmed`.
- `## Open questions` — the checker requires the section to be non-empty, so
  when the interview left nothing open write exactly `- none` under the
  heading. An empty section is a schema failure, not a statement that there
  are no questions.

The confirmation gate below performs the altitude pass after this list has
been filled.

<!-- gate: capture-intent.product-problem-plain-words -->
<!-- The `gate:` markers in this file are prose gates: rules this station must follow, registered in the mechanism population and checked by cold-read evals — not checker rule ids. The checker rules are the `intent.*` / `standing.*` / `contract.*` ids named in the commands. -->
**A product Problem section is written in plain words only.** No file
paths, no function or class identifiers, no script filenames — the section
is what the user reads to recognise their own problem, and the checker
rule `intent.product-no-identifiers` rejects the file otherwise.
Engineering intents may name paths freely.
<!-- /gate -->

## Step 3 — Standing documents

```
python3 <loom-code>/scripts/loom_checker.py standing docs/loom/intent/<change-id>.md
```

Print its WARN lines to the user **verbatim** — do not summarise them, do
not add to them, do not act on them. They never block.

One outcome does block, `standing.product-principles-reject`: `kind:
product` in a repo with no ratified `PRINCIPLES.md`. Ratified means the
file carries a `ratified-by: <name> <date>` line and a `## Non-negotiables`
section with at least three items. When that happens, run the interview in
`loom-code`'s `contract/templates/PRINCIPLES-interview.md` **now, in this
same conversation** — not as a separate stop and not as a question about
whether to do it. Open with the template's opening line, translated into
the user's language — the template's current English sentence is:

> "Before building a product feature, this repo needs a set of product
> principles first. I'll ask you a few questions to produce it (about ten
> minutes), then confirm it together with the intent."

Ask its questions until the answers are clear, write `PRINCIPLES.md` with
its `ratified-by:` line left pending, and restate it together with the
intent in step 4.

## Step 4 — Decision point ①: restate and confirm

Compose **one message**. Everything below goes into it; you do not stop
twice, and this is the only stop this station makes.

1. **The restatement.** Problem and Acceptance in the user's own plain
   words — no file paths, no identifiers, no mechanism names:

   > 你要的是 ___，做完後你可以 ___、___、___。對嗎？
   >
   > (You want ___, and when it is done you will be able to ___, ___ and
   > ___. Is that right?)

   For the current contract, automatic publication is the default. This same
   restatement explicitly says that answering yes authorizes a later non-forced
   push and Ready PR after Review and publication checks pass, while merge
   remains a separate decision. Say that the user may explicitly opt out before
   publication. Do not hide that consequence in mechanism language or add it
   after the user has answered. Write
   `publication: automatic — authorized <date> by <name>` only after that
   informed yes; an opt-out leaves the field absent.

2. **Every one-way door found so far**, in consequence form. These are
   expensive or impossible to undo: a hard-to-swap platform or foundation; a
   monetary or standing obligation; future limits such as formats, export, or
   lock-in; an output-quality ceiling the user feels (accuracy, speed, cost,
   coverage, privacy); or an irreversible action on existing state, including
   rewriting/deleting data or sending it off-device. Existing-state actions
   count even without a fork. If Constraints or `PRINCIPLES.md` already fix
   their handling, do not ask again; restate the pinned handling and consequence
   in this message so the user still sees it.

   Four gates, in order: **check** the intent's Acceptance and Constraints
   and `PRINCIPLES.md` first — an axis already pinned there is not asked,
   you pick what complies and say which line pinned it; **measure** first
   when the candidates can be compared quickly on the user's own samples,
   then ask about the result, never about assumptions; **threshold** — for
   class (d), any axis differing by at least 20%, or the presence versus
   absence of money, privacy or coverage; **merge** — every one-way door of
   this change is asked once, here, inside this message. Never open an
   extra stop.

   State options as user consequences and recommend one with a reason. With no
   fork, state the irreversible consequence and safeguard (for example, what
   is rewritten, what stops reading it, and where the backup is kept).

3. **The cross-model review question, only for `second-vendor: ask`.** Read
   `references/second-vendor.md` for mode routing and the availability
   probe. A missing line is initialized as `second-vendor: suggest`; it
   adds no question here. The downstream notice may explain that reviewing
   with a second vendor costs a few minutes and some quota, and that five of the seven
   serious problems in this system's own spec review were found by
   only one of the two vendors. When the defaults carry `second-vendor: ask`,
   use the reference's host-aware native question or fallback in this same
   message; the answer governs this change only. In the small lane omit this
   opt-in question; Review computes the reviewer floor later from the complete
   branch delta. A fixed CLI also adds no question.

4. **The principles confirmation**, if step 3 ran the interview — restated
   in the same message, confirmed by the same yes.

Questions may only ask what the user wants, what they will see (reserved for
decision point ② at `write-spec`), whether acceptance worked (decision point ③
at `ship`), or state one-way-door consequences. Decide implementation choices
from repo evidence and record the reason; asking the user is a
`user-judgment-leak` review failure.

**Write down every question you asked**, as `{decision_point, text, type}`
with `type` one of `what` / `behaviour` / `done` / `consequence`. The
intent file has no section for this list, and inventing one would put a
second schema next to the contract's. The canonical carrier is the plan's
`## Questions asked` section. So **you pass the list forward in your hand-off
message in step 5, verbatim**, and say that the receiving station must write
it into that section. A question asked and not recorded makes the flow look
quieter than it is.

<!-- gate: capture-intent.no-confirmed-without-restatement -->
**No intent becomes `confirmed` without the restatement being answered.**
After drafting, make one altitude pass: **Keep, neutralize, defer, reopen, or
delete**. Defer behaviour to spec and method to plan; delete unsupported
detail. This self-check creates no fields, IDs, requirements, scenarios, or
product behaviour.

Publication and second-reviewer authorisation never enter Problem, Proposed
outcome, Acceptance, Constraints, or Out of scope. Keep publication
authorisation in the intent's `publication:` frontmatter line and the question
list in the step-5 hand-off.

Visible effects with an unknown surface and no spec require
`needs-design: yes` with a surface-neutral reason; internal files alone do not.

Use only user-supplied product claims: add no product nouns, interfaces, states,
scope dimensions, or guarantees. Put only unresolved outcome/scope choices or
missing required content in Open questions; either keeps the intent `open`.
Carry downstream spec/engineering questions in the hand-off.
Complete Step 2's altitude pass before confirmation. A fork with materially
different outcomes for the user or scope needs an explicit answer; an accepted
restatement is insufficient; reopen it — move it to Open questions, stop confirmation,
and the intent must remain `open`. Only an explicit answer makes it
`user-decided`. Implementation-only choices defer as
`agent-decided`.
You do not write `status: confirmed` because the request seemed clear, and
you never confirm on the user's behalf. On "no" or a correction, rewrite
the intent and restate again; there is no limit on rounds here.

**On "yes":**

1. Write `status: confirmed <date>` into the intent. When the confirmed
   restatement explicitly authorizes automatic publication, also write
   `publication: automatic — authorized <date> by <name>`; never derive it
   from status or prose. When step 3 ran, write
   `ratified-by: <name> <date>` into `PRINCIPLES.md`.
2. Commit with the message `docs(loom): intent <change-id> confirmed`. Its
   body **must contain the `needs-design:` line verbatim** — the checker
   compares the two strings character for character.
3. Verify:
   `python3 <loom-code>/scripts/loom_checker.py intent docs/loom/intent/<change-id>.md`
   Fix what it names and re-run until it exits 0.
<!-- /gate -->

## Step 5 — Hand off

Branch: the intent may be committed on the trunk or on the change branch — this station does not create branches. `loom-code:write-plan` creates `<change-id>` from the trunk before the plan commit if HEAD is still on the trunk; everything after the intent lives on that branch.

Read the `needs-design:` line you wrote:

- **`yes`** → hand the change to `loom-design:write-spec`.
- **`no`** → hand it to `loom-code:write-plan`.

In the hand-off message, name the change-id and paste the list of
questions you asked, one per line as
`<decision point> — <type> — <text>`, saying it belongs in the plan's
`## Questions asked` section.

Say two things so the next station is not re-run by accident: `write-plan`
will **not** run decision point ① again, because `status:` is already
`confirmed` — it reads the intent and starts planning. And decision point
② — "you type ___ and you see ___" — happens at `write-spec`, for product
changes only; engineering changes go from here to a plan with no further
stop until acceptance.

## On Codex CLI

Every step above is the same. Resolve `<loom-code>` to the installed plugin
directory; never create or invoke a repository-local checker copy.
