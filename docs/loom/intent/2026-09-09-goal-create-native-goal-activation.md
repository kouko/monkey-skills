# goal-create 原生 Goal 啟用
originator: kouko
kind: product
needs-design: yes — 使用者看到的指令結果會依 host 能力分成直接啟用、確認後啟用與手動貼上三種狀態，目前沒有既有互動規格涵蓋它
status: confirmed 2026-09-09

## Problem
現在使用 goal-create 只會得到 Goal 內文；即使所在平台支援原生 Goal，使用者仍要理解差異並手動啟用，而且系統可能把「已產生內文」誤說成「Goal 已啟用」。這影響同時在 Codex 與 Claude Code 使用 Loom 的人。

## Proposed outcome
保留共同的四欄 Goal 產生與檢查流程，完成後依目前 host 實際提供的能力啟用原生 Goal；只有無法啟用時，才提供可直接送出的替代指令。

## Acceptance
1. 我在 Codex 明確要求建立 SESSION Goal 時，可以看到通過檢查的完整四欄內容，而且目前 task 的原生 Goal 會直接啟用。
2. 我在提供 Goal proposal 能力的 Claude Code 互動 session 明確要求相同 outcome 時，可以由 goal-create 提出並啟用原生 Goal；需要確認的情境會清楚等待我的確認。
3. 我在沒有 Goal proposal 能力的 Claude Code 情境使用 goal-create 時，會看到尚未啟用的明確狀態，以及一條可直接送出的 `/goal` 指令。
4. 無論在哪個 host，只有收到 host 的成功證據時才會顯示 Goal 已啟用；工具不存在、拒絕、失敗或仍待確認都不會誤報。
5. 原有四欄格式、輸入不足時的拒絕、lint 行為與 ARC mode 維持不變。

## Constraints
- 使用 host 已提供的原生 Goal 能力，不啟動巢狀 Claude process，也不以自製 Stop hook 冒充內建 Goal。
- Claude Code 的 Goal proposal 是條件式能力；實作必須先看當前 session 是否真的提供，不能只依版本號推定。
- Codex 與 Claude Code 共用 Goal 內容與檢查規則，只有最後的啟用 adapter 分流。
- 未公開的 Claude Code 工具不能成為沒有 fallback 的必要依賴。

## Value case
GO — 這能在平台允許時移除重複貼上的操作，同時讓不支援的環境維持可用且不誤報；現有實驗已證明能力確實會因 session 而缺席，因此現在需要把分流契約固定下來。

## Out of scope
- 替使用者開啟 Claude Code 的實驗旗標或修改帳號、管理政策。
- 透過 `claude -p` 啟動另一個 session。
- 實作自有的長時間 Goal／Stop-hook 引擎。
- 改動 ARC mode 或重新設計四欄 Goal 格式。

## Open questions
- none
