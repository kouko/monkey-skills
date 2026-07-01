# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Collect the redistill work-list from a .dbt-wiki/ knowledge layer.

`rescan` flags knowledge pages `stale: true` when their `derived_from` evidence
changes — but never re-distills (that keeps the daily path LLM-free). `redistill`
consumes the flags this script gathers.

Selection contract (deterministic, no LLM):
  - scan entities/ metrics/ concepts/*.md
  - SELECT pages where stale is truthy AND status not in {mature, archived}
      - mature stale pages are reported in `skipped_mature` (need --force-mature)
      - archived pages are dropped entirely
      - selected pages with no `derived_from` go to `skipped_no_provenance`
        (cannot be scoped to a domain / evidence set)
  - GROUP selected pages by the domain owning the majority of their
    `derived_from` uids, per `_internal/ownership.json` (the same map init's
    Phase B fan-out wrote). Ties resolve to the lexicographically-first domain.
  - FALLBACK: if ownership.json is absent (small / sequential init), there is no
    domain map — emit one '(all)' group and set `fallback: true`. uids that map
    to no domain land in an '(unmapped)' group.

Output: JSON to stdout (machine-readable for the redistill orchestrator).
"""
import sys
import json
from collections import Counter
from pathlib import Path

import yaml

KNOWLEDGE_FOLDERS = ("entities", "metrics", "concepts")
SKIP_STATUS = {"archived"}
MATURE_STATUS = {"mature"}
ALL_GROUP = "(all)"
UNMAPPED_GROUP = "(unmapped)"


def parse_frontmatter(text):
    """Return the YAML frontmatter dict of a page, or {} if absent/malformed."""
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    try:
        return yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return {}


def _load_uid_to_domain(wiki):
    """Invert ownership.json domains map → {uid: domain}. None if file absent."""
    path = wiki / "_internal" / "ownership.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    uid_to_domain = {}
    for domain, uids in (data.get("domains") or {}).items():
        for uid in uids:
            uid_to_domain[uid] = domain
    return uid_to_domain


def _majority_domain(derived_from, uid_to_domain):
    """Pick the domain owning the most derived_from uids (lexicographic tiebreak).

    Returns UNMAPPED_GROUP if no uid maps to a known domain."""
    votes = Counter(uid_to_domain[u] for u in derived_from if u in uid_to_domain)
    if not votes:
        return UNMAPPED_GROUP
    top = max(votes.values())
    return sorted(d for d, n in votes.items() if n == top)[0]


def collect_worklist(wiki):
    """Build the redistill work-list. `wiki` is the .dbt-wiki/ Path."""
    wiki = Path(wiki)
    uid_to_domain = _load_uid_to_domain(wiki)
    fallback = uid_to_domain is None

    groups = {}
    skipped_mature = []
    skipped_no_provenance = []
    total_stale = 0

    for folder in KNOWLEDGE_FOLDERS:
        for path in sorted((wiki / folder).glob("*.md")) if (wiki / folder).is_dir() else []:
            fm = parse_frontmatter(path.read_text(encoding="utf-8"))
            if not fm.get("stale"):
                continue
            total_stale += 1
            status = fm.get("status")
            slug = path.stem
            entry = {
                "slug": slug,
                "path": str(path),
                "folder": folder,
                "derived_from": list(fm.get("derived_from") or []),
            }
            if status in SKIP_STATUS:
                continue
            if status in MATURE_STATUS:
                skipped_mature.append(entry)
                continue
            if not entry["derived_from"]:
                skipped_no_provenance.append(entry)
                continue
            if fallback:
                domain = ALL_GROUP
            else:
                domain = _majority_domain(entry["derived_from"], uid_to_domain)
            groups.setdefault(domain, []).append(entry)

    total_selected = sum(len(v) for v in groups.values())
    return {
        "fallback": fallback,
        "groups": groups,
        "skipped_mature": skipped_mature,
        "skipped_no_provenance": skipped_no_provenance,
        "total_stale": total_stale,
        "total_selected": total_selected,
    }


def main(argv):
    wiki = Path(argv[1]) if len(argv) > 1 else Path(".dbt-wiki")
    if not wiki.is_dir():
        print(f"Not a directory: {wiki}", file=sys.stderr)
        return 1
    print(json.dumps(collect_worklist(wiki), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
