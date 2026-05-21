# Issue #119 Workaround — gws on Personal Gmail OAuth

> Upstream issue: `googleworkspace/cli#119` (TODO: fill in issue URL).
> Status: the workaround was confirmed effective when the MVP was
> implemented ([ASSUMPTION-3], PRODUCT-SPEC §3.3). If the upstream
> fix ever lands, see
> [When you can drop the workaround](#when-you-can-drop-the-workaround)
> at the end of this document.

## Background

The `gws` CLI (`googleworkspace/cli`) ships with a built-in OAuth
Client ID + Secret so that `gws auth login` works out of the box for
Google Workspace tenants.

But under the combination of **personal `@gmail.com`** +
**External + Testing consent screen**, this built-in client
consistently throws one of:

- `invalid_scope` — Google rejects the scope list gws requested
  (e.g. picking "all available scopes" in the consent picker — gws
  v0.22.5 has no `--preset recommended` flag; the 25-scope Testing-mode
  cap is the underlying constraint).
- `invalid_client` — Google does not recognize the gws built-in
  client as valid for a personal Gmail user. (Workspace-tenant
  clients cannot be used across tenants.)

## Root cause

gws's default OAuth flow is designed for **Google Workspace
tenants** — the ones with an Admin Console, a company domain, and
internal apps sanctioned by an Admin. Personal `@gmail.com` accounts
with an unverified External consent screen don't sit on that path —
Google treats "Workspace-tenant client × personal Gmail user" as
illegal cross-tenant use.

From the gws team's point of view this is not a bug; the target user
base (Workspace) explicitly doesn't include personal Gmail. From
this project's point of view it's a hard blocker (PRODUCT-SPEC
§6.3.3 Risk: gws issue #119, likelihood high, impact high).

## The workaround

**Override the built-in client with the OAuth client you created in
your own GCP project.**

gws honors two env vars that, when present, override its built-in
client:

- `GOOGLE_WORKSPACE_CLI_CLIENT_ID`
- `GOOGLE_WORKSPACE_CLI_CLIENT_SECRET`

The client you downloaded in `gcp-console-walkthrough.md` §4–§5
(`client_secret.json`) is a legitimate first-party client against
the OAuth consent screen *you* own in *your own* GCP project, so you
won't hit `invalid_client`. And the scope list is whatever your
consent screen accepts (you define it), so `invalid_scope` goes away
too.

## Concrete commands

### One-shot export (current shell only)

```bash
export GOOGLE_WORKSPACE_CLI_CLIENT_ID=$(jq -r .installed.client_id ~/.config/gws/client_secret.json)
export GOOGLE_WORKSPACE_CLI_CLIENT_SECRET=$(jq -r .installed.client_secret ~/.config/gws/client_secret.json)
```

**Prerequisites**:

- `~/.config/gws/client_secret.json` exists
  (`gcp-console-walkthrough.md` §5).
- `jq` is on PATH. Either put `~/.cache/gws-toolkit/bin/` on PATH,
  or alias `jq=~/.cache/gws-toolkit/bin/jq`.

### Write to shell profile (persistent)

Append the block below to `~/.zshrc` (the zsh default on macOS) or
`~/.bashrc` (for bash):

```bash
# slides-toolkit — gws issue #119 workaround
if [ -f ~/.config/gws/client_secret.json ]; then
  export GOOGLE_WORKSPACE_CLI_CLIENT_ID=$(jq -r .installed.client_id ~/.config/gws/client_secret.json 2>/dev/null)
  export GOOGLE_WORKSPACE_CLI_CLIENT_SECRET=$(jq -r .installed.client_secret ~/.config/gws/client_secret.json 2>/dev/null)
fi
```

The `2>/dev/null` keeps your terminal quiet when `jq` isn't on PATH
yet.

Open a new terminal or run `source ~/.zshrc` to activate.

### Use `env-guard.sh apply` (recommended)

Let the skill write the env vars into a standalone
`~/.config/gws/env.sh` (chmod 600) which
`scripts/gws/gws-wrap.sh` sources on every call:

```bash
bash scripts/gws/env-guard.sh apply
```

**Advantages**:

- Standalone file is easy to manage (remove the workaround by simply
  deleting `env.sh`).
- chmod 600 is set automatically.
- `gws-wrap.sh` sources it internally, so your global shell profile
  stays clean.
- Aligns with rule 2 of `standards/credential-hygiene.md`
  (credentials centralized under `~/.config/gws/`).

## How to verify the workaround is active

**Negative check** (before applying):

```bash
unset GOOGLE_WORKSPACE_CLI_CLIENT_ID GOOGLE_WORKSPACE_CLI_CLIENT_SECRET
gws auth login --scopes=presentations,drive,documents,spreadsheets
# Expected: error message containing invalid_scope or invalid_client
```

**Positive check** (after applying):

```bash
source ~/.config/gws/env.sh   # or reopen the terminal if persisted to profile
gws auth login --scopes=presentations,drive,documents,spreadsheets
# Expected: browser opens consent screen; afterwards `gws auth whoami` returns your email
```

Or use `env-guard.sh check`:

```bash
bash scripts/gws/env-guard.sh check
# Expected: {"workaround_needed":false}  ← already active
# If it returns {"workaround_needed":true} then env vars are not
# exported — rerun env-guard.sh apply.
```

## When you can drop the workaround

You can consider removing this workaround only when **all** of these
are true:

1. `googleworkspace/cli` officially fixes issue #119 (e.g. the
   built-in client starts accepting personal Gmail, or the CLI adds
   an official `--use-external-oauth-client` flag).
2. `~/.cache/gws-toolkit/bin/gws` has been upgraded to the fixed
   version.
3. `scripts/gws/env-guard.sh`'s feature flag detects a
   version >= known-fixed (see TECH-SPEC §6.1 final paragraph).

Until then **keep the workaround**. Every time `bootstrap.sh`
upgrades the gws binary, re-run both checks above (negative +
positive) — gws releases can silently fix the issue *or* silently
break the workaround. Either direction matters.

To stay on top of this: subscribe to the upstream issue, or attach
the latest issue status to the PR whenever `bootstrap.sh` pins a new
version.

## Related files

- `protocols/gcp-console-walkthrough.md` §8 — setup flow step 8
- `standards/credential-hygiene.md` — the hard rule that credentials
  live in `~/.config/gws/`
- `../../scripts/gws/env-guard.sh` — check / apply
  implementation
- `../../scripts/gws/gws-wrap.sh` — sources `env.sh`
  before every call
- TECH-SPEC §4.2 — `env-guard.sh` contract, exit 16
- TECH-SPEC §6.1 — full workaround implementation notes
- PRODUCT-SPEC §3.3 [ASSUMPTION-3] — workaround-stability assumption
