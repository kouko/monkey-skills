---
name: distill-sessions
description: |
  Mine past Claude Code session transcripts + /insights for friction patterns → a per-skill improvement-proposals doc. Use to audit skill-activation telemetry, or gather evidence before a refactor. For creating a skill use skill-creator-advance.
version: 0.5.1
---

# distill-sessions

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

## Bare invocation — preview-then-confirm

When invoked with no scoping context (e.g. user types `/distill-sessions`
alone, or "fire distill-sessions" with no target named), do NOT default
to full pipeline. Instead:

1. **Run Stage 1+2 preview only** — `python scripts/main.py
   --target-skill-pattern 'code-toolkit:*'` (the brief-locked v0.1
   default). This is cost-free local Python — no API call, seconds to
   complete. Print the stderr summary block (top-N skills + per-session
   friction levels) verbatim to chat.
2. **Pause for user confirmation before Stage 3** — Stage 3 is the
   expensive step (N parallel Sonnet subagents, each consuming a
   multi-hour session as input). Ask which subset to dispatch:
   single highest-friction skill / top-3 / all / different target
   pattern / stop at preview.
3. **Surface the context-overflow status** in the preview summary when
   relevant — the locked Sonnet 4.6 model has a 1M-context window.
   Overflow is a theoretical floor: the v0.3 post-ship dogfood
   observed max 559K tokens (56% of the 1M cap); skip+warn fires only
   for trajectories exceeding 1M tokens, none observed across v0.1 +
   v0.3 dogfood rounds. If any payload entry is projected to exceed 1M
   tokens (rough: `len(json.dumps(payload.input)) // 4 > 1_000_000`),
   warn the user and recommend filtering down before dispatch. See the
   [v0.3 post-ship dogfood memory](../../../.claude/projects/-Users-kouko-GitHub-monkey-skills/memory/project_distill_sessions_v0_3_post_ship_dogfood.md)
   for the empirical overflow distribution baseline.

This protocol exists because (a) bare invocation has no signal about
intent — `code-toolkit:*` is the v0.1 preset but the user may actually
want a different scope, (b) Stage 3 budget cost is non-trivial and
asymmetric to the cheap-preview, and (c) user's CLAUDE.md "Issue First"
discipline expects confirmation before deliverable-producing work.

When the user provides explicit scoping in their prompt (e.g. "挖一下
writing-plans", "audit code-toolkit:brainstorming activations", "MEMORY.md
graduation candidates"), skip the preview-pause and execute the
referenced flow directly.

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
  `skill-dev-toolkit:skill-creator-advance`.
- **Taste-driven output A/B tuning** — use `skill-dev-toolkit:skill-tuning`.
- **Token / structure refactor with output equivalence** — use
  `skill-dev-toolkit:skill-refactor`.

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
        |  model:   claude-sonnet-4-6              |
        +-----------------------------------------+
                              |
                              v
                       merged.json  (Claude collects)
                              |
                              v
        +-----------------------------------------+         +-----------------------------------------+
        | scripts/propose.py  (Stage 5a)          |         | scripts/report.py  (Stage 5c)           |
        |   merged.json + target SKILL.md         |         |   merged.json + --lang {zh-TW|en|ja}    |
        |   -> docs/skill-mining/<date>-<t>.md    |         |   -> JSON dispatch payload (stdout)     |
        +-----------------------------------------+         |   -> Claude dispatches subagent at      |
                              |                             |      agents/prompt-advisory-analyst.md  |
                              |                             |   -> orchestrator writes returned md to |
                              |                             |      docs/skill-mining/<date>-          |
                              |                             |      advisory-report.md                 |
                              |                             +-----------------------------------------+
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
entries with locked Sonnet 4.6 model literal + prompt path + session
events). Each `trajectory_id` is a deterministic uuid5 over
`(skill, session, kind)` so re-runs of the same mine produce stable IDs.

High-friction-success sessions (friction_level="high" AND
facet.outcome ∈ success-strings) emit TWO entries with distinct
`trajectory_id` values — one routed to `prompt-failure-analysis.md`,
one to `prompt-success-analysis.md`. **Counting caveat**: `--max-trajectories-per-skill`
counts dispatches, not sessions, so one such session consumes 2 of
the budget.

### Step 2 — Stage 3 subagent fan-out (Claude)

Claude reads `top.json`, then issues **one Agent tool call per
`subagent_payload[]` entry inside a single assistant message** so the
harness runs them concurrently. Each subagent:

