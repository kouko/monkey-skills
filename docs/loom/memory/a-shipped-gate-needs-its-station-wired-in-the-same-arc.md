---
name: a-shipped-gate-needs-its-station-wired-in-the-same-arc
description: A mechanical checker can ship fully built, tested, and registered — and still be dead code, because no workflow station's prose ever runs it; "wired the same way existing checkers are wired" means a named unconditional-gate paragraph in the consuming SKILL plus the reviewer check row instructing the run, and the wiring belongs in the same arc as the checker, verified by grepping for a caller
type: practice
origin: seam-contracts arc (2026-08-25) — check_seam_coverage.py landed with 9 passing tests and a fail-loud registration, while plan-format.md claimed in present tense it "is checked mechanically"; no station invoked it. Both whole-branch docs reviewers flagged it (one 🔴, citing the brief's own BI-5 "wired the same way existing plan/brief checkers are wired"); the fix round added the writing-plans unconditional Seam-coverage gate and recast Check 20 into the run-the-script sole-authority form
---

The checker existed, passed its tests, and was reachable by nothing. Prose
elsewhere asserted live enforcement in the present tense, so every reader
would assume the mechanical leg already ran — the exact false-safety this
store's 2026-08-04 backlog entry describes for rules that ship into a skill
but never reach their executing contract.

**Why:** building and wiring are separate artifacts that pass separate
tests. The checker's own suite proves behavior, not reachability; only a
grep for callers proves a station runs it.

**How to apply:** (1) a task that ships a gate script includes, in the same
arc, the consuming station's gate paragraph (the sibling-gate shape: named
**<X> gate (unconditional):**, the exact command, what a non-zero exit
blocks) and — where a reviewer enforces the same ground — the check row in
the run-the-script sole-authority form; (2) before writing present-tense
enforcement claims, grep the repo for a caller of the script and cite the
station; (3) at review, "who runs this?" is a mechanical question: zero
grep hits outside the script's own tests = unwired, a gating finding.
