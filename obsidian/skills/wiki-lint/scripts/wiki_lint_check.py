#!/usr/bin/env python3
"""Mechanical wiki lint validator — error-lane checks + conservation counters.

LOCKSTEP NOTE (SSOT): check semantics are defined by
``obsidian/skills/wiki-lint/references/lint-checks.md`` and the severity
map in ``obsidian/skills/wiki-lint/SKILL.md``. Semantic changes land in
those files FIRST; this script follows in lockstep.

Covered checks (deterministic lane): L01 frontmatter completeness,
L02 summary length, L03 required body sections, L04 wikilink format,
L07 broken intra-wiki wikilinks (alias-aware, ``## Source`` exemption),
L14 reference-page ``## Source`` wikilink.

Output: JSONL on stdout —
  {"type": "violation", "check_id", "severity", "file", "line", "detail"}
  {"type": "counters", "file", "words", "links", "headings"}
  {"type": "summary", "files", "violations", "errors", "warnings", "by_check"}
Exit code: 0 = clean, 1 = violations found.

Stdlib-only by contract (plugin self-containment). The stdlib has no YAML
parser, so frontmatter is read by a minimal YAML-subset parser (scalars,
inline lists, block lists) that unquotes values — honoring the SSOT's
"parse, do not regex-extract" rule for L14 basename comparison.
"""

import argparse
import json
import re
import sys
from pathlib import Path

WIKI_FOLDERS = ("entities", "concepts", "synthesis", "skills",
                "journal", "references")

KNOWLEDGE_FM = ("title", "type", "domain", "status", "updated",
                "tags", "sources_count", "summary")
REQUIRED_FM = {
    "wiki-entity": KNOWLEDGE_FM,
    "wiki-concept": KNOWLEDGE_FM,
    "wiki-synthesis": KNOWLEDGE_FM,
    "wiki-skill": KNOWLEDGE_FM,
    "wiki-journal": KNOWLEDGE_FM + ("date",),
    "wiki-reference": ("title", "type", "source_path", "date", "ingested",
                       "contributes_to", "tags", "summary"),
}

KNOWLEDGE_SECTIONS = ("## Summary", "## Key Facts", "## Connections")
REQUIRED_SECTIONS = {
    "wiki-entity": KNOWLEDGE_SECTIONS,
    "wiki-concept": KNOWLEDGE_SECTIONS,
    "wiki-synthesis": KNOWLEDGE_SECTIONS,
    "wiki-skill": KNOWLEDGE_SECTIONS,
    "wiki-journal": KNOWLEDGE_SECTIONS,
    "wiki-reference": ("## Source", "## TL;DR", "## Key Contributions"),
}

WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
BACKTICK_WIKILINK_RE = re.compile(r"`[^`]*\[\[[^\]]+\]\][^`]*`")
# L14 malformed-link regex verbatim from lint-checks.md
L14_MALFORMED_RE = re.compile(r"\[\[[^\]]*/[^\]]+\]\]|\[\[[^\]]+\.md[\]#]")
HEADING_RE = re.compile(r"^#{1,6}\s")
H2_RE = re.compile(r"^##\s+(.+?)\s*$")

OUT_OF_SCOPE = """\
Out-of-scope here (LLM-lane checks, run via the obsidian:wiki-lint skill):
  L05 Mermaid placement          L06 orphan pages
  L08 stale pages                L09 provenance drift
  L10 manifest divergence        L11 contradiction surfaced
  L12 cross-page disagreement    L13 aliases on cross-language slug
  L15 near-duplicate pages
"""


def unquote(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def parse_frontmatter(lines):
    """Minimal YAML-subset frontmatter parser (stdlib-only contract).

    Returns (fields, body_start_index, key_lines) where body_start_index
    is the 0-based index of the first body line and key_lines maps
    top-level keys to their 1-based line numbers.
    """
    fields, key_lines = {}, {}
    if not lines or lines[0].strip() != "---":
        return fields, 0, key_lines
    current_list_key = None
    for i in range(1, len(lines)):
        line = lines[i]
        if line.strip() == "---":
            return fields, i + 1, key_lines
        stripped = line.strip()
        if not stripped:
            continue
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if m and line[:1] not in (" ", "\t"):
            key, val = m.group(1), m.group(2).strip()
            key_lines[key] = i + 1
            current_list_key = None
            if val == "":
                fields[key] = []
                current_list_key = key
            elif val.startswith("[") and val.endswith("]"):
                fields[key] = [unquote(x) for x in val[1:-1].split(",")
                               if x.strip()]
            else:
                fields[key] = unquote(val)
        elif stripped.startswith("- ") and current_list_key is not None:
            fields[current_list_key].append(unquote(stripped[2:]))
    return fields, len(lines), key_lines  # unterminated: treat all as fm


def link_target(inner):
    """Resolve a wikilink's inner text to its link target:
    strip display alias (``|``) and anchor (``#``)."""
    return inner.split("|", 1)[0].split("#", 1)[0].strip()


def levenshtein_leq(a, b, cap=2):
    """Banded Levenshtein: distance if <= cap else None."""
    if abs(len(a) - len(b)) > cap:
        return None
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1,
                           prev[j - 1] + (ca != cb)))
        if min(cur) > cap:
            return None
        prev = cur
    return prev[-1] if prev[-1] <= cap else None


