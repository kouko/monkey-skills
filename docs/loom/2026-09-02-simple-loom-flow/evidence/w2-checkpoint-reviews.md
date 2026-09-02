# W2 checkpoint 審查紀錄 — 2026-09-03

## wave-end（bf370552 … 1a799c0d）
| reviewer | lens | verdict | 摘要 |
|---|---|---|---|
| sonnet-review-docs-w2 | docs 5 維＋冷讀 Task B | NEEDS_REVISION | 🔴 design-system 讀 `docs/loom/PRINCIPLES.md`（其他處都是根目錄）；🔴 design-md-schema 依賴舊 schema 的 `## Anchors`，主路徑永遠落 fallback；🟡 root README ja/zh 的 loom-workflow 列被誤改；examples 的 7 份 OpenSpec spec.md 缺 ARCHIVED；knowledge-triage 殘留「design seed」；①覆述句缺中文；站序表無路徑（冷讀 3 猜測皆為此）；PURPOSE.md fallback 未被授權；3+1 vs 4 措辭 |
| opus-review-code-w2 | code＋跨 plugin＋探針 | PASS_WITH_NOTES | 🔴 四站 Codex 指令模板代入組出不存在路徑；🟡 design-md-schema 指向已刪 skill；camelCase 誤擋 iPhone／iOS；單向門清單三份散文副本無一致性測試；validator 日期只驗形狀。機械面全綠（144／889、邊界、citations、codex sync）。探針：空 bullet 擋、單字非談判項放行（設計邊界）、code span 藏識別字擋、engineering 不跑② |
| sonnet-blindrun-w2 | 盲跑 Task B（capture-intent→build 第一 checkpoint） | 走得通 | 6 落差：識別字 regex 誤中日期「9/10」；Open questions 必填但無「沒有」寫法；誰呼叫 spec review 兩站矛盾；spec checkpoint 時 plan 不存在無從抄 questions[]；無 remote 時 merge-base fatal；`command -v` 見 alias；**(e) 必問 vs 先查閘優先權衝突**（裁定：先查優先、後果形重申，§4 已記） |
| opus-adversary-w2 | 對抗（13 探針） | NEEDS_REVISION | 🔴 P13 無 remote 的 trunk 上 branch_base==HEAD → diff 空 → needs-design 重算靜默；🔴 P05 `kind:` 自報，改標 engineering 躲② 與拒收；逃脫：P01 付費 API 藏 Design decision（散文）、P02 confirmed-behavior 未綁 sha、P03 REQ id 無重算、P04 非談判項重複、P06 yes 分支 UI flows N/A 無反向重算、P07 Codex 無 checker 無 stop、P08 validate_design_output 已刪成懸空引用、P09 spec 審後改寫無新鮮度、P12 status 偽造（接受）；held：P10 glob 聯集＋waiver 不蓋拒收、P11 contract 邊界 |

## 複審（3b5948c2 / bcb6ce0e / b435739e / d7d31008 / b0f356c3）
| reviewer | lens | verdict | 摘要 |
|---|---|---|---|
| sonnet-review-docs-w2b | docs 閉環＋冷讀 Task B r2 | PASS_WITH_NOTES | 22 條全關；冷讀 Task B **零猜測**（開檔 2）；notes：review description 未提 write-spec 為 spec 鏡頭呼叫者、gate 標記 vs checker id 未說明（7bf27b96 已修） |
| opus-review-code-w2b | code＋gate 閉環＋探針 | NEEDS_REVISION | A1–A9 全關（kind-recompute 只以 glob 命中觸發＝正確讀法）；W2 探針 11 held／2 設計接受；新 🔴 F1 checker 把 `ratified-by: pending` 當已批准（validator 擋、checker 不擋，而真閘是 checker）；🔴 F2 UI flows 反向重算只認字面 N/A，「沒有介面」穿過；🔴 F3/F4 spec 新鮮度 legacy 第三階無界（省略 spec_sha 即免查）；🟡 F5 needs-design-reason 只讀 HEAD 訊息（分支中段必誤報）；🟡 F6 日期只驗形狀 |
處置：checker 側 agent 修 F1–F6（拿掉 legacy 退化；本 change 的 review.json 由 orchestrator 補 spec_sha）。

處置落地：79efc3a9（ratified-by 文法＋真日期＋parity；UI flows 反轉為至少一條 `→`；spec 新鮮度無 legacy 退化；intent commit 訊息改讀最後動到 intent 的 commit；日期真實性）。本 repo 的 standing 閘正確擋下未簽 PRINCIPLES；intake 在補 spec_sha／@sha 後通過。
