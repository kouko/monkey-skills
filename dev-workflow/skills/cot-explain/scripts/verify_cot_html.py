#!/usr/bin/env python3
"""Verify a cot-explain HTML report against references/mermaid-cot-spec.md.

Usage:
  python3 scripts/verify_cot_html.py <report.html>
  python3 scripts/verify_cot_html.py --render <report.html>

Two levels, and the split matters more than any individual rule:

  FAIL  a mechanical invariant is broken — the contract, or something
        mermaid itself requires. Exits 1.
  WARN  a content or readability observation. NEVER blocks. Counts of
        nodes and bullets, label widths and squareness all live here on
        purpose: when a layout rule can fail a build, authors start
        trimming claims to satisfy it, and the diagram stops matching
        the reasoning. Content owns content; this script owns form.

`--stamp` records the outcome in the sibling `.md`'s `verified:` field —
`pass`, `pass --render`, or `fail` — and then the page must be rendered
again so the HTML carries it. The field exists because a page that
skipped its checks must say so; it is written **by this script and never
by hand**, for the same reason the artifact it checks carries a version
stamp: a self-reported success signal is exactly what fooled two review
agents into passing a broken page. A hand-typed `verified` can claim a
check that never ran, and did the opposite here — it stayed empty
through a run that passed.

`--render` additionally runs each diagram through the real mermaid
parser, because a diagram can pass every textual check here and still
render as a red error box. Needs `npx` and, on first use, network.
Without it a PASS means "matches the spec as text", not "renders".

`pass --render` is recorded only when a diagram was ACTUALLY parsed, not
when the flag was passed. On a machine without `npx` the flag alone once
produced a stamped `pass --render` and a printed "PASS (parsed by
mermaid)" over a run that parsed nothing — a verdict derived from a
request rather than from work done, which is the same self-reported
success signal this field exists to refuse.

**The exit code alone settles nothing**, so `render_check` reads the
output instead and treats two things as failure: no SVG produced, and an
SVG carrying an error marker. The inherited grounding —
`obsidian:obsidian-mermaid-visualizer`'s validator — records mermaid-cli
writing an error image and exiting 0; a live probe on 11.16.0 saw the
opposite for a malformed arrow, exit 1 with no file. Both happen, which
is exactly why neither signal is trusted on its own.

Neither stage checks fidelity to the source. Nothing mechanical can.
"""
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

SEP = "<br/>" + "━" * 6 + "<br/>"
BULLET = "• "
ARROWS = ("-->", "-.->", "==>")
MERMAID_VER = "11.16.0"   # exact, not the 11.x range — see NUMBER_SPACE_NOTE

# Advisory thresholds. None of these can fail a build.
WARN_PER_GROUP = 3
WARN_MIN_BULLETS, WARN_MAX_BULLETS = 3, 5
WARN_MIN_NODES, WARN_MAX_NODES = 5, 9
WARN_EDGE_W_MIN, WARN_EDGE_W_MAX = 4.0, 8.0
WARN_TITLE_W = 10.0
WARN_BULLET_W = 10.0      # the WIDEST bullet sets node width — see the spec
WARN_GROUP_TITLE_W = 8.0
LATIN_BUDGET_FACTOR = 1.4   # a CJK glyph is ~2 Latin ones; see limit_for()

AXES = {"TB": ("LR", "row", "r"), "LR": ("TB", "column", "c")}

PALETTE = {
    "#f8f9fa", "#fff4e6", "#ffe3e3", "#ffe8cc", "#e5dbff", "#c5f6fa",
}
EMPTY_CONNECTIVES = {"導致", "然後", "接著", "所以", "leads to", "then"}

# WARN, not FAIL. The rule was inherited as "mermaid parses `1. ` as a
# markdown list and dies", and against the pinned parser that is no
# longer true: mermaid-cli 11.16.0 rendered `標題 1. 第一步` cleanly, both
# quoted (the form this spec mandates) and unquoted — exit 0, no error
# SVG, verified live rather than cited. It stays as an observation
# because the artifact is also meant to open in Obsidian, whose bundled
# mermaid is a different version, and because `--render` now gives the
# real answer for whatever parser is actually in play. Failing a build on
# it would reject correct content — "Step 1. do this" is an ordinary
# sentence — which is the failure this file's WARN/FAIL split exists to
# prevent.
NUMBER_SPACE_NOTE = (
    "node {nid}: {where} contains a `number. space` run. This parsed "
    "cleanly on the pinned mermaid ({ver}), but older renderers have "
    "treated it as a markdown list. `--render` settles it for your "
    "parser; if that is unavailable and the target renderer is old, `1.` "
    "with no space, `①` or `(1)` sidestep it"
)


