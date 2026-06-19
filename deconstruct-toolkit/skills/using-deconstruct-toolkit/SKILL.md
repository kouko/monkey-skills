---
name: using-deconstruct-toolkit
description: |
  Route to the right deconstruction skill when the user wants to reverse-engineer/拆解 an artifact, argument, or hidden assumptions but hasn't named which. Code → sourceatlas; forward production → copy/docs/design plugins.
---

# Using Deconstruct Toolkit

Help the user find the right deconstruction skill for their artifact.
Detect what they brought, what they want surfaced, then dispatch to
the best-fit sibling skill with the appropriate lens combination
preselected.

## Boundary check first

Before routing, run a 3-question boundary check. If any answer is
"yes," do NOT route into this toolkit — redirect.

| Question | If yes, redirect to |
|---|---|
| Is the target source code, a code repository, or a build artifact? | `sourceatlas` (impact / flow / overview / pattern / deps) |
| Does the user want help thinking through their *own* problem (not analyzing an external artifact)? | `philosophers-toolkit` |
| Does the user want to **produce** copy / docs / design / a slide deck (forward direction, not reverse)? | `copywriting-toolkit` / `docs-team` / `design-team` / `slides-toolkit` |

If all three are "no," proceed to routing.

## Routing Guide

Ask the user ONE question: **"What did you bring, and what do you want to surface?"**

Then match the answer through the two-axis lookup below.

### Axis 1 — Artifact type

| Artifact | Default skill | Default lens combination |
|---|---|---|
| Marketing copy / landing page / advertising | `artifact-deconstruct` | lens-persuasion + lens-rhetoric |
| Document pack / playbook / SOP / onboarding kit | `artifact-deconstruct` | lens-genre + 6-dimension full |
| UI / app onboarding flow / website screen | `artifact-deconstruct` | lens-ux + lens-persuasion |
| Long-form argument / op-ed / proposal / political text | `argument-deconstruct` | Toulmin + Burke pentad + warrant surface |
| Strategy memo / policy brief / social-media thread (suspect hidden assumptions) | `assumption-surface` | reverse-Toulmin + symptomatic reading |
| Speech / political address | `artifact-deconstruct` | lens-rhetoric + lens-frame |
| Literature / film / advertising imagery | `artifact-deconstruct` | lens-semiotic + lens-frame |
| Slide deck / presentation | `artifact-deconstruct` | lens-rhetoric + lens-genre |

### Axis 2 — User intent override

The artifact type sets the default; the user's stated intent can override which skill to dispatch:

| User says | Override to |
|---|---|
| "拆解設計" / "deconstruct the design" / "為什麼這份寫得這麼好" | `artifact-deconstruct` (full 6-lens × 6-dim treatment) |
| "找隱性假設" / "surface the hidden assumptions" / "what is this *assuming*" / "stress-test the claims" | `assumption-surface` (atomic, fast) |
| "拆解論證" / "find the warrant" / "is this argument valid" / "where does this argument fail" | `argument-deconstruct` (Toulmin focus) |
| "找說服機制" / "what's manipulating me here" / "spot the dark patterns" | `artifact-deconstruct` with lens-persuasion + lens-ux preselected |

If artifact type and user intent disagree, **user intent wins**.

## Three filters before dispatching

After tentative routing, run these filters:

1. **Length filter** — if the artifact is < 200 words AND not a structured argument, there is not enough design to deconstruct. Tell the user, do not dispatch.
2. **Information-only filter** — if the artifact is purely reference (Wikipedia, dictionary entry, raw data table), there is no *design* to recover. Tell the user, do not dispatch.
3. **Multi-modal filter** — if the artifact is image-heavy (UI screenshots, ad imagery) and you cannot inspect images directly, ask the user to either (a) describe the visual elements in text, or (b) pre-extract text via OCR / defuddle.

## Detect language and cultural register (v0.2.0+)

Before dispatching, determine three signals so the downstream skill can
select the right cultural-lens variant:

1. **Primary language** — English / Japanese / Chinese (TC vs SC) /
   mixed / other (Korean / Vietnamese / Thai / etc.)
2. **Cultural register** — academic / business / literary / political
   / consumer-marketing
3. **Translation provenance** — is this a translation (e.g.,
   JP-original translated to English)?

Pass these signals to the dispatched skill in the dispatch sentence.
The receiving skill (`artifact-deconstruct`) routes to the appropriate
language variant of `lens-rhetoric` / `lens-persuasion` / `lens-genre`
/ `lens-frame` per
`artifact-deconstruct/protocols/lens-variant-selection.md`.

Plugin scope is permanently EN / JA / ZH per
[ADR-0004](../../docs/adr/0004-cultural-lens-variants.md). For
artifacts in other languages, dispatch with `-anglo` fallback **and a
caveat** ("not grounded in your artifact's cultural register") rather
than pretending coverage.

## Disambiguation prompts

If the user's request is ambiguous, ask ONE narrowing question. Examples:

- "Are you bringing the *artifact itself* (copy, screenshots, document) or asking me to *find one* online?"
  → If "find one online", the user likely needs research first; suggest fetching with defuddle or attaching the document.

- "Do you want a *full deconstruction* (design, frameworks, mechanisms, ethics, weaknesses) or a *focused look* at one aspect?"
  → If "focused", route to `argument-deconstruct` (for argument structure) or `assumption-surface` (for hidden assumptions).

- "Is the goal *learning* (so you can reproduce the technique) or *judgment* (so you can decide if you trust this)?"
  → Both go to `artifact-deconstruct`, but the report emphasis differs. Note the user's purpose so the skill can adjust the "5 replicable lessons" vs "weaknesses & warnings" emphasis.

## After routing

Once you've identified the right skill:

1. State which skill you're dispatching and why (one sentence)
2. State the lens combination you've preselected (one sentence)
3. Invoke the skill — do NOT perform the deconstruction yourself

Example:
> Dispatching to `artifact-deconstruct` with `lens-persuasion + lens-rhetoric` preselected, language=Japanese, register=consumer-marketing → variants `-ja`. Running now.

## Rules

- Do NOT perform deconstruction in this skill — only route
- Do NOT explain lens content in detail — let the dispatched skill do that
- Recommend ONE skill, not multiple. If the user wants two passes (e.g., assumption-surface first, then artifact-deconstruct), do them sequentially
- If the user already specified the skill, skip routing and invoke directly
- If none of the skills fit, say so honestly — not every artifact deserves deconstruction; sometimes a normal read is correct

## When NOT to use this skill

| Situation | Use instead |
|---|---|
| User said `/deconstruct-toolkit:artifact-deconstruct` (or similar) explicitly | Invoke that skill directly |
| Target is code | `sourceatlas` |
| User is debugging their own thinking | `philosophers-toolkit` |
| User wants to write new copy / docs / design | `copywriting-toolkit` / `docs-team` / `design-team` |
| Artifact < 200 words and not a structured argument | Tell the user there's not enough design to deconstruct |
