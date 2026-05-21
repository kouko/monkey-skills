#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# calendar-confirm-insert.sh — auto-tier confirm gate for Calendar event insert
# -----------------------------------------------------------------------------
# Wraps `gws calendar events insert` behind a tiered confirmation gate.
# Default mode is dry-run: every invocation without --confirm prints the
# planned event metadata and exits 0 without calling the API. Claude must
# explicitly re-run with --confirm to execute.
#
# Why this exists (PRODUCT-SPEC §6.3.x write-asymmetry):
# Creating a Calendar event with attendees sends invitation emails to those
# attendees — a side-effect that is visible to people other than the caller
# and partially irreversible (the email is sent immediately; cancelling the
# event afterward sends a second "cancelled" notification). The wrapper
# distinguishes:
#   L1 — Solo event (no attendees). Reversible: delete the event and only
#        the caller sees the change. Still --confirm-gated to preserve the
#        cross-wrapper invariant {dry-run preview} → {--confirm execute}.
#   L2 — Attendee event (attendees.length > 0). Email invites go out the
#        moment the API call succeeds. dry-run JSON surfaces
#        `visibility_warning: "sends invite emails to N attendees"` so
#        Claude can show the user the blast radius before --confirm.
#
# Usage:
#   calendar-confirm-insert.sh --summary X --start S --end E [flags]   # dry-run
#   calendar-confirm-insert.sh --summary X --start S --end E [flags] --confirm
#
# Required flags:
#   --summary <TEXT>       Event title
#   --start <RFC3339>      Start time (e.g. 2026-06-01T10:00:00Z)
#   --end <RFC3339>        End time
#
# Optional flags:
#   --attendees <CSV>      Comma-joined emails (triggers L2 tier)
#   --calendar <ID>        Calendar ID (default: primary)
#   --location <TEXT>      Event location
#   --description <TEXT>   Event description / body
#   --confirm              Execute (otherwise dry-run)
#
# Stdout: JSON
#   dry-run:   {action:"insert", dry_run:true, tier:"L1"|"L2",
#              metadata:{summary, start, end, attendees, calendar_id,
#                        location, description},
#              [visibility_warning:"sends invite emails to N attendees"],
#              warnings:[...], next:"<re-run cmd>"}
#   executed:  {action:"inserted", dry_run:false, tier, event_id,
#              html_link, summary}
# Stderr: human-readable progress + warnings.
#
# Exit codes (mirror safe-delete.sh):
#   0   success (dry-run preview, or executed insert)
#   1   usage / pre-flight error
#   2   calendar not found / 404 (passed through from gws-wrap)
#   3   confirmation gate failed (reserved; this wrapper currently has no
#       typed-name gate — L2 only requires --confirm)
#   10  auth / scope error (passed through from gws-wrap)
#   11  rate limit
#   12  generic API error
# =============================================================================

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly GWS_WRAP="${SCRIPT_DIR}/gws-wrap.sh"

die() { printf 'calendar-confirm-insert: %s\n' "$*" >&2; exit "${2:-1}"; }
usage() {
  sed -n '5,60p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
  exit 1
}

# --- arg parse -------------------------------------------------------------
SUMMARY=""
START=""
END=""
ATTENDEES_CSV=""
CALENDAR_ID="primary"
LOCATION=""
DESCRIPTION=""
CONFIRM=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --summary)       SUMMARY="${2:-}";       shift 2 ;;
    --summary=*)     SUMMARY="${1#*=}";      shift ;;
    --start)         START="${2:-}";         shift 2 ;;
    --start=*)       START="${1#*=}";        shift ;;
    --end)           END="${2:-}";           shift 2 ;;
    --end=*)         END="${1#*=}";          shift ;;
    --attendees)     ATTENDEES_CSV="${2:-}"; shift 2 ;;
    --attendees=*)   ATTENDEES_CSV="${1#*=}"; shift ;;
    --calendar)      CALENDAR_ID="${2:-}";   shift 2 ;;
    --calendar=*)    CALENDAR_ID="${1#*=}";  shift ;;
    --location)      LOCATION="${2:-}";      shift 2 ;;
    --location=*)    LOCATION="${1#*=}";     shift ;;
    --description)   DESCRIPTION="${2:-}";   shift 2 ;;
    --description=*) DESCRIPTION="${1#*=}";  shift ;;
    --confirm)       CONFIRM=1;              shift ;;
    -h|--help)       usage ;;
    -*)              die "unknown flag: $1" ;;
    *)               die "unexpected positional: $1" ;;
  esac
done

[[ -n "${SUMMARY}" ]] || die "missing required --summary"
[[ -n "${START}"   ]] || die "missing required --start"
[[ -n "${END}"     ]] || die "missing required --end"
[[ -x "${GWS_WRAP}" ]] || die "gws-wrap.sh not executable at ${GWS_WRAP}"
command -v jq >/dev/null 2>&1 || die "jq not found"

