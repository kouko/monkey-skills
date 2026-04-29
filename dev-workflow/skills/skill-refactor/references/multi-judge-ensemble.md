# Multi-Judge Ensemble

How to spawn 3 independent LLM judges for `skill-refactor` Q1's
Layer 2 semantic check.

## Why ensemble

Single LLM-as-judge has documented failure modes (verbosity bias,
position bias, self-preference, insensitivity to subtle change).
A 3-judge ensemble:

1. **Reduces variance** — single judge's idiosyncratic verdict gets
   averaged out
2. **Surfaces uncertainty** — disagreement among judges is a signal,
   not noise; auto-escalate to human
3. **Catches subtle behavior change** — a single dissenting judge
   pointing to a specific behavior diff outranks numeric majority

3 is the minimum that allows majority vote with a tiebreaker; more
judges (5, 7) reduce variance further but cost more tokens. Default
to 3.

## How to spawn

Each judge runs as a separate `Task` subagent with a different
prompt framing.

### Judge 1: Functional equivalence (utility-oriented)

```
You are evaluating whether two outputs serve the same user goal.

User's request: <prompt>
Output A: <output_a>
Output B: <output_b>

Question: Could the user accomplish the same task with Output A as
with Output B? Same recommendations, same actions, same artifacts?

Answer with one of:
- equivalent: yes, same value to user
- not_equivalent: no, A and B differ in load-bearing way
- uncertain: borderline; explain what's unclear

Then give a 1-2 sentence reason. If "not_equivalent", name the
specific behavior change.
```

### Judge 2: Information completeness (content-oriented)

```
You are checking whether two outputs contain the same information.

User's request: <prompt>
Output A: <output_a>
Output B: <output_b>

Question: Does either output contain information the other lacks?
Edge cases, warnings, recommendations, examples? Ignore phrasing /
ordering / tone differences.

Answer with one of:
- equivalent: same information set
- not_equivalent: one contains load-bearing content the other lacks
- uncertain: surface differences but unclear if load-bearing

Then give a 1-2 sentence reason. If "not_equivalent", name the
specific content gap.
```

### Judge 3: Edge-case behavior (boundary-oriented)

```
You are checking whether two outputs handle the same edge cases.

User's request: <prompt>
Output A: <output_a>
Output B: <output_b>

Question: For inputs near the boundary of the request — ambiguous
phrasing, missing information, unusual values — would A and B
guide the user the same way? Or does one skip checks the other
performs?

Answer with one of:
- equivalent: same boundary behavior
- not_equivalent: one handles a boundary case the other doesn't
- uncertain: boundaries unclear from the prompt

Then give a 1-2 sentence reason. If "not_equivalent", name the
specific boundary behavior diff.
```

## Why varied framing

Each frame tests a different equivalence aspect:

| Judge | Frame | What it catches |
|---|---|---|
| 1 (utility) | "same value to user" | Output structure preserved |
| 2 (content) | "same information set" | No content silently dropped |
| 3 (boundary) | "same edge-case handling" | No fallback / warning lost |

Without varied framing, all three judges would tend to align (LLM
self-preference). Varied framing forces them to look at different
dimensions.

## Random output labeling (position bias mitigation)

For each judge call, **randomly assign baseline / candidate to A /
B**. Don't always put baseline as A. Some judges are biased toward
"first option" or "second option" regardless of content. Random
labeling averages this out across the ensemble.

Track the assignment in the call log so you can decode the result:

```json
{
  "judge_id": 1,
  "frame": "utility",
  "a_is": "baseline",
  "b_is": "candidate",
  "verdict": "equivalent",
  "reason": "..."
}
```

## Consensus rules (recap from equivalence-check-protocol.md)

| Result | Verdict |
|---|---|
| 3/3 `equivalent` | PASS high confidence |
| 2/3 `equivalent`, 1 `uncertain` | PASS moderate confidence |
| 2/3 `equivalent`, 1 `not_equivalent` | **FLAG → Tier 2** |
| ≤1 `equivalent` | FAIL → REJECT |
| Any `not_equivalent` cites *specific* behavior change | **FLAG → Tier 2** even if 2/3 said equivalent |

Specific behavior diff outranks numeric majority. The gate
explicitly does not let majority-rules over a substantive dissent.

## Token cost

Per refactor round: 3 judge calls × (prompt + 2 outputs) ≈ 3-5K
tokens depending on output size.

For a skill with 3 test prompts running 3 rounds: 9 ensembles × 3K
≈ 27K tokens. Reasonable for an automation that's preserving
behavior.

## When ensemble is overkill

If the refactor is purely *structural* and the test prompts are
deterministic (file transforms, code generation), Layer 1 alone
may be sufficient. You can skip the LLM ensemble if **all three of
these hold**:

1. Layer 1 structural check is exhaustive (covers all output
   dimensions)
2. Test prompts are deterministic (same input → same output)
3. The refactor move is from the catalog's "Low" risk tier

In that case, Layer 1 pass = PROCEED. Document in
`results.tsv` as `eval_mode: structural_only`.

For any non-deterministic / prose / creative output, run the full
ensemble.
