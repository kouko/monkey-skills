# Plan: bounded auto-third-round + fix-dispatch / finishing-entry hardening

Source brief: docs/loom/specs/2026-08-06-bounded-auto-third-round-and-dispatch-hardening.md
Goal: the docs-review cap runs one mechanically-gated scoped third round
    on its own (reported, once per branch, hard-stop after), fix
    dispatches carry the placement guard, and finishing's conductor
    reads the current skill text before executing
Stage: finishing
Total tasks: 6
Critical-path depth: 4 (≤5)
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-08-06 16:28)
Steps:
  1. 核心條款
  2. 鄰居同步
  3. 版本收束
  4. 行為探針

## Task 1 — rdr Directive 1: bounded auto-third-round
- Status: done(43e13664)
- Description: Amend requesting-docs-review's convergence contract so a
  round-2 NEEDS_REVISION whose structured verdict shows (a) zero
  surviving prior findings (all fix-verified), (b) NEW findings with
  zero 🔴 and at most 2 🟡, and (c) no auto-third-round yet on this
  branch, auto-runs ONE delta-scoped round 3 (scope = the NEW findings'
  fixes only) and reports the auto-round in the terminal rollup; any
  other shape STOPs and surfaces as today; a round-3 verdict other than
  PASS/PASS_WITH_NOTES hard-stops (round 4 never runs without explicit
  user authorization). Reword every cap-stating site inside the same
  file consistently (frontmatter description, :19, :36, :43 — Directive
  1's own cap sentence, :63, :69 — "A round past the cap needs explicit
  user authorization", which directly contradicts the auto-round if
  left, :82, :152, :164, :173). Raise the word ceiling deliberately.
- Gloss: 讓 docs 審查在「前輪全修好、只剩 ≤2 個小新發現」時自動跑一輪
  限定範圍的第三輪並回報，不再停下來等你授權——連續三個 arc 的重複
  授權停頓從此消失，且發散時仍在第三輪硬停。
- Module: loom-code/skills/requesting-docs-review
- Files touched: loom-code/skills/requesting-docs-review/SKILL.md,
  loom-code/scripts/test_requesting_docs_review_skill.py,
  loom-code/scripts/test_rdr_extraction_pointers.py
- Context paths:
  - loom-code/scripts/test_reviewer_r3_conditional.py
  - docs/loom/memory/splicing-into-a-pinned-sentence-creates-false-readings.md
- Acceptance:
  - RED: test_requesting_docs_review_skill.py::test_auto_third_round_mechanical_conditions
    (asserts the three conditions + once-per-branch + report-the-round +
    hard-stop wording present) fails against current text
  - GREEN: new test passes; existing cap pins (:507/:519/:528 family)
    updated to the new wording and pass; test_rdr_extraction_pointers.py
    ceiling raised to (new measured count + margin ≤20) and passes;
    full loom-code/scripts/ suite green
- Dependencies: none
- Independent: true
- Brief item covered: "requesting-docs-review Directive 1 gains a
  bounded auto-third round with purely mechanical conditions"

## Task 2 — finishing: cap pointer + placement guard + entry read duty
- Description: Three edits in finishing-a-development-branch/SKILL.md:
  (1) the Step-3 docs-arm cap-STOP bullet re-routes on rdr's new
  contract by POINTER (names the auto-round existing and that
  finishing surfaces only the shapes rdr still stops on — does not
  copy the conditions); (2) Step 4 gains one sentence: when applying
  review findings to prose contracts, new material goes in its OWN
  sentence or inside the placeholder it governs, never spliced into an
  existing pinned sentence (cite the memory entry by name); (3) the
  conductor paragraph (:14 area) gains one sentence: before executing,
  Read the CURRENT SKILL.md from the installed plugin — never run the
  flow from memory or a compacted summary. Each new sentence is its
  own sentence (self-applying the placement rule).
- Status: done(5acd237e)
- Gloss: 讓收尾流程跟上新規則並堵住兩個洞：修 review 發現前帶著「新材
  料獨立成句」警告（上輪兩個 placement 缺陷的直接預防）；入口強制先讀
  現行 skill 檔，compaction 後照舊版文本漏跑職責的事故不再重演。
