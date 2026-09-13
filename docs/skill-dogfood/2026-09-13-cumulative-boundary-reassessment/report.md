# Cumulative boundary reassessment — negative result

## Status

`NOT_ADMITTED` — the candidate made the intended L1 decision, but the frozen
bar requires two auditors to agree that the baseline missed it. One auditor
graded both L1 arms correct; the other graded the baseline insufficient. The
candidate also loaded its detailed reference in all four cases, and the two
auditors disagreed on whether its L4 command record proved the three-diff cap.

The runtime contract therefore has no behavioral admission. W2-02 restored
the baseline contract byte for byte, removed the candidate-only reference and
focused contract test, and retained this negative evidence. Package manifests
and the changelog remain unchanged because the candidate was not admitted.
The rejected candidate is the exact commit
`e2161e2fe6b3bf40d33b8a0c45cb035f77d2d73c`; all candidate byte, hash, and
path claims below are recomputed from that Git object rather than accepted from
this report.

## W2-02 disposition

- Restored `loom-code/skills/write-plan/SKILL.md` to SHA-256
  `e4c249bae4a5badbd15c258fbfe6d4d2d920e9eba58329fa2ee05bfe573c0da4`,
  matching the frozen baseline revision.
- Removed the unadmitted
  `loom-code/skills/write-plan/references/cumulative-boundary-reassessment.md`
  and `loom-code/scripts/test_cumulative_boundary_contract.py` runtime
  candidate paths.
- Preserved the frozen cases, admission probe, and normalized evidence. The
  full probe passes only when it observes the exact six frozen non-admission
  reasons; it does not deselect or weaken the admission oracle.

The exact expected reasons are:

1. `status is not ADMITTED`
2. `L4 candidate does not meet the frozen rubric`
3. `L1 baseline does not meet the frozen non-tie requirement`
4. `conditional reference loading does not match the challenge corpus`
5. `baseline cost evidence is missing`
6. `candidate cost evidence is missing`

## Identities and execution

| Item | Observed identity |
|---|---|
| Baseline revision | `1973ff35c4919e4c40795808240249c7ee40f506` |
| Candidate revision | `e2161e2fe6b3bf40d33b8a0c45cb035f77d2d73c` |
| Fixture specification | `a9c3448869bc73985b3219ffeeb53770beb16c09134c888489639caf1a0b1723` |
| Frozen rubric | `ea89194e8d5673e3eba94b016318ba4e76d1da8d4893947a3d517658b1256594` |
| Baseline Write Plan | `e4c249bae4a5badbd15c258fbfe6d4d2d920e9eba58329fa2ee05bfe573c0da4` |
| Candidate Write Plan | `edeb377b3fe4b1a3d5d776dbfde5d4631fd52a03e46fc7d3bd8ae0d9b90e49d0` |
| Candidate reference | `0c6f5465cd0765efb6eb82b6a2dffef5d86fb2120af43e173541006c8b2a93b2` |
| Normalizer | `de640cfa9cb5a9e898dc26fdecef386f0e63987733be01da5e5f4cc3eae18735` |

The candidate commit contains a 30,427-byte Write Plan contract and a
2,601-byte detailed reference. Its complete committed path delta is the two
contract paths above plus
`loom-code/scripts/test_cumulative_boundary_contract.py`. The admission probe
recomputes those bytes, SHA-256 values, and paths with `git rev-parse
--verify`, `git show`, and `git diff-tree --no-commit-id --name-only -r`.

The normalized public evidence is bound to committed carriers, not current
working-tree copies:

| Carrier | Revision | Git blob |
|---|---|---|
| Frozen cases | `4864ea08d96824f74a9b824f39ded1e27b910fd9` | `e97ac10e201da9abd2885e3b6a548effb223eeff` |
| Frozen admission probe | `4864ea08d96824f74a9b824f39ded1e27b910fd9` | `ab40c5061e070d19cad2f3d106d1b4de7c308a42` |
| Normalized runner/auditor report | `d7e72bb348b8e0092c611992f1bee140ed2f2a6e` | `29d9be0261ccc4f9d65fba22ddd0d9cdd2c4febf` |

