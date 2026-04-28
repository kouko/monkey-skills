# korea-macro/docs

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

Developer-facing documentation and tooling for maintaining `korea-macro`.

## Contents

### Catalogue

- **`bok-ecos-keystat-catalog.md`** — Human-readable catalogue of all 98
  BOK ECOS KEYSTAT codes accessible via `FinanceDataReader` without an
  API key. Grouped by category (monetary, rates, markets, FX, activity,
  CI, labor, BoP, prices, demographics).
- **`bok-ecos-keystat.json`** — Raw JSON from `probe-keystat.py`,
  ready to be re-imported or diffed after BOK updates KEYSTAT.

### Tools

- **`tools/probe-keystat.py`** — Re-probe KEYSTAT catalogue (sweeps
  `K001-K500` by default). Re-run when BOK adds new key indicators.

## Maintenance

When BOK updates KEYSTAT (rare, ~1-2 per year), re-run the probe and
diff the output against the committed JSON:

```bash
cd investing-toolkit/skills/korea-macro/docs/tools
uv run probe-keystat.py
diff <(jq --sort-keys . ../bok-ecos-keystat.json) <(jq --sort-keys . ../bok-ecos-keystat.json.new)
```

If there are additions, update `bok-ecos-keystat-catalog.md` with the
new rows and decide whether any should become presets (see `SKILL.md`
for the 10-group structure as of v1.8.0).

## Full ECOS vs KEYSTAT

This documentation covers **KEYSTAT only** (BOK's curated 100대 통계지표
subset, ~98 codes). The full BOK ECOS catalogue (10,000+ series)
requires an API key. See the "Why not the full ECOS catalog?" section at
the bottom of `bok-ecos-keystat-catalog.md`.
