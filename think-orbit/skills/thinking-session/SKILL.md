---
name: thinking-session
description: |
  Core sitting protocol of think-orbit — a thinking, planning, or decision discussion where every reasoning step lands as a node file, branches carry named assumptions, and the DAG view is regenerated at each milestone; a sitting may end in an open question or a plan outline, not only a DECISION. Enter via using-think-orbit, which owns intake — if entered directly, run the router's `<root>` ladder before anything else; fires on 幫我想 / 想一下 X / 想清楚 / 整理思路 / 規劃 X / 思考 / 我要決定 / 決策推演 / "help me think" / "think through X" / "plan X" / "figure out" / "help me decide".
source_language: en
tags: [decision-making, chain-of-thought, dag, reasoning, assumptions, part-1-draft]
---

# Thinking session — the core sitting protocol

This is the sitting protocol of think-orbit: the user talks, and the
discussion lands as files. You normally arrive here from
`using-think-orbit`, which already resolved the project root `<root>`
and delivered the resume opening. If you were entered directly, without a
`<root>`, run the router's own ladder first: the message names a
directory, else the working directory holding `nodes/` or `assumptions/`,
else ask once. Never create a root deep inside the plugin.

The value of this plugin only appears **across sittings**. A line of
thinking finished in one conversation needs no graph; three weeks later,
the user cannot remember which premise the conclusion stands on.
Everything below exists to make that premise findable.

A sitting need not end in a DECISION. A chain of CLAIM and FACT nodes
ending in an open question, or in a plan outline, is a complete and
valid record of the sitting. DECISION is one kind of ending, not the
only one — it is written only when the user actually rules.

## The family contract — three interrupt points

There are exactly three **kinds** of interrupt, and each one is a single
short exchange, never a form. The count is not three: you confirm the
GOAL once, you ask for assumptions **each** time a branch opens, and you
confirm a DECISION **whenever** one is reached — a two-fork sitting
therefore interrupts more than three times, by design, while a sitting
that never reaches a ruling interrupts on (a) and (b) only.

| # | Interrupt | Why it earns the interruption |
|---|---|---|
| a | Confirm the GOAL — ask 「你想弄清楚／規劃的是什麼？」 and confirm the GOAL node you wrote | Wrong goal, wrong graph |
| b | When a branch opens, ask 「這條路踩在什麼上面？」 and have the user confirm the assumptions | Only moment the user knows why this path |
| c | When a DECISION is reached, confirm it — you ask, the owner rules | This is the thing they take away |

Those three are the complete list of moments you stop and wait — no
forms, and no per-node confirmation. Everything outside them splits
into two kinds of speech, and only one of the two is banned.

**Progress narration stays banned.** 「我寫了節點 4」, 「正在整理中」 and
every other report of your own file activity is noise the user did not
ask for. When the mechanical gate passes you say nothing at all; it
speaks only when it blocks.

**Reasoning-aloud is required.** Before writing each node, say in one or
two sentences what you are about to claim and what it stands on. Say it
before the action, not after the thought — spoken first, the user can
stop a wrong step while stopping it is still cheap. You never wait for a
reply: you say the sentence, then you write the file.

This skill is a deliberate exception to a host-level "be terse, no
preamble, no narration" preference. Transparency is the product here,
not a side effect of it — a sitting whose reasoning was never spoken has
failed even when every file it produced is schema-clean. The exception
covers reasoning-aloud only, and never licenses progress narration.

Short paragraphs are the house style here — 2–4 sentences each, one
idea per paragraph. The gate checks this on node files, and this SKILL
follows the same rule.

## First sitting

The user pastes or points at sources — meeting notes, competitor pages,
a data export. Read them, then ask 「你想弄清楚／規劃的是什麼？」 and
write the answer — the question to answer, or the plan to shape — to
`<root>/nodes/<id>.md` as `type: GOAL` with an author-named
`id`, `seq: 1`, a one-line `summary`, and `inputs: []`. Ask the user to
confirm that GOAL node — this is interrupt (a).

When the opening message already states the goal, do not ask the
question again. Write the GOAL node from what the user said and ask a
one-line confirmation of the wording instead. Interrupt (a) is a
confirmation of the goal, not a ritual question.

From there the discussion runs normally: you say the sentence, then you
write the node. Every
distinct reasoning step becomes one node file with a monotonic `seq`
and `inputs: [{ref, load_bearing}]` pointing at the nodes it stands on.
`load_bearing: true` means this node collapses if that input falls,
`false` that it merely weakens; tag every input, because the gate
rejects an untagged one.

Use `CLAIM` for your own inference and `FACT` for a sourced statement
(which also carries `source` and a verbatim `quote`). A FACT body
restates and contextualizes the quote; any "this means…" inference
belongs in a CLAIM node that inputs the FACT.

