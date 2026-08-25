# loom-workflow skill compaction: dual-host weak-model A/B

Date: 2026-08-25

## Decision

**CLEAN after repair and focused retest.** Task 6 (`handoff`) and Task 8
(`recap-state`) now pass both hosts with grounded activation and two replicates
per baseline/candidate arm. No confirmed regression remains across the eight
workflow skill compactions.

- Initial `handoff` candidate: both Claude `haiku` replicates made a denied
  reference read the only blocker instead of applying the self-evident
  missing-expected-output gate. The repaired candidate now reports the missing
  expected output, requests the corrected HANDOFF/schema, and stops on both
  hosts and both replicates.
- First `recap-state` repair: both Claude replicates still wrapped the tags in
  a Markdown `xml` fence. Removing the fenced template while retaining the raw
  tag skeleton fixed this in attempt 4: every Claude and Codex final recap
  payload starts with `<thinking>`, uses sibling raw tags, has no fence or
  wrapper, and stops after the Synthesis-check.
- The restored Japanese and Traditional Chinese triggers now pass the targeted
  README consistency test. Attempt 4 also cleared the prior live-behavior
  blocker.

All eight skills have no confirmed behavioral regression after the focused
repairs. Every automatic
`INCONCLUSIVE` was retained and reviewed from raw evidence; read-count,
reference-read, and command-spelling differences alone were not promoted to a
behavioral verdict.

## Fixed inputs

- Baseline root: full `loom-workflow/` tree from `8b917bef` (parent of the first
  family compaction commit), extracted into an isolated baseline root.
- Candidate root: full reviewed tree from `c3625988`, extracted at
  an isolated candidate root.
- Weak models: Claude Code `haiku`; Codex `gpt-5.6-luna`.
- Strong adjudicator: Codex `gpt-5.6-sol`, acting without delegation and reading
  the raw JSONL directly.
- Accepted corpus and comparison were retained in the isolated run workspace.
- Accepted raw convention:
  `<case>-<host>-<root>-<rep>.jsonl`,
  where case `0..7`, host is `claude|codex`, root is
  `baseline|candidate`, and rep is `0|1`. This names all 64 runs without
  duplicating the comparison JSON's per-run argv, observable, model, and path.
- Claude `cot-explain` activation evidence also uses the four Claude case-2
  files in attempt 1: all four contain structured `Skill` events. Attempt 2
  split one activation miss into each arm; the stronger judge classified that
  symmetric miss as stochastic, not candidate-caused.
- Working directories remained empty. No run wrote project files or sent an
  external message.

The comparator invocation was:

```text
python3 loom-code/scripts/loom_firing_harness.py compare \
  --corpus <corpus.jsonl> \
  --baseline <baseline-root> \
  --candidate <candidate-root> \
  --raw-dir <raw-evidence-dir> \
  --out <comparison.json> \
  --replicates 2 --max-turns 4 \
  --working-directory <empty-work-dir> \
  --claude-model haiku --codex-model gpt-5.6-luna
```

Codex authentication symlinks existed only inside the two isolated comparison
homes during execution. They were moved out of both homes immediately after
the run; no credential value is recorded here.

## Size result

| Skill | Words, baseline → candidate | Bytes, baseline → candidate |
|---|---:|---:|
| brief-before-asking | 3,066 → 2,387 (-679) | 20,088 → 15,785 (-4,303) |
| complexity-critique | 2,150 → 1,545 (-605) | 13,665 → 10,320 (-3,345) |
| cot-explain | 4,348 → 3,263 (-1,085) | 26,157 → 20,063 (-6,094) |
| dbt-model-style | 3,569 → 2,782 (-787) | 25,022 → 18,670 (-6,352) |
| git-memory | 2,341 → 1,710 (-631) | 16,013 → 11,861 (-4,152) |
| handoff | 1,446 → 1,160 (-286) | 9,708 → 7,903 (-1,805) |
| proposal-critique | 1,366 → 928 (-438) | 9,366 → 6,281 (-3,085) |
| recap-state | 1,421 → 1,122 (-299) | 9,547 → 7,673 (-1,874) |
| **Total** | **19,707 → 14,897 (-4,810; 24.4%)** | **129,566 → 98,556 (-31,010; 23.9%)** |

## Replicate matrix

Each cell is `activation / tool-count / turns / latency-ms`. `B1,B2,C1,C2`
are baseline/candidate replicate 1/2. Codex exposes one completed turn but not
wall-clock latency (`N/A`). Activation is grounded only by a Claude structured
`Skill` event or a Codex installed `SKILL.md` read.

