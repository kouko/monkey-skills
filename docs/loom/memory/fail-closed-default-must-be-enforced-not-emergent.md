---
name: fail-closed-default-must-be-enforced-not-emergent
description: A fail-closed "never trust by default" gate must ENFORCE the default with an explicit guard, not let it EMERGE from a comparison — e.g. `accuracy >= threshold` with 0 labels + min_samples≤0 + threshold 0.0 evaluates 0.0 >= 0.0 → TRUSTED with zero ground truth. Add `if not evidence or min_samples < 1: NOT_TRUSTED` before the comparison ladder, and pin it with a zero-evidence test.
type: gotcha
origin: 2026-07-14 session — investing-toolkit analysis-kpi slice 5 (reliability gate evaluate); adversarial code-quality review caught the TRUSTED-by-omission path
---

The operational-kpi reliability gate must be fail-closed: a company is TRUSTED
only when measured extraction accuracy ≥ a threshold over a large-enough
held-out label set; anything else (no labels, too few, no threshold, below bar)
is WITHHELD / NOT_EVALUATED. The first implementation expressed the verdict as a
comparison ladder:

```python
if sample_size < min_samples: verdict = NOT_EVALUATED
elif accuracy >= threshold:   verdict = TRUSTED    # BUG surface
else:                         verdict = WITHHELD
```

With `min_samples <= 0` (an operator could pass `--min-samples 0`) and zero
labels, `sample_size(0) < min_samples(0)` is False, so it fell through to
`accuracy(0/0 → 0.0) >= threshold(0.0)` → **TRUSTED with zero ground truth** —
the exact trusted-by-omission the gate exists to prevent. The fail-closed
property was EMERGENT (it happened to hold for min_samples ≥ 1), not enforced.

**Why:** a safety default that only holds "for the normal inputs" is not a
default — it is a latent bug waiting for the edge input (here, an operator flag).
Fail-closed must be the FIRST thing the code asserts, unconditionally, before any
"does it pass?" comparison.

**How to apply:** for any trust/allow/pass gate, write the fail-closed guard as an
explicit early return covering the "no evidence to judge on" cases (empty label
set, non-positive sample floor, unset threshold) BEFORE the comparison that can
grant trust — never rely on the comparison's operands happening to fall the safe
way. Pin it with a zero-evidence / degenerate-config test that asserts NOT-trusted
(it would go TRUSTED under the emergent-only version). Same discipline as
[[required-identity-guard-must-reject-whitespace-not-just-empty]] (an
authorization boundary enforced explicitly, not left to a falsy accident).
