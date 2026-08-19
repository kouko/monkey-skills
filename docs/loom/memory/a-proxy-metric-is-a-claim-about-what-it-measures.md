---
name: a-proxy-metric-is-a-claim-about-what-it-measures
description: A number stood in for a property nobody verified it tracked — squareness `min(W,H)/max(W,H)` was used to decide whether a mermaid subgraph's `direction` had taken effect, and it cannot tell "the rows are laid out horizontally" from "the boxes happen to be wide", so it ranked the best-looking WRONG shape first (0.807, rows secretly stacked) above the correct one (0.686); when a metric is standing in for a property, validate it against a case where the two must disagree, and read the underlying structure directly at least once
type: practice
origin: 2026-08-19 cot-explain arc (dev-workflow 2.27.0) — a layout rule, its appendix of fifteen measurements, and a proposed fix were all decided on squareness; the fix was adopted and had to be withdrawn after node coordinates were parsed out of the SVG
---

A proxy is adopted because the real property is awkward to observe. That is
the whole point, and it is also why nobody goes back and checks that the
proxy tracks it.

Here the real property was "did this subgraph's declared `direction` take
effect". The proxy was the rendered figure's squareness. It is a reasonable
first guess — a laid-out row IS wider — and it survived a full appendix of
fifteen variants, a shipped rule, and two releases.

Then a candidate fix scored **0.807**, the best of three, and its rows were
stacked the entire time; the correct shape scored **0.686**. The proxy did
not merely lose resolution, it **inverted the ranking**. The figure was
squarer because the boxes were wider, which is a different cause with the
same signature.

**Why it survives review:** the proxy produces a number, and numbers read as
measurement. Nobody asks "measurement of what?" once a table of them exists.
Every reviewer of that appendix, including its author, checked whether the
numbers were correctly obtained — none checked whether the quantity was the
one the rule needed.

**How to apply:**

- When a metric stands in for a property, name both in one sentence: *"X is
  a proxy for Y."* If that sentence is awkward to write, the substitution is
  doing more work than anyone has noticed.
- Validate on a case where proxy and property MUST disagree — construct the
  adversarial shape deliberately rather than waiting for it. One such case
  here (wide boxes, stacked rows) would have retired the metric immediately.
- Read the underlying structure directly at least once, however tedious:
  parse the coordinates, dump the DOM, count the rows. A single direct
  observation is what turns the proxy from an assumption into a calibrated
  instrument.
- Prefer a check that cannot be satisfied accidentally. The replacement here
  asserts each declared row shares one y and increases in x — a property
  that is either true of the layout or not, with no second cause.

Related: [[a-tool-behaviour-measured-in-one-repo-state-is-not-a-general-fact]],
[[an-inherited-external-tool-fact-is-a-claim-with-a-version-attached]],
[[a-control-placed-downstream-of-what-it-guards-is-not-a-control]].
