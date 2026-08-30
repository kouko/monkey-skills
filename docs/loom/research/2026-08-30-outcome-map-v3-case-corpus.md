# Outcome Map v3：真實案例分類 corpus

日期：2026-08-30

## 目的與證據邊界

這份 corpus 用真實工作壓測 Outcome Map v3 的四種 ticket 邊界。它同時涵蓋 Loom 本身的演進，以及用 Loom 交付其他專案的 delivery arcs。分類依據是「什麼證據使 ticket 關閉」，不是執行過程用了哪些活動；因此，同一個 delivery 內可以包含查資料、討論或測量，仍不會因此變成 research、grilling 或 prototype。

Claude Code transcript 只用本機可見的 user/assistant 訊息與工具紀錄補回當時脈絡；不使用隱藏推理，也不把 transcript 傳出本機。正式可重現證據優先指向 repository artifact、Git commit 或 PR。

此 repository 沒有 `docs/loom/PRINCIPLES.md`：本次 spec 不受 repository principles 約束。

## 案例表

| # | 專案 | 實際工作與證據 | v3 類型 | 關閉證據 | 與 delivery arc 的關係 | 分類壓力 |
|---:|---|---|---|---|---|---|
| 1 | monkey-skills | 決定 family relocation 第一刀先搬 hooks；`docs/loom/maps/family-relocation/tickets/grilling-first-cut.md` | grilling | 使用者對方向選擇的具名 ratification | 決定下一個 delivery slice，但本身不交付程式 | 純粹的價值／順序裁決，邊界清楚 |
| 2 | monkey-skills | 查明 Claude/Codex plugin-root primitive；`tickets/research-plugin-root-primitives.md` | research | 有來源支持、可引用的事實答案 | 降低後續 relocation delivery 的不確定性 | 查到答案即結束，不需要人挑候選物 |
| 3 | monkey-skills | 實測跨 plugin store access；`tickets/feasibility-cross-plugin-store-access.md` | research | 可重現 probe 與 factual conclusion | 解除 relocation delivery 的技術未知 | v2 稱 prototype 且要求 ratification；v3 應把 machine-measured feasibility 歸 research，否則與 research 重疊 |
| 4 | monkey-skills | 盤點 family contract consumers；`tickets/task-inventory-consumers.md` | research | 完整、可核對的 consumer inventory | 為 relocation delivery 定義 blast radius | v2 `task` 只是產出答案；證明 generic task 沒有獨立 closure semantics |
| 5 | monkey-skills | 搬移 family hooks；`tickets/task-relocate-family-hooks.md` | delivery | 正式變更、測試、PR/CI 交付 | 一個直接推進 Destination 的 slice | v2 `task` 同時被拿來表示真正交付，與案例 4 完全不同 |
| 6 | monkey-skills | backlog/map boundary v2；`docs/loom/specs/2026-08-30-backlog-map-boundary-v2.md`、PR #764 | delivery | 合併的跨 plugin 契約與測試 | 改善長期 Loom 工作控制的一個 arc，不完成整體方向 | 一個 delivery 內含大量 decisions/research，仍以正式交付關閉 |
| 7 | kumiko-zaiku-app-icons | 看樣：紋樣尺寸與窗框形狀配對；`docs/loom/look-dev/2026-08-27-pattern-size-and-shape-pairing.md`、PR #24 | prototype | 人對新產生的視覺候選做觀察／選擇 | 可能生成後續 delivery，自己不等同產品交付 | 真正需要 HITL 感知比較，符合 prototype 專屬邊界 |
| 8 | kumiko-zaiku-app-icons | 紙張深淺、焦距、陰影等量測；`docs/loom/measurements/2026-08-18-*.md` 至 `2026-08-20-*.md` | research | 命名輸入、量測值與可重現結論 | 為 render delivery 提供事實約束 | 雖會產生 render 樣本，只要 closure 是量測答案就不是 prototype |
| 9 | kumiko-zaiku-app-icons | 淺木色與更深窗內紙；`plans/2026-08-20-light-wood-and-darker-inside-paper.md`、PR #20、commit `86a9ed8` | delivery | 出貨色值、重渲、回歸測試與合併 PR | 交付一個視覺成果 slice | 內含測量與先前人類偏好，但 ticket 關閉靠 shipped change |
| 10 | kumiko-zaiku-app-icons | 非圓形容器；`plans/2026-08-24-non-circular-container.md`、PR #23、commit `430f6f6` | delivery | config 到 render 的端到端功能與相容測試 | 長期產品目的下的另一個獨立 arc | 規模大仍只是 slice；不可讓 delivery 自動 clear Map |
| 11 | kumiko-zaiku-app-icons | 壓平 PNG 輸出；PR #22、commit `ef3d3bd` | delivery | 可使用的 PNG 產物、腳本與測試 | 包裝流程的一個交付 | 規格曾縮範圍，顯示 delivery 以承諾的 slice 而非 Map 目的關閉 |
| 12 | youtube-summarize-scraper | Retry-After 配額韌性；`docs/loom/specs/2026-06-09-quota-retry-after-cooldown.md`、PR #47、commit `7815896` | delivery | provider cooldown 行為、測試與合併 PR | 提升可靠性的單一 delivery arc | 先研究 API 行為不會把整個 arc 變成 research |
| 13 | youtube-summarize-scraper | openai-compatible 多實例 HA；`docs/loom/specs/2026-06-29-lmstudio-ha-multi-instance.md`、PR #61、commit `ebc1d85` | delivery | named instances、failover、文件與測試 | 另一個可靠性 delivery arc | 同一長期 outcome 可由多個 delivery 累積，而不是一張 Map 對一個大實作 |
| 14 | reading-list-summarize-scraper | RSS/Atom source；`docs/loom/specs/2026-06-15-rss-source.md`、PR #9、commit `ff589aa` | delivery | 新 source 可端到端擷取並通過測試 | 擴大輸入來源的一個 slice | delivery 的 closure 是可交付能力，不是所有來源問題都解完 |
| 15 | reading-list-summarize-scraper | 分頁文章擷取；`docs/loom/specs/2026-06-15-paginated-article-extraction.md`、PR #10、commit `8a357af` | delivery | next-page traversal、合併內容與測試 | 改善抽取品質的另一個 slice | 與案例 14 並列，支持一張長期 Map 內多 delivery |
| 16 | meeting-emo-transcriber | speaker identification 四項改善；`docs/loom/specs/2026-05-05-speaker-id-improvements-design.md`、後續 PR #16/#17 commits | delivery | CLI/匹配行為、相容處理、測試與合併 | 語者辨識 outcome 下的實際交付 arc | 一個 delivery 可以拆成多 PR；ticket 應綁整個 arc 的正式完成證據，而非單一 commit |

