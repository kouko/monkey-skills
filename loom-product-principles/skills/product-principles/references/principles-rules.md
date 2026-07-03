# PRINCIPLES.md authoring contract — principles-rules

This document is the authoring contract for a product's `PRINCIPLES.md` — the
product constitution. It defines the required sections, the load-bearing
falsifiable-check rule, and synthetic ✅/❌ examples.

**Consumed by:**
- `scripts/validate_principles_output.py` (the validator) — mechanically checks
  the two required sections exist and that every principle carries a check.
- the `product-principles` SKILL.md — the generator that writes `PRINCIPLES.md`
  reads this contract to know the shape and rules it must emit.

`PRINCIPLES.md` is **product-level** (one per product), **key-free**, **in-repo**,
and **git-diffable**. It is the supreme input that governs downstream
interface-design, spec-expansion (functional design), and code.

---

## Grounding — constitution / steering pattern

This follows the established **constitution / steering** pattern, not an
invented format:

- **GitHub Spec Kit `constitution.md`** — governing principles that are
  auto-read by every downstream command. The constitution is the first thing
  authored and every subsequent command reads it automatically.
- **Kiro steering `product.md`** with `inclusion: always` — the mechanism that
  loads product purpose/objectives as always-on context at every downstream
  stage.

We adopt the **pattern** (a falsifiable, always-on product constitution), not a
CLI dependency. The value of the pattern is conditional on the principles being
**checkable** — otherwise they are dead text. That condition is enforced by the
per-principle falsifiable-check rule below.

---

## Jurisdictions — Product / Design / Engineering

`PRINCIPLES.md` sections are organized by **jurisdiction** — which lens judges a
clause and what turf that clause covers:

| Jurisdiction | Content scope |
| --- | --- |
| **Product** | What the product is, for whom, and the success trade-offs it makes. |
| **Design** | How the interface behaves and feels — interaction posture, feedback/error stance, information density, accessibility floor, and tone where checkable. |
| **Engineering** | How it is built — stack choices, dependency posture, the conservative↔aggressive style dial, a test-rigor **CEILING** set above the TDD iron-law floor (never below it), and explicit negative decisions. |

---

## Required section — `## North Star`

The `## North Star` section states **two** things:

1. The product's **original goal** — the one-sentence reason the product exists.
2. A **concrete, checkable definition of "success"** — a condition you could
   actually evaluate against a shipped product, not an aspiration.

North Star is the product goal used as a **decision filter**. Keep it
lightweight — it is *not* a market/business-model/strategy document (that turf
belongs to a `PRODUCT-SPEC.md`).

**Format:**

```markdown
## North Star

**Goal:** <one sentence — why this product exists>

**Success:** <a concrete, checkable condition that means the goal is met>
```

**Synthetic example:**

```markdown
## North Star

**Goal:** Let a solo operator capture a structured note in under five seconds
without leaving the keyboard.

**Success:** A first-time user completes capture-to-saved in ≤5s measured on the
happy-path flow, keyboard-only, with zero mouse events.
```

---

## Required section — `## Product Principles`

The `## Product Principles` section lists **3–7 non-negotiable principles**. Fewer than
3 is not a constitution; more than 7 dilutes the "non-negotiable" weight and
nothing stays supreme.

### LOAD-BEARING RULE — every principle MUST carry a falsifiable check

Each principle **MUST** carry a **falsifiable check**: a concrete, testable
condition that could, in principle, be shown false by inspecting a real
artifact. The check is what makes a principle usable later as a downstream gate.

Use an inline `— check: <testable condition>` marker on every principle:

```markdown
## Product Principles

1. <principle statement> — check: <concrete, testable condition>
2. <principle statement> — check: <concrete, testable condition>
3. <principle statement> — check: <concrete, testable condition>
```

**Platitudes are rejected.** A statement with no `— check:` marker, or with a
"check" that no artifact could ever falsify (e.g. "feels good", "is high
quality"), is not a principle. The validator rejects a `## Product Principles`
section where any entry lacks a falsifiable check.

A good check is **observable** (you can point at where you'd measure it),
**binary or thresholded** (pass/fail or a number), and **artifact-bound** (it
refers to the flow, the output, the file — something that exists).

---

## Falsifiable vs platitude — synthetic ✅/❌ examples

These contrast a falsifiable principle against a platitude. Use only synthetic
phrasing; never name a real brand, company, customer, or product.

**Example 1**

- ✅ `Primary task completes in ≤3 steps — check: count steps in the happy-path flow`
- ❌ `Be delightful` — no check; nothing to inspect, nothing can falsify it.

**Example 2**

- ✅ `The primary flow is never blocked by a modal — check: grep the flow's screens for blocking modal dialogs; expect zero on the happy path`
- ❌ `Keep the experience smooth` — "smooth" is not observable; no artifact can be shown to violate it.

**Example 3**

- ✅ `Output is offline-readable — check: render the output with the network disabled; it must display its full content`
- ❌ `Be reliable` — no threshold, no artifact, no way to fail it.

The pattern in every ✅: a statement plus an `— check:` that names *where* and
*how* you would catch a violation. The pattern in every ❌: an adjective with no
falsifiable condition.

---

## Validator contract (summary)

`scripts/validate_principles_output.py` enforces, at minimum:

1. A `## North Star` section exists and is **non-empty** — at least one
   non-whitespace, non-heading line of body text appears under the heading
   before the next `##`.
2. A `## Principles` section exists with **3–7** principle **entries**, where an
   entry is a **top-level ordered-list item** (a line matching `^\d+\.\s` — i.e.
   `1.`, `2.`, …). Unordered bullets, nested items, and the ✅/❌ example lines
   are NOT counted as entries.
3. **Every** principle entry carries a falsifiable check. The check marker is the
   **literal token `— check:`** — an em dash (U+2014 `—`), a single space, the
   lowercase word `check`, then a colon — appearing **on the same line as the
   principle entry**. An entry without that exact marker fails validation.

**Generators MUST emit the exact `— check:` marker** (em dash, not a hyphen
`-`/`--`; lowercase `check:`; same line). This is the load-bearing lexeme the
validator keys on; emitting a hyphen or a different-cased word is a generation
bug, not a validator gap.

The validator is mechanical (section structure + the literal marker above); the
*quality* of a check (is it truly falsifiable, not a disguised platitude) is the
generator's and reviewer's responsibility, guided by the ✅/❌ examples above.
