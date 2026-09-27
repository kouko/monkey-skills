# Evaluation Protocol Reference

Purpose: The complete evaluation workflow for skill-creator-advance, extracted from SKILL.md for token efficiency. SKILL.md keeps only routing pointers; this reference holds the full procedural detail.

---

## Do NOT Load Guards

**SKILL.md embedding instructions include explicit guards at these points:**

- **After Step 1 (Choosing Your Eval Path)**: "Only read this reference if you selected the Full eval path. Quick path users stop here."
- **Before Step 1 (Spawn all runs)**: "Do NOT load this reference until you have decided on Full eval path and prepared eval_metadata.json for each test case."
- **Before Step 3 (Self-assessment pass)**: "Do NOT load `references/iteration-automation.md` until all runs have completed and you have timing data captured."
- **Before Step 4 (Grade, aggregate)**: "Do NOT load `agents/grader.md` or `agents/analyzer.md` until Step 4 — premature loading burns context on instructions not yet needed."

---

## Phase 1: Choosing Your Eval Path

Not every skill needs the full benchmark treatment. Choose based on complexity:

| | Quick eval path | Full eval path |
|---|---|---|
| **For** | Simple skills (formatters, templates, single-step workflows) whose quality is best judged by looking at the output | Complex skills (multi-step workflows, objective criteria, many moving parts) needing quantitative comparison |
| **Method** | Run 2-3 test cases manually (no subagent spawning); review outputs inline with the user; skip grading and benchmarking; **for improvements, still run baseline comparison**; **for new skills on the quick path: no baseline needed**; iterate on direct user feedback | Spawn parallel subagent runs with baselines; grade with assertions, aggregate benchmarks; structured inline review with markdown reports |

After determining the skill is simple enough for the quick path, if still uncertain, start with the quick path — you can always escalate if it isn't giving enough signal. **Evaluation-first (full eval path) remains the default for new skills of unknown complexity.**

---

## Phase 2: Full Eval Path — Complete Sequence

The full eval path follows this sequence — don't stop partway through. Do NOT use `/skill-test` or any other testing skill.

Put results in `<skill-name>-workspace/`, a sibling of the skill directory, organized by iteration (`iteration-1/`, `iteration-2/`, etc.) and, within that, a directory per test case (`eval-0/`, `eval-1/`, etc.). Create directories as you go, not upfront.

### Step 1: Spawn all runs (with-skill AND baseline) in the same turn

For each test case, spawn multiple subagent runs per configuration to enable statistical aggregation. Default: **3 runs per configuration** (with-skill and baseline each). Don't spawn the with-skill runs first and come back for baselines later — launch everything at once so it all finishes around the same time.

**With-skill runs** (repeat for runs 1..N):
```
Execute this task:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Input files: <eval files if any, or "none">
- Save outputs to: <workspace>/iteration-<N>/eval-<ID>/with_skill/run-<R>/outputs/
- Outputs to save: <what the user cares about — e.g., "the .docx file", "the final CSV">
```

**Baseline runs** (same prompt, repeat for runs 1..N, baseline depends on context):
- **Creating a new skill**: no skill at all. Same prompt, no skill path, save to `<workspace>/iteration-<N>/eval-<ID>/without_skill/run-<R>/outputs/`.
- **Improving an existing skill**: the old version. Before editing, snapshot the skill (`cp -r <skill-path> <workspace>/skill-snapshot/`), then point the baseline subagent at the snapshot. Save to `<workspace>/iteration-<N>/eval-<ID>/old_skill/run-<R>/outputs/`.

Write an `eval_metadata.json` per test case (assertions should be drafted BEFORE spawning runs if possible; can be empty for exploratory runs). Give each eval a descriptive name based on what it's testing — not just "eval-0" — and use it for the directory too. If this iteration uses new or modified eval prompts, create these files for each new eval directory — they don't carry over from previous iterations.

```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name-here",
  "prompt": "The user's task prompt",
  "assertions": []
}
```

### Step 2: While runs are in progress, draft or finalize assertions

Use the wait productively: draft quantitative assertions for each test case and explain them to the user. If assertions already exist in `evals/evals.json`, review them and explain what they check.

Good assertions are objectively verifiable, with descriptive names that read clearly in the benchmark report — someone glancing at the results should immediately understand what each one checks. Subjective skills (writing style, design quality) are better evaluated qualitatively — don't force assertions onto things that need human judgment.

**Important:** Update `eval_metadata.json` with assertions BEFORE the grader runs in Step 4. The grader reads `eval_metadata.json` directly for its assertion list. If assertions are drafted after runs spawn, ensure they are written to `eval_metadata.json` before Step 4 begins. Also sync to `evals/evals.json` (where the field is named `expectations`) for the master eval record.

### Step 3: As runs complete, capture timing data

When each subagent task completes, you receive a notification containing `total_tokens` and `duration_ms`. Save this data immediately to `timing.json` in the run directory:

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

