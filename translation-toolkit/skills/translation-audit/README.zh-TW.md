# translation-audit

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> 對既有 `(source, target)` 配對跑完整的 5-gate suite review，並發出 diff 報告。

[translation-toolkit](../..) plugin 的一部分。Claude 載入的 operational
spec 是 [`SKILL.md`](SKILL.md)；此 README 提供給人類。

## 為何需要獨立的 audit skill

順向 skill（`translation-i18n`、`translation-doc`、`translation-creative`）
把 gate 校在「不要在 draft → revise 過程中阻擋合法的風格重構」。當 target
是固定的、問題是 **「這個 target 可以接受嗎」** 時，那種校準就錯了。

audit 跑 **完整的 M1 + M2 + S1 + S2 + I1** matrix，並且 **把 S1 + S2 從
SHOULD upgrade 為 HARD** — 低於 threshold 的判定是 FAIL（不是 WARN），給
reviewer 一份具體的 triage queue。這是工具組中唯一 S1 / S2 會生 HARD
failure 的 context，也是唯一 output 是 **review 文件** 而非翻譯產物的 skill。
Layer 3（DRAFT / REFLECT / IMPROVE）刻意 skip — 使用者提供的 target 才是
被審視的 unit。

## 輸入

| 輸入 | 必填 | Notes |
|---|---|---|
| `source` | 是 | 工具組可 parse 的任何 format（`.po` / `.json` / `.xliff` / `strings.xml` / `.strings` / `.md` / `.mdx` / 純文字） |
| `existing target` | 是 | 檔案路徑或 inline 字串。format 可與 source 不同（migration audit、vendor delivery review）。 |
| `intake-spec` | 推薦 | 來自 `translation-intake`。若缺，先對 source 跑 intake。攜帶 `mode` / `register` / locale pair，全都會 inform S2 strictness 與 I1 framing。 |
| `glossary_path` | 可選 | 預設為 `<repo>/docs/i18n/glossary-{target_locale}.md` |

## Pipeline

```
intake-spec（來自 translation-intake；或從 source 自動推論）
        │
Layer 2 — Preparation
        ├── parse source 與 target **兩邊**（format 可不同）
        ├── 兩邊都跑 protect-pass（dual tokenization 才能讓 M1 的
        │   count-parity check 有意義）
        ├── 兩邊都跑 source analysis（target 可能有獨立於 source 的問題）
        └── glossary resolve（4-tier；對 source term 解析、
            對 target 檢查合規）
        │
Layer 3 — SKIPPED（使用者提供的 target 即為審視 unit）
        │
Layer 4 — Verification（FULL M1 + M2 + S1 + S2 + I1；S1 + S2 升為 HARD）
        │
Layer 5 — Output
        ├── diff 報告（markdown；6 段；不重寫）
        └── audit-trail.json（完整 provenance）
```

## Verification gate matrix

附帶更嚴 semantics 的完整 matrix — 這個 skill 存在的理由。

| Gate | audit 中的 Tier | 檢查內容 |
|---|---|---|
| **M1** | HARD | dual protect-pass 後比對 source / target placeholder count。Diff 格式逐 chunk 記錄 `source_count` / `target_count` / `missing_in_target` / `extra_in_target`。 |
| **M2** | HARD | Project glossary 合規。違規依 term 報告，附 `project_glossary` vs `target_used` 與 tier / audit_path provenance。`notes: context-dependent` entry 仍適用 PASS_ADVISORY。 |
| **S1** | **HARD**（原為 SHOULD） | Subagent 把 target → source-language 翻譯；對原 source 做 embedding-cosine 相似度。Threshold = **0.85**。低於 threshold → diff 報告中為 **FAIL**，不是 WARN。 |
| **S2** | **HARD**（原為 SHOULD） | LLM JUDGE 分類既有 target 的 register 並與 source + intake-spec 預期的 register 比對。不符 → **FAIL**。附 JUDGE rationale 讓 reviewer 判斷此不符是可接受的 shift 還是缺陷。 |
| **I1** | INFO | Untranslatability handling — 對每個被 flag 為 untranslatable 的 source phrase，target 必須出現 borrow / explain / approximate 的 handling。缺 handling 會報告，但不阻擋。 |