- runs on `claude-sonnet-4-6` (model literal locked in
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
        "section_anchor": "Examples",          // REQUIRED (v0.2) — must match a real heading in the target SKILL.md
        "requires_new_reference_file": false   // optional, default false
      }
    ]
  }
]
```

Field notes:

- `kind` ∈ `{"failure", "success"}` — drives §"Proposed modifications"
  vs §"Proposed additions" routing in `propose.py`.
- `section_anchor` — target heading in the SKILL.md being iterated
  (e.g. `"Examples"`, `"When to Use"`). **REQUIRED** as of v0.2 — the
  field must be present and non-blank, or `normalize_memory_item`
  raises `ValueError`. v0.1's silent default of `"Examples"` proved
  dead on real code-toolkit SKILL.md files; the orchestrator (or the
  subagent populating the item) MUST pick a real heading. If
  `propose.py` finds the anchor doesn't match any heading in the
  target SKILL.md at render time, the item routes to
  §"Anchor mismatch — needs review" rather than producing a
  dead-anchor addition / modification.
- `requires_new_reference_file` — `true` routes the item into
  §"Marked for v0.2" per Q4 (v0.1 ships SKILL.md write-back only).
  Optional; defaults to `false`.

### Step 3.5 — Stage 4 cluster: cross-session promotion (Python)

`propose.py` calls `cluster_memory_items(items, min_n=2)` (from
`scripts/cluster.py`) **before** the partition-and-render step. This
clusters Memory Items by normalized title + section anchor, splits them
into:

- **`promoted[]`** — items with N≥2 supporting sessions; these flow
  through to §"Proposed additions" / §"Proposed modifications" as usual
  (per decision Q-v0.3-1 Choice A from the brief),
- **`pending[]`** — items from a single session; these route to the new
  §"Cross-session evidence pending" bucket where they preserve their
  per-session anchor and wait for more evidence.

This is the minimal Stage 4 cluster promised in the v0.1 brief (§"Stage 4
full SDD consolidation"). Single-session items are not silent — operators
see them grouped, can manually re-route high-confidence ones if desired,
and they re-promote automatically on the next run once N≥2 sessions
support the same item (by title + anchor match).

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
- `## Anchor mismatch — needs review` — items whose `section_anchor`
  doesn't match any heading in the target SKILL.md (v0.2). Each entry
  names the dead anchor + lists the valid headings so the operator can
  re-route. `apply.py` would refuse these at the DiffMismatch gate
  anyway — surfacing them up-front prevents silent misapplication.
- `## Cross-session evidence pending` — Memory Items from a single
  session (N=1 cluster). Not yet pattern-confirmed; preserved here
  pending more evidence. Re-run after more session data accumulates.
- `## Marked for v0.2` — proposals requiring new `references/*.md`
  files are bucketed here per brief Q4 (SKILL.md-only at v0.1).

### Step 4b — Stage 5c advisory report (Python + Sonnet 4.6 subagent)

```bash
python scripts/report.py \
  --input merged.json \
  --lang zh-TW \
  [--output docs/skill-mining/<date>-advisory-report.md] \
  > dispatch_payload.json
```

v0.5 architecture: `report.py` is a thin payload constructor — it reads
the same `merged.json` produced by the subagent fan-out (Step 3),
validates `--lang`, and emits a JSON dispatch payload on stdout. The
orchestrator then dispatches one Sonnet 4.6 subagent at
`agents/prompt-advisory-analyst.md`, reads the returned markdown, and
writes it to `--output` (default `docs/skill-mining/<today>-advisory-report.md`).
The analyst — not Python — does the clustering, dedup, and prose.

**Orchestrator dispatch — 4 steps (cold-start checklist)**:

```
1. Read  agents/prompt-advisory-analyst.md
         → load the subagent's role, workflow, output template, hard constraints.
2. Read  the stdout JSON from `python report.py --input <merged.json> --lang <locale>`
         → extract `dispatch_payload.input` (merged_data / lang / date_str)
           and `output_path` (where to write the result).
3. Agent({subagent_type: "general-purpose", model: "sonnet",
          prompt: <prompt body + JSON input data>})
         → wait for the subagent to return the rendered markdown.
4. Write the subagent's response verbatim to `output_path`.
         No editing, no preamble — the response IS the file body.
```

**Model alias note**: the prompt's YAML frontmatter declares
`model: claude-sonnet-4-6` as documentation reference, but the actual
`Agent()` call uses the harness-level alias `model: "sonnet"` (which
the runtime routes to the current Sonnet generation — currently 4.6).
Passing the literal `"claude-sonnet-4-6"` to `Agent()` will fail enum
validation.

Key properties:

- **Mandatory `--lang zh-TW|en|ja`** — no default; explicit per
  invocation. The flag controls explanatory prose only; code blocks /
  identifiers / target SKILL.md and CLAUDE.md snippets stay English
  because they are English source artifacts. Mirrors the user's
  CLAUDE.md "Working languages: Traditional Chinese / Japanese /
  English (match my message language)" rule.
- **Independent surface** — report.py is not required for the
  `propose.py` → `apply.py` flow. Run it after Step 4 (propose.py) for
  a cross-target human summary; skip if you only need per-target
  proposals.
- **Inputs** — same `merged.json` as `propose.py`; no target SKILL.md
  argument (report is cross-target, not per-target).
- **Output** — single file (not one-per-target like proposals); 7
  sections: top anti-patterns (≤5 semantic clusters), per-target
  SKILL.md modification list, ≤5 CLAUDE.md candidates (semantic dedup
  across targets), new-skill candidates, numbers summary, action steps,
  and a header block naming the run + `--lang`.
