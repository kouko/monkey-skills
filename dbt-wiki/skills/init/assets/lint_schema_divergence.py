#!/usr/bin/env python3
"""
lint_schema_divergence.py — dbt-wiki knowledge-layer regression gate.

Detects "replicated-twin schema divergence" gaps: when an evidence-layer family
of structurally parallel models (per-segment / market / brand twins) has
DIVERGENT column schemas, but the distilled knowledge layer documents only one
shape — the failure mode where a consumer's cross-twin UNION silently errors
because the canonical column names don't apply to a renamed/stripped twin.

Two roles, one tool:
  • BASELINE — run before/after a distillation change to measure how many
    divergent twin families the knowledge layer documents (the eval metric).
  • GATE — exit non-zero when divergent families are undocumented (CI / review).

Deterministic; pure stdlib; reads the generated `.dbt-wiki/` only (evidence
columns + knowledge bodies). Never connects to a warehouse.

Twin detection is naming-convention-specific, so twin tokens are configurable:
  --strip-tokens eu,apac,latam,fcst
Two model names are twins iff they are equal after dropping those tokens as
whole `_`-delimited segments (and collapsing `__`). Without --strip-tokens the
linter cannot group twins and exits with guidance.

Usage:
  python lint_schema_divergence.py [WIKI_DIR] --strip-tokens eu,apac,latam,fcst [--json]
  # WIKI_DIR defaults to <git-root>/.dbt-wiki, else ./.dbt-wiki
"""
import os
import re
import sys
import json
import glob
import subprocess
from collections import defaultdict


def resolve_wiki_dir(argv):
    value_flags = {"--strip-tokens"}   # flags whose following token is a value, not a positional
    prev = ""
    for a in argv:
        if prev not in value_flags and not a.startswith("-") and os.path.isdir(a):
            return a if os.path.basename(a) == ".dbt-wiki" else os.path.join(a, ".dbt-wiki")
        prev = a
    try:
        root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"],
                                       text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        root = os.getcwd()
    return os.path.join(root, ".dbt-wiki")


def arg_value(argv, flag, default=None):
    if flag in argv:
        i = argv.index(flag)
        if i + 1 < len(argv):
            return argv[i + 1]
    return default


def frontmatter(path):
    txt = open(path, encoding="utf-8").read()
    if not txt.startswith("---"):
        return {}, txt
    parts = txt.split("---", 2)
    return parts[1], (parts[2] if len(parts) > 2 else "")


def evidence_models(wiki):
    """unique_id -> {name, columns:set}; also name -> unique_id."""
    by_uid, by_name = {}, {}
    for p in glob.glob(os.path.join(wiki, "_evidence", "models", "*.md")):
        fm, _ = frontmatter(p)
        uid = (re.search(r'^\s*unique_id:\s*(\S+)', fm, re.M) or [None, None])[1]
        if not uid:
            continue
        name = uid.split(".")[-1]
        cols = set(re.findall(r'^\s*-\s*name:\s*(\S+)', fm, re.M))
        by_uid[uid] = {"name": name, "cols": cols}
        by_name[name] = uid
    return by_uid, by_name


def knowledge_pages(wiki):
    """list of {path, slug, derived_from:[uid], body}"""
    out = []
    for folder in ("entities", "metrics", "concepts"):
        for p in glob.glob(os.path.join(wiki, folder, "*.md")):
            fm, body = frontmatter(p)
            df = re.findall(r'-\s*(model\.[A-Za-z0-9_.]+)', fm)
            out.append({"path": os.path.relpath(p, wiki),
                        "slug": os.path.basename(p)[:-3], "df": df, "body": body})
    return out


def normalize(name, tokens):
    segs = [s for s in name.split("_") if s and s not in tokens]
    return "_".join(segs)


