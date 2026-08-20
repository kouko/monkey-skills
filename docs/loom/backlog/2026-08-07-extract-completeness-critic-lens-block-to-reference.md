---
name: 2026-08-07-extract-completeness-critic-lens-block-to-reference
description: completeness-critic keeps its ~600-word 6-lens block inline; design-critic already extracted its equivalent
status: open
blocked: waiting on the next edit to completeness-critic/SKILL.md needing word-cap headroom
origin: 2026-08-07 family complexity audit (docs/loom/audits/2026-08-07-family-complexity-audit.md, item C1); reaffirms the earlier parked decision to extract loom-spec skills only when an edit needs the headroom
start: the next edit to loom-spec/skills/completeness-critic/SKILL.md needs word-cap headroom
---

completeness-critic/SKILL.md:191-252 holds the six lens descriptions
inline (~600 w; body total 3,947 w against the 4,500 cap). design-critic
already extracted its equivalent content to
references/design-heuristics.md, so the precedent and the mechanical
shape both exist — extraction is a ~15% cut with low risk.

Deliberately parked, not scheduled: the standing decision for the
loom-spec watchlist is "extract when an edit needs it", and no pending
edit does. When executing, follow the extraction discipline recorded in
docs/loom/memory/ (weak-model cold-read after any extraction that
separates a rule from a rule it depends on).
