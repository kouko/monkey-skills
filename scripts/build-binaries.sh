#!/bin/bash
# build-binaries.sh - Build platform-specific binaries for all skills
#
# This script finds and executes all build scripts across skills.
# It builds binaries from source using PyInstaller, CMake, etc.
# After building, it copies the binary to all skills that need it.
#
# Supported tools:
#   - yt-dlp (PyInstaller build, ~15MB platform-specific)
#   - ffmpeg (source build with LGPL compliance)
#   - whisper-cli (CMake build with Metal support on macOS)
#
# Prerequisites:
#   - Python 3.8+ with pip (for yt-dlp)
#   - CMake, make, git (for whisper)
#   - Xcode CLT on macOS / build-essential on Linux
#
# Usage:
#   ./scripts/build-binaries.sh [options]
#
# Options:
#   --dry-run          Show what would be executed without running
#   --only=TOOL        Build only specified tool (ytdlp, ffmpeg, whisper)
#   --skip=TOOL        Skip specified tool
#   --help             Show this help message
#
# Examples:
#   ./scripts/build-binaries.sh                    # Build all
#   ./scripts/build-binaries.sh --only=ytdlp      # Build only yt-dlp
#   ./scripts/build-binaries.sh --skip=whisper    # Skip whisper build

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$SCRIPT_DIR/../skills"

# Platform detection
get_platform_suffix() {
    local os arch
    os="$(uname -s)"
    arch="$(uname -m)"

    case "$os" in
        Darwin)               os="darwin" ;;
        Linux)                os="linux" ;;
        MINGW*|CYGWIN*|MSYS*) os="windows" ;;
        *)                    os="$(echo "$os" | tr '[:upper:]' '[:lower:]')" ;;
    esac

    case "$arch" in
        x86_64)        arch="amd64" ;;
        arm64|aarch64) arch="arm64" ;;
        i686|i386)     arch="386" ;;
    esac

    echo "${os}-${arch}"
}

PLATFORM_SUFFIX="$(get_platform_suffix)"

# Options
DRY_RUN=false
ONLY_TOOL=""
SKIP_TOOLS=()

# Parse arguments
for arg in "$@"; do
    case "$arg" in
        --dry-run)
            DRY_RUN=true
            ;;
        --only=*)
            ONLY_TOOL="${arg#--only=}"
            ;;
        --skip=*)
            SKIP_TOOLS+=("${arg#--skip=}")
            ;;
        --help|-h)
            head -32 "$0" | tail -30
            exit 0
            ;;
        *)
            echo "[ERROR] Unknown option: $arg" >&2
            echo "Use --help for usage information" >&2
            exit 1
            ;;
    esac
done

# Check if tool should be skipped
should_skip() {
    local script_name="$1"

    # Check --only filter
    if [ -n "$ONLY_TOOL" ]; then
        case "$script_name" in
            *ytdlp*|*yt-dlp*|*yt_dlp*)
                [ "$ONLY_TOOL" != "ytdlp" ] && return 0
                ;;
            *ffmpeg*)
                [ "$ONLY_TOOL" != "ffmpeg" ] && return 0
                ;;
            *whisper*)
                [ "$ONLY_TOOL" != "whisper" ] && return 0
                ;;
        esac
    fi

    # Check --skip filter
    for skip in "${SKIP_TOOLS[@]}"; do
        case "$script_name" in
            *ytdlp*|*yt-dlp*|*yt_dlp*)
                [ "$skip" = "ytdlp" ] && return 0
                ;;
            *ffmpeg*)
                [ "$skip" = "ffmpeg" ] && return 0
                ;;
            *whisper*)
                [ "$skip" = "whisper" ] && return 0
                ;;
        esac
    done

    return 1
}

# Get tool name from script name
get_tool_name() {
    local script_name="$1"
    case "$script_name" in
        *ytdlp*|*yt-dlp*|*yt_dlp*) echo "yt-dlp" ;;
        *ffmpeg*) echo "ffmpeg" ;;
        *whisper*) echo "whisper" ;;
        *) echo "unknown" ;;
    esac
}

# Get binary filename for a tool
get_binary_name() {
    local tool="$1"
    case "$tool" in
        yt-dlp)  echo "yt-dlp-${PLATFORM_SUFFIX}" ;;
        ffmpeg)  echo "ffmpeg-${PLATFORM_SUFFIX}" ;;
        whisper) echo "whisper-cli-${PLATFORM_SUFFIX}" ;;
    esac
}

# Find all skills that have build script for a tool
find_skills_for_tool() {
    local tool="$1"
    local pattern
    case "$tool" in
        yt-dlp)  pattern="*ytdlp*.sh" ;;
        ffmpeg)  pattern="*ffmpeg*.sh" ;;
        whisper) pattern="*whisper*.sh" ;;
    esac
    find "$SKILLS_DIR" -type f -name "_*build*" -name "$pattern" | \
        sed -E 's|.*/skills/([^/]+)/.*|\1|' | sort -u
}

