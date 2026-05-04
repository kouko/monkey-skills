# Recipe — insert-text

Run a single `presentations.batchUpdate` against the freshly built slides. Use `insertText` requests to write text directly into the placeholder `objectId`s returned by `createSlide`. Corresponds to TECH-SPEC §4.3 recipe table row 3.

## Purpose

- Expand each slide's `replacements` map into `insertText` requests via **placeholder role → objectId** lookup
- Insert text for the entire deck in a single batchUpdate call
- Do not use `replaceAllText` + `{{PLACEHOLDER}}` text anchors (the v0.3 template workflow removed this)

**Because** in the create-from-scratch model the placeholders come from Google's built-in layouts and have stable `objectId`s, so `insertText` can target them directly. This avoids the side effect where `replaceAllText` fails to match an empty layout placeholder (freshly created, no existing text to replace).

## Input

| Field | Required | From | Note |
|---|---|---|---|
| `presentation_id` | yes | `recipe-create-presentation` | — |
| `placeholder_map` | yes | `recipe-create-slides` | `{slide_X: {ROLE: objectId}}` |
| `slides[].slide_index` | yes | slide plan | — |
| `slides[].replacements` | no | slide plan | shape `{"{{ROLE}}": "value"}` |

If no slide has replacements → skip this recipe.

## Key → placeholder role mapping

In the slide plan, `replacements` keys take the form `{{ROLE}}` (role name wrapped in double braces). After **stripping the braces**, the role maps to a key in `placeholder_map[slide_X]`:

| replacements key | role (stripped) | placeholder-map key |
|---|---|---|
| `{{TITLE}}` | `TITLE` | `TITLE`, **falling back to `CENTERED_TITLE` when the slide uses TITLE layout** |
| `{{SUBTITLE}}` | `SUBTITLE` | `SUBTITLE` |
| `{{BODY_1}}` | `BODY_1` | `BODY_1` |
| `{{BODY_2}}` | `BODY_2` | `BODY_2` |
| `{{heading}}` | `HEADING` | — (invalid; no such role) |

**Rules**:
1. Strip `{{` and `}}`
2. Uppercase the result (`HEADING` / `TITLE` / `BODY_1`)
3. The role must exist in the layout's actual placeholders (as provided by `placeholder_map[slide_X]`)
4. **`TITLE` fallback**: if `placeholder_map[slide_X]` lacks `TITLE` but has `CENTERED_TITLE` (the cover-page TITLE-layout case), route `{{TITLE}}` to the `CENTERED_TITLE` objectId
5. If not found → **13a warning** (non-fatal; recorded in `warnings[]`)

**Because** the placeholder-role names (`TITLE` / `CENTERED_TITLE` / `BODY` / `SUBTITLE` etc.) come from the Google Slides API `Placeholder.type` enum (see TECH-SPEC §4.1); the TITLE layout only returns `CENTERED_TITLE` (not `TITLE`) in practice, so the `{{TITLE}}` mapping needs this fallback to avoid emitting 13a warnings for every cover page.

## Steps

### 1. Expand replacements → insertText requests

For each slide, for each replacement:

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

jq equivalent (pseudo; with `TITLE` → `CENTERED_TITLE` fallback):

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

### 2. Invoke batchUpdate

```bash
echo "$body" | scripts/gws/gws-wrap.sh slides presentations batchUpdate \
  --params "{\"presentationId\":\"$presentation_id\"}" \
  --json-stdin
```

**Live-tested gws CLI rules**: `presentationId` goes inside `--params` (not as `--presentationId=`); the `requests` body goes into `--json` / `--json-stdin`.

**gws command**:

```bash
gws slides presentations batchUpdate \
  --params "{\"presentationId\":\"$DECK_ID\"}" \
  --json '{"requests":[{"insertText":{"objectId":"<placeholder_object_id>","text":"<content>"}}]}'
```

### 3. Parse replies

```json
{"replies":[{}, {}, ...]}
```

In practice, a successful `insertText` reply is an **empty object `{}`** (not `{"insertText":{}}`). The API does not return an occurrence count; a nonexistent `objectId` fails at the request level with a 400 → exit 12/15.

