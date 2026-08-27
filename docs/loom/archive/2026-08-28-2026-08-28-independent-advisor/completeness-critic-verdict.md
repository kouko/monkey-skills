# completeness-critic verdict — independent-advisor

- change-id: `2026-08-28-independent-advisor`
- artifact under critique: `proposal.md` (seven chapters) + `specs/independent-advisor/spec.md`

verdict: PASS_WITH_NOTES


## Why PASS_WITH_NOTES

The author's revision took the disclosure route the user ruled on: the privacy
guarantee covers the dispatch packet only, and the fix is an obligation to say so
rather than a stronger scan. REQ-68..REQ-74 are written as MUST, they name what has
to be said, they name the moment it has to be said (the checkpoint, before approval
is accepted; the delivered report), and their scenarios assert the content of the
statement rather than the presence of a field. No B item is left STILL_OPEN, so the
draft may leave critique. Two of the four are PARTIAL: the disclosure obligation
closes the face of the finding the user ruled on, and leaves a named face untouched.
Those residuals are recorded in `proposal.md` §Blind spots and are repeated under
notes below.

## Rounds run, and what each round returned

- **Round 1** — five lenses (NFR/security, permission/role, missing objects and actors,
  state/error/loading, cross-object and system-level failure). 23 findings were merged and
  written back as REQ-27..REQ-49; a named residual list was left in §Provenance and a
  human/field-input table in §Blind spots.
- **Round 2** — three lenses (NFR/security, missing objects and actors, cross-object and
  system-level failure), each pointed at gaps REQ-27..REQ-49 themselves introduced or left
  half-closed. 18 findings were merged as REQ-50..REQ-67; four were held back as structural
  (B1..B4).
- **This pass** — one confirmation pass, no new lenses. It read only the author's revision
  (REQ-68..REQ-74 and the 已裁定 paragraphs under §Blind spots → 結構性問題) and asked, per
  B item, whether the new requirements are specific enough to be tested and whether the
  disclosure is worded so a passing scan cannot be read as safety.

**Qualitative read on lens diversity and overlap.** Round 2's three lenses converged
heavily — the single most severe finding (the scanned and pinned set is not the readable
and egressing set) was reached independently by all three. That convergence signals the
three lenses were probing one layer, the boundary between what this system inspects and
what the external process does on the host; it is **not** evidence that the space outside
that layer was searched. The two axes that stayed unlensed across both rounds are
unchanged by this pass: (a) a user-journey lens on the report as an artifact a human must
act on — REQ-68 and REQ-72 add material to the single checkpoint, which is the place that
lens would probe, and (b) a maintenance/evolution lens on the two pinned external CLIs.
This confirmation pass deliberately did not open either.

## B1..B4 — findings of this pass

- **B1 — the scanned and pinned set is not the readable and egressing set. → PARTIAL.**
  REQ-68 puts the disclosure at the checkpoint before approval is accepted, names what must
  be said (the packet was inspected, `scope_boundary` is the larger readable range, and what
  that range covers in practice), and requires non-technical wording. REQ-69 forbids stating
  a passing scan as safe content or any wording carrying that meaning, which is the misleading-
  wording trap. REQ-70 carries the limitation into every delivered report. REQ-71 demotes a
  pinned revision to the packet's origin. All four are MUST and their scenario THENs assert
  what the wording says. *What remains*: B1 had a third face — the proposer leg's blindness.
  REQ-10 checks packet text, while `scope_boundary` may authorise the incumbent's implementing
  files, so a leg reported as fully blind may have read them. REQ-68..REQ-71 disclose the
  privacy range; none of them constrains or qualifies the blindness claim the report makes
  about the proposer leg. That is an integrity claim, not a privacy claim, and the user's
  ruling does not dispose of it.

- **B2 — REQ-38 records the executor's loaded environment; loading is execution. → CLOSED.**
  REQ-72 states the obligation at the checkpoint, names the content (a dispatch causes the
  executor to load project instructions, hooks, skills and MCP servers, and loading them runs
  third-party code in the user's repository), and handles the case the spec must not invent
  external tool behaviour for: when the set cannot be enumerated, the system must say it cannot,
  and must not leave it unsaid in a way that reads as there being none. The scenario asserts both
  statements. Whether a suppression switch exists on the pinned CLIs stays a live-probe item and
  is already listed in §Blind spots.

- **B3 — REQ-30 protects the control plane; injected text still flows to consumers. → PARTIAL.**
  REQ-73 is MUST, requires the marking wherever external text is carried into the report, requires
  the marking to travel with the report to downstream consumers including an agent that adopts it
  without a human turn, and explicitly forbids limiting the protection to the controller's own
  fields. Its scenario asserts the marking is present in what the agent receives, so the marking is
  not merely held in the controller's memory. This is the mitigation B3 said was the only available
  move, and it is written as one. *What remains*: two things. REQ-73 binds text "carried into the
  report", while B3 also named the leg-to-leg path — proposer output is normalizer input and the
  normalized card is blind-judge input, and no requirement marks or inerts text on that path.
  And the author's own 已裁定 note leaves undecided whether a controlling agent adopting a
  divergence point must have a human restate it.

- **B4 — the audit record is a second copy of the egressing material. → PARTIAL.**
  REQ-74 refuses to pick the granularity for the author but makes the choice declarable: the record
  must declare whether it retains references and summaries or verbatim sent material, a verbatim
  record inherits the dispatch packet's handling restrictions, and its location is stated at the
  checkpoint. That converts a silent trade-off into a stated one, which is a real close on the
  disclosure face. *What remains*: B4's specific hazard was that the record, sitting in the same
  readable tree, becomes ordinary readable material for the next consultation's evidence paths and
  pre-dispatch scan. Inheriting the packet's handling restrictions governs how the record is treated
  as material being sent; it does not exclude the record from a later consultation's
  `scope_boundary` or from being picked up as evidence. No requirement states that exclusion, and the
  author's note defers location to the field-input table.

## Notes

Residuals carried out of this pass, all recorded in `proposal.md` §Blind spots:

- The proposer leg's blindness claim is not qualified by any requirement, although
  `scope_boundary` can authorise the incumbent's implementing files (B1 residual).
- No requirement marks or inerts external text on the leg-to-leg path
  (proposer → normalizer → blind judge), only on the path into the report (B3 residual).
- Whether an adopting agent must have a human restate a divergence point is undecided
  (B3 residual, named by the author).
- The audit record is not excluded from a later consultation's readable range or evidence
  paths; granularity, location, read permissions and retention stay field-input items
  (B4 residual).

Parameter gaps still open and unchanged by this revision: scan technique and its
false-positive behaviour; whether the two pinned CLIs offer a suppression switch;
per-leg timeout seconds, probe time budget and concurrency ceiling; `max_attempts` and
the output-contract thresholds; cost tolerance and spend ceiling values; the persistence
location and query interface for the egress record; the vendor, legal and organisational
items already tabled in §Blind spots.

Two asymmetries inside the new requirements themselves, offered as notes rather than as
blocking findings:

- REQ-72 says what to do when the loaded set cannot be enumerated; REQ-68 requires
  enumerating what `scope_boundary` covers and says nothing about the case where that
  enumeration is not available.
- REQ-73 requires the marking to travel but does not say what happens when a downstream
  channel cannot carry it.

## Coverage statement

coverage relative to seed + 5 lenses (round 1) / 3 lenses (round 2) / 1 confirmation pass

## Next action

None blocking. The PARTIAL residuals above are author or field decisions and are recorded
where the author's decision log already sits.
