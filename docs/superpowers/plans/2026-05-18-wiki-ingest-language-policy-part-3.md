# Plan: wiki-ingest language policy — part 3 (commit 3 scope)

**Source brief**: docs/superpowers/specs/2026-05-18-wiki-ingest-language-policy-design.md
**Total tasks**: 3 (≤5 ✓)
**Execution order**: parallel-where-possible
**Plan-document-reviewer verdict**: PASS (2026-05-18 round-1, 13/13 applicable checks; check 12 N/A — not a BLOCKED fallback)

## Scope of this plan

**Commit 3** per brief §7. Final commit before merge / finishing-a-branch handoff. Builds on part-1 (4 commits, all DONE) + part-2 (5 commits, all DONE). Branch state: 12 commits ahead of main; 6 pytest PASS; verify-drift.py confirms all 4 functional copies in sync.

**Commit 3 deliverables**:
- pytest discovery fix (`obsidian/pyproject.toml` testpaths extend to include `scripts/` — currently CI only discovers `tests/` and silently ignores our 6 new test files at `obsidian/scripts/`)
- Dogfood capture (verify-drift.py exit code 0 + pytest output proof) for PR body
- Version bump `obsidian/.claude-plugin/plugin.json` 3.10.0 → 3.11.0 + marketplace.json description sync

**CC-LL-01..05 pytest deferred — not feasible**: Design brief §6 promised `test_language_policy.py` with 5 fixtures. After recon, the language policy is enforced by Claude reading SKILL.md + language-policy.md prose; there is no Python implementation to unit-test. The wiki-lint L13 check (CC-LL-05) is also Claude-driven, not a Python script. Testing CC-LL-01..04 would require either: (a) an LLM-loop test harness (not pytest-scope), (b) writing a Python implementation of the language policy resolver (out of scope — design has Claude do this), or (c) snapshot tests of expected Claude behavior (brittle + slow). MVP defers all CC-LL pytest to a post-merge Phase 2 PR if real demand emerges; manual dogfood in T2 substitutes for now.

**Out of part-3 scope** → finishing-a-branch phase:
- PR title / body composition (use design spec + 3 plan docs as source)
- Merge decision
- Post-merge plugin reload + smoke validation

## Dependency graph

```
T1 (pyproject.toml testpaths)     T2 (dogfood capture)     T3 (version bump)
            \                              |                       /
             \                             |                      /
              ↘                            ↓                     ↙
                                  (all parallel — different files; safe)
```

All 3 tasks parallel-eligible: different files, no shared symbols. SDD via `dispatching-parallel-agents` MAY dispatch all 3 implementers in one assistant message.

---

## Task 1 — Fix pyproject.toml testpaths to discover scripts/ tests

- **Description**: Edit `obsidian/pyproject.toml`. Current state: `[tool.pytest.ini_options] testpaths = ["tests"]`. Our 6 new pytest files (T2 + T3 of part-2) live at `obsidian/scripts/test_*.py` (adjacent-to-script pattern), so they are NOT discovered by CI's `python3 -m pytest tests/ -v` invocation. Fix: extend testpaths to `["tests", "scripts"]` so CI finds both. Verify: `python3 -m pytest` (no path arg, defers to testpaths) from `obsidian/` discovers all 6 tests.
- **Module**: `obsidian/pyproject.toml`
- **Files touched**: `obsidian/pyproject.toml`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-language-policy/obsidian/pyproject.toml (current state)
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-language-policy/.github/workflows/test-obsidian.yml (CI workflow that runs `pytest tests/ -v` — does NOT pick up scripts/ tests today)
- **Acceptance**:
  - **RED**: `grep -c 'testpaths.*scripts' obsidian/pyproject.toml` returns 0
  - **GREEN**:
    - `grep -c 'testpaths' obsidian/pyproject.toml` returns 1
    - testpaths value includes both "tests" and "scripts"
    - From worktree root: `cd obsidian && PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -v 2>&1 | grep -c 'PASSED'` returns 6 (the 6 tests in scripts/ are now discovered)
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: §6 Test plan (test infra correctness — CI must discover the scripts/ smoke tests added in part-2)

## Task 2 — Dogfood capture on worktree state

