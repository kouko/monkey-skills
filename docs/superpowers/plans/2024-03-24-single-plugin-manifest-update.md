# Single-Plugin Manifest Update Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Synchronize manifest and documentation files to reflect the transition from a multi-plugin structure to a single-plugin flat structure.

**Architecture:** Targeted updates to manifest files and documentation to ensure all paths point to the root-level `skills/` and `agents/` directories.

**Tech Stack:** `replace` tool, `write_file` tool, `grep_search` tool.

---

### Task 1: Update `GEMINI.md` Imports

**Files:**
- Modify: `GEMINI.md`

- [ ] **Step 1: Replace multi-plugin skill paths with flat root-level skill paths**

```markdown
@./plugins/code-team/skills/using-code-team/SKILL.md
@./plugins/design-team/skills/using-design-team/SKILL.md
@./plugins/research-team/skills/using-research-team/SKILL.md
@./plugins/obsidian-workflow/skills/using-obsidian-workflow/SKILL.md
@./plugins/youtube-skills/skills/using-youtube-skills/SKILL.md
```
becomes:
```markdown
@./skills/using-code-team/SKILL.md
@./skills/using-design-team/SKILL.md
@./skills/using-research-team/SKILL.md
@./skills/using-obsidian-workflow/SKILL.md
@./skills/using-youtube-skills/SKILL.md
```

- [ ] **Step 2: Commit**

```bash
git add GEMINI.md
git commit -m "docs: update GEMINI.md skill paths for flat structure"
```

---

### Task 2: Update `AGENTS.md` Description

**Files:**
- Modify: `AGENTS.md`

- [ ] **Step 1: Update the agents directory description**

Change `All agent definitions are in agents/` (if it was outdated) to reflect the new root structure.

- [ ] **Step 2: Commit**

```bash
git add AGENTS.md
git commit -m "docs: update AGENTS.md description"
```

---

### Task 3: Update `.claude-plugin/marketplace.json`

**Files:**
- Modify: `.claude-plugin/marketplace.json`

- [ ] **Step 1: Replace the `plugins` array with a single entry for the consolidated plugin**

```json
{
  "name": "monkey-skills",
  "description": "Personal agent skills — code, design, research teams + obsidian workflows + youtube processing",
  "source": "."
}
```

- [ ] **Step 2: Commit**

```bash
git add .claude-plugin/marketplace.json
git commit -m "chore: consolidate marketplace.json to single plugin"
```

---

### Task 4: Create/Update `.claude-plugin/plugin.json`

**Files:**
- Create: `.claude-plugin/plugin.json`

- [ ] **Step 1: Define the single plugin metadata**

```json
{
  "name": "monkey-skills",
  "description": "Personal agent skills — code, design, research teams + obsidian workflows + youtube processing",
  "version": "1.0.0"
}
```

- [ ] **Step 2: Commit**

```bash
git add .claude-plugin/plugin.json
git commit -m "chore: add/update root plugin.json"
```

---

### Task 5: Update `README.md` Structure and Instructions

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update repository structure tree**

Ensure it shows:
```
monkey-skills/
├── agents/
└── skills/
```

- [ ] **Step 2: Update installation instructions for Claude Code**

Change:
```bash
claude plugin marketplace add kouko/monkey-skills
claude plugin install code-team@monkey-skills
...
```
to:
```bash
claude plugin marketplace add kouko/monkey-skills
claude plugin install monkey-skills
```

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: update README.md structure and install guide"
```

---

### Task 6: Final Verification

**Files:**
- Scan: Root directory files

- [ ] **Step 1: Scan for any remaining `./plugins/` paths**

Run: `grep -r "./plugins/" . --exclude-dir=.git`

- [ ] **Step 2: Fix any remaining paths found**

- [ ] **Step 3: Verify all paths in `GEMINI.md` are valid**

Run a script or check manually for file existence.
