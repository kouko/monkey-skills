# Brief — P2: principles-conformance lens in the existing critics

**Date:** 2026-06-17
**Touches:** `code-toolkit:requesting-code-review` (SKILL + code-reviewer agent) + `spec-toolkit:completeness-critic` (SKILL)
**Type:** doc/agent-prose (skill + agent markdown). No new gate engine, no new synced standard.

## Problem

(Axis 1 — JTBD) `product-principles-toolkit` produces a **PRINCIPLES.md** (North Star +
3–7 falsifiable principles, each carrying a `— check:` clause) that is declared to govern
**all** downstream design / spec / code. But **nothing downstream verifies conformance** —
the pipeline dogfood (2026-06-15) surfaced exactly this: principles governed every artifact,
yet no station checked whether the spec or the code actually honored them. A constitution
that is never enforced is decoration.

Job story: *When my project has a PRINCIPLES.md, I want the spec critic and the code review
to actually check the artifacts against it — so a principle I committed to (e.g. "介面極簡",
"must work offline") can't be silently violated or silently dropped downstream.*

Industry confirms the shape (Axis 4, WebSearch EN+JA): **Spec Kit's `/speckit.review`** is a
*constitution-aware quality gate* that "validates the implementation adheres to the project's
constitution"; Spec Kit also runs a **constitutional gate at plan time** where the LLM reads
the constitution and verifies compliance, documenting justified exceptions rather than silently
passing. Academic prior art: arXiv 2602.02584 *Constitutional Spec-Driven Development*.

## Users

(Axis 2) An agent (or kouko) running `requesting-code-review` on a branch, OR
`completeness-critic` on a spec draft, in a consumer project that **has a
`docs/product-principles-toolkit/PRINCIPLES.md`**. Most projects won't have one → the check
must degrade to a no-op N/A when PRINCIPLES.md is absent (no false findings, no noise).

## Smallest End State

(Axis 3 — Option A, user-confirmed: code-side full conformance + spec-side omission-framed)

**Asymmetric by design — each critic keeps its native question shape:**

1. **Code side (strong fit, Spec Kit prior art) — `requesting-code-review`:**
   - **code-reviewer agent**: add a 9th dimension **`principles-conformance`** to the
     `dimension_scores` block + the dimension→source mapping. It asks the *conformance*
     question: *does the branch diff VIOLATE any PRINCIPLES.md `— check:` clause?* Mapped to
     the **consumer's PRINCIPLES.md artifact** (NOT a code-team standard). Severity: a clear
     violation of a falsifiable check = 🟡 should-fix (or 🔴 if the principle is safety/
     security-bearing); ambiguous = 🟢 note. Graceful N/A when PRINCIPLES.md absent.
   - **requesting-code-review SKILL.md**: in the dispatch step, **discover**
     `docs/product-principles-toolkit/PRINCIPLES.md` in the consumer repo and **pass its path**
     to the reviewer with the conformance instruction. If absent, pass nothing (dimension N/A).

