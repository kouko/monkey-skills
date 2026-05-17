# Plan: wiki-ingest zero-prompt + oldest-first — part 2 (commit 2 scope)

**Source brief**: docs/superpowers/specs/2026-05-17-wiki-ingest-zero-prompt-oldest-first-design.md
**Total tasks**: 5 (≤5 ✓)
**Execution order**: parallel-where-possible
**Plan-document-reviewer verdict**: PASS (2026-05-17 21:40)

## Scope of this plan

**Commit 2** per brief §7. Builds on part-1 (commits `a027a8e..6d3022f`, all DONE). Adds config read, `topic_filter` feature, batching-policy reference doc, wiki-setup template update, and 5 more CC fixtures. CI workflow (`.github/workflows/test-obsidian.yml`) deferred to part-3 alongside dogfood (commit 3) to stay within 5-task ceiling here.

**Commit 2 deliverables**:
- `select-batch.py` adds `TOPIC_FILTER` env var → substring filter on basename + frontmatter `tags` / `aliases`
- `wiki-ingest/SKILL.md` reads `OBSIDIAN_WIKI_BATCH_ORDER` from config in pre-flight; STEP 1 decision table topic-word row activates filter behavior; STEP 3 passes `BATCH_ORDER` from config (overridden by prompt hint)
- `wiki-setup/SKILL.md` adds `OBSIDIAN_WIKI_BATCH_ORDER=oldest-first` line to `.obsidian-wiki.config` template
- `references/batching-policy.md` (new, 8-section content per brief §6)
- 5 pytest cases CC-09..CC-13 for the `topic_filter` + config interactions

## CC-09..CC-13 reframe note

Brief §4 vault note's original CC-09..CC-13 table mixed SKILL.md prose verification (CC-09 "user prompt research/", CC-10 single-file, CC-11 ambiguous→AskUserQuestion) with script-side concerns. Since SKILL.md scope decisions aren't easily pytest-testable on the script and CC-11's AskUserQuestion path was reinterpreted as topic_filter per brief §What Becomes Obsolete, this plan reframes CC-09..CC-13 to **script-testable cases covering the topic_filter + config features that commit 2 introduces**:

- **CC-09**: `TOPIC_FILTER` filters to subset by basename substring (case-insensitive ASCII)
- **CC-10**: `TOPIC_FILTER` matches via frontmatter `tags` field
- **CC-11**: `TOPIC_FILTER` matches via frontmatter `aliases` field
- **CC-12**: `TOPIC_FILTER` zero-match → empty batch + empty remaining + scope_summary all-null
- **CC-13**: combined `TOPIC_FILTER` + `BATCH_ORDER=newest-first` interaction

SKILL-side scope decisions (path / single-file / topic) covered by T2's spec-reviewer judgment (no script-side testable assertion).

## Dependency graph

```
T1 (select-batch.py topic_filter)       T3 (wiki-setup template)      T4 (batching-policy.md)
            \                                                                  |
             \                                                                 |
              ↓                                                                ↓
       T2 (wiki-ingest SKILL.md)            T5 (pytest CC-09..13)
                  \                              /
                   ↓                            ↓
                          (all → wave-2 reviewers)
```

Parallel waves:
- **Wave 1**: T1, T3, T4 (independent — different files / no shared state)
- **Wave 2**: T2 (depends on T1 — needs TOPIC_FILTER env var name to reference in SKILL.md decision table), T5 (depends on T1 — tests the env var)

---

## Task 1 — Add `TOPIC_FILTER` env var + filter logic to `select-batch.py`

