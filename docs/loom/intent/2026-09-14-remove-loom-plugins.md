# Remove Loom plugins from monkey-skills
originator: kouko
kind: product
needs-design: yes — the published plugin marketplace and installation surface changes
evidence: [README.md, .claude-plugin/marketplace.json, docs/loom/]
status: confirmed 2026-09-14
publication: automatic — authorized 2026-09-14 by kouko
lane: gate-only — declared 2026-09-14 by kouko

## Problem
People installing skills from monkey-skills can encounter Loom plugins that are
now maintained and published elsewhere, creating duplicate or stale choices.

## Proposed outcome
When people use monkey-skills, they see only the remaining plugins; Loom users
can find the independent repository, while historical records remain available.

## Acceptance
1. The marketplace and repository layout no longer offer Loom plugins.
2. Loom-only CI, hooks, runners, extraction tooling, and tests are absent.
3. Existing non-Loom plugins retain passing repository checks and valid
   marketplace metadata.
4. Historical Loom records remain available for reference; only the active
   package-test default is updated to remove a deleted runner.

## Constraints
- Preserve the independent `kouko/loom-plugins` repository and its history.
- Do not delete or rewrite historical records under `docs/loom/`, except the
  active package-test default needed to remove the deleted runner.
- Do not merge or publish the branch without the user's separate merge decision.

## Out of scope
- Antigravity compatibility work in `loom-plugins`.
- Changes to the independent Loom repository.
- Redesigning non-Loom plugin behavior.

## Open questions
- none
