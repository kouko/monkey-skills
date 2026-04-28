# File Conventions

Defines the semantic boundaries of the four subdirectories under a
domain-team skill, plus naming and path rules.

## Primary Sources

- Observed precedent: all 7 existing domain-team skills (`code-team`, `docs-team`, `qa-team`, `devops-team`, `research-team`, `design-team`, `planning-team`)
- Repo convention SSOT: `/Users/kouko/GitHub/monkey-skills/CLAUDE.md` §"Skill Structure"

## Directory Semantics

Every domain-team skill has **four required** subdirectories plus one
**optional fifth** (`research/`). Each has a distinct role in the read
chain of worker/evaluator agents.

| Directory | Required? | Purpose | Who reads it | Typical file count |
|-----------|-----------|---------|--------------|-------------------|
| `standards/` | Required | SSOT rules, terminology, primary-source anchors. Stable, slow-changing. | Both worker and evaluator, every launch | 1–6 |
| `protocols/` | Required | Workflow SOPs — step-by-step "how to produce X". Execution recipes. | Worker, one selected per task | 2–8 |
| `checklists/` | Required | Binary PASS / FAIL_FIXABLE / FAIL_FATAL gate criteria. | Evaluator, one per gate | 1–3 |
| `rubrics/` | Required | Qualitative 🔴 / 🟡 / 🟢 flag-based gate criteria. | Evaluator, one per gate | 1–4 |
| `research/` | **Optional** | Primary-source grounding audit trail. Deep research notes from grounding refactors. **NOT read by worker/evaluator at runtime** — maintainer-facing only. Exempt from Diátaxis single-quadrant rule (research notes are fundamentally mixed-mode: Explanation + Reference + ADR). | Humans (PR reviewer, future maintainer) | 0–1 per version |

### Why `research/` is optional

Only skills that have undergone a primary-source grounding refactor need
a `research/` subdirectory. Skills created before the grounding research
convention existed (pre-v4.7.0) are grandfathered without retroactive
backfill, unless their original research was captured in a recoverable
form. The presence of a `research/` directory is a signal that the skill
has been grounded to the v4.7.0+ standard; its absence does not imply
the skill is ungrounded, only that its research audit trail pre-dates
the in-repo convention.

### research/ file naming

