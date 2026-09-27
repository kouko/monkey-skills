---
name: skill-creator-advance
description: |
  Creates skills, redesigns them, or optimizes description triggering. Triggers: "build a skill", "make a slash command", "redesign", "improve". About to create a new skill or improve an existing one.
---

# Skill Creator Advance

**Process pattern.** This skill follows the Process pattern: every skill it produces must have a clear lifecycle — create → test → evaluate → improve → repeat.

A skill for creating new skills and iteratively improving them.

The core loop: **draft → test → review → improve → repeat**.

- Decide what the skill should do → write a draft
- Create test prompts → run claude-with-the-skill on them
- Evaluate results (qualitative review + quantitative assertions)
- Rewrite based on feedback → repeat until satisfied
- Optionally optimize the description for better triggering

Your job is to figure out where the user is in this process and help them progress — from scratch or from an existing draft. Be flexible: if they say "just vibe with me", skip the formal eval machinery.

## NEVER (anti-patterns to avoid)

These anti-patterns recur across skill creation sessions. Each has a WHY clause explaining the failure mode — violating it will waste tokens or produce a broken skill.

1. **Never write workflow steps in the description.** The description is a trigger; SKILL.md body is the instruction. When the description summarizes the workflow, Claude may skip reading SKILL.md and follow the description instead — which lacks nuance. [WHY: description loads in system prompt at session start; body loads only on activation. If description = workflow, body becomes documentation Claude may never read.]

2. **Never use first/second person in the description.** The description is injected into the system prompt; pronoun inconsistency causes selection problems. [WHY: Anthropic best-practices doc has an explicit Warning block; "I can help you" confuses the matcher.]

3. **Never create a skill without validating the need.** Every skill must pass Pre-Creation Gates (Gate 1 worth-it check, Gate 2 smallest-end-state check) — except on the quick eval path, where only Gate 2 (smallest-end-state) is answered inline and the full reference protocol is skipped. [WHY: building the wrong skill has permanent cost — maintenance burden without solving anything.]

4. **Never spawn baselines after with-skill runs.** Always launch baseline runs BEFORE or WITH with-skill runs in the same workflow turn. Spawning baselines after with-skill causes straggler waits and uneven timing data. [WHY: parallel execution ensures comparable conditions; baseline must match with-skill runtime environment. Evaluation-first workflows should run baselines first to establish ground truth before testing skill effectiveness. Exception: new skills on the quick eval path need no baseline.]

5. **Never modify the description without trigger eval queries.** Manually tweaking the description without a proper 20-query eval set (8-10 should-trigger + 8-10 should-not-trigger) is guessing and leads to poor triggering. The Description Optimization workflow is the approved method for creating eval queries and optimizing descriptions. [WHY: description is the primary triggering mechanism; without objective eval, you optimize blind. The structured workflow ensures you create valid eval queries before optimizing.]

6. **Never skip the iteration loop.** A skill is never "done" after one pass. The loop (improve → rerun → present → feedback → repeat) is where quality converges. [WHY: first drafts are always under-optimized; patterns emerge only after multiple iterations.]

7. **Never nest subdirectories inside skill subdirectories.** A skill may contain `SKILL.md` plus single-level subdirectories (scripts/, references/, assets/, agents/); those subdirectories must themselves be flat. [WHY: Anthropic skill convention; violation is caught by `.claude/hooks/validate-skill-folder-structure.sh`.]

---

## Communicating with the user

Users range from non-technical to expert. Gauge familiarity from context cues: "evaluation" and "benchmark" are generally OK; for "JSON" and "assertion", look for serious cues the user knows the term before using it without explanation. When in doubt, briefly define terms inline — better to over-explain once than to lose someone.

---

## Creating a skill

> **Evaluation-first is the default path for new skills.** Quick path (2-3 test cases, no baseline) is permitted ONLY for simple skills (formatters, templates, single-step workflows), when success criteria are already documented, or for one-off prototypes — document the skip reason in evals/evals.json. **Determine simplicity first; only after confirming the skill is simple enough, if still uncertain, start with the quick path — you can always escalate.**

### Pre-Creation Gates (recommended; skip only with stated reason)

**Do NOT Load:** Skip this reference if the skill qualifies for the quick eval path (see the eval-path note above) — in that case, still answer the Gate 2 questions inline (they are short); the full reference protocol is only for the full creation workflow. Load only when starting a full skill creation workflow.

The full Pre-Creation Gates protocol (Gate 1 Worth-it check, Gate 2 Smallest-end-state check, Gate 3 User-input check) is in [references/pre-creation-gates.md](references/pre-creation-gates.md).

