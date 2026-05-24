# Plan: skill-log-mining v0.1 — Part 2 (Trace2Skill prompts + propose + apply + main + E2E)

> ✏️ **2026-05-24 post-ship note** — shipped as **`dev-workflow:distill-sessions`** (PR #328). Plan terminology (`skill-log-mining`) is the historical narrow-scope codename; see Part 1 preface for naming-change context.

**Source brief**: docs/code-toolkit/specs/2026-05-22-skill-log-mining-v0.1-brief.md
**Total tasks**: 5 (≤5 ✓)
**Execution order**: parallel-where-possible (T6 ∥ T7 ∥ T8 ∥ T9 after Part 1 ships, then T10)
**Plan-document-reviewer verdict**: PASS (2026-05-22, round 2 — round 1 NEEDS_REVISION on check 11, fixed by routing cross-Part edge into plan-meta notes)

## Plan-time decisions (inherited from Part 1)

See `2026-05-22-skill-log-mining-v0.1-part-1.md` §"Plan-time decisions locked". Relevant carry-overs:
- **LLM model**: Trace2Skill prompts target Haiku 4.5 (per-trajectory) + Sonnet 4.6 (orchestrator merge).
- **UI surface**: stdout summary + `docs/skill-mining/<date>-<target-skill>-proposals.md` diff file.
- **Subagent dispatch**: handled by Claude at runtime via `code-toolkit:dispatching-parallel-agents`. Python scripts do NOT call `Agent()` themselves — they emit a JSON payload that the SKILL.md prose (Part 3 T11) instructs Claude to read and fan out.

## Cross-cutting plan notes

- **Cross-part prerequisite** (schema clarification): per `plan-format.md`, the `Dependencies` field enum is within-plan only (`"none"` / `"Task N completes first"` / `"Tasks N, M parallel"`). Part 2 begins only AFTER Part 1's ship-gate (all 5 Part-1 tasks PASS + `pytest dev-workflow/skills/skill-log-mining/scripts/` green); this is enforced by part-ordering, NOT by per-task Dependencies. Hence T6-T9 carry `Dependencies: none` (no in-Part-2 predecessors) and T10 carries `Tasks 6, 7, 8, 9 complete first` (in-Part-2 predecessors only). The cross-Part edge is plan-meta.
- **Commit format** (memory feedback_cc_type_whitelist.md, 9 prior hits): `feat(skill-log-mining): T<N> <short>`. Part-2 PR commit: `feat(dev-workflow): skill-log-mining v0.1 part-2 Stage 3-5 (closes #<issue>)`.
- **External surfaces (memory project_external_surface_grounding_discipline.md)**:
  - T9 (main.py) references `code-toolkit:dispatching-parallel-agents` skill name in JSON payload → internal sibling skill, NOT 3rd-party. Verify path `code-toolkit/skills/dispatching-parallel-agents/SKILL.md` exists; do not invent skill name.
  - T6 (prompt files) reference Trace2Skill prompt schema → academic source (arxiv 2603.25158, Mar 2026). Implementer reads `references/error_analysis_system_llm.txt` URL from research memo §"Deep dive: Trace2Skill"; do not hallucinate prompt structure.
- **Cross-skill schema-rename blind spot (memory feedback_cross_skill_schema_rename_blind_spot.md)**: T6 + T7 + T8 + T9 all consume the `Event` / `Signal` / `AggregateRecord` dataclasses from Part 1. If Part 1 implementer renamed any field, the consumers here cascade. Code-quality-reviewer at Part 2 MUST `grep -rn <Event-field-name> dev-workflow/skills/skill-log-mining/` to confirm alignment.
- **No silent writes guard**: T8 (apply.py) MUST refuse to run without `--approved` CLI flag. Brief Decision §"No silent writes" is load-bearing.

## Task 6 — Add agents/prompt-{failure,success}-analysis.md (Trace2Skill prompt templates)

- **Description**: Create `agents/prompt-failure-analysis.md` and `agents/prompt-success-analysis.md` as bundled subagent prompt files. Each is markdown with frontmatter `{role, input_contract, output_contract, hard_constraints}` plus a 4-step body (Trace2Skill §"Prompt design (failure analysis)"): (1) Understand task, (2) Identify what went wrong / went right, (3) Trace to behavior, (4) Write structured Memory Items (max 3, generalizable). **Failure-side hard constraints**: NEVER mention ground truth; reason from agent's PoV only; max 3 Memory Items; each Item has `Title / Description / Content`. **Success-side**: strip dead ends / failed attempts; keep only Lean Solution Path; ≤3 Success Memory Items. Both files include a final §"How the orchestrator dispatches this prompt" block: model=Haiku 4.5; input = `{session_events: list[Event], target_skill_path: str, target_skill_md_content: str}`; output = strict markdown matching `Memory Item schema`.
- **Module**: `dev-workflow/skills/skill-log-mining/agents/`
- **Files touched**: `dev-workflow/skills/skill-log-mining/agents/prompt-failure-analysis.md`, `dev-workflow/skills/skill-log-mining/agents/prompt-success-analysis.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/docs/code-toolkit/specs/2026-05-22-skill-log-mining-research.md` (§"Deep dive: Trace2Skill — our architecture template" — prompt design constraints + Memory Item schema)
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/skills/dispatching-parallel-agents/SKILL.md` (how prompts are consumed by parallel Agent() dispatch)
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/skills/subagent-driven-development/agents/spec-reviewer-prompt.md` (template reference for SDD-style agent prompt files)
- **External surfaces**:
  - **Trace2Skill (academic source, 1st-party-equivalent)**: arxiv 2603.25158 (Mar 2026) + github Qwen-Applications/Trace2Skill `analysis/error_analysis_system_llm.txt`. Implementer MUST treat as ground source for prompt structure; do not invent constraints. Research memo §"Deep dive: Trace2Skill" quotes the relevant constraints — verify against linked file URL before authoring.
- **Acceptance**:
  - **RED**: `pytest scripts/test_prompts_parseable.py::test_both_prompt_files_have_required_sections -x` fails with `FileNotFoundError`.
  - **GREEN**: test asserts both files exist + parse markdown frontmatter with required keys `{role, input_contract, output_contract, hard_constraints, model}` + body contains the 4 numbered steps + a "Memory Item schema" section with `Title / Description / Content` template. Both files lint clean (no broken links). Failure-side file explicitly forbids ground-truth reasoning; success-side explicitly demands dead-end stripping.
- **Dependencies**: none
- **Independent**: true (file-disjoint from T7, T8, T9, T10)
- **Brief item covered**: Smallest End State §"fan-out via `code-toolkit:dispatching-parallel-agents` to subagents that produce structured Failure/Success Memory Items (Trace2Skill-style prompt)".

## Task 7 — Add scripts/propose.py (merge subagent outputs → diff renderer)

- **Description**: `scripts/propose.py` with CLI `python -m propose --input <subagent_results.json> --target-skill <path> --output <docs/skill-mining/<date>-<target>.md>`. Reads subagent results JSON (list of Memory Items per session), merges by deduping near-identical Items (text-overlap heuristic + Title-key match), groups by target SKILL.md section, renders a markdown proposal file: §"Proposed additions" with each addition tagged `[insert into §<section>]`, §"Proposed modifications" with unified-diff blocks, §"Marked for v0.2" listing any proposal flagged `requires_new_reference_file: true`. **No write to target SKILL.md** here — only writes the proposal file.
- **Module**: `dev-workflow/skills/skill-log-mining/scripts/propose.py`
- **Files touched**: `dev-workflow/skills/skill-log-mining/scripts/propose.py`, `dev-workflow/skills/skill-log-mining/scripts/test_propose.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/skill-log-mining/agents/prompt-failure-analysis.md` (from T6 — Memory Item output schema)
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/skill-log-mining/agents/prompt-success-analysis.md` (from T6)
  - `/Users/kouko/GitHub/monkey-skills/docs/code-toolkit/specs/2026-05-22-skill-log-mining-v0.1-brief.md` (Q4 — SKILL.md only; `requires_new_reference_file: true` deferral marker)
- **Acceptance**:
  - **RED**: `pytest scripts/test_propose.py::test_renders_unified_diff_block_per_modification -x` fails with `ImportError`.
  - **GREEN**: 3 tests — (a) merge dedups 2 near-identical Memory Items (Title-key match) into 1 proposal; (b) `requires_new_reference_file: true` items go to §"Marked for v0.2" not main diff; (c) output markdown file contains a fenced `diff` block per modification with `+` / `-` lines. Snapshot test against `scripts/fixtures/expected_proposals.md`.
- **Dependencies**: none
- **Independent**: true (file-disjoint from T6, T8, T9)
- **Brief item covered**: Smallest End State §"orchestrator merges → human sees diff against SKILL.md only" + Q4 (`requires_new_reference_file: true` deferral marker).

## Task 8 — Add scripts/apply.py (approval gate + SKILL.md write-back)

- **Description**: `scripts/apply.py` with CLI `python -m apply --proposal <docs/skill-mining/<date>-<target>.md> --target-skill <path> --approved`. **Refuses to run without `--approved` flag** (exits 2 with message "approval gate not satisfied — re-run with --approved after human review"). When `--approved`: parses proposal file's diff blocks, applies them in-place to target SKILL.md (insertions go to the marked section anchor; modifications match-and-replace), writes target SKILL.md atomically via `Path.replace`. On any parse error or anchor mismatch, refuses to write and exits 3 with diagnostic. Never modifies any file under `references/`.
- **Module**: `dev-workflow/skills/skill-log-mining/scripts/apply.py`
- **Files touched**: `dev-workflow/skills/skill-log-mining/scripts/apply.py`, `dev-workflow/skills/skill-log-mining/scripts/test_apply.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/skill-log-mining/scripts/propose.py` (from T7 — proposal file format)
  - `/Users/kouko/GitHub/monkey-skills/docs/code-toolkit/specs/2026-05-22-skill-log-mining-v0.1-brief.md` (Decision §"No silent writes")
  - `/Users/kouko/GitHub/monkey-skills/docs/code-toolkit/specs/2026-05-22-skill-log-mining-research.md` (§"Deep dive: claude-coach Guardrails — `no silent writes`")
- **Acceptance**:
  - **RED**: `pytest scripts/test_apply.py::test_refuses_without_approved_flag -x` fails with `ImportError`.
  - **GREEN**: 4 tests — (a) running without `--approved` exits 2 + writes nothing; (b) `--approved` + valid proposal applies to fixture SKILL.md; (c) anchor mismatch exits 3 without writing; (d) attempting to write to a path under `references/` exits 3 with "Q4: v0.1 SKILL.md only" diagnostic.
- **Dependencies**: none
- **Independent**: true (file-disjoint from T6, T7, T9)
- **Brief item covered**: Smallest End State §"approve / reject / edit → write. No silent writes." + Q4 (no `references/` writes at v0.1).

## Task 9 — Add scripts/main.py (Stage 1+2 orchestrator + subagent payload emitter)

- **Description**: `scripts/main.py` with CLI `python -m main --target-skill-pattern 'code-toolkit:*' [--config <override.json>] [--top-n 5] [--max-trajectories-per-skill 5]`. (a) Loads thresholds via `friction_signals.load_thresholds(config_path)`. (b) Walks `~/.claude/projects/**/*.jsonl` via `ingest.ingest_claude_jsonl`. (c) Joins facets via `facets.attach_facets_to_events`. (d) Extracts signals via `friction_signals.detect_*`. (e) Aggregates + ranks via `aggregate.rank_top_n`. (f) Emits JSON to stdout: `{run_id, top_skills: [{skill, sessions: [{session_id, friction_level, event_count}], aggregate_record}], subagent_payload: [{prompt_path, model: 'claude-haiku-4-5-20251001', input: {session_events, target_skill_path, target_skill_md_content}}]}`. (g) Markdown human-readable summary to stderr.
- **Module**: `dev-workflow/skills/skill-log-mining/scripts/main.py`
- **Files touched**: `dev-workflow/skills/skill-log-mining/scripts/main.py`, `dev-workflow/skills/skill-log-mining/scripts/test_main.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/skill-log-mining/scripts/ingest.py` (from Part 1 T2)
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/skill-log-mining/scripts/facets.py` (from Part 1 T3)
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/skill-log-mining/scripts/friction_signals.py` (from Part 1 T4)
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/skill-log-mining/scripts/aggregate.py` (from Part 1 T5)
  - `/Users/kouko/GitHub/monkey-skills/code-toolkit/skills/dispatching-parallel-agents/SKILL.md` (sibling skill name to reference in JSON payload — verify exists)
- **External surfaces**:
  - `code-toolkit:dispatching-parallel-agents` — **internal sibling skill, not 3rd-party**. Plugin path `code-toolkit/skills/dispatching-parallel-agents/SKILL.md`. Implementer MUST verify by `ls` before encoding skill-name string in payload. Model ID `claude-haiku-4-5-20251001` (from system prompt environment metadata, locked at this writing).
- **Acceptance**:
  - **RED**: `pytest scripts/test_main.py::test_main_emits_payload_json_to_stdout -x` fails with `ImportError`.
  - **GREEN**: 4 tests — (a) `main(['--target-skill-pattern', 'code-toolkit:*'], project_root=fixture_dir)` emits valid JSON on stdout with `top_skills` key and `subagent_payload` key; (b) `--top-n 3` caps top_skills length at 3; (c) `--config override.json` swaps thresholds (cross-checks T4 load_thresholds); (d) stderr contains a markdown summary block with section headers.
- **Dependencies**: none
- **Independent**: true (file-disjoint from T6, T7, T8)
- **Brief item covered**: Smallest End State §"reads ... → normalizes ... → per-skill aggregation ... → top-N high-friction skills × ≤5 trajectories each → fan-out via `code-toolkit:dispatching-parallel-agents`" — main.py is the Stage 1+2 entry that emits the fan-out payload.

## Task 10 — Add scripts/test_main_e2e.py (golden-fixture end-to-end test)

- **Description**: `scripts/test_main_e2e.py` — a single golden-fixture E2E test that (a) creates a tiny project tree under `scripts/fixtures/e2e/projects/<project>/<session>.jsonl` with 3 sessions exercising 2 friction patterns (interrupt-after-brainstorm + tool-error-cluster), (b) creates matching `scripts/fixtures/e2e/facets/<session_id>.json`, (c) runs `main.py --target-skill-pattern 'code-toolkit:*' --project-root scripts/fixtures/e2e/projects --facets-root scripts/fixtures/e2e/facets`, (d) parses JSON output, (e) asserts: ≥1 top_skill returned, top_skill has `friction_level: high` for ≥1 session, `subagent_payload` has correct `prompt_path` pointing to `agents/prompt-failure-analysis.md`, model is `claude-haiku-4-5-20251001`. Snapshot a hash of the stable subset of output.
- **Module**: `dev-workflow/skills/skill-log-mining/scripts/test_main_e2e.py`
- **Files touched**: `dev-workflow/skills/skill-log-mining/scripts/test_main_e2e.py`, `dev-workflow/skills/skill-log-mining/scripts/fixtures/e2e/projects/<example-project>/sample-session-1.jsonl`, `dev-workflow/skills/skill-log-mining/scripts/fixtures/e2e/facets/<session-id>.json`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/skill-log-mining/scripts/main.py` (from T9)
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/skill-log-mining/agents/prompt-failure-analysis.md` (from T6)
  - `/Users/kouko/.claude/projects/-Users-kouko-GitHub-monkey-skills/` (sample real JSONL — anonymize before committing fixture)
- **Acceptance**:
  - **RED**: `pytest scripts/test_main_e2e.py -x` fails with `FileNotFoundError` on fixture path.
  - **GREEN**: test passes; fixtures committed; main.py JSON output stable across runs (uses `--seed` if any nondeterminism). Total fixture footprint ≤30KB (avoid bloating repo).
- **Dependencies**: Tasks 6, 7, 8, 9 complete first
- **Independent**: false (depends on all Part 2 task outputs)
- **Brief item covered**: Smallest End State paragraph as a whole — E2E verifies the full Stage 1→2→3-payload chain.

## Notes

- **Parallel-dispatch hint for SDD orchestrator**: T6 + T7 + T8 + T9 all have `Independent: true` with disjoint `Files touched` after Part 1 ships. dispatching-parallel-agents SHOULD dispatch all 4 implementers in one assistant message. T10 must wait sequentially for all 4. This is the largest parallel wave in this v0.1 effort — exercise the pattern.
- **Doc-code race guard (memory feedback_parallel_dispatch_doc_code_race.md)**: T6 is a doc-only task BUT it does not describe T7/T8/T9 behavior (it describes Trace2Skill prompt contract). No race risk in this fan-out.
- **Part-2 ship gate (for Part 3 to start)**: all 5 tasks PASS; full `pytest dev-workflow/skills/skill-log-mining/scripts/` green; E2E test passes end-to-end.
- **Out of scope for Part 2**: SKILL.md body (Part 3 T11) — main.py / propose.py / apply.py exist as CLI tools but the SKILL.md prose that tells Claude when and how to invoke them is Part 3. Tri-lang READMEs (Part 3 T12), plugin metadata (Part 3 T13), test-prompts.json (Part 3 T14) also Part 3.
- **No `references/` files at v0.1**: this skill's own `references/` directory is NOT created. Per CLAUDE.md "single-level subfolder" rule + Q4 minimization — defer to v0.2 if dogfood demands deeper docs.
