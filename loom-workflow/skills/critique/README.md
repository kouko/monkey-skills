# Critique

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Judge a proposal before it is built, through one of two lenses:
> `mode: proposal` triages a list into KEEP / DEFER / DROP;
> `mode: complexity` weighs one change deletion-first.

A user-invoked **gate skill**. You invoke it when a plan, backlog, or
proposed change looks bigger than the problem, and you want a critical
pass before anyone acts on it.

This README is for humans reading the skill on GitHub. The operational
file Claude actually loads is [`SKILL.md`](SKILL.md).

---

## Why does this skill exist?

Two failure modes, one root: nothing forces an item to earn its place.

**Charitable lists.** Asked to plan, Claude produces seven items, three
options, a P0/P1/P2 backlog that is really "ship everything" wearing
priorities. Most items carry weak grounding ("industry standard",
"future-proofing") and unclear necessity ("nice to have"). Without
pushback, the bloated proposal becomes the plan.

**The additive default.** Every change is framed as "what should we
add?" — rarely "what could we *not* add", almost never "what does this
make obsolete?". The codebase grows toward entropy: more files, more
flexibility for unknown futures, more lines nobody asked for.

`mode: proposal` catches the first. `mode: complexity` catches the
second.

---

## How does it work?

**Pick the mode first.** A list, plan, or prose recommendation with two
or more supporting claims → `proposal`. One specific change — refactor,
feature on existing code, debt cleanup, named greenfield feature →
`complexity`. Three or more distinct proposals: triage first, then run
`complexity` on each survivor.

### mode: proposal

Every item gets two values — **evidence grounding** (`GROUNDED` /
`HEURISTIC-OK` / `SPECULATIVE`) and **necessity** (`ESSENTIAL` /
`SPECULATIVE`) — which map through a triage matrix to `KEEP`,
`KEEP-WITH-CAVEAT`, `DEFER`, or `DROP`. A `DEFER` without an articulable
re-trigger condition falls through to `DROP`, so the deferral pile
cannot become a parking lot.

### mode: complexity

Three questions, in order, after loading one named mindset from
[`references/`](references/):

1. **Q1 — smallest end state.** Not the smallest change: what the
   codebase should look like afterwards, including "decline to build".
2. **Q2 — less total code?** Lines, functions, files, before and after.
   Growth is allowed but must be named and costed.
3. **Q3 — what can we delete?** Real, bundled deletions, not promises.

The verdict is one of `PROCEED`, `PROCEED-WITH-CAVEAT`, `RESHAPE`, or
`REJECT`.

---

## What it will not do

Assertion is not evidence; uncertainty is stated, never invented; a
`DROP` is never softened into a `DEFER` to be agreeable; and the gate is
never handed back to you to run yourself.

It also stays out of: simple Q&A, explanatory bullets with no advocated
action, trivial renames, shrinking an already-written diff, and
pre-completion verification.

---

## Attribution

`mode: complexity` descends from a chain of MIT-licensed upstream
projects (`reducing-entropy`). The full chain, what each link
contributed, and the license text live in [`NOTICE`](NOTICE) and
[`LICENSE`](LICENSE). The four bundled mindsets track canonical versions
under `domain-teams:code-team/standards/`.
