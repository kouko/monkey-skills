# philosophers-toolkit

> 12 個哲學思考框架，轉化為互動式 Claude Code skill — 用提問引導思考，而非單向講授。

Read this in: [English](README.md) | [日本語](README.ja.md) | **繁體中文**

**Version**: 1.0.4
**Part of**: [monkey-skills](https://github.com/kouko/monkey-skills)
**License**: MIT

## Background

多數「思考框架」工具會丟出一份 checklist 就走人。本 plugin 反其道而行。
每個 skill 都把 Claude 變成一個哲學對談者，**和你一起**執行框架
— 在對的時機問對的問題，拒絕預判答案，把結論交還給你。

本 toolkit 結合兩個傳統：

- **Western philosophy（西方哲學）** — Socrates、Aristotle、Descartes、
  Hegel、Popper。分解、對話、可否證的方法論。
- **日本哲學** — 守破離、生き甲斐、改善、反省、侘寂。
  階段診斷、存在意義、持續改善、blame-free 反省、
  good-enough 的方法論。

每個 skill 都能用 slash command 呼叫。不確定要用哪一個時，
router skill（`/think`）會幫你挑選。

## Install

本 plugin 收錄於 `monkey-skills` marketplace。

```bash
# 在 Claude Code 內
/plugin marketplace add kouko/monkey-skills
/plugin install philosophers-toolkit
```

## Usage

知道要用哪個 method 時，直接呼叫對應的 skill：

```
/philosophers-toolkit:socratic
/philosophers-toolkit:first-principles
/philosophers-toolkit:dialectics
```

不確定時讓 router 替你選：

```
/philosophers-toolkit:think
```

router 只問一個問題 —「你想做什麼？」— 然後導向最適合的 skill。

## Skills

### Western philosophy（西方哲學）

#### Socratic method（蘇格拉底式問答）

| 項目 | 內容 |
|-------|-------|
| Origin | 古雅典，約西元前 5 世紀 |
| 哲學家 | Socrates（透過 Plato 的對話錄） |
| Core idea | Maieutics（產婆術）— 想法的「助產士」。知識是從學習者身上引出，而非灌輸進去。 |
| Method | Claude 拒絕講授。每次回應都以提問結束，逼你把自己的想法清楚講出來。 |
| Use when | 想透過開放對話檢驗自己的思考；說出「教我」「我卡住了」的時候。 |
| Command | `/philosophers-toolkit:socratic` |

#### Aristotle's Four Causes（四因說）

| 項目 | 內容 |
|-------|-------|
| Origin | 《物理學》《形上學》，約西元前 350 年 |
| 哲學家 | Aristotle |
| Core idea | 任何存在物都有四個解釋性的因 — 質料因、形式因、動力因、目的因。檢視四者才能完整理解。 |
| Method | Claude 用四個透鏡結構化分析：是由什麼構成、是什麼讓它成為它、是什麼造成它、它為了什麼而存在。 |
| Use when | 想深入理解一個系統、產品或概念的本質。 |
| Command | `/philosophers-toolkit:four-causes` |

#### First Principles（第一原理）

| 項目 | 內容 |
|-------|-------|
| Origin | Aristotle《後分析篇》；於現代工程實踐中重新被重視 |
| 哲學家 | Aristotle |
| Core idea | 分解到不可再分的根本真理，再從那裡重建 — 拒絕用類比推論。 |
| Method | Claude 幫你剝掉「best practices」與慣例，只留下不可再分的事實，然後往上推論。 |
| Use when | 既有假設綁住新思考；想把問題從零重新想過。 |
| Command | `/philosophers-toolkit:first-principles` |

#### Hegelian Dialectics（黑格爾辯證法）

| 項目 | 內容 |
|-------|-------|
| Origin | 19 世紀初德國觀念論 |
| 哲學家 | Georg Wilhelm Friedrich Hegel |
| Core idea | 每個立場都內含自身矛盾的種子。正→反→合在更高層次的框架中讓對立消解。 |
| Method | Claude 把對立明確化，然後推向 synthesis（合題）— 不是妥協。 |
| Use when | 面對二選一、互相競爭的優先級、或對立立場的 stakeholder。 |
| Command | `/philosophers-toolkit:dialectics` |

#### Popper's Falsifiability（可否證性）

| 項目 | 內容 |
|-------|-------|
| Origin | 《科學發現的邏輯》，1934 |
| 哲學家 | Karl Popper |
| Core idea | 一個主張只有在你能指出什麼證據可以推翻它時才有意義。能解釋一切的理論，什麼都沒解釋。 |
| Method | Claude 把模糊主張轉成可檢驗假設，並協助你設計能推翻它的測試。 |
| Use when | 有需要驗證的假設；說了「X 比 Y 好」卻沒給出可量測的標準。 |
| Command | `/philosophers-toolkit:falsify` |

#### Descartes' Methodical Doubt（方法性懷疑）

| 項目 | 內容 |
|-------|-------|
| Origin | 《沉思錄》，1641 |
| 哲學家 | René Descartes |
| Core idea | 只要有一絲可疑就視為偽 — 直到找到完全無法懷疑的東西。然後在那個基岩上重建。 |
| Method | Claude 系統性剝除每一層不確定性，浮現出能撐過最大懷疑的東西。 |
| Use when | 稽核信任假設；評估證據；投入資源前先壓力測試一份計畫。 |
| Command | `/philosophers-toolkit:doubt` |

### 日本哲學

#### 守破離（Shu-Ha-Ri）

| 項目 | 內容 |
|-------|-------|
| Origin | 日本武道傳統；遠藤征四郎於合氣道體系化 |
| 傳統 | 武道（budō） |
| Core idea | 習熟經三階段 — 守（守型）、破（破型）、離（離型）。階段是「依領域而定」，不是絕對的。 |
| Method | Claude 在特定 skill 或方法論中診斷你的階段，並給出對應階段的指導。 |
| Use when | 在猶豫「該守規則還是走自己的路」；想評估自己在某項技術的習熟度。 |
| Command | `/philosophers-toolkit:shu-ha-ri` |

#### 生き甲斐（Ikigai）

| 項目 | 內容 |
|-------|-------|
| Origin | 沖繩／本土日本的人生意義概念；4 軸 framework 在現代 career 與 PMF 論述中廣為流傳 |
| 傳統 | 日本生きがい傳統 |
| Core idea |「喜歡的事」「擅長的事」「世界需要的事」「能得到報酬的事」四軸交集處能持續產生意義。少一軸就會有空虛感。 |
| Method | Claude 帶你逐軸檢視，診斷哪一軸缺了。 |
| Use when | 專案或產品感覺沒有目的；感覺 PMF 沒到；職涯轉折點。 |
| Command | `/philosophers-toolkit:ikigai` |

#### 改善（Kaizen）

| 項目 | 內容 |
|-------|-------|
| Origin | 戰後豐田生產方式；大野耐一、今井正明體系化 |
| 傳統 | 製造業；現在已廣泛應用 |
| Core idea | 把今天的工作做得比昨天好一點點。小改善持續累積，產生大成果。 |
| Method | Claude 帶領 6 步驟迴圈，找出最小可行的改善並執行。 |
| Use when | 感覺「不知為何很沒效率」；既有流程有摩擦或浪費；「想改很多但不知從哪開始」。 |
| Command | `/philosophers-toolkit:kaizen` |

#### 反省（Hansei）

| 項目 | 內容 |
|-------|-------|
| Origin | 日本內省傳統；融入豐田的持續學習文化 |
| 傳統 | 日本自我修養 |
| Core idea | 為了學習而反省，不是為了究責。問「我漏看了什麼」而非「誰的錯」。 |
| Method | Claude 帶領 4 階段內省流程，聚焦在結構性盲點，而非表面教訓。 |
| Use when | 專案逾期；功能沒被採用；決策事後出問題；季度／年度回顧。 |
| Command | `/philosophers-toolkit:hansei` |

#### 侘寂（Wabi-Sabi）

| 項目 | 內容 |
|-------|-------|
| Origin | 茶道美學；千利休體系化、松尾芭蕉深化 |
| 傳統 | 日本美意識 |
| Core idea | 在不完整、無常、不完美中看到美。能砍的就砍。讓時間與使用為它增色。刻意留白，邀請參與。 |
| Method | Claude 問你 — 這份打磨是在提升本質，還是在逃避恐懼？ |
| Use when | 在掙扎「MVP 就上還是再磨」；覺得 API 太複雜；完美主義拖住釋出。 |
| Command | `/philosophers-toolkit:wabi-sabi` |

### Getting started

#### `/think` router

| 項目 | 內容 |
|-------|-------|
| Skill | `using-philosophers-toolkit` |
| Core idea | 把意圖和 method 對上。對的框架比流行的框架更重要。 |
| Method | Claude 只問一個問題 —「你想做什麼？」— 然後導向最合適的 skill。 |
| Use when | 想深入思考但不確定哪個 method 合用；問題還很模糊，需要先釐清。 |
| Command | `/philosophers-toolkit:think` |

## Design principles

貫穿所有 skill 的設計原則：

**互動流程，不是講授。** 每個 skill 把 Claude 變成你的思考夥伴。
skill 提問。你回答。skill 再深入挖。結論是你的，不是 Claude 的。

**確認 topic，但不預判答案。** 每個 skill 在開始前先確認分析對象。
拒絕事先 declare synthesis、不可懷疑的基岩、或「正確的階段」會是什麼。

**用起源的語言。** 日本框架就用日文 — 守破離、生き甲斐、改善、反省、
侘寂 — 不用 romaji 或硬譯英文。Western 哲學家名一律保留原文。
概念在它自己的文化形式中流動。

**操作導向，不是學術。** 每個 skill 的產出是更銳利的問題定義
或更完整的分析，而不是哲學論文。每個都是有具體步驟的 procedure，
不是漫談。

**一個情境一種 method。** 每個 skill 的 `Do NOT use when` 區塊在
選錯工具時把你導去別處。falsify 一個主張、doubt 一個前提、
分解一個問題、對話一個開放問題 — 各有專屬的 skill。

## Roadmap

考慮中的框架列在 [ROADMAP.md](ROADMAP.md) — 包括 Occam's Razor、
pragmatism、功利主義／義務論、三現主義、道家／無為等。

## Contributing

歡迎 contribution。新框架請先開 issue 討論。每個新 skill 必須：

- 用 `When to Use` 與 `Do NOT use when` 兩個區塊對應到一個明確的問題類別
- 是互動式 procedure，而不是靜態 reference
- 非西方框架要保留起源語言
- 通過 [domain-teams skill-team](https://github.com/kouko/monkey-skills/tree/main/domain-teams/skills/skill-team) 的結構性 gate

PR 遵循 [Conventional Commits](https://www.conventionalcommits.org/)。

## License

MIT — 詳見 repository root 的 [LICENSE](../LICENSE)。
