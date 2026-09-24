NEEDS_REVISION — R3 與 R6 尚未完全成立；修正語言基線與 vault 慣例後才適合合併。

### Table A

| 需求 | 裁定 | 證據 |
|---|---|---|
| R1 | PASS | 明定獨立研究筆記、無 wiki 欄位；後續 ingest 由使用者決定。[SKILL.md:8](/Users/kouko/.herdr/worktrees/monkey-skills/obsidian-skill-3/obsidian/skills/obsidian-research/SKILL.md:8)、[SKILL.md:97](/Users/kouko/.herdr/worktrees/monkey-skills/obsidian-skill-3/obsidian/skills/obsidian-research/SKILL.md:97) |
| R2 | PASS | 只允許 host 工具與本 plugin 技能；實際引用 `defuddle`、`obsidian-markdown` 均屬 obsidian。[SKILL.md:10](/Users/kouko/.herdr/worktrees/monkey-skills/obsidian-skill-3/obsidian/skills/obsidian-research/SKILL.md:10)、[SKILL.md:53](/Users/kouko/.herdr/worktrees/monkey-skills/obsidian-skill-3/obsidian/skills/obsidian-research/SKILL.md:53)、[SKILL.md:88](/Users/kouko/.herdr/worktrees/monkey-skills/obsidian-skill-3/obsidian/skills/obsidian-research/SKILL.md:88) |
| R3 | PARTIAL | 預設與主題語言規則正確，但「使用者指定語言＝只搜那些語言」可取消 EN＋JA 基線。[SKILL.md:35](/Users/kouko/.herdr/worktrees/monkey-skills/obsidian-skill-3/obsidian/skills/obsidian-research/SKILL.md:35) |
| R4 | PASS | 3–6 個獨立角度、預設 gap check、反證式關鍵說法查核都有明確程序。[SKILL.md:43](/Users/kouko/.herdr/worktrees/monkey-skills/obsidian-skill-3/obsidian/skills/obsidian-research/SKILL.md:43)、[SKILL.md:59](/Users/kouko/.herdr/worktrees/monkey-skills/obsidian-skill-3/obsidian/skills/obsidian-research/SKILL.md:59) |
| R5 | PASS | 四層職責、骨架僅為建議、結論＋目錄先於骨架章節均明載。[SKILL.md:12](/Users/kouko/.herdr/worktrees/monkey-skills/obsidian-skill-3/obsidian/skills/obsidian-research/SKILL.md:12)、[SKILL.md:74](/Users/kouko/.herdr/worktrees/monkey-skills/obsidian-skill-3/obsidian/skills/obsidian-research/SKILL.md:74) |
| R6 | PARTIAL | 是 checkpoints 而非完整模板，且強制 TOC；但 frontmatter 是固定欄位後「再加」CLAUDE.md 欄位，不是真正服從 vault 慣例。[SKILL.md:76](/Users/kouko/.herdr/worktrees/monkey-skills/obsidian-skill-3/obsidian/skills/obsidian-research/SKILL.md:76) |
| R7 | PASS | 會讀 `research/` 最新 2–3 篇並跟隨標題與語氣，空資料夾也有 fallback。[SKILL.md:72](/Users/kouko/.herdr/worktrees/monkey-skills/obsidian-skill-3/obsidian/skills/obsidian-research/SKILL.md:72) |

### Findings

