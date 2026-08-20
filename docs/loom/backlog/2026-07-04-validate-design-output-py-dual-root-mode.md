---
name: 2026-07-04-validate-design-output-py-dual-root-mode
description: validate_design_output.py dual-root mode
status: closed
origin: live-verify finding 4 (report docs/loom/dogfood/2026-07-04-loom-pipeline-v1-live-verify.md); the validator assumes DESIGN.md + ui-flows.md are colocated, but the sanctioned layout (audit #472) splits product-level vs per-change — exit 1 is structurally guaranteed. Needs --design-root/--flows-root (or equivalent) arguments.
start: next loom-interface-design touch
---

- Start: next loom-interface-design touch
- Origin: live-verify finding 4 (report
  docs/loom/dogfood/2026-07-04-loom-pipeline-v1-live-verify.md); the
  validator assumes DESIGN.md + ui-flows.md are colocated, but the
  sanctioned layout (audit #472) splits product-level vs per-change —
  exit 1 is structurally guaranteed. Needs --design-root/--flows-root
  (or equivalent) arguments.

Swept 2026-08-06: shipped in loom-interface-design 0.4.0 (2026-07-04) /
PR #472 — `validate_design_output.py:77-91` `_resolve_design_doc` resolves
DESIGN.md most-specific-first (change folder, then parent), killing the
guaranteed exit-1.
