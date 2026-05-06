# translation-novel

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> 翻譯小說章節 / long-form fiction。
> Scene-aware chunking + scene-window prompt（相較 whole-doc windowing 約 17× cost 削減）。

[translation-toolkit](../..) plugin 的一部分。Claude 載入的 operational
spec 是 [`SKILL.md`](SKILL.md)；此 README 提供給人類。

## 為何需要專用的 novel skill

小說以 prose 為主。`translation-doc` 處理的 markdown AST 工作（code block、
math、mermaid、frontmatter）並不適用，而它依賴的 whole-doc
`<TRANSLATE_THIS>` windowing 在 chunk 數上是 O(N²) 成本。30-scene 的章節
若用 whole-doc windowing 跑，共享 context 會被重送 900× — 5-10 chunk 的
technical document 還能忍，fiction 批次則直接破產。

novel-mode 還需要 doc-mode 不必煩惱的 **cross-scene voice continuity**：
同一角色的稱呼、同一 speech-tier、scene 之間一致的 register。doc-mode 因為
whole-doc context 的存在剛好順便保住，但一旦因為成本掉到 scene window，
voice continuity 就必須被明確攜帶。

`translation-novel` 一次解掉這兩件事：用 heading / explicit-marker / blank-gap /
token-fill 邊界做 scene-aware chunking，再用 scene-window prompt 攜帶上一
scene 的 **target 語言** 翻譯（`prev_scene_v2`）以及下一 scene 的 source 開頭
（`next_scene_source`）。成本退化為 O(N)，voice 錨定於 target 端的歷史。

（v0.2.0 plan Decision 1：這是新 skill，不是 `translation-doc` 的 flag —
chunking、prompt、gate 權重的分歧夠大值得獨立。）

## Pipeline

```
intake-spec（來自 translation-intake）
        │
Layer 2 — Preparation
        ├── 把章節當 plain prose 解析（不做 markdown AST）
        ├── 可選 protect-pass（預設 OFF — fiction 沒有 code / math /
        │   diagram；M1 僅在 ON 時強制）
        ├── scene chunk: heading > explicit_marker > blank_gap >
        │   fallback_token_fill，max_scene_tokens=2000
        └── per-scene glossary resolve（4-tier: L1 project → L2 bundled
            → L3 web → L4 LLM）；scope = current + prev_source + next_source
        │
Layer 3 — Per-scene core loop（DRAFT → REFLECT 4D → IMPROVE）
        │   └── scene-window prompt（Decision 4）：
        │       params → glossary → prev_scene_v2（~500 tok）→
        │       <TRANSLATE_THIS>current</TRANSLATE_THIS> →
        │       next_scene_source（~200 tok）→ output requirements
        │
Layer 4 — Verification（M1 + M2 HARD；S1 + S2 SHOULD；I1 INFO）
        │
Layer 5 — Output
        ├── 還原 ⟦P:NN⟧ → 原本 span（僅 protect-pass 啟用時）
        ├── 依原 index 順序串接 scene v2，重新發出消耗掉的邊界 string
        │   （explicit-marker / blank-gap）
        ├── roundtrip check（scene 順序、heading、scene 內段落、
        │   章節層級 glossary、無 truncation-window 外洩）
        └── 發出 audit-trail.json
```

## Scene-window vs whole-doc — 成本故事

`translation-doc` 用 **whole-doc `<TRANSLATE_THIS>` windowing**：每個 chunk
的 prompt 都重發整份文件，僅 active chunk 被包裹。成本對 chunk 數是 **O(N²)**。

`translation-novel` 用 **scene-window prompt**：只有 `prev_scene_v2`
（最後 ~500 token）+ 當前 scene + `next_scene_source`（前 ~200 token）會
出現。每個 scene 成本是 **O(N)** — 30-scene 的章節大約比 whole-doc windowing
**小 17×**。

Voice continuity 來自 `prev_scene_v2`（前一 scene 的 **target 端** 翻譯，
依 Decision 5）— 而不是每次 prompt 都重譯 source。WRITER 直接看到上一次
翻譯如何處理一個再登場角色的 voice，不必每個 scene 重新發現該選擇。
glossary term 的章節層級一致性靠 M2（HARD）守住，並由 checklist 項目 5
雙重檢查。

低於 2000-token chunk threshold 時，章節即單一 scene，windowing 退化成
prev / next 為空的普通 prompt。

## Verification gate matrix

針對 scene 長度 prose（典型 500-2000 token）校準：

