#!/usr/bin/env python3
"""Render units-JSON (from adjudication_split.py) into a self-contained
HTML view per the adjudication-view protocol
(loom-code/skills/using-loom-code/protocols/adjudication-view.md).

Doc mode: one section per unit — the target-language `rendition` (the
language `--lang` selects, default zh-Hant) is the primary text; the EN
`source_text` is collapsible beside it in a
`<details><summary>原文</summary>...</details>` block. `heading` and
`source_text` are html.escape'd; `rendition` is parsed as markdown and
injected as raw HTML (bold, italic, lists, tables, blockquotes, and
Mermaid fences are all converted); raw HTML inside a rendition is escaped
by the parser, not passed through — see `_render_markdown`.

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
import re
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
# Handles headings, lists, blockquotes, bold/italic, tables, and fenced
# code blocks (including ` ```mermaid ` → <pre><code
# class="language-mermaid">).
# `html: False` — commonmark's default passes raw HTML straight through,
# and a `rendition` is agent-written, not developer-authored. Every feature
# used here is markdown syntax, so escaping raw HTML costs nothing.
# The table rule is re-registered rather than merely `.enable("table")`d,
# for its `alt` list. commonmark ships `table` disabled with
# alt=['paragraph', 'reference']; this registration adds 'blockquote',
# which is what lets a table interrupt a blockquote's lazy continuation.
# Without it, a table written directly under a `>` line stays literal pipe
# text inside the quote — and renditions do carry blockquotes. Measured:
# adding 'list' as well changes nothing (13 list-shaped probes render
# identically), so it is not carried. Pinned by
# test_table_interrupts_blockquote_lazy_continuation; a plain
# `.enable("table")` is NOT equivalent.
_MD = MarkdownIt("commonmark", {"html": False})
_MD.block.ruler.before("fence", "table", table, {
    "alt": ["paragraph", "reference", "blockquote"],
})

# Matches ONE mermaid fence's open tag, body, and close tag together, so the
# close tag of a non-mermaid fence is never rewritten. DOTALL because a
# diagram spans lines. Non-greedy is safe here specifically because the
# parser escapes fence bodies first: a diagram containing the literal text
# `</code></pre>` arrives as `&lt;/code&gt;&lt;/pre&gt;` and cannot
# terminate the match early. IGNORECASE because ` ```Mermaid ` is a
# realistic input — the rendition is agent-written — and without it such a
# fence silently renders as a code block instead of a diagram. Widening the
# match adds no injection surface: the class attribute is parser-generated,
# and with `html: False` no attacker-controlled text can reach it.
_MERMAID_FENCE_RE = re.compile(
    r'<pre><code class="language-mermaid">(.*?)</code></pre>',
    re.DOTALL | re.IGNORECASE,
)


def _render_markdown(md_text: str) -> str:
    """Convert markdown text to HTML via markdown-it.

    Fenced code blocks (including ` ```mermaid `) are converted to HTML.
    Mermaid fences specifically become `<div class="mermaid">` (not
    `<pre><code class="language-mermaid">`) so browser-side Mermaid JS
    can locate and render them — the browser scans the DOM for elements
    with class="mermaid" and transforms them in place.

    Tables are converted to `<table><thead><tbody>`, including a table
    written directly under a blockquote line — see the parser setup above
    for why that case needs a widened `alt` list rather than a plain
    `.enable("table")`.

    Other markdown syntax (bold, italic, lists, blockquotes, etc.)
    is also converted.

    Raw HTML in the input is ESCAPED, not passed through (`html: False` on
    the shared parser). commonmark's default is the opposite, and that
    default is wrong here: a `rendition` is written by an orchestrator-side
    agent, so it is model output rather than developer-authored text — if
    the artifact being rendered carries `<script>`, the agent can carry it
    through, and the output lands in a page the author opens locally.
    Everything this function advertises is markdown syntax, so escaping raw
    HTML removes no capability.

    The output is still interpolated into the page unescaped — that is what
    makes the markdown render — so this parser setting is the only thing
    standing between a rendition and the DOM. Keep it.
    """
    if not md_text:
        return ""
    result = _MD.render(md_text)
    # Convert mermaid fences from <pre><code class="language-mermaid">
    # to <div class="mermaid"> for browser-side Mermaid JS compatibility.
    # Rewrite the OPEN and CLOSE tags as one match: a blanket
    # `.replace('</code></pre>', '</div>')` also rewrites the close tag of
    # every OTHER fenced block, leaving `<pre><code class="language-python">
    # …</div>` — malformed, and only visible when a unit carries both a
    # mermaid diagram and an ordinary code block.
    result = _MERMAID_FENCE_RE.sub(
        lambda m: '<div class="mermaid">' + m.group(1) + "</div>",
        result,
    )
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
</body>
</html>
"""

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
    as-is -- html.escape guards the untrusted `title`, and each unit's
    `id` / `heading` / `source_text` at their own call site. A unit's
    `rendition` is the one exception: it arrives already rendered to HTML
    and is interpolated unescaped on purpose, guarded by the parser's
    `html: False` instead (see `_render_markdown`).

    `mermaid_script` is BOTH the embedded mermaid library and its
    `initialize` call, as one string — they travel together so a page can
    never carry the call without the library (that pairing is the fix for
    verdict mode, which passes "" and gets neither). Never a CDN URL: the
    module's no-external-URLs constraint is what makes the output readable
    offline and leak-free.
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
    """Return the bundled mermaid library AND its initialize call, as one
    string: a `<script>` whose src is a base64 data URL, followed by a
    `<script>` calling `mermaid.initialize`.

    The two are emitted together deliberately — a page carrying the call
    without the library throws ReferenceError on load, which is what
    happened while the initialize call lived in the page template instead.

    The library is read from this module's own directory. Unreadable for
    any reason (absent, permissions, a directory) → returns "", so the page
    ships neither tag and a diagram degrades to visible fence text.
    """
    script_path = Path(__file__).parent / "mermaid.min.js"
    try:
        js_content = script_path.read_bytes()
    except OSError:
        # Missing, unreadable, or a directory — the page simply ships no
        # diagram support. Returning "" also suppresses the initialize
        # call below, so a reader gets un-rendered fence text rather than
        # a ReferenceError.
        return ""
    base64_str = base64.b64encode(js_content).decode("ascii")
    return (
        f'<script src="data:application/javascript;base64,{base64_str}"></script>\n'
        # securityLevel is set EXPLICITLY, not left to the bundle's default.
        # The mermaid div is a second sink that the parser's `html: False`
        # does not reach: markdown-it escapes the fence body, the browser
        # decodes those entities back to text, and mermaid builds DOM from
        # that text. Bundled mermaid 11.16.1 happens to default to "strict",
        # but that is a library default this file would otherwise be
        # silently depending on.
        '<script>mermaid.initialize({startOnLoad: true, '
        'securityLevel: "strict"});</script>'
    )


def render_doc(units, title="Adjudication View", lang="zh-Hant"):
    """Render `units` (a list of unit dicts per the units-JSON schema)
    into a single self-contained HTML document string. `lang` selects
    the language profile (Task 3) that supplies the page's `<html
    lang>` attribute and font stack; default "zh-Hant" matches the
    pre-Task-3 hardcoded behavior byte-for-byte.

    The `rendition` field is parsed as markdown (via markdown-it) and
    injected as raw HTML — so `**bold**` becomes `<strong>bold</strong>`,
    `- list` becomes `<li>list</li>`, and ` ```mermaid ` fences become
    `<div class="mermaid">`, which is what browser-side Mermaid JS scans
    the DOM for.

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
    # contains block-level HTML from markdown-it. `rendition` is
    # deliberately NOT escaped here — that is what makes the markdown
    # render. What keeps that safe is the parser's `html: False`, not
    # anything at this call site; see _render_markdown's docstring.
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
