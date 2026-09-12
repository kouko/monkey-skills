# Main-relative model/effort cost pilot protocol

Status: pre-registered before execution.

## Question

For the same complex policy-review task, does `frontier/low` preserve useful
review quality at lower total cost than `standard/medium`?

Host mapping for this pilot:

- `standard/medium` = Claude Code `sonnet/medium`
- `frontier/low` = Claude Code `opus/low`

The aliases are execution inputs, not proof of the actual model. Every accepted
run must be verified against the result JSON's canonical model and the matching
persisted session record's effort.

## Frozen input and arms

- Corpus: the complete independent-review packet from the earlier planning run.
- Corpus SHA-256: `eafe902d69b4ff1c0afe311ea76e065b4a4c6af5787cc9c985856d27d4384de2`.
- Same instruction, schema, corpus bytes, tool policy, and per-run budget.
- Two independent sessions per arm.
- Per-run hard budget: USD 1.00; total hard budget: USD 4.00.
- The replay runner verifies its required Claude CLI flags before the paid call
  and removes its generated session identifier before writing publication
  artifacts.

## Pre-registered scoring

The earlier independent review supplies nine known required-change themes:

1. High effort additionally requires the frontier model.
2. A model escalation at the frontier ceiling falls through to effort.
3. Redispatch has a hard cap and terminal outcome.
4. `frontier/medium` plus complex intentionally remains unchanged initially.
5. Unknown capabilities are unsupported; known unsupported overrides are
   omitted before execution.
6. The complex classifier needs a checkable cross-module condition.
7. Missing task evidence has a packet-repair action or ceases to be a class.
8. Mechanical lowering is model-first rather than lowering both dimensions.
9. Existing dogfood covers effort behavior, not model-tier cost or frequency.

Scoring is semantic, not exact-string matching. A theme counts once per run
when the response identifies the same defect and required direction. Also
record unsupported blocking findings as false positives. Cost, duration, token
counts, canonical model, and effort come only from control-plane records.

## Decision rule

- Do not claim equivalence from two replicates.
- `frontier/low` is a promising default for this task class only if its union
  recall is no worse, it introduces no unsupported blocking finding, and its
  mean observed cost is lower.
- Otherwise retain `standard/medium`, or mark the result inconclusive when
  within-arm variance dominates the difference.
- This one-corpus pilot cannot justify a repository-wide policy by itself.

## Staged extension

Stage 1 was registered after the initial four-arm pilot and before its calls:

- Add `standard/high` = Claude Code `sonnet/high`, two replicates.
- Add `frontier/medium` = Claude Code `opus/medium`, two replicates.
- Keep the corpus, prompt, schema, isolation, and scoring oracle unchanged.
- Use a USD 2.00 equivalent-cost guard per run to avoid truncating an accepted
  subscription-backed call; this is not incremental billing under the verified
  Claude Max login.
- Do not run `frontier/high` in this stage.

Stage 1 answers three comparisons: Sonnet medium versus high, Opus low versus
medium, and Sonnet high versus Opus medium. Stop before Stage 2 and interpret
the result rather than automatically filling the matrix.

Stage 2 was registered after interpreting Stage 1 and before its calls:

- Add `standard/low` = Claude Code `sonnet/low`, two replicates.
- Keep every other control unchanged.
- Compare Sonnet low versus medium to isolate effort, and Sonnet low versus
  Opus low to isolate model tier.
- Stop after these two calls. Do not add `frontier/high` or an economy-model
  review arm without a new task-specific reason.

Stage 2 was stopped after its first `sonnet/low` replicate when external prior
art was reviewed. The raw run is retained but excluded from comparative claims
because it has no replicate. No second call is required: a broader Claude
matrix would duplicate stronger public evidence without answering a Loom-only
question.

## External-evidence-informed remaining scope

Public evidence reviewed after Stage 1 changes the remaining test objective:

- Anthropic's cost-optimization cookbook already sweeps Opus and Sonnet across
  low, medium, and high with two trials per cell.
- `effortmining` reports roughly 450 pre-registered per-subagent effort runs,
  three replicates per cell, mechanical or hidden-test grading where possible,
  and explicit fit-blindness failures.
- Stet reports GPT-5.5 Codex across low through xhigh on 26 real repository
  tasks; it shows that passing tests alone misses semantic-quality differences.
- ReasonBENCH repeats configurations ten times and shows that run variance can
  change rankings.

Sources:

- https://platform.claude.com/cookbook/cost-optimization-cost-optimization
- https://github.com/nagisanzenin/effortmining
- https://www.stet.sh/benchmarks/gpt-55-codex-graphql-reasoning-curve
- https://reasonbench.github.io/

The external results are priors, not Loom acceptance evidence. Loom now tests
only decisions that remain host- or workflow-specific.

### Claude

No additional model/effort matrix runs. The accepted local complex-review runs
remain a workload calibration point. Re-test Claude only after a model alias
changes canonical model or a real Loom failure contradicts the current route.

### Codex quality calibration

Use three real Loom corpora, two independent runs per arm:

1. Mechanical transformation with a deterministic oracle:
   `economy/low` versus `standard/low`.
2. Bounded implementation with hidden tests:
   `standard/low` versus `standard/medium`.
3. Complex review with the existing nine-item oracle:
   `standard/medium` versus `frontier/low`.

This is 12 Codex runs, not a 3 x 3 matrix repeated across three corpora (54
runs). Resolve each portable tier to the current host model immediately before
execution and record the actual model and effort. Do not compare subscription
quota consumption to Claude's API-price-equivalent dollars.

### Mechanism verification

Do not spend model calls on deterministic routing mechanics. Unit or integration
tests enumerate all five portable effort tiers, initial and escalation
reachability, inherited host-native values, clamping, model-specific unsupported
efforts, unknown capabilities, atomic omit-both fallback, and the two-redispatch
cap. One live success probe and one forced unsupported-override probe per host
validate the adapter boundary.

### Stop and escalation rules

- Do not test `standard/high`, `frontier/high`, `xhigh`, or `max` as initial
  routes.
- Test `frontier/medium` or higher only after a complete lower-profile attempt
  exhibits the corresponding retained failure signal.
- Test `xhigh` only after a completed `frontier/high` attempt retains an xhigh
  trigger. Do not spend a model call testing newly routed `max`; it is
  inheritance-only in this design.
- Do not add a third replicate merely to break an inconvenient tie. Mark the
  cell inconclusive and obtain a second corpus first.
- A model alias change, different task class, or different host invalidates
  numerical transfer but not the protocol.
