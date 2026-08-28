---
name: an-extracted-helper-inherits-none-of-its-call-sites-tests
description: Extracting duplicated logic into a shared helper moves the code but not the coverage — every call site can pass while a branch none of them takes is unprotected, and when the extraction lands as two copies (separate import roots, independent package hashing) the untested twin can be reverted to the exact defect the extraction removed with its whole suite still green
type: gotcha
origin: pin-granularity arc (2026-08-28) — a review arm mutated `heading_window.line_leading` and found survivors across all 44 call sites; a later arm found five more surviving in the untested second copy, including reverting the helper to the bare substring search the branch existed to eliminate
---

Twelve hand-rolled copies of a line-leading heading anchor were consolidated
into one `line_leading(text, heading, start=0)` per import root. Every
consumer suite stayed green. A reviewer then mutated the helper and found
two mutants alive against **all 44 call sites**: `max(0, start - 1)` → `start`,
and dropping the `start == 0` guard.

Neither is exotic. They are the two offset decisions that separate this
helper from a naive one. They survived because **no consumer reaches them**:
every call passes `start=0`, on documents whose headings never sit at offset
0. The branches are unreachable from the consumer side by construction, so
consumer coverage says nothing about them, however many consumers there are.

**The twin makes it worse.** The extraction produced two copies — the plugin
trees are hashed independently as cold-install packages and must not import
across each other, so one helper per import root is correct. Tests were
written beside one copy. Against the other, five mutants survived its full
237-test suite, including `find("\n" + heading)` → `find(heading)` — reverting
to the bare substring search the entire branch existed to remove, invisibly.

**Why nothing warns you.** The green suite is not lying: those call sites do
pass. Deletion-first and Rule-of-Three audits both approve the extraction.
Mutation testing scoped to the consumers reports the helper as covered,
because it is — everywhere the consumers go.

**How to apply.**

1. An extracted helper gets its own test file, at extraction time, in the
   same commit. Not "when it grows"; the gap exists the moment the code
   moves.
2. Write those tests from the helper's CONTRACT, not from what the callers
   happen to do. The clauses worth pinning are exactly the ones no caller
   exercises — boundary values, the sentinel, the argument only one site
   passes. If a test could equally have lived in a consumer suite, it is not
   the test this file needed.
3. Name the mutant each test kills, in the test's own docstring, and prove
   it: mutate, watch it fail, restore. A test asserting a branch nobody
   reaches is otherwise indistinguishable from decoration.
4. **When the extraction lands as N copies, it lands as N coverage gaps.**
   Copy the tests beside every copy. Duplication that is correct for
   package-boundary reasons still duplicates every future repair, and this
   arc had three fixes land on one twin while the other kept the defect.

Related: [[a-mutation-test-must-run-the-production-assertion]] (a
mutation-proof suite going green because the wiring, not the logic, was what
changed); [[unifying-a-normalization-has-a-scope]] (an extraction claiming
broader applicability than it earned); [[per-task-review-misses-duplicated-fallback-fix]]
(a fix landing at one site while its siblings keep the defect — the same
shape one layer up, and the reason the twin was missed three times here).
