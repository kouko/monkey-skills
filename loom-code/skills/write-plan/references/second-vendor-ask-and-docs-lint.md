# Second-vendor modes and `docs-lint:`

This file owns CLI availability probes and the user-facing behavior for
`second-vendor: suggest`, `second-vendor: ask`, and a fixed CLI.

## Availability probe

A second reviewer only counts if it is a non-interactive command-line tool
from a **different model vendor than the host you are running on**: on
Claude Code look for `codex` or `gemini`, on Codex look for `claude` or
`gemini`. Detect it with `command -v <cli>` **and** a probe that it runs —
`<cli> --version` must exit 0. In zsh `command -v` may print an alias or a
function body rather than a path; do not try to parse it. **Any non-empty
output plus a `<cli> --version` that exits 0 counts as present**, and
nothing else does. Never `which`: it reports shell aliases and stale
hashes, and suggesting a tool that turns out not to run costs the user a
question for nothing. Never suggest the host itself.

Probe candidates in canonical order: Claude, Codex, Gemini, excluding the
host vendor. Supply every passing candidate to `second_vendor_policy.py` as
observed data. Do not install, authenticate, select models, or infer
availability from configuration. When the defaults file has no
`second-vendor:` line, create it from the template if needed and record
`- second-vendor: suggest — default non-blocking visibility (<date>)`.

## `second-vendor: suggest`

Run the policy only after the plan's Risk lines exist. The policy owns risk
classification and vendor choice; the station supplies grounded risk items
as `{signal, anchors}`; do not reclassify risk or synthesize a reason
the returned JSON did not contain.

For `availability`, tell the user that the returned other-vendor CLI is
available. For `recommendation`, recommend it and render the returned
`recommendation_reasons` with their anchors. In both cases, continue without
waiting. There is no background listener, reminder, or persistent opt-in
state: only a reply received in the active task before Closing Review causes
one policy reevaluation.

When that reevaluation returns `selection-confirmed`, append
`user-decided — second-vendor selection-confirmed: <vendor>` to the plan's
`## Risks` section and commit that plan edit before Closing Review starts.
The plan charter's `plan-maintained` edits-after rule authorizes this update
even when the initial plan commit already exists. Closing Review consumes
that line as the selected reviewer; it is a result record, not a fabricated
entry in `## Questions asked`.

In the small lane the notice is informational only and the active change
cannot gain another reviewer. If the user accepts anyway, report the policy's
`next-change-only` result; it does not mutate the current reviewer identity or
the standing default. A reply after Closing Review starts is likewise
next-change-only. No reply means no second vendor for this change.

## `second-vendor: ask`

`ask` is a standing choice that puts the question to the user on every
full-lane change. The answer governs only that change and never rewrites the
KICKOFF line.

When `docs/loom/KICKOFF-DEFAULTS.md` carries `second-vendor: ask`, ask one
plain sentence, in the same decision-point-① message as everything else:

> 這次要不要用 Codex 當第二位讀者？
>
> (Do you want to use Codex as the second reader this time?)

Add the question to the running list kept in step 3, so it lands in the
plan's `## Questions asked` section and the intent's decision record. That
answer names a CLI or declines a second vendor for this change.

**In the small lane**, there is only one reader, so this question is not
asked at all.

## Fixed CLI

A fixed CLI remains the standing reviewer choice. Probe it with the same
rule before use and follow the existing review failure behavior if it is not
usable; do not silently substitute another vendor.

## `docs-lint: <command> | none — <why>`

`docs/loom/KICKOFF-DEFAULTS.md` may also carry this line — a repo declaring
its own prose linter, so the review station's reviewer contract can trust
it instead of raising style findings itself (declared → no style findings;
`none` → style findings capped at `nit`).

This station never installs a docs linter and never asks about one on first
contact with a repo. When the line is absent, treat it as `none` — there is
no detection step for it the way there is for `package-tests:`.