**為何 S1 / S2 在此升為 HARD**：WARN-only 是為順向 skill 的 draft → revise
loop 校準的。當 target 固定時，每一個客觀及 structured-judgment 議題都應
作為具體 failure surface 進 reviewer 的 triage queue。M2 的
`notes: context-dependent` PASS_ADVISORY 例外保留 — 那個例外是針對 entry，
不是針對 gate tier。

## Diff 報告

依 [`protocols/diff-report.md`](protocols/diff-report.md) 的 markdown 文件，
含 6 段：header（路徑 + timestamp + intake snapshot + glossary 版本）、
summary verdict、per-gate verdict block（M1 / M2 / S1 / S2 / I1 與 diff）、
帶行號的 inline issue、recommendations（指引非 edit）、用以捕捉 reviewer
決策的 sign-off block。

改進建議在每個 inline issue 旁出現，但報告 **絕不** 寫出修正後的 target。
reviewer 在下游施 fix（典型做法是對 source 重跑
`translation-{i18n,doc,creative}`，或手動編輯後 re-audit）。

## 輸出路徑

預設 emit（caller 可透過 service interface 覆寫）：

- `<target_path>.audit.md` — diff 報告
- `<target_path>.audit-trail.json` — machine-readable 配套

audit 不會修改磁碟上的 target 檔。

## 何時使用

- pre-merge 翻譯 review
- 廠商 / agency delivery 品質檢查
- 重譯後的 regression check
- localized release 發布前的內部 QA gate
- 同一 source 兩個競爭翻譯的 A/B 比較（每個候選跑一次，共兩次）

## 何時 **不** 使用

- 順向翻譯 — 改用 `translation-{i18n,doc,creative}`
- 僅做 intake clarification — 改用 [`translation-intake`](../translation-intake)
- 想生出競爭翻譯 — audit 不會生成

## Web search 策略

預設 ON。Audit 模式是 4 個 active skill 中最受惠於 web search 的 — L3
（web）glossary lookup 經常 surface 出 existing target 忽視的 authoritative
target form。只有 offline 執行（例如 network-isolated CI host 上）才覆寫
為 OFF：

```
--web-search=off
```

## Roles

詞彙與工具組其餘相同，**僅扣除 WRITER / REVISER**（因 Layer 3 skip）：

- **CRITIC** — 在 S2 / I1 framing 期間對既有 target 產出 structured 4D / 5D
  critique；不重寫
- **BACK-TRANSLATOR** — 盲目把 target → source 重譯，供 S1 使用
- **JUDGE** — register 分類，供 S2 使用

## 此 skill **不做** 的事

- **不重寫既有 target。** Audit 設計上 read-only。Layer 3 skip；不存在
  `--produce-target` flag（那條路徑屬於順向 skill）。
- **不套用改進建議** — 那些是給 reviewer 的指引，不是 edit。
- **不變更檔案 format。** 不寫回。磁碟上原 target 檔不動。
- **不 bypass M1 / M2 / S1 / S2。** 沒有 `--bypass-gates` flag
  （依 spec Decision #15 為反模式）。5 個 gate 全跑。
- **I1 期間不 prompt。** target 中既存的 untranslatability handling 會被
  記錄；handling 缺漏會報告為 issue。
- **不取代人類 reviewer 判斷。** S1 / S2 的 FAIL 判定是替 reviewer flag
  議題；ship / no-ship 決策由 diff 報告的 sign-off 段捕捉，不是 skill。

## See also

- [`SKILL.md`](SKILL.md) — operational spec
- [`protocols/diff-report.md`](protocols/diff-report.md) ·
  [`checklists/audit-completeness-checklist.md`](checklists/audit-completeness-checklist.md)
- [`references/verification-gates.md`](references/verification-gates.md) ·
  [`references/protect-pass-spec.md`](references/protect-pass-spec.md)
- Plugin: [`../../README.md`](../../README.md) ·
  Router: [`../using-translation-toolkit`](../using-translation-toolkit) ·
  Layer 1: [`../translation-intake`](../translation-intake)
- 順向 skill: [`translation-i18n`](../translation-i18n) ·
  [`translation-doc`](../translation-doc) ·
  [`translation-creative`](../translation-creative)
