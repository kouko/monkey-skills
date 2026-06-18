#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6"]
# ///
"""Emit the bundle's physical-anchor layer `knowledge/_relations.md`.

dbt-wiki:pack drops the `_evidence/` layer when freezing a bundle, so the
emitted `knowledge/` names dbt relations (`int_x.col`) but not the
schema-qualified table an analyst needs in a `FROM`. This script restores the
thin, high-value anchor: for every relation a knowledge page derives from, the
**schema + column list**, so a warehouse-connected agent at a repo-less target
can qualify the `FROM` without round-tripping.

Two layers of column data:
  - OFFLINE (default): schema + column NAMES + descriptions, read from the
    source `.dbt-wiki/_evidence/` pages (pack already stands on them). No
    manifest, no warehouse needed. Schema is the load-bearing piece — it is
    complete and stable.
  - --catalog (optional): real column TYPES from a live-warehouse
    `information_schema.columns` dump (the orchestrator runs the query with its
    own warehouse tool and passes the JSON here). Overrides the offline columns
    for relations it covers.

Usage:
  build_relations_anchor.py --evidence-dir <.dbt-wiki/_evidence> \\
      --knowledge-dir <bundle/knowledge> --out <bundle/knowledge/_relations.md> \\
      [--catalog <dump.json>]

The catalog dump is the JSON shape an execute-SQL tool returns for
  SELECT table_schema, table_name, ordinal_position, column_name, data_type
  FROM information_schema.columns WHERE ... ORDER BY 1,2,3
i.e. {"data": [{"table_schema","table_name","column_name","data_type", ...}]}.
"""
from __future__ import annotations
import argparse, glob, json, os, collections, sys
import yaml


def parse_frontmatter(path):
    txt = open(path, encoding="utf-8").read()
    if not txt.startswith("---"):
        return None
    parts = txt.split("---", 2)
    if len(parts) < 3:
        return None
    try:
        return yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return None


def main(argv=None):
    ap = argparse.ArgumentParser(description="Emit bundle knowledge/_relations.md physical anchor.")
    ap.add_argument("--evidence-dir", required=True, help=".dbt-wiki/_evidence directory")
    ap.add_argument("--knowledge-dir", required=True, help="bundle knowledge/ directory")
    ap.add_argument("--out", required=True, help="output path (…/knowledge/_relations.md)")
    ap.add_argument("--catalog", help="optional information_schema.columns JSON dump")
    args = ap.parse_args(argv)

    # --- index evidence pages by unique_id -> (relation_name, schema, [(col,type,desc)]) ---
    evidence = {}
    for sub in ("models", "sources", "seeds", "snapshots"):
        for p in glob.glob(os.path.join(args.evidence_dir, sub, "*.md")):
            fm = parse_frontmatter(p)
            if not fm or not fm.get("unique_id"):
                continue
            uid = fm["unique_id"]
            relname = fm.get("table_name") or uid.split(".")[-1]
            cols = []
            for c in (fm.get("columns") or []):
                if isinstance(c, dict) and c.get("name"):
                    cols.append((c["name"], c.get("type"), (c.get("description") or "").strip()))
            evidence[uid] = (relname, fm.get("schema"), cols)

    # --- cited relations from the bundle's knowledge derived_from ---
    cited = set()
    for p in glob.glob(os.path.join(args.knowledge_dir, "*.md")):
        base = os.path.basename(p)
        if base in ("INDEX.md", "_relations.md"):
            continue
        fm = parse_frontmatter(p)
        if fm:
            cited.update(fm.get("derived_from") or [])

    # --- optional live catalog: {(schema, table): [(col, type)]} ---
    catalog = collections.defaultdict(list)
    cat_meta = None
    if args.catalog and os.path.exists(args.catalog):
        cj = json.load(open(args.catalog, encoding="utf-8"))
        cat_meta = {k: cj.get(k) for k in ("total_count", "returned_count", "has_more")}
        for r in cj.get("data", []):
            catalog[(r.get("table_schema"), r.get("table_name"))].append(
                (r.get("column_name"), r.get("data_type")))

    rels = {}  # name -> (schema, source_tag, columns[(name,type)], desc_map)
    n_catalog = n_evidence = n_empty = 0
    for uid in cited:
        info = evidence.get(uid)
        if not info:
            continue
        relname, schema, ecols = info
        desc_map = {c: d for c, _, d in ecols if d}
        cat = catalog.get((schema, relname))
        if cat:
            cols = cat; tag = "live catalog"; n_catalog += 1
        elif ecols:
            cols = [(c, t) for c, t, _ in ecols]; tag = "evidence"; n_evidence += 1
        else:
            cols = []; tag = "live"; n_empty += 1
        rels[(schema, relname)] = (schema, relname, tag, cols, desc_map)

    by_schema = collections.Counter(k[0] for k in rels)
    out = ["# 實體錨點 (physical relations)", "",
           "> 每個知識頁引用到的 dbt relation → **schema + 欄位**，把 `model.column` 補成可跑的",
           "> `schema.table`。標 *live catalog* 的欄位型別來自即時倉儲；其餘為 evidence 欄位名或",
           "> 需對 live 反查。dev 環境把前綴的正式 schema 換成你的 dev schema。快照——重 pack 更新。", "",
           f"_共 {len(rels)} relation；schema：" +
           (", ".join(f"`{s}`×{c}" for s, c in by_schema.most_common()) or "—") +
           f"。欄位來源：live catalog ×{n_catalog}、evidence ×{n_evidence}、需反查 ×{n_empty}。_", ""]
    for key in sorted(rels):
        schema, relname, tag, cols, desc_map = rels[key]
        out.append(f"### `{schema}.{relname}`")
        if cols:
            line = f"欄位（{tag}）：" + ", ".join(
                f"`{c}`" + (f" *{t}*" if t else "") for c, t in cols)
            out.append(line)
            described = [(c, desc_map[c]) for c, _ in cols if c in desc_map]
            if described:
                out.append("")
                out.extend(f"- `{c}` — {d}" for c, d in described)
        else:
            out.append("_(本層未列欄位 → 對 live 倉儲反查 `information_schema.columns` / `SELECT … LIMIT 0`)_")
        out.append("")
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    open(args.out, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print(json.dumps({"relations": len(rels), "live_catalog": n_catalog, "evidence": n_evidence,
                      "needs_introspect": n_empty, "catalog_dump": cat_meta}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
