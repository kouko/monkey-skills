#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# sync-upstream-skills.sh — vendor selected upstream gws skills into gws-toolkit
# -----------------------------------------------------------------------------
# Fetches SKILL.md for the 9 vendored upstream skills (gws-shared, gws-drive,
# gws-docs, gws-slides, gws-sheets, gws-gmail, gws-gmail-read, gws-calendar,
# gws-calendar-agenda) from googleworkspace/cli at the commit
# pinned in UPSTREAM_GWS_VERSION, writes them under gws-toolkit/skills/<name>/
# SKILL.md, and injects provenance metadata into the frontmatter.
#
# Idempotent: re-running with the same pin overwrites with identical content.
# Updating the pin in UPSTREAM_GWS_VERSION → re-run → review the diff.
#
# Apache-2.0 compliance:
#   - LICENSE-APACHE-2.0.txt is shipped at gws-toolkit root (this script
#     verifies its presence; does NOT regenerate it).
#   - Each vendored SKILL.md gets a metadata block in frontmatter declaring
#     vendored_from / vendored_at / upstream_license.
#   - No upstream NOTICE file exists in googleworkspace/cli @ v0.22.5 (verified
#     2026-05-04); if a future release adds one, this script must be extended.
#
# Usage:
#   bash gws-toolkit/scripts/sync-upstream-skills.sh
#   bash gws-toolkit/scripts/sync-upstream-skills.sh --dry-run
#
# Env:
#   GH                Path to `gh` CLI (default: gh in PATH)
#   GWS_TOOLKIT_ROOT  Override (default: directory containing this script's parent)
#
# Exit codes:
#   0   success
#   1   usage / pre-flight (missing gh / jq / pin file / LICENSE)
#   2   upstream fetch failed for any skill
#   3   pin file format invalid
# =============================================================================

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly TOOLKIT_ROOT="${GWS_TOOLKIT_ROOT:-$(cd "${SCRIPT_DIR}/.." && pwd)}"
readonly PIN_FILE="${TOOLKIT_ROOT}/UPSTREAM_GWS_VERSION"
readonly LICENSE_FILE="${TOOLKIT_ROOT}/LICENSE-APACHE-2.0.txt"
readonly SKILLS_DIR="${TOOLKIT_ROOT}/skills"
readonly GH="${GH:-gh}"

# Vendored skill names — keep in sync with UPSTREAM_GWS_VERSION's synced_skills list
readonly VENDORED_SKILLS=(gws-shared gws-drive gws-docs gws-slides gws-sheets gws-gmail gws-gmail-read gws-calendar gws-calendar-agenda)

DRY_RUN=0
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=1
fi

die() { printf 'sync-upstream-skills: %s\n' "$*" >&2; exit 1; }

# --- pre-flight -------------------------------------------------------------
command -v "${GH}" >/dev/null 2>&1 || die "gh CLI not found"
command -v jq >/dev/null 2>&1 || die "jq not found"
[[ -f "${PIN_FILE}" ]] || die "pin file missing: ${PIN_FILE}"
[[ -f "${LICENSE_FILE}" ]] || die "LICENSE-APACHE-2.0.txt missing at toolkit root: ${LICENSE_FILE}"

# --- parse pin --------------------------------------------------------------
RELEASE="$(awk -F': ' '/^gws_cli_release:/ {print $2}' "${PIN_FILE}" | tr -d '[:space:]')"
COMMIT="$(awk -F': ' '/^gws_cli_commit:/ {print $2}' "${PIN_FILE}" | tr -d '[:space:]')"
REPO="$(awk -F': ' '/^upstream_repo:/ {print $2}' "${PIN_FILE}" | tr -d '[:space:]')"
LICENSE_TAG="$(awk -F': ' '/^upstream_license:/ {print $2}' "${PIN_FILE}" | tr -d '[:space:]')"

[[ -n "${RELEASE}" && -n "${COMMIT}" && -n "${REPO}" && -n "${LICENSE_TAG}" ]] \
  || { printf 'pin file format invalid (need gws_cli_release / gws_cli_commit / upstream_repo / upstream_license)\n' >&2; exit 3; }

