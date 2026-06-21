# Plan: distill-sessions v0.4 — Sonnet-1M-only subagent model

**Source brief**: docs/loom/specs/2026-05-26-distill-sessions-v0.4-brief.md
**Total tasks**: 5 (≤5 ✓)
**Execution order**: parallel-where-possible (Wave 1 = T1; Wave 2 = T2 + T3 + T4 dispatch-parallel; Wave 3 = T5)
**Plan-document-reviewer verdict**: PASS 14/14 (2026-05-26)

## Task 1 — Swap HAIKU_MODEL_ID → SUBAGENT_MODEL_ID = "claude-sonnet-4-6" in main.py + co-located unit tests

- **Description**: In [`scripts/main.py`](../../../dev-workflow/skills/distill-sessions/scripts/main.py), rename `HAIKU_MODEL_ID` to `SUBAGENT_MODEL_ID` and replace its value with `"claude-sonnet-4-6"`. Update the module-level docstring at L18 referencing the locked Haiku literal. The single in-file reference at L320 (`"model": HAIKU_MODEL_ID,`) auto-updates via rename. In [`scripts/test_main.py`](../../../dev-workflow/skills/distill-sessions/scripts/test_main.py) L165, flip the assertion `entry["model"] == "claude-haiku-4-5-20251001"` to `entry["model"] == "claude-sonnet-4-6"` FIRST (RED), then apply the production change (GREEN).
- **Module**: `dev-workflow/skills/distill-sessions/scripts/main.py`
- **Files touched**: `dev-workflow/skills/distill-sessions/scripts/main.py`, `dev-workflow/skills/distill-sessions/scripts/test_main.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/distill-sessions/scripts/main.py` (L18 docstring + L55-56 constant + L320 reference)
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/distill-sessions/scripts/test_main.py` (L165 assertion)
  - `/Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-05-26-distill-sessions-v0.4-brief.md` (Q-v0.4-1 + Q-v0.4-2 lock + Sonnet literal verification)
- **Acceptance**:
  - **RED**: `pytest scripts/test_main.py -k "model" -v` fails with `AssertionError: 'claude-haiku-4-5-20251001' != 'claude-sonnet-4-6'` (after assertion-first flip, before constant change)
  - **GREEN**: same pytest invocation passes; `grep -n "HAIKU_MODEL_ID" scripts/main.py scripts/test_main.py` returns empty; `grep -n "claude-haiku-4-5" scripts/main.py scripts/test_main.py` returns empty
- **External surfaces**:
  - SDK package: Claude API model identifier `claude-sonnet-4-6` — grounding: WebFetch https://platform.claude.com/docs/en/about-claude/models/overview (captured 2026-05-26; "Claude API ID" column for Sonnet 4.6 row; confirmed dateless format IS the pinned snapshot per Note block on the page)
- **Dependencies**: none (wave leader)
- **Independent**: false  # wave leader with no parallel partner; downstream waves depend on this constant change
- **Brief item covered**: "Q-v0.4-1: Sonnet 4.6 1M-context chosen" + "Q-v0.4-2: rename to `SUBAGENT_MODEL_ID` chosen" + Current State Evidence "Forward (model literal definition) [scripts/main.py:55-56]"

## Task 2 — Update e2e test assertion to expect Sonnet literal

- **Description**: In [`scripts/test_main_e2e.py`](../../../dev-workflow/skills/distill-sessions/scripts/test_main_e2e.py) L495-497, flip the assertion `entry["model"] == "claude-haiku-4-5-20251001"` to `entry["model"] == "claude-sonnet-4-6"` and update the accompanying error message string at L497 from `"expected claude-haiku-4-5-20251001"` to `"expected claude-sonnet-4-6"`. This is fixture-maintenance to keep the e2e test consistent with T1's contract change. Iron-law-legitimate: the assertion change makes the existing-RED test (which fails after T1 lands because production now emits Sonnet) GREEN again.
- **Module**: `dev-workflow/skills/distill-sessions/scripts/test_main_e2e.py`
- **Files touched**: `dev-workflow/skills/distill-sessions/scripts/test_main_e2e.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/distill-sessions/scripts/test_main_e2e.py` (L495-497 assertion + error message)
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/distill-sessions/scripts/main.py` (verify T1's SUBAGENT_MODEL_ID landed at L56)
- **Acceptance**:
  - **RED**: `pytest scripts/test_main_e2e.py -v` fails (the assertion at L495 still expects Haiku literal, but T1 already changed production to emit Sonnet)
  - **GREEN**: same pytest invocation passes; `grep -n "claude-haiku-4-5" scripts/test_main_e2e.py` returns empty
- **Dependencies**: Task 1 completes first
- **Independent**: true  # Files touched (test_main_e2e.py) is disjoint from T3 (test_prompts_parseable.py) and T4 (SKILL.md)
- **Brief item covered**: Current State Evidence "Reverse (callers + tests) → `grep HAIKU_MODEL_ID` → test_main_e2e.py [tests that hardcode the Haiku literal need flipping to Sonnet]"

## Task 3 — Update prompts-parseable test fixture EXPECTED_MODEL constant

- **Description**: In [`scripts/test_prompts_parseable.py`](../../../dev-workflow/skills/distill-sessions/scripts/test_prompts_parseable.py) L51, change `EXPECTED_MODEL = "claude-haiku-4-5-20251001"` to `EXPECTED_MODEL = "claude-sonnet-4-6"`. Single-line constant flip; same fixture-maintenance rationale as T2.
- **Module**: `dev-workflow/skills/distill-sessions/scripts/test_prompts_parseable.py`
- **Files touched**: `dev-workflow/skills/distill-sessions/scripts/test_prompts_parseable.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/distill-sessions/scripts/test_prompts_parseable.py` (L51 EXPECTED_MODEL constant)
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/distill-sessions/scripts/main.py` (verify T1's SUBAGENT_MODEL_ID landed at L56)
- **Acceptance**:
  - **RED**: `pytest scripts/test_prompts_parseable.py -v` fails (EXPECTED_MODEL still Haiku, but payloads thread Sonnet from T1)
  - **GREEN**: same pytest invocation passes; `grep -n "claude-haiku-4-5" scripts/test_prompts_parseable.py` returns empty
- **Dependencies**: Task 1 completes first
- **Independent**: true  # Files touched (test_prompts_parseable.py) is disjoint from T2 (test_main_e2e.py) and T4 (SKILL.md)
- **Brief item covered**: Current State Evidence "Reverse (callers + tests) → test_prompts_parseable.py [tests that hardcode the Haiku literal need flipping]"

## Task 4 — Update SKILL.md prose blocks (cap doc + ASCII diagram + Locked-Haiku §Future block)

- **Description**: In [`dev-workflow/skills/distill-sessions/SKILL.md`](../../../dev-workflow/skills/distill-sessions/SKILL.md), make three coordinated updates:
  1. **L78-90 bare-invocation protocol cap doc**: rewrite the "context overflow → skip + warn" block. Old prose assumes 200K Haiku cap and frames overflow as "4-out-of-5 real" trajectories skipped. New prose: 1M Sonnet 4.6 cap; overflow is now a theoretical floor (max observed in v0.3 dogfood was 559K = 56% of 1M cap); skip+warn fires only for trajectories >1M tokens (none observed across two dogfood rounds). Reference [v0.3 post-ship dogfood memory](../../../.claude/projects/-Users-kouko-GitHub-monkey-skills/memory/project_distill_sessions_v0_3_post_ship_dogfood.md) as the empirical baseline.
  2. **L147 ASCII pipeline diagram**: replace `|  model:   claude-haiku-4-5-20251001     |` with `|  model:   claude-sonnet-4-6              |` (preserve ASCII-box alignment by adjusting trailing spaces).
  3. **L414-417 §"Locked Haiku model literal" §Future block**: replace the whole block. Old text anticipated v0.4 swap. New §Operating notes block describes v0.4 reality: `scripts/main.py` pins `SUBAGENT_MODEL_ID = "claude-sonnet-4-6"` for per-trajectory subagents; 1M-context capacity covers all v0.3-observed trajectory sizes (max 559K); cost premium ~3× Haiku acceptable at locked cadence (2-5×/week post-PR cycle); operator can override at orchestration time per v0.1 escape hatch. Add cross-link to this v0.4 brief.
  4. **L209 prose**: change `runs on \`claude-haiku-4-5-20251001\` (model literal locked in` to `runs on \`claude-sonnet-4-6\` (model literal locked in` (single literal swap).
- **Module**: `dev-workflow/skills/distill-sessions/SKILL.md`
- **Files touched**: `dev-workflow/skills/distill-sessions/SKILL.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/distill-sessions/SKILL.md` (L78-90, L147, L209, L414-417)
  - `/Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-05-26-distill-sessions-v0.4-brief.md` (§"What Becomes Obsolete" describes each prose-block change explicitly)
  - `/Users/kouko/GitHub/monkey-skills/.claude/projects/-Users-kouko-GitHub-monkey-skills/memory/project_distill_sessions_v0_3_post_ship_dogfood.md` (overflow baseline: max 559K)
- **Acceptance**:
  - **RED**: `grep -n "claude-haiku-4-5" dev-workflow/skills/distill-sessions/SKILL.md` returns 3+ matches (L147, L209, L415 — current state)
  - **GREEN**: same grep returns empty; `grep -n "claude-sonnet-4-6" dev-workflow/skills/distill-sessions/SKILL.md` returns 3+ matches at the same line ranges; `grep -n "200K" dev-workflow/skills/distill-sessions/SKILL.md` shows no remaining "200K cap" framing in §bare-invocation protocol block
- **Dependencies**: Task 1 completes first (so SKILL.md prose matches the constant name `SUBAGENT_MODEL_ID` and literal `claude-sonnet-4-6` actually in the code)
- **Independent**: true  # Files touched (SKILL.md) is disjoint from T2 (test_main_e2e.py) and T3 (test_prompts_parseable.py)
- **Brief item covered**: §What Becomes Obsolete "L78-90 bare-invocation protocol cap doc; L142-155 ASCII pipeline diagram; L414-417 §Locked Haiku model literal §Future block; L209 prose"

## Task 5 — Add stderr cost-estimate preview line to `_render_summary_markdown`

- **Description**: In [`scripts/main.py`](../../../dev-workflow/skills/distill-sessions/scripts/main.py) `_render_summary_markdown` function (line ~336+), append a line to the stderr summary: `- estimated cost: ~$<N> input @ Sonnet 4.6 rates ($3/Mtok)`, where `<N>` is computed as `sum(len(json.dumps(entry, separators=(',', ':'))) for entry in subagent_payload) / 4 / 1_000_000 * 3.0` (byte-count / 4 ≈ token-count heuristic per OpenAI/Anthropic published rule-of-thumb; bytes→tokens conversion is rough but informative for order-of-magnitude). Add `.2f` formatting. Land directly below the existing `max_trajectories_per_skill` line at [main.py:347](../../../dev-workflow/skills/distill-sessions/scripts/main.py#L347). Answers Open Question #2 from v0.4 brief affirmatively (operator gets cost-of-dispatch signal before confirming at preview pause).
- **Module**: `dev-workflow/skills/distill-sessions/scripts/main.py`
- **Files touched**: `dev-workflow/skills/distill-sessions/scripts/main.py`, `dev-workflow/skills/distill-sessions/scripts/test_main.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/distill-sessions/scripts/main.py` (`_render_summary_markdown` function L336+; preview-line insertion point ~L347)
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/distill-sessions/scripts/test_main.py` (existing tests covering `_render_summary_markdown` — find via `grep -n "_render_summary_markdown\|estimated cost\|cost" scripts/test_main.py`)
- **Acceptance**:
  - **RED**: new test `test_main.py::test_render_summary_markdown_includes_cost_estimate` fails — asserts `"estimated cost"` substring appears in `_render_summary_markdown` output for a non-empty `subagent_payload` fixture
  - **GREEN**: same test passes; manual eyeball of stderr line shows e.g. `- estimated cost: ~$0.45 input @ Sonnet 4.6 rates ($3/Mtok)` for a 12-entry payload
- **Dependencies**: Tasks 1, 2, 3, 4 complete first (T5 touches same files as T1 — `main.py` + `test_main.py` — so cannot dispatch-parallel with Wave 2; sequenced after to avoid file-edit conflicts and to ensure T1's constant rename is visible to T5's implementer)
- **Independent**: false  # Files touched overlaps T1's `Files touched` set; cannot run parallel
- **Brief item covered**: §Open Questions #2 "Cost monitoring... Decide at plan time" — this plan answers AFFIRMATIVELY by including T5

## Notes

### Wave structure

- **Wave 1**: T1 alone (constant rename + production swap; gates all downstream)
- **Wave 2 (dispatch-parallel)**: T2, T3, T4 — all `Independent: true` with disjoint `Files touched` (test_main_e2e.py / test_prompts_parseable.py / SKILL.md). Per [`code-toolkit:dispatching-parallel-agents`](../../../code-toolkit/skills/dispatching-parallel-agents/SKILL.md), SDD MAY dispatch their implementers in **one assistant message** with three `Agent` calls.
- **Wave 3**: T5 alone (touches files T1 also touched — `main.py` + `test_main.py`; cannot dispatch-parallel with Wave 2 because Wave 2's T2/T3 also pytest-execute against main.py after T1 lands)

### Module-scope justification (T2 + T3 vs combined)

Per [`references/plan-format.md`](../../../code-toolkit/skills/writing-plans/references/plan-format.md) §Anti-patterns "Multi-module task. If `Module:` lists 2+ files, split." T2 and T3 stay separate because:
- `test_main_e2e.py` is the e2e test module (end-to-end pipeline invocation)
- `test_prompts_parseable.py` is the prompts-parseable test module (schema validation of agent prompt files)
- These ARE separate logical modules with different test scopes
- Splitting also gives dispatch-parallel benefit in Wave 2

Combining T2 + T3 would burn the parallel-dispatch benefit, save ~1 subagent triad (~2 min orchestrator time), and violate the strict ≤1-module rule. Net negative.

### Post-ship dogfood validation (not an SDD task)

After all 5 tasks land + PR merges, kouko runs manual dogfood:

1. `python main.py --target-skill-pattern 'code-toolkit:*' --top-n 5 --max-trajectories-per-skill 5` against real `~/.claude/projects`
2. Verify: 12/12 (100%) trajectories dispatched (vs 5/12 in v0.3 dogfood baseline) — confirms 1M Sonnet covers all observed sizes including 559K worst case
3. Verify: Stage 4 cluster N≥2 promotion fires on at least one writing-plans cluster (3d998518 + b4cb3d6e + a83bdc52 had semantically-related titles per v0.3 dogfood memory) — confirms second-order win from full coverage
4. Verify: stderr cost-estimate line appears at preview-confirm pause + matches actual post-dispatch Anthropic billing within ~20% (sanity check on byte/4 heuristic)
5. Write memory `project_distill_sessions_v0_4_first_dogfood.md` capturing outcomes

This is operator-manual validation per v0.1 bare-invocation protocol, not subagent work. Belongs to [`code-toolkit:finishing-a-development-branch`](../../../code-toolkit/skills/finishing-a-development-branch/SKILL.md)'s post-merge verification step.

### Open Questions deferred to v0.4.1 (NOT in this plan)

Per v0.4 brief §Open Questions:
- **#3 Prompt caching for `target_skill_md_content`** — defer until real cadence cost data confirms cost binds (>$60/mo)
- **#4 Stage 4 cluster promotion verification** — depends on post-ship dogfood findings; potential v0.5+ work
- **#5 Backward-compat for `HAIKU_MODEL_ID` import** — `grep -rn "HAIKU_MODEL_ID"` outside scripts/ at start of T1; if 0 external refs, free rename (expected case per v0.1 module-encapsulation)

### Brief-to-task coverage map

| Brief §Smallest End State item | Covering task(s) |
|---|---|
| Replace Haiku model literal in `_build_subagent_entries` payload | T1 (constant change + L320 reference auto-update) |
| `HAIKU_MODEL_ID` constant rename → `SUBAGENT_MODEL_ID` | T1 |
| All existing tests that assert the model literal update | T1 (test_main.py) + T2 (test_main_e2e.py) + T3 (test_prompts_parseable.py) |
| SKILL.md bare-invocation protocol cap doc 200K → 1M | T4 |
| SKILL.md ASCII pipeline diagram literal update | T4 |
| SKILL.md §"Locked Haiku model literal" §Future → §Operating notes | T4 |
| (Open Q #2 affirmative answer) cost-estimate stderr preview | T5 |

Brief-task coverage is complete; no orphan tasks; no brief item unmapped.
