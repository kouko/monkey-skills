# Freshness Gate

## Scope Boundary

Review the **freshness** of a documentation artifact against the metadata
convention defined in `standards/freshness-metadata.md`. This is a MAY gate
— it only runs on user request or on documents that already have freshness
metadata.

**Metadata reference**: `standards/freshness-metadata.md`

## Special Verdict: NEEDS_METADATA

Unlike other gates, this gate has a **fourth possible verdict**:

- `NEEDS_METADATA` — the document has no freshness metadata at all
  (no `last_reviewed`, no `applies_to`, no `owner`). The gate cannot apply.

The expected response to `NEEDS_METADATA` is:
1. Add frontmatter metadata per `standards/freshness-metadata.md`, OR
2. Skip this gate for this document with a stated reason (e.g., "README is
   maintained continuously via PRs; freshness metadata not applicable").

`NEEDS_METADATA` is **not** `NEEDS_REVISION`. It signals that the gate is
inapplicable, not that the document is broken.

## Flag Definitions

### Metadata Presence

- 🔴 **Fatal**: Frontmatter exists but is missing required fields
  (`last_reviewed`, `applies_to`, `owner`) without explanation.
- 🟡 **Warning**: Frontmatter exists with required fields but missing optional
  fields that would be useful (`mode`, `deprecated`, `superseded_by`).
- 🟢 **Clear**: All required fields present; optional fields used where relevant.

(If frontmatter is **entirely absent**, return `NEEDS_METADATA`, not a fatal flag.)

### Staleness (based on `last_reviewed`)

Compute age from `last_reviewed` to the current date.

- 🔴 **Fatal**: Age > 12 months (stale — blocking review required).
- 🟡 **Warning**: Age 6-12 months (warn — review scheduled).
- 🟢 **Clear**: Age < 6 months.

Projects with faster update cycles can tighten thresholds; projects with
stable systems can loosen them. The default thresholds are in
`standards/freshness-metadata.md` §Staleness Thresholds.

### Version Drift (based on `applies_to`)

Compare `applies_to` against the current system version.

- 🔴 **Fatal**: Major version behind current (`applies_to: v3.x.x` when
  current is `v4.0.0+`) — likely broken, needs rewrite.
- 🟡 **Warning**: Minor version behind (`applies_to: v3.2.x` when current is
  `v3.5.0`) — may need updating.
- 🟢 **Clear**: Applies-to matches current minor version or is explicitly
  marked as applicable to multiple versions.

### Cross-Reference Validity

- 🔴 **Fatal**: Internal links point to files that no longer exist; code
  references point to moved or renamed symbols.
- 🟡 **Warning**: Internal links exist but anchor IDs have changed; external
  links may be stale (not directly verified).
- 🟢 **Clear**: All internal links resolve; cross-references are valid.

## Verdict Rules

1. **NEEDS_METADATA**: No frontmatter at all (special verdict, not revision)
2. **NEEDS_REVISION**: Any 1 🔴 fatal flag
3. **NEEDS_REVISION**: 2 or more 🟡 warning flags
4. **PASS_WITH_NOTES**: Exactly 1 🟡 warning flag, no 🔴
5. **PASS**: All 🟢 clear

## Rules

- **Do not penalize new documents.** A doc created yesterday with today's
  `last_reviewed` date is fresh, even if it was just written. Age is the
  measure, not creation date.
- **Be honest about uncertainty.** If `applies_to: v3.x.x` and the current
  version is unclear from available context, flag as warning rather than
  fatal and ask for clarification.
- **External link checking is out of scope.** This gate does not make
  network requests. External link validity is a SHOULD (not enforceable here).
- **NEEDS_METADATA is not a failure.** It signals the gate can't apply.
  Treat it as "gate skipped" rather than "document broken."

## Output Format

For standard verdicts:

1. **Flags**: List each triggered flag with `[🔴 Dimension]` or `[🟡 Dimension]`
2. **Evidence**: Quote the relevant frontmatter field or link
3. **Fix instruction**: Update metadata, update reference, or review content
4. **Verdict**: PASS / PASS_WITH_NOTES / NEEDS_REVISION

For `NEEDS_METADATA`:

1. **Verdict**: NEEDS_METADATA
2. **Suggested metadata**: A frontmatter block the author can copy-paste and
   fill in
3. **Skip rationale template**: A sentence the author can use if they want to
   explicitly skip the gate

## Source

- `standards/freshness-metadata.md` — frontmatter convention and staleness thresholds
- [Software Engineering at Google — Chapter 10](https://abseil.io/resources/swe-book/html/ch10.html) — docs-rot and freshness-date practice
