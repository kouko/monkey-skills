#!/bin/bash
# verify-utility-sync.sh - Verify all _utility__ scripts are identical across skills
#
# Usage:
#   ./scripts/verify-utility-sync.sh
#
# Description:
#   Checks that all copies of _utility__*.sh files across skills are identical.
#   This ensures that replicated utility scripts stay in sync.
#
# Exit codes:
#   0 - All utility scripts are in sync
#   1 - Some utility scripts differ between skills

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$SCRIPT_DIR/../skills"

# ANSI colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=== Verifying _utility__ scripts consistency ==="
echo ""

EXIT_CODE=0

for name in naming ensure_jq download_jq ensure_ytdlp download_ytdlp build_ytdlp ensure_ffmpeg download_ffmpeg build_ffmpeg; do
    files=$(find "$SKILLS_DIR" -name "_utility__${name}.sh" 2>/dev/null | sort)

    if [ -z "$files" ]; then
        continue
    fi

    count=$(echo "$files" | wc -l | tr -d ' ')

    # Calculate unique hashes
    unique_hashes=$(echo "$files" | xargs md5 2>/dev/null | awk '{print $NF}' | sort -u | wc -l | tr -d ' ')

    if [ "$unique_hashes" = "1" ]; then
        echo -e "${GREEN}✅${NC} _utility__${name}.sh: ${count} copies, all identical"
    else
        echo -e "${RED}❌${NC} _utility__${name}.sh: ${count} copies, ${unique_hashes} different versions!"
        echo "   Files:"
        echo "$files" | while read -r f; do
            hash=$(md5 -q "$f" 2>/dev/null || md5sum "$f" 2>/dev/null | awk '{print $1}')
            echo "   - $(basename "$(dirname "$(dirname "$f")")"): $hash"
        done
        EXIT_CODE=1
    fi
done

echo ""

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}All utility scripts are in sync.${NC}"
else
    echo -e "${RED}Some utility scripts are out of sync!${NC}"
    echo -e "${YELLOW}Please ensure all copies are identical before committing.${NC}"
fi

exit $EXIT_CODE