- **Description**: Extend `obsidian/skills/wiki-ingest/scripts/select-batch.py` (from part-1 commit `85694d4`) to read optional `TOPIC_FILTER` env var. When set, filter NEW + MODIFIED candidates BEFORE sort+cap: keep candidate iff (a) basename contains TOPIC_FILTER substring (case-insensitive ASCII; CJK exact-equals via `in` operator works on Python str directly), OR (b) frontmatter `tags` list contains TOPIC_FILTER as exact match, OR (c) frontmatter `aliases` list contains TOPIC_FILTER as exact match. When env unset / empty, filter no-op (preserve part-1 behavior). Filter applied AFTER bucket (NEW/MODIFIED/UNCHANGED) but BEFORE sort+cap, so UNCHANGED skipped count is unaffected.
- **Module**: `obsidian/skills/wiki-ingest/scripts/select-batch.py`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-zero-prompt/obsidian/skills/wiki-ingest/scripts/select-batch.py (current state; the part-1 frontmatter parser is reusable)
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-zero-prompt/docs/superpowers/specs/2026-05-17-wiki-ingest-zero-prompt-oldest-first-design.md (§3 contract + §What Becomes Obsolete on topic_filter scope)
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-zero-prompt/docs/superpowers/plans/2026-05-17-wiki-ingest-zero-prompt-oldest-first-part-2.md (this plan — Task 1 section)
- **Acceptance**:
  - **RED**: `env BATCH_ORDER=oldest-first BATCH_CAP=15 MANIFEST_PATH=/tmp/m.json VAULT_ROOT=/tmp/v TOPIC_FILTER=invest python3 obsidian/skills/wiki-ingest/scripts/select-batch.py < /dev/null` returns same JSON as without TOPIC_FILTER (env var ignored — feature not yet added)
  - **GREEN**: same invocation honors TOPIC_FILTER — only matching candidates appear in batch/remaining; `skipped_unchanged` count unaffected by filter
- **Dependencies**: none
- **Brief item covered**: §3 (extended contract — `TOPIC_FILTER` env var entry); §2 decision table topic-word row → script-side filter mechanism

## Task 2 — Update `wiki-ingest/SKILL.md`: config read + topic_filter scope rule + pass BATCH_ORDER

- **Description**: Edit `obsidian/skills/wiki-ingest/SKILL.md` (current state from part-1 commit `6d3022f`):
  - **(a) Pre-flight**: extend the `.obsidian-wiki.config` read to also accept optional `OBSIDIAN_WIKI_BATCH_ORDER` (default `oldest-first` if absent — backward-compatible with part-1 hardcode).
  - **(b) STEP 1 decision table** topic-word row: change the part-1 placeholder ("Topic-only hints fall back to whole-vault delta with summary line annotation") to specify that topic word → `topic_filter` activated: Claude passes `TOPIC_FILTER=<topic>` env var to `select-batch.py`. Topic resolution = the user prompt's non-path / non-time-keyword content (case-insensitive ASCII substring of basename + frontmatter tags/aliases match per T1).
  - **(c) STEP 3 invocation**: pass `BATCH_ORDER` from config (overridden by per-run prompt hint if applicable per STEP 1 decision table). Show env var assignment in the invocation example.
  - **(d) Reference `references/batching-policy.md`** (created in T4) under STEP 3's references section.
- **Module**: `obsidian/skills/wiki-ingest/SKILL.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-zero-prompt/obsidian/skills/wiki-ingest/SKILL.md (current part-1 state)
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-zero-prompt/docs/superpowers/specs/2026-05-17-wiki-ingest-zero-prompt-oldest-first-design.md (§5 config; §2 decision table; §6 batching-policy.md)
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-zero-prompt/obsidian/skills/wiki-ingest/scripts/select-batch.py (T1 output — confirm TOPIC_FILTER env var name)
- **Acceptance**:
  - **RED**: `grep -c 'OBSIDIAN_WIKI_BATCH_ORDER' obsidian/skills/wiki-ingest/SKILL.md` returns 0; `grep -c 'TOPIC_FILTER' obsidian/skills/wiki-ingest/SKILL.md` returns 0; `grep -c 'batching-policy.md' obsidian/skills/wiki-ingest/SKILL.md` returns 0; STEP 1 topic-word row still says "fall back to whole-vault delta"
  - **GREEN**: `grep -c 'OBSIDIAN_WIKI_BATCH_ORDER' obsidian/skills/wiki-ingest/SKILL.md` ≥ 1 (in pre-flight); `grep -c 'TOPIC_FILTER' obsidian/skills/wiki-ingest/SKILL.md` ≥ 1 (in STEP 3 env section); `grep -c 'batching-policy.md' obsidian/skills/wiki-ingest/SKILL.md` ≥ 1 (lazy-load reference); STEP 1 topic-word row mentions topic_filter activation; `.claude/hooks/validate-skill-folder-structure.sh` passes
- **Dependencies**: Task 1 completes first
- **Brief item covered**: §5 Config (OBSIDIAN_WIKI_BATCH_ORDER); §2 decision table topic-word row (activate topic_filter); §6 batching-policy.md reference

## Task 3 — Add `OBSIDIAN_WIKI_BATCH_ORDER` to `wiki-setup/SKILL.md` config template

- **Description**: Edit `obsidian/skills/wiki-setup/SKILL.md` — locate the `.obsidian-wiki.config` template block (the one that gets written when user runs `/wiki-setup`); append a new line `OBSIDIAN_WIKI_BATCH_ORDER=oldest-first` with a 2-line comment above explaining purpose (oldest-first backfill posture vs newest-first; prompt-hint override). Match the existing comment style in the template. Preserve all existing keys.
- **Module**: `obsidian/skills/wiki-setup/SKILL.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-zero-prompt/obsidian/skills/wiki-setup/SKILL.md (current state)
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-zero-prompt/docs/superpowers/specs/2026-05-17-wiki-ingest-zero-prompt-oldest-first-design.md (§5 — exact template wording)
- **Acceptance**:
  - **RED**: `grep -c 'OBSIDIAN_WIKI_BATCH_ORDER' obsidian/skills/wiki-setup/SKILL.md` returns 0
  - **GREEN**: `grep -c 'OBSIDIAN_WIKI_BATCH_ORDER=oldest-first' obsidian/skills/wiki-setup/SKILL.md` returns 1 (exactly one line in template); comment block above documents oldest-first / newest-first / prompt-hint override
