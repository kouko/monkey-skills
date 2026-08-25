# loom-design skill compaction: dual-host weak-model A/B

Date: 2026-08-26

## Decision

**CLEAN.** All nine compacted loom-design entrypoints preserve their tested
observable contracts on Claude Code `haiku` and Codex `gpt-5.6-luna`. The
accepted evidence contains 72 weak-model runs:

```text
9 skills × 2 hosts × 2 roots × 2 replicates = 72 calls
```

Automatic `INCONCLUSIVE` results below are tool-sequence differences, not
silent passes. Codex `gpt-5.6-sol` read the raw weak-model evidence only for
those pairs and classified every one `NON_REGRESSION`. It did not execute the
test cases. The signed-off rows and exact raw-evidence filenames are retained
beside the isolated run as `strong-adjudication.md`.

One accepted Claude candidate run for `completeness-critic` produced the
correct refusal through direct Read/Bash instead of a structured `Skill`
event. A targeted diagnostic attempt then reproduced the same activation miss
on the unchanged baseline before a later host non-zero stopped that attempt.
Because baseline and candidate frontmatter are byte-identical and the skill
body is unavailable before activation, this is symmetric host noise rather
than candidate-caused behavior.

No accepted run wrote a project file, sent an external message, or left a file
in its isolated working directory. Authentication symlinks were removed from
every isolated Codex home after execution.

## Fixed inputs

- Baseline: the full loom-design plugin tree at `d560b172`, before this
  family's first compaction.
- Candidate: the full reviewed plugin tree at `1ba64739`, after all nine
  compactions and reviewer repairs.
- Weak executors: Claude Code `haiku`; Codex `gpt-5.6-luna`.
- Strong adjudicator: Codex `gpt-5.6-sol`, raw-evidence review only.
- Replicates: two per host/root/case; maximum four turns.
- Corpus: nine chat-only gate, refusal, or routing cases. Generator cases stop
  on an intentionally missing prerequisite rather than writing artifacts.
- Raw naming: `<case>-<host>-<root>-<rep>.jsonl`; independently executed cases
  use local case index `0` inside their own case folder.

## Size result

No content was moved into references in this family batch.

| Skill | Words, baseline → candidate | Bytes, baseline → candidate |
|---|---:|---:|
| business-value | 1,291 → 930 (-361) | 8,908 → 6,594 (-2,314) |
| completeness-critic | 4,004 → 3,190 (-814) | 27,992 → 22,392 (-5,600) |
| design-critic | 2,323 → 1,683 (-640) | 16,882 → 12,311 (-4,571) |
| design-system | 1,982 → 1,423 (-559) | 13,486 → 10,030 (-3,456) |
| interaction-flows | 1,445 → 1,094 (-351) | 10,401 → 8,178 (-2,223) |
| product-principles | 3,023 → 2,124 (-899) | 21,454 → 15,835 (-5,619) |
| user-insights | 1,321 → 929 (-392) | 9,490 → 6,902 (-2,588) |
| using-loom-design | 2,082 → 1,512 (-570) | 14,906 → 10,894 (-4,012) |
| using-loom-pipeline | 2,671 → 1,896 (-775) | 19,587 → 14,494 (-5,093) |
| **Total** | **20,142 → 14,781 (-5,361; 26.6%)** | **143,106 → 107,630 (-35,476; 24.8%)** |

## Replicate matrix

`B` and `C` are baseline and candidate. `2/2` means both replicates had
grounded activation: a Claude structured `Skill` event or a Codex installed
`SKILL.md` read.

| Case | Claude activation / result | Codex activation / result | Observable contract |
|---|---|---|---|
| business-value | B 2/2, C 2/2; adjudicated NON_REGRESSION | B 2/2, C 2/2; adjudicated NON_REGRESSION | Skip personal throwaway/already-decided work; no interrogation or artifact. |
| completeness-critic | B 2/2, C 1/2; symmetric activation noise, NON_REGRESSION | B 2/2, C 2/2; NON_REGRESSION | Reject a UI sketch that is not a spec-expansion draft. |
| design-critic | B 1/2, C 2/2; baseline-only activation noise, NON_REGRESSION | B 2/2, C 2/2; NON_REGRESSION | Stop on behavioral spec; route away without panel verdict. |
| design-system | automatic PASS | B 2/2, C 2/2; NON_REGRESSION | Missing principles requires recommendation plus explicit consent. |
| interaction-flows | automatic PASS | B 2/2, C 2/2; NON_REGRESSION | Missing principles blocks generation until explicit choice. |
| product-principles | automatic PASS | B 2/2, C 2/2; NON_REGRESSION | Thin headless seed returns BLOCKED; no fabricated principles. |
| user-insights | automatic PASS | B 2/2, C 2/2; NON_REGRESSION | Refuse worth-it verdict and route to business-value. |
| using-loom-design | automatic PASS | B 2/2, C 2/2; NON_REGRESSION | Existing spec draft routes to completeness-critic; router does not author. |
| using-loom-pipeline | automatic PASS | B 2/2, C 2/2; NON_REGRESSION | Missing Workflow returns loom-design N/A and stops without fallback. |

## Diagnostic attempt

A targeted `completeness-critic` diagnostic reproduced a structured-Skill
  miss on baseline, then stopped when a later Claude invocation exited
  non-zero before candidate execution. It is not accepted A/B behavior
  evidence; it is retained only as evidence that activation selection is
  stochastic and symmetric.

## Verification

The final candidate also passes every independently collectible loom-design
package suite:

```text
discovery: 86 passed
interface: 190 passed
pipeline: 237 passed
principles: 302 passed
spec: 185 passed
total: 1,000 passed
```

The five directories run separately because the repository intentionally has
duplicate top-level pytest module basenames across them; a single collection
would fail before executing tests. Plugin-boundary validation and
`git diff --check` also pass.
