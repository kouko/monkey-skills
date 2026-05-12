# translation-creative

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> 用 faithful 或 transcreation 模式翻譯 ad copy / headline / tagline / catchphrase。

[translation-toolkit](../..) plugin 的一部分。Claude 載入的 operational
spec 是 [`SKILL.md`](SKILL.md)；此 README 提供給人類。

## 為何需要專用 creative skill

ad copy 失敗的方式 prose 翻譯偵測不到。back-translation 相似度可能 PASS
而 target 卻丟掉 source 的說服 intent — CTA 力道不足、死掉的 pun、外來的
文化參照、沉默的 taboo。把 "Just do it." 忠實譯成日文文法正確但作為
tagline 完全不可用。

`translation-creative` 加上其他 format specialist 沒有的兩件事：**第 5 個
critique 軸**（Effectiveness，transcreation 模式下）判斷 target 在 target
文化中是否保住說服 intent；以及 **mode 條件式 S1 tier flip** — 當 WRITER
被授權偏離 source 表面時，把 back-translation 升級為 HARD。variant 也是
first-class 輸出模式 — A/B 候選取代 paraphrase noise。

## 兩個 mode

mode 由 intake-spec 宣告，控制 REFLECT 軸數 + S1 gate tier：

| Mode | REFLECT | S1 tier | Threshold | 何時使用 |
|---|---|---|---|---|
| **faithful** | 4D（Accuracy / Fluency / Style / Terminology） | SHOULD（低於就 WARN） | 0.85 | source 結構 + 句界應保留；只調整 phrasing |
| **transcreation** | 5D（4D + Effectiveness） | **MUST**（低於就 FAIL） | 0.70 | source 表面可拋下，以在 target 文化中達成等效說服 |

若 intake-spec 未指定 mode，上游 `translation-intake` 將 ad-shaped genre
預設為 `transcreation`，把偏向 prose 的 marketing brief content 預設為
`faithful`，並記錄解析後的 mode + 原因。

完整 mode-entry contract — 第 5 個 Effectiveness 軸、variant 差異、
S1 MUST contract、glossary leeway rule — 見
[`protocols/transcreation-mode.md`](protocols/transcreation-mode.md)。

## Pipeline

```
intake-spec（來自 translation-intake）
        │
Layer 2 — Preparation
        ├── brand brief intake（transcreation 推薦；faithful 可選）
        ├── protect-pass: URL / HTML / brand token mask 為 ⟦P:NN⟧
        ├── source analysis: 文化參照、wordplay、CTA verb、
        │   untranslatability 候選
        └── glossary resolve（4-tier）
        │
Layer 3 — Core loop（DRAFT → REFLECT 4D-or-5D → IMPROVE）
        │   └── WRITER 收到 brand-brief context；遵守 signature
        │       phrase + do-not-say 清單
        │
Layer 4 — Verification（M1 + M2 HARD；S1 mode 條件式；
        │   S2 SHOULD；I1 INFO）
        │
Layer 5 — Output
        ├── 預設: 1 個翻譯
        ├── --variants=N: N 個獨立 core-loop run，使用軸差異化的
        │   prompt（不是 paraphrase）
        └── 發出 audit-trail.json（適用時帶 variant_index）
```

## Brand brief

依 [`protocols/brand-brief-intake.md`](protocols/brand-brief-intake.md)
捕捉。transcreation 推薦、faithful 可選（沒給 brief 時 fallback 到
intake-spec 的 `register` + `intent`）。

brief 捕捉的內容：brand archetype（Hero / Sage / Outlaw 等）、
tone-of-voice 軸（authoritative ↔ playful、formal ↔ casual、
warm ↔ cool）、do-not-say 清單、signature phrase（verbatim-preserve
vs locale-transcreate）、target persona、CTA style、各 locale 的
brand-name 處理（preserve / transliterate / locale-substitute）。
輸出落到 audit-trail 的 `brand_brief` block。

## Verification gate matrix

與其他 format specialist 的決定性差異：**mode 條件式 S1 tier flip** —
back-translation 在 faithful 下為 SHOULD、在 transcreation 下升為 MUST。
這是工具組中唯一一處 tier flip 驅動 HARD gate。