Procedural and social content produces **no node** — scheduling, "thanks",
"let me check", "shall we continue" are not propositions. Granularity is
judgment, not a rule: extract a node per distinct claim or fact you
actually use, not per paragraph of input.

### The warrant duty — what every body's first paragraph answers

The first paragraph of every node body answers three things: which
load-bearing upstream node this step stands on, restated in prose — naming its `id`
inside a sentence that says what it claimed, never leaving the id to sit
alone in `inputs`; what this step adds on top of that upstream; and what
would collapse it. A reader three weeks later must be able to follow the
step without opening the upstream file. A node with no upstream — a
GOAL, or a FACT standing on its own `source` — says so and says why it
has none, and never invents an upstream to point at.

Write that paragraph even though the same reasoning was already spoken
aloud a moment earlier. The spoken sentence and the file are two faces
of one reasoning step and neither substitutes for the other — the
conversation is gone tomorrow, the file is what is left. The gate's
`input-narration` rule checks only that a load-bearing input's `id` appears in the
prose; the three answers above are what make that sentence worth
reading.

### When the discussion forks

The moment two paths appear, open a branch: set `branch` (a short id)
and `branch_type` on every member node. `exclusive` means the paths
compete and one will be chosen (走 A 方案 vs 走 B 方案); `complementary`
means they coexist and all get weighed (成本面／風險面／時程面).

Marking the type is not cosmetic. Between exclusive branches,
contradiction is the design intent, not a defect — a later reader who
does not know that will read your deliberate fork as a bug.

Each path then opens with one CLAIM node stating that path's position,
written before any of that path's assumptions. A branch box holding only
premises and no claim to support argues nothing, which is why the gate's
`branch-has-node` rule rejects a branch carried by assumptions alone.

A fork often becomes visible only after one path is already under way,
its nodes written with no `branch` field at all. Open the branch
retroactively: tag the existing path's nodes with the new `branch` id
and `branch_type`, and if none of them already states that path's
position as a CLAIM, write one now. Both paths end up inside the
branch; neither is left standing outside it.

The reason is what `exclusive` means: the paths compete for the same
decision, and a competitor sitting outside the branch is invisible in
the rendered DAG. A later reader then sees a one-sided argument and
cannot tell that an alternative was ever weighed. Retroactive tagging is
editing the record to match what was actually being reasoned about, not
rewriting history.

Then interrupt (b): ask 「這條路踩在什麼上面？」 and offer the
blind-spot checklist in `references/blind-spot-checklist.md` **once**,
right here. If the user waves it off, move on — never re-offer it at
the next node.

Draft **at most 3** assumption files per branch as
`<root>/assumptions/<id>.md` with `id`, `status: open`, `statement`,
and `breaks_if` — the four the gate requires — plus the `branch` id and
`source` where one exists (recommended, not gated). You draft, the user
confirms — one exchange, not a questionnaire. The cap of three is
deliberate: it forces ranking, and needing seven means the branch is not
thought through yet. Three premises supporting one stated position is
what the cap means — not three premises standing on their own.

A pivotal assumption that governs several branches is not filed under
one of them. Leave `branch` out and it is project-wide, outside every
branch's cap of three, and each node that depends on it cites it in that
node's own `inputs`. A later `break` then reaches every branch the
premise actually carries, instead of only the one it was filed under.

**Falsifiability check**: if you cannot answer "what event breaks this",
the assumption goes back for rewrite before it is written to disk. A
wish is not an assumption. `breaks_if` must name an observable event
(「主管在 10 月前通知預算下修」), not a mood.

### Endings — a DECISION is one of them

A `DECISION` node is written only when the user rules — interrupt (c).
You may say the paths are now comparable and ask which one they take;
you may never infer the ruling from the discussion's momentum.
Authorship is the whole point: `DECISION` is written by the owner's
ruling, and nothing else creates one.

When no ruling comes, the sitting still ends whole. Leave the chain
standing on its last CLAIM — an open question the user is still turning
over, or a plan outline they will act on — and say so plainly instead of
manufacturing a DECISION to round the graph off.

## Minimal examples

Node files carry `status: current | stale (only break writes stale)`, so
everything you write by hand is `current` and the `stale` value only ever
arrives through the break flow.

Write these four shapes from memory; `references/node-schema.md` is
the field SSOT and the place to check anything not shown here. Do not
restate the schema in conversation.

GOAL node — `nodes/q4_goal.md`:

<!-- example: nodes/q4_goal.md -->
```markdown
---
id: q4_goal
type: GOAL
seq: 1
summary: Pick the Q4 growth motion
status: current
inputs: []
---
One growth motion gets funded for Q4, and the two candidates on the table are a referral programme and an outbound team. This node fixes what the sitting is for, and every step below is judged against it. It stands on no upstream node, and it collapses only if the Q4 funding question itself is withdrawn.
```

