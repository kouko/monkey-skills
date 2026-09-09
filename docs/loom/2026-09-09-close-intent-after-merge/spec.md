# Derived intent delivery state — spec
intent: 2026-09-09-close-intent-after-merge@bf1a64c038a86d3d42469723f7b557690b27927b
pre-build-review: required — changes Loom's public intent lifecycle contract and the cross-boundary interpretation of evidence on the default branch
confirmed-behavior: 2026-09-09 @33ba883

## Requirements

REQ-1 — Delivery derived from the default branch
  WHEN a current-contract intent's canonical attestation is present on the selected default-branch ref and identifies that intent, Loom shall report the intent as delivered without changing the intent document → Acceptance #1

REQ-2 — Unmerged evidence remains active
  WHILE a confirmed intent's evidence exists only in a feature branch, open pull request, index, or working tree, Loom shall report the intent as active → Acceptance #2

REQ-3 — Existing delivered intents disappear from active results
  WHEN Loom lists active intents against the current default-branch ref, the intents delivered by PRs #810, #811, #812, and #813 shall not appear even though their documents remain confirmed → Acceptance #3

REQ-4 — Evidence identity is recomputed
  IF the selected remote-default snapshot lacks the canonical intent or a canonical attestation with supported schema, complete required payload, and matching change-id THEN Loom shall not report the intent as delivered → Acceptance #4

REQ-5 — Optional merge metadata stays derived
  WHEN a caller requests a pull-request number or merge time for a delivered intent, Loom shall derive it from repository or GitHub history and shall still report the repository-proven delivered state when that optional metadata is unavailable → Acceptance #5

REQ-6 — Existing publication and merge boundaries remain unchanged
  The Loom lifecycle shall preserve separate merge authorization, exact-HEAD publication checks, the privacy gate, and non-forced publication behaviour → Acceptance #6

REQ-7 — Legacy closure remains readable
  WHERE an intent already carries a valid legacy closed status, Loom shall continue to report it as closed while current-contract delivery produces no new close transition → Acceptance #7

## Design decision

- agent-decided — Separate decision state from delivery state: `status: confirmed` records the user's decision, while delivery is recomputed from the default branch. This avoids storing the same merge fact twice.
- agent-decided — Use only the canonical attestation path and its matching `change_id` as the repository-local delivery witness. A similarly named file or working-tree artifact is not evidence.
- agent-decided — Validate the delivery witness's supported schema and required payload shape, but do not revalidate its historical `content_digest` against the current default-branch tree; unrelated later merges must not make a delivered intent active again.
- agent-decided — Resolve authority only through `refs/remotes/<selected-remote>/HEAD`; support any default-branch name and never fall back to a local branch as delivery evidence. A missing, invalid, or unreadable remote-default ref yields `indeterminate` and blocks intake until refreshed.
- agent-decided — Keep PR number and merge time optional because repository delivery can be proven offline, while GitHub metadata may require network access or be unavailable on another forge.
- agent-decided — Preserve legacy explicit `closed` states as terminal historical records, but stop generating new ones under the current contract.
- agent-decided — Add the delivery resolver to the existing `loom_checker.py` and share it between active-intent reporting and `intake.confirmed`; a separate status script would create another command surface and a second source of truth.
- agent-decided — Make delivered-state intake blocking part of the existing `intake.confirmed` rule rather than adding a second lifecycle gate. The same recomputation should power listing and duplicate-work prevention.

## Alternatives considered

- Write a close commit after merge — rejected because it creates a new SHA after successful CI and requires another pull request or a protected-branch bypass.
- Add the PR number to the intent before merge — rejected because the number is unavailable before PR creation and any later update changes the checked HEAD.
- Open a draft PR to reserve the number — rejected because draft workflows differ by repository and cannot guarantee that expensive CI runs only once.
- Pre-write `closed` on the feature branch — rejected because an unmerged branch would claim completion and publication currently requires a confirmed canonical intent.
- Copy successful statuses to a new close-only SHA — rejected because GitHub binds required checks to the latest commit and synthetic status reuse weakens the trust boundary.

## Current state evidence

- Forward: `loom-code/skills/ship/SKILL.md:139` ends publication at a separately authorized direct merge and defines no intent lifecycle action afterward.
- Reverse: `loom-code/scripts/loom_checker.py:1268` accepts confirmed intents for write-spec and write-plan, but only detects explicit historical close transitions.
- Error: `loom-code/scripts/loom_checker.py:1328` treats every valid confirmed intent as eligible, so an already delivered current-contract intent can be planned again.
- Data: `loom-code/scripts/loom_checker.py:3307` derives a change-id from the canonical attestation path and `loom-code/scripts/loom_checker.py:3325` reads its committed payload.
- Boundary: `loom-code/scripts/loom_checker.py:3277` finishes publish after PR creation and CI observation; this change adds derived status and intake protection but does not alter publication, CI, or merge execution.

## UI flows

- User asks for active intents after refreshing the default-branch ref → Loom lists only confirmed intents without matching canonical delivery evidence; delivered PR #810–#813 intents are absent.
- User asks about one delivered intent → Loom reports delivered from repository evidence and includes PR or merge metadata only when it can derive that metadata reliably.
- User asks about a confirmed intent whose evidence exists only outside the default branch → Loom reports active and does not infer delivery from the local working tree or open pull request.
- User tries to plan a confirmed intent already delivered on the default branch → intake stops and explains that the change is delivered and a new change needs a new intent.
- Delivery evidence is absent, malformed, misplaced, or names another intent → Loom keeps the intent active and names the invalid evidence boundary instead of guessing.
- A legacy closed intent is inspected → Loom reports the recorded closed state and continues to reject reopening it.
- Default-branch evidence cannot be resolved locally → Loom reports that delivery cannot be determined from the available repository snapshot and tells the caller to refresh the ref; it does not contact GitHub or change refs silently.
- A caller attempts intake while the selected remote-default snapshot is indeterminate → Loom blocks duplicate-work intake until a usable remote-default ref is available.
- A canonical attestation contains only a matching change-id, has an unsupported schema, has an incomplete payload, or has no canonical intent beside it → Loom keeps the intent active rather than accepting a partial witness.
- A valid delivered attestation is followed by unrelated merges → Loom continues to report that intent as delivered without comparing its historical content digest to the newer tree.
