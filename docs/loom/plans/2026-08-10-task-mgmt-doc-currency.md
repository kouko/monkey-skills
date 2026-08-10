# Plan: task-management doc currency sweep

Source brief: docs/loom/specs/2026-08-10-task-mgmt-doc-currency.md
Goal: 任務管理相關活文件全部反映 0.71.0 機制實況——兩份 plan ledger 收官、工具路徑教雙層解析、ROADMAP 指標改標歷史、backlog 條目對齊已出貨事實
Stage: finishing
Total tasks: 4
Critical-path depth: 2 (T1 ∥ T2 ∥ T3 → T4)
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-08-10, round 3, 15/15)
Endpoint recording: endpoint named: no → human-pumped（push/PR 前向 user 確認）

## Notes

- 兩份審計報告（backlog 91/91 真實性、活文件 stale-reference 12 findings）是本 plan 的規格來源；每項編輯都可回溯到一列審計表。
- 憲章紀律：backlog 條目**只附加證據行與範圍收窄註記，永不改寫原始 ask**。
- README 三語組（loom-code、philosophers-toolkit）三語同刀（repo memory: skill READMEs require tri-language）。
- T4 依賴 T1-T3 全完（regen 需在所有條目編輯落定後跑一次）。
- Decision Log（plan-gate 2 輪上限越權，round 3）: round 2 唯一 finding 是 round-2 修訂自身引入的一個欄位（T2 `Review-weight: prose` 對生成器目標檔 DIRECTION.md 不合 Check 16），修法為 reviewer 自開處方「拔掉該欄」——brief 無恙、非結構問題，故套用單欄修正後跑 round 3 而非中斷向 user 升級；本行即審計記錄。
- Decision Log（commit 對照，whole-branch 🟡 補記）: 各任務的交付 commit 與其審查修正 commit——T1=7a9cb468（無修正）；T2=43f7533e（無修正）；T3=交付 c8a41a42、審查 🟡 修正 9e85e34c（repo-root 限定+zh-TW 措辭）；T4=交付 f46864bd、審查 🟡 修正 e2f15f19（行號引用更正）。ledger done() 欄記的是各任務終態 commit，本行補齊交付 commit 供追溯。

## Task 1 — 兩份 plan ledger 收官

- Description: 以 `python3 scripts/plan_card.py <plan> --set-stage "finishing"` 分別翻 `docs/loom/plans/2026-08-07-loom-mechanical-dedup-arc1.md`（現 `Stage: sdd:wave-1`）與 `docs/loom/plans/2026-08-07-loom-arc2-deletion-first-dimension.md`（現 `Stage: review:round-1`）——兩弧 9/9 任務 done、PR 已 merge（各自出貨於 loom-code 0.65.2 / 0.66.0，屬收於 0.68.0 的複雜度體檢五弧系列）、分支已刪。用機制自己的寫入器，不手改。
- Module: docs/loom/plans（ledger 欄位，機制活面）
- Files touched: docs/loom/plans/2026-08-07-loom-mechanical-dedup-arc1.md, docs/loom/plans/2026-08-07-loom-arc2-deletion-first-dimension.md
- Context paths:
  - docs/loom/plans/2026-08-07-loom-mechanical-dedup-arc1.md
- Acceptance:
  - RED: `grep -l "^Stage: finishing" <兩檔>` 目前 0 檔命中
  - GREEN: 兩檔皆 `Stage: finishing`；`python3 scripts/plan_card.py <各檔>` exit 0
- External surfaces: 無
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State #1「Both stale plans read Stage: finishing」
- Status: done(7a9cb468)
- Gloss: 把兩個已出貨弧的進度表頭從「進行中」改成收官，帳跟上事實

## Task 2 — 工具路徑雙層解析普查修正

- Description: TECH-SPEC 與 AGENTS.md 的全部本弧編輯集中於此（避免與 T3 撞檔）：(a) `loom-code/TECH-SPEC.md:83-88` §2.1 scripts/ 清單補 plan_card.py + backlog_index.py、刪不存在的 scripts/README.md；(a2) `loom-code/TECH-SPEC.md:6` 表頭 Roadmap 行改指 `docs/loom/DIRECTION.md`、ROADMAP 連結標 historical；(b) `docs/loom/backlog/README.md:196-202` 產生器段補雙層解析一句，`:126,150-151` 兩處 bare path 改指該段；(c) `docs/loom/DIRECTION.md:5-6` 憲章句補「(repo-root first, else the loom-code plugin copy)」；(d) `docs/loom/README.md:12` 同型改法，且目錄圖補一行 `DIRECTION.md` —— 措辭含「human `## Next`/`## Later`; `## Now` generated — never hand-edit」；(e) `docs/loom/memory/a-shared-index-file-is-regenerated-from-entries-never-hand-merged.md:23` How-to-apply 改為「the store's generator (resolution per the backlog charter)」；(f) AGENTS.md 腳本清單補兩支腳本各一 bullet（含解析順序）；(f2) `AGENTS.md:196-199` philosophers-toolkit 段改「planned work now lives in docs/loom/DIRECTION.md / backlog entries」。均為每處自成句補充，不 splice 進被釘句。
- Module: 跨檔散文（單一性質：工具路徑現況）
- Files touched: loom-code/TECH-SPEC.md, docs/loom/backlog/README.md, docs/loom/DIRECTION.md, docs/loom/README.md, docs/loom/memory/a-shared-index-file-is-regenerated-from-entries-never-hand-merged.md, AGENTS.md
- Context paths:
  - docs/loom/backlog/README.md
  - docs/loom/memory/README.md