### Capture Intent and Interview

**Do NOT Load:** Skip this reference if the user's request is simply "help me write a skill" without any specific workflow to capture.

The Capture Intent questions (what the skill enables, when it should trigger, expected output format, test-case decision) and the Interview and Research protocol are in [references/capture-intent.md](references/capture-intent.md).

### Plan the Skill Structure

Before writing any file, decide the target skill's file layout. Progressive disclosure works only when it is planned up front, not retrofitted after the body overflows:

1. **List the content blocks** gathered from the interview: workflow steps, domain knowledge, examples, schemas, scripts, agent prompts.
2. **Assign each block a home**:
   - **SKILL.md body** — the core workflow the agent must follow on every invocation
   - `references/` — detail loaded only when needed (protocols, schemas, design patterns); one file per concern, each with a stated load trigger ("read when X")
   - `scripts/` — deterministic or repetitive code the skill runs
   - `assets/` — templates and static files
   - `agents/` — subagent instruction files
3. **Estimate the SKILL.md body size.** If the inline blocks total over ~3,750 words, move more into references now — splitting after drafting wastes a rewrite.
4. **Show the tree to the user** before writing files:

   ```
   my-skill/
   ├── SKILL.md          # core workflow + routing (~3,000 words)
   ├── references/
   │   ├── protocol.md   # read when running the full workflow
   │   └── schemas.md    # read when writing grading.json
   └── scripts/
       └── convert.py
   ```

Layout follows the flat-structure and progressive-disclosure conventions in [references/skill-writing-guide.md](references/skill-writing-guide.md). For improvements to existing skills, reuse the existing structure unless the redesign justifies a new one.

### Step 0: Evaluation-First (full eval path)

**Do NOT Load:** Skip this section if you selected the quick eval path. Load only when doing full benchmark with baseline comparison. The basic baseline running instructions are included above; see [references/eval-protocol.md](references/eval-protocol.md) for the detailed protocol for multiple runs, timing capture, and advanced features.

> **Note:** This section describes the full Evaluation-First path (Step 0). The Quick eval path is an alternative to this full path, used only for simple skills (when success criteria are already documented, or for one-off prototypes). The two paths are compared in the Choosing Your Eval Path section below.

**Before writing the skill draft, build and validate evaluation cases:**

1. **Extract 3+ eval cases** from real user pain points or observed gaps
   - Draw from: past support tickets, forum threads, personal workflow pain points
   - Each case should be a concrete task a user would type
   - Document why each case needs the skill (what fails without it)

2. **Run baseline (no skill)** on all eval cases
   - For each eval case, run the task prompt WITHOUT the skill
   - **Creating a new skill**: no skill at all - just run the prompt on base Claude
   - **Improving an existing skill**: snapshot the current version first (`cp -r <skill-path> <workspace>/skill-snapshot/`), then run the prompt on the snapshot
   - Record exact failure modes and output quality in `<workspace>/iteration-<N>/eval-<ID>/without_skill/run-<R>/outputs/` (new skill) or `<workspace>/iteration-<N>/eval-<ID>/old_skill/run-<R>/outputs/` (existing skill)
   - Note which parts Claude skips, guesses, or gets wrong

3. **Write minimal SKILL.md** that addresses the eval case gaps
   - Keep instructions lean; focus on what the skill enables
   - Do NOT include workflow steps in description

4. **Run initial with-skill tests** on all eval cases (single run each) to compute eval pass rate
   - For each eval case, run the task prompt WITH the draft skill
   - Score outputs against assertions (if any) or qualitative criteria
   - Compute pass rate as fraction of eval cases where skill output meets criteria

5. **Proceed only if eval pass rate ≥ baseline + 15%**
   - If not met, refine the eval cases or the skill and rerun
   - Document baseline metrics for future comparison

> **Why this step**: Skills built without validation often solve imagined needs rather than real problems. Evaluation-first ensures every skill addresses a documented gap.

> **Reference**: Full evaluation protocol (including the 15% improvement threshold and iteration loop) is in [references/eval-protocol.md](references/eval-protocol.md)

### Step 1: Write the SKILL.md

Based on the user interview and the planned structure above, fill in these components:

- **name**: Skill identifier (lowercase, hyphens only, 1-64 chars)
- **description**: What it does + when to use it (use positive specificity; see Description Best Practices below and the §House description standard — avoid "Do NOT use for X" negation)
- **compatibility**: Required tools, dependencies (optional)
- **license**: SPDX identifier or path to LICENSE file (optional)
- **allowed-tools**: Space-separated pre-approved tools (e.g., "Bash(git *) Read"; optional)
- **metadata**: Optional key-value pairs (version, author, etc.)
- **the rest of the skill :)**

