# Continue after CI failure — plan
intent: 2026-09-10-continue-after-ci-failure@19dd439bfbf3e378412b73083a716e6661b03902
spec: docs/loom/2026-09-10-continue-after-ci-failure/spec.md@19dd439bfbf3e378412b73083a716e6661b03902
charter: 1.0

## Task DAG

### Wave 1 — One contract-only continuation change

**W1-01 Keep an active task moving after CI failure**  after: none  acceptance: 1, 2, 3, 4
- Files: loom-code/skills/ship/SKILL.md, loom-code/skills/maintain/SKILL.md, loom-code/scripts/test_simplified_station_text.py
- Test: A1 positive: failed-checks-and-logs; boundary: missing-diagnostics-block. A2 positive: existing-test-repair; boundary: same-review-episode. A3 positive: PR-text-reuse; negative: committed-version-rereview. A4 positive: diagnosed-external-block; negative: unattributed-no-retry.
- Risk: agent-decided — replace existing sentences instead of adding recovery machinery; add no runtime, classifier, state, hook, checker rule, retry budget, or command contract.

## Questions asked

1 — what — 你要的是：當自動檢查失敗時，只要同一個工作仍在執行，Agent 就自行讀取錯誤並在原工作內做最小修復；只有實際功能改變才重新驗證，單純發布資料修正不重跑功能檢查；無法安全判斷時才停下來告訴你。對嗎？
1 — consequence — 回答「對」也代表：Review 與發布檢查通過後，可以自動 non-forced push 並開好 Ready PR；合併仍需你另外授權，你也可以在發布前明確取消。
1 — what — 這次 Closing Review 要使用 Claude Code 當第二位讀者嗎？
2 — behaviour — 也就是你看到 CI 失敗後，Agent 會自行完成可安全判斷的修復，同時保留功能修改後的完整 testing 保護。這個行為符合預期嗎？
2 — behaviour — 你是否同意採用第一個方案：版本檔變更仍重新 Closing Review？

## Risks

1. A prose-only contract guides capable agents but cannot guarantee identical recovery behavior on every executor; tests pin the minimum wording without adding runtime enforcement.
2. Any committed repair changes the functional digest and consumes the next slot in the existing bounded Closing Review episode, including code, tests, and version files.
3. Failed-log availability depends on the CI provider; missing diagnostics stop with a concrete blocker rather than creating automatic retries.
