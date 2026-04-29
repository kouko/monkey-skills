---
name: skill-creator-advance
description: >-
  Create new skills, do major redesigns of existing skills (add, split,
  or merge phases; change agent decomposition; redesign workflow;
  change input/output contract), measure skill performance with
  iterative eval-driven development, and optimize a skill's
  description for better triggering accuracy. Use when users want to
  create a skill from scratch, redesign or significantly rewrite a
  skill, run evals, benchmark performance, or optimize description
  triggering. Also responds to vague "improve this skill" requests
  by asking the user to clarify the type of improvement before
  proceeding (router behavior — see Improving an Existing Skill
  section). Also use when the user says "build a skill", "make a
  slash command", "write a new skill", or "test my skill". Do NOT
  use for token / structure refactor of an existing skill with
  output equivalence preserved (use dev-workflow:skill-refactor
  instead). Do NOT use for domain-team skills with convention
  discipline (use domain-teams:skill-team instead). スキル作成・
  大規模再設計・評価ループ。技能建立・大幅重設計・評估迴圈。
---

# Skill Creator Advance

A skill for creating new skills and iteratively improving them.

The core loop: **draft → test → review → improve → repeat**.

- Decide what the skill should do → write a draft
- Create test prompts → run claude-with-the-skill on them
- Evaluate results (qualitative review + quantitative assertions)
- Rewrite based on feedback → repeat until satisfied
- Optionally optimize the description for better triggering

Your job is to figure out where the user is in this process and help them progress. Maybe they want to start from scratch, or maybe they already have a draft. Be flexible — if they say "just vibe with me", skip the formal eval machinery.

## Communicating with the user

Users range from non-technical to expert — plumbers opening terminals, grandparents googling "how to install npm", alongside experienced developers. Pay attention to context cues to gauge their familiarity:

- "evaluation" and "benchmark" are borderline, but generally OK
- For "JSON" and "assertion", look for serious cues the user knows these terms before using them without explanation

When in doubt, briefly define terms inline. It's better to over-explain once than to lose someone.

---

## Creating a skill

### Pre-Creation Gates (recommended; skip only with stated reason)

Before launching into intake / interview / drafting, run two
lightweight gates against the user's request. Each is one or two
focused questions; together they prevent shipping a skill that
should not have been built.

**Gate 1 — Worth-it check (`dev-workflow:proposal-critique`)** —
applicable when the user proposes ≥2 skills at once, or one skill
with multiple supporting claims ("we need this because A, B, and
C"). The triage matrix sorts items into KEEP / DEFER / DROP via
evidence grounding + YAGNI. If the proposal is a single skill with
a single load-bearing reason, this gate is naturally low-cost —
skip after a short check rather than running the full 5-step flow.

**Gate 2 — Smallest-end-state check (`dev-workflow:complexity-critique`)** —
applicable to **every** new skill proposal, single or multi. The
three questions:

1. What's the smallest end state that solves this? (Could it be 0
   functions — i.e., this isn't really a skill, just a one-off
   prompt? Could it be one existing skill plus a new section
   instead of a new skill?)
2. Does this result in less total skill-ecosystem code than not
   building it? (A new skill adds to the ecosystem's surface area;
   defaults toward "no" unless the skill subtracts other artifacts
   or replaces ad-hoc prompts.)
3. What does this skill make obsolete? (If nothing, the rationale
   is purely additive — apply the same skepticism `complexity-critique`
   applies to feature adds.)

