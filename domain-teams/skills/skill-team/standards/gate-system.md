# Gate System

Defines the 4-tier quality gate hierarchy and the verdict semantics
that domain-team skills use to enforce quality.

## Primary Sources

- Repo convention SSOT: `/Users/kouko/GitHub/monkey-skills/CLAUDE.md` §"Quality Gates"
- Observed precedent: `qa-team/SKILL.md`, `docs-team/SKILL.md`, `devops-team/SKILL.md` Quality Gates sections
- Agent contracts: `domain-teams/agents/evaluator.md`

## The Four Tiers

Domain-team skills use exactly four gate tiers. Tier determines how a
gate interacts with the workflow.

### 1. SELF Check (every delivery, always)

- **Who runs it**: the main agent or worker, on its own output
- **When**: immediately before delivering any artifact
- **What**: a 4-step self-audit — re-read the request, list 3-5 acceptance criteria, verify each, fix any issues
- **Fails**: the artifact is revised until SELF check passes; the user never sees a pre-SELF-check draft
- **Why it's mandatory**: evaluators are launched for MUST/SHOULD gates, but SELF check catches cheap errors (typos, missing sections) without burning an evaluator turn

SELF check is NOT a file — it is written as a numbered process in
SKILL.md §Quality Gates.

### 2. MUST Gates (auto-trigger, non-skippable)

- **Trigger**: explicit trigger condition (e.g. "output is a README.md" or "output contains deployment configs")
- **When**: after worker delivers artifact, before returning to user
- **What**: evaluator runs a checklist or rubric
- **Fails**: on FAIL_FATAL or 2+ warnings, verdict is NEEDS_REVISION — the main agent stops and presents the issue to the user
- **Cannot be skipped**: the main agent MUST launch the evaluator if the trigger matches; "skipping for speed" is an anti-pattern

Typical MUST gates cover: structural completeness, security, correctness
of output format.

### 3. SHOULD Gates (auto-trigger, skippable with stated reason)

- **Trigger**: same as MUST (matches an output condition)
- **When**: after MUST gates pass
- **What**: evaluator runs a checklist or rubric, usually quality-focused
- **Skippable**: the main agent may skip if it states a reason ("legacy monolith — 12-Factor not applicable", "user explicitly accepted lower quality for speed")
- **Fails**: verdict handled same as MUST

Typical SHOULD gates cover: quality dimensions, style conformance,
depth of grounding.

### 4. MAY Gates (optional)

- **Trigger**: explicit user request OR specific workflow condition
- **When**: only when requested
- **Why the distinction**: MAY gates are usually expensive (full audit, benchmark) or narrowly applicable (only for one workflow)

Typical MAY gates cover: audits, detailed quality reviews, specialist checks.

## Verdict Semantics

Both checklists and rubrics produce one of these verdicts.

| Verdict | Meaning | Next action |
|---------|---------|-------------|
| `PASS` | All checks pass / all green | Gate cleared, proceed |
| `PASS_WITH_NOTES` | 1 yellow flag OR only FAIL_FIXABLE items | Auto-revise, re-run from first MUST gate |
| `NEEDS_REVISION` | ≥1 red flag OR ≥1 FAIL_FATAL OR 2+ yellow | STOP, escalate to user |
| `NEEDS_METADATA` (docs-team only) | Required metadata is missing, cannot judge | Not a revision — add metadata or skip gate with reason |

### Auto-revise rules

When a gate returns `PASS_WITH_NOTES`:
1. Main agent relaunches worker with: original requirements + current artifact + evaluator feedback
2. Worker produces a revised artifact
3. Re-run from the FIRST MUST gate (not just the gate that flagged)
4. Each retry launches a FRESH evaluator — no accumulated retry history
5. Cap: 2-3 rounds. After the cap, escalate to user as NEEDS_REVISION.

### Escalation rules

When a gate returns `NEEDS_REVISION`:
1. Do NOT auto-revise
2. Present the evaluator's full feedback to the user
3. Wait for user decision (fix approach, skip gate with reason, abandon task)

## Checklist vs Rubric Format

### Checklists (`checklists/*.md`)

Binary, ID-tagged, per-item verdict.

Structure:
1. **Evaluation Instructions** — strict auditor framing
2. **Checklist** — bulleted items with `CHK-{SCOPE}-{NNN}` IDs and `[FATAL]` or `[FIXABLE]` tags
3. **Verdict Rules** — how to combine item verdicts into overall verdict
4. **Output Format** — JSON schema for the evaluator's response

Each item must specify:
- The check (what the evaluator looks for)
- The failure type (FATAL or FIXABLE)
- The evidence requirement (specific file reference or finding)

### Rubrics (`rubrics/*.md`)

Qualitative, flag-based, dimension-scored.

Structure:
1. **Scope Boundary** (optional) — what the rubric does/doesn't review
2. **Flag Definitions** — for each dimension, define 🔴 Fatal / 🟡 Warning / 🟢 Clear
3. **Verdict Rules** — how to combine flags (usually: 1 🔴 → NEEDS_REVISION; 2+ 🟡 → NEEDS_REVISION; 1 🟡 → PASS_WITH_NOTES; all 🟢 → PASS)
4. **Rules** — editorial guidance (e.g. "don't be a gatekeeper", "require alternatives on NEEDS_REVISION")
5. **Output Format** — usually prose, not JSON

## Design Discipline

### Keep gates SSOT

The gate criteria live in the gate file, NOT in SKILL.md. SKILL.md only
references the gate by filename. This avoids drift when criteria change.

### Trigger conditions must be unambiguous

"Output contains deployment configs" is better than "whenever relevant".
Vague triggers make gates skippable-in-practice.

### Gate count budget

Per team skill, suggested budget:
- MUST: 1–3 gates (one per critical output type)
- SHOULD: 1–3 gates
- MAY: 0–3 gates

Too many MUST gates turn every delivery into a grind. Too few means
quality is advisory only.

### Cross-domain: delegate, don't duplicate

If an artifact needs a quality check from another domain (e.g.
docs-team needs security review of a technical README), delegate to
that team's gate rather than copying criteria.

## Anti-Patterns

- ❌ SELF check skipped "because it's a simple task"
- ❌ MUST gate marked optional because "it's slow"
- ❌ Inlining gate criteria into SKILL.md
- ❌ Gates that duplicate what another team's gate already checks
- ❌ Auto-revise on NEEDS_REVISION (only PASS_WITH_NOTES auto-revises)
- ❌ Accumulating retry history across auto-revise rounds (must be fresh evaluator each time)
- ❌ Compressing artifacts before passing to evaluator (loses evidence)
