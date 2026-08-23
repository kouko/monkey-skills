# Body Validation — proposal-critique gate logic

This file documents the **B-test** (body-validation test) that the
v0.1 dogfood run executed manually. It captures one fixture: input
proposal + ground truth + skill verdict per version. It is not an
automated test — there is no `run_loop`-equivalent for body output
yet. Treat this as a **frozen reference run**: any future change to
the gate logic should be re-validated against this fixture and the
expected output updated only with explicit reasoning.

## Fixture #1 — v0.1.0 → v0.1.2 dogfood iteration (recursive birth)

### Input proposal (7-item P0–P3 backlog)

This was Claude's actual draft after worker research returned on
description-design.md improvements (in the session that produced
proposal-critique itself). The user invoked manual triage via
natural-language pushback ("業界證實 嗎?" / "可以簡化 嗎?") and
produced the ground truth below.

```
P0-1  Add run_loop.py wiring to description-design.md
      (Layer 3 broken connection)
P0-2  Add over-triggering countermeasures section
      (after §3, before §4)
P1-1  Add skill collision / disambiguation section
P1-2  Add failure mode catalog
P2-1  Add OpenAI / MCP / Cursor cross-framework comparison
P2-2  Mark "14-sample stats" as "indicative, not authoritative"
P3    Run actual A/B test on git-memory description with run_loop.py
```

### Ground truth (manual user triage)

