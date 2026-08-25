---
name: proposal-critique
description: |
  Triage a proposal (list, plan, or prose recommendation) into KEEP / DEFER / DROP using evidence grounding and YAGNI. Use for 'critique this', 'over-engineered?', 'can this be simpler?', '業界證實'. Single specific change → complexity-critique.
---

# Proposal Critique

A user-invoked gate for turning a multi-item proposal into a recommendation. An untriaged list, plan, or prose recommendation is a draft: every item must earn its place through evidence grounding and necessity.

## Iron Law

```
NO MULTI-ITEM PROPOSAL SHIPS WITHOUT TRIAGE
```

Do not call every item a good idea or hide unneeded work behind priorities. The output is a decision surface, not the original proposal annotated in place.

## Gate Function

Run these five steps in order:

1. **ENUMERATE-OR-DECOMPOSE.** Surface every concrete item.
   - **List or plan:** treat each numbered item, bullet, or P0/P1/P2 entry as one target.
   - **Prose:** extract the recommendation and each supporting claim. The main verb phrase is usually the recommendation; clauses introduced by “because,” “since,” “given,” or “so that” are supporting claims. Split compound claims before judging them.

2. **GROUND.** Assign one evidence-grounding value to every item:
   - `GROUNDED` — supported by a citation, measurement, or documented failure mode.
   - `HEURISTIC-OK` — uncited, but its mechanism is industry-known.
   - `SPECULATIVE` — intuition or a novel claim without support.

3. **ESSENTIAL?** Assign one necessity value:
   - `ESSENTIAL` — load-bearing for the stated goal; removal breaks the proposal.
   - `SPECULATIVE` — future-proofing, “nice to have,” or optimization for a hypothetical case.

4. **TRIAGE.** Map the two values through The Triage Matrix below, then apply the DEFER fall-through rule.

5. **PRESENT.** Show three buckets—KEEP, DEFER, and DROP—with a one-line reason per item. Put `KEEP-WITH-CAVEAT` items in KEEP and state the caveat. Do not intermix the full original list with verdicts.

## The Triage Matrix

| Grounding | ESSENTIAL | SPECULATIVE necessity |
|---|---|---|
| **GROUNDED** | KEEP | DEFER |
| **HEURISTIC-OK** | KEEP-WITH-CAVEAT | DEFER |
| **SPECULATIVE** | KEEP-WITH-CAVEAT | DROP |

- **KEEP** — ship as-is.
- **KEEP-WITH-CAVEAT** — ship, but expose weak grounding such as “n=1,” “industry intuition,” or “no benchmark yet.”
- **DEFER** — exclude from the current proposal and record the event that would make it relevant.
- **DROP** — remove it; the assumption does not justify the cost.

### DEFER fall-through

DEFER is valid only with an **articulable re-trigger condition**: a concrete observation or event that could change the verdict. If none exists, **fall through DEFER to DROP**. “Do it later,” a lower priority, gradual ecosystem change, or an unspecified future need is not a re-trigger. This prevents DEFER from becoming a parking lot that disguises “ship everything.”

## Judgment Rules

- “Industry standard” or “best practice” without a source is `SPECULATIVE` grounding, not evidence.
- “Future-proofing,” “in case we need it,” and “nice to have” are `SPECULATIVE` necessity unless tied to the present goal.
- A weak source does not automatically mean DROP: an essential item may be KEEP-WITH-CAVEAT.
- A grounded item is not automatically necessary: GROUNDED × SPECULATIVE maps to DEFER and still needs a re-trigger.
- P0/P1/P2 ranks do not replace triage. A low-priority promise remains work unless it becomes DEFER with a re-trigger or DROP.
- If compound prose contains a recommendation plus multiple claims, judge each separately. Do not let one grounded clause lend evidence to its neighbors.
- If five or more items survive without a DROP, recheck whether necessity judgments were too charitable; this is a diagnostic, not a quota.

## Output Contract

Use this compact shape:

```markdown
## KEEP
- Item — verdict inputs and why it is load-bearing.
- Item (caveat: weak grounding) — why it still survives.

## DEFER
- Item — re-trigger: <observable condition>.

## DROP
- Item — unsupported, unnecessary, or no valid re-trigger.
```

Preserve distinctions in the reason: name both the grounding and necessity result when ambiguity matters. Do not silently convert DROP into DEFER to soften the recommendation, and do not ask the user to perform the triage that this skill exists to provide.

### Compact example

For “rewrite auth to JWT because it is stateless, scales better, and is the industry standard,” first decompose the recommendation and three claims. A cited statelessness claim may be GROUNDED × ESSENTIAL → KEEP. The rewrite may be HEURISTIC-OK × ESSENTIAL → KEEP-WITH-CAVEAT. A scalability claim may be GROUNDED × SPECULATIVE → DEFER with “when this workload is benchmarked” as its re-trigger. An uncited “industry standard” claim is SPECULATIVE × SPECULATIVE → DROP. The example illustrates the process; do not copy its verdicts when the evidence or stated goal differs.

## Routing Boundaries

Apply this skill to a multi-item list or plan, or prose that advocates one recommendation through two or more supporting claims. Typical requests include “complexity audit,” “is this over-engineered?”, “what's the MVP?”, “業界證實嗎?”, “可以簡化嗎?”, “audit this proposal,” and “should we keep all of these?”

Do not invoke it for:

- Simple Q&A or a single factual answer.
- A Single specific change; use `complexity-critique` for deletion-first before/after analysis.
- Explanatory bullets with no advocated action.
- Code-only micro-changes; use the host's code-simplification workflow.
- Pre-completion verification; use the host's verification workflow.

This skill judges the proposal text. It does not perform primary-source research, simplify implementation code, or verify completed execution. When a surviving item needs one of those actions, hand it to the relevant research, code, or verification capability only after triage.

Automatic self-triggering on the assistant's own proposed backlog is deferred. Reconsider only after at least ten successful user-triggered audits and an explicit user request for self-firing.
