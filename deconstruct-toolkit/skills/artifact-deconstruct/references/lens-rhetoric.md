# Lens: Rhetorical Analysis (Burke + Toulmin)

> **Sources**:
> - Kenneth Burke, *A Grammar of Motives* (Prentice-Hall, 1945; expanded by University of California Press, 1969). The dramatistic pentad (act / scene / agent / agency / purpose) is introduced in the Introduction and developed throughout Part One. Burke's framing question per Introduction: "What is involved, when we say what people are doing and why they are doing it?"
> - Stephen Toulmin, *The Uses of Argument* (Cambridge University Press, 1958; updated edition with new preface 2003). 264 pages total. The 6-component argument model is in Ch 3 "The Layout of Arguments." The model itself is concentrated in roughly the first 14 pages of Ch 3 (the "heart" of the chapter per academic reception).

> **Synthesis note**: This file combines Burke's dramatistic pentad (1945) and Toulmin's argument model (1958). The two were not co-published. Combining them is a methodological choice by `deconstruct-toolkit` — Burke surfaces *motive structure* (why the argument is being made), Toulmin surfaces *logical structure* (whether the argument coheres). They complement rather than contradict. For deeper argument-only analysis, see also `argument-deconstruct/references/lens-toulmin.md` and `argument-deconstruct/references/lens-burke-pentad.md`, which deliberately split the two for fuller treatment. See [ADR-0003](../../../docs/adr/0003-lens-synthesis-disclosure.md).

Two complementary frameworks: Burke's **dramatistic pentad** for narrative
and motive analysis, Toulmin's **argument layout** for argument structure
and warrant surfacing.

## When to apply this lens

- Speeches, proposals, political texts
- Long-form arguments (op-eds, position papers, manifestos)
- Persuasive writing where structural validation matters
- Any artifact that makes claims and deserves rebuttal-test

## When NOT to apply

- Reference material with no argumentative structure
- Pure narrative without persuasive intent
- Single-claim short texts (a tagline doesn't deserve Toulmin)

---

## Part 1: Burke's Dramatistic Pentad

For any narrative or argument, identify five elements:

| Element | Asks |
|---|---|
| **Act** | What action is called for? What is being done or recommended? |
| **Scene** | Where / when does it take place? What's the context? |
| **Agent** | Who's the actor? Who's responsible? |
| **Agency** | How? What means / tools / methods? |
| **Purpose** | Why? What's the ultimate goal? |

### Pentad ratios — the critical move

After identifying all 5, examine which **two elements dominate**. The
ratio reveals the underlying motive structure:

| Ratio | Meaning |
|---|---|
| Scene-Act | "Circumstances force the action" — situational determinism |
| Agent-Act | "Who you are determines what you do" — character-driven |
| Agent-Agency | "Who you are determines how" — identity-via-method |
| Act-Purpose | "The action *is* the goal" — process-driven |
| Agency-Purpose | "The means determine the ends" — instrumental |
| Scene-Agent | "Setting determines who you become" — structural |

Most arguments hide behind a **claimed** ratio while operating on a
**different** one. Surfacing the discrepancy is the deconstruction.

### Worked example: Tech company DEI speech

- Act: "Hire 500 underrepresented engineers"
- Scene: "Post-2020 racial reckoning"
- Agent: "Our company"
- Agency: "Targeted university partnerships + sponsorship"
- Purpose: "Build the most diverse engineering team in industry"

- Claimed ratio: **Agent-Act** ("we are taking action because we are committed")
- Actual ratio: **Scene-Act** ("we are taking action because the moment demands it")

The deconstruction: the speech presents *character-driven* commitment
but is actually *circumstance-driven* response. This isn't necessarily
bad — but the speech style misleads about the underlying motive.

---

## Part 2: Toulmin's Argument Model

For any argumentative text, surface six components. **The critical move
is making the warrant explicit** — most arguments hide their warrant.

| Component | Question |
|---|---|
| **Claim** | What's the conclusion? |
| **Grounds** | What evidence supports it? |
| **Warrant** | What's the implicit bridge from grounds to claim? |
| **Backing** | What authority backs the warrant? |
| **Rebuttal** | What counter-arguments are acknowledged? |
| **Qualifier** | Under what conditions does the claim hold? |

### How to surface a hidden warrant

1. State the claim and grounds explicitly
2. Ask: "How does the grounds *get to* the claim? What must be true for the leap to work?"
3. The answer is the warrant. State it as a sentence beginning with "Because…"
4. Test the warrant: would a reasonable opponent accept it?

### Example: Industry-trend argument

> "60% of strategy teams have adopted AI tools, so we should too."

- **Claim**: We should adopt AI tools.
- **Grounds**: 60% industry adoption rate (cited from survey).
- **Hidden Warrant**: "Following industry majority is the correct strategy."
- **Backing**: An industry survey (which itself does not validate the warrant).
- **Missing Rebuttal**: What if the industry is wrong? What if our context differs?
- **Missing Qualifier**: Under what conditions does this not apply?

The deconstruction: the argument's persuasive force comes from a
warrant the writer never states and likely could not defend. Industry
follow-the-leader logic is the warrant — and that's a substantive
claim deserving its own grounds.

### Common warrant types (recognize these)

| Warrant pattern | Example |
|---|---|
| "Authority X said it, so it's true" | "Gartner says…" |
| "Majority does it, so it's right" | "60% have adopted…" |
| "It worked there, so it works here" | "Stripe does it this way…" |
| "Past trend predicts future" | "X has grown 10 years, so it will continue…" |
| "Correlation implies causation" | "Adopters perform better, so adoption causes performance" |
| "If we don't, we'll lose" | "Falling behind in AI = falling behind period" |

---

## Combining Burke + Toulmin

The two frameworks complement each other:

- **Burke** reveals the *motive structure* — why the argument is being made
- **Toulmin** reveals the *logical structure* — whether the argument coheres

A strong argument has both clear pentad ratios AND a defensible warrant.
A weak argument either obscures motive or hides warrant — usually
both.

### Output format

```markdown
### Burke pentad
- Act: ...
- Scene: ...
- Agent: ...
- Agency: ...
- Purpose: ...
- **Claimed ratio**: <pair>
- **Actual ratio**: <pair> (if differs from claimed)

### Toulmin model
| Component | Content |
|---|---|
| Claim | ... |
| Grounds | ... |
| Warrant (hidden) | ... |
| Backing | ... |
| Rebuttal acknowledged? | yes/no |
| Qualifier present? | yes/no |
```

End with a 1-line synthesis: "The argument operates on warrant X,
which is undefended; the pentad ratio Y reveals motive Z."

## Pitfalls

- **Naming pentad without ratio**: just listing 5 elements is bookkeeping. The ratio analysis is where insight lives.
- **Missing the warrant**: if your Toulmin section says "warrant: data supports claim", you have not surfaced the warrant. The warrant is *why* data → claim, not *that* data → claim.
- **Forcing rebuttal where none belongs**: if the argument acknowledges no rebuttal, **say so** as a finding — do not invent one.
- **Treating qualifier as decoration**: a missing qualifier ("always," "everyone," "everywhere") is a red flag worth naming.
