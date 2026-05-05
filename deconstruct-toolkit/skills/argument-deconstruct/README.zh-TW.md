# argument-deconstruct

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> 對長篇論證做深度解構 — 揭出隱性 warrant（論證根據）、指名缺席的 rebuttal、揭穿動機 ratio。

聚焦論證的深度 skill。`artifact-deconstruct` 對任何作品跑完整的 6 lens × 6 維度 treatment，而 `argument-deconstruct` 則收斂到單一 artifact-class — 長篇論證 — 並以更高解析度套用 Toulmin + Burke。關鍵動作：**揭出隱性 warrant**。

## 使用時機

觸發語（任意語言）：

- 「拆解這個論證」「這份提案論證哪裡弱」「找隱性 warrant」
- 「論証を脱構築して」「この社説の隠れた前提は？」
- "deconstruct this argument" / "find the warrant" / "where does this argument fail"
- "is this argument valid" / "what's the hidden assumption in this claim"

不該用的時機：

- 對象沒有論證骨幹（描述性 / 敘事性 / 參考文件） → 改用 `artifact-deconstruct`
- 對象短於約 200 字 — 太薄無法解構
- 對象是程式碼 — 改用 `sourceatlas`

該改用兄弟 skill 的時機：

- 多 lens treatment（rhetoric + persuasion + frame + genre + UX + semiotic）→ [`artifact-deconstruct`](../artifact-deconstruct/)
- 不需完整 Toulmin treatment 的原子級假設揭出 → [`assumption-surface`](../assumption-surface/)

## 方法（與 artifact-deconstruct 的 lens-rhetoric 差異）

`artifact-deconstruct/references/lens-rhetoric-anglo.md` 把 Burke pentad + Toulmin 模型在 survey 解析度下整合進同一個 lens。`argument-deconstruct` 刻意把它們 **拆開** — 詳見 [`references/lens-toulmin.md`](references/lens-toulmin.md) 與 [`references/lens-burke-pentad.md`](references/lens-burke-pentad.md) — 對各自做更完整的 treatment。依 ADR-0002，此 synthesis 拆分屬刻意：同一 primary source、不同 operationalization 深度。

### Toulmin 模型（完整 6 構件）

| 構件 | 提問 |
|---|---|
| **Claim**（主張） | 結論為何？ |
| **Grounds**（證據） | 有什麼證據支撐？ |
| **Warrant** ⭐ | 從證據到主張之間的隱性橋樑為何？ |
| **Backing** | 什麼權威背書這個 warrant？ |
| **Rebuttal**（反駁） | 承認了哪些反論？ |
| **Qualifier**（限定詞） | 主張在什麼條件下成立？ |

warrant 是 **焦點動作**。大多數論證都把 warrant 藏起來。解構論證就是把 warrant 大聲說出來，並檢驗一個合理的反對者是否會接受它。

### 8 種隱性 warrant 模式（已建檔）

當你無法清楚說出 warrant 時，去 [`references/lens-toulmin.md`](references/lens-toulmin.md) 比對下列模式：

| 模式 | 聽起來像 |
|---|---|
| 訴諸權威 | 「X 說了，所以是真的」 |
| 訴諸多數 | 「大家都這樣，所以是對的」 |
| 類比 | 「在那邊有效，在這邊也會有效」 |
| 趨勢外推 | 「過去趨勢預測未來」 |
| 從相關推因果 | 「採用 X 的人也做 Y，所以 X 造成 Y」 |
| 損失趨避 | 「不做就會輸」 |
| 第一原理主張 | 「從基本原理推得 X」 |
| 自明 | 「顯然…」 |

### Burke pentad ratio

5 元（act / 行為、scene / 場景、agent / 行為者、agency / 手段、purpose / 目的）加上 **ratio** 分析：哪兩個元素主導，揭露動機結構。

| Ratio | 意義 |
|---|---|
| Scene-Act | 情境迫使行動 |
| Agent-Act | 你是誰決定你做什麼 |
| Agent-Agency | 身分決定方法 |
| Act-Purpose | 行動本身就是目的 |
| Agency-Purpose | 手段決定目的 |
| Scene-Agent | 場景決定你成為誰 |

把 **聲稱的** ratio 與 **實際的** ratio 的落差揭出 — 那個 gap 就是動機洗白的藏身處。

## 你會得到什麼（output）

- **論證圖** mermaid 形式（可視化 claim / grounds / warrant / backing / rebuttal / qualifier；隱性 warrant 用 dotted edge 強調）
- **Warrant 明示化** — 把每個隱性 warrant 都寫成以「因為…」開頭的完整句
- **缺席 rebuttal 表** — 作者忽略或先發制人迴避了哪些反論
- **Burke pentad ratio 分析** — 聲稱 ratio vs 實際 ratio，附動機詮釋
- **倫理立場**（針對偵測到的說服機制標 🟢/🟡/🔴/⚫）

## 實作範例

請見 [`eval/cases/argument-deconstruct-01-op-ed.yaml`](../../eval/cases/argument-deconstruct-01-op-ed.yaml) 與 [`eval/cases/argument-deconstruct-02-vc-pitch.yaml`](../../eval/cases/argument-deconstruct-02-vc-pitch.yaml) 的 must_find 正解資料。

## 相關

- [`SKILL.md`](SKILL.md) — 完整 canon
- [`references/lens-toulmin.md`](references/lens-toulmin.md) — 完整 Toulmin treatment（Toulmin 1958, Ch 3）
- [`references/lens-burke-pentad.md`](references/lens-burke-pentad.md) — 完整 Burke treatment（Burke 1945, Introduction）
- 兄弟 skill：[`artifact-deconstruct`](../artifact-deconstruct/) | [`assumption-surface`](../assumption-surface/)
- Plugin 總覽：[`../../README.md`](../../README.md)