FACT node — `nodes/churn_fact.md`:

<!-- example: nodes/churn_fact.md -->
```markdown
---
id: churn_fact
type: FACT
seq: 3
summary: Monthly logo churn is 5.0%
status: current
source: 2026-07 retention export
quote: "Monthly logo churn: 5.0%"
inputs: []
---
The 2026-07 retention export puts monthly logo churn at 5.0%, quoted verbatim above so the figure survives a dead link. This node stands on no upstream node: it is a measurement entering the graph, not an inference drawn inside it. It collapses only if the export is restated or withdrawn.
```

CLAIM node with inputs — `nodes/referral_scales.md`:

<!-- example: nodes/referral_scales.md -->
```markdown
---
id: referral_scales
type: CLAIM
seq: 4
summary: Referral motion scales faster than outbound here
status: current
branch: b_referral
branch_type: exclusive
inputs:
  - {ref: q4_goal, load_bearing: true}
  - {ref: churn_fact, load_bearing: false}
---
This stands on q4_goal, which asked which growth motion Q4 should fund, and answers it with the referral path. What it adds is a rate argument: referral capacity grows with the installed base, while outbound capacity grows only with headcount. It collapses if customers turn out to be unwilling to refer, which is the assumption filed under this branch, and the churn_fact figure only colours the comparison, so it is tagged non-load-bearing.
```

Assumption — `assumptions/customers_will_refer.md`:

<!-- example: assumptions/customers_will_refer.md -->
```markdown
---
id: customers_will_refer
status: open
statement: Existing customers are willing to refer
breaks_if: Two referral asks in a row are declined
source: 2026-08-14 1-on-1
branch: b_referral
---
The user named this in the 2026-08-14 1-on-1 as the thing the referral path rests on. It is filed under `b_referral` because it carries that path alone, and the CLAIM above is what it supports.
```

## The gate — silent on pass

After writing or editing **any** node or assumption file, run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dag.py check <root>
```

Run one `check` per written or edited file —
never one check for a batch of files. A batch check tells you the batch
is dirty, not which file is, and the boundary this gate protects is the
file you just wrote.

On pass it prints nothing and you say nothing. On failure it prints one
line per violation: relay each line to the user in plain words, fix the
file, and run it again. Never suppress a violation, never hand-wave one
as cosmetic, and never edit the checker to make a file pass.

Silence on pass is what keeps this tool alive. A gate that speaks at
every node boundary gets switched off within a day.

## The view — regenerate, never read

After each milestone — GOAL confirmed, branch opened, DECISION written, assumption broken, sitting ends on an open question — run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dag.py render <root>
```

It prints one line, `dag view: views/dag.md`; relay that path to the
user. That file is the chain of thought made visible, and it is the
artifact that makes a three-week-old decision readable again.

The view is a derived read model for the human.
**You never read any file under `views/`** — it is lossy and it goes
stale. When you need
the graph structure, recompute it from the frontmatter of `nodes/`,
`assumptions/`, and `research/`, or regenerate the view. The
prohibition is on the rendered file, not on the knowledge.

## Research rules

Full rules live in `references/research-rules.md`; the short form is
below. If the project docs already answer it, just infer. If one missing
external fact blocks you, verify with **one arm** (a single dispatch or
a single search — never a retry loop) and land the result as a `FACT`
node with `source` and a verbatim `quote`, then add it to the current
node's `inputs` with `load_bearing` set.

If a topic needs surveying, or the user explicitly asks for research,
write a standalone research note at `<root>/research/*.md` with `id`
and `claim`. Downstream nodes reference its `claim` line, not the whole
note — the body can be edited freely, and only a changed `claim`
concerns dependents.

> **Hard rule**: any external fact entering the reasoning must be
> findable in the docs. Verified in chat but not written down is not
> verified.

## Hand-offs

When the user says an assumption broke, or that the situation changed,
hand off to the `break-assumption` skill. Do not re-implement the break
flow here — that skill owns propagation, the impact view, and the rule
that the agent only raises its hand while the user declares the break.

Intake and the resume opening belong to `using-think-orbit`. The
resume opening (`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dag.py claims <root> --since HEAD`,
then restating the last DECISION and the open
assumptions) is the router's verb; this skill does not run it. If the
user arrives asking to start a whole new project, or to be reminded
where things stand, that is the router's job, not this one's.

## The user hand-edits files

The user may edit any file between turns — that is a feature, not a
race condition. At the start of every turn, re-read the files you are
about to reason about; never trust your memory of their contents.

Then run `check` again before you continue. A hand edit can break the
schema, and finding that at the next node boundary is exactly the
point of a mechanical gate.

## Not yet in Part 1

Mainline and per-branch views, compiling the winning path into a
proposal, and milestone git commits all land in Part 2. Say so plainly
if the user asks for them; do not improvise a substitute.
