# Loom-code rule sheet — deltas only

## Preamble

General LLM knowledge of Clean Code / SOLID / DRY / TDD / F.I.R.S.T /
OWASP is baseline. This sheet covers only loom-code deltas not in
training data. Standards files are on-demand citation targets, not
preloads.

## Thresholds + verdict aggregation

- Function length: 20-line soft (Clean Code Ch.3) / 50-line hard
  (house) / 100-line gate-warning (`naming-and-functions.md`).
- Verdict (`quality-gate.md` §Verdict Rules): any 🔴 → NEEDS_REVISION;
  2+ 🟡 → NEEDS_REVISION; 1 🟡 → PASS_WITH_NOTES; all 🟢 → PASS.
  Opaque finding (no `where:` / `source:`) → NEEDS_REVISION.
  Scope: quality / architecture dimensions. The spec-reviewer is
  binary per its role contract (PASS / NEEDS_REVISION only, no
  PASS_WITH_NOTES) — there a lone 🟡 → NEEDS_REVISION, not
  PASS_WITH_NOTES.
- Severity: 🔴 fatal / 🟡 should-fix / 🟢 nit (informational).

## Dimension → standard path

Paths under `subagent-driven-development/`:

- security → `checklists/security-checklist.md` +
  `standards/app-security-standard.md` +
  `standards/character-encoding-security.md`
- architecture → `rubrics/arch-gate.md` + `standards/solid-principles.md`
- correctness → `rubrics/quality-gate.md` + implementer `test_results`
- naming → `standards/naming-and-functions.md`
- tests → `standards/tdd-standard.md`
- refactoring → `standards/refactoring-standard.md` +
  `standards/pragmatic-principles.md`
- external-surface-grounding → `standards/external-surface-grounding.md`

## Cite-on-fire discipline

MUST `Read` before citing: `character-encoding-security.md` (徳丸本
Ch.6); `app-security-standard.md` (OWASP ASVS V5 §X.Y.Z); house
thresholds + verdict rules.

May cite from memory: Clean Code chapters; Fowler smells; Beck 2002.