### Description Best Practices

Before drafting the description, read
[references/description-design.md](references/description-design.md) —
it owns the design patterns: WHAT+WHEN (not WHAT+WORKFLOW),
third-person voice, length guidance, a validation checklist, and
examples. The house standard for descriptions is defined in
description-design.md §Principles (Principles 1–4). Principle 4
specifically covers length requirements.

### Skill Writing Guide

**Do NOT Load:** Load when planning a new skill's file layout. Skip if you are only optimizing an existing skill's description or making minor tweaks.

For the anatomy of a skill, flat-structure rules (no nested subdirectories), progressive disclosure, plugin ecosystem conventions, user-input patterns (AskUserQuestion), and writing patterns — see [references/skill-writing-guide.md](references/skill-writing-guide.md).

### Quick eval path: Testing

**Do NOT Load:** Read [references/improvement-workflows.md](references/improvement-workflows.md) §Quick eval path: Testing only when running the Quick eval path. It holds the test-prompt workflow, the evals.json starter schema, and the quick-path iteration loop.

---

## Improving an Existing Skill

When a user asks to "improve" or "optimize" an existing skill, **first determine which kind of improvement** before doing any work. Three distinct shapes — they need different tools:

### Router: Identify the Improvement Type

Ask the user to clarify (or infer from their phrasing):

| Improvement type | Signal | Handler |
|---|---|---|
| **(a) Token / structure refactor** with output behavior unchanged | "shorten", "reduce tokens", "tidy up", "縮減 SKILL.md", "整理結構" — and **no behavior change desired** | Hand off to `skill-dev-toolkit:skill-refactor`. Do not handle here. |
| **(b) Output quality / variant exploration** with human judgment | "test different phrasings", "improve outputs", "A/B variants", "輸出風格", "我來選哪個比較好" — taste-sensitive output dimensions | Hand off to `skill-dev-toolkit:skill-tuning`. Do not handle here. |
| **(c) Structural change** — add / split / merge phases, change agent decomposition, change input/output contract | "rewrite", "redesign", "add a phase", "split this skill", "重新設計", "拆 skill" | Use the Structural Rewrite Flow below (steps 1–4), then evaluate using the iteration loop (quick or full eval path, depending on complexity). Skip Step 0 (Evaluation-First) — reuse existing eval cases from the original skill. |
| **(d) Description optimization** | "improve description", "optimize triggering", "better trigger accuracy", "改善說明", "最佳化觸發" | Handle internally using the Description Optimization section below |

If the user's intent is unclear, ask them to clarify which of (a), (b), (c), or (d) applies. Do **not** default into the creation flow without confirming — picking the wrong tool wastes time on the wrong type of work.

### Case (c): Structural Rewrite Flow

**Do NOT Load:** Read [references/improvement-workflows.md](references/improvement-workflows.md) §Case (c): Structural Rewrite Flow only when the router above identified case (c) — a structural change (add/split/merge phases, change agent decomposition, change input/output contract).

For case (c), use that flow (steps 1–4). **Skip Step 0 (Evaluation-First)** — the skill already has eval cases from its original creation or previous improvements; reuse those. Cases (a) and (b) hand off to the dedicated sibling skills above and do **not** use these steps. Case (d) is handled internally using the Description Optimization section below.

---

