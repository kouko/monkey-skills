# Canvas skill layout templates + output validator
originator: kouko
kind: engineering
needs-design: no — skill content edits are pinned as the skill artifact type by the repo's interface-surfaces standing default (SKILL.md is not a user interface); the validator script is agent-invoked, not a CLI/API/commands surface; no interface-surface glob matches
map: 
evidence: [reports/Obsidian Canvas 運用研究.md, research_notes/Obsidian Canvas 運用研究/community-use-cases.md, research_notes/Obsidian Canvas 運用研究/professional-industry-use.md, research_notes/Obsidian Canvas 運用研究/ecosystem-best-practices.md]
status: confirmed 2026-10-05
publication: automatic — authorized 2026-10-05 by kouko

## Problem
`obsidian/skills/obsidian-canvas-creator` 只支援兩種版型（MindMap、freeform）。2026-10 的研究（見 evidence）顯示 Obsidian 社群實際使用收斂為六大模式，其中看板（kanban）、儀表板／首頁、研究地圖、moodboard 四種是主流用法，skill 完全沒有對應的版型規則或範例，使用者要求這些版型時 LLM 只能自行發揮。另外，skill 產出的 `.canvas` 檔品質完全依賴 LLM 遵守 SKILL.md 的文字規則自我檢查，沒有任何程式可以機器驗證（ID 重複、edge 引用不存在、節點重疊、缺必要欄位），錯誤檔案要等使用者匯入 Obsidian 才會發現。

## Proposed outcome
skill 能依看板／儀表板（首頁）／研究地圖／moodboard 四種社群常用版型產生 `.canvas` 檔；並提供一個驗證腳本，能對產出或既有的 `.canvas` 檔做結構正確性檢查，錯誤能被指名道姓地報告，且有自動化測試保護。

## Acceptance
1. skill 內有四種新版型（看板、儀表板／首頁、研究地圖、moodboard）各自的版型規則文件（節點組成、群組、連線、顏色語意）。
2. 依 skill 對四種新版型任一種的請求，產出的 `.canvas` 檔結構符合該版型的規則。
3. 驗證腳本能檢查 `.canvas` 檔：JSON 可解析、ID 為唯一的 16 字元小寫 hex、edge 的 fromNode/toNode 都存在、各節點型別必要欄位齊全、節點無重疊；乾淨的檔案以 exit 0 通過，任何違規以非零結束並逐項指出違規內容。
4. 驗證腳本有自動化測試，併入 repo 既有 pytest 測試套件後全數通過。
5. plugin README 與 skill attribution 表更新到與新能力一致。

## Constraints
- skill 內容維持英文（現有 skill 慣例）。
- 驗證腳本僅用 Python 標準庫，不新增 runtime 依賴。
- 測試併入 repo 既有 pytest 套件（`python3 -m pytest`）。
- 既有 MindMap 與 freeform 版型行為不變。
- 保留並更新 skill 的 MIT attribution（Axton Liu + Steph Ango json-canvas），標註本 repo 的衍生修改。

## Out of scope
- 上游同步（axtonliu、kepano，含 knap skill）。
- 程式化產生 canvas 版型（腳本只驗證、不生成）。
- JSON Canvas 規格之外的節點型別、協作編輯、Obsidian 本體外掛功能。
- 新增參考文件的日文／繁中翻譯。

## Open questions
- none
