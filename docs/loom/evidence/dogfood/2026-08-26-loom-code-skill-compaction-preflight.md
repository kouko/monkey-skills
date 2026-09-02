# loom-code skill compaction preflight

Date: 2026-08-26
Verdict: PASS — all pre-refactor inputs and weak-model baseline runs are frozen; no `SKILL.md` or reference changed.

## Method

- The user previously acknowledged genuine prompts and weak-model equivalence testing on Claude Code and Codex.
- All 13 target directories have a schema-valid `test-prompts.json`; the two existing corpora were not semantically changed.
- Every prompt ran twice on Claude Code `haiku` and twice on Codex `gpt-5.6-luna` against an immutable full-plugin `HEAD` export.
- Each invocation used an isolated work directory; every Codex invocation also used an isolated `CODEX_HOME`. Temporary authentication links were removed after use.
- An audit rejected 26 Claude runs that had exited nonzero at the original four-turn bound. All 26 were rerun to exit zero with bounded turn limits; one Codex run was also rerun because its original invocation provenance was not deterministically recoverable. The accepted set has zero host errors.
- Every accepted raw file has a sidecar whose fingerprint binds the baseline commit/tree, corpus and prompt hashes, expected-behavior hash, host/model/replicate, argument semantics, turn limit, and timeout. The machine record also binds each raw file's SHA-256.

## Evidence

| Measure | Result |
|---|---:|
| Target skills | 13 |
| Prompt corpus entries | 41 |
| Raw runs | 164 |
| Claude / Codex runs | 82 / 82 |
| Replicates per prompt and host | 2 |
| Host errors in accepted record | 0 |
| Baseline classifications | 78 EXACT / 22 FAMILY / 64 MISS |

`MISS` and `FAMILY` are frozen baseline observations, not candidate regressions. Later A/B compares each candidate against these same per-prompt, per-host replicates.

These classifications describe routing only; they are not a new correctness judgment. Final multi-judge semantic equivalence consumes the bound host-native raw outputs and the expected-behavior hashes, not only the compact observable fields in the machine record.

Accepted invocation provenance: 139 runs at 4 turns, 15 at 12 turns, 7 at 24 turns, and 3 at 48 turns. Every accepted run exited zero and remains independently checkable with:

`python3 scripts/skill_compaction_preflight.py --verify-record-raw docs/loom/dogfood/2026-08-26-loom-code-skill-compaction-preflight.json`

Machine record: `docs/loom/dogfood/2026-08-26-loom-code-skill-compaction-preflight.json`

Raw workspaces:

- `/tmp/loom-code-preflight-20260826-first-half-v2`
- `/tmp/loom-code-preflight-20260826-second-half-v2`

The machine record stores only stable labels, hashes, word counts, invariant summaries, classifications, and observable counts. Host-native commands and absolute runtime paths remain only in the external raw workspaces.

## Frozen word counts

| Skill | `wc -w` |
|---|---:|
| brainstorming | 3,645 |
| dispatching-parallel-agents | 1,827 |
| finishing-a-development-branch | 4,470 |
| loom-memory | 1,058 |
| requesting-code-review | 4,496 |
| requesting-docs-review | 4,063 |
| systematic-debugging | 2,200 |
| tdd-iron-law | 1,833 |
| ui-verification | 1,196 |
| using-git-worktrees | 1,298 |
| using-loom-code | 1,671 |
| verification-before-completion | 1,154 |
| writing-plans | 4,498 |

Total: 33,409 words.
