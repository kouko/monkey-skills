# Plan: wiki-ingest zero-prompt + oldest-first — part 3 (commit 3 scope)

**Source brief**: docs/superpowers/specs/2026-05-17-wiki-ingest-zero-prompt-oldest-first-design.md
**Total tasks**: 4 (≤5 ✓)
**Execution order**: parallel-where-possible
**Plan-document-reviewer verdict**: PASS (2026-05-17 21:58)

## Scope of this plan

**Commit 3** per brief §7. Builds on part-1 + part-2 (all 18 commits shipped, 16 tests pass on branch `feat/wiki-ingest-zero-prompt-oldest-first`). Final commit before merge / finishing-a-branch.

**Commit 3 deliverables**:
- SKILL.md STEP 6 next-batch preview block (consume `scope_summary` JSON from STEP 3's `select-batch.py` output)
- pytest CC-14 (zero NEW + zero MOD → up-to-date case) + CC-15 (frontmatter `status` doesn't filter at script level — gate is SKILL.md STEP 4 prose)
- `.github/workflows/test-obsidian.yml` (deferred from part-2 to keep that plan within 5-task ceiling)
- Version bump `obsidian/.claude-plugin/plugin.json` 3.9.0 → 3.10.0 + sync `marketplace.json` description if drift (per repo memory `plugin_json_location_and_description_sync`)

**Out of part-3 scope** (handled in finishing-a-branch phase):
- Dogfood on `~/kouko-obsidian-vault` (manual run; not a pytest-able SDD task — kouko runs `/wiki-ingest` against real vault and verifies oldest-first behavior captures the next ~15 of the remaining 4493 NEW notes)
- PR title / body / changelog write-up
- README / CHANGELOG.md edits (if any)

## CC-14 and CC-15 reframe note

Brief vault note CC table defines:
- **CC-14**: 全 vault 已 ingest（NEW + MODIFIED = 0）→ 報告 "Up-to-date"，不跑 STEP 3-4 (= now 4-5)
- **CC-15**: NEW 中有 `wiki-auto-research` 產出但 status != reviewed-accept → 仍套用 batch order，但 STEP 4 (= now STEP 5 per-source loop, sub-section 4a/5a — actually 4a per part-1 T5 renumbering)... wait the per-source loop is STEP 4 in current SKILL.md and the auto-research gate is in section 4a. The CC-15 spec says "STEP 4 仍會 skip 並記 log" — that's the SKILL.md prose gate, NOT the script.

**Script-side reframe** (consistent with part-2's reframe philosophy):
- **CC-14** is script-testable directly: zero NEW + zero MOD → batch=[], remaining=[], scope_summary all null/0. SKILL.md STEP 6 "Up-to-date" message is part of T1's STEP 6 preview block (use scope_summary's `remaining_count == 0` to trigger the up-to-date message).
- **CC-15** is partially script-testable: the script does NOT examine `frontmatter.status` (that's SKILL.md's job). Test: build NEW files with various `frontmatter.status` values (reviewed-accept / pending-review / missing) → assert all appear in batch (script applies batch order, not status filter). The "STEP 4 skip + log" behavior is verified by spec-reviewer's prose check on T1's SKILL.md edit (STEP 6 preview should NOT claim the auto-research-gated files were skipped — that's STEP 4's per-source loop concern; STEP 6 reports what STEP 3 selected).

## Dependency graph

```
T1 (SKILL.md STEP 6)     T2 (pytest CC-14+15)     T3 (CI workflow)     T4 (version bump)
       |                        |                        |                    |
       └────────────────────────┴────────────────────────┴────────────────────┘
                                  (all parallel — different files / no shared state)
```

No hard sequential dependencies among the 4 tasks; SDD can dispatch all 4 implementers in one wave.

---

## Task 1 — SKILL.md STEP 6 next-batch preview block

- **Description**: Edit `obsidian/skills/wiki-ingest/SKILL.md` STEP 6 (currently bare "Report and recommend" block — was STEP 5 pre-part-1, renumbered by part-1 T5). Add a "Next batch on next run" preview block that consumes the `scope_summary` JSON emitted by `select-batch.py` (STEP 3 output). Specifically:
  - If `scope_summary.remaining_count == 0`: print "All NEW sources ingested. Wiki is up-to-date with vault." (CC-14 behavior)
  - Else: print `Next batch on next run: <remaining_first_date> → <remaining_last_date> (~{remaining_count} remaining NEW)` (per brief §1 STEP 6 row and §3 scope_summary contract)
  - Place inside the existing STEP 6 report block (between "Sources processed" stats and "Recommended next steps")
  - Keep all existing STEP 6 content (sources processed / pages created / etc.) — additive change
- **Module**: `obsidian/skills/wiki-ingest/SKILL.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-zero-prompt/obsidian/skills/wiki-ingest/SKILL.md (current state — STEP 6 at lines ~235+)
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-zero-prompt/obsidian/skills/wiki-ingest/scripts/select-batch.py (scope_summary JSON shape authority)
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-zero-prompt/docs/superpowers/specs/2026-05-17-wiki-ingest-zero-prompt-oldest-first-design.md (§1 STEP 6 row mentions "1 行預告"; §3 scope_summary contract)
- **Acceptance**:
  - **RED**: `grep -c 'Next batch on next run\|Up-to-date' obsidian/skills/wiki-ingest/SKILL.md` returns 0
  - **GREEN**: `grep -c 'Next batch on next run' obsidian/skills/wiki-ingest/SKILL.md` ≥ 1; `grep -c 'Up-to-date\|up-to-date' obsidian/skills/wiki-ingest/SKILL.md` ≥ 1 (the conditional branch); `grep -c 'scope_summary' obsidian/skills/wiki-ingest/SKILL.md` ≥ 1 (the JSON field reference); STEP 6 still has existing sub-sections (Sources processed / Recommended next steps)
- **Dependencies**: none
- **Brief item covered**: §1 STEP 6 row "末段加 1 行預告"; §3 scope_summary fields

## Task 2 — pytest CC-14 + CC-15 (up-to-date + frontmatter-status)

- **Description**: Extend `obsidian/tests/wiki_ingest/test_select_batch.py` parametrize list with 2 cases:
  - **CC-14**: Zero candidates after bucket = zero NEW + zero MOD (i.e., all candidates already in manifest with matching hash → UNCHANGED). Build: 3 files, populate manifest with REAL SHA-256 hashes matching their content (use `hashlib.sha256(content.encode("utf-8")).hexdigest()` in builder; opposite pattern from CC-07 which used synthetic stale hashes for MODIFIED). Expected: batch=[], remaining=[], skipped_unchanged=3, scope_summary fields all None.
  - **CC-15**: Script doesn't filter by frontmatter `status` field. Build: 4 NEW files with frontmatter:
    - 1 with `status: reviewed-accept`
    - 1 with `status: pending-review`
    - 1 with `status: reviewed-reject`
    - 1 without any `status` field
    All 4 dated 2023-01-01..2023-01-04, no manifest entries. Expected: batch=4 (all 4 appear; script applies date sort + cap, doesn't filter by status), sorted oldest-first.

Use the existing `_run()` helper. CC-14 needs custom manifest setup (real SHA hashes); easiest path = standalone test function `test_select_batch_cc14` similar to CC-07 (pre-populated manifest pattern). CC-15 fits standard parametrize harness (empty manifest).

Document in test comment that CC-15 verifies a NEGATIVE: script does NOT filter by status; the auto-research gate lives in SKILL.md STEP 4a (per-source loop, section 4a "Read source content"), not in select-batch.py.

- **Module**: `obsidian/tests/wiki_ingest/test_select_batch.py`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-zero-prompt/obsidian/tests/wiki_ingest/test_select_batch.py (existing — extend without breaking CC-01..CC-13)
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-zero-prompt/obsidian/skills/wiki-ingest/scripts/select-batch.py (verify script doesn't look at frontmatter.status)
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-zero-prompt/obsidian/skills/wiki-ingest/SKILL.md (STEP 4a auto-research gate prose for reference)
- **Acceptance**:
  - **RED**: `pytest obsidian/tests/wiki_ingest/test_select_batch.py -v -k "cc14 or cc15"` collects 0 matching items
  - **GREEN**: `pytest obsidian/tests/wiki_ingest/ -v` exits 0 AND `pytest -v` output lines contain both `cc14` and `cc15` as PASSED test ids (verbatim substring match); total test count = 16 pre-T2 + 2 new = 18 PASSED (regardless of standalone vs parametrize structure for CC-14, both must appear as PASSED entries)
- **Dependencies**: none (test file extension only; existing CC-01..13 unchanged)
- **Brief item covered**: §4 Test harness — "CC-14..CC-15" (reframed per §"CC-14 and CC-15 reframe note" above)

## Task 3 — `.github/workflows/test-obsidian.yml` CI workflow

- **Description**: Create `.github/workflows/test-obsidian.yml` mirroring `.github/workflows/test-code-toolkit.yml` layout. Trigger: `pull_request` on paths `obsidian/**` and `.github/workflows/test-obsidian.yml` itself. Runner: ubuntu-latest. Steps: checkout → setup-python (3.10 or 3.11) → `cd obsidian && python3 -m pip install -e ".[dev]"` (installs pytest from pyproject.toml dev extra) → `python3 -m pytest tests/ -v` with PYTHONDONTWRITEBYTECODE=1 env var.
- **Module**: `.github/workflows/test-obsidian.yml`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-zero-prompt/.github/workflows/test-code-toolkit.yml (mirror layout)
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-zero-prompt/obsidian/pyproject.toml (verify dev extra spec)
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-zero-prompt/obsidian/tests/wiki_ingest/ (verify tests dir layout)
- **Acceptance**:
  - **RED**: `ls .github/workflows/test-obsidian.yml` returns "No such file"
  - **GREEN**: file exists; `yq '.jobs' .github/workflows/test-obsidian.yml` parses without error (valid YAML structure); workflow can be triggered by `gh workflow run` once branch is pushed (will be verified at PR-open time)
- **Dependencies**: none
- **Brief item covered**: §4 Test harness — "CI: .github/workflows/test-obsidian.yml (仿 code-toolkit 既有)"; deferred from part-1 plan T1 + part-2 plan §Out of scope

## Task 4 — Version bump plugin.json 3.9.0 → 3.10.0 + marketplace.json sync

- **Description**: Bump `obsidian/.claude-plugin/plugin.json` `version` field from `3.9.0` → `3.10.0` (per brief §8 — minor bump for new feature without breaking existing explicit usage). Verify `marketplace.json` entry for the obsidian plugin doesn't have a stale `description` field — per repo memory `plugin_json_location_and_description_sync` and CI `scripts/check-marketplace-description-sync.py`, marketplace.json should keep description in sync OR not have it (plugin.json is single SoT). If description drift exists, sync to plugin.json's value.
- **Module**: `obsidian/.claude-plugin/plugin.json` (primary)
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-zero-prompt/obsidian/.claude-plugin/plugin.json (current 3.9.0)
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-zero-prompt/.claude-plugin/marketplace.json (verify sync — touch only if drift)
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-zero-prompt/scripts/check-marketplace-description-sync.py (CI enforcer — run to verify)
- **Acceptance**:
  - **RED**: `jq -r .version obsidian/.claude-plugin/plugin.json` returns `3.9.0`
  - **GREEN**: `jq -r .version obsidian/.claude-plugin/plugin.json` returns `3.10.0`; `python3 scripts/check-marketplace-description-sync.py` exits 0 (no drift)
- **Dependencies**: none
- **Brief item covered**: §8 PR / version bump rationale (minor bump v3.9.0 → v3.10.0)

---

## Notes

- All 4 tasks parallel-eligible. SDD wave 1 = 4 implementers concurrent. Wave 2 = N/A (no sequential deps).
- T2 has a potential standalone-vs-parametrize architecture decision for CC-14 (real SHA-256 hashes in manifest); implementer choose per CC-07 precedent. Document in self_review.
- After part-3 SDD complete and reviewers all PASS, invoke `code-toolkit:finishing-a-development-branch` for:
  - Final dogfood on `~/kouko-obsidian-vault` (verify next ~15 of 4493 remaining oldest NEW notes get picked up correctly)
  - PR title (`wiki-ingest: zero-prompt default + oldest-first auto-batching (v3.10.0)`)
  - PR body with 8 design decisions + per-part SDD verdict matrix + dogfood capture
  - Merge to main
- `.serena/` untracked dir in worktree is plugin-cache; ignore (not committable).

## Out of scope (handled in finishing-a-branch phase)

| Item | Why |
|---|---|
| Dogfood manual run on `~/kouko-obsidian-vault` | Manual action; not pytest-testable; verifies real-vault behavior before merge |
| PR title / body composition | finishing-a-branch skill responsibility |
| Final review of all 22 commits | finishing-a-branch consolidates |
| Merge decision (squash vs merge commit) | User + finishing-a-branch decide |
| Post-merge re-test on main | Out of branch scope |

## Open questions surfaced (carry to finishing-a-branch / post-merge)

1. **`/loop` integration**: brief deferred to "future PR" (Phase 2 candidate). Not part of v3.10.0. Carry to v3.11.0+ if dogfood reveals demand.
2. **Agent self-judging cap**: per design doc §Out of scope, deferred to Phase 2 future PR (Option C minimal SKILL.md guidance). Not part of v3.10.0.
3. **scan-vault.sh first-time 4500-file perf**: existing problem, not addressed by this PR per design doc §Out of scope. May surface as friction during dogfood; if so, file as v3.11.0 candidate.
4. **CC-14 implementation choice (parametrize vs standalone)**: T2 implementer decides; if standalone, follow CC-07 pattern.
