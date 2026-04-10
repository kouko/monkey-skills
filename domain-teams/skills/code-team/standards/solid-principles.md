# SOLID Principles

SRP / OCP / LSP / ISP / DIP — the five object-oriented design
principles that Robert C. Martin compiled in 2000 and that Michael
Feathers later named "SOLID". Load-bearing architectural principle
set for code-team when evaluating class-level and module-level
design.

## Primary Sources

- Martin, R.C. (2000) *Design Principles and Design Patterns*, objectmentor.com. **The original compilation** of SRP/OCP/LSP/ISP/DIP. The objectmentor.com site is defunct; the canonical mirror is the academic archive at https://staff.cs.utu.fi/~jounsmed/doos_06/material/DesignPrinciplesAndPatterns.pdf.
- Martin, R.C. (2017) *Clean Architecture: A Craftsman's Guide to Software Structure and Design*, Prentice Hall. ISBN 978-0134494166. Part III "Design Principles" devotes one chapter to each SOLID principle; specific chapter numbers within Part III are not independently verified from public TOC listings, so this standard cites as *Clean Architecture* Part III, chapter on {principle}.
- Martin, R.C. (2002) *Agile Software Development, Principles, Patterns, and Practices*, Prentice Hall. ISBN 978-0135974445 — earlier book-length systematization of the same principles.
- SOLID acronym attribution: **Michael Feathers** coined the mnemonic ordering (~2004), which Martin credits in subsequent writing. The acronym is Feathers's; the principles are Martin's compilation of prior work (e.g. Bertrand Meyer for OCP, Barbara Liskov for LSP).

## SRP — Single Responsibility Principle

**Martin 2000 §3 / *Clean Architecture* (2017) Part III, chapter on
SRP**:

> *"A class should have only one reason to change."*

The 2017 restatement in *Clean Architecture* sharpens "reason to
change" as *"A module should be responsible to one, and only one,
actor"* — where an *actor* is the person or group whose requirements
the module serves. Two requirements from two different actors in one
class is an SRP violation; merging them creates friction when actors
disagree.

SRP is the principle that catches the "god object" anti-pattern
before it metastasizes.

## OCP — Open/Closed Principle

**Martin 2000 §4 / *Clean Architecture* (2017) Part III, chapter on
OCP**:

> *"Software entities (classes, modules, functions) should be open
> for extension but closed for modification."*

Originally formulated by **Bertrand Meyer** (1988, *Object-Oriented
Software Construction*) in the context of inheritance; Martin
reframed OCP around **polymorphism and abstraction boundaries** —
you extend behavior by adding new classes that implement existing
interfaces, not by editing existing classes.

In practice: when adding a new feature requires editing (not adding
to) an existing module, ask whether the module is missing an
extension point. Not every edit violates OCP, but a pattern of
edits to the same class for each new variant is a signal.

## LSP — Liskov Substitution Principle

**Martin 2000 §5 / *Clean Architecture* (2017) Part III, chapter on
LSP**, citing **Barbara Liskov** (1987 keynote, "Data Abstraction
and Hierarchy"):

> *"Subtypes must be substitutable for their base types."*

If `S` is a subtype of `T`, then wherever code uses `T` it should
work correctly with `S` without knowing the difference. The
canonical LSP violation is the *Square-Rectangle problem*: `Square
extends Rectangle` breaks because code that calls `rect.setWidth(5);
rect.setHeight(10)` expects the two operations to be independent,
but a `Square` forces them to stay equal.

LSP violations are often disguised as "optimizations" or "special
cases" in overridden methods.

## ISP — Interface Segregation Principle

**Martin 2000 §6 / *Clean Architecture* (2017) Part III, chapter on
ISP**:

> *"Clients should not be forced to depend on interfaces they do not
> use."*

A "fat" interface that bundles unrelated methods forces every client
to couple to behaviors it doesn't care about. Split fat interfaces
into smaller role-based interfaces per client.

## DIP — Dependency Inversion Principle

**Martin 2000 §7 / *Clean Architecture* (2017) Part III, chapter on
DIP**:

> *"High-level modules should not depend on low-level modules. Both
> should depend on abstractions."*
>
> *"Abstractions should not depend on details. Details should depend
> on abstractions."*

DIP is the architectural backbone of *Clean Architecture* — the
"dependency rule" that source-code dependencies must point inward,
toward higher-level policy, is DIP restated at the system level.

DIP in practice means: define an interface owned by the consuming
module, and have the low-level implementation module depend on that
interface. This inverts the "natural" dependency direction where
high-level code imports low-level libraries.

## When SOLID Applies — and When It Over-Engineers

SOLID is a set of principles, not a checklist. Apply judgment:

- **Small scripts, one-off tools, prototypes** — SOLID is usually
  over-engineering. A 50-line data-cleaning script does not need DIP.
- **Long-lived production modules with multiple clients** — SOLID
  earns its complexity cost. SRP and OCP are especially valuable
  when multiple teams contribute to the same codebase.
- **Hot paths** — sometimes an OCP-respecting polymorphic dispatch
  has measurable overhead, and a switch statement is the right call.
  Document the trade-off (see `pragmatic-principles.md` Trade-off
  Dimensions).

Reasonable public pushback exists on dogmatic SOLID application
(e.g. Dan North's "CUPID" reframing, Fowler's nuanced bliki entries
on SRP). code-team treats SOLID as **load-bearing for class / module
design in large codebases** and as **optional guidance for small
scripts**.

## Cross-References

- `naming-and-functions.md` — SRP at the function level (Clean Code
  Ch.3 "Do One Thing") is a finer-grained restatement of the same
  principle.
- `refactoring-standard.md` — "Divergent Change" and "Shotgun
  Surgery" smells (Fowler 2018) are the symptoms of SRP violations.
- `pragmatic-principles.md` — Orthogonality is the module-level
  principle that motivates SRP.

## Anti-Patterns

- ❌ **God object** — one class that knows about everything, reached
  by every other module (SRP violation, then DIP violation)
- ❌ **Concrete dependencies** — high-level policy modules importing
  concrete infrastructure classes (DIP violation)
- ❌ **LSP violation disguised as override** — a subclass that
  throws `NotSupportedException` on a method inherited from the
  base type
- ❌ **Fat interface** — a service interface with 30 methods where
  most clients use 2 (ISP violation)
- ❌ **Edit-to-extend** — every new variant of a feature requires
  adding a branch to the same switch/if-chain (OCP violation)
- ❌ **SOLID cargo-culting** — applying all five principles to a
  50-line script "because SOLID"
