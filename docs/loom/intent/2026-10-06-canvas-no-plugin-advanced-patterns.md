# Canvas no-plugin advanced patterns
originator: kouko
kind: engineering
needs-design: no — skill content edits are pinned as the skill artifact type by the repo's interface-surfaces standing default; no CLI/API/commands surface touched; new templates stay under assets/
evidence: [docs/loom/2026-10-05-canvas-layout-templates-validator/spec.md, docs/loom/2026-10-05-canvas-layout-templates-validator/evidence/acceptance-test-evidence.md]
status: confirmed 2026-10-06
publication: automatic — authorized 2026-10-06 by kouko

## Problem
`obsidian/skills/obsidian-canvas-creator` 目前涵蓋六種單一畫布版型（MindMap、freeform、看板、儀表板、研究地圖、moodboard）。研究（reports/Obsidian Canvas 運用研究.md，位於 repo 外 `~/.herdr/obsidian-canvas-research/`）指出還有數種「只用 Obsidian 核心功能即可達成」的較複雜應用沒有被文件化：巢狀畫布（Canvas-in-Canvas）分層工作區、研究專案雙畫布（Research＋Results）、資料管線文件化、輸出即成品的稽核／事故檢討／onboarding map、教師班級畫布、世界觀建構基礎、Bases 嵌入畫布（1.9+ 核心功能）、以及 canvas-only vault／2D MOC 實驗。使用者要求這些應用時 skill 沒有對應指引；skill 也缺少「何時不該用 canvas（drift 反模式）」的警告——社群實證把 canvas 當持續維護的 live dashboard 兩週內失敗。

## Proposed outcome
skill 以零外掛（僅核心功能）文件化上述應用的做法：多畫布工作流（研究雙畫布、管線文件化、稽核／檢討／onboarding）、巢狀畫布結構（含一個模板）、Bases 內嵌（標注 1.9+）、canvas-only／2D MOC 的做法與限制、以及「何時不該用 canvas」的 drift 反模式。

## Acceptance
1. skill 內有每一個上述應用的建置指引（巢狀畫布、研究雙畫布、資料管線、稽核／事故檢討／onboarding、教師班級、世界觀基礎、Bases 內嵌、canvas-only／2D MOC），全部僅用核心功能；Bases 指引標注需要 Obsidian 1.9+。
2. 巢狀畫布有可用且通過驗證器的 `.canvas` 模板（含嵌入的子畫布節點與指向說明）。
3. skill 文件化 canvas drift 反模式：哪些場景不該用 canvas（持續維護的 live dashboard），與該改用什麼。
4. SKILL.md 路由到新的文件；既有六種版型的行為不變。
5. plugin README／attribution 與新能力一致，plugin 版本依 repo gate bump（skill 內容變動）。

## Constraints
- 內容英文；零外掛：每個技術僅用 Obsidian 核心功能（Bases 以 1.9+ 條件式說明）；不新增 runtime 依賴與腳本。
- 既有六種版型（MindMap、freeform、看板、儀表板、研究地圖、moodboard）行為不變。
- 模板放 assets/（不放 templates/）。
- 保留並更新 MIT attribution（Axton Liu + kepano json-canvas + 本 repo 衍生修改）。

## Out of scope
- 任何需要社群外掛的應用（Dataview 儀表板、Metadata Menu、Hover Editor、Canvas Kanban Sync、Advanced Canvas 的簡報/Portal/摺疊群組/形狀/PDF 標註、Enhanced Canvas、Caret、AI 擴充）。
- 驗證器行為擴充（維持現有五項檢查）。
- 新增文件的日／繁中翻譯（僅 README 同步）。

## Open questions
- none
