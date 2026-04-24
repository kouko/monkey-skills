# Chart selection — data shape to chart type reference

**Primary sources**:
- Cleveland, W.S. & McGill, R. (1984) "Graphical Perception: Theory, Experimentation, and Application to the Development of Graphical Methods" *Journal of the American Statistical Association* 79(387):531–554. Canonical ranking of visual-encoding accuracy.
- Few, S. (2012) *Show Me the Numbers: Designing Tables and Graphs to Enlighten* 2nd ed. Analytics Press. Practitioner canon for matching data shape to chart type.

This reference helps you decide **which chart type** fits a given dataset. **MVP does not generate charts** (PRODUCT-SPEC §3.2 Non-Goal). Produce the PNG yourself with matplotlib / Excel / Sheets and pass the path to `slide-plan.json` `images[].local_path`.

---

## 1. Data-shape to chart-type table

| Data shape | First choice | Alternative | Warning |
|---|---|---|---|
| **Category comparison** (カテゴリ比較 / 類別比較) — regional revenue, product market share | **Horizontal bar** (棒グラフ / 長條圖) | Vertical bar | > 8 categories: horizontal reads better than vertical |
| **Time series** (時系列 / 時序趨勢) — monthly revenue, stock price | **Line chart** (折れ線グラフ / 折線圖) | Area chart (highlights magnitude) | < 6 points: switch to bar (line is unstable) |
| **Part-to-whole** (構成比 / 部分 vs 整體) — market share, budget allocation | **Stacked bar** (積み上げ棒 / 堆疊長條) | Bar with % labels; Pie when slices ≤ 5 | **Pie with > 5 slices: always switch to bar** (Cleveland 1984: angle is harder to read than length) |
| **Correlation** (相関 / 相關性) — price vs volume | **Scatter plot** (散布図 / 散點圖) | Bubble chart (adds third variable) | > 500 points: add jitter / alpha to avoid overplot |
| **Distribution** (分布 / 分布) — age distribution, response time | **Histogram** (ヒストグラム / 直方圖) | Box plot, density plot | Box plot is better for comparing distribution across categories |
| **Timeline / milestones** (年表 / 時間軸) — roadmap, project milestones | **Timeline** | Gantt chart (with durations) | > 20 events: group them or switch to a table |
| **Multi-attribute comparison** (多次元比較 / 多維度比較) — product scorecard | **Heatmap** (ヒートマップ / 熱度圖) | Radar chart (≤ 6 axes) | Radar with > 6 axes is unreadable; use heatmap |
| **Network / relationships** (ネットワーク / 網路關係) — org chart, dependency graph | **Node-link graph** (ノードリンク図 / 節點連結圖) | Hierarchy tree (Phase 2+) | Use sparingly in MVP; ASCII or mermaid is often enough |
| **Single key number** (大型数字 / 單一關鍵數字) — NPS = 72 | **Big number** (大きな数字 / 大型數字) | Bullet chart (with target line) | Do not draw a single ratio as a pie (wastes the canvas) |

### Utterance triggers by data shape

Use these phrase patterns to recognize intent before picking a chart type.

- **Category comparison** (カテゴリ比較 / 類別比較)
  - EN: "compare by category", "rank these", "which is biggest"
  - JP: 「カテゴリで比較」「ランキング」「どれが一番多い」
  - ZH: 「各類比較」「排名」「哪個最多」
- **Time series** (時系列 / 時序趨勢)
  - EN: "trend over time", "monthly change", "growth curve"
  - JP: 「時系列で」「月ごとの推移」「成長トレンド」
  - ZH: 「隨時間變化」「每月走勢」「成長曲線」
- **Part-to-whole** (構成比 / 部分 vs 整體)
  - EN: "share of total", "breakdown", "composition"
  - JP: 「全体の内訳」「構成比」「シェア」
  - ZH: 「占比」「組成比例」「份額」
- **Correlation** (相関 / 相關性)
  - EN: "does X drive Y", "relationship between", "correlation"
  - JP: 「XとYの関係」「相関」「連動」
  - ZH: 「X 和 Y 的關係」「相關性」「連動」
- **Distribution** (分布 / 分布)
  - EN: "how are they spread", "distribution", "histogram"
  - JP: 「ばらつき」「分布」「ヒストグラム」
  - ZH: 「分布情況」「分布」「直方圖」

---

## 2. Cleveland & McGill (1984) visual-encoding accuracy ranking

Cleveland 1984 experimentally ranked how accurately the eye decodes different visual encodings, from best to worst:

```
1. Position on common scale              ← bar / scatter x-axis (first choice)
2. Position on non-aligned scale         ← small multiples
3. Length                                 ← bar length
4. Angle / slope                          ← line chart slope
5. Area                                   ← bubble / treemap
6. Volume / curvature                     ← 3D chart (usually avoid)
7. Shading / colour saturation            ← heatmap
```

**Why pie chart (円グラフ / 圓餅圖) ranks low**: pie encodes with **angle + area** (#4 + #5) at the same time. Bar encodes with **length on a common scale** (#1 + #3). Once slices exceed five, readers cannot reliably judge size differences. Default to bar.

---

## 3. Decision tree — three questions to pick a chart type

```
Q1. Is the data a continuous time series?
    YES → Line chart (≥ 6 points) or bar (< 6 points)
    NO  → go to Q2

Q2. Am I emphasizing comparison, composition, relationship, or distribution?
    Comparison   → Bar (≤ 30 categories) / Table (> 30 or exact values needed)
    Composition  → Stacked bar / Bar + % labels / Pie (≤ 5 slices)
    Relationship → Scatter (2 variables) / Bubble (3 variables)
    Distribution → Histogram (1 variable) / Box plot (across categories)

Q3. Is this slide's Pyramid role "conclusion" or "evidence"?
    Conclusion → Big number + one-line note (skip the complex chart)
    Evidence   → Pick by Q1 / Q2; add an annotation that marks the key point
```

---

## 4. Slide-plan mapping — chart type to layout_hint

The `slide-plan.json` `slides[].layout_hint` field is a **generic hint** (not a hard binding). Suggested mapping:

| Chart type | Suggested `layout_hint` | `replacements` / `images` |
|---|---|---|
| Big number | `title-body` | `{{title}}` = conclusion / `{{body}}` = the number |
| Bar / line / scatter (single chart) | `headline-image` | `{{headline}}` = conclusion / `images[].local_path` = chart PNG |
| Stacked bar + commentary | `headline-image` + bullets | headline + left image + right bullets |
| Table (exact values) | `title-body` | body holds a markdown-style table |
| Quote / pull quote | `quote` | single sentence plus attribution |

**Example**:

```
Slide 5 shows "APAC is 45% of revenue":
  - This is a conclusion → Big number encoding
  - layout_hint: "title-body"
  - replacements: {"{{title}}": "APAC drives 45% of revenue", "{{body}}": "45%"}

Slide 6 shows "Revenue ranking across 8 APAC countries":
  - Category comparison with > 5 items → horizontal bar
  - layout_hint: "headline-image"
  - replacements: {"{{headline}}": "Japan + Taiwan together account for 60% of APAC"}
  - images[].local_path: "~/Desktop/apac_countries_bar.png"
```

---

## 5. Common mistakes

| Mistake | Why it happens | Fix |
|---|---|---|
| 8-slice pie chart (円グラフ / 圓餅圖) | Aesthetic habit | Horizontal bar (Cleveland 1984 #1 vs #4) |
| 3D bar / 3D pie | Decoration | Drop the 3D; Cleveland #6 is the worst encoding |
| Dual-y-axis line chart | Wanting two units on one plot | Split into two small multiples |
| Stacked bar with > 5 slices | Part-to-whole with too many categories | Aggregate small slices into "Other", or switch to side-by-side bar |
| Scatter plot with < 10 points | No distribution visible | Switch to bar with labels |
| Line chart on categorical data | Misread as a trend | Switch to bar |

---

## 6. MVP scope reminder

- Yes: this reference helps you **pick** a chart type
- No: this reference does **not generate charts** (Non-Goal PRODUCT-SPEC §3.2; MVP has no matplotlib / Python runtime)
- No: no automatic chart-to-slide insertion (the builder's `recipe-insert-image.md` handles PNG upload)

Produce the PNG yourself in matplotlib / Excel / Sheets / Plotly and pass the path to `slide-plan.json` `images[].local_path`.

---

## 7. Phase 2+ extensions (trigger-gated)

| Extension | Primary source | Trigger |
|---|---|---|
| Small multiples / sparkline deep-dive | Tufte (2001) *The Visual Display of Quantitative Information* 2nd ed. Graphics Press | Weekly-report deck needs dashboard-style comparison |
| Dashboard design | Few (2013) *Information Dashboard Design* 2nd ed. | Dashboard-style deck request arrives |
| Dynamic chart generation (CSV → PNG) | matplotlib / plotnine | First real chart-generation request (PRODUCT-SPEC §3.5) |
| Node-link / hierarchy graph | Munzner (2014) *Visualization Analysis and Design* CRC Press | Network / org / dependency visualization scenario |

MVP does not expand the above. Cleveland & McGill (1984) plus the table above already covers ≥ 80% of business-deck scenarios.
