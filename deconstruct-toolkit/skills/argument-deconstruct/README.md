# argument-deconstruct

> Deep dive on long-form arguments — surface the hidden warrant, name the missing rebuttal, expose the motive ratio.

Argument-focused deep dive. Where `artifact-deconstruct` runs the full
6-lens × 6-dimension treatment for any polished artifact,
`argument-deconstruct` zooms into a single artifact-class — long-form
arguments — and applies Toulmin + Burke at higher resolution. The
critical move: **surface the hidden warrant**.

## When to use

Trigger phrases (any language):

- 「拆解這個論證」「這份提案論證哪裡弱」「找隱性 warrant」
- 「論証を脱構築して」「この社説の隠れた前提は？」
- "deconstruct this argument" / "find the warrant" / "where does this argument fail"
- "is this argument valid" / "what's the hidden assumption in this claim"

When to skip:

- Target has no argumentative spine (descriptive / narrative / reference docs) — use `artifact-deconstruct`
- Target is shorter than ~200 words — too thin to deconstruct
- Target is code — use `sourceatlas`

When to use sister skills instead:

- Multi-lens treatment (rhetoric + persuasion + frame + genre + UX + semiotic) → [`artifact-deconstruct`](../artifact-deconstruct/)
- Atomic assumption surfacing without full Toulmin treatment → [`assumption-surface`](../assumption-surface/)

## Method (what differentiates from artifact-deconstruct's lens-rhetoric)

`artifact-deconstruct/references/lens-rhetoric-anglo.md` combines Burke
pentad + Toulmin model in one lens at survey resolution.
`argument-deconstruct` deliberately **splits** them — see
[`references/lens-toulmin.md`](references/lens-toulmin.md) and
[`references/lens-burke-pentad.md`](references/lens-burke-pentad.md) — for
fuller treatment of each. Per ADR-0002, this synthesis split is
intentional: same primary sources, different operationalization depth.

### Toulmin model (full 6 components)

| Component | Question |
|---|---|
| **Claim** | What's the conclusion? |
| **Grounds** | What evidence supports it? |
| **Warrant** ⭐ | What's the implicit bridge from grounds to claim? |
| **Backing** | What authority backs the warrant? |
| **Rebuttal** | What counter-arguments are acknowledged? |
| **Qualifier** | Under what conditions does the claim hold? |

The warrant is **the focal move**. Most arguments hide their warrant.
Deconstructing the argument means stating the warrant out loud and
testing whether a reasonable opponent would accept it.

### 8 hidden-warrant patterns (catalogued)

When you cannot articulate a warrant, check these patterns in
[`references/lens-toulmin.md`](references/lens-toulmin.md):

| Pattern | Sounds like |
|---|---|
| Authority appeal | "X said it, so it's true" |
| Majority appeal | "Most do it, so it's right" |
| Analogy | "It worked there, so it works here" |
| Trend extrapolation | "Past trend predicts future" |
| Causation from correlation | "Adopters of X also Y, so X causes Y" |
| Loss-aversion | "If we don't, we'll lose" |
| First-principles claim | "From basic principles, X follows" |
| Self-evidence | "Obviously…" |

### Burke pentad ratios

5 elements (act / scene / agent / agency / purpose) plus the **ratio**
analysis: which two elements dominate reveals motive structure.

| Ratio | Meaning |
|---|---|
| Scene-Act | Circumstances force the action |
| Agent-Act | Who you are determines what you do |
| Agent-Agency | Identity determines method |
| Act-Purpose | The action IS the goal |
| Agency-Purpose | Means determine ends |
| Scene-Agent | Setting determines who you become |

Surface the discrepancy between **claimed** ratio and **actual** ratio —
that gap is where motive laundering lives.

## What you get (output)

- **Argument map** in mermaid (visualizes claim / grounds / warrant /
  backing / rebuttal / qualifier with hidden-warrant emphasis on dotted edges)
- **Warrant explicitization** — every implicit warrant stated as a
  full sentence beginning with "Because…"
- **Missing-rebuttal table** — what counter-arguments the author
  ignored or pre-empted
- **Burke pentad ratio analysis** — claimed ratio vs actual ratio with
  motive interpretation
- **Ethical position** on persuasion mechanisms detected (🟢/🟡/🔴/⚫)

## Worked example

See [`eval/cases/argument-deconstruct-01-op-ed.yaml`](../../eval/cases/argument-deconstruct-01-op-ed.yaml)
and [`eval/cases/argument-deconstruct-02-vc-pitch.yaml`](../../eval/cases/argument-deconstruct-02-vc-pitch.yaml)
for must_find ground-truth.

## See also

- [`SKILL.md`](SKILL.md) — full canon
- [`references/lens-toulmin.md`](references/lens-toulmin.md) — full Toulmin treatment (Toulmin 1958, Ch 3)
- [`references/lens-burke-pentad.md`](references/lens-burke-pentad.md) — full Burke treatment (Burke 1945, Introduction)
- Sister skills: [`artifact-deconstruct`](../artifact-deconstruct/) | [`assumption-surface`](../assumption-surface/)
- Plugin overview: [`../../README.md`](../../README.md)
