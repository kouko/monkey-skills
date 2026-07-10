---
name: imperative-trigger-cards-beat-descriptive-preloads
description: Preloading a rule into session context fixes "rule never read", NOT "rule read but not obeyed" — weak models act on short imperative action-moment cards ("before typing X → invoke Y FIRST", 2/2 flip) while descriptive discipline prose provably in context moved behavior 0/2; phrase always-loaded cards as imperatives anchored to the acting moment
type: practice
origin: more-visualization branch dogfood (docs/loom/dogfood/2026-07-10-visual-trigger-weak-model-dogfood.md)
---

Two always-loaded injections were A/B-tested on haiku the same day: an
imperative action-moment trigger card (ascii-graph-toolkit 0.5.0:
"Before typing any box-drawing diagram … invoke the `ascii-graph` skill
FIRST") flipped behavior 2/2 vs 0/2 baseline; a descriptive
relay-discipline section (family-relay §(b) Visual defaults, preloaded
by loom-pipeline 0.7.0) was provably in context — the probe quoted it
verbatim — yet moved behavior 0/2, with one run directly violating the
loaded rule.

**Why:** getting a rule INTO context and getting a weak model to ACT on
it are separate problems. Descriptive prose ("Flow / state shape →
ascii-graph-toolkit") states a mapping; it does not interrupt the
model's reflexive next action. An imperative anchored to the acting
moment ("before typing the first `┌` → do Y FIRST") does.

**How to apply:** when a rule must change model behavior (not just be
citable), write the always-loaded card as a short imperative bound to
the moment of action, and behaviorally test it on the weakest model
tier that will run it (headless-branch-plugin-testing-recipe). Preload
of longer doctrine is still fine for reference/citation purposes — just
do not expect it alone to steer behavior.
