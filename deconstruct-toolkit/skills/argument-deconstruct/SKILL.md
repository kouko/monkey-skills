---
name: argument-deconstruct
description: >-
  Reverse-engineer the structure of any long-form argument — op-ed,
  proposal, manifesto, political text, paper introduction. Surfaces
  the claim-grounds-warrant chain, makes hidden warrants explicit,
  detects missing rebuttals, identifies Burke pentad ratios, and
  produces an argument map with ethical position. Use when user asks
  "拆解這個論證 / 反駁這份提案 / find the warrant / where does this
  argument fail". Do NOT use for non-argumentative texts (use
  artifact-deconstruct), for hidden-assumption hunts (use
  assumption-surface), or for codebase reasoning (use sourceatlas).
  論証の脱構築。論證逆向解構。
---

# Argument Deconstruct

Reverse-engineer the *logical* structure of an argument. Where
`artifact-deconstruct` covers all design layers across 6 lenses,
this skill goes **deeper into one layer**: the argument itself.

The critical move: **make the hidden warrant explicit**. Most
arguments hide their warrant; surfacing it is the deconstruction.

## When to use

Trigger phrases (any language):

- 「拆解這個論證」「這份提案論證哪裡弱」「找隱性 warrant」
- "deconstruct this argument", "find the warrant", "where does this argument fail"
- "is this argument valid" / "what's the hidden assumption in this claim"

Skip when:

- Artifact has no argumentative structure (descriptive / narrative / reference) — use `artifact-deconstruct`
- User wants hidden-assumption hunting across many claims — use `assumption-surface`
- Target is < 200 words — there is not enough argument to deconstruct
- Target is code — use `sourceatlas`

## Workflow

Five steps:

```
Argument Deconstruction Progress:
- [ ] Step 1: Identify the central claim (and any sub-claims)
- [ ] Step 2: Run Toulmin model on each claim
- [ ] Step 3: Run Burke pentad on the argument as narrative
- [ ] Step 4: Generate argument map (mermaid)
- [ ] Step 5: Self-check — warrant surfaced? rebuttal accounted for?
```

### Step 1: Identify the central claim

Read the artifact and answer:

- **What is the main claim?** State it as a single sentence beginning with "The text claims that…"
- **What sub-claims support it?** List them as bullets.
- **What is the conclusion the writer wants the reader to reach?** This may differ from the explicit claim — the writer may be asking the reader to *act*, not just *believe*.

If you cannot extract a clear central claim, the artifact may not be argumentative. Stop and route to `artifact-deconstruct` instead.

### Step 2: Run Toulmin on each claim

For the central claim and each sub-claim, fill in the 6-component model. Read [`references/lens-toulmin.md`](references/lens-toulmin.md) for the full method.

Quick form:

| Component | Question |
|---|---|
| Claim | What is the conclusion? |
| Grounds | What evidence supports it? |
| **Warrant (hidden)** | What must be true for grounds → claim to work? |
| Backing | What authority backs the warrant? |
| Rebuttal | What counter-arguments are acknowledged? |
| Qualifier | Under what conditions does the claim hold? |

**Critical rule**: If your warrant entry just restates the grounds, you have not surfaced the warrant. The warrant is the *bridge* — usually a generalization the writer takes for granted.

### Step 3: Run Burke pentad

For the argument viewed as narrative, identify five elements. Read [`references/lens-burke-pentad.md`](references/lens-burke-pentad.md) for the full method.

Quick form:

- Act / Scene / Agent / Agency / Purpose
- **Claimed ratio**: which two dominate by surface emphasis?
- **Actual ratio**: which two dominate by deeper structure?
- **Discrepancy**: if claimed ≠ actual, the argument is doing motive-laundering

### Step 4: Generate argument map

Use [`protocols/argument-mapping.md`](protocols/argument-mapping.md) for the mermaid format. The map shows:

- Central claim at the top
- Sub-claims branching down
- Grounds attached to each claim
- **Warrants explicitly labeled in dotted lines** (since they are usually hidden)
- Missing rebuttals marked with ⚠️

### Step 5: Self-check

Before delivering:

- [ ] **Warrant surfaced**: did I write each warrant as a sentence starting with "Because…", and would a reasonable opponent contest it?
- [ ] **Rebuttal accounted for**: did I note whether the argument acknowledges counter-arguments, and if not, what counter-arguments would matter?
- [ ] **Qualifier present**: did I note whether the claim has conditions, or whether it overreaches with "always / everyone / never"?
- [ ] **Pentad ratio identified**: did I name the dominant two pentad elements, and did I note any discrepancy between claimed and actual?
- [ ] **Argument map renders**: does the mermaid block produce a readable graph?
- [ ] **Ethical position assigned** (if applicable): if the argument uses persuasion mechanisms beyond logical argumentation, did I name them and assign 🟢/🟡/🔴/⚫?

## Lenses available

This skill ships with 2 self-contained lens references:

- [`references/lens-toulmin.md`](references/lens-toulmin.md) — Toulmin argument model (1958)
- [`references/lens-burke-pentad.md`](references/lens-burke-pentad.md) — Burke dramatistic pentad (1945)

Both are also present in `artifact-deconstruct/references/lens-rhetoric.md` (which combines them). The duplication is intentional per ADR-0002 — each skill is independently loadable.

## Output format

```markdown
# Argument Deconstruction: <text title>

## Central claim
<one sentence>

## Toulmin layout

| Component | Content |
|---|---|
| Claim | ... |
| Grounds | ... |
| **Hidden warrant** | Because ... |
| Backing | ... |
| Rebuttal acknowledged? | yes/no — describe |
| Qualifier present? | yes/no — describe |

## Sub-claims (if any)
<repeat Toulmin per sub-claim>

## Burke pentad
- Act: ...
- Scene: ...
- Agent: ...
- Agency: ...
- Purpose: ...
- **Claimed ratio**: <pair>
- **Actual ratio**: <pair> (note any discrepancy)

## Argument map

\```mermaid
flowchart TD
    Claim[Main Claim] --> Sub1[Sub-claim 1]
    Sub1 -.warrant.-> W1[Hidden warrant: ...]
    Sub1 --> G1[Grounds: ...]
    Claim --> Sub2[...]
    ...
\```

## Findings
- Strongest move: ...
- Weakest move: ...
- Hidden warrant most worth contesting: ...
- Missing rebuttal that matters most: ...

## Bottom line
<One sentence: argument is **strong / sound-but-narrow / hand-waving /
manipulative** because **X**.>
```

## Sample fixtures

- [`assets/sample-op-ed-AI-regulation.md`](assets/sample-op-ed-AI-regulation.md)
- [`assets/sample-vc-pitch-memo.md`](assets/sample-vc-pitch-memo.md)

## Anti-patterns

- **Restating grounds as warrant**: a warrant must be a *bridge generalization*, not a restatement of the data
- **Inventing rebuttals where none belong**: if the argument acknowledges no rebuttal, **say so**; do not pretend it does
- **Pentad without ratio**: just listing 5 elements is bookkeeping; the ratio reveals motive
- **Argument map without warrants labeled**: the map's *value* is showing the hidden warrants — if you draw only claim→grounds, you reproduced the surface
- **Missing ethical position when persuasion exists**: if the argument also uses Cialdini-style appeals, assign 🟢/🟡/🔴/⚫
