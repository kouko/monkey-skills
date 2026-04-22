# Anchor Library Lint Baseline — v1.13.2

**Run date**: 2026-04-22
**Lint script**: `scripts/lint-anchor-library.py`
**Total anchors scanned**: 90
**Clean**: 76 (84%)
**Clean with warnings**: 2
**Failed**: 12 (13%)

## Context

v1.13.2 audits lint's enforcement against actual runtime consumers in the pipeline. Earlier v1.13.0 baseline (71 clean / 19 failed) included two categories of spurious failures:

1. **`creator_type` missing (5 files)** — audit found zero runtime consumers for this frontmatter field (neither SKILL.md nor any rubric nor any agent reads the value). Dropped from required fields.

2. **`Over-mimic risk:` "missing" (3 files)** — files DID have the line, but with bold-wrapped values (`Over-mimic risk: **HIGH**`). Regex `([A-Z+\-]+)` failed to match through the `**` markup. Fixed regex to accept both plain and bold-wrapped forms.

Result: 8 false positives removed from failure set. Remaining 12 failures are real content/schema issues deferred to future releases.

## Runtime-consumer audit (v1.13.2)

Lint now enforces ONLY fields with verified runtime consumers:

| Field | Runtime consumer | Enforcement |
|---|---|---|
| `schema_version` (frontmatter) | Pass 3 Step 1 schema gate | REQUIRED |
| `anchor_slug` (frontmatter) | Pass 3 Step 2 candidate pool matching | REQUIRED |
| `culture` (frontmatter) | Pass 3 Step 2 filtering | REQUIRED |
| `quadrant` (frontmatter) | Pass 3 Step 2 filtering | REQUIRED |
| `landmark` (frontmatter) | Pass 3 Step 2 landmark-targeted read | REQUIRED |
| `Over-mimic risk:` (metadata body) | Pass 3 Step 6 safe-substitute + Dimension 6 gate | REQUIRED |
| `Cross-reference-valid-for:` (metadata body) | Pass 3 Step 1 cross-lang opt-in | OPTIONAL (no lint check) |
| `creator_type` (frontmatter) | — | NOT enforced (no consumer) |
| `Trigger slug:` (metadata body) | — | NOT enforced (no consumer; anchor files referenced by filename) |
| `Pairs with form:` (metadata body) | — | NOT enforced (no consumer) |

Body sections (required unconditionally, reflect v2 schema structure):
- `## Voice direction` with `**Native critical read**` bullet list (≥3 entries)
- `## Prose mechanics` (≥5 rules)
- `## Examples` (≥5 verbatim entries)
- `## Don't / Over-mimic` with Failure mode + Mitigation

## Failure breakdown (12)

### Missing `**Native critical read**` block (8 files)

Voice direction section lacks the bullet list of ≥3 verbatim-attributed phrases. Affected files:

- `anchor-en-david-abbott-economist-aphoristic.md`
- `anchor-en-richard-reed-innocent-wackaging.md`
- `anchor-en-tim-delaney-patek-philippe-stewardship.md`
- `anchor-en-wieden-just-do-it-minimal-imperative.md`
- `anchor-jp-hara-kenya-design-manifesto.md`
- `anchor-jp-jr-central-souda-kyoto-discovery.md`
- `anchor-jp-kurashicom-aoki-kohei-lifestyle-narrative.md`
- `anchor-jp-uniqlo-sato-kashiwa-lifewear.md`
- `anchor-zh-tw-nan-fang-shuo-lexical-archaeology.md`

Fix effort: primary-source research required per anchor (3-5 verbatim critical phrases with attribution). NOT mechanical.

### Non-standard quadrant format — dual-quadrant descriptive (2 files)

- `anchor-en-basecamp-fried-dhh-contrarian-manifesto.md` — `quadrant: dual (Q1 toward-Q2 manifesto + Q4 center plain-practical)`
- `anchor-en-schoolcraft-oatly-activist-typewriter.md` — `quadrant: dual (Q2 toward-Q3 activist manifesto + Q3 center irreverent peer)`

Fix effort: architectural decision. Options: (a) pick primary quadrant + demote secondary to prose; (b) extend schema to support `quadrant_primary` + `quadrant_secondary`; (c) split into two anchors.

### Examples count below 5 (1 file)

- `anchor-zh-hk-kc-tsang-cantonese-vernacular-pun.md` — only 3 verbatim entries

Fix effort: primary-source research; find 2+ more verbatim sources.

## Warnings (2 files) — non-blocking

Files that pass lint but surface non-canonical values (warnings only):

- `anchor-jp-taniyama-masakazu-discipline.md` — `quadrant: Q2-Q3` (edge designation; primary quadrant preferred)
- `anchor-jp-yoshimoto-banana-j-bungaku.md` — Over-mimic risk `'LOW-MEDIUM'` not in canonical set

These are acceptable; future release may normalize.

## Migration plan

**v1.13.2 (this release)**: lint rules aligned with runtime consumers. No anchor files edited; baseline reduced via correct lint.

**v1.14.x** (future): fix the 12 content/schema failures. Each requires research (primary-source verbatim + Native critical read phrases) or schema design decision (dual-quadrant handling).

## CI integration (future)

Once baseline is clean, wire `scripts/lint-anchor-library.py` to GitHub Actions:

```yaml
- name: Lint anchor library
  run: python copywriting-toolkit/scripts/lint-anchor-library.py
```

Exit codes:
- 0 — all files pass
- 1 — at least one ERROR (blocks merge)
- 2 — warnings only, `--strict` mode (soft block)

Until baseline is 0/90, CI can run informationally or use a baseline-exception-list mechanism (future enhancement).

## Reproducing this baseline

```bash
python copywriting-toolkit/scripts/lint-anchor-library.py 2>&1 | grep "^\[FAIL\]"
# Should list exactly the 12 files documented above.
```

If you see a DIFFERENT failure list:
- More failures: a new anchor was added with drift
- Different failures: an anchor was fixed (update this doc)
- Fewer failures: congrats, 12 → X progress (update this doc)

## Changes from v1.13.0 baseline

| Category | v1.13.0 | v1.13.2 | Change |
|---|---|---|---|
| Clean | 71 | 76 | +5 |
| Clean with warnings | 0 | 2 | +2 |
| Failed | 19 | 12 | −7 |
| Total | 90 | 90 | — |

No anchor file content modified. Pure lint rule audit.
