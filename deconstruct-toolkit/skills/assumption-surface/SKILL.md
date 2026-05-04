---
name: assumption-surface
description: >-
  Surface the hidden assumptions in any text — strategy memo, social-
  media thread, policy brief, opinion piece. Outputs a 5–15 row
  assumption table with strength ratings (foundational / load-bearing
  / decorative) and falsifiability checks per foundational assumption.
  Use when user asks "find the hidden assumptions / what is this
  *assuming* / stress-test these claims / 揭露隱性假設". Do NOT use
  for full design analysis (use artifact-deconstruct), pure argument
  structure (use argument-deconstruct), or self-thinking (use
  philosophers-toolkit:descartes-methodical-doubt).
  隠れた前提の浮上化。隱性假設揭露。
---

# Assumption Surface

A focused, atomic skill: extract the **hidden assumptions** that an
external text takes for granted. Where `argument-deconstruct` builds
a full Toulmin layout, this skill produces a flat **assumption
table** — faster, broader, less structural.

The output is a working surface for the user to inspect, not a
finished argument. It is what you'd run before a board meeting to
prepare counter-questions, or before a contract signing to spot what
the other side is *quietly assuming you'll grant*.

## When to use

Trigger phrases (any language):

- 「揭露這份備忘錄的隱性假設」「這個策略在假設什麼」「stress-test 這些主張」
- "find the hidden assumptions", "what is this *assuming*", "stress-test these claims before deciding"
- "surface the implicit world-model"

Skip when:

- User wants a **full argument deconstruction** with claim-grounds-warrant chain — use `argument-deconstruct`
- User wants **all design layers** (rhetoric / frame / persuasion / etc) — use `artifact-deconstruct`
- User wants to doubt their **own** premises — use `philosophers-toolkit:descartes-methodical-doubt`
- Target is < 100 words — there are not enough assumptions to surface usefully

## Workflow

Four steps:

```
Assumption Surface Progress:
- [ ] Step 1: List all explicit claims
- [ ] Step 2: Run reverse-Toulmin per claim → extract assumptions
- [ ] Step 3: Apply symptomatic reading → extract negative-space assumptions
- [ ] Step 4: Classify each assumption + run falsifiability test on foundational ones
```

### Step 1: List explicit claims

Read the artifact and list every distinct claim it makes. Use a
numbered list. Aim for 5–20 claims for a typical strategy memo or
op-ed.

A "claim" here is broader than Toulmin's claim — it includes any
assertion of fact, value, or recommendation. Examples:
- "Our market is growing 20% YoY"
- "Customer trust is the foundation of our business"
- "We should invest in mobile-first design"

### Step 2: Reverse-Toulmin per claim

For each claim, ask: **"What must already be true for this claim to make sense?"**

Each answer is an assumption. Write each as a sentence beginning with
"Assumes that…".

Read [`protocols/reverse-toulmin.md`](protocols/reverse-toulmin.md) for
the full method. Quick form:

| Claim | Reverse-Toulmin assumptions |
|---|---|
| "Our market is growing 20% YoY" | Assumes that current measurement methodology captures market boundaries; assumes growth pattern continues; assumes competitor data is verifiable |
| "Customer trust is the foundation" | Assumes that customer trust is meaningfully measurable; assumes our customer composition is stable enough that "trust" is a coherent variable |

A single claim usually yields 2–4 assumptions. Don't force more.

### Step 3: Symptomatic reading

Now scan the artifact for what is *not said*. Read [`references/lens-symptomatic-reading.md`](references/lens-symptomatic-reading.md)
for the full method.

Quick form: ask three questions of the artifact:

1. **What obvious counter-question is not posed?** (e.g., "if we're growing 20% but margin is shrinking, why does growth dominate the conversation?")
2. **What category of evidence is missing?** (e.g., quant claims with no source; qual claims with no methodology)
3. **What would the artifact's writer be uncomfortable to acknowledge?** (e.g., losing customers; pivoting away from the founding thesis; that a competitor is winning)

Each answer is an assumption — specifically, an assumption that
**something is not worth raising**.

### Step 4: Classify and falsifiability-test

Classify each surfaced assumption into one of three strength
categories:

| Category | Definition |
|---|---|
| **Foundational** | If false, the entire argument collapses |
| **Load-bearing** | If false, the argument has a serious wound but might survive |
| **Decorative** | If false, the argument loses style points but core stands |

For every **foundational** assumption, write a **falsifiability test**:
"This assumption is falsified if X observation is made."

If you cannot articulate a falsifiability test for a foundational
assumption, **flag it** — that is the marker of a *load-bearing
unfalsifiable* assumption, the most dangerous kind.

## Output format

```markdown
# Assumption Surface: <text title>

## Source claims (numbered)
1. ...
2. ...
3. ...
...

## Assumption table

| # | Assumption | Source claim(s) | Strength | Falsifiability test |
|---|---|---|---|---|
| 1 | Assumes that ... | claim 1 | Foundational | Falsified if ... |
| 2 | Assumes that ... | claim 2 | Load-bearing | (n/a if not foundational) |
| 3 | Assumes that ... | symptomatic reading | Decorative | (n/a) |
| ... | ... | ... | ... | ... |

## Foundational assumptions worth challenging

For each foundational assumption, propose a counter-question:

- **Assumption 1**: <restate>. **Counter-question**: ...
- **Assumption N**: ...

## Bottom line

<One sentence: the artifact rests on **N** foundational assumptions, of
which **K** are unfalsifiable; the most contestable is **X**.>
```

## Lenses available

This skill ships with 1 self-contained lens reference:

- [`references/lens-symptomatic-reading.md`](references/lens-symptomatic-reading.md) — Althusser-influenced "reading the absent" (1968 / 1970 *Reading Capital*)

Toulmin appears in this skill via the reverse-Toulmin protocol (which
inverts the standard direction). The full Toulmin reference lives in
`argument-deconstruct/references/lens-toulmin.md`. Per ADR-0002,
each skill is self-contained — this skill's protocol embeds the
relevant Toulmin material rather than cross-referencing.

## Sample fixtures

- [`assets/sample-company-strategy-memo.md`](assets/sample-company-strategy-memo.md)
- [`assets/sample-tweet-thread-productivity.md`](assets/sample-tweet-thread-productivity.md)

## Anti-patterns

- **Confusing "claim" with "assumption"**: a claim is what's *said*; an assumption is what's *taken for granted to make the claim work*.
- **Inflating assumption count**: more is not better. 5–15 is the sweet spot. 30+ assumptions usually means you're listing claims as assumptions.
- **Decorative-only output**: if all your surfaced assumptions are "decorative," you have not pressed hard enough — every text rests on at least one foundational assumption.
- **Skipping falsifiability test**: foundational assumptions without falsifiability tests are not yet useful for the user. They are just labels.
- **Treating symptomatic reading as gotcha-hunting**: the goal is to surface what's structurally absent, not to catch the writer in tonal slips. Stay structural.
