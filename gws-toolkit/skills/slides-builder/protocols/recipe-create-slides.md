# Recipe — create-slides

Run a single `presentations.batchUpdate` against the freshly created empty deck, using `createSlide` requests to build each page, with `slideLayoutReference.predefinedLayout` specifying a Google built-in layout per slide. Parse the response to extract each slide's placeholder `objectId`s and build the **placeholder map** for downstream recipes. Corresponds to TECH-SPEC §4.3 recipe table row 2.

## Purpose

- Iterate through the slide plan's `slides[]` array and `createSlide` each page in order
- Use the `layout_hint` enum to select a Google predefined layout
- Parse the `createSlide` response and assemble a **placeholder map** keyed by each slide's placeholder `objectId`
- Hand the placeholder map off to `recipe-insert-text` and `recipe-insert-image`

**Because** using Google's built-in predefined layouts (`TITLE` / `TITLE_AND_BODY` / ...) avoids the placeholder-drift risk that comes with template copy, and Google guarantees the layout has baseline visual readability (PRODUCT-SPEC v0.3 §4.4 Principle 2).

## Input

| Field | Required | Note |
|---|---|---|
| `presentation_id` | yes | handed off from `recipe-create-presentation` |
| `slides[].slide_index` | yes | `>= 0`; determines insertion order |
| `slides[].layout_hint` | yes | **must be one of the 7 enum values** |

`layout_hint` is **restricted to 7 values** (corresponding to Google Slides API `Page.slideProperties.layoutObjectId` → `predefinedLayout`; see TECH-SPEC §4.1):

| enum | Use |
|---|---|
| `TITLE` | Cover or section cover |
| `TITLE_AND_BODY` | Standard body page (title + bulleted content) |
| `TITLE_AND_TWO_COLUMNS` | Two-column comparison (left + right blocks) |
| `SECTION_HEADER` | Section break (large heading) |
| `MAIN_POINT` | Single-focus emphasis page |
| `BIG_NUMBER` | Large-number callout (KPI / metric) |
| `BLANK` | Blank page (free layout; no default placeholders) |

**Any other value → exit 15** (pre-flight already catches this; defense-in-depth if it reaches this recipe).

## Steps

### 1. Handle the default first slide

`presentations.create` returns a deck with **one default slide** (usually layout `TITLE`). Strategy:

- If the plan's `slides[0].layout_hint == "TITLE"` → **keep** the default slide as `slide_index: 0`; subsequent `createSlide` requests start from index 1
- Otherwise → issue a `deleteObject` request to remove the default first, then `createSlide` all entries starting from `slide_index: 0`

**Because** keeping and reusing is one round trip cheaper than delete + recreate; but on a layout mismatch it is not worth using `updatePageProperties` to patch `layoutReference` (cross-master / layout references can break).

### 2. Assemble the batchUpdate body

Generate one `createSlide` request per entry in `slides[]`:

```json
{
  "createSlide": {
    "objectId": "slide_${index}",
    "insertionIndex": "${index}",
    "slideLayoutReference": {
      "predefinedLayout": "${layout_hint}"
    }
  }
}
```

Flatten with `jq` in one pass:

```bash
requests=$(jq '[
  .slides[] | {
    createSlide: {
      objectId: ("slide_" + (.slide_index | tostring)),
      insertionIndex: (.slide_index | tostring),
      slideLayoutReference: { predefinedLayout: .layout_hint }
    }
  }
]' slide-plan.json)

body=$(jq -n --argjson r "$requests" '{requests: $r}')
```

### 3. Invoke batchUpdate

```bash
scripts/gws/gws-wrap.sh slides presentations batchUpdate \
  --params "{\"presentationId\":\"$presentation_id\"}" \
  --json "$body"
```

**Live-tested gws CLI rules**:

- `presentationId` is a path parameter → must go inside the `--params '{"presentationId":"..."}'` JSON, **not** as a standalone `--presentationId=` flag
- The `requests` body goes into `--json '<JSON>'` (a flag value; `gws` v0.22.5 has no stdin variant)
- stderr always prints `Using keyring backend: keyring` (informational)

**Complete gws command example**:

```bash
gws slides presentations batchUpdate \
  --params "{\"presentationId\":\"$DECK_ID\"}" \
  --json '{"requests":[{"createSlide":{"objectId":"slide_body","slideLayoutReference":{"predefinedLayout":"TITLE_AND_BODY"}}}]}'
```

### 4. Parse response → placeholder map

Response shape (simplified):

```json
{
  "replies": [
    {"createSlide": {"objectId": "slide_0"}},
    {"createSlide": {"objectId": "slide_1"}}
  ]
}
```

**The `createSlide` reply does not include placeholder `objectId`s** — you must follow up with a `presentations.get` (or a per-slide `pages.get`) to read `pageElements`, where each `pageElement.shape.placeholder` carries both `type` and `objectId`.

**Recommended flow** (minimum API calls): after `createSlide`, call `presentations.get` once with a `fields` mask that returns `placeholder.type` and `placeholder.index` in a single response:

```bash
scripts/gws/gws-wrap.sh slides presentations get \
  --params "{\"presentationId\":\"$presentation_id\",\"fields\":\"slides(objectId,pageElements(objectId,shape(placeholder(type,index))))\"}"
```

**Live-tested gws CLI rules**: both `presentationId` and `fields` go inside the `--params` JSON; `--presentationId=` / `--fields=` as standalone flags are rejected.

Build the placeholder map from the result (keys are **placeholder roles**, matching the insertText lookup downstream; see `recipe-insert-text.md`):

