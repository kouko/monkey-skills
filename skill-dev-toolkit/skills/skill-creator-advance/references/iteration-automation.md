# Iteration Automation Reference

This document describes two automation features that enhance the eval
iteration loop: **self-assessment** (pre-screening before human review)
and **auto-regression detection** (catching quality regressions across
iterations).

---

## Self-Assessment Pass

### Purpose
Before presenting outputs to the human reviewer, perform a quick automated
check to catch obvious defects. This saves the human from reviewing outputs
that are clearly broken and reduces wasted iteration cycles.

### When It Runs
After all test case runs complete (Step 3 timing capture) and before
grading (Step 4). This is a new step inserted between Steps 3 and 4
of the main eval workflow.

### What It Checks

For each test case output, read the output files and check for:

1. **Empty or missing output** — The skill produced no files or only
   empty files in the outputs directory
2. **Format violations** — The output was supposed to be a specific format
   (e.g., markdown with required sections, JSON with required keys) but
   is malformed or missing required structure
3. **Obvious instruction violations** — The skill explicitly says "always
   include X" or "never do Y" and the output violates this
4. **Crash artifacts** — Error messages, stack traces, or partial outputs
   that indicate the skill execution failed midway

### What It Does NOT Check
- Subjective quality (writing style, design aesthetics)
- Nuanced correctness (that's what assertions and human review are for)
- Anything requiring comparison to a baseline

### The Self-Assessment Protocol

1. **Read each output** — Go through every test case's `with_skill/outputs/`
   directory
2. **Flag defects** — For each output, note any issues from the checklist
   above
3. **Decide: fix or skip** — If the defect is clearly caused by a skill
   instruction issue (not a test case edge case), fix the skill and rerun
   that specific test case. If the defect seems like a flaky/environmental
   issue, leave it for human review.
4. **One pass only** — Do NOT iterate. Fix the skill once, rerun once.
   If the rerun still fails, present it as-is. This prevents infinite
   repair loops.
5. **Log what happened** — Save a `self_assessment.json` in each test
   case directory:

```json
{
  "assessed": true,
  "defects_found": [
    {
      "type": "empty_output",
      "description": "No files produced in outputs/",
      "action": "fixed_and_rerun"
    }
  ],
  "skill_modified": true,
  "rerun": true
}
```

If no defects were found:

```json
{
  "assessed": true,
  "defects_found": [],
  "skill_modified": false,
  "rerun": false
}
```

### Presenting Self-Assessment Results

When presenting results to the user, note which test cases went through
self-assessment repair. In the summary, mention:
- "N out of M test cases passed self-assessment without issues"
- "K test cases had defects that were auto-fixed and rerun"
- Brief description of what was fixed

This transparency lets the human know which results are "first attempt"
vs "second attempt after auto-fix."

---

## Auto-Regression Detection

### Purpose
When iterating on a skill (iteration 2+), automatically detect cases
where a previously passing assertion now fails. This catches situations
where fixing one thing inadvertently breaks another.

### When It Runs
After grading is complete for iteration N (N >= 2), before aggregating
the benchmark. Compare the current iteration's grading results against
the previous iteration's.

### The Detection Protocol

1. **Load grading results** — Read `grading.json` from both:
   - Current iteration: `iteration-N/eval-*/with_skill/grading.json`
   - Previous iteration: `iteration-(N-1)/eval-*/with_skill/grading.json`

2. **Match assertions** — For each test case, match assertions by their
   `text` field between the two iterations. Only compare assertions that
   exist in both iterations.

3. **Classify changes** — For each matched assertion pair:
   - PASS → PASS: **Stable** (no action)
   - FAIL → PASS: **Fixed** (good news)
   - PASS → FAIL: **Regression** (flag this)
   - FAIL → FAIL: **Persistent failure** (no change)

4. **Generate regression report** — Save `regression_report.json` in the
   current iteration directory:

```json
{
  "iteration": 3,
  "compared_against": 2,
  "regressions": [
    {
      "eval_name": "descriptive-test-name",
      "eval_id": 1,
      "assertion": "Output includes executive summary section",
      "previous_status": "passed",
      "current_status": "failed",
      "evidence": "The executive summary section was removed in the restructured output"
    }
  ],
  "fixes": [
    {
      "eval_name": "another-test",
      "eval_id": 2,
      "assertion": "Chart has labeled axes",
      "previous_status": "failed",
      "current_status": "passed"
    }
  ],
  "stable_pass": 8,
  "stable_fail": 1,
  "summary": "1 regression, 1 fix, 8 stable passes, 1 persistent failure"
}
```

### Presenting Regression Results

When reporting to the user after grading:

1. **Lead with regressions** if any exist — these are the most actionable:
   > "Warning: 1 regression detected — 'Output includes executive summary
   > section' was passing in iteration 2 but now fails in iteration 3."

2. **Then mention fixes** — positive reinforcement:
   > "1 previously failing assertion now passes: 'Chart has labeled axes'"

3. **Include in benchmark.md** — Add a "Regression Analysis" section to
   the benchmark markdown output showing the full comparison table.

4. **Do NOT auto-fix regressions** — This is an information layer only.
   The human decides whether the regression is acceptable (intentional
   trade-off) or needs to be fixed in the next iteration. Sometimes a
   regression is expected when changing the skill's approach.

### Edge Cases

- **New assertions** added in the current iteration have no previous
  data — skip them in the comparison, note them as "New (no baseline)"
- **Removed assertions** that existed previously but not now — note them
  as "Removed (was PASS/FAIL)" so the human knows coverage changed
- **Different test cases** between iterations — only compare test cases
  that exist in both iterations (matched by eval_id or eval_name)
