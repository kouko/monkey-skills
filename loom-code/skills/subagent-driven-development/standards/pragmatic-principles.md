<!--
FUNCTIONAL COPY — DO NOT EDIT IN PLACE
SSOT: domain-teams/skills/code-team/standards/pragmatic-principles.md
Sync via: loom-code/scripts/distribute.py
-->

# Pragmatic Principles

Principle-level craft grounding for code-team — DRY, ETC,
Orthogonality, Tracer Bullets, YAGNI, Rule of Three, KISS. These are
the "pragmatic" heuristics that sit above language specifics and
below architectural patterns. 設計の原則であって、特定の言語や
framework には依存しない。

## Primary Sources

- Hunt, A. & Thomas, D. (2019) *The Pragmatic Programmer: Your Journey to Mastery, 20th Anniversary Edition*, Addison-Wesley. ISBN 978-0135957059. 10 chapters, 53 topics, 100 tips. Chapter-and-title citations follow the research-verified format — Ch.2 Topic numbers (8–15) are independently verified; other chapters cite by title only.
- Fowler, M. — bliki entry "Yagni": https://martinfowler.com/bliki/Yagni.html (authoritative Fowler bliki, counts as primary per `grounding-principle.md`).
- Fowler, M. (2018) *Refactoring: Improving the Design of Existing Code*, 2nd edition, Addison-Wesley. ISBN 978-0134757599 — for the Rule of Three attribution to Don Roberts (discussed in the "When Should You Refactor?" section of Ch.2 Principles).

> Citation honesty note: Pragmatic Programmer 20th anniv. publicly
> enumerates only Ch.2 Topic numbers (Topics 8–15). For other chapters,
> this standard cites as `Ch.N, Topic "{title}"` without fabricating a
> number, per `standards/grounding-principle.md` anti-pattern "citation
> laundering".

## DRY — Don't Repeat Yourself

**Pragmatic Programmer Ch.2, Topic 9 "DRY — The Evils of Duplication"**:

> *"Every piece of knowledge must have a single, unambiguous,
> authoritative representation within a system."*

DRY is **not** "do not copy-paste lines of code" — it is about
knowledge. Two code fragments that happen to look similar today but
represent different business rules are **not** a DRY violation; they
are *coincidental similarity*. Pursuing coincidental deduplication is
an anti-pattern (see "Over-abstraction" below).

## Orthogonality

**Pragmatic Programmer Ch.2, Topic 10 "Orthogonality"**:

Two components are orthogonal if changes to one do not require
changes to the other. Orthogonal systems are easier to test, refactor,
and reuse. The practical test: *"If I change X, how many other
modules do I need to touch?"* A low number means orthogonal; a high
number means coupled.

Orthogonality is the principle that **justifies** SRP (see
`solid-principles.md`) at the module level.

## ETC — Easier to Change

**Pragmatic Programmer Ch.2, Topic 8 "The Essence of Good Design
(ETC)"**:

> *"Good design is easier to change than bad design."*

ETC is Hunt & Thomas's "meta-principle" — the reason we care about
DRY, Orthogonality, SOLID, and every other design guideline is that
they make future change cheaper. When two guidelines conflict, prefer
the one that leaves the code easier to change.

## Tracer Bullets

**Pragmatic Programmer Ch.2, Topic 12 "Tracer Bullets"**: build a
minimal end-to-end working version of the system early, then iterate.
Tracer bullets are distinct from prototypes — they are **production
code** that happens to be incomplete, not disposable experiments.

Use tracer bullets when the architecture is uncertain; use prototypes
(Topic 13) when a specific design question needs a quick answer that
will be thrown away.

## YAGNI — You Ain't Gonna Need It

**Fowler, bliki "Yagni"** (https://martinfowler.com/bliki/Yagni.html):

> *"Yagni originally is an acronym that stands for 'You Aren't Gonna
> Need It'. It is a mantra from Extreme Programming that's often
> used generally in agile software teams. It's a statement that some
> capability we presume our software needs in the future should not
> be built now because 'you aren't gonna need it'."*

Fowler's bliki adds a critical nuance: YAGNI does not forbid thinking
ahead. It forbids *building* speculative capability. Design for
change (ETC), but implement for today.

## Rule of Three

**Fowler 2018, Ch.2 "Principles in Refactoring", §"When Should You
Refactor?"** attributes the Rule of Three to **Don Roberts**:

> *"The first time you do something, you just do it. The second time
> you do something similar, you wince at the duplication, but you do
> the duplicate thing anyway. The third time you do something
> similar, you refactor."*

The Rule of Three is the **tension resolver** between DRY ("deduplicate
knowledge") and YAGNI ("don't build abstractions you don't need").
Wait for three concrete examples before extracting a shared abstraction;
with fewer, you don't yet know the right abstraction shape.

## KISS — Keep It Simple, Stupid

KISS is a long-standing software folk principle (Kelly Johnson,
Lockheed Skunk Works, 1960s) but it appears as a load-bearing
heuristic in Pragmatic Programmer's overall stance: prefer the
simpler solution unless a more complex one is demonstrably justified.
Pragmatic Programmer does not devote a dedicated Topic to KISS, so
code-team treats KISS as a **folk principle** rather than a
citation-grounded rule — it is shorthand for "ETC + YAGNI applied to
a single design decision".

## Prefer the Standard Library

**Pragmatic Programmer Ch.7 "While You Are Coding"** (Topic numbers
in Ch.7 not independently verified — citing by chapter and theme
only): the discussion of *Programming by Coincidence* and *Refactoring*
argues strongly for using well-tested library code over custom
re-implementations. Every line of custom code is a line you must
maintain forever.

code-team heuristic: **prefer stdlib / well-maintained library over
custom** unless (a) the library is abandoned, (b) the license is
incompatible, or (c) benchmarking shows a blocking performance gap.

## Trade-off Dimensions

When a design decision involves trade-offs, make the trade-offs
explicit. A non-exhaustive dimension list (house convention distilled
from Pragmatic Programmer's recurring theme of "context matters"):

- **Correctness** — does it produce the right answer?
- **Performance** — latency, throughput, memory
- **Maintainability / ETC** — how hard is this to change in 6 months?
- **Testability** — can we write a fast, isolated test?
- **Security** — does this create attack surface? (see `app-security-standard.md`)
- **Operational complexity** — deployment, observability, dependencies

Pragmatic Programmer does not fix a number of dimensions; this list
is a house convention suitable for code-review discussion.

## Anti-Patterns

- ❌ **Deduplicating coincidental similarity** — violating Rule of Three
  by abstracting on the second occurrence, creating a leaky abstraction
- ❌ **Speculative generality** — building config options, plugin
  points, or abstract base classes for features that may never exist
  (YAGNI violation)
- ❌ **Over-orthogonality** — slicing a system into so many "independent"
  modules that every user-visible change requires touching 10 files
- ❌ **Citation laundering "KISS"** — invoking KISS to justify a
  design without saying *what* specific complexity is being avoided
- ❌ **Re-implementing stdlib** — writing a custom JSON parser, date
  arithmetic library, or string formatter when the standard library
  provides one
- ❌ **Hiding trade-offs** — declaring a solution "best" without
  enumerating the dimensions it lost on
