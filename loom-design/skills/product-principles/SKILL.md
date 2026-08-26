---
name: product-principles
# soft-lint 150-250 exceeded (329 rendered): retains three-jurisdiction principle-guidance triggers the corpus doesn't yet cover
description: >-
  Turn a sparse product idea into a PRINCIPLES.md constitution (falsifiable
  product/design/engineering principles). Use BEFORE design/spec/build, or
  when asked what principles should guide a product/design/engineering
  decision or trade-off. Design/spec critique → design-critic/completeness-
  critic. Triggers: 產品原則 / 設計原則 / 工程原則 / 產品憲章 / プロダクト指針.
version: 0.4.0
---

# product-principles

Turn a sparse product idea into one project-level, key-free, in-repo,
git-diffable **`PRINCIPLES.md` constitution**. Its falsifiable principles govern
interface-design, spec-expansion, and code, including headless / CLI / library
products. See `references/principles-rules.md` for the jurisdiction table.

## Executor model — who does what

You are the executor: probe, map canons, derive falsifiable principles, and
reject platitudes. There is no external runtime or API key; only the final
stdlib validators.

## Boundary — principles, not strategy

This produces product/design/engineering principles plus the target user, not
market, business-model, or strategy content. Why the product exists belongs in
`docs/loom/PURPOSE.md`; read it when present but do not author it. Stop at the
constitution—no TDD, code, or UI design.

**Tripwire — unanswerable grilling.** If problem/users answers would be
guesses, never fabricate principles. Route to `using-loom-design`
(user-insights) for evidence-backed needs mapping, then resume from its value
commitments.

## Procedure — construction flow (user-stated-first, canon-anchored)

Run Product, Design, then Engineering with the same shape:

```
user states direction (their own words)
  → probe per question set (propose-then-react on stalls)
  → 2-3 canon candidates + fit/tension notes  → user decides
  → write: anchors (version-pinned) + deviation ledger
          + falsifiable principles
  → per-section read-back  (… final total read-back at the end)
```

### Step 1 — Read the authoring contract

Read **`references/principles-rules.md`** before writing. It defines exact
section formats, counts, examples, and the load-bearing same-line literal
`— check:` marker. The artifact MUST follow it exactly.

### Step 2 — User states first, then probe

The user states direction **first, in their own words**, including the idea and
**target user**. Then read and use **`references/question-sets.md`**: Product's
8 questions, the Design expert lane for a **design stance**, and Engineering's
5 questions plus tech-stack slot for an **engineering stance**. "Delegate to
agent" is always legal. Do not inline the questions here.

Probing rules:

- **Push until falsifiable**: each answer must reach a trade-off-bearing
  "X > Y" shape.
- **Propose-then-react on stalls** — when the user stalls, offer a concrete
  hypothesis to attack; **never repeat** the open question.
- **Cross-section answer propagation**: do not re-ask what an earlier decision
  answers; present the derived stance for confirmation-as-durable-principle.
- **Coverage self-check**: before leaving a section, **enumerate** its question
  set; each item was asked, propagated, or skipped with a reason.

Treat the lanes as one accumulating conversation, not independent interviews.
Product answers establish the user, values, exclusions, and success trade-offs.
Design and Engineering should expose only choices those answers have not
settled, turning prior commitments into proposed defaults for confirmation.
Preserve the user's vocabulary while sharpening it: clarification may make a
claim testable, but must not silently replace the domain object or trade-off
they named.

### Step 3 — Canon candidates (completeness audit)

When a section's stance is collected, **immediately** run the canon audit and
propose; this transition is mandatory. A **subagent** may run the audit.

- Propose 2-3 canon candidates with **fit/tension** notes from **≥2 distinct traditions**.
  One round contains **same-axis** alternatives answering the
  **same question**. Canons answering different questions are
  **complementary**: pin separate `## Anchors` rows, never one exclusive menu.
- **Per-round**, surface 1-2 **considered-but-rejected** candidates and reasons
  to the user. This applies to **every section**, not just the first.
- Before finalizing, consult all four lists as a **completeness audit**:
  `references/canon-product.md`, `references/canon-design-interaction.md`,
  `references/canon-design-visual.md`,
  `references/canon-engineering.md`. Re-check if all candidates sit in a
  popularity head. The user never sees the **raw lists**; Engineering's list
  is agent-only.
