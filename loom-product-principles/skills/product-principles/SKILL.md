---
name: product-principles
description: |
  Turn a sparse product idea into a PRINCIPLES.md project constitution — a north star + 3-7 falsifiable Product Principles, plus optional Design Principles and Engineering Principles, governing design/spec/code. Use BEFORE design/spec/build on a new product, and when the user asks what principles should guide a product/design/engineering decision or how to frame a trade-off. Triggers: product principles, project constitution, north star, 產品原則, 設計原則, 工程原則, 產品憲章, プロダクト指針, エンジニアリング原則. Not for critiquing an existing design or spec (design-critic / completeness-critic).
version: 0.4.0
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
reasoning (probing, canon mapping, drafting the North Star, deriving falsifiable
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

**Tripwire — unanswerable grilling.** If the user cannot answer the
problem/users probing with evidence (they would be guessing at who
needs what), do not dead-end into a fabricated North Star: route to
`using-loom-discovery` (user-insights) for evidence-backed needs mapping
first, then resume this skill using its value-commitment output as the
seed for the North Star and Product Principles.

## Procedure — construction flow (user-stated-first, canon-anchored)

The flow runs **per section** — Product, then Design, then Engineering —
same shape each time:

```
user states direction (their own words)
  → probe per question set (propose-then-react on stalls)
  → 2-3 canon candidates + fit/tension notes  → user decides
  → write: anchors (version-pinned) + deviation ledger
          + falsifiable principles
  → per-section read-back  (… final total read-back at the end)
```

### Step 1 — Read the authoring contract

Read **`references/principles-rules.md`** before writing anything. It is the
authoring contract: it pins the exact section formats (`## North Star`,
`## Product Principles`, the optional jurisdictions, `## Anchors`,
`## Deviation Ledger`, `## Open Questions`), the **load-bearing per-principle `— check:`
falsifiable-marker rule** (an em dash `—`, a single space, lowercase `check`,
a colon — on the same line as the principle), and the synthetic ✅/❌ examples.
The emitted `PRINCIPLES.md` **MUST** follow that contract exactly — the
validator keys on the literal `— check:` lexeme.

### Step 2 — User states first, then probe

The user states their direction **first, in their own words**, unprompted
structure — including the product idea and the **target user**. Only then
probe, using the per-section question sets in
**`references/question-sets.md`** (Product: the generic 8-question set;
Design: the expert lane — the user states their **design stance** and you
map it onto canon; Engineering: the 5 stance questions + tech-stack slot,
which elicit the **engineering stance** — "delegate to agent" is a legal
answer to every one). Never inline the question text here — read the
reference.

Probing rules:

- **Push until falsifiable** — each answer must reach the "X > Y" shape:
  it could lose a trade-off.
- **Propose-then-react on stalls** — when the user stalls, offer a concrete
  hypothesis to attack; **never repeat** the open question.
- **Cross-section answer propagation** — before asking any question in a
  later section, check whether an earlier section's decisions already
  answer it. If so, do NOT **re-ask** — present the derived stance for
  confirmation-as-durable-principle instead.
- **Coverage self-check** — before leaving a section, **enumerate** its
  question set and verify each question was asked, propagated, or
  explicitly skipped with a reason. Do not trust recall: a dropped
  question (dogfood: Q5 "why not existing") is invisible without the
  enumeration.

### Step 3 — Canon candidates (completeness audit)

The moment a section's stance is collected, **immediately** run the canon
audit and propose candidates — do not idle waiting for a prompt; this
transition is mechanical, not optional. Dispatching a **subagent** to run
the audit is sanctioned.

- Propose **2-3 canon candidates** with **fit/tension** notes, drawn from
  **≥2 distinct traditions**. The candidates in one proposal round MUST be
  **same-axis** alternatives — answers to the **same question** (e.g. all
  "how is code organized"). Canons answering different questions (data
  ownership vs code layering vs UI pattern) are **complementary** — pin
  them as separate `## Anchors` rows; never present them together as one
  exclusive pick-one menu.
- Name 1-2 **considered-but-rejected** candidates and **surface** them to
  the user with reasons — the rejection list is the honesty device, not an
  internal note. This guard is **per-round**: it applies to **every
  section's** candidate round (Product AND Design AND Engineering), not
  just the first.
- Before finalizing, consult the four canon base lists as a
  **completeness audit** ("did I miss a closer tradition?"):
  `references/canon-product.md`, `references/canon-design-interaction.md`,
  `references/canon-design-visual.md`, `references/canon-engineering.md`.
  If every candidate sits in a list's popularity head, re-check.
- The user **never sees the raw lists** — only the 2-3 fitted candidates.
  The Engineering list is consumed only by you (agent decisions + briefing
  option generation).

### Step 4 — User decides

The user picks. **Mix allowed** across canons; "no good canon for this
aspect — this section is **bespoke**" is a legal **escape hatch** (a bespoke
section loses the third-party anchor and compensates with stricter
falsifiability + read-back). A canon settles conventions and defaults; the
product-unique trade-off tiebreakers can never come from canon — picking a
framework is *some* principles entries, never all of them.

