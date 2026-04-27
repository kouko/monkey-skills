#!/usr/bin/env bash
# kobo_login.sh — manage Kobo authentication for the toolkit.
#
# Subcommands:
#   status                check auth state, print user list (default if no args)
#   add                   start interactive activation flow (`kobodl user add`)
#   remove EMAIL          remove a user from the config
#   import-from PATH      copy an existing kobodl.json into TSUNDOKU_ROOT
#   path                  print the canonical TSUNDOKU_KOBO_CONFIG path and exit
#
# Flags:
#   -h, --help            show this header
#
# Exit codes:
#   0  ok / already authed
#   1  not authed (status), or operation failed
#   2  argument error
#   3  prerequisite missing (binary not installed)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./tsundoku_paths.sh
source "$SCRIPT_DIR/../../../lib/tsundoku_paths.sh"

ensure_binary() {
    if [[ ! -x "$TSUNDOKU_KOBO_BINARY" ]]; then
        cat >&2 <<EOF
[login] kobodl binary not installed at:
        $TSUNDOKU_KOBO_BINARY
        Run kobo_install.sh first.
EOF
        exit 3
    fi
}

ensure_config_dir() {
    mkdir -p "$TSUNDOKU_ROOT"
    chmod 700 "$TSUNDOKU_ROOT"
}

secure_config_file() {
    if [[ -f "$TSUNDOKU_KOBO_CONFIG" ]]; then
        chmod 600 "$TSUNDOKU_KOBO_CONFIG"
    fi
}

cmd_status() {
    ensure_binary
    if [[ ! -f "$TSUNDOKU_KOBO_CONFIG" ]]; then
        echo "[status] no config at $TSUNDOKU_KOBO_CONFIG — not authed" >&2
        return 1
    fi
    if "$TSUNDOKU_KOBO_BINARY" --config "$TSUNDOKU_KOBO_CONFIG" user list 2>/dev/null | grep -q "@"; then
        "$TSUNDOKU_KOBO_BINARY" --config "$TSUNDOKU_KOBO_CONFIG" user list
        return 0
    fi
    echo "[status] config exists but contains no logged-in user" >&2
    return 1
}

cmd_add() {
    ensure_binary
    ensure_config_dir
    cat >&2 <<EOF
[login] starting activation flow.
        kobodl will print a 6-digit code. When you see it:
          1. open https://www.kobo.com/activate in a browser
          2. sign in to your Kobo account
          3. enter the 6-digit code shown below
        kobodl polls in the background and exits automatically once you activate.
        DO NOT cancel this command — it can take up to 60 seconds for the polling
        to register.
EOF
    "$TSUNDOKU_KOBO_BINARY" --config "$TSUNDOKU_KOBO_CONFIG" user add
    secure_config_file
    if "$TSUNDOKU_KOBO_BINARY" --config "$TSUNDOKU_KOBO_CONFIG" user list 2>/dev/null | grep -q "@"; then
        echo "[login] success — auth saved to $TSUNDOKU_KOBO_CONFIG (mode 600)" >&2
        return 0
    fi
    echo "[login] activation did not complete — re-run when ready" >&2
    return 1
}

cmd_remove() {
    ensure_binary
    local target="${1:-}"
    if [[ -z "$target" ]]; then
        echo "[remove] usage: kobo_login.sh remove <email>" >&2
        return 2
    fi
    "$TSUNDOKU_KOBO_BINARY" --config "$TSUNDOKU_KOBO_CONFIG" user rm "$target"
    secure_config_file
}

cmd_import_from() {
    local src="${1:-}"
    if [[ -z "$src" ]]; then
        echo "[import] usage: kobo_login.sh import-from <path-to-kobodl.json>" >&2
        return 2
    fi
    if [[ ! -f "$src" ]]; then
        echo "[import] source file not found: $src" >&2
        return 1
    fi
    if [[ -f "$TSUNDOKU_KOBO_CONFIG" ]]; then
        local backup="$TSUNDOKU_KOBO_CONFIG.bak.$(date +%Y%m%d-%H%M%S)"
        cp "$TSUNDOKU_KOBO_CONFIG" "$backup"
        chmod 600 "$backup"
        echo "[import] existing config backed up to $backup" >&2
    fi
    ensure_config_dir
    cp "$src" "$TSUNDOKU_KOBO_CONFIG"
    secure_config_file
    echo "[import] copied $src → $TSUNDOKU_KOBO_CONFIG (mode 600)" >&2
    if [[ -x "$TSUNDOKU_KOBO_BINARY" ]]; then
        if cmd_status >/dev/null 2>&1; then
            echo "[import] verified — auth ready" >&2
        else
            echo "[import] note: imported file did not pass verification — re-run 'kobo_login.sh add'" >&2
            return 1
        fi
    else
        echo "[import] note: binary not yet installed — run kobo_install.sh then kobo_login.sh status to verify" >&2
    fi
}

cmd_path() {
    echo "$TSUNDOKU_KOBO_CONFIG"
}

# Dispatch
case "${1:-status}" in
    status)        shift || true; cmd_status "$@" ;;
    add|login)     shift; cmd_add "$@" ;;
    remove|rm)     shift; cmd_remove "$@" ;;
    import-from)   shift; cmd_import_from "$@" ;;
    path)          cmd_path ;;
    -h|--help)     grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "kobodl_login: unknown subcommand: $1" >&2; exit 2 ;;
esac
