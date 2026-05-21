#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# gmail-confirm-send.sh — L3 typed recipient + subject gate for Gmail send
# -----------------------------------------------------------------------------
# Wraps `gws gmail +send` (which handles RFC 5322 + MIME + base64 encoding
# upstream) behind a single-tier confirmation gate. Default mode is dry-run:
# every invocation without BOTH typed-confirmation flags prints a metadata
# preview and exits 0 without sending.
#
# Why L3 (always, not opt-in like safe-delete.sh):
# Sending an email is irreversible once the recipient's MTA accepts it
# (~30 seconds after pressing send for Gmail's "Undo Send" window). There
# is no Trash equivalent, no provenance tag we could check to ease the
# friction. Every send is the equivalent of a permanent delete on a file
# the toolkit did not create. So every send requires L3 typed confirmation
# of BOTH the recipient list and the subject line — the two fields most
# likely to be wrong if Claude misroutes.
#
# Usage:
#   gmail-confirm-send.sh --to <emails> --subject <s> [--body <text>]    # dry-run
#   gmail-confirm-send.sh --to <emails> --subject <s> --body-file <path> # dry-run
#   printf '<body>' | gmail-confirm-send.sh --to <emails> --subject <s>  # dry-run via stdin
#   gmail-confirm-send.sh --to <emails> --subject <s> --body <text> \
#       --i-confirm-recipients="<exact-comma-joined-recipients>" \
#       --i-confirm-subject="<exact-subject>"                            # execute
#
# Args:
#   --to <s>            Comma-joined recipient(s) (required)
#   --subject <s>       Subject line (required)
#   --body <s>          Plain text body (lowest priority)
#   --body-file <path>  Read body from file (highest priority)
#   --cc <s>            Comma-joined CC recipient(s)
#   --bcc <s>           Comma-joined BCC recipient(s)
#   --from <s>          Send-as alias (omit for account default)
#   --html              Treat body as HTML
#   --attach <path>     Attachment (repeatable)
#   --i-confirm-recipients=<s>
#                       Typed confirmation of recipient list. MUST equal
#                       the value passed to --to verbatim.
#   --i-confirm-subject=<s>
#                       Typed confirmation of subject. MUST equal --subject
#                       verbatim.
#   -h | --help         Print this docstring.
#
# Body input priority (first non-empty wins):
#   1. --body-file <path>  (if file exists and is non-empty)
#   2. stdin               (if not a terminal and bytes are available)
#   3. --body <text>
#
# Stdout: JSON
#   dry-run:   {action:"send", dry_run:true,
#               metadata:{to, cc, bcc, subject, body_preview, attachments,
#                         from, html},
#               warnings:["L3: send is irreversible after Gmail's ~30s undo window"],
#               next:"<re-run cmd>"}
#   executed:  passthrough from `gws gmail +send` (response JSON or progress)
# Stderr: human-readable progress + warnings.
#
# Exit codes (mirror safe-delete.sh:48-54):
#   0   success (dry-run preview, or executed send)
#   1   usage / pre-flight error
#   2   not-found (reserved; not used by send path)
#   3   confirmation gate failed (typed mismatch / missing typed flag)
#   10  auth / scope error (from gws-wrap)
#   11  rate limit
#   12  generic API error
# =============================================================================

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly GWS_WRAP="${SCRIPT_DIR}/gws-wrap.sh"
readonly BODY_PREVIEW_BYTES=200

die() { printf 'gmail-confirm-send: %s\n' "$*" >&2; exit "${2:-1}"; }
usage() {
  sed -n '5,70p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
  exit 1
}

# --- arg parse -------------------------------------------------------------
TO=""
SUBJECT=""
BODY_TEXT=""
BODY_FILE=""
CC=""
BCC=""
FROM=""
HTML=0
ATTACH=()
TYPED_RECIP=""
TYPED_SUBJECT=""
TYPED_RECIP_SET=0
TYPED_SUBJECT_SET=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --to) TO="${2:-}"; shift 2 ;;
    --to=*) TO="${1#*=}"; shift ;;
    --subject) SUBJECT="${2:-}"; shift 2 ;;
    --subject=*) SUBJECT="${1#*=}"; shift ;;
    --body) BODY_TEXT="${2:-}"; shift 2 ;;
    --body=*) BODY_TEXT="${1#*=}"; shift ;;
    --body-file) BODY_FILE="${2:-}"; shift 2 ;;
    --body-file=*) BODY_FILE="${1#*=}"; shift ;;
    --cc) CC="${2:-}"; shift 2 ;;
    --cc=*) CC="${1#*=}"; shift ;;
    --bcc) BCC="${2:-}"; shift 2 ;;
    --bcc=*) BCC="${1#*=}"; shift ;;
    --from) FROM="${2:-}"; shift 2 ;;
    --from=*) FROM="${1#*=}"; shift ;;
    --html) HTML=1; shift ;;
    --attach) ATTACH+=("${2:-}"); shift 2 ;;
    --attach=*) ATTACH+=("${1#*=}"); shift ;;
    --i-confirm-recipients=*) TYPED_RECIP="${1#*=}"; TYPED_RECIP_SET=1; shift ;;
    --i-confirm-recipients) TYPED_RECIP="${2:-}"; TYPED_RECIP_SET=1; shift 2 ;;
    --i-confirm-subject=*) TYPED_SUBJECT="${1#*=}"; TYPED_SUBJECT_SET=1; shift ;;
    --i-confirm-subject) TYPED_SUBJECT="${2:-}"; TYPED_SUBJECT_SET=1; shift 2 ;;
    -h|--help) usage ;;
    -*) die "unknown flag: $1" ;;
    *) die "unexpected positional: $1" ;;
  esac
