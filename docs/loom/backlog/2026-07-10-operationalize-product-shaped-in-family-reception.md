---
name: 2026-07-10-operationalize-product-shaped-in-family-reception
description: Operationalize "product-shaped" in family reception
status: OPEN
origin: loom-discovery dogfood (`docs/skill-dogfood/2026-07-10-loom-discovery/report.md` FINDING-010) — three independent cold-readers flagged "product-shaped" as never operationalized; it gates on-ramp rows 1 AND 4, so the ambiguity is family-wide, not loom-discovery's.
start: next time any session or dogfood cold-reader again reports guessing at whether work is "product-shaped" vs "an increment" (one more occurrence past the 2026-07-10 loom-discovery dogfood, per the two-occurrence rule).
---

- Start: next time any session or dogfood cold-reader again reports
  guessing at whether work is "product-shaped" vs "an increment" (one
  more occurrence past the 2026-07-10 loom-discovery dogfood, per the
  two-occurrence rule).
- Origin: loom-discovery dogfood
  (`docs/skill-dogfood/2026-07-10-loom-discovery/report.md` FINDING-010)
  — three independent cold-readers flagged "product-shaped" as never
  operationalized; it gates on-ramp rows 1 AND 4, so the ambiguity is
  family-wide, not loom-discovery's.
- What: add a one-line decidable test (or 2 worked examples) to
  `loom-pipeline/hooks/family-reception.md` — mind the 60 non-empty-line
  budget enforced by `test_pipeline_reception.py`; may need to land in
  the entry skills' §Intake instead.
