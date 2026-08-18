---
name: decision-session
description: |
  Core sitting protocol of think-orbit — run a decision discussion so every reasoning step lands as a node file, branches carry named assumptions, and the DAG view is regenerated at each milestone. Normally reached via using-think-orbit; fires on 我要決定 / 決策推演 / 繼續上次的決策 / "help me decide" / "continue the decision".
source_language: en
tags: [decision-making, chain-of-thought, dag, reasoning, assumptions, part-1-draft]
---

# Decision session — the core sitting protocol

This is the sitting protocol of think-orbit: the user talks, and the
discussion lands as files. You normally arrive here from
`using-think-orbit`, which already resolved the project root `<root>`
and delivered the resume opening. If you somehow got here without a
`<root>`, ask for it once and continue — do not create one deep inside
the plugin.

The value of this plugin only appears **across sittings**. A decision
finished in one conversation needs no graph; three weeks later, the
user cannot remember which premise the conclusion stands on. Everything
below exists to make that premise findable.

## The family contract — three interrupt points

There are exactly three **kinds** of interrupt, and each one is a single
short exchange, never a form. The count is not three: you confirm the
GOAL once, but you ask for assumptions **each** time a branch opens and
confirm **each** DECISION — a two-fork sitting therefore interrupts more
than three times, by design.

| # | Interrupt | Why it earns the interruption |
|---|---|---|
| a | Confirm the GOAL — ask 「你要決定的是什麼」 and confirm the GOAL node you wrote | Wrong goal, wrong graph |
| b | When a branch opens, ask 「這條路踩在什麼上面？」 and have the user confirm the assumptions | Only moment the user knows why this path |
| c | Confirm the DECISION — you ask, the owner rules | This is the thing they take away |

Everything else is **silent file writing**. No forms, no per-node
confirmation, no progress narration. When the mechanical gate passes
you say nothing at all; it speaks only when it blocks.

Short paragraphs are the house style here — 2–4 sentences each, one
idea per paragraph. The gate checks this on node files, and this SKILL
follows the same rule.

## First sitting

The user pastes or points at sources — meeting notes, competitor pages,
a data export. Read them, then ask 「你要決定的是什麼」 and write the
answer to `<root>/nodes/<id>.md` as `type: GOAL` with an author-named
`id`, `seq: 1`, a one-line `summary`, and `inputs: []`. Ask the user to
confirm that GOAL node — this is interrupt (a).

From there the discussion runs normally and you write silently. Every
distinct reasoning step becomes one node file with a monotonic `seq`
and `inputs: [{ref, load_bearing}]` pointing at the nodes it stands on.
Use `CLAIM` for your own inference and `FACT` for a sourced statement
(which also carries `source` and a verbatim `quote`).

Procedural and social content produces **no node** — scheduling, "thanks",
"let me check", "shall we continue" are not propositions. Granularity is
judgment, not a rule: extract a node per distinct claim or fact you
actually use, not per paragraph of input.

`load_bearing: true` means this node collapses if that input falls;
`false` means it merely weakens. Tag every input — the gate rejects an
untagged one.

### When the discussion forks

The moment two paths appear, open a branch: set `branch` (a short id)
and `branch_type` on every member node. `exclusive` means the paths
compete and one will be chosen (走 A 方案 vs 走 B 方案); `complementary`
means they coexist and all get weighed (成本面／風險面／時程面).

Marking the type is not cosmetic. Between exclusive branches,
contradiction is the design intent, not a defect — a later reader who
does not know that will read your deliberate fork as a bug.

Then interrupt (b): ask 「這條路踩在什麼上面？」 and offer the
blind-spot checklist in `references/blind-spot-checklist.md` **once**,
right here. If the user waves it off, move on — never re-offer it at
the next node.

Draft **at most 3** assumption files per branch as
`<root>/assumptions/<id>.md` with `id`, `status: open`, `statement`,
`breaks_if`, and `branch` — the five the gate requires — plus `source`
where one exists (recommended, not gated). You draft, the user confirms —
one exchange, not a questionnaire. The cap of three is deliberate: it
forces ranking, and needing seven means the branch is not thought
through yet.

**Falsifiability check**: if you cannot answer "what event breaks this",
the assumption goes back for rewrite before it is written to disk. A
wish is not an assumption. `breaks_if` must name an observable event
(「主管在 10 月前通知預算下修」), not a mood.

### Reaching a DECISION

A `DECISION` node is written only when the user rules — interrupt (c).
You may say the paths are now comparable and ask which one they take;
you may never infer the ruling from the discussion's momentum.
Authorship is the whole point: `DECISION` is written by the owner's
ruling, and nothing else creates one.

## Minimal examples

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
Body text in short paragraphs. Two to four sentences per paragraph.
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
The quote is verbatim so the figure survives a dead link. Its source line names where to look again.
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
Why this follows from the goal and the churn figure. Second sentence.
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
```

## The gate — silent on pass

After writing or editing **any** node or assumption file, run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dag.py check <root>
```

On pass it prints nothing and you say nothing. On failure it prints one
line per violation: relay each line to the user in plain words, fix the
file, and run it again. Never suppress a violation, never hand-wave one
as cosmetic, and never edit the checker to make a file pass.

Silence on pass is what keeps this tool alive. A gate that speaks at
every node boundary gets switched off within a day.

## The view — regenerate, never read

After each milestone — GOAL confirmed, branch opened, DECISION written,
assumption broken — run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dag.py render <root>
```

Then tell the user where it is: `<root>/views/dag.md`. That file is the
chain of thought made visible, and it is the artifact that makes a
three-week-old decision readable again.

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