Skip explicitly if the user has already done the equivalent
analysis ("we discussed this last week and concluded we need a
dedicated skill"). Do NOT skip just to move faster — these gates
are short, and the cost of building the wrong skill is permanent.

If a gate produces a verdict of DROP / REJECT / RESHAPE, surface
the verdict to the user and ask how to proceed (drop the skill
proposal, defer, or reshape into a smaller scope) before
continuing to intake.

### Capture Intent

Start by understanding the user's intent. The current conversation might already contain a workflow the user wants to capture (e.g., "turn this into a skill"). If so, **extract answers from the conversation history first** — the tools used, the sequence of steps, corrections the user made, input/output formats observed. The user may need to fill gaps, and should confirm before proceeding.

Clarify these four questions:
1. What should this skill enable Claude to do?
2. When should this skill trigger? (what user phrases/contexts)
3. What's the expected output format?
4. Should we set up test cases? Skills with objectively verifiable outputs (file transforms, data extraction, code generation, fixed workflow steps) benefit from test cases. Skills with subjective outputs (writing style, art) often don't. Suggest the appropriate default, but let the user decide.

### Interview and Research

Proactively ask questions about edge cases, input/output formats, example files, success criteria, and dependencies. Wait to write test prompts until you've got this part ironed out.

Check available MCPs - if useful for research (searching docs, finding similar skills, looking up best practices), research in parallel via subagents if available, otherwise inline. Come prepared with context to reduce burden on the user.

### Write the SKILL.md

Based on the user interview, fill in these components:

- **name**: Skill identifier
- **description**: The primary triggering mechanism — include what the skill does AND when to use it. Claude tends to "undertrigger" skills, so make descriptions a little "pushy" (e.g., "Make sure to use this skill whenever the user mentions dashboards, data visualization, or internal metrics, even if they don't explicitly ask for a 'dashboard.'")
- **compatibility**: Required tools, dependencies (optional, rarely needed)
- **the rest of the skill :)**

#### Description Best Practices

For a deep dive on description design (Anthropic vs Superpowers
conventions, LLM semantic-match mechanics, length guidelines, and a
worked git-memory case study), see [references/description-design.md](references/description-design.md).

Quick summary of the patterns covered there:

**1. WHAT + WHEN, not WHAT + WORKFLOW.** Anthropic's three official
examples all open with a one-sentence outcome ("Generate commit
messages…") followed by `Use when …`. Superpowers' "ONLY when, NOT
what" rule is a defensive override against descriptions summarizing
the workflow (which lets Claude shortcut SKILL.md). Brief outcome
clauses are fine; step-by-step process recaps are not.

**2. "About-to-violate" symptoms.** The most discoverable trigger is
the moment **just before** the user takes the action your skill
should intercept. Pattern: `Use when [situation], before [action]`
(e.g. "before writing implementation code", "before merging",
"before running `git commit`"). After the action, the skill is too
late to help.

**3. Third-person.** Anthropic best-practices has an explicit Warning
block: pronoun inconsistency in the system prompt causes selection
problems. ✓ "Processes Excel files…" ✗ "I can help you process…"

**4. Natural keywords the user would type.** Claude's matcher favors
direct lexical overlap with everyday verbs and nouns. `git commit`
beats `version control commit operation`; `pivot table` beats
`cross-tabulation analysis`.

**5. Length 100–250 chars, ceiling ~500.** Empirical median of all
14 superpowers SKILL.md descriptions is ~107 chars; max is 234. The
1,024-char Agent Skills spec ceiling is generous, but long
descriptions burn system-prompt context that competes with the
SKILL.md body itself.

**6. Negative triggers** — Explicitly state when NOT to use the skill
to avoid collisions with similar skills:
> Do NOT use for domain-team skills (use skill-team instead). Do NOT use for simple file edits that don't need a skill.

**7. Multilingual trigger keywords (optional, low-cost insurance).**
If the skill's users speak multiple languages, add a short keyword
belt at the end. Claude is itself multilingual and semantic-matches
across languages without this — it's belt-and-suspenders, not the
primary mechanism.
> スキル作成・評価。技能建立・評估。

**Before/after example:**
- Before: "Create and test skills."
- After: "Create new skills, improve existing skills, and measure skill performance with iterative eval-driven development. Use when users want to create a skill from scratch, edit or optimize an existing skill, run evals, or benchmark performance. Do NOT use for domain-team convention skills (use skill-team). スキル作成・評価ループ。技能建立・評估迴圈。"

### Skill Writing Guide

#### Anatomy of a Skill

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description required)
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/    - Executable code for deterministic/repetitive tasks
    └── references/ - Docs loaded into context as needed
