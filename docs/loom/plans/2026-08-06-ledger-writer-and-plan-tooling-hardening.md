# Plan: deterministic ledger writer + plan-tooling hardening

Source brief: docs/loom/specs/2026-08-06-ledger-writer-and-plan-tooling-hardening.md
Goal: ledger flips become a validated one-line script edit instead of
    bare string surgery, malformed Steps declarations fail loudly, and
    the branch-start recipe plus the Dependencies-over-Independent rule
    are written where the next session will read them
Stage: finishing
Total tasks: 5
Critical-path depth: 5 (≤5)
Execution order: sequential (every level is a single task after the
    doc-mirrors-code edges)
Plan-document-reviewer verdict: PASS (2026-08-06 19:13)
Steps:
  1. 寫入器
  2. 守衛
  3. 接線
  4. 版本收束
  5. 行為探針

## Task 1 — plan_card --set-status ledger writer
- Status: done(fb6f552d)
- Description: Add `--set-status "T<N>=<status>"` to scripts/plan_card.py.
  Status grammar is exactly the schema's four kinds — `pending` |
  `claimed(@<agent>)` | `done(<sha>)` | `blocked` — parenthetical
  REQUIRED for claimed/done, FORBIDDEN for pending/blocked. Locate the
  task block by its `## Task <N>` heading and rewrite its existing
  `- Status:` line in place, wherever it sits in the block. Loud exit 1
  on: task not found, malformed status, zero `- Status:` lines in the
  block, more than one `- Status:` line in the block. Exit 0 prints the
  old and new line. The file is modified only on that one line.
- Gloss: 讓「把 T2 標成 done」變成一條有驗證的指令而不是裸字串編輯——
  上個 arc 的重複欄位事故和靜默 no-op 事故，以後會在指令層被大聲擋下
  而不是悄悄過關。
- Module: scripts (repo-root, host-neutral)
- Files touched: scripts/plan_card.py, scripts/test_plan_card.py
- Context paths:
  - loom-code/skills/writing-plans/references/plan-format.md
  - docs/loom/plans/2026-08-06-bounded-auto-third-round-and-dispatch-hardening.md
- Acceptance:
  - RED: test_plan_card.py::test_set_status_rewrites_in_place (happy
    path, done kind) fails against current script (unknown argument)
  - GREEN: it passes, plus sibling tests — one per status kind, each
    error path (missing task / malformed status / zero Status lines /
    duplicate Status lines), a Status line after Gloss AND one directly
    after the heading both rewrite, file byte-identical outside the one
    line; full suite `python3 -m pytest loom-code/scripts/ scripts/
    loom-pipeline/scripts/ -q` green
- Dependencies: none
- Independent: true
- Brief item covered: "scripts/plan_card.py --set-status — the
  deterministic ledger writer"

## Task 2 — loud Steps guard
- Status: done(383c314d)
- Description: A `Steps:` line with content after the colon exits 1
  with a message naming the correct format (bare `Steps:` line +
  indented numbered titles). Fixture: the inline form the 0.62.0 plan
  originally used (`Steps: a / b / c`).
- Gloss: 拼錯格式的 Steps 宣告從「靜默渲染成無標題」變成「大聲報錯教
  你正確寫法」——跟這家 repo 其他 fail-loud 檢查對齊。
- Module: scripts (repo-root, host-neutral)
- Files touched: scripts/plan_card.py, scripts/test_plan_card.py
- Context paths:
  - scripts/plan_card.py
- Acceptance:
  - RED: test_plan_card.py::test_inline_steps_declaration_fails_loud
    fails against current script (renders titleless at exit 0)
  - GREEN: it passes; existing Steps tests (bare-line form, count
    mismatch) still pass; full suite green
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: "Loud Steps guard"

## Task 3 — duty + docs wiring (prose)
- Status: done(a499cfce)
- Description: Four one-sentence edits: (a) SDD SKILL.md Progress-ledger
  paragraph — perform ledger flips via `python3 scripts/plan_card.py
  --set-status "T<N>=<status>"` when the script exists at the repo
  root, hand-edit only when absent; (b) plan-format.md Dependencies/
  Independent area — `Dependencies` is the ordering authority;
  `Independent: true` governs concurrency only among tasks at the same
  dependency level, never against a declared dependency; (c)
  plan-format.md Steps schema — the inline form is rejected loudly;
  (d) environment-gotchas.md — new-arc branch recipe: `git checkout -b
  <name> <main-tip-sha>`; both `git merge --ff-only origin/main` and
  `git checkout -b <name> origin/main` trip the push-guard's string
  match. Each addition its own sentence (implementer.md role-contract
  rule 12). SDD SKILL.md is at 3958 words vs its 3974 ceiling
  (test_sdd_extraction_pointers.py:81) — the sentence exceeds the 16-
  word headroom: deliberate raise, new ceiling = measured + margin
  ≤20, CHANGELOG-noted in T4's entry. Pin checks: grep the three
  target files' pin tests for touched phrases; update in the same
  commit.
