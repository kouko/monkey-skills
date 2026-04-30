# four-dx-coach

> 多 scope 的《執行的 4 個修練》顧問 —— 個人 solo、team-leader 主持、team-member 參與三種尺度都涵蓋。Agent 會切換角色：solo 時當 peer-witness，leader 時當 consultant，member 時當你自己的 personal coach（在別人定的 WIG 下工作）。

語言：[English](README.md) | [日本語](README.ja.md) | **繁體中文**

**版本**：0.2.0
**所屬於**：[monkey-skills](https://github.com/kouko/monkey-skills)
**License**：MIT

## 背景

《The 4 Disciplines of Execution》（McChesney / Covey / Huling / Thele / Walker，第 2 版 2021 年）是 FranklinCovey 顧問群整理的 execution methodology，跨約 4,000 個 client engagement 驗證。它的處方：

1. **D1 — 聚焦 Wildly Important Goal (WIG)**（一個 WIG，以 `From X to Y by When` 表達）
2. **D2 — 行動於 lead measure**（兼具 predictive AND influenceable）
3. **D3 — 維持 compelling scoreboard**（players' scoreboard，不是 coach's dashboard）
4. **D4 — 建立 cadence of accountability**（每週 peer commitment 的 WIG Session）

書本主要是寫給「在多個 team 推行 4DX 的 leader」。這個 plugin 把 methodology 延伸到書本沒充分服務的兩個 scope：

- **Personal** —— 單一 user 為個人目標導入 4DX；agent 扮演書中假設的同儕 peer-witness 角色。
- **Team-leader** —— 在單一 team 內部跑 4DX 的 leader（不是跨 team rollout）；agent 當 consultant。
- **Team-member** —— team 上的 contributor，leader 已經選好 WIG 了；agent 幫你「好好參與」，不是去重新設計系統。

## 你在哪個 scope？

| 如果你... | 用 ... 系列 skill | Agent 角色 |
|---|---|---|
| ... 一個人在追個人目標 | `personal-*` | peer-witness |
| ... 帶領一個正在導入 4DX 的 team | `team-*` | leader 的 consultant |
| ... 是某 team 的成員，team 已在跑 4DX | `member-*` | member 的 personal coach |

不確定的話，先用 router (`using-four-dx-coach`) —— 它會先做 scope triage。

## Skills（共 26 個 — D1-D4 全 3-scope 對稱）

### Personal（7 個）

| 階段 | Skill | 功能 |
|---|---|---|
| meta | [`4dx-meta-personal-strategy-triage`](skills/4dx-meta-personal-strategy-triage/) | 開始之前判斷你的目標是否適用 4DX |
| D1 | [`4dx-d1-personal-whirlwind-triage`](skills/4dx-d1-personal-whirlwind-triage/) | 透過 7 天時間稽核釐清 BAU vs WIG 衝突 |
| D1 | [`4dx-d1-personal-wig-defining`](skills/4dx-d1-personal-wig-defining/) | 引導 `From X to Y by When` WIG 寫法 |
| D2 | [`4dx-d2-personal-lead-measure-discovery`](skills/4dx-d2-personal-lead-measure-discovery/) | 找出 2–3 個 predictive + influenceable 的 lead measure |
| D3 | [`4dx-d3-personal-scoreboard`](skills/4dx-d3-personal-scoreboard/) | 設計通過 5 秒 test 的 players' scoreboard |
| D4 | [`4dx-d4-personal-wig-session`](skills/4dx-d4-personal-wig-session/) | 執行 20–30 分鐘每週 WIG Session —— agent = peer-witness |
| sustain | [`4dx-sustain-personal-momentum-rescue`](skills/4dx-sustain-personal-momentum-rescue/) | 診斷 cadence 哪裡斷掉，路由到對應的 rescue 流程 |

### Team-leader（8 個）

| 階段 | Skill | 功能 |
|---|---|---|
| meta | [`4dx-meta-team-strategy-triage`](skills/4dx-meta-team-strategy-triage/) | 判斷 team 是否該導入 4DX |
| D1 | [`4dx-d1-team-primary-wig-selection`](skills/4dx-d1-team-primary-wig-selection/) | 用 Battles 2x2 選出組織 Primary WIG |
| D1 | [`4dx-d1-team-wig-cascade`](skills/4dx-d1-team-wig-cascade/) | 把 org WIG 翻譯成 team WIG（Targets-not-Plans 紀律） |
| meta | [`4dx-meta-team-leader-onboarding`](skills/4dx-meta-team-leader-onboarding/) | 讓 direct-report leader 真心 buy-in —— commitment vs compliance |
| **D2** | [**`4dx-d2-team-lead-measure-facilitation`**](skills/4dx-d2-team-lead-measure-facilitation/) | **帶 team 一起找 2-3 個 lead measure（veto-not-dictate）** |
| **D3** | [**`4dx-d3-team-lead-scoreboard-design`**](skills/4dx-d3-team-lead-scoreboard-design/) | **帶 team 一起 build 公用、多角色可讀的 players' scoreboard** |
| D4 | [`4dx-d4-team-wig-session-lead`](skills/4dx-d4-team-wig-session-lead/) | 以 facilitator 身份主持 team 的 WIG Session |
| meta | [`4dx-meta-team-xps-evaluation`](skills/4dx-meta-team-xps-evaluation/) | 對 team 內部 4DX 實作做 XPS audit |

### Team-member（5 個）

| 階段 | Skill | 功能 |
|---|---|---|
| D1 | [`4dx-d1-member-team-wig-comprehension`](skills/4dx-d1-member-team-wig-comprehension/) | 理解被指派的 team WIG |
| **D2** | [**`4dx-d2-member-lead-measure-influence`**](skills/4dx-d2-member-lead-measure-influence/) | **找出對 inherited lead measure 的 sphere of influence** |
| **D3** | [**`4dx-d3-member-scoreboard-reading`**](skills/4dx-d3-member-scoreboard-reading/) | **讀 team scoreboard + 定位自己貢獻 + 必要時 escalate** |
| D4 | [`4dx-d4-member-commitment-prep`](skills/4dx-d4-member-commitment-prep/) | 為下次 WIG Session 準備你自己的 commitment |
| D4 | [`4dx-d4-member-account-debrief`](skills/4dx-d4-member-account-debrief/) | 開會前後對自己誠實 account |

### Topic-routers（5 個）—— 處理 topic 已知但 scope 模糊的 query

| Topic | Skill | 路由到 |
|---|---|---|
| meta-triage | [`4dx-meta-strategy-triage`](skills/4dx-meta-strategy-triage/) | personal vs team strategy-triage |
| D1 WIG | [`4dx-d1-wig-formulation`](skills/4dx-d1-wig-formulation/) | personal-define / team-select / member-comprehend |
| **D2 leads** | [**`4dx-d2-lead-measures`**](skills/4dx-d2-lead-measures/) | **personal-discover / team-facilitate / member-influence** |
| **D3 scoreboard** | [**`4dx-d3-scoreboard`**](skills/4dx-d3-scoreboard/) | **personal-design / team-lead-design / member-read** |
| D4 cadence | [`4dx-d4-cadence`](skills/4dx-d4-cadence/) | solo-session / team-lead-session / member-prep / member-debrief |

Topic-router 只在「topic 清楚但 scope/role 模糊」時觸發，問一句 Socratic 確認後派發到 atomic skill。

### Plugin router（1 個）

| Skill | 功能 |
|---|---|
| [`using-four-dx-coach`](skills/using-four-dx-coach/) | 入口路由 —— cold-start / cross-topic / 非 4DX query 用；scope triage 到 personal / team-leader / team-member 或在 4DX 不適用時轉介 |

## 何時使用

✅ **觸發訊號**：

- 「4DX 適合我嗎？」 / "Should I use 4DX for X?" / 「この目標に 4DX 使える？」
- 「我每天都在救火，重要的事都沒做」
- 「目標太模糊 / 想做的事太多」
- 「我有目標，但不知道每天該做什麼才有效果」
- 「我的追蹤工具太複雜，沒在看」
- 「想要每週固定 review 維持目標進度」
- 「我的 4DX 已經幾週沒做了，要怎麼重啟？」
- 「幫我們 team 選 Primary WIG / cascade org WIG」
- 「怎麼讓我的 leader 真的 buy-in，不是表面 compliance？」
- 「幫我主持 team 的 WIG Session」
- 「我加入了一個在跑 4DX 的 team，我要怎麼參與？」
- 「幫我準備明天 WIG Session 的 commitment」

❌ **轉介情境**：

- 跨多個 team 的 enterprise rollout → 直接讀書的 Part 2（第 6–10 章）或聯繫 FranklinCovey 顧問
- Habit formation → atomic habits / habit stacking 才是對的工具
- 多賭注 / 多新創 → OKR 或精實實驗
- 急診醫師 / 消防員等以救火為策略本身的角色
- 純創作產出（小說家、藝術家）—— Goodhart 效應會破壞 lead measure
- 臨床 burnout / 憂鬱 → 尋求專業協助，而非 4DX

## 安裝

```bash
# 在 Claude Code 中
/plugin marketplace add kouko/monkey-skills
/plugin install four-dx-coach@monkey-skills
```

Router skill `using-four-dx-coach` 會在通用查詢時觸發；特定 skill 在自己的 signal 上觸發。

## Industry-grounded boundaries

每個 atomic skill 在 Boundary section 都帶 `### Industry-experience addendum`，引用書本之外的學術 / 監管 / 業界文獻原始來源 —— 補書本的 selection bias 與 member-POV 缺漏。每 skill 的 `references/industry-grounding.md` 列出全部已驗證引用：

- D2 lead-measure-discovery：Goodhart 1975 / Strathern 1997 / CFPB 2016（Wells Fargo）/ VA OIG 2014 / GBI 2011（Atlanta APS）—— Goodhart 失敗案例
- D1 personal-wig-defining：Christensen 1997 / March 1991 / Dweck 2006 —— 過度聚焦風險 + 探索 vs 利用
- D3 personal-scoreboard：Tufte 1983 / Few 2006 / Ware 2012 —— 5 秒 test 的感知科學基礎
- D4 personal/team WIG-Session：Rogelberg 2019 / Lencioni 2004 / Edmondson 2012 —— 會議科學的實證依據
- Member skills：Edmondson 2018 / Grant 2016 / Meyer 2014 / Pfeffer 2010 / Drucker 1999 / Cialdini 1984 / Eurich 2017 / Wiseman 2010 —— 補書本 leader-POV 偏差
- Team-leader skills：Akao 1991 / Doerr 2018 / Kaplan-Norton 2001 / Ryan-Deci 2017 / Argyris 1991 / Kotter 1996 / Galbraith / Schein / Rumelt / Porter / Mintzberg / Hambrick-Fredrickson / CMMI / McKinsey OHI / Gallup Q12

16 個 skill × 48 個已驗證 primary-source 引用。

## 多語言觸發

Skill 的 `description` 和 trigger signal 支援 **英文 / 日文 / 繁體中文** —— 三種語言都可以問。Skill body（Interpretation / Execution / Boundary）統一英文以維持 portability。

## 建議學習順序

### Personal（solo）—— 從零開始

1. `4dx-meta-personal-strategy-triage` —— 確認 4DX 適合你的目標（或被轉介）
2. `4dx-d1-personal-whirlwind-triage` —— 釐清 BAU vs WIG 工作
3. `4dx-d1-personal-wig-defining` —— 寫出 WIG（X → Y → When）
4. `4dx-d2-personal-lead-measure-discovery` —— 找到 2–3 個 lead measure
5. `4dx-d3-personal-scoreboard` —— 設計一眼可讀的 scoreboard
6. `4dx-d4-personal-wig-session` —— 啟動每週 cadence
7. `4dx-sustain-personal-momentum-rescue` —— momentum 下滑時依需求載入

### Team-leader —— 從零開始

1. `4dx-meta-team-strategy-triage` —— 確認 4DX 是 team 該走的路
2. `4dx-d1-team-primary-wig-selection` —— Battles 2x2 選 Primary WIG
3. `4dx-d1-team-wig-cascade` —— 以 Targets-not-Plans 把 org WIG cascade 成 team WIG
4. `4dx-meta-team-leader-onboarding` —— 從 direct report 拿到 commitment（不是 compliance）
5. `4dx-d4-team-wig-session-lead` —— 以 facilitator 主持每週 WIG Session
6. `4dx-meta-team-xps-evaluation` —— 定期審視 team 內部 4DX 實作

### Team-member —— 加入一個已在跑 4DX 的 team

1. `4dx-d1-member-team-wig-comprehension` —— 理解被指派的 team WIG
2. `4dx-d4-member-commitment-prep` —— 為下次 session 準備 commitment
3. `4dx-d4-member-account-debrief` —— 每次 session 前後做誠實 self-account

## 出處

蒸餾自《The 4 Disciplines of Execution》（第 2 版 2021）—— Chris McChesney / Sean Covey / Jim Huling / Scott Thele / Beverly Walker（Simon & Schuster）。Pipeline：`tsundoku:book-distill`（RIA-TV++，改編自 kangarooking/cangjie-skill，MIT）。詳見 [ATTRIBUTION.md](ATTRIBUTION.md)。

## 相關 plugins

- [`tsundoku`](../tsundoku/) —— 產出本 plugin 的 book→skill 蒸餾 pipeline
- [`philosophers-toolkit`](../philosophers-toolkit/) —— 姊妹「個人思考方法」plugin
