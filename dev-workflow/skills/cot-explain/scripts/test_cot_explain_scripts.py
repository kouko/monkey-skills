"""test_cot_explain_scripts.py — tests for render_cot_html.py and verify_cot_html.py.

Every case here is a defect that a reviewer reproduced against the first
shipped version of these scripts, or a property the scripts' own docstrings
claim. They are written as tests rather than left as prose because the
review found the scripts carrying their regression history in comments —
"an earlier version looked for quotation characters", "failed its own test
suite within the hour" — where nothing re-runs it.

Grouped by what each defends:

A. Claims the scripts make about themselves
   1. the leftover-markdown check is SCOPED — a language-tagged code fence
      is legitimate content, not survived markdown
   2. `verified` is bound to the body it judged, like `fidelity_checked`
   3. the Artifact build does not carry the author's directory layout
   4. mermaid fence bodies reach the browser un-escaped (labels are raw HTML)

B. The gate must not falsely accuse valid input
   5. an indented diagram is valid mermaid
   6. a chained edge line `A -->|x| B -->|y| C` is two edges
   7. a `<code>` span may hold `**`, `#`, `|` without condemning the page

C. Nothing may report success it did not achieve
   8. the template's authoring comment is actually detected
   9. a stamp that could not be written is not reported as written

D. Round trip
   10. render -> verify -> stamp -> render lands the stamp on the page
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
RENDER = HERE / "render_cot_html.py"
VERIFY = HERE / "verify_cot_html.py"

sys.path.insert(0, str(HERE))
import render_cot_html as R  # noqa: E402
import verify_cot_html as V  # noqa: E402


FRONTMATTER = """---
title: "t"
type: cot-explain
date: 2026-08-19
tags:
  - cot-explain
source: "{source}"
source_mode: "file"
language: zh-TW
status: completed
processed_at: "2026-08-19T00:00:00+08:00"
generator: "dev-workflow:cot-explain"
arcs: 1
nodes: 5
layout: "rows"
verified: ""
fidelity_checked: ""
---
"""

SEP = "<br/>" + "━" * 6 + "<br/>"


def node(nid, title, extra_bullets=0):
    bullets = "<br/>".join(f"• 條列{i}" for i in range(1, 3 + extra_bullets + 1))
    return (
        f'{nid}["<div style=\'text-align:left\'>{title}{SEP}{bullets}</div>"]'
    )


def diagram(indent="", chained=False):
    """A minimal five-node diagram that satisfies the spec."""
    ids = "ABCDE"
    rows = [ids[:3], ids[3:]]
    out = ["graph TB"]
    for n, members in enumerate(rows, 1):
        out.append(f'{indent}subgraph r{n}["階段{n}"]')
        out.append(f"{indent}direction LR")
        for m in members:
            out.append(f"{indent}  {node(m, f'節點{m}')}")
        out.append(f"{indent}end")
    if chained:
        out.append("A -->|先推導| B -->|再推導| C")
    else:
        out.append("A -->|先推導| B")
        out.append("B -->|再推導| C")
    out.append("C -->|接續| D")
    out.append("D ==>|收束為| E")
    fills = ["#f8f9fa", "#fff4e6", "#ffe3e3", "#e5dbff", "#c5f6fa"]
    strokes = ["#868e96", "#e67700", "#c92a2a", "#5f3dc4", "#0c8599"]
    for m, f, st in zip(ids, fills, strokes):
        out.append(f"{indent}style {m} fill:{f},stroke:{st},stroke-width:2px")
    return "\n".join(out)


def make_md(tmp_path, body_extra="", source="/abs/path/to/source.md", **kw):
    md = tmp_path / "r.md"
    md.write_text(
        FRONTMATTER.format(source=source)
        + "\n### 概述\n\n一句話結論。\n\n### 推理鏈\n\n#### 弧\n\n```mermaid\n"
        + diagram(**kw)
        + "\n```\n"
        + body_extra,
        encoding="utf-8",
    )
    return md


def run(script, *args):
    return subprocess.run(
        [sys.executable, str(script), *map(str, args)],
        capture_output=True,
        text=True,
    )


# ---------------------------------------------------------------- A. claims

def test_language_tagged_code_fence_is_not_survived_markdown(tmp_path):
    """A ```bash fence holding `#` and `**` is content, not unconverted markdown.

    markdown-it emits `<pre><code class="language-bash">`; a scope regex
    matching only a bare `<code>` tag condemns every page carrying one.
    """
    md = make_md(
        tmp_path,
        body_extra="\n### 附註\n\n```bash\n# install the thing\nrun --with **args**\n```\n",
    )
    r = run(RENDER, md)
    assert r.returncode == 0, f"a tagged code fence was condemned: {r.stderr}"
    assert md.with_suffix(".html").exists()


def test_verified_is_bound_to_the_body_it_judged(tmp_path):
    """Editing the body after a stamp must invalidate `verified`.

    `fidelity_checked` carries `reviewed_md_sha256`; `verified` shipping
    without an equivalent binding is the staleness this tool exists to catch.
    """
    md = make_md(tmp_path)
    run(RENDER, md)
    run(VERIFY, "--stamp", md.with_suffix(".html"))
    stamped = md.read_text(encoding="utf-8")
    assert re.search(r'^verified: "pass', stamped, re.M)

    md.write_text(stamped.replace("### 概述", "### 概述\n\n新增一段。", 1), encoding="utf-8")
    run(RENDER, md)
    html = md.with_suffix(".html").read_text(encoding="utf-8")
    assert "閘：未執行" in html or "閘：stale" in html, (
        "the page still advertises a gate result for a body the gate never saw"
    )


def test_artifact_build_does_not_carry_the_authors_directory_layout(tmp_path):
    """The build's own docstring gives this as the reason it does not link."""
    md = make_md(tmp_path, source="/Users/someone/private/secret-project/design.md")
    out = tmp_path / "a.html"
    run(RENDER, md, "-o", out, "--artifact")
    html = out.read_text(encoding="utf-8")
    assert "/Users/someone/private/secret-project" not in html


