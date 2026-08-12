---
name: a-read-window-below-the-declaration-line-invents-the-name
description: Reading a file through a line-range window that starts BELOW the declaration line shows you the body and hides the identifier, and the identifier then gets written from memory of what the body meant — producing a confidently-wrong symbol name surrounded by facts that all check out, which is precisely what makes it survive review; when a citation names a symbol, the read that sourced it must have included the line that declares it
type: gotcha
origin: brief-item-addressability plan, round-2 review (2026-08-13) — a plan GREEN clause named a pytest function that does not exist; the sourcing read was `sed -n '95,120p'` against a file whose `def` sat at line 94
---

A plan task's GREEN clause asserted that an existing pin
`test_prose_referent_only_zero_coverage_exit_1` must keep passing. No test by
that name exists anywhere in the repo. The real one is
`test_malformed_plan_prose_only_zero_coverage_exit_1`.

The sourcing read was `sed -n '95,120p' <file>` — a window opening exactly one
line below the `def` at line 94. It showed the docstring and every assertion
and hid the only line carrying the name. The name was then written from what
the docstring *meant* ("a plan whose Brief item covered fields are all prose
referents… treat as zero coverage") — which is a fair description of the test
and a wrong identifier for it.

**Why it survives review:** everything adjacent to the invented name was
correct and had genuinely been read — the exit code, both stderr assertions
(`Empty result set`, `Single match`), and the sibling pin's name, which
happened to sit inside the window. A reviewer sampling the claim finds fact
after fact confirming, and the one token that does not resolve is the one
token nobody re-derives. The round-2 reviewer caught it only by grepping for
the name itself and getting zero hits.

**Why the window is the cause, not carelessness:** `sed -n 'N,Mp'`, `Read` with
`offset`, and `grep -A` all select by position relative to something you
already found. When what you found is a *docstring* or a *body line*, the
declaration is above your anchor, not below it — so the efficient window
systematically excludes exactly the token a citation needs.

**How to apply:** when a citation will name a symbol — a test function, a
class, a flag constant, a fixture — the read that sources it must include the
declaring line. Two cheap forms: grep the declaration directly
(`grep -n "^def test_" <file>`) rather than reading a range around the body,
or start the window some lines ABOVE the anchor you matched. And treat a
symbol name in a plan or review finding as the one claim to verify by
re-grepping, not by re-reading the passage that surrounds it — the surround is
what makes it look verified.

**Contradiction check:** distinct from
[[cite-only-after-reading-what-the-source-tells-you-to-read-first]], where an
efficient reading pattern skips a header carrying *instructions to citers* and
the failure is non-compliance with them. Here the skipped line carries the
*identifier itself* and the failure is fabrication. Both share the root shape —
efficient reading windows exclude the top of what they sample — so they belong
together, and neither replaces the other. Related in effect to
[[equivalence-gate-verifies-behavior-not-facts]]: a name is a fact, and no
behavioural check reaches it.
