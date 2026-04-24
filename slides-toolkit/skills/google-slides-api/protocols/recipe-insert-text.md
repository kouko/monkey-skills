# Recipe — insert-text

對剛建好的 slides 跑一次 `presentations.batchUpdate`，用 `insertText` requests 直接把文字插入 `createSlide` 回傳的 placeholder `objectId`。對應 TECH-SPEC §4.3 recipe table row 3。

## 目的

- 把 `slide-plan.json` 各頁 `replacements` map 以 **placeholder role → objectId** 對映方式展開成 `insertText` requests
- 一次 API call 完成全 deck 文字插入（deck-wide batchUpdate）
- 不再使用 `replaceAllText` + `{{PLACEHOLDER}}` 文字錨點（v0.3 移除 template workflow）

**Because** create-from-scratch 模型下 placeholder 由 Google 內建 layout 提供，有穩定 `objectId`，可直接 `insertText` 定位；避免 `replaceAllText` 在空 layout placeholder（首次建立、尚無任何文字）情境下不會命中的副作用。

## Input

| Field | Required | From | Note |
|---|---|---|---|
| `presentation_id` | yes | `recipe-create-presentation` | — |
| `placeholder_map` | yes | `recipe-create-slides` | `{slide_X: {ROLE: objectId}}` |
| `slides[].slide_index` | yes | `slide-plan.json` | — |
| `slides[].replacements` | no | `slide-plan.json` | `{"{{ROLE}}": "value"}` 形式 |

若整份 deck 皆無 replacements → skip 本 recipe。

## Key → placeholder role 對映規則

`slide-plan.json` 中 `replacements` 的 key 形式為 `{{ROLE}}`（雙大括號包 role 名），**剝殼後**對應 `placeholder_map[slide_X]` 的 key：

| replacements key | role (剝殼後) | 對應 placeholder_map key |
|---|---|---|
| `{{TITLE}}` | `TITLE` | `TITLE`，**若該 slide 是 TITLE layout 則 fallback 到 `CENTERED_TITLE`** |
| `{{SUBTITLE}}` | `SUBTITLE` | `SUBTITLE` |
| `{{BODY_1}}` | `BODY_1` | `BODY_1` |
| `{{BODY_2}}` | `BODY_2` | `BODY_2` |
| `{{heading}}` | `HEADING` | — (invalid；無此 role) |

**規則**：
1. `{{` 與 `}}` 剝殼
2. 剝殼後**轉大寫**（`HEADING` / `TITLE` / `BODY_1`）
3. 必須屬 layout 內實際存在的 placeholder role（由 `placeholder_map[slide_X]` 提供）
4. **`TITLE` fallback**：若 `placeholder_map[slide_X]` 無 `TITLE` 但有 `CENTERED_TITLE`（封面頁 TITLE layout 情境），把 `{{TITLE}}` 導向 `CENTERED_TITLE` 的 objectId
5. 找不到 → **13a warning**（non-fatal；記到 warnings[]）

**Because** placeholder role 名（`TITLE` / `CENTERED_TITLE` / `BODY` / `SUBTITLE` 等）來自 Google Slides API `Placeholder.type` enum（見 TECH-SPEC §4.1）；TITLE layout 實測只會回 `CENTERED_TITLE`（不是 `TITLE`），所以 `{{TITLE}}` 對映邏輯要加這層 fallback 才不會把封面頁全部擲到 13a warning。

## 步驟

### 1. 展開 replacements → insertText requests

對每個 slide 的每個 replacement：

```bash
# Pseudo-code intent
for slide in plan.slides:
    slide_key = "slide_" + slide.slide_index
    pm = placeholder_map[slide_key]
    for k, v in slide.replacements.items():
        role = k.strip("{}").upper()  # {{TITLE}} -> TITLE
        obj_id = pm.get(role)
        # TITLE layout fallback: {{TITLE}} → CENTERED_TITLE if TITLE absent
        if obj_id is None and role == "TITLE":
            obj_id = pm.get("CENTERED_TITLE")
        if obj_id is None:
            warnings.append(f"13a: slide_{slide.slide_index} role={role} not found in layout")
            continue
        requests.append({
          "insertText": {
            "objectId": obj_id,
            "text": v
          }
        })
```

jq 等價（pseudo；含 TITLE → CENTERED_TITLE fallback）：

```bash
requests=$(jq --argjson pm "$placeholder_map" '
  [ .slides[] as $s
    | ("slide_" + ($s.slide_index | tostring)) as $sk
    | ($s.replacements // {}) | to_entries[]
    | . as $kv
    | ($kv.key | gsub("[{}]"; "") | ascii_upcase) as $role
    | ( $pm[$sk][$role]
        // ( if $role == "TITLE" then $pm[$sk]["CENTERED_TITLE"] else null end )
      ) as $oid
    | select($oid != null)
    | {
        insertText: {
          objectId: $oid,
          text: $kv.value
        }
      }
  ]
' slide-plan.json)

body=$(jq -n --argjson r "$requests" '{requests: $r}')
```

### 2. 呼叫 batchUpdate

```bash
echo "$body" | scripts/google-slides/gws-wrap.sh slides presentations batchUpdate \
  --params "{\"presentationId\":\"$presentation_id\"}" \
  --json-stdin
```

**實測 gws CLI 規則**：`presentationId` 塞 `--params`（不是 `--presentationId=` flag）；body requests 放 `--json` / `--json-stdin`。

