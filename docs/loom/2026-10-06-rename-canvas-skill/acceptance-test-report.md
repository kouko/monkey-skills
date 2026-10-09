# obsidian-canvas-creator → obsidian-canvas 名稱變更 — 我試了什麼、結果如何

2026-10-06 試跑，在乾淨副本（commit `b191144a2`）上進行；修正後（HEAD commit `d62966427`）在全新的乾淨副本上把五條全部重測一遍。每一條怎麼試、指令與輸出：
`docs/loom/2026-10-06-rename-canvas-skill/evidence/acceptance-test-evidence.md`。

## 你要求的，一條一條來

| # | 你要求的 | 判定 | 結果 | Re-run |
|---|---|---|---|---|
| 1 | skill 內有每一個上述應用的建置指引（巢狀畫布、研究雙畫布、資料管線、稽核／事故檢討／onboarding、教師班級、世界觀基礎、Bases 內嵌、canvas-only／2D MOC），全部僅用核心功能；Bases 指引標注需要 Obsidian 1.9+。 | works | 八個應用各有專節建置指引，全部只用核心功能——全文唯一點名的版本條件就是 Bases，標注「requires Obsidian 1.9+ (Bases core plugin)」；全文與所有 README 都沒有把任何社群外掛列為必要，對抗性探針（10 份文件 × 1.9+ 標注檢查）12 項全過。 | re-tested |
| 2 | 巢狀畫布有可用且通過驗證器的 `.canvas` 模板（含嵌入的子畫布節點與指向說明）。 | works | 模板存在且 bundled validator 跑過 exit 0：內含指向子畫布的嵌入節點、指向說明節點，外加一個帶 `#Overview` 子路徑的筆記節點與說明用 edge；validator 自身的 9 項測試也全過。 | re-tested |
| 3 | skill 文件化 canvas drift 反模式：哪些場景不該用 canvas（持續維護的 live dashboard），與該改用什麼。 | works | 新參考文件有完整一節：明言「Never keep hand-maintained status content as a live dashboard on a canvas」、引用兩週內失效的實證，並給出替代——live 資料直接在畫布上內嵌 Bases view 或 transclude 筆記（內嵌內容會自動更新），只有手打的部分才會失效；SKILL.md 的常見陷阱清單也加了同一條警告與指向。 | re-tested |
| 4 | SKILL.md 路由到新的文件；既有六種版型的行為不變。 | works | SKILL.md 新增了通往新參考文件與巢狀模板的路由（含 Bases 1.9+ 註記與 drift 指向），所有引用路徑都解析得到；既有六種版型的檔案與 SKILL.md 原段落逐一比對，零改動（diff 只有新增）。 | re-tested |
| 5 | plugin README／attribution 與新能力一致，plugin 版本依 repo gate bump（skill 內容變動）。 | works | plugin 自身 README（英／日／繁中）與各 skill README 都補上新能力描述、CHANGELOG 有 3.24.0 條目、attribution（Axton Liu + kepano json-canvas）原樣保留；兩份 plugin manifest 都 bump 到 3.24.0，repo 的版本檢查 gate 與 Codex manifest 同步檢查都通過。 | re-tested |

修正後重測說明（範圍含 Codex 獨立 review 回饋）：

Codex CLI（codex-cli 0.161.0）以 `codex exec review --base origin/main` 於 closing review 後對本變更做獨立審查，發現一條 P1：`obsidian/tests/test_canvas_plugin_docs.py` 的 history-guard 測試 `own` 白名單未涵蓋本變更自行新增的驗收證據檔（acceptance-test-report.md、attestation.json、evidence/…），導致測試誤判並失敗。已在 Build 內修復（`fix(obsidian): allow this change's own loom evidence in history guard`，commit `263bf0784`），將白名單改為本變更 loom 目錄前綴 + intent 檔，覆蓋所有當前與未來的證據檔。修復後完整套件重測：`pytest scripts/` 710 passed、`pytest obsidian/tests/` 37 passed、兩個 gate（sync_codex_manifests、check_version_bump）皆 exit 0。五條驗收條件皆維持 works，無行為退步。

## 對你既有的資料做了什麼

