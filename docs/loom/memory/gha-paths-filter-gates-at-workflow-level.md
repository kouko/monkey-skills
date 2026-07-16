---
name: gha-paths-filter-gates-at-workflow-level
description: GitHub Actions `paths:` filters gate at the `on:`/workflow-trigger level, never per-job — a job that must see EVERY push to a branch (post-merge verifiers, repo-wide sweeps) cannot live inside a path-filtered workflow file; give it its own unfiltered workflow
type: gotcha
origin: PR feat/loom-memory-hardening-o4-o2-o3-o5-o6 Task 6 (2026-07-17)
---

While adding the post-merge memory-trailer verifier, the plan said "add a
second job to dev-workflow-ci.yml" — but that workflow's `on:` block carries
`paths: dev-workflow/**` filters. A memory-worthy PR usually touches OTHER
paths, so the new job would silently never fire on exactly the pushes it
exists to catch. GitHub Actions evaluates `paths:`/`paths-ignore:` when
deciding whether to trigger the WORKFLOW; there is no per-job path filter at
trigger time.

**Why:** the failure is silent — the job shows green history on the pushes
that did trigger it, and nobody notices the pushes where the workflow never
ran at all. Scope filters and must-see-everything jobs cannot share one
workflow file.

**How to apply:** when a job must run on every push to a branch (post-merge
verification, security sweeps), ship it as its own workflow file with an
unfiltered `push: branches: [...]` trigger, and keep path-scoped test jobs in
their own filtered workflow. Check the `on:` block's `paths:` before adding
any job to an existing workflow; document the file split's reason in the
workflow header (live example: `.github/workflows/memory-verify-merged.yml`).
