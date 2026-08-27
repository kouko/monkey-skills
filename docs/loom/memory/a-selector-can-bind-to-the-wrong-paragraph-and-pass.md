---
name: a-selector-can-bind-to-the-wrong-paragraph-and-pass
description: A check that locates its target by keyword can bind to a different passage carrying the same keywords, and every assertion after it then passes against text nobody meant to check — the check is green, dead, and reads as coverage; select the target by something only the target has, and prove the selection by a mutation that removes the intended target's content alone
type: gotcha
origin: PR after #748 (loom/reachable-anchor-lessons, review round 1, 2026-08-28)
---

A document's attribution paragraph was pinned by searching every paragraph for
one containing the vendor names, the three field names, and the quoted vendor
wording. The document also carries a citation block listing those same vendors,
the same field names, and the same quotes — one paragraph, because the bullets
have no blank line between them. The selector matched the citation block first.
Every assertion after it then passed, against a passage that was never the
subject. Two mutations aimed at the real paragraph left the test green; only
checking that the mutation had actually written to disk, and then asking why a
real edit changed nothing, exposed it. The version this replaced had used a
disambiguating keyword and said so in a comment; that comment was deleted along
with the keyword during a rewrite that was strengthening the assertions.

**Why:** the failure is invisible in exactly the situation that produces it.
Evidence-based pinning is the right instinct — quote what the source actually
says, so a reword cannot drift the claim — but the quotes live in the cited
material too, which is what makes the collision near-certain rather than
unlucky. And a green test after a mutation reads as "the mutation was
harmless", not as "the assertion was pointed elsewhere", so the diagnosis
runs in the wrong direction. Compare
[[a-test-can-be-correct-and-still-unable-to-fail]], where the assertions were
aimed correctly and the inputs made the mutation inert; here the inputs were
fine and the aim was wrong.

**How to apply:** select a passage by something only that passage carries — its
own heading, its bold lead label, its position — never by a conjunction of
terms that its subject matter also supplies. When a selector must use content,
assert the selection separately from what is being checked, so a miss fails as
"target not found" rather than passing silently. Prove the whole chain with a
mutation that removes the intended target's content and nothing else, and
**confirm the mutation reached the file before reading the result** — a
mutation that never applied and a mutation that was ignored are the same green.
Treat a mutation that leaves a test green as a claim about the test until
proven otherwise, and when a rewrite deletes a disambiguating term, read what
its comment said before assuming the term was decoration.
