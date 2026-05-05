# assumption-surface

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> 從任何文本中拉出隱性假設，並評定論證實際依靠的是哪幾條。

Atomic skill。`artifact-deconstruct` 跑完整 6-lens × 6 維度，
`argument-deconstruct` 跑完整 Toulmin + Burke，而 `assumption-surface`
聚焦於單一交付物：**一張隱性假設表**。比完整解構更快；設計用來在
你決定是否依據某份 memo / proposal / 主張行動之前做壓力測試。

## 何時使用

觸發語（不限語言）。EN / JP / ZH-TW 混用 OK：

- "find the hidden assumptions", "what is this *assuming*"
- "stress-test these claims before deciding", "surface the implicit world-model"
- 「揭露這份備忘錄的隱性假設」「這個策略在假設什麼」
- 「隠れた前提を出して」「この主張は何を前提にしている」

何時略過：

- 目標文本 < 100 字 — 不夠 surface 可以浮現
- 你想要的是已打磨的 argument-map 交付物 — 這是檢查表，不是那種交付物

何時改用姊妹 skill：

- 需要對作品做完整 design teardown → `artifact-deconstruct`
- 需要顯式 Toulmin warrant（論證根據）階梯的論證結構分析 → `argument-deconstruct`
- 質疑你**自己**的前提（不是外部文本）→ `philosophers-toolkit:descartes-methodical-doubt`
- 程式碼 → `sourceatlas`

## 方法

四個動作，以分層堆疊方式套用：

### 1. 逆 Toulmin

把 Toulmin 的 claim-grounds-warrant 模型**反過來**跑：從文本的主張
出發，反推作者必須相信什麼 warrant，grounds 才能支撐 claim。藉此
浮現隱性的支柱信念。見 [`protocols/reverse-toulmin.md`](protocols/reverse-toulmin.md)。

### 2. 症狀式閱讀（Althusser 影響）

依 [`references/lens-symptomatic-reading.md`](references/lens-symptomatic-reading.md) —
讀文本**沒有說**的部分。不在場不是缺漏；它們是關於作者認為什麼
過於顯然不必明說、或什麼風險過高不敢明說的結構性資料。借自
Althusser 與 Balibar《讀資本論》（*Lire le Capital*, Maspero 1965;
1968 簡縮版; Brewster 譯 NLB 1970）。

### 3. 反事實探針

對每條浮現的假設追問：「若這條假設為偽，論證會長成什麼樣子？」
若論證崩潰，這條假設是**基礎**。若論證以變形姿態存活，**支柱但
非基礎**。若毫無變化，**裝飾**。

### 4. 框架審計

文本是在哪一個概念框架內運作？（Goffman / Lakoff 意義下。）
為框架命名能浮現出嵌入框架本身的假設。

## 3 階強度分類

每條浮現的假設都會獲得三種強度評等之一：

| 階級 | 意義 | 應對作法 |
|---|---|---|
| **基礎** | 若為偽，論證完全崩潰 | MUST 跑可證偽性測試 |
| **支柱** | 若為偽，論證需要大幅重構框架 | SHOULD 跑可證偽性測試 |
| **裝飾** | 若為偽，論證原樣存活 | 記下繼續走 |

## 可證偽性測試（基礎階）

對每條基礎假設，設計一個可能**證明它為偽**的測試。若不存在這樣
的測試，這條假設便不可證偽 — 這本身就是值得浮現的發現。依 Popper，
不可證偽的假設無法用來論證；只能被相信。一條不可證偽的基礎假設
是最危險的一類，必須在報告中明確標記。

## 你會得到什麼（output）

- **Source claims** — 文本提出的每一條 distinct 主張的編號清單
- **Assumption table**（5–15 列）— assumption | source claim(s) | 強度階級 | 可證偽性測試（僅基礎）
- **值得挑戰的基礎假設** — 每條基礎列附一個反問
- **Bottom line** — 一句話：作品依靠 N 條基礎假設，其中 K 條不可證偽；最具爭議的是 X

5–15 列是 sweet spot。30+ 通常代表你把主張當成假設在列。

## Worked example

隨附的 sample fixture：

- [`assets/sample-company-strategy-memo.md`](assets/sample-company-strategy-memo.md)
- [`assets/sample-tweet-thread-productivity.md`](assets/sample-tweet-thread-productivity.md)

Eval ground-truth（must-find 清單）：

- `eval/cases/assumption-surface-01-strategy-memo.yaml`
- `eval/cases/assumption-surface-02-tweet-thread.yaml`

## See also

- [`SKILL.md`](SKILL.md) — 完整正典（workflow、output template、anti-patterns）
- [`references/lens-symptomatic-reading.md`](references/lens-symptomatic-reading.md) — Althusser 與 Balibar 原典
- [`protocols/reverse-toulmin.md`](protocols/reverse-toulmin.md) — backward-Toulmin 方法
- 姊妹 skill：[`artifact-deconstruct`](../artifact-deconstruct/)（完整 6-lens）| [`argument-deconstruct`](../argument-deconstruct/)（完整 Toulmin）
- Plugin 總覽：[`../../README.md`](../../README.md)
