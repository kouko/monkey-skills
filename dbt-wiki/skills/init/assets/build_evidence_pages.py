#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Emit the dbt-wiki EVIDENCE layer deterministically from manifest.json +
the sqlglot/comment JSONL extractions.

dbt-wiki ships this script as a plugin asset. /dbt-wiki:init copies it to
.dbt-wiki/_internal/build_evidence_pages.py and invokes it once to write
EVERY evidence page (models / sources / used-macros / seeds / singular
tests) plus index.md and lineage.md — per the `model` / `source` / `macro`
/ `seed` / `test` page contracts in SCHEMA.md.

This exists because hand-writing one page per model is infeasible beyond a
few dozen models (real projects have hundreds–thousands); the page shape is
fully derivable from manifest.json + the JSONL outputs, so it should be
mechanical and reproducible, not authored by hand.

Pure stdlib — no third-party dependency (sqlglot work already happened in the
upstream extraction scripts, whose JSONL this consumes). Runs identically
under `uv run` or plain `python3`.

Inputs
------
  --manifest PATH           target/manifest.json (required)
  --wiki-dir PATH           the .dbt-wiki/ directory (required; pages written under it)
  --dbt-dir PATH            dbt project root (for repo-relative `path:` frontmatter; required)
  --col-lineage PATH        JSONL from extract_column_lineage.py --batch (optional)
  --comments PATH           JSONL from extract_sql_comments.py --batch (optional)
  --recursive-lineage PATH  JSONL from extract_recursive_column_lineage.py (optional)
  --project-name NAME       dbt package name (optional; default = manifest metadata.project_name)
  --today YYYY-MM-DD        date stamp (optional; default = today)

