# W1 checkpoint 審查紀錄 — 2026-09-02

## after-task（W1-01 write-plan，e43bd203）
| reviewer | lens | verdict | 摘要 |
|---|---|---|---|
| sonnet-coldread-writeplan-1 | 冷讀 Task A | 7 猜測 | needs-design 判準沒寫、kind 值域、第二家 CLI 未排除 host、slug 規則、review.json 誰建、contract 規則 id、KICKOFF 不存在 |
| opus-review-writeplan-1 | spec-conformance＋docs | NEEDS_REVISION | 🔴 needs-design 判準缺；🔴 Codex 首次 scaffold＋授信步缺；🟡 standing.* 表歸屬、checkpoint vs wave 上限、after-task wave 必跑、second-vendor 偵測、(b)(c)(e) 未標 gate；🟢 維度名、無 spec 時 user-decided 落點、測試只驗形狀 |
處置：c4747e6f；冷讀第二輪 4 猜測（2 任務事實、2 真缺口）→ eecb4c9f；task-size 措辭 → 735b5d7d。

## wave-end（1c9ed208..29893175）
| reviewer | lens | verdict | 摘要 |
|---|---|---|---|
| sonnet-review-docs-w1 | docs 5 維＋conformance | NEEDS_REVISION | 🔴 W1 沒派 adversary → `push.probes-adversarial` 會擋；🔴 五張站序表漏列該規則；🔴 adversary.md 指錯 catalogue 路徑；🟡 build BLOCKED 分支「stop and ask」違反 §4；🟡 決策點①②的問題無 questions[] 回填路徑；🟡 docs/loom/ATTACK-CATALOGUE.md 陳舊；🟢 SKILL 版本欄不一、check_field_microstructure 偏離 plan 無理由行、root README 缺 loom-design（既有） |
| sonnet-blindrun-w1 | 盲跑（scratch repo，四站走完到 ship step 4） | 走得通 | 六種產物與表一致；指令全 exit 0；9 落差：`which` 抓到 alias 誤判第二家 CLI；references 路徑基準未講；**沒說要開 feature branch**；KICKOFF 模板 stamp 註解；package-test 偵測無 fallback；intake 指令段落位置；最小 plan 時 wave-end＋branch-end 重複；≤5 是否含 branch-end；push 輸出看不出 adversarial 有無重跑 |
| opus-review-code-w1 | code＋跨站＋探針 | （待） | |
| opus-adversary-w1 | 對抗（skill／gate） | （待） | |
