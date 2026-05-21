# Google Slides API — Error Code Reference

Maps Google Slides / Drive API HTTP error symptoms → `gws-wrap.sh` stderr patterns → TECH-SPEC §4.2 exit codes → recommended recovery path.

Every recipe in `protocols/` references this file for exit-code semantics.

---

## Fatal exit codes (non-zero, abort caller)

### `exit 10` — Authentication failure

**Upstream signals**:
- HTTP 401 Unauthorized
- HTTP 403 Forbidden (when it is a scope mismatch rather than a resource permission)
- OAuth error codes: `invalid_grant` / `invalid_token` / `token_expired`

**Root causes**:
- Refresh token hit the 7-day expiration window (External + Testing mode; Google OAuth policy)
- `gws auth login` was never completed
- Required scope missing (e.g. the call needs `presentations.batchUpdate` but login only granted `drive` / `documents` / `spreadsheets`)
- User revoked OAuth consent via myaccount.google.com

**Recovery** (smooth re-auth since v0.5.1):

**Recommended — use the helper script** (shared entry point for Claude orchestration and the user alias):
```bash
bash ~/GitHub/monkey-skills/slides-toolkit/scripts/gws/refresh-auth.sh
```

The script sources `env.sh` (issue #119 env vars) and calls
`gws auth login --scopes=<presentations,drive,documents,spreadsheets>` with full URLs,
avoiding the `-s` service-filter pitfall — see `docs/gws-cli-quirks.md` §3.

**Manual expansion** (if you prefer not to use the helper):
```bash
source ~/.config/gws/env.sh
export GOOGLE_WORKSPACE_CLI_CLIENT_ID GOOGLE_WORKSPACE_CLI_CLIENT_SECRET
gws auth login \
  --scopes=https://www.googleapis.com/auth/presentations,https://www.googleapis.com/auth/drive,https://www.googleapis.com/auth/documents,https://www.googleapis.com/auth/spreadsheets
```

Browser opens → click "Allow" → exit 0 → rerun the recipe. Token stays
fresh for another ~7 days (Testing mode).

**Claude orchestration pattern**: when exit 10 is detected, **do not**
just tell the user the command; invoke `refresh-auth.sh` directly
(browser opens automatically) → user clicks Allow → retry the original
operation. See `slides-builder/SKILL.md §Token expiry` for the
full recovery protocol.

---

### `exit 11` — Quota exhausted / rate limit persistent

**Upstream signals**:
- HTTP 429 with retry-after > 30 seconds
- Error body contains `quotaExceeded` / `userRateLimitExceeded` persisting across the `gws-wrap.sh` retry loop
- `gws-wrap.sh` exponential backoff (5s → 10s → 20s, 3 attempts) exhausted

**Root causes**:
- Personal GCP project default quota hit (60 write/min/user for Slides API)
- Batch too large (> 1000 requests in a single batchUpdate)

**Recovery**:
- Wait 1 minute and retry
- Split a large batchUpdate into chunks (`recipe-create-slides.md` documents the chunking pattern for > 50 slides)
- Check GCP Console → APIs & Services → Quotas for actual usage

---

### `exit 12` — Generic Google API error

**Upstream signals**:
- HTTP 400 Bad Request (malformed batchUpdate body)
- HTTP 404 Not Found (invalid `presentationId` / `fileId`)
- HTTP 500 / 502 / 503 (transient; but the `gws-wrap.sh` retry loop already ran)
- Error body contains `invalidArgument` / `failedPrecondition`

**Root causes**:
- `jq` produced a syntactically valid but semantically wrong batchUpdate request (e.g. insertText into a non-text shape; createImage with size > 25 megapixels)
- Resource was deleted between API calls (e.g. presentation deleted immediately after `presentations.create`)
- Google-side transient failure not recoverable within the retry window

**Recovery**:
- Read the structured stderr JSON for the specific API error message
- Consult the Slides API error table: https://developers.google.com/slides/api/guides/troubleshoot
- If reproducible: check the recipe's input validation

---

### `exit 15` — Invalid `layout_hint` enum

**Upstream signal** (from the recipe-create-slides pre-check, before the API call):
- Input `layout_hint` is not one of the 7 allowed values

**Allowed values** (Google Slides API `predefinedLayout`):
- `TITLE`
- `TITLE_AND_BODY`
- `TITLE_AND_TWO_COLUMNS`
- `SECTION_HEADER`
- `MAIN_POINT`
- `BIG_NUMBER`
- `BLANK`

**Recovery**:
- Fix the caller's slide plan / arguments to use one of the 7 values
- The pre-flight checklist in `slides-builder` catches this before the recipe runs

---

### `exit 16` — Issue #119 workaround required

**Upstream signal**:
- `env-guard.sh check` returns `workaround_needed: true` + `exit 16`
- OAuth error includes `invalid_scope` / `invalid_client` despite `client_secret.json` being present

**Root cause**:
- The `gws` CLI's hardcoded OAuth client fails on personal `@gmail.com` accounts
- Workaround: export `GOOGLE_WORKSPACE_CLI_CLIENT_ID` / `GOOGLE_WORKSPACE_CLI_CLIENT_SECRET` from the user's own GCP OAuth client

**Recovery**:
- Run `gws-setup` → `protocols/issue-119-workaround.md`
- Or directly: `eval "$(scripts/gws/env-guard.sh apply)"`

---

### `exit 18` — Credential backend unavailable

**Upstream signal**:
- `credential-check.sh` stdout: `{"backend": "none", "token_valid": false, ...}` + `exit 18`
- Neither macOS Keychain (`security find-generic-password -s gws -a $USER`) nor the file backend (`~/.config/gws/keyring-file.json`) is usable

**Root cause**:
- First use — `gws auth login` has never run
- Keychain silently fails in SSH / CI / sandbox contexts
- File backend not enabled via `GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND=file`

**Recovery**:
- Run `gws auth login --scopes=presentations,drive,documents,spreadsheets`
- On a headless host where Keychain fails: `export GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND=file`

---

## Non-fatal warnings (exit 0, but the recipe records a warning)

### `exit 13a` — InsertText: placeholder role not found on the target slide

**Upstream signal**:
- `recipe-insert-text.md` tries to resolve `{{ROLE}}` via `placeholder_map[slide_index][ROLE]` and the map entry is missing
- The API call itself succeeds for the other entries; this one is skipped

**Root cause**:
- The slide plan's `replacements` key references a role that does not exist on the chosen `layout_hint`
  - e.g. `layout_hint: "TITLE"` + `replacements: {"{{BODY_1}}": "..."}` — TITLE layout has no BODY role
- Google Slides layout schema changed upstream (rare)

**Recovery**:
- The caller (builder) collects warnings in the `warnings[]` array and emits them at the end of the pipeline
- Human review: adjust `layout_hint` or remove the unused `replacements` key

### `exit 13b` — InsertImage: placeholder objectId not found

**Upstream signal**:
- `recipe-insert-image.md` tries to resolve `placeholder_id` via `placeholder_map[slide_index][IMG_ROLE]` and the map entry is missing

**Root cause**:
- The image role is absent from the placeholder map (e.g. `IMG_MAIN` was specified, but the layout only has TITLE + BODY, with no image placeholder)
- For custom placements, use `BLANK` layout + explicit `pageElementProperties`

**Recovery**:
- If the intent is "image in a specific layout slot": ensure the layout has an image placeholder
- If the intent is "image anywhere": use `BLANK` layout + explicit `pageElementProperties.{size, transform}`

---

## Quick reference

| exit | Kind | Semantics | Typical fix |
|---|---|---|---|
| 0 | success | API call(s) succeeded; warnings may appear in output | — |
| 10 | fatal | Auth: token expired / scope missing / revoked | `gws auth login -s ...` |
| 11 | fatal | Rate limit: retries exhausted | Wait 1 min; chunk the batchUpdate |
| 12 | fatal | Generic API error (400/404/500 etc.) | Inspect stderr; consult Slides API docs |
| 13a | warning | InsertText: role not in layout | Review `replacements` keys vs `layout_hint` |
| 13b | warning | InsertImage: role not in layout | Use `BLANK` layout or pick a layout with an image slot |
| 15 | fatal | `layout_hint` enum invalid | Fix input to one of the 7 allowed values |
| 16 | fatal | Issue #119 workaround needed | Run the setup skill; export client_id/secret env |
| 18 | fatal | Credential backend unavailable | `gws auth login`; consider `GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND=file` |

---

## References

- Google Slides API troubleshooting: https://developers.google.com/slides/api/guides/troubleshoot
- Google OAuth 2.0 error responses: https://developers.google.com/identity/protocols/oauth2#errors
- Google Cloud quotas: https://console.cloud.google.com/apis/api/slides.googleapis.com/quotas
- TECH-SPEC §4.2 (full exit-code table + `gws-wrap.sh` mapping logic)
- TECH-SPEC §6 (risk-workaround implementations)