- One file per grounding event: `grounding-v{X.Y.Z}.md` where X.Y.Z is
  the plugin version that landed the grounding work (e.g.
  `grounding-v4.6.0.md` for code-team's initial grounding at v4.6.0)
- ASCII only in filename — CJK goes in the file body, never the filename
- No dates in the filename — dates live in git log and frontmatter

### When to use standards vs protocols

- **standards/** answers "what counts as right?" (rules, taxonomies, citations)
- **protocols/** answers "how do I produce this artifact step by step?"

Example: `sre-practices.md` in standards is *what SLIs / SLOs mean*; `monitoring-design.md` in protocols is *the 7-step workflow to design monitoring for a service*.

### When to use checklists vs rubrics

- **checklists/** are used when each item is objectively verifiable (present/absent, exact format, file exists)
- **rubrics/** are used when judgment is required (severity, adequacy, coherence)

Example: `readme-completeness.md` in checklists (`Section X exists: PASS/FAIL`) versus `diataxis-mode-clarity.md` in rubrics (`Mixing modes: 🔴 severe / 🟡 mild / 🟢 none`).

## File Naming

- **Case**: kebab-case (`infra-conventions.md`, not `infra_conventions.md` or `InfraConventions.md`)
- **Extension**: `.md` only
- **Descriptive**: `readme-completeness.md`, not `check1.md`
- **Suffix convention**:
  - Checklists: `{topic}-checklist.md` (e.g. `deployment-safety-checklist.md`)
  - Rubrics: `{topic}-gate.md` or topic alone (e.g. `iac-quality-gate.md`, `viewpoint-coverage.md`)
  - Standards: topic-only, no suffix (e.g. `sre-practices.md`)
  - Protocols: verb-noun or topic-only (e.g. `test-plan-writing.md`, `codebase-assessment.md`)

## Path Discipline

### Relative paths inside SKILL.md

Always relative from the skill root. The skill root is the directory
containing SKILL.md (e.g. `domain-teams/skills/qa-team/`).

✓ `standards/istqb-vocabulary.md`
✗ `domain-teams/skills/qa-team/standards/istqb-vocabulary.md`
✗ `/Users/kouko/GitHub/monkey-skills/domain-teams/skills/qa-team/standards/istqb-vocabulary.md`

Reason: Claude Code provides the skill base path at runtime; absolute
or plugin-rooted paths break portability across platforms (Copilot CLI,
Gemini CLI, Codex).

### One level flat — no nesting

Files go directly under `standards/`, `protocols/`, etc. Do NOT create
sub-subdirectories like `standards/japanese/jstqb.md`. If grouping is
needed, encode it in the filename (`jstqb-vocabulary.md`).

Reason: discovery. Workers and evaluators scan one level; nested dirs
require Glob walks and break the "Resource Manifest lists everything"
contract.

### Absolute paths only at launch time

The main agent resolves relative paths to absolute when launching a
worker or evaluator. See `agent-interface.md` for the exact protocol.

## Standards Splitting Discipline

When a standards file grows beyond its Tier-appropriate token budget
(Tier 1: ~2,500 tokens; Tier 2: ~4,000 tokens; Tier 3: ~7,000 tokens)
OR when its content no longer fits a single conceptual axis, split it.
The choice of split axis determines whether the result matches how
practitioners in the domain actually organize the subject matter.

### Three split axes

| Axis | When to use | Example |
|---|---|---|
| **Topic split** | Content covers two or more **independent subjects** with no hierarchical relationship | docs-team v4.3.0: `doc-writing.md` → `diataxis-mode-matrix.md` + `google-style.md` — Diátaxis and Google Style are independent authorities, not layers of the same concept |
| **Tier split** | Single topic, but **parametric strength** varies by sub-concept (some parts LLM-known, others hallucination hotspots) | Splitting Clean Code (Tier 1) from 徳丸本 Ch.6 (Tier 3 JP) when both could fit in one `code-quality.md` |
| **Scale-hierarchy split** | Single subject domain, but **practitioners organize it by analytical scale** — hierarchical layers where each layer asks a qualitatively different question | research-team v4.11.0: `investment-analysis-canon.md` (646 lines) → `investment-macro-regime.md` (L1) + `investment-sector-industry.md` (L2) + `investment-security-valuation.md` (L3) + `investment-portfolio-construction.md` (portfolio meta) |

### Scale-hierarchy decision rule (added v4.11.0)

Scale-hierarchy is appropriate when ALL of:

1. The domain has a **natural professional-practice taxonomy** —
   e.g., top-down investment (macro → sector → security → portfolio),
   strategic planning (strategic → tactical → operational), software
   architecture (system → module → function)
2. Each layer asks a **qualitatively different question**, not just a
   more detailed version of the same question
3. Practitioners specialize by layer (Macro Strategist vs Sector
   Analyst vs Equity Analyst vs Portfolio Manager — distinct roles)
4. Cross-layer claims exist but are a minority — most content is
   layer-local

When these hold, scale-hierarchy split produces files that match
professional mental models AND enable **per-layer loading** (worker
loads only the layer(s) needed by the question — see
`agent-interface.md §Per-Phase Resource Narrowing`).

### Do NOT use scale-hierarchy when

- The "layers" are actually independent topics pretending to be
  hierarchical → topic-split instead
- The "layers" are just increasingly detailed versions of the same
  concept → tier-split instead
- The domain has **no accepted professional taxonomy** for the split
  — inventing a scale taxonomy is the self-invented-taxonomies
  anti-pattern, even if the split looks clean

### Cross-layer claims require bridge sections

Scale-hierarchy splits inevitably leave some load-bearing claims that
span two layers (e.g., CAPE is both L1 market valuation AND L3
individual P/E in research-team v4.11.0; sector rotation is a
L1↔L2 bridge). Each cross-layer claim needs an explicit `## Cross-
Layer Usage Notes` section (or equivalent cross-reference) in BOTH
affected files — see `grounding-principle.md §Cross-Layer Bridge
Preservation` for the full rule.

## Deletion Over Deprecation

When a file becomes obsolete, delete it. Do NOT:
- Keep a stub file with "see X.md" redirects
- Keep `.legacy.md` or `.old.md` copies
- Leave commented-out references in SKILL.md

Reason: stale files bloat the skill directory and mislead agents who
Glob for resources. Git history preserves the old version.

Precedent: qa-team v4.2.0 deleted `test-conventions.md` (self-invented,
superseded by ISTQB grounding); docs-team v4.3.0 deleted `qa-gate.md`
and `doc-writing.md` (split into Diátaxis-specific files).

## Top-Level Files

A skill directory may contain these files at the top level:

| File | Required? | Purpose |
|------|-----------|---------|
| `SKILL.md` | Required | LLM-discovery SSOT — frontmatter + workflows + gate triggers. Read by Claude when the skill is invoked. |
| `README.md` | Optional | Human-facing GitHub-rendered overview. Optional sibling to `SKILL.md`; the two serve different audiences. See §README.md and SKILL.md Coexistence below. |
| `README.{lang}.md` | Optional | i18n translations of `README.md` using BCP 47 tags (e.g., `README.ja.md`, `README.zh-TW.md`). Only meaningful when `README.md` exists. |

No other files at the skill top level.

### README.md and SKILL.md Coexistence

**`SKILL.md` is the LLM-discovery SSOT.** Frontmatter (`name`, `description`),
workflow tables, gate triggers, and resource manifest live here. Claude
reads it when the skill is invoked.

**`README.md` is the human-facing overview.** GitHub renders `README.md`
when present (preferred over `SKILL.md` because of YAML frontmatter at the
top of the latter). Use `README.md` for: project background, install
instructions, usage examples, file-layout map, contributing notes,
license. It is **explanatory and accessibility-oriented**, not a
duplicate of `SKILL.md`'s LLM-discovery content.

When both exist:

- They MUST NOT contradict each other (e.g., different gate lists, different
  workflow names)
- `README.md` SHOULD link to `SKILL.md` for the authoritative workflow /
  gate / agent definitions; `README.md` summarizes, `SKILL.md` specifies
- Updates to gate names, workflow phases, or resource paths land in
  `SKILL.md` first; `README.md` follows in the same PR if affected

This dual-file pattern was adopted in v5.3.0 to improve GitHub UX without
sacrificing LLM-discovery clarity. The pattern is **opt-in per skill** —
skills without `README.md` continue to use `SKILL.md` as the only
top-level file.

## Anti-Patterns

- ❌ Nested directories under `standards/`, `protocols/`, `checklists/`, `rubrics/`
- ❌ Files at the skill top level other than `SKILL.md`, `README.md`, or `README.{lang}.md`
- ❌ Absolute paths or plugin-rooted paths inside SKILL.md
- ❌ Stub files or deprecation redirects
- ❌ Files with `.old`, `.bak`, `.legacy` suffixes
- ❌ `README.md` that duplicates `SKILL.md` content verbatim — they serve
  different audiences and must be intentionally distinct