| Case | Claude B1,B2,C1,C2 | Codex B1,B2,C1,C2 | Comparator / strong verdict |
|---|---|---|---|
| 0 brief-before-asking | yes/1/3/28743; yes/1/3/55422; yes/1/3/29343; yes/1/3/35766 | yes/1/1/N/A ×4 | PASS; Codex tool-sequence-only → NON_REGRESSION |
| 1 complexity-critique | yes/3/5/30829; yes/3/5/33440; yes/3/5/26949; yes/1/3/45481 | yes/1/1/N/A; yes/1/1/N/A; yes/2/1/N/A; yes/3/1/N/A | both INCONCLUSIVE → NON_REGRESSION |
| 2 cot-explain | attempt2: no/0/1/5542; yes/1/3/53007; yes/1/3/22833; no/0/1/11969 | yes/2/1/N/A; yes/2/1/N/A; yes/1/1/N/A; yes/1/1/N/A | symmetric activation noise; output/tool differences → NON_REGRESSION |
| 3 dbt-model-style | yes/1/3/14598; yes/1/3/20216; yes/1/3/13620; yes/1/3/16050 | yes/2/1/N/A; yes/1/1/N/A; yes/1/1/N/A; yes/1/1/N/A | Claude PASS; Codex read-count-only → NON_REGRESSION |
| 4 git-memory | yes/1/3/10665; yes/1/3/17573; yes/1/3/17535; yes/1/3/16709 | yes/2/1/N/A; yes/2/1/N/A; yes/1/1/N/A; yes/1/1/N/A | Claude PASS; Codex read-count-only → NON_REGRESSION |
| 5 handoff | yes/1/3/14262; yes/1/3/13364; yes/2/4/17376; yes/2/4/20613 | yes/2/1/N/A; yes/1/1/N/A; yes/1/1/N/A; yes/1/1/N/A | Claude output/stop divergence → **REGRESSION**; Codex NON_REGRESSION |
| 6 proposal-critique | yes/1/3/13979; yes/1/3/16706; yes/1/3/13813; yes/1/3/9618 | yes/1/1/N/A ×4 | Claude PASS; Codex command-only → NON_REGRESSION |
| 7 recap-state | yes/2/4/30910; yes/1/3/24366; yes/3/5/22406; yes/2/4/25660 | yes/1/1/N/A; yes/1/1/N/A; yes/3/1/N/A; yes/1/1/N/A | Claude output-contract divergence → **REGRESSION**; Codex NON_REGRESSION |

Raw byte sizes and exact argv for every row are retained in
`comparison.json`; raw transcript paths follow the fixed convention above.

## Invalid attempt

Attempt 1 was preserved in a separate isolated workspace and not overwritten.
It completed 64 calls, but several Codex runs answered from
the advertised description without reading installed `SKILL.md`; those runs
cannot prove activation. Attempt 2 changed only the corpus instruction: load
the named Skill first, and on Codex permit exactly the named installed
`SKILL.md` read while retaining the no-write/no-message constraints.

## Repair retest — attempt 3

Attempt 3 retested only the two initially failing skills with a fresh full
candidate plugin root copied from the repaired worktree, the unchanged
immutable baseline, the same activation-grounded corpus wording, and the same
pinned weak models. Raw evidence and the normalized result were retained in
that isolated run workspace.

```text
2 cases × 2 hosts × 2 roots × 2 replicates = 16 completed calls
Claude Code: haiku
Codex: gpt-5.6-luna
strong raw-evidence adjudicator: gpt-5.6-sol
```

| Skill | Host | Candidate replicate evidence | Strong verdict |
|---|---|---|---|
| handoff | Claude | 2/2 structured Skill activations; missing expected output named; corrected HANDOFF/schema requested; stopped | NON_REGRESSION |
| handoff | Codex | 2/2 installed `SKILL.md` reads; missing expected output named; corrected evidence requested; stopped | NON_REGRESSION |
| recap-state | Claude | 2/2 structured Skill activations; both outputs wrapped in forbidden `xml` fences | **REGRESSION** |
| recap-state | Codex | 2/2 installed `SKILL.md` reads; both emit prose before `<thinking>` | **REGRESSION** |

All four automatic comparisons were `INCONCLUSIVE` because tool sequences
differed; the stronger judge read all 16 raw files and classified the
observable output contracts above. No attempt-3 run wrote a file or sent an
external message. Its working directory is empty. Authentication symlinks were
removed from both isolated Codex homes immediately after the run.

Targeted repaired-surface verification passes:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest \
  loom-workflow/scripts/test_handoff_compaction.py \
  loom-workflow/scripts/test_recap_state_compaction.py \
  loom-workflow/skills/recap-state/scripts/test_readmes.py -q
3 passed in 0.11s
```

This demonstrates that the static tests encode the repaired wording but did
not predict live compliance until the fenced template itself was removed.

## Second recap-state repair retest — attempt 4

Attempt 4 used a fresh full candidate plugin root from the second repaired
worktree, the unchanged attempt-1 baseline, the same grounded recap case, and
the unchanged harness/model pins.

- Comparison and raw evidence were retained in the isolated attempt-4 workspace.
- Calls: `1 case × 2 hosts × 2 roots × 2 replicates = 8`
- Automatic result: Claude `INCONCLUSIVE`, Codex `INCONCLUSIVE` because tool
  sequences differed.
- Strong `gpt-5.6-sol` raw-evidence result: Claude `NON_REGRESSION`, Codex
  `NON_REGRESSION`, overall `NON_REGRESSION`.

All four candidate final recap payloads start directly with `<thinking>`,
contain sibling raw tags without Markdown fences or wrapper prose, end with the
Synthesis-check, and stop. Codex pre-read commentary occurred in baseline and
candidate, so it is symmetric host behavior rather than a candidate regression.
Every activation was grounded; no write or outbound-message operation occurred.
Authentication symlinks were removed and the attempt-4 work directory is empty.

## Verification

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest loom-workflow/ -q
221 passed
```

The pre-repair run was `220 passed, 1 failed`; the failure was the
Japanese-trigger regression. The final run above covers the repaired snapshot,
and attempt 4 supersedes attempt 3's live blocker.
