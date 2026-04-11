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

## Anti-Patterns

- ❌ Nested directories under `standards/`, `protocols/`, `checklists/`, `rubrics/`
- ❌ Files outside these four directories (except SKILL.md itself)
- ❌ Absolute paths or plugin-rooted paths inside SKILL.md
- ❌ Stub files or deprecation redirects
- ❌ Files with `.old`, `.bak`, `.legacy` suffixes
- ❌ `README.md` inside a skill directory (SKILL.md *is* the readme)
