# Plan: loom mechanical dedup arc 1 — drift-guard tests

Source brief: docs/loom/specs/2026-08-07-loom-mechanical-dedup-arc1.md
Goal: Three drift-guard tests + doc corrections + one comment update — zero rendered-prose changes, zero relocations, zero new mechanism types.
Stage: finishing
Total tasks: 9
Critical-path depth: 4 (≤5)
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-08-07, round 3)

Steps:
  1. 三支防漂移測試＋CI 觸發補線＋兩份文件修正（平行波）
  2. session-start 註解更新
  3. loom-code manifest 版本 bump
  4. CHANGELOG 條目

## Task 1 — T1 state-anchor carrier-inventory test
- Description: Add a pytest that greps `state anchor|state-anchor` over `loom-*/` (excluding `loom-code/CHANGELOG.md` and `loom-pipeline/hooks/test-prompts.json`) and asserts the hit set equals the pinned 11-location inventory (10 files; list in brief Evidence/Data) (figure superseded — the shipped pin is 12 hits / 9 files; see Decision Log 2026-08-07). Expose the check as a function taking a root path so RED can run against a mutated temp copy.
- Module: scripts/ (repo-root QA suite)
- Files touched: scripts/test_state_anchor_carrier_inventory.py
- Context paths:
  - docs/loom/specs/2026-08-07-loom-mechanical-dedup-arc1.md (Evidence §Data — carrier list; figures since corrected to 12 hits / 9 files)
  - scripts/backlog_index.py (house style for repo-root scripts)
- Acceptance:
  - RED: run the check function against a temp copy of the tree with one carrier line removed (extracted-copy mutation, zero residue in the real tree) → check reports the missing carrier and pytest assertion fails on that copy.
  - GREEN: `python3 -m pytest scripts/test_state_anchor_carrier_inventory.py -q` exits 0 against the real tree; failure message on mismatch prints the full expected-vs-actual carrier list (the sweep list).
- External surfaces: none — stdlib + pytest only, no new deps.
- Dependencies: none
- Independent: true
- Brief item covered: "T1 (B1): carrier-inventory test — greps `state anchor|state-anchor` over `loom-*/`, asserts the live-carrier list matches the pinned 11-location inventory" (brief figure since corrected — see Decision Log 2026-08-07)
- Status: done(fb9ccfd1)
- Gloss: 把 state-anchor 的 11 個載體位置釘進測試（數字後經修正為 12 hits / 9 files，見 Decision Log 2026-08-07）——語義要改時，測試失敗訊息就是完整掃描清單

