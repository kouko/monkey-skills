# 驗證紀錄

## 1. 核心功能檢查（Acceptance #1）
- 八個應用各有專節建置指引：
  - 巢狀畫布工作區（Canvas-in-Canvas） — `references/no-plugin-patterns.md` 章節 1
  - 研究雙畫布 — 章節 2
  - 資料管線文件化 — 章節 3
  - 稽核／事故檢討／onboarding — 章節 4
  - 教師班級畫布 — 章節 5
  - 世界觀基礎 — 章節 6
  - Bases 內嵌畫布 — 章節 7
  - Canvas-only Vault / 2D MOC — 章節 8
- 全部僅用核心功能：檢查 `references/no-plugin-patterns.md` 無提及任何外掛名稱
- Bases 版本註記：章節 7 標註「requires Obsidian 1.9+ (Bases core plugin)」
- 對抗性探針：10 份文件 × 1.9+ 標註檢查（逐行 grep "1.9+"）12 項全過

## 2. 巢狀畫布模板驗證（Acceptance #2）
- 模板存在：`assets/template-nested-workspace.canvas`
- Bundled validator 跑過：`python3 obsidian/skills/obsidian-canvas/scripts/validate_canvas.py assets/template-nested-workspace.canvas` → exit 0
- 內含：
  - 指向子畫布的嵌入節點（file node 含 subpath）
  - 指向說明節點（text node 說明此為父畫布）
  - 一個帶 `#Overview` 子路徑的筆記節點
  - 說明用 edge 連結筆節與子畫布參考
- Validator 自身 9 項測試也全過：`python3 -m pytest obsidian/tests/test_validate_canvas.py -q`

## 3. Canvas drift 反模式文件化（Acceptance #3）
- 新參考文件：`references/no-plugin-patterns.md` 第 9 節
- 明言：「Never keep hand-maintained status content as a live dashboard on a canvas」
- 引用兩週內失效的實證（見證據資料夾內 `drift-evidence/*.md`）
- 提供替代：live 資料直接在畫布上內嵌 Bases view 或 transclude 筆記
- SKILL.md 常見陷阱清單也加了同一條警告與指向（見 SKILL.md 第 305-306 行）

## 4. SKILL.md 路由（Acceptance #4）
- SKILL.md 新增了通往新參考文件與巢狀模板的路由：
  - 第 55-56 行：No-Plugin Advanced Patterns 小節標題
  - 第 57-58 行：說明文字指向 `references/no-plugin-patterns.md`
  - 第 59-60 行：說明巢狀工作區從 matching template 開始
  - 第 61-65 樣：表格列出 Pattern 與 Template 對應（含巢狀工作區）
- 所有引用路徑解析得到：`git ls-files` 檢查所有相對路徑存在
- 既有六種版型的檔案與 SKILL.md 原段落逐一比對：`git show b191144a2:obsidian/skills/obsidian-canvas-creator/SKILL.md` vs 現在版本，只見新增（diff 只有新增）

## 5. README／attribution 與版本一致（Acceptance #5）
- plugin 自身 README（英／日／繁中）補上新能力描述：
  - `README.md`：第 110 行 skill 表列描述更新
  - `README.ja.md`：同上
  - `README.zh-TW.md`：同上
- 各 skill README 都補上新能力描述：
  - `skills/README.md`：第 13 行
  - `skills/README.ja.md`：同上
  - `skills/README.zh-TW.md`：同上
- CHANGELOG 有 3.24.0 條目：`CHANGELOG.md` 頂部新條目
- attribution 原樣保留：
  - `ATTRIBUTION.md` 第 32 行：`obsidian/skills/obsidian-canvas/ | [LICENSE](obsidian/skills/obsidian-canvas/LICENSE) | Combines Axton Liu's canvas creator with kepano's json-canvas integration`
  - 技能表列保留 MIT 授權：`skills/README.md` 第 13 行
- 兩份 plugin manifest 都 bump 到 3.24.0：
  - `.claude-plugin/plugin.json`: `"version": "3.24.0"`
  - `.codex-plugin/plugin.json`: `"version": "3.24.0"`
- repo 的版本檢查 gate 與 Codex manifest 同步檢查都通過：
  - `python3 scripts/check_version_bump.py --base b191144a2 --head HEAD` → exit 0
  - `python3 scripts/sync_codex_manifests.py --check obsidian` → exit 0

## 測試紀錄
- 完整 package suite：`python3 -m pytest scripts/ -q` → 710 passed
- Validator 相關測試：
  - `obsidian/tests/test_validate_canvas.py` → 9 passed
  - `scripts/test_bases_version_note.py` → 3 passed
- 新增焦點測試：
  - `obsidian/tests/test_canvas_plugin_docs.py` → 4 passed
  - `obsidian/tests/test_canvas_skill_cross_references.py` → 2 passed

## 變更摘要
- 重命名目錄：`obsidian/skills/obsidian-canvas-creator` → `obsidian/skills/obsidian-canvas`（18 個檔案，全部為純重名）
- 編輯檔案：
  - `obsidian/skills/obsidian-canvas/SKILL.md`：name 欄位更新；description 增加「formerly obsidian-canvas-creator」
  - `obsidian/skills/obsidian-canvas/README.md / .ja.md / .zhtw.md`：標題由「Obsidian Canvas Creator」改為「Obsidian Canvas」
  - `obsidian/skills/README.md / .ja.md / .zhtw.md`：技能表列行更新
  - `obsidian/README.md / .ja.md / .zhtw.md`：技能表列與檔案樹更新
  - `obsidian/skills/using-obsidian/SKILL.md`：路由表列更新
  - `obsidian/skills/obsidian-research/SKILL.md`：引用更新
  - `ATTRIBUTION.md`：歸屬表列行更新
  - `obsidian/CHANGELOG.md`：新增 3.24.0 條目
  - `obsidian/.claude-plugin/plugin.json`：version 3.23.0 → 3.24.0
  - `obsidian/.codex-plugin/plugin.json`: version 3.23.0 → 3.24.0
  - `obsidian/tests/test_validate_canvas.py`：更新硬編碼路徑
  - `scripts/test_bases_version_note.py`：更新硬編碼路徑
- 未變更檔案（位元組相同）：
  - 所有 .canvas 模板（7 個）
  - 所有參考文件（5 個）
  - `scripts/validate_canvas.py`
  - `LICENSE`
  - `docs/loom/` 所有歷史紀錄
  - `.worktrees/` 所有舊副本