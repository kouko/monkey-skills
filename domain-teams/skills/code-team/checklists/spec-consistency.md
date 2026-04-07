# Spec Consistency Checklist Gate

## Evaluation Instructions

Check each item against the spec document.
Report with section references and evidence quotes.
Only report actual issues — do not report things that are correct.

## CHK-SPEC-001: Cross-Section Term Consistency [FIXABLE]
- [ ] Type/struct names match across all sections
- [ ] Field names in data structures match serialized output (JSON/YAML/etc.)
- [ ] Interface identifiers (CLI flags / API endpoints / config keys) are consistent
- [ ] File paths in directory structure match references in other sections
- [ ] Format/enum names are identical everywhere they appear

## CHK-SPEC-002: Architecture Diagram vs Text [FIXABLE]
- [ ] Component names in diagrams match textual descriptions
- [ ] Data flow arrows match processing steps
- [ ] Connections in diagrams match interface definitions

## CHK-SPEC-003: Interface ↔ Config ↔ Defaults [FIXABLE]
- [ ] Every interface element has matching config/env documentation (or is explicitly excluded)
- [ ] Default values are identical across all locations (interface def, config table, examples)
- [ ] Enum/option sets are identical in all locations

## CHK-SPEC-004: External Dependencies [FIXABLE]
- [ ] Versions are consistent across tech stack, config, and dependency sections
- [ ] Dependency names/labels are consistent
- [ ] License information is present and consistent

## CHK-SPEC-005: Outdated References [FIXABLE]
- [ ] No terms that were renamed during editing survive in old form
- [ ] No references to removed/replaced components, strategies, or paths
- [ ] Search for common rename patterns: old names in comments, diagrams, examples

## CHK-SPEC-006: Implementation Readiness [FATAL if BLOCKED modules exist]
For each module:
- [ ] Input format fully defined (types, ranges, examples)
- [ ] Output format fully defined
- [ ] External dependencies documented
- [ ] Error handling expectations clear
- [ ] Edge cases addressed
- Mark: READY / PARTIAL / BLOCKED

## CHK-SPEC-007: Formatting [FIXABLE]
- [ ] No Unicode replacement characters (U+FFFD)
- [ ] All code blocks properly closed
- [ ] Table columns consistent
- [ ] No orphaned list items or broken internal references
