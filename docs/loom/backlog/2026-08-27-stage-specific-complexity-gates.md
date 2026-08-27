---
name: 2026-08-27-stage-specific-complexity-gates
description: Loom stages evaluate the complexity they introduce without coupling independently installable plugins
status: bet
origin: user-established Codex goal for the stage-specific complexity mechanism
start: user explicitly promoted this arc on 2026-08-27
serves: makes Loom self-correcting against stage-specific accidental complexity while preserving cold standalone plugin adoption
---

Design and ship stage-specific complexity lenses for business planning,
process design, interface design, system architecture, and implementation
engineering. Each owning skill must judge complexity in its own terms and
leave enough project-owned evidence for downstream stages to understand the
trade-off without rerunning the upstream judgment.

Keep independently installable plugins autonomous: no mandatory sibling
skill, reference, script, or filesystem path. Cross-plugin cooperation may
use only project-owned `docs/loom/` artifacts and optional public-capability
detection. Do not introduce a universal complexity score, duplicated
orchestrator, synchronized prose regime, or unrelated cleanup.

Next step: freeze a deletion-first design brief grounded in the current
business-value, interface, spec, planning, and code-review checkpoints; then
implement it test-first through a reviewed PR that stops ready for human merge.
