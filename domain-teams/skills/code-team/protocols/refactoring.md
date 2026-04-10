# Refactoring Rubric

## Primary Sources

- **Fowler, M. (2018)** *Refactoring: Improving the Design of
  Existing Code*, 2nd edition, Addison-Wesley.
  ISBN 978-0134757599. **The canonical primary source on
  refactoring.** Chapters grounding this protocol:
  - Ch.1 opening definition: *"Refactoring is a disciplined
    technique for restructuring an existing body of code,
    altering its internal structure without changing its
    external behavior."* — this is the basis of the "NEVER
    change behavior" rule below.
  - Ch.2 "Principles in Refactoring" — the **Two Hats**
    principle (wear exactly one hat at a time: feature-hat or
    refactor-hat, never both) and **Rule of Three** (attributed
    by Fowler to **Don Roberts**: refactor on the third
    occurrence of a duplication, not the second).
- **Feathers, M. (2004)** *Working Effectively with Legacy Code*,
  Prentice Hall (Robert C. Martin Series). ISBN 978-0131177055.
  **Canonical source for refactoring without tests.** Chapters
  grounding this protocol: Ch.4 "The Seam Model" (finding the
  places where behavior can be altered without editing in place)
  and Ch.25 "Dependency-Breaking Techniques" (24 named micro-
  moves that turn untestable code into testable code). Feathers's
  Preface definition — *"Legacy code is code without tests"* —
  is the lens through which this protocol treats legacy refactors.
- Martin, R.C. (2008) *Clean Code*, Prentice Hall.
  ISBN 978-0132350884. Ch.17 "Smells and Heuristics" —
  supplementary catalog of ~66 code smells, largely overlapping
  with Fowler's Bad Smells chapter but with Martin's framing.
- Team standard: `standards/refactoring-standard.md` is the
  authoritative code-team reference for refactoring discipline,
  including smell taxonomy and legacy-code techniques.

## Protocol

1. **Receive instruction**: Get explicit refactoring task
   (what to change, not why)
2. **Analyze scope**: Which files, which symbols, what references
3. **Execute transformation**: Make the changes
4. **Verify**: Run existing tests, check for broken references
5. **Report**: List all files changed, what was done

## Rules

- **NEVER change behavior** — refactoring is structure-only
  (Fowler 2018 Ch.1 opening definition: *"altering its internal
  structure without changing its external behavior"*)
- **NEVER make additional "while I'm here" changes** — Two Hats
  principle (Fowler 2018 Ch.2): wear exactly one hat at a time.
  Mixing a refactor and a feature in one change creates something
  that is neither reviewable as a feature nor reversible as a
  refactor. Swap hats explicitly and commit between swaps.
- If a transformation would require a design decision, STOP and
  report what decision is needed
- Always verify tests still pass after refactoring. If the code
  has no tests, this is a Feathers 2004 scenario — write
  characterization tests (Feathers Ch.13) first, or decline the
  refactor on critical-path code.
- Preserve all existing formatting conventions

## Output Format

1. List of files modified
2. Transformation applied (what changed structurally)
3. Test results (pass/fail)
4. Broken references found (if any)
