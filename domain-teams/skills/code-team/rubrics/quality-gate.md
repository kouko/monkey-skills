# Code Quality Review Gate

## Primary Sources

- **Martin, R.C. (2008)** *Clean Code: A Handbook of Agile
  Software Craftsmanship*, Prentice Hall. ISBN 978-0132350884.
  Chapters grounding this gate: **Ch.2 Meaningful Names**,
  **Ch.3 Functions** (including the "Small!" rule —
  *"functions should rarely exceed 20 lines"*), and **Ch.9 Unit
  Tests** (F.I.R.S.T properties).
- **Fowler, M. (2018)** *Refactoring: Improving the Design of
  Existing Code*, 2nd edition, Addison-Wesley.
  ISBN 978-0134757599. **"Bad Smells in Code" chapter** (carried
  forward from 1st ed 1999 Ch.3) grounds the **Duplicated Code**
  and **Long Method** flags below. Ch.2 "Principles in
  Refactoring" attributes the **Rule of Three** to Don Roberts.
- **Beck, K. (2002)** *Test-Driven Development: By Example*,
  Addison-Wesley. ISBN 978-0321146533. Preface rule and the
  "tests as design feedback" framing grounding the Tests
  dimension below.
- **Feathers, M. (2004)** *Working Effectively with Legacy Code*,
  Prentice Hall. ISBN 978-0131177055. Ch.13 "Characterization
  Tests" — the primary-source framing for "critical-path
  coverage on legacy or untested code".
- Team standards: `standards/naming-and-functions.md` (Clean
  Code Ch.2 + Ch.3, plus code-team's 20-line soft target /
  50-line hard ceiling house relaxation),
  `standards/tdd-standard.md` (F.I.R.S.T + Beck discipline +
  critical-path rule), and `standards/refactoring-standard.md`
  (Fowler's smell catalog) are the authoritative code-team
  references for this gate's dimensions.

> Note on ISO/IEC 25010: earlier drafts of this gate referenced
> ISO/IEC 25010 (software product quality model). 25010 was
> **demoted to auxiliary** during the Phase 2 grounding research
> due to paywall access and granularity mismatch with line-level
> code review — it is not cited here. The named principles
> (Clean Code chapters, Fowler smells, Beck discipline) carry
> the load instead.

## Prerequisites

This gate runs AFTER the security checklist passes. Do not re-evaluate
security concerns already covered by `checklists/security-checklist.md`.

## Flag Definitions

### Correctness & Logic
- 🔴 **Fatal**: Obvious logic error, infinite loop risk, or unguarded null/undefined reference
- 🔴 **Fatal**: Race condition in concurrent code without synchronization (generic CS concurrency concern; no specific primary-source citation — but see `standards/tdd-standard.md` Anti-Patterns §"Sleep-based tests" for the related TDD smell)
- 🟡 **Warning**: Missing defensive programming for likely edge cases
- 🟡 **Warning**: Error handling catches too broadly (bare `catch` swallowing all errors)
- 🟢 **Clear**: Normal and exception paths are properly handled. **Framing**: Beck 2002 Preface + Feathers 2004 — if the code is hard to exercise through tests, that is itself a correctness signal (*"if it's hard to test, it's probably hard to use"*), pointing back to design.

### API & Breaking Changes
*This dimension is a **house convention** for protecting
downstream consumers. It has no direct primary-source grounding
in the Clean Code / Fowler / Beck canon — breaking-change policy
is an ecosystem concern (semver, deprecation windows) rather than
a code-craft principle. Kept as a gate dimension because API
contract violations are among the most costly quality failures.*

- 🔴 **Fatal**: Public API contract broken without version bump or migration path
- 🔴 **Fatal**: Database migration would cause data loss on existing records
- 🟡 **Warning**: Undocumented behavioral change in a public interface
- 🟢 **Clear**: API contracts preserved or properly versioned

### Design
- 🟡 **Warning**: Single function exceeds **100 lines** (code-team hard warning ceiling). **Grounded in**: Clean Code Ch.3 "Small!" — Martin's rule is *"functions should rarely exceed 20 lines"* and should "hardly ever" be 100+. code-team's 100-line threshold is a **hard warning ceiling, not the ideal**; Clean Code Ch.3 argues for a ~20-line soft target. See `standards/naming-and-functions.md` §"Small functions" for the code-team 20-line soft / 50-line hard / 100-line gate-warning tiering.
- 🟡 **Warning**: Variable names lack semantic meaning (e.g., `let a = 1`, `temp`, `data`). **Grounded in**: Clean Code Ch.2 "Use Intention-Revealing Names" and "Avoid Disinformation". See `standards/naming-and-functions.md` §"Semantic meaning over brevity".
- 🟡 **Warning**: Copy-paste duplication across **3+ locations**. **Grounded in**: Fowler 2018 **"Duplicated Code"** smell (*"the number one in the stink parade"*) + Fowler 2018 Ch.2 **Rule of Three** attribution to **Don Roberts** (*"the third time you do something similar, you refactor"*). The "3+" threshold is the Rule of Three, not a code-team invention. See `standards/refactoring-standard.md` §"Duplicated Code".
- 🟢 **Clear**: Code is clear, SOLID principles respected where appropriate. **Grounded in**: Martin 2000 SOLID compilation; see `standards/solid-principles.md` for the 5 principles and for the explicit judgment calls on when SOLID over-engineers (small scripts, hot paths).

### Tests
- 🟡 **Warning**: Critical path (money, auth, data mutation) lacks test coverage. **Grounded in**: Clean Code Ch.9 **F.I.R.S.T** (Fast, Independent, Repeatable, Self-Validating, Timely) — the acceptance criteria for good unit tests — plus Beck 2002 Preface discipline + Feathers 2004 Ch.13 **"Characterization Tests"** (the primary-source framing for "critical-path coverage on legacy or untested code"). See `standards/tdd-standard.md` §"Critical-Path Coverage".
- 🟢 **Clear**: Test coverage exists for high-risk paths (F.I.R.S.T respected, critical-path rule from `standards/tdd-standard.md` satisfied)

## Verdict Rules

1. **NEEDS_REVISION**: Any 1 🔴 fatal flag
2. **NEEDS_REVISION**: 2 or more 🟡 warning flags
3. **PASS_WITH_NOTES**: Exactly 1 🟡 warning flag, no 🔴
4. **PASS**: All 🟢 clear

## Rules

- Read the full file before flagging (don't review snippets in isolation)
- Suggest fixes, don't just point out problems
- If the code works and is clear, say "LGTM" — don't invent issues
- Max 5 flags per review (prioritize by impact)
- Reference `standards/code-conventions.md` for objective style rules

## Output Format

1. **Flags**: List each triggered flag with `[🔴 Dimension]` or `[🟡 Dimension]`
2. **Evidence**: File path + line number + specific problem
3. **Fix Instruction**: How the worker should resolve this flag
4. **Verdict**: PASS / PASS_WITH_NOTES / NEEDS_REVISION

PASS_WITH_NOTES issues will be auto-fixed without human review.
Include exact file paths and line numbers.
