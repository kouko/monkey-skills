# Changelog

All notable changes to the `loom-spec` plugin (formerly `spec-toolkit`) will be documented in this file.

Format: [Keep a Changelog](https://keepachangelog.com/).
Versioning: [Semantic Versioning](https://semver.org/).

## [0.7.0] — 2026-07-18 — outer revision cap + minted critic verdicts

### Added

- **`completeness-critic`**: the writer↔critic outer revision cycle is now
  capped at 2 — on the 2nd consecutive `NEEDS_REVISION` after a revision, the
  loop stops and hands back to the user with a plain-language list of
  unresolved findings instead of silently re-running.
- **`scripts/mint_critic_verdict.py`**: new content-hash-bound critic-verdict
  CLI (`mint --change-folder --critic --verdict-file --files` /
  `validate --change-folder --critic --files`) — sha256-binds a verdict to the
  exact files it covered; `validate` exits 0 fresh-`PASS_WITH_NOTES`, 2 no-verdict,
  3 fresh-`NEEDS_REVISION`, 4 stale-hash. `NEEDS_REVISION` still mints (a
  rejected draft's verdict is itself evidence); overwrite-in-place, path- and
  UTF-8-guarded.
- **`completeness-critic`**: the verdict step now additionally runs
  `mint_critic_verdict.py mint` for the change-folder on both verdict values.
- **`spec-expansion`**: gains a validate-before-fan-out step consuming
  `loom-interface-design`'s design-critic verdict — runs
  `mint_critic_verdict.py validate --files DESIGN.md,ui-flows.md` and
  proceeds only on exit 0; on 2/3/4 it stops and reports which condition
  blocked (never-ran / critic-blocked / stale) instead of fanning out over an
  unreviewed or stale design.

Design SSOT: `docs/loom/audits/2026-07-18-agent-loop-convergence-audit.md` §4
recs 2/7 + §4c Fix-4.

## [0.6.0] — 2026-07-18 — mechanize knowledge-triage enforcement semantics

### Added

- **`scripts/validate_spec_output.py`**: three deterministic checks over the
  emitted spec directory (`proposal.md` + `specs/**/spec.md`) —
  (1) `evidence_needed:` value whitelist (craft / domain-convention /
  project-local; any other value fails naming file:line + the offending
  value); (2) every `evidence_needed: domain-convention` occurrence must
  carry a SHAPING or DEFERRABLE tier label in its own list item/paragraph
  or that block's governing heading/lead-in line (structural scoping, not
  a character-distance window); (3) a SHAPING-classed domain-convention
  item without a `deferred: <reason>` note in its own scope fails naming
  the VERIFY gate rule. Mechanizes the enforcement semantics that a 3-leg
  weak-model dogfood proved prose-only instructions do not survive (see
  `docs/loom/dogfood/2026-07-18-knowledge-triage-live-spec-leg.md`).
- **`completeness-critic/references/consistency-lens.md`**: a cross-layer
  consistency lens — checks `proposal.md`'s FLAG/open-question items against
  `spec.md`'s requirement text; a requirement that silently resolves a
  question the proposal flagged as open is an OMISSION finding (severity 3
  by default), fed into the critic's existing consolidated/ranked pipeline.

## [0.5.0] — 2026-07-18 — domain-tag triage at edge-case expansion

### Added

- **`spec-expansion/references/domain-tag-triage.md`**: pinned three-bucket
  vocabulary (craft / domain-convention / project-local); non-derivable edge
  cases classify FIRST — domain-convention facts become tagged open questions
  (`evidence_needed:`), never invented answers. SHAPING-class tags (answer
  alters acceptance criteria, data semantics, or a state machine) block
  VERIFY unless explicitly `deferred: <reason>`; resolution routes OUTSIDE
  the skill between draft and gate — drafting stays closed-world.

## [0.4.3] — 2026-07-15

### Changed

- **`spec-expansion` SKILL.md 4,113 → 3,584 words (−12.9%)**: the persisted
  intent-layer sections (§Consuming prior-state + §Authoring TOP/MID) extracted
  to `references/intent-layer.md` with trigger-carrying pointers; the
  `[active|deferred]` declaration syntax and the ui-flows seam table stay
  inline. Behavior equivalence proven via 4 test prompts × 3-judge ensemble
  (12/12 EQUIVALENT); first `test-prompts.json` shipped for this skill.
  Slim round 2 of the Pocock token-economy roadmap.

## [0.4.2] — 2026-07-07

### Changed

- `using-loom-spec` §Intake now points at the family relay discipline
  (`loom-pipeline/hooks/family-relay.md`) instead of restating it inline —
  closes the BACKLOG loom-spec briefing-gate item. Verification:
  `test_family_relay.py::test_design_side_pointers[spec]` passed.

## [0.4.1] — 2026-07-05

### Added

- **`using-loom-spec/references/claude-code-tools.md`** + **`codex-tools.md`**
  — `completeness-critic`'s multi-lens panel already phrased subagent
  dispatch in host-neutral prose ("phrase this fan-out portably... not
  bound to any one harness/tool, because this skill is agent-portable"),
  but had zero concrete reference for what that resolves to on either
  host. Added the same host-neutral skill body + per-host tool-mapping
  reference pattern `loom-code` uses (`obra/superpowers` is the confirmed
  prior-art source for this pattern). Codex side documents `multi_agent`/
  `spawn_agent`/`wait_agent`/`close_agent`, verified 2026-07-05 via `codex
  features list` on a live Codex 0.139.0 install (feature flag itself
  live-confirmed) + OpenAI's official Codex manual §Subagents (verb
  names/behavior doc-confirmed, not independently re-exercised for this
  plugin's specific dispatch points). `completeness-critic/SKILL.md`'s
  panel section now points at both files.

## [0.4.0] — 2026-07-04

### Added

- `using-loom-spec` — a new thin entry/router skill completing the family's
  `using-loom-*` convention (loom family connective-tissue plan). §Intake
  checks upstream/peer fit against the loom-pipeline reception SSOT, then
  routes between loom-spec's two members by the specific verb: draft/expand
  from a seed → `spec-expansion`; critique/audit an existing draft → the
  member skill this router names — closing the #456-documented
  adjacent mis-route where a critique-an-existing-draft ask got sent to
  `spec-expansion` instead. Guarded by
  `scripts/test_spec_entry_skill.py`.

### Changed

- `test_spec_entry_skill.py::test_intake_step2_peer_check_present` is now
  step-2-scoped: it slices Step 2's own paragraph (between the `**Step 2`
  and `**Step 3` markers) and asserts the three redirect-target names
  (`using-loom-interface-design`, `using-loom-product-principles`,
  `using-loom-code`) are present within it, rather than grepping the whole
  file for `對站檢查`/`step 2` — the prior assertion stayed green even if
  step 2's redirect targets were dropped (and a whole-§Intake slice was
  still too coarse: Step 1 independently names two of the three targets).
  Mutation-verified: all three assertions fail on a step-2-stripped copy.
  Found during C1/C2's quality reviews.
- README §Scope: the `using-loom-spec` PARK paragraph now reflects the
  supersession — the thin entry shipped in 0.4.0; the park stands for the
  tiering-capable upgrade only, re-triggers unchanged.

### Verified

- `spec-expansion`'s existing `loom-code:writing-plans` next-station
  pointer (§Boundary — stops at GENERATE) already names the
  validated-change-folder → writing-plans handoff explicitly; no edit was
  needed — this release just confirms the wiring the brief asked to check.

## [Unreleased]

### Decided

- **[SUPERSEDED by 0.4.0]** — a THIN `using-loom-spec` entry (intake +
  member disambiguation, NO tiering judgment) shipped via the loom family
  connective-tissue plan; the park below concerned the tiering-capable
  router, whose re-triggers (DECLARE lands, discovery/persist scheduled)
  remain valid for adding tiering to the now-existing entry.
- **`using-loom-spec` router: parked, with explicit re-triggers** (audit
  close-out, reaffirming the MVP brief's v0.2 deferral). The router's
  load-bearing job per the 2026-06-11 research synthesis is the
  proportional-rigor **tiering judgment**, which depends on
  `spec-discovery` / `spec-persist` and the OpenSpec DECLARE layer — none
  built. The writer→judge sequencing concern that re-raised the question is
  already covered in-skill (spec-expansion handoff + completeness-critic
  verdict resolution, shipped in the audit's earlier PRs). Re-triggers in
  README §Scope: DECLARE lands, or discovery/persist are scheduled — the
  router ships with its tiering cargo, not before it. Also fixed the README's
  dead pointers to the pre-rename brief/research filenames (frozen docs keep
  old names; the pointers now match).

### Changed

- `spec-expansion` §Consuming a `ui-flows.md` seed now names the seed's
  canonical per-change location (`docs/loom/<change-id>/ui-flows.md`, the same
  change folder this skill emits into) — following loom-interface-design's
  move of `ui-flows.md` off the fixed product-level path.

### Added

- `completeness-critic` now ends every run with a **machine-readable two-valued
  verdict** — `PASS_WITH_NOTES` / `NEEDS_REVISION` (aligned with loom-code's
  reviewer vocabulary; an unqualified PASS is deliberately absent — it would be
  a completeness claim, and Blind spots is non-empty by construction). Verdict
  semantics: `NEEDS_REVISION` when a severity-3 finding cannot be concretely
  re-seeded or the validator fails post-write-back. The **severity scale is now
  defined** (3 = load-bearing / 2 = should-add / 1 = polish, same scale as
  design-critic), and the write-back is documented as the sanctioned
  GENERATE-station exception to the evaluator-does-not-modify rule (repo
  CLAUDE.md). Guarded by `test_verdict_two_valued_enum` +
  `test_severity_scale_defined`.

- `spec-expansion` now reads `docs/loom/PRINCIPLES.md` as a **governing
  constraint** before expanding (new §Governing constraint — constitution→spec
  seam): the constitution bounds the fan-out scope, steers Phase ③ pruning
  priorities, and sets the NFR posture; absence is surfaced loudly (expansion
  proceeds only with an explicit "ungoverned" caveat). Closes the seam gap
  where product-principles claimed to govern spec-expansion but only the
  completeness-critic's post-hoc lens ever read the constitution. Guarded by
  `test_body_reads_principles_as_governing_constraint`.

## [0.3.1] — 2026-06-21

### Changed

`validate_spec_output.py` now accepts `## MODIFIED Requirements` and
`## REMOVED Requirements` as valid delta-block openers, not just
`## ADDED Requirements`. An OpenSpec change may add, modify, or remove
requirements; gating the delta on `ADDED` alone walled off legitimate
MODIFIED/REMOVED change-folders. Backward-compatible — every input the
validator previously accepted still passes; it only stops rejecting the
two previously-walled-off block kinds. More OpenSpec-faithful.

Known edge (out of scope, documented in the validator): a pure
`## REMOVED Requirements` delta with no scenarios still fails the
GIVEN/WHEN/THEN scenario check — a removal may legitimately carry no
scenario. That is a separate, deeper decision; this change only makes
the three block openers reachable.
