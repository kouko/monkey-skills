# Plan: distill-sessions v0.3 — Part 1 (cross-skill routing + dual-dispatch)

**Source brief**: docs/loom/specs/2026-05-25-distill-sessions-v0.3-brief.md
**Total tasks**: 5 (≤5 ✓)
**Execution order**: parallel-where-possible
**Plan-document-reviewer verdict**: PASS (2026-05-25, 14/14 checks, cosmetic syntax fixed post-review)

Part 1 of 2: covers Finding #2 (cross-skill friction-density routing per Q-v0.3-2) + dual-dispatch (per Q-v0.3-3) from the parent brief. Part 2 (Stage 4 cluster per Q-v0.3-1) ships in a separate sequential plan after part 1 merges, per writing-plans §"Split into multiple sequential briefs" — applied to plans following the v0.1 precedent (one parent brief, multiple sequential plans at `docs/loom/plans/<topic>-part-{1..N}.md`).

## Task 1 — Dual-dispatch in `_kind_for_session`

- **Description**: Change `_kind_for_session` to return `list[str]` (single-kind path returns `[kind]`; high-friction-success path returns `["failure", "success"]`); adapt the single caller `_build_subagent_entries` to iterate over the returned list and emit one `subagent_payload[]` entry per kind. The existing `uuid5(namespace, f"{skill}|{session}|{kind}")` already includes `kind` → distinct `trajectory_id` per dispatch for free; no namespace bump. Update prompt_path selection inside the loop.
- **Module**: `dev-workflow/skills/distill-sessions/scripts/main.py`
- **Files touched**: `dev-workflow/skills/distill-sessions/scripts/main.py`, `dev-workflow/skills/distill-sessions/scripts/test_main.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/distill-sessions/scripts/main.py` (specifically `_kind_for_session` at lines 137-155 + `_build_subagent_entries` at lines 211-268)
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/distill-sessions/scripts/test_main.py`
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/distill-sessions/scripts/event.py` (Event + FacetRecord shape for fixtures)
  - `/Users/kouko/.claude/projects/-Users-kouko-GitHub-monkey-skills/memory/feedback_kind_classifier_facet_outcome_dominates.md` (the canonical statement of the fix shape)
- **Acceptance**:
  - **RED**: `test_main.py::test_high_friction_success_session_emits_dual_dispatch_entries` — a session with `friction_level="high"` AND `facet.outcome="fully_achieved"` produces 2 entries in `subagent_payload[]` (one `kind="failure"` + one `kind="success"`) with distinct `trajectory_id` values
  - **GREEN**: the new test passes; all existing `test_main.py` tests stay green (single-kind paths unchanged); existing `test_main_e2e.py` still green
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: Smallest End State §(c) — "when a session classifies as high-friction-but-succeeded ... `_build_subagent_entries` emits TWO `subagent_payload[]` entries with distinct `trajectory_id`"; Locked Q-v0.3-3 = A (counts as 2 dispatches)

## Task 2 — `aggregate.score_skill_in_session` helper (pure function)

- **Description**: Add `score_skill_in_session(rec: AggregateRecord, session_id: str) -> float` to `aggregate.py`. Sum a per-severity weight over `rec.signals` filtered to the given session: `high=3.0`, `mid=1.0`, `low=0.3`. Pure function — no I/O, no side effects, no mutation of `rec`. Return `0.0` when the session has no signals in `rec`.
- **Module**: `dev-workflow/skills/distill-sessions/scripts/aggregate.py`
- **Files touched**: `dev-workflow/skills/distill-sessions/scripts/aggregate.py`, `dev-workflow/skills/distill-sessions/scripts/test_aggregate.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/distill-sessions/scripts/aggregate.py` (AggregateRecord dataclass + reusability_score precedent for weight-style scoring)
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/distill-sessions/scripts/friction_signals.py` (Signal dataclass — `kind`, `session`, `severity`, `evidence` fields)
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/distill-sessions/scripts/test_aggregate.py`
- **Acceptance**:
  - **RED**: `test_aggregate.py::test_score_skill_in_session_sums_severity_weights` — a fixture record with 2 high + 1 mid signal for session_a and 1 low signal for session_b returns `7.0` for session_a (2×3.0 + 1×1.0) and `0.3` for session_b
  - **GREEN**: new test passes; covers zero-signals case (`score_skill_in_session(rec, "missing_session") == 0.0`); existing `test_aggregate.py` tests stay green
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: Smallest End State §(a) — "routes each Memory Item to the skill whose friction signals fired most in that session"; Locked Q-v0.3-2 = A (highest-friction-signal-density per (session, skill))

