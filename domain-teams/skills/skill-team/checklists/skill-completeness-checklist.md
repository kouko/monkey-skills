# Skill Completeness Checklist Gate

## Evaluation Instructions

You are a strict auditor. Check each item below against the SKILL.md
and its containing skill directory. For each item, give `PASS`,
`FAIL_FIXABLE`, or `FAIL_FATAL` with specific evidence.

The failure type for each item is defined below — use the type
specified.

Grounds on: `standards/skill-md-structure.md`, `standards/file-conventions.md`.

## Checklist

- [ ] **CHK-SKL-001 (Frontmatter)** [FIXABLE]: SKILL.md opens with YAML frontmatter containing `name` (matching directory name, kebab-case) and `description` (**40–200 words**). Description contains "Use when" trigger sentences AND "Do NOT use for" delegation clauses AND a "Delivers" clause.

    **Word count rule** (matches `standards/skill-md-structure.md` §Frontmatter Schema): count only the English prose body. **Exclude** YAML tokens (`>-`, `|`, `|-`), CJK / bilingual keyword suffix lines, punctuation characters, and markdown list bullets / block-quote markers.

    **Tokenization rule** (matches standard): hyphenated compounds (`code-team`, `cross-domain`, `product-level`) count as separate word tokens — `code-team` is 2 tokens. Slash-separated compounds (`UX/UI`, `investment/market`, `SLIs/SLOs`) also split into separate tokens per segment. This makes re-verification deterministic regardless of whether the counter uses natural `wc -w` or regex-tokenized counting.

    **Router-skill exemption**: a skill with no worker or evaluator launch templates and no per-workflow protocols (e.g. `using-domain-teams`) is exempt from the 40-word minimum. Router skills still MUST contain `Use when` / `Do NOT use for` clauses but may omit the mission sentence and Delivers list. Record "router skill — exempt" in the evidence field when this exemption applies.

- [ ] **CHK-SKL-002 (Persona block)** [FIXABLE]: Immediately after frontmatter, a persona block (~15–30 lines) establishes voice and mentions: an opening stance, primary-source anchors (2–5 sources named), a `Mission:` line, a `Delivers:` line, and a `Done when:` line.

- [ ] **CHK-SKL-003 (When to Use / When NOT to Use)** [FIXABLE]: Both sections exist. "When NOT to Use" uses arrow delegation to other teams (e.g. `→ code-team`).

- [ ] **CHK-SKL-004 (Quality Gates 4-tier)** [FIXABLE]: A `## Quality Gates` section contains all four sub-sections: SELF Check, MUST Gates, SHOULD Gates, MAY Gates. MUST and SHOULD sub-sections use tables with Gate / Trigger / File columns. At least one MUST gate is defined.

- [ ] **CHK-SKL-005 (Resource Manifest)** [FIXABLE]: A `## Resource Manifest` section lists worker default resources (standards + protocol placeholder) and evaluator default resources (standards + gate file reference). Every file listed exists on disk.

- [ ] **CHK-SKL-006 (Agent Launch Protocol)** [FIXABLE]: A `## Agent Launch Protocol` section contains both a worker launch template AND an evaluator launch template as fenced code blocks. Each template uses `### Task` / `### Resource Paths` / `### Input` (worker) or `### Resource Paths` / `### Artifact` / `### Requirements` (evaluator) headers.

- [ ] **CHK-SKL-007 (Workflows)** [FIXABLE]: A `## Workflows` section contains at least one workflow with a phase table (Phase / Agent / Protocol / Input / Output columns). No phase has `--` or empty cell for Protocol (that signals a broken workflow).

- [ ] **CHK-SKL-008 (Cross-Domain Awareness)** [FIXABLE]: A `## Cross-Domain Awareness` section exists with guidance on lightweight cross-team tasks and when to switch to another team.

- [ ] **CHK-SKL-009 (Worker BLOCKED Handling)** [FIXABLE]: A `## Worker BLOCKED Handling` section exists explaining what to do when a worker returns BLOCKED (do not proceed to gates, present reason, wait for user input).

- [ ] **CHK-SKL-010 (Token budget)** [FATAL]: SKILL.md total token count is ≤ ~6,000 tokens (~4,500 words). Count includes frontmatter and all sections. Use word count as a proxy (`wc -w`); lines are unreliable due to density variation.

- [ ] **CHK-SKL-011 (Relative paths)** [FATAL]: All references to files inside the skill directory (in both SKILL.md and any protocol/standard/gate file that references other files in the skill) use relative paths (`standards/x.md`, `protocols/y.md`) — never absolute paths and never plugin-rooted paths like `domain-teams/skills/...`.

- [ ] **CHK-SKL-012 (Directory structure)** [FATAL]: The skill directory contains these required subdirectories: `standards/`, `protocols/`, `checklists/`, `rubrics/`. An optional `research/` subdirectory is permitted for grounding audit trail notes (see `standards/file-conventions.md` §Directory Semantics (research/ row) and `standards/skill-md-structure.md` §Research Subdirectory Convention). **Any other subdirectory is FATAL.** No nested subdirectories. No files at the top level other than `SKILL.md`.

    **research/ file naming check**: if `research/` exists, every file inside MUST match the pattern `grounding-v{X.Y.Z}.md` (ASCII only, version-pegged) per `file-conventions.md` §research/ file naming. Any non-conforming filename in `research/` is FATAL.

    **Absence is not a failure**: a skill without `research/` is compliant. Pre-v4.7.0 grounded skills are grandfathered without retroactive backfill.

## Verdict Rules

- Any **1 item** is `FAIL_FATAL` → final verdict is `NEEDS_REVISION` (escalate to user)
- Only `FAIL_FIXABLE` items (no FATALs) → final verdict is `PASS_WITH_NOTES` (trigger auto-revise)
- All items are `PASS` → final verdict is `PASS`

## Output Format

```json
{
  "verdict": "PASS | PASS_WITH_NOTES | NEEDS_REVISION",
  "checklist_results": [
    {
      "id": "CHK-SKL-001",
      "status": "PASS | FAIL_FIXABLE | FAIL_FATAL",
      "evidence": "Specific line or file reference",
      "fix_instruction": "How to resolve (for failing items)"
    }
  ]
}
```
