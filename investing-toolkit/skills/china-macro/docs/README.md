# china-macro / docs

Developer-facing reference material. Not loaded by the skill at runtime —
kept here so future implementation work (e.g. a supplementary
`nbs_client.py` to replace stale akshare mirrors for industrial / trade
indicators) can consult it without re-discovering the NBS API under WAF
pressure.

User-facing indicator descriptions live in `../references/`. Those are
referenced by `SKILL.md` and consumed by Claude. The files here are
for humans browsing the repo.

## Files

| File | Purpose |
|---|---|
| `nbs-indicator-catalog.md` | Reverse-engineered `data.stats.gov.cn` new-SPA API: endpoint contracts, `dts` range syntax, session/cookie rules, WAF behaviour, akshare↔NBS preset mapping, worked CPI example |
| `nbs-tree-monthly.md` | Monthly catalog tree (14 top categories, 605 leaf tables) — folders and leaves with their UUIDs |
| `nbs-tree-quarterly.md` | Quarterly tree (8 categories, 116 leaves) |
| `nbs-tree-yearly.md` | Yearly tree (28 categories, 2187 leaves) |
| `nbs-indicators-monthly.{json,md}` | Full indicator UUID catalog for every monthly leaf (605 cids, ~15k indicator rows) |
| `nbs-indicators-quarterly.{json,md}` | 116 cids, ~3k indicators |
| `nbs-indicators-yearly.{json,md}` | 2187 cids, ~57k indicators |
| `tools/` | One-shot admin scripts used to capture the above catalogs. See `tools/README.md` for when to re-run. |

### How the two catalog layers fit

- `nbs-tree-*.md` — the NBS catalog **tree**. Folders for navigation,
  leaves represent statistical tables. The leaf `_id` is the `cid`
  parameter in the runtime API.
- `nbs-indicators-*.{json,md}` — the **inside** of each leaf table.
  Each row is a separate statistical indicator with its own UUID. Those
  UUIDs go into the `indicatorIds[]` array of
  `POST getEsDataByCidAndDt`.

Together, the tree tells you which `cid` to pass and the indicator
catalog tells you which `indicatorIds[]` to pass. A runtime
`nbs_client.py` hardcodes `(cid, indicatorIds[])` tuples per preset to
avoid runtime discovery (which is WAF-sensitive).

### Totals (2026-04-18 capture)

- **2908 leaf tables** (`cid`s) across monthly/quarterly/yearly
- **~75,719 distinct indicators** (`indicatorId`s)
- Avg ~26 indicators per leaf (CPI has 13, small tables have 1-3,
  cross-tabs like 分行業工業經濟指標 have 80+)
