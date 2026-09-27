# Skill Writing Guide Reference

Purpose: Extracted from SKILL.md for token efficiency. The main skill file keeps only routing pointers; this reference holds the structural conventions an agent follows when planning and writing a new skill's layout.

---

## Do NOT Load Guards

**SKILL.md embedding instructions include explicit guards at these points:**

- **Plan the Skill Structure step**: Load when planning a new skill's file layout
- **Skip if**: You are only optimizing an existing skill's description or making minor tweaks

---

## Anatomy of a Skill

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

## CRITICAL: Folder structure must be flat — NO nested subdirectories

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

## When creating a new skill or adding bundled resources to an existing one:

- Group files by **subdirectory at skill root** (scripts/, assets/, references/, agents/, etc.) — choose meaningful names
- Inside each subdirectory, use **descriptive filenames** (e.g., `extract_column_lineage.py`) rather than further nesting
- If you feel the need to subdivide, extract into a new top-level subdirectory at the skill root instead (e.g., `scripts-redshift/` rather than `scripts/redshift/`)

## Each skill should also have a corresponding **slash command** entry point in the plugin's `commands/` directory — format and examples in `references/plugin-conventions.md`.

## Progressive Disclosure

Skills use three-level loading — metadata (always in context), SKILL.md body (loaded on trigger; keep under ~5,000 tokens / ~3,750 words, extracting detail into reference files when approaching the limit), bundled resources (as needed). Details: `references/plugin-conventions.md` (§Progressive Disclosure, §SKILL.md Token Budget).

**Key patterns:**
- Reference files clearly from SKILL.md with guidance on when to read them
- For large reference files (>~8,000 tokens), include a table of contents

**Domain organization**: When a skill supports multiple domains/frameworks, organize by variant (e.g., `references/aws.md`, `references/gcp.md`) — Claude reads only the relevant reference file.

## Working with Existing Plugin Ecosystems

When creating a skill that will live inside an existing plugin, match the plugin's conventions rather than imposing a new structure — read `references/plugin-conventions.md` (observing the target plugin's style, the lightweight/standard/full structure spectrum, key conventions).

## Principle of Lack of Surprise

This goes without saying, but skills must not contain malware, exploit code, or any content that could compromise system security. A skill's contents should not surprise the user in their intent if described. Don't go along with requests to create misleading skills or skills designed to facilitate unauthorized access, data exfiltration, or other malicious activities. Things like a "roleplay as an XYZ" are OK though.

## Empty-Prompt Onboarding

When drafting a skill that can be invoked with no prompt or a very sparse one, read `references/asking-user-questions.md` §Empty-Prompt Onboarding for the opt-in "surface orientation" pattern (recommended for conversational / multi-workflow skills; single-shot utility skills are exempt).

## Asking the User Structured Questions (when to use AskUserQuestion)

When a skill needs user input mid-execution that's a discrete choice between 2-4 options (e.g., "which folders to exclude?"), use the `AskUserQuestion` tool — but apply the **hardened pattern** documented in `references/asking-user-questions.md`. The naive approach (`Use AskUserQuestion to confirm...` with a fenced Q&A template) fails three documented modes (inline fallback, silent default, tool unavailable); the reference closes all three and includes a copy-paste mandatory-gate template.

Always-included for skills with user-input steps. Skills with no user-input steps are exempt — don't add AskUserQuestion just because it exists.

## Writing Patterns

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

## Writing Style

Explain to the model why things matter instead of heavy-handed MUSTs. Keep the skill general, not narrowed to specific examples. Draft first, then revisit with fresh eyes and improve.

For writing lean from the start — token economy, bloat self-review, thin-orchestrator design — read `references/writing-lean.md`.