```json
{
  "slide_0": {
    "CENTERED_TITLE": "g1a2b3_0",
    "SUBTITLE":       "g1a2b3_1"
  },
  "slide_1": {
    "TITLE":  "g4c5d6_0",
    "BODY_1": "g4c5d6_1"
  }
}
```

**Mapping rule**: use `shape.placeholder.type` directly as the placeholder-map key. Common types:

| Layout | Observed `placeholder.type` values |
|---|---|
| `TITLE` (cover) | `CENTERED_TITLE` + `SUBTITLE` |
| `TITLE_AND_BODY` | `TITLE` + `BODY` (single BODY; stored as role key `BODY_1`) |
| `TITLE_AND_TWO_COLUMNS` | `TITLE` + `BODY` × 2 |
| `SECTION_HEADER` | `TITLE` (main heading) |
| `MAIN_POINT` | `TITLE` |
| `BIG_NUMBER` | `TITLE` (big number) + `BODY` |
| `BLANK` | (no placeholders) |

When the same `type` appears multiple times (the two `BODY` entries in `TITLE_AND_TWO_COLUMNS`), number them `BODY_1` / `BODY_2` ordered by `shape.placeholder.index` (0 → `_1`, 1 → `_2`); the `index` field is returned alongside `type` in practice.

**TITLE-layout role quirk**: a cover slide returns `CENTERED_TITLE` as the placeholder type (not `TITLE`). When the plan writes `{{TITLE}}`, the mapping logic in `recipe-insert-text` must route `TITLE` to the layout's actual `CENTERED_TITLE` role (see the mapping table in `recipe-insert-text.md`).

### 5. Hand off downstream

```json
{
  "presentation_id": "1NewDeckAbCdEf",
  "placeholder_map": { /* as above */ },
  "slides_created": N
}
```

## Error mapping

| Situation | Exit | Stderr |
|---|---|---|
| `layout_hint` not in the 7 enum (pre-flight miss) | **15** | `invalid layout_hint "<value>"; must be one of {TITLE, TITLE_AND_BODY, ...}` |
| `createSlide` returns 400 (invalid predefinedLayout) | **15** | same as above |
| API call fails (token / quota / 5xx) | 10 / 11 / **12** | as determined by `gws-wrap.sh` |
| `presentations.get` returns an empty placeholder map (layout has no placeholders, e.g. `BLANK`) | 0 (normal) | stderr info: `slide_N is BLANK, no placeholders` |
| 429 retries exhausted | 11 | `rate limit exhausted` |

## Notes

- **Enum validation belongs in pre-flight** (`checklists/pre-flight.md` item 3); this recipe only runs defense-in-depth
- **`BLANK` layout has no placeholders**: if downstream `recipe-insert-text` receives replacements for a `BLANK` slide, it emits **13a warning**
- **Contiguous `slide_index`**: assumes `slides[].slide_index` is 0, 1, 2, ... without gaps. With gaps, `insertionIndex` semantics follow the **final deck ordering**; generate the plan in order to avoid surprises
- **`createSlide` `objectId`**: set to `slide_<index>` for debuggability; Google accepts 6–50 characters from `a–z A–Z 0–9 _ -`

## Example

**Input** (excerpted from the slide plan):

```json
{
  "presentation_id": "1NewDeckAbCdEf",
  "slides": [
    {"slide_index": 0, "layout_hint": "TITLE"},
    {"slide_index": 1, "layout_hint": "SECTION_HEADER"},
    {"slide_index": 2, "layout_hint": "TITLE_AND_BODY"}
  ]
}
```

**batchUpdate body**:

```json
{
  "requests": [
    {"createSlide": {"objectId":"slide_0","insertionIndex":"0","slideLayoutReference":{"predefinedLayout":"TITLE"}}},
    {"createSlide": {"objectId":"slide_1","insertionIndex":"1","slideLayoutReference":{"predefinedLayout":"SECTION_HEADER"}}},
    {"createSlide": {"objectId":"slide_2","insertionIndex":"2","slideLayoutReference":{"predefinedLayout":"TITLE_AND_BODY"}}}
  ]
}
```

**Response + `presentations.get` → placeholder map**:

```json
{
  "presentation_id": "1NewDeckAbCdEf",
  "placeholder_map": {
    "slide_0": {"CENTERED_TITLE": "g_0_title", "SUBTITLE": "g_0_sub"},
    "slide_1": {"TITLE": "g_1_title"},
    "slide_2": {"TITLE": "g_2_title", "BODY_1": "g_2_body"}
  },
  "slides_created": 3
}
```

## Live-tested behavior (2026-04-24)

Observed from `gws slides presentations batchUpdate` + `presentations.get`:

- A `createSlide` request with `objectId: "slide_body"` (caller-assigned) echoes back in the reply: `{"replies":[{"createSlide":{"objectId":"slide_body"}}]}`
- Caller-assigned `objectId` accepts 6–50 characters from `a–z A–Z 0–9 _ -`; any non-conflicting name works
- `presentations.get` uses Google field-mask syntax in `--params.fields` (e.g. `slides(objectId,pageElements(objectId,shape(placeholder(type,index))))`); the reply JSON is pruned to the mask tree
- The default slide for TITLE layout returns `CENTERED_TITLE` + `SUBTITLE` (**not** `TITLE`); other layouts (`TITLE_AND_BODY` / `SECTION_HEADER` / ...) do return `TITLE`
- stderr prints `Using keyring backend: keyring` on every call (normal)

---

**See also**: TECH-SPEC §4.1 schema v1.2 (`layout_hint` enum), §4.3 recipe row 2, §4.6 E2E data flow step 2; PRODUCT-SPEC §4.4 Principle 2.
