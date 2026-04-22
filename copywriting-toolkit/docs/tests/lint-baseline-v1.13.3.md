# Anchor Library Lint Baseline — v1.13.3

**Run date**: 2026-04-22
**Lint script**: `scripts/lint-anchor-library.py`
**Total anchors scanned**: 90
**Clean**: 85 (94%)
**Clean with warnings**: 2
**Failed**: 3 (3%)

## Context

v1.13.3 unifies anchor file format — all 90 anchors now use a single canonical structure. Pre-v1.13.3 the library mixed three format variations that accumulated during the v1.4.0-v1.12.x expansion:

1. **Native critical read placement** — 81 files used inline `**Native critical read**:` bold label nested in `## Voice direction`; 9 files used `## Native critical read` standalone H2 section. Both were lint-acceptable via v1.13.2 regex tolerance, but ran as two invisible sub-standards.
2. **Metadata grouping** — 85 files grouped fields under `## Metadata` H2; 5 files used flat `## Trigger slug: ...` / `## Over-mimic risk: ...` H2-per-field layout at the same level as main content sections.
3. **Voice direction opening label** — 88 files used `**What this register achieves**:`; 1 file used bilingual `**What this register achieves (中文)**:`; 1 file (Tim Delaney) had no label at all.

### Decision: Pattern B + grouped Metadata + English canonical label

After surveying sample files from all three craft-gate representatives (糸井 / 龔大中 / Ogilvy — all Pattern A) and Pattern B representatives (Abbott / Reed — both canonical style), chose **Pattern B (standalone H2)** as canonical despite Pattern A being the 81-file majority. Rationale:

- Semantic clarity: Native critical read is distinct function from Voice direction (evidence vs framing); independent H2 reflects this better
- Parseable structure: H2 headings are load-bearing Markdown; nested bold is decoration
- Lint simplicity: 1-step H2 lookup vs 2-step section-then-bold search

Cost: 81 file migrations vs 9. Paid via one-off mechanical migration script (no prose rewrite).

### Migration artefacts

- One-off migration script converted 81 Pattern A files to Pattern B (replaces `**Native critical read**[(N)]:` with `## Native critical read` H2). Deleted after use.
- 5 flat-metadata files (Miyazawa / Sakamoto / Umeda / KC Tsang / Mike Chu): manual conversion to grouped `## Metadata` with bullet items.
- 1 bilingual label (龔大中): manual fix to English canonical.
- 1 missing label (Tim Delaney): manual addition of `**What this register achieves**:` prefix.

## Runtime-consumer audit (unchanged from v1.13.2)

Lint enforces ONLY fields with verified runtime consumers:

