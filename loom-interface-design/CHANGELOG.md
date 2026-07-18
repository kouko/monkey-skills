# Changelog

All notable changes to the `loom-interface-design` plugin (formerly `interface-design-toolkit`) are documented in this file.

Format: [Keep a Changelog](https://keepachangelog.com/).
Versioning: [Semantic Versioning](https://semver.org/).

> This file was reconstructed on 2026-07-02 from the git history — the plugin
> shipped its first three versions without a CHANGELOG.

## [0.8.0] — 2026-07-18 — outer revision cap + minted critic verdicts

### Added

- **`design-critic`**: the writer↔critic outer revision cycle is now capped
  at 2 — on the 2nd consecutive `NEEDS_REVISION` after a revision, the loop
  stops and hands back to the user with a plain-language list of unresolved
  findings instead of silently re-running.
- **`scripts/mint_critic_verdict.py`**: ported from `loom-spec` (byte-identical
  logic; only the default file list differs — `DESIGN.md,ui-flows.md`) —
  content-hash-bound `mint`/`validate` critic-verdict CLI, plus a lockstep
  test pinning it to the `loom-spec` original so the two never drift.
- **`design-critic`**: the verdict step now additionally runs
  `mint_critic_verdict.py mint` for the change-folder on both verdict values.

Design SSOT: `docs/loom/audits/2026-07-18-agent-loop-convergence-audit.md` §4
recs 2/7 + §4c Fix-4.

## [0.7.0] — 2026-07-18 — mechanical pre-check + literal SHAPING tier label

### Added

- **Ending gates** (`interaction-flows` + `design-system`): an imperative
  action-moment card near each skill's head — before ending ANY run,
  confirm the artifact file exists on disk and the validate step ran; a
  narrated analysis with no file written is a FAILED run. Closes the
  weak-executor early-stop path that never reaches the buried validate
  step (live incident: 2026-07-18 dogfood, a haiku run ended without
  writing ui-flows.md; imperative cards are the evidence-backed carrier —
  docs/loom/memory/imperative-trigger-cards-beat-descriptive-preloads.md).

- **`design-critic`**: a mechanical pre-check step runs BEFORE panel
  dispatch — greps the artifact for (1) `evidence_needed:` values outside
  `craft | domain-convention | project-local` and (2) tier-label
  discipline on every `evidence_needed: domain-convention` tag, split into
  two literal sub-greps: (2a) an untiered tag with no literal `SHAPING` or
  `DEFERRABLE` label nearby, and (2b) a literal `SHAPING` label declared
  non-blocking/deferred WITHOUT a `deferred: <reason>` marker. Either hit
  emits a `NEEDS_REVISION` finding directly (no panel needed for that
  finding; the panel still runs for everything else). Classifying
  SHAPING-ness itself stays the panel's judgment — the pre-check only
  checks for the literal label. Verdict vocabulary (`PASS_WITH_NOTES` /
  `NEEDS_REVISION`) unchanged.
- **`interaction-flows` + `design-system`**: both
  `references/knowledge-triage.md` gain two identical one-sentence
  supplements placed AFTER the pinned vocabulary block (never inside it):
  "SHAPING never ships as non-blocking: it either resolves before this
  station's gate or carries `deferred: <reason>`." — closes the
  prose-only-consequence gap a weak drafter inverted in live dogfood (leg
  2, `docs/loom/dogfood/2026-07-18-knowledge-triage-live-spec-leg.md`) —
  and "Every tagged open question written into ui-flows.md / DESIGN.md
  must carry a literal `SHAPING` or `DEFERRABLE` label alongside its
  `evidence_needed:` tag." — makes the tier label a literal artifact
  obligation the pre-check's mechanical grep can actually find, mirroring
  loom-spec's domain-tag-triage.md two-tier doctrine.

## [0.6.0] — 2026-07-18 — HIGH-bar knowledge triage + critic evidence flag

### Added

- **`interaction-flows` + `design-system`**: each gains
  `references/knowledge-triage.md` (pinned three-bucket vocabulary:
  craft / domain-convention / project-local) with an imperative mount at
  its drafting moment. SHAPING bar (HIGH, narrower than loom-spec's):
  the answer alters flow structure, a state machine, or a semantic
  display convention. SHAPING domain-convention facts get routed
  research BEFORE the critic verdict; deferrable ones become tagged open
  questions (`evidence_needed:`) in ui-flows.md / DESIGN.md for the spec
  station to inherit. Drafting skills never run WebSearch.
- **`design-critic`**: findings may carry the optional
  `evidence_needed: craft | domain-convention | project-local` tag —
  flag-never-search; verdict enum unchanged.

## [0.5.0] — 2026-07-13

### Added

- **Surface-treatment candidate pick** (`design-system`) — the station now
  proposes **3-5 surface-treatment candidates** from the new
  `references/canon-design-surface.md` (fit/tension notes), surfaces **1-2
  considered-but-rejected** with reasons, and the **user decides** (a
  `bespoke — no canon treatment fits` escape hatch is legal). The pick is
  **named + rationalized in prose** in Overview / Brand and then constrains the
  `## Elevation & Depth` and `## Shapes` token blocks. The anti-costume law
  carries over (a treatment never overrides a PRINCIPLES value) and a canon
  row's **WCAG risk flag is a blocker, not a note**. No 9th `##` section was
  added — the 8-section DESIGN.md contract is unchanged.
- **`references/canon-design-surface.md`** — relocated here from
  `loom-product-principles` (it is a stage-4 design-language sub-decision, not a
  constitution-stage one) and expanded **6 → 18 rows**, each with a
  live-verified source URL, era, currency note and WCAG risk flag. Grounded in
  `docs/loom/research/2026-07-12-ui-surface-treatments-canon.md`.

### Changed

- **`design-system` now INHERITS the visual mood instead of inventing it.**
  Step 2 reads the `## Anchors` section of `PRINCIPLES.md` and treats the
  **3-5 tone & manner adjectives** as the **governing mood** — it does **not**
  re-derive them (`design-md-schema.md`'s derivation contract agrees; `brand_voice`
  is fed from the anchor). When no anchor row exists, it derives as before **and
  says so explicitly** — never silently inventing while appearing to inherit.
  This is a **read-and-honor prose instruction, not a parser** (rationale +
  reversal trigger: `docs/loom/specs/2026-07-13-axis-b-relocation-and-tone-manner-seam.md`
  §Alternatives). Closes the unwired seam left by loom-product-principles 0.8.0.

## [0.4.2] — 2026-07-07

### Changed

- `using-loom-interface-design` §Intake now points at the family relay
  discipline (`loom-pipeline/hooks/family-relay.md`). Verification:
  `test_family_relay.py::test_design_side_pointers[interface-design]` passed.

## [0.4.1] — 2026-07-05

### Added

- **`using-loom-interface-design/references/claude-code-tools.md`** +
  **`codex-tools.md`** — `design-critic`'s multi-lens panel already phrased
  subagent dispatch in host-neutral prose ("dispatch one subagent per
  lens... not bound to any one harness"), but had zero concrete reference
  for what that resolves to on either host. Added the same host-neutral
  skill body + per-host tool-mapping reference pattern `loom-code` uses
  (`obra/superpowers` is the confirmed prior-art source for this pattern).
  Codex side documents `multi_agent`/`spawn_agent`/`wait_agent`/
  `close_agent`, verified 2026-07-05 via `codex features list` on a live
  Codex 0.139.0 install (feature flag itself live-confirmed) + OpenAI's
  official Codex manual §Subagents (verb names/behavior doc-confirmed, not
  independently re-exercised for this plugin's specific dispatch points).
  `design-critic/SKILL.md`'s panel section now points at both files.

## [0.4.0] — 2026-07-04

### Added

- **`## §Intake`** section on `using-loom-interface-design/SKILL.md`
  (loom family connective-tissue work): step 1 checks the target against
  the `loom-pipeline` family-reception on-ramp criteria (PRINCIPLES.md
  gap recommends `using-loom-product-principles` first), step 2
  redirects spec/code asks to their own entries, step 3 keeps the
  existing design-system/interaction-flows routing. Guarded by
  `test_entry_intake.py`.

### Changed

- **Next-station cross-refs** — `design-system/SKILL.md` (§Downstream)
  and `interaction-flows/SKILL.md` (§Boundary) each gain a "Next
  station." line pointing a finished `DESIGN.md` / `ui-flows.md` to
  `using-loom-spec` to expand the feature into a spec.
- `test_entry_intake.py`'s `§Intake`-section slice now stops at
  whichever comes first of the next `## ` heading or the
  `<EXTREMELY-IMPORTANT>` block — the old `\n## `-only boundary let the
  `<EXTREMELY-IMPORTANT>` block leak into the "§Intake section" a
  step-scoped assertion checked, mutation-proven (old test false-passed
  a stripped mutant; fixed test fails it).

### Decided

- **`DESIGN.md` machine consumer: parked, with explicit re-triggers** (audit
  batch ③ close-out). Wiring a loom-code review gate / implementer intake was
  evaluated and rejected for now — it would front-run #456's documented
  decision that consumer-side machinery (including the shadcn-vs-Material
  color-naming question a conformance check must interpret) is undecidable
  until a real frontend consumer lands, and the upstream DESIGN.md spec is
  alpha with consumer behavior unspecified. Re-triggers recorded in README
  §Scope: first real GUI product wiring its frontend to the pipeline, or
  upstream spec 1.0 / second-vendor adoption.

### Changed

- **`ui-flows.md` moves into a per-change folder** —
  `docs/loom/<change-id>/ui-flows.md`, sharing the `<change-id>`
  `loom-spec:spec-expansion` uses, so the design seed sits beside the spec
  delta it feeds. The old fixed product-level `docs/loom/ui-flows.md` meant
  the second feature overwrote the first ("per-feature/change" was declared
  but not honored by the path). `DESIGN.md` stays product-level.
  `validate_design_output.py` now resolves `DESIGN.md` most-specific-first
  (change folder, then its parent) — the legacy side-by-side layout still
  validates. `design-critic` inputs and README updated. Guarded by
  `test_change_folder_with_design_at_parent_passes` (+3 sibling tests),
  `test_ui_flows_emitted_per_change_folder`,
  `test_inputs_are_per_change_folder`.

### Added

- `design-critic` now ends every run with a **machine-readable two-valued
  verdict** — `PASS_WITH_NOTES` / `NEEDS_REVISION` (no unqualified PASS — that
  would be a completeness claim). The router carries the stage-3 resolution
  rule (`NEEDS_REVISION` → back to the generators; `PASS_WITH_NOTES` →
  `ui-flows.md` hands to spec-expansion). Drift-alignment with
  `completeness-critic`: explicit **write-back contract** (augment in place,
  never overwrite, `critic-found` provenance tags, validator run post
  write-back) and the **overlap-rate panel-diversity diagnostic** reported in
  the new round summary. Guarded by `test_verdict_two_valued_enum`,
  `test_write_back_carries_provenance`, `test_overlap_rate_diagnostic_present`.

### Fixed

- `design-system` / `interaction-flows` SKILL.md now state the correct
  skill-dir-relative validator path (`../../scripts/validate_design_output.py`);
  the previously claimed `scripts/…` form did not resolve from the skill
  directory in an installed plugin.
- README: `design-critic` listed as shipped (it landed in v0.2.0 but the README
  still called it deferred), scope section retitled to the current version line,
  and the `DESIGN.md` side-channel description aligned with the honest seam
  wording from #465 (no loom-code skill machine-reads `DESIGN.md`).
- Earlier unversioned post-0.3.0 fixes: trigger-description rewrites +
  DESIGN.md visual-concept layer (#456), reply-honesty prose + skill version
  fields (#465).

## [0.3.0] — 2026-06-21

### Changed

- **BREAKING**: plugin renamed `interface-design-toolkit` → `loom-interface-design`;
  router skill renamed `using-interface-design-toolkit` → `using-loom-interface-design`;
  artifact paths unified under `docs/loom/` (#440).

## [0.2.0] — 2026-06-17

### Added

- `design-critic` — adversarial writer≠judge panel hunting surface omissions
  (undrawn states, dead-end flows, a11y gaps) + principle conformance over the
  design change-folder, mirroring `loom-spec:completeness-critic` (#409).

## [0.1.0] — 2026-06-15

### Added

- MVP: `design-system` (GUI → 8-section `DESIGN.md`) + `interaction-flows`
  (`ui-flows.md`) + `using-interface-design-toolkit` router +
  `validate_design_output.py` change-folder validator. Cross-modal
  architecture (GUI/TUI/CLI), GUI-first (#399).
