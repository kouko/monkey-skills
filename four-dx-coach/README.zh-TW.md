# four-dx-coach

> 多 scope 的《執行的 4 個修練》顧問 —— 個人 solo、team-leader 主持、team-member 參與三種尺度都涵蓋。Agent 會切換角色：solo 時當 peer-witness，leader 時當 consultant，member 時當你自己的 personal coach（在別人定的 WIG 下工作）。

語言：[English](README.md) | [日本語](README.ja.md) | **繁體中文**

**版本**：0.6.0
**所屬於**：[monkey-skills](https://github.com/kouko/monkey-skills)
**License**：MIT

## 背景

《The 4 Disciplines of Execution》（McChesney / Covey / Huling / Thele / Walker，第 2 版 2021 年）是 FranklinCovey 顧問群整理的 execution methodology，跨約 4,000 個 client engagement 驗證。它的處方：

1. **D1 — 聚焦 Wildly Important Goal (WIG)**（一個 WIG，以 `From X to Y by When` 表達）
2. **D2 — 行動於 lead measure**（兼具 predictive AND influenceable）
3. **D3 — 維持 compelling scoreboard**（players' scoreboard，不是 coach's dashboard）
4. **D4 — 建立 cadence of accountability**（每週 peer commitment 的 WIG Session）

書本主要寫給「在多個 team 推行 4DX 的 leader」。這個 plugin 把 methodology 延伸到書本沒充分服務的兩個 scope：

- **Personal** —— 單一 user 為個人目標導入 4DX；agent 扮演書中假設的同儕 peer-witness 角色。
- **Team-leader** —— 在單一 team 內部跑 4DX 的 leader（不是跨 team rollout）；agent 當 consultant。
- **Team-member** —— team 上的 contributor，leader 已經選好 WIG 了；agent 幫你「好好參與」，不是去重新設計 system。

## Architecture

11 個 skill，分三類：

- **1 個 plugin router**（`using-four-dx-coach`）—— 處理冷啟動 / 跨 topic / 非 4DX query 的 dispatcher。
- **5 個 multi-file scope-flex skill** —— 每個是一個 topic，內含 2-4 個 protocol 檔案，分別覆蓋 personal / team-leader / team-member 變體。Skill 透過一句 Socratic 問題自動偵測 scope 後載入對應 protocol。這取代了 2026-04-30 合併前的 15 個 atomic skill + 5 個 topic-router。
- **5 個 single-file scope-specific skill** —— 每個只服務一個 scope，沒有內部拆分。書本對這幾個 topic 沒有跨 scope 的對應變體，所以保留為 compact 的 single-file `SKILL.md`。

Multi-file skill 收斂了 scope 重疊面，但完全保留 primary-source grounding：每個 protocol 仍掛 `### Industry-experience addendum`，共用 parent skill 的 `references/industry-grounding.md`。

## Skills（共 11 個）

### 1. Plugin router（1）

| Skill | 功能 |
|---|---|
| [`using-four-dx-coach`](skills/using-four-dx-coach/) | 入口路由 —— cold-start / cross-topic / 非 4DX query；scope triage 到 personal / team-leader / team-member 或 4DX 不適用時轉介 |

### 2. Multi-file scope-flex skills（5）

以下每個 skill 都會在內部用 Socratic 問題自動偵測 scope，再載入 `protocols/` 對應的 protocol 檔案。

| Skill | Topic | 內部 protocols [multi-file scope-flex] |
|---|---|---|
| [`4dx-meta-strategy-triage`](skills/4dx-meta-strategy-triage/) | Pre-D1 fit gate（6-verdict triage） | `personal-mode.md`、`team-mode.md` |
| [`4dx-d1-wig-formulation`](skills/4dx-d1-wig-formulation/) | 寫 / 選 / 解讀 *From X to Y by When* WIG | `personal-define.md`、`team-select.md`、`member-comprehend.md` |
| [`4dx-d2-lead-measures`](skills/4dx-d2-lead-measures/) | 發現 / 引導 / 找 sphere-of-influence on lead measures | `personal-discover.md`、`team-facilitate.md`、`member-influence.md` |
| [`4dx-d3-scoreboard`](skills/4dx-d3-scoreboard/) | 設計 / 引導 / 讀 players' scoreboard | `personal-design.md`、`team-lead-design.md`、`member-read.md` |
| [`4dx-d4-cadence`](skills/4dx-d4-cadence/) | 跑 / 主持 / 準備 / debrief 每週 WIG Session | `solo-session.md`、`team-leader-session.md`、`member-prep.md`、`member-debrief.md` |

### 3. Single-file scope-specific skills（5）

書本對這些 topic 只有單一 scope 的處理，所以保留為 single-file。

| Skill | Scope | 功能 |
|---|---|---|
| [`4dx-meta-whirlwind-triage`](skills/4dx-meta-whirlwind-triage/) | Personal | 7 天時間稽核；釐清 BAU vs WIG 衝突；保留 ~20% WIG slot |
| [`4dx-d1-wig-cascade`](skills/4dx-d1-wig-cascade/) | Team-leader | 把 Primary WIG 翻譯成 Battle WIG（Targets-not-Plans）；只在多 team 場景出現 |
| [`4dx-meta-team-leader-onboarding`](skills/4dx-meta-team-leader-onboarding/) | Team-leader | 讓 direct-report leader 真心 buy-in（commitment vs compliance） |
| [`4dx-meta-xps-evaluation`](skills/4dx-meta-xps-evaluation/) | Team-leader | Post-quarter XPS audit（0-4 scale；C1-C4 layer） |
| [`4dx-sustain-momentum-rescue`](skills/4dx-sustain-momentum-rescue/) | Personal | 診斷 4-discipline stack 哪裡斷掉，路由到對應 restart |

## Scope 偵測怎麼運作

你不需要手動選 scope。三種解法：

1. **Plugin router**（`using-four-dx-coach`）讀 query 中的 scope signal（「我們 team」「我加入了」「*我自己的*目標」）後 dispatch。
2. **Multi-file scope-flex skill** 在 flow 開頭用一句 Socratic 問題消除歧義，自動載入對應 protocol —— 不用手選。
3. **Single-file scope-specific skill** 只在 signal 已經鎖定 scope 時 activate（例：cascade → team-leader、whirlwind triage → personal）。

不確定就直接描述情境，router 會幫你判斷。

## 何時使用

觸發訊號：

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

轉介情境：

- 跨多個 team 的 enterprise rollout → 直接讀書的 Part 2（第 6-10 章）或聯繫 FranklinCovey 顧問
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

Router skill `using-four-dx-coach` 在通用查詢時觸發；特定 skill 在自己的 signal 上觸發。

## Industry-grounded boundaries

每個 topical skill（5 個 multi-file + 5 個 single-file = 10 個 atomic-equivalent）的 Boundary section 都帶 `### Industry-experience addendum`，引用書本之外的學術 / 監管 / 業界文獻原始來源 —— 補書本的 selection bias 與 member-POV 缺漏。每 skill 的 `references/industry-grounding.md` 列出全部已驗證引用：

- D2 lead-measure-discovery：Goodhart 1975 / Strathern 1997 / CFPB 2016（Wells Fargo）/ VA OIG 2014 / GBI 2011（Atlanta APS）—— Goodhart 失敗案例
- D1 personal-define：Christensen 1997 / March 1991 / Dweck 2006 —— 過度聚焦風險 + 探索 vs 利用
- D3 personal-scoreboard：Tufte 1983 / Few 2006 / Ware 2012 —— 5 秒 test 的感知科學基礎
- D4 solo + team WIG-Session：Rogelberg 2019 / Lencioni 2004 / Edmondson 2012 —— 會議科學的實證依據
- Member protocols：Edmondson 2018 / Grant 2016 / Meyer 2014 / Pfeffer 2010 / Drucker 1999 / Cialdini 1984 / Eurich 2017 / Wiseman 2010 —— 補書本 leader-POV 偏差
- Team-leader skills：Akao 1991 / Doerr 2018 / Kaplan-Norton 2001 / Ryan-Deci 2017 / Argyris 1991 / Kotter 1996 / Galbraith / Schein / Rumelt / Porter / Mintzberg / Hambrick-Fredrickson / CMMI / McKinsey OHI / Gallup Q12

Plan U merge 後仍保留 48 個已驗證 primary-source 引用。

## 多語言觸發

Skill 的 `description` 和 trigger signal 支援 **英文 / 日文 / 繁體中文** —— 三種語言都可以問。Skill body（Interpretation / Execution / Boundary）統一英文以維持 portability。

## 建議學習順序

### Personal（solo）—— 從零開始

1. `4dx-meta-strategy-triage` → `personal-mode.md` —— 確認 4DX 適合你的目標（或被轉介）
2. `4dx-meta-whirlwind-triage` —— 釐清 BAU vs WIG 工作
3. `4dx-d1-wig-formulation` → `personal-define.md` —— 寫出 WIG（X → Y → When）
4. `4dx-d2-lead-measures` → `personal-discover.md` —— 找到 2-3 個 lead measure
5. `4dx-d3-scoreboard` → `personal-design.md` —— 設計一眼可讀的 scoreboard
6. `4dx-d4-cadence` → `solo-session.md` —— 啟動每週 cadence
7. `4dx-sustain-momentum-rescue` —— momentum 下滑時依需求載入

### Team-leader —— 從零開始

1. `4dx-meta-strategy-triage` → `team-mode.md` —— 確認 4DX 是 team 該走的路
2. `4dx-d1-wig-formulation` → `team-select.md` —— Battles 2x2 選 Primary WIG
3. `4dx-d1-wig-cascade` —— 以 Targets-not-Plans 把 org WIG cascade 成 team WIG
4. `4dx-meta-team-leader-onboarding` —— 從 direct report 拿到 commitment（不是 compliance）
5. `4dx-d4-cadence` → `team-leader-session.md` —— 以 facilitator 主持每週 WIG Session
6. `4dx-meta-xps-evaluation` —— 定期審視 team 內部 4DX 實作

### Team-member —— 加入一個已在跑 4DX 的 team

1. `4dx-d1-wig-formulation` → `member-comprehend.md` —— 理解被指派的 team WIG
2. `4dx-d4-cadence` → `member-prep.md` —— 為下次 session 準備 commitment
3. `4dx-d4-cadence` → `member-debrief.md` —— 每次 session 後做誠實 self-account

## 出處

蒸餾自《The 4 Disciplines of Execution》（第 2 版 2021）—— Chris McChesney / Sean Covey / Jim Huling / Scott Thele / Beverly Walker（Simon & Schuster）。Pipeline：`tsundoku:book-distill`（RIA-TV++，改編自 kangarooking/cangjie-skill，MIT）。Plan U merge（2026-04-30）將 26 個 skill 整併為 11 個。詳見 [ATTRIBUTION.md](ATTRIBUTION.md)。

## 相關 plugins

- [`tsundoku`](../tsundoku/) —— 產出本 plugin 的 book→skill 蒸餾 pipeline
- [`philosophers-toolkit`](../philosophers-toolkit/) —— 姊妹「個人思考方法」plugin
