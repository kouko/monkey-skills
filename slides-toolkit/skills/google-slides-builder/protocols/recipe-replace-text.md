# Recipe — replace-text

對剛複製的 deck 跑一次 `presentations.batchUpdate`，用 `replaceAllText` 請求把所有 `{{PLACEHOLDER}}` 換成實際內容。對應 TECH-SPEC §4.3 table row 2。

## 目的

- 將 `slide-plan.json` 中所有 `slides[].replacements` map 攤平成 batchUpdate requests
- 一次 API call 完成全 deck 文字替換（比逐頁呼叫省配額）
- 回報每個 key 的 `occurrencesChanged`；為 0 的 key 歸類為 13a warning

## Input

```json
{
  "presentation_id": "1NewCopy_AbCdEf",
  "slides": [
    {
      "slide_index": 0,
      "replacements": {
        "{{TITLE}}": "2026-W17 Progress",
        "{{DATE}}": "2026-04-23"
      }
    },
    {
      "slide_index": 3,
      "replacements": {
        "{{HEADLINE}}": "Shipped v1.14.0",
        "{{BODY_1}}": "90 anchors / 5 JP craft-gate"
      }
    }
  ]
}
```

| Field | Required | Note |
|---|---|---|
| `presentation_id` | yes | 由 `recipe-copy-template` 傳來 |
| `slides[].replacements` | no | 若整份 deck 皆無替換文字，略過本 recipe |

## 步驟

### 1. 攤平 replacements（跨 slide 合併）

`replaceAllText` 是 **deck-wide** scope——會掃全 deck 所有 text run；因此不需按 slide 拆。將所有 slide 的 `replacements` merge 成單一 map（相同 key 會後寫覆蓋前寫；此情境通常不會碰撞因 placeholder 慣例以 `{{BODY_1}} / {{BODY_2}}` 明編號）。

```bash
# Pseudo-code intent (using jq)
flat=$(jq '[.slides[].replacements // {}] | add // {}' slide-plan.json)
```

### 2. 組 batchUpdate body

對每一個 `{{KEY}}: value`，產一筆 `replaceAllText` request：

```json
{
  "replaceAllText": {
    "containsText": {
      "text": "{{KEY}}",
      "matchCase": true
    },
    "replaceText": "value"
  }
}
```

用 `jq` 把 flat map 轉成 requests array：

```bash
requests=$(echo "$flat" | jq '[to_entries[] | {
  replaceAllText: {
    containsText: {text: .key, matchCase: true},
    replaceText: .value
  }
}]')

body=$(jq -n --argjson r "$requests" '{requests: $r}')
```

**UTF-8 注意**：value 含日文 / 中文 / emoji 時，`jq` 需在 UTF-8 locale 執行；`gws-wrap.sh` 已在首行 `export LC_ALL=en_US.UTF-8`（TECH-SPEC §8.5）。

### 3. 呼叫 batchUpdate

```bash
echo "$body" | scripts/google-slides/gws-wrap.sh slides presentations batchUpdate \
  --presentationId="$presentation_id" \
  --json-stdin
```

### 4. 解析 replies

response 結構：

```json
{
  "presentationId": "1NewCopy_AbCdEf",
  "replies": [
    {"replaceAllText": {"occurrencesChanged": 1}},
    {"replaceAllText": {"occurrencesChanged": 0}},
    ...
  ]
}
```

對照 requests array 的順序（同 index），把 `occurrencesChanged == 0` 的 key 收集成 warning list：

```bash
zero_keys=$(jq -r '
  [.replies | to_entries[]
    | select(.value.replaceAllText.occurrencesChanged == 0)
    | .key] as $idx
  | $idx
' response.json)
```

### 5. Warning 判定（exit 13a）

若 `zero_keys` 非空 → 把每個對應 key 名附 subcode `13a` 加到總 warnings，但 pipeline **繼續**跑下一 recipe；不 abort。

stderr 訊息範例：
```
[warn 13a] replaceAllText: {{FOO}} 在 template 中一個也找不到（occurrencesChanged=0）
```

## 注意事項

- **Placeholder 命名慣例**：一律 `{{UPPER_CASE_WITH_UNDERSCORE}}`（例：`{{TITLE}}`、`{{BODY_1}}`、`{{IMG_MAIN}}`）。避免和 Slides 原生 merge field（`<<name>>`）語法碰撞。
- **UTF-8 only**：value 內容若含 Shift_JIS / Big5 / GBK，pre-flight 需先 `iconv` 轉 UTF-8（MVP 不自動處理；見 TECH-SPEC §8.5）。
- **大 batch（>100 placeholder）**：單次 batchUpdate 上限 Google 未公開但實測 500 requests 穩定；若遇到超過，建議切成每 100 一批、串列呼叫（MVP 不自動切，由 user 判斷）。
- **`matchCase: true`** 預設開；avoid accidental match（例 `{{title}}` 不會被 `{{TITLE}}` 的 request 打到）。
- **空 replacements**：若整份 deck 所有 slide 的 `replacements` 皆為 `{}` 或不存在 → skip 本 recipe，直接進下一步。

## 錯誤對映

| 情境 | Exit | Stderr |
|---|---|---|
| 任一 key 零 replacement | **13a**（warning，non-fatal） | `[warn 13a] {{KEY}} occurrencesChanged=0` |
| batchUpdate 回 400 / malformed request | 15 | `schema validation failed` |
| Token 過期 | 10 | `401 / invalid_grant` |
| 429 重試 5 次仍敗 | 11 | `rate limit exhausted` |

## Example

**Input**（精簡）：

```json
{
  "presentation_id": "1NewCopy_AbCdEf",
  "slides": [
    {"replacements": {"{{TITLE}}": "週報 W17", "{{DATE}}": "2026-04-23"}},
    {"replacements": {"{{BODY_1}}": "v1.14.0 shipped"}}
  ]
}
```

**Flat map**:

```json
{
  "{{TITLE}}": "週報 W17",
  "{{DATE}}": "2026-04-23",
  "{{BODY_1}}": "v1.14.0 shipped"
}
```

**batchUpdate body**:

```json
{
  "requests": [
    {"replaceAllText": {"containsText": {"text": "{{TITLE}}", "matchCase": true}, "replaceText": "週報 W17"}},
    {"replaceAllText": {"containsText": {"text": "{{DATE}}", "matchCase": true}, "replaceText": "2026-04-23"}},
    {"replaceAllText": {"containsText": {"text": "{{BODY_1}}", "matchCase": true}, "replaceText": "v1.14.0 shipped"}}
  ]
}
```

**Response**:

```json
{
  "presentationId": "1NewCopy_AbCdEf",
  "replies": [
    {"replaceAllText": {"occurrencesChanged": 1}},
    {"replaceAllText": {"occurrencesChanged": 1}},
    {"replaceAllText": {"occurrencesChanged": 0}}
  ]
}
```

**Output**（給下一 recipe 的 warning 帶入）：

```json
{
  "presentation_id": "1NewCopy_AbCdEf",
  "warnings": ["13a: {{BODY_1}} occurrencesChanged=0"]
}
```

---

**See also**: TECH-SPEC §4.2（exit 13 sub-semantics）、§4.3、§8.5（UTF-8 unification）。