### Git replay assumptions

The replay harness requires Git 2.32 or newer and assumes the documented
porcelain/plumbing behavior of that release. Git 2.32 documents
`--initial-branch`, `--object-format`, and `--template` for `git init`, and the
revision/path selectors used by `rev-parse`, `show`, and `diff-tree`.[^git-init]
[^git-revisions] [^git-show] [^git-diff-tree]

Every Git subprocess clears inherited repository pointers, alternate object
stores, template selection, `GIT_CONFIG_PARAMETERS`, and every numbered
`GIT_CONFIG_KEY_*` / `GIT_CONFIG_VALUE_*` pair. It sets
`GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_SYSTEM=/dev/null`,
`GIT_CONFIG_NOSYSTEM=1`, and `GIT_CONFIG_COUNT=0`; fixture commands also use an
empty template directory, an empty `core.hooksPath`, and
`git commit --no-gpg-sign --no-verify`. These are the documented controls for
global/system configuration, environment-injected configuration, templates,
hooks, configured signing, and commit hooks.[^git-config] [^git-commit]

- Eight fresh Codex runners used `gpt-5.6-sol` at `medium` effort: one
  baseline and one candidate run for each frozen fixture. The only assigned
  resource difference was the Write Plan contract bundle.
- Two fresh Codex blind auditors used `gpt-6-astra` at `medium` effort. They
  saw neutral arms, fixture identities, requests, and the frozen rubric, but
  not arm mappings, contracts, each other, or raw runner streams.
- Raw operational streams and agent identifiers remain private. The table
  below retains normalized decisions, decisive evidence, task order, limits,
  costs, and content hashes.

## Normalized runner results

| Case | Arm | SHA-256 | Decision and decisive evidence | Ordered work | Reference | Elapsed |
|---|---|---|---|---|---|---:|
| L1 | A | `c0985cb59d718c8a083cf1dc3a58ff0cfa89bd9307cc3719442e44d00e2c8739` | Extract: `pricing.quote`, `checkout.checkout`, and pricing tests all acquired caller-owned audit state in `45a097b`. | Restore pure pricing; add JSONL store/replay; move event coordination to checkout. | no | 62 s |
| L1 | B | `5178c6a97be5d60a6e8cbc25250d5e9c25bc29ecfb3d6ea7a92d3694bc19924e` | Extract: pricing calculation and audit persistence/replay are distinct, with the same caller/signature/test ripple. | Characterize; restore pure quote and checkout sink; add JSONL; verify replay integration. | yes | unavailable |
| L2 | A | `bcfc4b7b95c818bf68abb5842913985d02cf0eb15fafbeb86e33bac4d53013bd` | Extract a private helper because policy rules accumulated, although callers, state, tests, and history remained cohesive. | Add tests; add helper; test rule interaction. | no | 58 s |
| L2 | B | `93afef334af2d7e8cb0e0ba0e17cb413a179d5698be21c91828e72576fc91dd1` | Preserve: `shipping.price` remains one local policy with one focused test and no locality failure. | Add tests; implement in `shipping.price`; test zone interaction. | yes | 69 s |
| L3 | A | `0109e7a1ae336bc9e3b6cca485ccf8e549eefe325f9290c3b7c690716db359c8` | Correct ownership instead of another split: sender mutates tracker state, tracker reverse-imports sender, and tests reset internals. | Add tracker API; remove reverse import; route sender through API; split focused tests. | no | 61 s |
| L3 | B | `b53d3da953d60e2272c0fa898a26a469f04a1923ff3d2e511a14f9f879c8dd73` | Correct ownership instead of another split, with shared-state, dependency, test, and co-change anchors. | Characterize; add tracker-owned API; update sender; separate focused tests. | yes | 69.897 s |
| L4 | A | `3ac9718a54e52ceb54583abcd7cd13c9694b0f8fc634af18124305027b8c4586` | Preserve: rename, formatting, and generated-header commits are noise; stable sort already supplies input-order ties. | Test stable ties; document policy; run regression. | no | 65 s |
| L4 | B | `6075da225143d9b49e8a4601f4f45715630c073222d11b2ce6b8769b4612a50a` | Preserve: ordering remains one policy and the three historical noise classes do not establish coupling. | Clarify tie behavior; implement in place; add focused tests; verify. | yes | 69 s |

