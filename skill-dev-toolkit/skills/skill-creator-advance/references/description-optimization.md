# Description Optimization Reference

Purpose: Complete description optimization workflow extracted from SKILL.md for token efficiency. Contains trigger eval design, optimization loop, and application procedures.

---

## Do NOT Load Guards

**SKILL.md embedding instructions include explicit guards at these points:**

- **Before Step 1 (Generate trigger eval queries)**: "Do NOT load this reference until you have a completed skill to optimize."
- **Before Step 2 (Review with user)**: "Only load this reference after you have drafted your initial 20 eval queries in JSON format."
- **Before Step 3 (Run optimization loop)**: "Do NOT load `scripts/run_loop` module until user has confirmed the eval set and you have saved it to `<workspace>/trigger-eval.json`."
- **Before Step 4 (Apply result)**: "Do NOT modify SKILL.md frontmatter until you have received the JSON output with `best_description` from the optimization loop."

---

## Phase 1: Generate trigger eval queries

Create 20 eval queries — a mix of should-trigger (8-10) and should-not-trigger (8-10). Save as JSON:

```json
[
  {"query": "the user prompt", "should_trigger": true},
  {"query": "another prompt", "should_trigger": false}
]
```

Before writing them, read [references/description-design.md] (§Trigger eval query design for the query-writing craft: realistic, concrete, detailed phrasing (with a bad/good example pair); should-trigger coverage across phrasings and competing-skill cases; and should-not-trigger near-misses that are genuinely tricky, never obviously irrelevant.)

### How triggering gates on task complexity

Skills appear in Claude's `available_skills` list with their name + description, and Claude decides whether to consult a skill based on that description. The important thing to know is that Claude only consults skills for tasks it can't easily handle on its own — simple, one-step queries like "read this PDF" may not trigger a skill even if the description matches perfectly, because Claude can handle them directly with basic tools. Complex, multi-step, or specialized queries reliably trigger skills when the description matches.

This means your eval queries should be substantive enough that Claude would actually benefit from consulting a skill. Simple queries like "read file X" are poor test cases — they won't trigger skills regardless of description quality.

### Query realism

The queries must be realistic and something a Claude Code or Claude.ai user would actually type. Not abstract requests, but requests that are concrete and specific and have a good amount of detail. For instance, file paths, personal context about the user's job or situation, column names and values, company names, URLs. A little bit of backstory. Some might be in lowercase or contain abbreviations or typos or casual speech. Use a mix of different lengths, and focus on edge cases rather than making them clear-cut (the user will get a chance to sign off on them).

Bad: `"Format this data"`, `"Extract text from PDF"`, `"Create a chart"`

Good: `"ok so my boss just sent me this xlsx file (its in my downloads, called something like 'Q4 sales final FINAL v2.xlsx') and she wants me to add a column that shows the profit margin as a percentage. The revenue is in column C and costs are in column D i think"`

### Should-trigger queries (8-10): coverage

Think about coverage. You want different phrasings of the same intent — some formal, some casual. Include cases where the user doesn't explicitly name the skill or file type but clearly needs it. Throw in some uncommon use cases and cases where this skill competes with another but should win.

### Should-not-trigger queries (8-10): near-misses

The most valuable ones are the near-misses — queries that share keywords or concepts with the skill but actually need something different. Think adjacent domains, ambiguous phrasing where a naive keyword match would trigger but shouldn't, and cases where the query touches on something the skill does but in a context where another tool is more appropriate.

The key thing to avoid: don't make should-not-trigger queries obviously irrelevant. "Write a fibonacci function" as a negative test for a PDF skill is too easy — it doesn't test anything. The negative cases should be genuinely tricky.

---

## Phase 2: Review with user

Present the eval set to the user inline for review. For each query, show:

```markdown
| # | Query | Should Trigger? |
|---|-------|-----------------|
| 1 | "ok so my boss sent me this xlsx..." | ✅ Yes |
| 2 | "can you analyze the trends in..." | ❌ No |
```

Ask the user to confirm, edit, add, or remove queries before proceeding. Save the final eval set to `<workspace>/trigger-eval.json`.

This step matters — bad eval queries lead to bad descriptions.

---

## Phase 3: Run the optimization loop

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

While it runs, periodically tail the output to update the user on which iteration it's on and the scores.

The script handles the full optimization loop automatically (train/held-out-test methodology and its rationale: `references/eval-methodology.md`). When done, it opens an HTML report in the browser and returns JSON with `best_description` — selected by test score rather than train score to avoid overfitting.

### How skill triggering works

Understanding the triggering mechanism helps design better eval queries — read [references/description-design.md] (§How skill discovery actually works, plus §Trigger eval query design on why simple one-step queries don't trigger skills even when the description matches).

---

## Phase 4: Apply the result

Take `best_description` from the JSON output and update the skill's SKILL.md frontmatter. Show the user before/after and report the scores.

---