- **Dependencies**: none
- **Brief item covered**: §5 Config — "`wiki-setup/SKILL.md` 的 config 範本同步"

## Task 4 — Create `references/batching-policy.md` (new reference doc)

- **Description**: Create `obsidian/skills/wiki-ingest/references/batching-policy.md` with 8 sections per brief §6:
  1. Purpose (cap policy + batch order resolution)
  2. Date resolution algorithm (decision tree: filename → frontmatter → mtime)
  3. Cap semantics (source count, not wiki page count)
  4. NEW vs MODIFIED interaction (combined sort + combined cap)
  5. Order override matrix (prompt > config)
  6. Undated files behavior (mtime fallback tail semantics)
  7. Three worked examples (use CC-01 / CC-03 / CC-07 from part-1's test suite)
  8. `/loop` integration note (not supported in this commit; rationale)

Stay grounded — quote from `select-batch.py` (T1 output) for accuracy; cross-reference vault paths to design doc + part-1/part-2 plans.

- **Module**: `obsidian/skills/wiki-ingest/references/batching-policy.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-zero-prompt/docs/superpowers/specs/2026-05-17-wiki-ingest-zero-prompt-oldest-first-design.md (§6 outline)
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-zero-prompt/obsidian/skills/wiki-ingest/scripts/select-batch.py (canonical source for behavior — quote env var names + JSON schema)
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-zero-prompt/obsidian/skills/wiki-ingest/references/delta-tracking.md (sibling reference doc — borrow markdown style + heading structure)
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-zero-prompt/obsidian/tests/wiki_ingest/test_select_batch.py (CC-01 / CC-03 / CC-07 worked examples)
- **Acceptance**:
  - **RED**: `ls obsidian/skills/wiki-ingest/references/batching-policy.md` returns "No such file"
  - **GREEN**: file exists; `grep -cE '^## ' obsidian/skills/wiki-ingest/references/batching-policy.md` returns ≥ 8 (eight top-level sections); `grep -c 'TOPIC_FILTER\|BATCH_ORDER\|BATCH_CAP' obsidian/skills/wiki-ingest/references/batching-policy.md` ≥ 3 (each env var named at least once)
- **Dependencies**: none
- **Brief item covered**: §6 batching-policy.md (full 8-section outline)

## Task 5 — pytest CC-09..CC-13 (topic_filter + config-interaction cases)

- **Description**: Extend `obsidian/tests/wiki_ingest/test_select_batch.py` parametrize list (or sibling test function for fixtures needing pre-populated state, mirroring CC-07 pattern from part-1) with 5 cases:
  - **CC-09**: TOPIC_FILTER substring on basename → only matching candidates in batch. Build: 5 NEW files, 3 with "invest" substring in basename, 2 without; TOPIC_FILTER="invest". Expected: batch=3 matching, remaining=[], `skipped_unchanged=0`.
  - **CC-10**: TOPIC_FILTER matches frontmatter `tags` list → kept. Build: 4 NEW files, 2 with frontmatter `tags: [investing, x]`, 2 with other tags; TOPIC_FILTER="investing". Expected: batch=2 by tag match.
  - **CC-11**: TOPIC_FILTER matches frontmatter `aliases` list → kept. Build: 4 NEW files, 2 with frontmatter `aliases: [stock, equity]`, 2 without; TOPIC_FILTER="stock". Expected: batch=2 by alias match.
  - **CC-12**: TOPIC_FILTER with zero matches → empty batch + empty remaining; scope_summary date fields all null. Build: 5 NEW files, none matching; TOPIC_FILTER="nomatch". Expected: batch=[], remaining=[], all scope_summary date fields null.
  - **CC-13**: TOPIC_FILTER + BATCH_ORDER=newest-first → matched subset sorted desc. Build: 6 NEW files (3 matching, 3 not), all dated, spread across dates; TOPIC_FILTER="invest" + BATCH_ORDER="newest-first". Expected: batch=3 matching sorted desc by date.

Use the existing `_run()` helper from part-1 T3 — extend it to take `topic_filter` arg (passed as TOPIC_FILTER env var). Don't break CC-01..CC-08 — TOPIC_FILTER defaults to None / unset in existing calls.

- **Module**: `obsidian/tests/wiki_ingest/test_select_batch.py`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-zero-prompt/obsidian/tests/wiki_ingest/test_select_batch.py (existing — extend without breaking CC-01..08)
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-zero-prompt/obsidian/skills/wiki-ingest/scripts/select-batch.py (T1 — confirms TOPIC_FILTER env semantics)
- **Acceptance**:
  - **RED**: `pytest obsidian/tests/wiki_ingest/test_select_batch.py -v -k "cc09 or cc10 or cc11 or cc12 or cc13"` collects 0 matching items
  - **GREEN**: `pytest obsidian/tests/wiki_ingest/test_select_batch.py -v` shows 13 PASSED (cc01..cc13, includes any standalone like cc07 from part-1); existing CC-01..CC-08 unchanged
- **Dependencies**: Task 1 completes first
- **Brief item covered**: §4 Test harness — "CC-09..CC-13" (reframed per §"CC-09..CC-13 reframe note" above); §3 TOPIC_FILTER env var behavior

---

## Notes

- **T1 + T3 + T4 parallel**: independent files, no shared state. T1 is the longest (touches existing script logic); T3 is mechanical (one config-template line); T4 is doc-write (~500-1000 lines markdown).
- **T2 + T5 parallel after T1**: both consume T1's TOPIC_FILTER env var. T2 modifies SKILL.md (doc), T5 modifies test file (code). Different files → safe parallel.
- **T4 grounds against design doc by default**; T4 author can also reference T1's output for accuracy if T1 lands first, otherwise document from design doc and revise during review if drift detected. Treated as parallel with T1 (no hard dep).
- **CC-13 combines TOPIC_FILTER + BATCH_ORDER=newest-first** to exercise the full new env surface in commit 2.
- This plan ships **commit 2 of 3** in the design doc §7 plan. Commit 3 (next-batch preview + CC-14..15 + dogfood + CI workflow) will get a part-3 plan after commit 2 ships and dogfood readiness is assessed.

## Out of scope (for part-3 plan)

| Brief item | Why deferred |
|---|---|
| STEP 6 next-batch preview + `scope_summary` consumption | part-3 (commit 3) |
| CC-14 (all-already-ingested up-to-date case) | part-3 (commit 3) |
| CC-15 (wiki-auto-research status interaction) | part-3 (commit 3) |
| `.github/workflows/test-obsidian.yml` (CI for obsidian pytest) | part-3 (alongside dogfood) — kept out of part-2 to honor 5-task ceiling |
| Dogfood on `~/kouko-obsidian-vault` | part-3 (commit 3) |
| PR description / changelog / version bump v3.10.0 | finishing-a-branch phase after commit 3 |

## Open questions surfaced (track to part-3)

1. **TOPIC_FILTER case-insensitivity precision**: Plan T1 specifies "case-insensitive ASCII; CJK exact-equals via `in`". Confirm in T1 implementer's actual logic whether `in` operator on Python str handles CJK comparison as substring (it does — Python str supports unicode codepoints). May need to clarify in batching-policy.md §1 Purpose.
2. **TOPIC_FILTER vs MODIFIED bucket interaction**: If TOPIC_FILTER excludes a MODIFIED source, the MODIFIED entry in manifest stays (not re-ingested). Is that desired? Likely yes (out-of-scope = don't touch), but T1 implementer should self-flag the semantics in commit message or `DONE_WITH_CONCERNS` if ambiguous.
3. **CC-14 dependency**: when batch is empty (all UNCHANGED), STEP 6 report should say "Up-to-date". Part-3 task; verify the script's current "all empty" output already supports this gracefully.
