#!/usr/bin/env python3
"""Render a cot-explain markdown artifact to standalone HTML.

Usage:
  python3 scripts/render_cot_html.py <report.md> [-o <out.html>] [--artifact]

The `.md` is the artifact; this HTML is derived from it. Never hand-edit
the HTML, and never let the two disagree.

**The conversion adds and removes nothing.** Headings, paragraphs, lists
and tables come out in the order and nesting the markdown put them in;
the card look and the conclusion callout are CSS applied where things
already stand. There is exactly one content transformation and it is
unavoidable: a ```mermaid fence becomes `<pre class="mermaid">` with its
body un-escaped, because mermaid node labels are raw HTML and would
otherwise reach the browser as literal text.

`--artifact` emits the Artifact build: no <!doctype>/<html>/<head>/<body>
wrapper and no mermaid CDN script, because Artifacts render
<pre class="mermaid"> natively and supply their own skeleton.

Markdown is parsed by **markdown-it-py**, matching
`loom-code/scripts/adjudication_render.py`, which is this repo's existing
markdown→HTML renderer. A hand-rolled converter was written first and
failed its own test suite within the hour: an unsupported `##` heading
passed through unconverted *and* slipped past the leftover check, because
the check only matched line-start markdown while the stray text had
already been wrapped in `<p>`. Parsing is a solved problem; the parts
worth writing here are the pipeline properties below.

Three of those, taken from a brief about a renderer of this exact kind
that failed silently five times in five days:

  * **Fail loud, write nothing.** If markdown survives into the output the
    run exits non-zero AND no file is written. A run that fails but still
    writes leaves exactly the deliverable the check exists to stop.
  * **The check is scoped.** Mermaid blocks and <code> spans legitimately
    contain `|`, `**` and `#`. An unscoped check condemns every correct page.
  * **The output is stamped.** Every page carries the version of the copy
    that actually ran, so a page rendered by a stale copy is identifiable
    and a page with no stamp came from a pre-stamp copy. An unreadable
    manifest stamps the literal `unknown` rather than faking a version.
"""
import argparse
import hashlib
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote

from markdown_it import MarkdownIt
from markdown_it.rules_block import table

CSS = """
:root {
  --bg: #ffffff; --fg: #1a1c1e; --muted: #5c636a; --rule: #e3e5e8;
  --card: #f8f9fa; --accent: #0c8599;
  --font: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans TC",
          "Hiragino Sans", "Yu Gothic", sans-serif;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #16181a; --fg: #e6e8ea; --muted: #9aa1a8;
    --rule: #2c3034; --card: #1e2124; --accent: #3bc9db;
  }
}
:root[data-theme="dark"] {
  --bg: #16181a; --fg: #e6e8ea; --muted: #9aa1a8;
  --rule: #2c3034; --card: #1e2124; --accent: #3bc9db;
}
* { box-sizing: border-box; }
body {
  margin: 0; padding: 2.5rem 1.25rem 5rem; background: var(--bg);
  color: var(--fg); font-family: var(--font); line-height: 1.75; font-size: 16px;
}
main { max-width: 52rem; margin: 0 auto; }
h1 { font-size: 1.75rem; line-height: 1.35; margin: 0 0 .75rem; }
/* The markdown uses the vault's heading levels: ### page section,
   #### arc, ##### node. markdown-it maps those to h3/h4/h5 — do not
   "fix" these selectors to h2/h3/h4 without changing the template too. */
h3 { font-size: 1.15rem; margin: 3rem 0 1rem; padding-bottom: .4rem;
     border-bottom: 2px solid var(--rule); }
h4 { font-size: 1.05rem; margin: 2.25rem 0 .75rem; color: var(--accent); }
h5 { font-size: 1rem; margin: 1.5rem 0 .4rem; }
p { margin: 0 0 1rem; }
.meta { color: var(--muted); font-size: .85rem; margin-bottom: 2rem; }
.meta a { color: inherit; text-decoration: underline; text-underline-offset: 2px; }
.meta strong { color: #c92a2a; font-weight: 600; }
@media (prefers-color-scheme: dark) { .meta strong { color: #ff8787; } }
pre.mermaid { overflow-x: auto; background: #ffffff; border: 1px solid var(--rule);
              border-radius: 8px; padding: 1.25rem; margin: 1rem 0; }
/* Presentation only. Nothing below moves, adds, or removes content — the
   HTML's structure is the markdown's structure, so the two can be read
   against each other with no translation step.
   A node card is an h5 plus the list after it, styled where it stands. */
h5 + ul { border: 1px solid var(--rule); border-radius: 8px;
          padding: .85rem 1.25rem .85rem 2.4rem; margin: 0 0 .85rem;
          background: var(--card); list-style: disc; }
h5 { margin-bottom: .35rem; }
/* The first section's first paragraph is the one-line conclusion, styled
   in place. An earlier version lifted it to the top and deleted its
   heading — deterministic, so it looked mechanical, but it left the two
   files disagreeing about what the document contains. */
h3:first-of-type + p { font-size: 1.1rem; background: var(--card);
        border-left: 4px solid var(--accent); padding: 1rem 1.25rem;
        border-radius: 0 6px 6px 0; margin-bottom: 1.5rem; }
blockquote { margin: 0 0 1.25rem; padding: .6rem 1rem; border-left: 3px solid var(--muted);
  background: transparent; color: var(--fg); font-size: .95rem; }
blockquote p { margin: 0 0 .4rem; }
blockquote p:last-child { margin: 0; }
ul { margin: 0 0 1rem; padding-left: 1.3rem; }
li { margin-bottom: .35rem; }
table { border-collapse: collapse; width: 100%; margin: 0 0 1rem; font-size: .95rem; }
th, td { border: 1px solid var(--rule); padding: .5rem .75rem; text-align: left;
         vertical-align: top; }
th { background: var(--card); font-weight: 600; }
footer { margin-top: 4rem; padding-top: 1rem; border-top: 1px solid var(--rule);
         color: var(--muted); font-size: .85rem; }
code { font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
       font-size: .9em; background: var(--card); padding: .1em .35em;
       border-radius: 3px; }
""".strip()

