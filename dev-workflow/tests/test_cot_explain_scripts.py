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

E. The second review round — two reviewers, run against the fixes for A-D
   11. no tag outside the label allow-list reaches the page as markup
   12. ...and arrows still do, which the first cut of that fix broke
   13. a failing conversion writes no file, and names the stale one it left
   14. `2**3` and `<em>x</em> - y` are prose, not survived markdown
   15. an arrow token inside an edge label is not a malformed arrow
   16. `A --> B & C` is diagnosed by name, not as "C has no edge"
   17. the renderer's and the verifier's body hashes agree
   18. a page built from a different body than the markdown is not stamped
   19. a `--stamp` without `--render` does not erase a `pass --render`
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

# The suite lives OUTSIDE the skill it tests, deliberately. Running
# pytest inside `skills/cot-explain/scripts/` creates `__pycache__/` and
# `.pytest_cache/` there — nested subfolders under a skill root, which
# this repo's PostToolUse hook forbids — so the skill's own tests locked
# the skill against further editing until swept by hand.
SKILL = Path(__file__).resolve().parents[1] / "skills" / "cot-explain"
SCRIPTS = SKILL / "scripts"
RENDER = SCRIPTS / "render_cot_html.py"
VERIFY = SCRIPTS / "verify_cot_html.py"

sys.path.insert(0, str(SCRIPTS))
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