### Step 5 — Write the sections

Write per the contract in `references/principles-rules.md`:

- **`## North Star`** — **Goal:** one sentence why the product exists +
  **Success:** a concrete, checkable condition (not an aspiration).
- **`## Product Principles`** — **3–7 non-negotiable principles**, a
  top-level ordered list, each carrying the literal `— check:` falsifiable
  marker on the same line. A good check is **observable**, **binary or
  thresholded**, and **artifact-bound**.
- **`## Design Principles`** / **`## Engineering Principles`** (optional,
  1–7 entries, same `— check:` marker) — write a clause only for a
  decision the user actually **commit**s to (or, in seeded mode, an
  agent-decided one — see below); never invent placeholder clauses.
  **Never emit an empty section**: a jurisdiction with zero committed
  clauses emits no heading at all. Any test-rigor clause is a **ceiling**
  above the TDD iron-law floor, never below it.
- **`## Anchors`** (likewise optional; omit when empty) — the chosen base
  canons, **version-pinned** (edition/version cell non-empty; canon drifts
  too — Material 2→3, HIG yearly).
- **`## Deviation Ledger`** (likewise optional; omit when empty) — every
  intentional break from an anchored canon:
  `— reason:` + `— principle:` markers binding the break to the
  product principle that licenses it. This is the guard against silent
  hybridization; unrecorded exceptions kill the anchor.

**Reject platitudes — push back.** A statement with no falsifiable check,
or a "check" no artifact could ever falsify (❌ "be delightful"), is not a
principle. Push back and ask for a checkable form (✅ "primary task
completes in ≤3 steps — check: count steps in the happy-path flow"). Fewer
than 3 is not a constitution; more than 7 dilutes the non-negotiable
weight. See the ✅/❌ examples in `references/principles-rules.md`.

**Draft-time count self-check**: count the entries in each jurisdiction
section **before presenting** a draft (3-7 Product; 1-7 optional sections);
if over, merge entries before showing the user — do not wait for the
validator to catch it.

**Artifact language**: the target repo convention wins when one exists;
absent one, write `PRINCIPLES.md` in the user's **conversation language** —
a designer/PM must be able to read their own constitution.

**Anchor-consistency check**: every `## Anchors` row must actually anchor
the stance it is cited for — a canon named as the anchor of a decision that
*rejects* that canon's direction (dogfood: "Local-First" cited for a
cloud+encryption choice) is a citation bug; fix it before read-back.

### Step 6 — Read-back

Read back **per-section** (after each section closes) and once more as a
**final total** read-back over the whole draft. The read-back must surface
the artifact's actual **key term**s — the exact nouns written in the
artifact, in the artifact's language — so a domain-meaning shift (dogfood:
user's 報價單/quote rendered as "Invoice") cannot hide behind a
conversation-language paraphrase. The user confirms or corrects; corrections
loop back into Step 5.

### Step 7 — Emit `PRINCIPLES.md` into the consumer project

Emit the result as **`PRINCIPLES.md`** into the **consumer project** at
**`docs/loom/PRINCIPLES.md`** (the established `docs/<toolkit>/`
convention). It is **project-level — one file per project**, not
per-feature. Do not scatter it; the constitution is a single supreme file.

### Step 8 — Validate, then fix

Run the validator and **fix any flagged issue before declaring done**.
The script lives in the PLUGIN repo; the artifact lives in the CONSUMER
project — resolve the script path to an absolute path and run from the
consumer project root:

```
cd <consumer-project-root>
python <resolved-absolute-path-to>/loom-product-principles/scripts/validate_principles_output.py docs/loom/PRINCIPLES.md
```

It mechanically enforces the contract summary in
`references/principles-rules.md` §Validator contract — required sections,
entry counts, the literal `— check:` marker on **every** entry, the
`## Anchors` / `## Deviation Ledger` / `## Open Questions` rules, and the legacy-heading
migration check (the path relative to this skill dir is
`../../scripts/validate_principles_output.py`). The validator checks
*structure*; the *quality* of each check (truly falsifiable vs disguised
platitude) is your responsibility.