2. **Spec side (omission frame, respects the skill's absence-not-inconsistency boundary) —
   `completeness-critic`:**
   - Add a **6th lens** to the panel framed as **omission**, not violation:
     *"what principle-ENTAILED behavior did the spec OMIT?"* (e.g. PRINCIPLES.md says "must work
     offline" → hunt where the spec drops offline handling). This fits the skill's explicit
     rule (SKILL.md:143 — "you hunt absence; inconsistency is Spec Kit's job"). The lens reads
     PRINCIPLES.md as an additional input view; N/A no-op when absent.

3. **Path-discovery convention (shared):** `docs/product-principles-toolkit/PRINCIPLES.md` in
   the consumer project. Absent → the check is N/A (announced once, no findings).

## Current State Evidence

- **Forward (code side):** `code-toolkit/agents/code-reviewer.md:296-304` — 8-dimension
  `dimension_scores` block; `:339-346` — dimension→source mapping table. The 9th dimension +
  mapping row slot in here. `requesting-code-review/SKILL.md` §Process step 2 currently passes
  "diff range, paths to rubrics + checklists, branch context" — PRINCIPLES.md discovery + path
  pass-through is the addition.
- **Forward (spec side):** `spec-toolkit/skills/completeness-critic/SKILL.md:187-218` — the
  five lenses (NFR/security, Policy/legal/permissions, Missing object/actor, State
  completeness, Cross-object/system-layer). 6th lens appends here. Panel mechanics (fan-out /
  union / loop-until-dry, SKILL.md:105-141) are **lens-agnostic** → adding a lens needs no
  machinery change. Honesty boundary at `:143` ("hunt absence, not inconsistency") is why the
  spec lens is omission-framed.
- **Reverse (SSOT / drift — critical):** `domain-teams/skills/code-team/` has **NO `agents/`
  dir** (verified: only checklists/protocols/research/rubrics/SKILL.md/standards). The agent
  files live ONLY in code-toolkit; `distribute.py` injects a *baseline block* into them
  (`AGENT_BASELINE_TARGETS` includes `agents/code-reviewer.md`), and `verify-drift.py` checks
  only that **block**, not the dimension body. So the dimension list/mapping is **house content
  owned by code-toolkit** — adding a dimension there is drift-safe **provided the edit lands
  outside the injected baseline / rule-sheet block**. The new dimension maps to the consumer's
  PRINCIPLES.md (an artifact), so **no new synced standard** is added → `verify-drift.py` stays
  green. MUST run `verify-drift.py` after the edit to confirm. Fallback if it ever flags:
  instruct conformance purely via the SKILL.md dispatch prompt (SKILL.md is not synced).
- **Error:** PRINCIPLES.md absent → both checks announce "principles-conformance: N/A (no
  PRINCIPLES.md)" and emit no findings. No regression to existing dimensions/lenses.
- **Boundary:** code-team (a generic code-quality team) has no concept of product PRINCIPLES.md
  — adding a product-principles standard there would be wrong coupling. The check references the
  consumer artifact directly, keeping the coupling correct.

## Decision

Build Option A: a **conformance dimension** in the whole-branch code-reviewer (asks "does the
diff violate a `— check:` clause?", mapped to the consumer PRINCIPLES.md, drift-safe house
edit) + an **omission-framed principles lens** in completeness-critic (asks "what
principle-entailed behavior is the spec missing?", respecting its absence-not-inconsistency
boundary) + a shared path-discovery convention (`docs/product-principles-toolkit/PRINCIPLES.md`,
N/A no-op when absent). We will **NOT** build a new gate engine/skill, **NOT** add a synced
standard to code-team, **NOT** touch the per-task code-quality-reviewer (whole-branch only,
matching Spec Kit's review-time gate), and **NOT** build the plan-time constitutional gate
(Spec Kit has it; that's a separate future seam). Verification: dogfood against
`~/pipeline-dogfood/invoice-tracker/` (has a PRINCIPLES.md + a spec change-folder + a code
surface) — confirm the conformance dimension and the omission lens both fire and degrade to N/A
when PRINCIPLES.md is removed.

## Alternatives Considered

(Axis 4 — WebSearch EN+JA)
1. **Constitution-aware review gate** (Spec Kit `/speckit.review`) — **CHOSEN for code side.**
   Direct prior art; both EN+JA converge. Review-time conformance check against the constitution.
2. **Plan-time constitutional gate** (Spec Kit's plan-phase compliance check + Complexity-
   Tracking exceptions) — **DEFERRED.** Valuable but a separate seam (writing-plans ↔ PRINCIPLES);
   out of P2 scope.
3. **New standalone principles-gate skill** — **REJECTED** (the brief's locked decision; a new
   gate engine duplicates the critics we already have). 
4. **Bolt full conformance onto completeness-critic** — **REJECTED** (semantic mismatch: the
   critic hunts omissions; SKILL.md:143 cedes inconsistency to Spec Kit). Spec side uses the
   omission frame instead.

## What Becomes Obsolete

(Axis 5) Nothing deleted. Purely additive (one dimension, one lens, one discovery convention).
Justified-not-YAGNI: it closes the dogfood-surfaced gap (declared-but-unenforced PRINCIPLES.md)
and is **verification-class scaffolding** (a check ON the output — Bitter-Lesson-proof per
`feedback_two_kinds_of_scaffolding_bitter_lesson`), unlike a crutch. The lens enumeration itself
stays deletable per completeness-critic's existing Bitter-Lesson note.

## Out of Scope

- Per-task `code-quality-reviewer` principles check (whole-branch reviewer only).
- New synced standard in `domain-teams:code-team`.
- Plan-time constitutional gate (writing-plans ↔ PRINCIPLES) — deferred future seam.
- Any change to `product-principles-toolkit` (it already emits the `— check:` clauses).
- A machine PRINCIPLES.md parser — conformance is LLM judgment against the `— check:` clauses.

## Open Questions

- None blocking. Exact severity calibration (when is a violation 🔴 vs 🟡) is a
  writing-plans / agent-prose detail; default 🟡, escalate to 🔴 only for safety/security-bearing
  principles.
