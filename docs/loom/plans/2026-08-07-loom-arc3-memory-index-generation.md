# Plan: loom arc 3 — memory index generation (D1)

Source brief: docs/loom/specs/2026-08-07-loom-arc3-memory-index-generation.md
Goal: The memory store's ## Index becomes generated — --write/--check join the existing validator, the six hand-append teaching surfaces flip to the regen procedure, and no new script, CI gate, or format change ships.
Stage: finishing
Total tasks: 6
Critical-path depth: 2 (≤5)
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-08-07, round 2)

Steps:
  1. 驗證器擴充 --write/--check（TDD）
  2. 五個教學面翻新＋索引首次生成（平行波）

## Task 1 — validator gains --write and --check (backlog trio)
- Description: Extend scripts/check_loom_memory_integrity.py with `--write` (regenerate the `## Index` section from entry frontmatter, sorted by entry name, deterministic and idempotent; splice between the `## Index` heading and EOF/next `## `) and `--check` (rebuild in memory, diff against the committed section, nonzero on drift), mirroring scripts/backlog_index.py's trio semantics. The five validate invariants and default validate mode stay byte-untouched (hook/CI callers unaffected). Extend scripts/test_check_loom_memory_integrity.py RED-first: (a) --check exits nonzero against a tmp store copy whose index drifts; (b) --write then --check exits 0 (idempotence); (c) --write output for a crafted 2-entry tmp store matches the expected lines exactly; existing validate tests untouched and green.
- Module: scripts/ (validator + its test, one TDD unit)
- Files touched: scripts/check_loom_memory_integrity.py, scripts/test_check_loom_memory_integrity.py
- Context paths:
  - scripts/backlog_index.py (trio precedent: --validate/--write/--check semantics)
  - docs/loom/memory/README.md (the ## Index shape at L132+)
- Acceptance:
  - RED: the three new tests fail before the flags exist (argparse error / missing behavior — shown).
  - GREEN: `python3 -m pytest scripts/test_check_loom_memory_integrity.py -q` all green; `python3 scripts/check_loom_memory_integrity.py` (validate, no flags) behavior byte-identical on the real store (exit 0 today); full suite `python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/ -q` green.
- External surfaces: none — stdlib + pytest.
- Dependencies: none
- Independent: true
- Brief item covered: "scripts/check_loom_memory_integrity.py gains `--write` … and `--check` … the five validate invariants stay byte-untouched" — and enables brief item 8 ("Review carries a plugin-wide contradiction-sweep arm for residual hand-append teaching"): the pinned command this task ships is the single grep key that sweep arm uses; the sweep itself is review conduct executed at the whole-branch stage, mandated here for traceability
- Status: done(ad6bfe06)
- Gloss: 驗證器學會生成與比對——backlog 三模式先例照抄，不開新腳本

## Task 2 — charter prose flip + first index generation
- Description: In docs/loom/memory/README.md: (a) L90-91 and L134-137 "copied byte-identical" wording flips from hand-copy instruction to generation-invariant statement (the index IS generated from frontmatter; the validator still checks the equality independently); (b) replace the L109-131 manual-sweep block with the three-command regen/check procedure (transcribe the PINNED command from ## Notes verbatim); (c) run `--write` ONCE to regenerate the committed index. Expected: content equal to the hand index modulo canonical sort order/whitespace — diff the before/after index lines as SETS (sort both, diff) and report: a set-level difference is a caught hand-maintenance bug, list it verbatim, do not silently absorb it.
- Module: docs/loom/memory/README.md (prose + generated section, one file)
- Files touched: docs/loom/memory/README.md
- Context paths:
  - docs/loom/specs/2026-08-07-loom-arc3-memory-index-generation.md (Evidence — the exact lines)
- Acceptance:
  - RED: `grep -n "How the list below was built" docs/loom/memory/README.md` exits 0 (manual-sweep block present pre-edit).
  - GREEN: that grep exits 1; the pinned regen command present; `python3 scripts/check_loom_memory_integrity.py` exit 0 AND `--check` exit 0; set-level index diff reported; hook fires clean on the edit.
- External surfaces: none.
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: "One `--write` run regenerates the committed index … Charter … L90-91 + L134-137 … L109-131"
- Status: done(5c32d61a)
- Gloss: 憲章改口＋索引首次機器生成——8,340 字的手工鏡像退役

## Task 3 — hook remediation text
- Description: In .claude/hooks/check-memory-store-integrity.sh, replace the hand-append remediation paragraph (~:98-104 — "give every entry one line … copied byte-identical …") with the PINNED regen command + "then re-run the check"; keep the hook's firing conditions, checker invocation, and all other text byte-untouched. `bash -n` clean.
- Module: .claude/hooks/check-memory-store-integrity.sh
- Files touched: .claude/hooks/check-memory-store-integrity.sh
- Context paths:
  - docs/loom/plans/2026-08-07-loom-arc3-memory-index-generation.md (## Notes pin)
- Acceptance:
  - RED: `grep -n "give every entry one line" .claude/hooks/check-memory-store-integrity.sh` exits 0.
  - GREEN: exits 1; pinned command present; `bash -n` exit 0; full suite green (a hook-message pin test may exist — grep scripts/ for the old phrase; if a test pins it, update that pin in-scope and report).
- External surfaces: none.
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "Hook … remediation text (:98-104) → run … --write"
- Status: done(f3914603)
- Gloss: hook 的補救指引從「手抄一行」變「跑生成器」

## Task 4 — loom-memory skill procedure + loom-pipeline 0.15.0
- Description: In loom-pipeline/skills/loom-memory/SKILL.md, record steps 4-5 (:65-73) and prune's index duties (:116-124) flip from append/hand-update to the PINNED regen command + validator re-run (procedure text is the skill's own — SSOT pointer discipline untouched); bump loom-pipeline 0.14.0 → 0.15.0 (manifest pair via the sync script) + CHANGELOG.md entry. Single release unit: skill text + manifests + CHANGELOG ship one version.
- Module: loom-pipeline release unit (skill + manifest pair + CHANGELOG, one version)
- Files touched: loom-pipeline/skills/loom-memory/SKILL.md, loom-pipeline/.claude-plugin/plugin.json, loom-pipeline/.codex-plugin/plugin.json, loom-pipeline/CHANGELOG.md
- Context paths:
  - docs/loom/plans/2026-08-07-loom-arc3-memory-index-generation.md (## Notes pin)
  - loom-pipeline/CHANGELOG.md (entry style)
- Acceptance:
  - RED: `grep -n "Append the index line" loom-pipeline/skills/loom-memory/SKILL.md` exits 0.
  - GREEN: exits 1; pinned command present in record and prune; both manifests 0.15.0 in sync (`python3 scripts/sync_codex_manifests.py --check loom-pipeline` exit 0); CHANGELOG entry present; `python3 -m pytest loom-pipeline/scripts/ -q` green.
- External surfaces: marketplace versioning (bump-or-silent-no-op).
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "loom-pipeline/skills/loom-memory/SKILL.md record steps 4-5 and prune's index duties … loom-pipeline version bump + CHANGELOG"
- Status: done(e701a07e)
- Gloss: 記憶 skill 的 record／prune 程序改用生成器；loom-pipeline 0.15.0

## Task 5 — finishing Step-8 bullet + loom-code 0.66.1
- Description: In loom-code/skills/finishing-a-development-branch/SKILL.md's memory-store integrity bullet (:233-249), the remediation wording ("fix the store, re-run until exit 0") flips to the PINNED regen command + re-run; the quoted index-line contract sentence updates to the generated-index reality. Check loom-code/scripts/test_finishing_memory_store_integrity.py for pins on the old wording — update any falsified pin string in-scope (that test's purpose survives; only wording pins move). Bump loom-code 0.66.0 → 0.66.1 (manifest pair) + CHANGELOG entry + version-pin test rewrite to _0_66_1 (house convention, RED-first on the missing heading).
- Module: loom-code release unit (skill bullet + its pin test + manifest pair + CHANGELOG + version pin, one version)
- Files touched: loom-code/skills/finishing-a-development-branch/SKILL.md, loom-code/scripts/test_finishing_memory_store_integrity.py, loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json, loom-code/CHANGELOG.md, loom-code/scripts/test_docs_review_blocking_class.py
- Context paths:
  - docs/loom/plans/2026-08-07-loom-arc3-memory-index-generation.md (## Notes pin)
  - loom-code/CHANGELOG.md (entry style)
- Acceptance:
  - RED: `grep -n "fix the store, re-run until exit 0" loom-code/skills/finishing-a-development-branch/SKILL.md` exits 0; version-pin test fails on missing `## [0.66.1]` heading after the flip (shown before the entry is written).
  - GREEN: bullet carries the pinned command; both manifests 0.66.1 in sync; CHANGELOG entry present; zero 0.66.0/0_66_0 residue in the version-pin test; full suite `python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/ -q` green.
- External surfaces: marketplace versioning.
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "finishing-a-development-branch SKILL.md Step 8 memory-store bullet … loom-code 0.66.1 patch bump + CHANGELOG + version-pin rewrite"
- Status: done(aa372671)
- Gloss: finishing 的補救指引同步；loom-code 0.66.1

## Task 6 — AGENTS.md checker description
- Description: Update AGENTS.md:112-117 (the checker's description) to the trio (validate default / --write regenerates / --check diffs), transcribing the PINNED command for the write form; no other AGENTS.md content changes.
- Module: AGENTS.md
- Files touched: AGENTS.md
- Context paths:
  - docs/loom/plans/2026-08-07-loom-arc3-memory-index-generation.md (## Notes pin)
- Acceptance:
  - RED: `grep -n "\-\-write" AGENTS.md` exits 1 in the checker's section (verify by extracting the section).
  - GREEN: trio described; pinned command present; no other sections in the diff.
- External surfaces: none — AGENTS.md is the Codex-side instruction mirror (repo-level, no plugin).
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "AGENTS.md:112-117 checker description → the trio"
- Status: done(715f83b4)
- Gloss: Codex 側說明同步三模式

## Notes

- Endpoint: continuous per /goal「繼續做下去吧」; PR-open terminal; never
  auto-merge; STOP-contract events halt.
- PINNED regen command (Tasks 2/3/4/5/6 transcribe VERBATIM):
  `python3 scripts/check_loom_memory_integrity.py --write`
- Kickoff briefing: zero one-way-door decisions — the trio shape, the
  no-new-CI call, and the sorted canonical order are all two-way doors
  recorded in the brief; no PRINCIPLES.md → nothing suppressed.
- Amendment log: verdict stamped PASS round 2 — stamping only (closed-list kind 1).
- Amendment log: Task 5's RED grep target
  ("fix the store, re-run until exit 0") was unsatisfiable as a single
  `grep -n` line — the phrase is hard-wrapped across lines in
  loom-code/skills/finishing-a-development-branch/SKILL.md's source;
  the implementer verified RED/GREEN with a multi-line probe instead.
  Recorded here so no later reviewer enforces the unsatisfiable
  single-line criterion.
- Change-folder binding: input is this brief (Layer 0 explicit handoff);
  the two non-archived investing change-folders remain unrelated, NOT
  bound — stated loudly.
- Review plan: whole-branch review carries the plugin-wide
  contradiction-sweep arm (semantics change: hand-append → generated) per
  repo memory; Tasks 2-6 all transcribe the pinned command so the sweep
  can grep one string.
- Wave discipline: Tasks 3-6 (Independent: true, disjoint files) run
  parallel after Task 1; Task 2 (Independent: false — prose edits and the
  generated-section regen share one file) dispatches in the same wave but
  under the sequential floor; one commit per Bash block while agents are
  live (parallel-wave-commit-discipline).
- Review-weight deliberately NOT declared on Task 2: its single file
  contains a GENERATED section (the regenerated ## Index), and the prose
  substitution's eligibility test excludes generated/sync artifacts —
  fail-closed to the full triad.
