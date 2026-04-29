# Equivalence Check Protocol

How `skill-refactor` Q1 verifies that a candidate refactored
SKILL.md produces output equivalent to the baseline.

## Two-layer check

### Layer 1: Structural comparison (deterministic)

Run by `scripts/equivalence_check.py`. Cheap, fast, catches gross
divergence.

For each test prompt's `(baseline_output, candidate_output)` pair:

| Check | Pass criterion | Failure example |
|---|---|---|
| Output type match | Same artifact types produced (file, JSON, prose, code) | Baseline produced `report.md`, candidate produced JSON |
| Section structure | Same set of `## ` heading texts (order may vary) | Candidate dropped a "Summary" section |
| File paths | Same set of file paths created / referenced | Candidate wrote to a different path |
| Tool calls | Same sequence of tool names invoked (count may differ ±1) | Candidate skipped a `Read` call |
| Token count | Within ±20% of baseline | Output dropped 60% — likely missing content |

**Pass rule**: all 5 checks pass. Layer 1 failure → REJECT
immediately, do not proceed to Layer 2.

### Layer 2: LLM-judge ensemble (semantic)

If Layer 1 passes, run 3 independent LLM judges (see
`multi-judge-ensemble.md`). Each judge receives:

- The user prompt that produced both outputs
- Both outputs labeled `Output_A` / `Output_B` (random which is
  baseline)
- Asked: "Are A and B semantically equivalent? Same information,
  same recommendations, same actions?"
- Returns: `equivalent` / `not_equivalent` / `uncertain` + 1-2
  sentence reason

**Consensus rules**:

| Result | Verdict |
|---|---|
| 3/3 `equivalent` | PASS (high confidence) |
| 2/3 `equivalent`, 1 `uncertain` | PASS (moderate confidence) |
| 2/3 `equivalent`, 1 `not_equivalent` | FLAG → Tier 2 (escalate to human) |
| 1/3 `equivalent` (or worse) | FAIL → REJECT round |
| Any `not_equivalent` reason cites specific behavior change | FLAG → Tier 2 even if 2/3 said equivalent |

**Important rule**: a single dissenting judge that points to a
*specific behavior change* outranks numeric majority. The dissent
is a signal that the refactor smuggled feature work; investigate
before committing.

## What "equivalent" means

Equivalent means **the user gets the same value from the output**:

- Same recommendations / answers / verdicts
- Same files / artifacts created (paths and contents semantically
  matching)
- Same edge cases handled
- Same warnings / caveats raised
- Same level of detail (within reason; some compression OK if no
  load-bearing detail dropped)

Equivalent does **not** require:

- Identical phrasing
- Identical word counts
- Identical sentence ordering
- Same tone (as long as content is preserved)

The line is: "could the user complete the same task with this
output as with the baseline?" If yes → equivalent. If no → not.

## What invalidates a "pass" verdict

Even if both layers pass, mark as suspicious if:

- Layer 1 pass but Layer 2 has any `uncertain` votes → moderate
  confidence at best
- Token count delta is suspiciously large (>30% reduction in
  output) → may indicate dropped content the structural check
  didn't catch
- Edge-case test prompts (intentionally tricky inputs) don't
  match — happy-path equivalence is necessary but not sufficient

## How to design test prompts for equivalence checking

Per `test-prompts-schema.md`, each skill should have ≥3 prompts:

1. **Happy path** — most common use case
2. **Edge case** — tricky input that exercises a specific instruction
3. **Stress prompt** — input deliberately incomplete or ambiguous
   (tests the skill's intake / clarification behavior)

Refactor that passes happy path but fails edge case is a **subtle
regression**; the equivalence check needs to cover both.

## Failure modes to avoid

| Failure mode | What goes wrong | Mitigation |
|---|---|---|
| **Single judge bias** | One judge consistently says equivalent (or not) regardless | 3-judge ensemble + varied prompt framing |
| **Verbosity bias** | Judge prefers longer output → marks shorter candidate as "less complete" | Layer 1 token-count rule prevents this from auto-rejecting; Layer 2 sees both with neutral framing |
| **Position bias** | Judge prefers `Output_A` over `Output_B` | Random labeling in Layer 2 (sometimes baseline = A, sometimes = B) |
| **Self-preference** | Judge prefers output it would have produced | Use different prompt frames per judge |
| **Insensitivity to subtle change** | Judges miss a small but load-bearing word change | Fall back to `skill-tasting` if you suspect this; refactor is the wrong tool for subtle taste |

## When this protocol is the wrong fit

If the target skill produces non-deterministic / creative output
(writing tone, design choices, persuasive copy), Layer 2's judge
becomes unreliable — taste enters. The skill self-aborts and
recommends `skill-tasting` instead. This is documented in
SKILL.md §Not-triggers.