def main(argv):
    wiki = resolve_wiki_dir(argv)
    as_json = "--json" in argv
    tokens = set(t for t in (arg_value(argv, "--strip-tokens", "") or "").split(",") if t)

    if not os.path.isdir(wiki):
        print(f"dbt-wiki: no knowledge base at {wiki}", file=sys.stderr)
        return 2
    if not tokens:
        print("lint_schema_divergence: no --strip-tokens given, so twin families "
              "cannot be grouped.\n  e.g. --strip-tokens eu,apac,latam,fcst "
              "(your project's market/brand/variant name tokens)", file=sys.stderr)
        return 2

    by_uid, by_name = evidence_models(wiki)
    pages = knowledge_pages(wiki)

    # group evidence models into twin families by normalized name
    families = defaultdict(dict)   # family_key -> {model_name: cols}
    for uid, m in by_uid.items():
        fam = normalize(m["name"], tokens)
        families[fam][m["name"]] = m["cols"]

    # divergent twin families = >=2 members whose column sets are not all identical
    divergent = []
    for fam, members in families.items():
        if len(members) < 2:
            continue
        colsets = list(members.values())
        union = set().union(*colsets)
        inter = set.intersection(*colsets)
        if union == inter:
            continue   # all members column-identical
        ref_name = max(members, key=lambda n: len(members[n]))   # superset = reference
        ref = members[ref_name]
        deltas = {}
        twin_only = set()   # columns that exist on a non-ref twin (added or rename-target)
        for n, cs in members.items():
            if n == ref_name:
                continue
            dropped = sorted(ref - cs)
            added = sorted(cs - ref)
            renames = [(d, a) for d in dropped for a in added
                       if d.replace("rh_", "") == a or a.replace("rh_", "") == d
                       or d.split("__")[0] == a.split("__")[0]]
            twin_only |= set(added)   # rename-targets are a subset of `added`
            deltas[n] = {"dropped": dropped, "added": added,
                         "renamed": [f"{d}->{a}" for d, a in renames]}
        divergent.append({"family": fam, "ref": ref_name, "members": list(members),
                          "deltas": deltas, "twin_only": sorted(twin_only)})

    # A family is "schema-documented" iff some knowledge page BOTH:
    #   (a) names >=2 of the family's member models (the per-variant map lists them), AND
    #   (b) names >=1 twin-only column as a whole word (the actual rename/added delta).
    # (b) is what distinguishes a genuine per-variant schema map from a page that merely
    # mentions a twin exists (e.g. an "HK comes from a different model" caveat). Whole-word
    # matching stops `region` matching inside `region_code`. NOTE: drop-only
    # families (twins only LOSE columns, no rename/add) have no twin-only token, so this
    # check can never mark them documented — it conservatively over-flags them (safe for a
    # gate; a reviewer confirms). Improve later by detecting an explicit drop note.
    def has_word(text, tok):
        return re.search(r'(?<![A-Za-z0-9_])' + re.escape(tok) + r'(?![A-Za-z0-9_])', text) is not None

    documented = {}
    for f in divergent:
        fam, members, ref = f["family"], set(f["members"]), f["ref"]
        twin_only = f["twin_only"]
        twins = members - {ref}
        docs = []
        for pg in pages:
            # genuine per-variant map = a line that names a (non-ref) twin model AND
            # one of its rename/added columns. Co-occurrence on one line is what a table
            # row provides and what stray prose (e.g. `product_line` in a grain sentence
            # far from any twin name) does not.
            hit = any(
                any(mn in line for mn in twins) and any(has_word(line, t) for t in twin_only)
                for line in pg["body"].splitlines()
            )
            if hit:
                docs.append(pg["slug"])
        documented[fam] = docs

    n_div = len(divergent)
    n_doc = sum(1 for f in divergent if documented[f["family"]])
    n_undoc = n_div - n_doc

    if as_json:
        print(json.dumps({
            "wiki": wiki, "strip_tokens": sorted(tokens),
            "divergent_families": n_div, "documented": n_doc, "undocumented": n_undoc,
            "families": [{**f, "documented_by": documented[f["family"]]} for f in divergent],
        }, indent=2, ensure_ascii=False))
        return 1 if n_undoc else 0

    print(f"dbt-wiki schema-divergence lint  ({wiki})")
    print(f"strip-tokens: {sorted(tokens)}")
    print(f"twin families: {len(families)} | divergent: {n_div} | "
          f"documented: {n_doc} | UNDOCUMENTED: {n_undoc}\n")
    print(f"SCORE (documented / divergent): {n_doc}/{n_div}\n")
    for f in sorted(divergent, key=lambda x: (bool(documented[x['family']]), x['family'])):
        fam = f["family"]
        status = f"documented by {documented[fam]}" if documented[fam] else "✗ UNDOCUMENTED"
        print(f"■ {fam}  [{status}]")
        print(f"    ref: {f['ref']}")
        for n, d in f["deltas"].items():
            bits = []
            if d["renamed"]:
                bits.append("rename " + ", ".join(d["renamed"]))
            only_drop = [c for c in d["dropped"]
                         if not any(c in r for r in d["renamed"])]
            if only_drop:
                bits.append("drops " + ", ".join(only_drop[:6]) +
                            (f" (+{len(only_drop)-6})" if len(only_drop) > 6 else ""))
            print(f"    └ {n}: {'; '.join(bits) if bits else 'differs'}")
        print()
    if n_undoc:
        print(f"GATE: {n_undoc} divergent twin family(ies) undocumented in the "
              f"knowledge layer — distillation should record a per-variant schema map "
              f"(distill-metrics §3b / distill-entities §3.4 rule 5).")
    return 1 if n_undoc else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
