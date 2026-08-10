# Plan: cheap hardening batch — five small fixes from the 0.73.0 ship review

Source brief: docs/loom/specs/2026-08-10-cheap-hardening-batch.md
Goal: 把 0.73.0 出貨檢討找出的五個便宜缺陷一次修掉——plan-gate 修訂自檢、AGENTS.md 動詞收錄、loom-init 巢狀 cwd 警告、活 repo 測試改 tmp fixture、兩條設計決議立案。
Stage: finishing
Total tasks: 6
Critical-path depth: 4 (≤5)
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-08-10, round 2)

## Task 1 — writing-plans revision-delta self-check + ratchet raise
- Description: In `loom-code/skills/writing-plans/SKILL.md`'s NEEDS_REVISION loop paragraph (currently "If reviewer returns `NEEDS_REVISION`, writing-plans **fixes the plan** and re-runs the reviewer. Up to 2 rounds; …"), add one new sentence immediately after "re-runs the reviewer." stating: before that re-dispatch, re-run the §Pre-patch self-screen on the revision delta itself — every line the fix added or changed — because three consecutive arcs' round-2 findings were defects the round-2 revision itself introduced. The new material is its OWN sentence, never spliced into the existing pinned sentence. In `loom-code/scripts/test_wp_extraction_pointers.py`, add a pin test asserting the revision-delta duty (grep for a stable phrase, e.g. "revision delta") inside the whitespace-normalized SKILL.md text, and raise the word-cap ratchet in `test_word_count_at_most_4047` (rename to the new cap, update the assert and message to record: raised deliberately by the 2026-08-10 cheap-hardening-batch arc for the revision-delta self-check sentence). New cap = measured word count after the edit + ~20 headroom, expected ≈4085.
- Module: loom-code/skills/writing-plans
- Files touched: loom-code/skills/writing-plans/SKILL.md, loom-code/scripts/test_wp_extraction_pointers.py
- Context paths:
  - loom-code/skills/writing-plans/SKILL.md (lines 100–115)
  - loom-code/scripts/test_wp_extraction_pointers.py (the (f) word-cap section and one pointer-pin test as shape example)
- Acceptance:
  - RED: new test `test_needs_revision_loop_self_screens_the_revision_delta` fails against current SKILL.md (phrase absent)
  - GREEN: pin test passes; word-cap test passes at the new recorded cap; full file `python3 -m pytest loom-code/scripts/test_wp_extraction_pointers.py -q` green
- Dependencies: none
- Independent: true
- Brief item covered: "writing-plans' NEEDS_REVISION loop states: before re-dispatching the reviewer, re-run the pre-patch self-screen on the revision delta itself"
- Status: done(91f71033)
- Gloss: 讓 plan 閘門在重派審查前先自檢「修訂本身」——堵住連三弧 round-2 自引缺陷的洞

## Task 2 — AGENTS.md declares loom_init + conventional pin test
- Description: Add one bullet to AGENTS.md's managed command-surface block (immediately after the backlog_index.py bullet, before `<!-- END command-surface (managed) -->`) declaring `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/loom_init.py" [repo-root]` — scaffolds the queue layer (backlog charter + DIRECTION skeleton + plans/ + specs/), self-verifies via backlog_index.py, refuses when either artifact exists; note it is plugin-shipped ONLY (a bootstrap verb has no repo-root tier). Add `test_agents_md_declares_loom_init` to `loom-code/scripts/test_loom_init.py` following the managed-block pin convention (`start = text.index("BEGIN command-surface (managed)")` … assert "loom_init.py" in managed_block), precedent `test_writing_plans_change_binding.py:148`.
- Module: AGENTS.md command surface
- Files touched: AGENTS.md, loom-code/scripts/test_loom_init.py
- Context paths:
  - AGENTS.md (lines 150–172, the plan_card/backlog_index bullets as shape)
  - loom-code/scripts/test_writing_plans_change_binding.py (lines 148–158, pin convention)
- Acceptance:
  - RED: `test_agents_md_declares_loom_init` fails (loom_init.py absent from managed block)
  - GREEN: pin passes; `python3 -m pytest loom-code/scripts/test_loom_init.py -q` green
- Dependencies: none
- Independent: false
- Brief item covered: "AGENTS.md's managed command-surface block declares `loom_init.py`, with the conventional `test_agents_md_declares_*` pin"
- Status: done(b87c7a1)
- Gloss: 補上指令表漏掉的最新動詞，並用慣例釘測試防再漏

