# A — Harness 診斷：token 洩漏 / 失焦 / 錯誤 前三名

> 日期：2026-07-06 · 作者：Fable 5 制度外化 session（第一段）
> 證據基礎：近 30 天全專案 transcript 掃描（865 場 session，
> `~/.claude/projects/**/*.jsonl`），掃描腳本見本檔末尾〈量測方法與侷限〉。
> 引用基準：[A0 制度盤點](2026-07-06-a0-institution-map.md)。

## 診斷 #1 — loom session-start hooks：最大單一 token 洩漏源

**現象**：`loom-code` 與 `loom-pipeline` 的 SessionStart hook 每次注入
約 **14.2 KB（≈3.5K tokens）** 進 context（loom-code 灌完整
`using-loom-code` SKILL.md ~11 KB＋loom-pipeline 灌 reception ~3.1 KB），
matcher 是 `startup|clear|compact` —— 意即：

> **2026-07-06 第二段修正**：初版寫 44.3 KB/次（9.5M tokens/月），
> 那是 hook 的 **wire 輸出**——同一內容以三個 JSON key 重複發出
> （canonical + 2 個 defensive key，跨 host 防漂移的刻意設計，
> 有整合測試鎖定），harness 只消費一份。實際 context 注入 14.2 KB/次，
> 月洩漏下修為 **~3.1M tokens**。發現本身不變（仍是最大單一注入源、
> 全專案生效、compact 重打），量級修正 3×。教訓：量 hook 洩漏要量
> **被消費的 context**，不是 stdout bytes。

1. **每場 session 開場**注入一次（**所有專案**，包括 Obsidian / Xcode / dbt
   等永遠不會碰 loom 的 session）；
2. **每次 `/clear`** 再注入一次；
3. **每次 context compaction** 再注入一次（context 越長的 session 被扣越多次）。

**證據**：
- Hook 實跑輸出量測：`loom-code/0.23.1/hooks/session-start` → 34,089 bytes
  wire（= 11 KB 內容 ×3 keys）；`loom-pipeline/0.5.0` → 10,209 bytes wire
  （= 3.1 KB ×3）。消費量 = 單份：11 KB + 3.1 KB ≈ 14.2 KB/次。
- 近 30 天 865 場 session；其中大量位於非 loom 專案
  （`-Users-kouko`：240 場、komado-Refs：27 場、obsidian-vault：21 場、dotfiles：12 場…）。
- 下限估算：865 × 14.2 KB ≈ 12.3 MB ≈ **~3.1M input tokens / 30 天**，
  compaction / clear 重注入未計入，實際更高。
- 內容檢視：注入物 = loom reception（3.1 KB，合理）＋ `using-loom-code`
  **完整 SKILL.md body**（~11 KB）。後者與 Skill 系統重複——真正調用
  `using-loom-code` 時 Skill tool 本來就會載入完整內容。reception 自己
  寫著「Pointer only… pull-not-push stays intact」，但 hook 對 SKILL body
  做的正是 push。

**修法**（2026-07-06 第二段修正後的範圍；落點：`loom-code/hooks/`，
loom family 管轄，走正常 PR）：
1. **loom-code 注入物瘦身**：不再灌完整 SKILL.md body（Skill 調用時本來
   就會載入），改灌 ~2 KB router card：coding 強制路由宣告＋五條
   load-bearing 規則＋SUBAGENT-STOP。**剪之前必須過 firing 驗證**
   （corpus 28 條，方法照 docs/loom/dogfood/2026-07-04-family-tissue-firing-test.md）。
2. **loom-pipeline reception 不動**：3.1 KB 已是 pointer-only 設計，
   再剪傷 firing 換不到多少 token。
3. 專案判別（非 git repo 不注入）**降為 watch item**：瘦身後單次成本
   已低，判別的 false-negative 風險（在合法 repo 靜默失去 loom）大於收益。

預期效益：11 KB → ~2 KB，每月省 ~1.9M input tokens（含 clear/compact 重打更多）。

## 診斷 #2 — 主對話自己下場乾重活：失焦與 context 膨脹的主因

**現象**：主對話（指揮官位置）直接執行大量讀取與掃描，而不是派 subagent
只收結論；同一檔案在同場 session 內反覆重讀。

**證據**：
- 30 天內主對話吞入的工具結果：Read 10.0 MB、Bash 8.7 MB —— 合計約為
  Agent 回報量（6.4 MB）的三倍。委派比例明顯偏低。
- 同場重讀（單場 ≥3 次才計，跨場加總）：`AppDelegate.swift` 53 次、
  `pipeline.go` 34 次、`MEMORY.md` 22 次、`ImageReaderView.swift` 24 次、
  多個 SKILL.md 11-14 次。重讀 = 同一內容多次計費＋擠壓真正在做的任務。
- 使用者打斷 30 天共 62 次；打斷密集場：dotfiles/b8f0c131（5 次）、
  obsidian-vault/9e195a61（4 次）。