- Module: loom-code/skills/finishing-a-development-branch
- Files touched: loom-code/skills/finishing-a-development-branch/SKILL.md,
  loom-code/scripts/test_finishing_docs_arm.py
- Context paths:
  - loom-code/skills/requesting-docs-review/SKILL.md
  - docs/loom/memory/splicing-into-a-pinned-sentence-creates-false-readings.md
- Acceptance:
  - RED: test_finishing_docs_arm.py::test_cap_stop_routes_on_bounded_contract
    + ::test_fix_application_placement_guard +
    ::test_entry_reads_current_skill fail against current text
  - GREEN: all three pass; the existing :146-156 cap pins updated and
    pass; full loom-code/scripts/ suite green
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "finishing-a-development-branch's cap-STOP bullet
  routes on rdr's new contract by POINTER" + "one sentence in finishing
  Step 4" + "Finishing entry duty"

## Task 3 — implementer agent: placement rule
- Status: done(33ca2406)
- Description: Add one rule to loom-code/agents/implementer.md's role
  contract: when a fix task edits prose contracts (skill text, agent
  contracts, schema references), new material goes in its OWN sentence
  or inside the placeholder it governs — never spliced into an existing
  sentence that pins or enumerations depend on; name the memory entry
  splicing-into-a-pinned-sentence-creates-false-readings as the
  incident source. Pin the rule in
  test_implementer_req_tag_guard.py (same file that already pins
  implementer.md content).
- Gloss: 讓每個被派去修東西的 implementer 都帶著「別把新句子插進既有
  pinned 句」的規則出發——presence-pin 看不見的那類缺陷，從派工契約
  層面預防。
- Module: loom-code/agents
- Files touched: loom-code/agents/implementer.md,
  loom-code/scripts/test_implementer_req_tag_guard.py
- Context paths:
  - docs/loom/memory/splicing-into-a-pinned-sentence-creates-false-readings.md
- Acceptance:
  - RED: test_implementer_req_tag_guard.py::test_placement_guard_rule_present
    fails against current implementer.md
  - GREEN: it passes; full loom-code/scripts/ suite green
- Dependencies: none
- Independent: true
- Brief item covered: "one rule in agents/implementer.md's role
  contract"

## Task 4 — neighbor mention sweep (rcr + docs-reviewer agent)
- Description: Reword the two remaining cap mentions to the new
  semantics: requesting-code-review/SKILL.md:90 — "the 2-round
  convergence cap" becomes "the bounded convergence cap (2 rounds + one
  conditional auto-delta round)"; agents/docs-reviewer.md:519 — "2-round
  cap" in the See-also pointer becomes "bounded cap (2 rounds + one
  conditional auto-delta round)". No other file changes;
  design-evidence.md stays historical; SDD/writing-plans/
  continuous-mode caps are different loops and out of population.
- Status: done(e4eeaa75)
- Gloss: 把其他兩處還寫著「2 輪上限」的舊描述改成新語義，避免讀者在
  不同檔案讀到互相矛盾的規則——語義改動的全 plugin 矛盾掃描義務。
- Module: loom-code (two files, one-line each)
- Files touched: loom-code/skills/requesting-code-review/SKILL.md,
  loom-code/agents/docs-reviewer.md
- Context paths:
  - loom-code/skills/requesting-docs-review/SKILL.md