### 4. Collect warnings

The 13a warnings gathered in step 1 are appended to the pipeline's warnings list; **do not abort**. The pipeline continues into `recipe-insert-image`.

## Error mapping

| Situation | Exit | Stderr |
|---|---|---|
| Stripped role not found in `placeholder_map` | **13a** (warning; non-fatal) | `[warn 13a] slide_<N> role=<ROLE> not found in layout` |
| `insertText` returns 400 (`objectId` not found) | 12 | `object not found: <objectId>` |
| Token expired | 10 | `401 / invalid_grant` |
| 429 retries exhausted | 11 | `rate limit exhausted` |
| Empty body (no replacements anywhere) | 0 | skip (info) |

## Notes

- **Omitting `insertionIndex`**: in practice, omitting `insertionIndex` appends to the end of the text box; for an empty placeholder that is equivalent to writing from position 0. If you need to insert at an explicit offset, Google's API still accepts `insertionIndex: 0`, but it is not required.
- **UTF-8 only**: values with Japanese / Chinese / emoji flow through `jq` + `gws` without special handling; `gws-wrap.sh` sets `export LC_ALL=en_US.UTF-8` at the top (TECH-SPEC §8.5).
- **`BLANK` layout slides**: no placeholders. Any replacements targeting a `BLANK` slide produce 13a warnings (layout selection should have avoided this upstream).
- **Empty `replacements`**: if the deck has no replacements at all, skip this recipe and go straight to `recipe-insert-image`.
- **Key casing**: prefer upper-case keys in the plan (`{{TITLE}}` rather than `{{title}}`); the uppercase rule here is a fallback.
- **`{{TITLE}}` → `CENTERED_TITLE` fallback**: cover slides in TITLE layout only expose `CENTERED_TITLE`; writing `{{TITLE}}` on the plan side still resolves via the mapping rule #4.

## Example

**Input**:

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

**Expanded requests** (`{{TITLE}}` on slide_0 falls back to the `CENTERED_TITLE` objectId):

```json
[
  {"insertText":{"objectId":"g_0_title","text":"週報 W17"}},
  {"insertText":{"objectId":"g_0_sub","text":"2026-04-23"}},
  {"insertText":{"objectId":"g_2_title","text":"Shipped v1.14.0"}},
  {"insertText":{"objectId":"g_2_body","text":"anchor autonomy\nformat unification"}}
]
```

Note: slide_0's actual placeholder map is `{"CENTERED_TITLE": "g_0_title", "SUBTITLE": "g_0_sub"}` (no `TITLE`); `{{TITLE}}` resolves via mapping rule #4 to `CENTERED_TITLE`.

**gws call**:

```bash
gws slides presentations batchUpdate \
  --params '{"presentationId":"1NewDeckAbCdEf"}' \
  --json '{"requests":[{"insertText":{"objectId":"g_0_title","text":"週報 W17"}}, ...]}'
```

**Output** (handed off downstream):

```json
{
  "presentation_id": "1NewDeckAbCdEf",
  "text_inserts_success": 4,
  "warnings": []
}
```

## Live-tested behavior (2026-04-24)

- Minimal `insertText` request body: `{"objectId":"<placeholder_object_id>","text":"<content>"}`; `insertionIndex` is optional.
- The `text` field supports UTF-8: Traditional Chinese / Japanese / emoji (✓ / 🎉 etc.) write directly into a Slides placeholder without escaping.
- `\n` inside `text` produces a line break (equivalent to a shift+enter soft break in Slides).
- Each successful `insertText` in the batch reply is an empty `{}` object (the reply does not repeat the request type name): `{"replies":[{}, {}, {}, {}]}`.
- stderr prints `Using keyring backend: keyring` on every call (normal, not an error).

---

**See also**: TECH-SPEC §4.2 exit 13a, §4.3 recipe row 3, §4.6 E2E data flow step 3, §8.5 (UTF-8); PRODUCT-SPEC §4.4 Principle 2.