MERMAID_CDN = """<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11.16.0/dist/mermaid.esm.min.mjs';
  // 'antiscript', not 'loose': node labels are raw HTML by design (the
  // left-align <div>), so 'strict' would render them as literal text.
  // This is defence in depth over what mermaid itself renders, and NOT
  // the control that keeps script out of the page — the browser parses
  // <pre> content as markup before mermaid ever runs, so anything the
  // converter emits raw is live regardless of this setting. The control
  // is unescape_label_markup()'s allow-list, upstream, where the fence
  // body is turned back into markup in the first place.
  mermaid.initialize({ startOnLoad: true, theme: 'default', securityLevel: 'antiscript' });
</script>"""

# Matches ONE mermaid fence's open tag, body and close tag together, so the
# close tag of a non-mermaid fence is never rewritten. DOTALL because a
# diagram spans lines. Non-greedy so two diagrams do not merge into one.
MERMAID_FENCE = re.compile(
    r'<pre><code class="language-mermaid">(.*?)</code></pre>', re.S
)

_MD = MarkdownIt("commonmark", {"html": False})
_MD.block.ruler.before("fence", "table", table, {"alt": ["paragraph", "reference"]})


def version():
    """Version of the copy of this script that is actually running.

    Read from the plugin manifest located relative to this file, not to a
    working directory: a stale copy then stamps its own older number, and
    that mismatch is the entire point of stamping.
    """
    try:
        manifest = Path(__file__).resolve().parents[3] / ".claude-plugin" / "plugin.json"
        v = json.loads(manifest.read_text(encoding="utf-8")).get("version")
        return v if isinstance(v, str) and v else "unknown"
    except Exception:
        return "unknown"


def split_front_matter(text):
    # `\r?\n` throughout: a markdown file edited on Windows, or pasted
    # through a tool that normalises to CRLF, otherwise fails to match at
    # all — and the failure is silent, since an unmatched frontmatter is
    # indistinguishable here from a file that has none.
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n(.*)$", text, re.S)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        km = re.match(r'^(\w+):\s*"?(.*?)"?\s*$', line)
        if km and km.group(2):
            meta[km.group(1)] = km.group(2)
    return meta, m.group(2)


