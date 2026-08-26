# Dogfood report — `skill-refactor`

## Metadata

| Field | Value |
|---|---|
| Skill path | `skill-dev-toolkit/skills/skill-refactor` |
| Skill version | `0.1.0` |
| Date | `2026-08-27` |
| Passes run | executor replay only; activation corpus and cold-reader not run |
| Model pinned | Claude Code `haiku`; Codex `gpt-5.6-luna` |
| Activation fidelity | real host replay, two requested replicates per host |

This is a partial dogfood finding record, not a dogfood PASS. The replay was
the release gate for package-resource mode; it was not the full 20-query
activation and distractor corpus prescribed by `dogfood-skill-testing`.

## Severity summary

| Severity | Count |
|---|---:|
| Critical | 1 |
| High | 0 |
| Medium | 0 |
| Low | 0 |
| **Total** | **1** |

## Findings

### FINDING-001: Claude skipped the package protocol and invented target-file accounting

- **Severity**: Critical
- **Category**: Progressive-disclosure
- **Pass**: informed
- **Probe prompt**: “Use the installed skill-refactor skill to assess this
  request: Shorten a skill's bundled reference file without changing
  behavior. Do not edit files or run the refactor; explain the required
  package-resource sequence, including the external manifest digest and
  canonical path, baseline snapshot, accounting, gate order, and host failure
  handling, then stop.”
- **Expected**: Load `skill-refactor`, read
  `references/package-resource-mode.md`, and describe immutable Git export,
  external manifest digest, canonical manifest path, same-operation verified
  snapshot, whole-package Q2, layered evidence, and fail-closed host errors.
- **Actual**: The Claude run loaded the skill but emitted no `Read` event. It
  described a digest of the target resource, applied Q2 to the target file,
  and recommended `git revert`, contradicting the package protocol.
- **Transcript evidence**: “Measure on the target bundled file alone (not the
  whole skill)” and “git can revert and re-baseline.” Tool sequence: `Skill`
  only.
- **Root cause**: The entrypoint used a soft “then read” handoff. A weak
  executor could answer from nearby entrypoint rules instead of loading the
  conditional package protocol.
- **Why static review missed it**: Contract tests proved the reference path
  existed and the prose said to read it; they did not prove a live weak model
  would actually invoke the file-reading tool before answering.
- **Location**: `skill-dev-toolkit/skills/skill-refactor/SKILL.md`, package-mode
  selection immediately before `### Round scope`
- **Suggested fix direction**: Replace the soft handoff with a fail-closed
  load gate: read the protocol whole before explaining, planning, or baseline
  work; if reading fails, stop with `UNGRADABLE`; forbid reconstructing package
  mode from the entrypoint.
- **Repro**: Run the probe above through Claude Code `haiku` with `Skill,Read`
  allowed and inspect the JSONL tool sequence plus final result.

## Raw outputs appendix

### A. Activation runs

Not run as a full distractor-corpus pass. The release replay itself activated
`skill-dev-toolkit:skill-refactor`; this report does not claim trigger coverage.

### B. Cold-reader audit

Not run.

### C. Executor artifact excerpt

```text
Q2: Token Reduction (Entrypoint Mode Threshold)
Measure on the target bundled file alone (not the whole skill).
...
If users report behavior change post-deployment, git can revert and re-baseline.
```

### D. Executor trajectory

```text
Claude tool sequence: Skill
Required but absent tool event: Read references/package-resource-mode.md
```

### E. Auditor judgment

```text
FAIL — the output is valid-looking but contradicts the controlling package
protocol on accounting scope, manifest-digest meaning, and rollback behavior.
```

## Resolution verification

Commit `37b0b293` replaced the soft handoff with `PACKAGE-MODE LOAD GATE`.
The final real-host replay retained raw JSONL under
`/private/tmp/skill-refactor-package-replay-load-gate-final/raw/`:

- Claude Code `haiku`, replicates 0 and 1: both fired
  `skill-dev-toolkit:skill-refactor`, then emitted `Read` for
  `references/package-resource-mode.md`; both outputs matched the package
  contract.
- Codex `gpt-5.6-luna`, replicates 0 and 1: both read the installed
  `SKILL.md` and `references/package-resource-mode.md`; both outputs matched
  the package contract.

The finding is behaviorally resolved for this probe. This still does not turn
the partial run into a full dogfood PASS: the broad activation distractor
corpus and cold-reader pass remain outside this release replay.
