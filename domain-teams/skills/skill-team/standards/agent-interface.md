# Agent Interface

Defines the contract between the main agent and the worker / evaluator
agents in domain-team skills. This is the Resource Paths Input Contract.

## Primary Sources

- `domain-teams/agents/worker.md` — worker role definition and Input Contract
- `domain-teams/agents/evaluator.md` — evaluator role definition and Input Contract
- Repo convention SSOT: `/Users/kouko/GitHub/monkey-skills/CLAUDE.md` §"Agent Launch Convention"

## Core Rule

> **Pass file paths, not file contents.**

The main agent never inlines the body of a standard or protocol into
an agent launch prompt. Instead, it passes absolute paths in a
structured Resource Paths block. The agent then Reads the files itself
using its own tool.

Why:
- Token efficiency — paths are ~50 bytes, file bodies can be thousands
- Traceability — the agent can cite where a claim came from
- Freshness — file content is always current at read time, not frozen
  at launch time
- Auditability — the Resource Paths block in the prompt is the
  definitive record of what context the agent had

## Worker Input Contract

When launching a `worker` agent, use this exact block structure:

```
### Task
{Plain-English description of what to produce.}

### Resource Paths
- protocol: {absolute path to one protocol .md file, OR "none"}
- standards: [
    {absolute path to standard .md file},
    {absolute path to standard .md file},
    ...
  ]
- additional: [
    {absolute paths to other reference files — optional}
  ]

### Input
{Artifact or context from the previous phase — optional}
```

Rules:
- `protocol`: exactly ONE protocol, or literally `"none"` if the task
  has no SOP. Never multiple protocols.
- `standards`: the full team-default list (all files in `standards/`),
  plus any extras specific to this workflow
- `additional`: ad-hoc reference files (other team's outputs, prior
  research notes, spec files)
- `Input`: the upstream artifact when this is a multi-phase workflow

## Evaluator Input Contract

When launching an `evaluator` agent, use this exact block structure:

```
### Resource Paths
- gate_file: {absolute path to one checklist or rubric .md file}
- standards: [
    {absolute path to standard .md file},
    ...
  ]

### Artifact
{The work product to evaluate — full content, not compressed}

### Requirements
{The original user request, or the task description the worker received}
```

Rules:
- `gate_file`: exactly ONE — the checklist or rubric for this gate
- `standards`: the full team-default list, so the evaluator can
  cross-reference standards cited in the gate file
- `Artifact`: full, uncompressed content. Compressing loses evidence.
- `Requirements`: the original asking context, so the evaluator can
  judge "was the task met?" not just "is the artifact well-formed?"

## Path Resolution

SKILL.md stores relative paths (`standards/istqb-vocabulary.md`). At
launch time, the main agent resolves to absolute paths by prepending
the skill's base directory:

```
{skill_base_path}/standards/istqb-vocabulary.md
→ /Users/.../plugins/marketplaces/monkey-skills/domain-teams/skills/qa-team/standards/istqb-vocabulary.md
```

The main agent gets the base path from the skill's runtime context
(Claude Code provides it when the skill is invoked).

Never write absolute paths directly in SKILL.md — they break when the
plugin is installed in a different location.

## Behavioral Boundaries

Knowledge access is open (any agent can Read any file in the skill
directory). Role separation is enforced by behavior, not by permission.

| Role | Produces | Does NOT produce |
|------|----------|-------------------|
| main agent | Orchestration, workflow decisions, user-facing messages | Gate verdicts |
| worker | Artifacts (docs, code, reports) | Gate verdicts (PASS/FAIL/flags) |
| evaluator | Gate verdicts + fix instructions | Modified artifacts (only judgment) |

- A worker that self-evaluates has crossed the line
- An evaluator that rewrites the artifact has crossed the line
- A main agent that produces a verdict has crossed the line

## Language Handling

Detect the user's language in the main agent, then pass it as
`output_language` in every agent launch:

```
### Task
{English or user-language description}

### Resource Paths
...

### Input
output_language: zh-TW    # or ja, en, etc.
```

The worker/evaluator produces its final artifact in the requested
language. Internal reasoning (the agent's own thinking) can be any
language; only the delivered artifact must match `output_language`.

## Worker BLOCKED Handling

If a worker determines it cannot proceed (missing data, contradictory
requirements, destructive action requested), it returns a structured
JSON block instead of an artifact:

```json
{
  "status": "BLOCKED",
  "reason": "Clear explanation of what is missing or conflicting",
  "suggested_next_steps": "What the user needs to provide"
}
```

Valid reasons to return BLOCKED (per `agents/worker.md`):
- Required library/API is deprecated and no documentation exists
- User's requirements logically contradict each other
- Task requires destructive actions not explicitly authorized
- Critical information missing and cannot be inferred
- Executing would violate security or compliance constraints

The main agent MUST:
1. NOT proceed to gates
2. Present the BLOCKED reason and suggested next steps to the user
3. Wait for user input

A BLOCKED status is not a failure of the worker — it's the worker
acting responsibly. It saves token cost by catching impossible tasks
early, rather than producing a flawed artifact the evaluator must reject.

## Output Footer Convention

Both worker and evaluator end their output with a checkpoint footer
line. This is enforced by the agent files (`agents/worker.md` and
`agents/evaluator.md`), and documented here so main agents can
recognize and route on it.

Worker footer:
```
> 🔄 CHECKPOINT: This artifact is raw output. Pipeline: consult your workflow for the next gate.
```

Evaluator footer:
```
> 🔄 CHECKPOINT: Evaluation complete. Pipeline: consult your workflow for verdict handling.
```

The main agent SHOULD use these footers to detect that a phase has
completed and decide the next workflow step (e.g., launch the next
evaluator, escalate a NEEDS_REVISION, or deliver to the user).

## Anti-Patterns

- ❌ **Inlining file content** into the launch prompt: `"Here is the
  standard: {file content}. Now do X."` — pass the path instead
- ❌ **Compressing the artifact** before evaluator launch — evaluator
  needs full content to judge completeness and cite evidence
- ❌ **Multiple protocols** in one worker launch — pick one or none
- ❌ **Evaluator modifying the artifact** — it only judges
- ❌ **Worker producing a verdict** — it produces artifacts; verdicts
  belong to evaluator
- ❌ **Absolute paths in SKILL.md** — always relative, resolve at launch
- ❌ **Skipping `Requirements` in evaluator launch** — without the
  original ask, the evaluator can't judge fit
