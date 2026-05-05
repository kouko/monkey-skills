# artifact-deconstruct

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> 還原任何非程式碼作品背後的設計藍圖 — 哪些是被決定的、哪些是被借用的、哪些是刻意留白的。

`deconstruct-toolkit` 的旗艦 skill。逆向解構任何外部、非程式碼作品（文案 / 文件包 / SOP / playbook / 簡報 / UI 截圖 / 廣告 / 文學）的設計藍圖。目標是 **設計考古** — 還原作者所做的決定、所借用的 framework、以及刻意省略的部分。

## 何時使用

觸發詞（任何語言）：

- EN: "deconstruct this", "reverse engineer", "design behind this", "teardown", "why does this work"
- JP: 「この制作物を脱構築して」「なぜこれはこんなに刺さるのか」「設計を逆引きして」
- ZH-TW: 「拆解這份」「反推這個」「為什麼這份寫得這麼好」「這份是怎麼設計的」

略過情境：

- 使用者要的是 **摘要** — 用一般閱讀即可
- 作品 < 200 字且不是結構化論證 — 沒有足夠的設計可還原
- 對象是純資訊性 reference（維基百科、辭典、原始資料）
- 對象是 source code → 改用 `sourceatlas`
- 對象是使用者自己的思考 → 改用 `philosophers-toolkit`

## 運作方式（6 步驟）

1. **辨識類型** — marketing / playbook / SOP / deck / UI / article / speech / literature / UI screen
2. **挑選 lens** — 從 6 lens 庫挑 1–3 個（決策樹見 [`protocols/lens-selection.md`](protocols/lens-selection.md)）
3. **跑完六維度（dimensions）** — 不論挑哪些 lens，這條 backbone 永遠執行
4. **套用 lens** — 4 個文化敏感 lens 透過 [`protocols/lens-variant-selection.md`](protocols/lens-variant-selection.md) 解析 variant
5. **產出 report** — 6 段式解構，附倫理立場判定
6. **自我檢查** — 交付前跑 [`checklists/anti-patterns.md`](checklists/anti-patterns.md)

完整 instruction 在 [`SKILL.md`](SKILL.md)。

## lens 庫

6 個 lens，以可選組合方式套用（**不是**全六個一起 — 那代表猶豫不決）：

| Lens | 來源 | 文化 variant |
|---|---|---|
| `lens-semiotic` | Barthes 1970 (S/Z, 5 codes) | （無 — v0.2.0 為止僅 Anglo grounded） |
| `lens-rhetoric` ✱ | Burke 1945 + Toulmin 1958 (anglo) · Hinds 1983/1987 + Oh 2025 起承転結 (ja) · 劉勰《文心雕龍》六觀 (zh) | -anglo / -ja / -zh |
| `lens-frame` ✱ | Goffman 1974 + Lakoff 1980 (anglo) · + Doi 1971 / Yamamoto 1977 / Markus & Kitayama 1991 (ja) · + Hu 1944 / Hwang 1987 / Peng & Nisbett 1999 (zh) | -anglo / -ja / -zh |
| `lens-genre` ✱ | Swales 1990 + Bhatia 1993 (anglo) · + 木下 1981 + Hinds 1987 (ja) · + 行政院公文程式條例 (zh) | -anglo / -ja / -zh |
| `lens-ux` | Nielsen 1994/2020 + Norman 1988/2013 | （無） |
| `lens-persuasion` ✱ | Cialdini 2021 + Brignull 2024 (anglo) · + Doi 1971 + 跨文化實證研究 (ja) · + Hwang 1987 面子/關係/人情 (zh) | -anglo / -ja / -zh |

（✱ = 走語言 variant 路由；套用前先用 [`protocols/lens-variant-selection.md`](protocols/lens-variant-selection.md) 解析 variant）

## 六維度 backbone

不論還搭配哪些 lens，每個作品都會跑完六個維度：

1. **讀者路由** — 誰、何時、讀到什麼？
2. **生成順序** — 閱讀順序 vs 實際被書寫的可能順序
3. **來源系譜** — 借用了哪些既有 framework？
4. **修辭結構** — 它怎麼說服人？
5. **設計模式** — 反覆出現的技巧有哪些？
6. **負空間** — 哪些是刻意省略的？

