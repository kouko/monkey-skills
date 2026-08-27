# Independent Advisor

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Get a second opinion on the current plan or decision from a **different
> executor** — a stronger model, a higher effort level, or another vendor.
> What changes is who answers, not which critique lens is applied.

---

## Overview — what this skill does

`loom-workflow:independent-advisor` consults an executor other than the one
you are talking to. Executor capability is written as a tier pair: model tier
`economy` / `standard` / `frontier` crossed with effort `low` / `medium` /
`high`. Those six words are the whole vocabulary — a record never substitutes
a vendor's marketing name for a tier.

Two modes:

- **`explore`** — the solution space is still open. An independent proposal is
  generated, both proposals are normalised to one template, anonymised, and
  judged blind under **both card orders**, so a position bias in the judge
  shows up instead of hiding inside a single verdict.
- **`audit`** — the work already exists. A single leg runs with full context
  and attacks the incumbent. No blind proposal leg is dispatched in this mode.

The mode is chosen from a fact you can quote — a commit identifier, a PR and
its state, an approval line, the user's own wording — recorded verbatim next
to the mode. When nothing is quotable, the skill asks you rather than guessing.

---

## When to use vs the sibling critique skills

| Situation | Skill |
|---|---|
| You want a different **executor** to answer — stronger model, higher effort, another vendor | `loom-workflow:independent-advisor` |
| You want a different **critique lens** on a proposal, same executor | `loom-workflow:proposal-critique` |
| You suspect over-engineering specifically | `loom-workflow:complexity-critique` |

The distinction is the whole point: the sibling skills change the lens, this
one changes the executor. Because it spends money and sends material off this
machine, it is the wrong tool when a lens change is what you actually want.

---

## Example invocation phrases

- "second opinion"
- "ask a stronger model"
- "get an independent read on this plan"
- "have another vendor's model check this"
- "run this by a higher effort level"

Japanese and Traditional Chinese phrasings fire the skill too — see the
sibling READMEs.

---

## Honest framing — what this does NOT give you

Read these before you rely on a result:

- **Privacy scope.** The privacy guarantee covers the **dispatch packet** —
  what is deliberately assembled and sent. It does not cover everything the
  external executor can read once it is running. Assume anything reachable
  from its environment is in scope for it.
- **Blindness is a claim about the packet, not the leg.** The challenger is
  not shown your proposal — it is kept out of the dispatch packet. But the
  challenger may still read files inside the range it was authorised to open,
  and those files can describe your proposal. So the report qualifies the
  independence claim rather than asserting it.
- **Agreement is weak evidence.** When two legs read the same material and
  reach the same conclusion, that agreement measures the material, not the
  world. It is not a strong signal, and a report must not present it as one.
- **No coverage claim.** The findings are a sample of what one other executor
  noticed under one dispatch. Nothing here surveys the whole risk space, and
  the skill never describes its output as covering everything.

---

## Files

```
independent-advisor/
├── README.md            <- English (this file)
├── README.ja.md         <- 日本語
├── README.zh-TW.md      <- 繁體中文
├── SKILL.md             <- operational file (for Claude)
└── scripts/
    └── test_independent_advisor_readmes.py
```
