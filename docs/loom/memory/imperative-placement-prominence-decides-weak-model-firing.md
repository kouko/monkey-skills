---
name: imperative-placement-prominence-decides-weak-model-firing
description: An action-moment imperative that NAMES the skill can still fail to fire on a weak model if it's buried as a prose aside appended after routing logic — the SAME sentence promoted to a prominent bold directive (a numbered load-bearing rule, or inside an <EXTREMELY-IMPORTANT> block, near the router's core guidance) fires reliably; placement/prominence is a second axis beyond imperative-vs-descriptive, and guard tests that only assert the string is PRESENT are blind to it
type: gotcha
origin: feat-bba-proactive-trigger-hardening (2026-07-25) rounds 4-5 weak-model dogfood
---

The bba-hardening branch added the SAME imperative ("before you ask a
complex fork … run `dev-workflow:brief-before-asking` first", + the
verbatim triple) to five carriers. On haiku, the four design-side
routers split cleanly by PLACEMENT, not wording:

- interface-design put it as a numbered load-bearing rule inside an
  `<EXTREMELY-IMPORTANT>` block → **3/3 briefed**.
- discovery / product-principles / spec appended it as a prose aside a
  few paragraphs after the routing logic → **0/3, 1/3, 1/3**.

Rewriting the three weak ones into a prominent bold directive (a peer
"Step N —" rule, a standalone bold-imperative paragraph, or moved into
the `<EXTREMELY-IMPORTANT>` block) — no wording change to the imperative
itself — lifted them to **3/3, 3/3, 2-3/3**. All six guard tests stayed
green the whole time because they only assert the skill-ID + triple are
PRESENT.

**Why:** getting an imperative INTO the always-relevant text is
necessary but not sufficient on a weak model — a buried aside is read
past. This is a second axis beyond
[[imperative-trigger-cards-beat-descriptive-preloads]] (imperative vs
descriptive): among imperatives, PROMINENCE at the acting moment decides
firing. String-presence guards can't see it, so a placement regression
ships green.

**How to apply:** (1) place a behavior-steering imperative as a
prominent directive at the acting moment — a numbered load-bearing rule
or an `<EXTREMELY-IMPORTANT>`-block peer, near the router's core
guidance — never as a trailing prose aside; (2) match the target file's
own convention for prominence (a "Step N —" router uses a peer step; an
`<EXTREMELY-IMPORTANT>`-block router uses a peer rule); (3) don't trust
a string-presence guard as evidence it fires — behaviorally cold-read on
the weak tier, comparing placement variants, is the only test that
catches a buried-imperative regression.
