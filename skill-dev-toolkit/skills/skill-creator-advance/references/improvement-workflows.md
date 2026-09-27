# Improvement Workflows Reference

Purpose: The situational workflows of skill-creator-advance — quick-path testing, structural rewrite flow, the improvement iteration loop, and blind comparison — extracted from SKILL.md for token efficiency. SKILL.md keeps only routing pointers; this reference holds the full procedural detail.

---

## Do NOT Load Guards

**SKILL.md embedding instructions include explicit guards at these points:**

- **Quick eval path: Testing**: "Read only when running the Quick eval path."
- **Case (c) Structural Rewrite Flow**: "Read only when the improvement router identified case (c) — a structural change."
- **Improving the skill (iteration loop)**: "Read after presenting eval results, when turning user feedback into skill changes."
- **Advanced: Blind comparison**: "Read only when the user asks whether the new version is actually better."

---

## Quick eval path: Testing

For skills on the quick eval path, skip Step 0 (Evaluation-First) and test the draft directly: come up with 2-3 realistic test prompts — the kind of thing a real user would actually say — and share them with the user: "Here are a few test cases I'd like to try. Do these look right, or do you want to add more?" (not necessarily verbatim). Then run them. **For improvements to an existing skill, also run the old skill version on the same test cases as the baseline comparison** (snapshot before editing: `cp -r <skill-path> <workspace>/skill-snapshot/`); for brand-new skills, no baseline is needed.

Save test cases to `evals/evals.json`. Don't write assertions yet — just the prompts. You'll draft assertions later if you escalate to the full path.

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

**Quick-path iteration loop:** After improving the skill, rerun the 2-3 test cases manually — for improvements, include baseline comparison (run the old skill version on the same test cases); iterate on direct user feedback as in the original Quick eval path. Keep going until the user says they're happy, the feedback is all empty, or you're not making meaningful progress.

---

## Case (c): Structural Rewrite Flow

For case (c) — structural change (add / split / merge phases, change agent decomposition, change input/output contract) — use this flow (steps 1–4). **Skip Step 0 (Evaluation-First)** — the skill already has eval cases from its original creation or previous improvements; reuse those. Cases (a) and (b) hand off to the dedicated sibling skills (`skill-refactor`, `skill-tuning`) and do **not** use these steps. Case (d) is handled by the Description Optimization workflow.

### 1. Assess the Current State

Read the existing SKILL.md and all bundled files. Understand:
- What the skill does and how it's structured
- What conventions it follows (check the parent plugin's style)
- Known issues the user reports or you observe

### 2. Diagnose Improvement Areas

Look at these dimensions (these apply to **structural** rewrites; they are not the right lens for token refactor or output A/B):
- **Triggering**: Is the description specific enough? Does it undertrigger or overtrigger?
- **Instructions**: Are they clear? Do they explain the "why"? Are there gaps?
- **Structure**: Is the directory organization appropriate for the skill's complexity?
- **Coverage**: Are edge cases handled? Are there missing workflows?
- **Bundled files**: Are reference files up to date? Are scripts working?

### 3. Propose Changes

Present a concise improvement plan to the user before making changes. Group changes by impact:
- **High impact**: Changes that affect the skill's core behavior or triggering
- **Low impact**: Cleanup, reorganization, wording improvements

### 4. Evaluate

Use the eval workflow (quick or full path, depending on complexity) to verify improvements. When improving an existing skill, the baseline should be the original version — snapshot it before editing:

```bash
cp -r <skill-path> <workspace>/skill-snapshot/
```

Then use the improvement iteration loop below.

---

## Improving the skill (the iteration loop)

The heart of the loop: turn the user's feedback on the test results into a better skill.

### How to think about improvements

1. **Generalize from the feedback.** You're creating a skill to be used a million times across many prompts; you iterate on a few examples only for speed — a skill that works only for those examples is useless. Rather than fiddly overfitty changes or oppressively constrictive MUSTs, when an issue is stubborn try branching out — different metaphors, different patterns of working. It's cheap to try and you might land on something great.

2. **Keep the prompt lean.** Remove things that aren't pulling their weight. Read the **transcripts**, not just the final outputs — outputs tell you *what* happened, transcripts *how*. If the skill makes the model waste time on unproductive work, remove the parts causing it.

3. **Explain the why.** Today's LLMs have good theory of mind and, given a good harness, go beyond rote instructions. Even if the user's feedback is terse or frustrated, understand why they wrote what they wrote and transmit that understanding into the instructions. If you find yourself writing ALWAYS or NEVER in all caps, that's a yellow flag — reframe and explain the reasoning so that the model understands why it matters.

4. **Look for repeated work across test cases.** If the transcripts show subagents independently writing similar helper scripts or taking the same multi-step approach (all 3 test cases wrote a `create_docx.py`), that's a strong signal the skill should bundle that script: write it once, put it in `scripts/`, and tell the skill to use it.

### The loop

After improving the skill:

1. Apply your improvements to the skill
2. **For Full eval path:** Rerun all test cases into a new `iteration-<N+1>/` directory, including baseline runs. If you're creating a new skill, the baseline is always `without_skill` (no skill) — that stays the same across iterations. If you're improving an existing skill, use the snapshot of the current version (taken before editing) as the baseline for all iterations. This ensures consistent comparison against the version being improved.
3. **For Quick eval path:** Rerun the 2-3 test cases manually as described in the Quick eval path section above.
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