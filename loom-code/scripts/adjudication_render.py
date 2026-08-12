#!/usr/bin/env python3
"""Render units-JSON (from adjudication_split.py) into a self-contained
HTML view per the adjudication-view protocol
(loom-code/skills/using-loom-code/protocols/adjudication-view.md).

Doc mode: one section per unit — the target-language `rendition` (the
language `--lang` selects, default zh-Hant) is the primary text; the EN
`source_text` is collapsible beside it in a
`<details><summary>原文</summary>...</details>` block. All content
interpolations (heading / source_text / rendition) are html.escape'd —
source and rendition are untrusted text, never raw-HTML-injected.

Styling is embedded (single `<style>` block, no external stylesheet,
no external URLs of any kind) and restrained: one CSS accent-color
variable (`--accent`), no gradients, no card borders/shadows, no emoji
in chrome, print-safe (A4 @page rule).

Verdict mode: one 4-column table row per finding, as inline markdown by
default or as an HTML page under `--html`.

CLI:
    python3 adjudication_render.py doc <units-json-file> [-o out.html]
                                      [--lang <tag>]
    python3 adjudication_render.py verdict <units-json-file> [--html]
                                      [-o out.html] [--lang <tag>]

Emits HTML to stdout by default, or to the path given by `-o`.
"""

import argparse
import html
import json
import sys
from pathlib import Path

from adjudication_profiles import get_profile

# Sentinel replaced (via str.replace, not str.format -- CSS is full of
# braces that str.format would otherwise try to parse) with the
# resolved profile's `font_stack` at render time. Kept as a plain
# marker rather than a `{font_stack}` format field for that reason.
_FONT_STACK_PLACEHOLDER = "__FONT_STACK__"

STYLE = """
:root {
  --accent: #2b5797;
  --fg: #1a1a1a;
  --bg: #ffffff;
  --muted: #555555;
}
* { box-sizing: border-box; }
body {
  font-family: __FONT_STACK__;
  color: var(--fg);
  background: var(--bg);
  max-width: 52rem;
  margin: 0 auto;
  padding: 2rem 1.5rem;
  line-height: 1.6;
}
h1 {
  font-size: 1.4rem;
  border-bottom: 1px solid var(--accent);
  padding-bottom: 0.4rem;
}
section.unit {
  margin: 1.75rem 0;
}
section.unit h2 {
  font-size: 1.05rem;
  color: var(--accent);
  margin-bottom: 0.5rem;
}
p.rendition {
  white-space: pre-wrap;
  margin: 0 0 0.5rem 0;
}
details {
  color: var(--muted);
  margin-top: 0.4rem;
}
details summary {
  cursor: pointer;
  color: var(--accent);
}
details pre {
  white-space: pre-wrap;
  font-family: inherit;
  margin: 0.4rem 0 0 0;
}
@media print {
  @page { size: A4; margin: 2cm; }
  details { break-inside: avoid; }
}
table.verdict {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
}
table.verdict th, table.verdict td {
  border: 1px solid var(--muted);
  padding: 0.4rem 0.6rem;
  text-align: left;
  vertical-align: top;
}
table.verdict th {
  color: var(--accent);
}
""".strip()

DOC_PAGE_TEMPLATE = """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
{style}
</style>
</head>
<body>
<h1>{title}</h1>
{units_html}
</body>
</html>
"""

UNIT_TEMPLATE = """<section class="unit" id="{unit_id}">
<h2>{heading}</h2>
<p class="rendition">{rendition}</p>
<details>
<summary>原文</summary>
<pre>{source_text}</pre>
</details>
</section>"""


def _render_page(title, units_html, lang):
    """Resolve `lang` to its profile ONCE and fill the shared
    DOC_PAGE_TEMPLATE -- the single template both doc and verdict-HTML
    modes reuse, parameterized by the page attributes (`<html lang>`,
    font stack) instead of forking a per-language template. `page_lang`
    / `font_stack` come from a frozen, developer-authored profile (not
    attacker-reachable request/unit data), so they are interpolated
    as-is -- html.escape is reserved for the untrusted `title` and
    per-unit content, kept uniform with the rest of this module."""
    profile = get_profile(lang)
    style_rendered = STYLE.replace(_FONT_STACK_PLACEHOLDER, profile.font_stack)
    return DOC_PAGE_TEMPLATE.format(
        lang=profile.page_lang,
        title=html.escape(title),
        style=style_rendered,
        units_html=units_html,
    )


def render_doc(units, title="Adjudication View", lang="zh-Hant"):
    """Render `units` (a list of unit dicts per the units-JSON schema)
    into a single self-contained HTML document string. `lang` selects
    the language profile (Task 3) that supplies the page's `<html
    lang>` attribute and font stack; default "zh-Hant" matches the
    pre-Task-3 hardcoded behavior byte-for-byte."""
    units_html = "\n".join(
        UNIT_TEMPLATE.format(
            unit_id=html.escape(unit["id"]),
            heading=html.escape(unit["heading"]),
            rendition=html.escape(unit["rendition"]),
            source_text=html.escape(unit["source_text"]),
        )
        for unit in units
    )
    return _render_page(title, units_html, lang)


