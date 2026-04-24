# Google Slides API — Error Code Reference

Maps Google Slides / Drive API HTTP error symptoms → `gws-wrap.sh` stderr patterns → TECH-SPEC §4.2 exit codes → recommended recovery path.

All recipes in `protocols/` reference this file for exit-code semantics.

---

## Fatal exit codes (non-zero, abort caller)

### `exit 10` — Authentication failure

**Upstream signals**:
- HTTP 401 Unauthorized
- HTTP 403 Forbidden（when scope mismatch rather than resource permission）
- OAuth error codes: `invalid_grant` / `invalid_token` / `token_expired`

**Root causes**:
- Refresh token 7-day expiration（External + Testing mode；Google OAuth policy）
- `gws auth login` never completed
- Required scope missing（e.g. requested `presentations.batchUpdate` but login only granted `drive.file`）
- Revoked OAuth consent（user removed access via myaccount.google.com）

**Recovery**:
```bash
gws auth login -s presentations,drive.file
```

Then rerun the recipe. Token becomes fresh for another 7 days.

---

### `exit 11` — Quota exhausted / rate limit persistent

**Upstream signals**:
- HTTP 429 with retry-after > 30 seconds
- Error body contains `quotaExceeded` / `userRateLimitExceeded` persisting across `gws-wrap.sh` retry loop
- `gws-wrap.sh` exponential backoff（5s → 10s → 20s, 3 attempts）exhausted

**Root causes**:
- Personal GCP project default quota hit（60 write/min/user for Slides API）
- Batch too large（> 1000 requests in single batchUpdate）

**Recovery**:
- Wait 1 minute + retry
- Split large batchUpdate into chunks（recipe-create-slides.md documents chunking pattern for > 50 slides）
- Check GCP Console → APIs & Services → Quotas for actual usage

---

### `exit 12` — Generic Google API error

**Upstream signals**:
- HTTP 400 Bad Request（malformed batchUpdate body）
- HTTP 404 Not Found（presentationId / fileId invalid）
- HTTP 500 / 502 / 503（transient; but gws-wrap.sh retry already ran）
- Error body contains `invalidArgument` / `failedPrecondition`

**Root causes**:
- `jq` assembled batchUpdate body with syntactically valid but semantically wrong request（e.g. insertText into non-text shape; createImage size > 25 megapixels）
- Resource deleted between API calls（e.g. presentation deleted right after `presentations.create`）
- Google-side transient failure not recoverable within retry window

**Recovery**:
- Read stderr JSON for specific API error message
- Consult Slides API error table: https://developers.google.com/slides/api/guides/troubleshoot
- If repeatable: check recipe input validation

---

### `exit 15` — Invalid `layout_hint` enum

**Upstream signal**（from recipe-create-slides.md pre-check, before API call）:
- Input `layout_hint` is not one of the 7 allowed values

**Allowed values**（Google Slides API `predefinedLayout`）:
- `TITLE`
- `TITLE_AND_BODY`
- `TITLE_AND_TWO_COLUMNS`
- `SECTION_HEADER`
- `MAIN_POINT`
- `BIG_NUMBER`
- `BLANK`

**Recovery**:
- Fix caller's `slide-plan.json` / arguments to use one of the 7 values
- Pre-flight checklist in `google-slides-builder` catches this before here

---

### `exit 16` — Issue #119 workaround required

**Upstream signal**:
- `env-guard.sh check` returns `workaround_needed: true` + `exit 16`
- OAuth error includes `invalid_scope` / `invalid_client` despite `client_secret.json` present

**Root cause**:
- `gws` CLI's hardcoded OAuth client fails on personal `@gmail.com` accounts
- Workaround: export `GOOGLE_WORKSPACE_CLI_CLIENT_ID` / `GOOGLE_WORKSPACE_CLI_CLIENT_SECRET` from user's own GCP OAuth client

**Recovery**:
- Run `google-slides-setup` → `protocols/issue-119-workaround.md`
- Or directly: `eval "$(scripts/google-slides/env-guard.sh apply)"`

---

### `exit 18` — Credential backend unavailable

**Upstream signal**:
- `credential-check.sh` stdout: `{"backend": "none", "token_valid": false, ...}` + `exit 18`
- Neither macOS Keychain (`security find-generic-password -s gws -a $USER`) nor file backend (`~/.config/gws/keyring-file.json`) usable

**Root cause**:
- First-time use, `gws auth login` never run
- Keychain silent-fail in SSH / CI / sandbox context
- File backend not enabled via `GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND=file`

**Recovery**:
- Run `gws auth login -s presentations,drive.file`
- If Keychain fails on headless host: `export GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND=file`

---

## Non-fatal warnings（exit 0 but recipe records warning）

### `exit 13a` — InsertText: placeholder role not found in target slide

**Upstream signal**:
- `recipe-insert-text.md` tries to resolve `{{ROLE}}` via `placeholder_map[slide_index][ROLE]` → map entry missing
- API call itself succeeds for other entries; this one skipped

**Root cause**:
- `slide-plan.json` `replacements` key references a role that doesn't exist on the chosen `layout_hint`
  - e.g. `layout_hint: "TITLE"` + `replacements: {"{{BODY_1}}": "..."}` — TITLE layout has no BODY role
- Google Slides layout schema changed upstream（rare）

**Recovery**:
- Caller (builder) collects warnings in `warnings[]` array, emits at end of pipeline
- Human review: adjust `layout_hint` or remove unused `replacements` key

### `exit 13b` — InsertImage: placeholder objectId not found

**Upstream signal**:
- `recipe-insert-image.md` tries to resolve `placeholder_id` via `placeholder_map[slide_index][IMG_ROLE]` → map entry missing

**Root cause**:
- Image role not in `placeholder_map`（e.g. `IMG_MAIN` specified but layout only has TITLE + BODY, no image placeholder）
- Must use `BLANK` layout + manually position images via `pageElementProperties` for custom placements

**Recovery**:
- If intent is "image on a specific layout slot": ensure layout has image placeholder
- If intent is "image anywhere": use `BLANK` layout + explicit `pageElementProperties.{size, transform}`

---

## Quick reference table

| exit | Kind | Semantic | Typical fix |
|---|---|---|---|
| 0 | success | API call(s) succeeded; warnings may exist in output | — |
| 10 | fatal | Auth: token expired / scope missing / revoked | `gws auth login -s ...` |
| 11 | fatal | Rate limit: retry exhausted | Wait 1 min + chunk batchUpdate |
| 12 | fatal | Generic API error (400/404/500 etc.) | Inspect stderr; consult Slides API docs |
| 13a | warning | InsertText: role not in layout | Review `replacements` keys vs `layout_hint` |
| 13b | warning | InsertImage: role not in layout | Use `BLANK` layout or pick layout with image slot |
| 15 | fatal | `layout_hint` enum invalid | Fix input to one of 7 allowed values |
| 16 | fatal | Issue #119 workaround needed | Run setup skill; export client_id/secret env |
| 18 | fatal | Credential backend unavailable | `gws auth login`; consider `KEYRING_BACKEND=file` |

---

## References

- Google Slides API troubleshooting: https://developers.google.com/slides/api/guides/troubleshoot
- Google OAuth 2.0 error responses: https://developers.google.com/identity/protocols/oauth2#errors
- Google Cloud Quotas: https://console.cloud.google.com/apis/api/slides.googleapis.com/quotas
- TECH-SPEC §4.2 (full exit code table + `gws-wrap.sh` mapping logic)
- TECH-SPEC §6 (risk workaround implementations)
