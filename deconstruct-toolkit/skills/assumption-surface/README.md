# assumption-surface

> Pull the hidden assumptions out of any text and rate which ones the argument actually rests on.

Atomic skill. Where `artifact-deconstruct` runs full 6-lens × 6-dim and
`argument-deconstruct` runs full Toulmin + Burke, `assumption-surface`
zooms into a single deliverable: **a table of hidden assumptions**.
Faster than full deconstruction; designed for stress-testing a memo /
proposal / claim before you decide whether to act on it.

## When to use

Trigger phrases (any language). Mix EN, JP, ZH-TW:

- "find the hidden assumptions", "what is this *assuming*"
- "stress-test these claims before deciding", "surface the implicit world-model"
- 「揭露這份備忘錄的隱性假設」「這個策略在假設什麼」
- 「隠れた前提を出して」「この主張は何を前提にしている」

When to skip:

- Target text is < 100 words — not enough surface to surface from
- You want a polished argument-map deliverable — not an inspection table

When to use sister skills instead:

- Need a full design teardown of an artifact → `artifact-deconstruct`
- Argument-structure analysis with explicit Toulmin warrant ladder → `argument-deconstruct`
- Doubting your **own** premises (not an external text) → `philosophers-toolkit:descartes-methodical-doubt`
- Code → `sourceatlas`

## Method

Four moves, applied as a layered stack:

### 1. Reverse-Toulmin

Run Toulmin's claim-grounds-warrant model **backwards**: start from the
text's claims, work backward to the warrant the author would have to
believe for the grounds to support the claim. Surfaces the implicit
load-bearing belief. See [`protocols/reverse-toulmin.md`](protocols/reverse-toulmin.md).

### 2. Symptomatic reading (Althusser-influenced)

Per [`references/lens-symptomatic-reading.md`](references/lens-symptomatic-reading.md) —
read for what the text **does not say**. Absences are not gaps; they
are structural data about what the author considered too obvious to
state, or too risky to state. Borrowed from Althusser & Balibar,
*Reading Capital* (*Lire le Capital*, Maspero 1965; abridged 1968;
Brewster trans. NLB 1970).

### 3. Counterfactual probe

For each surfaced assumption, ask: "What would the argument look like
if this assumption were false?" If the argument collapses, the
assumption is **foundational**. If the argument survives in altered
form, **load-bearing but not foundational**. If unchanged,
**decorative**.

### 4. Frame audit

What conceptual frame is the text operating in? (Goffman / Lakoff
sense.) Naming the frame surfaces assumptions baked into the framing
itself.

## 3-tier strength classification

Every assumption surfaced gets one of three strength ratings:

| Tier | Meaning | What to do |
|---|---|---|
| **Foundational** | If false, argument collapses entirely | MUST falsifiability-test |
| **Load-bearing** | If false, argument needs major reframing | SHOULD falsifiability-test |
| **Decorative** | If false, argument survives unchanged | Note and move on |

## Falsifiability test (foundational tier)

For every foundational assumption, design a test that could **prove it
wrong**. If no such test exists, the assumption is unfalsifiable —
itself a finding worth surfacing. Per Popper, unfalsifiable
assumptions cannot be argued from; they can only be believed. An
unfalsifiable foundational assumption is the most dangerous kind and
must be flagged explicitly in the report.

## What you get (output)

- **Source claims** — numbered list of every distinct claim the text makes
- **Assumption table** (5–15 rows) — assumption | source claim(s) | strength tier | falsifiability test (foundational only)
- **Foundational assumptions worth challenging** — counter-question per foundational row
- **Bottom line** — one sentence: the artifact rests on N foundational assumptions, of which K are unfalsifiable; the most contestable is X

5–15 rows is the sweet spot. 30+ usually means you are listing claims
as assumptions.

## Worked example

Sample fixtures shipped:

- [`assets/sample-company-strategy-memo.md`](assets/sample-company-strategy-memo.md)
- [`assets/sample-tweet-thread-productivity.md`](assets/sample-tweet-thread-productivity.md)

Eval ground-truth (must-find lists):

- `eval/cases/assumption-surface-01-strategy-memo.yaml`
- `eval/cases/assumption-surface-02-tweet-thread.yaml`

## See also

- [`SKILL.md`](SKILL.md) — full canon (workflow, output template, anti-patterns)
- [`references/lens-symptomatic-reading.md`](references/lens-symptomatic-reading.md) — Althusser & Balibar source
- [`protocols/reverse-toulmin.md`](protocols/reverse-toulmin.md) — backward-Toulmin method
- Sister skills: [`artifact-deconstruct`](../artifact-deconstruct/) (full 6-lens) | [`argument-deconstruct`](../argument-deconstruct/) (full Toulmin)
- Plugin overview: [`../../README.md`](../../README.md)