def width(text):
    """Display width in CJK units: full-width 1, everything else 1/2."""
    return sum(
        1.0 if unicodedata.east_asian_width(ch) in ("W", "F") else 0.5
        for ch in text
    )


def latin_ratio(text):
    visible = [ch for ch in text if not ch.isspace()]
    if not visible:
        return 0.0
    return sum(1 for ch in visible if ch.isascii() and ch.isalnum()) / len(visible)


def limit_for(text, base):
    """Width budget, widened for Latin-script text.

    Budgets are pixel-width budgets expressed in CJK units, and a CJK
    glyph is about twice a Latin one — so `base` CJK units buys only
    ~2x base Latin characters, cramped for English.
    """
    return base * LATIN_BUDGET_FACTOR if latin_ratio(text) > 0.6 else base


class Report:
    def __init__(self):
        self.fails, self.warns = [], []
        # How many diagrams the REAL parser actually consumed. `--render`
        # asks for the check; this records whether it happened. A verdict
        # derived from the flag rather than from work done is a
        # self-reported success signal, which is the one thing this
        # script exists to refuse.
        self.parsed = 0
        # ...out of how many. Printing `parsed/parsed` reads as full
        # coverage on a partial run, and a per-diagram timeout or OSError
        # skips one WITHOUT failing — so the denominator has to come from
        # the block list, not from the numerator.
        self.total = 0

    def scoped(self, tag):
        outer = self

        class Scope:
            def fail(self, msg):
                outer.fails.append(f"{tag}: {msg}")

            def warn(self, msg):
                outer.warns.append(f"{tag}: {msg}")

        return Scope()


def diagrams(raw):
    """Every mermaid block, with HTML comments stripped first.

    A comment may itself mention <pre class="mermaid">, which would make
    the block regex start matching inside the comment.
    """
    stripped = re.sub(r"<!--.*?-->", "", raw, flags=re.S)
    return re.findall(r'<pre class="mermaid">(.*?)</pre>', stripped, re.S | re.I)


def parse_edges(body):
    """(src, arrow, label, dst) tuples, from a skeleton with labels stripped.

    The destination is matched by lookahead, never consumed. `A -->|x| B
    -->|y| C` is one legal mermaid line carrying two edges; consuming `B`
    as the first edge's destination leaves the scan starting after it, so
    the second edge does not match — and the arrow/edge count then
    disagrees, reporting a malformed arrow in a correct diagram.
    """
    skeleton = re.sub(r'\["[^"]*"\]', "", body)
    skeleton = re.sub(r"^\s*subgraph.*$", "", skeleton, flags=re.M)
    arrow_re = "|".join(re.escape(a) for a in ARROWS)
    found = re.findall(
        rf"([A-Z])\s*({arrow_re})\s*(?:\|([^|]*)\|)?\s*(?=([A-Z])\b)", skeleton
    )
    edges = [(s, a, lab, d) for s, a, lab, d in found]

    # Count arrows with the edge labels stripped too, the same way node
    # labels already are. An edge may legitimately say
    # `A -->|前提 ==> 結論| B`; counting the arrow token inside its own
    # label made the totals disagree and reported "an arrow is malformed"
    # about a diagram with no malformed arrow.
    bare = re.sub(r"\|[^|]*\|", "", skeleton)
    return edges, len(re.findall(arrow_re, bare))


def check(path, do_render=False):
    r = Report()
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()

    # Match the placeholder *shape*, not a bare "{{" — a report may
    # legitimately discuss templating in its prose.
    left = sorted(set(re.findall(r"\{\{[A-Z][A-Z_]*\}\}", raw)))
    if left:
        r.fails.append(f"unreplaced placeholder(s): {', '.join(left)}")
    # The string must match what assets/cot-report-template.md actually
    # ships. It once read "report template" while the template said
    # "markdown template", so the check could never fire — a check that
    # cannot fail is worse than none, because it reads as coverage.
    if "cot-explain markdown template" in raw:
        r.fails.append(
            "the template's own authoring comment is still in the file — "
            "delete the leading <!-- cot-explain markdown template ... --> block"
        )

    check_spec_quotes(raw, r)

    blocks = diagrams(raw)
    if not blocks:
        r.fails.append('no <pre class="mermaid"> block found')
        return r

    r.total = len(blocks)
    for n, block in enumerate(blocks, 1):
        check_diagram(block.strip(), r.scoped(f"diagram {n}"))
    if do_render:
        render_check(blocks, r)
    return r


