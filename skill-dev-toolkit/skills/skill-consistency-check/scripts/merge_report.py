#!/usr/bin/env python3
"""Merge detector findings into one consistency report (stdlib only).

Usage:
  python3 merge_report.py --target <skill_dir> --plan <plan.json>
      --findings <f1.json> [<f2.json> ...] --model "<model>" --out <dir>

Writes <out>/consistency-report.json and <out>/consistency-report.md, never
inside the target. Exit 0 pass, 1 needs-revision, 2 error.
"""
import argparse
import json
import os
import sys

RANK = {"high": 0, "medium": 1, "low": 2}
LINE_WINDOW = 2
REFERENCE = {"model": "Claude Sonnet (200k context)", "max_validated_tokens": 25000}
BLIND_SPOTS = [
    "conditional contradictions (conflict only under a shared condition)",
    "multi-step contradictions (need several inference hops or unstated background knowledge)",
]


class InputError(Exception):
    pass


def _inside(path, root):
    path, root = os.path.realpath(path), os.path.realpath(root)
    return path == root or path.startswith(root.rstrip(os.sep) + os.sep)


def _load(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError) as exc:
        raise InputError(f"cannot read {path}: {exc}") from exc


def _near(lines_a, lines_b):
    return any(abs(a - b) <= LINE_WINDOW for a in lines_a for b in lines_b)


def _same(f, g):
    fa, fb, ga, gb = f["side_a"], f["side_b"], g["side_a"], g["side_b"]
    if {fa["file"], fb["file"]} != {ga["file"], gb["file"]}:
        return False
    for x, y in (((ga, gb)), ((gb, ga))):
        if fa["file"] == x["file"] and fb["file"] == y["file"] \
                and _near(fa["lines"], x["lines"]) and _near(fb["lines"], y["lines"]):
            return True
    return False


def merge(findings_files):
    """findings_files: list of (source name, findings list). Returns merged list."""
    groups = []  # each: list of (source, finding)
    for source, findings in findings_files:
        for f in findings:
            for group in groups:
                if any(_same(f, g) for _, g in group):
                    group.append((source, f))
                    break
            else:
                groups.append([(source, f)])
    merged = []
    for group in groups:
        best = min((g for _, g in group), key=lambda g: RANK[g["confidence"]])
        merged.append({
            "confidence": best["confidence"], "type": best.get("type"),
            "side_a": best["side_a"], "side_b": best["side_b"],
            "why": best.get("why", ""), "steps": best.get("steps", []),
            "sources": [{"file": s, "id": g.get("id")} for s, g in group],
        })
    merged.sort(key=lambda m: RANK[m["confidence"]])
    return merged


def build_report(plan, merged, model):
    counts = {k: sum(1 for m in merged if m["confidence"] == k) for k in RANK}
    return {
        "verdict": "needs-revision" if counts["high"] else "pass",
        "findings": merged,
        "counts": counts,
        "grouped": bool(plan.get("grouped")),
        "over_limit": bool(plan.get("over_limit")),
        "uncovered_pairs": plan.get("uncovered_pairs", []),
        "model": model,
        "reference": dict(REFERENCE),
        "model_matches_reference": "sonnet" in model.lower(),
        "blind_spots": list(BLIND_SPOTS),
    }


def _loc(side):
    lines = ",".join(str(n) for n in side.get("lines", []))
    return f"{side['file']}:{lines}"


def _finding_md(n, m):
    a, b = m["side_a"], m["side_b"]
    return [
        f"{n}. [{m['confidence']}] ({m.get('type')}) {m.get('why', '')}",
        f"   - {_loc(a)} — \"{a.get('quote', '')}\"",
        f"   - {_loc(b)} — \"{b.get('quote', '')}\"",
    ]


def render_md(r):
    out = ["# Consistency report", "", f"Verdict: **{r['verdict']}**", ""]
    if r["over_limit"]:
        out += ["> Warning: the core files alone are over the group size limit "
                f"({REFERENCE['max_validated_tokens']:,} tokens); every group "
                "still carries the whole core, so results are less reliable.", ""]
    high = [m for m in r["findings"] if m["confidence"] == "high"]
    rest = [m for m in r["findings"] if m["confidence"] != "high"]
    out += ["## High-confidence findings (blocking)", ""]
    out += [line for i, m in enumerate(high, 1) for line in _finding_md(i, m)] or ["None."]
    out += ["", "## Medium / low-confidence findings (advisory)", ""]
    out += [line for i, m in enumerate(rest, 1) for line in _finding_md(i, m)] or ["None."]
    out.append("")
    if r["grouped"]:
        out += ["## Not checked together", ""]
        out += [f"- {a} ↔ {b}" for a, b in r["uncovered_pairs"]] or ["None."]
        out.append("")
    out += ["## Known limits", ""] + [f"- {b}" for b in r["blind_spots"]] + [""]
    ref = r["reference"]
    out.append(f"Model used: {r['model']} — validated on: {ref['model']}, "
               f"packages up to {ref['max_validated_tokens']:,} tokens")
    if not r["model_matches_reference"]:
        out += ["", "> Warning: Accuracy with this model is not validated."]
    return "\n".join(out) + "\n"


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--target", required=True)
    p.add_argument("--plan", required=True)
    p.add_argument("--findings", required=True, nargs="+")
    p.add_argument("--model", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args(argv)
    try:
        if not os.path.isdir(args.target):
            raise InputError(f"target is not a directory: {args.target}")
        if _inside(args.out, args.target):
            raise InputError(f"--out must be outside the checked skill: {args.out}")
        plan = _load(args.plan)
        batches = []
        for path in args.findings:
            data = _load(path)
            if not isinstance(data, dict) or not isinstance(data.get("findings"), list):
                raise InputError(f"{path}: expected {{\"findings\": [...]}}")
            for f in data["findings"]:
                if f.get("confidence") not in RANK or "side_a" not in f or "side_b" not in f:
                    raise InputError(f"{path}: malformed finding {f.get('id')}")
            batches.append((os.path.basename(path), data["findings"]))
        report = build_report(plan, merge(batches), args.model)
        os.makedirs(args.out, exist_ok=True)
        json_path = os.path.join(args.out, "consistency-report.json")
        md_path = os.path.join(args.out, "consistency-report.md")
        with open(json_path, "w", encoding="utf-8") as fh:
            json.dump(report, fh, ensure_ascii=False, indent=2)
        with open(md_path, "w", encoding="utf-8") as fh:
            fh.write(render_md(report))
    except (InputError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(md_path)
    print(report["verdict"])
    return 1 if report["verdict"] == "needs-revision" else 0


if __name__ == "__main__":
    sys.exit(main())