Output
------
Writes .dbt-wiki/_evidence/{models,sources,macros,seeds,tests}/*.md + index.md
+ lineage.md, and prints a stats JSON object to stdout (consumed by the init
SKILL for the log.md entry).
"""
from __future__ import annotations

import argparse
import collections
import datetime
import hashlib
import json
import os
import sys


def jq(s):
    """Emit a string as a YAML-safe scalar (a JSON string is valid YAML)."""
    return json.dumps("" if s is None else str(s), ensure_ascii=False)


def load_jsonl(path):
    out = []
    if not path or not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


TIER_ORDER = ["staging", "intermediate", "interm", "marts", "snapshots"]
TIER_LABEL = {"staging": "Staging", "intermediate": "Intermediate", "interm": "Intermediate",
              "marts": "Marts", "snapshots": "Snapshots"}


def tier_label(tier):
    return TIER_LABEL.get(tier, tier.replace("_", " ").title())


def render_tree(tree, uid_to_name, indent=2):
    """Render an extract_recursive_column_lineage tree as markdown bullets."""
    lines = []
    pad = " " * indent
    for key, sub in tree.items():
        if key in ("_cycle", "_max_depth"):
            lines.append(f"{pad}- _{key.strip('_')}_")
            continue
        parts = key.split("::")
        if parts[0] == "_unresolved":
            label = f"`{parts[1]}.{parts[2]}` *(unresolved)*" if len(parts) >= 3 else f"`{key}`"
        else:
            uid = parts[0]
            col = parts[1] if len(parts) > 1 else ""
            short = uid_to_name.get(uid, uid)
            kind = uid.split(".")[0]
            tag = {"source": " *(source)*", "seed": " *(seed)*", "snapshot": " *(snapshot)*"}.get(kind, "")
            label = f"`{short}.{col}`{tag}"
        lines.append(f"{pad}- {label}")
        if sub:
            lines.extend(render_tree(sub, uid_to_name, indent + 2))
    return lines


def main(argv=None):
    ap = argparse.ArgumentParser(description="Emit dbt-wiki evidence layer from manifest + JSONL.")
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--wiki-dir", required=True)
    ap.add_argument("--dbt-dir", required=True)
    ap.add_argument("--col-lineage")
    ap.add_argument("--comments")
    ap.add_argument("--recursive-lineage")
    ap.add_argument("--project-name")
    ap.add_argument("--today")
    args = ap.parse_args(argv)

    today = args.today or datetime.date.today().isoformat()
    wiki = os.path.abspath(args.wiki_dir)
    ev = os.path.join(wiki, "_evidence")
    for sub in ("models", "sources", "macros", "seeds", "snapshots", "tests"):
        os.makedirs(os.path.join(ev, sub), exist_ok=True)

    repo_root = os.path.dirname(wiki)
    dbt_rel = os.path.relpath(os.path.abspath(args.dbt_dir), repo_root)

    def repo_path(ofp):
        return f"{dbt_rel}/{ofp}"

    with open(args.manifest, encoding="utf-8") as f:
        man = json.load(f)
    manifest_sha = hashlib.md5(open(args.manifest, "rb").read()).hexdigest()
    project = args.project_name or (man.get("metadata") or {}).get("project_name") or "project"

    col_lineage = {r["path"]: r["result"] for r in load_jsonl(args.col_lineage)}
    comments = {r["path"]: r["comments"] for r in load_jsonl(args.comments)}
    recursive = collections.defaultdict(dict)
    for r in load_jsonl(args.recursive_lineage):
        recursive[r["model_uid"]][r["column"]] = {"ancestors": r.get("ancestors", {}),
                                                  "descendants": r.get("descendants", {})}

    nodes = man.get("nodes", {})
    sources = man.get("sources", {})
    macros = man.get("macros", {})
    # manifest nodes carry unique_id, but be defensive: guarantee it's present
    for u, n in nodes.items():
        n.setdefault("unique_id", u)
    models = {u: n for u, n in nodes.items() if n.get("resource_type") == "model"}
    seeds = {u: n for u, n in nodes.items() if n.get("resource_type") == "seed"}
    snapshots = {u: n for u, n in nodes.items() if n.get("resource_type") == "snapshot"}
    tests = {u: n for u, n in nodes.items() if n.get("resource_type") == "test"}
    singular_tests = {u: n for u, n in tests.items() if n.get("test_metadata") is None}
    generic_tests = {u: n for u, n in tests.items() if n.get("test_metadata") is not None}

    uid_to_name = {u: n.get("name") for u, n in nodes.items()}
    for u, s in sources.items():
        uid_to_name[u] = f'{s["source_name"]}.{s["name"]}'
    macro_label = {}
    for u, m in macros.items():
        pkg, nm = m["package_name"], m["name"]
        macro_label[u] = nm if pkg == project else f"{pkg}.{nm}"
    src_lookup = {(s["source_name"], s["name"]): u for u, s in sources.items()}

    def comment_for(ofp):
        if ofp in comments:
            return comments[ofp]
        # comments JSONL is keyed relative to the models dir root → strip first segment
        if "/" in ofp:
            return comments.get(ofp.split("/", 1)[1], [])
        return []

    # reverse maps
    feeds_into = collections.defaultdict(list)
    for u, n in list(models.items()) + list(snapshots.items()):
        for dep in n.get("depends_on", {}).get("nodes", []):
            feeds_into[dep].append(n["name"])
        for sn, tn in n.get("sources", []):
            su = src_lookup.get((sn, tn))
            if su:
                feeds_into[su].append(n["name"])
    for k in feeds_into:
        feeds_into[k] = sorted(set(feeds_into[k]))

    macro_used_by = collections.defaultdict(list)
    for u, n in models.items():
        for muid in n.get("depends_on", {}).get("macros", []):
            macro_used_by[muid].append(n["name"])
    for k in macro_used_by:
        macro_used_by[k] = sorted(set(macro_used_by[k]))

    tests_by_model = collections.defaultdict(list)
    for u, t in generic_tests.items():
        target = t.get("attached_node")
        if not target:
            mdeps = [d for d in t.get("depends_on", {}).get("nodes", []) if d.startswith("model.")]
            if len(mdeps) == 1:
                target = mdeps[0]
        if target:
            tests_by_model[target].append({"name": (t.get("test_metadata") or {}).get("name") or t["name"],
                                           "column": t.get("column_name")})
    singular_by_model = collections.defaultdict(list)
    for u, t in singular_tests.items():
        for d in t.get("depends_on", {}).get("nodes", []):
            if d.startswith("model."):
                singular_by_model[d].append(t["name"])

    name_counts = collections.Counter(n["name"] for n in models.values())
    model_file_by_uid = {}
    for u, n in models.items():
        model_file_by_uid[u] = (f'{n["package_name"]}__{n["name"]}.md'
                                if name_counts[n["name"]] > 1 else f'{n["name"]}.md')

    def tier_of(n):
        parts = n["original_file_path"].split("/")
        return parts[1] if len(parts) >= 2 and parts[0] == "models" else "other"

    sqlglot_ok = sqlglot_failed = sqlglot_none = 0
    written = collections.Counter()

    # ---- model pages ----
    for u, n in models.items():
        ofp = n["original_file_path"]
        cfg = n.get("config", {})
        cl = col_lineage.get(ofp, {})
        if "_error" in cl:
            extraction = "failed"; sqlglot_failed += 1; cl = {}
        elif not cl:
            extraction = "schema_yml_only"; sqlglot_none += 1
        else:
            extraction = "sqlglot"; sqlglot_ok += 1

        schema_cols = {c["name"]: c for c in n.get("columns", {}).values()}
        all_cols = sorted(set(schema_cols) | set(k for k in cl if k != "_error"))
        col_tests = collections.defaultdict(list)
        model_level_tests = []
        for t in tests_by_model.get(u, []):
            (col_tests[t["column"]].append(t["name"]) if t["column"] else model_level_tests.append(t["name"]))

        refs, src_deps, mac_deps = [], [], []
        for d in n.get("depends_on", {}).get("nodes", []):
            if d.startswith(("model.", "seed.", "snapshot.")):
                refs.append(uid_to_name.get(d, d))
        for sn, tn in n.get("sources", []):
            src_deps.append(f"{sn}.{tn}")
        for muid in n.get("depends_on", {}).get("macros", []):
            mac_deps.append(macro_label.get(muid, muid))
        refs, src_deps, mac_deps = sorted(set(refs)), sorted(set(src_deps)), sorted(set(mac_deps))

        fm = ["---", f"unique_id: {u}", "type: model", f'package: {n["package_name"]}',
              f"path: {repo_path(ofp)}", f'materialization: {cfg.get("materialized")}',
              f'schema: {n.get("schema")}', f'database: {jq(n.get("database"))}',
              f'tags: {json.dumps(cfg.get("tags") or [], ensure_ascii=False)}',
              f'group: {jq(n.get("group")) if n.get("group") else "null"}',
              f'access: {n.get("access")}',
              f'contract_enforced: {str((n.get("contract") or {}).get("enforced", False)).lower()}',
              f"last_updated: {today}", f"manifest_sha: {manifest_sha}",
              f"columns_extracted_via: {extraction}", "columns:"]
        for c in all_cols:
            sc = schema_cols.get(c, {})
            fm.append(f"  - name: {jq(c)}")
            fm.append(f'    type: {jq(sc.get("data_type")) if sc.get("data_type") else "null"}')
            if sc.get("description"):
                fm.append(f'    description: {jq(sc["description"])}')
            fm.append(f"    declared_in_schema_yml: {str(c in schema_cols).lower()}")
            if col_tests.get(c):
                fm.append(f"    tests: {json.dumps(sorted(set(col_tests[c])), ensure_ascii=False)}")
            if cl.get(c):
                fm.append("    sources:")
                for s in cl[c]:
                    fm.append(f"      - {jq(s)}")
        fm.append("depends_on:")
        fm.append("  refs:")
        for r in refs: fm.append(f"    - {jq(r)}")
        fm.append("  sources:")
        for s in src_deps: fm.append(f"    - {jq(s)}")
        fm.append("  macros:")
        for m in mac_deps: fm.append(f"    - {jq(m)}")
        fm.append("feeds_into:")
        for d in feeds_into.get(u, []): fm.append(f"  - {jq(d)}")
        fm.append("generic_tests:")
        for t in sorted(set(model_level_tests)): fm.append(f"  - {jq(t)}")
        fm.append("recorded_decisions: []")
        fm.append("---")

        body = ["\n## Description", n.get("description") or "_No description in schema.yml._",
                "\n## Materialization Notes"]
        mat = [f"- **{k}**: `{json.dumps(cfg[k], ensure_ascii=False)}`"
               for k in ("materialized", "incremental_strategy", "unique_key", "sort", "sort_type",
                         "dist", "on_schema_change", "persist_docs", "tags")
               if cfg.get(k) not in (None, [], {}, "")]
        body.append("\n".join(mat) if mat else "_Default materialization config._")
        raw = (n.get("raw_code") or "").splitlines()
        more = f"\n-- … ({len(raw)} lines total; see {repo_path(ofp)})" if len(raw) > 30 else ""
        body += ["\n## SQL Preview", f"```sql\n{chr(10).join(raw[:30])}{more}\n```",
                 "\n## Inline Comments (from raw_code)"]
        cmts = comment_for(ofp)
        body.append("```\n" + "\n".join(f"[line {c['line']}] {c['text']}" for c in cmts) + "\n```"
                    if cmts else "_No inline comments in source._")
        body.append("\n## Column Sources (from sqlglot — direct, single-hop)")
        cs = [f"- {c} ← {', '.join(srcs)}" for c, srcs in cl.items() if c != "_error" and srcs]
        body.append("\n".join(cs) if cs else "_No column sources extracted._")
        body.append("\n## Column Lineage Chains (recursive, full DAG)")
        rec = recursive.get(u, {})
        chains = []
        for col in sorted(rec):
            anc, desc = rec[col]["ancestors"], rec[col]["descendants"]
            if not anc and not desc:
                continue
            chains.append(f"\n### {col}")
            if anc:
                chains.append("**Ancestors** (where this column comes from):")
                chains += render_tree(anc, uid_to_name)
            if desc:
                chains.append("\n**Descendants** (where this column flows to):")
                chains += render_tree(desc, uid_to_name)
        body.append("\n".join(chains) if chains else "_No recursive lineage available._")
        body += ["\n## Tests",
                 f"- Column-level: {sum(len(v) for v in col_tests.values())}; see frontmatter `columns[].tests`",
                 f"- Model-level: {len(set(model_level_tests))}; see frontmatter `generic_tests`",
                 f"- Singular tests: {', '.join(singular_by_model.get(u, [])) or 'none'}"]
        up = ", ".join(f"[{uid_to_name.get(d, d)}]({model_file_by_uid.get(d, uid_to_name.get(d, d) + '.md')})"
                       for d in n.get("depends_on", {}).get("nodes", []) if d.startswith("model."))
        down = ", ".join(f"[{dn}]({dn}.md)" for dn in feeds_into.get(u, []))
        body += ["\n## Cross-references", f"- Upstream models: {up or 'none'}",
                 f"- Downstream models: {down or 'none'}"]

        with open(os.path.join(ev, "models", model_file_by_uid[u]), "w", encoding="utf-8") as fh:
            fh.write("\n".join(fm) + "\n" + "\n".join(body) + "\n")
        written["models"] += 1

    # ---- source pages ----
    for u, s in sources.items():
        fm = ["---", f"unique_id: {u}", "type: source",
              f'source_name: {jq(s["source_name"])}', f'table_name: {jq(s["name"])}',
              f'schema: {jq(s.get("schema"))}', f'database: {jq(s.get("database"))}']
        if s.get("loaded_at_field"):
            fm.append(f'loaded_at_field: {jq(s["loaded_at_field"])}')
        fr = s.get("freshness") or {}
        wa, ea = (fr.get("warn_after") or {}), (fr.get("error_after") or {})
        if wa.get("count") or ea.get("count"):
            fm.append("freshness:")
            if wa.get("count"):
                fm.append(f'  warn_after: {{ count: {wa["count"]}, period: {wa["period"]} }}')
            if ea.get("count"):
                fm.append(f'  error_after: {{ count: {ea["count"]}, period: {ea["period"]} }}')
        fm.append("columns:")
        for c in s.get("columns", {}).values():
            fm.append(f'  - name: {jq(c["name"])}')
            if c.get("description"):
                fm.append(f'    description: {jq(c["description"])}')
        fm.append("feeds_into:")
        for d in feeds_into.get(u, []):
            fm.append(f"  - {jq(d)}")
        fm += [f"last_updated: {today}", "---"]
        body = ["\n## Description", s.get("description") or "_No description in sources.yml._",
                "\n## Feeds Into",
                "\n".join(f"- [{d}](../models/{d}.md)" for d in feeds_into.get(u, []))
                or "_No models depend on this source._"]
        with open(os.path.join(ev, "sources", f'{s["source_name"]}__{s["name"]}.md'), "w", encoding="utf-8") as fh:
            fh.write("\n".join(fm) + "\n" + "\n".join(body) + "\n")
        written["sources"] += 1

    # ---- macro pages (used by >=1 model) ----
    for u in sorted(uu for uu in macro_used_by if macro_used_by[uu]):
        m = macros.get(u)
        if not m:
            continue
        args_list = [a["name"] for a in (m.get("arguments") or [])]
        fm = ["---", f"unique_id: {u}", "type: macro", f'package: {m["package_name"]}',
              f'path: {jq(m.get("original_file_path"))}',
              f"arguments: {json.dumps(args_list, ensure_ascii=False)}",
              f'description: {jq(m.get("description"))}',
              f"used_by_models: {json.dumps(macro_used_by[u], ensure_ascii=False)}",
              f"last_updated: {today}", "---"]
        body = ["\n## Description", m.get("description") or "_No macro description._",
                f"\n## Used By ({len(macro_used_by[u])} models)",
                ", ".join(macro_used_by[u][:50]) + (" …" if len(macro_used_by[u]) > 50 else "")]
        pkg, nm = m["package_name"], m["name"]
        fn = f"{nm}.md" if pkg == project else f"{pkg}__{nm}.md"
        with open(os.path.join(ev, "macros", fn), "w", encoding="utf-8") as fh:
            fh.write("\n".join(fm) + "\n" + "\n".join(body) + "\n")
        written["macros"] += 1

    # ---- seed pages ----
    for u, n in seeds.items():
        fm = ["---", f"unique_id: {u}", "type: seed", f'package: {n["package_name"]}',
              f'path: {repo_path(n["original_file_path"])}', f'schema: {n.get("schema")}', "columns:"]
        for c in n.get("columns", {}).values():
            fm.append(f'  - name: {jq(c["name"])}')
            if c.get("description"):
                fm.append(f'    description: {jq(c["description"])}')
        fm.append("feeds_into:")
        for d in feeds_into.get(u, []):
            fm.append(f"  - {jq(d)}")
        fm += [f"last_updated: {today}", "---"]
        body = ["\n## Description", n.get("description") or "_No description._",
                "\n## Feeds Into",
                "\n".join(f"- [{d}](../models/{d}.md)" for d in feeds_into.get(u, []))
                or "_No models depend on this seed._"]
        with open(os.path.join(ev, "seeds", f'{n["name"]}.md'), "w", encoding="utf-8") as fh:
            fh.write("\n".join(fm) + "\n" + "\n".join(body) + "\n")
        written["seeds"] += 1

    # ---- snapshot pages ----
    for u, n in snapshots.items():
        fm = ["---", f"unique_id: {u}", "type: snapshot", f'package: {n["package_name"]}',
              f'path: {repo_path(n["original_file_path"])}', f'schema: {n.get("schema")}',
              "feeds_into:"]
        for d in feeds_into.get(u, []):
            fm.append(f"  - {jq(d)}")
        fm += [f"last_updated: {today}", "---"]
        body = ["\n## Description", n.get("description") or "_No description._"]
        with open(os.path.join(ev, "snapshots", f'{n["name"]}.md'), "w", encoding="utf-8") as fh:
            fh.write("\n".join(fm) + "\n" + "\n".join(body) + "\n")
        written["snapshots"] += 1

    # ---- singular test pages ----
    for u, t in singular_tests.items():
        tested = sorted(uid_to_name.get(d, d) for d in t.get("depends_on", {}).get("nodes", [])
                        if d.startswith(("model.", "source.")))
        fm = ["---", f"unique_id: {u}", "type: test", f'name: {jq(t["name"])}',
              f'package: {t["package_name"]}', f'path: {repo_path(t["original_file_path"])}',
              f"tests_resource: {json.dumps(tested, ensure_ascii=False)}",
              f"last_updated: {today}", "---"]
        raw = (t.get("raw_code") or "").splitlines()
        body = ["\n## Description", t.get("description") or "_Singular (bespoke) data test._",
                "\n## Tests", "\n".join(f"- {x}" for x in tested) or "_No direct refs._",
                "\n## SQL Preview", "```sql\n" + "\n".join(raw[:40]) + ("\n-- …" if len(raw) > 40 else "") + "\n```"]
        with open(os.path.join(ev, "tests", f'{t["name"]}.md'), "w", encoding="utf-8") as fh:
            fh.write("\n".join(fm) + "\n" + "\n".join(body) + "\n")
        written["tests"] += 1

    total_models = len(models)

    # ---- group helpers ----
    by_tier, by_mat, by_tag, by_group = (collections.defaultdict(list) for _ in range(4))
    for u, n in models.items():
        by_tier[tier_of(n)].append(n)
        by_mat[n.get("config", {}).get("materialized")].append(n)
        for t in (n.get("config", {}).get("tags") or []):
            by_tag[t].append(n)
        if n.get("group"):
            by_group[n["group"]].append(n)
    ordered_tiers = [t for t in TIER_ORDER if t in by_tier] + sorted(set(by_tier) - set(TIER_ORDER))

    # ---- index.md ----
    idx = ["---", "title: dbt-wiki Index", "type: index", f"last_updated: {today}",
           f"manifest_sha: {manifest_sha}", "---", "", "# dbt-wiki Index", "",
           "> Knowledge-first catalog. Regenerated on every `/dbt-wiki:init` / `/dbt-wiki:refresh`. Do not edit by hand.", "",
           "## Entities", "", "_(Phase B knowledge distillation populates this.)_", "",
           "## Metrics", "", "_(Phase B knowledge distillation populates this.)_", "",
           "## Concepts", "", "_(Phase B knowledge distillation populates this.)_", "",
           "## Evidence: Models", ""]
    for tier in ordered_tiers:
        idx.append(f"### {tier_label(tier)} (`models/{tier}/`) — {len(by_tier[tier])}")
        for n in sorted(by_tier[tier], key=lambda x: x["name"]):
            idx.append(f'- [{n["name"]}](_evidence/models/{model_file_by_uid[n["unique_id"]]}) `{n.get("config", {}).get("materialized")}`')
        idx.append("")
    idx.append("## Evidence: Models by Materialization\n")
    for mat in sorted(by_mat, key=lambda x: (x is None, x)):
        idx.append(f"### {mat} — {len(by_mat[mat])}")
        idx.append(", ".join(sorted(x["name"] for x in by_mat[mat])) + "\n")
    idx.append("## Evidence: Models by Tag\n")
    idx.append("\n".join(f"### {t} — {len(by_tag[t])}\n{', '.join(sorted(x['name'] for x in by_tag[t]))}\n"
                         for t in sorted(by_tag)) if by_tag else "_No tags configured._\n")
    idx.append("## Evidence: Models by Group\n")
    idx.append("\n".join(f"### {g} — {len(by_group[g])}\n{', '.join(sorted(x['name'] for x in by_group[g]))}\n"
                         for g in sorted(by_group)) if by_group else "_No groups configured._\n")
    idx.append("## Evidence: Sources\n")
    by_srcname = collections.defaultdict(list)
    for u, s in sources.items():
        by_srcname[s["source_name"]].append(s)
    for sn in sorted(by_srcname):
        idx.append(f"### {sn} — {len(by_srcname[sn])}")
        for s in sorted(by_srcname[sn], key=lambda x: x["name"]):
            idx.append(f'- [{sn}.{s["name"]}](_evidence/sources/{sn}__{s["name"]}.md)')
        idx.append("")
    idx.append(f"## Evidence: Macros (used) — {written['macros']}\n")
    used = [u for u in macro_used_by if macro_used_by[u] and u in macros]
    proj_m = sorted(macros[u]["name"] for u in used if macros[u]["package_name"] == project)
    ext_m = sorted(f'{macros[u]["package_name"]}.{macros[u]["name"]}' for u in used if macros[u]["package_name"] != project)
    idx.append("**Project macros**: " + (", ".join(proj_m) or "none") + "\n")
    idx.append("**External package macros**: " + (", ".join(ext_m) or "none") + "\n")
    idx.append("## Evidence: Seeds / Snapshots / Tests / Exposures\n")
    idx.append(f"- **Seeds** ({len(seeds)}): " + (", ".join(sorted(n["name"] for n in seeds.values())) or "none"))
    idx.append(f"- **Snapshots** ({len(snapshots)}): " + (", ".join(sorted(n["name"] for n in snapshots.values())) or "none"))
    idx.append(f"- **Singular tests** ({len(singular_tests)}): " + (", ".join(sorted(t["name"] for t in singular_tests.values())) or "none"))
    idx.append("- **Exposures** (0): none\n")
    pct = (100 * sqlglot_ok // total_models) if total_models else 0
    idx += ["## Statistics", "", f"- Total models: {total_models}", f"- Total sources: {len(sources)}",
            f"- Total macros (used): {written['macros']}",
            f"- Generic tests: {len(generic_tests)}  |  Singular tests: {len(singular_tests)}",
            f"- Column lineage extracted: {sqlglot_ok}/{total_models} ({pct}%)",
            f"- sqlglot parse failures: {sqlglot_failed} (see log.md)",
            f"- schema.yml-only (no compiled SQL matched): {sqlglot_none}",
            "- Knowledge pages: entities 0, metrics 0, concepts 0 (Phase B populates)"]
    with open(os.path.join(wiki, "index.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(idx) + "\n")

    # ---- lineage.md ----
    depth_cache = {}

    def node_depth(uid, seen=frozenset()):
        if uid in depth_cache:
            return depth_cache[uid]
        if uid in seen:
            return 0
        seen = seen | {uid}
        n = nodes.get(uid)
        deps = []
        if n:
            deps = list(n.get("depends_on", {}).get("nodes", []))
            for sn, tn in n.get("sources", []):
                su = src_lookup.get((sn, tn))
                if su:
                    deps.append(su)
        d = 0 if not deps else 1 + max((node_depth(x, seen) for x in deps), default=0)
        depth_cache[uid] = d
        return d

    max_depth = max((node_depth(u) for u in models), default=0)
    leaf_models = [n["name"] for u, n in models.items() if not feeds_into.get(u)]

    lin = ["---", "title: dbt-wiki Lineage", "type: lineage", f"last_updated: {today}",
           f"manifest_sha: {manifest_sha}", "---", "", "# dbt Project Lineage (DAG)", "",
           "> Auto-generated from manifest.json (model-level) + sqlglot column-level. Do not edit.", "",
           "## Statistics", "", f"- Models: {total_models}", f"- Sources (declared): {len(sources)}",
           f"- DAG depth (longest source→leaf path): {max_depth}",
           f"- Leaf models (no downstream): {len(leaf_models)}", f"- Root sources: {len(sources)}", ""]
    if total_models > 500:
        lin += ["## Tier-aggregated view (>500 nodes)", "", "```"]
        for tier in ordered_tiers:
            lin.append(f"{tier_label(tier)}: {len(by_tier[tier])} models")
        lin += ["```", ""]
    else:
        lin += ["## ASCII Tree (per source/seed)", "", "```"]
        roots = list(sources.keys()) + list(seeds.keys())
        for root in roots:
            seen_t = set()

            def walk(uid, depth):
                nm = uid_to_name.get(uid, uid)
                if uid in seen_t:
                    lin.append("  " * depth + f"↺ {nm}")
                    return
                seen_t.add(uid)
                lin.append("  " * depth + f"→ {nm}")
                for child in sorted(feeds_into.get(uid, [])):
                    cuid = next((cu for cu, cn in models.items() if cn["name"] == child), None)
                    if cuid and depth < 30:
                        walk(cuid, depth + 1)
            label = uid_to_name.get(root, root)
            kind = "source" if root in sources else "seed"
            lin.append(f"{kind}: {label}")
            for child in sorted(feeds_into.get(root, [])):
                cuid = next((cu for cu, cn in models.items() if cn["name"] == child), None)
                if cuid:
                    walk(cuid, 1)
        lin += ["```", ""]
    lin.append("## Adjacency List (per model, alphabetical)\n")
    for u, n in sorted(models.items(), key=lambda kv: kv[1]["name"]):
        refs = sorted(set(uid_to_name.get(d, d) for d in n.get("depends_on", {}).get("nodes", [])
                          if d.startswith(("model.", "seed.", "snapshot."))))
        srcs = sorted(f"{sn}.{tn}" for sn, tn in n.get("sources", []))
        macs = sorted(set(macro_label.get(m, m) for m in n.get("depends_on", {}).get("macros", [])))
        downs = feeds_into.get(u, [])
        extracted = "yes (sqlglot)" if col_lineage.get(n["original_file_path"]) and "_error" not in col_lineage.get(n["original_file_path"], {}) else "no"
        lin.append(f'### {n["name"]}')
        lin.append("- **depends_on (model refs)**: " + (", ".join(f"[{r}]({model_file_by_uid.get('model.'+project+'.'+r, r+'.md')})" for r in refs) if refs else "none"))
        lin.append("- **depends_on (sources)**: " + (", ".join(srcs) if srcs else "none"))
        lin.append("- **depends_on (macros)**: " + (", ".join(macs) if macs else "none"))
        lin.append("- **feeds_into (models)**: " + (", ".join(f"[{d}]({d}.md)" for d in downs) if downs else "none"))
        lin.append(f"- **column-level lineage extracted**: {extracted}")
        lin.append("")
    with open(os.path.join(wiki, "lineage.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lin) + "\n")

    print(json.dumps({
        "manifest_sha": manifest_sha, "project": project,
        "compiled_files_parsed": len(col_lineage),
        "sqlglot_ok": sqlglot_ok, "sqlglot_failed": sqlglot_failed, "schema_yml_only": sqlglot_none,
        "total_models": total_models, "written": dict(written),
        "sources": len(sources), "macros_used": written["macros"],
        "seeds": len(seeds), "snapshots": len(snapshots),
        "generic_tests": len(generic_tests), "singular_tests": len(singular_tests),
        "dag_depth": max_depth, "leaf_models": len(leaf_models),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
