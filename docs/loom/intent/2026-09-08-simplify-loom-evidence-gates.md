# 簡化 Loom 證據與發布關卡
originator: kouko
kind: engineering
needs-design: yes — push hook、公開文字檢查與驗證狀態都會改變，且包含多種失效與重用狀態
evidence: [docs/loom/2026-09-07-push-gate-cheap-checks-first/review.json, docs/loom/2026-09-07-push-gate-cheap-checks-first/blind-run-report.md]
status: confirmed 2026-09-08

## Problem
功能已經驗證完成後，剩餘時間主要耗在手動維護 review ledger、commit 形狀、隱私判斷與證據 SHA 對齊。純文字或帳務修正會讓有效證據失效，甚至迫使完整測試再次執行；這些往返成本已高於程式實作本身。

## Proposed outcome
把 Loom 收斂成獨立失效的內容驗證與發布驗證，並由單一自動收尾動作產生 ledger 與 checkpoint。內容驗證以功能內容指紋重用 suite、probe 與 review 結果；發布驗證快速處理版本、文件、commit／PR 格式與秘密掃描。只有真正可能識別私人對象的文字才啟動隱私 judge，誤報可留下理由後繼續。

## Acceptance
1. 功能內容未變時，只修改 ledger、版本文件或公開文字，不會重跑完整 suite、probes 或 branch review。
2. 功能內容改變時，舊內容證據必定失效，且 repository mutation、錯誤指紋與偽造證據仍會阻擋發布。
3. 一個自動收尾動作可以收集 verdict 與 probes、計算 rounds 與 dispatches，並產生唯一 checkpoint，不需人工編輯衍生欄位。
4. commit 與 PR 文字永遠接受確定性的秘密掃描；公開 repository 名稱、PR 編號、Task ID 與公開廠商名稱不會觸發 AI judge。
5. 真正可能識別私人對象的文字會交給 judge；格式錯誤或誤報只阻擋該公開文字，並可用有理由、可稽核的方式放行。
6. 機制可供其他 repository 使用，不依賴 monkey-skills 的語言、框架、檔名或測試工具。
7. 本輪以新流程驗證自身：保留實際測試與獨立 review，但不再使用舊 review.json、舊 checkpoint、舊 SHA 對齊、舊 privacy judge 或舊 push gate 作為發布前提。

## Constraints
- 一個 intent、一個實作 branch、一次最終 branch review 與一個 PR；內部可分成獨立測試階段。
- 保留完整 package suite、adversarial probes、獨立 reviewer 與 repository mutation 防護提供的實質品質保障。
- 新機制完成前，以 baseline、TDD、聚焦測試、完整 package suite 與獨立 reviewer 避免循環自證。
- 不修改或刪除 main checkout 的未追蹤 `work/`，也不改動現有其他 worktree。
- 使用 Claude Fable 作為第二供應商 reviewer。

## Out of scope
- 降低功能測試、adversarial probes 或獨立 review 的品質標準。
- 為 monkey-skills 的特定語言、框架或路徑建立例外。
- 同時維護可長期切換的新舊兩套發布流程。
- 合併任何其他 worktree 或未相關變更。

## Open questions
- none
