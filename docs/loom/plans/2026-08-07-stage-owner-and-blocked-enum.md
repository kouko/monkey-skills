# Plan: Stage-update owner for review rounds + blocked:user-decision enum value

Source brief: docs/loom/specs/2026-08-07-stage-owner-and-blocked-enum.md
Goal: The Stage header gains an owner for review-round transitions (a duty sentence in requesting-code-review, plus the docs-arm rider) and a blocked:user-decision enum value across both prose copies and the pin test, shipped with the loom-code version bump and CHANGELOG entry.
Stage: finishing
Endpoint named: yes → continuous (user: 「先做 PR A 吧」)
Total tasks: 5
Critical-path depth: 3 (≤5)
Execution order: sequential
Plan-document-reviewer verdict: PASS (2026-08-07, round 1, 15/15)

## Task 1 — plan-format.md: enum value + when-to-set duty + pin update
- Description: Extend the Stage enum schema line in plan-format.md with `blocked:user-decision`, add the when-to-set duty as its own sentence, and update the verbatim pin RED-first.
- Module: loom-code/skills/writing-plans (reference docs + its pin test)
- Files touched: loom-code/scripts/test_plan_format_progress_fields.py, loom-code/skills/writing-plans/references/plan-format.md
- Context paths:
  - loom-code/skills/writing-plans/references/plan-format.md
  - loom-code/scripts/test_plan_format_progress_fields.py
  - docs/loom/memory/splicing-into-a-pinned-sentence-creates-false-readings.md
- Acceptance:
  - RED: `test_stage_enum_line_present` (STAGE_ENUM_LINE updated to the new five-value enum, verbatim below) fails against the unedited plan-format.md; a new `test_blocked_duty_sentence_present` pin fails likewise.
  - GREEN: `pytest loom-code/scripts/test_plan_format_progress_fields.py` passes after the .md edit.
- Frozen facts (verbatim; the enum line replaces the current one at plan-format.md:36):
  - Enum line: `Stage: <planning | sdd:wave-N | review:round-N | blocked:user-decision | finishing — updated by the orchestrator at each transition, committed with the nearest ledger or close-out commit>`
  - Duty sentence (own sentence, placed as a sibling explanatory line under the Stage schema entry, NOT spliced into any existing sentence): `blocked:user-decision marks an arc halted awaiting a user ruling: set it when the orchestrator stops mid-arc to wait for a user decision (an open finding, a deferred choice), and on resume flip Stage to the stage the ruling re-enters.`
- External surfaces: none (repo-internal prose + pytest)
- Dependencies: none
- Independent: false
- Brief item covered: "writing-plans/references/plan-format.md:36 enum copy gains the same value PLUS the when-to-set duty text" + "Pin test …test_plan_format_progress_fields.py:49-53 (STAGE_ENUM_LINE, verbatim) updated RED-first"
- Status: done(672f5d3a)
- Gloss: 給 Stage 加上「等使用者裁決」狀態值——schema 檔與它的 pin 測試同步改，先紅後綠

## Task 2 — writing-plans SKILL.md: enum line + new pin assertion
- Description: Add `| blocked:user-decision` to the SKILL.md schema-block enum line (SKILL.md:147) and pin that line with a new assertion in the same test file.
- Module: loom-code/skills/writing-plans (SKILL.md + its pin test)
- Files touched: loom-code/scripts/test_plan_format_progress_fields.py, loom-code/skills/writing-plans/SKILL.md
- Context paths:
  - loom-code/skills/writing-plans/SKILL.md
  - loom-code/scripts/test_wp_extraction_pointers.py
- Acceptance:
  - RED: new `test_skill_md_enum_line_matches` assertion (pinning the extended SKILL.md enum fragment `enum planning | sdd:wave-N | review:round-N | blocked:user-decision |`) fails against the unedited SKILL.md.
  - GREEN: that assertion passes AND `test_wp_extraction_pointers.py::test_word_count_at_most_4047` stays green (current 4039; the edit adds 2 words — margin 8).
