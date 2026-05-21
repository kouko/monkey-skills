# Setup State Checklist — gws-setup

> After running setup — or when coming back to diagnose a problem —
> work through the 6 state checks below in order. **If any check
> fails, fix it using the matching walkthrough section before moving
> on. Don't skip ahead.**

## How to use this checklist

Run checks 1 through 6 in order. Each check gives you:

- **Check command** (copy-paste ready)
- **Expected output** (and what counts as pass)
- **Failure branch** (pointer into
  `protocols/gcp-console-walkthrough.md` or elsewhere)

If you want to automate, fold the checks into an extended version
of `scripts/gws/credential-check.sh`. This checklist is
the manual version — useful during first-time setup and debugging.

---

## 1. Is the `gws` binary present?

**Why**: `~/.cache/gws-toolkit/bin/gws` is the execution point
for every Google Slides backend operation. No binary, no show.

**Check**:

```bash
ls ~/.cache/gws-toolkit/bin/gws
```

**Expected output**:

```
/Users/<you>/.cache/gws-toolkit/bin/gws
```

And it should run:

```bash
~/.cache/gws-toolkit/bin/gws --version
# Expected: gws vX.Y.Z (version depends on bootstrap.sh pin; TODO: fill in current pin)
```

**Failure branch**:

- File missing → `gcp-console-walkthrough.md` §7 (run
  `bootstrap.sh`).
- Present but not executable (`Permission denied`) →
  `chmod +x ~/.cache/gws-toolkit/bin/gws`, or rerun
  `bash scripts/gws/bootstrap.sh --force`.
- `--version` fails to run → rerun `bash scripts/gws/bootstrap.sh --force`
  to re-download. (SHA-256 verification was retired in v0.4.0; HTTPS +
  URL pin + official GitHub org is now the integrity boundary —
  TECH-SPEC §2.3.)

---

## 2. Is the `jq` binary present?

**Why**: the BYO-client env-var mechanism uses `jq` to extract fields
from `client_secret.json` when setting env vars; the builder pipeline
also uses `jq` to validate slide-plan schemas.

**Check**:

```bash
ls ~/.cache/gws-toolkit/bin/jq
~/.cache/gws-toolkit/bin/jq --version
# Expected: jq-1.7.1 or newer
```

**Failure branch**:

- File missing → `gcp-console-walkthrough.md` §7
  (`bootstrap.sh` fetches gws and jq together — they usually
  succeed or fail as a pair).
- Present but version < 1.7.1 →
  `bash scripts/gws/bootstrap.sh --force`.
- Correct version but `command not found` at runtime → PATH doesn't
  include `~/.cache/gws-toolkit/bin`. Pick one:
  1. Temporary: `export PATH="$HOME/.cache/gws-toolkit/bin:$PATH"`
  2. Permanent: append to `~/.zshrc`
  3. Per-call: use the absolute path
     `~/.cache/gws-toolkit/bin/jq`

---

## 3. Is `gcloud` installed? (optional)

**Why**: **the MVP does not depend on gcloud** (runtime
minimalism — PRODUCT-SPEC §4.4 principle 1). This check is
optional: **gcloud can speed up some Console tasks (switching
project, checking quota), but its absence doesn't affect this
skill.**

**Check**:

```bash
which gcloud && gcloud --version
```

**Expected output** (either case counts as pass):

- Case A (**recommended**, aligned with runtime minimalism):

  ```
  gcloud not found
  ```

  Not installed = matches the MVP pure-shell path.

- Case B (installed):

  ```
  /opt/homebrew/bin/gcloud
  Google Cloud SDK 4XX.0.0
  ...
  ```

  Installed, no side effects, feel free to keep it.

**Failure branch**: none — this check never blocks setup. If a
future Phase 2+ introduces a gcloud dependency, update this check.

---

## 4. Does `~/.config/gws/client_secret.json` exist?

**Why**: gws reads this file to find the Client ID / Client Secret.
The BYO-client env vars (`GOOGLE_WORKSPACE_CLI_CLIENT_ID/_SECRET`)
are also extracted from it (see `protocols/issue-119-workaround.md`
§Concrete commands — the file path keeps the historical name as a
stable cross-link anchor).

**Check**:

```bash
ls -l ~/.config/gws/client_secret.json
```

**Expected output**:

```
-rw-------  1 <you>  staff  ~400  ...  client_secret.json
```

Key points:

- **Exists**
- **Permissions = `600`** (`-rw-------`) — enforced by
  `standards/credential-hygiene.md` rule 2.

Deeper check (confirms the client type is Desktop):

```bash
~/.cache/gws-toolkit/bin/jq -r '.installed.client_id' ~/.config/gws/client_secret.json
# Expected: non-empty string, usually ending in .apps.googleusercontent.com
```

If `jq` returns `null` or `key "installed" not found`, you
downloaded a Web-type `client_secret.json` (it uses `.web.client_id`
internally) — return to `gcp-console-walkthrough.md` §4 and
recreate as Desktop type.

**Failure branch**:

- File missing → `gcp-console-walkthrough.md` §5 (download + mv +
  chmod).
- Permissions not 600 → `chmod 600 ~/.config/gws/client_secret.json`,
  and verify `chmod 700 ~/.config/gws/` while you're at it.
