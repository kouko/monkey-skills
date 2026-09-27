# Plugin Conventions

This file documents conventions for plugin structure, folder layout,
slash commands, and token budget management.

## Folder Structure
- SKILL.md at root
- Single-level subdirectories only (references/, scripts/, agents/, etc.)
- No nested subdirectories

## Slash Commands
Each skill should have a corresponding slash command entry point in the plugin's `commands/` directory.

### Format
- File: `commands/<skill-name>.md` (or `commands/<plugin>/<skill-name>.md` for multi-skill plugins)
- Frontmatter required:
  ```yaml
  ---
  name: <skill-name>
  description: One-line description of what the skill does
  category: <skill-category>
  ---
  ```
- Body: Brief usage instructions, key triggers, and example invocations

### Examples
**Simple skill:**
```markdown
---
name: json-to-yaml-converter
description: Convert JSON files to YAML format
category: conversion
---

# /json-to-yaml-converter

Convert JSON files to YAML format.

**Usage:** `/json-to-yaml-converter <input.json> [--output <output.yaml>]`

**Triggers:** "convert this JSON to YAML", "save as YAML"
```

**Complex skill:**
```markdown
---
name: skill-creator-advance
description: Create new skills with evaluation-first workflow
category: development
---

# /skill-creator-advance

Create new skills using an evaluation-first development workflow.

**Usage:** `/skill-creator-advance <intent>`

**Triggers:** "build a skill", "make a slash command", "redesign [a skill]", "improve [a skill]"
```

## Token Budget
- SKILL.md under 5,000 tokens
- Progressive disclosure via Do NOT Load guards
- Reference files for content exceeding token limits

## Progressive Disclosure
- Core skill logic stays the same
- Platform-specific adaptations in dedicated files
- Use conditional loading based on detected platform

## SKILL.md Token Budget
- Target: ~5,000 tokens (~3,750 words) soft limit
- Extract detail to reference files behind Do NOT Load guards when approaching limit
- Each reference file: ~2,000-5,000 tokens depending on complexity
- Total skill package: ~25,000 tokens max for reliable context handling