class Page:
    def __init__(self, path, rel):
        self.path = path
        self.rel = rel  # posix path relative to wiki root
        text = path.read_text(encoding="utf-8")
        self.lines = text.split("\n")
        self.fields, self.body_start, self.key_lines = \
            parse_frontmatter(self.lines)
        self.body_lines = self.lines[self.body_start:]
        self.body = "\n".join(self.body_lines)
        self.is_reference = rel.startswith("references/")
        # level-2 headings: normalized text -> 1-based line number
        self.h2 = {}
        for idx, line in enumerate(self.body_lines):
            m = H2_RE.match(line)
            if m:
                self.h2.setdefault("## " + m.group(1), self.body_start + idx + 1)

    def body_line_no(self, body_idx):
        return self.body_start + body_idx + 1

    def source_section_span(self):
        """1-based (start, end] line range of the ``## Source`` section
        body (heading line excluded, up to next H2 or EOF), or None."""
        start = self.h2.get("## Source")
        if start is None:
            return None
        end = len(self.lines)
        for idx in range(start, len(self.lines)):  # lines after heading
            if H2_RE.match(self.lines[idx]):
                end = idx  # 1-based line number of next H2 minus 1... see use
                break
        return (start, end)


def scan_wiki(wiki_root):
    pages = []
    for folder in WIKI_FOLDERS:
        d = wiki_root / folder
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.md")):
            pages.append(Page(p, f"{folder}/{p.name}"))
    return pages


def build_inventory(pages):
    """Link-resolution inventory: key -> [page rel paths]. Keys are
    filename stems AND frontmatter aliases (page-format.md: bare-basename
    match including frontmatter aliases)."""
    inv = {}
    for page in pages:
        keys = {page.path.stem}
        aliases = page.fields.get("aliases", [])
        if isinstance(aliases, str):
            aliases = [aliases]
        keys.update(a for a in aliases if a)
        for k in keys:
            inv.setdefault(k, []).append(page.rel)
    return inv


def check_l01(page, out):
    ptype = page.fields.get("type")
    if not isinstance(ptype, str) or ptype not in REQUIRED_FM:
        out("L01", "error", page.rel, None,
            f"missing or unknown page type: {ptype!r}")
        return
    missing = [f for f in REQUIRED_FM[ptype] if f not in page.fields]
    if missing:
        out("L01", "error", page.rel, None,
            f"missing frontmatter fields: [{', '.join(missing)}]")


def check_l02(page, out):
    summary = page.fields.get("summary")
    if not isinstance(summary, str) or not summary:
        return  # absence is L01's finding
    line = page.key_lines.get("summary")
    problems = []
    if len(summary) > 200:
        problems.append(f"too long ({len(summary)} chars > 200)")
    if "\n" in summary:
        problems.append("not single-line")
    if re.search(r"`|\*\*|\[\[|\]\(|^#", summary):
        problems.append("contains markdown")
    if problems:
        out("L02", "error", page.rel, line,
            "summary " + "; ".join(problems))


def check_l03(page, out):
    ptype = page.fields.get("type")
    required = REQUIRED_SECTIONS.get(ptype if isinstance(ptype, str) else "")
    if not required:
        return  # unknown type already reported by L01
    missing = [s for s in required if s not in page.h2]
    if missing:
        out("L03", "error", page.rel, None,
            f"missing body sections: [{', '.join(missing)}]")


def check_l04(page, out):
    """Wikilink format. The ``## Source`` section of reference pages is
    exempt: L14 owns source-wikilink format there (same one-check-owns-
    one-defect split the SSOT states between L04 and L07)."""
    exempt_span = page.source_section_span() if page.is_reference else None
    for idx, line in enumerate(page.body_lines):
        lineno = page.body_line_no(idx)
        if exempt_span and exempt_span[0] < lineno <= exempt_span[1]:
            continue
        for m in BACKTICK_WIKILINK_RE.finditer(line):
            out("L04", "error", page.rel, lineno,
                f"backtick-wrapped wikilink renders as code, not a link: "
                f"{m.group(0)}")
        for m in WIKILINK_RE.finditer(line):
            target = link_target(m.group(1))
            if "/" in target:
                out("L04", "error", page.rel, lineno,
                    f"wikilink has path prefix (must be bare filename): "
                    f"[[{m.group(1)}]]")
            elif target.endswith(".md"):
                out("L04", "error", page.rel, lineno,
                    f"wikilink has .md extension: [[{m.group(1)}]]")