def body_sha(body):
    """Fingerprint of the page body — must match verify_cot_html.source_sha.

    The gate stamp carries the first twelve characters of this, so the
    page can tell whether the body it is showing is the body the gate
    judged. Without it `verified: "pass"` survives any later edit and the
    page keeps advertising a result for text the gate never saw — the
    exact staleness this tool exists to catch, reintroduced on the field
    that reports the catching.

    It is also emitted into the page as <meta name="cot-body-sha">, which
    is what lets the verifier prove the HTML it just judged was built
    from the markdown it is about to stamp. Without that link the gate
    reads one file and fingerprints another.
    """
    # Normalised, so CRLF and LF copies of the same body hash alike —
    # must stay identical to verify_cot_html.source_sha, which a test
    # pins across six frontmatter shapes.
    return hashlib.sha256(body.replace("\r\n", "\n").encode("utf-8")).hexdigest()


# The only tags a mermaid label may contain. Applied first, while their
# `&gt;` is still distinguishable from an arrow's.
LABEL_TAGS = [
    ("&lt;div style='text-align:left'&gt;", "<div style='text-align:left'>"),
    ("&lt;/div&gt;", "</div>"),
    ("&lt;br/&gt;", "<br/>"),
    ("&lt;br&gt;", "<br>"),
]


def unescape_label_markup(fence_body):
    """Un-escape what mermaid needs, and no tag outside the allow-list.

    A blanket `html.unescape` here is a cross-site scripting hole, and the
    review that found it is the reason this function exists. markdown-it
    runs with `html: False`, so every `<` in the document is escaped and
    the page is safe — except inside this fence, where the label syntax
    genuinely needs `<div>` and `<br/>` to arrive as markup. Unescaping
    the whole body to get them also delivers `<script>` and
    `<img onerror=…>`, live, from whatever source document was
    summarised.

    mermaid's own `securityLevel` cannot save this. The browser parses
    `<pre>` content as markup at load time, before mermaid initializes —
    the sanitizer sits downstream of the injection point. A control
    placed after the thing it guards is not a control.

    The cut is **`<`, not `>`**. A lone `>` cannot open a tag, and the
    diagram is full of legitimate ones: `-->`, `==>`, `-.->` are arrows
    and mermaid will not parse them escaped. So `&gt;` is restored
    everywhere, while `&lt;` is restored only as part of a tag in
    LABEL_TAGS. Everything else keeps its `&lt;` and renders as text —
    `<script>` included, which is the point.

    Order is load-bearing: the allowed tags first, while their `&gt;` is
    still an entity and can be told from an arrow's; then the `&lt;`
    neutralisation; then `&gt;` and the quote that delimits labels.

    `&amp;` is deliberately NOT restored. Left alone it decodes to `&`
    exactly once, at the browser stage, which is what the reader should
    see — and restoring it would undo the `&lt;` neutralisation above and
    reconstitute numeric character references like `&#60;` into a second
    route to the same hole.
    """
    for escaped, raw in LABEL_TAGS:
        fence_body = fence_body.replace(escaped, raw)

    # THERE ARE TWO DECODE STAGES, and this is the one that is easy to
    # miss. The browser decodes the <pre> to get textContent, mermaid
    # takes that textContent as the diagram source, and then inserts each
    # label with innerHTML — which decodes a SECOND time. So a `&lt;` here
    # becomes the character `<` in textContent and is parsed as a tag by
    # the innerHTML pass, arriving at mermaid's own sanitizer as real
    # markup. Defending only the first stage leaves the second one relying
    # on a downstream control, which is the posture this file rejects.
    #
    # Anything meant to READ as text therefore needs one extra level of
    # escaping, so that exactly one decode is consumed at each stage.
    # `&amp;lt;` → textContent `&lt;` → innerHTML → the character `<`,
    # displayed. Correct for fidelity as well as safety: a `<div>` written
    # in the source is text the reader should see, not an element that
    # silently disappears into the label.
    fence_body = fence_body.replace("&lt;", "&amp;lt;")
    fence_body = fence_body.replace("&gt;", ">")
    return fence_body.replace("&quot;", '"')