## Task 3 — Wire friction-density routing into `_build_subagent_entries`

- **Description**: In `main()`, before building subagent entries, compute `score_skill_in_session(rec, session_id)` for every (session, skill) pair across `top_skills`. For each session, attribute it to the skill with the maximum score (alphabetic tie-break = current behavior, preserved). Pass the resulting `session_to_skill: dict[str, str]` into `_build_subagent_entries` and skip entries where `session_to_skill[session_id] != skill_name`. Effect: when a session invokes brainstorming + writing-plans and friction signals favor brainstorming, Memory Items route ONLY to brainstorming's subagent batch.
- **Module**: `dev-workflow/skills/distill-sessions/scripts/main.py`
- **Files touched**: `dev-workflow/skills/distill-sessions/scripts/main.py`, `dev-workflow/skills/distill-sessions/scripts/test_main.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/distill-sessions/scripts/main.py` (specifically `main()` at lines ~440-490 where `_build_subagent_entries` is invoked per skill)
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/distill-sessions/scripts/aggregate.py` (uses the helper landed by Task 2)
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/distill-sessions/scripts/test_main.py`
- **Acceptance**:
  - **RED**: `test_main.py::test_cross_skill_routing_attributes_session_to_highest_friction_skill` — a fixture with one session invoking both `code-toolkit:brainstorming` (2 high signals) and `code-toolkit:writing-plans` (0 signals) produces a `subagent_payload[]` where the session appears under brainstorming's entries ONLY (not writing-plans's)
  - **GREEN**: new test passes; existing tests stay green; alphabetic tie-break preserved (added test: equal scores → alphabetic-first skill wins)
- **Dependencies**: Task 2 completes first
- **Independent**: false
- **Brief item covered**: Smallest End State §(a) — "routes each Memory Item to the skill whose friction signals fired most in that session (not the lexically-first skill in `top_skills`)"

## Task 4 — SKILL.md documentation update

- **Description**: Update `dev-workflow/skills/distill-sessions/SKILL.md` to reflect the two shipped fixes: (a) in §Pipeline §Step 1, document that high-friction-success sessions emit 2 entries and that `--max-trajectories-per-skill` counts both dispatches; (b) in §Pipeline §Step 1, document the friction-density routing (one session attributed to one skill per (session, skill) signal density); (c) in §Future, remove the dual-dispatch bullet (lines ~404-420) since shipped; (d) in §Future, keep the Stage 4 cluster bullet (deferred to part-2); (e) update §Operating notes with one short sentence on cross-skill routing semantics.
- **Module**: `dev-workflow/skills/distill-sessions/SKILL.md`
- **Files touched**: `dev-workflow/skills/distill-sessions/SKILL.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/distill-sessions/SKILL.md` (current state — §Step 1 at lines 173-194, §Operating notes at lines 358-388, §Future at lines 390-453)
  - `/Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-05-25-distill-sessions-v0.3-brief.md` (canonical wording for the two fixes)
- **Acceptance**:
  - **RED**: `grep -F 'high-friction-success' SKILL.md` returns 0 matches in §Pipeline (only in §Future as currently); `grep -F 'friction-density' SKILL.md` returns 0 matches; `grep -F 'Dual-dispatch on high-friction-but-succeeded sessions (v0.2)' SKILL.md` returns 1 match (the §Future bullet)
  - **GREEN**: after edit — `grep -F 'high-friction-success' SKILL.md` returns ≥1 match in §Pipeline §Step 1; `grep -F 'friction-density' SKILL.md` returns ≥1 match in §Pipeline §Step 1 (or §Operating notes); `grep -F 'Dual-dispatch on high-friction-but-succeeded sessions (v0.2)' SKILL.md` returns 0 matches (bullet removed from §Future); SKILL.md body stays ≤6000 tokens per CLAUDE.md project rule
