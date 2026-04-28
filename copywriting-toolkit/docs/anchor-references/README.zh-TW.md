# Anchor References

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

**目的**：保存那些**不**符合 v2 inclusion criterion（個別創作者 + 可辨識的 sentence-level register）所以無法成為 Layer 1 voice anchor 的 register / format / movement 描述。這些內容仍有價值 — Pass 3 over-mimic registry 會將其中一些當作 mitigation-only 引用；Phase 8 form-check 可能參考其他項目當作 format convention — 但它們**不**會被當作 voice anchor 載入。

**v1.13.1 整併**：從原本的 `docs/format-templates/` + `docs/register-references/` 合併而來。兩個資料夾都收非 Layer 1 reference 且功能重疊；合併成單一資料夾以減少導覽負擔。

## 兩類條目

### Format templates（`jp-*`、`en-*`、`zh-tw-*-platforms-*`、`zh-tw-*-institutional-*`）

機構 / 平台 / IP 實體所產出的可重用結構性 format。範例：
- **雜誌 / 報紙 / 通訊社** 由輪替作者撰寫（天声人語 / 東洋経済 / Reuters JP / 日経社説）
- **機構平台 / SNS / IP 吉祥物**（研之有物 / 故宮粉絲團 / 全聯 SNS / クックパッド つくれぽ / ワークマン SNS）
- **電商平台** 由分散式作者撰寫（Shopee 雙11 / PChome / MOMO / Pinkoi）
- **品牌的機構式聲音**, 在 register-defining 時刻沒有單一具名作者（Amazon product copy / REI expert-advice / IKEA assembly voice）

Voice 來自於由同一隻手反覆鍛鍊出的 sentence-level 一致敏感度。這些實體產出的是 **FORMAT、PROTOCOL 或 TEMPLATE** — 輪替的作者收斂到 house-style 規則, 而不是表達單一作者的 voice。

### Register references（運動層級 / campaign 層級 / 出版時代）

被記錄下來的運動 / 著名 campaign / 編輯部 voice — 影響力強到會洩漏進 draft 變成 anti-pattern, 但沒有可載入的單一作者 voice。範例：
- **被記錄下來的運動**, 帶有 civic-declarative 或 manifesto register（XR Declaration / Occupy declarations）
- **出版社的機構聲音**, 即使編輯輪替, house style 仍可作為 mitigation reference（Economist brand voice / 天下雜誌 / 商業周刊 / 報導者）
- **Campaign 層級**, register 來自團隊共識（某些 Nike 「Dream Crazy」執行案 — 由輪替的 CW 撰寫）

format-template 與 register-reference 之間的區分是 soft 的 — 兩者都不是 Layer 1, 兩者都服務於下游 gate 而非 Pass 3 voice 選擇。條目按主要 lens（結構性 format vs 被記錄下來的運動）歸檔, 但整個資料夾就是一個 「non-anchor references」 桶。

## Pass 3 與 gate 如何使用這個資料夾

- **Pass 3 不會把這些檔案當作 voice anchor 載入。** `voice-consistency-gate.md` 的 Voice Consistency（Dimension 6）與 Thesis Alignment（Dimension 7）只在 `standards/anchor-*.md` 的 Layer 1 條目上運作。
- **`voice-anchor-meta.md §Over-mimic mitigation fallback registry` 中的 over-mimic registry** 會引用此處的部分條目作為 mitigation 來源 — 例如「XR Declaration civic-declarative register ONLY；NOT for commercial product copy」。
- **Phase 8 form-check（8a）** 可能會參考 format template 取得平台特定 convention（電商 product copy 節奏 / 通訊社 headline 長度 / SNS IP 吉祥物 register）。
- **Audit / evaluator** 可能會引用這些當作「draft 在模仿一個平台 format template 或 civic-movement 節奏, 不是 voice register — 重新 anchor 或重新導向」這類 rationale。

## 與其他 skill layer 的關係

- **正規 voice library**（`standards/anchor-*.md`）— Layer 1 個別創作者的 voice anchor（80+ 條目）。Pass 3 從這裡載入。
- **Anchor references**（本資料夾）— 非 Layer 1：format templates + register references。僅供 mitigation / form-convention 使用。
- **Voice anchor notes**（`../voice-anchor-notes/`）— Layer 2/3 研究 artifact, 對應 Layer 1 條目 + 被淘汰候選的研究軌跡。

## 重要：這不是 voice register 來源

如果一個 brief 落入這個資料夾的領域, skill 會 route 到：
1. **Form appropriateness**（Phase 8 8a）— 若是 format-template, 使用該 template 的結構 convention
2. **Over-mimic mitigation**（Dimension 6）— 若是 register-reference, 把它當作 anti-pattern 引用
3. **Tone** — 從品牌 brief 或從 Layer 1 另外選一個具名個人的 voice anchor 派生

絕不要「把 Amazon product copy 當作 voice register」 — Amazon 的 register **就是** product copy template 本身。把 template 當結構用；voice anchor 從 Layer 1 另外選。「把 XR Declaration 當作 voice」也一樣 — 那是 mitigation warning, 不是 source。

## 移轉狀態

Phase C（v1.5.0）原本把 `docs/format-templates/` + `docs/register-references/` 建立成兩個分離資料夾。v1.13.1 把兩者整併成 `docs/anchor-references/` — 內容相同, 單一導覽目標。

**從 v1 `standards/*-anchors.md` 逐條移轉到本資料夾**：依 `docs/voice-library-recast-audit.md` 漸進進行。明確映射到 format-template（輪替作者產出 house style）或 register-reference（運動或出版時代）的條目落到此處；代表個別創作者 sentence-level register 的條目則進到 `standards/anchor-{slug}.md` 作為 Layer 1。