def check_spec_quotes(raw, r):
    """A node's source quotation must be a blockquote, and non-empty.

    Structure is checkable; punctuation is not. An earlier version looked
    for quotation characters in a list item and rejected every plain
    ASCII `"`, because markdown-it escapes it to `&quot;` — six
    characters that match no quote mark. It blamed the author for
    omitting marks they had typed. A `<blockquote>` either exists or does
    not.
    """
    for m in re.finditer(r"<blockquote>(.*?)</blockquote>", raw, re.S):
        if not re.sub(r"<[^>]*>", "", m.group(1)).strip():
            r.fails.append(
                "an empty blockquote — delete it, or quote the source. An "
                "empty one implies the source specified nothing"
            )

    # The label survives from the older list-item form; it means the quote
    # was pasted as prose, where nothing can tell it from a paraphrase.
    stray = re.search(
        r"<li>\s*<strong>\s*(?:規格原文|Spec verbatim)\s*</strong>", raw
    )
    if stray:
        r.fails.append(
            "a 規格原文 list item — the source's own sentences go in a "
            "markdown blockquote (`> …`) under the node, not in a labelled "
            "bullet. Inside a bullet a quotation and a paraphrase look "
            "identical, which is the one thing this rule exists to prevent"
        )


def check_diagram(body, s):
    m = re.match(r"^graph\s+(TB|LR)\b", body)
    if not m:
        s.fail(
            "must start with `graph TB` (a linear chain, drawn as rows) or "
            "`graph LR` (a branching chain, drawn as columns) — the axis "
            "follows the shape of the reasoning, see the spec"
        )
        return
    axis = m.group(1)
    inner, word, prefix = AXES[axis]

    if "classDef" in body:
        s.fail("uses classDef — the convention forbids it, use inline style lines")

    # Legal mermaid, outside this spec. Caught by name so the diagnosis
    # says what is wrong; left to the edge parser it surfaced as "node C
    # has no edge at all", which points at the wrong thing entirely.
    # `&` reaches this text as `&amp;`: the converter leaves ampersands
    # entity-encoded so that nothing it emits is decoded twice on the way
    # to mermaid's label parser. Match both forms.
    if re.search(
        r"(?:-->|-\.->|==>)\s*(?:\|[^|]*\|)?\s*[A-Z]\s*(?:&|&amp;)\s*[A-Z]",
        body,
    ):
        s.fail(
            "uses mermaid's multi-destination `A --> B & C` form — this "
            "spec draws one edge per line so that every edge can carry "
            "its own label; write the branches as separate lines"
        )

    edges, arrow_count = parse_edges(body)
    check_groups(body, s, inner, word, prefix, edges)
    check_nodes(body, s)
    check_edges(body, s, edges, arrow_count)
    check_styles(body, s)


def check_groups(body, s, inner, word, prefix, edges):
    # `^[ \t]*`, not `^`: indenting a subgraph body is ordinary mermaid
    # style, and the `direction` check already tolerated it. Anchored at
    # the line start only, an indented diagram was reported as having no
    # subgraph rows at all — a false diagnosis pointing at the one thing
    # the diagram did have.
    groups = re.findall(
        r"^[ \t]*subgraph\s+(\S+)\s*\[(.*?)\]\s*\n(.*?)^[ \t]*end[ \t]*$",
        body, re.S | re.M,
    )
    if not groups:
        s.fail(
            f'no subgraph {word}s — every node must sit in a '
            f'`subgraph {prefix}N["標題"]` block; a flat chain renders 13:1 wide'
        )
        return

    adjacency = {}
    for src, _, _, dst in edges:
        adjacency.setdefault(src, set()).add(dst)
        adjacency.setdefault(dst, set()).add(src)

    all_ids = re.findall(r'\b([A-Z])\["', body)
    grouped = []
    for gid, title, block in groups:
        if re.fullmatch(r"[A-Z]", gid):
            s.fail(
                f"subgraph id `{gid}` is a bare capital letter and collides "
                f"with the node id space — use `{prefix}1`, `{prefix}2`, …"
            )
        if not re.search(rf"^\s*direction\s+{inner}\s*$", block, re.M):
            s.fail(
                f"subgraph {gid}: missing its own `direction {inner}` line — "
                "without it mermaid emits one flat column (0.14 squareness "
                "against 0.81) and the subgraph buys nothing"
            )
        members = re.findall(r'\b([A-Z])\["', block)
        grouped += members
        if not members:
            s.fail(f"subgraph {gid}: contains no node definitions")
            continue

        # Mermaid ignores a declared direction when the members have no
        # edges among themselves, and lays them out along the other axis.
        if len(members) > 1 and not connected(members, adjacency):
            s.fail(
                f"subgraph {gid}: its nodes ({', '.join(members)}) are not "
                f"connected to each other, so mermaid IGNORES `direction "
                f"{inner}` and lays them out along the other axis. Group nodes "
                "that are actually linked; put independent branches in "
                "separate subgraphs"
            )
        if len(members) > WARN_PER_GROUP:
            s.warn(
                f"subgraph {gid}: {len(members)} nodes in one {word} — over "
                f"{WARN_PER_GROUP} the {word} gets unwieldy"
            )
        t = re.sub(r'^"|"$', "", title.strip())
        lim = limit_for(t, WARN_GROUP_TITLE_W)
        if t and width(t) > lim:
            s.warn(
                f"subgraph {gid}: title '{t}' is {width(t):g} wide — over "
                f"{lim:g} it competes with the node titles"
            )

    orphans = sorted(set(all_ids) - set(grouped))
    if orphans:
        s.fail(f"node(s) defined outside any subgraph: {', '.join(orphans)}")


