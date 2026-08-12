#!/usr/bin/env python3
"""Render units-JSON (from adjudication_split.py) into a self-contained
HTML view per the adjudication-view protocol
(loom-code/skills/using-loom-code/protocols/adjudication-view.md).

Doc mode (this task): one section per unit — the ZH `rendition` is the
primary text; the EN `source_text` is collapsible beside it in a
`<details><summary>原文</summary>...</details>` block. All content
interpolations (heading / source_text / rendition) are html.escape'd —
source and rendition are untrusted text, never raw-HTML-injected.

Styling is embedded (single `<style>` block, no external stylesheet,
no external URLs of any kind) and restrained: one CSS accent-color
variable (`--accent`), no gradients, no card borders/shadows, no emoji
in chrome, print-safe (A4 @page rule).

Verdict mode (Task 6) will add a table-mode renderer — `MODES` below
is the extension point: add a `"verdict": render_verdict` entry, no
change to `main()`.

CLI:
    python3 adjudication_render.py doc <units-json-file> [-o out.html]

Emits HTML to stdout by default, or to the path given by `-o`.
"""

import argparse
import html
import json
import sys
from pathlib import Path

STYLE = """
:root {
  --accent: #2b5797;
  --fg: #1a1a1a;
  --bg: #ffffff;
  --muted: #555555;
}
* { box-sizing: border-box; }
body {
  font-family: -apple-system, "Segoe UI", "Noto Sans TC", sans-serif;
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
""".strip()

DOC_PAGE_TEMPLATE = """<!doctype html>
<html lang="zh-Hant">
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


def render_doc(units, title="Adjudication View"):
    """Render `units` (a list of unit dicts per the units-JSON schema)
    into a single self-contained HTML document string."""
    units_html = "\n".join(
        UNIT_TEMPLATE.format(
            unit_id=html.escape(unit["id"]),
            heading=html.escape(unit["heading"]),
            rendition=html.escape(unit["rendition"]),
            source_text=html.escape(unit["source_text"]),
        )
        for unit in units
    )
    return DOC_PAGE_TEMPLATE.format(
        title=html.escape(title), style=STYLE, units_html=units_html
    )


# Mode dispatch — Task 6 adds "verdict": render_verdict here.
MODES = {"doc": render_doc}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=sorted(MODES), help="render mode")
    parser.add_argument("path", help="path to the units-JSON file")
    parser.add_argument(
        "-o", "--output", help="output HTML path (default: stdout)", default=None
    )
    args = parser.parse_args(argv)

    units = json.loads(Path(args.path).read_text(encoding="utf-8"))
    rendered = MODES[args.mode](units)

    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
