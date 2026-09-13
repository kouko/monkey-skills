# W1-01 write-plan refactor evidence

Date: 2026-09-13  
Mode: `skill-refactor` package-resource mode  
Overall verdict: **PROCEED**

## Frozen baseline

- Revision: `d5548b0d10f15769093c5aa18336395cef0cbaac`
- Canonical manifest: `/Users/kouko/.codex/baselines/2026-09-13-shrink-three-loom-skill-entrypoints/write-plan/baseline/manifest.json`
- External manifest SHA-256: `3640966106aca26f5a10075cf25374b216ec466cd9211e06eab40d145e2e6101`
- `package_gate.py verify`: PASS before candidate comparison.
- Candidate was edited under `/Users/kouko/.codex/candidates/2026-09-13-shrink-three-loom-skill-entrypoints/write-plan/package` and applied to the worktree only after Q1-Q3 passed.

`test-prompts.json` is the W0 evaluation input created after the pinned export;
as declared in `baseline.md`, it is outside both baseline and candidate package
totals. Accounting therefore uses the isolated Git-exported package, not the
worktree directory that also contains this evaluation input.

## Refactor

The round changed only `SKILL.md`; no bundled reference content or dependency
changed. It deleted the duplicate station-summary table, compressed the
user-question overview, removed three illustrative implementation-choice rows
whose governing rule remains, and tightened repeated spec/task-shape prose.
Every decision, refusal, conservative-default, confirmation, product-behavior,
and handoff obligation remains in the entrypoint.

## Q1 — behavioral equivalence

The current and candidate packages were replayed through all three confirmed
prompts before the candidate was applied:

1. confirmed engineering intent and normal plan production;
2. refusal to plan an unconfirmed intent;
3. missing product spec handoff to `loom-design:write-spec`.

Normalized captures are outside the repository under the candidate workspace.
`equivalence_check.py` reported `PASS_LAYER_1`: output type, headings, paths,
tool sequence, and word-count tolerance all passed. Three independent Codex
judges used utility, information-completeness, and boundary framings with
alternating A/B labels; all three returned `equivalent`. No judge identified a
missing decision, refusal, or handoff behavior.

Verdict: **PASS (3/3 equivalent, high confidence)**.

## Q2 — whole-package reduction

| Measure | Baseline | Candidate | Reduction |
|---|---:|---:|---:|
| `SKILL.md` words | 4,498 | 3,737 | 761 (16.92%) |
| `SKILL.md` bytes | 29,872 | 25,298 | 4,574 (15.31%) |
| Package words | 6,364 | 5,603 | 761 (11.96%) |
| Package bytes | 42,124 | 37,550 | 4,574 (10.86%) |

The package result is below the at-most-5,727-word target. Because references
were unchanged, all reduction is deletion or compression rather than prose
relocation.

Verdict: **PASS (whole package reduced by at least 10%)**.

## Q3 — invariants

- Frontmatter `name: write-plan` and `version: 1.0.1` are unchanged.
- The three reference files are byte-identical to the frozen baseline.
- Declared checker, template, second-vendor policy, and reference dependencies
  remain present.
- Required anchors remain: Decision boundary, both intake gates, Steps 4-6,
  and the post-decision conservative-default gate.
- The required phrase that reviewer count comes from the installed Review
  policy remains in the station-order table.

Verdict: **PASS**.

## Layered reducer and focused checks

`package_gate.py reduce` returned `PASS` for resource, owning-skill, package,
and the permitted Codex host replay. Claude Code was not used, per the user's
instruction.

Commands and results:

```text
python3 -m pytest loom-code/scripts/test_write_plan_shape_text.py loom-code/scripts/test_write_plan_station_text.py loom-code/scripts/test_simplified_station_text.py loom-code/scripts/test_codex_hook_trust_contract.py -q
47 passed

python3 scripts/check-skill-structure.py loom-code
All 5 skills PASS

python3 loom-code/scripts/check-skill-crossrefs.py
OK

python3 scripts/check_plugin_boundaries.py loom-code
OK

python3 -m pytest scripts/test_loom_plugin_install_layout.py -q
14 passed

git diff --check
PASS
```

An initial isolated test run exposed that deleting the duplicate summary also
removed the pinned reviewer-policy phrase. The candidate was corrected before
the gate verdict; the repeated focused run then passed 47/47 tests.