def diagram(indent="", chained=False, payload="", arrow_in_label=False,
            multi_destination=False):
    """A minimal five-node diagram that satisfies the spec."""
    ids = "ABCDE"
    rows = [ids[:3], ids[3:]]
    out = ["graph TB"]
    for n, members in enumerate(rows, 1):
        out.append(f'{indent}subgraph r{n}["階段{n}"]')
        out.append(f"{indent}direction LR")
        for m in members:
            title = f"節點{m}" + (payload if m == "A" else "")
            out.append(f"{indent}  {node(m, title)}")
        out.append(f"{indent}end")
    if chained:
        out.append("A -->|先推導| B -->|再推導| C")
    elif multi_destination:
        out.append("A -->|先推導| B & C")
    elif arrow_in_label:
        out.append("A -->|前提 ==> 中段| B")
        out.append("B -->|再推導| C")
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
    template = (SKILL / "assets" / "cot-report-template.md").read_text(
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


# ------------------------------------------- E. the second review round
#
# Every case below is a defect two independent code reviewers reproduced
# against the first remediation round.

def test_script_in_a_label_never_reaches_the_page_as_markup(tmp_path):
    """The fence un-escape must not hand the browser live tags.

    Label text comes from whatever source document was summarised, and
    the page is built to be shared. mermaid's own securityLevel cannot
    help: the browser parses <pre> content before mermaid initializes,
    so the sanitizer sits downstream of the injection point.
    """
    md = make_md(tmp_path, payload="<script>alert(1)</script><img src=x onerror=alert(2)>")
    assert run(RENDER, md).returncode == 0
    html = md.with_suffix(".html").read_text(encoding="utf-8")
    assert "<script>" not in html
    assert "<img" not in html
    # DOUBLE-escaped, not merely escaped. The browser decodes the <pre>
    # to textContent and mermaid then inserts each label with innerHTML,
    # so a single `&lt;` here becomes a real tag at the second stage and
    # only mermaid's own sanitizer stands between it and the reader.
    assert "&amp;lt;script&amp;gt" in html or "&amp;lt;script>" in html
    assert "&lt;script" not in html.replace("&amp;lt;script", "")


def test_arrows_reach_the_page_as_arrows(tmp_path):
    """`-->` must survive as `-->`, not `--&gt;`.

    The narrowing that closed the injection hole cut `>` as well as `<`
    on its first attempt, which escapes every arrow in the diagram and
    leaves mermaid with a graph that has no edges.
    """
    md = make_md(tmp_path)
    run(RENDER, md)
    html = md.with_suffix(".html").read_text(encoding="utf-8")
    block = re.search(r'<pre class="mermaid">(.*?)</pre>', html, re.S).group(1)
    assert "-->" in block and "==>" in block
    assert "--&gt;" not in block


def test_fail_loud_writes_no_file(tmp_path):
    """The module's headline property, which nothing pinned.

    A mutant that keeps the exit code and ALSO writes the broken page
    passed the whole suite.
    """
    md = tmp_path / "r.md"
    # A table row with no delimiter row: markdown-it leaves it in a
    # paragraph, which is exactly what "markdown survived conversion"
    # means. Writing a literal <p> tag would not do — html:False escapes
    # it, so it never reaches the check.
    md.write_text(FRONTMATTER.format(source="/x.md") + "\n| 甲 | 乙 |\n",
                  encoding="utf-8")
    out = tmp_path / "r.html"
    r = run(RENDER, md, "-o", out)
    assert r.returncode == 1
    assert not out.exists(), "a failing run wrote the broken deliverable anyway"


def test_stale_page_left_by_an_earlier_run_is_named(tmp_path):
    """Writing nothing is not the same as leaving nothing."""
    md = make_md(tmp_path)
    assert run(RENDER, md).returncode == 0
    md.write_text(md.read_text(encoding="utf-8") + "\n| 甲 | 乙 |\n",
                  encoding="utf-8")
    r = run(RENDER, md)
    assert r.returncode == 1
    assert "STALE" in r.stderr


def test_prose_may_contain_arithmetic_double_star(tmp_path):
    """`2**3` is not unconverted bold; condemning it blocks a correct page."""
    md = make_md(tmp_path, body_extra="\n### 附註\n\n公式 2**3 的意思。\n")
    r = run(RENDER, md)
    assert r.returncode == 0, r.stderr


def test_inline_emphasis_followed_by_prose_punctuation(tmp_path):
    """A `>` anchor matches any inline tag's close, condemning ordinary prose."""
    md = make_md(
        tmp_path,
        body_extra="\n### 附註\n\n**節點 A** - 這是說明文字。\n\n*強調* | 直線 | 收尾\n",
    )
    r = run(RENDER, md)
    assert r.returncode == 0, r.stderr


def test_arrow_token_inside_an_edge_label_is_not_a_malformed_arrow(tmp_path):
    """Edge labels are stripped before arrows are counted, like node labels."""
    md = make_md(tmp_path, arrow_in_label=True)
    run(RENDER, md)
    r = run(VERIFY, md.with_suffix(".html"))
    assert "an arrow is malformed" not in r.stdout, r.stdout
    assert r.returncode == 0, r.stdout


def test_multi_destination_form_is_diagnosed_by_name(tmp_path):
    """`A --> B & C` is legal mermaid, outside this spec.

    Left to the edge parser it surfaced as "node C has no edge at all",
    which points at the wrong thing entirely.
    """
    md = make_md(tmp_path, multi_destination=True)
    run(RENDER, md)
    r = run(VERIFY, md.with_suffix(".html"))
    assert r.returncode == 1
    assert "multi-destination" in r.stdout


def test_the_two_body_hashes_agree(tmp_path):
    """The staleness binding rests on these never diverging.

    They are two independently-authored copies in two modules, edited
    for different reasons.
    """
    shapes = [
        FRONTMATTER.format(source="/x.md") + "\nbody\n",
        FRONTMATTER.format(source="/x.md").replace("\n", "\r\n") + "\r\nbody\r\n",
        "no frontmatter at all\n",
        "---\n---\nbody\n",
        FRONTMATTER.format(source="/x.md") + "\nbody with --- inside\n",
        "\n" + FRONTMATTER.format(source="/x.md") + "\nbody\n",
    ]
    for text in shapes:
        assert R.body_sha(R.split_front_matter(text)[1]) == V.source_sha(text), (
            f"the renderer and the verifier disagree on the body of {text[:20]!r}"
        )


def test_stamp_refuses_a_page_built_from_a_different_body(tmp_path):
    """The gate judges the HTML; the stamp lands in the markdown.

    Editing the markdown without re-rendering leaves the checker reading
    a stale page while fingerprinting the new body — the page then reads
    `pass` for a conclusion the gate never saw.
    """
    md = make_md(tmp_path)
    run(RENDER, md)
    md.write_text(
        md.read_text(encoding="utf-8").replace("一句話結論。", "換掉的結論。", 1),
        encoding="utf-8",
    )
    r = run(VERIFY, "--stamp", md.with_suffix(".html"))
    assert "Nothing recorded" in r.stdout, r.stdout
    assert 'verified: ""' in md.read_text(encoding="utf-8")

    # ...and the fingerprint arm on its own. The rebuild comparison
    # normally reaches this case first, so without forcing the fallback
    # the sha arm could be deleted with the suite still green — and it is
    # the only guard left where the renderer cannot be imported.
    saved, V.rebuild_page = V.rebuild_page, lambda *a, **k: None
    try:
        msg = V.stamp_markdown(md.with_suffix(".html"), "pass")
    finally:
        V.rebuild_page = saved
    assert "the markdown changed after the page was rendered" in msg, msg
    assert 'verified: ""' in md.read_text(encoding="utf-8")


def test_stamp_without_render_does_not_downgrade_a_render_pass(tmp_path):
    """`--render` proved the diagram parses; the body has not changed."""
    md = make_md(tmp_path)
    run(RENDER, md)
    body12 = V.source_sha(md.read_text(encoding="utf-8"))[:12]
    md.write_text(
        md.read_text(encoding="utf-8").replace(
            'verified: ""', f'verified: "pass --render @ {body12}"', 1
        ),
        encoding="utf-8",
    )
    run(RENDER, md)
    run(VERIFY, "--stamp", md.with_suffix(".html"))
    assert f'verified: "pass --render @ {body12}"' in md.read_text(encoding="utf-8")


def test_sha_on_a_missing_file_reports_cleanly(tmp_path):
    r = run(VERIFY, "--sha", tmp_path / "nope.html")
    assert r.returncode == 2
    assert "Traceback" not in r.stderr


# ---------------------------------------- F. the third review round
#
# Each of these killed a mutant that the 26-case suite let through, or
# closes a finding the reviewers reproduced against round two.

def test_a_page_without_the_body_sha_is_not_stamped(tmp_path):
    """Half the binding was unguarded: no test fed a meta-less page.

    Deleting the `if not pm:` arm passed the whole suite, and the
    meta-less page is not hypothetical — it is the --artifact build.
    """
    md = make_md(tmp_path)
    out = tmp_path / "r.html"
    run(RENDER, md, "-o", out, "--artifact")
    r = run(VERIFY, "--stamp", out)
    assert "Nothing recorded" in r.stdout, r.stdout
    assert 'verified: ""' in md.read_text(encoding="utf-8")

    # ...and the meta arm specifically, isolated. The rebuild comparison
    # normally catches this case first, so without forcing the fallback
    # the meta arm could be deleted with the suite still green — it is
    # the only guard left on a machine that has this script but not
    # markdown-it.
    md2 = make_md(tmp_path)
    run(RENDER, md2)
    page = md2.with_suffix(".html")
    page.write_text(
        re.sub(r'<meta name="cot-body-sha"[^>]*>\n?', "",
               page.read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    saved, V.rebuild_page = V.rebuild_page, lambda *a, **k: None
    try:
        msg = V.stamp_markdown(page, "pass")
    finally:
        V.rebuild_page = saved
    assert "carries no cot-body-sha" in msg, msg
    assert 'verified: ""' in md2.read_text(encoding="utf-8")


def test_a_hand_edited_page_is_not_stamped(tmp_path):
    """The meta tag is self-declared inside the file being judged.

    On its own it proves the page NAMES this markdown, not that it was
    built from it — so a hand-fixed FAIL could mint a verdict the source
    never earned. "Never hand-edit the HTML" is a convention, not a
    control.
    """
    md = make_md(tmp_path)
    run(RENDER, md)
    html_path = md.with_suffix(".html")
    html_path.write_text(
        html_path.read_text(encoding="utf-8").replace("一句話結論。", "偷改的結論。", 1),
        encoding="utf-8",
    )
    r = run(VERIFY, "--stamp", html_path)
    assert "edited by hand" in r.stdout, r.stdout
    assert 'verified: ""' in md.read_text(encoding="utf-8")


def test_render_pass_is_not_claimed_when_nothing_was_parsed(tmp_path):
    """`pass --render` must follow work done, not the flag.

    With npx off PATH, render_check warns "nothing was parsed" and
    returns — and the run still stamped `pass --render` and printed
    "PASS (parsed by mermaid)". The no-downgrade branch then re-affirmed
    that false, stronger claim on every later run.
    """
    md = make_md(tmp_path)
    run(RENDER, md)
    r = subprocess.run(
        [sys.executable, str(VERIFY), "--render", "--stamp",
         str(md.with_suffix(".html"))],
        capture_output=True, text=True, env={"PATH": "/nonexistent"},
    )
    assert "0/1 diagram(s) were parsed" in r.stdout, r.stdout
    assert "parsed by mermaid" not in r.stdout
    assert '--render' not in re.search(
        r'^verified: "(.*)"', md.read_text(encoding="utf-8"), re.M
    ).group(1)


def test_render_check_counts_the_diagrams_it_really_parsed(tmp_path):
    """The POSITIVE arm of the counter, which the npx-absent test cannot reach.

    Without this, never incrementing `parsed` passes the suite — the
    counter would refuse every legitimate `pass --render` and nothing
    would say so.
    """
    calls = []

    def fake_run(cmd, **kw):
        out = cmd[cmd.index("-o") + 1]
        Path(out).write_text("<svg>fine</svg>", encoding="utf-8")
        calls.append(out)
        return subprocess.CompletedProcess(cmd, 0, "", "")

    r = V.Report()
    saved_which, saved_run = V.shutil.which, V.subprocess.run
    V.shutil.which, V.subprocess.run = (lambda _: "/usr/bin/npx"), fake_run
    try:
        V.render_check(["graph TB", "graph LR"], r)
    finally:
        V.shutil.which, V.subprocess.run = saved_which, saved_run
    assert len(calls) == 2
    assert r.parsed == 2, "a clean parse was not counted"
    assert not r.fails


def test_a_partly_parsed_run_does_not_claim_a_full_one(tmp_path):
    """A per-diagram OSError skips a diagram with a WARN and no fail.

    `parsed > 0` would then stamp the strong result for a run that
    checked part of the page, and print `1/1` for it.
    """
    def half_run(cmd, **kw):
        out = cmd[cmd.index("-o") + 1]
        if out.endswith("d1.svg"):
            raise OSError("boom")
        Path(out).write_text("<svg>fine</svg>", encoding="utf-8")
        return subprocess.CompletedProcess(cmd, 0, "", "")

    r = V.Report()
    r.total = 2
    saved_which, saved_run = V.shutil.which, V.subprocess.run
    V.shutil.which, V.subprocess.run = (lambda _: "/usr/bin/npx"), half_run
    try:
        V.render_check(["graph TB", "graph LR"], r)
    finally:
        V.shutil.which, V.subprocess.run = saved_which, saved_run
    assert r.parsed == 1 and not r.fails, (r.parsed, r.fails)
    assert r.parsed != r.total, "the partial run must not read as complete"


def test_render_verdict_claims_only_full_coverage():
    """Both of these survived a mutation battery while inline in main().

    Only an end-to-end run with a real parser could reach them there,
    which is exactly the run CI cannot do.
    """
    assert V.render_verdict(True, 2, 2) == (
        True, " (parsed by mermaid: 2/2 diagram(s))")

    # Partial: one diagram skipped by a timeout, no failure raised.
    rendered, note = V.render_verdict(True, 1, 2)
    assert rendered is False, "a partial parse claimed the strong result"
    assert "1/2" in note, note

    # The denominator must come from the block list, never the numerator.
    assert "1/2" in V.render_verdict(True, 1, 2)[1]
    assert "0/3" in V.render_verdict(True, 0, 3)[1]

    assert V.render_verdict(True, 0, 0)[0] is False
    assert V.render_verdict(False, 0, 1) == (
        False, " (text only — add --render to prove it parses)")


def test_stamping_writes_no_bytecode_into_the_skill(tmp_path):
    """`--stamp` imports the renderer; the import must not cache beside it.

    A __pycache__ under a skill root is what this repo's hook blocks
    edits on — the hazard this branch documents twice and then caused
    from inside its own fix.
    """
    cache = SCRIPTS / "__pycache__"
    for f in cache.glob("*.pyc") if cache.exists() else []:
        f.unlink()
    if cache.exists():
        cache.rmdir()
    md = make_md(tmp_path)
    # Spawn with PYTHONDONTWRITEBYTECODE stripped. CI sets it for the whole
    # job, and the local run instructions set it too — so with it inherited
    # this test passes because of the ENVIRONMENT and not because of the
    # guard, and deleting the guard leaves it green. A check that cannot
    # fail reads as coverage.
    env = {k: v for k, v in os.environ.items() if k != "PYTHONDONTWRITEBYTECODE"}
    for script, *args in ((RENDER, md), (VERIFY, "--stamp", md.with_suffix(".html"))):
        subprocess.run(
            [sys.executable, str(script), *map(str, args)],
            capture_output=True, text=True, env=env,
        )
    assert not cache.exists(), f"{cache} was created by a --stamp run"


def test_the_number_space_observation_still_fires(tmp_path):
    """The most contestable behavioural change on the branch.

    Deleting the WARN entirely left every other test green, so the
    demotion could rot into silence unnoticed.
    """
    md = make_md(tmp_path, payload=" 1. 第一步")
    run(RENDER, md)
    r = run(VERIFY, md.with_suffix(".html"))
    assert "number. space" in r.stdout
    assert r.returncode == 0, "the observation must not block"


def test_stamping_preserves_crlf(tmp_path):
    """One --stamp rewrote every line of a CRLF-authored artifact.

    The sibling converter goes out of its way to accept CRLF; destroying
    it here would make the two scripts disagree about whether that input
    is supported.
    """
    md = make_md(tmp_path)
    md.write_bytes(md.read_text(encoding="utf-8").replace("\n", "\r\n").encode())
    run(RENDER, md)
    before = md.read_bytes().count(b"\r\n")
    run(VERIFY, "--stamp", md.with_suffix(".html"))
    after = md.read_bytes()
    assert after.count(b"\r\n") == before, "CRLF line endings were rewritten"
    assert b"\n" not in after.replace(b"\r\n", b""), "mixed line endings"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
