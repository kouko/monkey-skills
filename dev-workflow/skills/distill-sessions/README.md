# Skill Log Mining

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Mine `~/.claude/projects` JSONL transcripts plus `/insights` facets
> to surface missed-trigger patterns in shipped `dev-workflow:*` and
> `loom-code:*` skills, then propose data-grounded edits to their
> SKILL.md files.

A user-invoked **skill-iteration skill**: when you've run a stretch of
multi-PR work and want to know which of your shipped skills are
under-triggering, mis-triggering, or accumulating friction, you invoke
this skill to get a ranked top-N report plus concrete proposed diffs
against each target SKILL.md.

This README is for humans reading the skill on GitHub. The operational
file Claude actually loads is [`SKILL.md`](SKILL.md).

---

## Why this exists

**The graduation pipeline**: MEMORY.md collects per-project feedback
memos like "reviewer mis-aggregation", "parallel-dispatch doc-code
race", "lint-checks.md second drift surface". Each entry is a friction
signal — usually pointing at a specific shipped skill whose
description, anti-pattern list, or activation triggers missed.
Reading the memos manually and remembering to fold them back into the
right SKILL.md is the failure mode this skill exists to prevent.

The author of a skill can't reliably catch this themselves. The skill
*feels* well-targeted because they wrote the description. Only when
measured against the actual JSONL transcript record — where the skill
should have fired but didn't, or fired and the user immediately
interrupted — does the gap become visible.

This skill captures that measurement. The core formula:

> **Shipped Skill Quality = What the description claims × What the logs prove**

Every shipped skill is ranked on four normalized signals:

- **frequency_norm** — how often it appears in friction sessions
- **time_cost_norm** — how much friction time it accumulates
- **cross_project_norm** — how many projects show the pattern
- **recency_norm** — how recent the pattern is

A high-confidence target is one the logs flag repeatedly across
multiple projects in the last 30 days. A low-confidence target is one
flagged once, in one project, two months ago.

---

## How it works

The skill runs a multi-stage pipeline:

```
~/.claude/projects/*.jsonl  +  ~/.claude/usage-data/facets
              │
              ▼  Stage 1+2: scripts/main.py
              │   - friction-signal detection
              │   - per-skill aggregation
              │   - top-N ranking
              ▼
       JSON payload (stdout) + Markdown summary (stderr)
              │
              ▼  Stage 3: Claude dispatches subagents via
              │   loom-code:dispatching-parallel-agents
              │   - one Haiku-4.5 subagent per (skill, session)
              │   - failure vs success prompt selected per friction
              ▼
       per-trajectory analysis JSON
              │
              ▼  Stage 3 (cont.): scripts/propose.py
              ▼
       diff file (proposed SKILL.md edits)
              │
              ▼  human review (silent-writes refused)
              │
              ▼  scripts/apply.py --approved
              ▼
       edits land in the target SKILL.md files
```

See [`SKILL.md`](SKILL.md) §Pipeline for the full step-by-step.

### Key v0.3 features

- **Cross-skill friction-density routing** — when a session invokes
  multiple target skills (e.g. brainstorming + writing-plans), Memory
  Items route to the skill with the highest severity score in that
  session, not the lexically-first skill. This ensures feedback
  attributes to the friction-owning skill.

- **Dual-dispatch on high-friction-success sessions** — sessions
  classifying `friction_level="high"` AND outcome=success emit **two**
  subagent_payload entries — one routed to failure-analysis, one to
  success-analysis. The `--max-trajectories-per-skill` budget counts
  both dispatches.

- **Stage 4 cluster + N≥2 promotion** — Memory Items cluster by
  normalized (title, section_anchor) pair. Items with N≥2 supporting
  sessions promote to §"Proposed additions" / §"Proposed modifications";
  single-session items (N=1) route to the new §"Cross-session evidence
  pending" bucket and re-promote automatically when a second session
  matches.

---

## Installation

The skill ships with the `dev-workflow` plugin. In Claude Code:

```
Skill(skill: "dev-workflow:distill-sessions")
```

Or, if a slash-command alias is configured:

```
/distill-sessions
```

No external dependencies — the Python scripts are stdlib-only and
target `python3.11+`.

---

## Quick start

```bash
# From the repo root, with no overrides — uses the Q5 defaults:
cd dev-workflow/skills/distill-sessions/scripts
python3 main.py
```

Expected output sketch:

```
# distill-sessions v0.1 — run summary    (stderr)

- run_id: `b3a1...`
- target_pattern: `loom-code:*`
- top_n: 5
- max_trajectories_per_skill: 5

## Top skills

- **loom-code:writing-plans**
  - session `2026-05-20-...`: friction=high, events=12
  - session `2026-05-18-...`: friction=mid,  events=7
- **loom-code:brainstorming**
  - session `2026-05-19-...`: friction=mid,  events=5
...
```

Stdout receives the full JSON payload (top_skills + subagent_payload)
consumed by the next stage of the pipeline.

---

## Configuration

v0.1 ships with 6 baked-in defaults from the brief Q5. To override,
pass a JSON config:

```bash
python3 main.py --config /path/to/my-thresholds.json
```

The override schema is documented in
[`SKILL.md`](SKILL.md) §Configuration. CLI flags also exist for the
most common levers:

- `--target-skill-pattern` (default `loom-code:*`)
- `--top-n` (default `5`)
- `--max-trajectories-per-skill` (default `5`)
- `--project-root` (override `~/.claude/projects`, mainly for tests)
- `--facets-root` (override `~/.claude/usage-data/facets`)

---

## Future roadmap

v0.2+ deferred items (see [`SKILL.md`](SKILL.md) §Future for the
full list):

- Stage 4 SDD consolidation when proposals across runs conflict
- YAML config swap for the override schema
- Persistent cross-run fingerprint ledger
- Codex / Gemini / Cline / Cursor CLI adapters
- Layer A standalone OSS surface

---

## License

This skill is part of the [monkey-skills](https://github.com/kouko/monkey-skills)
repository, MIT-licensed — see the repository root `LICENSE` file.

### Third-party attributions

The two prompt-analyst templates under `agents/` are direct adaptations of
Trace2Skill (arxiv 2603.25158 / github.com/Qwen-Applications/Trace2Skill,
Apache 2.0 License). The MIT license of monkey-skills is compatible with the
Apache 2.0 license of the upstream — both permit commercial + derivative use
with attribution preserved.