# The two content column labels come from the resolved profile
# (`verdict_labels`); `#` and `severity` are protocol field names and
# are not translated. Before Task 3's profile layer reached verdict mode
# these were Traditional-Chinese literals baked into both templates.
VERDICT_TABLE_HEADER_TEMPLATE = "| # | severity | {summary} | {anchor} |\n|---|---|---|---|"

VERDICT_HTML_TABLE_TEMPLATE = """<table class="verdict">
<thead><tr><th>#</th><th>severity</th><th>{summary}</th><th>{anchor}</th></tr></thead>
<tbody>
{rows}
</tbody>
</table>"""

VERDICT_ROW_TEMPLATE = "<tr><td>{id}</td><td>{severity}</td><td>{rendition}</td><td>{where}</td></tr>"


def _field_value(source_text, field_name):
    """Extract a field's value verbatim from a unit's source_text field
    block (one `key: value` line per field, as produced by
    adjudication_split.py's split_verdict()). Returns "" if the field
    is absent. This is the ONLY way severity/where reach the table —
    they are copied from the parsed field, never recomputed from the
    unit's other data (heading, anchors)."""
    prefix = f"{field_name}:"
    for line in source_text.splitlines():
        if line.startswith(prefix):
            return line[len(prefix) :].strip()
    return ""


def _md_cell(text):
    """Collapse a rendition to one markdown-table line: newlines become
    spaces (a table row is one line), and a literal `|` is escaped so
    it can't be misread as an extra column boundary."""
    return text.replace("\r\n", " ").replace("\n", " ").replace("\r", " ").replace(
        "|", "\\|"
    )


def render_verdict(units, lang="zh-Hant"):
    """Render `units` (verdict-mode units-JSON, see adjudication_split.py
    split_verdict()) into an inline markdown table: one row per finding,
    in source order (never re-sorted by severity or anything else).
    severity and the anchor (where) are extracted verbatim from each
    unit's source_text field block — copied, never recomputed — per the
    adjudication-view protocol's severity carry-through rule. `lang`
    selects the profile supplying the two content column labels; default
    "zh-Hant" matches the pre-profile-layer header byte-for-byte."""
    summary_label, anchor_label = get_profile(lang).verdict_labels
    lines = [
        VERDICT_TABLE_HEADER_TEMPLATE.format(
            summary=summary_label, anchor=anchor_label
        )
    ]
    for unit in units:
        severity = _field_value(unit["source_text"], "severity")
        where = _field_value(unit["source_text"], "where")
        rendition = _md_cell(unit["rendition"])
        lines.append(f"| {unit['id']} | {severity} | {rendition} | {where} |")
    return "\n".join(lines) + "\n"


def render_verdict_html(units, title="Adjudication Verdict", lang="zh-Hant"):
    """Render `units` into a self-contained HTML page holding the same
    4-column table as `render_verdict`, reusing the doc template's
    styling (STYLE, DOC_PAGE_TEMPLATE). All cell content is
    html.escape'd — rendition/severity/where may carry attacker-
    reachable text from a translated finding. `lang` selects the
    language profile the same way `render_doc` does (Task 3); default
    "zh-Hant" matches the pre-Task-3 hardcoded behavior byte-for-byte."""
    rows = "\n".join(
        VERDICT_ROW_TEMPLATE.format(
            id=html.escape(unit["id"]),
            severity=html.escape(_field_value(unit["source_text"], "severity")),
            rendition=html.escape(unit["rendition"]),
            where=html.escape(_field_value(unit["source_text"], "where")),
        )
        for unit in units
    )
    summary_label, anchor_label = get_profile(lang).verdict_labels
    table_html = VERDICT_HTML_TABLE_TEMPLATE.format(
        rows=rows, summary=summary_label, anchor=anchor_label
    )
    return _render_page(title, table_html, lang)


# The accepted `mode` values, nothing more: `main()` branches on the
# mode explicitly (verdict has two renditions, doc has one), so this
# stopped being a dispatch table and only its keys were ever live.
MODES = ("doc", "verdict")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=sorted(MODES), help="render mode")
    parser.add_argument("path", help="path to the units-JSON file")
    parser.add_argument(
        "-o", "--output", help="output HTML path (default: stdout)", default=None
    )
    parser.add_argument(
        "--html",
        action="store_true",
        help="verdict mode only: emit the HTML table rendition instead of markdown",
    )
    parser.add_argument(
        "--lang",
        default="zh-Hant",
        help="language profile tag for page attributes (default: zh-Hant)",
    )
    args = parser.parse_args(argv)
    get_profile(args.lang)  # resolve once up front -- fail loud on an
    # unknown tag before doing any rendering work, for both modes.

    units = json.loads(Path(args.path).read_text(encoding="utf-8"))
    if args.mode == "verdict" and args.html:
        rendered = render_verdict_html(units, lang=args.lang)
    elif args.mode == "verdict":
        rendered = render_verdict(units, lang=args.lang)
    else:
        rendered = render_doc(units, lang=args.lang)

    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
