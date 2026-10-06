# Rename obsidian-canvas-creator skill to obsidian-canvas
originator: kouko
kind: engineering
needs-design: no — skill content edits are pinned as the skill artifact type by the repo's interface-surfaces standing default (SKILL.md and skill docs are not a user interface); the rename changes the skill's internal identifier and repo-internal cross references only, no interface-surface glob matches
map: 
evidence: [docs/loom/2026-10-06-canvas-no-plugin-advanced-patterns/acceptance-test-report.md]
status: open
publication: automatic — authorized 2026-10-06 by kouko

## Problem
Obsidian plugin 的 canvas skill 名為「canvas-creator」，是從上游（axtonliu）匯入時的遺留名稱。2026-10 的兩輪變更（3.22.0 版型規則＋驗證器、3.23.0 零外掛進階應用）之後，這個 skill 的實際範圍已經遠超「建立」：它還涵蓋編輯既有畫布、輸出驗證、八種多畫布工作流，以及「何時不要用 canvas」的治理指引。名稱低估了範圍，與同 plugin 內偏功能域命名的兄弟 skill（markdown、bases、research、cli）不一致，使用者與 LLM 在閱讀 skill 清單時需要多猜一次「creator」是什麼意思。

## Proposed outcome
skill 更名為 `obsidian-canvas`，讓名稱與實際能力範圍相符；改名後所有 repo 內的活文件（README、路由、交叉引用、attribution、測試）都指向新名稱，舊名稱在文件中以更名說明保留一次性蹤跡。

## Acceptance
1. skill 資料夾與 skill 名稱（SKILL.md 的 name 欄位）改為 `obsidian-canvas`，skill 內容（模板、參考文件、驗證器）原樣保留。
2. repo 內所有活的交叉引用（plugin README 三語、skills README 三語、using-obsidian 路由、obsidian-research 交叉引用、ATTRIBUTION、CHANGELOG 新條目）指向 `obsidian-canvas`；attribution 中 axtonliu／kepano 的授權標註原樣保留並加註更名。
3. 引用舊資料夾路徑的自動化測試與 repo 檢查（validator 測試、bases 版本註記測試、Codex manifest 同步、版本檢查 gate）全部通過。
4. 描述欄位標注一次舊名（formerly obsidian-canvas-creator），兩份 plugin manifest 版本 bump。
5. `docs/loom/` 歷史紀錄與 `.worktrees/` 舊副本不改動。

## Constraints
- skill 內容維持英文（現有 skill 慣例）。
- 純改名：skill 的行為、模板、參考文件內容不變；不順手做任何內容改寫。
- 保留 MIT attribution（Axton Liu + kepano json-canvas），加註本 repo 的更名事實。
- plugin 版本依 repo gate bump（skill 內容與結構變動）。

## Out of scope
- 上游同步（axtonliu、kepano）。
- docs/loom/ 歷史紀錄與 .worktrees/ 內的舊副本。
- skill 內容的任何重寫、翻譯或功能變更。
- plugin 對外的別名機制（讓舊名繼續可用的 alias）。

## Open questions
- none