## Task 3 — loom_init nested-cwd advisory warning
- Description: In `loom-code/scripts/loom_init.py` `main()`, after target resolution (line ~96), run `git -C <target> rev-parse --show-toplevel` via subprocess; if it succeeds AND its output resolved != target, print one advisory line to STDERR ("loom-init: note — <target> is not the git repo root (<toplevel>); scaffolding here anyway (monorepo subdirs are legitimate)") and PROCEED; any git failure (git absent, not a repo) → silent skip. Never changes exit code. Add a test in `test_loom_init.py`: scaffold into a subdir of a tmp git repo (`git init` the tmp_path, target = tmp_path/"sub") → warning appears on stderr AND scaffold succeeds (exit 0); plus a no-warning assertion for the plain tmp_path (non-git) success case.
- Module: loom-code/scripts
- Files touched: loom-code/scripts/loom_init.py, loom-code/scripts/test_loom_init.py
- Context paths:
  - loom-code/scripts/loom_init.py (main(), lines 95–150)
  - loom-code/scripts/test_loom_init.py (tmp fixture shapes at lines 60–90)
- Acceptance:
  - RED: `test_nested_cwd_run_warns_but_proceeds` fails (no warning emitted)
  - GREEN: warning test + non-git silence test pass; all existing loom_init tests stay green (stderr channel unasserted by them, verified in brief Boundary evidence)
- Dependencies: Task 2 completes first
- Independent: false
- Brief item covered: "`loom_init.py` warns (stderr, advisory — never refuses) when the target dir is inside a git repo but is not `git rev-parse --show-toplevel`"
- Status: done(c13d6e98)
- Gloss: 巢狀目錄跑 loom-init 會被提醒不是 repo 根——但單 repo 子包合法所以只警告不擋

## Task 4 — existence test drops the live-repo probe
- Description: In `loom-code/scripts/test_loom_init.py`, rewrite `test_loom_init_ships_with_its_templates_and_runs` so the refusal probe runs against a tmp fixture (mkdir `tmp_path/docs/loom/backlog` then run `loom_init.py <tmp_path>`) instead of `cwd=REPO_ROOT` against the live repo; keep the three file-existence asserts and the "already exists" + returncode 1 asserts unchanged in meaning. The comment explaining the probe's purpose updates to name the tmp fixture.
- Module: loom-code/scripts
- Files touched: loom-code/scripts/test_loom_init.py
- Context paths:
  - loom-code/scripts/test_loom_init.py (lines 88–115)
- Acceptance:
  - RED: grep-style check — current test body contains `cwd=REPO_ROOT` (pre-state); after the edit the function no longer references REPO_ROOT as the run target (diagnostic RED: assert on the pre-state fails once edited — verified by running the suite before/after)
  - GREEN: `python3 -m pytest loom-code/scripts/test_loom_init.py -q` green with the rewritten probe
- Dependencies: Task 3 completes first
- Independent: false
- Brief item covered: "`test_loom_init_ships_with_its_templates_and_runs` runs its refusal probe against a tmp fixture with a pre-made store, not `REPO_ROOT`"
- Status: done(37a7edf7)
- Gloss: 測試不再拿活 repo 當探針，改用拋棄式 fixture——消掉理論上的環境耦合