**gws 命令**：

```bash
gws slides presentations batchUpdate \
  --params "{\"presentationId\":\"$DECK_ID\"}" \
  --json '{"requests":[{"insertText":{"objectId":"<placeholder_object_id>","text":"<content>"}}]}'
```

### 3. 解析 replies

```json
{"replies":[{}, {}, ...]}
```

實測 `insertText` 的 reply 是**空物件 `{}`**（不是 `{"insertText":{}}`）即代表成功（API 不回 occurrence count；不存在的 objectId 會在 request 層即回 400 → exit 12/15）。

### 4. 整理 warnings

步驟 1 收集到的 13a warnings 全部加進 pipeline warnings list，**不 abort**；pipeline 繼續跑 `recipe-insert-image`。

## 錯誤對映

| 情境 | Exit | Stderr |
|---|---|---|
| replacement key 剝殼後 role 找不到對應 `placeholder_map` entry | **13a**（warning；non-fatal） | `[warn 13a] slide_<N> role=<ROLE> not found in layout` |
| `insertText` 回 400（`objectId` 不存在） | 12 | `object not found: <objectId>` |
| Token 過期 | 10 | `401 / invalid_grant` |
| 429 重試耗盡 | 11 | `rate limit exhausted` |
| body 為空（全無 replacements） | 0 | skip (info) |

## 注意事項

- **省略 `insertionIndex`**：實測 `insertText` 省略 `insertionIndex` 即 append 到 text box 末端（一般 placeholder 初始為空，append 等同從頭寫入）；若明確要從 0 插入，Google API 規範仍允許帶 `insertionIndex: 0`，但非必要
- **UTF-8 only**：value 含日文 / 中文 / emoji 時 `jq` + `gws` 處理無虞；`gws-wrap.sh` 首行 `export LC_ALL=en_US.UTF-8`（TECH-SPEC §8.5）
- **`BLANK` layout slide**：無 placeholder；對 `BLANK` slide 下 replacements 一律為 13a warning（layout 選擇階段就該避免）
- **空 `replacements`**：若整份 deck 無 replacements → skip 本 recipe，直接進 `recipe-insert-image`
- **Key 大小寫**：建議 plan 產出時就用大寫 key（如 `{{TITLE}}` 而非 `{{title}}`）；本 recipe 的 upper-case 規則是 fallback
- **`{{TITLE}}` → `CENTERED_TITLE` fallback**：封面頁 TITLE layout 只有 `CENTERED_TITLE`，plan 側用 `{{TITLE}}` 仍可命中（本 recipe 的對映規則第 4 條）

## Example

**Input**：

```json
{
  "presentation_id": "1NewDeckAbCdEf",
  "placeholder_map": {
    "slide_0": {"TITLE": "g_0_title", "SUBTITLE": "g_0_sub"},
    "slide_2": {"TITLE": "g_2_title", "BODY_1": "g_2_body"}
  },
  "slides": [
    {"slide_index": 0, "replacements": {"{{TITLE}}": "週報 W17", "{{SUBTITLE}}": "2026-04-23"}},
    {"slide_index": 2, "replacements": {"{{TITLE}}": "Shipped v1.14.0", "{{BODY_1}}": "anchor autonomy\\nformat unification"}}
  ]
}
```

**展開後 requests**（`{{TITLE}}` on slide_0 經 fallback 對到 `CENTERED_TITLE` 的 objectId）：

```json
[
  {"insertText":{"objectId":"g_0_title","text":"週報 W17"}},
  {"insertText":{"objectId":"g_0_sub","text":"2026-04-23"}},
  {"insertText":{"objectId":"g_2_title","text":"Shipped v1.14.0"}},
  {"insertText":{"objectId":"g_2_body","text":"anchor autonomy\nformat unification"}}
]
```

注意 slide_0 的 `placeholder_map` 實際是 `{"CENTERED_TITLE": "g_0_title", "SUBTITLE": "g_0_sub"}`（非 `TITLE`）；`{{TITLE}}` 由對映規則第 4 條 fallback 到 `CENTERED_TITLE`。

**gws 呼叫**：

```bash
gws slides presentations batchUpdate \
  --params '{"presentationId":"1NewDeckAbCdEf"}' \
  --json '{"requests":[{"insertText":{"objectId":"g_0_title","text":"週報 W17"}}, ...]}'
```

**Output**（往下游傳）：

```json
{
  "presentation_id": "1NewDeckAbCdEf",
  "text_inserts_success": 4,
  "warnings": []
}
```

## Live-tested behavior (2026-04-24)

- `insertText` request body 最精簡寫法：`{"objectId":"<placeholder_object_id>","text":"<content>"}`；`insertionIndex` 可省
- `text` 欄位支援 UTF-8：繁中 / 日文 / emoji（✓ / 🎉 等）實測可直接寫入 Slides placeholder，無需 escape
- `\n` 在 `text` 內實測能建立換行段落（Slides 內即 shift+enter 的軟換行）
- Batch reply 每個成功的 `insertText` 對映一個 `{}` 空物件（整個 reply 不重複 request 類型名）：`{"replies":[{}, {}, {}, {}]}`
- stderr 每次印 `Using keyring backend: keyring`（正常，非錯誤）

---

**See also**: TECH-SPEC §4.2 exit 13a、§4.3 recipe row 3、§4.6 E2E data flow step 3、§8.5（UTF-8）；PRODUCT-SPEC §4.4 Principle 2。
