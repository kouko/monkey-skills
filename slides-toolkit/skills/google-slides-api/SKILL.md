---
name: google-slides-api
description: Low-level Google Slides API recipe reference — structured, per-operation recipes for create-presentation / create-slides / insert-text / insert-image via `gws` CLI wrapper. Each recipe documents args, stdin/stdout, placeholder-map flow, error mapping, and dry-run behavior. Use when composing a workflow, debugging a single API op, or learning Slides API semantics. 低層 Slides API 操作食譜・API 單步呼叫參考・debug Slides 錯誤・學 Slides batchUpdate 語法。
---

# google-slides-api

Low-level recipe reference for the Google Slides API via `gws` CLI. Lives in the Google Slides backend layer — higher-level workflow orchestration lives in `google-slides-builder`.

## When to use

- You're composing a Slides workflow and need **a single per-op recipe** (e.g. "how do I createImage with a specific size?")
- Debugging a Slides API error and need the **structured error code mapping**（401/403/429/quotaExceeded → TECH-SPEC exit codes）
- Learning Slides batchUpdate semantics（createSlide vs. insertText vs. replaceAllText）
- Writing a new high-level skill that needs Slides API access without re-deriving the call patterns

## When NOT to use

- Want a turnkey "brief → deck URL" pipeline → **use `google-slides-builder`**（consumes slide-plan.json v1.2, orchestrates all 4 recipes）
- Want narrative structure / chart selection advice → **use `slides-design`**（backend-agnostic）
- First-time setup / auth error → **use `google-slides-setup`**
- Want raw API discovery (list of resources / methods) → run `gws slides --help` or `gws schema slides.<resource>.<method>` (gws CLI built-in)

## Prerequisites

- `google-slides-setup` completed (OAuth + `~/.cache/slides-toolkit/bin/gws` in place)
- `gws auth whoami` returns a Google identity
- Scope includes `presentations`（and `drive.file` for `recipe-insert-image`）

## Recipes（`protocols/`）

Each recipe documents input contract, gws command pattern with `jq` body assembly, exit code, and dry-run behavior. Recipes are designed to compose: chain output of one as input of the next.

| Recipe | Google Slides API op | Wraps via | Typical exit codes |
|---|---|---|---|
| [`recipe-create-presentation.md`](protocols/recipe-create-presentation.md) | `presentations.create` | `gws-wrap.sh slides presentations create` | 0 / 10 / 11 / 12 |
| [`recipe-create-slides.md`](protocols/recipe-create-slides.md) | `presentations.batchUpdate` (CreateSlide with `slideLayoutReference.predefinedLayout`) | `gws-wrap.sh slides presentations batchUpdate` | 0 / 12 / 15 |
| [`recipe-insert-text.md`](protocols/recipe-insert-text.md) | `presentations.batchUpdate` (InsertText into placeholder objectId) | `gws-wrap.sh slides presentations batchUpdate` | 0 / 12 / 13a (non-fatal) |
| [`recipe-insert-image.md`](protocols/recipe-insert-image.md) | `drive.files.create` + `drive.permissions.create` + `presentations.batchUpdate` (CreateImage) | `gws-wrap.sh drive / slides` | 0 / 10 / 12 / 13b (non-fatal) |

Exit code semantics live in [`references/api-error-codes.md`](references/api-error-codes.md).

## Composition pattern — placeholder_map threading

Recipes compose via a lightweight data artifact called **`placeholder_map`** — a mapping from `(slide_index, placeholder_role)` to Slides API `objectId`. It is **produced** by `recipe-create-slides.md` (from `createSlide` response + `presentations.get` follow-up) and **consumed** by `recipe-insert-text.md` and `recipe-insert-image.md` to target shapes without relying on fragile `{{TEXT_ANCHOR}}` placeholders.

Example shape:

```json
{
  "1": {
    "TITLE": "p1_title_obj_id",
    "BODY_1": "p1_body_obj_id"
  },
  "2": {
    "TITLE": "p2_title_obj_id",
    "IMG_MAIN": "p2_img_obj_id"
  }
}
```

## Layer boundary（what this skill does NOT do）

- ❌ Consume `slide-plan.json` v1.2（that's `google-slides-builder`'s job）
- ❌ Run a 4-step workflow end-to-end（same — go to builder）
- ❌ 10-item pre-flight checklist（builder's `checklists/pre-flight.md`）
- ❌ Decide which layout to use for which slide（`slides-design`'s job）
- ❌ Auth / OAuth setup（`google-slides-setup`'s job）
- ❌ HTML / PPTX / Marp recipes（Phase 2+ trigger-gated per PRODUCT-SPEC §3.5）

## Upstream refs

- Google Slides API: https://developers.google.com/slides/api/reference/rest
- `gws` CLI: https://github.com/googleworkspace/cli — executed via `scripts/google-slides/gws-wrap.sh`
- TECH-SPEC §4.3 recipe table + §4.6 end-to-end data flow（cross-skill perspective）

## Security（OWASP ASVS L1 inherited from plugin scope）

- V1 least privilege: scope limited to `presentations` + `drive.file`（no full `drive`）
- V5 output encoding: all user input passes through `jq -R` before assembly into batchUpdate JSON
- V13 secrets: credentials never logged; all errors go to structured stderr JSON
- V16 logging: exit codes are stable; error messages never include credential contents

## Character encoding（徳丸 Ch.6）

UTF-8 only across all recipes. 日本語 / 繁體中文 / 简体中文 / emoji 內容均以 UTF-8 bytes 進入 `jq` → HTTPS POST to Google Slides API（API 本身接受 UTF-8 string）。

## License

MIT（plugin root）— all recipes in this skill are originally authored; no upstream code copied. `gws` CLI（Apache-2.0）called at runtime via subprocess, not bundled in repo.
