# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Phase-B reconcile pass (init SKILL Step 6.7), as a deterministic script.

1. Collect every `relationships[].target` across all knowledge pages.
2. Resolve missing targets:
   - reserved entity with no page  -> WARNING (do NOT stub a reserved slug;
     its owning domain agent should have produced it).
   - genuine dangling reference     -> create a `status: seed` stub so the
     markdown link resolves.
3. Lint `derived_from` cross-domain contamination (uids spanning >1 domain),
   which would cause spurious stale-cascades on refresh.

Reads `_internal/ownership.json` when present (the domain fan-out map written by
the orchestrator for large projects). **Small projects skip domain fan-out and
have no ownership.json** — the script degrades gracefully: no reserved entities
(every dangling ref becomes a seed stub) and no contamination lint (no domain
map to span). Pure stdlib + pyyaml. Writes only seed stubs. Idempotent.
No project specifics.

Usage:  uv run reconcile.py <wiki-dir> [YYYY-MM-DD]    # date defaults to today
"""
import json
import sys
import re
import os
import datetime
from pathlib import Path
from collections import Counter
import yaml

KFOLDERS = ["entities", "metrics", "concepts"]
KTYPE = {"entities": "knowledge-entity", "metrics": "knowledge-metric",
         "concepts": "knowledge-concept"}


def parse_fm(text):
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    try:
        return (yaml.safe_load(text[3:end]) or {}), text[end + 4:]
    except Exception:
        return {}, text[end + 4:]


def resolve_target(src_folder, target):
    """Return (folder, filename) for a relationships target string."""
    target = target.strip()
    if target.startswith("../"):
        m = re.match(r"\.\./([^/]+)/(.+)", target)
        if m:
            return m.group(1), os.path.basename(m.group(2))
    return src_folder, os.path.basename(target)  # bare slug -> sibling in src_folder


def main(wiki: Path, today: str) -> int:
    # ownership.json is optional (only large projects with domain fan-out have it)
    own_path = wiki / "_internal" / "ownership.json"
    if own_path.exists():
        own = json.loads(own_path.read_text(encoding="utf-8"))
        reserved = own.get("reserved_entities", {})
        domains = own.get("domains", {})
    else:
        reserved, domains = {}, {}
    uid_to_domain = {u: dom for dom, uids in domains.items() for u in uids}

    existing = {}
    for fol in KFOLDERS:
        d = wiki / fol
        if d.exists():
            for p in d.glob("*.md"):
                existing[(fol, p.name)] = p

    targets = []
    contamination = []
    for fol in KFOLDERS:
        d = wiki / fol
        if not d.exists():
            continue
        for p in sorted(d.glob("*.md")):
            fm, _ = parse_fm(p.read_text(encoding="utf-8"))
            for rel in (fm.get("relationships") or []):
                if isinstance(rel, dict) and rel.get("target"):
                    tf, tn = resolve_target(fol, str(rel["target"]))
                    targets.append((fol, p.name, tf, tn))
            df = fm.get("derived_from") or []
            doms = [uid_to_domain[u] for u in df if u in uid_to_domain]
            if len(set(doms)) > 1:
                majority = Counter(doms).most_common(1)[0][0]
                foreign = [(u, uid_to_domain[u]) for u in df
                           if u in uid_to_domain and uid_to_domain[u] != majority]
                contamination.append((f"{fol}/{p.name}", set(doms), foreign, majority))

    warnings, stubs, seen = [], [], set()
    for sf, sn, tf, tn in targets:
        if (tf, tn) in existing or (tf, tn) in seen:
            continue
        seen.add((tf, tn))
        slug = tn[:-3] if tn.endswith(".md") else tn
        if slug in reserved:
            warnings.append(f'reserved entity "{slug}" (owner: "{reserved[slug]}") '
                            f'referenced by {sf}/{sn} has NO page — resolve manually')
        else:
            target_dir = wiki / tf
            target_dir.mkdir(parents=True, exist_ok=True)
            ktype = KTYPE.get(tf, "knowledge-concept")
            (target_dir / tn).write_text(
                f"---\ntype: {ktype}\ntitle: \"{slug}\"\nstatus: seed\n"
                f"summary: null\nupdated: {today}\nderived_from: []\n"
                f"relationships: []\nlast_changed_by: \"auto-stub (reconcile pass)\"\n"
                f"tags: []\naliases: []\ntitle_local: null\n"
                f"stale: false\nstale_at: null\nstale_reason: null\n---\n\n"
                f"<!-- Auto-generated stub (reconcile). Referenced by {sf}/{sn} "
                f"but not yet distilled. Replace with a real distillation pass. -->\n",
                encoding="utf-8")
            stubs.append(f"{tf}/{tn}  (referenced by {sf}/{sn})")

    print(f"=== reconcile: {len(targets)} relationship targets scanned "
          f"({'ownership.json present' if own_path.exists() else 'no ownership.json — small-project mode'}) ===")
    print(f"\n--- dangling reserved-entity WARNINGS ({len(warnings)}) ---")
    for w in warnings:
        print(f"  ⚠ {w}")
    print(f"\n--- seed stubs created ({len(stubs)}) ---")
    for s in stubs:
        print(f"  + {s}")
    print(f"\n--- derived_from cross-domain contamination ({len(contamination)}) ---")
    for path, doms, foreign, majority in contamination:
        print(f"  ✗ {path}: spans {sorted(doms)} (majority={majority})")
        for u, fd in foreign:
            print(f"      uid {u} -> {fd}")
    if not contamination:
        print("  (none — all pages have clean single-domain derived_from)")
    return 0


if __name__ == "__main__":
    if not (2 <= len(sys.argv) <= 3):
        print(__doc__)
        sys.exit(2)
    day = sys.argv[2] if len(sys.argv) == 3 else datetime.date.today().isoformat()
    sys.exit(main(Path(sys.argv[1]), day))
