# Loom skill compaction: dual-host weak-model A/B

Date: 2026-08-25

## Decision

The three pilot compactions are **CLEAN**. Across Claude Code (`haiku`) and
Codex (`gpt-5.6-luna`), every accepted baseline and candidate replicate loaded
the intended Skill and preserved the case's observable stop behavior. No
accepted run wrote to the isolated work directory. Replicated differences in
read count, token use, or command spelling were reviewed by Claude Sonnet and
classified `NON_REGRESSION`; the raw adjudication is
`/tmp/loom-skill-ab-20260825/stronger-adjudication.jsonl`.

Automatic `INCONCLUSIVE` values below mean the comparator retained different
tool sequences. They are not silently promoted: the stronger-model evidence
review is the final verdict for those rows. Token counts remain reported but
are excluded from the behavioral verdict because cost is not behavior.

## Size result

| Pilot | Baseline → candidate | Words | Bytes |
|---|---|---:|---:|
| distill-sessions | `eb21ffaf^` → `eb21ffaf` | 3,726 → 2,480 (-1,246) | 30,011 → 18,301 (-11,710) |
| spec-expansion | `ca73898b^` → `ca73898b` | 4,487 → 3,243 (-1,244) | 30,763 → 23,678 (-7,085) |
| subagent-driven-development | `ef2c80f7^` → `ef2c80f7` | 4,504 → 3,282 (-1,222) | 34,348 → 25,517 (-8,831) |

Total: 12,717 → 9,005 words (-3,712, 29.2%); 95,122 → 67,496 bytes
(-27,626, 29.0%).

## Accepted cases and replicates

`Tools` is the count of observable Skill/read/check operations. Claude latency
comes from `duration_ms`; Codex does not expose wall-clock latency in these
JSONL events, so it is `N/A`. All Codex rows expose one completed turn.