def connected(members, adjacency):
    """Do these node ids form one connected run under the diagram's edges?"""
    want = set(members)
    seen, stack = {members[0]}, [members[0]]
    while stack:
        for nxt in adjacency.get(stack.pop(), ()):
            if nxt in want and nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return seen == want


def check_nodes(body, s):
    """The node checks, in three passes: the id set, each label, the widths."""
    # The spec forbids a literal " inside a label, so [^"]* is exact.
    nodes = re.findall(r'\b([A-Z])\["([^"]*)"\]', body)
    check_node_ids([i for i, _ in nodes], s)

    widest = (0.0, None, None)
    widest_title = (0.0, None, None)
    for nid, label in nodes:
        title, bullets = check_node_label(nid, label, s)
        if title is None:
            continue
        if width(title) > widest_title[0]:
            widest_title = (width(title), nid, title)
        for text in bullets:
            if width(text) > widest[0]:
                widest = (width(text), nid, text)

    check_widths(widest_title, widest, s)


def check_node_ids(ids, s):
    if len(ids) != len(set(ids)):
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        s.fail(f"node id(s) defined more than once: {', '.join(dupes)}")
    if not WARN_MIN_NODES <= len(set(ids)) <= WARN_MAX_NODES:
        s.warn(
            f"{len(set(ids))} nodes — below {WARN_MIN_NODES} a diagram rarely "
            f"earns its place, above {WARN_MAX_NODES} the source usually holds "
            "more than one arc. Draw what the reasoning has; this is an "
            "observation, not a limit"
        )


def check_node_label(nid, label, s):
    """Check one node's label; return its (title, bullet texts).

    Returns (None, []) when the label has no usable separator — the title
    and bullets cannot be told apart then, and every measurement after
    that point would be of a structure that does not exist.
    """
    if "<div style='text-align:left'>" not in label:
        s.fail(f"node {nid}: missing the <div style='text-align:left'> wrapper")
    if "\n" in label:
        s.fail(f"node {nid}: literal newline in label — use <br/> only")
    if "|" in label:
        s.fail(f"node {nid}: '|' in label breaks the edge parser")
    if label.count(SEP) != 1:
        s.fail(
            f"node {nid}: separator must appear exactly once as "
            f"<br/>{'━' * 6}<br/> (six U+2501) — found {label.count(SEP)}"
        )
        return None, []

    n_bullets = label.count(BULLET)
    if n_bullets == 0:
        s.fail(f"node {nid}: no bullets — each is prefixed with U+2022 + space")
    elif not WARN_MIN_BULLETS <= n_bullets <= WARN_MAX_BULLETS:
        s.warn(
            f"node {nid}: {n_bullets} bullets, outside the usual "
            f"{WARN_MIN_BULLETS}-{WARN_MAX_BULLETS}. This is an "
            "observation, not a quota: if the source gives this node "
            f"{n_bullets} facts then {n_bullets} is the right answer and "
            "this warning is noise. Adding a bullet to clear it is the "
            "one response that is always wrong"
        )

    head, rest = label.split(SEP, 1)
    title = re.sub(r"<[^>]*>", "", head)
    if re.search(r"\d+\.\s", title):
        s.warn(NUMBER_SPACE_NOTE.format(nid=nid, where="title", ver=MERMAID_VER))

    bullets = []
    for b in re.sub(r"</?div[^>]*>", "", rest).split("<br/>"):
        b = b.strip()
        if not b.startswith(BULLET):
            continue
        text = b[len(BULLET):].strip()
        if re.search(r"\d+\.\s", text):
            s.warn(NUMBER_SPACE_NOTE.format(
                nid=nid, where=f"bullet '{text}'", ver=MERMAID_VER
            ))
        bullets.append(text)
    return title, bullets


