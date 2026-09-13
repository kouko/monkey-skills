# W3-01 integration evidence

Date: 2026-09-13  
Scope: integration only; the complete package suite and Closing Review remain
reserved for the Review station.  
Overall verdict: **PASS after one release-test correction**

## Integrated measurements and verdicts

The counts below use the same `skill-refactor` package accounting recorded by
each isolated round, rather than `wc`'s different tokenization.

| Skill | Baseline `SKILL.md` | Final `SKILL.md` | Entrypoint reduction | Baseline package | Final package | Package reduction | Q1 | Q2 | Q3 |
|---|---:|---:|---:|---:|---:|---:|---|---|---|
| `write-plan` | 4,498 | 3,682 | 816 (18.14%) | 6,364 | 5,548 | 816 (12.82%) | PASS, 3/3 equivalent | PASS, >=10% | PASS |
| `capture-intent` | 3,553 | 2,930 | 623 (17.53%) | 4,822 | 4,199 | 623 (12.92%) | PASS, 3/3 equivalent | PASS, >=10% | PASS |
| `independent-advisor` | 4,035 | 1,946 | 2,089 (51.77%) | 7,620 | 5,531 | 2,089 (27.41%) | PASS, 3/3 equivalent | PASS, >=10% | PASS |
| **Total** | **12,086** | **8,558** | **3,528 (29.19%)** | **18,806** | **15,278** | **3,528 (18.76%)** | **PASS** | **PASS** | **PASS** |

Q1 is behavioral equivalence, Q2 is whole-package reduction, and Q3 is
invariant/capability quality. Every skill passed independently; no reduction
was borrowed across packages. Bundled references stayed byte-identical, so the
package reductions are deletion/compression, not relocation.

Claude Code was not used for baseline replay, judging, refactoring, or this
integration pass, per the user's constraint. All equivalence judgments in the
three refactor records came from independent Codex judges.

## Rejected write-plan move

The first `write-plan` candidate removed `## Station summary`. Although its
write-plan-only checks passed, the cross-plugin capture-intent contract found
that the table is a byte-identical cold-reader contract shared by both install
shapes. That candidate was rejected as a Q3 failure. The final candidate
restored the section and recovered the required reduction from non-contract
repetition instead.

## Release and marketplace state

| Plugin | Claude manifest | Codex manifest | Marketplace source |
|---|---:|---:|---|
| `loom-code` | 3.1.3 | 3.1.3 | `./loom-code/` |
| `loom-design` | 2.1.4 | 2.1.4 | `./loom-design/` |
| `loom-workflow` | 4.3.2 | 4.3.2 | `./loom-workflow/` |

The root marketplace schema has no per-entry `version` field; its three
entries already exist and point to the correct plugin roots. Version SSOT is
the plugin's `.claude-plugin/plugin.json`, mirrored into
`.codex-plugin/plugin.json`. No marketplace content change was required.

## Integration checks

The first integration pass ran the planned checks once. Every gate before the
focused suites passed. The focused suite then found one stale release assertion
in `loom-code/scripts/test_write_plan_station_text.py`: it still expected
`3.1.2` after the manifests and changelog advanced to `3.1.3`. The assertion
was corrected as W3 integration scope and the focused suite was rerun.

| Check | Result |
|---|---|
| `check-skill-structure.py` for loom-code, loom-design, loom-workflow | PASS: 5, 4, and 11 skills |
| `sync_codex_manifests.py --check` for all three plugins | PASS |
| `check_version_bump.py --base d5548b0d... --head HEAD` | PASS |
| marketplace description sync | PASS: 24 plugins |
| marketplace/plugin manifest focused tests | PASS: 12 tests |
| skill cross-references | PASS |
| plugin boundaries for all three plugins | PASS |
| isolated Loom install layout | PASS: 14 tests |
| focused skill contract suites, first pass | FAIL: 95 passed, 1 stale `3.1.2` assertion |
| focused skill contract suites, after correction | PASS: 96 tests |
| `git diff --check` after correction | PASS |

The complete repository/package suite was deliberately not run here; it remains
the Review/finalize-review responsibility.
