#!/usr/bin/env python3
"""Score contradiction-check findings against a corpus set's answer key.

Usage:
  python3 score.py <set-dir> <findings.json> [<findings.json> ...] [--doc doc_N]

<set-dir> is single-a/, single-b/ or multi/ (it holds truth.json).
Single-file sets: each findings file covers one doc, taken from --doc or
from a `doc_N` in the file name; only that doc's plants are scored.

A finding catches a plant when side_a and side_b touch two DIFFERENT sides
of the plant (within 1 line; same file when files are given). Single-a
plants list flat lines; they are split into sides wherever consecutive
lines are more than 2 apart. A high-confidence finding that matches no
plant and no genuine item is listed under unmatched_high for human triage;
unmatched does not mean false. Stdlib only; prints JSON to stdout.
"""
import argparse
import json
import re
import sys
from pathlib import Path


def clusters(lines):
    out, cur = [], []
    for n in sorted(lines):
        if cur and n - cur[-1] > 2:
            out.append(cur)
            cur = []
        cur.append(n)
    return out + ([cur] if cur else [])


def load_items(set_dir):
    """Return (plants, genuine); each item has id, type, doc, sides=[(file, lines)]."""
    truth = json.loads((Path(set_dir) / "truth.json").read_text(encoding="utf-8"))
    plants = []
    for p in truth["plants"]:
        if "sides" in p:
            sides = [(s.get("file"), s["lines"]) for s in p["sides"]]
        else:
            sides = [(None, c) for c in clusters(p["lines"])]
        plants.append({"id": p["id"], "type": p.get("type"), "doc": p.get("doc"), "sides": sides})
    genuine = []
    for i, g in enumerate(truth.get("genuine", [])):
        gid = f"G{i + 1}"
        if "docs" in g:
            for doc, d in g["docs"].items():
                genuine.append({"id": gid, "doc": doc, "sides": [(None, d["lines"])]})
        else:
            genuine.append({"id": gid, "doc": None,
                            "sides": [(s.get("file"), s["lines"]) for s in g["sides"]]})
    return plants, genuine


def touches(fside, iside):
    file, lines = iside
    if file is not None and fside.get("file") != file:
        return False
    return any(abs(a - b) <= 1 for a in fside.get("lines", []) for b in lines)


def touched(fside, item):
    return {i for i, s in enumerate(item["sides"]) if touches(fside, s)}


def catches_plant(f, plant):
    ta, tb = touched(f["side_a"], plant), touched(f["side_b"], plant)
    return any(i != j for i in ta for j in tb)


def matches_genuine(f, item):
    return bool(touched(f["side_a"], item)) and bool(touched(f["side_b"], item))


def load_findings(paths, doc_arg):
    out = []
    for p in map(Path, paths):
        doc = doc_arg
        if doc is None:
            m = re.search(r"doc_\d+", p.name)
            doc = m.group(0) if m else None
        for f in json.loads(p.read_text(encoding="utf-8"))["findings"]:
            out.append((p.name, doc, f))
    return out


def score(set_dir, findings_paths, doc=None):
    plants, genuine = load_items(set_dir)
    findings = load_findings(findings_paths, doc)
    single = any(p["doc"] for p in plants)
    if single:
        docs = sorted({d for _, d, _ in findings if d})
        if any(d is None for _, d, _ in findings):
            raise ValueError("single-file set: pass --doc or name findings files doc_N.*.json")
        plants = [p for p in plants if p["doc"] in docs]

    def same_doc(item, fdoc):
        return item["doc"] is None or item["doc"] == fdoc

    report = []
    for p in plants:
        by = [f"{src}:{f.get('id')}" for src, fdoc, f in findings
              if same_doc(p, fdoc) and catches_plant(f, p)]
        row = {"id": p["id"], "type": p["type"], "caught": bool(by), "caught_by": by}
        if p["doc"]:
            row["doc"] = p["doc"]
        report.append(row)

    unmatched = []
    for src, fdoc, f in findings:
        if f.get("confidence") != "high":
            continue
        if any(same_doc(p, fdoc) and catches_plant(f, p) for p in plants):
            continue
        if any(same_doc(g, fdoc) and matches_genuine(f, g) for g in genuine):
            continue
        unmatched.append({"source": src, "doc": fdoc, "id": f.get("id"),
                          "side_a": f.get("side_a"), "side_b": f.get("side_b"),
                          "why": f.get("why")})

    result = {
        "set": Path(set_dir).name,
        "findings_total": len(findings),
        "plants": report,
        "recall": {"caught": sum(r["caught"] for r in report), "total": len(report)},
        "unmatched_high": unmatched,
    }
    if single:
        result["docs"] = docs
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("set_dir")
    ap.add_argument("findings", nargs="+")
    ap.add_argument("--doc", help="doc id (e.g. doc_4) for single-file sets")
    args = ap.parse_args(argv)
    try:
        result = score(args.set_dir, args.findings, args.doc)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