def check_widths(widest_title, widest, s):
    # Column width is set by the single widest LINE, so the gate names only
    # the widest title and the widest bullet. Warning on every long title
    # produced fifteen warnings on one English page, which is the same as
    # producing none: nobody reads a list that long, and the one line that
    # actually drives the layout is lost in it.
    if widest_title[1] and widest_title[0] > limit_for(widest_title[2], WARN_TITLE_W):
        s.warn(
            f"widest title is node {widest_title[1]}'s '{widest_title[2]}' at "
            f"{widest_title[0]:g} CJK units — titles and bullets share the "
            "column width, so this is the other line worth shortening. A "
            "pixel-width budget, not a character count; judge by the rendered "
            "figure, and the full title is in the card either way"
        )
    if widest[1] and widest[0] > limit_for(widest[2], WARN_BULLET_W):
        s.warn(
            f"widest bullet is node {widest[1]}'s '{widest[2]}' at "
            f"{widest[0]:g} CJK units — this one line sets the width of every "
            "column. Shortening it is the cheapest route to a squarer figure, "
            "but not at the cost of the claim: the full text is in the card"
        )


def check_edges(body, s, edges, arrow_count):
    if not edges:
        s.fail("no edges found")
        return

    culminating = 0
    for src, arrow, label, dst in edges:
        if label is None or not label.strip():
            s.fail(
                f"edge {src} {arrow} {dst} carries no label — every edge must "
                "name the relation; a bare arrow is a defect"
            )
            continue
        lab = label.strip()
        if lab in EMPTY_CONNECTIVES:
            s.fail(
                f"edge {src} {arrow} {dst}: '{lab}' is an empty connective — "
                "state the actual relation"
            )
        hi = limit_for(lab, WARN_EDGE_W_MAX)
        if not WARN_EDGE_W_MIN <= width(lab) <= hi:
            s.warn(
                f"edge {src} {arrow} {dst}: label '{lab}' is {width(lab):g} "
                f"wide, outside the usual {WARN_EDGE_W_MIN:g}-{hi:g}. Several "
                "edges may share one label when they really are the same "
                "relation"
            )
        if arrow == "==>":
            culminating += 1

    if arrow_count != len(edges):
        s.fail(
            f"{arrow_count} arrows in the diagram but only {len(edges)} parsed "
            "as edges — an arrow is malformed"
        )
    if culminating == 0:
        s.warn(
            "no `==>` edge — it usually marks the culminating step into the "
            "conclusion. Absent is fine if the reasoning has no single one"
        )

    connected_ids = {n for e in edges for n in (e[0], e[3])}
    stranded = sorted(set(re.findall(r'\b([A-Z])\["', body)) - connected_ids)
    if stranded:
        s.fail(f"node(s) with no edge at all: {', '.join(stranded)}")


def check_styles(body, s):
    ids = set(re.findall(r'\b([A-Z])\["', body))
    styled = dict(
        re.findall(r"^[ \t]*style\s+([A-Z])\s+fill:(#[0-9a-fA-F]{6})", body, re.M)
    )
    missing = sorted(ids - set(styled))
    extra = sorted(set(styled) - ids)
    if missing:
        s.fail(f"no style line for node(s): {', '.join(missing)}")
    if extra:
        s.fail(f"style line for undefined node(s): {', '.join(extra)}")
    for nid, fill in styled.items():
        if fill.lower() not in PALETTE:
            s.fail(f"node {nid}: fill {fill} is not in the house palette")

    lines = [ln.strip() for ln in body.splitlines() if ln.strip()]
    first = next((i for i, ln in enumerate(lines) if ln.startswith("style ")), None)
    if first is not None and [
        ln for ln in lines[first:] if not ln.startswith("style ")
    ]:
        s.fail("style lines must all come after every edge line")


