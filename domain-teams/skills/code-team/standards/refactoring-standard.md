# Refactoring Standard

Refactoring is **behavior-preserving change to internal structure**.
code-team's refactoring discipline is grounded in Fowler's canonical
definition, Feathers's legacy-code techniques, and the Bad Smells
catalog that both books share.

## Primary Sources

- **Fowler, M. (2018) *Refactoring: Improving the Design of Existing Code*, 2nd edition, Addison-Wesley. ISBN 978-0134757599.** The canonical primary source on refactoring. The 2nd edition uses JavaScript examples, contains 68 refactorings, and introduces refactoring techniques for non-class-centric code. Cited sections: Ch.1 opening walkthrough, Ch.2 "Principles in Refactoring" (including Rule of Three attribution and Two Hats discussion), and the "Bad Smells in Code" chapter. Note: 2nd ed chapter numbers for Bad Smells are not independently verified from public TOC listings — in the 1st ed (1999) this was Ch.3; the content carries forward to the 2nd ed but the chapter number in 2nd ed is not listed on martinfowler.com/books/refactoring.html. This standard cites as "Fowler 2018, 'Bad Smells in Code' chapter (carried forward from 1999 1st ed Ch.3)".
- **Feathers, M. (2004) *Working Effectively with Legacy Code*, Prentice Hall (Robert C. Martin Series). ISBN 978-0131177055.** The canonical primary source for refactoring in the absence of tests. Cited sections: Preface ("legacy code = code without tests"), Ch.4 "The Seam Model", Ch.13 "Characterization Tests", Ch.25 "Dependency-Breaking Techniques" (24 specific techniques).
- Martin, R.C. (2008) *Clean Code*, Prentice Hall. ISBN 978-0132350884. Ch.17 "Smells and Heuristics" — a catalog of ~66 code smells, largely overlapping with Fowler's but with Martin's framing. Supplementary to Fowler.
- Don Roberts — the Rule of Three is attributed to Roberts (a refactoring researcher) and cited by Fowler in both editions; Don Roberts is not himself the author of a public primary, so the attribution flows through Fowler 2018 Ch.2.

## Definition of Refactoring

**Fowler 2018, Ch.1 opening**:

> *"Refactoring is a disciplined technique for restructuring an
> existing body of code, altering its internal structure without
> changing its external behavior."*

Three things follow immediately from this definition:

1. **Behavior preservation is the load-bearing constraint.** If a
   change alters observable behavior, it is a bug fix or a feature
   change, not a refactor — even if it "cleans up" the code.
2. **A test suite is the safety net.** Without tests, you cannot
   verify behavior preservation. See Feathers 2004 below for the
   legacy-code case where tests do not yet exist.
3. **Refactoring is discrete.** Each refactor is a small,
   reversible step (rename, extract, inline, move) with tests
   running green before and after.

## Two Hats Principle

**Fowler 2018, Ch.2 "Principles in Refactoring"** discusses the Two
Hats principle (carried forward from 1st ed 1999; independent
verification of 2nd ed section numbering is not available, so this
standard cites the principle by name rather than by section):

When working on code, you wear exactly one of two hats at a time:

- **Feature hat** — you are adding new behavior. You do NOT refactor.
  You add new tests and new code to pass them.
- **Refactor hat** — you are improving existing structure. You do
  NOT add features. Tests stay green from start to finish.

Mixing the two creates a change that is neither reviewable as a
feature nor reversible as a refactor. Swap hats explicitly, and
commit between hat switches.

## Rule of Three

**Fowler 2018, Ch.2 "Principles in Refactoring", §"When Should You
Refactor?"** attributes the rule to **Don Roberts**:

> *"The first time you do something, you just do it. The second
> time you do something similar, you wince at the duplication, but
> you do the duplicate thing anyway. The third time you do something
> similar, you refactor."*

The Rule of Three is why duplication thresholds in code review are
usually set at 3+ occurrences. With two occurrences, you don't yet
know the right shape of the abstraction; extracting prematurely
creates a leaky abstraction you will regret (see also
`pragmatic-principles.md`).

## Bad Smells in Code

**Fowler 2018, "Bad Smells in Code" chapter** (carried forward from
Fowler 1999 1st ed Ch.3); complemented by **Clean Code Ch.17 "Smells
and Heuristics"**. The smells most relevant to code-team reviews:

### Duplicated Code

