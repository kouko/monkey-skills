# Capture Intent Reference

Purpose: Extracted from SKILL.md for token efficiency. The main skill file keeps only routing pointers; this reference holds the full protocol.

---

## Do NOT Load Guards

**SKILL.md embedding instructions include explicit guards at these points:**

- **Before Capture Intent**: Load only when starting a full skill creation workflow (not a simple redesign)
- **Skip if**: The user's request is simply "help me write a skill" without any specific workflow — use the full creation flow instead

---

## Capture Intent

Start by understanding the user's intent. The current conversation might already contain the workflow to capture (e.g., "turn this into a skill") — if so, **extract answers from the conversation history first** (tools used, step sequence, corrections the user made, input/output formats observed); the user fills gaps and confirms before proceeding.

Clarify these four questions:
1. What should this skill enable Claude to do?
2. When should this skill trigger? (what user phrases/contexts)
3. What's the expected output format?
4. Should we set up test cases? Objectively verifiable outputs (file transforms, data extraction, code generation, fixed workflow steps) benefit from test cases. Subjective outputs (writing style, creative work) often don't benefit from quantitative test cases — evaluate these qualitatively by reviewing outputs inline with the user and using the quick eval path with direct feedback. Suggest the appropriate default, but let the user decide.

## Interview and Research

Proactively ask questions about edge cases, input/output formats, example files, success criteria, and dependencies. Wait to write test prompts until you've got this part ironed out.

Check available MCPs — if useful for research (docs, similar skills, best practices), research in parallel via subagents if available, otherwise inline. Come prepared with context to reduce burden on the user.