# Plan: loom arc 2 — deletion-first dimension + prune runbook

Source brief: docs/loom/specs/2026-08-07-loom-arc2-deletion-first-dimension.md
Goal: A scored deletion-first dimension on the two code reviewers (rubric rows moved, not copied), a pin test guarding the two hand-authored copies, the E3 prune runbook, and the T2 ride-along fix — no new stations, blocks, or skills.
Stage: finishing
Total tasks: 9
Critical-path depth: 3 (≤5)
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-08-07, round 1)

Steps:
  1. 六個平行任務：rubric 搬移／兩個 reviewer 加維度／SKILL 範例補齊／runbook／T2 搭車修正
  2. pin 測試（等兩個 reviewer 定義落地）
  3. 版本 bump 0.66.0 ＋ CHANGELOG

## Task 1 — move arch-gate YAGNI rows into a deletion-first scoring section
- Description: In the CANONICAL rubric (domain-teams/skills/code-team/rubrics/arch-gate.md), move the YAGNI/Speculative-Generality severity rows (the :54-69 region — speculative-future-problem 🔴, 3x-more-complex 🔴, over-abstraction 🟡, unnecessary-extension-points 🟡) out of the architecture scoring section into a new own-heading section titled for the deletion-first dimension (same file), so the defect class is scored exactly once; architecture keeps structural/boundary/coupling rows. Run `python3 loom-code/scripts/distribute.py` in the same change so the loom-code functional copy updates; `python3 loom-code/scripts/verify-drift.py` must exit 0.
- Module: code-team knowledge layer (canonical + distribute-generated copy, one sync unit — the ROUTE mechanism regenerates the copy from the canonical, so splitting them across tasks would guarantee drift)
- Files touched: domain-teams/skills/code-team/rubrics/arch-gate.md, loom-code/skills/subagent-driven-development/rubrics/arch-gate.md
- Context paths:
  - loom-code/skills/subagent-driven-development/standards/pragmatic-principles.md (§YAGNI the rows cite)
  - loom-code/scripts/distribute.py (ROUTE workflow)
- Acceptance:
  - RED: `grep -n "deletion-first" loom-code/skills/subagent-driven-development/rubrics/arch-gate.md` exits 1 (no section yet).
  - GREEN: that grep exits 0 in BOTH canonical and copy; the moved rows no longer appear under the architecture section (grep the architecture section span for "Speculative" exits 1); `python3 loom-code/scripts/verify-drift.py` exits 0; full suite `python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/ -q` green.
- External surfaces: none — markdown + existing repo scripts.
- Dependencies: none
- Independent: true
- Brief item covered: "Rubric move, not copy: arch-gate.md's YAGNI/Speculative-Generality rows … move to a `deletion-first` scoring section"
- Status: done(28c3eb1a)
- Gloss: 把 YAGNI 細則從 architecture 維度搬進新維度的專屬記分區——同一缺陷只記一次分

