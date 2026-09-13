# W1-01 write-plan refactor evidence

Date: 2026-09-13  
Mode: `skill-refactor` package-resource mode  
Final verdict: **PROCEED**

## Frozen baseline

- Revision: `d5548b0d10f15769093c5aa18336395cef0cbaac`
- Canonical manifest: `/Users/kouko/.codex/baselines/2026-09-13-shrink-three-loom-skill-entrypoints/write-plan/baseline/manifest.json`
- External manifest SHA-256: `3640966106aca26f5a10075cf25374b216ec466cd9211e06eab40d145e2e6101`
- `package_gate.py verify`: PASS before each candidate comparison.
- `test-prompts.json` was created after the pinned export and is included in
  the corrected cumulative candidate package total.

## Rejected first candidate

The first isolated candidate removed `## Station summary` and initially passed
the write-plan-only checks. Integration then ran
`loom-design/scripts/spec/test_capture_intent_contract.py`, which requires that
section to remain byte-identical between `capture-intent` and `write-plan` so a
cold reader sees the same whole-flow table in either install shape. That was a
Q3 capability-quality failure. The earlier PROCEED was invalidated; the first
candidate was not retained as the final implementation.

## Final refactor

The final candidate was recreated from the frozen Git export. It preserves
`## Station summary` byte-for-byte and instead deletes the second, expanded
whole-station-order table. It also compresses the user-question overview,
removes illustrative implementation-choice rows whose governing rule remains,
and tightens repeated spec/task-shape prose. Only `SKILL.md` changed; references
and dependencies did not. All decision, refusal, confirmation,
conservative-default, product-behavior, and handoff duties remain in the
entrypoint.

## Q1 — behavioral equivalence

Baseline and final candidate were replayed against all three confirmed prompts:
normal engineering planning, refusal of an unconfirmed intent, and missing
product-spec handoff. `equivalence_check.py` returned `PASS_LAYER_1` for output
type, headings, paths, tool sequence, and output size. Three independent Codex
judges used boundary, utility, and completeness framings with alternating A/B
labels; all returned `equivalent`. No judge found a missing decision, refusal,
plan requirement, or handoff.

Verdict: **PASS (3/3 equivalent, high confidence)**.

## Q2 — whole-package reduction

| Measure | Baseline | Final candidate | Reduction |
|---|---:|---:|---:|
| `SKILL.md` words | 4,498 | 3,513 | 985 (21.90%) |
| `SKILL.md` bytes | 29,872 | 24,086 | 5,786 (19.37%) |
| Package words | 6,364 | 5,618 | 746 (11.72%) |
| Package bytes | 42,124 | 38,324 | 3,800 (9.02%) |

The corrected package, including `test-prompts.json`, is below the
at-most-5,727-word target. References are
unchanged, so the reduction is deletion/compression rather than relocation.

Verdict: **PASS (whole package reduced by at least 10%)**.

## Q3 — invariants and capability quality

- Frontmatter `name: write-plan` and `version: 1.0.1` are unchanged.
- All three bundled references are byte-identical to the frozen baseline.
- Checker, template, policy, and reference dependencies remain declared.
- Decision boundary; Steps 4-6; confirmed-intent, confirmed-behavior, and
  post-decision conservative-default gates remain.
- `## Station summary` is byte-identical to both the frozen write-plan baseline
  and the current capture-intent section.
- The cross-plugin capture-intent contract passes.

Verdict: **PASS**.

## Reducer and focused verification

`package_gate.py reduce` returned `PASS` for resource, owning-skill, package,
and Codex host evidence. Claude Code was not used.

```text
python3 -m pytest <write-plan focused tests> \
  loom-design/scripts/spec/test_capture_intent_contract.py -q
80 passed

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
