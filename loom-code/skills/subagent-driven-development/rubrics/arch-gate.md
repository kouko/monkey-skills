<!--
FUNCTIONAL COPY — DO NOT EDIT IN PLACE
SSOT: domain-teams/skills/code-team/rubrics/arch-gate.md
Sync via: loom-code/scripts/distribute.py
-->

# Architecture Review Gate

## Primary Sources

- **Martin, R.C. (2000)** *Design Principles and Design Patterns*,
  objectmentor.com. **The original compilation of SRP / OCP / LSP
  / ISP / DIP** — the five principles later mnemonic-ordered as
  "SOLID" by Michael Feathers (~2004). objectmentor.com is
  defunct; canonical academic mirror:
  https://staff.cs.utu.fi/~jounsmed/doos_06/material/DesignPrinciplesAndPatterns.pdf.
- **Martin, R.C. (2017)** *Clean Architecture: A Craftsman's
  Guide to Software Structure and Design*, Prentice Hall.
  ISBN 978-0134494166. **Part III "Design Principles"** devotes
  one chapter to each SOLID principle and frames the "dependency
  rule" (source-code dependencies point inward, toward higher-
  level policy) that grounds the Boundary Design dimension below.
- **Fowler, M. (2018)** *Refactoring: Improving the Design of
  Existing Code*, 2nd edition, Addison-Wesley.
  ISBN 978-0134757599. **"Bad Smells in Code" chapter** (carried
  forward from 1st ed 1999 Ch.3) is the canonical catalog of
  architecture smells. The smells cited below — **Divergent
  Change**, **Shotgun Surgery**, **Large Class**, **Feature
  Envy**, **Speculative Generality** — are all from this chapter.
- Team standards: `standards/solid-principles.md` (SRP/OCP/LSP/
  ISP/DIP in code-team vocabulary) and
  `standards/refactoring-standard.md` (Bad Smells catalog with
  Fowler's 2018 framing) are the authoritative code-team
  references for this gate's dimensions.

> **Note on numeric thresholds.** The specific numbers in this
> rubric ("3x+ more complex", "5+ files across 3+ modules",
> "3+ distinct concerns") are **house heuristics** used as
> tie-breakers in ambiguous reviews. They are **not** Martin or
> Fowler primary-source rules. Treat them as useful triggers for
> further investigation, not as hard verdict criteria. The smell
> *name* (e.g. "Shotgun Surgery", "Large Class") is the primary
> source; the count is code-team shorthand.

## Scope Boundary

Review the _shape_ of the solution, not its implementation details.
Do NOT review code quality, bugs, or security — those belong to
quality-gate and the security checklist.

## Flag Definitions

### Approach Fitness
- 🔴 **Fatal**: Chosen approach is 3x+ more complex than an obviously simpler alternative that meets the same requirements (house heuristic; see "Note on numeric thresholds" above). Underlying principle: Fowler 2018 **"Speculative Generality"** smell + Fowler bliki "Yagni" (*"capability we presume our software needs in the future should not be built now"*).
- 🔴 **Fatal**: Solution solves a hypothetical future problem, not the actual current requirement. **Grounded in**: Fowler bliki "Yagni" (https://martinfowler.com/bliki/Yagni.html); see `standards/pragmatic-principles.md` §YAGNI.
- 🟡 **Warning**: Complexity is borderline justified — could go either way
- 🟢 **Clear**: Approach matches problem complexity; boring solution preferred (ETC-consistent per Pragmatic Programmer Ch.2 "The Essence of Good Design")

### Boundary Design
- 🔴 **Fatal**: Circular dependency between modules/services (DIP violation at system level; *Clean Architecture* 2017 "dependency rule")
- 🔴 **Fatal**: **God object / module** that absorbs responsibilities from 3+ distinct concerns (house count). **Grounded in**: Martin 2000 **SRP** — *"A class should have only one reason to change"* — and Fowler 2018 **"Large Class"** smell. See `standards/solid-principles.md` §SRP and `standards/refactoring-standard.md` §"Large Class".
- 🟡 **Warning**: Dependencies point in the wrong direction (high-level policy depending on low-level detail). **Grounded in**: Martin 2000 **DIP** — *"High-level modules should not depend on low-level modules. Both should depend on abstractions."* See `standards/solid-principles.md` §DIP.
- 🟡 **Warning**: **Over-abstraction** — abstraction layer exists but has only one implementation with no foreseeable second. **Grounded in**: Fowler bliki "Yagni" (XP discipline) and Fowler 2018 **"Speculative Generality"** smell. See `standards/pragmatic-principles.md` §YAGNI.
- 🟢 **Clear**: Boundaries are in the right places; coupling is appropriate (Pragmatic Programmer Ch.2 "Orthogonality" respected)

### Change Tolerance
- 🔴 **Fatal**: The most likely future change exhibits Fowler 2018 **"Shotgun Surgery"** — *"Every time you make a kind of change, you have to make a lot of little changes to a lot of different classes."* The code-team house shorthand for this is "5+ files across 3+ modules for one feature", but the primary-source signal is the smell itself: responsibility for a single concept is spread across too many modules. See `standards/refactoring-standard.md` §"Shotgun Surgery".
- 🟡 **Warning**: Module exhibits Fowler 2018 **"Divergent Change"** — *"one module is often changed in different ways for different reasons"* — indicating multiple actors pulling the module in different directions (SRP violation at the symptom level). See `standards/refactoring-standard.md` §"Divergent Change".
- 🟡 **Warning**: Extension points exist where the domain is stable (unnecessary flexibility — Speculative Generality smell + YAGNI)
- 🟢 **Clear**: Rigid where stable, flexible where it will evolve — ETC principle (Pragmatic Programmer Ch.2 "The Essence of Good Design")

### Ecosystem Fit
*This dimension is a **house heuristic** — it captures "fits the
project's existing architecture and team conventions" which is
not a principle from any specific primary source. Kept as a gate
dimension because convention fit is often the single strongest
predictor of whether a design is reviewable by teammates.*

- 🟡 **Warning**: Deviates from project conventions without documented rationale
- 🟡 **Warning**: Other developers would need explanation to understand the design intent
- 🟢 **Clear**: Fits existing architecture; conventions followed

## Verdict Rules

1. **NEEDS_REVISION**: Any 1 🔴 fatal flag
2. **NEEDS_REVISION**: 2 or more 🟡 warning flags
3. **PASS_WITH_NOTES**: Exactly 1 🟡 warning flag, no 🔴
4. **PASS**: All 🟢 clear

## Rules

- If the approach works and the cost of being wrong is low, PASS. Don't be a gatekeeper for the sake of gatekeeping.
- When issuing NEEDS_REVISION, you MUST include an "Alternatives Considered" section with at least one concrete alternative approach and its trade-offs.
- Evaluate against actual problem scope, not hypothetical larger scope.

## Output Format

1. **Flags**: List each triggered flag with `[🔴 Dimension]` or `[🟡 Dimension]`
2. **Evidence**: Specific structural problem with rationale
3. **Alternatives Considered** (NEEDS_REVISION only): Concrete alternatives with trade-offs
4. **Verdict**: PASS / PASS_WITH_NOTES / NEEDS_REVISION

PASS_WITH_NOTES issues will be auto-revised without human review.
Be specific about what to restructure and how.
