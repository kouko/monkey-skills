---
name: a-subset-check-needs-a-refusal-test-because-an-empty-listing-passes-vacuously
description: When a guard is "every listed item must be in the declared set", a GREEN test that only shows a conforming input sealing proves nothing — an EMPTY listing from a broken producer is a subset of anything; pin every subset/allow-list check with a RED test whose input contains one item that must be refused, on every producer branch (here the root-commit branch of `git diff-tree` listed zero paths without `--root`, and the seal-only test stayed green through two review layers)
type: gotcha
origin: batch-review-hardening (2026-08-31) — Task 3's declared-files check had a root-commit fallback whose `git diff-tree` call lacked `--root`; the fallback returned an empty list, the "root commit member seals" test passed vacuously, per-task triad and batch aggregate review both accepted it, and an implementer fixing an unrelated quoting bug noticed the empty listing
---

The shape is general: `changed ⊆ declared` is trivially true when `changed`
is empty, and a producer that silently returns nothing — a git flag missing,
a glob that matches no file, a parser that swallows its input — makes the
guard look like it works. A test that feeds a conforming input and asserts
"sealed" cannot tell "nothing undeclared" from "nothing listed".

Recognise it by: an allow-list or subset guard whose only test asserts the
happy path, or whose refusal test exercises just one of the producer's
branches (non-root commits but not root commits; files but not directories).

Correct path: for each producer branch, one RED test whose listing contains
exactly one forbidden item and asserts refusal naming that item. If the
producer has a fallback, the fallback gets its own refusal test — that is
where the empty listing hides. When reviewing such a guard, ask for the
refusal test before reading the seal test; the seal test is the one that
lies.
