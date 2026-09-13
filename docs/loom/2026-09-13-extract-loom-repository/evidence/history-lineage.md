# Reviewed history boundary

Source: `6fc6fef8969f411f81e9cb566539d7068d379e10`, the fetched
`origin/main` selected for this change. Final eligibility is that primary
ancestry plus the minimum ancestry of five explicitly cited evidence snapshot
tips recorded in `scripts/loom-repository-bootstrap/docs/migration/auxiliary-history.json`.
Four tips are outside main ancestry; one is a primary-ancestry snapshot boundary
with no retained-path delta. Each tip must exist and be justified by a current
retained citation, then survive filtering under a local archive ref. Other
branch-only development commits, abandoned branches and GitHub PR discussion
are not claimed as migrated history. Final counts are in `verification.md`.

## Package lineage

| Current package | Reviewed predecessor | Evidence |
| --- | --- | --- |
| loom-code | code-toolkit | `016445aed` (#440) renames manifests, runtime, tests and docs; `557d6f04c` (#294) is the original creation commit, including new manifests and plugin files. |
| loom-design | loom-discovery, loom-interface-design, loom-pipeline, loom-product-principles, loom-spec | `e5b978e08` (#697) consolidates these roots using observable Git renames; conductor hooks also move to loom-code. |
| loom-design | spec-toolkit, interface-design-toolkit, product-principles-toolkit | `016445aed` (#440) renames these to loom-prefixed roots. Their creation commits are `ffd82717a` (#387), `d17073a50` (#399), `98805236a` (#398). |
| loom-design | loom-discovery, loom-pipeline creation | `4cf04014c` (#523) and `b8df2cb03` (#479) create these new plugins. |
| loom-workflow | dev-workflow | `d1905e32f` (#730) renames manifests, skills and tests. First path commit `d1f414bb6` creates dev-workflow files; `7ac2ec278` later adds its plugin manifest. |
| loom-workflow | loom-memory | `1b534ccdc` (#822) renames the standalone plugin's skill, scripts and tests into loom-workflow. `41e02f50b` (#821) creates the standalone plugin. |

The allowlist retains whole historical package roots, including subsequently
retired package content, so their internal history is not selected by current
filenames alone. Historical roots are absent from the candidate's current tree.
The `docs/code-toolkit/` predecessor archive and the three renamed CI workflow
files are included explicitly. Broad `docs/loom/` and `docs/superpowers/` imports
are rejected: the latter demonstrably contains investing-toolkit records.
Code-toolkit's initial commit describes copied domain-teams knowledge; that is
an imported-content boundary, not an earlier package rename. Domain-teams is
not imported wholesale.

## Extraction proof and pruning rule

The inventory records every source-reachable commit and selects a commit when
its diff against any parent (or the empty tree for roots) touches an explicit
allowlisted path. A fresh clone is pinned to the full source SHA and all other
refs/remotes are removed there. No source ref or configuration is changed.

Default filter-repo pruning failed on real merge `9de458125` (#64): it dropped a
commit touching retained LICENSE relative to one parent, even with degenerate
merge pruning disabled. The implementation therefore disables automatic empty
pruning and uses a callback that skips **only** original commit IDs outside the
independently computed touching population, except for the five explicitly cited
snapshot tips identified during W3. Those tips remain even when their own delta
does not touch retained paths, because their selected tree is the evidence.
Every retained commit must map to
a nonzero SHA, match its selected original file tree (paths, blob IDs and modes),
and preserve author/committer identity, dates and message. A retained commit
that fails any check stops the extraction.

Filter-repo omits callback-skipped IDs from its own map. The original output is
preserved verbatim; the complete map adds zero rows only for independently
classified unrelated IDs. The complete population is checked for omissions,
duplicates and malformed IDs. The generated provenance commit is separate from
rewritten history.

TDD: the W2 tests first failed with missing extraction/snapshot entry points
(3 failures, 21 passing). Bootstrap README coverage also failed before copying
templates was implemented. Integration tests use real fresh Git repositories
and filter-repo, prove unrelated-only commits are pruned and retained merges
survive, and check blame, metadata, source state, destination isolation and no
remote. `python3 -m pytest scripts/test_extract_loom_repository.py -q` passed
25 tests before the full-history run.

Intermediate W2 run (superseded by W3's expanded proof): 1,709
source commits in the complete map; 479 retained commits verified; 321 mixed
commits; 481 current retained files. Filtered head:
`c753c1c464e610628775e7ea228ea53e8a5ade93`. Complete map SHA-256:
`cecf7eb82b799dd8342024d9929711e3f5ce0506782ba538fc343084b478c479`.
The intermediate source snapshot was unchanged and the candidate had no remotes.
Git-filter-repo version: `a40bce548d2c`. This proves history extraction;
the independent development/package gates remain W3 work.

A subsequent real shallow-clone regression initially failed because extraction
accepted incomplete ancestry. Extraction now rejects shallow sources before
creating a destination. The real source was independently checked as nonshallow.