```

Each skill should also have a corresponding **slash command** entry point in the plugin's `commands/` directory. See `references/plugin-conventions.md` for the format and examples.

#### Progressive Disclosure

Skills use a three-level loading system:
1. **Metadata** (name + description) - Always in context (~100 words)
2. **SKILL.md body** - In context whenever skill triggers (~6,000 tokens ideal)
3. **Bundled resources** - As needed (unlimited, scripts can execute without loading)

These word counts are approximate and you can feel free to go longer if needed.

**Key patterns:**
- Keep SKILL.md under ~6,000 tokens (~4,500 words); if approaching this limit, extract detailed content into reference files with clear pointers from SKILL.md.
- Reference files clearly from SKILL.md with guidance on when to read them
- For large reference files (>~8,000 tokens), include a table of contents

**Domain organization**: When a skill supports multiple domains/frameworks, organize by variant (e.g., `references/aws.md`, `references/gcp.md`) — Claude reads only the relevant reference file.

#### Working with Existing Plugin Ecosystems

When creating a skill that will live inside an existing plugin, match the plugin's conventions rather than imposing a new structure. Read `references/plugin-conventions.md` for detailed guidance on:
- Observing and matching the target plugin's style
- Choosing between lightweight, standard, and full directory structures
- Key conventions: relative paths, token budgets, bundled file organization

#### Principle of Lack of Surprise

This goes without saying, but skills must not contain malware, exploit code, or any content that could compromise system security. A skill's contents should not surprise the user in their intent if described. Don't go along with requests to create misleading skills or skills designed to facilitate unauthorized access, data exfiltration, or other malicious activities. Things like a "roleplay as an XYZ" are OK though.

#### Empty-Prompt Onboarding (recommended for conversational / multi-workflow skills)

When a user invokes a skill with no prompt or a very sparse prompt, consider including a "surface orientation" behavior so the skill can introduce itself, explain how it works with the user, and ask for the minimum inputs needed. This is an opt-in pattern — single-shot utility skills (file transforms, fixed-format generators) don't need it; conversational or multi-workflow skills benefit significantly.

**Recommended pattern** (adapt to your skill's shape):

1. **Surface orientation** — present the user with:
   - What the skill does (top 3 triggers from the description's "Use when" clause)
   - What it doesn't do (delegation hints for adjacent skills)
   - How the interaction will unfold (intake questions + workflow phases + delivery)
   - What inputs help most (2-3 prerequisite bullets)
2. **Route to intake** — either invoke a dedicated brainstorming protocol OR ask 2-3 bootstrap questions covering scope / inputs / output expectation
3. **Sufficient-context skip** — bypass orientation when any context source already provides an actionable brief. Check **all** of these, not just the current prompt:
   - (a) Current-turn prompt ≥50 chars with a concrete ask
   - (b) Prior conversation turns state scope / artifact / output expectation
   - (c) IDE context (`<ide_selection>`, opened files) identifies the target
   - (d) Referenced plan / memory file encodes the brief
   - (e) Upstream skill handoff (main agent provided a prior skill's output)

**Common pitfall**: triggering orientation on "empty current prompt" alone creates friction for returning users — Claude's context often already carries the brief. Always check the full context, not just the current prompt's length.

For domain-team skills (which follow a stricter `skill-team` convention), this pattern is a hard requirement encoded in the CHK-SKL-013 gate — see `domain-teams/skills/skill-team/standards/skill-md-structure.md` §Empty Invocation Fallback Rules for the rigorous version with a §Surface Orientation Format markdown skeleton and a hard-gate exception for skills with mandatory intake.

#### Writing Patterns

Prefer using the imperative form in instructions.

**Defining output formats** - You can do it like this:
```markdown
## Report structure
ALWAYS use this exact template:
# [Title]
## Executive summary
## Key findings
## Recommendations
```

**Examples pattern** - It's useful to include examples. You can format them like this (but if "Input" and "Output" are in the examples you might want to deviate a little):
```markdown
## Commit message format
**Example 1:**
Input: Added user authentication with JWT tokens
Output: feat(auth): implement JWT-based authentication
```

### Writing Style

Try to explain to the model why things are important in lieu of heavy-handed musty MUSTs. Use theory of mind and try to make the skill general and not super-narrow to specific examples. Start by writing a draft and then look at it with fresh eyes and improve it.

### Test Cases

After writing the skill draft, come up with 2-3 realistic test prompts — the kind of thing a real user would actually say. Share them with the user: [you don't have to use this exact language] "Here are a few test cases I'd like to try. Do these look right, or do you want to add more?" Then run them.

Save test cases to `evals/evals.json`. Don't write assertions yet — just the prompts. You'll draft assertions in the next step while the runs are in progress.

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's task prompt",
      "expected_output": "Description of expected result",
      "files": []
    }
  ]
}
```