def render_check(blocks, r):
    """Run each diagram through the real parser.

    mermaid-cli writes an error SVG and exits 0 on a syntax error, so the
    exit code proves nothing — the SVG content is what has to be read.
    """
    if not shutil.which("npx"):
        r.warns.append("--render skipped: npx not on PATH, so nothing was parsed")
        return
    with tempfile.TemporaryDirectory() as tmp:
        for n, block in enumerate(blocks, 1):
            src = os.path.join(tmp, f"d{n}.mmd")
            out = os.path.join(tmp, f"d{n}.svg")
            with open(src, "w", encoding="utf-8") as fh:
                fh.write(block.strip() + "\n")
            try:
                subprocess.run(
                    ["npx", "-y", f"@mermaid-js/mermaid-cli@{MERMAID_VER}",
                     "-i", src, "-o", out],
                    capture_output=True, text=True, timeout=600,
                )
            except (subprocess.TimeoutExpired, OSError) as exc:
                r.warns.append(f"--render skipped for diagram {n}: {exc}")
                continue
            if not os.path.exists(out):
                r.fails.append(f"diagram {n}: mermaid produced no SVG at all")
                continue
            with open(out, encoding="utf-8", errors="replace") as fh:
                svg = fh.read()
            if "Syntax error" in svg or 'aria-roledescription="error"' in svg:
                r.fails.append(
                    f"diagram {n}: mermaid rendered a SYNTAX ERROR image — it "
                    "would appear as a red error box, not a diagram"
                )
                continue
            # Only here — an SVG exists and carries no error marker — has
            # the real parser actually consumed this diagram. Every path
            # above `continue`s without counting, so `pass --render`
            # cannot be claimed for work that did not happen.
            r.parsed += 1


def source_sha(md_text):
    """SHA-256 of the page body — everything after the frontmatter.

    The verdict is about the reasoning a reader receives, so the hash
    covers exactly that and nothing else. Frontmatter is provenance:
    the stamps are written into it (hashing them would invalidate every
    verdict the moment it was recorded), and editing a title or making a
    path absolute changes no claim on the page. An earlier version hashed
    the whole file and duly invalidated a verdict over a path format — a
    check that fires on harmless edits is one people learn to wave
    through, which is how a real warning gets missed.
    """
    m = re.match(r"^---\r?\n.*?\r?\n---\r?\n(.*)$", md_text, re.S)
    body = m.group(1) if m else md_text
    # Line endings are not content. Hashing them made a CRLF-authored
    # artifact impossible to stamp — the renderer reads through universal
    # newlines and hashes LF, the stamper reads with newline="" so it can
    # preserve CRLF, and the two then disagreed about a file neither had
    # changed. A check that fires on a harmless difference is one people
    # learn to wave through.
    return hashlib.sha256(body.replace("\r\n", "\n").encode("utf-8")).hexdigest()


def rebuild_page(md_path, md_text):
    """What the converter would build from this markdown, or None.

    None means the comparison could not be made — the renderer is not
    importable here, usually because markdown-it-py is not installed on a
    machine that only received the HTML. The caller then falls back to
    the page's own fingerprint and is weaker for it, which is why this
    degrades loudly at the call site rather than silently returning the
    page unchanged.
    """
    # Importing a sibling script writes __pycache__ NEXT TO IT — a nested
    # subfolder under a skill root, which this repo forbids and whose
    # PostToolUse hook then blocks every later edit to the skill. One
    # `--stamp` was enough to recreate it. The suite lives outside the
    # skill for exactly this reason; this import had reintroduced the
    # hazard from inside.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    saved_bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        import render_cot_html
    except Exception:
        return None
    finally:
        sys.dont_write_bytecode = saved_bytecode
    try:
        # Normalise line endings first. This function's caller reads the
        # markdown with newline="" so it can preserve CRLF when it writes
        # back, but the converter's own CLI reads through universal
        # newlines — so feeding it the raw CRLF text produced a page that
        # never matched the one on disk, and every CRLF artifact was
        # refused as "edited by hand".
        doc, leftovers = render_cot_html.build(
            md_text.replace("\r\n", "\n"), False, Path(md_path).parent
        )
    except Exception:
        return None
    return None if leftovers else doc


