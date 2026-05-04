---
name: google-slides-api
description: Low-level Google Slides API recipe reference — structured, per-operation recipes for create-presentation / create-slides / insert-text / insert-image via `gws` CLI wrapper. Each recipe documents args, stdin/stdout, placeholder-map flow, error mapping, and dry-run behavior. Use when composing a workflow, debugging a single API op, or learning Slides API semantics. 低層 Slides API 操作食譜・API 單步呼叫參考・debug Slides 錯誤・學 Slides batchUpdate 語法。
---

# google-slides-api

Low-level recipe reference for the Google Slides API via the `gws` CLI. This skill sits at the Google Slides backend layer; higher-level workflow orchestration lives in `google-slides-builder`.

## When to use

- You are composing a Slides workflow and need **a single per-op recipe** (e.g. "how do I `createImage` with a specific size?")
- You are debugging a Slides API error and need the **structured error-code mapping** (401 / 403 / 429 / `quotaExceeded` → TECH-SPEC exit codes)
- You are learning Slides `batchUpdate` semantics (`createSlide` vs. `insertText` vs. `replaceAllText`)
- You are writing a new high-level skill that needs Slides API access without re-deriving the call patterns

## When NOT to use

- You want a turnkey "brief → deck URL" pipeline → use **`google-slides-builder`** (consumes slide plan v1.2 and orchestrates all four recipes)
- You want narrative structure or chart selection guidance → use **`slides-design`** (backend-agnostic)
- First-time setup or auth error → use **`google-slides-setup`**
- You want raw API discovery (list of resources / methods) → run `gws slides --help` or `gws schema slides.<resource>.<method>` (built into the gws CLI)

## Prerequisites

- `google-slides-setup` has completed (OAuth + `~/.cache/slides-toolkit/bin/gws` installed)
- `gws auth whoami` returns a Google identity
- Granted scopes include `presentations` (plus `drive.file` for `recipe-insert-image`)

## Recipes (`protocols/`)

Each recipe documents the input contract, the `gws` command pattern with `jq` body assembly, exit codes, and dry-run behavior. Recipes are designed to compose: the output of one feeds the next.

| Recipe | Google Slides API op | Wraps via | Typical exit codes |
|---|---|---|---|
| [`recipe-create-presentation.md`](protocols/recipe-create-presentation.md) | `presentations.create` | `gws-wrap.sh slides presentations create` | 0 / 10 / 11 / 12 |
| [`recipe-create-slides.md`](protocols/recipe-create-slides.md) | `presentations.batchUpdate` (`CreateSlide` with `slideLayoutReference.predefinedLayout`) | `gws-wrap.sh slides presentations batchUpdate` | 0 / 12 / 15 |
| [`recipe-insert-text.md`](protocols/recipe-insert-text.md) | `presentations.batchUpdate` (`InsertText` into placeholder `objectId`) | `gws-wrap.sh slides presentations batchUpdate` | 0 / 12 / 13a (non-fatal) |
| [`recipe-insert-image.md`](protocols/recipe-insert-image.md) | `drive.files.create` + `drive.permissions.create` + `presentations.batchUpdate` (`CreateImage`) | `gws-wrap.sh drive / slides` | 0 / 10 / 12 / 13b (non-fatal) |

Exit-code semantics live in [`references/api-error-codes.md`](references/api-error-codes.md).

## Composition pattern — threading the placeholder map

Recipes compose via a small data artifact called the **placeholder map** — a mapping from `(slide_index, placeholder_role)` to a Slides API `objectId`. It is **produced** by `recipe-create-slides.md` (from the `createSlide` reply plus a follow-up `presentations.get`) and **consumed** by `recipe-insert-text.md` and `recipe-insert-image.md` to target shapes directly, without relying on fragile `{{TEXT_ANCHOR}}` substitution.

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

## Layer boundary (what this skill does NOT do)

- Does not consume `slide-plan.json` v1.2 (that is the builder's job)
- Does not run a 4-step workflow end to end (same — use the builder)
- Does not own the 10-item pre-flight checklist (lives in the builder's `checklists/pre-flight.md`)
- Does not choose which layout to use for which slide (that is `slides-design`'s job)
- Does not handle auth or OAuth setup (that is `google-slides-setup`'s job)
- Does not cover HTML / PPTX / Marp recipes (Phase 2+, trigger-gated per PRODUCT-SPEC §3.5)

## Upstream references

- Google Slides API: https://developers.google.com/slides/api/reference/rest
- `gws` CLI: https://github.com/googleworkspace/cli — executed through `scripts/google-slides/gws-wrap.sh`
- TECH-SPEC §4.3 (recipe table) + §4.6 (end-to-end data flow, cross-skill view)

## Security (OWASP ASVS L1 inherited from plugin scope)

- V1 least privilege: scopes limited to `presentations` + `drive.file` (no full `drive`)
- V5 output encoding: all user input passes through `jq -R` before assembly into the `batchUpdate` JSON
- V13 secrets: credentials are never logged; all errors go to structured stderr JSON
- V16 logging: exit codes are stable; error messages never include credential content

## Character encoding (徳丸 Ch.6)

UTF-8 only across all recipes. 日本語 / 繁體中文 / 简体中文 / emoji content all flows as UTF-8 bytes through `jq` and into the HTTPS POST to the Google Slides API (which itself accepts UTF-8 strings).

## License

MIT (plugin root). All recipes in this skill are originally authored; no upstream code is copied. The `gws` CLI (Apache-2.0) is called at runtime via subprocess, not bundled in the repo.
