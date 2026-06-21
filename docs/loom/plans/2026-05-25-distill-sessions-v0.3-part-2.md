# Plan: distill-sessions v0.3 — Part 2 (Stage 4 cluster + N≥2 promotion)

**Source brief**: docs/loom/specs/2026-05-25-distill-sessions-v0.3-brief.md (parent brief — Q-v0.3-1 cluster strategy locked = Filter; this plan implements that decision)
**Total tasks**: 5 (≤5 ✓)
**Execution order**: sequential (each task depends on the prior)
**Plan-document-reviewer verdict**: PASS (2026-05-25, 14/14 checks; T1 Independent flipped true→false post-review per `[[independent-true-lone-wave-leader]]`)

Part 2 of 2: Stage 4 cluster with title+anchor normalization + N≥2 promotion + N=1 → §"Cross-session evidence pending" bucket. Part-1 (cross-skill routing + dual-dispatch) shipped in [PR #332](https://github.com/kouko/monkey-skills/pull/332) per [[distill-sessions-v0-3-part-1-shipped]] memory. v2.6.1 known-bugs hotfix shipped between as [PR #333](https://github.com/kouko/monkey-skills/pull/333) per [[distill-sessions-v2-6-1-known-bugs-hotfix]] memory.

## Task 1 — `cluster.py` module + `test_cluster.py` + multi-session fixture

- **Description**: New `dev-workflow/skills/distill-sessions/scripts/cluster.py` module. Single public function `cluster_memory_items(items: list[dict], min_n: int = 2) -> tuple[list[dict], list[dict]]` returning `(promoted, pending)`:
  - Normalize each item's `(title, section_anchor)` pair: lowercase + collapse whitespace + strip punctuation.
  - Group items by normalized (title, section_anchor) key.
  - Groups with ≥ min_n distinct supporting sessions → promoted (one representative item per group; supporting session IDs tracked in a new `supporting_sessions: list[str]` field).
  - Groups with < min_n distinct sessions → pending (preserved one-per-session for §"Cross-session evidence pending" bucket renderer).
  - Pure function: no I/O, no mutation of input items, deterministic ordering (sort promoted by group size desc, pending by session_id alphabetic).
  - Stdlib-only per v0.1 Q1 (no embeddings; title+anchor normalization is the v0.3 baseline; semantic clustering deferred to v0.5+ per parent brief §Alternatives Considered #5.2).
- **Module**: `dev-workflow/skills/distill-sessions/scripts/cluster.py` (new)
- **Files touched**: `dev-workflow/skills/distill-sessions/scripts/cluster.py` (new), `dev-workflow/skills/distill-sessions/scripts/test_cluster.py` (new)
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/feat+distill-sessions-v0.3-part-2/dev-workflow/skills/distill-sessions/scripts/propose.py` (input shape — `extract_memory_items` returns flat list of items with `title`, `description`, `content`, `section_anchor`, `kind`, `session_id` per `fixture_subagent_results.json`)
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/feat+distill-sessions-v0.3-part-2/dev-workflow/skills/distill-sessions/scripts/fixture_subagent_results.json` (single-session example shape — extend inline in test fixture for multi-session multi-skill scenarios)
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/feat+distill-sessions-v0.3-part-2/dev-workflow/skills/distill-sessions/scripts/aggregate.py` (precedent for pure-function module shape — `score_skill_in_session` placed at top-level, no I/O)
  - `/Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-05-25-distill-sessions-v0.3-brief.md` (§Alternatives Considered §"Finding #5 cross-session clustering" — Recommended approach #1 (title+anchor normalization + N≥2) with the explicit "single-session items → label NOT silently drop" UX choice from §Locked Q-decisions Q-v0.3-1 = A)
- **Acceptance**:
  - **RED**: `test_cluster.py::test_cluster_promotes_items_supported_by_two_or_more_sessions` — fixture with 3 items: same `(title, section_anchor)` normalized in session_a + session_b (2 distinct sessions → promoted), one different `(title, section_anchor)` in session_c only (1 session → pending). Assert `len(promoted) == 1` with `supporting_sessions == ["session_a", "session_b"]`, `len(pending) == 1`. Plus `test_cluster.py::test_cluster_normalizes_title_case_whitespace_punctuation` — items with semantically equivalent titles but different surface (`"Use Read before Edit"` vs `"  use read before edit. "`) cluster together.
  - **GREEN**: both new tests pass; cluster.py module imports cleanly; `PYTHONDONTWRITEBYTECODE=1 python -m pytest dev-workflow/skills/distill-sessions/scripts/test_cluster.py -v` reports both tests PASS.
- **Dependencies**: none
- **Independent**: false  # lone wave-leader per [[independent-true-lone-wave-leader]] — no parallel sibling, so `true` would be semantically empty
- **Brief item covered**: Smallest End State §(b) (deferred from part-1) — "clusters Memory Items across subagents and promotes only items supported by N≥2 sessions to `## Proposed additions` / `## Proposed modifications`; single-session items route to a new `## Cross-session evidence pending` bucket with their per-session anchor preserved". Q-v0.3-1 = A (Filter).

## Task 2 — `propose.py` integration: cluster pipeline + new §"Cross-session evidence pending" bucket renderer

- **Description**: Wire `cluster_memory_items` into `propose.py`'s `render_proposal_markdown` flow. After `extract_memory_items` produces the flat list AND before the existing anchor-mismatch partition (per [[distill-sessions-v0-2-narrow-hotfix]] anchor-validation), invoke `cluster_memory_items(items, min_n=2)` → `(promoted, pending)`. Existing flow routes `promoted` items through `partition_by_anchor_match` → `## Proposed additions` / `## Proposed modifications` (per `kind`). NEW: `pending` items render under a new `## Cross-session evidence pending` section, grouped by normalized (title, section_anchor), with per-item session_id annotations so the operator sees "would have clustered; only 1 session". The new section sits BETWEEN existing `## Anchor mismatch — needs review` and `## Marked for v0.2` per propose.py's existing layout convention.
- **Module**: `dev-workflow/skills/distill-sessions/scripts/propose.py`
- **Files touched**: `dev-workflow/skills/distill-sessions/scripts/propose.py`, `dev-workflow/skills/distill-sessions/scripts/test_propose.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/feat+distill-sessions-v0.3-part-2/dev-workflow/skills/distill-sessions/scripts/propose.py` (existing `render_proposal_markdown` function — locate the section-rendering sequence)
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/feat+distill-sessions-v0.3-part-2/dev-workflow/skills/distill-sessions/scripts/cluster.py` (T1 output — imports `cluster_memory_items`)
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/feat+distill-sessions-v0.3-part-2/dev-workflow/skills/distill-sessions/scripts/test_propose.py` (existing test patterns — extend with new fixture for cross-session bucket case)
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/feat+distill-sessions-v0.3-part-2/dev-workflow/skills/distill-sessions/scripts/fixture_expected_proposals.md` (existing golden output — may need to extend with the new §"Cross-session evidence pending" section)
- **Acceptance**:
  - **RED**: `test_propose.py::test_render_proposal_includes_cross_session_evidence_pending_section` — input fixture: 2 items (one in session_a, one in session_b) with semantically-different titles (won't cluster) + 1 item also in session_a with the same title as a session_b item (2 sessions → cluster). Assert: rendered output contains `## Cross-session evidence pending` header; the 2 non-clustering items appear under that header with their session_id annotated; the 1 clustered item appears under `## Proposed additions` / `## Proposed modifications` (per `kind`).
  - **GREEN**: new test passes; existing `test_propose.py` tests stay green; `apply.py` still refuses items from the new §"Cross-session evidence pending" section (apply.py only applies §Proposed additions/modifications by anchor match — verify no regression).
- **Dependencies**: Task 1 completes first
- **Independent**: false (depends on Task 1's `cluster_memory_items` symbol)
- **Brief item covered**: Same as T1 — §(b) renderer side of the cluster pipeline.

## Task 3 — SKILL.md docs: document Stage 4 cluster + cross-session bucket

- **Description**: Update `dev-workflow/skills/distill-sessions/SKILL.md` to reflect Stage 4 cluster:
  - **§Pipeline §Step 4 (or new sub-step before Step 4)**: document `cluster_memory_items` between Step 3 (subagent fan-out) and Step 4 (propose.py rendering). Explain the N≥2 promotion + N=1 routing to the new bucket.
  - **§Pipeline §Step 4 Stage 5a description**: extend with the new §"Cross-session evidence pending" output section + describe what the operator should do with it (re-run after more session evidence accumulates).
  - **§Future**: remove the "Stage 4 full SDD consolidation" bullet (or rewrite to reflect "minimal Stage 4 shipped at v0.3; full SDD spec-reviewer + code-quality-reviewer triad deferred to v0.5+ if minimal proves insufficient" per parent brief §What Becomes Obsolete §"Becomes obsolete on v0.4 ship").
- **Module**: `dev-workflow/skills/distill-sessions/SKILL.md`
- **Files touched**: `dev-workflow/skills/distill-sessions/SKILL.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/feat+distill-sessions-v0.3-part-2/dev-workflow/skills/distill-sessions/SKILL.md` (current state — §Pipeline §Step 4 around lines 274-322; §Future Stage 4 bullet around lines 430-435)
  - `/Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-05-25-distill-sessions-v0.3-brief.md` (canonical wording for the cluster behavior + Q-v0.3-1 decision rationale)
- **Acceptance**:
  - **RED**: `grep -cF 'cluster_memory_items' dev-workflow/skills/distill-sessions/SKILL.md` returns 0; `grep -cF 'Cross-session evidence pending' dev-workflow/skills/distill-sessions/SKILL.md` returns 0.
  - **GREEN**: after edit, both greps return ≥1; `grep -F 'Stage 4 full SDD consolidation' dev-workflow/skills/distill-sessions/SKILL.md` returns 0 (or returns 1 with rewritten "minimal shipped + full deferred" wording); SKILL.md body still ≤4500 words (≤6000 tokens).
- **Dependencies**: Task 2 completes first (cannot document what is not yet implemented)
- **Independent**: false
- **Brief item covered**: §What Becomes Obsolete §"Same-PR removal on v0.3 ship" + §"Becomes obsolete on v0.4 ship" §"Stage 4 full SDD consolidation" rewrite.

## Task 4 — README tri-lang sync (en/ja/zh-TW): Stage 4 cluster + v0.3 user-facing surface

- **Description**: Update `dev-workflow/skills/distill-sessions/README.md` + `README.ja.md` + `README.zh-TW.md` to describe the v0.3 user-facing surface changes shipped in part-1 + part-2: (a) cross-skill friction-density routing, (b) dual-dispatch on high-friction-success, (c) Stage 4 cluster with N≥2 promotion + §"Cross-session evidence pending" bucket. Keep each README's structure unchanged — only extend the existing sections describing pipeline behavior. Tri-lang content stays semantically equivalent (verb tense + naming consistent across languages per PR #150 rule).
- **Module**: `dev-workflow/skills/distill-sessions/` (tri-lang docs unit — single logical "docs i18n" module per PR #150 convention)
- **Files touched**: `dev-workflow/skills/distill-sessions/README.md`, `dev-workflow/skills/distill-sessions/README.ja.md`, `dev-workflow/skills/distill-sessions/README.zh-TW.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/feat+distill-sessions-v0.3-part-2/dev-workflow/skills/distill-sessions/README.md` (current EN baseline)
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/feat+distill-sessions-v0.3-part-2/dev-workflow/skills/distill-sessions/README.ja.md` (current JA baseline — match structure)
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/feat+distill-sessions-v0.3-part-2/dev-workflow/skills/distill-sessions/README.zh-TW.md` (current ZH-TW baseline — match structure)
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/feat+distill-sessions-v0.3-part-2/dev-workflow/skills/distill-sessions/SKILL.md` (after T3 — canonical wording source for the 3 features, translate per-language)
  - `/Users/kouko/.claude/projects/-Users-kouko-GitHub-monkey-skills/memory/feedback_skill_readme_i18n_required.md` (PR #150 tri-lang rule)
- **Acceptance**:
  - **RED**: `grep -lF 'cluster' dev-workflow/skills/distill-sessions/README*.md | wc -l` returns 0 (current state — no cluster mention in any README); same for `cross-skill` and `dual-dispatch`.
  - **GREEN**: all 3 README files (EN/JA/ZH-TW) contain mentions of Stage 4 cluster + cross-skill routing + dual-dispatch in their natural language; structure preserved (no new sections, only extended); `grep -lF 'cluster' dev-workflow/skills/distill-sessions/README*.md | wc -l` returns 3.
- **Dependencies**: Task 3 completes first (README mirrors SKILL.md wording)
- **Independent**: false
- **Brief item covered**: §Plan-time atomic task preview §Task 7 — "README tri-language sync (en/ja/zh-TW) — describe Stage 4 cluster + dual-dispatch + cross-skill routing".

## Task 5 — Version bump v2.6.1 → v2.7.0 + marketplace sync (ship commit)

- **Description**: Bump `dev-workflow/.claude-plugin/plugin.json` from `2.6.1` → `2.7.0` (minor — new user-visible feature: Stage 4 cluster). `code-toolkit/.claude-plugin/plugin.json` stays at `0.9.1` (no code-toolkit-side changes in part-2). Sync `marketplace.json` description if needed (CI-enforced via `scripts/check-marketplace-description-sync.py`). Distill-sessions SKILL.md frontmatter `version:` bumps from `0.1.0` → `0.3.0` (catching up — v0.2 + v0.3 part-1 both kept it at 0.1.0 per precedent; v0.3 final ship is the right moment to align to the conceptual version). Full test suite must stay GREEN.
- **Module**: `dev-workflow/.claude-plugin/plugin.json` (single canonical version source; marketplace.json + SKILL.md frontmatter version are paired mechanical follow-ups)
- **Files touched**: `dev-workflow/.claude-plugin/plugin.json`, `marketplace.json`, `dev-workflow/skills/distill-sessions/SKILL.md` (frontmatter `version:` only)
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/feat+distill-sessions-v0.3-part-2/dev-workflow/.claude-plugin/plugin.json` (current v2.6.1)
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/feat+distill-sessions-v0.3-part-2/marketplace.json` (dev-workflow entry — description sync check)
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/feat+distill-sessions-v0.3-part-2/scripts/check-marketplace-description-sync.py` (CI gate)
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/feat+distill-sessions-v0.3-part-2/dev-workflow/skills/distill-sessions/SKILL.md` (frontmatter `version: 0.1.0` → `0.3.0`)
- **Acceptance**:
  - **RED**: `cat dev-workflow/.claude-plugin/plugin.json | python3 -c 'import sys,json; print(json.load(sys.stdin)["version"])'` returns `2.6.1`; `head -25 dev-workflow/skills/distill-sessions/SKILL.md | grep version:` returns `version: 0.1.0`.
  - **GREEN**: plugin.json shows `"version": "2.7.0"`; SKILL.md frontmatter shows `version: 0.3.0`; `python3 scripts/check-marketplace-description-sync.py` exits 0; full distill-sessions pytest suite still GREEN (84 prior + new tests from T1 + T2); `PYTHONDONTWRITEBYTECODE=1 python -m pytest dev-workflow/skills/distill-sessions/scripts/ -q` evidence captured in commit.
- **Dependencies**: Tasks 1, 2, 3, 4 complete first (version bump = ship commit; everything must already be green)
- **Independent**: false
- **Brief item covered**: §Plan-time atomic task preview §Task 8 — "dev-workflow `plugin.json` + monkey-skills `marketplace.json` version bump v0.1.0 → v0.3.0 + description sync (CI-enforced)". Adapted: plugin version `2.6.1 → 2.7.0`; SKILL.md frontmatter `0.1.0 → 0.3.0`.

## Notes

- **Execution mode**: full SDD (per-task triad implementer + spec-reviewer + code-quality-reviewer) — matches part-1's pattern. NOT B2 inline (which was for the v2.6.1 hotfix). Justification: part-2 introduces a NEW MODULE (`cluster.py`) and changes the proposal rendering pipeline shape — more design-y than pure docs/version-bump, warrants full triad review.
- **Reviewer dispatch prompts MUST include `PYTHONDONTWRITEBYTECODE=1` discipline**: per [[whole-branch-reviewer-pycache-discipline]] memory, reviewer subagents that run pytest as part of verification must explicitly set the env-var to avoid the `__pycache__` hook blocking the orchestrator's next Edit. Implementer dispatch prompts also include this (they already follow it per [[distill-sessions-v2-6-1-known-bugs-hotfix]]).
- **Commit subject discipline**: per `code-toolkit/agents/implementer.md` Role contract rule #8 (live as of v0.9.1) — every commit MUST follow `<type>(<scope>): <subject>` format. Examples: `feat(distill-sessions): cluster_memory_items pure function`, `test(distill-sessions): RED for cross-session bucket renderer`, `docs(distill-sessions): Stage 4 cluster in §Pipeline`, `chore(dev-workflow): v2.7.0 — distill-sessions v0.3 part-2 ship`.
- **Dependency chain is strictly sequential**: T1 → T2 → T3 → T4 → T5. No parallel-dispatch eligibility because each task depends on the prior task's artifact. SDD's sequential dispatch is the only mode applicable.
- **Total estimated implementer LOC**: T1 ~120 (cluster.py + test_cluster.py) + T2 ~50 (propose.py integration + test) + T3 ~40 (docs) + T4 ~150 (tri-lang README) + T5 ~10 (version bump) = ~370 LOC.