## Task 2 — code-quality-reviewer gains the deletion-first dimension
- Description: In loom-code/agents/code-quality-reviewer.md (hand-authored delta sections only — do not touch managed blocks): frontmatter description "7 dimensions"→"8 dimensions" (:3); role line "seven dimensions" (:16) updated; `dimension_scores:` enum (:352) gains the pinned enum line; the Dimensions table (:406-420) gains the pinned definition row (transcribe VERBATIM from plan Notes pin — never re-derive); add a short expanded section pointing at the rubric's new deletion-first scoring section (Task 1's heading) for severity rows.
- Module: loom-code/agents/code-quality-reviewer.md
- Files touched: loom-code/agents/code-quality-reviewer.md
- Context paths:
  - docs/loom/plans/2026-08-07-loom-arc2-deletion-first-dimension.md (## Notes — the pinned definition text)
  - loom-code/agents/code-reviewer.md (sibling shape precedent: D8/D9 expanded sections)
- Acceptance:
  - RED: `grep -c "deletion-first" loom-code/agents/code-quality-reviewer.md` returns 0.
  - GREEN: frontmatter says 8 dimensions; enum + table + expanded section all carry the pin's anchor tokens; `python3 loom-code/scripts/verify-drift.py` exits 0 (managed blocks untouched); full suite green.
- External surfaces: none.
- Dependencies: none
- Independent: true
- Brief item covered: "Dimension `deletion-first` added to code-quality-reviewer (7→8)"
- Status: done(5a29a9f9)
- Gloss: per-task 品質審查多一條「這行可以不存在嗎」的記分維度

## Task 3 — code-reviewer gains the deletion-first dimension
- Description: In loom-code/agents/code-reviewer.md (hand-authored sections only): frontmatter "10 dimensions"→"11 dimensions" (:3); FIX the pre-existing stale role line ":10 '7-dimension scores'" to eleven; `dimension_scores:` enum (:357) gains the pinned enum line; Dimensions table (:414-427) gains the pinned row (VERBATIM from Notes pin); add an expanded section (house shape like §D9) noting the whole-branch angle: speculative machinery that per-task review excused task-by-task can still fail branch-wide (cumulative abstractions with one user each), and pointing at the rubric section.
- Module: loom-code/agents/code-reviewer.md
- Files touched: loom-code/agents/code-reviewer.md
- Context paths:
  - docs/loom/plans/2026-08-07-loom-arc2-deletion-first-dimension.md (## Notes pin)
  - loom-code/agents/code-reviewer.md (existing §D8/§D9 shapes)
- Acceptance:
  - RED: `grep -c "deletion-first" loom-code/agents/code-reviewer.md` returns 0.
  - GREEN: frontmatter 11; stale ":10" phrase gone (`grep -n "7-dimension scores"` exits 1); enum + table + expanded section carry the pin's anchor tokens; verify-drift exit 0; full suite green.
- External surfaces: none.
- Dependencies: none
- Independent: true
- Brief item covered: "and code-reviewer (10→11) … also fixing code-reviewer.md:10's pre-existing stale '7-dimension scores'"
- Status: done(c9946599)
- Gloss: whole-branch 審查同步加維度，順手修掉沉積的「7-dimension」舊句

## Task 4 — requesting-code-review SKILL example block completes its enum
- Description: In loom-code/skills/requesting-code-review/SKILL.md's `dimension_scores:` example block (:121-130), add BOTH `deletion-first:` (new) and `deliberate-simplification:` (pre-existing gap) lines, matching the block's existing formatting; no other prose changes.
- Module: loom-code/skills/requesting-code-review/SKILL.md
- Files touched: loom-code/skills/requesting-code-review/SKILL.md
- Context paths:
  - loom-code/agents/code-reviewer.md (the authoritative enum order)
- Acceptance:
  - RED: `grep -n "deliberate-simplification:" loom-code/skills/requesting-code-review/SKILL.md` exits 1 within the example block (verify by extracting the block).
  - GREEN: both lines present in the block; file stays under the 4,500-word cap (`wc -w` reported in the task report); full suite green (prose-pin tests unaffected).
- External surfaces: none.
- Dependencies: none
- Independent: true
- Brief item covered: "requesting-code-review/SKILL.md `dimension_scores:` example block (:121-130) gains `deletion-first:` AND the already-missing `deliberate-simplification:`"
- Status: done(78921fd1)
- Gloss: 範例區塊補上兩條缺席的維度行，示例與契約一致

## Task 5 — pin test for the two hand-authored dimension copies
- Description: Add scripts/test_deletion_first_dimension_pin.py (repo-root suite, arc-1 token-pin pattern): assert the pinned anchor tokens ("deletion-first", "smaller shape", "≥2 concrete users" — transcribe from Notes pin) appear in BOTH agents' Dimensions tables and both `dimension_scores:` enums carry the `deletion-first:` line; expose check(root) for RED-on-copy; include a permanent mutation-catch test (perturb the NON-baseline file copy, per arc-1's round-3 lesson).
- Module: scripts/ (repo-root QA suite)
- Files touched: scripts/test_deletion_first_dimension_pin.py
- Context paths:
  - scripts/test_router_card_rule_tokens.py (the pattern to mirror, incl. its mutation-catch shape)
  - docs/loom/plans/2026-08-07-loom-arc2-deletion-first-dimension.md (## Notes pin)
- Acceptance:
  - RED: true TDD RED — write the test before implementing check(), NameError/failure shown; then extracted-copy mutation (remove the token from the copy's code-reviewer.md — the non-baseline file) fails naming the file.
  - GREEN: `python3 -m pytest scripts/test_deletion_first_dimension_pin.py -q` exits 0 against the real tree; full suite green.
- External surfaces: none — stdlib + pytest.
- Dependencies: Tasks 2, 3 complete first
- Independent: false
- Brief item covered: "Pin test (repo-root scripts/, arc-1 pattern): the dimension's anchor tokens present in BOTH agent files"
- Status: done(2a0cd0a8)
- Gloss: 兩份手寫維度定義上鎖——改一份忘另一份時 CI 點名

## Task 6 — E3 complexity-prune runbook
- Description: Write docs/loom/references/complexity-prune-runbook.md: when to run (human-invoked; suggested when mechanism growth is felt or ~quarterly), the four-arm read-only audit recipe (core-chain / support-surface / siblings / glue, each returning file:line-grounded findings), the load-bearing do-not-touch discipline (incident-backed mechanisms are exempt from slimming proposals), proposal-critique triage (KEEP/DEFER/DROP with re-triggers), outputs (dated audit doc in docs/loom/audits/ + PARKED/OPEN backlog entries), and a Worked example section pointing at the 2026-08-07 audit + arcs 1-2. State loudly it is proposal-only and NOT a skill (audit E3 caveat).
- Module: docs/loom/references
- Files touched: docs/loom/references/complexity-prune-runbook.md
- Context paths:
  - docs/loom/audits/2026-08-07-family-complexity-audit.md (the recipe's worked instance)
- Acceptance:
  - RED: file does not exist (`test -f` fails).
  - GREEN: file exists with the sections above (grep for "proposal-only", "do-not-touch", "proposal-critique" all exit 0); `python3 scripts/check_loom_memory_integrity.py` still OK (no store impact); living-spec index regen shows expected diff or none.
- External surfaces: none.
- Dependencies: none
- Independent: true
- Brief item covered: "E3 runbook at docs/loom/references/complexity-prune-runbook.md"
- Status: done(149c6b73)
- Gloss: 體檢配方落成 runbook——機制修剪從此有可重複的操作手冊

## Task 7 — ride-along: lockstep mutation test perturbs a non-baseline router
- Description: In scripts/test_brief_clause_lockstep.py's test_check_catches_a_perturbed_router, perturb `ROUTER_FILES[1]` instead of `ROUTER_FILES[0]` (the baseline), so the naming assertion can fail on misattribution (arc-1 round-3 reviewer finding, one-word fix). Verify the docstring claim "naming that router" now holds by the reviewer's own probe: a mutant emitting a wrong file name must FAIL the assertion (demonstrate on an extracted copy, zero residue).
- Module: scripts/ (repo-root QA suite)
- Files touched: scripts/test_brief_clause_lockstep.py
- Context paths:
  - docs/loom/audits/… (not needed; the finding is quoted in this Description)
- Acceptance:
  - RED: `grep -n "ROUTER_FILES\[0\]" scripts/test_brief_clause_lockstep.py` shows the mutation line targeting index 0 (pre-edit state).
  - GREEN: mutation targets index 1; misattribution probe demonstrated; `python3 -m pytest scripts/test_brief_clause_lockstep.py -q` green; full suite green.
- External surfaces: none.
- Dependencies: none
- Independent: true
- Brief item covered: "Ride-along: T2 one-word fix — … perturbs ROUTER_FILES[1] instead of ROUTER_FILES[0]"
- Status: done(fe360503)
- Gloss: arc-1 帶出的一字債清償——命名斷言從此可證偽

## Task 8 — loom-code manifest bump 0.65.2 → 0.66.0
- Description: Bump version in loom-code/.claude-plugin/plugin.json and loom-code/.codex-plugin/plugin.json (minor — the reviewers gain scoring behavior). Single-module justification: the manifest pair is one sync unit (codex-manifest-drift CI byte-checks it). Use scripts/sync_codex_manifests.py if present (verify with its docstring), else edit both identically.
- Module: loom-code plugin manifest pair (one sync unit, see Description)
- Files touched: loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json
- Context paths:
  - .github/workflows/loom-code-ci.yml (version-bump + codex-drift gates)
- Acceptance:
  - RED: `git diff main --name-only | grep -q loom-code` succeeds while both manifests read 0.65.2.
  - GREEN: both read 0.66.0 and agree.
- External surfaces: marketplace versioning (version-gated deploys; repo memory).
- Dependencies: Tasks 2, 3 complete first
- Independent: false
- Brief item covered: "loom-code 0.66.0 (minor — behavior-adding): manifests pair"
- Status: done(22f9d32a)
- Gloss: 版本 bump 0.66.0——維度行為變更隨 minor 版發佈

## Task 9 — CHANGELOG entry + version-pin full rewrite
- Description: Add a 0.66.0 entry to loom-code/CHANGELOG.md (house style): the deletion-first dimension on both code reviewers (definition + anti-over-correction guard), the rubric row move, the pin test, the SKILL example completion, the E3 runbook (repo-level), and the ride-along fix. Rewrite the version-pin test per house convention (rename …_at_0_65_2 → …_at_0_66_0, docstring, both asserts) — RED-first: flip the pin before writing the entry, show the missing-heading failure, then write the entry to GREEN.
- Module: loom-code CHANGELOG + its version-pin test (one release unit — the pin's CHANGELOG assert is satisfied only by this task's entry, splitting them leaves a red intermediate)
- Files touched: loom-code/CHANGELOG.md, loom-code/scripts/test_docs_review_blocking_class.py
- Context paths:
  - loom-code/CHANGELOG.md (0.65.2 entry shape)
- Acceptance:
  - RED: renamed/flipped pin test fails on missing `## [0.66.0]` heading (shown before the entry is written).
  - GREEN: entry present naming the dimension; pin test passes; zero "0_65_2"/"0.65.2" residue in the pin test; full suite green.
- External surfaces: none.
- Dependencies: Task 8 completes first
- Independent: false
- Brief item covered: "CHANGELOG + version-pin test rewrite per house convention"
- Status: done(7d957f55)
- Gloss: CHANGELOG 記錄 0.66.0；版本 pin 整組換版

## Notes

- Endpoint: continuous per user /goal「繼續做下去吧」— recorded at kickoff;
  PR-open terminal stop; never auto-merge; STOP-contract events halt.
- PINNED dimension text (Tasks 2/3/5 transcribe VERBATIM — repo memory:
  pin-shared-wording-in-plan-copies-transcribe-from-pin):
  - Table row:
    `| deletion-first | Every NEW abstraction, config, flag, or extension point in this scope must justify itself: ≥2 concrete users now, an explicit request, or a visible motivation in the task text. A finding REQUIRES naming a smaller shape that does the same job — no finding without a concrete simpler alternative. Well-motivated complexity passes. |`
  - Enum line: `  deletion-first: PASS | PASS_WITH_NOTES | NEEDS_REVISION`
    (AMENDED wave-1 review: angle brackets dropped — both agent files'
    sibling enum lines are bracket-free, and bracketed placeholders risk
    weak-tier literalization; repo memory worked-example-is-prescriptive.)
  - Pin-test anchor tokens: "deletion-first", "smaller shape",
    "≥2 concrete users".
- Kickoff briefing: zero one-way-door decisions (all text edits,
  reversible); dimension name pinned in the brief; no PRINCIPLES.md in
  repo → nothing suppressed by appetite read.

## Decision Log

- 2026-08-07 (wave 1): enum-line pin amended bracket-free (T2 quality 🟡 —
  style collision with both files' sibling lines + weak-model
  literalization precedent). Table-row pin unchanged; the pin test's
  anchor tokens are unaffected.
- 2026-08-07 (wave 1): D10 to gain an operational branch-scope trigger
  (T3 quality 🟡 — D8 defers cross-task consumer-counting to D10, which
  only carried narrative); fix round adds the counting rule.
- Review-weight markers deliberately NOT set: the reviewer-contract edits
  are semantic (Check 16 would reject mechanical), and the whole-branch
  review MUST carry a plugin-wide contradiction sweep arm (repo memory:
  a-semantics-change-needs-a-plugin-wide-contradiction-sweep-arm) — the
  reviewers' own contract text changes meaning here.
- Amendment log: verdict stamped PASS round 1 — stamping only, no re-review (closed-list kind 1).
- Change-folder binding: Layer 0 explicit handoff — input is this brief;
  the two non-archived investing change-folders are unrelated, NOT bound
  (stated loudly per the detection cascade).
