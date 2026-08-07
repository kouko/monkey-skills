# Plan: loom arc 4a — prose slims A2 + A3 (A1 deferred to post-#674)

Source brief: docs/loom/specs/2026-08-07-loom-arc4-prose-slim.md
Goal: requesting-docs-review's convergence contract moves to a reference (4,428 → ~3,330 w) with every pin keeping a carrier, writing-plans' wrong-bind paragraph becomes one line, the audit's A-lane figures get corrected, and loom-code ships 0.67.0 — semantics everywhere byte-preserved.
Stage: finishing
Total tasks: 4
Critical-path depth: 2 (≤5)
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-08-07, round 2)

Steps:
  1. A2 抽取＋A3 降級＋審計數字修正（平行波）
  2. 版本 bump 0.67.0＋CHANGELOG

## Task 1 — A2: convergence contract extracts to a reference
- Description: Move requesting-docs-review/SKILL.md's convergence block (:43-84, 1,446 w — the four binding Directives) to a NEW file loom-code/skills/requesting-docs-review/references/convergence-contract.md (verbatim body; add only a two-line header naming it the binding contract loaded per round). Inline replacement: the imperative pointer ("Read references/convergence-contract.md before running any round — the four directives there are binding") + a compact per-directive one-line summary + the existing "What to hand the user" decision surface stays where it is. RULE SEMANTICS BYTE-PRESERVED — this is a move. Then migrate every pin whose phrase left the SKILL body: test_requesting_docs_review_skill.py pins at :534/:551/:571-576 (bounded cap / once-per-branch / auto-third-round), :607-609 (delta-scoped), :817-837 (round-N handoff / retained), :551-557 (oscillation) and test_docs_reviewer_agent.py:279 (delta-scoped) — each pin re-anchors to the reference file (or the surviving inline summary when that is what it guarded), preserving each pin's PURPOSE; run each adjusted test RED-first against a copy missing the target phrase where the file's own convention demands it. Extraction-severing duty: note in the report any rule separated from a rule it cross-references (feeds the review-stage cold-read).
- Module: requesting-docs-review extraction unit (SKILL.md + its new reference + the pins that carry its phrases — an atomic move; splitting leaves red pins mid-plan)
- Files touched: loom-code/skills/requesting-docs-review/SKILL.md, loom-code/skills/requesting-docs-review/references/convergence-contract.md, loom-code/scripts/test_requesting_docs_review_skill.py, loom-code/scripts/test_docs_reviewer_agent.py
- Context paths:
  - docs/loom/specs/2026-08-07-loom-arc4-prose-slim.md (§Smallest End State 1 + Evidence)
  - loom-code/skills/requesting-code-review/SKILL.md (line 18 — the imperative pointer precedent)
- Acceptance:
  - RED: `grep -c "CONVERGENCE CONTRACT" loom-code/skills/requesting-docs-review/references/convergence-contract.md` fails (file absent).
  - GREEN: reference exists carrying the four directives verbatim; SKILL.md `wc -w` ≤ 3,450; pointer present in imperative form; `python3 -m pytest loom-code/scripts/test_requesting_docs_review_skill.py loom-code/scripts/test_docs_reviewer_agent.py -q` green; full suite `python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/ -q` green; report lists every pin moved and its new carrier.
- External surfaces: none — markdown + pytest.
- Dependencies: none
- Independent: true
- Brief item covered: "A2: requesting-docs-review 4,428 → ~3,330 w … moves to references/convergence-contract.md" — also anchors brief item 4's review-stage duty ("Weak-model cold-read per extraction … A2 mandatory"): the cold-read runs as a probe leg at whole-branch review, against this task's output
- Status: done(c2ef0938)
- Gloss: 收斂契約整段搬進 reference——主文回到可編輯的體量，每個 pin 都有新家

## Task 2 — A3: wrong-bind protocol downgrades to one line
- Description: Replace writing-plans/SKILL.md's wrong-bind reversal paragraph (:206, 44 w) with one line: "**Wrong-bind reversal trigger.** A confirmed wrong-bind incident downgrades layer (i) to confirm-before-use — restore the full protocol from git history." Verify test_writing_plans_change_binding.py:103-112's pins ("wrong-bind"/"confirm-before-use") survive in the new line (they should — confirm by running; if a pin needs its window adjusted, adjust the window only, never the pinned phrase).
- Module: loom-code/skills/writing-plans/SKILL.md
- Files touched: loom-code/skills/writing-plans/SKILL.md, loom-code/scripts/test_writing_plans_change_binding.py
- Context paths:
  - docs/loom/specs/2026-08-07-loom-arc4-prose-slim.md (§Smallest End State 3)
- Acceptance:
  - RED: `grep -c "layer (i) downgrades from opportunistic-auto" loom-code/skills/writing-plans/SKILL.md` exits 0 (old protocol wording present — verify the actual phrase by Reading :206 first; re-anchor the grep to what is really there).
  - GREEN: paragraph replaced by the one-liner; `python3 -m pytest loom-code/scripts/test_writing_plans_change_binding.py -q` green; full suite green; SKILL.md wc -w reported.
