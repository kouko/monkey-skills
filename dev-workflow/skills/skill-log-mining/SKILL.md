---
name: skill-log-mining
description: >-
  Mine `~/.claude/projects/**/*.jsonl` Claude Code session transcripts joined
  with `~/.claude/usage-data/facets/*.json` `/insights` outputs, detect
  friction-signal patterns (interrupt-after-brainstorm, NEEDS_REVISION streaks,
  re-dispatch concentration, tool-error clusters), aggregate per target Skill,
  dispatch per-trajectory Haiku subagents in parallel via
  `code-toolkit:dispatching-parallel-agents`, and emit a reviewable
  `docs/skill-mining/<date>-<target>-proposals.md` whose §"Proposed additions"
  / §"Proposed modifications" blocks apply.py can write back into a target
  SKILL.md only after `--approved`. Use when auditing skill activation
  telemetry after a heavy `code-toolkit:*` cycle, when MEMORY.md is past its
  soft limit and you need graduation candidates, or before a `skill-refactor`
  session so the refactor lands on evidence not vibes. Do NOT use for creating
  new skills from scratch (use `dev-workflow:skill-creator-advance`), for
  taste-driven A/B output tuning (use `dev-workflow:skill-tuning`), for
  token / structure refactors of an existing skill (use
  `dev-workflow:skill-refactor`), or for real-time session coaching (out of
  scope at v0.1). 技能ログ採掘・SKILL.md 改善提案・トリガー漏れ検出・活性化ログ分析・
  /insights ファセット結合・並列サブエージェント分析。技能日誌挖掘・SKILL.md 迭代提案・
  觸發遺漏偵測・啟動日誌分析・/insights facet 結合・並行子代理分析。
version: 0.1.0
---

# skill-log-mining

Stage 1+2+3+5 of the v2 mining architecture: ingest Claude Code session
transcripts, attach `/insights` per-session facets, detect friction
signals, aggregate per target Skill, dispatch per-trajectory subagents
in parallel, and emit a reviewable SKILL.md edit proposal.

The skill is engine-generic; v0.1 ships `code-toolkit:*` as the default
target preset (14 sessions of dogfood evidence) with `--target-skill-pattern`
parameterizing wider scopes. Stage 4 (full SDD spec-reviewer +
code-quality-reviewer consolidation) is deferred to v0.2 if dogfood
shows orchestrator merge conflicts.

## When to use

Triggered by any of:

- **After a multi-PR cycle on a skill family** — e.g. several PRs in
  one week against `code-toolkit:*`. Friction patterns
  (NEEDS_REVISION re-dispatch streaks, interrupt-after-brainstorm,
  tool-error clusters) have accumulated and are now mineable.
- **MEMORY.md soft-limit breach** — when MEMORY.md exceeds its
  24.4 KB soft cap, you need a graduation pipeline: which auto-memory
  feedback entries should land in a skill body. Mining surfaces the
  candidates from telemetry instead of mental archaeology.
- **Before a `skill-refactor` session** — gather the evidence first;
  let the refactor diff be data-grounded, not taste-grounded.
- **Recurring "skill didn't fire when it should have"** — missed-trigger
  patterns are exactly what the `interrupt-after-brainstorm` and
  description-vs-actual-invocation diff aim at.

Example trigger phrases:

- EN: "mine my skill logs for code-toolkit", "audit skill activation
  telemetry", "what skills are graduation candidates from MEMORY.md".
- JA:「最近の code-toolkit ログを掘って改善提案を出して」「SKILL.md
  をテレメトリ根拠で iterate したい」「MEMORY.md から graduation
  候補を抽出して」.
- ZH-TW:「挖一下最近 code-toolkit 的 session log」「想根據觸發資料
  改 SKILL.md」「從 MEMORY.md 找出可以畢業到 skill 的條目」.

## When NOT to use

- **Real-time in-session coaching** — claude-coach territory; this
  skill is post-hoc batch analysis of completed sessions.
- **Discovering brand-new skills via clustering** — crune-style
  reusability scoring on unstructured prompts; this skill iterates
  *existing* SKILL.md files, it does not propose new ones.
- **`/insights` already covers it** — Claude Code 2.1.x's `/insights`
  slash command produces the per-session report. If you only need the
  session-level reflection, use `/insights` directly. This skill
  *consumes* the facet output as Stage 1 input for per-skill
  cross-session aggregation.
- **Creating a new skill from scratch** — use
  `dev-workflow:skill-creator-advance`.
