# Skill Completeness Checklist Gate

## Evaluation Instructions

You are a strict auditor. Check each item below against the SKILL.md
and its containing skill directory. For each item, give `PASS`,
`FAIL_FIXABLE`, or `FAIL_FATAL` with specific evidence.

The failure type for each item is defined below — use the type
specified.

Grounds on: `standards/skill-md-structure.md`, `standards/file-conventions.md`.

## Checklist

- [ ] **CHK-SKL-001 (Frontmatter)** [FIXABLE]: SKILL.md opens with YAML frontmatter containing `name` (matching directory name, kebab-case) and `description` (two-tier length: normal skills **target ≤150 chars, 250 is a SOFT lint line** (not a hard cap); router/CONDITIONAL skills exception band **≤500** REQUIRING a firing-evidence note in the evidence field; **≥30 word-token floor** either way — number authority: `skill-dev-toolkit/skills/skill-creator-advance/references/description-design.md` §Principle 5). Description contains a "Use when" trigger sentence AND a positive delegation redirect ("→ sibling-team", not "Do NOT use for X") AND (optional) a "Delivers" clause.

    **Word count rule** (matches `standards/skill-md-structure.md` §Frontmatter Schema): count only the English prose body. **Exclude** YAML tokens (`>-`, `|`, `|-`), CJK / bilingual keyword suffix lines, punctuation characters, and markdown list bullets / block-quote markers.

    **Tokenization rule** (matches standard): hyphenated compounds (`code-team`, `cross-domain`, `product-level`) count as separate word tokens — `code-team` is 2 tokens. Slash-separated compounds (`UX/UI`, `investment/market`, `SLIs/SLOs`) also split into separate tokens per segment. This makes re-verification deterministic regardless of whether the counter uses natural `wc -w` or regex-tokenized counting.

    **Router-skill exemption**: a skill with no worker or evaluator launch templates and no per-workflow protocols (e.g. `using-domain-teams`) is exempt from the 30-word minimum. Router skills still MUST contain a `Use when` clause and a positive delegation redirect but may omit the mission sentence and Delivers list. Record "router skill — exempt" in the evidence field when this exemption applies.

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

- [ ] **CHK-SKL-012 (Directory structure)** [FATAL]: The skill directory contains these required subdirectories: `standards/`, `protocols/`, `checklists/`, `rubrics/`. An optional `research/` subdirectory is permitted for grounding audit trail notes (see `standards/file-conventions.md` §Directory Semantics (research/ row) and `standards/skill-md-structure.md` §Research Subdirectory Convention). **Any other subdirectory is FATAL.** No nested subdirectories. Top-level files are limited to `SKILL.md` (required), plus optionally `README.md`, `README.{lang}.md` BCP 47 translations, and `test-prompts.json` (behavioral eval input set; see `standards/file-conventions.md` §Top-Level Files for the full table and the README.md / SKILL.md coexistence rule). Any other top-level file is FATAL.

    **research/ file naming check**: if `research/` exists, every file inside MUST match the pattern `grounding-v{X.Y.Z}.md` (ASCII only, version-pegged) per `file-conventions.md` §research/ file naming. Any non-conforming filename in `research/` is FATAL.

    **Absence is not a failure**: a skill without `research/` is compliant. Pre-v4.7.0 grounded skills are grandfathered without retroactive backfill.

- [ ] **CHK-SKL-013 (Empty Invocation Fallback)** [FIXABLE]: SKILL.md contains a `## Empty Invocation Fallback` section (per `standards/skill-md-structure.md` §Empty Invocation Fallback Rules). The section MUST contain the 3 required elements:

    1. **Surface orientation** — references `standards/skill-md-structure.md` §Surface Orientation Format (synthesis from frontmatter / When to Use / When NOT to Use / Workflows / intake protocol). A static "≤5-line intro" is no longer acceptable — runtime synthesis is required.
    2. **Route to intake** — either references an existing brainstorming protocol by relative path (`protocols/{team}-brainstorming.md`) OR provides 2-3 bootstrap questions covering scope / inputs / output expectation
    3. **Sufficient-context skip** — explicit rule that fallback is bypassed when ANY of 5 context sources provides an actionable brief: (a) current-turn prompt ≥50 chars, (b) prior conversation, (c) IDE context (`<ide_selection>`, opened files), (d) plan / memory file, (e) upstream skill handoff. Checking only current-turn prompt length is FAIL_FIXABLE — the check must cover all 5 sources.

    **Hard-gate variant**: skills with mandatory intake (`copywriting-team`, `planning-team`) replace element 3 with "Never skip" plus a short rationale (intake surfaces elements context cannot reliably provide — Schwartz awareness, voice, job story, risks). This variant PASSES CHK-SKL-013 when the rationale is present.

    **Router-skill exemption**: skills whose sole purpose is routing (`using-domain-teams`, `using-philosophers-toolkit`) are exempt and do NOT need this section. Record "router skill — exempt" in the evidence field when this exemption applies.

- [ ] **CHK-SKL-014 (AskUserQuestion Pattern)** [FIXABLE]: When SKILL.md or any bundled file contains a reference to `AskUserQuestion` (tool invocation, mandatory step, user-input prompt), the section using it MUST follow the hardened pattern documented in `standards/asking-user-questions.md`. Specifically, all four hardenings MUST be present:

    1. **MUST verb** — wording uses `MUST call AskUserQuestion`, `must call`, or an explicit mandatory-gate clause (`This step is mandatory. Do not proceed to STEP X+1 without...`). Soft phrasings (`Use AskUserQuestion`, `Consider using`) FAIL.
    2. **Args-schema example** — a fenced ` ```json` block shows the actual tool-call argument shape (`{ "questions": [...] }`). Prose Q&A templates (`Question: ... Options:`) FAIL.
    3. **Fallback contract** — explicit clause for tool-unavailable environments (subagent / web client / sandbox) that mandates inlining the question rather than silently defaulting. Absence FAILS.
    4. **(Recommended) marker** — when default option exists, first option's `label` field includes `(Recommended)` suffix. Prose-level "(recommended default)" labels in flat option lists FAIL.

    **Exemption**: skills with NO user-input branching steps are exempt. Record "no user-input steps" in the evidence field. Examples: pure deterministic skills (formatters, lint), single-shot generators, skills where input is gathered upstream by another skill.

    **Why this matters**: industry research and an empirical A/B test (subagent context, 2026-05-04) confirmed that the soft-verb pattern fails in three modes (inline fallback, silent default, tool-unavailable). The 4 hardenings close all three. See `standards/asking-user-questions.md` for full rationale, references, and copy-paste mandatory-gate template.

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