| Gate | Tier | 檢查內容 |
|---|---|---|
| **M1** | HARD | Placeholder integrity — `⟦P:NN⟧` count + ID set parity。protect-pass OFF（prose-only novel 預設）時為 no-op。 |
| **M2** | HARD | Project glossary 合規 — L1-mandated 的每個 source term 都以對應 target form 出現。**novel-mode 之下尤其關鍵** — 角色名與地名會跨 scene 再現，per-scene M2 PASS 不保證章節層級一致（checklist 項目 5 才會抓到）。 |
| **S1** | SHOULD（faithful）/ MUST（transcreation） | Back-translation — BACK-TRANSLATOR 對每個 scene blind 把 v2 → source 重譯；對 source 做 embedding-cosine 相似度。對 scene 長 prose 可靠。runtime 沒提供 isolation 時帶 audit-trail flag 跳過。 |
| **S2** | SHOULD | Register preservation — JUDGE 在 discourse / formality 軸上分類 source vs target。fiction register 在 scene 長度上訊號清楚。 |
| **I1** | INFO | Untranslatability flagging — 文化指涉、wordplay、慣用句、無法翻譯的敬稱。記錄 borrow / explain / approximate 決策；不阻擋、不詢問 user。 |

S1 / S2 是 SHOULD 不是 HARD：成因明確的單一 scene failure（例如 JUDGE
誤判方言 register）會記錄到 audit-trail 並 surface 給 caller，但不阻擋
emit。M1 / M2 失敗仍 HARD-block。

## Roundtrip checklist

emit 前 [`checklists/novel-quality-checklist.md`](checklists/novel-quality-checklist.md)
會 verify：

1. Scene 順序保留
2. Scene 邊界 text 被正確消耗（explicit-marker + blank-gap 已重新發出）
3. Heading level 相符
4. Scene 內段落保留
5. 章節層級 M2 cross-scene glossary 一致性
6. 無 truncation-window 外洩（prev / next 片段沒漏進 v2）

任何項目失敗就 halt emit 並 surface 給 caller。

## Web search 策略

預設 ON。針對 novel batch（例如一次翻 30-scene 章節）覆寫為 OFF：

```
--web-search=off
```

OFF 時 glossary resolution 停在 L2（bundled） — L3（web）跳過，
L4（LLM-fallback）仍跑。重複出現的虛構 term（造詞地名、魔法體系詞彙）
本來就常常 web 抓不到，所以對 fiction 而言 OFF 通常是合理預設。

## 此 skill **不做** 的事

- **不跑 intake。** 交棒給 [`translation-intake`](../translation-intake)
  （或用 `--intake`）
- **不解析 markdown AST。** novel 章節以 prose text 處理；protect-pass
  預設 OFF。若 source 嵌有 code / math / diagram，請改 route 到
  [`translation-doc`](../translation-doc)。
- **不改寫章節結構。** scene 順序保留；chunker 的 round-trip 合約是 spec，
  不是建議。
- **不生成 transcreation variant。** 用 `--variants=N` 改 route 到
  [`translation-creative`](../translation-creative)。novel-mode 對每個
  scene 跑單一 faithful 翻譯。
- **不 audit 既有翻譯配對。** 改 route 到 [`translation-audit`](../translation-audit)。
- **不 bypass M1 / M2。** 沒有 `--bypass-gates` flag（依 spec Decision #15
  為反模式）。
- **不做整本小說的 context 組裝。** voice continuity 僅止於 scene window；
  跨整本小說的角色 arc 翻譯屬 Tier 2（character pre-pass），已 deferred。
- **不在 I1 階段詢問 user。** untranslatability 決策只記錄不詢問。

## See also

- [`SKILL.md`](SKILL.md) — operational spec
- [`protocols/scene-chunking.md`](protocols/scene-chunking.md) ·
  [`protocols/scene-window-context.md`](protocols/scene-window-context.md)
- [`checklists/novel-quality-checklist.md`](checklists/novel-quality-checklist.md)
- [`references/verification-gates.md`](references/verification-gates.md) ·
  [`references/core-loop.md`](references/core-loop.md)（scene-window builder）
- [`references/4d-reflection.md`](references/4d-reflection.md)（Accuracy / Fluency / Style / Terminology）
- Typography: [`typography/jlreq-summary.md`](typography/jlreq-summary.md)（ja-JP）·
  [`typography/clreq-summary.md`](typography/clreq-summary.md)（zh-CN / zh-TW）
- Plugin: [`../../README.md`](../../README.md) ·
  Router: [`../using-translation-toolkit`](../using-translation-toolkit) ·
  Layer 1: [`../translation-intake`](../translation-intake) ·
  Sibling: [`../translation-doc`](../translation-doc)
