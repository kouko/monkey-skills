# /// script
# requires-python = ">=3.10"
# ///
"""Flatten in-page links for a flat dbt-wiki:pack bundle.

pack Step 2 relocates entities/metrics/concepts/syntheses into a FLAT
`knowledge/` but copies page content verbatim, so in-page relative links
keep the NESTED source-layout paths and break in the bundle. This rewrites
them, in order:

  - ](../{entities,concepts,metrics,syntheses}/<slug>.md)
                     -> ](<slug>.md)         (flat sibling)
  - target: ../{...}/<slug>.md
                     -> target: <slug>.md    (frontmatter edge)
  - [label](<any remaining pathed .md link>)
                     -> label                (dead in a portable bundle -> delink)

The delink pass is deliberately general: after the knowledge folders are
flattened to siblings, ANY relative `.md` link that still carries a path
points outside the bundle — the dropped `_evidence/` layer (both the
`../_evidence/...` and SCHEMA-synthesis `.dbt-wiki/_evidence/...` shapes),
`_archive/`, or source-repo files (`../../models/...`) — none of which
exist at a portable target. The label is kept as plain text.

Pure path-shape logic — no project/company/personal specifics. Idempotent
(safe to re-run after any re-freeze). Exit code 1 if any broken intra-knowledge
link remains, so it can gate Step 7.

Usage:  uv run flatten_links.py <bundle>/knowledge
"""
import sys
import re
from pathlib import Path

KNOWLEDGE_FOLDERS = ("entities", "concepts", "metrics", "syntheses")

_CROSS_BODY = re.compile(r"\]\(\.\./(?:" + "|".join(KNOWLEDGE_FOLDERS) + r")/([^)]+\.md)\)")
_CROSS_FM = re.compile(r"(target:\s*)\.\./(?:" + "|".join(KNOWLEDGE_FOLDERS) + r")/([^\s]+\.md)")
# Any markdown link to a *pathed* .md target that survived the flatten above
# is dead in a portable bundle (dropped layer or source-repo path) -> delink.
_DEAD_PATHED = re.compile(r"\[([^\]]+)\]\((?!https?://)[^)]*/[^)]*\.md\)")


def _basename(path: str) -> str:
    return path.rsplit("/", 1)[-1]


def flatten_text(text: str) -> tuple[str, int, int]:
    """Return (rewritten_text, cross_folder_count, dead_delinked_count)."""
    cross = 0
    dead = 0

    def _body(m):
        nonlocal cross
        cross += 1
        return f"]({_basename(m.group(1))})"

    def _fm(m):
        nonlocal cross
        cross += 1
        return f"{m.group(1)}{_basename(m.group(2))}"

    def _dead(m):
        nonlocal dead
        dead += 1
        return m.group(1)  # keep the label, drop the dead link

    # Order matters: flatten knowledge-folder links to siblings FIRST,
    # then delink whatever pathed .md links remain (all dead by design).
    text = _CROSS_BODY.sub(_body, text)
    text = _CROSS_FM.sub(_fm, text)
    text = _DEAD_PATHED.sub(_dead, text)
    return text, cross, dead


def count_broken(kdir: Path) -> list[str]:
    broken = []
    for md in kdir.glob("*.md"):
        for m in re.finditer(r"\]\(([^)]+\.md)\)", md.read_text(encoding="utf-8")):
            link = m.group(1).strip()
            if link.startswith("http"):
                continue
            if not (md.parent / link).resolve().exists():
                broken.append(f"{md.name} -> {link}")
    return broken


def main(kdir: Path) -> int:
    files = cross = evid = 0
    for md in sorted(kdir.glob("*.md")):
        original = md.read_text(encoding="utf-8")
        rewritten, c, e = flatten_text(original)
        cross += c
        evid += e
        if rewritten != original:
            md.write_text(rewritten, encoding="utf-8")
            files += 1
    print(f"flatten_links: {files} files rewritten | "
          f"{cross} cross-folder links flattened | {evid} dropped-evidence links delinked")
    broken = count_broken(kdir)
    print(f"flatten_links: {len(broken)} broken intra-knowledge links remain")
    for b in broken:
        print(f"  STILL BROKEN: {b}")
    return 1 if broken else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(Path(sys.argv[1])))
