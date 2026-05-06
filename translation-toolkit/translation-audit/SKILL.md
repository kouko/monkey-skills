---
name: translation-audit
description: Audit existing translations against source. Takes (source, existing-target) input. Runs full M1+M2+S1+S2+I1 verification. Outputs diff report + improvement suggestions; no rewrite.
version: 0.1.0
---

# translation-audit

> **TODO**: full audit-pipeline prompt body lands in Task E1.

## Purpose

Audits an existing translation against its source. Read-only — outputs a diff report + improvement suggestions; does NOT rewrite the target. Useful for QA, vendor review, and pre-publish gate.

## Reference

- `references/audit-loop.md` — audit pipeline (no DRAFT step)
- `references/4d-reflection.md` — critique axes
- `references/verification-gates.md` — M1+M2+S1+S2+I1 all run
- `references/diff-report-format.md` — report schema
