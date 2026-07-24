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
``check_id`` is one of the covered checks or ``PARSE`` (unreadable /
non-UTF-8 file, frontmatter beyond the minimal-parser subset).
Exit code: 0 = clean, 1 = violations found, 2 = internal error (crash
path — distinct from "has violations" so loop callers never conflate).

Stdlib-only by contract (plugin self-containment). The stdlib has no YAML
parser, so frontmatter is read by a minimal YAML-subset parser (scalars,
inline lists, block lists) that unquotes values — honoring the SSOT's
"parse, do not regex-extract" rule for L14 basename comparison.
"""

import argparse
import json
import re
import sys
import unicodedata
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
# YAML block-scalar indicator (| / > with optional chomping/indent) —
# beyond the minimal parser's subset; must be reported, never swallowed
BLOCK_SCALAR_RE = re.compile(r"^[|>][0-9+-]{0,2}$")

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

    Returns (fields, body_start_index, key_lines, issues):
    body_start_index is the 0-based index of the first body line;
    key_lines maps top-level keys to their 1-based line numbers;
    issues is a list of (lineno, key, message) parse-level findings
    (values the subset parser cannot represent — never swallowed).

    An empty value parses to ``None`` (converted to a list only when
    block-list ``- item`` lines follow); block-scalar values (``|``/``>``)
    parse to ``None`` plus an issue.
    """
    fields, key_lines, issues = {}, {}, []
    if not lines or lines[0].strip() != "---":
        return fields, 0, key_lines, issues
    current_list_key = None
    end = len(lines)  # unterminated: treat all as frontmatter
    for i in range(1, len(lines)):
        line = lines[i]
        if line.strip() == "---":
            end = i + 1
            break
        stripped = line.strip()
        if not stripped:
            continue
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if m and line[:1] not in (" ", "\t"):
            key, val = m.group(1), m.group(2).strip()
            key_lines[key] = i + 1
            current_list_key = None
            if val == "":
                fields[key] = None
                current_list_key = key
            elif BLOCK_SCALAR_RE.match(val):
                fields[key] = None
                issues.append(
                    (i + 1, key,
                     f"frontmatter key '{key}' uses a YAML block scalar "
                     f"('{val}') the minimal parser cannot read"))
            elif val.startswith("[") and val.endswith("]"):
                fields[key] = [unquote(x) for x in val[1:-1].split(",")
                               if x.strip()]
            else:
                fields[key] = unquote(val)
        elif stripped.startswith("- ") and current_list_key is not None:
            if fields[current_list_key] is None:
                fields[current_list_key] = []
            fields[current_list_key].append(unquote(stripped[2:]))
    return fields, end, key_lines, issues


def link_target(inner):
    """Resolve a wikilink's inner text to its link target: strip display
    alias (``|``) and anchor (``#``), NFC-normalize (macOS filesystems
    hand back NFD names while links are typed NFC — both sides must
    land on one form or every accented/CJK link is a false L07)."""
    return unicodedata.normalize(
        "NFC", inner.split("|", 1)[0].split("#", 1)[0].strip())


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
        (self.fields, self.body_start,
         self.key_lines, self.fm_issues) = parse_frontmatter(self.lines)
        self.unparsed_keys = {key for _, key, _ in self.fm_issues}
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
    """Returns (pages, failures); failures = [(rel, message)] for files
    that cannot be read/decoded — one bad file must not abort the scan."""
    pages, failures = [], []
    for folder in WIKI_FOLDERS:
        d = wiki_root / folder
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.md")):
            rel = f"{folder}/{p.name}"
            try:
                pages.append(Page(p, rel))
            except (UnicodeDecodeError, OSError) as exc:
                failures.append((rel, f"cannot read file: {exc}"))
    return pages, failures


def build_inventory(pages):
    """Link-resolution inventory: key -> [page rel paths]. Keys are
    filename stems AND frontmatter aliases (page-format.md: bare-basename
    match including frontmatter aliases)."""
    inv = {}
    for page in pages:
        keys = {page.path.stem}
        aliases = page.fields.get("aliases") or []
        if isinstance(aliases, str):
            aliases = [aliases]
        keys.update(a for a in aliases if a)
        for k in keys:
            inv.setdefault(unicodedata.normalize("NFC", k), []) \
                .append(page.rel)
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
    if "summary" not in page.fields:
        return  # absence is L01's finding
    if "summary" in page.unparsed_keys:
        return  # PARSE owns the block-scalar defect; don't double-report
    summary = page.fields["summary"]
    line = page.key_lines.get("summary")
    if not isinstance(summary, str) or not summary.strip():
        out("L02", "error", page.rel, line,
            "summary is empty or not a string")
        return
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
    expected = unicodedata.normalize("NFC", Path(source_path).stem)
    for target in links:
        if target != expected:
            out("L14", "warning", page.rel, start,
                f"source wikilink basename [[{target}]] != source_path "
                f"stem '{expected}' (likely stale)")


def conservation_counters(page):
    # Words semantics (since 3.20.1): each [[...]] wikilink — including
    # [[target|display]] / [[target#anchor]] — is normalized to a single
    # placeholder token before whitespace-splitting, so the count is
    # insensitive to the link TARGET's word count. Benign retargets
    # ([[Two Word Target]] -> [[Oneword]]) no longer shift the counter,
    # while deleting the link (or surrounding prose) still lowers it.
    # Motivation: wiki-update smoke Finding #1 — ratchet false breach
    # 308->307 on an L07-class retarget.
    return {
        "type": "counters",
        "file": page.rel,
        # U+FFFC OBJECT REPLACEMENT CHARACTER: non-whitespace, so a link
        # glued to punctuation ("[[x]].") still merges into one token,
        # exactly as the pre-3.20.1 counter treated single-word targets.
        "words": len(WIKILINK_RE.sub("￼", page.body).split()),
        "links": len(WIKILINK_RE.findall(page.body)),
        "headings": sum(1 for line in page.body_lines
                        if HEADING_RE.match(line)),
    }


def run(wiki_root, stream):
    pages, failures = scan_wiki(wiki_root)
    inventory = build_inventory(pages)
    stems = sorted({unicodedata.normalize("NFC", p.path.stem)
                    for p in pages})
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

    for rel, message in failures:
        out("PARSE", "error", rel, None, message)
    for page in pages:
        for lineno, _key, message in page.fm_issues:
            out("PARSE", "error", page.rel, lineno, message)
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
        "files": len(pages) + len(failures),
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
    try:
        return run(wiki_root, sys.stdout)
    except Exception as exc:  # crash path: exit 2, distinct from
        # "violations found" (1) so loop callers never misread a crash
        print(f"wiki_lint_check: internal error: {exc!r}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
