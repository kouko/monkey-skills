# W1-03 independent-advisor refactor evidence

Date: 2026-09-13  
Mode: `skill-refactor` package-resource mode  
Overall verdict: **PROCEED**

## Frozen baseline

- Revision: `d5548b0d10f15769093c5aa18336395cef0cbaac`
- Canonical manifest: `/Users/kouko/.codex/baselines/2026-09-13-shrink-three-loom-skill-entrypoints/independent-advisor/baseline/manifest.json`
- External manifest SHA-256: `313a90b9aff9af452cef011f9573274b7b14af561e6bc8a58a2acbb05d974663`
- `package_gate.py verify`: PASS before candidate comparison.
- Candidate: `/Users/kouko/.codex/candidates/2026-09-13-shrink-three-loom-skill-entrypoints/independent-advisor/package`.

The candidate was applied only after Q1-Q3 and the layered reducer passed.
`test-prompts.json` is the confirmed W0 evaluation input and remains outside
both package totals.

## Refactor

Only `SKILL.md` changed. The round deleted repeated explanation and worked
wording already carried by the executor-detection, dispatch-protocol, and
report-contract references, then compressed the remaining orchestration prose.
All bundled resources are byte-identical to the frozen baseline, so the package
reduction is deletion and compression, not relocation.

Privacy and egress disclosure, complete approval, executor exclusion, live
probe, frontier fail-loud, proposer blindness, two independent bias controls,
and report honesty duties remain visible in the entrypoint. The exact-phrase
contract suite also keeps every externally observed carrier explicit.

## Q1 — behavioral equivalence

The frozen baseline and final isolated candidate were replayed through all three
confirmed prompts before application:

1. explore mode with an independent proposer and counterbalanced blind judging;
2. refusal when no eligible different-family executor is runnable; and
3. audit mode with cost-only partial approval and a frontier fail-loud boundary.

`equivalence_check.py` returned `PASS_LAYER_1`: output type, headings, paths,
tool sequence, and word-count tolerance passed. The normalized baseline output
was 190 words and the candidate output 189 words (0.5% difference).

Three independent Codex judges used utility, information-completeness, and
boundary framings with alternating A/B labels. All nine prompt-level verdicts
were `equivalent`; no judge found a load-bearing difference in decisions,
refusals, approvals, privacy warnings, blindness controls, or report duties.
Claude Code was not used, per the user's instruction.

Verdict: **PASS (3/3 equivalent, high confidence)**.

## Q2 — whole-package reduction

| Measure | Baseline | Candidate | Reduction |
|---|---:|---:|---:|
| `SKILL.md` words | 4,035 | 1,946 | 2,089 (51.77%) |
| `SKILL.md` bytes | 24,828 | 13,227 | 11,601 (46.73%) |
| Package words | 7,620 | 5,531 | 2,089 (27.41%) |
| Package bytes | 54,806 | 43,205 | 11,601 (21.17%) |

The package is below the at-most-6,858-word target.

Verdict: **PASS (whole package reduced by at least 10%)**.

## Q3 — invariants

- Frontmatter `name: independent-advisor` and `version: 0.1.0` are unchanged.
- The three references, three localized READMEs, and owning README test are
  byte-identical to the frozen baseline; no dependency or package file changed.
- Mode routing still uses a verbatim citable basis and preserves conflicts and
  overrides.
- Static detection still excludes four distinguishable failures and refuses a
  same-controller or same-family substitute.
- The one checkpoint still binds leg assignments, cost, egress, readable scope,
  local repository setup, and audit retention before any probe or dispatch.
- The live probe remains read-only, verifies both model and effort, and makes a
  frontier mismatch fail loud without an implicit downgrade.
- Explore mode retains an incumbent-free proposer, fidelity-only normalizer,
  distinct judge, anonymisation, opposite-order fresh processes, and the
  inconclusive and post-normalisation early-stop rules.
- Reports retain distinct failure attribution, untrusted-source marking,
  coverage and blindness qualifications, actual cost, and no completeness claim.

Verdict: **PASS**.

## Layered reducer and focused checks

`package_gate.py reduce` returned `PASS` for resource, owning-skill, package,
and three Codex host evidence records. Claude Code was not used.

Commands and results:

```text
python3 -m pytest loom-workflow/scripts/test_independent_advisor_compaction.py loom-workflow/scripts/test_independent_advisor_plugin_readmes.py loom-workflow/skills/independent-advisor/scripts/test_independent_advisor_readmes.py -q
11 passed

python3 scripts/check-skill-structure.py loom-workflow
All 11 skills PASS

python3 scripts/check_plugin_boundaries.py loom-workflow
OK

python3 -m pytest scripts/test_loom_plugin_install_layout.py -q
14 passed

git diff --check
PASS
```