| Field | Runtime consumer | Enforcement |
|---|---|---|
| `schema_version` (frontmatter) | Pass 3 Step 1 schema gate | REQUIRED |
| `anchor_slug` (frontmatter) | Pass 3 Step 2 candidate pool matching | REQUIRED |
| `culture` (frontmatter) | Pass 3 Step 2 filtering | REQUIRED |
| `quadrant` (frontmatter) | Pass 3 Step 2 filtering | REQUIRED |
| `landmark` (frontmatter) | Pass 3 Step 2 landmark-targeted read | REQUIRED |
| `Over-mimic risk:` (in ## Metadata) | Pass 3 Step 6 safe-substitute + Dimension 6 gate | REQUIRED |
| `Cross-reference-valid-for:` (in ## Metadata) | Pass 3 Step 1 cross-lang opt-in | OPTIONAL (no lint check) |
| `creator_type` (frontmatter) | — | NOT enforced (no consumer) |
| `Trigger slug:` (in ## Metadata) | — | NOT enforced (no consumer) |
| `Pairs with form:` (in ## Metadata) | — | NOT enforced (no consumer) |

### v1.13.3 canonical body structure (required, enforced by lint)

```
## Voice direction
**What this register achieves**: ...prose...

## Native critical read
- citation 1 (media, year)
- citation 2
- citation 3  (≥3)

## Prose mechanics
- rule 1
...  (≥5)

## Examples
- verbatim 1
...  (≥5)

## Don't / Over-mimic
- **Failure mode**: ...
- **Mitigation**: ...

## Metadata
- Trigger slug: ...
- Over-mimic risk: ...
- ...
```

Lint enforces all 6 H2 sections + canonical `**What this register achieves**:` label.

## Failure breakdown (3)

### Non-standard quadrant format — dual-quadrant descriptive (2 files)

- `anchor-en-basecamp-fried-dhh-contrarian-manifesto.md` — `quadrant: dual (Q1 toward-Q2 manifesto + Q4 center plain-practical)`
- `anchor-en-schoolcraft-oatly-activist-typewriter.md` — `quadrant: dual (Q2 toward-Q3 activist manifesto + Q3 center irreverent peer)`

Fix effort: architectural decision (deferred to v1.14.x). Options:
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

## CI integration (wired in v1.13.3)

CI lint gate lives in `.github/workflows/skill-structure.yml` → job `copywriting-anchor-lint`. On every push to `main` and every PR targeting `main`:

```yaml
- name: Lint voice anchor library (v1.13.3 canonical format)
  run: |
    python3 copywriting-toolkit/scripts/lint-anchor-library.py \
      --baseline copywriting-toolkit/scripts/lint-baseline.txt
```

### Baseline exception mechanism

`scripts/lint-baseline.txt` lists the 3 currently-accepted failures (2 dual-quadrant + 1 Examples<5). Under `--baseline` mode:

| Condition | Exit | CI behavior |
|---|---|---|
| Failures ⊆ baseline | 0 | ✅ PASS |
| New failure not in baseline | 1 | ❌ FAIL — block merge |
| Baseline entry now passes | 0 + nudge | ✅ PASS + reminder to prune baseline |

This lets CI block new drift while allowing progressive cleanup of existing debt.

### Updating the baseline

When an anchor in `lint-baseline.txt` is fixed, delete the line. CI will print a "baseline entries now passing" nudge until you prune, but does not fail. When adding a new accepted-failure (rare — should mostly happen when intentionally deferring research), add the filename + comment explaining rationale.

### Exit codes (existing, unchanged)

- 0 — all files pass (or all failures covered by baseline when `--baseline` used)
- 1 — at least one ERROR outside baseline (blocks merge)
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

v1.13.2 → v1.13.3 lint rules are STRICTER (single canonical format enforced). Clean count still rose because 9 Pattern B files that v1.13.2 lint false-positive-failed (misread as "missing Native critical read") are now genuinely clean under the canonical-only rule.

## Lint rule evolution

| Release | Native critical read | Metadata | What-this-label |
|---|---|---|---|
| v1.13.0 | Only Pattern A accepted (regex bug) | Either grouped or flat accepted | Not enforced |
| v1.13.2 | (unchanged) | (unchanged) | (unchanged) |
| v1.13.3 | Only Pattern B canonical (H2 required) | Only grouped ## Metadata | Canonical `**What this register achieves**:` required |

## Recursive dead-ceremony pattern (continued audit trail)

| Release | Issue | Resolution |
|---|---|---|
| v1.13.0 | Pass 3 4-condition rubric had no runtime consumer | Removed |
| v1.13.2 | `creator_type` / `Trigger slug` / `Pairs with form` enforced without runtime consumer | Dropped from lint |
| v1.13.2 | `Over-mimic risk: **HIGH**` regex failed through `**bold**` wrapping | Fixed regex |
| v1.13.3 | Two silent-alternative formats for Native critical read + Metadata | Unified to single canonical |

v1.13.3 closes the main format drift surface. Remaining 3 failures are substantive (schema design + content gap), not regex artefacts or silent-alternative formats.
