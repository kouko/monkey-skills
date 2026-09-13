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
| `write-plan` | 4,498 | 3,513 | 985 (21.90%) | 6,364 | 5,618 | 746 (11.72%) | PASS, 3/3 equivalent + bounded review verification | PASS, >=10% | PASS |
| `capture-intent` | 3,553 | 2,695 | 858 (24.15%) | 4,822 | 4,251 | 571 (11.84%) | PASS, 3/3 equivalent + bounded review verification | PASS, >=10% | PASS |
| `independent-advisor` | 4,035 | 1,924 | 2,111 (52.32%) | 7,620 | 6,781 | 839 (11.01%) | PASS, 3/3 equivalent + Round 2 verification | PASS, >=10% | PASS |
| **Total** | **12,086** | **8,132** | **3,954 (32.72%)** | **18,806** | **16,650** | **2,156 (11.46%)** | **PASS** | **PASS** | **PASS** |

Q1 is behavioral equivalence, Q2 is whole-package reduction, and Q3 is
invariant/capability quality. Every skill passed independently; no reduction
was borrowed across packages. Package totals include the shipped
`test-prompts.json` files. Bundled references stayed byte-identical, so the
remaining reductions are deletion/compression, not relocation.

Round 1 Closing Review found that the earlier accounting excluded those prompt
fixtures. The skills were reduced further, all three focused contract suites
were rerun, and the same reviewers verified the functional fix delta.
It also restored `independent-advisor`'s rule that a missing template field is
not blindly retried, with a focused regression assertion.
Finalization then exposed exact cross-package prose pins absent from focused
coverage; the final digest restores only those carriers and keeps every package
above the independent 10% word-reduction threshold.

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
| `loom-code` | 3.1.4 | 3.1.4 | `./loom-code/` |
| `loom-design` | 2.1.5 | 2.1.5 | `./loom-design/` |
| `loom-workflow` | 4.3.3 | 4.3.3 | `./loom-workflow/` |

The root marketplace schema has no per-entry `version` field; its three
entries already exist and point to the correct plugin roots. Version SSOT is
the plugin's `.claude-plugin/plugin.json`, mirrored into
`.codex-plugin/plugin.json`. No marketplace content change was required.

## Integration checks

The first integration pass ran the planned checks once. Every gate before the
focused suites passed. The focused suite then found one stale release assertion
in `loom-code/scripts/test_write_plan_station_text.py`: it still expected
`3.1.2` after the manifests and changelog advanced. The assertion
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