def render_body(md_text):
    out = _MD.render(md_text)

    # markdown-it escapes fence bodies. Mermaid node labels are raw HTML
    # (<div style='text-align:left'>) and must reach the browser as
    # markup, so the allowed tags — and only those — are un-escaped here.
    out = MERMAID_FENCE.sub(
        lambda m: '<pre class="mermaid">\n'
        + unescape_label_markup(m.group(1))
        + "</pre>",
        out,
    )

    return out


def leftover_markdown(rendered):
    """Markdown that survived conversion, ignoring where it is legitimate.

    Mermaid blocks and <code> spans really do contain `|`, `**` and `#`.

    The anchor is a BLOCK-tag open, not a bare `>`. Unconverted text ends
    up inside a tag, where a line-start-only check cannot see it — that
    hole let a stray `##` through during development — but `>` alone also
    matches the close of any inline tag, so `<em>x</em> - 說明` and
    `<strong>A</strong> | B` were condemned as survived markdown. Both
    are ordinary prose, and the policy here writes no file at all, so a
    false accusation is a hard stop on a correct page.

    `**` cannot be anchored that way, because unconverted bold appears
    mid-paragraph. It needs the PAIR instead: a lone `**` is arithmetic
    (`2**3`), a pair opening at a word boundary is markdown that did not
    convert.
    """
    scoped = re.sub(r'<pre class="mermaid">.*?</pre>', "", rendered, flags=re.S)
    # `<code[^>]*>` and not `<code>`: markdown-it tags a fence's inner code
    # element with the language (`<code class="language-bash">`), so a bare
    # `<code>` scope leaves every language-tagged fence in the text being
    # searched — and a ```bash block holding `# install …` is then reported
    # as an unconverted heading. The check condemned legitimate content.
    scoped = re.sub(r"<code[^>]*>.*?</code>", "", scoped, flags=re.S)
    block = r"(?:^|<(?:p|li|td|th|div|h[1-6])[^>]*>)\s*"
    found = []
    # The pair must open on a non-space and close on a non-space, as
    # markdown itself requires — otherwise `2 ** 3 ** 4` in prose matches
    # and hard-stops a correct page.
    if re.search(r"(?:^|[\s>])\*\*\S[^*\n]{0,200}\S\*\*", scoped, re.M):
        found.append("literal ** (bold marker)")
    if re.search(block + r"-\s+\S", scoped, re.M):
        found.append("literal `- ` list rows")
    if re.search(block + r"\|.*\|", scoped, re.M):
        found.append("literal | table rows")
    if re.search(block + r"#{1,6}\s", scoped, re.M):
        found.append("literal # headings")
    if "```" in scoped:
        found.append("literal ``` fences")
    if re.search(r"\{\{[A-Z][A-Z_]*\}\}", scoped):
        found.append("unreplaced {{PLACEHOLDER}}")
    return found


def path_link(value, artifact=False):
    """Render a path as a clickable file:// link when that can work.

    Only an absolute path is linked. A relative one has no defined base
    once the page leaves the directory it was written in, and guessing a
    root would produce links that look right and go nowhere — worse than
    plain text.

    The Artifact build neither links nor prints an absolute path. It is
    served over https, where browsers refuse file:// navigation, so the
    link would be dead — and printing the path as plain text still hands
    the author's directory layout to everyone the page is shared with,
    which was the other half of the reason for not linking. The file name
    alone identifies the source to anyone who has it and discloses
    nothing to anyone who does not.
    """
    if artifact:
        return html.escape(Path(value).name if value.startswith("/") else value)
    if not value.startswith("/"):
        return html.escape(value)
    return (f'<a href="file://{html.escape(quote(value))}">'
            f"{html.escape(value)}</a>")


