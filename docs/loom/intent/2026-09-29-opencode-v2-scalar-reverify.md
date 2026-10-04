# OpenCode v2 scalar parser residual fix verification
originator: kouko
kind: engineering
needs-design: no — internal loader-tooling fix and its verification only; no new user-facing interface surface in this repo
status: confirmed 2026-09-29
publication: automatic — authorized 2026-09-29 by kouko

## Problem
The opencode-v2-plugin-compat change's closing-review episode ended NON_CONVERGENT: its Round 3 terminal verification (second vendor codex) reproduced one real defect in the loader's YAML scalar parser — plain-scalar comment stripping treated embedded quote characters as quoted regions, so `description: foo "bar # baz" # tail` yielded `foo "bar # baz"` where PyYAML yields `foo "bar`. The fix (commit 7de9eb66c) is committed and locally verified (698 package tests, 5 adversarial programs, PyYAML cross-check byte-for-byte on 20 cases; loom reviewer independently PASSed the post-fix tree), but loom's bounded-episode rule forbids a Round 4, so the second vendor never re-reviewed the final digest.

## Proposed outcome
The committed plain-scalar comment-stripping fix (7de9eb66c) receives a fresh closing-review episode whose Round 1 reviews the final digest with both vendors, so the residual fix verification gap closes and the opencode-v2 change can converge and ship.

## Acceptance
1. The scalar parser in `scripts/opencode-loader.template.js` matches PyYAML 6 ground truth byte-for-byte on plain scalars with embedded quotes followed by comments, quoted scalars with trailing comments, and the YAML 1.2 double-quote escape table (including `\0 \a \v \e \N \L \P` and escaped backslash-n).
2. A fresh closing-review Round 1 on the final digest returns no NEEDS_REVISION from either the second vendor (codex) or the loom reviewer.
3. The full package suite and all 5 committed adversarial programs pass on the final digest.
4. Existing host packaging and all previously verified behavior (block scalars, folded scalars, chomping, description-less skip, async transform await, byte-exact generation) remain intact.

## Constraints
- No new functional content: the fix is already committed (7de9eb66c); this episode verifies it, it does not extend the loader.
- Same branch (feat/2026-09-29-opencode-v2-plugin-compat); no rework of already-reviewed commits.
- Second vendor remains codex per the prior change's selection.

## Out of scope
- Any new loader features or refactors beyond the committed fix.
- Re-opening findings already fixed and verified in the prior episode (Rounds 1-2).

## Open questions
- none