- **Dependencies**: Tasks 1, 3 complete first (cannot document what is not yet implemented)
- **Independent**: false
- **Brief item covered**: §What Becomes Obsolete §"Same-PR removal on v0.3 ship" — §Future block "Dual-dispatch on high-friction-but-succeeded sessions (v0.2)" moves from §Future to §Operating notes / §Pipeline §Step 1 inline

## Task 5 — Version bump + marketplace sync

- **Description**: Bump `dev-workflow/.claude-plugin/plugin.json` from `2.5.1` to `2.6.0` (minor: shipping two new user-visible features — dual-dispatch + cross-skill routing). Update `marketplace.json` entry for `dev-workflow` so `description` matches the new plugin.json description verbatim (CI-enforced sync per `feedback_plugin_json_location_and_description_sync.md`). README tri-language sync deferred to part-2 (when Stage 4 cluster lands as the same-version surface change). SKILL.md `version:` frontmatter unchanged (precedent: v0.2 narrow hotfix kept SKILL.md version at 0.1.0 — bump on the full v0.3 ship in part-2).
- **Module**: `dev-workflow/.claude-plugin/plugin.json` (single canonical version source; marketplace.json sync is mechanical follow-up)
- **Files touched**: `dev-workflow/.claude-plugin/plugin.json`, `marketplace.json`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/.claude-plugin/plugin.json` (current: version 2.5.1)
  - `/Users/kouko/GitHub/monkey-skills/marketplace.json` (current dev-workflow entry — description must match plugin.json)
  - `/Users/kouko/GitHub/monkey-skills/scripts/check-marketplace-description-sync.py` (CI gate that enforces the match)
  - `/Users/kouko/.claude/projects/-Users-kouko-GitHub-monkey-skills/memory/feedback_plugin_json_location_and_description_sync.md` (the discipline statement)
- **Acceptance**:
  - **RED**: `python scripts/check-marketplace-description-sync.py` exits 0 currently (existing state synced at v2.5.1); after bumping plugin.json to 2.6.0 WITHOUT updating marketplace.json, the script exits non-zero (description mismatch / version reference drift); this is the RED state the implementer reproduces first
  - **GREEN**: after syncing marketplace.json — `python scripts/check-marketplace-description-sync.py` exits 0; plugin.json shows `"version": "2.6.0"`; full pytest suite (`pytest dev-workflow/skills/distill-sessions/scripts/`) still 77/77 GREEN plus the 3 new tests added in Tasks 1+2+3 = 80/80 GREEN
- **Dependencies**: Tasks 1, 2, 3, 4 complete first (version bump = ship commit; everything must already be green)
- **Independent**: false
- **Brief item covered**: §Plan-time atomic task preview §Task 8 — "dev-workflow `plugin.json` + monkey-skills `marketplace.json` version bump + description sync (CI-enforced)"

## Notes

- Tasks 1 + 2 are dispatch-parallel-eligible (both `Independent: true`; `Files touched` sets disjoint — Task 1 touches `main.py` + `test_main.py`, Task 2 touches `aggregate.py` + `test_aggregate.py`). Recommend `dispatching-parallel-agents` for wave 1 per [`../using-code-toolkit/SKILL.md`](../../code-toolkit/skills/using-code-toolkit/SKILL.md) §"Auto-suggest hook".
- Task 3 must wait for Task 2's helper to land (uses `score_skill_in_session`).
- Task 4 must wait for Tasks 1 + 3 — documentation cannot describe unshipped behavior.
- Task 5 is last — version bump is the ship commit; gates on all prior tasks being green.
- Total estimated implementer LOC: T1 ~30 + T2 ~25 + T3 ~50 + T4 ~40 docs + T5 ~10 mechanical = ~155 LOC for part-1.
- Part-2 plan (Stage 4 cluster + N≥2 promotion + §Cross-session evidence pending bucket + README tri-lang sync + final v0.3.0 version bump) will be authored after part-1 merges to main.
