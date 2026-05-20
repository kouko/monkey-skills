#!/usr/bin/env bash
# =============================================================================
# tty-guard.sh — shared controlling-terminal guard for salesforce-toolkit
# -----------------------------------------------------------------------------
# Provides `require_tty`, a shell function other scripts source to enforce that
# they are invoked from a real interactive terminal (Terminal.app / iTerm2 /
# VSCode integrated terminal) rather than a piped stdin or a background Bash
# invocation by Claude Code.
#
# Why this guard exists:
#   The auto-setup.sh flow (Part 2 of this plugin) walks the user through
#   guided UI sub-steps that open browser tabs and `read` from the controlling
#   terminal. Without a TTY, the script either silently hangs or spams the
#   user with browser tabs before the read fails — fail-loud at the start is
#   strictly better. Pattern lifted from gws-toolkit/scripts/gws/auto-setup.sh
#   `have_working_tty` + pre-flight check in main().
#
# Contract:
#   - Designed to be `source`d:  `source "${CLAUDE_PLUGIN_ROOT}/scripts/common/tty-guard.sh"`
#   - Exposes one public function: `require_tty`
#   - `require_tty` returns 0 when stdin is a TTY; otherwise prints
#     `auto-setup.sh requires a controlling terminal` to stderr and `exit 10`
#     (exit-10 == auth/interaction error, mirrors gws-toolkit convention).
#
# Why `tty -s` (not `[ -t 0 ]`):
#   Both work for the basic case. `tty -s` is POSIX-standard and matches the
#   plan's "tty -s 檢查" wording verbatim. `[ -t 0 ]` is a bash builtin and
#   would be equally valid; `tty -s` was chosen for portability + spec match.
#
# Not done in this helper (intentional):
#   - No /dev/tty open-write probe (auto-setup.sh's stricter check) — that
#     belongs in the caller if it needs to read from /dev/tty. `require_tty`
#     only verifies stdin is a terminal; that's sufficient for the scripts
#     this plugin ships in v0.1.0.
#   - No die_json wrapper — this helper has no JSON contract; plain stderr
#     line + exit 10 is enough. Callers that emit JSON results wrap this in
#     their own error funnel.
# =============================================================================

# Public: ensure caller is running with a controlling terminal.
# Returns 0 on success; exits 10 on failure (does not return).
require_tty() {
  if tty -s; then
    return 0
  fi
  printf '%s\n' "auto-setup.sh requires a controlling terminal" >&2
  exit 10
}
