# Replay seed 3 — API schema-diff CLI for CI pipelines (synthetic)

Feed §Seed to §Headless / seeded mode as run-input; every bullet = user-stated verbatim.

## Seed

- **Idea**: 我想做一個開發者用的 CLI 工具，讀取 OpenAPI/GraphQL schema 檔案，在 PR 裡自動檢查 breaking change 並產生人類看得懂的 diff 報告，取代團隊現在手動 review API 合約的流程。這個 CLI 打算整組用 Rust 寫，理由是要發布單一 binary 給工程師直接下載、不需要裝 runtime，schema parsing 用現成的 openapiv3 crate。
- **Q1 task**: 只做「schema diff 偵測 + breaking change 分類 + CLI/CI 輸出報告」
- **Scope-out**: mock server、schema 產生器、API gateway
- **Q2 user**: 後端工程師（CI pipeline 裡跑，也可本機手動跑）
- **Q3 quality pick**: 準確性（不能漏報）＞ 執行速度 ＞ 報告美觀度
- **Q4 success**: 對 100 個已知 breaking-change 案例召回率 ≥ 98%
- **Q5 why-new**: 現有工具（openapi-diff 等）誤報率高、不支援 GraphQL、CI 整合麻煩
- **Q6 languages**: 僅英文 CLI 輸出（開發者工具慣例）
- **Q7 money**: 開源 MIT license，之後可能做付費 SaaS 團隊儀表板；roadmap 是先開源衝 star 數，6 個月後再談 monetization
- **Q8 lifecycle**: 單次 CLI 呼叫數秒內完成；不維護長駐 process、不存歷史（CI 自己存 artifact）
- **Product canon**: Working Backwards / PR-FAQ（先寫使用者故事再回頭做技術決策）
- **Design stance**: 輸出格式要同時對人類與機器可讀——預設彩色人類可讀表格，`--json` flag 給機器解析；錯誤訊息要能直接複製貼上去修 schema。互動慣例接近 Shneiderman's Eight Golden Rules 的「錯誤預防+一致性」，也吸收 Nielsen's 10 Usability Heuristics 的「見錯即知如何修」
- **Eng stances**: 打磨優先度=功能正確性優先於美觀輸出／可逆性=breaking rule 要能覆寫（使用者可 opt-out 特定規則）／隱私=不上傳任何 schema 內容到外部伺服器，純本地執行／升級胃口=agent 自行決定內部模組切分，不需事前審
- **Eng canon**: Hexagonal/Ports & Adapters（parser 要能替換 OpenAPI/GraphQL adapter）＋ 12-Factor App（CLI 設定走 env var 的 cross-cutting checklist）