- `jq ... .installed.client_id` returns null → wrong client type
  (Web instead of Desktop); return to `gcp-console-walkthrough.md`
  §4 and recreate.

---

## 5. Are the BYO-client env vars exported?

**Why**: on External + Testing (personal Gmail or Workspace BYO),
you must export `GOOGLE_WORKSPACE_CLI_CLIENT_ID/_SECRET` for gws to
use your own OAuth client (there is no shared `gws` consumer client;
the IAP OAuth Admin API was deprecated in 2025 — see upstream
README §Authentication). Full details:
`protocols/issue-119-workaround.md` (filename is historical;
content covers the now-canonical BYO-client mechanism).

**Check**:

```bash
# If you went through env-guard.sh:
ls -l ~/.config/gws/env.sh
# Expected: exists, chmod 600

# Or check the current shell directly:
echo "ID length: ${#GOOGLE_WORKSPACE_CLI_CLIENT_ID}"
echo "SECRET length: ${#GOOGLE_WORKSPACE_CLI_CLIENT_SECRET}"
# Expected: both > 20
```

Or use `env-guard.sh check`:

```bash
bash scripts/gws/env-guard.sh check
# Expected: {"workaround_needed":false}
```

**Pass criteria**:

- Both env vars in the current shell have length > 20, **and**
- `env-guard.sh check` returns `workaround_needed: false`.

**Failure branch**:

- Env vars empty / not exported →
  `protocols/issue-119-workaround.md` §Concrete commands (pick one
  of the three options: one-shot export, shell profile, or
  `env-guard.sh apply`).
- `env.sh` exists but isn't active in the current terminal →
  `source ~/.config/gws/env.sh`, or reopen the terminal (if
  persisted to `~/.zshrc`).
- `env.sh` permissions not 600 → `chmod 600 ~/.config/gws/env.sh`.

---

## 6. Does `gws auth whoami` return correctly?

**Why**: this is the **end-to-end check** for the whole setup.
`whoami` returning your email means: the Client Secret is paired
correctly, the BYO-client env vars are active, your Test user is
on the list, the APIs are enabled, the refresh token is valid, and
Keychain (or the explicit file-backend override) is readable.
**whoami passing = the entire setup is green.**

**Check**:

```bash
gws auth whoami
```

**Expected output**:

```
your_email@gmail.com
```

Compare against expected: exactly the email you added as a Test
user in `gcp-console-walkthrough.md` §3.

**Failure branch** (routed by error message):

| Error | Root cause | Go to |
|---|---|---|
| `401 Unauthorized` / `token expired` | Token expired (>7 days unused) | SKILL.md [Every 7 days maintenance](../SKILL.md#every-7-days-maintenance) |
| `403 access_denied` | The Gmail you signed in with isn't in Test users | `gcp-console-walkthrough.md` §3 |
| `403` + `API not enabled` | Slides / Drive API not enabled | `gcp-console-walkthrough.md` §6 |
| `invalid_scope` / `invalid_client` | BYO-client env vars aren't active | Check 5 failed + `protocols/issue-119-workaround.md` |
| `Keychain item not found` / `KeyError` | Keychain unavailable (v0.22.3+ macOS is strict — no silent fallback) | SKILL.md [Workarounds](../SKILL.md#macos-keychain-v0223-strict-mode); explicitly set `GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND=file` if needed |
| `No such file or directory` `gws` | gws not on PATH | Check 1 failed |
| Command exits 0 with no output | Unusual state / outdated gws | `bash scripts/gws/bootstrap.sh --force` to refetch |

---

## Quick run-all

Run all 6 checks in one go:

```bash
echo "--- 1. gws binary ---"        && ls ~/.cache/gws-toolkit/bin/gws && ~/.cache/gws-toolkit/bin/gws --version
echo "--- 2. jq binary ---"         && ls ~/.cache/gws-toolkit/bin/jq && ~/.cache/gws-toolkit/bin/jq --version
echo "--- 3. gcloud (optional) ---" && (which gcloud && gcloud --version 2>/dev/null) || echo "gcloud not installed (OK, MVP doesn't need it)"
echo "--- 4. client_secret.json ---" && ls -l ~/.config/gws/client_secret.json
echo "--- 5. env vars ---"          && bash scripts/gws/env-guard.sh check
echo "--- 6. gws auth whoami ---"   && gws auth whoami
```

The first line that errors out is your blocker. Use the "Failure
branch" column above to fix it, then rerun from that point.

## Related files

- `../SKILL.md` (main flow + error messages guide)
- `../protocols/gcp-console-walkthrough.md` (10-step tutorial)
- `../protocols/issue-119-workaround.md` (BYO-client env-var
  mechanism, full detail — filename historical, content current)
- `../standards/credential-hygiene.md` (`client_secret.json` /
  `env.sh` chmod rules)
- `../../scripts/gws/credential-check.sh` (automated
  state detection)
- `../../scripts/gws/env-guard.sh` (check / apply for the BYO-client
  env-var mechanism)
- TECH-SPEC §3.2 (gws-setup state-detection contract)
- TECH-SPEC §4.2 (`credential-check.sh` / `env-guard.sh` script
  contract)