def test_mermaid_labels_reach_the_page_unescaped(tmp_path):
    """Node labels are raw HTML; escaped, mermaid renders them as literal text."""
    md = make_md(tmp_path)
    run(RENDER, md)
    html = md.with_suffix(".html").read_text(encoding="utf-8")
    block = re.search(r'<pre class="mermaid">(.*?)</pre>', html, re.S).group(1)
    assert "<div style='text-align:left'>" in block
    assert "&lt;div" not in block


# ------------------------------------------------- B. no false accusations

def test_indented_diagram_is_valid(tmp_path):
    """`direction` already tolerates indentation; subgraph and style must too.

    The failure this pins is not the refusal but the diagnosis: the gate
    reported "no subgraph rows" for a diagram carrying two.
    """
    md = make_md(tmp_path, indent="  ")
    run(RENDER, md)
    r = run(VERIFY, md.with_suffix(".html"))
    assert r.returncode == 0, f"an indented diagram was rejected:\n{r.stdout}"


def test_chained_edge_line_counts_as_two_edges(tmp_path):
    """`A -->|x| B -->|y| C` is legal mermaid and is two edges, not one."""
    md = make_md(tmp_path, chained=True)
    run(RENDER, md)
    r = run(VERIFY, md.with_suffix(".html"))
    assert "not connected to each other" not in r.stdout, (
        "a chained edge line produced a false disconnection diagnosis"
    )
    assert r.returncode == 0, r.stdout


def test_code_span_may_hold_markdown_characters(tmp_path):
    md = make_md(tmp_path, body_extra="\n### 附註\n\n用 `**bold**` 和 `# heading` 當例子。\n")
    r = run(RENDER, md)
    assert r.returncode == 0, r.stderr


# ------------------------------------------- C. no unearned success reports

