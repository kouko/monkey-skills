# Gate friction pack — brief + plan (2026-07-06)

## Problem (upstream artifacts)

`docs/harness-audit/2026-07-06-iteration-roadmap.md` item 2 + BACKLOG
"Mechanical-gates v2 candidates" (c). Friction data, all from live use:
- **Strict-HEAD marker cost ×3 today**: docs-only amend (b076e3f0),
  codex-manifest one-liner (05e642c4), rebase-onto-main (#503) each
  forced a fresh review or marker rewrite despite unchanged content
  (or unchanged branch-diff content).
- **cd-chain guard miss**: `cd ~/dotfiles && git push` gated against the
  ORIGINAL cwd's repo markers (memory:
  loom-git-guard-evaluates-in-shell-cwd). `git -C` form already works
  (git-guard.py:271-276); the compound-`cd` form does not.
- **Marker-format discovery-by-crash ×3**: dimension_scores block
  required, findings need `where:` path tokens, suite-line needs
  "N passed" and no FAIL tokens — each learned via exit-4 retries.

## Smallest end state

Four cuts, all in loom-code, each independently shippable:

1. **Patch-id relaxation** (the headline). `loom_gate_markers.py
   review-pass` additionally records `base_sha` (merge-base with the
   default branch) and `patch_id` (`git diff base..HEAD | git patch-id
   --stable`). `git-guard.py::_gate_push` accepts a marker whose
   `head_sha` mismatches IFF the recomputed patch-id (current
   merge-base..HEAD) equals the recorded one — covering message-only
   amends AND content-preserving rebases. Fail-closed on any
   computation error. `verified.json` gets the same treatment.
2. **cd-chain tracking**. git-guard's segment loop tracks `cd <path>`
   segments and applies the effective cwd to later segments in the
   same command string (absolute + relative + `~` forms; unknown/
   dynamic paths → keep previous cwd, fail-closed toward gating).
3. **`validate` subcommand**. `loom_gate_markers.py validate
   --verdict-file X [--suite-line Y]` runs the exact write-time schema
   checks in dry-run and prints every violation at once (today's
   writers exit on the FIRST error — the ×3 retry loop).
4. **Marker-format spec doc**. The requirements live only in code
   today; add a §Gate markers reference block to
   `loom-code/skills/requesting-code-review/SKILL.md` (or references/)
   listing: verdict block requirements, suite-line grammar, waiver
   semantics, and the write-markers-then-push-separately ordering rule.

## Non-goals

- No weakening: patch-id equality is a *stricter-than-nothing* bypass —
  content changes still force re-review; only provably-identical
  branch diffs pass.
- No shell-emulation beyond `cd` (no subshells, no `$(...)`, no `pushd`).
- Waiver `scope` read-side check (BACKLOG item a) stays deferred —
  no friction datum yet.

## Acceptance

1. RED→GREEN in `loom-code/scripts/test_git_guard.py` +
   `test_loom_gate_markers.py`:
   - message-only amend passes gate with old marker (patch-id equal)
   - content change after verdict still blocks (patch-id differs)
   - rebase onto advanced main with unchanged branch diff passes
   - `cd /other/repo && git push` gates against /other/repo's markers
   - `validate` reports ALL schema violations in one run, exit 0 on clean
2. Full pytest for both files green
   (`PYTHONDONTWRITEBYTECODE=1 python -m pytest loom-code/scripts/ -k
   "git_guard or gate_markers"`).
3. Docs block lands (cut 4) and cites this plan.
4. 2×Sonnet panel review (G4 recipe) → union PASS; PR; no auto-merge.

## Tasks

1. RED: patch-id tests (markers write side + guard accept/reject side)
2. GREEN: markers `review-pass`/`verified` record base_sha+patch_id
3. GREEN: guard `_gate_push` patch-id fallback
4. RED→GREEN: cd-chain tracking in guard main loop
5. RED→GREEN: `validate` subcommand
6. Docs: marker-format spec block
7. Panel review → markers → push → PR
