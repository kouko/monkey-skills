# Plan: synthesis calibration-prepend (缺口 1, Option A)

Source brief: docs/loom/specs/2026-06-15-synthesis-calibration-prepend.md
Total tasks: 3
Critical-path depth: 3 (≤5)
Execution order: sequential (all tasks chain — same module then doc-mirrors-code)
Plan-document-reviewer verdict: PASS (2026-06-15, 11/14 checks, rest N/A)

Working dir: research-toolkit/skills/deep-deep-research/ (worktree deep-research-r2)
Test command (package level): `cd research-toolkit/skills/deep-deep-research/scripts && PYTHONDONTWRITEBYTECODE=1 python -m pytest -q`

## Task 1 — calibrate.py core (static directive + function)
- Description: Create new house module `scripts/calibrate.py` with a module docstring recording
  provenance (GRADE anti-averaging + NMA weakest-link; ICD-203; ICMJE/CONSORT-A "spin"
  abstract-consistency) WITHOUT leaking it into runtime, a `CALIBRATION_BLOCK` string constant
  encoding the 3 anti-laundering rules, and a `calibration_block()` function returning it. Mirror
  the structure/style of `mode_route.py` (flat imports, `from __future__ import annotations`).
  The 3 rules: (1) merged finding confidence = weakest load-bearing claim (no high if any source
  is secondary/single/blog/split); (2) summary confidence ≤ body confidence; (3) split/tied votes
  OR mutually-conflicting confirmed claims must not be presented as consensus.
- Module: research-toolkit/skills/deep-deep-research/scripts/calibrate.py
- Files touched: research-toolkit/skills/deep-deep-research/scripts/calibrate.py, research-toolkit/skills/deep-deep-research/scripts/test_calibrate.py
- Context paths:
  - research-toolkit/skills/deep-deep-research/scripts/mode_route.py (template to mirror)
  - research-toolkit/skills/deep-deep-research/scripts/test_mode_route.py (test style)
- Acceptance:
  - RED: `test_calibrate.py::test_calibration_block_encodes_three_rules` — imports `calibration_block`, asserts the returned string contains all three rule signals (weakest/weakest-load-bearing; summary ≤/not exceed body; consensus/conflict not flattened). Fails (ModuleNotFoundError) before.
  - GREEN: function returns the static directive containing all three rules; test passes.
- Dependencies: none
- Independent: false
- Brief item covered: "Build a new house module `scripts/calibrate.py` that emits a STATIC calibration directive" + the 3 anti-laundering rules (Decision section).

## Task 2 — calibrate.py CLI (`block` + unknown-subcommand)
- Description: Add a `main(argv=None)` CLI to `calibrate.py` mirroring `mode_route.py` main():
  `calibrate.py block` writes `{"calibration_block": "<directive>"}` as JSON to stdout and exits 0;
  unknown/missing subcommand → message to stderr + exit 1. No stdin, no schema, no classify
  (static). Add `if __name__ == "__main__": sys.exit(main())`.
- Module: research-toolkit/skills/deep-deep-research/scripts/calibrate.py
- Files touched: research-toolkit/skills/deep-deep-research/scripts/calibrate.py, research-toolkit/skills/deep-deep-research/scripts/test_calibrate.py
- Context paths:
  - research-toolkit/skills/deep-deep-research/scripts/mode_route.py (CLI shape, exit codes)
- Acceptance:
  - RED: `test_calibrate.py::test_cli_block_roundtrip` (subprocess `python calibrate.py block` → stdout parses as JSON with key `calibration_block`, exit 0) and `test_calibrate.py::test_cli_unknown_subcommand_exits_1` (exit 1, stderr non-empty). Fail before CLI exists.
  - GREEN: both subprocess tests pass.
  - Command surface: `calibrate.py block` is the declared invocation; verified runnable via the subprocess round-trip test (no new build/make verb — Python script invoked directly, consistent with sibling lever scripts).
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: "CLI: `calibrate.py block` → stdout `{\"calibration_block\": \"<directive>\"}`. No stdin, no schema, no classify (static). Exit 0; unknown subcommand → stderr + exit 1 (mirror mode_route)."

## Task 3 — SKILL.md Stage 6 opt-in "Calibration prepend" subsection
- Description: Add an opt-in, ADDITIVE "Calibration prepend" subsection to SKILL.md Stage 6 (after
  the purpose-fit subsection), describing: the static directive, the `calibrate.py block` call, the
  updated prepend order **purpose-fit → meta-mode → calibration → base** (calibration closest to
  base, governing tagging mechanics), the "default path unchanged / opt-in" framing, and a
  Degradation line ("if calibrate.py errors, fall back to the unmodified prompt — never block").
  Update the existing prepend-order reference in the purpose-fit subsection so the documented order
  is consistent across the file.
- Module: research-toolkit/skills/deep-deep-research/SKILL.md
- Files touched: research-toolkit/skills/deep-deep-research/SKILL.md
- Context paths:
  - research-toolkit/skills/deep-deep-research/SKILL.md (Stage 6, L389-564 — meta-mode + purpose-fit subsections to mirror)
  - research-toolkit/skills/deep-deep-research/scripts/calibrate.py (final CLI shape to document)
- Acceptance:
  - RED: grep SKILL.md for the new section heading ("Calibration prepend") AND the order string "purpose-fit → meta-mode → calibration → base" — both absent before (diagnostic returns no match).
  - GREEN: both present; the purpose-fit subsection's old order line is updated to include calibration; SKILL.md body still within token budget (~6,000 tokens / spot-check, no new subfolder).
- Dependencies: Task 2 completes first (doc mirrors the final CLI command/behavior — doc-mirrors-code, sequential despite different file)
- Independent: false
- Brief item covered: "SKILL.md Stage 6: add an opt-in 'Calibration prepend' subsection. Prepend order becomes purpose-fit → meta-mode → calibration → base ... Degradation: if calibrate.py errors, fall back ... never block."

## Notes
- `prompts.py` / `schemas.py` are SYNCED primitives — NOT touched by any task (Out of Scope in brief). calibrate.py is a NEW non-synced house module, so no drift-gate impact.
- No new subfolder (Anthropic flat-skill rule); calibrate.py + test_calibrate.py live in existing scripts/.
- Full-suite green (was 82) + siblings unchanged verified at verification stage, not a plan task.
