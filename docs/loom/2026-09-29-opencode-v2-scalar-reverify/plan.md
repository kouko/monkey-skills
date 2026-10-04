# OpenCode v2 scalar parser residual fix verification — plan
intent: 2026-09-29-opencode-v2-scalar-reverify@48267532a
charter: 1.1

## Current State Evidence
- Forward: opencode-v2 change complete except Round 3 codex found a plain-scalar comment-stripping defect; fix 7de9eb66c committed, locally verified (698 tests, 5 adversarial, PyYAML cross-check; loom PASSed).
- Reverse: loom bounded-episode forbids Round 4; codex never re-reviewed final digest. This episode re-runs closing-review Round 1 on final digest with both vendors.
- Error: Quotes inside plain scalar must not protect `#`; only leading quote makes scalar quote-aware. Fix added 9 QUOTED_SCALAR_CASES.
- Data: Final loaders (21) byte-match template; `generate_opencode_loaders.py --check` passes.
- Boundary: Existing host packaging unchanged; no interface-surface globs touched.

## Task DAG

**V-01** Verify the residual fix digest with both closing-review vendors  after: —  acceptance: 1, 2, 3, 4
- Files: (verification only) scripts/opencode-loader.template.js, scripts/test_opencode_loaders.py, 21× `.opencode-plugin/index.js`, docs/opencode.md, README.ja.md, docs/loom/2026-09-29-opencode-v2-plugin-compat/evidence/*
- Test: A1 positive: scalar parser matches PyYAML on reproduction corpus; A2 positive: fresh Round 1 returns PASS from both vendors; A3 positive: full suite + 5 adversarial pass; A4 positive: diff vs base shows no rework of reviewed content.
- Risk: Verification-only. If a vendor finds a new defect, record and return to Build; no known blockers.

## Simplicity check
- Single-task verification episode — taken

## Questions asked
1 — what — 開新 slim episode 收尾：新 intent 只做「把已修好的最終 fix 送回 codex 與 loom re-review」，拿到 codex 對最終 digest 的 PASS 後收斂並 ship — 使用者選「開新 slim episode (Recommended)」

## Risks
1. Closing-review Round 1 on the final digest returns NEEDS_REVISION from a vendor; per bounded-episode rules this fresh episode gets its own 3-digest budget, so a fix here does not collide with the prior episode's cap.
2. The loom reviewer's prior Round-3 PASS was on the post-fix tree; this episode's fresh dispatch must be a new fresh-context reviewer, not a resume of the prior one, so the verdict is clean.