**Fowler 2018 / Clean Code Ch.17 §G5**: the "number one in the
stink parade". The same (or near-same) code appearing in multiple
places is a knowledge-DRY violation. Typical refactors: *Extract
Function*, *Extract Class*, *Pull Up Method*.

### Long Method / Long Function

**Fowler 2018**: methods that do too much. Typical refactors:
*Extract Function*, *Replace Temp with Query*, *Decompose
Conditional*. See also `naming-and-functions.md` for code-team's
20-line soft target / 50-line hard ceiling.

### Large Class

**Fowler 2018 / Clean Code Ch.10**: a class that has too many
responsibilities (SRP violation — see `solid-principles.md`).
Typical refactor: *Extract Class*.

### Divergent Change

**Fowler 2018**: *"Divergent change occurs when one module is often
changed in different ways for different reasons."* This is the
direct symptom of SRP violation: the module has multiple actors
(Martin *Clean Architecture* 2017) pulling it in different
directions.

### Shotgun Surgery

**Fowler 2018**: *"Every time you make a kind of change, you have
to make a lot of little changes to a lot of different classes."*
The opposite of Divergent Change: responsibility for a single
concept is spread across too many modules. Typical refactors:
*Move Method*, *Move Field*, *Inline Class*.

This is the smell code-team uses to flag changes that touch "5+
files across 3+ modules for one feature" — the threshold is a
house heuristic, but the smell it points at is Fowler's.

### Feature Envy

**Fowler 2018 / Clean Code Ch.17 §G14**: a method that seems more
interested in another class's data than its own. Typical refactor:
*Move Method* into the class it envies.

## Legacy Code: Refactoring Without Tests

**Feathers 2004, Preface**, canonical definition:

> *"Legacy code is code without tests."*

Feathers reframes "legacy" from "old code" to "code we cannot
safely change". A 6-month-old untested codebase is legacy; a
6-year-old well-tested codebase is not. This shifts the
conversation from "when will we rewrite this" to "how do we make
it testable".

### The Seam Model

**Feathers 2004, Ch.4 "The Seam Model"**:

> *"A seam is a place where you can alter behavior in your program
> without editing in that place."*

Seams exist wherever you can substitute one implementation for
another — at polymorphism points (object seams), at link time (link
seams), at preprocessor level (preprocessing seams). Finding seams
is the first step in making legacy code testable.

### Characterization Tests

**Feathers 2004, Ch.13 "Characterization Tests"**: when you don't
know what legacy code is *supposed* to do, write tests that capture
what it *currently does*. These tests lock in current behavior so
that subsequent refactors can proceed safely, even if the current
behavior contains bugs — you deal with those once the suite is
green.

### Dependency-Breaking Techniques

**Feathers 2004, Ch.25 "Dependency-Breaking Techniques"**: 24
specific, named techniques for replacing hard dependencies with
seams. Examples: *Extract Interface*, *Subclass and Override
Method*, *Parameterize Constructor*, *Replace Global Reference
with Getter*. These are the micro-moves that turn "I can't test
this" into "I have a seam I can exploit".

## When to Refactor

**Fowler 2018 Ch.2**: the answer is *"opportunistically"*, not *"as
a scheduled task"*. Refactor when:

- You're about to add a feature and the current code makes it hard
  (Preparatory Refactoring)
- You don't understand the code and refactoring helps you read it
  (Comprehension Refactoring)
- You see duplicated code for the third time (Rule of Three)

Avoid "refactoring sprints" as a standalone activity — they are
hard to review, hard to justify to stakeholders, and typically
change more than necessary.

## Cross-References

- `naming-and-functions.md` — function-size thresholds, naming
  fixes that often eliminate the need for a refactor
- `solid-principles.md` — SRP/OCP violations that Divergent Change
  and Shotgun Surgery are symptoms of
- `tdd-standard.md` — the Refactor step of Red/Green/Refactor

## Anti-Patterns

- ❌ **Refactoring without tests** on a critical path (Feathers
  2004 says: write characterization tests first)
- ❌ **Refactoring + feature addition in one commit** (Two Hats
  violation — impossible to review)
- ❌ **Rewriting instead of refactoring** — deleting and retyping
  a module is not refactoring; you've lost the behavior-preservation
  guarantee
- ❌ **Deduplicating on 2nd occurrence** — violates Rule of Three
- ❌ **Big-bang refactor** — one commit that touches 50 files and
  is impossible to review or bisect
- ❌ **Refactoring to a pattern the team doesn't know** — introduces
  cognitive load that the "cleaner" structure doesn't repay