done

[[ -n "${TO}" ]] || die "missing --to <emails>"
[[ -n "${SUBJECT}" ]] || die "missing --subject <s>"
[[ -x "${GWS_WRAP}" ]] || die "gws-wrap.sh not executable at ${GWS_WRAP}"
command -v jq >/dev/null 2>&1 || die "jq not found"

# --- resolve body (priority: file > stdin > --body) ------------------------
BODY=""
BODY_SOURCE="none"
if [[ -n "${BODY_FILE}" ]]; then
  [[ -f "${BODY_FILE}" ]] || die "--body-file not found: ${BODY_FILE}"
  BODY="$(cat "${BODY_FILE}")"
  [[ -n "${BODY}" ]] && BODY_SOURCE="file"
fi
if [[ -z "${BODY}" && ! -t 0 ]]; then
  # stdin is not a terminal — try reading. Use timeout-free read (caller pipes).
  stdin_body="$(cat || true)"
  if [[ -n "${stdin_body}" ]]; then
    BODY="${stdin_body}"
    BODY_SOURCE="stdin"
  fi
fi
if [[ -z "${BODY}" && -n "${BODY_TEXT}" ]]; then
  BODY="${BODY_TEXT}"
  BODY_SOURCE="flag"
fi
[[ -n "${BODY}" ]] || die "missing body (use --body, --body-file, or stdin)"

# --- compose metadata ------------------------------------------------------
# body_preview: first N bytes, single-line (newlines collapsed to space)
body_preview="$(printf '%s' "${BODY}" | tr '\n' ' ' | cut -c1-${BODY_PREVIEW_BYTES})"

# attachments JSON array
if (( ${#ATTACH[@]} > 0 )); then
  attach_json="$(printf '%s\n' "${ATTACH[@]}" | jq -R -s 'split("\n") | map(select(length > 0))')"
else
  attach_json="[]"
fi

metadata_json="$(jq -nc \
  --arg to "${TO}" \
  --arg cc "${CC}" \
  --arg bcc "${BCC}" \
  --arg subject "${SUBJECT}" \
  --arg body_preview "${body_preview}" \
  --arg from "${FROM}" \
  --argjson html "$([[ "${HTML}" == "1" ]] && echo true || echo false)" \
  --argjson attachments "${attach_json}" \
  --arg body_source "${BODY_SOURCE}" \
  '{
    to: $to,
    cc: $cc,
    bcc: $bcc,
    subject: $subject,
    body_preview: $body_preview,
    body_source: $body_source,
    from: $from,
    html: $html,
    attachments: $attachments
  }')"

warnings_json='["L3: send is irreversible after Gmail'"'"'s ~30s undo window"]'

# --- L3 gate evaluation ----------------------------------------------------
# Both typed flags required to execute. If either is missing → dry-run.
# If either is present but mismatched → exit 3.
GATE_OPEN=0
if (( TYPED_RECIP_SET == 1 || TYPED_SUBJECT_SET == 1 )); then
  # user is attempting to confirm — both must be present + match
  if (( TYPED_RECIP_SET == 0 )); then
    die "L3 confirmation incomplete: --i-confirm-subject was passed but --i-confirm-recipients is missing" 3
  fi
  if (( TYPED_SUBJECT_SET == 0 )); then
    die "L3 confirmation incomplete: --i-confirm-recipients was passed but --i-confirm-subject is missing" 3
  fi
  if [[ "${TYPED_RECIP}" != "${TO}" ]]; then
    die "L3 typed-recipients mismatch: --i-confirm-recipients=\"${TYPED_RECIP}\" does not match --to \"${TO}\"" 3
  fi
  if [[ "${TYPED_SUBJECT}" != "${SUBJECT}" ]]; then
    die "L3 typed-subject mismatch: --i-confirm-subject=\"${TYPED_SUBJECT}\" does not match --subject \"${SUBJECT}\"" 3
  fi
  GATE_OPEN=1
fi

# --- dry-run path ----------------------------------------------------------
if (( GATE_OPEN == 0 )); then
  next_cmd="bash gmail-confirm-send.sh --to \"${TO}\" --subject \"${SUBJECT}\" ... --i-confirm-recipients=\"${TO}\" --i-confirm-subject=\"${SUBJECT}\""
  jq -nc \
    --argjson metadata "${metadata_json}" \
    --argjson warnings "${warnings_json}" \
    --arg next "${next_cmd}" \
    '{
      action: "send",
      dry_run: true,
      tier: "L3",
      metadata: $metadata,
      warnings: $warnings,
      next: $next
    }'
  exit 0
fi

# --- execute ---------------------------------------------------------------
printf '[gmail-confirm-send] sending to %s (subject="%s")\n' "${TO}" "${SUBJECT}" >&2

# Build gws gmail +send invocation. Upstream handles RFC 5322 / MIME / base64.
# Body passed via --body flag (gws does not read stdin for this command per
# vendored skill ref; see gws-toolkit/skills/gws-gmail-send/SKILL.md).
send_args=(gmail +send --to "${TO}" --subject "${SUBJECT}" --body "${BODY}")
[[ -n "${CC}" ]] && send_args+=(--cc "${CC}")
[[ -n "${BCC}" ]] && send_args+=(--bcc "${BCC}")
[[ -n "${FROM}" ]] && send_args+=(--from "${FROM}")
(( HTML == 1 )) && send_args+=(--html)
for a in "${ATTACH[@]+"${ATTACH[@]}"}"; do
  send_args+=(--attach "${a}")
done

exec "${GWS_WRAP}" "${send_args[@]}"
