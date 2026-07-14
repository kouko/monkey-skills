---
name: description-sweeps-must-run-owning-plugin-suite
description: Frontmatter-description edits look test-free but plugins pin description content in scripts/ guard tests ("Axis 0" mandate, "not for"/N/A needles, isolation clauses) — a sweep dispatch that omits the owning plugin's package suite ships red guards to close-out; every description-sweep task packet must carry that plugin's suite as its Resolved test command
type: gotcha
origin: feat/description-token-economy Task 7c collateral (2026-07-14) — two loom-code guards red at close-out; the 7c dispatch omitted the package suite and verdict-only reviewers never ran tests
type_note: also proven the other direction — loom-discovery's whole-file isolation guard forced a 7a description clause to stay (body line-wraps mid-phrase)
---

Task 7c rewrote six loom-code descriptions; its dispatch packet omitted
a Resolved test command (the orchestrator assumed prose edits are
test-free), the implementer ran only a length self-check, and both
reviewers were verdict-only. Two description-pinning guards
(`test_brainstorming_axis0`, `test_ui_verification_skill`) went red and
stayed red until the close-out fix round. The reverse case in the same
arc: `test_using_skill.py`'s whole-file isolation assertion is only
satisfiable by the router DESCRIPTION (the body's phrase line-wraps),
so the sweep had to keep a clause a pure cutting-rules reading would
delete.

**Why:** description text is contract surface — plugins pin routing
mandates, N/A announcements, and isolation phrases in scripts/ tests.
A sweep that only measures char counts is blind to these pins in both
directions (breaking them, or wrongly deleting what they require).

**How to apply:** every description-sweep or frontmatter-edit task
packet carries the owning plugin's package suite (plus the repo tri-dir
suite) as its Resolved test command, and the implementer greps the
plugin's scripts/ for tests reading the SKILL.md before cutting.