def stamp_markdown(html_path, outcome):
    """Record the gate outcome, and the fidelity verdict if one exists.

    Neither field is ever typed by hand. `verified` comes from the run
    that just happened. `fidelity_checked` comes from a verdict file the
    Step 6 rounds leave beside the page — `<name>.fidelity.md`, whose
    first line reads `verdict: PASS` or `verdict: FAIL`. No file means
    the check did not run, and the field stays empty so the page says so.
    A claimed check nobody can point at is the failure this whole tool
    was built to catch; it would be absurd to reintroduce it here.
    """
    md = Path(html_path).with_suffix(".md")
    if not md.exists():
        return f"--stamp: no sibling {md.name} to record into"
    # Read with newline="" so the file's own line endings survive.
    # read_text() applies universal-newline translation and write_text()
    # then emits LF, so one --stamp silently rewrote every line of a
    # CRLF-authored artifact — a whole-file diff where only the
    # `verified:` line was meant to change. The sibling converter goes out
    # of its way to accept CRLF; destroying it here would make the two
    # scripts disagree about whether that input is supported.
    with open(md, encoding="utf-8", newline="") as fh:
        text = fh.read()
    crlf = "\r\n" in text

    # The gate judged the HTML; the stamp goes in the markdown. Nothing
    # ties those together unless this does. Editing the markdown without
    # re-rendering leaves the checker reading a stale page and stamping
    # the NEW body's hash, so the page comes back saying `pass` for a
    # conclusion the gate never saw — the whole failure again, one file
    # to the left. The renderer emits the body hash it built from; if it
    # disagrees with the markdown on disk, this run proved nothing about
    # the current markdown and must not stamp.
    page = Path(html_path).read_text(encoding="utf-8")
    current = source_sha(text)

    # The meta tag is a self-declared field inside the file being judged,
    # so on its own it proves the page names this markdown — not that it
    # was BUILT from it. Hand-fixing a real FAIL in the HTML would
    # otherwise mint a `verified` the source never earned, and "never
    # hand-edit the HTML" is a convention, not a control. When the
    # renderer is importable, rebuild from the markdown and compare; the
    # meta tag is the fallback for a machine that only has this script.
    rebuilt = rebuild_page(md, text)
    if rebuilt is not None and rebuilt.strip() != page.strip():
        return (
            f"--stamp: {Path(html_path).name} is not what the converter "
            f"builds from {md.name} — it has been edited by hand, or was "
            "rendered by a different version. Re-render, then verify "
            "again. Nothing recorded"
        )

    pm = re.search(
        r'<meta name="cot-body-sha" content="([0-9a-f]{64})"', page
    )
    if not pm:
        return (
            f"--stamp: {Path(html_path).name} carries no cot-body-sha — it "
            "was built by a pre-stamp copy of the converter, or is the "
            "--artifact build. Re-render with render_cot_html.py, then "
            "verify again. Nothing recorded"
        )
    if pm.group(1) != current:
        return (
            f"--stamp: {Path(html_path).name} was built from body "
            f"{pm.group(1)[:12]}… but {md.name} is now {current[:12]}… — "
            "the markdown changed after the page was rendered, so this "
            "run checked a stale page. Re-render, then verify again. "
            "Nothing recorded"
        )

    # The outcome carries the fingerprint of the body it judged. Without
    # it the field survives any later edit and the rendered page keeps
    # announcing a result for text the gate never saw — the same
    # staleness `reviewed_md_sha256` exists to catch, on the field that
    # reports the catching. The renderer compares this prefix and shows
    # `stale` when it disagrees.
    #
    # A `--stamp` run without `--render` does not erase an existing
    # `pass --render` for the SAME body. What --render proves is that the
    # diagram parses, the diagram lives in the body, and the body is
    # unchanged — so the older, stronger result still holds, and silently
    # downgrading it would discard a real check nothing had invalidated.
    if outcome == "pass" and re.search(
        rf'^verified:\s*"pass --render @ {current[:12]}"\s*$', text, re.M
    ):
        outcome = "pass --render"
    value = f"{outcome} @ {current[:12]}"
    text, n = re.subn(
        r'^verified:.*$', f'verified: "{value}"', text, count=1, flags=re.M
    )
    if not n:
        return f"--stamp: {md.name} has no `verified:` line in its frontmatter"
    notes = [f'verified: "{value}"']

    verdict_file = Path(html_path).with_suffix(".fidelity.md")
    if verdict_file.exists():
        head = verdict_file.read_text(encoding="utf-8")[:600]
        vm = re.search(r"verdict:\s*(PASS|FAIL)", head, re.I)
        sm = re.search(r"reviewed_md_sha256:\s*([0-9a-f]{64})", head, re.I)
        if not vm:
            notes.append(
                f"{verdict_file.name} states no `verdict: PASS|FAIL` — "
                "fidelity_checked left empty rather than guessed"
            )
        elif not sm:
            notes.append(
                f"{verdict_file.name} carries no `reviewed_md_sha256:` — a "
                "verdict that names no file cannot be shown to be about this "
                "one. fidelity_checked left empty"
            )
        elif sm.group(1).lower() != current:
            notes.append(
                f"{verdict_file.name} judged {sm.group(1)[:12]}… but the "
                f"markdown is now {current[:12]}… — the page changed after "
                "the check. fidelity_checked left empty; re-run Step 6"
            )
        else:
            fid = f"{vm.group(1).upper()} ({verdict_file.name})"
            # `subn`, and the count is read: a markdown with no
            # `fidelity_checked:` line takes this substitution silently,
            # and the run then reports writing a field that is not in the
            # file — a success report for work that did not happen, which
            # is the failure class this script was built against.
            text, fn = re.subn(
                r'^fidelity_checked:.*$', f'fidelity_checked: "{fid}"',
                text, count=1, flags=re.M,
            )
            notes.append(
                f'fidelity_checked: "{fid}"' if fn else
                f"{md.name} has no `fidelity_checked:` line in its "
                f"frontmatter — the {vm.group(1).upper()} verdict was NOT "
                "recorded; add the field and re-stamp"
            )

    with open(md, "w", encoding="utf-8", newline="\r\n" if crlf else "\n") as fh:
        fh.write(text.replace("\r\n", "\n"))
    return ("--stamp: " + "; ".join(notes)
            + f" → {md.name}. Re-render to carry it into the HTML")


