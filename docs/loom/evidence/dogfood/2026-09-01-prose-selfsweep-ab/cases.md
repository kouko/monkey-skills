# A/B case manifest — prose-edit self-sweep

Date: 2026-09-01 · 4 historical prose-task cases (2 kumiko-zaiku-app-icons,
2 monkey-skills), each an already-merged, real prose-consistency fix mined
from git history — reused here as an A/B dispatch input, not re-litigated.
Substitution rule (brief): if a case's pre-state cannot be reconstructed
cleanly, substitute a same-project case and record the substitution here.
No substitution was needed for any of the 4 cases below.

All 4 pre-state shas verified via `git cat-file -e <sha>` in their owning
repo (see per-case "Verified" line).

## Case 1 — kumiko: flat-render cause correction

- **Source project / branch**: kumiko-zaiku-app-icons, `main`, commit
  `20a67d43d5c57db251e09b9949b328d3d7970f89`
  ("docs(loom): 平圖成因在它的出生地就地更正，原句保留").
- **Pre-state sha**: `3c98e953a9a1b3e34021226ba0bcc7b87040c6a9`
  (`20a67d4~1`). **Verified**: `git -C <kumiko repo> cat-file -e
  3c98e953a9a1b3e34021226ba0bcc7b87040c6a9` → exit 0.
- **Reconstructed task text**: "`decisions.md`'s 2026-08-10 entry
  ‘第一張渲染圖是平的' states a false cause (main light already tilted at
  render time) for a rejected diagnosis. The true cause is that the camera
  was orthographic at the time, so vertical side-wall projection width was
  exactly zero — no amount of relighting could have fixed it. Correct this
  in place at its origin (both the heading's second half and the body
  paragraph), preserving the original sentence, per this repo's
  correct-in-place convention (see the 2026-08-01 precedent in the same
  file). Do not claim the tilted-light premise was true at the time."
- **Files the task edits**: `docs/loom/decisions.md` (single file).

## Case 2 — kumiko: three-statement supersession annotation

- **Source project / branch**: kumiko-zaiku-app-icons, `main`, commit
  `33eccfd36150364c12f1db003d7597b4a44a7fae` ("docs(loom): 就地加註舊
  brief 與出貨狀態註被本 arc 推翻的三處敘述").
- **Pre-state sha**: `5a80b6efe7bc4a31daefcf596253d285bf7548e8`
  (`33eccfd~1`). **Verified**: `git -C <kumiko repo> cat-file -e
  5a80b6efe7bc4a31daefcf596253d285bf7548e8` → exit 0.
- **Reconstructed task text**: "Three prior statements across two spec
  files and one backlog entry were superseded by this arc's final render
  geometry and need in-place annotation (original sentences preserved):
  (1) the 08-17 spec's Alternatives §3 perspective-plus-elevation binding;
  (2) the 08-14 spec's three occurrences of the 8.91 view-width figure,
  which only holds on the z=0 panel plane under perspective (it is 8.71 at
  the window-paper's z=0.18975), plus two same-claim restatements and one
  Proposal-section phrase in the same file; (3) the backlog's T6/T7
  shipped-state note's camera half (the light-tilt half stays, dated
  correctly). Do not annotate the 08-14 spec's line 18 — it describes that
  spec's own camera at authoring time and is not superseded."
- **Files the task edits**:
  `docs/loom/specs/2026-08-17-window-depth-and-inside-paper.md`,
  `docs/loom/specs/2026-08-14-render-look-and-paper-backing.md`,
  `docs/loom/backlog/m1-part-4-blender-render.md`.

## Case 3 — monkey-skills: living-spec scope correction

- **Source project / branch**: monkey-skills, commit
  `89c1a7b42b6999a79338b8f179668316112ea0a1` ("docs(loom): correct Task 2
  living-spec scope").
- **Pre-state sha**: `5ec6ef4cc7c232cdb9a843da184e1d1c02493e82`
  (`89c1a7b4~1`). **Verified**: `git cat-file -e
  5ec6ef4cc7c232cdb9a843da184e1d1c02493e82` (run in this repo) → exit 0.
- **Reconstructed task text**: "Task 2 in this plan declares a review
  scope that omits the generated living-spec index required by REQ-99's
  new test, so the declared scope doesn't match the task's actual
  merge-boundary gate. Include the generated living-spec index in Task 2's
  declared review scope so the two agree."
- **Files the task edits**:
  `docs/loom/plans/2026-08-31-docs-review-baseline.md` (single file).

## Case 4 — monkey-skills: decision-map T1 round-2 fixes

- **Source project / branch**: monkey-skills, `loom-workflow`
  decision-map arc, commit `8f02ae005d0ac7e2d94eeb6e19e093cb6cd79933`
  ("docs(loom-workflow): T1 fixes — acyclicity enforcement disclosure,
  ratification x stale-claim").
- **Pre-state sha**: `0e7079ce23ae58ea888b88eeefe14011ad45b332`
  (`8f02ae00~1`). **Verified**: `git cat-file -e
  0e7079ce23ae58ea888b88eeefe14011ad45b332` (run in this repo) → exit 0.
- **Reconstructed task text**: "docs-review round 1 found two defects in
  the map-format reference: (1) the dangling/cycle checks are described
  without naming that they are machine-gated by `map_store.py`'s
  `validate`, reading as a manual or prose-only check; (2) the
  ratification section doesn't say whether a `pending` ratification
  survives a stale-claim reclaim — it should, because ratification tracks
  measurement state, not claimant state. Fix both in place."
- **Files the task edits**:
  `loom-workflow/skills/decision-map/references/map-format.md` (single
  file).

## Substitutions

None. All 4 cases above reconstructed cleanly from their source repos'
git history on the first attempt.
