# Recipe — create-presentation

Call `gws slides presentations create` to create a **blank** new Google Slides deck as the target for the downstream recipes (`recipe-create-slides` / `recipe-insert-text` / `recipe-insert-image`). Corresponds to TECH-SPEC §4.3 recipe table row 1.

## Purpose

- Use the slide plan's top-level `output_title` as the new deck's `title`
- Create an empty deck (no slides) in a single API call and obtain a fresh `presentationId`
- Pass `presentationId` downstream (consumed by `recipe-create-slides`)
- No template copy (removed in v0.3; see PRODUCT-SPEC §3.2 Non-Goal)

**Because** create-from-scratch has zero template-management overhead, zero risk of leaking a Drive ID, and zero schema drift (PRODUCT-SPEC v0.3 §4.4 Principle 2 — Layout-based).

## Input

| Field | Required | From | Note |
|---|---|---|---|
| `output_title` | yes | top-level of slide plan | UTF-8 only; non-empty |

```json
{
  "output_title": "2026-W17 Weekly Report"
}
```

## Steps

### 1. Read `output_title`

```bash
title=$(jq -r '.output_title' slide-plan.json)
[[ -n "$title" ]] || { echo "missing output_title" >&2; exit 15; }
```

### 2. Invoke gws

```bash
body=$(jq -n --arg t "$title" '{title: $t}')

resp=$(echo "$body" | scripts/gws/gws-wrap.sh slides presentations create \
  --json-stdin)
```

**Live-tested gws CLI invocation**:

```bash
gws slides presentations create --json '{"title":"<output_title>"}'
```

- No path parameter (`presentations.create` has no `presentationId` input)
- Entire body goes into `--json` (or `--json-stdin`)
- stderr always prints `Using keyring backend: keyring` (informational, not an error; stdout remains clean JSON)

### 3. Parse the response

Live-tested response (abbreviated):

```json
{
  "presentationId": "1NewDeckAbCdEf",
  "title": "2026-W17 Weekly Report",
  "pageSize": {"width": {...}, "height": {...}, "unit": "EMU"},
  "layouts": [ /* every predefined layout definition (TITLE / TITLE_AND_BODY / ...) */ ],
  "masters": [ /* master slide */ ],
  "slides": [
    {
      "objectId": "<default_slide_id>",
      "pageElements": [
        {"objectId": "...", "shape": {"placeholder": {"type": "CENTERED_TITLE"}}},
        {"objectId": "...", "shape": {"placeholder": {"type": "SUBTITLE"}}}
      ]
    }
  ]
}
```

**Note**: `presentations.create` returns **one default slide** (layout `TITLE`) containing two placeholders: **`CENTERED_TITLE`** and **`SUBTITLE`** (not `TITLE` — Google Slides' `Placeholder.type` uses `CENTERED_TITLE` for the TITLE layout). The top-level `layouts[]` array also returns the full definition of every predefined layout, useful for downstream debugging.

Downstream strategy in `recipe-create-slides`: if the plan's `slides[0].layout_hint == "TITLE"`, keep the default slide and fold it into the placeholder map (mapping roles `CENTERED_TITLE` / `SUBTITLE`); otherwise issue a `deleteObject` request to remove it first.

Extract `presentationId`:

```bash
deck_id=$(echo "$resp" | jq -r '.presentationId')
```

### 3b. Fetch default-slide placeholder object IDs (if reusing)

```bash
gws slides presentations get \
  --params "{\"presentationId\":\"$deck_id\",\"fields\":\"slides(objectId,pageElements(objectId,shape(placeholder(type))))\"}"
```

- **Note**: `presentationId` goes inside the `--params` JSON, **not** as a standalone flag (the gws CLI places every path parameter inside `--params`)
- `fields` also lives inside the same `--params` JSON
- The top-level reply JSON is `{"slides":[{"objectId":"...","pageElements":[...]}]}`

### 4. Hand off downstream

```json
{
  "presentation_id": "1NewDeckAbCdEf",
  "deck_url": "https://docs.google.com/presentation/d/1NewDeckAbCdEf/edit"
}
```

## Error mapping

| Situation | Exit | Stderr |
|---|---|---|
| `output_title` missing / not a string / empty | 15 | `schema validation failed: output_title` |
| Token expired | 10 | `401 / invalid_grant; run gws auth login` |
| 403 forbidden (missing scope / Drive quota / policy) | **10** | `insufficient permissions — check presentations + drive.file scope` |
| 429 still failing after 5 retries | **11** | `rate limit exhausted` |
| Other 5xx | determined by `gws-wrap.sh` (retry); exhausted → 11 | — |
| Response missing `presentationId` | 12 | `create failed: no presentationId in response` |

**Note**: in the v0.3 exit-code table (TECH-SPEC §4.2), exit 10 covers both unauthenticated and scope-missing cases; 403 is mapped to 10 so Claude can route uniformly to `gws-setup` for re-auth.

## Notes

- **UTF-8 only**: Japanese / Chinese / emoji content in `output_title` works fine through gws, but `jq` must run in a UTF-8 locale. `gws-wrap.sh` sets `export LC_ALL=en_US.UTF-8` at the top (TECH-SPEC §8.5).
- **Dry-run**: when `dry_run: true`, this recipe is **not executed**; pre-flight short-circuits and returns `{"url":null,"presentation_id":null,...}` (see pre-flight item 10 in `checklists/pre-flight.md`).
- **No Drive folder selection**: MVP places the new deck in the user's Drive root. Folder placement is Phase 2+ (no confirmed trigger).

## Example

**Input** (excerpted from the slide plan):

```json
{
  "output_title": "2026-W17 週報"
}
```

**gws command**:

```bash
gws slides presentations create --json '{"title":"2026-W17 週報"}'
```

**Response** (abbreviated):

```json
{
  "presentationId": "1Xyz123NewDeck",
  "title": "2026-W17 週報",
  "slides": [{
    "objectId": "g_default_slide",
    "pageElements": [
      {"objectId": "g_default_title", "shape": {"placeholder": {"type": "CENTERED_TITLE"}}},
      {"objectId": "g_default_sub",   "shape": {"placeholder": {"type": "SUBTITLE"}}}
    ]
  }]
}
```

**Output** (handed off downstream):

```json
{
  "presentation_id": "1Xyz123NewDeck",
  "deck_url": "https://docs.google.com/presentation/d/1Xyz123NewDeck/edit"
}
```

## Live-tested behavior (2026-04-24)

Observed while running `gws slides presentations create --json '{"title":"..."}'`:

- stderr always prints `Using keyring backend: keyring` (single line, not an error — gws is reading the token store). Callers that want pure-JSON stdout should redirect with `2>/dev/null` or `2>err.log`.
- Top-level stdout JSON includes `presentationId` / `title` / `pageSize` / `slides[]` / `layouts[]` (every predefined layout definition) / `masters[]` / `notesMaster` / `revisionId`.
- The new deck **already contains one default slide** (layout = TITLE) with **two placeholders**: `CENTERED_TITLE` (not `TITLE`) and `SUBTITLE`.
- Deck URL format is fixed: `https://docs.google.com/presentation/d/<presentationId>/edit`.
- For `presentations.get`, both `presentationId` and `fields` go inside `--params`: `gws slides presentations get --params "{\"presentationId\":\"$DECK_ID\",\"fields\":\"slides(objectId,pageElements(objectId,shape(placeholder(type))))\"}"`.

---

**See also**: TECH-SPEC §4.2 exit codes, §4.3 recipe table row 1, §4.6 E2E data flow step 1; PRODUCT-SPEC §4.4 Principle 2 (Layout-based).