- Acceptance:
  - RED: `grep -rl "loom-code plugin" <六檔>` 中 backlog README/DIRECTION/docs README 目前 0 命中該片語（audit 已證）
  - GREEN: 六檔各自含雙層解析描述或指向；`python3 scripts/check_loom_memory_integrity.py` exit 0（memory 檔 description 未動，僅 body）；`python3 -m pytest loom-code/scripts/ scripts/ -q` 全綠
- External surfaces: 無（散文；`${CLAUDE_PLUGIN_ROOT}` 字面量僅得出現於 AGENTS.md 說明性上下文，須明言「載入時替換」）
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State #2 + #4「docs/loom/README's directory map gains a DIRECTION.md row」+ #3 之 TECH-SPEC/AGENTS 部分
- Status: done(43f7533e)
- Gloss: 讓所有教人跑進度工具的活文件都知道 plugin 副本的存在，方向層在目錄圖上現身

## Task 3 — ROADMAP 墓碑指標改標歷史

- Description: ROADMAP 指標改標（TECH-SPEC 與 AGENTS.md 的對應編輯已移入 T2，本任務不碰該兩檔）：(a) `loom-code/README.md:187` + `README.ja.md:181` + `README.zh-TW.md:181` ROADMAP 行改「(historical design record — forward direction: docs/loom/DIRECTION.md)」各語對應措辭；(b) `loom-code/PRODUCT-SPEC.md:6` 表頭 Roadmap 行改指 DIRECTION.md、ROADMAP 連結標 historical；(c) `philosophers-toolkit/README.md:228` + `README.ja.md:226` + `README.zh-TW.md:219` 同型改法。三語組各自語言一致。
- Module: 跨檔散文（單一性質：方向層指標）
- Files touched: loom-code/README.md, loom-code/README.ja.md, loom-code/README.zh-TW.md, loom-code/PRODUCT-SPEC.md, philosophers-toolkit/README.md, philosophers-toolkit/README.ja.md, philosophers-toolkit/README.zh-TW.md
- Context paths:
  - loom-code/ROADMAP.md
- Acceptance:
  - RED: 上列七檔目前 0 檔在 ROADMAP 提及處含「DIRECTION.md」指向（audit 已證）
  - GREEN: 七檔的每個 ROADMAP 活指標旁都有 DIRECTION.md 前向指向；`python3 -m pytest loom-code/scripts/ scripts/ -q` 全綠
- External surfaces: 無
- Dependencies: none
- Independent: true
- Review-weight: prose
- Brief item covered: Smallest End State #3（README 三語組 + PRODUCT-SPEC；TECH-SPEC/AGENTS 部分由 T2 承載）
- Status: done(9e85e34c)
- Gloss: 別再把讀者送去已封存的路線圖，前向方向一律指 DIRECTION.md

## Task 4 — backlog 條目對齊 + regen

- Description: 五條目：(a) `2026-07-26-investing-toolkit-full-three-statement-management-kpi-history-in-kpi-sto.md` 附加證據行——sub-arc (a) 已由 PR #619 (2.38.0, kpi_us_statements_ingest.py) 交付，範圍收窄至 (b)+(c)，status 維持 OPEN；(b) `2026-07-02-468-reviewer-next-touch-nits-loom-code-tech-spec-ci.md` 附加——子項 (a) 已由 PR #672 交付（8-/11-dimension 已一致）、(c) 原已標 fixed，僅 (b) 存活，OPEN 不變；(c) `2026-07-15-operational-kpi-full-dimensional-signature-slice-follow-ups-2026-07-15.md` 附加——末 bullet 已由 PR #573 (2.21.0 multi-filing fetch) 交付，(a)-(d) 存活；(d)+(e) `2026-08-02-backlog-index-two-frontmatter-readers-disagree-on-duplicate-keys.md` 與 `2026-08-06-plan-card-cjk-aware-gloss-line-join.md` 檔案指標由 `scripts/<name>.py` 改 `loom-code/scripts/<name>.py`（本尊所在；附一行 #680 搬移註記）。全部附加式，不改原文。完成後 `--validate` → `--write` → `--direction-write`，有 diff 則入 commit。
- Module: docs/loom/backlog
- Files touched: docs/loom/backlog/2026-07-26-investing-toolkit-full-three-statement-management-kpi-history-in-kpi-sto.md, docs/loom/backlog/2026-07-02-468-reviewer-next-touch-nits-loom-code-tech-spec-ci.md, docs/loom/backlog/2026-07-15-operational-kpi-full-dimensional-signature-slice-follow-ups-2026-07-15.md, docs/loom/backlog/2026-08-02-backlog-index-two-frontmatter-readers-disagree-on-duplicate-keys.md, docs/loom/backlog/2026-08-06-plan-card-cjk-aware-gloss-line-join.md, docs/loom/BACKLOG.md
- Context paths:
  - docs/loom/backlog/README.md
- Acceptance:
  - RED: 五條目目前 0 條含今日證據行（grep "#619\|#672\|#573\|#680" 各檔）
  - GREEN: `python3 scripts/backlog_index.py --validate` exit 0；`--check` exit 0（regen 後）
- External surfaces: 無
- Dependencies: Tasks 1, 2, 3 complete first
- Independent: false
- Brief item covered: Smallest End State #5
- Status: done(e2f15f19)
- Gloss: 讓待辦帳本承認已經出貨的事，指標指向程式碼本尊

## Steps

1. 帳跟上事實（T1+T2+T3 並行）
2. 待辦帳本對齊與再生（T4）
