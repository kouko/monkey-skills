---
name: google-slides-builder
description: Execute slide-plan.json v1.2 against Google Slides backend — create blank deck, build slides with Google predefined layouts, insert text to placeholders, insert local images, emit deck URL. Use when user has a structured slide-plan (or equivalent) and asks to generate / 生成 / 匯出 / 做簡報 / create deck / google slides / プレゼン作成. MVP 僅支援 target=google-slides；html / pptx / marp 未實作。
---

# google-slides-builder

**Single-skill end-to-end pipeline for the Google Slides backend.** Read `slide-plan.json` v1.2, validate via pre-flight, then chain four bundled recipes (create-presentation → create-slides → insert-text → insert-image) and return the Drive URL. This skill **does not make design decisions** (go to `slides-design`), **does not handle first-time setup** (auth / gws install → `google-slides-setup`), and **does not manage templates** (removed in v0.3; see PRODUCT-SPEC §3.2 Non-Goals and §3.5 Phase 2+ triggers).

The 4 per-op recipes (formerly the separate `google-slides-api` skill, absorbed in v0.4 α-trim) now live under `protocols/` of this skill. For raw API method discovery (resource × method tables, parameter shapes), use upstream `gws-slides` skill or run `gws schema slides.<resource>.<method>`.

This skill invokes the `gws` CLI through `scripts/google-slides/gws-wrap.sh` (under the plugin root); all shell-script contracts and exit-code mappings are defined in TECH-SPEC §4.2.

## Composition pattern — threading the placeholder map

Recipes compose via a small data artifact called the **placeholder map** — a mapping from `(slide_index, placeholder_role)` to a Slides API `objectId`. It is **produced** by `protocols/recipe-create-slides.md` (from the `createSlide` reply plus a follow-up `presentations.get`) and **consumed** by `recipe-insert-text.md` and `recipe-insert-image.md` to target shapes directly, without relying on fragile `{{TEXT_ANCHOR}}` substitution.

Example shape:

```json
{
  "1": { "TITLE": "p1_title_obj_id", "BODY_1": "p1_body_obj_id" },
  "2": { "TITLE": "p2_title_obj_id", "IMG_MAIN": "p2_img_obj_id" }
}
```

## When to use

- The user has a `slide-plan.json` (schema v1.2) with top-level `target == "google-slides"`
- The user pastes structured input (text outline + local image paths + per-slide `layout_hint`) and asks for an automatic Google Slides deck
- "Run the pipeline" / "Export the deck" / "Turn this plan into Google Slides"

## When NOT to use

- **Design consultation** (Minto / SCQA / chart type / layout choice) → `slides-design`
- **First-time setup** (gws not installed, OAuth not configured, Keychain / env issues) → `google-slides-setup`
- `target != "google-slides"` (html / pptx / marp are all Phase 2+ trigger-gated; see PRODUCT-SPEC §3.5)
- Task is outside the slides-toolkit scope (copywriting → `copywriting-toolkit`; investment analysis → `investing-toolkit`)

## Prerequisites

- `google-slides-setup` has been run once:
  - `~/.cache/slides-toolkit/bin/gws` and `jq` are downloaded (HTTPS + `curl -f`; v0.3 does not pin SHA-256)
  - Google OAuth is granted (scopes: `presentations` + `drive.file`; see TECH-SPEC §4.4)
  - `~/.config/gws/env.sh` includes the issue #119 workaround (if detected)
- Runs on macOS + Claude Code; all input files are **UTF-8 only**

## Layout enum (required values for `layout_hint` in the slide plan)

Every slide's `layout_hint` must be one of the 7 Google Slides API `predefinedLayout` values (TECH-SPEC §4.1):

| enum | Use |
|---|---|
| `TITLE` | Cover or section cover |
| `TITLE_AND_BODY` | Standard body page (title + bulleted content) |
| `TITLE_AND_TWO_COLUMNS` | Two-column comparison |
| `SECTION_HEADER` | Section break (large heading) |
| `MAIN_POINT` | Single-focus emphasis page |
| `BIG_NUMBER` | Large KPI number |
| `BLANK` | Blank (no default placeholders; free layout) |

Any other value → pre-flight exit 15.

## Input contract (slide plan v1.2)

Full schema in TECH-SPEC §4.1. Required top-level fields:

| Field | Type | Required | Note |
|---|---|---|---|
| `version` | string | yes | Must be `"1.2"` |
| `target` | string | yes | MVP only accepts `"google-slides"`; anything else → exit 12 |
| `output_title` | string | yes | New deck file name (UTF-8) |
| `dry_run` | bool | no (default `false`) | `true` → validate schema / `layout_hint` enum / local images only, without calling the API |
| `slides[]` | array | yes | May be empty (creates an empty deck); each slide requires `layout_hint` and may include `replacements` + `images[]` |
| `slides[].slide_index` | int | yes | `>= 0` |
| `slides[].layout_hint` | string | **yes** | Must be one of the 7 enum values |
| `slides[].replacements` | object | no | `{"{{ROLE}}": value}`; ROLE maps to a layout placeholder (TITLE / SUBTITLE / BODY_N etc.; see `recipe-insert-text.md`) |
| `slides[].images[]` | array | no | Each image needs a `placeholder_id` (layout placeholder role) and `local_path`; `~` / absolute / cwd-relative are all accepted |

**v0.3 changes vs v1.1**:
- Removed `backend_config.template_ref` (template workflow removed)
- `layout_hint` changed from a free-form string to a **required enum**
- The `{{ROLE}}` inside `replacements` now maps to a placeholder role (no longer a template text anchor)

## Workflow

Execute the following four steps. If any step fails, report according to the exit-code table and stop.

### Step 1 — Pre-flight check

