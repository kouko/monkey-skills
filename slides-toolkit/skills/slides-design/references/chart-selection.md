# Chart selection — 資料形態 → chart type 對照

**Primary sources**：
- Cleveland & McGill (1984) "Graphical Perception: Theory, Experimentation, and Application to the Development of Graphical Methods" *Journal of the American Statistical Association* 79(387):531–554. — 視覺編碼準確度排序原典
- Few (2012) *Show Me the Numbers: Designing Tables and Graphs to Enlighten* 2nd ed. Analytics Press. — 資料對照 chart 的 practitioner canonical

本 reference 幫助決定「這組資料該用哪種圖表」。**MVP 不含圖表生成**（PRODUCT-SPEC §3.2 Non-Goal）；使用者自行用 matplotlib / Excel / Sheets 產 PNG，再填入 slide-plan 的 `images[].local_path`。

---

## 1. 資料形態 → chart type 對照表

| 資料形態 | 首選 | 備選 | Warning |
|---|---|---|---|
| **比較類別**（e.g. 各地區 revenue、各產品市佔） | **Horizontal bar** | Vertical bar | 類別 > 8 個 → horizontal 易讀 > vertical |
| **時序趨勢**（e.g. 月 revenue、股價） | **Line** | Area（強調量級） | 點數 < 6 → 改 bar（line 不穩） |
| **部分 vs 整體**（e.g. 市佔、預算分配） | **Stacked bar** | Bar（百分比標註）、Pie（slice ≤ 5） | **Pie slice > 5 一律改 bar**（Cleveland 1984：角度比長度難辨） |
| **兩變數相關**（e.g. 價格 vs 銷量） | **Scatter** | Bubble（+第三變數） | 點數 > 500 → 加 jitter / alpha，避免 overplot |
| **分布**（e.g. 客戶年齡分布、response time） | **Histogram** | Box plot、Density plot | Box plot 適合跨類別比分布 |
| **時間事件**（e.g. 產品 roadmap、里程碑） | **Timeline** | Gantt（含期間） | 事件 > 20 → 分群或改 table |
| **多維度比較**（e.g. 產品多屬性評分） | **Heatmap** | Radar（≤ 6 維） | Radar 維度 > 6 不可讀；改 heatmap |
| **網路關係**（e.g. 組織架構、依賴圖） | **Node-link graph** | Hierarchy tree（Phase 2+） | MVP 少用；推薦 ASCII / mermaid 代替 |
| **單一關鍵數字**（e.g. NPS = 72） | **Big number**（大字） | Bullet chart（含 target） | 別用 Pie 畫單一比例（浪費畫面） |

---

## 2. Cleveland & McGill (1984) 視覺編碼準確度排序（核心依據）

Cleveland 1984 實驗證明：人眼對不同視覺編碼的**判讀準確度**由高到低排序：

```
1. Position on common scale              ←  bar / scatter x-axis（首選）
2. Position on non-aligned scale         ←  small multiples
3. Length                                 ←  bar length
4. Angle / slope                          ←  line chart 斜率
5. Area                                   ←  bubble / treemap
6. Volume / curvature                     ←  3D chart（通常別用）
7. Shading / colour saturation            ←  heatmap
```

**Because Pie chart 排序靠後**：Pie 用 **angle + area** 同時編碼（#4+#5），Bar 用 **length on common scale**（#1+#3）。當 slice > 5，讀者難判大小差異。**預設改 Bar**。

---

## 3. Decision tree — 3 個問題選 chart type

```
Q1. 資料是連續的時間序列嗎？
    YES → Line chart（點數 ≥ 6）或 Bar（點數 < 6）
    NO  → 繼續 Q2

Q2. 我要強調「比較」「組成」「關係」「分布」中哪一個？
    比較 → Bar（類別 ≤ 30）／ Table（類別 > 30 或需精確值）
    組成 → Stacked bar ／ Bar + % label ／ Pie（slice ≤ 5）
    關係 → Scatter（2 變數）／ Bubble（3 變數）
    分布 → Histogram（1 變數）／ Box plot（跨類別分布）

Q3. Slide 的 Pyramid 角色是「結論」還是「證據」？
    結論 → Big number + 一行註解（不用複雜圖）
    證據 → 依 Q1/Q2 選；加 annotation 標出關鍵點
```

