# Changelog

All notable changes to the `loom-interface-design` plugin (formerly `interface-design-toolkit`) are documented in this file.

Format: [Keep a Changelog](https://keepachangelog.com/).
Versioning: [Semantic Versioning](https://semver.org/).

> This file was reconstructed on 2026-07-02 from the git history — the plugin
> shipped its first three versions without a CHANGELOG.

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
