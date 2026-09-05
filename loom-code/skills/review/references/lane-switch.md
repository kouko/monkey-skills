# Lane switch — the three-option prompt

Read this whenever the user asks to change verification lane, whether at
decision point ① or mid-build — "快速模式", "切換模式", "只過閘", "不用審",
or a plainer request to move faster or slower. `SKILL.md` §1 points here.

## Spoken mapping

The user speaks in plain terms; the station maps the words to a lane
name, fixed and never inferred fresh each time:

| What the user says | Lane |
|---|---|
| 快速模式 | `express` |
| 切換模式 | (asks which lane — present the prompt below) |
| 只過閘 | `gate-only` |
| 不用審 | `gate-only` |

## The three-option prompt

Present all three lanes in consequence form, every time, even the one
this change's delta forbids. For each lane, name what the user loses,
what stays, and an estimate:

| Lane | What you lose | What stays | Estimate |
|---|---|---|---|
| `full` | (current lane keeps everything) | two or more readers, the blind run, the branch-end adversary | — |
| `express` | one reader instead of two or more, the wave-end checkpoint | one reader, the blind run when an Acceptance line resists mechanical checking, one branch-end adversary | from this change's `review.json` `cost` block and the last change recorded in this lane |
| `gate-only` | every reader, the blind run | the probes, the package tests, one branch-end adversary | from this change's `review.json` `cost` block and the last change recorded in this lane |

Read the estimate column from `review.json`'s own `cost` block (`rounds`,
`dispatches`, `hours_plan_to_pr`) together with the most recent change
recorded in the same lane; write "no estimate" in the cell when neither
source carries a number. Mark, in the prompt itself, which lane the
change currently runs in.

The option this change's delta forbids stays listed, with its reason
named beside it — a checker, hook, agent-contract or `SKILL.md` path in
the delta forbids `gate-only`; any `gate`-typed path forbids both
`express` and `gate-only`. Dropping the forbidden option from the list
would hide the trade-off instead of naming it.

## The switch-line grammar

Only the user writes this line — an agent proposing it, or one found in
a plan, is the `user-judgment-leak` finding `references/lenses.md`
defines. It lands as a line in the intent file, and the switch commit's
message carries the identical line:

```
lane: <name> — switched <YYYY-MM-DD> by <name>, from <wave <n>|round <n>>
```

The switch applies to every round after the named `from`; the round
already in flight finishes in the lane it started under, and the
`intent` checker subcommand blocks a switch commit whose message omits
this line, the same way it blocks a `needs-design:` change with no
matching commit line.

## Recording the answer

Append the user's answer to `questions[]` in `review.json`, one entry
with `type: consequence`:

```json
{"decision_point": 1, "text": "Switching to express from round 3 drops one reader and the wave-end checkpoint — OK?", "type": "consequence"}
```
