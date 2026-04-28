# User-Terminal Handoff Convention

When a skill needs to invoke an **interactive command** — anything that
expects a TTY for stdout that the human must read in real time, or stdin
for input the human must type — the skill MUST hand off to the user's
own terminal rather than running the command via Claude's Bash tool.

## Primary Sources

- Anthropic Claude Code Bash tool reference (output truncation behavior):
  https://code.claude.com/docs/en/tools-reference#bash-tool
- investing-toolkit `docs/mcp-setup.md` — v1.16.1 retrospective on
  Cowork sandbox URL allowlist behavior (empirical evidence, merged
  PR #154)
- Industry precedent for device-flow handoff: `gh auth login`,
  `gcloud auth login`, `terraform login`, `flyctl auth login`,
  `1password signin` — all print the device-flow code to the user's
  own terminal; the parent CLI never proxies stdout

## Why TTY-Bound Commands Fail Inside the Bash Tool

1. **Output truncation**: Claude Code's Bash tool collapses live
   subprocess output to a "+N lines" indicator while the process is
   running. Codes / OTPs / progress prompts emitted mid-flight are not
   visible to the user as they appear.
2. **Cowork sandbox**: in Claude Desktop's Cowork tab, plugin-installed
   subprocesses (and stdio MCP servers) run inside a sandbox with a
   URL allowlist that blocks external HTTP. Device-flow auth that
   needs to reach an OAuth provider hangs indefinitely on the network
   call. See `investing-toolkit/docs/mcp-setup.md`.
3. **No TTY**: Bash tool subprocesses run without a controlling
   terminal, so commands that detect TTY (curses UIs, password prompts,
   spinners, polling loops with Ctrl-C handling) silently degrade or
   block. Even if output were visible, stdin prompts cannot be
   answered.

The user's own terminal sidesteps all three: real TTY, no sandbox,
direct stdout visibility, working stdin.

## When This Convention Applies

A skill MUST use the user-terminal handoff pattern if its core action
involves any of:

- **Device-flow auth**: OAuth device codes, magic-link codes, OTP /
  TOTP entry that the user must read and type back into a browser or
  app
- **Interactive password / passphrase prompts**: `sudo`, GPG unlock,
  SSH key passphrase, encrypted-file decryption
- **Two-factor / step-up confirmation**: Touch ID / Face ID prompts,
  hardware security key tap, push notifications the user must approve
- **Long-running TUIs**: `htop`, `fzf` selection menus, `vim`-style
  full-screen editors invoked by a wrapping tool
- **Polling loops with progress that the user needs to see**: anything
  printing live progress where seeing it shapes the user's next action

A skill MAY use the Bash tool freely for:

- Idempotent file operations (`mkdir`, `chmod`, `mv`, `cp`)
- Read-only status checks (`status`, `list`, `--check` flags)
- Tool installation that's quiet on success (`brew install`, `npm
  install`, `pip install` once dependencies are resolved)
- Anything where stdout / stderr is purely informational and the user
  doesn't need to react in real time

## The Pattern

A skill that needs the handoff MUST structure its flow like this:

### Step 1 — Bash-run any non-interactive prerequisites

Tool install, directory creation, status pre-check, etc. These are
fine inside the Bash tool because they don't need TTY.

### Step 2 — Decide whether handoff is needed

Often the interactive step can be skipped (e.g. user is already
authed). Run a status check first; if state is already good, exit
early without bothering the user.

### Step 3 — Print the command for the user, do NOT Bash-run

Print a self-contained block the user can copy-paste into their own
terminal. Include:
- Exact command(s), with absolute paths (no shell variables that
  depend on Claude's environment)
- A one-paragraph description of what will happen and what the user
  needs to do (URL to open, code to type, prompt to answer, etc.)
- A clear stop signal — what reply ("done", "ok", "ready") the user
  should send back to Claude when finished

The skill MUST NOT wrap the printed command in a Bash tool call. It
prints the command as text and waits.

### Step 4 — Wait for the user's confirmation reply

Claude does nothing until the user replies. No background polling, no
optimistic Bash status checks, no time-based heuristics — just wait.

### Step 5 — Verify state and continue

After the user confirms, run a Bash status check to verify the
expected post-state (auth file exists, daemon running, etc.). If
verification fails, surface the failure and let the user retry Step 3
or pivot. If verification passes, proceed with the rest of the flow.

## Anti-Patterns

| Anti-pattern | Problem |
|---|---|
| `Bash(kobo_login.sh add)` then "Claude relays code to user" | Bash tool truncates the code mid-flight; user never sees it |
| Wrapping the printed command in a Bash call so it "looks like running" | Defeats the entire point — same truncation / sandbox issue |
| `Bash(read -p "code:")` to prompt the user | No stdin handoff; user can't type back |
| Polling status repeatedly via Bash hoping the user is done | Wastes turns; ask once and wait for reply |
| Skipping Step 2 and always sending the user to their terminal | Bad UX; verify first, ask only when needed |
| Skipping Step 5 verification | User says "done" but operation actually failed; downstream skills break with cryptic errors |

## Reference Implementation

`tsundoku/skills/kobo-auth/SKILL.md` Flow A is the canonical
implementation in this repo. Read it as a template when designing a
new TTY-bound skill flow.

## Cross-References

- For Claude Desktop Cowork sandbox limitations specifically (which
  motivated this convention's strict form), see
  `investing-toolkit/docs/mcp-setup.md` v1.16.1 retrospective
- For the broader Cowork-compatibility marking convention applied to
  affected plugins, see commit log for PR #154 (`docs: add Cowork
  sandbox compatibility notes to affected plugins`)
