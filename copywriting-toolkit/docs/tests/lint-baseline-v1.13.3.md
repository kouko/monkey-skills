# Anchor Library Lint Baseline — v1.13.3

**Run date**: 2026-04-22
**Lint script**: `scripts/lint-anchor-library.py`
**Total anchors scanned**: 90
**Clean**: 85 (94%)
**Clean with warnings**: 2
**Failed**: 3 (3%)

## Context

v1.13.3 fixes a lint regex bug that flagged 9 anchors as "missing Native critical read" when they actually had complete, compliant content using a different valid structural pattern. This mirrors the v1.13.2 `Over-mimic risk: **HIGH**` regex bug — same dead-ceremony pattern: lint regex failed to match a format variation, then surfaced the variation as a content failure.

### Root cause

Two structurally valid patterns for `Native critical read` existed in the library since v1.4.0:

- **Pattern A** (糸井 / 龔大中 / Ogilvy / ~78 files): `**Native critical read**:` bold label nested inside `## Voice direction`
- **Pattern B** (Abbott / Reed / Wieden / Hara / 9 files): `## Native critical read` as standalone H2 section

v1.13.0 lint only matched Pattern A. All 9 Pattern B files had ≥3 entries with attribution (media + year in most cases), but lint reported `§Voice direction missing **Native critical read** block` — false positive.

### Fix

`check_native_critical_read` now tries Pattern B (standalone H2) first, falls back to Pattern A (inline bold). Both enforce ≥3 entries.

## Runtime-consumer audit (unchanged from v1.13.2)

Lint enforces ONLY fields with verified runtime consumers:

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
- `## Voice direction` — either inline `**Native critical read**` OR separate `## Native critical read` H2 section (≥3 entries)
- `## Prose mechanics` (≥5 rules)
- `## Examples` (≥5 verbatim entries)
- `## Don't / Over-mimic` with Failure mode + Mitigation

## Failure breakdown (3)

### Non-standard quadrant format — dual-quadrant descriptive (2 files)

- `anchor-en-basecamp-fried-dhh-contrarian-manifesto.md` — `quadrant: dual (Q1 toward-Q2 manifesto + Q4 center plain-practical)`
- `anchor-en-schoolcraft-oatly-activist-typewriter.md` — `quadrant: dual (Q2 toward-Q3 activist manifesto + Q3 center irreverent peer)`

Fix effort: architectural decision. Options:
- (a) pick primary quadrant + demote secondary to prose
- (b) extend schema to support `quadrant_primary` + `quadrant_secondary`
- (c) split into two anchors

Not content drift — the creators genuinely bridge two quadrants; schema currently has no clean way to express this.

### Examples count below 5 (1 file)

- `anchor-zh-hk-kc-tsang-cantonese-vernacular-pun.md` — only 3 verbatim entries

Fix effort: primary-source research; find 2+ more verbatim Cantonese ad examples from KC Tsang's TVB / Metro Radio catalogue.

## Warnings (2 files) — non-blocking

Files that pass lint but surface non-canonical values (warnings only):

- `anchor-jp-taniyama-masakazu-discipline.md` — `quadrant: Q2-Q3` (edge designation; primary quadrant preferred)
- `anchor-jp-umeda-satoshi-uchinaru-kotoba.md` — Over-mimic risk `'MEDIUM-HARD'` not in canonical set

These are acceptable; future release may normalize.

## Migration plan

**v1.13.3 (this release)**: lint regex bug fixed; 9 false-positive failures turned into genuine passes. Zero anchor files edited.

**v1.14.x** (future): address the 3 remaining real failures:
- 2 dual-quadrant → schema design decision
- 1 Examples < 5 → primary-source research (KC Tsang)

## CI integration (now feasible)

With only 3 remaining real failures, CI lint gate via baseline exception list becomes practical:

```yaml
- name: Lint anchor library
  run: python copywriting-toolkit/scripts/lint-anchor-library.py --baseline copywriting-toolkit/scripts/lint-baseline.txt
```

Baseline file lists the 3 known-failing anchors; new failures → PR block. Not wired yet in v1.13.3 (follow-up).

Exit codes (existing):
- 0 — all files pass
- 1 — at least one ERROR (blocks merge)
- 2 — warnings only, `--strict` mode (soft block)

## Reproducing this baseline

```bash
python copywriting-toolkit/scripts/lint-anchor-library.py 2>&1 | grep "^\[FAIL\]"
# Should list exactly the 3 files documented above.
```

If you see a DIFFERENT failure list:
- More failures: a new anchor was added with drift
- Different failures: an anchor was fixed (update this doc)
- Fewer failures: congrats, 3 → X progress (update this doc)

## Changes from v1.13.2 baseline

| Category | v1.13.2 | v1.13.3 | Change |
|---|---|---|---|
| Clean | 76 | 85 | +9 |
| Clean with warnings | 2 | 2 | — |
| Failed | 12 | 3 | −9 |
| Total | 90 | 90 | — |

No anchor file content modified. Pure lint regex fix — same class of bug as v1.13.2 `**HIGH**` bold-wrapped regex.

## Recursive dead-ceremony pattern

Three audits in a row have surfaced the same pattern:

| Release | What lint flagged | Actual cause | Fix |
|---|---|---|---|
| v1.13.0 | — (initial rollout) | — | — |
| v1.13.2 | `Over-mimic risk` "missing" on 3 files | Regex couldn't match through `**bold**` wrapping | Regex accepts bold |
| v1.13.2 | `creator_type` / `Trigger slug` / `Pairs with form` missing | Fields had zero runtime consumers | Drop from lint |
| v1.13.3 | `Native critical read` "missing" on 9 files | Regex only recognised one of two valid structural patterns | Regex accepts both |

Each audit removed ceremony that lint ADDED without checking against real library structure or runtime consumers. v1.13.3 should be the last round — remaining 3 failures are substantive (schema design + content gap), not regex artefacts.