## Task 5 — two backlog entries + index regen
- Description: Create two backlog entries per the charter (docs/loom/backlog/README.md) format: (a) `2026-08-10-queue-layer-family-ownership-north-star.md` — status OPEN; body records: the queue layer (backlog store + DIRECTION + plan ledger) is conceptually family-wide but physically owned by loom-code because `${CLAUDE_PLUGIN_ROOT}` cannot point at sibling plugins (cross-plugin primitive gap); note the dual-owner inconsistency (loom-memory ships in loom-pipeline, backlog tooling in loom-code); start condition: next cross-plugin primitive change, or the partial-merge evaluation arc opening. (b) `2026-08-10-family-integration-evaluation-seed.md` — status OPEN; body records the adjudicated direction: behavioral pull not packaging (`--family-scan` visibility built on shipped primitives; no stub files — presence-conditional machinery would consume hollow constitutions; Axis 0's product-shaped moment is the only hard-gate candidate), with partial merge loom-code⊕loom-pipeline as the foundation option; start condition: user authorizes the family-integration evaluation arc. Then regenerate the index: `python3 scripts/backlog_index.py --write` and include the refreshed `docs/loom/BACKLOG.md`; `--validate` exits 0.
- Module: docs/loom/backlog
- Files touched: docs/loom/backlog/2026-08-10-queue-layer-family-ownership-north-star.md, docs/loom/backlog/2026-08-10-family-integration-evaluation-seed.md, docs/loom/BACKLOG.md
- Context paths:
  - docs/loom/backlog/README.md (charter: entry format + status enum)
  - docs/loom/backlog/2026-08-10-loom-lacks-a-milestone-layer-between-plan-stage-and-direction.md (freshest entry as shape example)
- Acceptance:
  - RED: `python3 scripts/backlog_index.py --check` fails after the two entries exist but before regen (index missing them)
  - GREEN: `--validate` exit 0 AND `--check` exit 0 with both entries indexed
- Dependencies: none
- Independent: true
- Brief item covered: "Two backlog entries filed + index regenerated: (a) queue-layer North Star … (b) family-integration evaluation seed"
- Status: done(c63b8f4d)
- Gloss: 把對話裡裁掉的兩個方向性決議寫成正式檔案，未來的弧才有起點可引

## Task 6 — version carrier: 0.73.0 → 0.74.0
- Description: Bump `loom-code/.claude-plugin/plugin.json` version to "0.74.0"; add a `## [0.74.0]` CHANGELOG.md entry (revision-delta self-screen, AGENTS.md loom_init declaration, loom_init nested-cwd advisory, live-repo probe removal); migrate the shipping-version pin in `loom-code/scripts/test_docs_review_blocking_class.py` — rename `test_plugin_version_and_changelog_at_0_73_0` to `..._at_0_74_0` and update both literal assertions ("0.74.0" in plugin.json text, `## [0.74.0]` in CHANGELOG text). As the terminal task, its completion report to the orchestrator must carry the close-out surfacing duty: the fired start condition of backlog item `2026-07-06-anti-copy-acceptance-greps-pass-paraphrase-copies` (its trigger — "next touch of writing-plans SKILL.md" — fires with this arc's Task 1) is surfaced to the user in the close-out report for a separate open/decline decision.
- Module: loom-code plugin manifest
- Files touched: loom-code/.claude-plugin/plugin.json, loom-code/CHANGELOG.md, loom-code/scripts/test_docs_review_blocking_class.py
- Context paths:
  - loom-code/scripts/test_docs_review_blocking_class.py (lines 195–230)
  - loom-code/CHANGELOG.md (top entry as shape)
- Acceptance:
  - RED: migrated pin test fails while plugin.json still reads 0.73.0
  - GREEN: `python3 -m pytest loom-code/scripts/test_docs_review_blocking_class.py -q` green; literal "0.74.0" present in all three files; close-out report surfaces the fired start condition of backlog item 2026-07-06-anti-copy-acceptance-greps-pass-paraphrase-copies to the user
- Dependencies: Tasks 1, 2, 3, 4 complete first
- Independent: false
- Brief item covered: "loom-code 0.73.0 → 0.74.0 (items 1/3/4 change plugin content), CHANGELOG entry, and migration of the shipping-version pin test"
- Status: done(5a89bee0)
- Gloss: 版本載體——沒 bump 則 plugin update 靜默 no-op，外部 repo 拿不到這批修正

## Notes

- Kickoff decision (adjudicated in brief §Decision): Task 3 is advisory-not-refusal — monorepo-subdir adoption is legitimate; refusal would false-positive (same advisory-vs-red split as `--stale-scan`).
- Kickoff decision: Task 1's ratchet raise uses the sanctioned deliberate-raise mechanism with the reason recorded in the test message (precedent: 4023→4047, 2026-08-06).
- Out-of-scope backlog item `2026-07-06-anti-copy-acceptance-greps-pass-paraphrase-copies` fires its start condition with this arc (touches writing-plans SKILL.md); the surfacing duty is owned by Task 6 (terminal task — see its Description + GREEN clause), deliberately not absorbed as work.
- Round-1 revision delta self-screen (2026-08-10, the duty Task 1 legislates, applied to this plan's own revision): delta = ① Task 5 Review-weight field REMOVED (full triad runs — cleanest Check-16 cure, no split needed; remaining fields untouched, Independent/Files unchanged so Check 15's wave shape holds); ② Task 6 Description + GREEN gained the close-out surfacing duty using the reviewer's own prescription verbatim (no Files-touched change — it is a reporting duty, not an artifact change, so Checks 6/7 scope unaffected); ③ this Notes bullet. Re-checked the delta against Checks 16, 8, 6, 7, 15: no new obligation sentence introduced except the one now owned by Task 6; no field schema broken.
- Wave shape: wave 1 = T1 + T2 + T5 (disjoint files); then T3 → T4 (both edit test_loom_init.py after T2's pin lands); T6 last.
- Verdict stamped PASS (2026-08-10, round 2) — stamping the verdict, amendment kind 1, no re-review.
