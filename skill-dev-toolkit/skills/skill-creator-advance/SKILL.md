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

3. **Never create a skill without validating the need.** Every skill must pass Pre-Creation Gates (Gate 1 worth-it check, Gate 2 smallest-end-state check). Skipping these produces skills that solve imagined needs rather than real problems. [WHY: building the wrong skill has permanent cost — maintenance burden without solving anything.]

4. **Never spawn baselines after with-skill runs.** Always launch baseline runs BEFORE or WITH with-skill runs in the same workflow turn. Spawning baselines after with-skill causes straggler waits and uneven timing data. [WHY: parallel execution ensures comparable conditions; baseline must match with-skill runtime environment. Evaluation-first workflows should run baselines first to establish ground truth before testing skill effectiveness. Exception: new skills on the quick eval path need no baseline.]

5. **Never modify the description without trigger eval queries.** Manually tweaking the description without a proper 20-query eval set (8-10 should-trigger + 8-10 should-not-trigger) is guessing and leads to poor triggering. The Description Optimization workflow is the approved method for creating eval queries and optimizing descriptions. [WHY: description is the primary triggering mechanism; without objective eval, you optimize blind. The structured workflow ensures you create valid eval queries before optimizing.]

6. **Never skip the iteration loop.** A skill is never "done" after one pass. The loop (improve → rerun → present → feedback → repeat) is where quality converges. [WHY: first drafts are always under-optimized; patterns emerge only after multiple iterations.]

7. **Never nest subdirectories inside skill subdirectories.** A skill may contain `SKILL.md` plus single-level subdirectories (scripts/, references/, assets/, agents/); those subdirectories must themselves be flat. [WHY: Anthropic skill convention; violation is caught by `.claude/hooks/validate-skill-folder-structure.sh`.]

---

## Communicating with the user

Users range from non-technical to expert. Gauge familiarity from context cues: "evaluation" and "benchmark" are generally OK; for "JSON" and "assertion", look for serious cues the user knows the term before using it without explanation. When in doubt, briefly define terms inline — better to over-explain once than to lose someone.

---

## Creating a skill

### Pre-Creation Gates (recommended; skip only with stated reason)

**Phase 1/3: Initial validation** — Before intake / interview / drafting, run two lightweight gates against the user's request — one or two focused questions each; they prevent shipping a skill that should not have been built.

**Gate 1 — Worth-it check** —
applicable when the user proposes ≥2 skills at once, or one skill
with multiple supporting claims ("we need this because A, B, and
C"). Triage each proposed item into KEEP / DEFER / DROP, judging it
on evidence grounding (is the need real and recurring, not
speculative?) and YAGNI (would you build it now?). A single skill
with a single load-bearing reason keeps this gate cheap — confirm
the reason holds, then move to Gate 2.

**Gate 2 — Smallest-end-state check** —
applicable to **every** new skill proposal, single or multi. The
three questions:

1. What's the smallest end state that solves this? (Could it be 0
   functions — not really a skill, just a one-off prompt? One
   existing skill plus a new section instead of a new skill?)
2. Does this result in less total skill-ecosystem code than not
   building it? (A new skill adds surface area; default "no"
   unless it subtracts other artifacts or replaces ad-hoc prompts.)
3. What does this skill make obsolete? (If nothing, the rationale
   is purely additive — apply deletion-first skepticism as for any
   feature add.)