**Interactive sessions ALSO run the seed-coverage checker.** After the
structural validator passes, also run
`check_seed_traceability.py <artifact> <inventory>` (path relative to this
skill dir: `../../scripts/check_seed_traceability.py`) against the
`docs/loom/PRINCIPLES.md` artifact and the seed-inventory document, fix
any miss line it reports, and **proceed only on exit 0** — mirroring the
same gate-then-proceed shape as `writing-plans/SKILL.md`'s validator
gating. Interactive sessions have no run-input seed to inventory ahead of
time, so **derive `seed-inventory.md` from the confirmed user answers**
(the entities named across Steps 2-4) BEFORE running this checker, using
the same format as §Headless / seeded mode's inventory-authoring step.

## Headless / seeded mode

When this skill is driven with **no user available** (a loom-pipeline
Segment 1 Workflow agent, a batch context), every decision point degrades
to its **"delegate to agent"** answer:

- You pick the canon candidates and stances yourself, seeded by whatever
  intent the caller supplied; a **run-input seed** may pre-supply answers
  to any question — a seeded answer counts as user-stated.
- **Thin seed → refuse loudly.** The no-fabrication rule is unconditional
  here too: if the seed is too thin to ground a North Star (you would be
  guessing at who needs what), return a **BLOCKED**-style structured
  refusal to the conductor — state what the seed lacks and name
  `using-loom-discovery` (user-insights) as the human-side remedy. Never
  fabricate a North Star to keep the run going.
- **Inventory authoring — BEFORE drafting.** Before writing any
  `PRINCIPLES.md` section, extract every seed-named entity (canon,
  guideline, model, framework, language, library, format, technology,
  or deferred/undecidable stance) into a `seed-inventory.md` file, one
  token per named entity, using the checker's oracle key format (the
  format contract in `../../scripts/check_seed_traceability.py`): a
  `named_anchors:` line for canons/traditions/tech-stack choices, a
  `deferred_items:` line for undecidable/deferred stances, each a
  `;`-separated token list, empty sentinel `none in this seed` when a
  key has nothing to list. **Never use `negative:`** — that key's
  semantics is must-be-**ABSENT** (the checker fails if a `negative:`
  token IS present), the opposite sense of an inventory, which lists
  what the seed DOES contain. This step is **write-only** — author the
  file with your own Write tool; do not run any script here.
- **Seed-traceability invariant (no silent drops)** — the headless mirror
  of the interactive coverage self-check: EVERY seed item must land in the
  artifact in at least one of a carrying principle, an `## Anchors` row, an
  Open Question (with a re-trigger condition, formatted per the
  `## Open Questions` contract in `references/principles-rules.md`), an
  explicit `## Deviation Ledger` entry, or — for North-Star-bound facts
  (the idea, the target user, the success condition) — the `## North Star`
  section. A seed **item** is each individual stance, named canon,
  tech-stack choice, or deferred marker, even when several of them share
  one bullet or line of the seed — a walk at bullet granularity that drops
  stances packed inside one bullet violates the invariant. Seed content
  outside this skill's jurisdiction (per §Boundary — market /
  business-model / strategy turf) is explicitly noted as
  **out-of-jurisdiction** during the seed walk — not silently skipped, and
  not laundered into a spurious Open Question. A seed-named canon,
  tradition, or tech-stack choice is never out-of-jurisdiction — that
  landing applies **only to the §Boundary-listed categories** (market /
  business-model / strategy-document content); classifying a named canon
  or stack choice as "downstream spec" or "TECH-SPEC turf" during the seed
  walk is a **violation** of this invariant. Name it as such (the flow's
  own tech-stack slot proves stack choices are in-jurisdiction). A seed stance marked
  undecidable/deferred (e.g. 無法判斷) MUST become an Open Question with a
  re-trigger — never dropped; every seed-named canon or tech-stack choice
  MUST land as a version-pinned `## Anchors` row; every seed stance MUST
  have a carrying principle — merging stances is fine, dropping one is not.
- **Seed-coverage gate — mechanical, not a self-report walk.** The
  item-by-item seed walk is no longer a self-report step here: Step 8's
  checker gate (`check_seed_traceability.py`, run against the
  `seed-inventory.md` written above) enforces this invariant
  mechanically after drafting — see Step 8. Do not additionally rely on
  memory to re-walk the seed; the pipeline runs the check.
- Record every choice you made alone with the literal marker
  **`(agent-decided)`**, appended at the **end of the same physical line**
  as the choice it tags — a `## Deviation Ledger` entry when it breaks an
  anchor, or the principle's `— check:` clause line otherwise — so a
  human can late-veto it.
- Read-back has no reader: mark it **deferred-to-human** in the run output
  instead of silently claiming confirmation. The deferred read-back is
  mechanical: grep `(agent-decided)` and walk the human through each hit.

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

**Next station.** Once `PRINCIPLES.md` is shipped, hand off to
`using-loom-interface-design` for UI-bearing products, or to `using-loom-spec`
to expand a feature directly when the product is headless / CLI-only.
