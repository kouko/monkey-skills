---
name: capture-intent
description: |
  Interview the user and write a confirmed intent at docs/loom/intent/<change-id>.md. Use when someone describes a problem, desired outcome, feature idea, or recurring bug they want changed and no intent file exists yet — including when they have not chosen the product behaviour or implementation. This is the entry station for every change when loom-design is installed.
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

1. **Here (this station), "is this what you want?"** — I restate the
   problem and what you will be able to do when it is done. You say yes,
   or you correct me.
2. **Here, any choice that is expensive to undo** — asked in the same
   message, as consequences ("from then on it only runs on ___, ___ per
   month"), never as jargon.
3. **Here, only when the repo uses `second-vendor: ask` in the full lane**
   — whether to use another vendor for this change. `suggest` adds no
   question at capture-intent; write-plan owns its post-plan notice.
4. **Here, if this is a product change and this repo has no product
   principles yet** — about ten minutes of questions, in this same
   conversation, confirmed together with question 1.
5. **Later, at `write-spec`, product changes only** — "you type ___ and
   you see ___". Engineering changes skip it.
6. **Later, at the end** — you read a report that says, for every line of
   your Acceptance list, how it was tried and what happened, and you say
   OK or not OK.

Questions 5 and 6 belong to later stations. Nothing about how the work is
split, reviewed, or verified is ever put to you.

With `loom-code` installed on its own, questions 1–4 are asked by its
`write-plan` station instead, in the same words; the user sees no
difference. On Codex there is also one non-decision authorisation stop the
first time a repo is used — see the last section.

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
When prior conversation and evidence are already sufficient, draft directly.
Product intake may need a value decision; neither kind owes an intake question
quota, and existing decision points remain unchanged.

Cover, in the user's own words and with no jargon:

- **Who is affected**, and what they do today instead.
- **What "done" looks like**, written as things the user can do: "when
  this is finished I can ___". Each line must be provable by someone who
  has never seen the change, running it in a clean environment — that is
  what these lines are for. "The code is cleaner" is not one; "I can set a
  due date when I add a task and see it in the list" is.
- **Constraints** — anything already fixed: platform, language, a service
  they pay for, data they cannot move.
- **What is out of scope**, said out loud, so it does not creep back.
- **For product, the value case** — why now, why this rather than an
  existing tool, and what concretely loses the time. End with GO or NO-GO
  and one reason. A NO-GO is a real outcome: write the intent with
  `status: withdrawn — <reason>` and stop.

Use only user-supplied product claims. Add no product nouns, interfaces,
states, scope dimensions, or guarantees; `write-spec` owns unchosen decisions.

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
- **Open questions** — unresolved choices or missing required fields; the intent
  must remain `open`. Delegate a spec question or engineering question without
  answering it.

## Step 2 — Write the intent

Write intent and decision-point dialogue in the user's language. Plans, specs,
reviews, evidence, tests, and commits are English; blind-run reports and PR
bodies use the user's language.

Write `docs/loom/intent/<change-id>.md` from the `intent.md` template in
`loom-code`'s `contract/templates/` directory. Fill in:

- `originator: <the user's name>` — or `map:<id>` when a decision map
  raised it.
- `kind:` — `product` when the product's user-visible behaviour changes,
  `engineering` otherwise.
- `needs-design:` — `yes` when either holds, and the line always carries
  the reason:
  - **(a)** the change touches a surface the user reads or types into — a
    GUI, a TUI, CLI arguments and output, an external API — and no
    `DESIGN.md` or ui-flows document already covers that surface; or
  - **(b)** the behaviour is multi-state or multi-object and there is no
    spec for it.

  Otherwise `no — <reason>`. The same rule applies to both kinds. You do
  not get the last word on `no`: the checker recomputes it
  (`intent.needs-design-recompute`) against this repo's declared
  interface-surface globs, and a change that touches one while the intent
  says `no` is blocked later.

  Worked example — "CLI todo gains a due date": adding a due date changes
  the arguments the user types and the list they read back, and no
  ui-flows document covers due dates, so (a) holds →
  `needs-design: yes — CLI surface changes, no ui-flows cover due dates`.

- `status: open` for now; step 4 turns it into `confirmed`.
- `## Open questions` — the checker requires the section to be non-empty, so
  when the interview left nothing open write exactly `- none` under the
  heading. An empty section is a schema failure, not a statement that there
  are no questions.

After drafting, make one altitude pass: **Keep, neutralize, defer, reopen, or delete**.
Keep supported intent; neutralize overcommitment; defer behaviour to spec or
method to plan; reopen as defined by the confirmation gate below; delete
unsupported detail. This author self-check is not a review loop and creates no
fields, IDs, requirements, scenarios, or product behaviour.

Keep workflow authorisation outside product fields in its existing carrier.

Observable means GUI/TUI, CLI input/output, external API, or user-dependent
file output. Visible effects with an unknown surface and no spec require
`needs-design: yes` with a surface-neutral reason; internal files alone do not.

<!-- gate: capture-intent.product-problem-plain-words -->
<!-- The `gate:` markers in this file are prose gates: rules this station must follow, registered in the mechanism population and checked by cold-read evals — not checker rule ids. The checker rules are the `intent.*` / `standing.*` / `contract.*` ids named in the commands. -->
**A product Problem section is written in plain words only.** No file
paths, no function or class identifiers, no script filenames — the section
is what the user reads to recognise their own problem, and the checker
rule `intent.product-no-identifiers` rejects the file otherwise.
Engineering intents may name paths freely.

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

2. **The one-way doors found so far**, in consequence form. A one-way door
   is a choice that is expensive or impossible to undo. The reference that
   defines them lives in `loom-code`'s `write-plan` station — the file
   `one-way-door.md` in that skill's own references directory, which you
   cannot read from here; the classes are:
   - **(a)** hard to swap later — framework, language, database,
     authentication method, hosting platform, package manager;
   - **(b)** creates money or a standing obligation — paid services,
     third-party APIs needing an account, infrastructure to maintain;
   - **(c)** limits what the user can do in future — data formats, export
     ability, platform lock-in;
   - **(d)** sets the ceiling on output quality — model, algorithm or data
     source, when candidates differ on an axis the user feels (accuracy,
     speed, cost per run, language or format coverage, privacy);
   - **(e)** an irreversible action on the user's existing state —
     rewriting or deleting their data in place, changing an existing file
     format with no backup, sending their data off their machine. This one
     is asked **even when there is no fork at all**. Class (e) still yields to
   the **check** gate below: when the intent's Constraints or `PRINCIPLES.md`
   already pin how that existing data is handled, do **not** ask — restate
   the handling in consequence form inside this same message ("this will
   rewrite your ___, I am doing it the way you said: ___"), so the user sees
   it without being stopped for it.

   Four gates, in order: **check** the intent's Acceptance and Constraints
   and `PRINCIPLES.md` first — an axis already pinned there is not asked,
   you pick what complies and say which line pinned it; **measure** first
   when the candidates can be compared quickly on the user's own samples,
   then ask about the result, never about assumptions; **threshold** — for
   class (d), any axis differing by at least 20%, or the presence versus
   absence of money, privacy or coverage; **merge** — every one-way door of
   this change is asked once, here, inside this message. Never open an
   extra stop.

   The shape is fixed and carries no mechanism vocabulary:

   > Option A: from then on it only runs on ___, it costs ___ per month,
   > and swapping it out means rewriting ___. Option B: ___. I suggest A,
   > because ___.

   With no fork — class (e) — the same shape states the consequence and the
   safeguard: "this will rewrite your ___ into a new format and the old
   program will not read it; I will keep a backup at ___ first. Is that
   OK?"

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

**Every question in this message must be one of three types, or the
consequence form for one-way doors**: what do you want (the restatement), what will
you see (visible behaviour — that belongs to decision point ② at
`write-spec`), did it work (acceptance — decision point ③ at `ship`). A
question fitting none of them is a question the user cannot answer. Three
that fail the test, and what to do instead:

| Not a question for the user | Why | Instead |
|---|---|---|
| "Should the parser be recursive or table-driven?" | They would have to read the grammar and the call sites to have an opinion | Pick the one the existing code already uses; note the reason |
| "Should this live in `auth/` or a new `session/` module?" | A module boundary is only visible from inside the code | Follow the repo's existing boundaries; note it |
| "Should the new tests use pytest fixtures or a helper class?" | The answer is whatever the suite already does | Read one existing test and match it |

The review station has a dimension for exactly this, `user-judgment-leak`,
and returns NEEDS_REVISION when it finds one.

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