- External surfaces: none
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: "writing-plans/SKILL.md:147 enum line gains `| blocked:user-decision` (+2 words against an 8-word margin: cap 4047, current 4039)"
- Status: done(0853a917)
- Gloss: SKILL.md 裡的 enum 副本跟上同一個新值，並補上它一直缺的 pin；字數天花板 4047 不破

## Task 3 — requesting-code-review: round-flip duty sentence + new pin test
- Description: Add ONE self-contained duty sentence to requesting-code-review/SKILL.md making the orchestrator flip the plan's Stage to review:round-N at each round start, pinned by a new test file.
- Module: loom-code/skills/requesting-code-review (SKILL.md + new pin test)
- Files touched: loom-code/scripts/test_review_stage_flip_duty.py, loom-code/skills/requesting-code-review/SKILL.md
- Context paths:
  - loom-code/skills/requesting-code-review/SKILL.md
  - loom-code/scripts/test_rcr_extraction_pointers.py
  - docs/loom/memory/splicing-into-a-pinned-sentence-creates-false-readings.md
- Acceptance:
  - RED: new `loom-code/scripts/test_review_stage_flip_duty.py::test_rcr_carries_stage_flip_duty` (substring pin on the duty sentence below) fails before the edit.
  - GREEN: pin passes AND `test_rcr_extraction_pointers.py::test_word_count_at_most_3900` stays green (current 3832; sentence ≤40 words — margin 68).
- Frozen facts (verbatim duty sentence; placed as its own paragraph in the whole-branch procedure section, near where rounds begin, NOT spliced into an existing sentence): `At the start of each review round (round 1 included), update the plan's Stage: header to review:round-N by hand-edit — plan_card.py has no stage setter — and commit it with that round's verdict or fixes.`
- External surfaces: none
- Dependencies: none
- Independent: false
- Brief item covered: "requesting-code-review/SKILL.md gains ONE self-contained duty sentence: at the start of each whole-branch review round, the orchestrator flips the plan's Stage: to review:round-N (hand-edit…)"
- Status: done(f57d0e63)
- Gloss: review 每一輪開始就把 plan 的 Stage 翻到 round-N——把無主轉換補上 owner，配新 pin 測試

## Task 4 — requesting-docs-review rider: same duty, docs-arm variant
- Description: Add the docs-arm round-flip duty sentence to requesting-docs-review/SKILL.md as its own paragraph, pinned in the Task-3 test file.
- Module: loom-code/skills/requesting-docs-review (SKILL.md + shared pin test)
- Files touched: loom-code/scripts/test_review_stage_flip_duty.py, loom-code/skills/requesting-docs-review/SKILL.md
- Context paths:
  - loom-code/skills/requesting-docs-review/SKILL.md
- Acceptance:
  - RED: new `test_rdr_carries_stage_flip_duty` assertion (substring pin on the sentence below) fails before the edit.
  - GREEN: pin passes AND the full suite `pytest loom-code/scripts/` shows no new failure (brief flags no known rdr word cap; if a hidden cap test goes red, STOP and report — do not trim other prose to fit).
- Frozen facts (verbatim): `Docs-arm rounds carry the same Stage duty: at the start of each round, update the plan's Stage: header to review:round-N by hand-edit and commit it with that round's verdict or fixes.`
- External surfaces: none
- Dependencies: Task 3 completes first
- Independent: false
- Brief item covered: "Rider (mechanical criterion…): the same one-sentence round-flip duty in requesting-docs-review/SKILL.md IF its word cap allows" — cap check at plan time found no rdr word-cap test; rider included with an in-task tripwire.
- Status: blocked
- Gloss: docs 審查臂同樣輪次也要翻 Stage——同一義務的 docs 版，搭車一起修

## Task 5 — version bump + CHANGELOG
- Description: Bump loom-code plugin version 0.64.0 → 0.65.0 and add the CHANGELOG entry describing Tasks 1-4.
- Module: loom-code (manifest + CHANGELOG)
- Files touched: loom-code/.claude-plugin/plugin.json, loom-code/CHANGELOG.md
- Context paths:
  - loom-code/CHANGELOG.md
  - loom-code/.claude-plugin/plugin.json