- **Description**: Capture proof-of-correctness from current worktree state and append to `docs/superpowers/plans/2026-05-18-wiki-ingest-language-policy-part-3.md` (this plan file itself) under a new `## Dogfood capture` section, OR a new file `docs/superpowers/audits/2026-05-18-wiki-ingest-language-policy-v3.11.0-dogfood.md`. Captures: (a) `python3 obsidian/scripts/verify-drift.py` exit code + output ("OK: all 4 functional copies match canonical + SSOT header"), (b) `cd obsidian && PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -v` output showing 6 PASSED, (c) brief note documenting why LLM-behavior CC-LL-01..05 dogfood is deferred (per design brief reality check — language policy is Claude-prose-enforced not script-enforced; post-merge Phase 2 candidate for LLM-loop test harness if demand emerges), (d) sanity check confirming `obsidian/skills/wiki-{cross-linker,query,lint,auto-research}/references/language-policy.md` all exist with SSOT header.
- **Module**: `docs/superpowers/audits/2026-05-18-wiki-ingest-language-policy-v3.11.0-dogfood.md` (new file recommended; cleaner than appending to plan doc)
- **Files touched**: `docs/superpowers/audits/2026-05-18-wiki-ingest-language-policy-v3.11.0-dogfood.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-language-policy/obsidian/scripts/verify-drift.py (T2 part-2)
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-language-policy/obsidian/scripts/distribute.py (T1 part-2)
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-language-policy/docs/superpowers/audits/ (existing audit pattern — `2026-05-13-systems-thinking-toolkit-dogfood.md` etc. for format reference)
- **Acceptance**:
  - **RED**: `ls docs/superpowers/audits/2026-05-18-wiki-ingest-language-policy-v3.11.0-dogfood.md` returns "No such file"
  - **GREEN**:
    - File exists; `wc -l` returns ≥ 30 (substantive content)
    - Contains literal "Exit: 0" or "OK: all 4 functional copies match canonical" (verify-drift output capture)
    - Contains literal "6 passed" (pytest output capture)
    - Contains paragraph explaining CC-LL-01..05 LLM-behavior deferral rationale
    - Lists all 4 functional copies as existing
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: §6 Test plan dogfood; §Out of Scope migration "natural drift only" (this audit doc justifies the MVP migration strategy with concrete proof)

## Task 3 — Version bump plugin.json 3.10.0 → 3.11.0 + marketplace sync

- **Description**: Bump `obsidian/.claude-plugin/plugin.json` `version` field from `3.10.0` → `3.11.0` (per design brief §8 — minor bump, new feature without breaking backward-compat). Verify `scripts/check-marketplace-description-sync.py` passes (per v3.10.0 part-3 T4 pattern + repo memory `plugin_json_location_and_description_sync`). If marketplace.json has version field independently, sync; usually only description must match.
- **Module**: `obsidian/.claude-plugin/plugin.json`
- **Files touched**: `obsidian/.claude-plugin/plugin.json` (marketplace.json only touched if drift exists)
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-language-policy/obsidian/.claude-plugin/plugin.json (current 3.10.0)
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-language-policy/.claude-plugin/marketplace.json (sync target — touch only if drift)
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-language-policy/scripts/check-marketplace-description-sync.py (CI enforcer; run to verify)
- **Acceptance**:
  - **RED**: `jq -r .version obsidian/.claude-plugin/plugin.json` returns `3.10.0`
  - **GREEN**:
    - `jq -r .version obsidian/.claude-plugin/plugin.json` returns `3.11.0`
    - `python3 scripts/check-marketplace-description-sync.py` exits 0 (no drift)
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: §8 PR / version bump (minor v3.10.0 → v3.11.0)

---

## Notes

- **All 3 parallel**: T1 + T2 + T3 independent (different files, no shared state); SDD via `dispatching-parallel-agents` MAY dispatch all 3 implementers in one assistant message.
- **No fancy pytest CC-LL fixtures**: per §Scope explanation, language-policy enforcement is Claude-prose-driven not script-driven. Post-merge demand may drive a Phase 2 PR adding an LLM-loop harness OR a Python policy resolver. MVP defers.
- **T2 (dogfood capture) is documentation work**: no LLM call, no /wiki-ingest run — just capturing verify-drift + pytest output as concrete proof for PR body. LLM-behavior dogfood (actually running `/wiki-ingest` on kouko vault to see body language change) defers to post-merge plugin reload + manual user observation.
- This plan covers **commit 3 only**. After SDD complete, invoke `code-toolkit:finishing-a-development-branch` for code-review, PR creation, merge decision.

## Out of scope (handled in finishing-a-branch phase)

| Item | Why |
|---|---|
| Whole-branch code-review (Step 1) | finishing-a-branch responsibility |
| PR title / body composition | finishing-a-branch responsibility (will use design spec + 3 plans as source) |
| Push + gh pr create | finishing-a-branch responsibility |
| Post-merge plugin reload + LLM-behavior smoke (kouko vault actually using `/wiki-ingest`) | Out of branch scope; manual user action |
| Worktree cleanup | finishing-a-branch responsibility |

## Open questions surfaced (carry to finishing-a-branch / post-merge)

1. **LLM-behavior dogfood after merge**: post-merge, kouko reloads plugin and runs `/wiki-ingest` on real vault with `OBSIDIAN_WIKI_LANGUAGE_POLICY=enabled` + custom decision tree. Captures real-world behavior (does Claude actually use zh-TW for `investing/` paths? does aliases get added when slug ≠ body?). If observed behavior diverges from design intent, Phase 2 PR adds prose tightening to language-policy.md or wiki-ingest STEP 4c.
2. **`/wiki-relang` migration command**: design Phase 2; triggered if kouko wants to backfill 80+ existing wiki pages with new policy. Not part of v3.11.0.
3. **wiki-lint L13 severity upgrade** (design Open Q3): MVP = SHOULD (warning). Post-dogfood, if false-positive rate is low and missing-aliases is genuinely problematic, upgrade to MUST (error). Phase 2 candidate.
4. **CC-LL-01..05 LLM-loop test harness** (design §6 promised, MVP deferred): if test-quality demands surface (e.g. v3.12+ regression in language policy behavior), build an LLM-loop test harness invoking Claude on fixture vaults + snapshot-checking output. Not v3.11.0 scope.
