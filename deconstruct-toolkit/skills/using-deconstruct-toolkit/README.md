# using-deconstruct-toolkit

> Pick the right deconstruction skill and lens combination for the artifact in front of you.

The router. Picks the right deconstruction skill (`artifact-deconstruct`
/ `argument-deconstruct` / `assumption-surface`) and the right lens
combination based on what the user brought and what they want surfaced.
Use this skill when you don't already know which sibling skill applies.

## When to use

Trigger phrases (any language):

- "help me deconstruct this" / "拆解這份" / "脱構築したい"
- "what's the design behind this copy / page / playbook"
- "what is this argument actually claiming"
- "find the hidden assumptions" / "stress-test these claims"
- "I have an artifact but I don't know which skill to use"

When to skip:

- User already specified which sibling skill (e.g., `/deconstruct-toolkit:artifact-deconstruct`) — invoke that directly
- Target is source code or a build artifact — use `sourceatlas`
- User wants help thinking through their own problem — use `philosophers-toolkit`
- User wants to **produce** new copy / docs / design — use `copywriting-toolkit` / `docs-team` / `design-team` / `slides-toolkit`

## Boundary check first

Before routing into this toolkit, the router runs three boundary checks
to redirect mis-targeted requests:

| Question | If yes, redirect to |
|---|---|
| Is the target source code? | `sourceatlas` (impact / flow / overview / pattern / deps) |
| Self-thinking (your problem, not external artifact)? | `philosophers-toolkit` |
| Forward production (write new copy / docs / design)? | `copywriting-toolkit` / `docs-team` / `design-team` / `slides-toolkit` |

All three must be "no" before routing proceeds.

## Two-axis routing

### Axis 1 — Artifact type

| Artifact | Default skill | Default lens combo |
|---|---|---|
| Marketing copy / LP / advertising | `artifact-deconstruct` | persuasion + rhetoric |
| Document pack / playbook / SOP / onboarding | `artifact-deconstruct` | genre + 6-dim full |
| UI / app onboarding / website screen | `artifact-deconstruct` | ux + persuasion |
| Long-form argument / op-ed / proposal / political | `argument-deconstruct` | Toulmin + Burke + warrant surface |
| Strategy memo / policy brief / SNS thread (suspect hidden assumptions) | `assumption-surface` | reverse-Toulmin + symptomatic reading |
| Speech / political address | `artifact-deconstruct` | rhetoric + frame |
| Literature / film / advertising imagery | `artifact-deconstruct` | semiotic + frame |
| Slide deck / presentation | `artifact-deconstruct` | rhetoric + genre |

### Axis 2 — User intent (overrides Axis 1)

| User says | Override to |
|---|---|
| "deconstruct the design" / "為什麼這份寫得這麼好" | `artifact-deconstruct` (full 6-lens × 6-dim) |
| "find hidden assumptions" / "what is this *assuming*" | `assumption-surface` (atomic, fast) |
| "find the warrant" / "is this argument valid" | `argument-deconstruct` (Toulmin focus) |
| "what's manipulating me here" / "spot dark patterns" | `artifact-deconstruct` with persuasion + ux |

If artifact type and user intent disagree, **user intent wins**.

## Three filters before dispatching

| Filter | Meaning |
|---|---|
| Length | < 200 words AND not structured argument → not enough design; tell user, do not dispatch |
| Information-only | Pure reference (Wikipedia / dictionary / raw data) → no design to recover; tell user, do not dispatch |
| Multi-modal | Image-heavy + you cannot inspect images directly → ask user to describe text or pre-extract via OCR / defuddle |

## Cultural-variant detection (v0.2.0+)

Before dispatching, the router determines:

1. **Primary language** — English / Japanese / Chinese (TC vs SC) / mixed / other
2. **Cultural register** — academic / business / literary / political / consumer-marketing
3. **Translation provenance** — is this a translation?

These signals are passed to the receiving skill so it can route to the
correct cultural variant of `lens-rhetoric` / `lens-persuasion` /
`lens-genre` / `lens-frame` per `artifact-deconstruct/protocols/lens-variant-selection.md`.

Plugin scope is permanently EN / JA / ZH per
[ADR-0004](../../docs/adr/0004-cultural-lens-variants.md). Other
languages get `-anglo` fallback **with explicit caveat**, not implied
coverage.

## What you get (output)

A 1-3 sentence dispatch:

> "Dispatching to `artifact-deconstruct` with `lens-persuasion +
> lens-rhetoric` preselected, language=Japanese,
> register=consumer-marketing → variants `-ja`. Running now."

Then the dispatched sibling skill runs.

## Rules

- Do NOT perform deconstruction in this skill — only route
- Do NOT explain lens content — let the dispatched skill do that
- Recommend ONE skill, not multiple
- If the user already specified the skill, skip routing and invoke directly
- If none of the skills fit, say so honestly — not every artifact deserves deconstruction

## See also

- [`SKILL.md`](SKILL.md) — full canon
- Sister skills: [`artifact-deconstruct`](../artifact-deconstruct/) | [`argument-deconstruct`](../argument-deconstruct/) | [`assumption-surface`](../assumption-surface/)
- Cultural-variant routing: [`../artifact-deconstruct/protocols/lens-variant-selection.md`](../artifact-deconstruct/protocols/lens-variant-selection.md)
- Plugin overview: [`../../README.md`](../../README.md)