def render_verdict(do_render, parsed, total):
    """(claim `--render`?, the note to print) — a pure decision, so it
    can be tested without npx.

    EVERY diagram must have parsed, not merely one. A per-diagram timeout
    or OSError skips a diagram with a WARN and no fail, so `parsed > 0`
    would claim the strong result for a run that checked part of the page
    — the self-reported-success class, inside the fix for it. And the
    denominator comes from the block list, never from the numerator:
    printing `parsed/parsed` reads as full coverage on a partial run.

    It lives out here because both defects survived a mutation battery
    while sitting inline in main(), where only an end-to-end run with a
    real parser could reach them.
    """
    if do_render and total > 0 and parsed == total:
        return True, f" (parsed by mermaid: {parsed}/{total} diagram(s))"
    if do_render:
        return False, (
            f" (text only — --render was requested but only {parsed}/{total} "
            "diagram(s) were parsed; see the WARN above)"
        )
    return False, " (text only — add --render to prove it parses)"


def main():
    argv = sys.argv[1:]
    if "-h" in argv or "--help" in argv:
        print(__doc__.strip())
        return 0
    do_render = "--render" in argv
    do_stamp = "--stamp" in argv
    do_sha = "--sha" in argv
    argv = [a for a in argv if a not in ("--render", "--stamp", "--sha")]
    # The arity check comes FIRST, for every mode. `--sha` with no file
    # used to index argv[0] straight away and die with an IndexError and
    # a traceback, where every other misuse of this script prints a usage
    # line and exits 2.
    if len(argv) != 1:
        print(
            "usage: verify_cot_html.py [--render] [--stamp] [--sha] <report.html>",
            file=sys.stderr,
        )
        return 2
    if do_sha:
        md = Path(argv[0]).with_suffix(".md")
        if not md.exists():
            print(f"--sha: no such file: {md}", file=sys.stderr)
            return 2
        print(source_sha(md.read_text(encoding="utf-8")))
        return 0

    r = check(argv[0], do_render)
    for w in r.warns:
        print(f"WARN: {w}")
    for f in r.fails:
        print(f"FAIL: {f}")
    # `pass --render` is claimed only when a diagram was really parsed.
    # Deriving it from `do_render` alone meant a machine without npx —
    # where render_check warns "nothing was parsed" and returns — still
    # stamped `pass --render` and printed "PASS (parsed by mermaid)".
    rendered, note = render_verdict(do_render, r.parsed, r.total)
    outcome = "fail" if r.fails else ("pass --render" if rendered else "pass")
    if do_stamp:
        print(stamp_markdown(argv[0], outcome))
    if r.fails:
        return 1
    print("PASS" + note)
    return 0


if __name__ == "__main__":
    sys.exit(main())
