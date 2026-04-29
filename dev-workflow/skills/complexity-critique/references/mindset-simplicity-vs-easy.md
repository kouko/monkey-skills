# Simplicity-vs-Easy Mindset

> **Bundled functional copy.** Canonical version with full
> cross-references lives at
> `domain-teams:code-team/standards/mindset-simplicity-vs-easy.md`.
> References below to sibling mindsets (`mindset-*.md`) resolve in
> this `references/` directory. References to other code-team
> standards (e.g. `pragmatic-principles.md`, `refactoring-standard.md`,
> `solid-principles.md`) are descriptive — install `domain-teams`
> to read them. Drift between this copy and the canonical version
> is governed by the SSOT policy in
> `domain-teams:code-team/standards/mindset-extension-standard.md`.

A philosophical anchor for design-time decisions: *simple* and *easy*
are not the same thing, and the conflation is the most common single
source of accidental complexity. Simple is an objective property of
the design; easy is a subjective property of the human evaluating it.
The mindset is the discipline of choosing simple over easy when they
disagree.

## Primary Sources

- **Hickey, R. (2011) "Simple Made Easy"**, Strange Loop. https://www.infoq.com/presentations/Simple-Made-Easy/ — the canonical source for the distinction. Hickey traces *simple* to its etymology: *sim-plex*, "one fold" — opposed to *complex* / *complected*, "braided together". *Easy* traces to "near at hand" — adjacent to one's existing capability.
- **Hickey, R. (2012) "The Value of Values"**, JaxConf / InfoQ. https://www.infoq.com/presentations/Value-Values/ — develops the same intuition through immutable values vs stateful objects.
- **Moseley, B. & Marks, P. (2006) "Out of the Tar Pit"**. https://curtclifton.net/papers/MosesleyMarks06a.pdf — the formal essential-vs-accidental complexity distinction that supplies the theoretical backing for Hickey's practitioner framing.

## The Core Distinction

| Property | Simple | Easy |
|----------|--------|------|
| Etymology | *sim-plex* — one fold | "near at hand" |
| Measure | Objective — about the design | Subjective — about the evaluator |
| Stability | Absolute, doesn't change | Drifts as you learn |
| Test | "Is this concept braided with another?" | "Is this familiar to me right now?" |
| Failure mode when chosen | Initial unfamiliarity | Long-term complexity |

**Hickey, *Simple Made Easy* (2011)**:

> *"We have to choose simple things. We can't always make them easy,
> but we can stop making things complex."*

## Why the Distinction Matters

When designers reach for the *easy* solution — the familiar pattern,
the framework already adopted, the abstraction used last project —
they often introduce complexity. The easy path complects: it weaves
new concerns into pre-existing structures because the structures were
"already there".

The *simple* solution may be unfamiliar. It may require thinking. But
it does not braid concerns that should be separable. Hickey's wager:
familiarity feels productive in the short term; simplicity *is*
productive over the lifetime of the code.

## Complecting: The Verb Behind Complexity

Hickey resurrects *complect* — to braid or twine together. Complexity
is the result of complecting concerns that should be independent.
Examples of common complections:

- **State and identity** — using a mutable object both as the
  current value and as the long-lived reference
- **Data and behavior** — a method that both reads and modifies
  internal state, so callers can't reason about it as a function
- **Configuration and code** — magic strings, environment-dependent
  branches, framework conventions that the call site has to "know"
- **Time and value** — a method whose result depends on when it is
  called, not just on its arguments

Each complection is a future debugging session. Each separation is a
piece of future change made cheap.

## What "Simple" Looks Like in Code

A simple piece of code:

- Has **one role** — the function does one thing, the data structure
  represents one concept
- Has **one task** at a time — no multi-purpose methods that "also"
  do logging, also do caching, also do validation
- Has **one concept** per construct — no objects that are both
  identity and value, both API and storage

If the explanation of what the code does has to use the word "and"
multiple times, simplicity is the diagnostic the explanation is
failing.

## The Choice in Practice

When designing, the discriminating question is:

> "Am I choosing this because it's simple, or because it's familiar?"

Familiar feels productive. Familiar wins arguments. Familiar passes
code review on autopilot. But familiar often means "we've used this
pattern before" — independent of whether the pattern is appropriate
to the current problem.

The mindset is the discipline of asking the question and tolerating
the unfamiliar answer when simple disagrees with easy.

## Out of the Tar Pit's Formal Backing

Moseley & Marks separate complexity into:

- **Essential complexity** — the irreducible difficulty of the
  problem itself; you cannot remove this, you can only confront it
- **Accidental complexity** — complexity introduced by the chosen
  representation, language, framework, or approach

Their thesis: in real systems, accidental dominates essential by a
large margin, and the largest accidental sources are *state* and
*control flow*. The simple-vs-easy mindset is the operational version
of this thesis: a designer's job is to identify and refuse accidental
complexity, especially complexity invited by familiar patterns.

## Practical Application

Before committing to a design choice:

1. **Articulate what the code's *one* job is.** If you can't, the
   design is already complected.
2. **Ask: would I choose this if it were unfamiliar?** If "no", you
   are choosing easy, not simple. That may still be the right call,
   but admit which call you are making.
3. **Test for complection** — what happens if I want to change just
   one of these concerns? If I can't, they were braided.
4. **Prefer separation over reuse.** Reusing a class because it
   "already does most of this" usually adds a complection. A new,
   single-purpose function is often the simpler answer.

## When This Mindset Doesn't Apply

- **Genuine essential complexity** — some problems are irreducibly
  hard (concurrency, distributed consensus, cryptography). The
  mindset doesn't promise simple solutions to complex problems; it
  promises that you should not *add* accidental complexity on top.
- **Time-boxed deliverables with throwaway code** — an MVP under a
  deadline may legitimately reach for "easy because it ships". The
  mindset says: name that you're choosing easy, so future-you knows
  the debt.
- **Team conventions that keep the team productive** — a
  team-familiar pattern that is "easy" but not "simple" may be the
  right pragmatic choice. The mindset asks you to name the trade,
  not to ban the choice.

## Cross-References

- `pragmatic-principles.md` — KISS, ETC (Easier to Change), YAGNI —
  pragmatic restatements of the same intuition at the heuristic level
- `mindset-design-is-taking-apart.md` — sibling mindset; the
  *complect* / *compose* distinction is the operational mechanism
  this mindset names
- `mindset-data-over-abstractions.md` — sibling mindset; choosing
  data over custom types is one specific application of "choose
  simple over easy"
- `refactoring-standard.md` — Bad Smells (Long Method, Large Class,
  Feature Envy) — symptoms of choices that were easy at the time
  but not simple

## Anti-Patterns

- ❌ **Familiarity as proxy for fit** — "we always use X" without
  asking whether X braids with the current problem
- ❌ **Pattern-matching to last project** — porting an architecture
  that worked once into a context where its complections don't pay off
- ❌ **Reusing a class because it "mostly does this"** — adding a
  third reason for the class to change (SRP violation; see
  `solid-principles.md`)
- ❌ **Conflating concise with simple** — a one-line clever
  expression can be highly complected (state, control, side effect
  in one line); brevity ≠ simplicity
- ❌ **Refusing to admit you chose easy** — pragmatic shortcuts are
  fine; pretending the shortcut was the simple choice misleads the
  next reader