- 打斷原因抽樣分析（2 場、9 次打斷，Sonnet subagent 逐次分類）——
  **誠實修正：打斷多數不是助手的錯**。9 次中 6 次是使用者主動注入新資訊
  或自我修正（USER_CHANGED_MIND=4、自我補充=2），助手可歸因的 3 次：
  - WRONG_DIRECTION ×2：(a) dotfiles 場——使用者只要「全部 agent 共用
    CLAUDE.md」，助手已在執行複雜的 core + per-tool 多檔架構；
    (b) obsidian 場——使用者說的「COT」是 Table of Contents，助手當成
    Chain of Thought 並基於錯誤前提發了四選項 AskUserQuestion。
  - OVER_SCOPE ×1：dotfiles 場——一輪不停頓輸出超長 A/B/C 選項分析，
    使用者回「？？」。
  - 共同模式：**歧義詞先假設再行動**（該先一句確認）與**長回合不落停頓點**
    （與 memory 條目 briefing-buried-by-AskUserQuestion 同根）。
  - 對本診斷的含義：失焦的主要代價不在互動面（打斷），而在 context 面
    （委派偏低＋重讀）；互動面修法已由 brief-before-asking 制度覆蓋，
    需補的是「歧義名詞一句話確認」這條輕量判準（→ 第二段交付 D）。

**修法**（落點：第二段交付 C〈模型調度守則〉的核心條款＋派工模板）：
1. 指揮官不下場：預期輸出 >2 個檔案的讀取、repo 掃描、網頁查詢、批次改檔
   一律派 subagent，主對話只收結論＋`檔案:行號`。
2. 長檔用 Read 的 offset/limit 窗口，不整檔重讀；重讀前先自問
   「這檔案這場讀過沒」。
3. 大型產物落檔傳路徑，不貼進對話（既有慣例，寫進派工回報合約固定欄位）。

## 診斷 #3 — Edit 紀律錯誤群：最高頻的可預防錯誤

**現象**：Edit 相關的機械性錯誤是全 harness 最大錯誤群，且都有固定解法，
純屬紀律問題——正是弱模型會反覆踩的類型。

**證據**（30 天、all projects）：
- **135 次**「File has not been read yet」——沒先 Read 就 Edit/Write。
- **25 次**「File has been modified since read」——stale read 後直接重試。
- 合計 160 / 3,734 次 Edit = **4.3% 失敗率**，每次失敗 = 一輪錯誤往返
  （error + 重試 ≈ 1-2K tokens × 160 ≈ 每月 ~0.3M tokens，且中斷任務節奏）。
- **9 次**「Refusing to write through symlink: ~/.claude/CLAUDE.md」——
  全域 CLAUDE.md 是 symlink（→ `~/dotfiles/claude/.claude/CLAUDE.md`），
  必須寫 dotfiles 真實路徑，9 次全是同一個坑。
- 25 次 push-to-main 攔截＋15 次 merge 攔截＋3 次 loom review-gate 攔截：
  guard 正常工作，但重複嘗試代表模型在撞牆後未改變策略。
- AskUserQuestion / Monitor InputValidationError 共 ~8 次——弱模型 schema
  填錯的典型樣態。

**修法**：
1. 派工模板（第二段交付 E/C）固定兩行紀律：
   「改既有檔案：先 Read 再 Edit」「撞 modified-since-read：重新 Read 後
   重下 Edit，禁止原 diff 直接重試」。
2. symlink 坑寫入 auto-memory（feedback 條目）＋未來制度檔：
   改全域 CLAUDE.md 一律寫 `~/dotfiles/claude/.claude/CLAUDE.md`。
3. Guard 撞牆規則：同一 guard 連續攔兩次 → 停手，把 guard 訊息完整回報
   使用者，不嘗試第三次（與 memory 中 push-guard 教訓一致，此處升為通則）。

## 次要發現（不進前三，但影響第二段設計）

- **facets 全空**：`~/.claude/usage-data/facets/` 為 0 檔——`/insights`
  從未執行過，`distill-sessions` 的 signal 偵測一直在 heuristic fallback
  模式下運行。F（維護協議）應納入「定期暖 facets」或接受 heuristic 品質。
- **B 的前提修正**：全域＋專案 CLAUDE.md 合計僅 10.4 KB，**不是**主要
  token 成本；第二段的 B 應降級為小幅精簡，主力放診斷 #1 的 hook 瘦身。
- auto-memory MEMORY.md 15.5 KB / 24.4 KB 軟上限（64%），尚健康，
  但索引行風格已高度縮寫化——對弱模型的可讀性是潛在風險（未量測，標註為推測）。

## 量測方法與侷限（誠實條款）

- 掃描器：session scratchpad `scan_harness.py`——逐行 parse JSONL，
  聚合 tool_result bytes / is_error 簽名 / Read 重複 / 打斷字串。
- **侷限 1**：bytes ≈ tokens 用 4:1 粗換算，CJK 內容實際 token 密度更高，
  估算偏保守（低估）。
- **侷限 2**：「口頭糾正」偵測（regex 開頭比對）回報 0，屬量測方法太窄，
  不代表沒有糾正行為；失焦證據以打斷次數＋抽樣敘事為準。
- **侷限 3**：主對話 vs subagent transcript 未完全區分（subagent 事件
  混在部分 project 目錄），tool 統計是全體混合值；「委派偏低」的結論
  由 Read/Bash vs Agent 比例＋重讀模式共同支撐，非單一數字。
- **侷限 4**：distill-sessions Stage 1+2 訊號（git-memory 高頻 mid-friction）
  經檢視多為「每次 commit 必 fire」的結構性雜訊，未採用為診斷依據；
  其 Stage 3（$18.66 Sonnet 艦隊）對 harness 級診斷不划算，未執行。

---
Changelog:
- 2026-07-06 初版；打斷原因抽樣待 subagent 回報後補入。
