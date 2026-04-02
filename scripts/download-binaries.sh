#!/bin/bash
# download-binaries.sh - Download official release binaries for all skills
#
# This script finds and executes all download scripts across skills.
# It does NOT re-implement download logic - it reuses existing scripts.
#
# Supported tools:
#   - jq (from GitHub jqlang/jq)
#   - ffmpeg (from martin-riedl.de LGPL build)
#
# Skipped by default:
#   - yt-dlp: Use build-binaries.sh instead (smaller platform-specific binary)
#   - whisper models: Large files, use --include-models to include
#
# Usage:
#   ./scripts/download-binaries.sh [options]
#
# Options:
#   --dry-run         Show what would be executed without running
#   --include-ytdlp   Include yt-dlp downloads (use build-binaries.sh instead)
#   --include-models  Include whisper model downloads (large files)
#   --help            Show this help message

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$SCRIPT_DIR/../skills"

# Options
DRY_RUN=false
INCLUDE_YTDLP=false
INCLUDE_MODELS=false

# Parse arguments
for arg in "$@"; do
    case "$arg" in
        --dry-run)
            DRY_RUN=true
            ;;
        --include-ytdlp)
            INCLUDE_YTDLP=true
            ;;
        --include-models)
            INCLUDE_MODELS=true
            ;;
        --help|-h)
            head -26 "$0" | tail -24
            exit 0
            ;;
        *)
            echo "[ERROR] Unknown option: $arg" >&2
            echo "Use --help for usage information" >&2
            exit 1
            ;;
    esac
done

echo "[INFO] Scanning for download scripts in $SKILLS_DIR..." >&2

# Build exclusion patterns
exclude_patterns=()
[ "$INCLUDE_YTDLP" = false ] && exclude_patterns+=("*ytdlp*")
[ "$INCLUDE_MODELS" = false ] && exclude_patterns+=("*model*")

# Find all download scripts with exclusions
download_scripts=()
while IFS= read -r script; do
    script_name=$(basename "$script")
    skip=false

    for pattern in "${exclude_patterns[@]}"; do
        case "$script_name" in
            $pattern) skip=true; break ;;
        esac
    done

    [ "$skip" = false ] && download_scripts+=("$script")
done < <(find "$SKILLS_DIR" -type f -name "_*download*.sh" | sort)

echo "[INFO] Found ${#download_scripts[@]} download scripts" >&2
[ "$INCLUDE_YTDLP" = false ] && echo "[INFO] Skipping yt-dlp downloads (use build-binaries.sh or --include-ytdlp)" >&2
[ "$INCLUDE_MODELS" = false ] && echo "[INFO] Skipping model downloads (use --include-models to include)" >&2

for script in "${download_scripts[@]}"; do
    skill_name=$(echo "$script" | sed -E 's|.*/skills/([^/]+)/.*|\1|')
    script_name=$(basename "$script")

    echo "" >&2
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >&2
    echo "[INFO] Skill: $skill_name" >&2
    echo "[INFO] Script: $script_name" >&2
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >&2

    if [ "$DRY_RUN" = true ]; then
        echo "[DRY-RUN] Would execute: $script" >&2
    else
        if bash "$script"; then
            echo "[OK] $script_name completed" >&2
        else
            echo "[WARN] $script_name failed (continuing...)" >&2
        fi
    fi
done

echo "" >&2
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >&2
echo "[SUCCESS] All download scripts executed!" >&2

# Summary
echo "" >&2
echo "[INFO] Downloaded binaries:" >&2
find "$SKILLS_DIR"/*/bin -type f ! -name ".gitkeep" -exec ls -lh {} \; 2>/dev/null | awk '{print "  " $NF ": " $5}' >&2 || true
