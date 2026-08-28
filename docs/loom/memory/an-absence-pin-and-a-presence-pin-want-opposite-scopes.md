---
name: an-absence-pin-and-a-presence-pin-want-opposite-scopes
description: A presence pin must be narrowed to the region that owns the claim or it goes false-green, but narrowing an ABSENCE pin is a silent weakening — a retired instruction is a defect wherever it lives, so scoping its absence check to one section lets it return in any other with the suite green; keep an absence pin only when it is paired with a positive assertion of the replacement AND the retired string is a conflicting instruction, and leave it unwindowed
type: practice
origin: pin-granularity migration (2026-08-28) — twelve batch agents settled this rule three incompatible ways and all three landed on one branch; whole-branch review found it, and both arms independently flagged the windowed case
---

Refactoring markdown pins to assert invariants rather than wording produced
one rule everyone had to apply and nobody had been given: what to do with
`assert "<retired wrong phrase>" not in text`. Twelve independent agents split
2–2 and shipped three different treatments on the same branch — one widened
the scope (correct), one narrowed it to a section, one deleted four of them.

**Why the two shapes pull opposite ways.** A presence pin answers "does the
region that owns this rule still state it?", so its window is what gives it
force: matched against whole-file text, a short phrase survives the deletion
of the very rule it stands for. An absence pin answers "did this retired
instruction come back?", and a retired instruction is a defect *wherever* a
reader can find it — an executor who reads it in the frontmatter acts on it
just as readily as one who reads it in the section it used to govern. So the
window that strengthens the first assertion weakens the second, and the
weakening is invisible: it reads as the same discipline being applied
uniformly, and the suite stays green.

**Why an absence pin is never the primary guard.** It can only detect a
literal copy-paste return, never a reworded one. That is a real but narrow
power, and it does not carry the rule — the positive assertion does. Its
residual value is the case the positive assertion cannot cover: the retired
sentence being re-added *alongside* the new one, where every presence pin
stays green and a reader can still follow the old instruction. That is a
supplemented-not-replaced defect, and it is the only thing the absence pin is
for.

**How to apply.**

1. Keep an absence pin only when BOTH hold: it is paired with a positive
   assertion of the replacement rule in the same test, and the retired string
   is a **conflicting instruction** — its literal return would change what an
   executor does. A retired rationale, gloss, or topic sentence instructs
   nobody; delete it.
2. Leave every absence pin **unwindowed**. Say so in a comment next to it,
   because the next person tidying pins will otherwise narrow it for
   consistency with its positive neighbour.
3. Delete an absence pin when a wording-independent check already covers
   every form of the same regression — a structural regex, or a sibling pin
   on the retired mechanism's *name* rather than its sentence.
4. Prove the pin by mutation before trusting it: re-insert the retired string
   **in a different section from the one it used to live in**. A windowed
   absence pin passes that mutation, which is exactly how this defect hides.

Related: [[a-doc-pin-makes-a-prose-defect-permanent]] (the presence-side rule
this is the mirror of — prefer the distinction over a token, and the same
review found four pins on tokens that recurred inside their own windows);
[[a-verbatim-pin-proves-nobody-edited-the-sentence]] (what a wording pin can
and cannot answer); [[asserting-absence-needs-full-text-not-an-abstract]]
(the same shape one layer up — an absence CLAIM is only as strong as the
surface it was checked against, and a narrowed check is a shallow read).