負空間維度是強制的 — 作品 **沒說** 的部分是資料，不是空白。

## 你會拿到什麼（輸出格式）

6 段式解構 report（template 在 [`assets/report-template.md`](assets/report-template.md)）：

```
1. 表層觀察           (你看到什麼)
2. 設計決策           (讀者 / 順序 / 修辭)
3. 借用的 framework   (系譜)
4. 修辭機制           (附倫理立場 🟢/🟡/🔴/⚫)
5. 可複製的學習       (5 條具體 takeaway)
6. 弱點 / 警告        (缺漏的招式 / 可疑的 warrant / 黑暗模式風險)
```

最後以一句 **bottom-line verdict** 收尾。

每一個被偵測到的說服機制或 UX 機制，都會被標上四種倫理立場其中一種：

| 立場 | 意義 |
|---|---|
| 🟢 透明 | 使用了原理，使用者看得見也可以拒絕 |
| 🟡 灰色地帶 | 使用了原理，使用者不知道 |
| 🔴 操弄 | 製造緊迫或錯誤信念 |
| ⚫ 黑暗模式 | 主動欺騙、傷害使用者 |

不允許中性描述。

## 文化 variant 路由（v0.2.0+）

對文化敏感的 4 個 lens（rhetoric / persuasion / genre / frame），variant 由 **作品的 register** 決定，不由作者或品牌出身決定。Toyota 的英文 LP 套用 `-anglo`（英文作品），不是 `-ja`（日系品牌）。演算法見 [`protocols/lens-variant-selection.md`](protocols/lens-variant-selection.md)。

輸出 report MUST 寫出實際套用了哪個 variant：

> "Applied lens-rhetoric-ja (kishōtenketsu mode, op-ed register) to artifact at [URL] in Japanese."

這讓分析可被審計 — 不認同 variant 選擇的讀者可以換一個重跑。

## worked example

Anglo:

- [`assets/sample-dropbox-landing-2024.md`](assets/sample-dropbox-landing-2024.md) — 2026-05-05 實際 fetch 的 Dropbox LP（must-find 標準答案在 plugin root 的 `eval/cases/artifact-deconstruct-01-dropbox-landing.yaml`）
- [`assets/sample-notion-onboarding-pack.md`](assets/sample-notion-onboarding-pack.md)
- [`assets/sample-stripe-signup-flow.md`](assets/sample-stripe-signup-flow.md)

文化 variant fixture（JP + ZH 共 8 件）：

- JP: `sample-ja-op-ed.md` · `sample-ja-ec-lp.md` · `sample-ja-business-letter.md` · `sample-ja-political-speech.md`
- ZH: `sample-zh-op-ed.md` · `sample-zh-ec-lp.md` · `sample-zh-gongwen.md` · `sample-zh-political-speech.md`

全 11 個 case 在 plugin root 的 `eval/cases/` 都有對應的 `must_find` 標準答案 spec。

## 不要用這個 skill 的時候

- 以論證為核心的深挖 → 改用 `argument-deconstruct`（Toulmin + Burke pentad，聚焦隱性 warrant）
- 單點的隱性假設挖掘 → 改用 `assumption-surface`（reverse-Toulmin + Althusser 症狀式閱讀）
- 程式碼逆向工程 → 改用 `sourceatlas`
- 自我思考 → 改用 `philosophers-toolkit`
- < 200 字且不是結構化論證 — 設計密度不足

## 延伸閱讀

- [`SKILL.md`](SKILL.md) — 完整 canon（本 README 是給 GitHub 瀏覽器讀者看的門面，SKILL.md 是給 LLM 讀的 instruction 本體）
- [`protocols/six-dimensions.md`](protocols/six-dimensions.md)
- [`protocols/lens-selection.md`](protocols/lens-selection.md)
- [`protocols/lens-variant-selection.md`](protocols/lens-variant-selection.md)
- [`checklists/anti-patterns.md`](checklists/anti-patterns.md)
- plugin overview: [`../../README.md`](../../README.md)
