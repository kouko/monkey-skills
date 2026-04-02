# Design Spec: Single-Plugin Manifest & Documentation Update
Date: 2024-03-24
Topic: Manifest and Documentation Update after Single-Plugin Merge

## 1. Goal
The objective is to synchronize the repository's manifest and documentation files to reflect the transition from a multi-plugin "Pattern B" structure to a single-plugin flat structure.

## 2. Context
The directory structure has changed from:
```
monkey-skills/
└── plugins/
    ├── code-team/
    │   ├── skills/
    │   └── agents/
    └── design-team/
        ├── skills/
        └── agents/
```
To a flat structure:
```
monkey-skills/
├── agents/
└── skills/
    ├── code-team/
    ├── design-team/
    └── ...
```

## 3. Proposed Changes

### 3.1 `GEMINI.md`
- Replace imports targeting `plugins/*/skills/` with the root `skills/` path.
- Example: `@./plugins/code-team/skills/using-code-team/SKILL.md` becomes `@./skills/using-code-team/SKILL.md`.

### 3.2 `AGENTS.md`
- Update the description of the `agents/` folder to accurately reflect it as the root for all agent definitions.

### 3.3 `.claude-plugin/marketplace.json`
- Overwrite with a single plugin entry for `monkey-skills` instead of a list of plugins.
- Current structure: `{"name": "monkey-skills", "plugins": [...]}`.
- New structure: Requested JSON object with `source: "."`.

### 3.4 `.claude-plugin/plugin.json` (New/Update)
- Create or update with:
```json
{
  "name": "monkey-skills",
  "description": "Personal agent skills — code, design, research teams + obsidian workflows + youtube processing",
  "version": "1.0.0"
}
```

### 3.5 `README.md` and other root files
- Update the visual directory tree.
- Update the "Installation" instructions for Claude Code to a single command `claude plugin install monkey-skills` instead of installing multiple plugins.
- Fix any remaining relative paths that point to `plugins/`.

## 4. Testing & Verification
- **Validation:** Use `grep_search` to ensure no `plugins/` references remain in the documentation or manifests.
- **Verification:** Ensure all `SKILL.md` paths in `GEMINI.md` are valid by checking for their existence.

## 5. Self-Review
- **Placeholder scan:** No placeholders.
- **Consistency:** The changes consistently reflect the root-level `skills/` and `agents/` folders.
- **Scope check:** This covers all requested files and any others needing updates for structural consistency.
- **Ambiguity check:** The prompt specifically requested `source: "."` in `marketplace.json`, which I will follow.

## 6. Implementation Plan (Summary)
1. Read each file to be updated.
2. Use `replace` or `write_file` to apply the changes.
3. Use `grep_search` to verify.