See `references/schemas.md` for the full schema (including the `assertions` field, which you'll add later).

---

## Improving an Existing Skill

When a user asks to "improve" or "optimize" an existing skill, **first determine which kind of improvement** before doing any work. Three distinct shapes — they need different tools:

### Router: Identify the Improvement Type

Ask the user to clarify (or infer from their phrasing):

| Improvement type | Signal | Handler |
|---|---|---|
| **(a) Token / structure refactor** with output behavior unchanged | "shorten", "reduce tokens", "tidy up", "縮減 SKILL.md", "整理結構" — and **no behavior change desired** | Hand off to `dev-workflow:skill-refactor`. Do not handle here. |
| **(b) Output quality / variant exploration** with human judgment | "test different phrasings", "improve outputs", "A/B variants", "輸出風格", "我來選哪個比較好" — taste-sensitive output dimensions | Hand off to `dev-workflow:skill-tasting`. Do not handle here. |
| **(c) Structural change** — add / split / merge phases, change agent decomposition, change input/output contract | "rewrite", "redesign", "add a phase", "split this skill", "重新設計", "拆 skill" | Continue with the full creation flow below, using the existing skill as the starting baseline rather than starting from scratch. |

If the user's intent is unclear, ask them to clarify which of (a), (b), or (c) applies. Do **not** default into the creation flow without confirming — picking the wrong tool wastes time on the wrong type of work.

### Case (c): Structural Rewrite Flow

For case (c), use this flow (steps 1–4). Cases (a) and (b) hand off to the dedicated sibling skills above and do **not** use these steps.

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

Use the eval workflow (quick or full path, depending on complexity) to verify improvements. When improving an existing skill, the baseline should be the original version — snapshot it before editing (`cp -r <skill-path> <workspace>/skill-snapshot/`).

---

## Running and evaluating test cases

### Choosing Your Eval Path

Not every skill needs the full benchmark treatment. Choose based on complexity:

**Quick eval path** — For simple skills (formatters, templates, single-step workflows):
- Run 2-3 test cases manually (no subagent spawning)
- Review outputs inline with the user
- Skip grading, benchmarking, and baseline comparison
- Iterate based on direct user feedback
- Use this when the skill's quality is best judged by looking at it

**Full eval path** — For complex skills (multi-step workflows, skills with objective criteria):
- Spawn parallel subagent runs with baselines
- Grade with assertions, aggregate benchmarks
- Use structured inline review with markdown reports
- Use this when you need quantitative comparison or the skill has many moving parts

When in doubt, start with the quick path. You can always escalate to the full path if the quick path isn't giving enough signal.

---

The full eval path follows this sequence — don't stop partway through. Do NOT use `/skill-test` or any other testing skill.

Put results in `<skill-name>-workspace/` as a sibling to the skill directory. Within the workspace, organize results by iteration (`iteration-1/`, `iteration-2/`, etc.) and within that, each test case gets a directory (`eval-0/`, `eval-1/`, etc.). Don't create all of this upfront — just create directories as you go.

### Step 1: Spawn all runs (with-skill AND baseline) in the same turn

For each test case, spawn two subagents in the same turn — one with the skill, one without. This is important: don't spawn the with-skill runs first and then come back for baselines later. Launch everything at once so it all finishes around the same time.

**With-skill run:**

```
Execute this task:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Input files: <eval files if any, or "none">
- Save outputs to: <workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/
- Outputs to save: <what the user cares about — e.g., "the .docx file", "the final CSV">
```

**Baseline run** (same prompt, but the baseline depends on context):
- **Creating a new skill**: no skill at all. Same prompt, no skill path, save to `without_skill/outputs/`.
- **Improving an existing skill**: the old version. Before editing, snapshot the skill (`cp -r <skill-path> <workspace>/skill-snapshot/`), then point the baseline subagent at the snapshot. Save to `old_skill/outputs/`.

Write an `eval_metadata.json` for each test case (assertions can be empty for now). Give each eval a descriptive name based on what it's testing — not just "eval-0". Use this name for the directory too. If this iteration uses new or modified eval prompts, create these files for each new eval directory — don't assume they carry over from previous iterations.

```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name-here",
  "prompt": "The user's task prompt",
  "assertions": []
}
```

### Step 2: While runs are in progress, draft assertions

Don't just wait for the runs to finish — you can use this time productively. Draft quantitative assertions for each test case and explain them to the user. If assertions already exist in `evals/evals.json`, review them and explain what they check.

Good assertions are objectively verifiable and have descriptive names — they should read clearly in the benchmark report so someone glancing at the results immediately understands what each one checks. Subjective skills (writing style, design quality) are better evaluated qualitatively — don't force assertions onto things that need human judgment.

Update `eval_metadata.json` and `evals/evals.json` with assertions. Explain to the user what they'll see — both the qualitative outputs and the quantitative benchmark.

### Step 3: As runs complete, capture timing data

When each subagent task completes, you receive a notification containing `total_tokens` and `duration_ms`. Save this data immediately to `timing.json` in the run directory:

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

This is the only opportunity to capture this data — it comes through the task notification and isn't persisted elsewhere. Process each notification as it arrives rather than trying to batch them.

### Step 3.5: Self-assessment pass

Before grading and presenting results to the human, perform a quick automated check on each output. Read `references/iteration-automation.md` for the full protocol. In brief:
- Read each test case's output and check for obvious defects (empty output, format violations, crash artifacts)
- If a defect is clearly caused by a skill instruction issue, fix the skill and rerun that test case once
- Log results to `self_assessment.json` in each test case directory
- One pass only — no infinite repair loops

### Step 4: Grade, aggregate, and present results

Once all runs are done:

1. **Grade each run** — spawn a grader subagent (or grade inline) that reads `agents/grader.md` and evaluates each assertion against the outputs. Save results to `grading.json` in each run directory. The grading.json expectations array must use the fields `text`, `passed`, and `evidence` (not `name`/`met`/`details` or other variants). For assertions that can be checked programmatically, write and run a script rather than eyeballing it — scripts are faster, more reliable, and can be reused across iterations.

2. **Check for regressions** (iteration 2+) — After grading, compare results against the previous iteration. Read `references/iteration-automation.md` for the full protocol. Lead with any regressions when reporting to the user.

3. **Aggregate into benchmark** — run the aggregation script from the skill-creator directory:
   ```bash
   python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
   ```
   This produces `benchmark.json` and `benchmark.md` with pass_rate, time, and tokens for each configuration, with mean +/- stddev and the delta. If generating benchmark.json manually, see `references/schemas.md` for the exact schema.
Put each with_skill version before its baseline counterpart.

4. **Do an analyst pass** — read the benchmark data and surface patterns the aggregate stats might hide. See `agents/analyzer.md` (the "Analyzing Benchmark Results" section) for what to look for — things like assertions that always pass regardless of skill (non-discriminating), high-variance evals (possibly flaky), and time/token tradeoffs.

5. **Present results inline** — For each test case, show the results directly in the conversation:

   ```markdown
   ### Test Case: {eval_name}
   **Prompt:** {the task prompt}
   **Output:** {summary of key output files or inline content}
   **Grades:** {assertion pass/fail results with evidence, if graded}
   **Previous:** {what changed from last iteration, if iteration 2+}
   ```

   After presenting all test cases, show the benchmark summary (pass rates, timing, token usage).

6. **Save a markdown report** to `<workspace>/iteration-N/review.md` containing all test case results and benchmark data. This persists the results for cross-iteration comparison.

7. **Ask for feedback** — After presenting results, ask the user for feedback on each test case. Focus on the cases where they have specific complaints; no comment means it looked fine.

---

## Improving the skill

This is the heart of the loop. You've run the test cases, the user has reviewed the results, and now you need to make the skill better based on their feedback.

### How to think about improvements

1. **Generalize from the feedback.** You're trying to create skills that can be used a million times across many different prompts. You and the user are iterating on only a few examples because it helps move faster, but if the skill works only for those examples, it's useless. Rather than put in fiddly overfitty changes or oppressively constrictive MUSTs, if there's some stubborn issue, try branching out — use different metaphors, recommend different patterns of working. It's relatively cheap to try and maybe you'll land on something great.

2. **Keep the prompt lean.** Remove things that aren't pulling their weight. Make sure to read the **transcripts**, not just the final outputs — if it looks like the skill is making the model waste a bunch of time doing things that are unproductive, try getting rid of the parts of the skill that are causing that. The distinction matters: outputs tell you *what* happened, but transcripts tell you *how* it happened.

3. **Explain the why.** Try hard to explain the **why** behind everything you're asking the model to do. Today's LLMs are *smart* — they have good theory of mind and when given a good harness can go beyond rote instructions. Even if the feedback from the user is terse or frustrated, try to actually understand the task and why the user is writing what they wrote, and then transmit this understanding into the instructions. If you find yourself writing ALWAYS or NEVER in all caps, that's a yellow flag — reframe and explain the reasoning so that the model understands why it matters.

4. **Look for repeated work across test cases.** Read the transcripts from the test runs and notice if the subagents all independently wrote similar helper scripts or took the same multi-step approach. If all 3 test cases resulted in the subagent writing a `create_docx.py` or a `build_chart.py`, that's a strong signal the skill should bundle that script. Write it once, put it in `scripts/`, and tell the skill to use it.

This task is important and your thinking time is not the blocker; take your time and really mull things over. Write a draft revision and then look at it anew with fresh eyes. Really do your best to get into the head of the user and understand what they want and need.

### The iteration loop

After improving the skill:

1. Apply your improvements to the skill
2. Rerun all test cases into a new `iteration-<N+1>/` directory, including baseline runs. If you're creating a new skill, the baseline is always `without_skill` (no skill) — that stays the same across iterations. If you're improving an existing skill, use your judgment on what makes sense as the baseline: the original version the user came in with, or the previous iteration.
3. Present results inline and save to `review.md`, noting changes from previous iteration
4. Wait for the user to review and tell you they're done
5. Read the new feedback, improve again, repeat

Keep going until:
- The user says they're happy
- The feedback is all empty (everything looks good)
- You're not making meaningful progress

---

## Advanced: Blind comparison

For situations where you want a more rigorous comparison between two versions of a skill (e.g., the user asks "is the new version actually better?"), there's a blind comparison system. Read `agents/comparator.md` and `agents/analyzer.md` for the details. The basic idea is: give two outputs to an independent agent without telling it which is which, and let it judge quality. Then analyze why the winner won.

This is optional, requires subagents, and most users won't need it. The human review loop is usually sufficient.

> **Boundary note vs `dev-workflow:skill-tasting`**: the blind comparator uses an LLM subagent as judge — fast and cheap, but inherits LLM-as-judge limitations (verbosity bias, position bias, weak signal on taste-sensitive output dimensions like voice / tone / creative quality). For taste-sensitive A/B that needs reliable preference signal, use `skill-tasting` instead — it uses **human** judgment per iteration and accumulates a preference log. Rule of thumb: blind comparator for objective / structured outputs (file transforms, code generation, fixed-format generators); `skill-tasting` for subjective / creative outputs (writing style, design feel, persuasive copy).

---

## Description Optimization

The description field in SKILL.md frontmatter is the primary mechanism that determines whether Claude invokes a skill. After creating or improving a skill, offer to optimize the description for better triggering accuracy.

### Step 1: Generate trigger eval queries

Create 20 eval queries — a mix of should-trigger and should-not-trigger. Save as JSON:

```json
[
  {"query": "the user prompt", "should_trigger": true},
  {"query": "another prompt", "should_trigger": false}
]
```

The queries must be realistic and something a Claude Code or Claude.ai user would actually type. Not abstract requests, but requests that are concrete and specific and have a good amount of detail. For instance, file paths, personal context about the user's job or situation, column names and values, company names, URLs. A little bit of backstory. Some might be in lowercase or contain abbreviations or typos or casual speech. Use a mix of different lengths, and focus on edge cases rather than making them clear-cut (the user will get a chance to sign off on them).

Bad: `"Format this data"`, `"Extract text from PDF"`, `"Create a chart"`

Good: `"ok so my boss just sent me this xlsx file (its in my downloads, called something like 'Q4 sales final FINAL v2.xlsx') and she wants me to add a column that shows the profit margin as a percentage. The revenue is in column C and costs are in column D i think"`

For the **should-trigger** queries (8-10), think about coverage. You want different phrasings of the same intent — some formal, some casual. Include cases where the user doesn't explicitly name the skill or file type but clearly needs it. Throw in some uncommon use cases and cases where this skill competes with another but should win.

For the **should-not-trigger** queries (8-10), the most valuable ones are the near-misses — queries that share keywords or concepts with the skill but actually need something different. Think adjacent domains, ambiguous phrasing where a naive keyword match would trigger but shouldn't, and cases where the query touches on something the skill does but in a context where another tool is more appropriate.

The key thing to avoid: don't make should-not-trigger queries obviously irrelevant. "Write a fibonacci function" as a negative test for a PDF skill is too easy — it doesn't test anything. The negative cases should be genuinely tricky.

### Step 2: Review with user

Present the eval set to the user inline for review. For each query, show:

```markdown
| # | Query | Should Trigger? |
|---|-------|-----------------|
| 1 | "ok so my boss sent me this xlsx..." | ✅ Yes |
| 2 | "can you analyze the trends in..." | ❌ No |
```

Ask the user to confirm, edit, add, or remove queries before proceeding. Save the final eval set to `<workspace>/trigger-eval.json`.

This step matters — bad eval queries lead to bad descriptions.

### Step 3: Run the optimization loop

Tell the user: "This will take some time — I'll run the optimization loop in the background and check on it periodically."

Save the eval set to the workspace, then run in the background:

```bash
python -m scripts.run_loop \
  --eval-set <path-to-trigger-eval.json> \
  --skill-path <path-to-skill> \
  --model <model-id-powering-this-session> \
  --max-iterations 5 \
  --verbose
```

Use the model ID from your system prompt (the one powering the current session) so the triggering test matches what the user actually experiences.

While it runs, periodically tail the output to give the user updates on which iteration it's on and what the scores look like.

This handles the full optimization loop automatically. It splits the eval set into 60% train and 40% held-out test, evaluates the current description (running each query 3 times to get a reliable trigger rate), then calls Claude to propose improvements based on what failed. It re-evaluates each new description on both train and test, iterating up to 5 times. When it's done, it opens an HTML report in the browser showing the results per iteration and returns JSON with `best_description` — selected by test score rather than train score to avoid overfitting.

### How skill triggering works

Understanding the triggering mechanism helps design better eval queries. Skills appear in Claude's `available_skills` list with their name + description, and Claude decides whether to consult a skill based on that description. The important thing to know is that Claude only consults skills for tasks it can't easily handle on its own — simple, one-step queries like "read this PDF" may not trigger a skill even if the description matches perfectly, because Claude can handle them directly with basic tools. Complex, multi-step, or specialized queries reliably trigger skills when the description matches.

This means your eval queries should be substantive enough that Claude would actually benefit from consulting a skill. Simple queries like "read file X" are poor test cases — they won't trigger skills regardless of description quality.

### Step 4: Apply the result

Take `best_description` from the JSON output and update the skill's SKILL.md frontmatter. Show the user before/after and report the scores.

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

The agents/ directory contains instructions for specialized subagents. Read them when you need to spawn the relevant subagent.

- `agents/grader.md` — How to evaluate assertions against outputs
- `agents/comparator.md` — How to do blind A/B comparison between two outputs
- `agents/analyzer.md` — How to analyze why one version beat another

The references/ directory has additional documentation:
- `references/schemas.md` — JSON structures for evals.json, grading.json, etc.
- `references/plugin-conventions.md` — Plugin ecosystem conventions, directory structures, and slash command format
- `references/iteration-automation.md` — Self-assessment and auto-regression detection protocols
- `references/eval-methodology.md` — Eval methodology principles: why the eval workflow is designed this way (optional)
- `references/platform-adaptations.md` — Claude.ai and Cowork platform-specific adjustments
- `references/mermaid-usage-guidelines.md` — When to use Mermaid diagrams vs prose in skill authoring (decision trees / state machines / routing), syntax conventions, cost-benefit framework

---

**Core loop reminder:** Draft → Test → Evaluate (inline review + evals) → Improve → Repeat → Package. Good luck!