- **Taste-driven output A/B tuning** — use `dev-workflow:skill-tuning`.
- **Token / structure refactor with output equivalence** — use
  `dev-workflow:skill-refactor`.

## Pipeline

Five steps; Python (Stage 1+2) → Claude (Stage 3 subagent fan-out) →
Python (Stage 5 proposal render + approval-gated write-back).

```
~/.claude/projects/**/*.jsonl                ~/.claude/usage-data/facets/*.json
              \                              /
               \                            /
                v                          v
        +-----------------------------------------+
        | scripts/main.py  (Stage 1+2)            |
        |  ingest -> facet-join -> signal detect  |
        |  -> aggregate per skill -> rank top-N   |
        +-----------------------------------------+
                              |
                              v
                          top.json  (stdout)
                              |
                              v
        +-----------------------------------------+
        | Claude reads top.json                   |
        | dispatches N subagents in parallel via  |
        | code-toolkit:dispatching-parallel-agents|
        |  one Agent call per session-trajectory  |
        |  prompts: agents/prompt-{failure,       |
        |           success}-analysis.md          |
        |  model:   claude-haiku-4-5-20251001     |
        +-----------------------------------------+
                              |
                              v
                       merged.json  (Claude collects)
                              |
                              v
        +-----------------------------------------+
        | scripts/propose.py  (Stage 5a)          |
        |   merged.json + target SKILL.md         |
        |   -> docs/skill-mining/<date>-<t>.md    |
        +-----------------------------------------+
                              |
                              v
                  Human reviews the diff
                              |
                              v  (on approval)
        +-----------------------------------------+
        | scripts/apply.py  (Stage 5b)            |
        |   --approved gate; refuses references/  |
        |   atomic write-back to SKILL.md         |
        +-----------------------------------------+
```

### Step 1 — Stage 1+2 orchestrator (Python)

```bash
python scripts/main.py \
  --target-skill-pattern 'code-toolkit:*' \
  [--config path/to/override.json] \
  [--top-n 5] \
  [--max-trajectories-per-skill 5] \
  > top.json
```

`main.py` walks `~/.claude/projects/**/*.jsonl`, joins
`~/.claude/usage-data/facets/*.json` per-session facets, runs four
signal detectors (interrupt-after-brainstorm, tool-error clusters,
NEEDS_REVISION streaks, re-dispatch concentration), aggregates by
target skill, ranks top-N by a four-axis confidence score (frequency
+ time-cost + cross-project + recency), and emits a JSON payload on
stdout plus a markdown summary on stderr.

`top.json` carries `top_skills[]` (per-skill aggregates + per-session
friction levels) and `subagent_payload[]` (per-trajectory dispatch
entries with locked Haiku model literal + prompt path + session
events). Each `trajectory_id` is a deterministic uuid5 over
`(skill, session, kind)` so re-runs of the same mine produce stable IDs.

### Step 2 — Stage 3 subagent fan-out (Claude)

Claude reads `top.json`, then issues **one Agent tool call per
`subagent_payload[]` entry inside a single assistant message** so the
harness runs them concurrently. Each subagent:

- runs on `claude-haiku-4-5-20251001` (model literal locked in
  `scripts/main.py`),
- loads `agents/prompt-failure-analysis.md` for failure-kind sessions
  or `agents/prompt-success-analysis.md` for success-kind sessions
  (`kind` is set per session by `main.py` from `/insights`
  outcome facet, falling back to friction-level heuristic),
- receives the session events + the target SKILL.md body as input,
- **returns strict-markdown Memory Items** per the schema in
  `agents/prompt-{failure,success}-analysis.md` §"Memory Item schema
  (strict markdown)" — `# {Failure|Success} Memory Item <i>` with
  `## Title` / `## Description` / `## Content` sub-headings, **not**
  raw JSON.

Use `code-toolkit:dispatching-parallel-agents` for the fan-out — it
encapsulates the "one assistant message with N Agent calls" pattern,
the per-branch TDD iron-law discipline, and verdict aggregation. See
its SKILL.md for parallel-eligibility rules (no shared files / no
sequential data dependency between sibling subagents — satisfied here
because each subagent reads a disjoint session).

### Step 3 — Collect + convert subagent outputs → `merged.json`

Each subagent emits strict-markdown Memory Items (per
`agents/prompt-{failure,success}-analysis.md` §"Memory Item schema").
**Claude must convert these markdown blocks into JSON `memory_items[]`
before piping to `propose.py`** — `propose.py` reads JSON, not
markdown. The conversion is mechanical: each `# {Failure|Success}
Memory Item <i>` block becomes one `memory_items[]` entry, with
`## Title` → `title`, `## Description` → `description`, `## Content` →
`content`, and `kind` set from which prompt was dispatched.