printf '[sync] upstream pin: %s @ %s (%s)\n' "${RELEASE}" "${COMMIT}" "${REPO}" >&2

# --- inject provenance into vendored SKILL.md frontmatter -------------------
# Adds a `metadata.vendored_from` / `vendored_at` / `upstream_license` block
# right after the existing `metadata:` line, or appends one if upstream's file
# has no metadata block.
inject_provenance() {
  local skill="$1"
  local raw_file="$2"
  local out_file="$3"
  local today
  today="$(date -u +%Y-%m-%d)"

  # If the file already has a `metadata:` block, append vendored_* keys under it.
  # Otherwise (e.g. user-edited prior version with no metadata), insert one
  # before the closing `---`.
  if grep -qE '^metadata:' "${raw_file}"; then
    awk -v rel="${RELEASE}" -v sha="${COMMIT}" -v repo="${REPO}" -v lic="${LICENSE_TAG}" -v today="${today}" '
      BEGIN { injected = 0 }
      /^metadata:/ && !injected {
        print
        print "  vendored_from: \"" repo "@" sha "\""
        print "  vendored_release: \"" rel "\""
        print "  vendored_at: \"" today "\""
        print "  upstream_license: \"" lic "\""
        injected = 1
        next
      }
      { print }
    ' "${raw_file}" > "${out_file}"
  else
    # No metadata block — insert one before the closing --- of frontmatter
    awk -v rel="${RELEASE}" -v sha="${COMMIT}" -v repo="${REPO}" -v lic="${LICENSE_TAG}" -v today="${today}" '
      BEGIN { in_frontmatter = 0; injected = 0 }
      /^---$/ {
        if (in_frontmatter == 0) { in_frontmatter = 1; print; next }
        if (in_frontmatter == 1 && injected == 0) {
          print "metadata:"
          print "  vendored_from: \"" repo "@" sha "\""
          print "  vendored_release: \"" rel "\""
          print "  vendored_at: \"" today "\""
          print "  upstream_license: \"" lic "\""
          injected = 1
        }
        in_frontmatter = 2
        print
        next
      }
      { print }
    ' "${raw_file}" > "${out_file}"
  fi
}

# --- per-skill fetch loop ---------------------------------------------------
TMP="$(mktemp -d -t sync-upstream.XXXXXX)"
trap 'rm -rf "${TMP}"' EXIT

failed=0
for skill in "${VENDORED_SKILLS[@]}"; do
  upstream_path="skills/${skill}/SKILL.md"
  raw_file="${TMP}/${skill}.SKILL.md.raw"
  patched_file="${TMP}/${skill}.SKILL.md.patched"
  target_dir="${SKILLS_DIR}/${skill}"
  target_file="${target_dir}/SKILL.md"

  printf '[sync] %s ... ' "${skill}" >&2
  if ! "${GH}" api "repos/${REPO}/contents/${upstream_path}?ref=${COMMIT}" --jq '.content' 2>/dev/null \
    | base64 -d > "${raw_file}"; then
    printf 'FETCH FAILED\n' >&2
    failed=$((failed + 1))
    continue
  fi
  [[ -s "${raw_file}" ]] || { printf 'EMPTY\n' >&2; failed=$((failed + 1)); continue; }

  inject_provenance "${skill}" "${raw_file}" "${patched_file}"

  if (( DRY_RUN == 1 )); then
    printf 'OK (dry-run; would write %s)\n' "${target_file}" >&2
    continue
  fi

  mkdir -p "${target_dir}"
  cp "${patched_file}" "${target_file}"
  printf 'OK\n' >&2
done

if (( failed > 0 )); then
  printf '[sync] %d skill(s) failed to fetch\n' "${failed}" >&2
  exit 2
fi

printf '[sync] all %d skill(s) synced\n' "${#VENDORED_SKILLS[@]}" >&2
if (( DRY_RUN == 0 )); then
  printf '[sync] review changes: git diff -- gws-toolkit/skills/gws-{shared,drive,docs,slides,sheets,gmail,gmail-read,calendar,calendar-agenda}/\n' >&2
fi