**Do NOT Load:** Do not load `references/eval-protocol.md` beyond its Phase 1 decision table until you have decided on the Full eval path (quick path users read only Phase 1, then stop — see that reference's guard notes).

### Choosing Your Eval Path

Not every skill needs the full benchmark treatment. Choose based on complexity:
| | Quick eval path | Full eval path |
|---|---|---|
| **For** | Simple skills (formatters, templates, single-step workflows) whose quality is best judged by looking at the output | Complex skills (multi-step workflows, objective criteria, many moving parts) needing quantitative comparison |
| **Method** | Run 2-3 test cases manually (no subagent spawning); review outputs inline with the user; skip grading and benchmarking; **for improvements, still run baseline comparison; for new skills on the quick path, no baseline needed**; iterate on direct user feedback | Spawn parallel subagent runs with baselines; grade with assertions, aggregate benchmarks; structured inline review with markdown reports |

> **Note:** The "when in doubt, start with quick path" guidance applies only AFTER you have determined the skill is simple enough for the quick path (see the Choosing Your Eval Path section for details). After making that determination, if still uncertain, start with the quick path — you can always escalate if it isn't giving enough signal.


For the full eval protocol (Steps 1-4: spawn runs, draft assertions, capture timing, grade/aggregate/present), see [references/eval-protocol.md](references/eval-protocol.md) — it owns the complete sequence including directory structure, baseline runs, timing capture, self-assessment pass, and the 15% improvement threshold.

Put results in `<skill-name>-workspace/`, a sibling of the skill directory, organized by iteration (`iteration-1/`, `iteration-2/`, etc.) and, within that, a directory per test case (`eval-0/`, `eval-1/`, etc.). Create directories as you go, not upfront.

## Improving the skill

**Do NOT Load:** Read [references/improvement-workflows.md](references/improvement-workflows.md) §Improving the skill (the iteration loop) only after presenting eval results, when turning user feedback into skill changes. It holds the improvement principles (generalize, keep lean, explain why, bundle repeated work) and the full-path iteration loop; the quick-path loop is in its Quick eval path section.

---

## Advanced: Blind comparison

**Do NOT Load:** Read [references/improvement-workflows.md](references/improvement-workflows.md) §Advanced: Blind comparison only when the user asks whether the new version is actually better. It holds the comparator workflow and the boundary note vs `skill-dev-toolkit:skill-tuning`. Optional — the human review loop is usually sufficient.

---

## Description Optimization

**Do NOT Load:** Skip this entire section if you are not optimizing a skill's description. Load only when you have a completed skill and want to improve its triggering accuracy.

The frontmatter description is the primary mechanism determining whether Claude invokes a skill. After creating or improving a skill, offer to optimize it for better triggering accuracy.

For the full description optimization workflow, see [references/description-optimization.md](references/description-optimization.md).

> **Note:** The Description Optimization workflow satisfies NEVER #5 by generating a validated 20-query eval set before optimizing. If modifying descriptions manually outside this workflow, you must still follow all 7 NEVER rules.

### House description standard (the optimization target)

Any description you write or optimize MUST follow the house standard in [references/description-design.md](references/description-design.md): §Principles 1–4 (Principle 4 owns the length numbers: normal ≤150 target / 250 soft lint line; router/CONDITIONAL ≤500 with firing evidence), plus §Multilingual keyword belt and the context-listing-budget note. The optimization loop must keep `best_description` within these rules.

For the full step-by-step workflow, see [references/description-optimization.md](references/description-optimization.md) — it owns the complete sequence including eval query generation, user review, the optimization loop, and result application.

---

### Packaging

After the skill is complete, package it for distribution:

```bash
python -m scripts.package_skill <path/to/skill-folder>
```

This creates a `.skill` file that can be shared and installed.

---

## Platform Adaptations

The instructions above assume Claude Code. If you're running in **Claude.ai** or **Cowork**, some mechanics change (no subagents, no browser, etc.). Read `references/platform-adaptations.md` for the platform-specific adjustments.

---

## Reference files

The agents/ directory holds instructions for specialized subagents — read when spawning the relevant one.

- `agents/grader.md` — How to evaluate assertions against outputs
- `agents/comparator.md` — How to do blind A/B comparison between two outputs
- `agents/analyzer.md` — How to analyze why one version beat another

The references/ directory has additional documentation:
- `references/pre-creation-gates.md` — Pre-Creation Gates protocol (Gate 1/2/3)
- `references/capture-intent.md` — Capture Intent questions and Interview/Research protocol
- `references/schemas.md` — JSON structures for evals.json, grading.json, etc.
- `references/plugin-conventions.md` — Plugin ecosystem conventions, directory structures, slash command format
- `references/iteration-automation.md` — Self-assessment and auto-regression detection protocols
- `references/eval-methodology.md` — Why the eval workflow is designed this way (optional)
- `references/platform-adaptations.md` — Claude.ai and Cowork platform-specific adjustments
- `references/mermaid-usage-guidelines.md` — When to use Mermaid diagrams vs prose in skill authoring, syntax conventions, cost-benefit framework
- `references/eval-protocol.md` — Complete evaluation workflow (full eval path detail)
- `references/improvement-workflows.md` — Quick-path testing, structural rewrite flow, iteration loop, blind comparison
- `references/description-optimization.md` — Description optimization workflow
- `references/description-design.md` — Description design patterns and best practices
- `references/evaluation-design.md` — Evaluation case design template
- `references/asking-user-questions.md` — Hardened AskUserQuestion patterns
- `references/writing-lean.md` — Token economy and lean writing patterns
- `references/process-pattern.md` — Core process pattern lifecycle
- `references/skill-writing-guide.md` — Skill anatomy, flat-structure conventions, progressive disclosure

---

**Core loop reminder:** Draft → Test → Evaluate (inline review + evals) → Improve → Repeat → Package. Good luck!