- **Tone & manner first.** Derive **3-5 tone & manner adjectives** from the
  product's values / **Product Principles**. They are the primary visual anchor
  and get their own **version-pinned `## Anchors` row**, pinned to the
  PRINCIPLES.md version that produced them.
- Run one **single Axis-A candidate round** (Axis A) from
  `references/canon-design-visual.md`. It is downstream of the tone & manner anchor,
  supplies mood / creative-direction inspiration, and is never a pick-one menu.
  The **surface-treatment axis** is decided downstream at the DESIGN station
  (`loom-design`), so separation is structural, not
  instructional; do not pin a surface-treatment row here.
- **Visual carve-out:** propose **3-5 canon candidates**, including 1-2 labeled
  divergent/exploratory choices, instead of the generic 2-3. They may challenge
  aesthetic stance but must remain **defensible** against Product Principles.
- **Anti-costume law:** a movement may enrich candidates but never overrides a PRINCIPLES value.
  Values win; e.g. low-stimulus still excludes Memphis.

Candidate notes must make the decision legible. For each option, state which
collected stance it fits, which commitment it tensions, and which default it
would establish. Rejection reasons must identify real mismatches, not mere
unfamiliarity. If canons on different axes both fit, retain complementary
anchors instead of forcing a false choice. Canon is recall insurance and a
source of tested defaults; it never outranks the constitution or authorizes
importing an entire doctrine wholesale.

When no candidate fits cleanly, explain the gap instead of stretching a famous
canon until it appears relevant. The bespoke escape hatch is preferable to a
misleading citation, provided its principles carry stronger checks and the
read-back makes the absent external default explicit.

### Step 4 — User decides

The user picks. **Mix allowed**; **bespoke** is a legal **escape hatch**, with
no third-party anchor and stricter falsifiability/read-back. Canons set defaults,
not product-specific trade-offs, so they never supply every principle.

### Step 5 — Write the sections

Write per `references/principles-rules.md`:

- **`## Product Principles`**: **3–7** non-negotiable top-level ordered entries;
  each has a same-line literal `— check:` that is observable, binary or
  thresholded, and artifact-bound.
- **`## Design Principles`** / **`## Engineering Principles`**: optional,
  **1–7** entries with the same marker. Emit only actually **committed** (or
  seeded agent-decided) clauses, never placeholders or an empty section. Test
  rigor is a **ceiling** above the TDD iron-law **floor**, never below it.
- **`## Anchors`** (likewise optional; omit when empty): chosen base canons,
  **version-pinned** with a non-empty edition/version.
- **`## Deviation Ledger`** (likewise optional; omit when empty): every canon
  break, with same-line `— reason:` + `— principle:` markers binding its
  justification and licensing Product Principle.

**Reject platitudes — push back.** A statement without an artifact-falsifiable
check is not a principle; ask for a checkable form. Fewer than 3 is not a
constitution and more than 7 dilutes it. See the contract's ✅/❌ examples.

**Before writing a `— check:` clause that requires guessing an unverified
fact, classify it via `references/knowledge-triage.md` FIRST.**

A principle must change a later decision. State the preference, its losing
side, and a check tied to an inspectable artifact. Thresholds need a named
measurement surface; binary rules need a clear pass/fail observation. Do not
hide unresolved evidence behind precise-looking numbers. If the project has
not committed a Design or Engineering clause, omit that jurisdiction rather
than filling it with generally desirable behavior. Anchors document chosen
external defaults; the Deviation Ledger records intentional exceptions, not
ordinary project-specific details.

**Draft-time count self-check:** count the entries **before presenting** (3-7
Product; 1-7 optional); if over, merge before showing—do not wait for the
validator.

**Artifact language:** repo convention wins; otherwise use the user's
**conversation language**.

**Anchor-consistency check:** every row must support the stance it cites; fix a
canon that contradicts that stance before read-back.

### Step 6 — Read-back

Read back **per-section**, then do a **final total** read-back. Surface the
artifact's exact **key terms** in its language so meaning shifts cannot hide in
paraphrase. Confirmation closes; corrections return to Step 5.

### Step 7 — Emit `PRINCIPLES.md` into the consumer project

