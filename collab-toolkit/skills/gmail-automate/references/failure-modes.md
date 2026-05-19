# gmail-automate Failure Modes (gws CLI)

Failure modes against the Google Workspace CLI (`gws`). Read-only protocols only.

## `GOOGLE_CLOUD_PROJECT` env var required

**Symptom**: `gws gmail ...` exits with an error mentioning `project not set`, `quotaProject`, or `GOOGLE_CLOUD_PROJECT`.

**Background**: `gws` invokes the Gmail API through Google's Application Default Credentials (ADC) flow. ADC requires a Cloud project ID to attribute quota usage; the CLI surfaces this requirement as a hard error rather than silently using a default.

**Remediation**:

```bash
export GOOGLE_CLOUD_PROJECT=<your-gcp-project-id>
```

Persist it in your shell rc (`~/.zshrc` / `~/.bashrc`) so every session inherits it. `/collab-setup` records this requirement during the gmail-row acceptance.

## `gws auth` browser flow — `connection refused`

**Symptom**: `gws auth` prints a localhost callback URL (e.g. `http://localhost:8080/...`); the browser opens it; browser shows `ERR_CONNECTION_REFUSED` or `connection refused`.

**Background**: `gws auth` spins up a short-lived loopback HTTP server to receive the OAuth callback. If another process holds the port, or the agent took longer than the OAuth window to redirect, the loopback shuts down before the browser arrives.

**Remediation**:

1. Kill any process bound to the callback port (commonly `:8080`):
   ```bash
   lsof -i :8080
   kill <pid>
   ```
2. Re-run `gws auth` — it will choose a fresh port and re-open the browser.
3. Complete the consent within ~60s of the redirect.

## OAuth scope — 25-item Google limit

**Symptom**: during `gws auth` consent, Google returns `invalid_scope` or the consent screen fails to render after selecting many APIs.

**Background**: Google's OAuth 2.0 implementation caps a single consent request at **25 scopes** (documented in JA-language `gws` notes — Sakasegawa / Qiita). `gws` requests one scope per enabled Workspace surface, so enabling all surfaces (gmail / calendar / drive / sheets / docs / slides / forms / admin / etc.) can collide with the limit.

**Remediation**:

- Enable only the surfaces this skill needs: `gmail.readonly` for gmail-automate, `calendar.readonly` for gcal-automate. Skip surfaces you don't use.
- If you've already enabled too many, run `gws auth --reset` (or remove `~/.config/gws/` credentials) and redo consent with a slimmer scope set.

## Gmail API rate limit

**Symptom**: `gws gmail ...` returns HTTP 429 / "Rate Limit Exceeded" / "User-rate limit exceeded".

**Background**: Gmail API enforces a per-user quota of ~250 quota units / second and a daily cap. Each `messages.list` costs 5 units; each `threads.get` costs 10 units. Bulk enumeration is the typical trigger.

**Remediation**:

- Implement exponential backoff: wait 2s, retry; on second 429 wait 8s; on third surface the error to the user.
- For bulk operations (enumerating all threads in a label), throttle to <10 requests/s.
- The 429 response includes a `Retry-After` header — honor it when present.

## Token refresh

**Symptom**: `gws gmail ...` returns 401 / "invalid_grant" / "token expired".

**Background**: `gws` stores the OAuth refresh token under `~/.config/gws/` (or platform equivalent) and refreshes the access token transparently. Refresh-token expiry is rare but possible (Google rotates refresh tokens after 6 months of inactivity, or on password change).

**Remediation**:

- First failure in a session: retry once.
- Persistent: re-run `gws auth` to redo the consent flow from scratch.

## Tool / subcommand name verification needed

**Status**: subcommand shapes below are **assumed** based on the public `gws` documentation (Sakasegawa / Qiita JA references). They have **not been verified against the live binary** during the v0.2.0 rewrite — flagged for follow-up before any production usage.

**Assumed invocations**:

- `gws gmail messages list --query "<q>" --max-results <n>` (mail-search, inbox-summary, label-read messages section)
- `gws gmail messages list --labels INBOX[,CATEGORY_*] --max-results <n>` (inbox-summary)
- `gws gmail threads get <thread_id>` (thread-read)
- `gws gmail labels list` (label-read)

**Verification procedure** (one-shot, run after first `gws auth`):

1. Run `gws gmail --help` to enumerate the actual subcommand tree.
2. Compare to the assumed forms above. Pay attention to:
   - Flag names (`--query` vs `-q` vs `--filter`)
   - Plural vs singular (`messages` vs `message`)
   - Output format flag (`--json` vs `--format json`)
3. If any subcommand differs, update both the `SKILL.md` allowed-tools comment block (still `Bash(gws:*)` — no change needed there) and each protocol's invocation examples.

## Empty result vs error

**Disambiguation**:

- CLI exits 0 with `[]` JSON or empty stdout → valid empty result. Emit `No <items> matching <filter>.`
- CLI exits non-zero or prints to stderr → error. Surface `ERR: <stderr line>` to user.