- **Semantic clustering via LLM** — the advisory-analyst subagent does
  the clustering natively in its prompt. This supersedes v0.4.1's
  surface-token heuristic which merged unrelated items via shared
  generic tokens (the v0.4.1 first-dogfood collapsed 31/33 Memory
  Items into a single cluster via the `axis` token); semantic
  clustering is the v0.5 fix and there is no `--mode heuristic`
  fallback (clean break per Q-v0.5-3).
- **Cost** — ~$0.23 / run (1 Sonnet 4.6 call, ~50K input + ~5K output
  tokens). Negligible vs Stage 3 (~$3-8 / run across N parallel
  trajectory subagents).
- **Suggested invocation** — run post-`propose.py`, same `merged.json`.
  Provides the "why am I repeatedly fixing this?" human perspective that
  complements the per-target machine-actionable proposals.

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

- **Cross-skill friction-density routing** — when a session invokes
  multiple target skills (e.g. brainstorming + writing-plans), the
  orchestrator computes a severity score for each (session, skill) pair
  based on accumulated signal weights in that session. Memory Items
  route to the skill with the highest score; alphabetic is the tie-break.
  This ensures Memory Items attribute to the friction-owning skill, not
  lexically-first.
- **§Cross-session evidence pending bucket** — when reviewing proposals,
  triage single-session items (N=1) separately. They are preserved
  intentionally, not bugs; they become promotable to full proposals once
  a subsequent run shows a second session with the same evidence.
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
- **Locked subagent model (v0.4)** — `scripts/main.py` pins
  `SUBAGENT_MODEL_ID = "claude-sonnet-4-6"` for per-trajectory
  subagents (previously Haiku 4.5, swapped in v0.4). The 1M-context
  window covers all v0.3-observed trajectory sizes (max 559K observed
  in v0.3 post-ship dogfood = 56% of cap). Cost note: ~3× prior Haiku
  pricing; acceptable at locked cadence (2-5×/week post-PR cycle) per
  [v0.4 brief Q-v0.4-1](../../../docs/code-toolkit/specs/2026-05-26-distill-sessions-v0.4-brief.md).
  Operator can override at orchestration time per v0.1 bare-invocation
  protocol (pause-for-confirmation gate at Stage 3).
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

  **Operator discipline (v2.6.1)**: always run pytest with
  `PYTHONDONTWRITEBYTECODE=1`:

  ```bash
  PYTHONDONTWRITEBYTECODE=1 python -m pytest dev-workflow/skills/distill-sessions/scripts/ -v
  ```

  Reason: `conftest.py`'s own bytecode is written *before*
  `sys.dont_write_bytecode = True` runs (chicken-and-egg). The env-var
  blocks all bytecode at interpreter start, before any module loads —
  no `__pycache__` ever appears, so the `validate-skill-folder-structure.sh`
  PostToolUse hook does not fire on subsequent Edit/Write tool calls.
  If `__pycache__` does accidentally appear, do NOT use `rm -rf` — the
  repo's `dcg` safety hook blocks it. **Also avoid** the inline
  `python -c "import shutil; shutil.rmtree(...)"` shortcut: `dcg` rule
  `heredoc.python:shutil_rmtree` matches the string `shutil.rmtree(`
  inside a `python -c` heredoc and refuses too. The dcg-safe pattern
  is a two-pass `find -delete`:

  ```bash
  find dev-workflow/skills/distill-sessions -type d -name __pycache__ \
    -print | xargs -I {} find {} -type f -delete
  find dev-workflow/skills/distill-sessions -type d -name __pycache__ \
    -empty -delete
  ```

## Future (v0.2+)

Deferred per brief Decision §"Out of Scope (v0.1)" and §"Future
roadmap":

- **v1.0 broad-scope `skill-log-mining` sibling** — this skill
  (`distill-sessions`) is the narrow v0.1 ship of a wider vision
  documented in `docs/code-toolkit/specs/2026-05-22-skill-log-mining-v0.1-brief.md`.
  The broad-scope `skill-log-mining` is planned to also surface
  (a) new-skill proposals from clustering recurring prompts (crune-style),
  (b) `CLAUDE.md` rule extractions from recurring user corrections
  (claude-coach-style). v0.1 explicitly excluded both to ship the
  narrowest end state first; v1.0 will re-brainstorm the unified
  pipeline that covers all three surfaces.
- **Stage 4 full SDD consolidation** — minimal Stage 4 (title+anchor
  cluster + N≥2 promotion) shipped at v0.3 part-2; full `spec-reviewer` +
  `code-quality-reviewer` triad version deferred to v0.5+ if minimal
  proves insufficient.
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
- **Brief** — `docs/code-toolkit/specs/2026-05-22-distill-sessions-v0.1-brief.md`
  carries the six locked decisions (Q1-Q6) and the empirical
  derivation of the Q5 thresholds from the mining-demo Pattern 1-4
  findings.