def build(md_text, artifact=False, out_dir=None):
    meta, body = split_front_matter(md_text)
    rendered = render_body(body)
    ver = version()

    title = meta.get("title") or meta.get("source") or "CoT Explain"
    stamp = f"dev-workflow:cot-explain/{ver}"

    # Every frontmatter key reaches the full page's <head> (the Artifact
    # build has no <head> of its own, so it carries none). The markdown carried
    # nineteen and an earlier version forwarded two, one of which it read
    # under a name the template had since changed — so the date rendered
    # blank and nothing said so. Whatever the artifact records, the
    # derived file records too.
    head_meta = "\n".join(
        f'<meta name="cot-{html.escape(k)}" content="{html.escape(v)}">'
        for k, v in meta.items()
    )

    # verified / fidelity_checked are deliberately shown even when empty.
    # A page that ran no checks must say so: silence reads as "fine", and
    # this whole tool exists because a silent artifact was mistaken for a
    # good one. `verified` additionally carries the fingerprint of the
    # body the gate judged, so a stale result reads as stale rather than
    # as a pass.
    verified_raw = meta.get("verified", "").strip()
    vm_gate = re.match(r"^(.*?)\s*@\s*([0-9a-f]{6,64})$", verified_raw)
    if not verified_raw:
        verified_shown = "<strong>閘：未執行</strong>"
    elif not vm_gate:
        verified_shown = (
            "<strong>閘：stale — 這筆結果沒有頁面指紋，無法證明它判的是這份內容"
            "（重跑 verify --stamp）</strong>"
        )
    elif not body_sha(body).startswith(vm_gate.group(2)):
        verified_shown = (
            "<strong>閘：stale — 檢查之後頁面被改過，這筆結果不適用"
            "（重跑 verify --stamp）</strong>"
        )
    else:
        verified_shown = f"閘：{html.escape(vm_gate.group(1))}"

    fidelity_raw = meta.get("fidelity_checked", "").strip()
    fm = re.match(r"^(PASS|FAIL)\s*\((.+)\)$", fidelity_raw)
    if fm and out_dir:
        target = str(Path(out_dir).resolve() / fm.group(2))
        fidelity_shown = f"{fm.group(1)} ({path_link(target, artifact)})"
    else:
        fidelity_shown = html.escape(fidelity_raw)

    meta_line = "　·　".join([
        f'來源：{path_link(meta.get("source", "—"), artifact)}',
        f'產出：{html.escape(meta.get("processed_at") or meta.get("date", "—"))}',
        html.escape(stamp),
        verified_shown,
        (f"忠實度檢查：{fidelity_shown}" if fidelity_shown
         else "<strong>忠實度檢查：未執行</strong>"),
    ])
    parts = [
        f"<h1>{html.escape(title)}</h1>",
        f'<p class="meta">{meta_line}</p>',
        rendered,
        f'<footer class="stamp">{html.escape(stamp)} — rendered from the '
        f"markdown artifact; do not hand-edit this file.</footer>",
    ]
    inner = "\n".join(p for p in parts if p)

    leftovers = leftover_markdown(inner)
    if leftovers:
        return None, leftovers

    if artifact:
        return f"<style>\n{CSS}\n</style>\n<main>\n{inner}\n</main>\n", []
    return (
        "<!doctype html>\n"
        '<html lang="zh-TW">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f'<meta name="generator" content="{html.escape(stamp)}">\n'
        f'<meta name="cot-body-sha" content="{body_sha(body)}">\n'
        f"{head_meta}\n"
        f"<title>{html.escape(title)}</title>\n<style>\n{CSS}\n</style>\n</head>\n"
        f"<body>\n<main>\n{inner}\n</main>\n{MERMAID_CDN}\n</body>\n</html>\n"
    ), []


def main():
    ap = argparse.ArgumentParser(description="Render cot-explain markdown to HTML.")
    ap.add_argument("markdown")
    ap.add_argument("-o", "--out")
    ap.add_argument("--artifact", action="store_true")
    args = ap.parse_args()

    src = Path(args.markdown)
    out = Path(args.out) if args.out else src.with_suffix(".html")
    doc, leftovers = build(
        src.read_text(encoding="utf-8"), args.artifact, out.parent
    )

    if leftovers:
        msg = (
            "FAIL: markdown survived conversion — " + "; ".join(leftovers)
            + "\nNo file written. A run that fails but still writes leaves "
              "exactly the broken deliverable this check exists to stop."
        )
        # Writing nothing is not the same as leaving nothing. A page from
        # an earlier good run sits there looking current, for a source
        # that no longer converts — say so, or the silence reads as "the
        # file on disk is fine".
        if out.exists():
            msg += (
                f"\nWARNING: {out} is still on disk from an earlier run and "
                "is now STALE — it does not reflect the current markdown."
            )
        print(msg, file=sys.stderr)
        return 1

    out.write_text(doc, encoding="utf-8")
    print(f"wrote {out}  ({version()})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
