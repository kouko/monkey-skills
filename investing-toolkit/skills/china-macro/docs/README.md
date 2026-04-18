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
| `nbs-tree-monthly.txt` | Full monthly indicator tree (14 categories, ~600 leaves), name + UUID |
| `nbs-tree-quarterly.txt` | Full quarterly indicator tree (8 categories, ~120 leaves) |
| `nbs-tree-yearly.txt` | Full yearly indicator tree (28 categories, ~2200 leaves) |

Leaf `_id` in the tree files doubles as the `cid` value for
`POST getEsDataByCidAndDt`. Per-leaf indicator IDs must still be fetched
separately via `queryIndicatorsByCid?cid=<leaf_id>`.
