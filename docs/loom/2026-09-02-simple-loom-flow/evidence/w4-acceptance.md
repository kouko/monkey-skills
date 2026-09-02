# W4 驗收紀錄 — 2026-09-03

| task | 結果 | 證據 |
|---|---|---|
| W4-01 冷讀 Task A／B（REQ-9） | ✅ 兩者零猜測、開檔 2；A 三輪 7→4→0、B 兩輪 3→0 | cold-read-A.md、cold-read-B.md（interim 見 cold-read-A-interim.md） |
| W4-04 量測（REQ-5／8） | ✅ skill 17、形狀 5、session-start 658（基線 5281）；名詞 61 **不達** ≤40（Open question） | measurements.md |
| W4-03 replay（REQ-10） | ⚠️ #771 真跑：commit 34 vs 31（**不合格**；每 checkpoint 固定 3 commit）、審查派工 12 vs 22 ✓、決策點 2 ✓；#772 37/35/2 ✓；#775 18/16/2 ✓；首輪 vs 後續輪 finding 40%/60%。三個機制缺陷：對抗檔無處放（已修 3101ab2b）、wave 定義雙源（已修）、checkpoint commit 係數（intent Open question） | replay-771.md、replay-772.md、replay-775.md、ceremony-cost-old-vs-new.md §v10 實測 |
| W4-02 Codex 實走（REQ-2）第一輪 | ❌ 使用者面相同（檔案、決策點、規則 id 一致）；機制面三破：`--probe` 未經 Codex hook 引擎（永遠報活）、scaffold 副本命中 `**/templates/**` glob、`.codex/` 在 Codex sandbox 不可寫；另 change-id 日期照抄範例 | req2-codex-walk.md（三次 codex exec 逐字紀錄） |
處置：W4-02 修正（fb726221／3920a959）→ 第二輪實走 ✅ **REQ-2 通過**（req2-codex-walk-r2.md：未授信→sandbox 句／`/hooks` 句並停、零工件；授信→probe 被 hook 擋→intent exit 0（scaffold 在 diff 內）→plan→hand-off；Codex 增量＝scaffold commit＋一次 /hooks 停點）。未測：真 `/hooks` TUI（以 bypass 代）、F4 日期恰等於範例日期無法判別。