The merged.json top-level shape (consumed by `propose.py`,
source-of-truth schema lives at `scripts/propose.py:32-49` + canonical
example at `scripts/fixture_subagent_results.json`):

```json
[
  {
    "session_id": "<from subagent_payload>",
    "target_skill_path": "<from subagent_payload>",
    "memory_items": [
      {
        "title": "Use Read before Edit on existing files",
        "description": "Failure: agent attempted Edit before Read; tool errored.",
        "content": "When editing an existing file, always invoke Read first so the harness can track file state.",
        "kind": "failure",
        "section_anchor": "Examples",
        "requires_new_reference_file": false
      }
    ]
  }
]
```

Field notes:

- `kind` ∈ `{"failure", "success"}` — drives §"Proposed modifications"
  vs §"Proposed additions" routing in `propose.py`.
- `section_anchor` — target heading in the SKILL.md being iterated
  (e.g. `"Examples"`, `"When to Use"`). Optional; defaults to
  `"Examples"` if omitted.
- `requires_new_reference_file` — `true` routes the item into
  §"Marked for v0.2" per Q4 (v0.1 ships SKILL.md write-back only).
  Optional; defaults to `false`.

### Step 4 — Stage 5a proposal render (Python)

```bash
python scripts/propose.py \
  --input merged.json \
  --target-skill /path/to/target/SKILL.md \
  --output docs/skill-mining/<date>-<target>-proposals.md
```

`propose.py` consolidates the N subagent edit suggestions into a
single reviewable markdown with:

- `## Proposed additions` — `### Addition <n> [insert into §<Section>]`
  blocks with fenced verbatim text,
- `## Proposed modifications` — `### Modification <n> [§<Section>]`
  blocks with `- old` / `+ new` diff bodies,
- `## Marked for v0.2` — proposals requiring new `references/*.md`
  files are bucketed here per brief Q4 (SKILL.md-only at v0.1).

### Step 5 — Human review + Stage 5b approval-gated write-back

Read the proposal markdown. Eyeball each addition / modification. On
approval:

```bash
python scripts/apply.py \
  --proposal docs/skill-mining/<date>-<target>-proposals.md \
  --target-skill /path/to/target/SKILL.md \
  --approved
```

`apply.py` enforces three gates:

1. **`--approved` flag required** — without it, exit 2 (brief
   Decision §"No silent writes"). Approval is an intent statement,
   not an environment override.
2. **`references/` write refused** — exit 3. v0.1 ships SKILL.md
   write-back only; new reference files defer to v0.2.
3. **Anchor + diff exact match** — section headings must exist in
   the target; `- old` lines must match a contiguous run inside the
   anchored section. No fuzzy matching at v0.1.

Writes are atomic (temp file + `os.fsync` + `Path.replace`) so a
failed write never corrupts the target.

## Configuration

`main.py` accepts `--config path/to/override.json` to swap any of the
six baked Q5 defaults derived empirically from the v0.1 mining demo
(Pattern 1-4 findings). JSON over YAML at v0.1 per Q1 stdlib-lean
discipline — no third-party deps.

Default values (when `--config` is omitted):

```json
{
  "interrupt_window_sec": 600,
  "needs_revision_threshold": 2,
  "redispatch_threshold": 2,
  "tool_error_proximity_events": 10,
  "min_session_count": 3,
  "cross_project_count": 2
}
```

Threshold meanings:

| Threshold | Meaning |
| --- | --- |
| `interrupt_window_sec` | A user interrupt within N seconds of a `brainstorming` / `writing-plans` invocation counts as an interrupt-after-brainstorm signal. 600 s = 10 min covers "I changed my mind mid-plan" without firing on next-day resumes. |
| `needs_revision_threshold` | N or more consecutive `NEEDS_REVISION` verdicts from a code-quality-reviewer on the same task trigger a streak signal. 2 = catches "reviewer rejected, implementer fixed, reviewer rejected again" patterns. |
| `redispatch_threshold` | N or more implementer re-dispatches on a single atomic task trigger a re-dispatch-concentration signal. 2 = catches the case where the first fix didn't take. |
| `tool_error_proximity_events` | N events surrounding a tool error count as a tool-error cluster. 10 events ≈ "the tool error wasn't isolated; the surrounding context was also struggling." |
| `min_session_count` | A target skill must have at least N qualifying sessions to be ranked. 3 = filters one-off coincidences from real patterns. |
| `cross_project_count` | A signal that appears across N or more distinct project paths gets a cross-project confidence bump. 2 = "this isn't just one repo's quirk." |