def test_template_authoring_comment_is_detected(tmp_path):
    """The check must match the comment the template actually ships.

    It once looked for "cot-explain report template" while the template
    said "markdown template" — a check that could never fire.
    """
    template = (HERE.parent / "assets" / "cot-report-template.md").read_text(
        encoding="utf-8"
    )
    first_comment = re.search(r"<!--(.*?)-->", template, re.S).group(1)
    marker = first_comment.strip().splitlines()[0].strip()

    md = make_md(tmp_path)
    run(RENDER, md)
    html_path = md.with_suffix(".html")
    html_path.write_text(
        html_path.read_text(encoding="utf-8").replace(
            "<main>", f"<!-- {marker} -->\n<main>", 1
        ),
        encoding="utf-8",
    )
    r = run(VERIFY, html_path)
    assert r.returncode == 1, "a retained template comment passed the gate"


def test_stamp_reports_only_what_it_wrote(tmp_path):
    """A markdown with no `fidelity_checked:` line must not be told one landed."""
    md = make_md(tmp_path)
    md.write_text(
        re.sub(r"^fidelity_checked:.*$\n", "", md.read_text(encoding="utf-8"), flags=re.M),
        encoding="utf-8",
    )
    verdict = md.with_suffix(".fidelity.md")
    body_sha = V.source_sha(md.read_text(encoding="utf-8"))
    verdict.write_text(
        f"verdict: PASS\nreviewed_md_sha256: {body_sha}\n", encoding="utf-8"
    )
    run(RENDER, md)
    r = run(VERIFY, "--stamp", md.with_suffix(".html"))
    wrote_claim = 'fidelity_checked: "PASS' in r.stdout
    landed = "fidelity_checked:" in md.read_text(encoding="utf-8")
    assert wrote_claim == landed, (
        "the stamp reported a write that did not land"
    )


def test_fidelity_stamp_refuses_a_verdict_for_another_body(tmp_path):
    md = make_md(tmp_path)
    verdict = md.with_suffix(".fidelity.md")
    verdict.write_text("verdict: PASS\nreviewed_md_sha256: " + "0" * 64 + "\n", encoding="utf-8")
    run(RENDER, md)
    r = run(VERIFY, "--stamp", md.with_suffix(".html"))
    assert "the page changed after the check" in r.stdout
    assert 'fidelity_checked: ""' in md.read_text(encoding="utf-8")


# --------------------------------------------------------- D. the round trip

def test_round_trip_lands_both_stamps(tmp_path):
    md = make_md(tmp_path)
    assert run(RENDER, md).returncode == 0
    verdict = md.with_suffix(".fidelity.md")
    verdict.write_text(
        "verdict: PASS\nreviewed_md_sha256: "
        + V.source_sha(md.read_text(encoding="utf-8"))
        + "\n",
        encoding="utf-8",
    )
    assert run(VERIFY, "--stamp", md.with_suffix(".html")).returncode == 0
    assert run(RENDER, md).returncode == 0
    html = md.with_suffix(".html").read_text(encoding="utf-8")
    assert "閘：pass" in html
    assert "忠實度檢查：PASS" in html


def test_leftover_markdown_is_detected_on_unconverted_text(tmp_path):
    """The postcondition's whole point: unconverted markdown must not ship."""
    md = make_md(tmp_path)
    raw = md.read_text(encoding="utf-8")
    found = R.leftover_markdown(raw)
    assert found, "raw markdown passed the leftover check"


def test_source_sha_covers_the_body_not_the_frontmatter(tmp_path):
    md = make_md(tmp_path)
    text = md.read_text(encoding="utf-8")
    before = V.source_sha(text)
    retitled = text.replace('title: "t"', 'title: "something else"', 1)
    assert V.source_sha(retitled) == before, "a frontmatter edit changed the body hash"
    edited = text.replace("一句話結論。", "改過的結論。", 1)
    assert V.source_sha(edited) != before, "a body edit did not change the hash"


def test_sha_flag_without_a_file_reports_usage(tmp_path):
    r = run(VERIFY, "--sha")
    assert r.returncode == 2
    assert "usage" in (r.stderr + r.stdout).lower()


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
