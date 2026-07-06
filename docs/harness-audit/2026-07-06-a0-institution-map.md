# A0 — 制度盤點（Institution Map）

> 日期：2026-07-06 · 作者：Fable 5 制度外化 session（第一段）
> 用途：後續所有 harness-audit 產出的引用基準。任何新規則落地前，
> 先對照本表標注 `EXTEND` / `REPLACE` / `NEW`。
> 現場驗證方式：所有數字直接量自磁碟（wc / ls / hook 實跑），非印象。

## 1. 每場 session 自動載入的內容（token 固定成本）

| 來源 | 實測大小 | 載入時機 | 備註 |
|---|---|---|---|
| 全域 CLAUDE.md | 5.8 KB | 每場 | **symlink** → `~/dotfiles/claude/.claude/CLAUDE.md`（直接寫 `~/.claude/CLAUDE.md` 會被拒，近 30 天已撞 9 次） |
| 專案 CLAUDE.md（monkey-skills） | 4.6 KB | 每場（本 repo） | 技能開發規範、gate 定義、agent 行為規則 |
| auto-memory MEMORY.md | 15.5 KB | 每場（本 repo scope） | 225 個記憶檔的索引；軟上限 24.4 KB，已用 64% |
| **loom-code session-start hook** | **11 KB 消費**（wire 34.1 KB＝同內容 ×3 defensive keys） | **startup + 每次 /clear + 每次 compact，所有專案** | 注入 `using-loom-code` 完整 SKILL.md body（0.24.0 起改 ~2 KB router card，PR 進行中） |
| **loom-pipeline session-start hook** | **3.1 KB 消費**（wire 10.2 KB） | 同上 | 注入 family reception（已是 pointer-only，不動） |
| 全域 settings hooks | ~0 | — | cmux 狀態、dcg、bash-guard、waiting-notify：功能性，無 context 注入 |

合計：在 monkey-skills 一場 session 的制度固定成本 ≈ 40 KB（~10K tokens）；
在**無關專案**（Obsidian / Xcode / dbt）≈ 14.2 KB，全部來自 loom 兩支 hook。
（2026-07-06 修正：本表初版誤用 wire bytes——hook 以 3 個 JSON key 重複同內容，
harness 只消費一份；量洩漏要量被消費的 context。詳見 A 診斷 #1 修正框。）

## 2. 制度層（誰管什麼）

### 2.1 loom 家族（5 plugins，含機械 gate）
- 管轄：product principles → interface design → spec → code → pipeline 編排。
- 入口規則：`using-loom-*` 先行；on-ramp 準則表的 SSOT 在 reception hook。
- 機械 gate：`loom-code/hooks/git-guard.py`（PreToolUse:Bash）——擋直接 push main、
  無 review-PASS 的 push、pr merge（近 30 天實際攔截 25+15+3 次）。
- 行為契約（專案 CLAUDE.md + loom SKILL.md 已成文）：
  - TDD iron law（無 failing test 不寫 production code）
  - SDD 三 agent（implementer / spec-reviewer / code-quality-reviewer），原子任務 ≤5 min
  - worker 不出 verdict、evaluator 不改 artifact（GENERATE 站 critic 有明文豁免）
  - verdict 詞彙固定：PASS / PASS_WITH_NOTES / NEEDS_REVISION（spec-reviewer 二值）
  - 派工傳**路徑**不傳內容；Worker Input Contract = Resource Paths → Task → Input
  - cross-plugin delegation contract（toolkit 管 data，domain-teams 管分析與 gate）
  - verification-before-completion（宣稱完成前必跑 package 級測試）
  - requesting-code-review（whole-branch review 先於任何 push/PR）