Skip explicitly if the user has already done the equivalent
analysis ("we discussed this last week and concluded we need a
dedicated skill"). Do NOT skip just to move faster — the cost of
building the wrong skill is permanent.

If a gate verdict is DROP / REJECT / RESHAPE, surface it and ask
the user how to proceed (drop, defer, or reshape smaller) before
continuing to intake.

**Gate 3 — User-input check (after intake, before drafting)** —
Does this skill have any user-input branching? If yes, plan to apply
the hardened `AskUserQuestion` pattern from
[`references/asking-user-questions.md`](references/asking-user-questions.md)
when drafting the relevant STEP — without it, the skill is highly likely
to inline-fallback or silently default in production. If no user input
is needed, this gate is N/A.

### Capture Intent

**Do NOT Load:** Skip this section if the user's request is simply "help me write a skill" without any specific workflow. Use the full creation flow instead.

Start by understanding the user's intent. The current conversation might already contain the workflow to capture (e.g., "turn this into a skill") — if so, **extract answers from the conversation history first** (tools used, step sequence, corrections the user made, input/output formats observed); the user fills gaps and confirms before proceeding.

Clarify these four questions:
1. What should this skill enable Claude to do?
2. When should this skill trigger? (what user phrases/contexts)
3. What's the expected output format?
4. Should we set up test cases? Objectively verifiable outputs (file transforms, data extraction, code generation, fixed workflow steps) benefit from test cases. Subjective outputs (writing style, creative work) often don't benefit from quantitative test cases — evaluate these qualitatively by reviewing outputs inline with the user and using the quick eval path with direct feedback. Suggest the appropriate default, but let the user decide.

### Interview and Research

Proactively ask questions about edge cases, input/output formats, example files, success criteria, and dependencies. Wait to write test prompts until you've got this part ironed out.

Check available MCPs — if useful for research (docs, similar skills, best practices), research in parallel via subagents if available, otherwise inline. Come prepared with context to reduce burden on the user.

### Write the SKILL.md

Based on the user interview, fill in these components:

- **name**: Skill identifier (lowercase, hyphens only, 1-64 chars)
- **description**: What it does + when to use it (use positive specificity; see Description Best Practices below and the §House description standard — avoid "Do NOT use for X" negation)
- **compatibility**: Required tools, dependencies (optional)
- **license**: SPDX identifier or path to LICENSE file (optional)
- **allowed-tools**: Space-separated pre-approved tools (e.g., "Bash(git *) Read"; optional)
- **metadata**: Optional key-value pairs (version, author, etc.)
- **the rest of the skill :)**

> **Evaluation-first is the default path for new skills.** Quick path (2-3 test cases, no baseline) is permitted ONLY for simple skills (formatters, templates, single-step workflows), when success criteria are already documented, or for one-off prototypes — document the skip reason in evals/evals.json. **Determine simplicity first; then if still uncertain, start with the quick path.**

### Step 0: Evaluation-First (full eval path)

**Do NOT Load:** Skip this section if you selected the quick eval path. Load only when doing full benchmark with baseline comparison. The basic baseline running instructions are included above; see [references/eval-protocol.md](references/eval-protocol.md) for the detailed protocol for multiple runs, timing capture, and advanced features.

> **Note:** This section describes the full Evaluation-First path (Step 0). The Quick eval path is described in the Choosing Your Eval Path section above — it is an alternative to this full path, used only for simple skills, when success criteria are already documented, or for one-off prototypes.

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

#### Step 1: Write the SKILL.md

Based on the user interview, fill in these components:

- **name**: Skill identifier (lowercase, hyphens only, 1-64 chars)
- **description**: What it does + when to use it (use positive specificity; see Description Best Practices below and the §House description standard — avoid "Do NOT use for X" negation)
- **compatibility**: Required tools, dependencies (optional)
- **license**: SPDX identifier or path to LICENSE file (optional)
- **allowed-tools**: Space-separated pre-approved tools (e.g., "Bash(git *) Read"; optional)
- **metadata**: Optional key-value pairs (version, author, etc.)
- **the rest of the skill :)****

#### Description Best Practices

Before drafting the description, read
[references/description-design.md](references/description-design.md) —
it owns the design patterns: WHAT+WHEN (not WHAT+WORKFLOW),
third-person voice, length guidance, a validation checklist, and
examples. The house standard for descriptions is defined in
description-design.md §Principles (Principles 1–4). Principle 4
specifically covers length requirements.

### Skill Writing Guide