| Case | Host | Root | Rep | Model | Observable result | Tools / turns / latency ms | Raw bytes | Size delta | Final verdict | Raw transcript |
|---|---|---|---:|---|---|---|---:|---|---|---|
| distill | Claude | baseline | 1 | haiku | Skill loaded; stopped for transcript + insights | 1 / 3 / 19071 | 157266 | -1,246 words / -11,710 bytes | PASS | `/tmp/loom-skill-ab-20260825/raw/distill-attempt3/0-claude-baseline-0.jsonl` |
| distill | Claude | baseline | 2 | haiku | Skill loaded; stopped for transcript + insights | 1 / 3 / 15216 | 154352 | -1,246 / -11,710 | PASS | `/tmp/loom-skill-ab-20260825/raw/distill-attempt3/0-claude-baseline-1.jsonl` |
| distill | Claude | candidate | 1 | haiku | Skill loaded; stopped for transcript + insights | 1 / 3 / 24906 | 150747 | -1,246 / -11,710 | PASS | `/tmp/loom-skill-ab-20260825/raw/distill-attempt3/0-claude-candidate-0.jsonl` |
| distill | Claude | candidate | 2 | haiku | Skill loaded; stopped for transcript + insights | 1 / 3 / 14404 | 141328 | -1,246 / -11,710 | PASS | `/tmp/loom-skill-ab-20260825/raw/distill-attempt3/0-claude-candidate-1.jsonl` |
| distill | Codex | baseline | 1 | gpt-5.6-luna | Skill read; stopped for transcript + insights | 3 / 1 / N/A | 22420 | -1,246 / -11,710 | NON_REGRESSION | `/tmp/loom-skill-ab-20260825/raw/distill-attempt3/0-codex-baseline-0.jsonl` |
| distill | Codex | baseline | 2 | gpt-5.6-luna | Skill read; stopped for transcript + insights | 3 / 1 / N/A | 33545 | -1,246 / -11,710 | NON_REGRESSION | `/tmp/loom-skill-ab-20260825/raw/distill-attempt3/0-codex-baseline-1.jsonl` |
| distill | Codex | candidate | 1 | gpt-5.6-luna | Skill read; stopped for transcript + insights | 1 / 1 / N/A | 12149 | -1,246 / -11,710 | NON_REGRESSION | `/tmp/loom-skill-ab-20260825/raw/distill-attempt3/0-codex-candidate-0.jsonl` |
| distill | Codex | candidate | 2 | gpt-5.6-luna | Skill read; stopped for transcript + insights | 1 / 1 / N/A | 12150 | -1,246 / -11,710 | NON_REGRESSION | `/tmp/loom-skill-ab-20260825/raw/distill-attempt3/0-codex-candidate-1.jsonl` |
| spec | Claude | baseline | 1 | haiku | Skill loaded; seed-adequacy stop | 1 / 3 / 17401 | 154022 | -1,244 / -7,085 | PASS | `/tmp/loom-skill-ab-20260825/raw/spec-attempt3/0-claude-baseline-0.jsonl` |
| spec | Claude | baseline | 2 | haiku | Skill loaded; seed-adequacy stop | 1 / 3 / 19764 | 157680 | -1,244 / -7,085 | PASS | `/tmp/loom-skill-ab-20260825/raw/spec-attempt3/0-claude-baseline-1.jsonl` |
| spec | Claude | candidate | 1 | haiku | Skill loaded; seed-adequacy stop | 1 / 3 / 20211 | 148195 | -1,244 / -7,085 | PASS | `/tmp/loom-skill-ab-20260825/raw/spec-attempt3/0-claude-candidate-0.jsonl` |
| spec | Claude | candidate | 2 | haiku | Skill loaded; seed-adequacy stop | 1 / 3 / 19803 | 149036 | -1,244 / -7,085 | PASS | `/tmp/loom-skill-ab-20260825/raw/spec-attempt3/0-claude-candidate-1.jsonl` |
| spec | Codex | baseline | 1 | gpt-5.6-luna | Skill read; seed-adequacy stop | 3 / 1 / N/A | 35701 | -1,244 / -7,085 | NON_REGRESSION | `/tmp/loom-skill-ab-20260825/raw/spec-attempt3/0-codex-baseline-0.jsonl` |
| spec | Codex | baseline | 2 | gpt-5.6-luna | Skill read; seed-adequacy stop | 3 / 1 / N/A | 35897 | -1,244 / -7,085 | NON_REGRESSION | `/tmp/loom-skill-ab-20260825/raw/spec-attempt3/0-codex-baseline-1.jsonl` |
| spec | Codex | candidate | 1 | gpt-5.6-luna | Skill read; seed-adequacy stop | 2 / 1 / N/A | 27881 | -1,244 / -7,085 | NON_REGRESSION | `/tmp/loom-skill-ab-20260825/raw/spec-attempt3/0-codex-candidate-0.jsonl` |
| spec | Codex | candidate | 2 | gpt-5.6-luna | Skill read; seed-adequacy stop | 2 / 1 / N/A | 28231 | -1,244 / -7,085 | NON_REGRESSION | `/tmp/loom-skill-ab-20260825/raw/spec-attempt3/0-codex-candidate-1.jsonl` |
| SDD | Claude | baseline | 1 | haiku | Skill loaded; exact missing-plan stop; no dispatch | 2 / 4 / 15183 | 160151 | -1,222 / -8,831 | NON_REGRESSION | `/tmp/loom-skill-ab-20260825/raw/sdd-attempt1/0-claude-baseline-0.jsonl` |
| SDD | Claude | baseline | 2 | haiku | Skill loaded; exact missing-plan stop; no dispatch | 2 / 4 / 20102 | 162790 | -1,222 / -8,831 | NON_REGRESSION | `/tmp/loom-skill-ab-20260825/raw/sdd-attempt1/0-claude-baseline-1.jsonl` |
| SDD | Claude | candidate | 1 | haiku | Skill loaded; exact missing-plan stop; no dispatch | 2 / 4 / 17465 | 153829 | -1,222 / -8,831 | NON_REGRESSION | `/tmp/loom-skill-ab-20260825/raw/sdd-attempt1/0-claude-candidate-0.jsonl` |
| SDD | Claude | candidate | 2 | haiku | Skill loaded; exact missing-plan stop; no dispatch | 3 / 5 / 17152 | 155437 | -1,222 / -8,831 | NON_REGRESSION | `/tmp/loom-skill-ab-20260825/raw/sdd-attempt1/0-claude-candidate-1.jsonl` |
| SDD | Codex | baseline | 1 | gpt-5.6-luna | Skill read; exact missing-plan stop; no dispatch | 1 / 1 / N/A | 36505 | -1,222 / -8,831 | NON_REGRESSION | `/tmp/loom-skill-ab-20260825/raw/sdd-attempt1/0-codex-baseline-0.jsonl` |
| SDD | Codex | baseline | 2 | gpt-5.6-luna | Skill read; exact missing-plan stop; no dispatch | 1 / 1 / N/A | 36408 | -1,222 / -8,831 | NON_REGRESSION | `/tmp/loom-skill-ab-20260825/raw/sdd-attempt1/0-codex-baseline-1.jsonl` |
| SDD | Codex | candidate | 1 | gpt-5.6-luna | Skill read; exact missing-plan stop; no dispatch | 3 / 1 / N/A | 28861 | -1,222 / -8,831 | NON_REGRESSION | `/tmp/loom-skill-ab-20260825/raw/sdd-attempt1/0-codex-candidate-0.jsonl` |
| SDD | Codex | candidate | 2 | gpt-5.6-luna | Skill read; exact missing-plan stop; no dispatch | 3 / 1 / N/A | 28732 | -1,222 / -8,831 | NON_REGRESSION | `/tmp/loom-skill-ab-20260825/raw/sdd-attempt1/0-codex-candidate-1.jsonl` |

