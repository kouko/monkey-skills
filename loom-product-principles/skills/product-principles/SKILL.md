---
name: product-principles
description: |
  Turn a sparse product idea into a PRINCIPLES.md project constitution — a north star + 3-7 falsifiable Product Principles, plus optional Design Principles and Engineering Principles, governing design/spec/code. Use BEFORE design/spec/build on a new product, and when the user asks what principles should guide a product/design/engineering decision or how to frame a trade-off. Triggers: product principles, project constitution, north star, 產品原則, 設計原則, 工程原則, 產品憲章, プロダクト指針, エンジニアリング原則. Not for critiquing an existing design or spec (design-critic / completeness-critic).
version: 0.2.0
---

# product-principles

Turn a **sparse product idea** into a single **`PRINCIPLES.md`** — the
**project constitution**. This is the **principles-first** layer: before any
interface-design, spec, or code, fix the product's *original goal* and its
*non-negotiable, falsifiable principles* as the supreme input every downstream
decision is checked against.

`PRINCIPLES.md` is **project-level** (one per project), **key-free**,
**in-repo**, and **git-diffable**. It is the cross-cutting **constitution** that
governs **interface-design, spec-expansion (functional design), and code** — and
it applies to **any** product, including pure-**headless / CLI / library** work
that has no UI at all. It is organized by **jurisdiction** — the required
**`## Product Principles`** section covers what the product is, for whom, and
the success trade-offs it makes; see `references/principles-rules.md` for the
full jurisdiction table.

## Executor model — who does what

**You (the agent running this skill) are the executor.** You supply the LLM
reasoning (eliciting intent, drafting the North Star, deriving falsifiable
principles, pushing back on platitudes). There is no external runtime and no API
key — the method rides the host agent you are already in. The only tool is a
stdlib validator you run at the end.

## Boundary — principles, not strategy

This produces **product design principles + the target user**, NOT a full
market / business-model / strategy document — that turf stays in a
`PRODUCT-SPEC.md`. The **North Star** here is the product goal used as a
lightweight **decision filter**, not a business plan. Stop at the constitution;
do not run TDD, write code, or design the UI — those are downstream stations
that *read* this file.

## Procedure — principles-first

### Step 1 — Read the authoring contract

Read **`references/principles-rules.md`** before writing anything. It is the
authoring contract: it pins the exact `## North Star` and `## Product Principles`
formats, the **load-bearing per-principle `— check:` falsifiable-marker rule**
(an em dash `—`, a single space, lowercase `check`, a colon — on the same line
as the principle), and the synthetic ✅/❌ examples. The emitted `PRINCIPLES.md`
**MUST** follow that contract exactly — the validator keys on the literal
`— check:` lexeme.

### Step 2 — Elicit the idea and the target user

Briefly elicit, from the user, **the product idea** and **the target user**
(e.g. "a keyboard-only capture tool for a solo operator"). Keep it short — a few
lines of intent is enough to seed the constitution; you are fixing direction,
not gathering a full requirements set. If the idea is too sparse to name a goal
and a target user, **ask** rather than invent one.

### Step 3 — Write `## North Star`

Write the `## North Star` section: the product's **goal** (one sentence — why
the product exists) **plus a concrete, checkable success condition** — a
condition you could actually evaluate against a shipped product, not an
aspiration. Use the format in the contract:

```markdown
## North Star

**Goal:** <one sentence — why this product exists>

**Success:** <a concrete, checkable condition that means the goal is met>
```

### Step 4 — Write `## Product Principles` (each with a falsifiable `— check:`)