- Acceptance:
  - RED: diagnostic — `grep '"version": "0.65.0"' loom-code/.claude-plugin/plugin.json` exits non-zero and CHANGELOG has no `0.65.0` heading before the edit.
  - GREEN: both greps hit; full `pytest loom-code/scripts/` green (mechanical-lane self-check); any repo version-sync check (marketplace/frontmatter) still green.
- External surfaces: none
- Dependencies: Tasks 1, 2, 3, 4 complete first
- Independent: false
- Brief item covered: "loom-code version bump + CHANGELOG entry (skill-content PR ⇒ bump is mandatory; marketplace sync per repo convention)"
- Status: done(910d32af)
- Gloss: 版本 0.65.0 與 CHANGELOG——skill 內容改動不 bump 就不會發佈，這是出貨的門票

## Notes
- T4 DESCOPED (2026-08-07, during execution): the plan-time claim "no rdr word-cap test" was WRONG — `loom-code/scripts/test_rdr_extraction_pointers.py::test_word_ceiling` pins requesting-docs-review/SKILL.md at 4430 words and the file sits at 4427 (the pin's own tokenizer); the rider sentence — 31 words by that tokenizer — trips it (4427 + 31 = 4458 > 4430). [Numbers corrected post-T5-review: an earlier version of this note said "exactly at 4430" / "28-word", derived from a different tokenizer.] The brief's pre-recorded rule governs: "Cap blown → skip the rider, note it in the PR body" (brief §Smallest End State item 5). Task-4 working-tree edits reverted (diff archived in session scratchpad t4-descoped-edits.diff); T3's test docstring corrected in the same commit so it no longer prescribes the descoped sibling. Status ledger uses `blocked` (closest grammar value; semantics here = descoped-by-brief-rule, not awaiting unblock). PR body must carry the skip note.
- Amend skip note: T2/T4 Dependencies parenthetical annotations removed post-PASS to satisfy plan_card's dependency grammar — fixing a typo/formatting, assertion unchanged ("shared test file" rationale already lives in Decision Log entry 2), no re-review.
- Change-folder binding: N/A — the caller handed this run the brainstorming brief explicitly (Layer-0 input); the two non-archived docs/loom/ change-folders (2026-07-12-us-sec…, 2026-07-19-8k…) belong to prior investing arcs and are not bound.
- plan_card.py needs NO change: Stage is free text to it (scripts/plan_card.py:318-320).
- Task-file locations follow the repo's flat loom-code/scripts/ test convention; the new test file name test_review_stage_flip_duty.py avoids the reserved basename trap (never `report.md`-like collisions; n/a for .py but noted for artifacts).
- Backlog items lit by this arc (surfaced, deliberately NOT folded in — see brief §Out of Scope): 2026-07-06-anti-copy-acceptance-greps-pass-paraphrase-copies (start: next touch of writing-plans SKILL.md — lit by Task 2), 2026-07-10-change-binding-chain-integration-test (start: next loom-code touch).
- Implementer commit discipline: pathspec-scoped commits only (staged obsidian/ WIP exists in the tree; never `git add -A`), conventional-commits type+scope per repo CI, re-check staged set immediately before each commit.

## Decision Log
- (exec) T4 rider dropped per the brief's cap-blown rule instead of raising the 4430 ceiling — raising is a deliberate scope act the brief did not authorize; continuous mode may not re-scope (crutch-vs-verification line). Revisit only if the user asks for the docs-arm duty later (then: raise ceiling + CHANGELOG note per that test's own docstring).
- (plan) Duty prose lives in plan-format.md, not wp SKILL.md — wp cap margin is 8 words; references are uncapped by design (extraction-pointer architecture).
- (plan) T1→T2 and T3→T4 sequenced only by shared test files; no parallel dispatch — tasks are minutes-scale, parallel implementers on one tree would need index-race guards for no wall-clock gain.