| Bucket | Item | Reason |
|---|---|---|
| **KEEP** (1) | P2-2 | grounded (n=14 is a measured fact) + essential (file's trustworthiness rests on it) |
| **DEFER** (2) | P0-1, P3 | both have plausible re-trigger conditions: P0-1 ships when P3 lands; P3 ships when v0.1 dogfood produces measurable signal |
| **DROP** (4) | P0-2, P1-1, P1-2, P2-1 | over-triggering / collision / failure-mode are speculative (no observation); cross-framework is breadth not depth |

**Total**: 1 KEEP / 2 DEFER / 4 DROP

### Skill v0.1.0 verdict (matrix without fall-through rule)

Running the gate on the same input with v0.1.0 SKILL.md (matrix
alone, no §Fall-through rule subsection):

| # | Item | GROUND | ESSENTIAL? | Matrix → |
|---|---|---|---|---|
| P0-1 | run_loop wiring | HEURISTIC-OK | SPECULATIVE | DEFER |
| P0-2 | over-triggering | SPECULATIVE | SPECULATIVE | DROP |
| P1-1 | collision | SPECULATIVE | SPECULATIVE | DROP |
| P1-2 | failure catalog | SPECULATIVE | SPECULATIVE | DROP |
| P2-1 | cross-framework | HEURISTIC-OK | SPECULATIVE | **DEFER** ← divergence |
| P2-2 | mark indicative | GROUNDED | ESSENTIAL | KEEP |
| P3 | A/B test | GROUNDED | SPECULATIVE | DEFER |

**v0.1.0 output**: 1 KEEP / 3 DEFER / 3 DROP

**Divergence vs ground truth**: 1 item (P2-1). Skill says DEFER,
ground truth says DROP.

### Root cause analysis

P2-1's matrix verdict was DEFER (HEURISTIC-OK × SPECULATIVE), but no
plausible re-trigger condition can be articulated for "cross-framework
comparison" — frameworks update gradually, no future event would
reliably change the calculus. The DEFER bucket requires re-trigger;
without one, the verdict should fall through to DROP.

The rule existed in v0.1.0 §Common Failures ("P2/P3 used as 'ship
later' instead of DEFER → Force a real DEFER with re-trigger or
DROP") but was invisible at the matrix-consumption point in step 4
of the gate. A consumer reading §The Triage Matrix would not see
the fall-through requirement.

### Skill v0.1.2 verdict (matrix + fall-through rule)

v0.1.2 added §Fall-through rule directly under §The Triage Matrix.
Re-running the gate on the same input:

| # | Item | Matrix → | Fall-through check | Final |
|---|---|---|---|---|
| P0-1 | run_loop wiring | DEFER | re-trigger plausible (after P3) | DEFER |
| P0-2 | over-triggering | DROP | n/a | DROP |
| P1-1 | collision | DROP | n/a | DROP |
| P1-2 | failure catalog | DROP | n/a | DROP |
| P2-1 | cross-framework | DEFER | **no plausible re-trigger → DROP** | **DROP** |
| P2-2 | mark indicative | KEEP | n/a | KEEP |
| P3 | A/B test | DEFER | re-trigger plausible (when dogfood signal arrives) | DEFER |

**v0.1.2 output**: 1 KEEP / 2 DEFER / 4 DROP

**Match with ground truth**: 7/7. Fixture passes.

### What this fixture validates

- Matrix gate produces sound base verdicts on a real over-proposed
  list (4 of 7 items correctly identified as DROP without any rule
  beyond GROUND × ESSENTIAL?)
- The §Fall-through rule (added in v0.1.2) closes the one
  observable gap; without it, the matrix produces "valid-looking"
  DEFERs that aren't actually sound
- The 1 KEEP verdict matches across versions — fall-through doesn't
  affect items that were already correctly categorized
- Recursive consistency: this skill correctly triages the proposal
  that birthed it (after v0.1.2)

### What this fixture does NOT validate

- Prose-shape input (Example 2 in SKILL.md is a separate teaching
  example with no ground truth)
- Cross-skill collision (multiple skills competing for same trigger)
- Fixtures across multiple sessions / authors / projects
- Adversarial inputs (proposals deliberately crafted to break the
  matrix)

n=1. Indicative, not authoritative — same discipline as
`description-design.md` §Length §Caveat block. Future versions
should add fixtures from independent sessions / projects to grow n.

## Fixture #2 — prose-shape proposal (JWT architecture decision)

### Input proposal (prose form)

> "We should rewrite the auth module to use JWT instead of session
> cookies because JWT is stateless, scales better horizontally, and
> is the industry standard for microservices."

This is the proposal used in SKILL.md §Worked Examples Example 2.
That instance is a **teaching example** demonstrating DECOMPOSE; this
instance is a **validation fixture** with frozen ground truth.

### DECOMPOSE step output

The §Gate Function step 1 (ENUMERATE-OR-DECOMPOSE) extracts:

| # | Type | Content |
|---|---|---|
| 1 | recommendation | Refactor auth module → JWT |
| 2 | claim | JWT is stateless |
| 3 | claim | JWT scales better horizontally than session cookies |
| 4 | claim | JWT is the industry standard for microservices |

Heuristic applied: main verb phrase = recommendation; "because" /
"since" / "given" clauses = supporting claims. The proposal had one
"because" introducing three clauses (joined by "," and "and").

### Ground truth (manual triage with current SKILL.md gate)

| # | Item | GROUND | ESSENTIAL? | Bucket | Reason |
|---|---|---|---|---|---|
| 2 | JWT is stateless | GROUNDED | ESSENTIAL | KEEP | RFC 7519 codifies stateless property; the recommendation rests primarily on this |
| 1 | refactor auth → JWT | HEURISTIC-OK | ESSENTIAL | KEEP-WITH-CAVEAT | rec is essential to the proposal but evidence rests on weaker claims #3 + #4 |
| 3 | scales better horizontally | GROUNDED | SPECULATIVE | DEFER | causal claim verifiable via benchmark; defer until measured for THIS specific workload |
| 4 | industry standard for microservices | SPECULATIVE | SPECULATIVE | DROP | classic ungrounded sociological assertion ("everyone does it") with no source; common-knowledge appeal |

**Total**: 1 KEEP / 1 KEEP-WITH-CAVEAT / 1 DEFER / 1 DROP

### What this fixture validates

- The DECOMPOSE step (§Gate Function step 1, prose path) correctly
  separates recommendation from supporting claims using the main-verb
  + "because/since/given" heuristic
- The matrix produces sound verdicts when items have **different**
  grounding × essentialness profiles within a single proposal
  (Fixture #1 was 7 items with similar profiles; this is 4 items
  spanning all 4 corners of the matrix)
- The KEEP-WITH-CAVEAT bucket is exercised (Fixture #1 has 0 of these)
- The DEFER fall-through rule is **not** triggered (claim #3 has a
  plausible re-trigger: "when this team's specific workload is
  benchmarked")
- Different shapes (list in #1, prose in #2) flow into the same
  downstream gate as designed in §Operational flow

### What this fixture does NOT validate

- Multi-paragraph prose (this is one sentence with three clauses;
  real architecture decisions span paragraphs)
- Nested claims (claim that itself has supporting sub-claims)
- Contradictory claims within the same proposal
- Adversarial decomposition (claims phrased to evade the
  "because/since/given" heuristic — e.g. "...; this is good for X;
  also helps with Y")

n=2 fixtures total. Still indicative, not authoritative — same
discipline as Fixture #1's caveat.

## Re-running the fixture

There is no automation. Re-validate manually:

1. Load the input proposal as if Claude just produced it
2. Apply the current SKILL.md gate (5 steps)
3. Compare output to the ground truth above
4. Any divergence indicates either (a) the gate logic changed
   (intentional, update expected output), or (b) the gate logic
   regressed (unintentional, fix the change)

Automation deferred. Re-trigger condition: ≥3 fixtures accumulated
+ regression detected manually that an automated runner would have
caught earlier.
