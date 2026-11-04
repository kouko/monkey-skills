---
name: skill-consistency-check
description: |
  Finds rules that contradict each other inside a skill folder. Use for 'check this skill for contradictions' or 'do these instructions conflict?'.
---
# Skill Consistency Check

Finds places where a skill package contradicts itself — one file requires
what another forbids, two limits disagree, or following one rule forces a
step another rule bans — so an agent obeying every line literally cannot
succeed. Independent LLM detectors discover candidates by reading the text;
the reporting caller verifies them before merge. Two stdlib-only Python scripts
do the deterministic parts (grouping, merging, verdict, report).

Two detectors, each calibrated in earlier blind experiments:

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
- `over_limit` — `true` when any actual group exceeds 25,000 estimated
  tokens, including a whole-package group when `grouped` is `false`.
  This conservative nominal reporting bound qualifies the report; it
  does not change the 30,000-token split threshold or prove an accuracy
  cliff at 25,000 tokens.

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
output exists and parses as JSON with a `findings` list; also inspect its
completion message and available tool results. Re-dispatch once with the
same assigned file list if the output is missing or malformed, the detector
explicitly reports unfinished work, or visible reading demonstrably omits
required files or sections. Preserve incomplete output and hand-back outside
the merge globs (e.g. `partial-read-1.json` and `partial-read-1.md`) before
retrying. If the retry fails or remains incomplete, stop before merge and
name the unchecked method/group — no whole-package verdict. Missing tool
detail alone does not prove incompleteness; completed checks with empty
findings remain valid.
<!-- /gate -->

### 4. Model

<!-- gate: skill-consistency-check.model-record -->
Use the host's mid-tier or stronger model for the detectors, never the
smallest tier: in the experiments the smallest tier stopped after 1–3
findings and missed most planted contradictions.

Record the exact model identifier only when the host exposes it for each
detector's runtime. A selected alias, parent `modelUsage`, or copied parent
identifier does not prove a child's identity. If every detector's observed
identifier is identical, copy it character for character for step 6;
never paraphrase or shorten it. Otherwise pass `unknown` and tell the user
the shared detector identity could not be observed. Step 6 retains the
not-validated warning.
`unknown` is report metadata, never a provider model identifier.
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
Before merging, the reporting caller must review every candidate from every
completed detector output, including thorough-mode runs:

1. Preserve each raw JSON file byte-for-byte outside `read-*.json` and
   `simulate-*.json` (e.g. `raw-read-1.json`) before changing a planned file.
2. Read each candidate's cited files in full, plus relevant entry-file and
   delegated authorities. Before subset selection, record in run notes or a reply
   its detector filename/original ID, exact governing entry-file scope/delegation,
   precedence and exception quotes with file:line, or file:line ranges searched
   if none applies. Explain why the claim is supported, excluded or unchecked,
   its shared conditions, and how those qualifications govern it. Duplicates
   may explicitly reuse a record only when claim and qualifications match.
3. Judge the original `why` claim, not a different concern in its side quotes.
   For action conflicts, try a concrete execution obeying both rules; compatible
   execution can refute the claim. Extra keys, aliases or workarounds do not
   reconcile conflicting facts, field definitions or values in the same scope.
   Exclude unsupported or overstated claims (e.g. permission inferred as a duty),
   even if quotes support a narrower concern. Record why retained claims remain
   incompatible or the source-grounded exclusion reason. Never add findings
   from the caller's own context.
4. Only after every candidate's review is recorded, write subsets of each raw
   file's findings to its original planned filename; do not add or rewrite
   findings or change confidence. Use `low` only for uncertainty about a remaining
   incompatibility, never for compatible rules. Reviewed empty `findings` lists
   are valid; never omit a method/group.

If required review cannot finish, including when relevant source is unread
or unavailable, stop before merge, name the unchecked candidates/groups and
give no whole-package verdict. JSON validity alone does not finish review.

```bash
python3 scripts/merge_report.py --target "<target>" --plan "<run>/plan.json" \
  --findings <run>/read-*.json <run>/simulate-*.json \
  --model "<model id from step 4, or unknown>" --out "<run>"
```

Pass every planned group's reviewed output file to `--findings`, including
empty lists and every thorough-mode run. The script merges
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
- The size caution when present: at least one group exceeded the
  conservative nominal reporting bound, even if the package was not split.
- The known limits: conditional and multi-step contradictions may be
  missed; 25,000 estimated tokens is a conservative nominal reporting
  bound, not a proven accuracy cliff.
- The model line, and the warning when the model differs from the
  validation reference.
- Raw-output paths and source-grounded exclusion reasons; explain that earlier
  detector/corpus calibration does not validate this caller-review variant.

Give the report's path in the run directory. Do not edit the target.
<!-- /gate -->

## Validated on

Validated on: Claude Sonnet (200k context) on skill packages of about 25,000 tokens; other models are unvalidated until they pass the regression corpus.

This historical detector/corpus calibration does not validate the step 6 caller
review, even with matching model metadata. The CLI metadata remains unchanged.

The existing validated corpus fixture estimates to 25,135 tokens
(approximately 25k) and is still read whole. The report JSON's
`reference.nominal_reporting_bound_tokens` records the conservative
25,000-token notice bound. The legacy `reference.max_validated_tokens`
key retains 25,000 as a compatibility alias for that nominal bound,
not an empirical maximum or an accuracy ceiling. The plan's `group_max` stays
25,000 as the grouping target and notice bound; `limit` stays 30,000 as
the split threshold. Exceeding the notice bound alone does not establish
that accuracy is worse.

The regression corpus (planted contradictions with answer keys and a
scoring helper) lives in this plugin's `tests/consistency-check-corpus/`
folder. Before relying on a different model, run the check on the corpus
and score it there.