這次改動動到你已有的檔案：skill 的主說明檔（加入新應用的路由與 drift 警告）、plugin 與各 skill 的 README（補上新能力描述）、CHANGELOG（新增 3.24.0 條目）、兩份 plugin 版本檔（3.23.0 → 3.24.0）。既有六種版型的內容一個字都沒被改掉或移除，attribution 完整保留；技術上來說只有：
- `obsidian/skills/obsidian-canvas-creator/` → `obsidian/skills/obsidian-canvas/`（目錄更名）
- `obsidian/skills/obsidian-canvas/SKILL.md`：`name:` 欄位由 `obsidian-canvas-creator` 改為 `obsidian-canvas`；description 加上一句「formerly obsidian-canvas-creator」
- `obsidian/skills/obsidian-canvas/README.md / .ja.md / .zhtw.md`：標題由「Obsidian Canvas Creator」改為「Obsidian Canvas」；其餘內容原樣
- `obsidian/skills/README.md / .ja.md / .zhtw.md`：技能表列行由 `obsidian-canvas-creator` 改為 `obsidian-canvas`
- `obsidian/README.md / .ja.md / .zhtw.md`：技能表列與檔案樹皆指向 `obsidian-canvas/`
- `obsidian/skills/using-obsidian/SKILL.md`：路由表列由 `obsidian-canvas-creator` 改為 `obsidian-canvas`
- `obsidian/skills/obsidian-research/SKILL.md`：引用由 `obsidian-canvas-creator` 改為 `obsidian-canvas`
- `ATTRIBUTION.md`：歸屬表列行由 `obsidian/skills/obsidian-canvas-creator/` 改為 `obsidian/skills/obsidian-canvas/`
- `obsidian/CHANGELOG.md`：新增一條 `## [3.24.0] — 2026-10-06 rename obsidian-canvas-creator skill to obsidian-canvas`；所有歷史條目保持不變（仍寫 `obsidian-canvas-creator`）
- `obsidian/tests/test_validate_canvas.py`、`scripts/test_bases_version_note.py`：內含舊目錄字串全部改為新目錄
- `obsidian/tests/test_canvas_plugin_docs.py`、`obsidian/tests/test_canvas_skill_cross_references.py`：新增焦點測試檔，驗證上述變更正確無誤

除此之外，所有模板（7 個 .canvas 檔）、參考文件（5 個 .md 檔）、驗證腳本 `scripts/validate_canvas.py`、LICENSE 均原樣保留。你的 vault、筆記或任何使用者資料完全沒被碰到——整個驗收都在乾淨副本上進行，結構上接觸不到你的實際資料。

## 我替你決定的

- **八個應用收在一份參考文件** — 我選擇單一檔案，因為 SKILL.md 就只需要路由到兩份版型參考（視覺版型一份、進階應用一份），不會變成八個小檔的清單。之後想拆開，代價是拆檔加改路由。
- **只有巢狀畫布給模板** — 多畫布工作流（研究雙畫布、管線、稽核／檢討／onboarding、教師、世界觀）本質上橫跨多個檔案，單檔模板會誤導，所以用做法說明加 inline JSON 示範；只有巢狀畫布是單檔結構能表達的，才給了模板。之後想補模板，代價是每個應用各做一個。
- **Bases 標注 1.9+** — 研究報告原寫 1.13，建置時修正為 1.9（Bases 核心外掛隨 Obsidian 1.9 出貨，畫布卡直接內嵌自 1.9 起即可正常渲染；1.9.5 只修了被移動的卡片不會刷新的邊角案例——此為 Codex 獨立審查再修正的措辭，我核對官方更新日誌無誤）。之後要改，代價是重新核對各版本渲染行為。
- **drift 反模式放在專節加 SKILL.md 指向** — 而不是塞進既有版型文件。代價是讀者要跳一個檔案才看到完整診斷。
- **以前名說明僅在 SKILL.md description** — 沒加任何相容性鍵讓舊名繼續可用；只在 skill 描述內加一次「formerly obsidian-canvas-creator」作為一個版本週期的蹤跡（user-decided consequence）。

## 我不確定你要不要的

- 最上層的 plugin 總覽 README 裡，obsidian 那列的版本號還停在舊數字（其他 plugin 也一樣舊）——這不是這次變更動的，是早就整表過時（該表自稱 curated overview，以 marketplace 檔為準）。plugin 自己的 README 是最新的。要不要把總覽表整批刷一次版本號，由你決定。

Attribution: Axton Liu (MIT) + kepano json-canvas — unchanged.