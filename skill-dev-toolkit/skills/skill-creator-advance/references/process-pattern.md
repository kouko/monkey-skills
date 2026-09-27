# Process Pattern Reference

**Process pattern.** This skill follows the Process pattern: every skill it produces must have a clear lifecycle — create → test → evaluate → improve → repeat.

A skill for creating new skills and iteratively improving them.

The core loop: **draft → test → review → improve → repeat**.

- Decide what the skill should do → write a draft
- Create test prompts → run claude-with-the-skill on them
- Evaluate results (qualitative review + quantitative assertions)
- Rewrite based on feedback → repeat until satisfied
- Optionally optimize the description for better triggering

Your job is to figure out where the user is in this process and help them progress — from scratch or from an existing draft. Be flexible: if they say "just vibe with me", skip the formal eval machinery.

--- 

**Usage:** This reference contains the core process pattern explanation extracted from SKILL.md for token efficiency. SKILL.md keeps only routing pointers; this reference holds the full procedural detail.

**Do NOT Load Guards**  
**SKILL.md embedding instructions include explicit guards at these points:**

- **After Step 1 (Choosing Your Eval Path)**: Only read this reference if you selected the Full eval path. Quick path users stop here.
- **Before Step 1 (Spawn all runs)**: Do NOT load this reference until you have decided on Full eval path and prepared eval_metadata.json for each test case.
- **Before Step 3 (Self-assessment pass)**: Do NOT load `references/iteration-automation.md` until all runs have completed and you have timing data captured.
- **Before Step 4 (Grade, aggregate)**: Do NOT load `agents/grader.md` or `agents/analyzer.md` until Step 4 — premature loading burns context on instructions not yet needed.

For the full process pattern details, see this file.