## Claude Code 可見歷史的交叉證據

- Kumiko session `52b23b55-39b9-46d3-9ff8-ce255ae3361a` 的可見 user prompt 明確要求 3D 真實感、陰影、立體感，以及窗內底紙顯著較深；後續 repo artifacts 把這個長期視覺方向拆成量測、看樣與多次 delivery。
- Kumiko sessions `ee83f727-5010-43ef-a371-ad6c0c3b46d0`、`20d8b47b-0373-4991-8f8a-0edfe05c77f1` 可見 `D9B382` 與非圓容器工作的執行脈絡；正式結果分別落在 PR #20 與 #23。
- YouTube Summarizer sessions `44a33171-7645-49d6-9f7d-851a316534af`、`3c863674-0046-49d0-8503-b11ed69ee09f` 可見 Retry-After 工作脈絡；正式交付落在 brief 與 PR #47。
- 這些 transcript 證明需求會跨 session 演化；repo artifacts 與 Git 則提供可重現的 closure evidence。兩者用途不同，不互相替代。

## 從案例凍結的分類規則

1. **只看 closure test。** ticket 內做過哪些活動不決定 type；使它合法關閉的證據才決定 type。
2. **grilling**：唯一 closure 是人對價值、方向或取捨的具名裁決。
3. **research**：唯一 closure 是有證據支持、可被反駁的 factual answer；machine-measured feasibility 在此。
4. **prototype**：唯一 closure 是人對新產生候選 artifact 的反應、比較或選擇；沒有 HITL 感知裁決就不應使用。
5. **delivery**：唯一 closure 是約定 outcome slice 的正式交付證據；可以跨多個 commits/PRs，但不會因自身關閉而宣告 Map 完成。
6. **沒有 task/unblock。** 盤點答案回到 research；實際實作回到 delivery；純依賴與 blockers 只作結構欄位。

## 對生命週期的直接要求

- Delivery ticket 是 arc 的 map-level owner；Brief、Plan、Git、PR/CI 是 delivery arc 的詳細 SSOT。
- ticket 到 Brief 必須有穩定、機械可驗證的 join key；不得延續自由文字 `Map part:`。
- Map 只能唯讀派生 delivery progress，不能把 Brief/Plan/PR 狀態複製回 ticket 形成第二份真相。
- Map clear 至少要求 fog 空、所有 tickets terminal（成功 closed 或具名撤回 withdrawn），且 Destination acceptance 被明確證明；只清空工作清單不足以證明 outcome 成立。
- 一次 delivery 關閉後，可以根據新事實生成下一個 ticket 或 fog；這是長期控制迴圈，不是預先列完的 backlog。

## 尚待規格化的壓力點

- Delivery ticket 綁 Brief 的 canonical path 與反向引用語法。
- 一個 delivery 跨多 PR，以及一個 PR 是否可滿足多 delivery tickets。
- Destination acceptance 的 schema 與 validator 如何避免主觀「看起來完成」。
- v2 `task` 的 deterministic migration：按 closure evidence 分流 research 或 delivery，不能只做名稱替換。
- 舊 feasibility prototype 如何安全分流成 research，而不抹掉既有 human ratification 歷史。
