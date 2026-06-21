# docs/loom/ — Pre-OpenSpec Archive

**Status**: Frozen as historical archive (2026-05-30).

This directory holds [code-toolkit](../../code-toolkit/) brainstorming briefs and writing-plans output from **2026-05-18 ~ 2026-05-27**, before code-toolkit adopted OpenSpec as its specification layer.

## Where new work goes

New code-toolkit changes are tracked in `openspec/changes/<change-id>/` (proposal + design + tasks + delta specs), per the OpenSpec integration brief at [specs/2026-05-30-openspec-integration-brief.md](specs/2026-05-30-openspec-integration-brief.md).

## What's here

| Folder | Content | Format |
|---|---|---|
| [`specs/`](specs/) | Brainstorming briefs (5-axis output) | Free-form Markdown |
| [`plans/`](plans/) | Writing-plans output (atomic task lists) | Free-form Markdown |

Files are kept for git-history searchability (`git log --grep` / `grep -rn` against historical decision context). They are **not maintained** and are not consumed by any active skill or workflow.

## Why frozen, not migrated

Per [OpenSpec brownfield-first philosophy](https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md#brownfield-first), the baseline `openspec/specs/` files (as they are after migration) become the new source of truth. Historical proposals do not need to be back-converted into OpenSpec format. The integration brief documents this decision (Q3 = C1).
