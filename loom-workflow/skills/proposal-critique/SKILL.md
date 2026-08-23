---
name: proposal-critique
description: |
  Triage a proposal (list, plan, or prose recommendation) into KEEP / DEFER / DROP using evidence grounding and YAGNI. Use for 'critique this', 'over-engineered?', 'can this be simpler?', '業界證實'. Single specific change → complexity-critique.
---

# Proposal Critique

A user-invoked gate skill: forces any proposal — numbered backlog,
multi-step plan, or prose recommendation with supporting claims —
through a triage pass before the user acts on it.

## Overview

An untriaged multi-item proposal is a draft, not a recommendation.
Each item must earn its place via two checks:

- **Evidence grounding** — does the item cite a source / known
  failure mode / measured signal, or is it heuristic / intuition?
- **Necessity (YAGNI)** — is the item load-bearing for the stated
  goal, or speculative future-proofing?

Items that fail both checks are pure overhead. Triage forces an
explicit verdict: KEEP / DEFER / DROP.

## The Iron Law

```
NO MULTI-ITEM PROPOSAL SHIPS WITHOUT TRIAGE
```

Three-bucket discipline is non-negotiable. "All of these are good
ideas" is a draft, not a proposal.

## The Gate Function

When invoked, run these 5 steps in order:

1. **ENUMERATE-OR-DECOMPOSE.** Surface every concrete item.
   - **List shape** (numbered backlog, bullet list of ≥3 items, P0/P1/P2):
     each list item is one target.
   - **Prose shape** (architecture decision, strategy memo, single
     recommendation with supporting claims): extract the concrete
     recommendation + each supporting claim. Heuristic: the main
     verb phrase is the recommendation; clauses introduced by
     "because / since / given / so that" are supporting claims.

2. **GROUND.** For each item, mark grounding:
   - `GROUNDED` — has a citation, measurement, or well-documented
     failure mode this addresses
   - `HEURISTIC-OK` — no source but the underlying mechanism is
     industry-known
   - `SPECULATIVE` — pure intuition, no source, novel claim

3. **ESSENTIAL?** For each item, mark necessity:
   - `ESSENTIAL` — load-bearing for the stated goal; removing it
     breaks the proposal
   - `SPECULATIVE` — future-proofing, "nice to have", premature
     optimization for hypothetical cases

4. **TRIAGE.** Map each item to a bucket via §The Triage Matrix.

5. **PRESENT.** Show the user three buckets, one-line reason per
   item. Do not show the full original list intermixed with verdicts.

## The Triage Matrix

|                          | ESSENTIAL (load-bearing)  | SPECULATIVE (future-proof) |
|--------------------------|---------------------------|----------------------------|
| **GROUNDED** (cited)     | KEEP                      | DEFER                      |
| **HEURISTIC-OK**         | KEEP-WITH-CAVEAT          | DEFER                      |
| **SPECULATIVE** (no src) | KEEP-WITH-CAVEAT          | DROP                       |

- **KEEP** — ship as-is.
- **KEEP-WITH-CAVEAT** — ship but mark the weak grounding ("n=1",
  "industry intuition", "no benchmark yet") so the user knows.
- **DEFER** — record with **an articulable re-trigger condition**
  ("do this when X observed"); do NOT ship in the current proposal.
- **DROP** — cut entirely; the underlying assumption isn't worth
  the cost.

### Fall-through rule (must apply in step 4)

DEFER is only valid when you can name the event that would change
the verdict. If no plausible re-trigger condition can be articulated,
**fall through DEFER to DROP**.

