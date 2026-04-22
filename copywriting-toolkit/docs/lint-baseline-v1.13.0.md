# Anchor Library Lint Baseline — v1.13.0

**Run date**: 2026-04-22 (C2 commit in v1.13.0 PR)
**Lint script**: `scripts/lint-anchor-library.py`
**Total anchors scanned**: 90
**Clean**: 71 (79%)
**Failed**: 19 (21%)

## Context

v1.13.0 introduces `scripts/lint-anchor-library.py` to enforce v2 schema at library-entry time (moving curation off runtime per `voice-anchor-meta.md §Anchor selection rubric`). On introduction, the lint surfaces 19 pre-existing anchor files that drift from v2 schema. These are documented here as known baseline issues; they are NOT fixed in the v1.13.0 simplification PR to keep its scope focused.

**Runtime impact**: ZERO. Pass 3 already loads these anchors regardless of lint status; they currently work in pipeline runs. The lint is introduced as a forward-looking CI tool — future PRs MUST pass lint for newly-added or edited anchors, and existing baseline failures should be fixed incrementally.

## Failure categories

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

Fix effort: add 3-5 verbatim critical phrases per anchor (requires research; not mechanical).

### Missing `creator_type` frontmatter field (4 files)

- `anchor-jp-miyazawa-shinshou-sketch.md`
- `anchor-jp-sakamoto-yuji-kotoba-no-majutsushi.md`
- `anchor-jp-umeda-satoshi-uchinaru-kotoba.md`
- `anchor-zh-hk-kc-tsang-cantonese-vernacular-pun.md`
- `anchor-zh-hk-mike-chu-titus-cinematic-romance-inversion.md`

Fix effort: mechanical; add `creator_type: named copywriter` or equivalent to frontmatter.

### Missing `Over-mimic risk:` line (3 files)

- `anchor-en-kate-kiefer-lee-mailchimp-voice-tone.md`
- `anchor-jp-itoi-shigesato-state-proposal.md`
- `anchor-jp-taniyama-masakazu-discipline.md`

Fix effort: mechanical; assign risk level after content review.

### Non-standard quadrant format (2 files — dual-quadrant descriptive)

- `anchor-en-basecamp-fried-dhh-contrarian-manifesto.md` — `quadrant: dual (Q1 toward-Q2 manifesto + Q4 center plain-practical)`
- `anchor-en-schoolcraft-oatly-activist-typewriter.md` — `quadrant: dual (Q2 toward-Q3 activist manifesto + Q3 center irreverent peer)`

Fix effort: architectural decision needed. Options: (a) pick primary quadrant, demote secondary to prose note; (b) extend schema to support `quadrant_primary` + `quadrant_secondary` fields; (c) split into two anchors.

### Examples count below 5 (1 file)

- `anchor-zh-hk-kc-tsang-cantonese-vernacular-pun.md` — only 3 verbatim examples

Fix effort: research-dependent; find 2+ more verbatim sources.

## Migration plan

**v1.13.0 (this PR)**: introduce lint script, document baseline, NO fixes attempted.

**v1.13.x patches** (future): fix the mechanical failures (creator_type, Over-mimic risk) in batches. Each patch commit runs lint to verify no new failures introduced.

**v1.14.x** (future): fix content failures (missing Native critical read, dual-quadrant ambiguity, sparse Examples). These need research + schema-design decisions.

## CI integration (future)

Once baseline issues are resolved, wire `scripts/lint-anchor-library.py` into repo CI:

```yaml
# Example GitHub Actions step
- name: Lint anchor library
  run: python copywriting-toolkit/scripts/lint-anchor-library.py
```

Exit codes:
- 0 — all files pass
- 1 — at least one ERROR (blocks merge)
- 2 — warnings only, `--strict` mode (soft block)

Until baseline is clean, CI can use `|| true` to track without blocking, or use `--baseline=docs/lint-baseline-v1.13.0.md` style exception-listing (future enhancement).

## Reproducing this baseline

```bash
python copywriting-toolkit/scripts/lint-anchor-library.py 2>&1 | grep "^\[FAIL\]"
# Should list exactly the 19 files documented above.
```

If you see a DIFFERENT failure list, either (a) the lint was tightened, (b) new anchors were added, or (c) this baseline is stale. Update this doc.