- Acceptance:
  - RED: grep -n "2-round convergence cap"
    loom-code/skills/requesting-code-review/SKILL.md returns :90 AND
    grep -n "2-round cap" loom-code/agents/docs-reviewer.md returns
    :519 (each file's own pre-edit string)
  - GREEN: both old strings absent from their files; the literal
    "conditional auto-delta round" present in both files; the absence
    pins in test_docs_reviewer_agent.py (:231/:247 "round 2 only"
    absent) still pass; full loom-code/scripts/ suite green
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "requesting-code-review :90 and
  agents/docs-reviewer.md :519 one-line rewords"

## Task 5 — version 0.62.0
- Description: Bump loom-code to 0.62.0 in both manifests
  (.claude-plugin/plugin.json + .codex-plugin/plugin.json), add the
  CHANGELOG [0.62.0] entry (bounded auto-third-round + placement guard
  + entry read duty + the deliberate rdr ceiling raise noted), and
  rewrite the shipping-version pin in
  test_docs_review_blocking_class.py:200-226 to 0.62.0 — the full pin
  spans the function name test_plugin_version_and_changelog_at_0_61_0
  (:200), its docstring (:208-209), the plugin.json assert (:219-220),
  AND the CHANGELOG assert (:224-225); all four sites rewrite, so the
  GREEN "CHANGELOG entry present" has a real oracle.
- Status: done(eecf5252)
- Gloss: 版本升到 0.62.0 並讓版本 pin 同步——沒有 bump 的內容改動在
  裝置端 update 時會靜默拿不到。
- Module: loom-code (manifests + CHANGELOG + pin)
- Files touched: loom-code/.claude-plugin/plugin.json,
  loom-code/.codex-plugin/plugin.json, loom-code/CHANGELOG.md,
  loom-code/scripts/test_docs_review_blocking_class.py
- Context paths:
  - loom-code/CHANGELOG.md
- Acceptance:
  - RED: test_docs_review_blocking_class.py shipping pin rewritten to
    0.62.0 fails against the un-bumped manifests
  - GREEN: pin passes after both manifests bump; CHANGELOG entry
    present; full loom-code/scripts/ suite green
- Dependencies: Tasks 1, 2, 3, 4 complete first
- Independent: false
- Brief item covered: "loom-code → 0.62.0 (both manifests + CHANGELOG +
  shipping-version pin rewrite)"

## Task 6 — haiku probes + dogfood report
- Description: Three fresh-context haiku probe legs, written exercises:
  (a) new Directive 1 text + a conditions-met round-2 verdict fixture
  (zero surviving, 2 new 🟡, no prior auto-round) → expected: run ONE
  delta-scoped round 3 and report it; (b) conditions-not-met fixtures
  (3 new 🟡 / one 🔴 / one unverified prior finding) → expected: STOP
  and surface; (c) finishing entry duty — what must the conductor do
  before Step 1 and why. Write the dogfood report to
  docs/loom/dogfood/2026-08-06-bounded-auto-round3-probe.md (Write
  under an alias then mv if the basename is refused).
- Status: done(bb08a8f4)
- Gloss: 用最弱的模型冷讀新條款做三個情境測驗——證明「機械可判」不是
  只有作者讀得懂，弱模型也判得對、不會自簽通過。
- Module: docs/loom/dogfood
- Files touched: docs/loom/dogfood/2026-08-06-bounded-auto-round3-probe.md
- Context paths:
  - loom-code/skills/requesting-docs-review/SKILL.md
  - loom-code/skills/finishing-a-development-branch/SKILL.md
- Acceptance:
  - RED: probe answers diverge from expected behavior (any leg) →
    treat as a wording defect in T1/T2, fix and re-probe
  - GREEN: 3/3 legs CLEAN; report file exists with per-leg verdicts
- Dependencies: Task 5 completes first
- Independent: false
- Brief item covered: "Haiku probes (a)/(b)/(c) + dogfood report"

## Notes

- Kickoff decision (user-ratified in conversation): discriminator is
  count/verdict-shape only — "non-semantic finding" rejected because it
  requires judgment prose (weak models self-certify past it).
- Endpoint named at kickoff (「開跑吧 三件一起收」) → continuous mode,
  push + PR without re-ask; merge stays with the user.
- rdr ceiling raise is a deliberate banked-headroom act, noted in the
  T5 CHANGELOG entry.
- Steps declaration: 4 steps = 核心條款 (T1+T3) / 鄰居同步 (T2+T4) /
  版本收束 (T5) / 行為探針 (T6).

## Decision Log

- (planning) Wave 1 = T1+T3 parallel (disjoint files, no semantic
  dependency: T3 cites the memory entry, not T1's new wording).
