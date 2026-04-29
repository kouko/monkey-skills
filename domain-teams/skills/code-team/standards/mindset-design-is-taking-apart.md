# Design-Is-Taking-Apart Mindset

A philosophical anchor for design-time decisions: good design is the
work of separating concerns and removing dependencies, not the work
of adding structure or features. The mindset reframes "design"
from constructive (assembling parts) to subtractive (pulling things
apart so each piece can stand alone).

## Primary Sources

- **Hickey, R. (2011) "Simple Made Easy"**, Strange Loop. https://www.infoq.com/presentations/Simple-Made-Easy/ — the canonical source for the *complect* / *compose* distinction and the argument that "simple" means "not braided together with something else".
- **Moseley, B. & Marks, P. (2006) "Out of the Tar Pit"**. https://curtclifton.net/papers/MosesleyMarks06a.pdf — argues that the dominant cost in real-world software is *complexity*, distinguishes essential from accidental complexity, and identifies state and control as the two largest accidental sources.
- **Ousterhout, J. (2018) *A Philosophy of Software Design*, 2nd edition**, Yaknyam Press. ISBN 978-1732102217. The "deep modules vs shallow modules" framing (deep = simple interface hiding substantial implementation; shallow = thin interface barely hiding a thin implementation) is Ousterhout's contribution to the same conversation Hickey opens.
- **Brooks, F. (1986) "No Silver Bullet — Essence and Accident in Software Engineering"**. https://www.cs.unc.edu/techreports/86-020.pdf — the original essential/accidental distinction that Moseley & Marks build on.

## The Core Insight

**Hickey, *Simple Made Easy* (2011)**:

> *"Design is about taking things apart."*

Good design is not measured by what you added. It is measured by what
you successfully kept separate — concerns that did not braid together,
dependencies that did not have to exist, coupling that the design
refused.

## Complect vs Compose

Hickey defines **complect** (verb) as "to braid or twine together".
Two concerns are *complected* when they cannot be reasoned about,
tested, or changed independently — even if the code looks tidy.

The opposite is **compose**: two pieces that fit together at a
boundary but do not reach into each other's internals. Composed pieces
can be replaced, tested in isolation, and combined with new pieces
they were never originally designed for.

| Trait | Complected | Composed |
|-------|-----------|----------|
| Independence | None | Each piece stands alone |
| Test surface | Coupled — must test together | Each piece testable in isolation |
| Change cost | Touching one risks breaking another | Local change stays local |
| Reuse | Bound to original context | Free to combine with new pieces |
| What it means in code | Inheritance, shared mutable state, "framework" base classes | Pure functions over data, narrow interfaces, dependency injection at edges |

## Why Composing Beats Constructing

When designing, the constructive instinct is "what features must this
have?" The subtractive instinct is "what could this *not* know
about?".

The subtractive question yields:
- **Smaller interfaces** — each piece's API is a list of what it
  needs from outside, not a list of what it provides
- **Cheaper change** — a local change touches one piece, not the
  graph of pieces that knew about it
- **Free composition** — pieces can be assembled in combinations the
  original designer did not anticipate

Out of the Tar Pit's argument is the formal version of the same
claim: most cost-of-change in software is *accidental* complexity —
state, control flow, coupling — that the design imposed but the
problem did not require.

## The Anti-Pattern: Kitchen Sink / God Object

The opposite of composition is the *kitchen sink* — one thing that
knows about everything, does everything, and cannot be changed
without breaking everything. Classic instances:

- The `User` class with 40 methods (auth, profile, billing, audit log)
- The `Application` singleton everything reaches into
- The `BaseController` / `BaseService` with shared state
- The framework's "everything-magic" decorator stack

Every helper method added to such a class is a small step deeper in.
Every "this feels related" addition is another braid.

## Practical Application

Before adding a method, wrapper, or abstraction, ask:

1. **Does this separate concerns, or combine them?** If two formerly
   independent concerns now both flow through this piece, you are
   complecting.
2. **Could this be a function over data instead?** A free function
   takes inputs and returns outputs without owning state — the most
   composed shape a piece of code can have.
3. **What would a reader of this code six months from now have to
   understand to change it safely?** The smaller the answer, the
   better the design.

## Ousterhout's Deep Module Refinement

Ousterhout sharpens the same intuition: a *deep module* has a small
interface hiding substantial implementation; a *shallow module* has
a thin interface barely covering a thin body. Shallow modules are
typically the result of over-applying "separation of concerns" — the
file count goes up, but each file barely earns its keep, and the
total cognitive load increases.

The mindset says **separate**, but Ousterhout's correction says
**separate at meaningful boundaries**, not at every syntactic
opportunity. A 3-line method extracted "for clarity" and never reused
is shallow modularization, not composition.

## When This Mindset Doesn't Apply

- **Performance-critical hot paths** — when cache locality, branch
  prediction, or vectorization dominate, the data layout has to
  drive the design even at the cost of conceptual cleanliness.
- **Framework code** — base classes, mixins, and inheritance
  hierarchies are sometimes the language's only mechanism for
  expressing a contract; fighting the framework is more cost than
  the cleaner design saves.
- **One-off scripts** — a 50-line script that runs once does not
  benefit from being decomposed into seven files.

## Cross-References

- `pragmatic-principles.md` — Orthogonality (the operational test
  for whether two pieces are composed or complected), DRY (about
  knowledge, not duplicate-looking code)
- `solid-principles.md` — SRP / DIP — the SOLID restatement of the
  same intuition at the OO-architecture level
- `refactoring-standard.md` — Divergent Change / Shotgun Surgery
  smells — the symptoms of complected design that this mindset
  prevents at design time
- `mindset-data-over-abstractions.md` — sister mindset; both push
  toward composing simple pieces over building specialized objects

## Anti-Patterns

- ❌ **Inheritance for code reuse** — base classes that exist to
  share methods, complecting subclass behavior with parent state
- ❌ **God object growth** — adding "just one more method" to a
  class that already has 30, because it "feels related"
- ❌ **Stateful service singletons** — global mutable state hidden
  behind `getInstance()`, complecting every caller with the
  service's lifecycle
- ❌ **Shallow extract-method spree** — pulling out 3-line methods
  with names that are longer than the body, in the name of
  "readability"
- ❌ **Framework-shaped code that cannot be tested without the
  framework** — the framework has complected itself into the
  domain logic