Codex activation is grounded in observable reads of the installed
`.../<plugin>/<version>/skills/<skill>/SKILL.md` path, not the model saying it
used a Skill. Claude activation is the structured `Skill` tool event.

## Discarded attempts

- Distill attempt 1: all Codex calls returned 401 because the isolated
  `CODEX_HOME` lacked local authentication. The harness originally normalized
  the error stream as completed; those files were accidentally overwritten
  during diagnosis and are not accepted as evidence. The defect now has the
  fail-loud test `test_run_host_rejects_nonzero_exit`.
- Distill attempt 2 (`/tmp/loom-skill-ab-20260825/raw/distill/`) and spec
  attempt 1 (`/tmp/loom-skill-ab-20260825/raw/spec-attempt1/`): authentication
  succeeded, but `--ignore-user-config` hid the plugin installed inside the
  isolated home. The agents reported the Skill unavailable. The invocation now
  loads only that isolated config, covered by
  `test_codex_root_invocation_loads_isolated_plugin_config`.
- Spec attempt 2 (`/tmp/loom-skill-ab-20260825/raw/spec-attempt2/`): the first
  corpus wording prohibited even reading the installed Skill, causing one
  baseline replicate to stop before activation. Attempt 3 permits only the
  installed Skill read and is the accepted evidence.

No secret value appears in this record or the accepted transcript summaries.
Temporary authentication symlinks are removed after the runs.

## Exact invocation shape

Each accepted pilot used the documented Task 2 shape plus:

```text
--replicates 2 --max-turns 4 --working-directory /tmp/loom-skill-ab-20260825/work --claude-model haiku --codex-model gpt-5.6-luna
```

The three corpus/baseline/candidate/raw/out paths are respectively the
`distill-attempt3`, `spec-attempt3`, and `sdd-attempt1` paths recorded above.
Claude's live help confirms `--model`; Codex's live `exec --help` confirms
`--model`/`-m`.
