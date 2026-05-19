# gcal-automate Failure Modes (gws CLI)

Failure modes against the Google Workspace CLI (`gws`). Read-only protocols only.

## Shared OAuth with gmail-automate

**Background**: `gws` uses a single OAuth grant covering Gmail + Calendar + Drive scopes. The grant is established by `gws auth` once and shared across all `gws` subcommands and all sibling skills (`gmail-automate`, `gcal-automate`, future `gdrive-automate`).

**Implication**: if `gws auth` fails OR the grant is revoked, **both** `gmail-automate` and `gcal-automate` break simultaneously. Conversely, re-authing here fixes both.

**Symptom**: tool call returns `auth: token expired` / `auth: refresh failed` / `403 insufficient_scope` / a redirect to `accounts.google.com`.

**Remediation**:
1. Run `gws auth` — opens the browser, prompts for Google login, refreshes the shared grant.
2. Retry the failing protocol.
3. If `gws auth` itself fails, verify `GOOGLE_CLOUD_PROJECT` is set (see next section) — the OAuth client lives under that project.

## GOOGLE_CLOUD_PROJECT environment variable

**Background**: `gws` requires `GOOGLE_CLOUD_PROJECT` to identify which Google Cloud project hosts the OAuth client used for authentication.

**Symptom**: `gws auth` or any `gws calendar` subcommand returns `ERR: GOOGLE_CLOUD_PROJECT not set` / `project required` / similar.

**Remediation**:
```bash
export GOOGLE_CLOUD_PROJECT=<your-gcp-project-id>
```

Persist via `~/.zshrc` (macOS default shell) or `/collab-setup` (which records this on first-run). Verify with `echo $GOOGLE_CLOUD_PROJECT`.

## Timezone handling

**Background**: Google Calendar stores event times as RFC-3339 timestamps with explicit UTC offsets. `gws calendar events list` returns `start.dateTime` and `end.dateTime` typically in UTC (`...Z`).

**Implications for protocols**:
- **Always pass `--time-min` / `--time-max` with explicit offset** (e.g., `2026-05-19T00:00:00+08:00`, not `2026-05-19T00:00:00`). Naked-naive timestamps may be interpreted as UTC, shifting the window 8 hours in `Asia/Taipei`.
- **`find-free-slots` clipping** must convert UTC returned timestamps to the user's tz before comparing against business-hours `HH:MM` strings.
- **All-day events** use `start.date` (no time component) — these are date-only and tz-independent.

**Common symptom**: agenda-view returns events that appear "off by one day" or "off by 8 hours" — verify offset on `--time-min` / `--time-max`.

## Recurring-event expansion

**Background**: by default, `gws calendar events list` returns *master* recurring events (one entry per recurrence rule, with `recurrence` field but no per-instance `start`/`end`). To get one row per occurrence, pass `--single-events true`.

**Symptom**: agenda-view shows fewer events than expected, or `find-free-slots` misses busy slots from a recurring meeting.

**Remediation**: ensure all events-list invocations pass `--single-events true`. The protocols document this in their `## Steps` sections; verify the flag is present.

**Caveat**: `--single-events true` is *not* a default — it must be passed explicitly per call.

## Subcommand-name verification

**Status**: subcommand names below are **assumed** based on Google Calendar API REST endpoint naming and the gws sibling-skill pattern. Verified against the actual `gws --help` output: **not done during initial v0.2.0 rewrite** — flagged for follow-up.

**Assumed subcommand names**:
- `gws calendar events list --time-min <iso> --time-max <iso>` (for protocols/agenda-view.md, protocols/find-free-slots.md)
- `gws calendar events search --query "<text>"` (for protocols/event-search.md)
- `gws calendar events list --calendar <id> ...` (for protocols/shared-calendar-read.md)
- `gws calendar list` (for protocols/shared-calendar-read.md — enumerate subscribed calendars)

**Verification procedure** (one-shot, run after first `gws auth`):
1. Run `gws calendar --help` and `gws calendar events --help`.
2. Compare returned subcommand names + flag names to the assumed list above.
3. If any name differs, update both `SKILL.md` and the protocol's example invocations + `## Input` mapping.

## Rate limit

**Symptom**: subcommand returns 429 / "Rate Limit Exceeded" / "Quota exceeded".

**Background**: Google Calendar API per-user quota is generous (default ~600 req/min per user), but a tight loop in `find-free-slots` across many calendars can hit it.

**Remediation**:
- Implement exponential backoff: wait 2s, retry; on second 429 wait 8s; on third give up and surface error.
- For multi-calendar busy-merge in `find-free-slots`, throttle to ≤5 req/s.

## Empty result vs error

**Disambiguation**:
- Subcommand returns `items: []` with exit code 0 → valid empty result. Emit `No events in <date range>.`
- Subcommand returns non-zero exit code → error. Surface `ERR: <stderr>` to user.
