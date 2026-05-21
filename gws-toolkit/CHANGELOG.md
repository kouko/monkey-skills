# Changelog

All notable changes to `gws-toolkit` are documented in this file.
This plugin originated from `slides-toolkit` v0.6.0 via strangler fig
fork (2026-05-04); entries below v0.4.0 describe the upstream
slides-toolkit lineage and remain accurate for that fork point.

本檔案採 [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) 格式，
版本編號遵循 [Semantic Versioning](https://semver.org/lang/zh-TW/)。

## [Unreleased]

### Backlog — test infrastructure (post-Phase-1 milestone)

Today the only automated test is
[`scripts/dev/smoke-test-api-coverage.sh`](scripts/dev/smoke-test-api-coverage.sh)
(integration; hits real Google APIs across 4 services). No unit tests
for individual scripts; no `--dry-run` shape assertions; no CI workflow.
The 2026-05-04 strangler-fig fork moved fast on `auto-setup.sh` (5
revisions) so unit tests would have churned alongside; with Phase 1
closed and surfaces stable, it is now the right time to add them.

Trigger: after slides-toolkit Phase 3 deprecation closes (gws-toolkit
≥ v0.5.0 stable on daily use).

Tooling: [bats-core](https://github.com/bats-core/bats-core) — brew-
installable; mock external commands via PATH-injected stubs (no Google
API calls), so tests can run on CI without OAuth secrets.

Phased ROI:

1. **High ROI (~4-6 h)** — `safe-delete.sh` arg parsing + L1/L2/L3
   tier decision; `gws-wrap.sh` `map_gws_error` exit-code mapping +
   `is_retryable` regex; `credential-check.sh`
   `compute_expires_in_days` arithmetic.
2. **Medium ROI (~4 h)** — `auto-setup.sh` `parse_args` + dry-run
   plan output; `gws-login.sh` / `gws-logout.sh` arg parsing +
   `--switch` / idempotent paths.
3. **Skipped** — `bootstrap.sh` (one-shot binary download; no
   unit-test surface worth the lines).

## [0.7.2] - 2026-05-21

Audit-driven maintenance release. End-to-end cross-check against (a)
upstream `googleworkspace/cli@v0.22.5/705fb0ec` Rust source and (b)
Google's 2026 official OAuth / GCP Console docs surfaced 10 deltas +
6 upstream-side changes since the v0.4.0 strangler-fig rename. v0.7.2
absorbs all P0+P1+P2 fixes in one patch so future v0.8.0 development
starts from accurate ground truth.

### Fixed

- **`KEYRING_BACKEND` → `GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND`** —
  P0. The env-var name in `skills/gws-setup/SKILL.md` (lines 217 +
  227) and `standards/credential-hygiene.md` was missing the
  `GOOGLE_WORKSPACE_CLI_` prefix that upstream requires
  (`credential_store.rs:150,161`). Setting the old name was a silent
  no-op in v0.7.1 and earlier — `gws` ignored it and used its
  default Keychain backend.
- **macOS Keychain v0.22.3+ strict mode** — P1. v0.22.3 removed the
  silent file-backend fallback on macOS / Windows; the SKILL.md and
  credential-hygiene.md narrative still described the (no-longer-
  present) auto-fallback path. Rewritten to: "Keychain is strict;
  explicit `GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND=file` opt-in if you
  need the file backend."
- **`--preset recommended` warning** — P1. gws v0.22.5 has no
  `recommended` preset flag (verified via `auth_commands.rs:362-395`
  flag surface). The warning was stale guidance from an older gws
  version. Replaced with the current 25-scope Testing-mode cap
  caveat (upstream README §Authentication line 438-446).
- **`exit 17 SHA-256 mismatch`** — P1. SHA-256 verification was
  retired in v0.4.0 (PRODUCT-SPEC v0.3 Non-Goal); 3 stale references
  in `SKILL.md:308`, `checklists/setup-state.md:55`,
  `protocols/gcp-console-walkthrough.md:557` removed.
- **`gcloud projects create` 403 PERMISSION_DENIED detection** — P1.
  `auto-setup.sh ensure_project()` previously surfaced any project-
  create failure as generic `exit 12`. Workspace users without
  `roles/resourcemanager.projectCreator` at the org level were the
  silent victim. v0.7.2 captures stderr and surfaces a friendly
  "ask your Workspace admin for projectCreator role OR set
  `GWS_TOOLKIT_PROJECT_ID=<existing>` to point at a project you
  already have access to" message.
- **gws-setup §Quota awareness 403/429 fact** — P1 (carry-over from
  v0.7.1 reviewer 🟡). Old text said "403 / 429 rate-limit errors
  are handled transparently by gws-wrap.sh's exponential backoff",
  but `gws-wrap.sh:187` maps 403 to exit 10 (auth/scope) — only 429
  + 5xx are retried at `:201`. Sentence rewritten to reflect
  actual behaviour.

### Added

- **§OAuth client maintenance** sub-section in
  `skills/gws-setup/SKILL.md` documenting two Google-side behaviours
  introduced in the 2025-06 Cloud Console UI update:
  - Client secret is **shown only once** after creation (Console
    masks it on every subsequent view; if lost, delete + recreate).
  - **6-month inactivity → auto-delete** of OAuth clients, with a
    30-day restore window.

### Changed

- **Reframe `env-guard.sh` from "issue #119 workaround" to
  "BYO OAuth client mechanism"** — P2. Upstream now documents
  `GOOGLE_WORKSPACE_CLI_CLIENT_ID/_SECRET` as the first-class
  External-audience BYO-client mechanism (`README §Authentication`,
  `setup.rs:1457` `manual_oauth_instructions()`). The original issue
  #119's underlying parsing bug was separately fixed by upstream
  PR #177 (merged 2026-03-05; shipped in v0.22.5, which is what we
  pin). The script's behaviour is unchanged; only the narrative
  framing is updated across `env-guard.sh` header, `SKILL.md`
  Workarounds section, `checklists/setup-state.md` check 5,
  `standards/credential-hygiene.md`, `commands/gws-setup.md`. The
  file `protocols/issue-119-workaround.md` keeps its filename as a
  stable cross-link anchor; its content is updated.
- **`refresh-auth.sh` header note** — P2. Clarified that upstream
  `gws` v0.22.5 has no native `gws auth refresh` subcommand
  (`auth_commands.rs:398-429` shows the 5-subcommand surface
  `login | setup | status | export | logout`). Our `refresh-auth.sh`
  re-runs `gws auth login` with the cached 6-scope set when the
  refresh token itself has expired.
- **Legacy `slides-toolkit` → `gws-toolkit` rename (5+ surfaces)** —
  P2. Strangler-fig fork from v0.4.0 left these legacy fragments:
  - Cache path: `~/.cache/slides-toolkit/bin/` → `~/.cache/gws-toolkit/bin/`
    (15 references across `auto-setup.sh`, `bootstrap.sh`,
    `refresh-auth.sh`, `env-guard.sh`, `credential-check.sh`,
    `gws-wrap.sh`, `gws-login.sh`, `gws-logout.sh`,
    `scripts/dev/reset-local.sh`, `scripts/dev/smoke-test-api-coverage.sh`,
    SKILL.md, checklists, credential-hygiene.md).
  - Project ID prefix: `slides-toolkit-<YYMMDD>` → `gws-toolkit-<YYMMDD>`.
  - Env vars: `SLIDES_TOOLKIT_PROJECT_ID` → `GWS_TOOLKIT_PROJECT_ID`,
    `SLIDES_TOOLKIT_BINARY_TTL_DAYS` → `GWS_TOOLKIT_BINARY_TTL_DAYS`.
    Old names retained as **deprecated aliases** with a one-line
    `[auto-setup] note: SLIDES_TOOLKIT_PROJECT_ID is deprecated;
    prefer GWS_TOOLKIT_PROJECT_ID` stderr warning when used.
  - Script header docstrings: `slides-toolkit X` → `gws-toolkit X`
    in `auto-setup.sh`, `bootstrap.sh`, `refresh-auth.sh`.
  - **Migration impact for existing users**: re-running
    `bash gws-toolkit/scripts/gws/bootstrap.sh` re-downloads `gws` +
    `jq` to the new cache path; old `~/.cache/slides-toolkit/bin/`
    can be removed manually if desired. Setup is otherwise
    backward-compatible (deprecated env-var aliases work; no re-auth
    needed).
- **`plugin.json`** — version bumped `0.7.1` → `0.7.2`. Description
  unchanged (no user-facing capability added; this is a maintenance
  release).
- **`marketplace.json`** — gws-toolkit description still matches
  plugin.json byte-identical (no change needed — description is the
  same).

### Notes

- **Upstream pin held** at `v0.22.5 / 705fb0ec` — purely additive
  doc + script-rename cleanups; upstream version bump is a separate
  concern for v0.8.0.
- **No OAuth scope changes** — the 6 scopes from v0.7.0 stay; no
  re-consent needed.
- **Audit sources**: research-agent cross-references against (a)
  upstream `googleworkspace/cli` v0.22.5 / 705fb0ec source files
  (`setup.rs`, `auth_commands.rs`, `auth.rs`, `credential_store.rs`,
  `README.md`), and (b) Google's official OAuth / GCP Console
  documentation as of 2026-05-21 (Google Auth Platform path, OAuth
  consent screen UI, granular OAuth rollout 2026-01-07, Workspace
  app-audience policy, Desktop client OAuth flow, restricted-scope
  classification, 2026-05-01 Gmail/Calendar API quota change).

### Audit findings deferred to v0.8.0 backlog

These v0.8.0-backlog items were carried forward from v0.7.1 already;
v0.7.2 does not address them:

- **DRY across 4 safety wrappers** — extract `scripts/gws/_common.sh`
  for die/usage/preflight (~50 LOC duplicated 4×; Rule of Three).
- **Shared input-sanitization helper** — `_validate.sh` covering
  CRLF email header injection (gmail-confirm-send) + USER_ENTERED
  formula injection (sheets-confirm-write).
- **bats-core test infrastructure** — carried from v0.7.0
  [Unreleased] backlog.
- **Vendor remaining upstream skills** — 6 gmail-* helpers +
  gws-sheets-read + 51 recipe-* + 10 persona-* + gws-tasks +
  gws-meet + gws-people.
- **Upstream pin bump beyond v0.22.5** — independent PR concern.

## [0.7.1] - 2026-05-20

Close the v0.7.0 write asymmetry — vendor 5 new upstream write-side
skills (Gmail send / Calendar insert / Docs write / Sheets append /
Drive upload) and ship 4 new first-party app-layer safety wrappers
modeled on the `safe-delete.sh` (3-tier) + `tag-create.sh` (provenance)
precedent. No OAuth scope changes: full r/w grant from v0.7.0 already
covers every write op v0.7.1 adds; no re-consent needed.

### Added

- **`skills/gws-gmail-send/SKILL.md`** (Part 1 T3) — vendored upstream
  `gws-gmail-send`; covers Gmail send via `gws gmail +send`. Sync
  materialization round.
- **`skills/gws-calendar-insert/SKILL.md`** (Part 1 T3) — vendored
  upstream `gws-calendar-insert`; covers Calendar event create via
  `gws calendar +insert`.
- **`skills/gws-docs-write/SKILL.md`** (Part 1 T3) — vendored upstream
  `gws-docs-write`; covers Docs body / `replaceAllText` write surface.
- **`skills/gws-sheets-append/SKILL.md`** (Part 1 T3) — vendored
  upstream `gws-sheets-append`; covers Sheets row append +
  range update / clear write surface.
- **`skills/gws-drive-upload/SKILL.md`** (Part 1 T3) — vendored
  upstream `gws-drive-upload`; covers Drive file upload write surface.
  Composes with toolkit's `tag-create.sh` provenance wrapper.
- **`scripts/gws/gmail-confirm-send.sh`** (Part 2 T1) — first-party L3
  typed-name safety wrapper for Gmail send. Default mode is dry-run
  (renders the message envelope without calling the destructive API);
  execute requires `--i-confirm-recipients` + `--i-confirm-subject`
  typed-name gates. Modeled on `safe-delete.sh` L3.
- **`scripts/gws/calendar-confirm-insert.sh`** (Part 2 T2) — first-party
  auto-tier safety wrapper for Calendar event insert. Attendees > 0 →
  L2 + `visibility_warning` (invite emails fire on insert); attendees
  == 0 → L1 (solo event, no broadcast).
- **`scripts/gws/sheets-confirm-write.sh`** (Part 2 T3) — first-party
  op-aware safety wrapper for Sheets append / clear / update. `append`
  → L1 (additive); `clear` / `update` → L2 with dual-gate
  `--confirm-recovery="version_history_only"` (30-day version-history
  recovery, no immediate undo).
- **`scripts/gws/docs-confirm-append.sh`** (Part 2 T4) — first-party L1
  safety wrapper for Docs append / replace. `replaceAllText` with
  match-count > 5 surfaces a broad-stroke warning before execution.
- **`skills/gws-setup/SKILL.md` §Quota awareness** (Part 3 T3) — new
  sub-section under §Prerequisites documenting the 2026-05-01
  Gmail / Calendar API quota change. Pre-2026-05-01 projects are
  grandfathered on the prior quota; projects created on/after
  2026-05-01 follow the new quota schedule and may incur billing
  later in 2026.

### Changed

- **`UPSTREAM_GWS_VERSION` `synced_skills:` list** (Part 1 T1) — 9 → 14
  entries; added the 5 new vendored skill names alongside the existing
  9 (alphabetical / grouped-by-domain per v0.7.0 convention).
- **`scripts/sync-upstream-skills.sh` `VENDORED_SKILLS=(…)` array**
  (Part 1 T2) — mirrored to 14 entries so future upstream syncs pull
  all 14 vendored skills.
- **`gws-toolkit/README.md`** (Part 3 T1) — Status table Release column
  bumped 0.7.0 → 0.7.1; vendored-skill table extended 9 → 14 rows; the
  ASCII Architecture diagram annotates the 4 new safety wrappers with
  their tier labels (L1 / L2 / L3 typed-name).
- **`gws-toolkit/TECH-SPEC.md`** (Part 3 T2) — Revision History row
  added for v0.7.1; §2.1 plugin-layout tree extended with the 5 new
  vendored-skill entries + 4 new safety-wrapper script entries under
  `scripts/gws/`.
- **`skills/using-gws-toolkit/SKILL.md`** (Part 3 T4) — routing table
  extended with 5 vendored write-skill rows (gws-gmail-send /
  gws-calendar-insert / gws-docs-write / gws-sheets-append /
  gws-drive-upload) and a unified safety-wrappers row covering the
  4 new `confirm-*.sh` scripts plus a cross-reference to the existing
  `tag-create.sh`.
- **`plugin.json`** (Part 4 T1) — `version` bumped 0.7.0 → 0.7.1;
  `description` field extended to surface the write-safety wrapper
  capability.
- **`marketplace.json`** (Part 4 T1) — `gws-toolkit` plugin
  `description` mirrored byte-identical to `plugin.json` per
  `MEMORY.md feedback_plugin_marketplace_sync` (Required CI check).

### Notes

- **Purpose** — close the v0.7.0 write asymmetry. The OAuth grant from
  v0.7.0 was full read-write, but first-party code paths only existed
  for Slides + Drive. v0.7.1 ships first-party safety wrappers + the
  vendored upstream write helpers for Gmail / Calendar / Docs / Sheets
  / Drive, modeled on the `safe-delete.sh` (3-tier) +
  `tag-create.sh` (provenance) precedent from v0.4.0.
- **No OAuth scope changes** — full r/w grant from v0.7.0 already
  covers every write op v0.7.1 adds; no re-consent needed.
- **Upstream pin held** at `v0.22.5 / 705fb0ecac6f4249679958f6325b809b63fdde17`
  — purely additive vendoring; upstream version bump deferred to an
  independent PR.
- **2026-05-01 API quota change context** — Gmail + Calendar API
  quotas were updated 2026-05-01, active when v0.7.1 ships.
  Grandfathering is documented in §Quota awareness for users with
  pre-2026-05-01 projects.
- **Safety tier mapping** (per brief §Q3): gmail-send → L3 typed-name
  (irreversible after ~30s undo); calendar-insert → L2 (sends invite
  emails when attendees > 0) / L1 (solo); sheets-append → L1 /
  sheets-clear-or-update → L2 (recoverable via version history,
  30-day); docs → L1 (Drive version history); drive-upload covered
  by existing `tag-create.sh` L1.

### Discharged from v0.7.0 backlog

- **Write-side vendored skills + app-layer safety wrappers** — v0.7.0
  §Open follow-ups noted: "ship when first write JTBD lands; gate on
  user-confirmable dry-run shape before live send/insert." v0.7.1
  discharges this for 5 of 11 upstream write helpers (`gws-gmail-send`,
  `gws-calendar-insert`, `gws-docs-write`, `gws-sheets-append`,
  `gws-drive-upload`) + 4 new app-layer safety wrappers
  (`gmail-confirm-send.sh`, `calendar-confirm-insert.sh`,
  `sheets-confirm-write.sh`, `docs-confirm-append.sh`). Drive write
  was already covered by `tag-create.sh` (v0.4.0+).
- **Brief Axis 5 correction to v0.7.0 finding** — `find-free-slots`
  does have a native upstream equivalent: `recipe-find-free-time`
  (51 recipes web-fetched 2026-05-20). The v0.7.0 CHANGELOG said
  "no native upstream equivalent" — this was an incomplete WebFetch
  scope at v0.7.0 brief time (inspected only top-level `skills/gws-*`
  not `skills/recipe-*`). v0.8.0 will correct this by vendoring the
  `recipe-*` tree.

### Open follow-ups (v0.8.0 backlog)

- **Remaining 6 upstream `gmail-*` helpers** — `gmail-reply`,
  `gmail-reply-all`, `gmail-forward`, `gmail-triage`, `gmail-watch`,
  plus a `gmail-confirm-reply.sh` wrapper that composes
  `gmail-confirm-send.sh`.
- **`gws-sheets-read` vendored skill** — additive read-only completion
  of the Sheets surface.
- **51 upstream `recipe-*` skills** — composition layer
  (`recipe-find-free-time`, `recipe-label-and-archive-emails`,
  `recipe-create-events-from-sheet`, `recipe-draft-email-from-doc`,
  `recipe-batch-invite-to-event`, etc.).
- **10 upstream `persona-*` skills** — `persona-exec-assistant`,
  `persona-project-manager`, `persona-researcher`, etc.
- **3 new non-write services** — `gws-tasks` (todo from email /
  calendar), `gws-meet` (calendar Meet link pairing), `gws-people`
  (recipient resolution for mail-send).
- **bats-core test infrastructure** — `[Unreleased]` backlog carried
  forward from v0.7.0; runs in a separate PR.
- **Code-quality reviewer 🟡 debt from v0.7.1**:
  - Part 2 T1 — CRLF header-injection defense-in-depth on
    `gmail-confirm-send.sh` (OWASP ASVS V5.2.6); ~10 LOC pre-flight
    check.
  - Part 2 T2 — `calendar-confirm-insert.sh` `visibility_warning` may
    be aspirational; verify upstream `gws calendar +insert` default
    for `sendUpdates` or explicitly set `sendUpdates=all` in params.
  - Part 2 T3 — `sheets-confirm-write.sh` hard-coded
    `valueInputOption=USER_ENTERED` allows formula injection; consider
    exposing `--value-input-option=USER_ENTERED|RAW` as a flag.
  - Part 2 T4 — `docs-confirm-append.sh` `--help` `sed` range
    overshoots by 5 lines (leaks code into help output); 1-line fix
    (range `5,68` → `5,62`).
  - Part 1 T2 — plan-document regex `grep -c '"gws-'` is technically
    malformed against bash array entries (entries are unquoted);
    should be `grep -c '^  gws-'` in future plans.

## [0.7.0] - 2026-05-19

Gmail + Calendar absorption — vendor 4 new upstream skills, add 2
restricted-tier OAuth scopes (gmail + calendar), and enable 2 Workspace
APIs. No write-side user-facing paths ship in this release; OAuth grant
is full read-write (mirroring the v0.4.0 Drive precedent) while code
paths stay read-only until write JTBDs land in v0.7.x.

### Added

- **`skills/gws-gmail/SKILL.md`** (Part 1 T5 / commit `5031eb4`) —
  vendored upstream `gws-gmail` skill; covers compose / reply / forward
  / move / delete / label operations. Vendored via `sync-upstream-skills.sh`;
  Apache-2.0 upstream.
- **`skills/gws-gmail-read/SKILL.md`** (Part 1 T5 / `5031eb4`) —
  vendored upstream `gws-gmail-read` skill; covers list / read / search /
  thread / attachment operations. Read-path counterpart to `gws-gmail`.
- **`skills/gws-calendar/SKILL.md`** (Part 1 T5 / `5031eb4`) —
  vendored upstream `gws-calendar` skill; covers event create / update /
  delete / share operations.
- **`skills/gws-calendar-agenda/SKILL.md`** (Part 1 T5 / `5031eb4`) —
  vendored upstream `gws-calendar-agenda` skill; covers event list /
  search / free-busy / agenda-view operations. Read-path counterpart to
  `gws-calendar`.
- **Gmail OAuth scope** (`https://www.googleapis.com/auth/gmail` — full
  read-write, restricted tier) added to `scripts/gws/auto-setup.sh`
  (Part 1 T1 / `1d4b950`). The org-policy probe at
  `myaccount.google.com/permissions` showed macOS Mail already holds
  the broader `https://mail.google.com/` scope at the iChef org level;
  the narrower API scope we request is therefore allowed.
- **Calendar OAuth scope** (`https://www.googleapis.com/auth/calendar` —
  full read-write, restricted tier) added to `scripts/gws/auto-setup.sh`
  (Part 1 T1 / `1d4b950`).
- **`gmail.googleapis.com`** enabled in `scripts/gws/auto-setup.sh`
  Workspace API enable step (Part 1 T1 / `1d4b950`).
- **`calendar.googleapis.com`** enabled in `scripts/gws/auto-setup.sh`
  Workspace API enable step (Part 1 T1 / `1d4b950`).

### Changed

- **`scripts/gws/auto-setup.sh`** (Part 1 T1 / `1d4b950`) — added
  Gmail + Calendar OAuth scopes to `OAUTH_SCOPES` array; added
  `gmail.googleapis.com` + `calendar.googleapis.com` to the API enable
  step; refreshed Phase 1 banner to list 6 APIs.
- **`scripts/gws/refresh-auth.sh`** (Part 1 T2 / `8e5260d`) — updated
  scope list to include gmail + calendar scopes so re-auth flows grant
  all 6 scopes (not just the original 4).
- **`scripts/gws/gws-login.sh`** (Part 1 T3 / `b94dc6b` + round-2 fix
  `5169c0b`) — updated scope enumeration in login flow; round-2 fix
  corrected a missed reference in the scope-list construction.
- **`UPSTREAM_GWS_VERSION` + `sync-upstream-skills.sh`** (Part 1 T4 /
  `756caf4`) — updated upstream pin comment to document the 4 newly
  vendored skills; `sync-upstream-skills.sh` updated with the new skill
  names so future upstream syncs pull all 9 vendored skills.
- **Vendored SKILL.md files × 9** (Part 1 T5 / `5031eb4`) — 4 new
  (`gws-gmail`, `gws-gmail-read`, `gws-calendar`, `gws-calendar-agenda`)
  + 5 metadata-refreshed (`gws-shared`, `gws-drive`, `gws-docs`,
  `gws-slides`, `gws-sheets`) via sync script run against
  `v0.22.5 / 705fb0ec`.
- **`commands/gws-setup.md`** (Part 2 T1 / `3af41c2`) — updated
  prerequisite list and confirmation checklist to surface Gmail +
  Calendar as newly covered services.
- **`skills/gws-setup/SKILL.md`** (Part 2 T2 / `2d249d9`) — updated
  capabilities narrative and service enumeration; setup walkthrough now
  references 6 enabled APIs.
- **`skills/using-gws-toolkit/SKILL.md` routing table** (Part 2 T3 /
  `be8ebe6`) — Gmail + Calendar skills added to the skill-dispatch
  table; routing description updated to surface gws-gmail-read and
  gws-calendar-agenda as the read-path entry points.
- **`README.md` + `TECH-SPEC.md` + `UPSTREAM_GWS_VERSION` header**
  (Part 2 T4 / `9b0e9bf`) — README banner + service enumeration +
  ASCII architecture diagram updated to include Gmail + Calendar;
  TECH-SPEC.md vendored-skills table updated (4 new rows); upstream
  pin header comment refreshed.
- **`plugin.json`** (this commit) — `version` bumped `0.6.0` → `0.7.0`;
  `description` field extended with `/ gmail / calendar`; `keywords`
  array appended with `"gmail"` and `"google-calendar"`.
- **`README.md` Status table Release column** (this commit) — bumped
  from `0.5.0` (stale) to `0.7.0` to match `plugin.json`.
- **`README.md` Architecture ASCII diagram** (this commit) — Workspace
  APIs node parenthetical extended from
  `(Slides v1 / Drive v3 / Docs v1 / Sheets v4)` to
  `(Slides v1 / Drive v3 / Docs v1 / Sheets v4 / Gmail v1 / Calendar v3)`.

### Notes

- **Full r/w scope rationale** — App-layer least-privilege via
  `safe-delete.sh` replaces scope-boundary enforcement (same pattern
  as the v0.4.0 Drive decision). OAuth grant is full read-write;
  code paths stay read-only this release; write-side wrappers ship in
  v0.7.x when first write JTBD lands. Gmail/Calendar extend the same
  contract: OAuth grant is full (`https://www.googleapis.com/auth/gmail`
  + `https://www.googleapis.com/auth/calendar`), but no compose / insert
  user-facing path ships until a confirmed write JTBD is scoped.
- **iChef Workspace admin-policy probe** — macOS Mail already holds
  `https://mail.google.com/` scope per `myaccount.google.com/permissions`
  (confirmed full Gmail grant unblocked for iChef org). Calendar scope
  follows the same org policy; no admin unblock required.
- **Upstream pin held at `v0.22.5 / 705fb0ec`** — additive vendoring
  only; no upstream version bump in this PR per brief §Out of Scope.
  5 previously vendored skills were metadata-refreshed from the same
  pin; no behavior changes expected.

### Open follow-ups (v0.7.x backlog)

- **`find-free-slots`** + **`shared-calendar-read`** — no native
  upstream equivalent in `v0.22.5`; would require toolkit-original
  wrapper skills when the JTBD is confirmed.
- **Write-side vendored skills** (`gws-gmail-send` / `gws-calendar-insert`)
  + **app-layer safety wrappers** (`gmail-confirm-send.sh` /
  `calendar-confirm-insert.sh`, analogous to `safe-delete.sh`) — ship
  when first write JTBD lands (compose email / insert event); gate on
  user-confirmable dry-run shape before live send/insert.
- **bats-core test infrastructure** — carried from `[Unreleased]`
  backlog; highest ROI on `safe-delete.sh` arg parsing + `gws-wrap.sh`
  error-code mapping. Unblocked now that Phase 1 + Phase 2 surfaces are
  stable.

## [0.6.0] - 2026-05-19

Google Workspace account support — auto-detect by gcloud account email
domain. Prior releases assumed personal `@gmail.com` accounts only;
Workspace users (`@company.com`) hit the External + Testing's 7-day
refresh-token expiry every week despite their Internal-app eligibility,
and got walked through the Test User step that Internal apps don't
require. v0.6.0 detects account type from the active gcloud account's
email domain and dual-paths the OAuth consent walkthrough accordingly.

### Added

- **`detect_account_type()` in `scripts/gws/auto-setup.sh`** (Part 1
  T1) — domain-based detection from `gcloud auth list --filter=status:ACTIVE`
  email. `@gmail.com` / `@googlemail.com` → `personal`; all other
  domains → `workspace`. `--audience=internal|external` flag override
  available for edge cases (BYO-Workspace-as-personal, personal-as-
  Workspace test fixtures).
- **`account_type` field in `scripts/gws/credential-check.sh` JSON
  output** (Part 1 T4) — `"personal" | "workspace" | "unknown"`.
  Downstream consumers (skill body, future cron) can branch on token-
  expiry handling without re-detecting.

### Changed

- **Dual-path `step_5a_branding` in `scripts/gws/auto-setup.sh`**
  (Part 1 T2) — Internal Audience walkthrough for Workspace accounts
  (no Test User section, no 7-day refresh policy); External Audience
  walkthrough preserved verbatim for personal accounts.
- **Conditional `step_5b_test_user` in `scripts/gws/auto-setup.sh`**
  (Part 1 T3) — skipped entirely for Workspace (Internal apps don't
  need Test Users); preserved for personal accounts.
- **`skills/gws-setup/SKILL.md` narrative dual-pathed** (Part 2 T1) —
  Prerequisites, Setup flow, and "Every 7 days maintenance" sections
  now branch on detected account type. Workspace branch omits the
  weekly refresh ritual.
- **`TECH-SPEC.md`** (Part 2 T2) — **no changes**. Plan stage expected
  to find "Workspace accounts are Phase 2+" caveats and remove them, but
  a grep against the current TECH-SPEC.md found 0 matches. The
  account-type / personal-vs-Workspace distinction was only documented
  in SKILL.md (now updated in Part 2 T1). Brief §line 140 had pre-flagged
  this with "locations TBD during plan stage grep" — confirmed empty.
  Linux / CI / WSL "Phase 2+" caveats untouched (still out of scope).
  Follow-up: TECH-SPEC.md §6.3 currently states the 7-day token policy
  universally; a future patch could add an account-type qualifier
  ("personal-account only") for factual precision, but the user-facing
  setup flow (in SKILL.md + auto-setup.sh) already routes Workspace
  users past it.

### Notes

- Workspace accounts are no longer subject to External + Testing's
  7-day refresh-token policy (Internal-app exemption per Google
  OAuth 2.0 docs).
- Workspace user OAuth flow skips the Test User step entirely
  (Internal apps don't require Test Users).
- User account-type is detected from `gcloud auth list --filter=status:ACTIVE`
  email domain: `@gmail.com` / `@googlemail.com` → `personal`; else →
  `workspace`.
- `--audience=internal|external` override available for edge cases
  where domain-based detection produces the wrong default.

### Open follow-ups

- Real-machine dogfood pending against an actual Workspace account
  (`kouko@ichef.com.tw`); first-use validation will close brief Open Q1.
- Issue #119 workaround applicability under Workspace OAuth client —
  verify in first-use (brief Open Q2); env-guard wiring may need
  Workspace-specific adjustment.
- GCP project creation under iChef org policy — verify in first-use
  that `gcloud projects create` is permitted; if blocked, document
  the BYO-project fallback in the next patch.

## [0.5.2] - 2026-05-19

Skill-UX fix: when `gws-setup` skill routes to the re-auth-only branch
(token expired but full setup unnecessary), Claude was deferring to the
user with a paste-it `!` `gws auth login` command instead of invoking
directly. Root cause: SKILL.md "Every 7 days maintenance" section
showed the command as a bare bash snippet without an agent directive,
so Claude played it safe. Fix: explicit `**Agent directive**: invoke
directly via the Bash tool. Do NOT print the command as a paste-it...`
+ point at `scripts/gws/refresh-auth.sh` (the existing wrapper that
sources `env.sh` + handles the 7-day refresh case specifically).

### Fixed

- **`skills/gws-setup/SKILL.md` "Every 7 days maintenance"** —
  explicit agent directive instructing Claude to invoke
  `bash scripts/gws/refresh-auth.sh` via Bash tool, not as
  paste-it `!` command. Browser-OAuth fires on the user's behalf;
  the blocking Bash call is the expected UX.
- Reference `refresh-auth.sh` (the right wrapper for 7-day refresh,
  same account) instead of bare `gws auth login` invocation.
  Distinguishes from `gws-login.sh --switch` (account-swap intent).

### Underlying scripts unchanged

- `scripts/gws/refresh-auth.sh` already existed and already
  worked correctly; this release only updates the skill body so
  Claude invokes it instead of asking the user to paste a command.

## [0.5.1] - 2026-05-19

Fix-only release: expose existing `auto-setup.sh` automation that was
previously dead code (no user-facing entry point). The 742-line
end-to-end onboarding script has been in the repo since v0.5.0 but
`gws-toolkit/commands/` was empty and `skills/gws-setup/SKILL.md`
walkthrough only documented the 10-step manual flow, so users
following the documented setup re-did manually what the script could
automate.

### Added

- **`commands/gws-setup.md`** — new slash command body. Invokes
  `bash ${CLAUDE_PLUGIN_ROOT}/scripts/gws/auto-setup.sh $ARGUMENTS`.
  Documents the 8 codified steps, supported args
  (`--dry-run` / `--force-reinstall`), prerequisites (macOS / TTY /
  personal Gmail), idempotence semantics, troubleshooting, and when
  to use the manual fallback (Path B).

### Changed

- **`skills/gws-setup/SKILL.md` "Setup flow" section** — restructured
  as Path A vs Path B chooser:
  - **Path A**: `/gws-setup` slash command (recommended; ~6-8 min
    first run, ~30 sec on re-run when already set up)
  - **Path B**: the existing 10-step manual walkthrough (kept
    verbatim as fallback for debugging / constrained environments /
    no-TTY contexts)

### Notes

- The underlying `scripts/gws/auto-setup.sh` is unchanged — this
  release only adds entry points + documentation. Anyone who was
  already invoking the script directly (`bash scripts/gws/auto-setup.sh`)
  sees no functional difference.
- Follow-up planned (separate release): refactor script placement
  (relocate plugin-level `scripts/gws/` into per-skill `scripts/`
  folders per Anthropic skill self-containment, using `code-toolkit`'s
  canonical + distribute + verify-drift pattern as precedent).
  Tracking PR: TBD.

## [0.5.0] - 2026-05-06

**Phase 1 validation closed; slides-toolkit enters Phase 3 deprecation.**

### Validation results (2026-05-05)

All 4 acceptance criteria from the prior `[Unreleased]` validation
period satisfied in a single live-test session:

1. ✅ ≥ 1 deck via `slides-builder` — 4-page deck with text + image
   (https://docs.google.com/presentation/d/1wxIRPN0WDVzCq9WvVum2Plug-swKqWD__5xTb2Gie9E)
2. ✅ ≥ 1 ad-hoc Drive op via `gws-drive` — `files.create` upload +
   `permissions.create` (anyoneWithLink reader)
3. ✅ ≥ 1 destructive op via `safe-delete.sh` — L1 trash executed
   (verified `trashed=true`); L2 → L3 typed-name escalation gate
   verified via dry-run
4. ✅ KR1 ≤ 3 min — 108 sec end-to-end across 4 API calls (text-only
   3-page path)

### Changed

- **`slides-toolkit` plugin enters Phase 3 deprecation.** Per its
  README banner the plugin is now deprecated; new users should install
  `gws-toolkit` instead. Existing installations continue to work; the
  `slides-toolkit/` directory remains in the repo for at least one more
  release before any consideration of hard deletion.
- **`.claude-plugin/marketplace.json` — `slides-toolkit` entry
  removed.** New marketplace discovery now points users at
  `gws-toolkit` only. Already-enabled installations are unaffected
  (Claude Code does not auto-uninstall on registry removal).
- **README banner — `gws-toolkit` graduates from 🚧 validation to
  ✅ stable.** Status row Release column bumped `0.1.0-mvp` → `0.5.0`
  (drift fix: `plugin.json` had stayed at `0.0.1-seed` since the
  strangler-fig seed; both are now aligned at `0.5.0`).

### Fixed

- **All 8 builder recipes** (`gws-toolkit/skills/slides-builder/protocols/`
  × 4 + `slides-toolkit/skills/google-slides-api/protocols/` × 4 fallback)
  rewritten from `echo "$body" | gws ... --json-stdin` to
  `gws ... --json "$body"`. `gws v0.22.5` does not support
  `--json-stdin`; only `--json '<JSON>'` as a flag value is accepted.
  Discovered during validation when the very first recipe step exited 12
  with `error[validation]: unexpected argument '--json-stdin'`. (PR #256,
  commit `f56b7bc`)

## [0.4.0-strangler-fig-seed] - 2026-05-04

**Strangler fig fork from slides-toolkit v0.6.0.** Generic Google
Workspace direction: 4 vendored upstream gws-* skills (gws-shared /
gws-drive / gws-docs / gws-slides / gws-sheets) layered with
toolkit-original setup automation, three-tier Drive delete safety,
Slides design knowledge, and slide-plan.json v1.2 builder. Plugin
renamed from slides-toolkit; old plugin frozen for ≥ 2-week
validation period before deprecation.

### Added

- **Vendored upstream skills** (Apache-2.0, attributed in
  frontmatter `metadata.vendored_from`): `skills/gws-shared/`,
  `skills/gws-drive/`, `skills/gws-docs/`, `skills/gws-slides/`,
  `skills/gws-sheets/` — all auto-generated from Google API Discovery
  documents; pinned to `googleworkspace/cli@v0.22.5`
  (`705fb0ecac6f4249679958f6325b809b63fdde17`)
- `LICENSE-APACHE-2.0.txt` at toolkit root (Apache-2.0 §4(a)
  compliance)
- `UPSTREAM_GWS_VERSION` — single source of truth for the upstream
  pin; both `bootstrap.sh` (binary) and `sync-upstream-skills.sh`
  (skills) reference this file
- `scripts/sync-upstream-skills.sh` — re-runnable sync script that
  fetches upstream SKILL.md files via `gh api` and injects
  provenance metadata (`vendored_from / vendored_release /
  vendored_at / upstream_license`) into the frontmatter
- `scripts/gws/safe-delete.sh` — three-tier Drive delete safety
  wrapper (L1 trash-default / L2 --permanent + --confirm / L3
  --permanent + non-provenance + --i-confirm-name=<exact-name>);
  default mode is dry-run (returns JSON preview without calling
  destructive API)
- `scripts/gws/tag-create.sh` — `files.create` wrapper that injects
  `appProperties.created_by = "gws-toolkit"`,
  `appProperties.created_by_version = <plugin.json version>`,
  `appProperties.created_at = <UTC ISO 8601>` into every file the
  toolkit creates; provenance tag drives safe-delete tier decision

### Changed

- **Plugin renamed** from `slides-toolkit` to `gws-toolkit`. Reflects
  the post-vendor scope — only `slides-design` and `slides-builder`
  remain Slides-specific; the rest covers generic Google Workspace
  through vendored skills + setup + safety wrappers
- **Skills renamed**: `google-slides-setup` → `gws-setup`;
  `google-slides-builder` → `slides-builder`; `using-slides-toolkit`
  → `using-gws-toolkit` (`slides-design` unchanged — content is
  genuinely Slides-specific)
- **Scripts directory renamed**: `scripts/google-slides/` →
  `scripts/gws/`
- **OAuth scope upgraded** from `presentations + drive.file` (2 scopes)
  to `presentations + drive + documents + spreadsheets` (4 scopes).
  Application-layer safety (safe-delete.sh) replaces the implicit
  guarantee that `drive.file` provided. ASVS V1 least-privilege now
  enforced at app layer, not scope boundary
- **`scripts/gws/refresh-auth.sh`** — `GWS_TOOLKIT_SCOPES` env var as
  primary override; `SLIDES_TOOLKIT_SCOPES` kept as deprecated alias
- **`scripts/gws/auto-setup.sh`** — `DRIVE_SCOPE` flipped to full
  `drive`; new `DOCS_SCOPE` / `SHEETS_SCOPE` constants

### Removed

- **`google-slides-api` skill (α-trim)** — its 4 per-op recipes
  + `api-error-codes.md` reference moved to
  `slides-builder/protocols/` and `slides-builder/references/`. The
  skill's primary value (per-op API method discovery) is now covered
  by upstream `gws-slides` + `gws schema slides.<r>.<m>`
  introspection. Toolkit-specific composition pattern
  (placeholder-map threading + 13a/13b non-fatal warnings) lives
  inline in slides-builder

### Architecture (post-strangler-fig snapshot)

```
gws-toolkit/
├── .claude-plugin/plugin.json     # name = gws-toolkit, version 0.4.0
├── PRODUCT-SPEC.md / TECH-SPEC.md  # v1.0 holistic rewrite
├── UPSTREAM_GWS_VERSION            # upstream pin (v0.22.5 / 705fb0ec)
├── LICENSE-APACHE-2.0.txt          # for vendored skills
├── skills/
│   ├── using-gws-toolkit/          # router (toolkit-original)
│   ├── gws-setup/                  # OAuth+bootstrap+state (toolkit-original)
│   ├── slides-design/              # Minto/SCQA/chart (toolkit-original)
│   ├── slides-builder/             # slide-plan v1.2 → deck (toolkit-original)
│   ├── gws-shared/                 # auth + global flags (vendored)
│   ├── gws-drive/                  # Drive API v3 (vendored)
│   ├── gws-docs/                   # Docs API v1 (vendored)
│   ├── gws-slides/                 # Slides API v1 (vendored)
│   └── gws-sheets/                 # Sheets API v4 (vendored)
└── scripts/
    ├── gws/
    │   ├── bootstrap.sh            # gws + jq binary fetch
    │   ├── credential-check.sh     # token state probe
    │   ├── env-guard.sh            # issue #119 workaround
    │   ├── gws-wrap.sh             # 429 retry + exit-code map
    │   ├── auto-setup.sh           # first-time setup flow
    │   ├── refresh-auth.sh         # 7-day re-auth helper
    │   ├── safe-delete.sh          # 3-tier Drive delete
    │   └── tag-create.sh           # appProperties provenance
    └── sync-upstream-skills.sh     # vendored-skill sync
```

### Validation gate (before next release)

- ≥ 2 weeks of validated daily use; if validation passes, slides-toolkit
  enters Phase 3 sunset (banner upgrade + marketplace archive flag).
  If validation fails, gws-toolkit may be reverted by removing
  `gws-toolkit/` and `marketplace.json` entry without affecting
  slides-toolkit (still at v0.6.0)

## [0.6.0-i18n] - 2026-04-24

**Language strategy formalisation** — technical layers rewritten in
native English; design / content layer gains trilingual (EN / JP / ZH)
anchors at key terminology points. No functional change; entirely a
documentation-voice refactor. `docs/*` keeps its Chinese-primary
narrative per user directive (internal maintenance notes).

### Changed

- **Technical skills — English-native rewrite** (not translation):
  - `skills/google-slides-api/SKILL.md` + all 4 recipe protocols
    (`recipe-create-presentation.md`, `recipe-create-slides.md`,
    `recipe-insert-text.md`, `recipe-insert-image.md`) +
    `references/api-error-codes.md`
  - `skills/slides-builder/SKILL.md` +
    `checklists/pre-flight.md`
  - `skills/gws-setup/SKILL.md` +
    `protocols/gcp-console-walkthrough.md` +
    `protocols/issue-119-workaround.md` +
    `standards/credential-hygiene.md` +
    `checklists/setup-state.md`
- **Shell script header docstrings — English rewrite**:
  - `scripts/gws/bootstrap.sh`, `gws-wrap.sh`, `env-guard.sh`,
    `credential-check.sh`, `auto-setup.sh`, `refresh-auth.sh`
  - Script body code, function-level comments, variable / function
    names unchanged
- **Design / content layer — trilingual anchors added**:
  - `skills/slides-design/SKILL.md` + `references/minto-scqa.md` +
    `references/chart-selection.md` +
    `rubrics/slide-plan-self-check.md`
  - `skills/using-gws-toolkit/SKILL.md` routing table
  - Anchor format: `English term (日本語 / 中文)` at key concept
    points; downstream references reuse the English term
  - Anchor density: ~8 per slides-design SKILL.md, ~19 on
    minto-scqa.md, ~25 on chart-selection.md, ~8 in router routing
    table, ~4 on self-check rubric
- **PRODUCT-SPEC** — added `§6.4 Language strategy` formalising (A)
  technical EN-primary / (B) design trilingual / (C) frontmatter multi
  / (D) maintenance rules

### Preserved

- All SKILL.md frontmatter `description` fields (bilingual / trilingual
  keyword triggers for Claude Code auto-routing — unchanged)
- Technical facts (commands, exit codes, JSON shapes, file paths, EMU
  values) — all v0.5.0 live-validated semantics intact
- Primary source citations (Minto 1987, Cleveland & McGill 1984, Few
  2012, Duarte 2008/2010, Tufte 2001)
- `docs/*.md` — still Chinese-primary per user directive (internal
  maintenance notes / implementation journals)
- Version history and revision annotations in script headers (`v0.3`,
  `v0.3.1`, `v0.3.2`, `v0.5.1`)

### Rationale

Technical content is 95% code-surface terms (gws commands, JSON, API
fields) that are inherently English; Chinese translation noise
outweighs readability gain. Design / content layer meets the user in
natural-language conversation ("棒グラフ" / "長條圖" / "bar chart"
should all route to the same recipe), so trilingual anchors preserve
alignment without bloating the prose. `docs/*` stays Chinese-primary
because it serves as internal maintenance record where authorial
velocity > international reach.

## [0.5.1-smooth-reauth] - 2026-04-24

**UX refinement**（非 pivot；無 scope 變動）— 把「7 天 token 過期」的
recovery 從「使用者 copy-paste 長指令」提升為「Claude 偵測 exit 10 →
自動呼叫 helper → browser open → user 點 Allow → retry」，無痛體驗。

### Added

- `scripts/gws/refresh-auth.sh`（60 lines）— 一鍵 re-auth helper：
  - 自動 source `~/.config/gws/env.sh`（issue #119 workaround env vars）
  - 呼叫 `gws auth login --scopes=<presentations,drive.file>`（完整 URL，
    避免 `-s` service filter 陷阱）
  - Pre-flight 驗 `client_secret.json` / `env.sh` / `gws` binary 存在
  - Exit 0 success / 10 gws auth fail / 1 generic
  - `SLIDES_TOOLKIT_SCOPES` env override
  - 三個 entry point 共用：Claude orchestration / user alias
    (`gws-relogin`) / cron（未來若加）

### Changed

- `skills/slides-builder/SKILL.md` §Token expiry — 從 "passive
  detect + 告知使用者手動跑" 升級為「exit 10 recovery protocol」5-step
  明文（偵測 → 告知 → 自動觸發 refresh-auth.sh → retry 原 op → 失敗
  才 escalate）。加 zsh alias `gws-relogin` 建議。
- `skills/google-slides-api/references/api-error-codes.md` exit 10 section
  — Recovery 指令從 `gws auth login -s presentations,drive.file`（錯的
  scope 語法）改為推薦 `refresh-auth.sh` helper + 保留手動展開版供 fallback。
  指向 `slides-builder/SKILL.md §Token expiry` 為權威 orchestration
  protocol。

### Rationale

v0.5.0 live E2E 驗證後，唯一 recurring friction 是每 7 天重跑 `gws auth
login`——該指令含兩條完整 scope URL + 需先 source env.sh + export。複
製貼上易出錯（例：`-s` vs `--scopes=` 語法差異）。

v0.5.1 把這一長串收斂到單一 helper script：
- **Claude 偵測 exit 10 → 呼叫 helper**：無需 Claude 記住長指令
- **User 偏好手動**：alias 一個 `gws-relogin` 詞即可
- **未來 cron / launchd 自動提醒**：仍指向同一 helper（DRY）

唯一仍需使用者互動的是瀏覽器點「Allow」（Google OAuth policy 強制，
`docs/google-oauth-automation-limits.md` 已記錄為永久邊界），約 10 秒。

## [0.5.0-live-validated] - 2026-04-24

**Live E2E Validated**（非 pivot；無 scope 變動）— 首次在真實環境完整跑
過 4 recipes 端對端流程。OAuth 認證 + 建 deck + 建 slides + 填文字 +
插入圖片全綠。過程中暴露出 walkthrough / recipes 與真實 gws CLI 行為的
若干 drift，全數修正。同時新增 `auto-setup.sh` 把可自動化部分 codify。

### Added

- `scripts/gws/auto-setup.sh` — 535 行 shell script，idempotent
  7 步自動化：detect/install gcloud → gcloud auth → GCP project create
  → enable APIs → open Console URLs → wait for client_secret → install
  credentials + write env.sh → gws auth login → verify。支援
  `--dry-run` / `--force-reinstall`；`SLIDES_TOOLKIT_PROJECT_ID` env
  override；stdout JSON contract `{status, project_id, account, scopes,
  elapsed_sec, dry_run}`
- `skills/gws-setup/protocols/gcp-console-walkthrough.md` 重寫
  為雙路徑：**Path A (Fast, ~6-8 min)** 走 auto-setup.sh；**Path B
  (Manual, ~10-15 min)** 純 Console；共用 §Local 結尾
- 4 個 recipe md 檔尾加「## Live-tested behavior (2026-04-24)」區塊，引用
  實測出的 JSON 片段

### Changed

- `gcp-console-walkthrough.md` 全面更新為 Google Cloud Console **新 UI**
  語言：Google Auth Platform / Branding / Audience / Clients（舊版
  "APIs & Services → OAuth consent screen → Test users" → 新版
  "Google Auth Platform → Audience → Test users section"）。每步 URL
  帶 `?project=<PROJECT_ID>` placeholder
- `recipe-create-presentation.md` — default slide placeholder 更正為
  `CENTERED_TITLE` + `SUBTITLE`（非 TITLE），加 `presentations.get`
  正確呼叫示範（`presentationId` / `fields` 皆入 `--params`）
- `recipe-create-slides.md` — `batchUpdate` 呼叫修正為
  `--params '{"presentationId":"..."}'`（非獨立 flag）；加 layout →
  placeholder type 對照表（TITLE 用 `CENTERED_TITLE` + `SUBTITLE`；
  其他 layout 用 `TITLE` + `BODY` etc.）
- `recipe-insert-text.md` — 加 `{{TITLE}} → CENTERED_TITLE` fallback
  mapping rule；`batchUpdate` 呼叫改 `--params`；修正 reply object
  為 `{}`（非 `{"insertText":{}}`）；刪除不必要的 `insertionIndex: 0`
- `recipe-insert-image.md` — **最大 delta**：
  - 加 ⚠️ cwd sandbox 警示：`gws drive files create --upload` 要求檔案
    在 cwd 或其子目錄；absolute path 會被 reject
  - `--upload-file` → `--upload`（flag 名字錯）
  - `drive permissions create` 的 `fileId` 入 `--params`
  - Image URL 手動拼 `https://drive.google.com/uc?id=<FILE_ID>`（
    **不用** response 的 `webContentLink`，後者帶 `&export=download`
    會讓 Slides createImage render 失敗）
  - 加 Gotchas 表（7 條 trap + fix）
  - EMU 座標值更新為實測驗證過的數字

### Rationale

Live E2E 在 kouko 本機跑過（macOS arm64、個人 @gmail）：
- gcloud 首次裝 + auth + project create + enable APIs 全自動
- Console 手動 2 步（Audience 加 test user / Clients 建 Desktop client +
  download JSON）— 無法自動化（Google IAP OAuth Admin API 已 2025-01-22
  deprecated，證據見 gws source `setup.rs:913` 註解）
- gws auth login 走 `--scopes=<URL>,<URL>` 而非 `-s`（後者是 service
  filter 不是 scope 指定）
- 實測產物：<https://docs.google.com/presentation/d/1rCqdw0HvYow4Hr5l38Ark1ZzpDsGYptWtW-dHkYT6lY/edit>
  （含 2 slides + 1 image，全部 4 recipes 實證有效）

此 validation round 把過往「spec 內寫的 recipe」變成「spec 內寫的是**實測
驗證過的** recipe」，是 MVP 從 paper design → working system 的關鍵里程碑。

## [0.4.2-api-sibling-skill] - 2026-04-24

**Architectural layer split**（純 refactor；無 scope / 功能變動）— 把
`slides-builder/protocols/` 下的 4 個 per-op recipe 抽出成 sibling
skill `google-slides-api`，builder 變薄保留 pipeline orchestration 職責。

### Added

- `skills/google-slides-api/SKILL.md` — 低層入口（op list + composition
  pattern via placeholder_map + when-to-use boundary）
- `skills/google-slides-api/references/api-error-codes.md` — 10/11/12/
  13a/13b/14/15/16/18 exit code 語意 + 救援 playbook，集中於此 reference

### Changed

- `skills/google-slides-api/protocols/recipe-create-presentation.md` ←
  `git mv` from `slides-builder/protocols/`
- `skills/google-slides-api/protocols/recipe-create-slides.md` ← git mv
- `skills/google-slides-api/protocols/recipe-insert-text.md` ← git mv
- `skills/google-slides-api/protocols/recipe-insert-image.md` ← git mv
- `skills/slides-builder/SKILL.md` — 變薄：改為引用 sibling
  skill 的 recipes；Step 2-4 路徑改為 `../google-slides-api/protocols/*`
- `skills/slides-builder/checklists/pre-flight.md` — 下游 recipe
  連結改為 sibling skill 路徑
- `skills/using-gws-toolkit/SKILL.md` — routing table 加第 4 分支
  （「單一 API op / debug / 學 batchUpdate」→ `google-slides-api`）
- `PRODUCT-SPEC.md` §6.3.1 + `TECH-SPEC.md` §2.1 目錄樹更新
- `TECH-SPEC.md` Revision History 加 v0.3.2 條目

### Rationale

- **SRP**：per-op recipe（low-level API wrapping）與 pipeline
  orchestration（high-level slide-plan.json consumer）為兩種獨立變動
  維度。分離後各自演進；Slides API 升版只動 api skill，pipeline 設計
  改動只動 builder。
- **OCP**：Phase 2+ 出現 second consumer（e.g. slide-deck-auditor,
  deck-diff tool）時，可直接引用 `google-slides-api` 而不需經 builder
  的 slide-plan.json schema 層。
- **授權自主**：新 skill 為原創 MIT 內容，與 gws-slides（Apache-2.0
  SKILL.md，僅 44 行 API 目錄）**無程式碼依賴**。`gws` binary 仍為
  runtime 被動呼叫（subprocess），不入 repo。未來想引用 gws-slides 成
  optional cross-reference link，不需 NOTICE / attribution。
- **架構對照 gws-slides**：研究確認 gws-slides 只是 API discovery
  reference（44 lines, 無 recipes），我們的 4 recipe 對其**非 redundant**
  （~20% overlap）— builder 層的 orchestration + placeholder_map 組裝 +
  error handling 為我們獨有價值。詳見研究結論（conversation record
  2026-04-24）。

### Removed

- `skills/slides-builder/protocols/` 目錄（內容移至 sibling skill）

## [0.4.1-auto-refresh-binary] - 2026-04-24

**Runtime simplification**（非 pivot）— 消除 `GWS_VERSION` TODO；gws
binary 改為解析 GitHub `/releases/latest/download/` redirect；加入 TTL
based auto-refresh。jq 繼續 pin `1.7.1`（release 穩定）。

### Added

- `bootstrap.sh` TTL-based auto-refresh：`.version.installed_at` 超過
  `SLIDES_TOOLKIT_BINARY_TTL_DAYS`（預設 30）時，自動重抓 latest
- `bootstrap.sh` auto-refresh 安全網：refresh 失敗（網路 / 上游 503）
  **保留既有 binary**、印 stderr warning、exit 0，不阻斷日常使用
- `bootstrap.sh` 透過 GitHub REST API（`/repos/.../releases/latest`）
  解析實際 tag 並寫入 `.version.gws_tag`，供 debug / audit
- `.version.source` 欄：`env-pinned` / `auto-resolved` / `auto-resolve-failed`
- Env `GWS_VERSION=v0.X.Y`：pin 某版（停用 auto-refresh）— 用於救火
  或固守穩定版
- Env `SLIDES_TOOLKIT_BINARY_TTL_DAYS`：客製 TTL

### Changed

- `bootstrap.sh` 預設 URL：`/releases/download/<tag>/` →
  `/releases/latest/download/`（GitHub 原生 302 redirect）
- `.version` schema：`{gws, jq, written_at}` →
  `{gws_tag, jq_tag, source, installed_at}`
- `GWS_VERSION` 環境變數從必填 → **optional pin override**

### Removed

- `bootstrap.sh` 的 `GWS_VERSION="v0.0.0-TODO"` default（改為空字串
  表 auto-resolve）

### Rationale

- `GWS_VERSION` pin 是 v0.3 唯一剩下的 TODO；auto-resolve 消掉它
- 30 天 TTL 讓 binary 自動跟上 upstream bugfix，不需使用者手動操作
- Pin override 給「upstream breaking change」的救火窗口
- jq 不走 latest：jq 1.7.1 已穩定 > 12 個月，無需自動追蹤

### Phase 2+（trigger-gated；見 `PRODUCT-SPEC.md §3.5`）

- `html-builder` skill（首次 HTML 輸出需求觸發）
- `pptx-builder` skill（首次 `.pptx` 輸出需求觸發）
- `marp-builder` skill（首次 Marp 輸出需求觸發）
- Template-based workflow return（Google predefined layouts 視覺品質不足
  或需品牌一致性時觸發）
- SHA-256 supply-chain pin（publish / CI / 安全事件觸發）
- `helpers/build_plan.py`（shell 組 JSON 首次出現痛苦時觸發）
- slide-plan schema 正式 backend-agnostic / backend-specific 切分
  （第二個 backend 實作時觸發）

## [0.4.0-scope-refinement] - 2026-04-24

**Scope Refinement**（非 pivot）— 對齊 PRODUCT-SPEC v0.3 + TECH-SPEC v0.3。
Job Story、4 Big Risks、MVP validated-learning 核心假設、OKR / NSM 皆未動。

### Removed

- `skills/slides-builder/templates/`（整個目錄 + `registry.md`）
  — 使用者自備 template + Drive ID lookup 不再是 MVP 路徑
- `skills/slides-builder/protocols/recipe-copy-template.md`
  — `gws drive files copy` 流程不再需要
- `skills/slides-builder/protocols/recipe-replace-text.md`
  — 改名為 `recipe-insert-text.md`（new file）
- `bootstrap.sh` 的 SHA-256 驗證：`GWS_SHA256_*` / `JQ_SHA256_*` 4 個常數、
  `verify_sha256()` / `expected_sha_for()` 函式、exit code 17 `SHA mismatch`
  — 改以 HTTPS + `curl -fLSs` + URL pin 為 integrity 邊界

### Added

- `skills/slides-builder/protocols/recipe-create-presentation.md`
  — `gws slides presentations create --json '{"title":"..."}'` 建空 deck
- `skills/slides-builder/protocols/recipe-create-slides.md`
  — `batchUpdate createSlide` 搭配 `layout_hint` enum（7 個 Google 預設
  predefinedLayout 值）逐 slide 建構
- `skills/slides-builder/protocols/recipe-insert-text.md`
  — `batchUpdate insertText` 到 placeholder object ID（不再用
  `{{PLACEHOLDER}}` 文字錨點）
- slide-plan.json schema v1.1 → **v1.2**：新增 `slides[].layout_hint`
  （必填 enum）；刪除 `backend_config.template_ref`

### Changed

- `skills/slides-builder/SKILL.md` — 重寫 workflow 為 4-step
  （pre-flight → create → build slides → insert text/image）
- `skills/slides-builder/protocols/recipe-insert-image.md`
  — 從 `replaceAllShapesWithImage` 改為 `createImage` with explicit
  `pageElementProperties`，接 `placeholder_map` 對位
- `skills/slides-builder/checklists/pre-flight.md` — 10 項 check
  更新（刪 registry 檢查、加 `layout_hint` enum 檢查）
- `PRODUCT-SPEC.md` v0.2 → v0.3（Scope Refinement；+2 Non-Goals
  template/SHA + 2 Future Phases trigger + Principle 2 rewrite
  Template-based → Layout-based）
- `TECH-SPEC.md` v0.2 → v0.3（schema v1.2 + 4 recipes + SHA 移除 +
  C13 refactor commit）

### Rationale

個人使用閉環下：
- **Template overhead > 視覺品質邊際增益** — maintain template deck +
  registry.md + placeholder drift 的成本大於 Google 預設 layout 不精美
  帶來的微差
- **SHA 維護成本 > 邊際安全增益** — 個人 scope 下，HTTPS + `curl -f`
  + GitHub org 信任邊界足夠；SHA pin 每次 upstream release 都要更新
  的 overhead 不成比例

兩條都列 Phase 2+ trigger：publish 給外部 / CI / 視覺不足 / 安全事件
→ 隨時可恢復。

## [0.3.0-scaffold] - 2026-04-23

**Scaffold 交付**（Platform Pivot 後的首次 code 階段）— 依 TECH-SPEC v0.2
C1–C7 commits 建出 plugin 骨架。仍**未**真正可運作（含 TODO placeholder
待 kouko 於本機填入版本 pin + SHA-256 + Drive ID）。

### Added

- `.claude-plugin/plugin.json` + `README.md` + `CHANGELOG.md` + `.gitignore`
- `.claude/settings.json` deny rule（TECH-SPEC §8.1 完整 13 條：含
  `Read` / `Bash(cat|cp|git add)` / `Write` 防護）
- `scripts/gws/` 下 4 支 shell script：
  - `bootstrap.sh`（抓 gws + jq binary；SHA-256 pin + verify；idempotent）
  - `gws-wrap.sh`（pre-flight + retry with exponential backoff 5s/10s/20s）
  - `env-guard.sh`（issue #119 workaround，ISP 拆 `check` / `apply`）
  - `credential-check.sh`（Keychain silent-fail 偵測 + file backend fallback）
- `scripts/common/.gitkeep`（Phase 2+ 預留）
- `incidents/README.md`（on-demand playbook 入口）
- 4 個 SKILL.md：
  - `using-gws-toolkit`（backend-agnostic router）
  - `slides-design`（backend-agnostic 知識層）+ `references/minto-scqa.md`
    + `references/chart-selection.md` + `rubrics/slide-plan-self-check.md`
  - `gws-setup` + `protocols/gcp-console-walkthrough.md`（10 步）
    + `protocols/issue-119-workaround.md` + `standards/credential-hygiene.md`
    + `checklists/setup-state.md`
  - `slides-builder` + 3 recipe protocols（copy-template / replace-text
    / insert-image）+ `templates/registry.md` + `checklists/pre-flight.md`

### Known placeholders

所有 `TODO_FILL_REAL_SHA256_64HEX` / `v0.0.0-TODO` / `TODO: fill Drive ID`
必須由 kouko 在本機填入後才能跑通 E2E。Public repo commit 前應確認
`registry.md` 的 Drive ID 仍為 `TODO` 骨架，避免洩漏。

## [0.2.0-spec] - 2026-04-23

**Platform Pivot**（Ries 2011 Part Two pivot type #5）— 僅 spec 階段變更，
尚未 code。架構從「為單一輸出格式服務的 application」轉為「以設計知識層
為核心、可插拔多 backend 的 platform」。Job Story、4 Big Risks、MVP
validated-learning 假設、3 core recipe 均不變動。

### Changed

- `skills/slides-setup/` → `skills/gws-setup/`
  （backend-prefix 命名；Google Slides backend 專屬）
- `skills/slides-builder/` → `skills/slides-builder/`
  （backend-prefix 命名；Google Slides backend 專屬）
- `scripts/` 分子目錄 → `scripts/common/` + `scripts/gws/`
- `using-gws-toolkit`（router）與 `slides-design`（knowledge）
  **保持通用命名**，不加 backend 前綴

### Added

- Multi-backend architecture 擴充點預留（`scripts/common/`、phase 2+
  `html-builder` / `pptx-builder` / `marp-builder` 觸發條件）
- `slide-plan.json` schema v1 → v1.1：新增 `target`（e.g.
  `"target": "google-slides"`）+ `backend_config` 欄位，避免 Google
  Slides 特有 detail 污染通用 slide-plan contract
- `PRODUCT-SPEC.md` v0.2 Revision History 條目 + §3.5 新 trigger 條件
  （html / pptx / marp 各自觸發 + backend interface 正式化觸發）
- `TECH-SPEC.md` v0.2 Revision History 條目 + §9 OPEN-11 回答（slide-plan
  `target` field 的 MVP 最小處理）+ rename migration log 表

### Rationale

輸出格式會演化（今天 Google Slides，未來 HTML / PPTX / Marp），但 Minto
/ SCQA / chart-selection 等設計原則穩定。把兩者解耦可避免重寫知識層，
且讓 Phase 2+ 新 backend 不需改動既有 skill。**不動搖 MVP 範圍**：MVP
仍僅實作 Google Slides backend。

## [0.1.0-spec] - 2026-04-23

PRODUCT-SPEC + TECH-SPEC 初版交付（spec 階段；尚未 code）。
經 4 輪 deep research 凍結 MVP 方向後產出。

### Added

- `PRODUCT-SPEC.md`（planning-team 擁有）— 跨域願景 + MVP scope
  - §1 Background & Opportunity（當前痛點 5W2H + Why now + opportunity framing）
  - §2 Target Users（primary = kouko / Job Story per Adams 2016）
  - §3 Goals & Non-Goals（Doerr OKR 4 KRs + Ubl Non-Goals + Cagan 4 Big
    Risks + Bland & Osterwalder Assumption Mapping + Ries MVP definition）
  - §4 Core Concept（value prop + 3 scenarios + 6 design principles）
  - §5 UX Direction（flow diagram + CLI-only + constraints）
  - §6 跨域考量（business / design / technical direction with rationale）
  - §7 Success Criteria（Ellis & Brown North Star + supporting KRs）
  - §8 Open Questions（10 條留給 TECH-SPEC）
  - §9 Risks & Assumptions summary
  - §10 Downstream Handoff（團隊分工 + 5W2H final check）
- `TECH-SPEC.md`（code-team 擁有）— 技術模組設計 + 10 OPEN answers
  - §1 Scope & Constraints（goals / non-goals / hard constraints）
  - §2 Architecture（plugin layout + diagram + binary cache）
  - §3-§6 Module design / Interface / Data flow / Error handling
  - §7 Testing（dry-run + golden snapshot + fixture strategy）
  - §8 Security & Credential Hygiene（ASVS L1 mapping + deny rule
    + .gitignore + pre-commit + incident response playbook + character
    encoding）
  - §9 Answers to 10 PRODUCT-SPEC OPEN questions
  - §10 Implementation phases + commit split
  - §11 Module Readiness Summary