| Gate | Tier | Action |
|---|---|---|
| **M1** | HARD | Placeholder integrity — count + ID set parity |
| **M2** | HARD | Project glossary 合規。在 transcreation，見 [`protocols/transcreation-mode.md`](protocols/transcreation-mode.md) §"Glossary leeway" — 文化驅動的違規可被 audit 但允許。 |
| **S1** | **transcreation 為 MUST、faithful 為 SHOULD** | Back-translation 相似度。Threshold = faithful **0.85**（WARN）、transcreation **0.70**（低於 FAIL 阻擋 output）。 |
| **S2** | SHOULD | Register preservation — JUDGE 分類 source vs target register；不符給 WARN。 |
| **I1** | INFO | Untranslatability flagging — transcreation 中尤其活躍。non-interactive: 記錄 borrow / explain / approximate 決策。 |

**為何 S1 在 transcreation 升為 MUST**（spec Decision #4）：當 WRITER 被
授權大幅偏離 source 表面時，M1（placeholder count）與 S2（register）對
徹底的 topic drift 防護不足 — S1 是唯一能抓出「v2 是寫得不錯但內容是
另一個產品的 copy」這種事的 gate。

## Variants

`--variants=N` 是 opt-in。設定時，skill 發出 N 個 **真正不同** 的替代
方案 — 每個 variant 是完整、獨立的 DRAFT → REFLECT → IMPROVE run，
WRITER prompt 被指示沿戰術軸 variation（保留 source 結構 / 為 target 節奏
重構 / 換成文化等效的隱喻 / 等）。

variant 不是同一個 draft 的 paraphrase — 這個 pattern 被明確禁止，因為
它只會生出 synonym-swap noise。audit trail 中的 `variant_index` 欄位
把 issue 歸屬到特定 variant。variant 在 transcreation 模式下 fail S1 就被
drop；N 個都 fail 時 run 直接 halt，而非 silently 發出少於 N 個。

## Web search 策略

預設 ON — creative 工作需要當下的文化 / campaign context。當既定的 brand
voice 有被競品 copy 污染風險時，覆寫為 OFF（`--web-search=off`）。
Effectiveness 軸 critique 在 web off 仍可從 training-time 知識動作；
transcreation 不需要 web search，但會失去近期 slogan / meme / campaign
參照的新鮮度。

## 跨 plugin composition

`copywriting-toolkit` 可在 creative 翻譯 **之後** 呼叫，作為 voice / form /
倫理潤飾。Composition **僅限使用者明示** — `translation-creative` 不會
auto-invoke `copywriting-toolkit`。需要時把兩者作為循序 pair 跑；兩個
skill 是互補的。

## 此 skill **不做** 的事

- **不跑 intake。** 交棒給 [`translation-intake`](../translation-intake)
- **不生成 brand strategy。** transcreation 模式缺 brief 會 WARN，而非生成
  一份 strategy。
- **不翻譯 brand name** — 沒有明確 intake 指示時預設為 verbatim-preserve。
- **不 auto-invoke `copywriting-toolkit`** — composition 必須明示。
- **不把單一 draft paraphrase 成 variant** — `--variants=N` 跑 N 個獨立
  core loop。
- **transcreation 模式下不 bypass S1。** S1 為 MUST 時，低於 threshold 的
  v2 會阻擋 output；revise 或上升給人類，**不要** 把 gate flip 掉。
- **不取代人類 creative review。** audit trail + variant index 是設計來讓
  下游 review 更快。

## See also

- [`SKILL.md`](SKILL.md) — operational spec
- [`protocols/brand-brief-intake.md`](protocols/brand-brief-intake.md) ·
  [`protocols/transcreation-mode.md`](protocols/transcreation-mode.md)
  （5D Effectiveness、variant strategy、S1 MUST contract、glossary leeway）
- [`checklists/creative-checklist.md`](checklists/creative-checklist.md) ·
  [`references/5d-effectiveness.md`](references/5d-effectiveness.md)
- Plugin: [`../../README.md`](../../README.md) ·
  Router: [`../using-translation-toolkit`](../using-translation-toolkit) ·
  Layer 1: [`../translation-intake`](../translation-intake)