Run `checklists/pre-flight.md` (10 items; each shell-runnable). All must pass before Step 2. Key validations:
- jq: `.version == "1.2"`, `.target == "google-slides"`, every slide's `.layout_hint` is in the 7-enum
- `gws auth status` token not expired (`credential-check.sh`)
- `scripts/google-slides/env-guard.sh check` does not return exit 16 (issue #119 workaround in place)
- Every `slides[].images[].local_path` exists and is within size limits

### Step 2 — Recipe 1: create-presentation

`protocols/recipe-create-presentation.md`

- gws command: `gws slides presentations create --json '{"title":"<output_title>"}'`
- Input: `output_title`
- Output: new deck's `presentationId` + `deck_url`
- Errors: 403 / missing scope → exit 10; 429 exhausted → exit 11

### Step 3 — Recipe 2: create-slides

`protocols/recipe-create-slides.md`

- gws command: `gws slides presentations batchUpdate` with `createSlide` requests (one per page, specifying `slideLayoutReference.predefinedLayout: <layout_hint>`)
- Input: the previous step's `presentation_id` + `slides[].slide_index` + `slides[].layout_hint`
- Output: the placeholder map (`{slide_X: {ROLE: objectId}}`), assembled from a follow-up `presentations.get`
- Errors: invalid layout enum → exit 15 (pre-flight already catches this); API failure → exit 12

### Step 4 — Recipes 3 + 4: insert-text + insert-image (per slide, as needed)

Execute as each slide requires; within one slide, insert-text runs before insert-image:

**Recipe 3 — insert-text** (`protocols/recipe-insert-text.md`):
- gws command: `gws slides presentations batchUpdate` with `insertText` requests
- Input: placeholder map + `slides[].replacements`
- Key strip + upper-case → role → `placeholder_map[slide_X][role]` → `objectId`
- Errors: role not found → **13a warning** (non-fatal)

**Recipe 4 — insert-image** (`protocols/recipe-insert-image.md`):
- gws flow: `drive.files.create` upload → `drive.permissions.create` (anyoneWithLink) → obtain `webContentLink` → `slides.presentations.batchUpdate` with `createImage` + `pageElementProperties` (explicit pageObjectId + transform)
- Input: placeholder map + `slides[].images[]`
- Errors: `placeholder_id` not found on current slide → **13b warning** (non-fatal); upload failed → exit 12; local file missing → exit 14

If `slides[]` is empty → run only Step 2 and return the URL directly.

### Step 5 — Emit result

On success, stdout prints a single line of JSON:

```json
{
  "url": "https://docs.google.com/presentation/d/<presentation_id>/edit",
  "presentation_id": "<id>",
  "slides_count": N,
  "warnings": ["13a: slide_2 role=BODY_1 not found in layout"]
}
```

stderr carries human-readable progress + TaskUpdate messages (recipe start / end, 429 retries, warning summaries).

## Error handling (exit-code mapping)

Full table in TECH-SPEC §4.2; common cases for this skill:

| Exit | Meaning | Action |
|---|---|---|
| 10 | Token expired / unauthenticated / scope missing | Return to `google-slides-setup` for re-auth; user runs `gws auth login` |
| 11 | 429 rate limit after 5 retries | Retry later |
| 12 | Google resource not found / `target` unsupported / upload failed | Check `target` field / Drive quota |
| 13a | insert-text placeholder role not found | **Warning**; check whether the layout provides this role |
| 13b | insert-image `placeholder_id` not found | **Warning**; check `placeholder_map[slide_X]` |
| 14 | Local image missing / too large / unsupported format | Check `local_path` |
| 15 | Schema validation failed (including `layout_hint` not in enum) | Fix the slide plan |
| 16 | Issue #119 / invalid_scope | Return to `google-slides-setup`; run `env-guard.sh apply` |
| 18 | Keychain + file backend both fail | Check `KEYRING_BACKEND` |

**Removed in v0.3**:
- ~~13c~~ (`replaceAllShapesWithImage` miss) — no longer used by this skill
- ~~13d~~ (template schema drift) — template workflow removed
- ~~17~~ (SHA-256 mismatch) — bootstrap no longer pins SHA (PRODUCT-SPEC v0.3 §3.2 Non-Goal)

**13a / 13b are warnings**: the pipeline continues to completion, then reports everything in `warnings[]`; no abort.

## Token expiry (smooth re-auth) — v0.5.1

Per TECH-SPEC §6.3: do **not** proactively refresh in the background, but
when Claude detects exit 10, **automatically trigger re-auth** (browser
opens → user clicks Allow → retry the pipeline). The user only needs to
click "Allow" once — no copy-pasting long commands.

### Exit 10 recovery protocol (Claude follows this)

1. **Detect**: pre-flight's `credential-check.sh` returns
   `expires_in_days <= 0`, or the builder's call to `gws-wrap.sh` returns
   exit 10 (`invalid_grant` / `token.*expired`)
2. **Notify the user**: print to stderr:
   > `Your gws refresh token has expired (Google External + Testing mode
   > 7-day lifetime). Launching re-auth now — browser will open, please
   > click "Allow".`
3. **Auto-trigger re-auth**: invoke
   `bash slides-toolkit/scripts/google-slides/refresh-auth.sh`
   - The script sources `env.sh`, exports env vars, and calls
     `gws auth login --scopes=<presentations,drive.file>`
   - Browser opens automatically; user clicks Allow; localhost callback; exit 0
4. **Retry the original operation**: once re-auth succeeds (script exit 0),
   **rerun** the interrupted pipeline step (create-presentation /
   batchUpdate / etc.)
5. **If re-auth fails** (script exit 10; user clicks Cancel, wrong
   scopes, etc.):
   - Do not retry; surface the error to the user
   - Point them at `google-slides-setup` for a full diagnosis

### Alias suggestion (non-Claude context)

For manual runs in a terminal (e.g. proactively refreshing a token you
suspect is about to expire):
```bash
# ~/.zshrc
alias gws-relogin='bash ~/GitHub/monkey-skills/slides-toolkit/scripts/google-slides/refresh-auth.sh'
```

**Because** at a cadence of 3–5 decks per week the user has a rhythm,
but should not be forced to copy-paste long commands. Folding scope
clamping and env-var handling into a helper script is ETC + DRY (multiple
entry points — Claude orchestration, user alias, cron — share the same
re-auth path).

## Output contract

**stdout** (single-line JSON on success):

```json
{
  "url": "https://docs.google.com/presentation/d/<id>/edit",
  "presentation_id": "<id>",
  "slides_count": 12,
  "warnings": []
}
```

**stderr**: human-readable progress + TaskUpdate events (recipe start / end, 429 retries, 13x warning summaries).

**Exit code**: 0 on success; non-zero per the error-handling table above.

## Further reading

- TECH-SPEC §3.4 (module definition), §4.1 (schema v1.2), §4.2 (exit codes), §4.3 (gws recipe mapping), §4.4 (OAuth scopes), §4.6 (E2E data flow v0.3)
- PRODUCT-SPEC §4.2 (three core scenarios), §4.4 Principle 2 (Layout-based), §3.5 (Phase 2+ template-return trigger)
- This skill's bundled files:
  - `checklists/pre-flight.md`
  - `protocols/recipe-create-presentation.md`
  - `protocols/recipe-create-slides.md`
  - `protocols/recipe-insert-text.md`
  - `protocols/recipe-insert-image.md`
  - `references/api-error-codes.md`

---

> 🔄 CHECKPOINT: This artifact is raw output. Pipeline: consult your workflow for the next gate.