## Task 2 — T2 brief-before-asking anchor-sentence lockstep test
- Description: Add a pytest that byte-compares the shared anchor sentence ("≥3 trade-offs, ≥2 implementation paths, or architectural blast radius" + the `dev-workflow:brief-before-asking` directive) across the four design-side router SKILL.md files, tolerating line-wrap differences (compare after whitespace normalization; loom-discovery's copy is word-identical but wrapped differently — brief Evidence §Data). Expose check(root) for RED-on-copy.
- Module: scripts/ (repo-root QA suite)
- Files touched: scripts/test_brief_clause_lockstep.py
- Context paths:
  - loom-discovery/skills/using-loom-discovery/SKILL.md (lines ~59-65)
  - loom-product-principles/skills/using-loom-product-principles/SKILL.md (~:43)
  - loom-interface-design/skills/using-loom-interface-design/SKILL.md (~:41)
  - loom-spec/skills/using-loom-spec/SKILL.md (~:19)
- Acceptance:
  - RED: check function against a temp copy with one router's anchor sentence perturbed (one word changed) → fails naming the diverging file.
  - GREEN: `python3 -m pytest scripts/test_brief_clause_lockstep.py -q` exits 0 against the real tree.
- External surfaces: none — stdlib + pytest only.
- Dependencies: none
- Independent: true
- Brief item covered: "T2 (C2): lockstep test — byte-compares the shared anchor sentence … across the 4 design-side router SKILL.md files"
- Status: done(b9141492)
- Gloss: 四個 router 共享的觸發句上鎖——改一份沒同步另外三份時 CI 直接點名

## Task 3 — T3 router-card rule-token presence test
- Description: Add a pytest asserting, for each of the five load-bearing rules, that its distinctive anchor tokens (e.g. "Brainstorm before implementing" / "tdd-iron-law" / "subagent-driven-development" / "finishing-a-development-branch" / "brief-before-asking") appear in BOTH loom-code/hooks/router-card.md (rules block :9-13) and loom-code/skills/using-loom-code/SKILL.md (rules block :15-21). Byte-equality is explicitly NOT asserted (deliberate compression, session-start:6-11). Expose check(root) for RED-on-copy.
- Module: scripts/ (repo-root QA suite)
- Files touched: scripts/test_router_card_rule_tokens.py
- Context paths:
  - loom-code/hooks/router-card.md
  - loom-code/skills/using-loom-code/SKILL.md
  - loom-code/hooks/session-start (lines 6-11, the deliberate-compression note)
- Acceptance:
  - RED: check function against a temp copy with rule 4's token removed from router-card.md → fails naming the rule and the file missing it.
  - GREEN: `python3 -m pytest scripts/test_router_card_rule_tokens.py -q` exits 0 against the real tree.
- External surfaces: none — stdlib + pytest only.
- Dependencies: none
- Independent: true
- Brief item covered: "T3 (D2): token-presence lockstep — for each of the 5 load-bearing rules, asserts its distinctive anchor tokens appear in BOTH"
- Status: done(e86c0bf4)
- Gloss: 五條家規在卡片與 router 兩邊都要在場——「改了一邊忘另一邊」從此被 CI 抓

## Task 4 — session-start comment points at the new guard
- Description: Update loom-code/hooks/session-start lines 6-11: replace the "kept out of verify-drift.py scope for now" caveat with a note that rule-level sync is guarded by scripts/test_router_card_rule_tokens.py (wording stays a comment; no rendered output changes).
- Module: loom-code/hooks
- Files touched: loom-code/hooks/session-start
- Context paths:
  - loom-code/hooks/session-start
  - scripts/test_router_card_rule_tokens.py (the guard being named)
- Acceptance:
  - RED: `grep -n "kept out of verify-drift" loom-code/hooks/session-start` exits 0 (stale caveat present).
  - GREEN: that grep exits 1; `grep -n "test_router_card_rule_tokens" loom-code/hooks/session-start` exits 0; `bash -n loom-code/hooks/session-start` exits 0.
- External surfaces: none — comment-only edit in a shell script.
- Dependencies: Task 3 completes first
- Independent: false
- Brief item covered: "update session-start:6-11 comment to name the guard"
- Status: done(0270c160)
- Gloss: 把「edit BOTH 靠人記」的註解改成指向新防護

## Task 5 — CI trigger wiring for cross-plugin drift tests
- Description: Add the four design-side router SKILL.md paths and loom-pipeline/hooks/family-relay.md to .github/workflows/loom-code-ci.yml `on.pull_request.paths` (and its push mirror if present), with a fail-open comment in the file's existing style explaining that repo-root drift tests read these files, so edits to them must fire this workflow.
- Module: .github/workflows
- Files touched: .github/workflows/loom-code-ci.yml
- Context paths:
  - .github/workflows/loom-code-ci.yml (existing paths + comment style)
- Acceptance:
  - RED: `grep -c "using-loom-spec/SKILL.md" .github/workflows/loom-code-ci.yml` returns 0.
  - GREEN: all five new paths present; `python3 -c "import yaml,sys; yaml.safe_load(open('.github/workflows/loom-code-ci.yml'))"` exits 0.
- External surfaces: GitHub Actions `paths:` filters gate at workflow-trigger level, never per-job (repo memory gha-paths-filter-gates-at-workflow-level) — this task exists because of that semantic.
- Dependencies: none
- Independent: true
- Brief item covered: Decision — "Where the new tests land decides version bumps … a repo-root location avoids bumps but needs CI wiring"
- Status: done(0d92c47e)
- Gloss: 補 CI 觸發路徑——sibling plugin 改到被鎖檔案時，跑得到根目錄的防漂移測試

## Task 6 — ride-along corrections: audit doc
- Description: In docs/loom/audits/2026-08-07-family-complexity-audit.md, apply the recorded corrections: (a) PR #669 noted debt — :109 drop "behavior-zero" for arc 1, :116 42→50, label the 50-file grep as "44 test files + 6 production scripts", hook count "13 hook files"→"12 tracked hook files (a 13th is a gitignored __pycache__ artifact)"; (b) recon-falsified premises — B1 "7 hand-copied files"→"11 paraphrased locations in 10 files (none byte-identical)" (both figures since superseded by the shipped pin: 12 hits / 9 files), B2 "NOT covered: … tdd-standard.md"→already ROUTE-managed (distribute.py:59-62, verify-drift.py:73-97); (c) Expected-impact table "state-anchor 7→1 files; tdd-standard 2→1"→reshaped drift-guard outcomes.
- Module: docs/loom/audits
- Files touched: docs/loom/audits/2026-08-07-family-complexity-audit.md
- Context paths:
  - docs/loom/specs/2026-08-07-loom-mechanical-dedup-arc1.md (§Problem — the correction list with evidence)
- Acceptance:
  - RED: `grep -n "42 test-pin surface" docs/loom/audits/2026-08-07-family-complexity-audit.md` exits 0 (stale value present; same probe for "behavior-zero, existing machinery, light review lane").
  - GREEN: both stale greps exit 1. Value-fix sweep duty: after edits, grep the file for every changed value's old form (42, 7→1, 2→1, "7 hand-copied", "13 hook files") and derived sentences — zero stale restatements (repo memory: measurement-value changes must sweep all old values).
- External surfaces: none — markdown only.
- Dependencies: none
- Independent: true
- Brief item covered: "Doc corrections (audit doc + execute-keep-lanes entry) per Ride-along"
- Status: done(bd395391)
- Gloss: 審計文件止血——修 PR #669 殘留與被偵察推翻的兩個前提，並全文清掃舊數值

## Task 7 — ride-along corrections: backlog entry + index
- Description: In docs/loom/backlog/2026-08-07-execute-complexity-audit-keep-lanes.md, rewrite the arc-1 item to the reshaped scope (three drift-guard tests + CI wiring, no relocation; B2 already managed), apply the same value sweep as Task 6 to this file (50-file labelling, near-verbatim wording), then run `python3 scripts/backlog_index.py --validate` and `--write` and stage the regenerated docs/loom/BACKLOG.md if it changed. Single-module justification: docs/loom/BACKLOG.md is mechanically regenerated from the backlog/ store by backlog_index.py, so hand-edit + regen is one sync unit, not two modules.
- Module: docs/loom backlog store (entry + generated index, one sync unit — see Description)
- Files touched: docs/loom/backlog/2026-08-07-execute-complexity-audit-keep-lanes.md, docs/loom/BACKLOG.md
- Context paths:
  - docs/loom/specs/2026-08-07-loom-mechanical-dedup-arc1.md (§Problem + §Smallest End State — the reshaped scope)
- Acceptance:
  - RED: `grep -n "existing machinery throughout" docs/loom/backlog/2026-08-07-execute-complexity-audit-keep-lanes.md` exits 0 (pre-reshape arc-1 wording present).
  - GREEN: entry describes the reshaped arc 1 (drift-guard tests, no relocation); `python3 scripts/backlog_index.py --validate` and `--check` exit 0; value sweep on this file zero stale restatements.
- External surfaces: none — markdown + existing validator script.
- Dependencies: none
- Independent: true
- Brief item covered: "update the execute-keep-lanes backlog entry to the reshaped arc-1 scope"
- Status: done(0a9fecf8)
- Gloss: backlog 執行計畫同步改形後的 arc 1 範圍，索引重生成

## Task 8 — loom-code manifest version bump
- Description: Bump loom-code 0.65.1 → 0.65.2 in loom-code/.claude-plugin/plugin.json and loom-code/.codex-plugin/plugin.json. Single-module justification: the two manifests are one sync unit — CI's codex-manifest-drift gate (loom-code-ci) byte-checks them as a pair, so splitting them across tasks would guarantee an inconsistent intermediate state.
- Module: loom-code plugin manifest pair (one sync unit, see Description)
- Files touched: loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json
- Context paths:
  - .github/workflows/loom-code-ci.yml (the version-bump + codex-manifest-drift gates this satisfies)
- Acceptance:
  - RED: `git diff main --name-only | grep -q loom-code` succeeds while both manifests still read 0.65.1 (the CI version-bump gate's failing condition, checked locally).
  - GREEN: both manifests read 0.65.2 and agree on version.
- External surfaces: marketplace versioning — plugin update is version-gated (repo memory: skill-content PR requires bump, else deploy is a silent no-op).
- Dependencies: Task 4 completes first
- Independent: false
- Brief item covered: Decision — "tests inside a plugin's scripts/ imply that plugin's patch bump" (the session-start edit is the bump trigger here)
- Status: done(86890509)
- Gloss: 版本 bump——讓裝置端 plugin update 拿得到這次的 hooks 註解變更

## Task 9 — loom-code CHANGELOG entry
- Description: Add a 0.65.2 entry to loom-code/CHANGELOG.md describing the session-start comment update and noting the three repo-root drift guards + CI trigger wiring that ride this release.
- Module: loom-code/CHANGELOG.md
- Files touched: loom-code/CHANGELOG.md
- Context paths:
  - loom-code/CHANGELOG.md (entry style)
- Acceptance:
  - RED: `grep -n "0.65.2" loom-code/CHANGELOG.md` exits 1 (no entry yet).
  - GREEN: that grep exits 0 and the entry names the session-start comment change.
- External surfaces: none — markdown only.
- Dependencies: Task 8 completes first
- Independent: false
- Brief item covered: Decision — "tests inside a plugin's scripts/ imply that plugin's patch bump" (release notes for that bump)
- Status: done(56854bbc)
- Gloss: CHANGELOG 記錄 0.65.2 的內容

## Notes

- Change-folder binding: two non-archived change-folders exist
  (docs/loom/2026-07-12-us-sec-primary-source-layer,
  docs/loom/2026-07-19-8k-prose-kpi-intake) but this plan's input is the
  explicitly handed, user-signed brief (Layer 0 — explicit handoff wins);
  both folders belong to unrelated investing work and are NOT bound. Stated
  loudly per the detection cascade's reporting discipline.
- Endpoint named: no → human-pumped (recorded at router entry).
- Test placement decision (brief Open Question, resolved with CI evidence):
  repo-root scripts/ — loom-code-ci already runs
  `python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/` (the
  pytest step in loom-code-ci.yml — this branch moved its line number), so
  root tests execute today; Task 5 closes the cross-plugin trigger gap. No
  design-side plugin files change → no design-side bumps; loom-code bumps
  only for Task 4's hooks edit.
- RED discipline for guard tests (Tasks 1-3): mutation runs against an
  extracted temp copy only, zero residue in the real tree (house pattern;
  repo memory: mutation/RED limited to extracted copies).
- Amendment log: header verdict stamped PASS (2026-08-07, round 3) —
  stamping the verdict, no re-review (closed-list kind 1).
- Kickoff decision: T1 inventory pin granularity → pin a file→hit-count
  map (10 files, 11 hits total) (measured at ship: 9 files, 12 hits — see
  Decision Log), NOT file:line pairs — line numbers churn on unrelated
  edits; a count change in any file is the drift signal.
- Kickoff decision: T2 comparison normalization → extract the sentence by
  anchoring on the byte-stable fragment "≥3 trade-offs", collapse all
  whitespace runs to single spaces, then require the 4 normalized
  sentences byte-identical.
- Kickoff decision: T3 token set → rule 1 "Brainstorm before
  implementing", rule 2 "tdd-iron-law", rule 3
  "subagent-driven-development", rule 4 "finishing-a-development-branch",
  rule 5 "Research before asking"; each must appear in BOTH files' rules
  blocks. (AMENDED during wave 1: the original rule-5 token
  "brief-before-asking" exists only in router-card.md — using-loom-code
  SKILL.md's rule 5 never names that skill; the rule TITLE "Research
  before asking" is verbatim in both blocks. Verified by T3 implementer
  NEEDS_CONTEXT round 1.)

## Decision Log

- 2026-08-07 (wave 1): T3 rule-5 anchor token corrected
  brief-before-asking → "Research before asking" — task-scoped fact,
  resolved by orchestrator per NEEDS_CONTEXT triage; no user ask
  (two-way door, no product consequence).
- 2026-08-07 (wave 1): T1 live re-derivation measured the state-anchor
  inventory at 12 hits across 9 files (pattern + exclusions stated
  in-test), superseding the recon/brief figure "11 locations / 10 files";
  the test pin is the living source of truth — downstream prose (audit
  doc, backlog entry) anchors to the pin in the wave-1 fix round rather
  than restating hand counts.
- Kickoff briefing: zero one-way-door decisions found (all tasks additive
  tests/docs/comment — two-way doors); no PRINCIPLES.md in this repo →
  nothing suppressed by appetite read.
- 2026-08-07 (close-out): T2's acceptance was completed by fix commit
  f9d2f7c6 (anchor-uniqueness guard) — ledger's done(b9141492) records the
  initial commit only.
