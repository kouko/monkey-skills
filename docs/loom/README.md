# docs/loom/ — loom family working directory

Live directory map for loom-* planning, memory, and verification
artifacts. One line per entry; each folder/file is its own source of
truth.

## What's here

| Entry | Content |
|---|---|
| [`backlog/`](backlog/) | Open items SSOT — cross-plugin debts, parked decisions, re-triggers; one entry per file, format contract in [`backlog/README.md`](backlog/README.md) |
| [`BACKLOG.md`](BACKLOG.md) | **Generated** index over `backlog/` — never hand-edit it; run `python3 scripts/backlog_index.py --write` (repo-root first, else the loom-code plugin copy) |
| [`DIRECTION.md`](DIRECTION.md) | Direction layer — human `## Next`/`## Later`; `## Now` generated — never hand-edit; regen via `python3 scripts/backlog_index.py --direction-write docs/loom/DIRECTION.md` (same two-tier resolution) |
| [`memory/`](memory/) | Practice-memory store — repo-native home for distilled loom-* practices, habits, processes, and recurring gotchas (one fact per file) |
| [`discovery/`](discovery/) | Problem-space artifacts per run: `user-insights.md` + evidence + research reports; `business-value.md` when the worth-it check fires — see the loom-design discovery station |
| [`specs/`](specs/) | Brainstorming briefs (5-axis output) |
| [`plans/`](plans/) | Writing-plans output (atomic task lists) |
| [`audits/`](audits/) | Audit reports and changesets |
| [`dogfood/`](dogfood/) | Dogfood-run records |
| [`research/`](research/) | Research notes backing loom design decisions |
| [`design/`](design/) | Design documents |
| [`firing-corpus/`](firing-corpus/) | Skill firing-test corpus |
| [`INDEX.md`](INDEX.md) | Living-spec index |
| [`codex-verification.md`](codex-verification.md) | Codex host verification notes |

## History

This directory began as a **frozen pre-OpenSpec archive**
(2026-05-30): code-toolkit (since renamed to [loom-code](../../loom-code/)) brainstorming briefs
and writing-plans output from 2026-05-18 ~ 2026-05-27, before
code-toolkit adopted OpenSpec as its specification layer (see the
[OpenSpec integration brief](specs/2026-05-30-openspec-integration-brief.md)).
Per [OpenSpec brownfield-first philosophy](https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md#brownfield-first),
those historical proposals were frozen rather than back-converted into
OpenSpec format (integration brief Q3 = C1) — kept for git-history
searchability (`git log --grep` / `grep -rn` against historical
decision context). The directory has since gone live again as the loom
family's working directory; the pre-2026-05-30 files in `specs/` and
`plans/` remain unmaintained archive content.
