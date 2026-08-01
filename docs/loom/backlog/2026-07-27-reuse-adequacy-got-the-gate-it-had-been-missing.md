---
name: 2026-07-27-reuse-adequacy-got-the-gate-it-had-been-missing
description: `Reuse-adequacy` got the gate it had been missing
status: SHIPPED
origin: source audit `docs/loom/audits/2026-07-27-investing-arc-defect-provenance-audit.md` §8 candidate 3; retargeted by `docs/loom/audits/2026-07-31-a-class-interceptability-backtest.md`, which ruled out candidate 1 as structurally unable to reach PR #619 A-2.
---

- What shipped: the field became two slots (`Observed` + an obligatory source
  marker from a closed three-value vocabulary, `Intended`), the author-side
  adequacy claim was removed, and `plan-document-reviewer` Check 17 now grades
  presence / marker / source cross-read / adequacy — the last carrying a tier
  floor. `CHK-SPEC-009` mirrors it on the SDD side. Design and measurement:
  `docs/loom/specs/2026-07-31-reuse-adequacy-declaration-hardening.md`.
- **Read this before treating the class as closed**: the change covers ONE slice
  of A-class — a plan instructing reuse of an existing helper on a new call path.
  The branch that shipped it generated seven A-class defects of its own, and the
  new machinery would have caught **none** of them (three under-declared `Files
  touched`, a false justification in a brief, an unowned derived sentence, an
  acceptance criterion specifying an impossible outcome, a drifted line-number
  citation). An eighth incident on the same branch — a scripted edit that
  corrupted the plan — is deliberately **excluded**: the next gate caught it, and
  evading the downstream gates is what makes A-class A-class. The first draft of
  this caveat counted it anyway, and a docs review caught that — a warning about
  one mechanism's narrow reach had padded its own evidence. The slice is real and
  was measured; the population around it is wide and mostly ungated.
- Origin: source audit
  `docs/loom/audits/2026-07-27-investing-arc-defect-provenance-audit.md` §8
  candidate 3; retargeted by
  `docs/loom/audits/2026-07-31-a-class-interceptability-backtest.md`, which
  ruled out candidate 1 as structurally unable to reach PR #619 A-2.
- What (the problem, as it stood **before** this entry shipped — pinned at
  `f5d9800e`, read with `git show f5d9800e:<path>`; the line numbers below no
  longer resolve to the content they describe, and
  `test_reuse_adequacy_field_present` was retired by the fix): the field shipped
  in loom-code 0.39.0 (`loom-code/skills/writing-plans/references/plan-format.md:141-147`) and
  **nothing enforced it**. No check in `loom-code/skills/writing-plans/references/plan-document-reviewer-prompt.md` names
  it, so a plan omitting it returns `PASS`; the nearest sibling
  `loom-code/skills/subagent-driven-development/checklists/spec-consistency.md:86` (`CHK-SPEC-008`) covers `External surfaces` only. Its
  two tests (`loom-code/scripts/test_plan_fact_grounding.py:230`,
  `loom-code/scripts/test_writing_plans_readme_sync.py:56`) assert the string is present in the
  document, not that any behaviour follows.
- Second, separable defect: the field's **direction of fit is ambiguous** — it
  reads equally as a report about existing code and as a spec for intended code.
  Measured 2026-07-31 on a sandbox reproducing the #619 A-2 shape: haiku asserted
  a match and invented a supporting behaviour in the future tense ("the archive
  **will** record all results including skipped entries"), sonnet read it as a
  report and refused the why-acceptable clause. Presence enforcement alone does
  not touch this half.
- Do not re-run the superseded experiment: stage 2 was designed to test a
  "two closed questions" contract, which the research round falsified before it
  ran (a declaration whose author also judges it is Chain-of-Verification's
  weakest variant). Stage 2 tests the brief's option D.