Emit one project-level file at **`docs/loom/PRINCIPLES.md`** in the consumer
project, never per-feature copies.

### Step 8 — Validate, then fix

Run from the consumer root with the plugin script's absolute path; fix every
failure before declaring done:

```
cd <consumer-project-root>
argv: ["python3", "${CLAUDE_PLUGIN_ROOT}/scripts/principles/validate_principles_output.py", "<principles-file>"]
```

Pass argv directly to process execution; never through a shell. The validator
enforces the rules contract's structure, counts, markers, optional sections,
and legacy-heading migration; you remain responsible for check quality.

**Interactive sessions also run seed coverage.** Derive `seed-inventory.md`
from confirmed user's answers in Steps 2-4, then run
`argv: ["python3", "${CLAUDE_PLUGIN_ROOT}/scripts/principles/check_seed_traceability.py", "<principles-file>", "<seed-inventory-file>"]`.
Fix every miss and proceed only on **exit 0**.

The inventory and artifact are paired evidence: the inventory records named
inputs that must remain traceable; the artifact records resolved, deferred, or
bounded outcomes. A green structural validator does not prove semantic
coverage, and a green traceability checker does not prove a principle is truly
falsifiable. Both gates must pass; interactive work still ends with read-back.

## Headless / seeded mode

With **no user available**, every decision becomes **"delegate to agent"**:

- Pick canons and stances from caller intent; a **run-input seed** may answer
  any question and counts as user-stated.
- **Thin seed → refuse loudly.** If grounding principles requires guessing who
  needs what, return a structured **BLOCKED** refusal stating what the seed
  lacks and naming `using-loom-design` (user-insights) as the human remedy.
  Never fabricate a principle.
- **Inventory before drafting.** Write every seed-named canon, guideline,
  model, framework, language, library, format, technology, and deferred stance
  to `seed-inventory.md`, one entity per semicolon-separated token:
  `named_anchors:` for canons/traditions/stack and `deferred_items:` for
  undecidable stances; use `none in this seed` when empty. Never use `negative:`
  (it means must-be-absent). This is **write-only**; run no script.
- **Seed-traceability invariant (no silent drops)** — the headless mirror
  of the interactive coverage self-check: EVERY seed item must land in the
  artifact in at least one of a carrying principle, an `## Anchors` row, an
  Open Question (with a re-trigger condition, formatted per the
  `## Open Questions` contract in `references/principles-rules.md`), or an
  explicit `## Deviation Ledger` entry. A seed **item** is each individual
  stance, named canon, tech-stack choice, or deferred marker, even when
  several of them share one bullet or line of the seed — a walk at
  bullet granularity that drops stances packed inside one bullet
  violates the invariant. Seed content outside this skill's jurisdiction (per §Boundary
  — market / business-model / strategy turf, plus the product's original
  idea and success condition, now `docs/loom/PURPOSE.md`'s jurisdiction) is
  explicitly noted as **out-of-jurisdiction** during the seed walk — not
  silently skipped, and not laundered into a spurious Open Question. The
  target user is NOT out-of-jurisdiction — it still lands via a carrying
  `## Product Principles` (or `## Design Principles`) entry. A seed-named
  canon, tradition, or tech-stack choice is never out-of-jurisdiction
  either — that landing applies **only to the §Boundary-listed categories**
  plus the PURPOSE.md-bound idea/success pair named above; classifying a
  named canon or stack choice as "downstream spec" or "TECH-SPEC turf"
  during the seed walk is a **violation** of this invariant. Name it as
  such (the flow's own tech-stack slot proves stack choices are
  in-jurisdiction). A seed stance marked
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
`loom-design:design-system` / `interaction-flows` (generators),
`loom-design:spec-expansion` (§Governing constraint), and the critics'
principles lenses (`design-critic`'s conditional PRINCIPLES lens,
`completeness-critic` lens 6).
At the code station the conformance gate is **live**: loom-code's
whole-branch `code-reviewer` scores a `principles-conformance` dimension
(D8, writer≠judge) against these principles when the file is present.
This skill *writes* the constitution; enforcement lives in those
downstream gates.

**Next station.** Once `PRINCIPLES.md` is shipped, hand off to
`using-loom-design` for UI-bearing products, or to `using-loom-design`
to expand a feature directly when the product is headless / CLI-only.
