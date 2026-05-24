# Plan: skill-log-mining v0.1 — Part 1 (scaffold + Stage 1 ingest/normalize + Stage 2 aggregate)

> ✏️ **2026-05-24 post-ship note** — shipped as **`dev-workflow:distill-sessions`** (PR #328). Plan terminology (`skill-log-mining`) is the historical narrow-scope codename; final skill name was changed to `distill-sessions` at branch-finishing time to free the broader `skill-log-mining` name for a future v1.0 that also covers new-skill discovery + CLAUDE.md rule extraction. See the brief's preface for context.

**Source brief**: docs/code-toolkit/specs/2026-05-22-skill-log-mining-v0.1-brief.md
**Total tasks**: 5 (≤5 ✓)
**Execution order**: parallel-where-possible (T1 → T2 → (T3 ∥ T4) → T5)
**Plan-document-reviewer verdict**: PASS (2026-05-22, round 2 — round 1 NEEDS_REVISION on check 3 + check 11, both fixed)

## Plan-time decisions locked (5 deferred-from-brief Open Questions)

1. **Language**: Python stdlib only (json / pathlib / re / dataclasses / argparse / datetime). PyYAML NOT added at v0.1 — config override is JSON. Brief Q5 said "YAML"; plan-time downgrade to JSON to preserve stdlib-lean Q1. README documents v0.2 may swap to YAML if dogfood demand surfaces.
2. **LLM model**: Haiku 4.5 for per-trajectory analyst subagents (Stage 3); Sonnet 4.6 for orchestrator merge (Stage 5). Locked here so prompt files in Part 2 know their target model.
3. **UI surface**: stdout markdown summary on `python scripts/main.py` run; full proposal diff written to `docs/skill-mining/<date>-<target-skill>-proposals.md`. No interactive `AskUserQuestion` per proposal at v0.1.
4. **Layer A OSS**: v0.1 does NOT publish. Surface in README §"Future" as "OTEL GenAI semantic conventions still Development status — Layer A standalone OSS is a v1.0+ option, not v0.1 scope."
5. **JSONL retention**: README §"Operating notes" cites `cleanupPeriodDays` default 30; no archival policy at v0.1.

## Cross-cutting plan notes

- **Commit format**: per CI whitelist (memory feedback_cc_type_whitelist.md, 9 prior hits) — type ∈ {feat / fix / refactor / chore / docs / test}, MANDATORY kebab-case scope. Suggested per-task commit: `feat(skill-log-mining): T<N> <short>`. Aggregate Part-1 PR commit: `feat(dev-workflow): skill-log-mining v0.1 part-1 scaffold + Stage 1+2 (closes #<issue>)`.
- **External surfaces (memory project_external_surface_grounding_discipline.md)**: T2 reads `~/.claude/projects/**/*.jsonl` (Claude Code session-log internal format, undocumented, verified 2026-05-22 v2.1.144). T3 reads `~/.claude/usage-data/facets/*.json` (Claude Code `/insights` Feb 2026 release internal format). Both implementers MUST validate parser against real sample fixtures before writing test, not against memo-quoted schema alone.
- **Cross-skill schema-rename blind spot (memory feedback_cross_skill_schema_rename_blind_spot.md)**: at plan-time and at code-quality-review-time, grep for any consumer of Event[] dataclass field names. v0.1 there is none (this is the first writer), but Part 2 will introduce consumers — flag in Part 2 review.
- **Prototype retirement**: `/tmp/code-toolkit-mine.py` (236 LOC) is NOT in this repo (lives at `/tmp/`). T2-T4 implementers SHOULD read it as a signal-definition reference but MUST NOT vendor its code wholesale — port the 4 Pattern definitions only. Post-merge cleanup `rm /tmp/code-toolkit-mine.py` is a manual user step, not a plan task.

## Task 1 — Scaffold skill directory

- **Description**: Create `dev-workflow/skills/skill-log-mining/` with SKILL.md stub (frontmatter only — name / description / version 0.1.0 / placeholder body "v0.1 in progress; see Part 3 for body finalization"), LICENSE (copied from sibling `dev-workflow/skills/skill-judge/LICENSE`), NOTICE (copied from sibling), and empty `scripts/` directory marker (touched via `.gitkeep` if needed). No other files at this task.
- **Module**: `dev-workflow/skills/skill-log-mining/`
- **Files touched**: `dev-workflow/skills/skill-log-mining/SKILL.md`, `dev-workflow/skills/skill-log-mining/LICENSE`, `dev-workflow/skills/skill-log-mining/NOTICE`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/skill-judge/SKILL.md` (reference for frontmatter shape)
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/skill-judge/LICENSE`
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/skill-judge/NOTICE`
  - `/Users/kouko/GitHub/monkey-skills/CLAUDE.md` (skill structure rules — flat subfolders MUST, 6k token SKILL.md ceiling)
- **Acceptance**:
  - **RED**: `python -c "import yaml; yaml.safe_load(open('dev-workflow/skills/skill-log-mining/SKILL.md').read().split('---')[1])"` fails with `FileNotFoundError`.
  - **GREEN**: same command parses frontmatter with `name: skill-log-mining`, non-empty `description` (≥120 chars including ja/zh-TW triggers), `version: 0.1.0`. `.claude/hooks/validate-skill-folder-structure.sh` PASSes when run on the new directory.
- **Dependencies**: none
- **Independent**: false (T2-T5 + all Part 2 + Part 3 depend on this scaffold existing)
- **Brief item covered**: Smallest End State §"skill scaffolding (SKILL.md + tests + README × tri-language per PR #150 rule)" — this task lands the SKILL.md stub; tri-lang READMEs land in Part 3 T12.

## Task 2 — Add scripts/ingest.py (JSONL adapter → Event[])

- **Description**: Define `Event` dataclass in `scripts/event.py` with fields `{agent: str, session: str, ts: str, role: str, text: str, tool_name: str | None, tool_error: str | None, user_interrupt: bool, is_subagent: bool, skill_invocation: str | None}`. Add `scripts/ingest.py` with `ingest_claude_jsonl(root: Path, exclude_globs: list[str]) -> Iterator[Event]` that walks `~/.claude/projects/**/*.jsonl` (default), parses each line as JSON, maps Claude Code's `{type, message, uuid, parentUuid, sessionId, timestamp}` schema to Event. Skip `*/subagents/*` paths.
- **Module**: `dev-workflow/skills/skill-log-mining/scripts/ingest.py`
- **Files touched**: `dev-workflow/skills/skill-log-mining/scripts/event.py`, `dev-workflow/skills/skill-log-mining/scripts/ingest.py`, `dev-workflow/skills/skill-log-mining/scripts/test_ingest.py`
- **Context paths**:
  - `/Users/kouko/.claude/projects/-Users-kouko-GitHub-monkey-skills/` (real JSONL fixtures to inspect before writing parser)
  - `/Users/kouko/GitHub/monkey-skills/docs/code-toolkit/specs/2026-05-22-skill-log-mining-research.md` (§"Cross-agent compatibility — two-layer split" for schema verification)
  - `/tmp/code-toolkit-mine.py` (200 LOC prototype — read for JSONL traversal patterns, do NOT vendor)
- **External surfaces** (per memory project_external_surface_grounding_discipline.md):
  - `~/.claude/projects/**/*.jsonl` — Claude Code session log format. **Undocumented 1st-party Anthropic internal.** Verified 2026-05-22 on `claude --version` v2.1.144. Implementer MUST `head -3` an actual fixture (e.g. `/Users/kouko/.claude/projects/-Users-kouko-GitHub-monkey-skills/<some-session>.jsonl`) before writing parser; do NOT rely on the schema quoted in the research memo alone — verify field presence on real data.
- **Acceptance**:
  - **RED**: `pytest scripts/test_ingest.py::test_ingest_parses_real_session_fixture -x` fails with `ModuleNotFoundError: No module named 'event'`.
  - **GREEN**: test ingests a real-world JSONL fixture (committed under `scripts/fixtures/sample.jsonl`, 5-10 lines from a known monkey-skills session), produces `≥3` Events with non-None `session` field, `role ∈ {'user', 'assistant'}`, and timestamps parseable as ISO-8601.
- **Dependencies**: Task 1 completes first
- **Independent**: false (T3, T4, T5 read `event.py` schema; if Event field names change later, they cascade)
- **Brief item covered**: Smallest End State §"reads `~/.claude/projects/**/*.jsonl` ... normalizes to unified Event[] schema" + research memo §"Final convergent architecture (v2) Stage 1: Multi-agent log ingestion".

## Task 3 — Add scripts/facets.py (facets/*.json adapter → joined Event[])

- **Description**: Add `scripts/facets.py` with `load_facets(root: Path = '~/.claude/usage-data/facets') -> dict[session_id, FacetRecord]` returning per-session pre-classified data: `goal_categories`, `outcome`, `claude_helpfulness`, `friction_counts`, `friction_detail`, `primary_success`. Also expose `attach_facets_to_events(events: Iterable[Event], facets: dict) -> Iterator[Event]` that adds `facet: FacetRecord | None` field by `event.session` join key. Update `Event` dataclass to add `facet: FacetRecord | None = None` field — coordinate via Task 2's `event.py`.
- **Module**: `dev-workflow/skills/skill-log-mining/scripts/facets.py`
- **Files touched**: `dev-workflow/skills/skill-log-mining/scripts/event.py` (Edit — adds `facet` field), `dev-workflow/skills/skill-log-mining/scripts/facets.py`, `dev-workflow/skills/skill-log-mining/scripts/test_facets.py`
- **Context paths**:
  - `/Users/kouko/.claude/usage-data/facets/` (49 real facet JSONs to inspect)
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/skill-log-mining/scripts/event.py` (from T2 — Event dataclass to extend with `facet` field)
  - `/Users/kouko/GitHub/monkey-skills/docs/code-toolkit/specs/2026-05-22-skill-log-mining-research.md` (§"Facets schema (per session, confirmed)")
- **External surfaces**:
  - `~/.claude/usage-data/facets/*.json` — Claude Code `/insights` output. **Undocumented 1st-party Anthropic internal**, released Feb 2026 in Claude Code 2.1.x. Implementer MUST `cat` a real fixture before writing parser. Schema from research memo §Facets schema:  `{session_id, underlying_goal, goal_categories, outcome, claude_helpfulness, friction_counts, friction_detail, primary_success, ...}`.
- **Acceptance**:
  - **RED**: `pytest scripts/test_facets.py::test_attach_facets_joins_by_session_id -x` fails with `AttributeError: 'Event' object has no attribute 'facet'`.
  - **GREEN**: test loads a real facets JSON fixture (committed `scripts/fixtures/sample_facet.json`) + a real JSONL fixture with matching `session_id`, attaches facet to all events of that session, leaves other-session events with `facet=None`. Coverage: `claude_helpfulness` enum (5 levels) parses; `friction_counts` empty dict tolerated.
- **Dependencies**: Task 2 completes first
- **Independent**: true (file-disjoint from T4)
- **Brief item covered**: Smallest End State §"reads `~/.claude/projects/**/*.jsonl` **+ `~/.claude/usage-data/facets/*.json`**" + Locked decision #1 ("`/insights` facets are Stage 1 mandatory input — not optional sidecar").

## Task 4 — Add scripts/friction_signals.py (4 detectors with baked Q5 thresholds)

- **Description**: Add `scripts/friction_signals.py` exporting 4 detector functions and 1 bundled threshold dict. **Thresholds (Q5 defaults, baked from mining demo Pattern 1-4)**: `{interrupt_window_sec: 600, needs_revision_threshold: 2, redispatch_threshold: 2, tool_error_proximity_events: 10}`. Detectors: `detect_interrupt_after_brainstorm(events, window_sec) -> list[Signal]` (Pattern 1), `detect_tool_error_clusters(events, proximity) -> list[Signal]` (Pattern 4), `detect_needs_revision_streak(events, threshold) -> list[Signal]` (Pattern 3), `detect_redispatch_concentration(events, threshold) -> list[Signal]` (Pattern 3 symmetric). Each Signal has `{kind, session, ts, severity, evidence: list[Event]}`. Override loader: `load_thresholds(override_path: Path | None) -> dict` reads JSON override file (NOT YAML — stdlib-lean per plan-time Decision 1) and merges over baked defaults. Schema documented in module docstring; trade-off (JSON over YAML at v0.1) noted in docstring.
- **Module**: `dev-workflow/skills/skill-log-mining/scripts/friction_signals.py`
- **Files touched**: `dev-workflow/skills/skill-log-mining/scripts/friction_signals.py`, `dev-workflow/skills/skill-log-mining/scripts/test_friction_signals.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/skill-log-mining/scripts/event.py` (from T2)
  - `/tmp/code-toolkit-mine.py` (the 4 Pattern detectors live here in prototype form — read to port logic, not code)
  - `/Users/kouko/GitHub/monkey-skills/docs/code-toolkit/specs/2026-05-22-skill-log-mining-research.md` (§"Mining demo findings" Pattern 1-4 detail)
- **Acceptance**:
  - **RED**: `pytest scripts/test_friction_signals.py::test_interrupt_after_brainstorm_pattern1 -x` fails with `ImportError`.
  - **GREEN**: 4 tests, one per Pattern. Each constructs synthetic Event[] reproducing the Pattern's signature (e.g. Pattern 1 = brainstorming Skill call followed by `[Request interrupted by user]` 50s later), asserts detector returns ≥1 Signal with correct `kind`. 5th test: `load_thresholds` with override JSON merges over defaults (e.g. override `interrupt_window_sec: 900` shadows the 600 default). Baked defaults match Q5 exactly (asserted as a `BAKED_THRESHOLDS` module constant).
- **Dependencies**: Task 2 completes first
- **Independent**: true (file-disjoint from T3)
- **Brief item covered**: Q5 ("Friction signal threshold defaults — baked from mining demo Pattern 1-4 + YAML override") + Decision §"Defaults baked from mining demo Pattern 1-4 findings; YAML override accepted" (here as JSON override per plan-time Decision 1).

## Task 5 — Add scripts/aggregate.py (per-skill aggregate + reusability score + cross-project fingerprint)

- **Description**: Add `scripts/aggregate.py` with: (a) `aggregate_by_skill(events, signals, target_pattern: str) -> dict[skill_name, AggregateRecord]` filters Event[] to those tagged with a Skill invocation matching `target_pattern` glob (default `'code-toolkit:*'`), groups by skill, attaches adjacent friction signals (within session). (b) `reusability_score(rec: AggregateRecord) -> float` using crune's 4-signal formula `0.35*frequency + 0.25*timeCost + 0.25*crossProject + 0.15*recency`. (c) `fingerprint_count(rec: AggregateRecord, projects: set[str]) -> int` — within-run in-memory count of how many distinct project trees the same friction-fingerprint appears in (sha256 of `kind + normalized_evidence_text`). (d) `min_session_count: 3` and `cross_project_count: 2` from Q5 baked as `AGGREGATE_THRESHOLDS` module constant; filter low-signal skills via `min_session_count`; tag confidence per `cross_project_count`. (e) `rank_top_n(records, n: int = 5) -> list[AggregateRecord]` sorted by reusability_score desc.
- **Module**: `dev-workflow/skills/skill-log-mining/scripts/aggregate.py`
- **Files touched**: `dev-workflow/skills/skill-log-mining/scripts/aggregate.py`, `dev-workflow/skills/skill-log-mining/scripts/test_aggregate.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/skill-log-mining/scripts/event.py` (from T2)
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/skill-log-mining/scripts/friction_signals.py` (from T4 — Signal dataclass + BAKED_THRESHOLDS)
  - `/Users/kouko/GitHub/monkey-skills/docs/code-toolkit/specs/2026-05-22-skill-log-mining-research.md` (§"Deep dive: crune — prioritization layer" for reusability formula; §"Mining demo findings Pattern 1-4" + Q5 for `min_session_count` / `cross_project_count`)
- **Acceptance**:
  - **RED**: `pytest scripts/test_aggregate.py::test_reusability_score_matches_crune_formula -x` fails with `ImportError`.
  - **GREEN**: 5 tests — (a) `aggregate_by_skill` with synthetic events containing 2 `code-toolkit:brainstorming` invocations across 3 sessions returns 1 AggregateRecord with `session_count == 3`; (b) `reusability_score` against fixture record matches crune 4-signal formula to 3 decimals; (c) `fingerprint_count` returns 2 when same Signal-kind fingerprint appears in 2 different `event.session` records (treated as 2 projects for the unit test); (d) `min_session_count=3` filter drops a skill with only 2 sessions; (e) `rank_top_n(n=3)` returns sorted-desc list of length 3.
- **Dependencies**: Task 4 completes first
- **Independent**: false (consumes friction_signals.py output)
- **Brief item covered**: Smallest End State §"per-skill aggregation against `code-toolkit:*` family with friction-signal scoring → top-N high-friction skills" + Q2 (`target_skill_pattern` glob) + Q6 ("Within-run fingerprint dict (≤20 LOC) gives 'appears in N projects' confidence tag").

## Notes

- **Parallel-dispatch hint for SDD orchestrator**: T3 + T4 both have `Independent: true` with disjoint `Files touched`. After T2 lands, dispatching-parallel-agents MAY dispatch T3 + T4 implementers in one assistant message. T5 must wait for T4 sequentially. The 4-way fan-out lives in Part 2.
- **Part-1 ship gate (for Part 2 to start)**: all 5 tasks PASS, full `pytest dev-workflow/skills/skill-log-mining/scripts/` passes locally. Skill folder structure validator hook PASSes on the new directory.
- **Out of scope for Part 1**: subagent prompt files (Part 2 T6), propose / apply / main.py (Part 2 T7-T9), E2E test (Part 2 T10), SKILL.md body (Part 3 T11), tri-lang READMEs (Part 3 T12), plugin metadata (Part 3 T13), test-prompts.json (Part 3 T14).
- **Risk flag** — JSON-vs-YAML config trade-off in T4: if dogfood operator strongly prefers YAML, v0.2 swap requires only `pip install PyYAML` + 5-line parser change in `friction_signals.load_thresholds`. Defer.