#### Anatomy of a Skill

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description required)
│   └── Markdown instructions
└── Bundled Resources (optional, single-level subdirectories ONLY)
    ├── scripts/    - Executable code for deterministic/repetitive tasks
    ├── references/ - Docs loaded into context as needed
    ├── assets/     - Templates / fixtures / static files
    ├── agents/     - Sub-agent definitions
    └── ... (any other single-level subdirectory you need)
```

#### CRITICAL: Folder structure must be flat — NO nested subdirectories

Anthropic skill convention forbids subdirectories inside subdirectories under a skill root. A skill may contain `SKILL.md` plus any number of single-level subdirectories; those subdirectories must themselves be flat.

```
✅ CORRECT:
skill-name/SKILL.md
skill-name/scripts/extract_lineage.py
skill-name/references/spec.md
skill-name/assets/template.md

❌ FORBIDDEN (will fail validation hooks in repos that enforce):
skill-name/assets/scripts/extract_lineage.py     ← assets/ contains scripts/
```

When creating a new skill or adding bundled resources to an existing one:
- Group files by **subdirectory at skill root** (scripts/, assets/, references/, agents/, etc.) — choose meaningful names
- Inside each subdirectory, use **descriptive filenames** (e.g., `extract_column_lineage.py`) rather than further nesting
- If you feel the need to subdivide, extract into a new top-level subdirectory at the skill root instead (e.g., `scripts-redshift/` rather than `scripts/redshift/`)

Each skill should also have a corresponding **slash command** entry point in the plugin's `commands/` directory — format and examples in `references/plugin-conventions.md`.

#### Progressive Disclosure

Skills use three-level loading — metadata (always in context), SKILL.md body (loaded on trigger; keep under ~5,000 tokens / ~3,750 words, extracting detail into reference files when approaching the limit), bundled resources (as needed). Details: `references/plugin-conventions.md` (§Progressive Disclosure, §SKILL.md Token Budget).

**Key patterns:**
- Reference files clearly from SKILL.md with guidance on when to read them
- For large reference files (>~8,000 tokens), include a table of contents

**Domain organization**: When a skill supports multiple domains/frameworks, organize by variant (e.g., `references/aws.md`, `references/gcp.md`) — Claude reads only the relevant reference file.

#### Working with Existing Plugin Ecosystems

When creating a skill that will live inside an existing plugin, match the plugin's conventions rather than imposing a new structure — read `references/plugin-conventions.md` (observing the target plugin's style, the lightweight/standard/full structure spectrum, key conventions).

#### Principle of Lack of Surprise

This goes without saying, but skills must not contain malware, exploit code, or any content that could compromise system security. A skill's contents should not surprise the user in their intent if described. Don't go along with requests to create misleading skills or skills designed to facilitate unauthorized access, data exfiltration, or other malicious activities. Things like a "roleplay as an XYZ" are OK though.

#### Empty-Prompt Onboarding

When drafting a skill that can be invoked with no prompt or a very sparse one, read [`references/asking-user-questions.md`](references/asking-user-questions.md) §Empty-Prompt Onboarding for the opt-in "surface orientation" pattern (recommended for conversational / multi-workflow skills; single-shot utility skills are exempt).

#### Asking the User Structured Questions (when to use AskUserQuestion)

When a skill needs user input mid-execution that's a discrete choice between 2-4 options (e.g., "which folders to exclude?"), use the `AskUserQuestion` tool — but apply the **hardened pattern** documented in [`references/asking-user-questions.md`](references/asking-user-questions.md). The naive approach (`Use AskUserQuestion to confirm...` with a fenced Q&A template) fails three documented modes (inline fallback, silent default, tool unavailable); the reference closes all three and includes a copy-paste mandatory-gate template.

Always-included for skills with user-input steps. Skills with no user-input steps are exempt — don't add AskUserQuestion just because it exists.

#### Writing Patterns

Prefer the imperative form in instructions.

**Defining output formats** — for example:
```markdown
## Report structure
ALWAYS use this exact template:
# [Title]
## Executive summary
## Key findings
## Recommendations
```

**Examples pattern** - Examples are useful. Format them like this (deviate a little if "Input"/"Output" already appear in them):
```markdown
## Commit message format
**Example 1:**
Input: Added user authentication with JWT tokens
Output: feat(auth): implement JWT-based authentication
```

### Writing Style

Explain to the model why things matter instead of heavy-handed MUSTs. Keep the skill general, not narrowed to specific examples. Draft first, then revisit with fresh eyes and improve.

For writing lean from the start — token economy, bloat self-review, thin-orchestrator design — read [references/writing-lean.md](references/writing-lean.md).

**Note:** This section describes the Quick eval path approach as an alternative to the full Evaluation-First path (Step 0). Use the Quick path only for simple skills (formatters, templates, single-step workflows), when success criteria are already documented, or for one-off prototypes — otherwise, follow the full Evaluation-First path starting at Step 0 below.

**Phase 2/3: Testing** — After writing the skill draft, come up with 2-3 realistic test prompts — the kind of thing a real user would actually say — and share them with the user: "Here are a few test cases I'd like to try. Do these look right, or do you want to add more?" (not necessarily verbatim). Then run them.

Save test cases to `evals/evals.json`. Don't write assertions yet — just the prompts. You'll draft assertions in the next step while the runs are in progress.

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's task prompt",
      "expected_output": "Description of expected result",
      "files": [],
      "expectations": [],
      "skip_reason": null
    }
  ]
}
```