### 2.2 記憶迴路（三套，各有分工）
| 系統 | 位置 | 管什麼 | 精簡機制 |
|---|---|---|---|
| auto-memory | `~/.claude/projects/<proj>/memory/` | user/feedback/project/reference 四類，跨 session | MEMORY.md 24.4 KB 軟上限；`index_archive` 歸檔 |
| repo 實務記憶 | `docs/loom/memory/`（21 條＋README） | loom 工作的 practice/gotcha，git 版本化，dual-host 鏡射 hook | recall via `loom-memory` skill，pull-not-push |
| git-memory trailers | commit trailers | Decision/Learning/Gotcha，`dev-workflow:git-memory` 是 commit 前強制 gate | 隨 git history |

- 教訓畢業管線：`dev-workflow:distill-sessions`（transcript 挖掘 → SKILL.md 修改提案，
  approval-gated write-back）。**目前退化運行：`~/.claude/usage-data/facets/` 為空
  （/insights 從未暖過），signal 偵測全靠 heuristic fallback。**
- 懸案 SSOT：`docs/loom/BACKLOG.md`。

### 2.3 skill 開發鏈（skill-dev-toolkit + dev-workflow）
- 造：skill-creator-advance；評：skill-judge（靜態）＋ dogfood-skill-testing（行為）；
  修：skill-refactor（token）＋ skill-tuning（輸出 A/B）。
- 結構 hook：`.claude/hooks/validate-skill-folder-structure.sh`（扁平資料夾強制）。
- 對話級工具：brief-before-asking（非平凡分岔先簡報）、proposal-critique / complexity-critique
  （YAGNI 三分法）、recap-state / handoff（狀態保存）。

### 2.4 Harness 原語（弱模型 session 實際可用的檔位）
- Agent tool `model` override：`sonnet` / `opus` / `haiku` / `fable`（fable 本 session 後不可用）。
- Workflow `agent()` opts：`model` + `effort`（`low`/`medium`/`high`/`xhigh`/`max`）+
  `schema`（強制結構化輸出）+ `isolation: worktree`。
- 全域預設 model：`claude-fable-5[1m]`（settings.json；日後需改回常駐型號）。
- permission mode：`bypassPermissions`（guard 責任全在 dcg / bash-guard / git-guard hooks）。
- 已知 harness 怪癖已成文於 memory：named-Agent 派工需 SendMessage、
  checkout -b from origin/main 觸發 push guard、dcg heredoc 字串誤傷、
  `~/.claude/CLAUDE.md` 是 symlink 要寫 dotfiles 真實路徑。

## 3. 缺口地圖（第二段立法的對照基準）

| 原 prompt 交付 | 既有覆蓋 | 判定 | 真正的缺口 |
|---|---|---|---|
| B. CLAUDE.md 精簡 | 全域+專案共 10.4 KB，**不是**主要 token 成本 | 前提部分不成立 | 真正的洩漏在 loom hooks（44 KB/次），見 A 診斷 #1 |
| C. 模型調度守則 | SDD 三 agent 契約、dispatching-parallel-agents、派工傳路徑 | `NEW`（窄） | 只缺：model/effort 對照表＋升降級路徑；派工結構一律引用 loom-code |
| D. 判斷力外化 | 何時算完成=verification-before-completion；何時問=brief-before-asking；換路 vs 重試=systematic-debugging 部分覆蓋 | `EXTEND` | 缺：何時升級模型、方向錯誤訊號（跨 debugging 之外）、品質底線通用驗法 |
| E. 派工模板 | loom-code agents/ 四份角色 prompt + Input Contracts | 條件式 | 待 A 診斷確認；初步看只缺「非 code 類」（研究/搜尋）模板 |
| F. 維護協議 | 三套記憶迴路+distill-sessions 畢業管線+BACKLOG SSOT | `EXTEND` | 缺：制度檔（harness-audit/*）本身的修改權限與精簡規則；facets 暖機習慣 |

## 4. 本表維護

- 本檔屬快照（2026-07-06）。plugin 版本、hook 大小、memory 用量會漂移；
  引用前用 §1 的驗證方式重量測，勿直接信舊數字。
- 更新判準：新增/移除 plugin、hook 注入量變動 >20%、記憶系統改制 → 更新本檔並記 changelog 於文末。

---
Changelog:
- 2026-07-06 初版（Fable 5 制度外化 session 第一段）。
