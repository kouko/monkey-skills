#!/usr/bin/env python3
"""Render units-JSON (from adjudication_split.py) into a self-contained
HTML view per the adjudication-view protocol
(loom-code/skills/using-loom-code/protocols/adjudication-view.md).

Doc mode: one section per unit — the target-language `rendition` (the
language `--lang` selects, default zh-Hant) is the primary text; the EN
`source_text` is collapsible beside it in a
`<details><summary>原文</summary>...</details>` block. `heading` and
`source_text` are html.escape'd; `rendition` is parsed as markdown and
injected as raw HTML (bold, italic, lists, blockquotes, and Mermaid
fences are all converted).

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
import base64
import html
import json
import sys
from pathlib import Path

from markdown_it import MarkdownIt
from markdown_it.rules_block import table

from adjudication_profiles import get_profile

# Sentinel replaced (via str.replace, not str.format -- CSS is full of
# braces that str.format would otherwise try to parse) with the
# resolved profile's `font_stack` at render time. Kept as a plain
# marker rather than a `{font_stack}` format field for that reason.
_FONT_STACK_PLACEHOLDER = "__FONT_STACK__"

# Cached markdown-it parser — constructed once, reused across all renders.
# The default config handles headings, lists, blockquotes, bold/italic,
# tables, and fenced code blocks (including ` ```mermaid ` → <pre><code
# class="language-mermaid">).
# The table rule is registered before 'fence' so table pipes don't
# interfere with fenced code block detection.
_MD = MarkdownIt()
_MD.block.ruler.before('fence', 'table', table, {
    'alt': ['paragraph', 'reference', 'blockquote', 'list'],
})


def _render_markdown(md_text: str) -> str:
    """Convert markdown text to HTML via markdown-it.

    Fenced code blocks (including ` ```mermaid `) are converted to HTML.
    Mermaid fences specifically become `<div class="mermaid">` (not
    `<pre><code class="language-mermaid">`) so browser-side Mermaid JS
    can locate and render them — the browser scans the DOM for elements
    with class="mermaid" and transforms them in place.

    Tables are converted to `<table><thead><tbody>` (the table rule is
    registered before the fence rule so pipe characters inside tables
    are not confused with fenced code block delimiters).

    Other markdown syntax (bold, italic, lists, blockquotes, etc.)
    is also converted.

    The output is safe for direct HTML interpolation (no raw user data —
    markdown-it generates the HTML structure from trusted source text).
    """
    if not md_text:
        return ""
    result = _MD.render(md_text)
    # Convert mermaid fences from <pre><code class="language-mermaid">
    # to <div class="mermaid"> for browser-side Mermaid JS compatibility.
    result = result.replace(
        '<pre><code class="language-mermaid">',
        '<div class="mermaid">',
    )
    result = result.replace('</code></pre>', '</div>')
    return result

STYLE = """
:root {
  --accent: #1a1a1a;
  --accent-light: #e0e0e0;
  --fg: #1a1a1a;
  --bg: #ffffff;
  --muted: #666666;
  --muted-light: #f0f0f0;
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
  font-size: 2.5rem;
  border-bottom: 2px solid var(--accent);
  padding-bottom: 0.5rem;
  margin-bottom: 0.6rem;
}
section.unit {
  margin: 2.5rem 0;
}
section.unit h2 {
  font-size: 1.8rem;
  color: var(--accent);
  margin-bottom: 0.7rem;
  font-weight: 600;
}
div.rendition h3 {
  font-size: 1.7rem;
  margin-top: 1.2rem;
  margin-bottom: 0.5rem;
  color: var(--accent);
  font-weight: 600;
}
div.rendition h4 {
  font-size: 1.6rem;
  margin-top: 1rem;
  margin-bottom: 0.4rem;
  color: var(--fg);
  font-weight: 600;
}
div.rendition h5 {
  font-size: 1.5rem;
  margin-top: 0.9rem;
  margin-bottom: 0.35rem;
  color: var(--fg);
  font-weight: 500;
}
div.rendition h6 {
  font-size: 1.4rem;
  margin-top: 0.8rem;
  margin-bottom: 0.3rem;
  color: var(--muted);
  font-weight: 500;
}
div.rendition {
  margin: 0 0 0.5rem 0;
  font-size: 0.95em;
  line-height: 1.7;
}
div.rendition p {
  margin: 0.5rem 0;
}
div.rendition p:first-child {
  margin-top: 0;
}
div.rendition p:last-child {
  margin-bottom: 0;
}
div.rendition table {
  border-collapse: collapse;
  margin: 0.75rem 0;
  font-size: 0.9em;
  width: 100%;
}
div.rendition th, div.rendition td {
  border: 1px solid var(--muted-light);
  padding: 0.5rem 0.75rem;
  text-align: left;
}
div.rendition th {
  color: var(--accent);
  background: var(--accent-light);
  font-weight: 600;
}
div.rendition tr:hover td {
  background: var(--muted-light);
}
div.rendition code {
  background: var(--muted-light);
  padding: 0.15em 0.35em;
  border-radius: 3px;
  font-size: 0.9em;
  font-family: "SF Mono", "Fira Code", "Cascadia Code", monospace;
}
div.rendition a {
  color: var(--accent);
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: border-color 0.15s;
}
div.rendition a:hover {
  border-bottom-color: var(--accent);
}
div.rendition blockquote {
  border-left: 3px solid var(--accent);
  margin: 0.75rem 0;
  padding: 0.4rem 0 0.4rem 1rem;
  color: var(--muted);
  background: var(--accent-light);
}
div.rendition blockquote p {
  margin: 0.3rem 0;
}
div.rendition ul, div.rendition ol {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
}
div.rendition li {
  margin: 0.25rem 0;
}
div.rendition .mermaid {
  margin: 1rem 0;
  padding: 0.75rem;
  background: var(--bg);
  border-radius: 4px;
  overflow-x: auto;
}
div.rendition pre {
  margin: 0.75rem 0;
}
details {
  color: var(--muted);
  margin-top: 0.6rem;
  border-top: 1px solid var(--muted-light);
  padding-top: 0.5rem;
}
details summary {
  cursor: pointer;
  color: var(--accent);
  font-size: 0.9em;
}
details pre {
  white-space: pre-wrap;
  font-family: inherit;
  margin: 0.4rem 0 0 0;
  padding: 0.5rem;
  background: var(--muted-light);
  border-radius: 4px;
}
@media print {
  @page { size: A4; margin: 2cm; }
  details { break-inside: avoid; }
  div.rendition th { background: var(--bg) !important; }
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
{mermaid_script}
<script>mermaid.initialize({{startOnLoad: true}});</script>
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

# Template for raw-HTML rendition (markdown-it output).
# Uses <div> instead of <p> because the rendition now contains
# block-level elements (<p>, <ul>, <pre>, <blockquote>, etc.).
UNIT_TEMPLATE_RAW = """<section class="unit" id="{unit_id}">
<h2>{heading}</h2>
<div class="rendition">{rendition}</div>
<details>
<summary>原文</summary>
<pre>{source_text}</pre>
</details>
</section>"""


def _render_page(title, units_html, lang, mermaid_script=""):
    """Resolve `lang` to its profile ONCE and fill the shared
    DOC_PAGE_TEMPLATE -- the single template both doc and verdict-HTML
    modes reuse, parameterized by the page attributes (`<html lang>`,
    font stack) instead of forking a per-language template. `page_lang`
    / `font_stack` come from a frozen, developer-authored profile (not
    attacker-reachable request/unit data), so they are interpolated
    as-is -- html.escape is reserved for the untrusted `title` and
    per-unit content, kept uniform with the rest of this module.

    `mermaid_script` is the embedded mermaid JS as a <script> tag
    (empty string = no script, CDN URL, or base64 data URL).
    """
    profile = get_profile(lang)
    style_rendered = STYLE.replace(_FONT_STACK_PLACEHOLDER, profile.font_stack)
    return DOC_PAGE_TEMPLATE.format(
        lang=profile.page_lang,
        title=html.escape(title),
        style=style_rendered,
        units_html=units_html,
        mermaid_script=mermaid_script,
    )


def _load_bundled_mermaid() -> str:
    """Load the bundled mermaid.min.js and return it as a base64 data URL.

    The script is read from the same directory as this module.
    If the file is not found, returns an empty string (no script).
    """
    script_path = Path(__file__).parent / "mermaid.min.js"
    try:
        js_content = script_path.read_bytes()
        base64_str = base64.b64encode(js_content).decode("ascii")
        return (
            f'<script src="data:application/javascript;base64,{base64_str}"></script>'
        )
    except FileNotFoundError:
        return ""


def render_doc(units, title="Adjudication View", lang="zh-Hant"):
    """Render `units` (a list of unit dicts per the units-JSON schema)
    into a single self-contained HTML document string. `lang` selects
    the language profile (Task 3) that supplies the page's `<html
    lang>` attribute and font stack; default "zh-Hant" matches the
    pre-Task-3 hardcoded behavior byte-for-byte.

    The `rendition` field is parsed as markdown (via markdown-it) and
    injected as raw HTML — so `**bold**` becomes `<strong>bold</strong>`,
    `- list` becomes `<li>list</li>`, and ` ```mermaid ` fences become
    `<pre><code class="language-mermaid">` that browser-side Mermaid JS
    can locate and render.

    The bundled mermaid.min.js is embedded as a base64 data URL, so the
    output is fully self-contained (no external URLs).
    """
    units_html = "\n".join(
        _build_unit_html(unit)
        for unit in units
    )
    mermaid_script = _load_bundled_mermaid()
    return _render_page(title, units_html, lang, mermaid_script)


def _build_unit_html(unit: dict) -> str:
    """Build one unit's HTML with markdown-rendered rendition."""
    unit_id = html.escape(unit["id"])
    heading = html.escape(unit["heading"])
    source_text = html.escape(unit["source_text"])
    rendition_html = _render_markdown(unit["rendition"])
    # UNIT_TEMPLATE_RAW uses <div> (not <p>) because the rendition now
    # contains block-level HTML from markdown-it.  Direct interpolation is
    # safe — markdown-it generates the HTML structure from trusted source.
    return UNIT_TEMPLATE_RAW.format(
        unit_id=unit_id,
        heading=heading,
        rendition=rendition_html,  # raw HTML, not escaped
        source_text=source_text,
    )


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
