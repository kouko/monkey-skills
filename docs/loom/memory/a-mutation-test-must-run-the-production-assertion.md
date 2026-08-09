---
name: a-mutation-test-must-run-the-production-assertion
description: A test written to prove a pin is not vacuous must mutate the INPUT and invoke the PRODUCTION assertion — never re-implement the assertion beside it against a helper, because then reverting the production call site leaves the whole "mutation-proof" suite green and the guard can be deleted silently; the recursive form of the vacuity it was written to kill
type: practice
origin: branch fix/design-md-spec-conformance (2026-08-10) — whole-branch review found two schema pins that could not fail; the remediation added eleven mutation tests to prove they now could; a delta reviewer reverted both production call sites with the document pristine and got 16/16 green
---

The arc's headline defect was two assertions that could not fail: a
`for group in TOKEN_GROUPS: assert group in normalized` grepping the whole
file, and a `token not in section` substring check over a section that also
contained the illustrative YAML. Deleting the very content each guarded left
the suite green.

The remediation rescoped both to structures (`_section`, `_bullet_line`) and
added eleven mutation tests to prove the vacuity was gone. Every mutation
test called the **helper** — `_assert_all_token_groups_named(mutated_text)` —
and asserted it raised.

**That proves the helper works. It does not prove anything still calls it.**
A delta reviewer reverted both production call sites to their original
defective forms, left the document untouched, and ran the suite: **16 passed**.
The eleven tests written to prove the guard could no longer be vacuous were
themselves unable to fail when the guard was removed.

**Why:** a mutation test's subject is not the predicate, it is the *pipeline*
— input → production assertion → verdict. Testing the predicate in isolation
tests the half that was never in doubt. The half that fails in practice is the
wiring: an implementer refactoring the production test, or a later editor
"simplifying" it, silently detaches the guard, and the mutation suite applauds.
This is the same vacuity one level up, which is why it is easy to ship while
feeling rigorous.

**How to apply.** A mutation test must (1) mutate the **input** the production
assertion reads — monkeypatch the module-level text/path accessor, or point
the production function at a fixture copy — and (2) invoke the **production
test function itself**, asserting it raises. Never construct the mutated input
and hand it to a helper. Cheapest check on an existing mutation suite: revert
the production call site to whatever it was before the fix, leave the fixture
pristine, and run. If it stays green, the mutation suite is decorative.

The fix on this arc did exactly that and the same probe then produced
**7 failures**, which is the signal the suite is wired to the thing it claims
to guard.

Related: [[assertion-must-encode-the-property-it-claims]] (the first-order
form — a predicate unrelated to the claimed property; this entry is its
recursive form, where the *proof* of non-vacuity is itself vacuous),
[[reviewers-rerun-mutations-before-accepting-fix]] (the reviewer-side duty
that catches this — and did, here), [[a-mechanical-check-can-go-green-by-skipping]].
