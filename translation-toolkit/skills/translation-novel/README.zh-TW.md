# translation-novel

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> 翻譯小說章節 / long-form fiction。
> Scene-aware chunking + scene-window prompt（相較 whole-doc windowing 約 17× cost 削減）。
> v0.3.0 加入 whole-book pre-pass、5D literary critic、M3 deterministic linter。

[translation-toolkit](../..) plugin 的一部分。Claude 載入的 operational
spec 是 [`SKILL.md`](SKILL.md)；此 README 提供給人類。

## v0.3.0 新增內容

四個 Tier 2 功能疊加在 v0.2.0 scene-window 基礎之上：

- **Whole-book pre-pass** — 在 per-chapter 翻譯前，skill 會先把全部章節
  走過一次，跑兩個 extractor：
  - `character_extractor` — 抓出每個 named character + paired-structure
    aliases + voice notes + first/last chapter index，輸出
    `characters.json`。
  - `world_glossary_extractor` — 抓出 places / organizations / world
    terms / cultural references，輸出 `world-glossary.json`。
    cultural reference 帶 closed-enum 的 `category`（literary_quotation /
    idiom / religious / food / place_culture / historical / other）與
    `handling_hint`（borrow / explain / approximate）。
  兩個 artifact 餵入 per-scene glossary lookup 作為 **L1.5** tier
  （介於 project glossary L1 與 bundled glossary L2 之間）— 在不撐爆
  whole-novel context 的前提下，提供跨章節一致的角色稱呼與 world
  term 錨定。
- **5D literary critic** — per-scene REFLECT step（novel mode 預設）
  在 v0.2.0 4D（Accuracy / Fluency / Style / Terminology）之上加入
  Literariness 軸。Sub-concerns：rhythm（句子 cadence）、euphony
  （sound pattern）、archaism（period vocabulary / honorific 適切性）、
  register-shift fidelity（narrator vs dialogue、同一角色內 formal vs
  casual）。與 `translation-creative` 的 5D（第五軸是 Effectiveness）
  不同。
- **M3 deterministic linter** — 在 S1 back-translation *之前* 跑的
  no-LLM 結構健全性檢查：M3a（residual source-script chars，HARD）、
  M3b（length-ratio band，SHOULD）、M3c（CJK fullwidth punctuation，
  SHOULD）。v0.3.0 由 `translation-doc` 同步採用（Decision H — novel
  與 doc 都會在 Layer 4 audit-trail 上 surface M3）。
- **Cheap-model split** — intake-spec 的 `model` 欄位接受 dict 形式
  `{default: ..., extractor: ..., back_translator: ...}`。whole-book
  pre-pass 在設定後會 route 至 `extractor` model，pre-pass 的固定成本
  得以對 per-scene translation 成本攤提。建議設定請見下方「為翻譯準備
  一本書」。

## 為翻譯準備一本書

翻譯多章節 book 的建議流程：

1. **將章節抽成 Markdown。** 用
   [`tsundoku:book-extract`](../../../tsundoku/skills/book-extract) 把
   EPUB 轉成 chapter-split `.md` 檔，放到 `book-ja/` 目錄；檔名要能用
   lexicographic sort 對應到閱讀順序（`chapter-01.md`、`chapter-02.md`、
   …）。
2. **跑一次 whole-book pre-pass。** 在翻譯任何章節之前，把 skill 對準
   `book-ja/` 來生成 `characters.json` 與 `world-glossary.json`。
   pre-pass 是唯一一次完整讀每章節的階段 — 之後的翻譯都是 per-scene
   執行。
3. **逐章翻譯。** 每個章節 run 載入兩份 pre-pass artifact，於 glossary
   lookup chain 中以 L1.5 查找（在 fallback 到 L2 / L3 / L4 之前）。
   Cross-scene voice continuity 仍由 `prev_scene_v2` 錨定，pre-pass 加上
   *cross-chapter* 的 canonical-rendering 錨定。
4. **書本內容變動時重跑 pre-pass。** 每份 artifact 都會 stamp 一個
   `book_manifest_hash`（涵蓋 filenames + per-file SHA-256）。manifest
   hash 漂移時（章節新增 / 編輯 / 重排），下一次 pre-pass run 會發出
   `UserWarning` 並覆蓋 artifact。skill 不會默默使用 stale artifact。

### 成本說明

只要傳入 `model: dict` 形式，pre-pass 預設使用 cheap 的 **extractor**
model — pre-pass 總成本只隨 raw chapter 文字增長，不被 per-scene prompt
overhead 放大，並對整本 book 攤提（付一次，每個章節都受惠）。在典型的
20-30 章節小說，pre-pass 成本通常在單一章節翻譯成本的 10% 以下；非常
小的 book（≤2 章節）比例會偏高，cheap-model split 是 load-bearing 的
設計選擇。smoke fixture（`scripts/tests/fixtures/sample-book-ja/`）
ship 一個 2-章節案例供 CI 行使 cost ceiling；calibrated 的 worst-case
bound 見 `scripts/tests/test_e2e_v030_tier2_smoke.py` 的
`test_prepass_cost_ceiling_assertion`。

dict 形式 `model` 欄位範例（intake spec）：

```yaml
model:
  default: claude-opus-4-7
  extractor: claude-haiku-4-5         # whole-book pre-pass
  back_translator: claude-haiku-4-5   # S1 round-trip
```

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
| **M2** | HARD | Project glossary 合規 — L1-mandated 的每個 source term 都以對應 target form 出現。**novel-mode 之下尤其關鍵** — 角色名與地名會跨 scene 再現，per-scene M2 PASS 不保證章節層級一致（checklist 項目 5 才會抓到）。v0.3.0+ 先在 pre-pass 的 `characters.json` / `world-glossary.json` 上以 **L1.5** 解析，之後才 fallback 到 project glossary L1 與 bundled glossary L2。 |
| **M3** | HARD（m3a）/ SHOULD（m3b、m3c） | Deterministic post-translation linter — 三條 subrule：m3a residual source-script chars（HARD；例如 JP→EN target 不應含 hiragana / katakana / CJK ideograph 超過 locale-pair 的 1% threshold）、m3b length-ratio band（target/source token 比落在 locale-pair tuned band 內）、m3c CJK fullwidth punctuation（依 JLReq / CLReq）。在 S1 *之前* 跑，當 target 結構毀損時 short-circuit 掉 S1 — 不為一個沒意義的 back-translation 付費。v0.3.0+；同 release `translation-doc` 也採用。 |
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
  [`references/core-loop.md`](references/core-loop.md)（DRAFT / REFLECT / IMPROVE 角色合約）
- [`references/4d-reflection.md`](references/4d-reflection.md)（Accuracy / Fluency / Style / Terminology）·
  [`references/prompt-reflect-5d-literary.md`](references/prompt-reflect-5d-literary.md)（5D literary critic — v0.3.0 預設）
- [`references/prompt-extract-characters.md`](references/prompt-extract-characters.md) ·
  [`references/prompt-extract-world-glossary.md`](references/prompt-extract-world-glossary.md)（whole-book pre-pass extractor — v0.3.0）
- Typography: [`typography/jlreq-summary.md`](typography/jlreq-summary.md)（ja-JP）·
  [`typography/clreq-summary.md`](typography/clreq-summary.md)（zh-CN / zh-TW）
- Plugin: [`../../README.md`](../../README.md) ·
  Router: [`../using-translation-toolkit`](../using-translation-toolkit) ·
  Layer 1: [`../translation-intake`](../translation-intake) ·
  Sibling: [`../translation-doc`](../translation-doc)