| 嚴重度 | 維度 | 發現 | 證據 | 一行修正 |
|---|---|---|---|---|
| important | A / R3 | 使用者只要「加入韓文來源」，目前會變成「只搜韓文」，違反至少 EN＋JA。 | [SKILL.md:37–41](/Users/kouko/.herdr/worktrees/monkey-skills/obsidian-skill-3/obsidian/skills/obsidian-research/SKILL.md:37) | 保留 EN＋JA；只有使用者明確排除某語言時才縮減。 |
| important | A / B / D / R6 | 固定 `research/`、只把 cwd 視為 vault root，且固定 frontmatter schema；巢狀工作目錄或不同 vault 慣例會得到錯路徑／錯 metadata。 | [SKILL.md:23](/Users/kouko/.herdr/worktrees/monkey-skills/obsidian-skill-3/obsidian/skills/obsidian-research/SKILL.md:23)、[SKILL.md:78](/Users/kouko/.herdr/worktrees/monkey-skills/obsidian-skill-3/obsidian/skills/obsidian-research/SKILL.md:78)、[SKILL.md:94](/Users/kouko/.herdr/worktrees/monkey-skills/obsidian-skill-3/obsidian/skills/obsidian-research/SKILL.md:94) | 向上尋找 `.obsidian/`，從 vault 指示與現有筆記推導資料夾及完整 frontmatter。 |
| important | C | `context → case → analysis → what generalizes` 不是 Yin 的標準 linear-analytic report sequence；且未說明 case study 是分析性概括，不是統計概括。 | [frameworks.md:20](/Users/kouko/.herdr/worktrees/monkey-skills/obsidian-skill-3/obsidian/skills/obsidian-research/references/frameworks.md:20) | 移除 Yin 歸因，或改成忠實的 linear-analytic 結構並補 analytic-generalization 限制。 |
| important | C | Hofstede 被泛化成一般文化分析，缺少國家層級資料與生態謬誤警告；Kano/JTBD 也被列為一般工具選型工具，適用面過寬。 | [frameworks.md:12](/Users/kouko/.herdr/worktrees/monkey-skills/obsidian-skill-3/obsidian/skills/obsidian-research/references/frameworks.md:12)、[frameworks.md:20](/Users/kouko/.herdr/worktrees/monkey-skills/obsidian-skill-3/obsidian/skills/obsidian-research/references/frameworks.md:20) | 限定 Hofstede 為跨國群體比較；Kano 用於需求滿意度、JTBD 用於使用者進展。 |
| nit | C | KJ 的 `group → label → relate → write up` 過度壓縮；是否把初始卡片／標籤製作算入「label」不明，我標為不確定。「Unknown unknowns」那題實際是 pre-mortem。 | [frameworks.md:21](/Users/kouko/.herdr/worktrees/monkey-skills/obsidian-skill-3/obsidian/skills/obsidian-research/references/frameworks.md:21)、[frameworks.md:39](/Users/kouko/.herdr/worktrees/monkey-skills/obsidian-skill-3/obsidian/skills/obsidian-research/references/frameworks.md:39) | 補 `cards → group → name groups → spatially relate → explain`；把 blind spot 改名 pre-mortem。 |
| important | E | 報告稱 raw outputs 在同目錄，卻沒有 activation transcript、9 次 dispatch 軌跡、62/65 次工具呼叫、auditor 原文或成本紀錄；這些數字無法重現。 | [report.md:4](/Users/kouko/.herdr/worktrees/monkey-skills/obsidian-skill-3/docs/skill-dogfood/2026-09-24-obsidian-research/report.md:4)、[report.md:13](/Users/kouko/.herdr/worktrees/monkey-skills/obsidian-skill-3/docs/skill-dogfood/2026-09-24-obsidian-research/report.md:13)、[report.md:95](/Users/kouko/.herdr/worktrees/monkey-skills/obsidian-skill-3/docs/skill-dogfood/2026-09-24-obsidian-research/report.md:95)；`find ... -maxdepth 1` 只列 5 個檔案。 | 加入消毒後原始軌跡與 auditor outputs，否則把相關敘述標成未附證據。 |
| important | E | 執行器測的是首個 commit；第二 commit 才加入 citation pass、信心上限等行為修正，最終 HEAD 沒有端到端重跑。 | [report.md:10](/Users/kouko/.herdr/worktrees/monkey-skills/obsidian-skill-3/docs/skill-dogfood/2026-09-24-obsidian-research/report.md:10)、[report.md:97](/Users/kouko/.herdr/worktrees/monkey-skills/obsidian-skill-3/docs/skill-dogfood/2026-09-24-obsidian-research/report.md:97)；`git diff 96f81dade..HEAD` 顯示實質流程變更。 | 對 HEAD 重跑至少一個完整 executor＋citation audit。 |
| nit | H | 82 行「完整範例」重複九項 checkpoints，仍會產生版型錨定；刪除不會損失任何需求。 | [research-note-example.md:1](/Users/kouko/.herdr/worktrees/monkey-skills/obsidian-skill-3/obsidian/skills/obsidian-research/references/research-note-example.md:1)、[SKILL.md:76](/Users/kouko/.herdr/worktrees/monkey-skills/obsidian-skill-3/obsidian/skills/obsidian-research/SKILL.md:76) | 改成只展示 frontmatter、TOC 精確連結與引用格式的短片段。 |
| nit | F | 指定 pytest 未得到有效 suite 結果：3 passed、19 setup errors，全部因唯讀環境無可寫暫存目錄，不是產品失敗。 | `python3 -m pytest obsidian/tests -q -s -p no:cacheprovider` → `3 passed, 19 errors`; `FileNotFoundError: No usable temporary directory` | 在可寫暫存環境重跑後再宣稱測試通過。 |
| nit | G | PR description 無法核對；不能據此宣稱它準確或失準。 | `gh pr view 848 --json ...` → `error connecting to api.github.com`；瀏覽器存取亦不可用。 | 在可連 GitHub 的環境重新核對，尤其是第二 commit 後已變更的 source guidance 與 framework 結構。 |

### What is solid

- Pre-flight 到 Step 6 有明確 fallback、停止條件、反證查核與不覆寫保存規則；沒有循環引用或必然無法執行的步驟。
- Bardach、SCQA/Minto、空・雨・傘、What–Where–Why–How、歷史來源批判、Braun & Clarke 歸因、fishbone、5 Whys、PESTEL、Five Forces、3C、VRIO 本身未發現明顯事實錯誤。
- 原始 TSV 可重算為 58 筆：40/40 應觸發、12/12 負例、6/6 模糊例；connector 20/20。executor 的 TOC 12/12、來源 1–39、語言 38 ja／1 en 也吻合。結構檢查中 `obsidian-research` PASS，唯一 `wiki-setup` FAIL 未被本 PR 修改；兩份 manifest 都是 3.21.0，三語 README 與 CHANGELOG 已更新。