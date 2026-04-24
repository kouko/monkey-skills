# Slide-plan self-check rubric

**用途**：draft 完 `slide-plan.json` 後、交給 `google-slides-builder`（或 Phase 2+ 其他 backend builder）前，跑以下 binary checklist 做 advisory self-check。

**性質**：**Advisory only**——MVP 不 hard-gate（不阻擋 pipeline）。目的是在執行前捕捉常見敘事 / layout / 資產問題，降低 deck 生成後的人工微調時間。

**何時用**：
- draft `slide-plan.json` 完成後
- 交給 builder 執行前
- 懷疑 deck 品質不穩定時，拿這份回頭檢查

---

## Checklist（9 項；全 binary）

### 敘事與資訊層級

- [ ] **每張 slide 只有一個主結論** — `replacements.{{title}}` / `{{headline}}` 只出現 1 個論點；一頁多結論 → 拆頁（Minto 1987）
- [ ] **Title 可獨立讀懂（不依賴口頭補充）** — 讀每張 slide 的 title，能否單獨理解該頁訊息？若只看到「Revenue breakdown」→ 改寫為結論式 title（例「APAC 驅動 45% revenue」）
- [ ] **敘事流有開場（SCQA）與結構（Minto Pyramid）** — 第 1–2 頁能辨識到 Situation → Complication → Question → Answer；中段依 Pyramid 主幹分支展開，sibling slides MECE（互斥且窮盡）

### 視覺與 layout

- [ ] **圖表選型合理** — 每個 chart 依 `references/chart-selection.md` 的對照表選型（Pie slice > 5 已改 Bar；類別比較用 Bar；時序用 Line；部分 vs 整體且 slice ≤ 5 才用 Pie）
- [ ] **`layout_hint` 欄位與內容匹配** — 有 image 的 slide 設 `headline-image`；純文字結論設 `title-body`；金句設 `quote`；與實際 `replacements` / `images` 內容一致

### 資產與 placeholder 對位

- [ ] **圖片路徑已確認存在** — 每個 `slides[].images[].local_path` 指向的本機檔案實際存在（`ls` 驗證）；無 broken path
- [ ] **Placeholder 命名對應 template** — `replacements` 的 key（e.g. `{{title}}`, `{{headline}}`, `{{date}}`）與 template deck 內的 placeholder 一致；參照 `google-slides-builder/templates/registry.md` 確認

### Backend 設定

- [ ] **`target` 欄位設為 `"google-slides"`** — MVP 唯一支援 backend；缺欄或設為 `"html"` / `"pptx"` / `"marp"` → builder exit 12（Phase 2+ trigger 未達）

### 安全

- [ ] **無敏感資訊** — `replacements` 內無 credential / API key / PII / 未遮蔽的個資；`images[].local_path` 非 screenshot of credential / token 等敏感內容

---

## 使用方式

### 對 Claude

逐項過 checklist；每項 PASS 打勾，FAIL 記錄具體問題 + 修法建議。全部跑完產出一段 summary：

```
Self-check summary：
  ✅ 8 / 9 passed
  ❌ 1 failed: 「Title 可獨立讀懂」— slide 3 title 「Revenue breakdown」為主題非結論
  建議修法：改寫為 「APAC 驅動 Q1 45% YoY」
```

### 對使用者

跑完後：
- 全 pass → 可交給 builder
- 有 fail → 視嚴重度決定是否修（MVP advisory，不強制 block）
- 敏感資訊 fail → **建議 block**（非 hard-gate，但強烈建議先修）

---

## 與 hard-gate 的關係

MVP **沒有** hard-gate（見 PRODUCT-SPEC §3.2 Non-Goal「design-quality-gate」）。kouko 親自當 gate。Phase 2+ 若 publish 給外部使用者，可能升級此 rubric 為 hard-gate（trigger：外部使用者需不依賴 kouko 判斷）。

---

## Primary sources（rubric 依據）

- Minto (1987) *The Pyramid Principle* — 「每張 1 個結論」、「Title 可獨立讀懂」、SCQA 開場
- Cleveland & McGill (1984) — 圖表選型準則
- Few (2012) *Show Me the Numbers* 2nd ed. — chart type 對照
- 本 plugin PRODUCT-SPEC v0.2 §4.4 design principles — backend-agnostic、credential never in repo
- 本 plugin TECH-SPEC v0.2 §4.1 — schema v1.1（`target` 欄位）