# Copy binary to all skills that need it
copy_to_all_skills() {
    local tool="$1"
    local source_skill="$2"
    local binary_name
    binary_name=$(get_binary_name "$tool")

    local source_path="$SKILLS_DIR/$source_skill/bin/$binary_name"

    if [ ! -f "$source_path" ]; then
        echo "[WARN] Binary not found: $source_path" >&2
        return 1
    fi

    echo "[INFO] Copying $binary_name to other skills..." >&2

    local skills
    skills=$(find_skills_for_tool "$tool")

    for skill in $skills; do
        if [ "$skill" = "$source_skill" ]; then
            continue
        fi

        local target_dir="$SKILLS_DIR/$skill/bin"
        local target_path="$target_dir/$binary_name"

        if [ "$DRY_RUN" = true ]; then
            echo "[DRY-RUN] Would copy to: $target_path" >&2
        else
            mkdir -p "$target_dir"
            cp "$source_path" "$target_path"
            chmod +x "$target_path"
            echo "  → $skill/bin/$binary_name" >&2
        fi
    done
}

echo "[INFO] Scanning for build scripts in $SKILLS_DIR..." >&2
echo "[INFO] Platform: $PLATFORM_SUFFIX" >&2

# Find all build scripts
build_scripts=()
while IFS= read -r script; do
    build_scripts+=("$script")
done < <(find "$SKILLS_DIR" -type f -name "_*build*.sh" | sort)

echo "[INFO] Found ${#build_scripts[@]} build scripts" >&2

# Track which tools we've already built (avoid duplicates)
# Using simple variables for bash 3.x compatibility
built_ytdlp=""
built_ffmpeg=""
built_whisper=""

is_tool_built() {
    local tool="$1"
    case "$tool" in
        yt-dlp)  [ "$built_ytdlp" = "1" ] ;;
        ffmpeg)  [ "$built_ffmpeg" = "1" ] ;;
        whisper) [ "$built_whisper" = "1" ] ;;
        *)       return 1 ;;
    esac
}

mark_tool_built() {
    local tool="$1"
    case "$tool" in
        yt-dlp)  built_ytdlp="1" ;;
        ffmpeg)  built_ffmpeg="1" ;;
        whisper) built_whisper="1" ;;
    esac
}

# Count stats
total=0
skipped=0
success=0
failed=0

for script in "${build_scripts[@]}"; do
    skill_name=$(echo "$script" | sed -E 's|.*/skills/([^/]+)/.*|\1|')
    script_name=$(basename "$script")
    tool_name=$(get_tool_name "$script_name")

    # Skip if filtered out
    if should_skip "$script_name"; then
        ((skipped++))
        continue
    fi

    # Skip if already built this tool (only build once per tool type)
    if is_tool_built "$tool_name"; then
        echo "[INFO] Skipping $script_name (already built $tool_name)" >&2
        ((skipped++))
        continue
    fi

    ((total++))

    echo "" >&2
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >&2
    echo "[INFO] Tool: $tool_name" >&2
    echo "[INFO] Skill: $skill_name" >&2
    echo "[INFO] Script: $script_name" >&2
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >&2

    if [ "$DRY_RUN" = true ]; then
        echo "[DRY-RUN] Would execute: $script" >&2
        echo "[DRY-RUN] Would copy to other skills" >&2
        mark_tool_built "$tool_name"
    else
        if bash "$script"; then
            echo "[OK] $tool_name build completed" >&2
            mark_tool_built "$tool_name"
            ((success++))

            # Copy to all other skills that need this tool
            copy_to_all_skills "$tool_name" "$skill_name"
        else
            echo "[WARN] $tool_name build failed" >&2
            ((failed++))
        fi
    fi
done

echo "" >&2
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >&2

if [ "$DRY_RUN" = true ]; then
    echo "[DRY-RUN] Would build $total tools (skipped $skipped)" >&2
else
    echo "[SUMMARY] Built: $success, Failed: $failed, Skipped: $skipped" >&2
fi

# Summary of built binaries
echo "" >&2
echo "[INFO] Platform-specific binaries:" >&2

# Get platform suffix
os="$(uname -s | tr '[:upper:]' '[:lower:]')"
[ "$os" = "darwin" ] && os="darwin"
arch="$(uname -m)"
case "$arch" in
    x86_64) arch="amd64" ;;
    arm64|aarch64) arch="arm64" ;;
esac
platform="${os}-${arch}"

# List platform-specific binaries
find "$SKILLS_DIR"/*/bin -type f -name "*${platform}*" -exec ls -lh {} \; 2>/dev/null | \
    awk '{print "  " $NF ": " $5}' >&2 || true

exit $failed
