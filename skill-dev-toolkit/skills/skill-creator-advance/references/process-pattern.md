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

**When to read:** Read this when you need the full lifecycle framing (create → test → evaluate → improve → repeat). SKILL.md carries a condensed version inline.