Arm A is the baseline and Arm B the candidate; that mapping was withheld from
both auditors. Every runner reported input and output token counts as
unavailable because the host did not expose them. They remain unavailable,
not zero.

## Blind audit

| Case | Baseline verdicts | Candidate verdicts | Result |
|---|---|---|---|
| L1 | correct / insufficient | correct / correct | Auditors disagree; the required baseline miss is not established. |
| L2 | incorrect / incorrect | correct / correct | Candidate avoids the baseline's cohesion false positive. |
| L3 | correct / correct | correct / correct | Both correct ownership without another shallow split. |
| L4 | correct / correct | correct / insufficient | Boundary decision is correct, but one auditor found the diff-cap evidence insufficient. |

Both auditors reported no mandatory skill, no user boundary decision, and no
L4 extraction false positive. They agreed that L2 Arm A was a false positive.
Auditor 1 called L1 a tie; auditor 2 called Arm B an improvement. The frozen
bar requires agreement, so the result is negative without arbitration or a
rerun.

## Minimal real implementations

The real runs used temporary copies rebuilt from the frozen L1 and L2 HEADs.
Tests were written and observed failing before production changes.

### L1

- RED: three errors — missing `audit` module, checkout expected list append,
  and `quote` still required `audit_events`.
- GREEN: `python3 -m unittest discover -s tests -v` — 3 passed.
- Final Python-tree SHA-256:
  `036e94b34863b042b6d8e6546c6bb68716592e5c5a0850ac39bdb4715b0b8d1b`.
- Initial implementation ripple: six files (`pricing.py`, `checkout.py`,
  `audit.py`, and three focused test files), versus the three-file coupled
  surface at fixture HEAD.
- Dependency-complete storage surface after extraction: two files and two
  named regions (`audit.py:JsonlAuditStore`, `tests/test_audit.py:AuditTest`),
  versus pricing, checkout, and pricing-test regions before extraction.
  Pricing tests no longer construct or assert storage state; checkout depends
  only on `record(event)`.
- Focused verification elapsed 0.098 seconds. The surrounding manual TDD edit
  interval and token counts were not exposed and are recorded as unavailable.

### L2

- Fixture-only behavior assumption: multiplier 2, weekend cap 60, cap before
  remote surcharge. This measures locality and is not a product recommendation.
- RED: one error — `price` rejected the new `weekend` argument.
- GREEN: `python3 -m unittest discover -s tests -v` — 2 passed.
- Final Python-tree SHA-256:
  `cdb34472284800ee5737edcf9a2804fce241b9699d60fc93b765843c678bfe47`.
- Feature surface: two files and two named regions
  (`shipping.py:price`, `tests/test_shipping.py:ShippingTest`), with no new
  module, caller ripple, shared state, or extraction.
- Focused verification elapsed 0.088 seconds. The surrounding manual TDD edit
  interval and token counts were not exposed and are recorded as unavailable.

## Cost and mechanism observations

- Baseline runner elapsed total: 246 seconds. Candidate total is unavailable
  because L1 did not expose elapsed time; observed L2-L4 subtotal is 207.897
  seconds.
- Baseline contract: 4,497 whitespace-delimited words. Candidate contract:
  4,588 words plus a 372-word detailed reference. The marked additions are an
  80-word always-run screen and a 364-word conditional reference.
- Candidate detailed-reference load rate: 4/4, or 100%. The observed average
  added contract context was therefore 444 marked words per plan, not the
  low-load shape required by the frozen corpus.
- `python3 loom-code/scripts/check_mechanisms.py --baseline 1973ff35c...`
  reported net mechanism count 119 both before and after: delta 0.
- `python3 loom-code/scripts/check_mechanisms.py --measure` reported 18 skills,
  6 artifact types, and 745 session-start words, below the recorded 5,278-word
  baseline.

## Reproduction commands

