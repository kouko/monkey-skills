# Freshness Metadata (Shared Standard)

Frontmatter convention for documentation freshness tracking. Combats "docs rot"
— the gradual divergence between documentation and the system it describes.

Primary source: *Software Engineering at Google*, Chapter 10 ([abseil.io/resources/swe-book/html/ch10.html](https://abseil.io/resources/swe-book/html/ch10.html))

## The Problem: Docs Rot

From the Google SRE / SWE@Google tradition:

> "Such documents note the last time a document was reviewed, and metadata in
> the documentation set will send email reminders when the document hasn't
> been touched in, for example, three months."

Documentation silently decays. The code changes, but the docs describing it
don't. Readers trust stale docs and follow outdated instructions. The fix is
to **make staleness visible** via metadata, so readers can judge trustworthiness
and maintainers can prioritize updates.

## Frontmatter Convention

Every reference, how-to, tutorial, and explanation document should carry
freshness metadata in its YAML frontmatter:

```yaml
---
title: How to rotate API keys
last_reviewed: 2026-04-10
applies_to: v3.2.x
owner: docs-team
mode: how-to
---
```

### Required fields

| Field | Type | Purpose |
|-------|------|---------|
| `last_reviewed` | ISO 8601 date (`YYYY-MM-DD`) | When a human last verified the content against the current system |
| `applies_to` | version string | The system version this document is known to apply to |
| `owner` | team or person identifier | Who is responsible for keeping this doc current |

### Optional fields

| Field | Type | Purpose |
|-------|------|---------|
| `mode` | `tutorial` / `how-to` / `reference` / `explanation` / `composite` | Explicit Diátaxis quadrant declaration (checked by Mode Clarity gate) |
| `deprecated` | boolean or date | Marks the doc as deprecated; reader should look elsewhere |
| `superseded_by` | file path | Points to the replacement doc when deprecated |

## Staleness Thresholds

Freshness is judged by elapsed time since `last_reviewed`:

| Age | Status | Action |
|-----|--------|--------|
| < 6 months | 🟢 Fresh | No action |
| 6-12 months | 🟡 Warn | Review scheduled; owner notified |
| 12-24 months | 🔴 Stale | Review blocking; doc marked in UI |
| > 24 months | ⚫ Decommission candidate | Remove or rewrite |

These thresholds are default guidance. Projects with fast-changing APIs should
tighten them (3/6/12/18 months); projects with stable systems (reference docs
for finalized specs) can loosen them or set `applies_to` to an immutable version.

## Review vs Modification

**Important distinction**: `last_reviewed` is updated when a human **verifies**
the content is still accurate, not just when the file is edited. A typo fix
doesn't require re-verification; a substantive review does.

Two separate timestamps are possible:
- `last_modified` — git-derived, updated on every edit (no human action needed)
- `last_reviewed` — manually set, only when a human audits correctness

Most projects only need `last_reviewed`. Use `last_modified` from git metadata
if a comparison is needed.

## Version Drift: `applies_to`

`applies_to` tracks which system version the doc was verified against. When
the current system version moves past `applies_to`, the doc may still work
but hasn't been verified against the new version.

Example:
```yaml
applies_to: v3.2.x
```

If the current version is v3.5.0, the doc is three minor versions behind and
should be reviewed. If the current version is v4.0.0, the doc is likely broken
(major version bump) and should be rewritten or marked deprecated.

## Cross-Reference Validity

Beyond frontmatter metadata, freshness also includes **link validity**:

- Internal links point to files that still exist
- External links return 200 OK (or the doc explicitly flags archived links)
- Code references (file paths, line numbers) still match the current code

The Freshness MAY gate (`rubrics/freshness.md`) can optionally check these
via a link checker, but requires the evaluator to have filesystem access.

## No Metadata → `NEEDS_METADATA`, Not `NEEDS_REVISION`

When the Freshness gate runs on a document that has no frontmatter at all,
it should return a special `NEEDS_METADATA` verdict rather than
`NEEDS_REVISION`. This signals that the gate cannot apply, not that the
document is stale.

The expected response to `NEEDS_METADATA` is: either add frontmatter using
this standard, or skip the Freshness gate for this document with a stated
reason (e.g., "README doesn't need last_reviewed because it's maintained
continuously via PRs").

## Adoption Strategy

Adopting freshness metadata is incremental:

1. **Start with reference docs** — they rot fastest and have the clearest
   contract with code
2. **Add to how-to guides next** — they often encode specific version behaviors
3. **Tutorials last** — they touch many features at once and are reviewed
   holistically
4. **Skip explanation** — Explanation docs discuss design and rarely go stale
   unless the design itself changes (in which case a new explanation is written)

## Sources

- [Software Engineering at Google — Chapter 10: Documentation](https://abseil.io/resources/swe-book/html/ch10.html) — primary source for docs-rot and freshness-date practice
- [Write the Docs — Documentation principles: Canonical](https://www.writethedocs.org/guide/writing/docs-principles/) — "Incorrect documentation is worse than missing documentation"