See `references/schemas.md` for the full schema (including the `expectations` field, which you'll add later).

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

For case (c), use this flow (steps 1–4). **Skip Step 0 (Evaluation-First)** — the skill already has eval cases from its original creation or previous improvements; reuse those. Cases (a) and (b) hand off to the dedicated sibling skills above and do **not** use these steps. Case (d) is handled internally using the Description Optimization section below.

#### 1. Assess the Current State

Read the existing SKILL.md and all bundled files. Understand:
- What the skill does and how it's structured
- What conventions it follows (check the parent plugin's style)
- Known issues the user reports or you observe

#### 2. Diagnose Improvement Areas

Look at these dimensions (these apply to **structural** rewrites; they are not the right lens for token refactor or output A/B):
- **Triggering**: Is the description specific enough? Does it undertrigger or overtrigger?
- **Instructions**: Are they clear? Do they explain the "why"? Are there gaps?
- **Structure**: Is the directory organization appropriate for the skill's complexity?
- **Coverage**: Are edge cases handled? Are there missing workflows?
- **Bundled files**: Are reference files up to date? Are scripts working?

#### 3. Propose Changes

Present a concise improvement plan to the user before making changes. Group changes by impact:
- **High impact**: Changes that affect the skill's core behavior or triggering
- **Low impact**: Cleanup, reorganization, wording improvements

#### 4. Evaluate

Use the eval workflow (quick or full path, depending on complexity) to verify improvements. When improving an existing skill, the baseline should be the original version — snapshot it before editing (see Step 0's baseline-run instructions for the command: `cp -r <skill-path> <workspace>/skill-snapshot/`).

---

**Do NOT Load:** Do not load `references/eval-protocol.md` until you have decided on Full eval path and prepared eval_metadata.json for each test case. Quick path users stop after Phase 1 (Choosing Your Eval Path).

**Phase 3/3: Evaluation** — Choose your eval path based on complexity:

### Choosing Your Eval Path

Not every skill needs the full benchmark treatment. Choose based on complexity:

| | Quick eval path | Full eval path |
|---|---|---|
| **For** | Simple skills (formatters, templates, single-step workflows) whose quality is best judged by looking at the output | Complex skills (multi-step workflows, objective criteria, many moving parts) needing quantitative comparison |
| **Method** | Run 2-3 test cases manually (no subagent spawning); review outputs inline with the user; skip grading and benchmarking; **for improvements, still run baseline comparison; for new skills on the quick path, no baseline needed**; iterate on direct user feedback | Spawn parallel subagent runs with baselines; grade with assertions, aggregate benchmarks; structured inline review with markdown reports |

> **Note:** The "when in doubt, start with quick path" guidance applies only AFTER you have determined the skill is simple enough for the quick path (see the Choosing Your Eval Path section for details). After making that determination, if still uncertain, start with the quick path — you can always escalate if it isn't giving enough signal.


For the full eval protocol (Steps 1-4: spawn runs, draft assertions, capture timing, grade/aggregate/present), see [references/eval-protocol.md](references/eval-protocol.md) — it owns the complete sequence including directory structure, baseline runs, timing capture, self-assessment pass, and the 15% improvement threshold.

Put results in `<skill-name>-workspace/`, a sibling of the skill directory, organized by iteration (`iteration-1/`, `iteration-2/`, etc.) and, within that, a directory per test case (`eval-0/`, `eval-1/`, etc.). Create directories as you go, not upfront.

**Do NOT Load:** Do not load `references/eval-protocol.md` until you have decided on Full eval path and prepared eval_metadata.json for each test case. Quick path users skip this section entirely.

## Improving the skill

The heart of the loop: turn the user's feedback on the test results into a better skill.

### How to think about improvements

1. **Generalize from the feedback.** You're creating a skill to be used a million times across many prompts; you iterate on a few examples only for speed — a skill that works only for those examples is useless. Rather than fiddly overfitty changes or oppressively constrictive MUSTs, when an issue is stubborn try branching out — different metaphors, different patterns of working. It's cheap to try and you might land on something great.

2. **Keep the prompt lean.** Remove things that aren't pulling their weight. Read the **transcripts**, not just the final outputs — outputs tell you *what* happened, transcripts *how*. If the skill makes the model waste time on unproductive work, remove the parts causing it.

3. **Explain the why.** Today's LLMs have good theory of mind and, given a good harness, go beyond rote instructions. Even if the user's feedback is terse or frustrated, understand why they wrote what they wrote and transmit that understanding into the instructions. If you find yourself writing ALWAYS or NEVER in all caps, that's a yellow flag — reframe and explain the reasoning so that the model understands why it matters.

4. **Look for repeated work across test cases.** If the transcripts show subagents independently writing similar helper scripts or taking the same multi-step approach (all 3 test cases wrote a `create_docx.py`), that's a strong signal the skill should bundle that script: write it once, put it in `scripts/`, and tell the skill to use it.

### The iteration loop

After improving the skill:

1. Apply your improvements to the skill
2. **For Full eval path:** Rerun all test cases into a new `iteration-<N+1>/` directory, including baseline runs. If you're creating a new skill, the baseline is always `without_skill` (no skill) — that stays the same across iterations. If you're improving an existing skill, use the snapshot of the current version (taken before editing) as the baseline for all iterations. This ensures consistent comparison against the version being improved.
3. **For Quick eval path:** Rerun the 2-3 test cases manually. **For improvements, include baseline comparison (run the old skill version on the same test cases)**; iterate on direct user feedback as in the original Quick eval path.
4. Present results inline and save to `review.md`, noting changes from previous iteration
5. Wait for the user to review and tell you they're done
6. Read the new feedback, improve again, repeat

Keep going until:
- The user says they're happy
- The feedback is all empty (everything looks good)
- You're not making meaningful progress

---

## Advanced: Blind comparison

For a more rigorous comparison between two versions of a skill (the user asks "is the new version actually better?"), read `agents/comparator.md` and `agents/analyzer.md`: give two outputs to an independent agent without telling it which is which, let it judge quality, then analyze why the winner won. Optional, requires subagents; the human review loop is usually sufficient.

> **Boundary note vs `skill-dev-toolkit:skill-tuning`**: the blind comparator uses an LLM subagent as judge — fast and cheap, but inherits LLM-as-judge limitations (verbosity bias, position bias, weak signal on taste-sensitive output dimensions like voice / tone / creative quality). For taste-sensitive A/B that needs reliable preference signal, use `skill-tuning` instead — it uses **human** judgment per iteration and accumulates a preference log. Rule of thumb: blind comparator for objective / structured outputs (file transforms, code generation, fixed-format generators); `skill-tuning` for subjective / creative outputs (writing style, design feel, persuasive copy).

---

## Description Optimization

**Do NOT Load:** Skip this entire section if you are not optimizing a skill's description. Load only when you have a completed skill and want to improve its triggering accuracy.

The frontmatter description is the primary mechanism determining whether Claude invokes a skill. After creating or improving a skill, offer to optimize it for better triggering accuracy.

For the full description optimization workflow, see [references/description-optimization.md](references/description-optimization.md).

> **Note:** The Description Optimization workflow satisfies NEVER #5 by generating a validated 20-query eval set before optimizing. If modifying descriptions manually outside this workflow, you must still follow all 7 NEVER rules.

### House description standard (the optimization target)

Any description you write or optimize MUST follow the house standard defined in:
[references/description-design.md](references/description-design.md) §Principles (Principles 1-4), with Principle 4 covering length requirements

- **Length: two-tier** (normal vs router/CONDITIONAL) — number authority:
  [references/description-design.md](references/description-design.md) §Principles (Principles 1-4), with Principle 4 covering length requirements. Descriptions
  share a context-listing budget; over-long ones silently evict OTHER skills from what Claude sees.
  Normal skills: target ≤150 chars; 250 is a SOFT lint line; YAML justification may exceed 250 (with a
  colocated justification comment). Router/CONDITIONAL skills: exception band ≤500 with firing evidence.
- **Content: what it does + when to use it** — positive, specific triggers front-loaded (real
  user phrasings). Keep the step-by-step **procedure / workflow / grounding citations OUT of the
  description**; those live in the body (the body loads in full on activation, so a what+when
  summary does NOT cause the body to be skipped — that fear is unverified).
- **Disambiguate by positive specificity** — prefer naming what triggers the skill. When multiple skills could match similar queries, add explicit negative triggers to prevent mis-routing (e.g., "Do NOT use for CSV files — use csv-processing instead"). Limit to 2-3 negative triggers. A light positive redirect ("for X, use skill-Y") is also fine.
- **Multilingual keyword belt (optional)** — for repos with mixed-language prompts, append a short keyword belt (≤50 chars) at the end: `Triggers: commit / PR / merge / コミット / 決定記録`. Zero of 14 superpowers skills use this; include it if your repo's prompts are routinely non-English; skip it otherwise.
- Third person, no XML tags. The optimization loop must keep `best_description` within these rules.

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
- `references/schemas.md` — JSON structures for evals.json, grading.json, etc.
- `references/plugin-conventions.md` — Plugin ecosystem conventions, directory structures, slash command format
- `references/iteration-automation.md` — Self-assessment and auto-regression detection protocols
- `references/eval-methodology.md` — Why the eval workflow is designed this way (optional)
- `references/platform-adaptations.md` — Claude.ai and Cowork platform-specific adjustments
- `references/mermaid-usage-guidelines.md` — When to use Mermaid diagrams vs prose in skill authoring, syntax conventions, cost-benefit framework
- `references/eval-protocol.md` — Complete evaluation workflow (full eval path detail)
- `references/description-optimization.md` — Description optimization workflow
- `references/description-design.md` — Description design patterns and best practices
- `references/evaluation-design.md` — Evaluation case design template
- `references/asking-user-questions.md` — Hardened AskUserQuestion patterns
- `references/writing-lean.md` — Token economy and lean writing patterns

---

**Core loop reminder:** Draft → Test → Evaluate (inline review + evals) → Improve → Repeat → Package. Good luck!
