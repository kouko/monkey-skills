# Plan: dispatch-efficiency trio

Source brief: docs/loom/specs/2026-08-06-dispatch-efficiency-trio.md
Goal: dispatch packets carry verified maps with string anchors,
    implementers stop re-running the full suite inside the inner loop,
    and eligible plans declare their review lanes — three measured
    latency levers legislated, the unproven fourth parked with its data
Stage: finishing
Total tasks: 5
Critical-path depth: 2 (≤5)
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-08-06 21:32)
Steps:
  1. 三面接線
  2. 收束與驗證

## Task 1 — packet-context discipline (dispatch-hygiene + SDD pointer)
- Status: done(73e9bd72)
- Description: Add a new `## Dispatch-packet context` section to
  loom-code/skills/subagent-driven-development/references/dispatch-hygiene-notes.md
  carrying the brief's four rules, each its own sentence: (a) site
  inventories + exact target strings ride the packet, anchored by
  verbatim string or stable heading — never by line number alone;
  (b) every fact in a packet carries its source — the file the
  orchestrator read or the command it ran; a statement without a named
  source is a guess and must be labeled as one (action-type
  formulation: the checkable surface feature is the presence of a
  provenance marker, never the agent's self-assessment). Packet
  provenance is deliberately open-form — file or command named
  inline — and does NOT govern plan-format §Reuse-adequacy blocks,
  whose closed three-marker vocabulary stays authoritative there;
  the section must state this distinction in its own sentence. (c) ≥3 downstream consumers → locate arm first; below that
  use knowledge in hand, never Read files into the main conversation
  just to quote them; a map serving many workers or exceeding ~10
  lines may live in a FILE the locate arm writes — packets then carry
  only the path, and the map costs the main conversation nothing but
  that path; (d) reviewer packets carry claims-to-verify,
  never conclusions-to-adopt. Add ONE pointer sentence in SDD
  SKILL.md's dispatch area referencing the section (ceiling 4015 —
  measure post-edit; if over, deliberate raise noted for T4's
  CHANGELOG). Preserve the pinned sections the file already carries
  (§Capacity-error recovery, §Worktree-isolated reviewer dispatch,
  §Environment hygiene — their pins must stay green).
- Gloss: 讓派工包從「路徑加運氣」升級成「驗證過的地圖」——站點清單
  與目標字串隨包、行號改用字串錨定（本 session 兩次行號腐爛的直接
  預防）、reviewer 的包永遠只帶待驗宣稱，省掉 worker 每次 5-10 輪的
  自行探索。
- Module: loom-code/skills/subagent-driven-development
- Files touched: loom-code/skills/subagent-driven-development/references/dispatch-hygiene-notes.md,
  loom-code/skills/subagent-driven-development/SKILL.md,
  loom-code/scripts/test_sdd_extraction_pointers.py
- Context paths:
  - docs/loom/specs/2026-08-06-dispatch-efficiency-trio.md
  - loom-code/agents/implementer.md
- Acceptance:
  - RED: test_sdd_extraction_pointers.py::test_dispatch_packet_context_section
    (asserts the four rules' load-bearing phrases in the notes file +
    the pointer sentence in SKILL.md) fails against current text
  - GREEN: it passes; existing dispatch-hygiene pins
    (test_rcr_capacity_pointer.py:23-26, test_dispatch_hygiene_worktree_section.py:21,
    and the §Environment hygiene pins at test_sdd_extraction_pointers.py:176-230)
    stay green; SKILL.md word count
    within its ceiling or the ceiling deliberately raised with both
    sites rewritten; full suite `python3 -m pytest loom-code/scripts/
    scripts/ loom-pipeline/scripts/ -q` green
- Dependencies: none
- Independent: true
- Brief item covered: "Packet-context discipline — new
  §Dispatch-packet context … four rules … Plus ONE pointer sentence"

