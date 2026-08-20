---
name: 2026-08-18-loom-decision-trail-as-dag-view-via-think-orbit-render
description: loom's engineering decisions are recorded in four disconnected carriers (brief Decision / plan Decision Log + Kickoff decision lines / commit Decision trailers / review verdicts) with no "what does this rest on" edge between them — give them one shared inputs field and reuse think-orbit's `render` as the human-facing DAG view instead of building loom a fifth trail
status: open
origin: 2026-08-18 think-orbit Part 1 SDD session — user asked whether loom itself needs a DAG-form CoT view to explain current decisions/specs; assessment was "the need is real, the missing piece is the dependency edge, not another renderer"
start: after the think-orbit Part 1 real-material checkpoint file (docs/loom/dogfood/2026-08-*-think-orbit-real-material.md) records go — the DAG-as-decision-trail bet must survive its own experiment first
---

- Start: after the think-orbit Part 1 real-material checkpoint file
  (docs/loom/dogfood/2026-08-*-think-orbit-real-material.md) records go —
  the DAG-as-decision-trail bet must survive its own experiment first

- Origin: 2026-08-18 think-orbit Part 1 SDD session — user asked whether
  loom itself needs a DAG-form CoT view to explain current decisions/specs;
  assessment was "the need is real, the missing piece is the dependency
  edge, not another renderer"

- **The gap**: to answer "why did we pick A, and what premise does it rest
  on" three weeks later, a loom user opens four kinds of file — the brief's
  `## Alternatives Considered` / `## Decision` (`docs/loom/specs/*.md`), the
  plan's `## Decision Log` and `Kickoff decision:` Notes lines
  (`docs/loom/plans/*.md`), commit `Decision:` trailers (git-memory), and
  review verdicts. None of them carries an edge to what it rests on. The
  2026-08-18 think-orbit session is a live case: the framing moved
  "assumption mechanism is the core" → "the CoT record is the core" → "the
  DAG is the viewing surface", and only the conclusions landed in the
  brief; the path lives in the transcript.

- **Why not just add a Mermaid**: loom already renders derived views (plan
  Task-flow diagram, brief Diagrams slot, adjudication-view). What is
  missing is the data — a decision node with `inputs` — not a renderer.
  Another standalone diagram is a fifth disconnected trail.

- **Proposed minimal shape (to brainstorm, not decided)**: give the four
  carriers one shared "rests on" field (working name `inputs`, mirroring
  think-orbit's node frontmatter `inputs: [{ref, load_bearing}]`), and
  reuse `think-orbit/skills/think-orbit/scripts/dag.py render` (Part 1
  Task 13) as the view over them — think-orbit becomes loom's viewing
  surface rather than loom growing its own. Do NOT port think-orbit's
  GOAL/FACT/CLAIM/DECISION node types onto loom decisions: the granularity
  differs (one inference vs one decision/requirement/task) and the
  2026-08-18 double-blind experiment showed richer taxonomies collapse
  agreement.

- **Evidence pointers**: think-orbit umbrella brief
  `docs/loom/specs/2026-08-18-think-orbit-plugin.md` (§Problem: "CoT
  transparent as DAG + one file per node"; §Alternatives: no shipped tool
  does user-declared premise → stale propagation); Part 1 plan
  `docs/loom/plans/2026-08-18-think-orbit-plugin-part-1.md` Task 13
  (`render`) and Task 12 (checkpoint). Vault research notes (not in repo):
  `~/kouko-obsidian-vault/research/2026-08-18 決策節點分類法的雙盲一致率實驗.md`.

- **Not this entry**: think-orbit Part 2 (views/proposal/milestones) — that
  is `docs/loom/specs/2026-08-18-think-orbit-plugin-part-2.md`.