> Example: a "cross-framework comparison" item triages to DEFER on
> the matrix (HEURISTIC-OK × SPECULATIVE), but no future event would
> reliably change the verdict (frameworks update gradually; "the
> comparison would help if X" produces no concrete X). With no
> articulable re-trigger, this is DROP, not DEFER.

This rule is the matrix-level expression of the §Common Failures
row "P2/P3 used as 'ship later' instead of DEFER" — promote items
to DROP rather than parking them in DEFER without exit conditions,
or DEFER becomes the new "ship everything" disguise.

## Common Failures

| Symptom | Meaning | Action |
|---|---|---|
| `≥7 items in a backlog` | Batched-proposal dump | Triage anyway; expect 60%+ DROP/DEFER |
| `"Industry standard"` without source | Sociological claim as fact | Mark SPECULATIVE on grounding |
| `"Future-proofing"` / `"in case we need"` | YAGNI violation | Mark SPECULATIVE on essential → DROP |
| `Compound prose with no decomposition` | Single sentence packs ≥2 claims | Run DECOMPOSE step before triage |
| `P2/P3 used as "ship later"` | Debt promise, not triage | Force real DEFER with re-trigger or DROP |

## Red Flags — STOP

If you see any of these in your draft proposal, you're about to
ship before triage:

- About to present a numbered list with no bucket assignment per item
- "We could also…" stacking — accumulating items without justification
- "Industry standard" / "best practice" claim with no citation
- "Future-proofing" / "in case we need" / "nice to have" framing
- ≥5 items with no DROP — triage rate is suspiciously charitable
- Using P0/P1/P2 priorities as a way to ship everything ("just call them P2")
- Compound prose claim that hasn't been decomposed into atomic claims

## Rationalization Prevention

| Excuse | Reality |
|---|---|
| "It's all good ideas." | Goodness ≠ essentialness. Triage anyway. |
| "I'll let the user decide." | Dumping unbatched IS the failure mode. The 3 buckets ARE the decision surface. |
| "More is safer." | Unjustified items dilute the signal of the justified ones. |
| "I'll just call them P2." | P2 ≠ DROP. P2 is a debt promise. |
| "n=1 is fine here." | Mark grounding as SPECULATIVE; don't hide it. |

## Composes With

This skill triages **the proposal text itself**. It does not do
deeper research, code-level simplification, or execution
verification. When the surviving (KEEP / KEEP-WITH-CAVEAT) items
need those, hand off:

- **Evidence verification** — when an item's grounding axis is
  borderline and you need primary-source confirmation, see
  `domain-teams:research-team` (quick mode is usually enough).
- **Code-level simplification** — when a KEEP item involves code
  that could itself be simpler, see Anthropic `simplify`.
- **Pre-completion verification** — when a triaged plan is
  about to be claimed done, see
  `superpowers:verification-before-completion`.

This skill names those tools but does not invoke them. Composability
is by reference, not by routing.

## Worked Examples

### Example 1 — list shape (this skill's recursive birth)

**Before** (Claude's 7-item backlog): proposal-critique +
simplify-pass + evidence-grader + complexity-meter +
multilingual-trigger-pack + backlog-formatter + eval-harness-extension.

**User pushback** (4 rounds): "is this over-engineered?" / "業界
證實 嗎?" / "我們真的需要 7 個 嗎?" / "what's the MVP?"

**After** (triaged):
- KEEP — proposal-critique (GROUNDED over-engineering is industry-
  known + ESSENTIAL the others depend on its premise)
- DEFER — evidence-grader (HEURISTIC-OK + SPECULATIVE; only if v0.1
  dogfood proves the gap)
- DROP × 5 — simplify-pass / complexity-meter / multilingual-trigger-
  pack / backlog-formatter / eval-harness-extension (each redundant
  with existing skills or pure speculation)

7 items → 1 KEEP / 1 DEFER / 5 DROP.

### Example 2 — prose shape (decomposition demo)

**Before**: "We should rewrite auth to use JWT instead of session
cookies because JWT is stateless, scales better horizontally, and
is the industry standard for microservices."

**DECOMPOSE** extracts: (rec) refactor auth → JWT; (claim) JWT is
stateless; (claim) scales better horizontally; (claim) industry
standard for microservices.

**After**:
- KEEP — "JWT is stateless" (GROUNDED via RFC 7519 + ESSENTIAL)
- KEEP-WITH-CAVEAT — refactor recommendation (ESSENTIAL but rests
  on weaker claims #3, #4)
- DEFER — "scales better horizontally" (causal claim, needs benchmark)
- DROP — "industry standard" (ungrounded sociological assertion)

Both examples teach the same matrix; Example 1 acknowledges its
n=1 limitation per `description-design.md`'s sample-size discipline.

## When To Apply

**Primary triggers (user-spoken)** — what the user types when
asking for the audit:

- "complexity audit" / "is this over-engineered" / "what's the MVP"
- "業界證實 嗎" / "可以簡化 嗎" / "audit this proposal"
- "should we keep all of these" / "我們真的需要這麼多 嗎"

**Shape-agnostic** — accepts:

- List (numbered backlog, P0/P1/P2)
- Plan (multi-step proposal)
- Prose (architecture decision, strategy memo, single recommendation
  with ≥2 supporting claims)

**Not-triggers** — do not invoke for:

- Simple Q&A or single factual answer
- Code-only micro-changes (use Anthropic `simplify`)
- Explanatory bullets in prose with no advocacy ("for three
  reasons: …" is description, not proposal)
- Pre-completion verification (use
  `superpowers:verification-before-completion`)

**Phase 2 (deferred)**: auto-trigger on Claude's own list-shape
output (≥3 numbered items, P0/P1/P2 backlog) is out of scope for
v0.1. Re-trigger condition: ≥10 successful user-triggered audits
+ user requests Claude self-fire.

## Bottom Line

```
Triage is the proposal.
Anything before triage is just a draft.
```
