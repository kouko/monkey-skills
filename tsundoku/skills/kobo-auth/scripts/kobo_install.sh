#!/usr/bin/env bash
# kobo_install.sh — download the kobodl macOS binary if not present.
#
# Idempotent. Does NOT touch credentials. Auth lives in kobo_login.sh.
#
# Exit codes:
#   0  binary ready (either already present or freshly downloaded)
#   1  download failure
#   2  argument error

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./tsundoku_paths.sh
source "$SCRIPT_DIR/tsundoku_paths.sh"

URL="https://github.com/subdavis/kobo-book-downloader/releases/latest/download/kobodl-macos"
FORCE=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --force) FORCE=true; shift ;;
        --url)   URL="$2"; shift 2 ;;
        -h|--help)
            grep '^#' "$0" | sed 's/^# \{0,1\}//'
            exit 0
            ;;
        *) echo "kobodl_install: unknown arg: $1" >&2; exit 2 ;;
    esac
done

tsundoku_ensure_dirs

if [[ -x "$TSUNDOKU_KOBO_BINARY" && "$FORCE" != true ]]; then
    echo "[install] kobodl binary already present: $TSUNDOKU_KOBO_BINARY" >&2
    "$TSUNDOKU_KOBO_BINARY" --version 2>/dev/null | head -n 1 >&2 || true
    exit 0
fi

echo "[install] downloading kobodl from $URL" >&2
tmp_path="$TSUNDOKU_KOBO_BINARY.partial"
trap 'rm -f "$tmp_path"' EXIT

if ! curl --fail --location --output "$tmp_path" "$URL"; then
    echo "[install] download failed" >&2
    exit 1
fi

# Sanity-check size — under 1 MB usually means we caught a 404 HTML page
size_bytes=$(stat -f%z "$tmp_path" 2>/dev/null || stat -c%s "$tmp_path" 2>/dev/null || echo 0)
if [[ "$size_bytes" -lt 1000000 ]]; then
    echo "[install] downloaded file is suspiciously small ($size_bytes bytes); aborting" >&2
    exit 1
fi

mv "$tmp_path" "$TSUNDOKU_KOBO_BINARY"
chmod +x "$TSUNDOKU_KOBO_BINARY"
xattr -d com.apple.quarantine "$TSUNDOKU_KOBO_BINARY" 2>/dev/null || true

echo "[install] kobodl binary installed: $TSUNDOKU_KOBO_BINARY" >&2
"$TSUNDOKU_KOBO_BINARY" --version 2>/dev/null | head -n 1 >&2 || true
