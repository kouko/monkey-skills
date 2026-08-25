# loom-code skill compaction: dual-host weak-model A/B

Date: 2026-08-26

## Decision

**CLEAN after repairs.** The 13 newly compacted loom-code entrypoints and the
earlier `subagent-driven-development` pilot preserve their tested observable
contracts. The weak executors were Claude Code `haiku` and Codex
`gpt-5.6-luna`; stronger agents only adjudicated host-native transcripts and
never substituted their own execution for a weak-model run.

The first candidate pass exposed two real weak-model escape paths and one
target-root ambiguity:

- `verification-before-completion` accepted stale focused-test evidence;
- `writing-plans` invented a third initial-depth option and allowed kickoff to
  be skipped;
- `loom-memory` treated the installed skill directory as the target repo and
  returned a false `N/A`.

Each finding received a RED-first static oracle, the smallest prose repair,
the full loom-code package suite, and a grounded weak-model retest. The final
repair tree is `654541c6`; all three repaired behaviors are `NON_REGRESSION`
against the immutable baseline.

## Fixed inputs

- Baseline for the 13-skill batch: full loom-code tree at `821bc938`.
- Final candidate: full loom-code tree at `654541c6`.
- Separate pilot: `subagent-driven-development`, `ef2c80f7^` → `ef2c80f7`.
- Weak executors: Claude Code `haiku`; Codex `gpt-5.6-luna`.
- Replicates: two per prompt, host, and root; 41 prompts in the main corpus.
- Original baseline: 164 completed calls with zero accepted host errors.
- First candidate pass: 164 attempted calls; 151 completed and 13 host errors
  (12 Claude, one Codex). Host errors were never treated as passes.
- Supplemental corpus: explicit skill-loading, read-only behavioral probes for
  inconclusive cells and repaired escape paths. Only pairs grounded in the
  expected skill were semantically compared.
- Strong adjudication: transcript review only; `NON_REGRESSION`, `REGRESSION`,
  or `INCONCLUSIVE` relative to the matching baseline behavior.

The final `loom-memory` Codex-only retry failed twice at the host boundary
before producing a comparison record. Its earlier grounded Codex pair was
already non-regressive; the final repair changed only target-root resolution,
which was covered by two grounded Claude candidate runs plus the static oracle.
This operational failure is disclosed rather than silently converted to PASS.

## Size result

No content was moved into references.

| Skill | Words, baseline → candidate | Bytes, baseline → candidate |
|---|---:|---:|
| brainstorming | 3,645 → 2,591 (-1,054) | 24,887 → 18,586 (-6,301) |
| dispatching-parallel-agents | 1,827 → 1,369 (-458) | 12,786 → 10,187 (-2,599) |
| finishing-a-development-branch | 4,470 → 3,576 (-894) | 31,676 → 25,929 (-5,747) |
| loom-memory | 1,058 → 768 (-290) | 7,245 → 5,556 (-1,689) |
| requesting-code-review | 4,496 → 3,555 (-941) | 34,469 → 28,193 (-6,276) |
| requesting-docs-review | 4,063 → 3,165 (-898) | 29,098 → 23,481 (-5,617) |
| systematic-debugging | 2,200 → 1,741 (-459) | 15,114 → 11,959 (-3,155) |
| tdd-iron-law | 1,833 → 1,285 (-548) | 12,024 → 8,471 (-3,553) |
| ui-verification | 1,196 → 920 (-276) | 8,269 → 6,632 (-1,637) |
| using-git-worktrees | 1,298 → 1,034 (-264) | 8,648 → 6,827 (-1,821) |
| using-loom-code | 1,671 → 1,334 (-337) | 11,813 → 9,533 (-2,280) |
| verification-before-completion | 1,154 → 917 (-237) | 7,826 → 6,465 (-1,361) |
| writing-plans | 4,498 → 3,598 (-900) | 33,554 → 27,670 (-5,884) |
| subagent-driven-development pilot | 4,504 → 3,282 (-1,222) | 34,348 → 25,517 (-8,831) |
| **Total** | **37,913 → 29,135 (-8,778; 23.2%)** | **271,757 → 215,006 (-56,751; 20.9%)** |

## Behavioral result

| Skill | Final relative verdict | Load-bearing probe |
|---|---|---|
| brainstorming | NON_REGRESSION | Refuses “just code”; alternatives, one-question gate, and brief stop remain. |
| dispatching-parallel-agents | NON_REGRESSION | Dispatches only independent domains and retains integrated verification. |
| finishing-a-development-branch | NON_REGRESSION | Review, current verification, publish authorization, CI, and no-auto-merge gates remain. |
| loom-memory | NON_REGRESSION after repair | Uses the user's project as target; exhaustive proposal and approval-before-delete remain. |
| requesting-code-review | NON_REGRESSION | Immutable scope and two-reviewer whole-branch gate remain. |
| requesting-docs-review | NON_REGRESSION | One whole review plus one bounded delta confirmation; no auto-fix loop. |
| systematic-debugging | NON_REGRESSION | Reproduce → isolate → hypothesize → verify ordering remains. |
| tdd-iron-law | NON_REGRESSION | Production-before-RED remains refused; exemptions stay closed. |
| ui-verification | NON_REGRESSION | UI-flow applicability and state-driving gate remain. |
| using-git-worktrees | NON_REGRESSION | Concurrent-branch trigger and safety checks remain. |
| using-loom-code | NON_REGRESSION | Review-only work routes without entering implementation. |
| verification-before-completion | NON_REGRESSION after repair | Stale or focused evidence cannot satisfy current package verification. |
| writing-plans | NON_REGRESSION after repair | Initial depth >5 has exactly two dispositions; kickoff cannot be skipped. |
| subagent-driven-development | NON_REGRESSION | See the pilot report for its independent dual-host matrix. |

## Evidence locations

- Frozen baseline record:
  `docs/loom/dogfood/2026-08-26-loom-code-skill-compaction-preflight.json`
- Baseline raw workspaces:
  `/tmp/loom-code-preflight-20260826-first-half-v2` and
  `/tmp/loom-code-preflight-20260826-second-half-v2`
- First candidate records:
  `/tmp/loom-code-candidate-20260826-first.json` and
  `/tmp/loom-code-candidate-20260826-second.json`
- First candidate raw workspaces:
  `/tmp/loom-code-candidate-20260826-first` and
  `/tmp/loom-code-candidate-20260826-second`
- Supplemental comparisons and transcripts:
  `/tmp/loom-code-repair-ab-20260826/cases/`
- Pilot report:
  `docs/loom/dogfood/2026-08-25-loom-skill-compaction-dual-host-ab.md`

Early supplemental attempts with missing Codex authentication, missing working
directories, or interrupted execution are quarantined and excluded. One weak
preflight run also created an unintended review packet and committed the plan
ledger; the packet was quarantined, the in-scope ledger commit was retained,
and no such side effect appears in the accepted read-only supplemental runs.

## Verification

- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest loom-code/scripts -q`:
  **1,824 passed** after the final repair.
- Every compaction oracle remains inside its target word range.
- `git diff 821bc938..654541c6 -- loom-code/skills/*/references` is empty.
- `git diff --check`, plugin-boundary validation, citation validation, and the
  two-layer commit-carrier privacy gate pass.
