# Plugin Conventions Reference

This document provides detailed guidance for creating skills that integrate
well with existing plugin ecosystems. Read this when building a skill that
will live inside an established plugin directory.

---

## Observing the Target Plugin

Before writing any code, read 2-3 existing skills in the target plugin to
absorb its conventions. Pay attention to:

1. **Directory depth** — Does each skill use subdirectories (standards/,
   protocols/, checklists/, rubrics/) or a flat layout (SKILL.md + references/)?
2. **Frontmatter style** — How long are descriptions? Do they include negative
   triggers? Multilingual keywords?
3. **Tone and persona** — Is the skill written as an imperative guide, a
   conversational companion, or a formal specification?
4. **Bundled file patterns** — Are reference files short (<100 lines) or
   comprehensive (300+ lines with TOC)?
5. **Naming conventions** — kebab-case? Suffixes like `-team`? Prefixes like
   `obsidian-`?

Match what you find. Consistency within a plugin matters more than following
a universal template.

---

## Structure Spectrum

Choose the right level of structure based on the skill's complexity:

### Lightweight Structure
Best for: focused tools, formatters, single-workflow skills.

```
skill-name/
├── SKILL.md
└── references/     (optional, for long reference content)
    └── guide.md
```

**When to use**: The skill does one thing well. Its instructions fit
comfortably in SKILL.md alone (under ~3,000 tokens). No quality gates
or multi-phase workflows are needed.

### Standard Structure
Best for: multi-step workflows, skills with evaluation criteria.

```
skill-name/
├── SKILL.md
├── references/
├── agents/         (subagent instructions)
├── scripts/        (deterministic/automation tasks)
└── assets/         (templates, HTML files)
```

**When to use**: The skill orchestrates multiple steps, spawns subagents,
or includes automation scripts.

### Full Structure (domain-teams style)
Best for: team-scoped skills with quality gates and primary-source grounding.

```
skill-name/
├── SKILL.md
├── standards/      (SSOT rules, primary-source grounding)
├── protocols/      (step-by-step SOPs)
├── checklists/     (binary pass/fail gates)
└── rubrics/        (qualitative scoring)
```

**When to use**: The skill enforces a disciplined process with formal quality
gates (SELF / MUST / SHOULD / MAY tiers). Typically used in `domain-teams/`.

---

## Key Conventions

### SKILL.md Token Budget
Keep the SKILL.md body under **~6,000 tokens** (~4,500 words). If approaching
this limit, extract detailed content into reference files and add clear
pointers from SKILL.md. Use word/token count rather than line count — lines
vary too much in density to be a reliable measure.

### Relative Paths
Always use **relative paths** (relative to the skill directory) when referencing
bundled files from SKILL.md:
- Good: `references/schemas.md`, `agents/grader.md`
- Bad: `dev-workflow/skills/skill-creator-advance/references/schemas.md`

Claude Code provides the base path at runtime; bundled files resolve from
the skill directory.

### Bundled File Organization
- `references/` — Docs loaded into context as needed
- `agents/` — Instructions for spawned subagents
- `scripts/` — Executable code for deterministic/repetitive tasks
- `assets/` — Files used in output (templates, icons, HTML)
- Scripts can execute without being loaded into context

### Progressive Disclosure
Skills use a three-level loading system:
1. **Metadata** (name + description) — Always in context (~100 words)
2. **SKILL.md body** — Loaded when the skill triggers (~6,000 tokens ideal)
3. **Bundled resources** — Loaded as needed (unlimited size)

---

## Slash Commands

Every skill should have a corresponding **slash command** entry point in the
plugin's `commands/` directory.

### Format

```markdown
---
description: "Brief description of what the command does."
---

Use the {plugin-name}:{skill-name} skill to handle this request.
```

### Example

For a skill named `skill-creator-advance` in the `dev-workflow` plugin:

**File**: `dev-workflow/commands/skill-creator-advance.md`

```markdown
---
description: "Create, improve, and evaluate skills with iterative testing and description optimization."
---

Use the dev-workflow:skill-creator-advance skill to handle this request.
```

### Conventions
- The command file name should match the skill name (kebab-case)
- The description should be a concise one-liner (distinct from the full
  skill description)
- The body delegates to the skill — do not duplicate skill instructions here
- One command per skill; router skills (e.g., `using-domain-teams`) are
  the exception where one command routes to multiple skills