# --- normalise attendees ---------------------------------------------------
# CSV → JSON array of strings (trimmed; empty entries dropped).
# jq -R on an empty stdin produces empty output, which breaks --argjson
# downstream; short-circuit to "[]" when the CSV is empty.
if [[ -z "${ATTENDEES_CSV}" ]]; then
  attendees_json="[]"
else
  attendees_json="$(
    printf '%s' "${ATTENDEES_CSV}" \
      | jq -R -c 'split(",") | map(gsub("^\\s+|\\s+$"; "")) | map(select(length > 0))'
  )"
fi
attendee_count="$(printf '%s' "${attendees_json}" | jq -r 'length')"

if (( attendee_count > 0 )); then
  TIER="L2"
else
  TIER="L1"
fi

# --- compose event-body JSON (used in both dry-run preview & execute) ------
# Per Calendar API events#resource: attendees is an array of {email:...}
# objects, not bare strings. start/end are {dateTime: RFC3339, ...}.
event_body_json="$(jq -nc \
  --arg summary "${SUMMARY}" \
  --arg start "${START}" \
  --arg end "${END}" \
  --argjson attendees "${attendees_json}" \
  --arg location "${LOCATION}" \
  --arg description "${DESCRIPTION}" \
  '{
    summary: $summary,
    start: { dateTime: $start },
    end:   { dateTime: $end },
    attendees: ($attendees | map({email: .})),
  }
  + (if $location    == "" then {} else {location: $location} end)
  + (if $description == "" then {} else {description: $description} end)
  ')"

# --- compose metadata for dry-run preview ----------------------------------
# Different shape than the API body: preserves CSV-ordered attendee list as
# plain strings (easier for Claude to render) and includes calendar_id.
metadata_json="$(jq -nc \
  --arg summary "${SUMMARY}" \
  --arg start "${START}" \
  --arg end "${END}" \
  --argjson attendees "${attendees_json}" \
  --arg calendar_id "${CALENDAR_ID}" \
  --arg location "${LOCATION}" \
  --arg description "${DESCRIPTION}" \
  '{
    summary: $summary,
    start: $start,
    end: $end,
    attendees: $attendees,
    calendar_id: $calendar_id,
    location: $location,
    description: $description
  }')"

# --- warnings --------------------------------------------------------------
if [[ "${TIER}" == "L2" ]]; then
  warnings_json="$(jq -nc --argjson n "${attendee_count}" \
    '[("L2: creating an event with " + ($n|tostring) + " attendee(s) sends invitation emails on success; cancelling later sends a second \"cancelled\" notification")]')"
else
  warnings_json="[]"
fi

# --- dry-run path ----------------------------------------------------------
if (( CONFIRM == 0 )); then
  # Build re-run command. Quote attendees to preserve CSV.
  if [[ -n "${ATTENDEES_CSV}" ]]; then
    next_cmd="bash calendar-confirm-insert.sh --summary \"${SUMMARY}\" --start \"${START}\" --end \"${END}\" --attendees \"${ATTENDEES_CSV}\" --confirm"
  else
    next_cmd="bash calendar-confirm-insert.sh --summary \"${SUMMARY}\" --start \"${START}\" --end \"${END}\" --confirm"
  fi

  if [[ "${TIER}" == "L2" ]]; then
    jq -nc \
      --arg action "insert" \
      --arg tier "${TIER}" \
      --argjson metadata "${metadata_json}" \
      --argjson n "${attendee_count}" \
      --argjson warnings "${warnings_json}" \
      --arg next "${next_cmd}" \
      '{
        action: $action,
        dry_run: true,
        tier: $tier,
        metadata: $metadata,
        visibility_warning: ("sends invite emails to " + ($n|tostring) + " attendees"),
        warnings: $warnings,
        next: $next
      }'
  else
    jq -nc \
      --arg action "insert" \
      --arg tier "${TIER}" \
      --argjson metadata "${metadata_json}" \
      --argjson warnings "${warnings_json}" \
      --arg next "${next_cmd}" \
      '{
        action: $action,
        dry_run: true,
        tier: $tier,
        metadata: $metadata,
        warnings: $warnings,
        next: $next
      }'
  fi
  exit 0
fi

# --- execute ---------------------------------------------------------------
printf '[calendar-confirm-insert] INSERT %s event "%s" (%s → %s) on calendar=%s\n' \
  "${TIER}" "${SUMMARY}" "${START}" "${END}" "${CALENDAR_ID}" >&2

params_json="$(jq -nc --arg cal "${CALENDAR_ID}" '{calendarId: $cal}')"

response_json="$(
  "${GWS_WRAP}" calendar events insert \
    --params "${params_json}" \
    --json "${event_body_json}"
)"

event_id="$(printf '%s' "${response_json}" | jq -r '.id // empty')"
html_link="$(printf '%s' "${response_json}" | jq -r '.htmlLink // empty')"

jq -nc \
  --arg tier "${TIER}" \
  --arg event_id "${event_id}" \
  --arg html_link "${html_link}" \
  --arg summary "${SUMMARY}" \
  '{
    action: "inserted",
    dry_run: false,
    tier: $tier,
    event_id: $event_id,
    html_link: $html_link,
    summary: $summary
  }'