- Gloss: 把這輪學到的三件事寫在下一個 session 真的會讀到的位置——
  flip 用指令、Dependencies 永遠壓過 Independent、開分支用 sha——
  不再依賴聊天記憶。
- Module: loom-code (three prose files)
- Files touched: loom-code/skills/subagent-driven-development/SKILL.md,
  loom-code/skills/writing-plans/references/plan-format.md,
  loom-code/skills/using-loom-code/references/environment-gotchas.md,
  loom-code/scripts/test_sdd_extraction_pointers.py
- Context paths:
  - scripts/plan_card.py
  - loom-code/agents/implementer.md
- Acceptance:
  - RED: test_sdd_extraction_pointers.py gains
    ::test_ledger_flip_names_the_writer (asserts the --set-status
    sentence present in SDD SKILL.md) — fails against current text
  - GREEN: it passes; WORD_CEILING raised deliberately at
    test_sdd_extraction_pointers.py:81 AND its assertion message at
    :326-328 rewritten to the new number and this arc (the function
    has no docstring — the provenance lives in that message); grep
    confirms the plan-format sentence ("ordering authority") and the
    gotchas recipe line present; full suite green
- Dependencies: Tasks 1, 2 complete first
- Independent: true
- Brief item covered: "Duty + docs wiring (prose)"

## Task 4 — version 0.63.0
- Status: done(7ebbb754)
- Description: Bump loom-code to 0.63.0 in both manifests, add the
  CHANGELOG [0.63.0] entry (ledger writer + Steps guard + the three
  doc wirings + the deliberate SDD ceiling raise), rewrite the
  shipping-version pin in test_docs_review_blocking_class.py (function
  name, docstring, plugin.json assert, CHANGELOG assert — all four
  sites at :200, :208-209, :219-220, :224-225 — currently at 0.62.0).
- Gloss: 版本升到 0.63.0 並讓版本 pin 同步——沒 bump 的內容改動在裝
  置端 update 時靜默拿不到。
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
- Independent: false
- Brief item covered: "loom-code → 0.63.0"

## Task 5 — haiku probe + dogfood note
- Status: done(552bdeaf)
- Description: One fresh-context haiku probe: given SDD's new
  ledger-flip sentence (verbatim) + the scenario "T2's reviewers both
  passed, its commit is abc1234, update the plan ledger", does the
  cold reader reach for the --set-status command instead of hand-
  editing? Write the verdict + a mini dogfood note (this arc's own
  ledger flips performed via the new writer where chronologically
  possible) to docs/loom/dogfood/2026-08-06-ledger-writer-probe.md.
- Gloss: 用最弱模型驗證新義務句真的會把人導向指令——加上本 arc 自己
  的 flip 就用新寫入器當第一個真實用戶。
- Module: docs/loom/dogfood
- Files touched: docs/loom/dogfood/2026-08-06-ledger-writer-probe.md
- Context paths:
  - loom-code/skills/subagent-driven-development/SKILL.md
- Acceptance:
  - RED: probe answer diverges from the command path → treat as a
    wording defect in T3(a), fix and re-probe
  - GREEN: probe CLEAN; report file exists with the verdict + dogfood
    note
- Dependencies: Task 4 completes first
- Independent: false
- Brief item covered: "One haiku probe … Mini dogfood note"

## Notes

- Endpoint: PR, continuous — per the session's standing arc pattern
  (four consecutive arcs, all PR endpoint, user merges via CLI); the
  kickoff 「可以直接做 1 2 4 5 嗎」 rides that recorded pattern.
- Retrospective item 3 (exemption-premise verification) deliberately
  excluded — memory-tier, not legislated (user ratified the split).
- T1/T2 share files → sequential by dependency; T3 shares no file with
  T2 but mirrors both T1's and T2's code, so it follows them.

## Decision Log

- (planning) T3 depends on T1 AND T2 (doc-mirrors-code both ways: the
  duty sentence names T1's flag grammar; the loud-rejection sentence
  documents T2's behavior). With T3 at level 3, its Independent: true
  marker buys no pairing — kept for schema consistency; Dependencies
  is the ordering authority (the very sentence T3(b) adds).
- (planning, reviewer note) T4's pin sites cited at line granularity
  per plan-format §Stated facts narrowest-form.