**Note:** The task notification provides `total_tokens` and `duration_ms` as base fields. `total_duration_seconds` is computed as `duration_ms / 1000`. For the complete timing.json schema including executor/grader timestamps (captured from other sources during execution), see [references/schemas.md](references/schemas.md).

This is the only opportunity to capture this data — it comes through the task notification and isn't persisted elsewhere. Process each notification as it arrives rather than trying to batch them.

### Step 3.5: Self-assessment pass

Before grading and presenting results to the human, perform a quick automated check on each output. Read `references/iteration-automation.md` for the full protocol. In brief:
- Read each test case's output and check for obvious defects (empty output, format violations, crash artifacts)
- If a defect is clearly caused by a skill instruction issue, fix the skill and rerun that test case once
- Capture timing data for the rerun and save to `timing-rerun.json` in the run directory (NOT to the original `timing.json` — keep original for baseline comparison)
- Log results to `self_assessment.json` in each test case directory
- One pass only — no infinite repair loops

### Step 4: Grade, aggregate, and present results

Once all runs are done:

1. **Grade each run** — spawn a grader subagent (or grade inline) that reads `agents/grader.md` and evaluates each assertion against the outputs. Save results to `grading.json` in each run directory. The grading.json expectations array must use the fields `text`, `passed`, and `evidence` (not `name`/`met`/`details` or other variants). Check programmatically-checkable assertions with a script rather than eyeballing — faster, more reliable, reusable across iterations.

2. **Check for regressions** (iteration 2+) — compare results against the previous iteration (`references/iteration-automation.md` has the full protocol); lead with any regressions when reporting to the user.

3. **Aggregate into benchmark** — run the aggregation script from the skill-creator-advance directory:
   ```bash
   python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
   ```
   This produces `benchmark.json` and `benchmark.md` with pass_rate, time, and tokens for each configuration, with mean +/- stddev and the delta. If generating benchmark.json manually, see `references/schemas.md` for the exact schema.
   Put each with_skill version before its baseline counterpart.

4. **Do an analyst pass** — read the benchmark data and surface patterns the aggregate stats might hide. See `agents/analyzer.md` (the "Analyzing Benchmark Results" section) for what to look for — non-discriminating assertions, high-variance (possibly flaky) evals, time/token tradeoffs.

5. **Present results inline** — For each test case, show the results directly in the conversation:

   ```markdown
   ### Test Case: {eval_name}
   **Prompt:** {the task prompt}
   **Output:** {summary of key output files or inline content}
   **Grades:** {assertion pass/fail results with evidence, if graded}
   **Previous:** {what changed from last iteration, if iteration 2+}
   ```

   After presenting all test cases, show the benchmark summary (pass rates, timing, token usage).

6. **Save a markdown report** to `<workspace>/iteration-N/review.md` containing all test case results and benchmark data, persisting them for cross-iteration comparison.

7. **Ask for feedback** — ask the user for feedback on each test case; focus on specific complaints — no comment means it looked fine.

---

### Minimum Improvement Threshold

Proceed to the next iteration only if the skill's eval pass rate exceeds the baseline by at least **15%**. If not met, refine the eval cases or the skill and rerun.

**For new skills on the quick path:** no baseline is needed. Run 2-3 test cases manually and iterate on direct user feedback.

## Iteration Loop

After improving the skill:

1. Apply your improvements to the skill
2. Rerun all test cases into a new `iteration-<N+1>/` directory, including baseline runs. If you're creating a new skill, the baseline is always `without_skill` (no skill) — that stays the same across iterations. If you're improving an existing skill, use the snapshot of the current version (taken before editing) as the baseline for all iterations. This ensures consistent comparison against the version being improved.
3. Present results inline and save to `review.md`, noting changes from previous iteration
4. Wait for the user to review and tell you they're done
5. Read the new feedback, improve again, repeat

Keep going until:
- The user says they're happy
- The feedback is all empty (everything looks good)
- You're not making meaningful progress

---

## Advanced: Blind Comparison

For a more rigorous comparison between two versions of a skill (the user asks "is the new version actually better?"), read `agents/comparator.md` and `agents/analyzer.md`: give two outputs to an independent agent without telling it which is which, let it judge quality, then analyze why the winner won. Optional, requires subagents; the human review loop is usually sufficient.

> **Boundary note vs `skill-dev-toolkit:skill-tuning`**: the blind comparator uses an LLM subagent as judge — fast and cheap, but inherits LLM-as-judge limitations (verbosity bias, position bias, weak signal on taste-sensitive output dimensions like voice / tone / creative quality). For taste-sensitive A/B that needs reliable preference signal, use `skill-tuning` instead — it uses **human** judgment per iteration and accumulates a preference log. Rule of thumb: blind comparator for objective / structured outputs (file transforms, code generation, fixed-format generators); `skill-tuning` for subjective / creative outputs (writing style, design feel, persuasive copy).