- External surfaces: none.
- Dependencies: none
- Independent: true
- Brief item covered: "A3: writing-plans' wrong-bind reversal paragraph (:206, 44 w) → one line"
- Status: done(b310b5df)
- Gloss: 無實證的假設性協議降為一行——需要時 git 史還原

## Task 3 — audit-doc A-lane figure corrections
- Description: In docs/loom/audits/2026-08-07-family-complexity-audit.md, correct the A-lane figures per recon: A2 block "1,424 w" → "1,446 w (:43-84)"; A3 "315 w" → "44 w (the audit's span included neighboring cascade text — population note)"; adjust any derived sentence (the ~-1,900 w impact arithmetic → recompute honestly with A1 pending: state A2+A3 land ~-1,150 w now, A1's 400-600 w follows post-#674). Value-sweep the file for stale restatements of the changed numbers.
- Module: docs/loom/audits
- Files touched: docs/loom/audits/2026-08-07-family-complexity-audit.md
- Context paths:
  - docs/loom/specs/2026-08-07-loom-arc4-prose-slim.md (§Problem — the recon corrections)
- Acceptance:
  - RED: `grep -n "1,424 w" docs/loom/audits/2026-08-07-family-complexity-audit.md` exits 0.
  - GREEN: corrected figures present; sweep greps ("1,424", "315 w", "-1,900") show zero stale restatements or an anchored revision basis; backlog validators exit 0 (no backlog file touched — confirm).
- External surfaces: none.
- Dependencies: none
- Independent: true
- Brief item covered: "Audit-doc ride-along: correct the A-lane figures"
- Status: done(509c7b7d)
- Gloss: 審計數字第三次校準——量測母體教訓繼續執行

## Task 4 — loom-code 0.67.0 + CHANGELOG + version pin
- Description: Bump loom-code 0.66.1 → 0.67.0 via `python3 scripts/sync_codex_manifests.py loom-code` (--check exit 0); CHANGELOG 0.67.0 entry (house style: the A2 extraction with pin migration, the A3 downgrade, A1 deferred to the follow-up); version-pin test rewrite _0_66_1 → _0_67_0 RED-first (flip pin, show missing heading, write entry, GREEN).
- Module: loom-code release unit (manifest pair + CHANGELOG + version pin, one version)
- Files touched: loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json, loom-code/CHANGELOG.md, loom-code/scripts/test_docs_review_blocking_class.py
- Context paths:
  - loom-code/CHANGELOG.md (0.66.1 entry shape)
- Acceptance:
  - RED: version-pin test fails on missing `## [0.67.0]` heading after the flip (shown pre-entry).
  - GREEN: both manifests 0.67.0 in sync; CHANGELOG entry present naming the deferral; zero 0.66.1/0_66_1 residue in the pin test; full suite green.
- External surfaces: marketplace versioning (bump-or-silent-no-op).
- Dependencies: Tasks 1, 2 complete first
- Independent: false
- Brief item covered: "loom-code minor bump (three core SKILL.md bodies change — two in this split) + CHANGELOG + version-pin rewrite" — and carries brief item 2 (A1: finishing's five ONCE-bullets collapse) as a RECORDED DEFERRAL per the brief §Decision's continuation-pressure split clause: this task's GREEN requires the CHANGELOG entry to name A1's deferral to the post-#674 follow-up
- Status: done(b8da774b)
- Gloss: 0.67.0——瘦身弧前半場隨 minor 版出貨

## Notes

- Endpoint: continuous per /goal「繼續做下去吧」; PR-open terminal; never
  auto-merge. SPLIT EXECUTION recorded: this plan ships A2+A3 (no overlap
  with PR #674); A1 (finishing collapse) is deferred to a follow-up brief
  after #674 merges — its file is arc-3-modified. The brief's Decision
  section pre-authorizes this split under continuation pressure.
- Review plan: whole-branch review carries (a) the standard code+docs arms
  and (b) a HAIKU COLD-READ probe leg on the slimmed requesting-docs-review
  (E-1 precedent; extraction-severing memory makes it mandatory): the probe
  executes the skill blind on one real docs-review round-1 scenario and
  must reach the reference file's directives (misread = wording fix, never
  reader-blame).
- Kickoff briefing: zero one-way-door decisions (moves and downgrades, all
  reversible from git history); no PRINCIPLES.md → nothing suppressed.
- Amendment log: verdict stamped PASS round 2 — stamping only (closed-list kind 1).
- Decision Log: 2026-08-07 (wave 1) — T2's one-liner amended beyond the
  plan's verbatim text to restore the surfacing duty ("is surfaced
  immediately and") after the quality reviewer showed the drop was a real
  semantic loss the plan itself had authored; pins unaffected.
- Change-folder binding: Layer 0 explicit handoff — input is the brief; the
  two non-archived investing change-folders remain unrelated, NOT bound
  (stated loudly).
- Wave discipline: Tasks 1-3 parallel (disjoint files); one commit per Bash
  block while agents live (parallel-wave-commit-discipline).