To override only one threshold, supply a JSON file containing just
that key — `main.py` merges over the defaults.

## Operating notes

- **`cleanupPeriodDays` default 30** — Claude Code's `/insights`
  facets under `~/.claude/usage-data/facets/` auto-delete after 30
  days by default. Mining picks up the live state. If you want
  longer history, extend retention in Claude Code config; this skill
  does not archive facets itself.
- **No silent writes** — `apply.py` refuses to run without
  `--approved`. The flag is required even when the proposal is
  empty; the gate is an intent statement, not a content check.
- **`/insights` is interactive-only** (Claude Code 2.1.x) — to warm
  facets for a session you must type `/insights` inside Claude Code.
  There is no headless flag at the time of writing. Sessions without
  facets still flow through mining; `main.py` falls back to the
  friction-level heuristic for `kind` classification.
- **Locked Haiku model literal** — `scripts/main.py` pins
  `claude-haiku-4-5-20251001` for per-trajectory subagents.
  Architecture-template precedent: Trace2Skill paired a mid-size
  model for per-trajectory analysis with a larger one for the
  orchestrator merge.
- **Local-only by default** — mining reads
  `~/.claude/projects/**/*.jsonl` from the user's machine. No
  network calls in `main.py`, `propose.py`, or `apply.py`. The
  Stage 3 subagent dispatch is the only step that talks to the
  Anthropic API, and it's invoked by Claude, not by these scripts.
- **Skill-folder structure + `__pycache__`** — the repo's skill-folder
  rule forbids nested subdirs under any subfolder. pytest's
  `__pycache__` is mitigated via `scripts/conftest.py`
  (`sys.dont_write_bytecode = True` + `pytest_sessionfinish` cleanup)
  and `scripts/pytest.ini` (`cache_dir → /tmp`). A root
  `pyproject.toml` migration may replace this in v0.2 — see §Future.

## Future (v0.2+)

Deferred per brief Decision §"Out of Scope (v0.1)" and §"Future
roadmap":

- **Stage 4 full SDD consolidation** — if v0.1 dogfood shows
  orchestrator merge conflicts across the ≤5 per-skill subagent
  outputs, promote the merge step to a real `spec-reviewer` +
  `code-quality-reviewer` cycle.
- **YAML config swap** — JSON at v0.1 for stdlib-lean (Q1). If users
  demand inline comments or anchors, swap to YAML with PyYAML in v0.2.
- **Persistent cross-run fingerprint ledger** — SQLite or JSON
  ledger so re-runs across days can deduplicate by signal
  fingerprint, not just within-run (Q6). v0.1 counts within-run only
  for the cross-project confidence tag.
- **Codex CLI adapter** — read `~/.codex/sessions/*.jsonl` per
  research memo §Cross-agent universality.
- **Gemini / Cline / Cursor adapters** — same pattern, different
  on-disk paths.
- **`AGENTS.md` / `GEMINI.md` / `.cursorrules` write-back** —
  apply.py-style proposal application against agent-specific
  instruction files, not just SKILL.md.
- **Layer A standalone OSS surface** — extract the engine-generic
  ingest / facet-join / signal-detect / aggregate layers as a
  stand-alone tool that other agents can consume, riding the OTEL
  GenAI semantic-convention convergence.
- **`pyproject.toml` root migration** — single project-root build
  config to eliminate the per-skill `conftest.py` + `pytest.ini`
  pair, contingent on the rest of the repo migrating.

## References

- **Trace2Skill** — architecture template for trajectory → skill-edit
  distillation. arxiv 2603.25158 ·
  github Qwen-Applications/Trace2Skill (Apache 2.0).
- **crune** — reusability scoring on unstructured prompts. Useful
  contrast: crune *discovers* skills from clusters, this skill
  *iterates* existing ones. github chigichan24/crune.
- **claude-coach** — signal taxonomy + agent-guardrail framing.
  github netresearch/claude-coach-plugin.
- **Brief** — `docs/code-toolkit/specs/2026-05-22-skill-log-mining-v0.1-brief.md`
  carries the six locked decisions (Q1-Q6) and the empirical
  derivation of the Q5 thresholds from the mining-demo Pattern 1-4
  findings.
