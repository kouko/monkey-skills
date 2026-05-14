# Hook: Self-Critique Block

Deep-mode artifact-finalization hook — worker MUST expose the
weakest links in its own argument before evaluator review.

Inspired by LangGraph `open_deep_research` (LangChain 2024)
`think_tool` reflection pattern. Implements the **disclosure**
step only; omits the iterative critique→revise loop to save the
extra LLM pass.

## When This Applies

- Mode: **deep only** (quick mode skips — the lighter SELF check
  in Phase 3 covers basic reflection at quick-mode bar)
- Phase: invoked at the **end of Phase 3 (Synthesis)**, immediately
  before artifact handoff
- Workflows: applies to any worker-dispatching workflow when
  `mode=deep`

## Rule

Worker MUST append a `## Self-Critique` section to the artifact,
≤200 words, addressing exactly three points:

1. **Weakest evidence link** — Which claim has the thinnest
   support? Single source? Stale data? Indirect inference?
2. **Ignored opposing evidence** — What contrary evidence or
   alternative interpretation did I underweight or skip? Why?
3. **Confidence-evidence match** — Are my confidence tags
   (高/中/低 or IPCC ladder) actually warranted by the evidence
   strength, or am I overclaiming?

Worker does **NOT** revise the artifact based on the critique —
disclosure is the deliverable. Evaluator uses the Self-Critique
section as a primary input to the SHOULD gate's
`Reasoning & Logic` and `Source Quality` dimensions.

### Protocol metadata record (3 lines)

Prepend the three points above with a **3-line metadata record**
that captures the production-side choices for downstream
reviewers. Each line is a single bullet; the format is structured
but lightweight (no JSON schema, no LLM-judge rationale prose):

```
- Protocol applied: <protocol-name>
- Onboarding form: <concept-first | scope-first | context-first | exempt> (per <protocol default | user override>)
- Onboarding tagging exemption applied per citation-standards §Onboarding-Layer Exemption.
```

The third line is fixed boilerplate when the artifact contains an
onboarding section; omit only when the workflow is exempt
(`research-summary` / `quick-lookup`). The line exists so a future
reviewer scanning the artifact does not flag the absence of tags
in the onboarding section as a violation — the exemption is
self-disclosed.

### Load-bearing claim sweep

Before finalizing the Self-Critique points above, perform the
load-bearing-by-use sweep defined in
`standards/citation-standards.md` §Load-Bearing Definition: scan
sentences that the synthesis / recommendation / TL;DR references
back to, and verify each carries a Fact / Analysis / Speculation
tag. Tag any that were missed. This catches the
"first-pass-could-not-predict-downstream-use" failure mode
without forcing the worker to over-tag defensively during initial
drafting.

## Failure Mode

A vacuous Self-Critique ("no major weaknesses identified",
"all claims well-supported") is itself a fatal flag. If the
worker genuinely sees no weaknesses, that signals either trivial
research scope or worker overconfidence — both warrant evaluator
flag.

## Example

```
## Self-Critique

- Protocol applied: stack-evaluation
- Onboarding form: concept-first (per protocol default)
- Onboarding tagging exemption applied per citation-standards §Onboarding-Layer Exemption.

1. **Weakest link**: The 35% growth claim rests on a single 2023
   industry report (Gartner) — not cross-verified against IDC or
   Forrester. Confidence should arguably be 中 not 高.
2. **Ignored**: I underweighted the 2024 EU AI Act's compliance
   cost on framework X — only one paragraph in §3, no quantitative
   estimate. Could shift the recommendation if cost is material.
3. **Match**: 中 confidence on adoption-trend projection is
   honest; 高 confidence on the cost-comparison table may be
   over-stated given vendor pricing opacity.
```
