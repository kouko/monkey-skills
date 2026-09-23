---
name: skill-consistency-check
description: |
  Finds rules that contradict each other inside a skill folder. Use for 'check this skill for contradictions' or 'do these instructions conflict?'.
---
# Skill Consistency Check

Finds places where a skill package contradicts itself — one file requires
what another forbids, two limits disagree, or following one rule forces a
step another rule bans — so an agent obeying every line literally cannot
succeed. Detection is done by independent LLM detectors reading the text
directly; two stdlib-only Python scripts do the deterministic parts
(grouping, merging, verdict, report).

Two detectors, each validated in blind experiments:

| Detector | Spec | What it does |
|---|---|---|
| Read-through | `references/detector-read.md` | Reads the files and reports conflicts |
| Walk-through | `references/detector-simulate.md` | Acts as the agent through 3–5 situations and reports where the next step cannot be followed |

Run every `python3 scripts/…` command from this skill's root directory
(the directory holding this SKILL.md). The scripts need only Python 3.

## Hard rules

<!-- gate: skill-consistency-check.hard-rules -->
- Never install anything (no pip, no package manager, no downloads).
- Never create or modify any file inside the checked skill folder. All
  output goes to a run directory outside it; `scripts/merge_report.py`
  refuses an output path inside the target.
- Never fix the findings. The check reports; the maintainer decides.
<!-- /gate -->

## Procedure

### 1. Target and run directory

The target is one skill folder path (the folder holding its SKILL.md);
resolve it to an absolute path. Create a fresh run directory outside it
(for example with `mktemp -d`) and note its absolute path; `<run>` below
stands for it. If it is inside the target, create another under a
different parent directory.

### 2. Plan the groups

<!-- gate: skill-consistency-check.plan-groups -->
Run the planner with the target as its only argument:

```bash
python3 scripts/plan_groups.py "<target>" > "<run>/plan.json"
```

Exit 0 = plan written. Exit 2 = the path is bad or the folder has no
SKILL.md at its root — relay the stderr message to the user and stop.
Read `<run>/plan.json`:

- `groups.read` — the file lists for read-through detectors.
- `groups.simulate` — the file lists for walk-through detectors.
- `grouped` — `false` means each list is the whole package (at or under
  30,000 estimated tokens); `true` means the package was split into
  groups aimed at 25,000 tokens each, each carrying SKILL.md, agents/
  files and the files SKILL.md cites, with the two groupings offset.
- `over_limit` — `true` when some group still exceeds 25,000 tokens
  (the core alone is too large, or a single large file needs a group of
  its own); the report then warns that the run is over the validated
  size.

Only Markdown files other than README*.md are checked: the package is
every `*.md` file under the target except README files, which are for
humans. Scripts and other non-Markdown files are not read.
<!-- /gate -->

### 3. Dispatch the detectors

<!-- gate: skill-consistency-check.dispatch-detectors -->
Choose the model first (step 4). Then **dispatch N independent subagents
in one message**, so the host runs them concurrently:

- one read-through detector per entry in `groups.read`, output
  `<run>/read-<i>.json`;
- one walk-through detector per entry in `groups.simulate`, output
  `<run>/simulate-<i>.json`.

`<i>` is the 1-based position of the group in its list (first group = 1).
These names are binding: `scripts/merge_report.py` matches each file to
its planned group by name and refuses a run with a missing group or an
unexpected name.

Describe and dispatch this abstractly as "dispatch N subagents" — the
wording maps onto whatever concurrent-subagent facility the host
provides (Claude Code, Codex, …). If the host cannot run them in
parallel, run each as a fresh subagent one after another. Each detector
must have its own fresh context: detections produced in your own context
are not independent and are not what was validated; if the host has no
subagents at all, say so to the user and stop.

Each detector gets, as paths (not file contents):

1. Its spec: the absolute path of `references/detector-read.md` or
   `references/detector-simulate.md`, with the instruction "Read this
   spec and follow it exactly."
2. The target path (the package root that `file` fields are relative to).
3. Its exact file list, copied from the plan entry — nothing added or
   removed. Reading order is not specified; leave it to the detector.
4. Its output JSON path in the run directory.

Detectors write only their output file. After all return, confirm each
output file exists and parses as JSON with a `findings` list. Re-dispatch
a detector whose file is missing or malformed once; if it fails again,
tell the user which group went unchecked and stop — a run with an
unchecked group has no verdict.
<!-- /gate -->

### 4. Model

<!-- gate: skill-consistency-check.model-record -->
Use the host's mid-tier or stronger model for the detectors, never the
smallest tier: in the experiments the smallest tier stopped after 1–3
findings and missed most planted contradictions.

Record the exact model identifier the detectors ran on, as the host
exposes it to the running agent — the model id in your own system or
environment information when the detectors run on your model, or the
host's model setting you chose for the subagents. Copy it character for character; never paraphrase or shorten it
(a shortened family name reads as a different model). If the exact id
is not observable, record `unknown` — step 6 then prints the
not-validated warning — and tell the user the model could not be
observed. Step 6 needs this value.
<!-- /gate -->

### 5. Thorough mode (opt-in only)

Run it only when the user asks for a thorough check. Each method runs
twice: dispatch two read-through detectors per `groups.read` entry and
two walk-through detectors per `groups.simulate` entry, all independent.
The first run writes `read-<i>.json` / `simulate-<i>.json` as usual; the
second writes `read-<i>-2.json` / `simulate-<i>-2.json`. The default is
one run per method.

### 6. Merge and report

<!-- gate: skill-consistency-check.merge-report -->
```bash
python3 scripts/merge_report.py --target "<target>" --plan "<run>/plan.json" \
  --findings <run>/read-*.json <run>/simulate-*.json \
  --model "<model id from step 4, or unknown>" --out "<run>"
```

Pass every detector output file to `--findings`. The script merges
duplicate findings, sets the verdict and writes
`<run>/consistency-report.md` and `<run>/consistency-report.json`.
Exit 0 = pass, exit 1 = needs revision (a result, not an error),
exit 2 = error: no report was written and there is no verdict. Relay the
stderr message to the user; when it names missing groups or bad file
names, re-dispatch those detectors with the correct output path and run
this step again. On exit 2, never present a verdict.
<!-- /gate -->

### 7. Present the result

<!-- gate: skill-consistency-check.present-verdict -->
Read `<run>/consistency-report.md` and present it in the user's language:

- The verdict. Only high-confidence findings block ("needs revision");
  medium and low findings are advisory.
- Each finding with both sides as file:line, the quoted text, and the
  one-sentence reason — high first, then medium and low marked advisory.
- The "Not checked together" list when the package was grouped: those
  file pairs were never read in the same group, so contradictions
  between them could be missed.
- The over-limit warning when present: at least one group exceeded the
  validated size.
- The known limits: conditional and multi-step contradictions may be
  missed.
- The model line, and the warning when the model differs from the
  validation reference.

Give the report's path in the run directory. Do not edit the target.
<!-- /gate -->

## Validated on

Validated on: Claude Sonnet (200k context) on skill packages of about 25,000 tokens; other models are unvalidated until they pass the regression corpus.

The regression corpus (planted contradictions with answer keys and a
scoring helper) lives in this plugin's `tests/consistency-check-corpus/`
folder. Before relying on a different model, run the check on the corpus
and score it there.