Write the `## Product Principles` section: **3–7 non-negotiable principles**, as a
top-level ordered list, **each carrying the literal `— check:` falsifiable
marker** (em dash, lowercase `check:`, same line). A good check is **observable**
(you can point at where you'd measure it), **binary or thresholded**, and
**artifact-bound** (it refers to the flow, the output, or a file that exists).

```markdown
## Product Principles

1. <principle statement> — check: <concrete, testable condition>
2. <principle statement> — check: <concrete, testable condition>
3. <principle statement> — check: <concrete, testable condition>
```

**Reject platitudes — push back.** A statement with no falsifiable check, or a
"check" no artifact could ever falsify (e.g. "feels good", "is high quality"),
is **not** a principle. If the user offers one (❌ "be delightful", ❌ "keep it
smooth"), **push back and ask for a checkable form** (✅ "primary task completes
in ≤3 steps — check: count steps in the happy-path flow"). Fewer than 3 is not a
constitution; more than 7 dilutes the non-negotiable weight. See the synthetic
✅/❌ examples in `references/principles-rules.md`.

### Step 5 — Elicit design posture and engineering posture (optional)

Ask, briefly, whether the project has already **committed** to any
**design-posture** or **engineering-posture** decisions — see the jurisdiction
table in `references/principles-rules.md` for what belongs in each.

For `## Engineering Principles` specifically: any test-rigor decision is a
**ceiling** set *above* the TDD iron-law floor — never below it.

**Elicit, don't imagine.** Write a clause only for a decision the user
actually commits to right now — never invent placeholder clauses to fill out
a jurisdiction. If the user has no committed decisions in a jurisdiction yet,
skip it entirely for this pass.

**Reject platitudes — push back**, the same as Step 4: a clause with no
falsifiable `— check:`, or a check nothing could ever falsify, is not a
principle here either. See the Design and Engineering ✅/❌ examples in
`references/principles-rules.md`.

For each committed clause, write it under `## Design Principles` and/or
`## Engineering Principles` in the same format as Product Principles — **1–7**
top-level ordered entries, each carrying the identical literal `— check:`
marker:

```markdown
## Design Principles

1. <principle statement> — check: <concrete, testable condition>
```

```markdown
## Engineering Principles

1. <principle statement> — check: <concrete, testable condition>
```

**Never emit an empty section.** A jurisdiction with zero committed clauses
emits **no** heading at all — do not write `## Design Principles` or
`## Engineering Principles` with nothing under it just to "look complete."

### Step 6 — Emit `PRINCIPLES.md` into the consumer project

Emit the result as **`PRINCIPLES.md`** into the **consumer project** at
**`docs/loom/PRINCIPLES.md`** (the established
`docs/<toolkit>/` convention). It is **project-level — one file per project**,
not per-feature. Do not scatter it; the constitution is a single supreme file.

### Step 7 — Validate, then fix

Run the validator and **fix any flagged issue before declaring done**:

```
python loom-product-principles/scripts/validate_principles_output.py docs/loom/PRINCIPLES.md
```

It mechanically checks the two required sections exist and that **every**
principle carries the literal `— check:` marker (the path relative to this
skill dir is `../../scripts/validate_principles_output.py`). The validator checks
*structure*; the *quality* of each check (truly falsifiable vs disguised
platitude) is your responsibility, guided by the ✅/❌ examples in the contract.

## Downstream — the cross-cutting constitution

`PRINCIPLES.md` is the supreme, **always-on** input that governs every
downstream station — **interface-design, spec-expansion, and code** (incl.
**headless / CLI** products with no UI). It is **key-free** and **git-diffable**,
so it lives in the repo and reviews like code. Downstream stations *read* it as
a governing constraint, each via its own intake section:
`loom-interface-design:design-system` / `interaction-flows` (generators),
`loom-spec:spec-expansion` (§Governing constraint), and the critics'
principles lenses (`design-critic`'s conditional PRINCIPLES lens,
`completeness-critic` lens 6).
At the code station the conformance gate is **live**: loom-code's
whole-branch `code-reviewer` scores a `principles-conformance` dimension
(D8, writer≠judge) against these principles when the file is present.
This skill *writes* the constitution; enforcement lives in those
downstream gates.