def check_l07(page, inventory, stems, out):
    """Broken intra-wiki wikilinks. Path-prefixed / .md forms are L04's;
    wikilinks inside a reference page's ``## Source`` section are exempt
    (validated by L14 against source_path instead)."""
    exempt_span = page.source_section_span() if page.is_reference else None
    for idx, line in enumerate(page.body_lines):
        lineno = page.body_line_no(idx)
        if exempt_span and exempt_span[0] < lineno <= exempt_span[1]:
            continue
        for m in WIKILINK_RE.finditer(line):
            target = link_target(m.group(1))
            if not target or "/" in target or target.endswith(".md"):
                continue  # caught by L04, not L07
            matches = inventory.get(target, [])
            if len(matches) == 1:
                continue
            if len(matches) == 0:
                suggestion = ""
                best = None
                for stem in stems:
                    d = levenshtein_leq(target, stem, 2)
                    if d is not None and (best is None or d < best[0]):
                        best = (d, stem)
                if best:
                    suggestion = f" (did you mean [[{best[1]}]]?)"
                out("L07", "error", page.rel, lineno,
                    f"broken wikilink [[{target}]]{suggestion}")
            else:
                out("L07", "error", page.rel, lineno,
                    f"wikilink [[{target}]] matches {len(matches)} pages "
                    f"(filename/alias collision): {', '.join(sorted(matches))}")


def check_l14(page, out):
    if not page.is_reference:
        return
    span = page.source_section_span()
    if span is None:
        out("L14", "warning", page.rel, None,
            "missing `## Source` section")
        return
    start, end = span
    section = "\n".join(page.lines[start:end])
    malformed = False
    for m in L14_MALFORMED_RE.finditer(section):
        malformed = True
        snippet = m.group(0)
        if "/" in snippet:
            detail = f"source wikilink has path prefix: {snippet}"
        else:
            detail = f"source wikilink has .md extension: {snippet}"
        out("L14", "error", page.rel, start,  # heading line as anchor
            detail)
    links = [link_target(m.group(1))
             for m in WIKILINK_RE.finditer(section)]
    if not links:
        out("L14", "warning", page.rel, start,
            "`## Source` section contains no wikilink")
        return
    if malformed:
        return  # fix the malformed link first; basename check would dup it
    source_path = page.fields.get("source_path")
    if not isinstance(source_path, str) or not source_path:
        return  # missing source_path is L01's finding
    expected = Path(source_path).stem
    for target in links:
        if target != expected:
            out("L14", "warning", page.rel, start,
                f"source wikilink basename [[{target}]] != source_path "
                f"stem '{expected}' (likely stale)")


def conservation_counters(page):
    return {
        "type": "counters",
        "file": page.rel,
        "words": len(page.body.split()),
        "links": len(WIKILINK_RE.findall(page.body)),
        "headings": sum(1 for line in page.body_lines
                        if HEADING_RE.match(line)),
    }


def run(wiki_root, stream):
    pages = scan_wiki(wiki_root)
    inventory = build_inventory(pages)
    stems = sorted({p.path.stem for p in pages})
    violations = []

    def out(check_id, severity, file, line, detail):
        violations.append({
            "type": "violation",
            "check_id": check_id,
            "severity": severity,
            "file": file,
            "line": line,
            "detail": detail,
        })

    for page in pages:
        check_l01(page, out)
        check_l02(page, out)
        check_l03(page, out)
        check_l04(page, out)
        check_l07(page, inventory, stems, out)
        check_l14(page, out)

    for v in violations:
        print(json.dumps(v, ensure_ascii=False), file=stream)
    for page in pages:
        print(json.dumps(conservation_counters(page), ensure_ascii=False),
              file=stream)
    by_check = {}
    for v in violations:
        by_check[v["check_id"]] = by_check.get(v["check_id"], 0) + 1
    summary = {
        "type": "summary",
        "files": len(pages),
        "violations": len(violations),
        "errors": sum(1 for v in violations if v["severity"] == "error"),
        "warnings": sum(1 for v in violations if v["severity"] == "warning"),
        "by_check": dict(sorted(by_check.items())),
    }
    print(json.dumps(summary, ensure_ascii=False), file=stream)
    return 1 if violations else 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Mechanical wiki lint validator: deterministic "
                    "error-lane checks L01/L02/L03/L04/L07/L14 + per-file "
                    "conservation counters (word/link/heading). Semantics "
                    "SSOT: references/lint-checks.md.",
        epilog=OUT_OF_SCOPE,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "wiki_root",
        help="path to the wiki/ directory (containing entities/, "
             "concepts/, synthesis/, skills/, journal/, references/)",
    )
    args = parser.parse_args(argv)
    wiki_root = Path(args.wiki_root)
    if not wiki_root.is_dir():
        parser.error(f"wiki root not found or not a directory: {wiki_root}")
    return run(wiki_root, sys.stdout)


if __name__ == "__main__":
    sys.exit(main())