```text
python3 -m pytest loom-code/scripts/test_probes_cumulative_boundary_reassessment.py -q
python3 loom-code/scripts/check_mechanisms.py --baseline 1973ff35c4919e4c40795808240249c7ee40f506
python3 loom-code/scripts/check_mechanisms.py --measure
```

## Limitations

- Four small Python fixtures and one model/profile pair do not establish a
  general effect across repositories, languages, models, or long histories.
- The runner contract copies omitted unrelated bundled Write Plan references;
  missing-reference messages were retained as limitations but did not alter
  the boundary rubric.
- L1 can already be solved from obvious current coupling, so this fixture does
  not isolate incremental value from historical reassessment.
- Candidate reference loading over-fired in every case; file separation did
  not reduce average context in this run.
- Token counts and one elapsed value were unavailable. Missing observations
  are admission failures, not zero-cost evidence.
- The L1 real run improved ownership clarity but increased initial changed-file
  count; it supports no universal claim of smaller diffs or faster agents.

## Normalized evidence

`null` means unavailable and must never be interpreted as zero.

```json evidence
{
  "status": "NOT_ADMITTED",
  "identities": {
    "fixture_spec_sha256": "a9c3448869bc73985b3219ffeeb53770beb16c09134c888489639caf1a0b1723",
    "rubric_sha256": "ea89194e8d5673e3eba94b016318ba4e76d1da8d4893947a3d517658b1256594",
    "baseline_revision": "1973ff35c4919e4c40795808240249c7ee40f506",
    "baseline_contract_sha256": "e4c249bae4a5badbd15c258fbfe6d4d2d920e9eba58329fa2ee05bfe573c0da4",
    "candidate_revision": "e2161e2fe6b3bf40d33b8a0c45cb035f77d2d73c",
    "candidate_contract_sha256": "edeb377b3fe4b1a3d5d776dbfde5d4631fd52a03e46fc7d3bd8ae0d9b90e49d0",
    "candidate_contract_bytes": 30427,
    "candidate_reference_sha256": "0c6f5465cd0765efb6eb82b6a2dffef5d86fb2120af43e173541006c8b2a93b2",
    "candidate_reference_bytes": 2601,
    "candidate_revision_paths": [
      "loom-code/scripts/test_cumulative_boundary_contract.py",
      "loom-code/skills/write-plan/SKILL.md",
      "loom-code/skills/write-plan/references/cumulative-boundary-reassessment.md"
    ],
    "candidate_changed_contract_paths": [
      "loom-code/skills/write-plan/SKILL.md",
      "loom-code/skills/write-plan/references/cumulative-boundary-reassessment.md"
    ],
    "artifact_carriers": {
      "cases": {
        "revision": "4864ea08d96824f74a9b824f39ded1e27b910fd9",
        "path": "docs/skill-dogfood/2026-09-13-cumulative-boundary-reassessment/cases.md",
        "blob": "e97ac10e201da9abd2885e3b6a548effb223eeff"
      },
      "admission_probe": {
        "revision": "4864ea08d96824f74a9b824f39ded1e27b910fd9",
        "path": "loom-code/scripts/test_probes_cumulative_boundary_reassessment.py",
        "blob": "ab40c5061e070d19cad2f3d106d1b4de7c308a42"
      },
      "normalized_report": {
        "revision": "d7e72bb348b8e0092c611992f1bee140ed2f2a6e",
        "path": "docs/skill-dogfood/2026-09-13-cumulative-boundary-reassessment/report.md",
        "blob": "29d9be0261ccc4f9d65fba22ddd0d9cdd2c4febf"
      }
    }
  },
  "fixtures": {
    "L1": {"head": "45a097b6180c90a8dc68d2f057b03d8d4ae7687a", "tree": "74e9c6734d9ebfd6f2a1920b99f461be253445bc"},
    "L2": {"head": "397c8269299ab56144ef7a1445188f497beb078f", "tree": "b723cb3b390d179d32274d4922d78005c9119a2d"},
    "L3": {"head": "d3c9f45e8d85b162f8485f0dde7937bbc1bfe943", "tree": "bbc3cff17e12cd61a7460f9cb88d75038d573604"},
    "L4": {"head": "3ec35ed5137e550b45690f7d454f88796e8be3e0", "tree": "3b4a97db3a058ee1d7f2fe3e6c4db23c88dfebdf"}
  },
  "runner_profile": {
    "baseline": {"model": "gpt-5.6-sol", "effort": "medium"},
    "candidate": {"model": "gpt-5.6-sol", "effort": "medium"}
  },
  "normalizer_sha256": "de640cfa9cb5a9e898dc26fdecef386f0e63987733be01da5e5f4cc3eae18735",
  "normalized_outputs": {
    "L1": {"baseline": "c0985cb59d718c8a083cf1dc3a58ff0cfa89bd9307cc3719442e44d00e2c8739", "candidate": "5178c6a97be5d60a6e8cbc25250d5e9c25bc29ecfb3d6ea7a92d3694bc19924e"},
    "L2": {"baseline": "bcfc4b7b95c818bf68abb5842913985d02cf0eb15fafbeb86e33bac4d53013bd", "candidate": "93afef334af2d7e8cb0e0ba0e17cb413a179d5698be21c91828e72576fc91dd1"},
    "L3": {"baseline": "0109e7a1ae336bc9e3b6cca485ccf8e549eefe325f9290c3b7c690716db359c8", "candidate": "b53d3da953d60e2272c0fa898a26a469f04a1923ff3d2e511a14f9f879c8dd73"},
    "L4": {"baseline": "3ac9718a54e52ceb54583abcd7cd13c9694b0f8fc634af18124305027b8c4586", "candidate": "6075da225143d9b49e8a4601f4f45715630c073222d11b2ce6b8769b4612a50a"}
  },
  "auditors": ["codex-blind-auditor-1", "codex-blind-auditor-2"],
  "cases": {
    "L1": {"baseline": ["correct", "insufficient"], "candidate": ["correct", "correct"]},
    "L2": {"baseline": ["incorrect", "incorrect"], "candidate": ["correct", "correct"]},
    "L3": {"baseline": ["correct", "correct"], "candidate": ["correct", "correct"]},
    "L4": {"baseline": ["correct", "correct"], "candidate": ["correct", "insufficient"]}
  },
  "reference_loaded": {"L1": true, "L2": true, "L3": true, "L4": true},
  "cost": {
    "baseline": {"elapsed_seconds": 246, "input_tokens": null, "output_tokens": null},
    "candidate": {"elapsed_seconds": null, "input_tokens": null, "output_tokens": null},
    "candidate_observed_elapsed_subtotal": 207.897,
    "candidate_reference_load_rate": 1.0,
    "average_added_contract_words": 444
  },
  "mechanism_delta": 0,
  "real_runs": {
    "L1": {
      "complete": true,
      "focused_tests_pass": true,
      "candidate_surface_clearer_or_smaller": true,
      "initial_changed_files": 6,
      "storage_surface_files_before": 3,
      "storage_surface_files_after": 2,
      "tree_sha256": "036e94b34863b042b6d8e6546c6bb68716592e5c5a0850ac39bdb4715b0b8d1b"
    },
    "L2": {
      "complete": true,
      "focused_tests_pass": true,
      "extraction_performed": false,
      "changed_files": 2,
      "tree_sha256": "cdb34472284800ee5737edcf9a2804fce241b9699d60fc93b765843c678bfe47"
    }
  },
  "claims_scope": "frozen-four-case-corpus-only"
}
```

[^git-init]: Git project, “git-init 2.32.0,” https://git-scm.com/docs/git-init/2.32.0.html
[^git-config]: Git project, “git-config 2.32.0 — Environment,” https://git-scm.com/docs/git-config/2.32.0.html#ENVIRONMENT
[^git-commit]: Git project, “git-commit 2.32.0,” https://git-scm.com/docs/git-commit/2.32.0.html
[^git-revisions]: Git project, “gitrevisions 2.32.0,” https://git-scm.com/docs/gitrevisions/2.32.0.html
[^git-show]: Git project, “git-show 2.32.0,” https://git-scm.com/docs/git-show/2.32.0.html
[^git-diff-tree]: Git project, “git-diff-tree 2.32.0,” https://git-scm.com/docs/git-diff-tree/2.32.0.html
