---
name: migration-acceptance-greps-scope-by-content-not-filetype
description: A migration task's acceptance grep scoped by file type (SKILL.md/README only) leaves .py/.yml/schema-doc consumers of the migrated names unscanned — sweep by content pattern repo-wide and justify carve-outs, or the blind spot ships
type: process
origin: PR (data-markets consolidation, branch finacial-analytics-r2, 2026-07-11)
---

During the data-markets consolidation, the doc-migration task's GREEN
criterion was `grep "data-{country}" skills/*/SKILL.md README*.md` — it
passed while three live consumers of the old names stayed broken/stale:
a weekly-cron build script (`etf_aggregator.py`, hardcoded deleted
paths), a REQUIRED CI workflow (`check-script-sync.yml`, diffing deleted
dirs), and five schema-overview docs (broken links + deleted-path
invocation examples). Each was caught only later — two by per-task
quality reviewers reading beyond their file lists, one by whole-branch
review.

**Why:** file-type-scoped acceptance greps encode an assumption about
where references live; renames/deletions have consumers in code, CI
config, and secondary docs that the assumption silently excludes. The
suite stays green because tests mock exactly the seams that broke.

**How to apply:** when a task renames or deletes a path/name, write the
acceptance grep over the whole repo by content pattern (no --include
file-type filter), then justify every residual hit as an explicit
carve-out (historical records: ADRs, CHANGELOG, provenance docs,
captured fixtures). Add a path-existence test for any script that
subprocess-invokes a sibling by constructed path.
