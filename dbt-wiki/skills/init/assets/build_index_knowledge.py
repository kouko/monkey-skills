# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Populate index.md's knowledge sections (## Entities / ## Metrics / ## Concepts)
deterministically from the distilled knowledge pages, using the SCHEMA canonical
line shape:

  - [<title>｜<title_local>](<folder>/<slug>.md) `<status>` — <summary> 〔aka: a, b〕

Replaces the three knowledge sections in place (between each `## <Section>` header
and the next `## ` header); leaves the evidence sections untouched. Also updates
the `- Knowledge pages:` statistics line if present.

Pure stdlib + pyyaml; reads only `.dbt-wiki/{entities,metrics,concepts}/*.md`
frontmatter (`title`, `title_local`, `status`, `summary`, `aliases`). Idempotent.
No project specifics.

Usage:  uv run build_index_knowledge.py <wiki-dir>     # e.g. .dbt-wiki
"""
import sys
import re
from pathlib import Path
import yaml

SECTIONS = [("entities", "## Entities"), ("metrics", "## Metrics"), ("concepts", "## Concepts")]


def parse_fm(text):
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    try:
        return yaml.safe_load(text[3:end]) or {}
    except Exception:
        return {}


def line_for(folder, path):
    fm = parse_fm(path.read_text(encoding="utf-8"))
    title = fm.get("title") or path.stem
    tl = fm.get("title_local")
    status = fm.get("status") or "developing"
    summary = (fm.get("summary") or "").strip()
    aliases = [str(a) for a in (fm.get("aliases") or []) if a is not None and str(a).strip()]
    head = f"{title}｜{tl}" if tl else f"{title}"
    line = f"- [{head}]({folder}/{path.name}) `{status}`"
    if summary:
        line += f" — {summary}"
    if aliases:
        line += f" 〔aka: {', '.join(aliases)}〕"
    return title, line


def section_lines(wiki, folder):
    d = wiki / folder
    rows = [line_for(folder, p) for p in sorted(d.glob("*.md"))] if d.exists() else []
    rows.sort(key=lambda x: x[0].lower())
    if not rows:
        return [f"_(none yet — run Phase B to distill {folder} from the evidence layer)_"]
    return [r[1] for r in rows]


def main(wiki: Path) -> int:
    index = wiki / "index.md"
    if not index.exists():
        print(f"build_index_knowledge: no index.md at {index}", file=sys.stderr)
        return 1

    counts = {}
    new_sections = {}
    for fol, hdr in SECTIONS:
        body = section_lines(wiki, fol)
        counts[fol] = 0 if body and body[0].startswith("_(none") else len(body)
        new_sections[hdr] = body

    lines = index.read_text(encoding="utf-8").split("\n")
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip() in new_sections:
            hdr = line.strip()
            out.append(line)
            out.append("")
            out.extend(new_sections[hdr])
            out.append("")
            i += 1
            while i < len(lines) and not lines[i].startswith("## "):
                i += 1
            continue
        if line.strip().startswith("- Knowledge pages:"):
            out.append(f"- Knowledge pages: entities {counts['entities']}, "
                       f"metrics {counts['metrics']}, concepts {counts['concepts']}")
            i += 1
            continue
        out.append(line)
        i += 1

    index.write_text("\n".join(out), encoding="utf-8")
    print(f"build_index_knowledge: index.md knowledge sections populated — "
          f"entities {counts['entities']}, metrics {counts['metrics']}, concepts {counts['concepts']}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(Path(sys.argv[1])))