## Task 2 — scoped inner-loop tests (implementer rule)
- Status: done(fe0b29d5)
- Description: Append one rule to loom-code/agents/implementer.md's
  role contract (own numbered item, matching rule 12's style): during
  the RED→GREEN inner loop, run the touched test file(s) only; run the
  full resolved package suite exactly once, after the last edit and
  before the commit. State explicitly that this final full run IS the
  per-task package-level gate (verification-before-completion
  unchanged) — only redundant intermediate full runs are eliminated.
  PLACEMENT: the new rule 13 must land BEFORE the
  `<!-- BEGIN baseline-v1` managed-block marker (:142) — distribute.py
  overwrites everything inside that block; note the embedded baseline
  is itself titled "12 rules", so the role-contract numbering (13) is
  correct and must not be confused with the baseline's count. Pin in
  test_implementer_req_tag_guard.py, RED-first, whitespace-normalized
  phrase asserts.
- Gloss: implementer 內迴圈不再每改一步就重跑 52 秒的全套件——只跑
  動到的測試檔、commit 前完整跑一次收官。每個 task 省 1-2 分鐘，
  而且 package 級驗證閘完全不動。
- Module: loom-code/agents
- Files touched: loom-code/agents/implementer.md,
  loom-code/scripts/test_implementer_req_tag_guard.py
- Context paths:
  - loom-code/skills/verification-before-completion/SKILL.md
- Acceptance:
  - RED: test_implementer_req_tag_guard.py::test_scoped_inner_loop_rule_present
    fails against current implementer.md
  - GREEN: it passes; full suite green
- Dependencies: none
- Independent: true
- Brief item covered: "Scoped inner-loop tests — one rule appended to
  implementer.md's role contract"

## Task 3 — lane-usage guidance (plan-format)
- Status: done(f4a063e1)
- Description: Add one authoring-guidance sentence (own sentence, not
  spliced) in plan-format.md's Review-weight area: when a task's
  Description already names an exact-spec target per Check 16's
  eligibility, declare `Review-weight: mechanical`; when every touched
  file is .md authored prose, consider `Review-weight: prose` — an
  eligible task left undeclared costs a full reviewer triad for zero
  marginal defect yield. Non-gating; Check 16 stays the gate. The
  sentence MUST land inside the "#### `Review-weight`" section
  (plan-format.md:101-111 area) — placement is load-bearing because
  test_plan_format_prose_weight.py's _review_weight_section() only
  reads text inside that heading window. Pin it there.
- Gloss: 讓「一行機械改動跑完整三方審」不再是預設浪費——plan 作者
  在符合資格時被明確提醒宣告 mechanical/prose 車道，每個合格 task
  省 6-8 分鐘 reviewer 時間，閘門本身一字不動。
- Module: loom-code/skills/writing-plans
- Files touched: loom-code/skills/writing-plans/references/plan-format.md,
  loom-code/scripts/test_plan_format_prose_weight.py
- Context paths:
  - loom-code/skills/writing-plans/references/plan-document-reviewer-prompt.md
- Acceptance:
  - RED: test_plan_format_prose_weight.py::test_review_weight_section_carries_lane_usage_guidance
    fails against current plan-format.md
  - GREEN: it passes; existing plan-format pins green; full suite green
- Dependencies: none
- Independent: true
- Brief item covered: "Lane-usage guidance — one authoring-guidance
  sentence in plan-format.md's Review-weight area"

## Task 4 — version 0.64.0
- Status: done(c028d07e)
- Description: Bump loom-code to 0.64.0 in both manifests, add the
  CHANGELOG [0.64.0] entry (packet discipline + scoped inner loop +
  lane guidance + any T1 ceiling raise), rewrite the shipping-version
  pin in test_docs_review_blocking_class.py — all four sites (function
  name, docstring, plugin.json assert, CHANGELOG assert; currently at
  0.63.0 — locate by grep, cite lines in the report).
- Gloss: 版本升到 0.64.0 並讓版本 pin 同步——沒 bump 的內容改動在
  裝置端 update 時靜默拿不到。
- Module: loom-code (manifests + CHANGELOG + pin)
- Files touched: loom-code/.claude-plugin/plugin.json,
  loom-code/.codex-plugin/plugin.json, loom-code/CHANGELOG.md,
  loom-code/scripts/test_docs_review_blocking_class.py
- Context paths:
  - loom-code/CHANGELOG.md
- Acceptance:
  - RED: the rewritten shipping pin fails against the un-bumped
    manifests
  - GREEN: pin passes after both manifests bump; CHANGELOG entry
    present; full suite green
- Dependencies: Tasks 1, 2, 3 complete first
- Independent: true
- Brief item covered: "loom-code → 0.64.0"

## Task 5 — probe + research note + lever-② backlog entry
- Status: done(d1c39188)
- Description: (a) FOUR adversarial haiku cold-read legs, one fresh
  context each, each given ONLY T1's shipped rules text plus one
  baited scenario: leg A (line-number temptation — "you read the pin
  at :326-328 ten minutes ago, commits landed since; compose the site
  inventory") expects string/heading anchoring; leg B (self-
  certification bait — two sourced facts plus one unsourced belief)
  expects the belief labeled a guess for lacking a named source — this
  is the judgment-to-action conversion under test; leg C (counting —
  a 4-consumer map vs a 1-consumer map) expects locate-arm first vs
  knowledge-in-hand, AND for the 4-consumer half expects the map
  written to a file with only the path in the packets (the file-map
  valve, the newest clause, must not ship unprobed); leg D (ready conclusion bait — "you already
  concluded the bug is in f(); compose the reviewer packet") expects
  claims-to-verify phrasing, no conclusion. Any leg failing = a T1
  wording defect: fix T1's text and re-probe the failed leg before
  close-out. (b) Research note at
  docs/loom/research/2026-08-06-subagent-latency-and-cache-research.md:
  the cross-project scan headline numbers (10,054 records, ~10s/call
  floor, bucket table), the industry-source verdict table (C1-C7 with
  URLs, from the session's two verification arms), and the lever-②
  experiment protocol + data (C1 10.6s; W 8.2/11.0/9.3/10.9s; verdict:
  no detectable effect at this scale; confounds named). (c) Backlog
  entry docs/loom/backlog/2026-08-06-same-type-dispatch-batching-cache-experiment.md
  (status OPEN; start: re-test with sonnet + real tool-using workloads
  ≥100k tokens; the JP single-source 2x claim and our null result both
  attached) + regenerate BACKLOG.md via backlog_index.py --write.
  (d) Dogfood report under docs/loom/dogfood/ with the probe verdict.
- Gloss: 用最弱模型驗證四條派工包規則冷讀可執行（會錨定字串、會標
  注猜測、不給 reviewer 餵結論）；同時把這輪的量測、業界查證、②
  實驗的完整數據落成可引用的研究記錄與 backlog 條目——資料不散失
  在對話裡。
- Module: docs/loom
- Files touched: docs/loom/research/2026-08-06-subagent-latency-and-cache-research.md,
  docs/loom/backlog/2026-08-06-same-type-dispatch-batching-cache-experiment.md,
  docs/loom/BACKLOG.md,
  docs/loom/dogfood/2026-08-06-dispatch-packet-probe.md,
  loom-code/skills/subagent-driven-development/references/dispatch-hygiene-notes.md,
  loom-code/scripts/test_sdd_extraction_pointers.py
  (the last two entries are written ONLY on a failed leg's
  fix-and-reprobe path)
- Context paths:
  - loom-code/skills/subagent-driven-development/references/dispatch-hygiene-notes.md
  - docs/loom/backlog/README.md
- Acceptance:
  - RED: any of the four legs diverges from its expected behavior →
    treat as a T1 wording defect, fix and re-probe that leg
  - GREEN: 4/4 legs CLEAN; research note + backlog entry + regenerated
    index + dogfood report all exist; backlog_index.py --validate green; full suite green
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: "Probe + research note … lever ②'s disposition
  per its data"

## Notes

- Endpoint: PR, continuous — per the session's standing arc pattern;
  kickoff 「先跑實驗驗證②然後把①③④收成 arc」.
- Lever ② excluded from legislation by the pre-registered decision
  rule (no clear win → backlog with data); T5(c) executes that rule.
- Wave 1 = T1+T2+T3 (pairwise disjoint Files touched, no semantic
  dependency: three independent surfaces). Level 2 holds T4 and T5;
  T5 is Independent: false (its conditional fix-and-reprobe path
  shares T1's files — Check 14), so T4 and T5 dispatch sequentially.
- Amendment skip note: T5's Context paths re-lists
  dispatch-hygiene-notes.md (already in Files touched — always-read,
  conditionally-written) — filling a schema field with a verbatim
  path copy, no re-review (reviewer round-4 optional note).
- User-directed hardening (post-round-1): T1 rule (b) reformulated
  action-type (provenance marker, not self-assessment) and T5 expanded
  to four adversarial legs — the weak-model stability concern
  (judgment-prose dies on weak models; verifiable-action prose
  survives).

## Decision Log

- (planning) The ② experiment's C1 was not globally cold (research
  arms ran within TTL; base-prefix warmth) — recorded as a confound in
  T5(b)'s protocol section, not silently dropped.
