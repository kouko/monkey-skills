# finishing-a-development-branch

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> Orchestrator skill — 把 branch 收尾流程串起來：[`requesting-code-review`](../requesting-code-review)（Step 1 人類審查） → [`verification-before-completion`](../verification-before-completion)（Step 2 套件層級測試） → P3-D 強制 `dev-workflow:git-memory` 委派（commit message trailer） → git commit → push → 可選 gh pr create → 可選 [`using-git-worktrees`](../using-git-worktrees) 清理。**不自動 merge** — 最終 merge 決定保留給使用者。

[loom-code](../..) plugin 的一部分。Agent 載入的是 [`SKILL.md`](SKILL.md)；本 README 是給人類看的。

## 流程

```
finishing-a-development-branch
  ├─→ Step 1: requesting-code-review        （人類審判品質）
  ├─→ Step 2: verification-before-completion （套件層級測試 pass）
  ├─→ Step 3: dev-workflow:git-memory       （commit message trailer，P3-D 強制）
  ├─→ Step 4: git commit                    （用 Step 3 的訊息）
  ├─→ Step 5: git push
  ├─→ Step 6: gh pr create                  （可選、user opt-in）
  └─→ Step 7: git worktree remove           （可選、user 確認）
```

每個 Step gate 下一個。🔴 fatal review findings 或 test failure 會 BLOCK 進度。每個 user-visible action（commit message 確認、push、PR 建立、worktree 移除）之前都要 user 確認。

## 使用時機

- 「結束這個 branch」/「feature 完成」/「可以 merge 嗎」/「ship」/「收尾這個 branch」
- 「幫這個 branch 開個 PR」
- 「我這邊做完了，下一步？」（「完成」框架 → 進下個 task 前先收尾）
- SDD 跑完多任務 plan、全部 DONE 後主動呼叫

## 不使用時機

[`SKILL.md`](SKILL.md) §When NOT to Use：
- 任務還沒完（SDD plan 未完成）
- 直接 commit 到 main 的 trivial（個人專案 1 行 doc fix）
- 要丟掉的 branch（skill 不適用；直接刪掉就好）
- 使用者明確 override AND 真的有理由（cherry-pick / 已知 trivial 清理）

## 大量委派 — 設計上如此

本 skill 刻意保持新邏輯極少。每個 step 都委派給 specialist：

| Step | 委派給 | 為什麼 orchestrator 不直接做 |
|---|---|---|
| 1 | `requesting-code-review` | 品質審查本身就是一個 skill |
| 2 | `verification-before-completion` | 套件層級測試 invocation 本身就是一個 skill |
| 3 | `dev-workflow:git-memory` | P3-D 強制 — git-memory 判斷 trailer 是否需要；orchestrator 不重複 |
| 4 | git CLI | 標準 git commit |
| 5 | git CLI | git push（新 branch 要設 upstream） |
| 6 | gh CLI | gh pr create（opt-in） |
| 7 | `using-git-worktrees` | Worktree 清理 pattern 在那邊 |

## 這個 skill 不做的事

- 自己不審 code（委派）
- 自己不跑測試（委派）
- 不決定 memory trailer（P3-D — 委派給 git-memory）
- 不 merge 到 main（使用者權限）
- 沒授權不 force-push
- 不 amend commit（按 CLAUDE.md 政策 — 永遠開新 commit）
- 沒 opt-in 不自動建 PR
- 沒確認不自動移除 worktree

## 參考

- [`SKILL.md`](SKILL.md) — 運作規格 + 7-step 預設流程 + Red Flags
- [`../requesting-code-review/SKILL.md`](../requesting-code-review/SKILL.md) — Step 1 委派
- [`../verification-before-completion/SKILL.md`](../verification-before-completion/SKILL.md) — Step 2 委派
- [`../using-git-worktrees/SKILL.md`](../using-git-worktrees/SKILL.md) — Step 7 委派
- `dev-workflow:git-memory` — Step 3 委派（P3-D 強制）
- [`../using-loom-code/SKILL.md`](../using-loom-code/SKILL.md) — Router；本 skill 是 Stage 8（Branch close）
- CLAUDE.md §"Committing changes with git" — 繼承的 git 政策