---

## 4. Slide-plan 對照：chart type → layout_hint

MVP 的 `slide-plan.json` `slides[].layout_hint` 為**通用 hint**（非強制對應）。建議 mapping：

| Chart type | 建議 `layout_hint` | `replacements` / `images` |
|---|---|---|
| Big number | `title-body` | `{{title}}` = 結論 / `{{body}}` = 大字數值 |
| Bar / Line / Scatter（單圖） | `headline-image` | `{{headline}}` = 結論 / `images[].local_path` = chart PNG |
| Stacked bar + 說明 | `headline-image` + bullets | headline + left image + right bullets |
| Table（精確值） | `title-body` | body 放 markdown-style table |
| Quote / 關鍵金句 | `quote` | 單句加作者 |

**Example**：

```
Slide 5 要呈現「APAC 占 45% revenue」：
  - 結論性 → 用 Big number 編碼
  - layout_hint: "title-body"
  - replacements: {"{{title}}": "APAC 驅動 45% revenue", "{{body}}": "45%"}

Slide 6 要呈現「APAC 內 8 個國家 revenue 排序」：
  - 比較類別 + > 5 項 → horizontal bar
  - layout_hint: "headline-image"
  - replacements: {"{{headline}}": "Japan + Taiwan 合計占 APAC 60%"}
  - images[].local_path: "~/Desktop/apac_countries_bar.png"
```

---

## 5. 常見錯誤

| 錯誤 | 原因 | 修法 |
|---|---|---|
| 8 slice Pie chart | 美觀慣性 | 改 horizontal bar（Cleveland 1984 #1 vs #4） |
| 3D bar / 3D pie | 裝飾 | 拿掉 3D；Cleveland #6 最差 |
| Dual y-axis line | 想同時展兩單位量 | 拆成 2 張 small multiples |
| Stacked bar slice > 5 | 部分 vs 整體但類別太多 | 聚合小 slice 成 "Other"；或改 side-by-side bar |
| Scatter 但點數 < 10 | 無 distribution 可看 | 改 bar + label |
| Line 但資料是類別（非時間） | 誤用 line 造成假 trend | 改 bar |

---

## 6. MVP scope 提醒

- ✅ **本 reference 幫你選 chart type**
- ❌ **本 reference 不產生圖表**（Non-Goal PRODUCT-SPEC §3.2；MVP 無 matplotlib / Python runtime）
- ❌ **不做自動 chart → slide 插入**（由 builder 的 `recipe-insert-image.md` 處理 PNG 上傳）

使用者需**自行**在 matplotlib / Excel / Sheets / Plotly 產好 PNG，路徑填進 `slide-plan.json` 的 `images[].local_path`。

---

## 7. Phase 2+ 擴展（trigger-gated）

| 擴展 | Primary source | Trigger |
|---|---|---|
| Small multiples / sparkline 深化 | Tufte (2001) *The Visual Display of Quantitative Information* 2nd ed. Graphics Press | 週報 deck 需 dashboard-style 比較 |
| Dashboard design | Few (2013) *Information Dashboard Design* 2nd ed. | 出現 dashboard-style deck 需求 |
| 動態圖表生成（CSV → PNG） | matplotlib / plotnine | 首次真實 chart-generation 需求（PRODUCT-SPEC §3.5） |
| Node-link / hierarchy graph | Munzner (2014) *Visualization Analysis and Design* CRC Press | 出現網路 / 組織 / 依賴關係場景 |

MVP 不展開以上 reference；Cleveland & McGill (1984) 排序原理 + 上述對照表已足以覆蓋商業 deck ≥ 80% 場景。
