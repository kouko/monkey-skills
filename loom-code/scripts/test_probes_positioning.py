"""Adversary-first probes for 2026-09-04-reviewer-and-adversary-positioning.

Written at W0-01 by the adversary agent BEFORE any implementer exists (build
station §2 adversary-first for `code`/`gate` tasks), so most cases below are
RED now and are what W1-01 / W1-02 / W1-03 have to turn GREEN. The adversary
did not implement any of W1-01/W1-02/W1-03 -- reviewer/adversary ne
implementer.

Attack surfaces, from plan.md W0-01:

  (1) reviewer.md and adversary.md each grow ONE paragraph starting `You own`,
      <= 6 sentences with no sentence over 40 words (sentence cap; see
      plan.md `## 單位決定`, W1-02), citing no `docs/` path (portability rule).
  (2) the reviewer paragraph names all three reconciliation directions
      (omission / overclaim / contradiction), says it MAY cite the
      adversary's execution evidence, and says it writes no probes itself;
      the adversary paragraph says negative + re-runnable on a clean tree +
      does not reconcile.
  (3) fix-rounds.md gains a sentence handing a reader's `important`
      executable finding to THIS fix round's adversary as a probe, AND still
      says probes are not re-run in a fix round. Both must hold: the new
      sentence is "write one and run it once", not "re-run the existing set".
  (4) the new README section: every line <= 72 display columns, all three
      contract file names present, both 並行 and 先後 present, and the
      embedded JSON payload regenerates the diagram byte-for-byte.
  (5) neither paragraph dresses the split up as "industry consensus" --
      the research (evidence/research-role-separation-ablations.md) found NO
      direct comparison of reviewer-vs-adversary as separate agents.
  (6) plugin.json version > 1.2.0 and the CHANGELOG carries that version.

Word counts use `len(str.split())`, never `wc` (BSD/GNU never agree; see the
repo's own memory entry). Display width uses `wcwidth` when importable, else
an `unicodedata.east_asian_width` fallback ('W','F' -> 2, else 1); the width
case says in its own docstring which oracle it used.

## Attack-catalogue classes considered against the PLANNED paragraphs

These are cold-read attempts against prose that does not exist yet, so they
cannot be pytest cases. Recorded here one line per class so W1-01's
implementer writes the wording defensively rather than discovering these at
checkpoint:

* forge an artifact the gate trusts -- LIVE RISK. The reviewer paragraph
  says the reader may CITE the adversary's execution evidence. Nothing
  makes a reader open the probe file: a reader can cite `probes[]` it never
  read, and the citation looks identical either way. Mitigation for W1-01:
  make the permission point at a checkable action ("cite the probe record
  by its `command`"), never at a judgement ("cite relevant evidence") --
  plan Risk 5 says the same thing.
* bypass a gate by editing its input -- HELD BY ABSENCE. Neither paragraph
  is marked `<!-- gate: <id> -->`, so per CLAUDE.md 散文不當閘 neither is a
  gate; there is no gate input here to edit. This is exactly why (1)-(6) are
  text probes, not checker invocations.
* replay a stale artifact -- LIVE RISK on surface (3). The fix-round
  sentence tells the adversary to write a probe from a reader finding, but
  a fix round does NOT re-run probes (that is the file's standing rule the
  sentence must not contradict). So the newly written probe's only pass
  evidence is the single run the adversary does by hand; if it later rots,
  nothing in the fix round notices -- `push` is the freshness check. W1-01
  should say "runs it once here" explicitly so the one run is a recorded
  fact, not an implied one.
* cross a trust boundary -- N/A to the paragraphs (single repo, single
  process, no cwd or worktree claim). It IS live for W1-01/W1-02 running in
  parallel in one tree: plan Risk 4 requires path-limited commits and no
  amend. Not probeable from here.
* self-exempt via a prose condition -- LIVE RISK on surface (2). "The
  reader does not write probes" invites the reading "...unless it is
  quicker to just write one", and nothing recomputes who authored a probe.
  The only real defence is that the adversary paragraph claims the negative
  exclusively; W1-01 must not soften either side into "primarily" or
  "generally".
* race a concurrent writer -- N/A to the paragraphs; live for the two
  parallel W1 tasks writing review.json-adjacent files, which is a build
  station concern, not contract text.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

REVIEWER = REPO_ROOT / "loom-code" / "agents" / "reviewer.md"
ADVERSARY = REPO_ROOT / "loom-code" / "agents" / "adversary.md"
FIX_ROUNDS = (
    REPO_ROOT / "loom-code" / "skills" / "review" / "references" / "fix-rounds.md"
)
README = REPO_ROOT / "docs" / "loom" / "README.md"
PLUGIN_JSON = REPO_ROOT / "loom-code" / ".claude-plugin" / "plugin.json"
CHANGELOG = REPO_ROOT / "loom-code" / "CHANGELOG.md"

# W1-02: import the shared sentence-split helper and its constants from the
# shipped module instead of re-implementing the split rule a third time
# (plan.md W1-02).
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_review_station_text import (  # noqa: E402
    SENTENCE_CAP,
    SENTENCE_WORD_CAP,
    _sentences,
)

WIDTH_CAP = 72
BASELINE_VERSION = (1, 2, 0)

BANNED_AUTHORITY_PHRASES = (
    "industry consensus",
    "業界共識",
    "industry standard",
)

GENERATOR_GLOB = (
    "ascii-graph-toolkit/*/skills/ascii-graph/scripts/generate.py"
)


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------


def _blocks(text: str) -> list[str]:
    """Split a markdown file into blank-line-separated blocks."""
    return [b for b in re.split(r"\n\s*\n", text) if b.strip()]


def _positioning_paragraph(path: Path) -> str:
    """Return the one block whose first non-blank line starts `You own`.

    Fails loud when there is none or more than one: the contract asks for
    exactly ONE positioning paragraph per file, and two would mean the
    boundary is stated twice and can drift.
    """
    text = path.read_text(encoding="utf-8")
    hits = [b for b in _blocks(text) if b.lstrip().startswith("You own")]
    assert hits, (
        f"{path.relative_to(REPO_ROOT)} has no paragraph starting `You own` "
        "-- the positioning paragraph is missing (RED until W1-01)"
    )
    assert len(hits) == 1, (
        f"{path.relative_to(REPO_ROOT)} has {len(hits)} `You own` paragraphs; "
        "the contract asks for exactly one"
    )
    return hits[0]


def _display_width(line: str) -> int:
    """Columns `line` occupies in a fixed-width terminal.

    Uses `wcwidth` when importable (the oracle `ascii-graph-toolkit`'s own
    generators use); otherwise falls back to
    `unicodedata.east_asian_width in ('W', 'F') -> 2 else 1`.
    """
    try:
        from wcwidth import wcswidth
    except ImportError:
        return sum(
            2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
            for ch in line
        )
    width = wcswidth(line)
    if width < 0:  # unprintable control char somewhere
        return sum(
            2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
            for ch in line
        )
    return width


def _role_section(text: str) -> tuple[str, list[str]]:
    """Return (heading, body lines) of the README's role-trigger section.

    Identified structurally, not by title text: it is the `##` section that
    mentions `blind-runner`. Requiring exactly one keeps a second copy of
    the section from being added elsewhere in the file.
    """
    lines = text.splitlines()
    starts = [i for i, ln in enumerate(lines) if ln.startswith("## ")]
    sections = []
    for idx, start in enumerate(starts):
        end = starts[idx + 1] if idx + 1 < len(starts) else len(lines)
        sections.append((lines[start], lines[start:end]))
    hits = [s for s in sections if any("blind-runner" in ln for ln in s[1])]
    assert hits, (
        "docs/loom/README.md has no `##` section mentioning `blind-runner` "
        "-- the role-trigger section is missing (RED until W1-02)"
    )
    assert len(hits) == 1, (
        f"docs/loom/README.md has {len(hits)} sections mentioning "
        "`blind-runner`; expected exactly one"
    )
    return hits[0]


def _fences(lines: list[str]) -> list[tuple[str, list[str]]]:
    """Return [(info string, content lines)] for every ``` fence in `lines`."""
    out: list[tuple[str, list[str]]] = []
    info: str | None = None
    body: list[str] = []
    for ln in lines:
        if ln.startswith("```"):
            if info is None:
                info = ln[3:].strip()
                body = []
            else:
                out.append((info, body))
                info = None
        elif info is not None:
            body.append(ln)
    return out


def _version_tuple(raw: str) -> tuple[int, ...]:
    return tuple(int(part) for part in raw.split("."))


# --------------------------------------------------------------------------
# surface (1) -- the paragraph exists, is capped, and cites no docs/ path
# --------------------------------------------------------------------------


@pytest.mark.parametrize("path", [REVIEWER, ADVERSARY], ids=["reviewer", "adversary"])
def test_positioning_paragraph_starts_capped_and_portable(path: Path) -> None:
    """Surface (1). RED until W1-01, re-pinned to the sentence cap at W1-02.

    Each contract grows exactly one `You own` paragraph, <= SENTENCE_CAP (6)
    sentences with no sentence over SENTENCE_WORD_CAP (40) words -- split and
    counted the shared way (`test_review_station_text._sentences`) -- and
    containing no `docs/` path -- an agent dispatched into another repo
    cannot resolve this repo's research files, which is CLAUDE.md's Contract
    Citations rule, not a style preference.
    """
    para = _positioning_paragraph(path)
    sentences = _sentences(para)
    assert len(sentences) <= SENTENCE_CAP, (
        f"{path.relative_to(REPO_ROOT)} positioning paragraph has "
        f"{len(sentences)} sentences, cap is {SENTENCE_CAP}: {sentences!r}"
    )
    for s in sentences:
        words = len(s.split())
        assert words <= SENTENCE_WORD_CAP, (
            f"{path.relative_to(REPO_ROOT)} positioning paragraph sentence "
            f"{s!r} is {words} words, cap is {SENTENCE_WORD_CAP}"
        )
    assert "docs/" not in para, (
        f"{path.relative_to(REPO_ROOT)} positioning paragraph cites a `docs/` "
        "path; a contract read from another repo cannot resolve it"
    )


# --------------------------------------------------------------------------
# surface (2) -- each paragraph claims its own kind of truth
# --------------------------------------------------------------------------


def test_reviewer_paragraph_owns_reconciliation_and_writes_no_probes() -> None:
    """Surface (2), reviewer half. RED until W1-01.

    The reviewer paragraph must name all three reconciliation directions
    (omission / overclaim / contradiction), must say it may lean on the
    adversary's execution evidence, and must say it writes no probes itself.
    Without the third clause the paragraph reads as "reconciliation only",
    which is the exact over-correction intent Proposed outcome 2 rejects.
    """
    para = _positioning_paragraph(REVIEWER)
    low = para.lower()
    for direction in ("omission", "overclaim", "contradiction"):
        assert direction in low, (
            f"reviewer positioning paragraph never names `{direction}`; "
            "all three reconciliation directions are required"
        )
    assert "adversary" in low, (
        "reviewer positioning paragraph never mentions the adversary, so it "
        "never grants the permission to cite its execution evidence"
    )
    assert re.search(r"\b(no|not|never|nor|without)\b[^.]{0,80}probe", low), (
        "reviewer positioning paragraph never says it writes no probes "
        "itself; the boundary against the adversary is unstated"
    )


def test_adversary_paragraph_owns_negative_rerunnable_no_reconciling() -> None:
    """Surface (2), adversary half. RED until W1-01.

    The adversary paragraph must claim the NEGATIVE (forbidden behaviour),
    must require evidence that re-runs on a CLEAN TREE (a case that ran only
    in one agent's head is not a probe), and must disclaim reconciliation --
    otherwise both roles claim the same truth and the split buys nothing.
    """
    para = _positioning_paragraph(ADVERSARY)
    low = para.lower()
    assert "negative" in low, (
        "adversary positioning paragraph never says it owns the negative"
    )
    assert re.search(r"re-?run", low), (
        "adversary positioning paragraph never requires re-runnable evidence"
    )
    assert "clean tree" in low, (
        "adversary positioning paragraph never says the evidence must re-run "
        "on a clean tree"
    )
    assert re.search(r"\b(no|not|never|nor|without)\b[^.]{0,80}reconcil", low), (
        "adversary positioning paragraph never disclaims reconciliation"
    )


# --------------------------------------------------------------------------
# surface (3) -- the fix-round sentence, and the rule it must not contradict
# --------------------------------------------------------------------------


def test_fix_rounds_hands_reader_finding_to_adversary_as_probe() -> None:
    """Surface (3), first half. RED until W1-01.

    Somewhere in fix-rounds.md there is a block naming all three of
    `important`, the adversary, and a probe -- the sentence that turns a
    reader's executable finding into a probe inside the same fix round.
    Placement is left to W1-01 (the whole file is searched) because the plan
    fixes the file, not the heading.
    """
    text = FIX_ROUNDS.read_text(encoding="utf-8")
    hits = [
        b
        for b in _blocks(text)
        if "important" in b.lower()
        and "adversary" in b.lower()
        and "probe" in b.lower()
    ]
    assert hits, (
        "fix-rounds.md has no block naming `important` + adversary + probe: "
        "a reader's executable finding is still handed to nobody"
    )


def test_fix_rounds_still_refuses_to_re_run_existing_probes() -> None:
    """Surface (3), second half. GREEN NOW -- a regression guard.

    The new sentence adds ONE probe and runs it once; it must not be written
    as, or allowed to erode into, "the fix round re-runs the probe set".
    This case is green before W1-01 on purpose: it pins the standing rule so
    W1-01 cannot pay for the new sentence by deleting the old one.
    """
    text = FIX_ROUNDS.read_text(encoding="utf-8")
    assert "## Probes are not re-run here" in text, (
        "fix-rounds.md lost its `Probes are not re-run here` section"
    )
    assert re.search(r"does not re-run", text), (
        "fix-rounds.md no longer says the resumed reader does not re-run "
        "probes; the new sentence must add a probe, not re-run the set"
    )


# --------------------------------------------------------------------------
# surface (4) -- the README role-trigger section
# --------------------------------------------------------------------------


def test_readme_role_section_names_roles_and_both_synchronicities() -> None:
    """Surface (4), content half. RED until W1-02.

    The section must name all three verification contracts by their contract
    file names (`blind-runner`, `reviewer`, `adversary`) and must say both
    what runs 並行 and what is 先後 -- Acceptance 4 asks for parallel AND
    sequential, and a section naming only one of the two answers half the
    question a future session comes back with.
    """
    heading, lines = _role_section(README.read_text(encoding="utf-8"))
    body = "\n".join(lines)
    for token in ("blind-runner", "reviewer", "adversary", "並行", "先後"):
        assert token in body, (
            f"README role-trigger section ({heading!r}) never mentions "
            f"`{token}`"
        )


def test_readme_role_section_fits_72_display_columns() -> None:
    """Surface (4), width half. RED until W1-02.

    Every line of the section -- diagram, table and prose alike -- must fit
    72 display columns so it survives a narrow IDE pane. Width oracle:
    `wcwidth` when importable in this interpreter, else
    `unicodedata.east_asian_width` in ('W','F') -> 2 else 1. Eyeballed CJK
    padding is exactly the failure this cap exists to catch.
    """
    heading, lines = _role_section(README.read_text(encoding="utf-8"))
    over = [
        (i, _display_width(ln), ln)
        for i, ln in enumerate(lines)
        if _display_width(ln) > WIDTH_CAP
    ]
    assert not over, (
        f"README role-trigger section ({heading!r}) has "
        f"{len(over)} line(s) wider than {WIDTH_CAP} columns: "
        + "; ".join(f"line +{i} = {w} cols" for i, w, _ in over[:5])
    )


def test_readme_diagram_regenerates_from_its_embedded_payload() -> None:
    """Surface (4), reproducibility half. RED until W1-02.

    The section carries the diagram in one fence and its generator payload
    in a ```json fence immediately after. Feeding that payload back to
    `ascii-graph` `generate.py seq` must reproduce the diagram line for
    line. Without this, the payload is a decorative claim: the diagram can
    drift from it silently and a future session regenerating it gets a
    different picture than the one documented.
    """
    matches = sorted(
        (Path.home() / ".claude" / "plugins" / "cache" / "monkey-skills").glob(
            GENERATOR_GLOB
        )
    )
    if not matches:
        pytest.skip(
            "ascii-graph generate.py not found under "
            "~/.claude/plugins/cache/monkey-skills/ascii-graph-toolkit/*/ -- "
            "the regeneration oracle is unavailable on this host"
        )
    generator = matches[-1]

    heading, lines = _role_section(README.read_text(encoding="utf-8"))
    fences = _fences(lines)
    assert len(fences) >= 2, (
        f"README role-trigger section ({heading!r}) has {len(fences)} fenced "
        "block(s); expected the diagram followed by its ```json payload"
    )
    diagram_info, diagram_lines = fences[0]
    payload_info, payload_lines = fences[1]
    assert diagram_info != "json", (
        "the first fenced block in the role-trigger section is json; the "
        "diagram must come first, its payload immediately after"
    )
    assert payload_info == "json", (
        f"the fence after the diagram is ```{payload_info}, not ```json; the "
        "payload must be machine-readable to be re-runnable"
    )

    obj = json.loads("\n".join(payload_lines))
    shape = "seq"
    if "participants" not in obj and "payload" in obj:
        shape = obj.get("shape", "seq")
        obj = obj["payload"]

    proc = subprocess.run(
        [sys.executable, str(generator), shape],
        input=json.dumps(obj),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0, (
        f"generate.py {shape} failed on the embedded payload: "
        f"rc={proc.returncode} stderr={proc.stderr.strip()!r}"
    )
    regenerated = proc.stdout.rstrip("\n").split("\n")
    assert regenerated == diagram_lines, (
        "the embedded payload does not regenerate the diagram in the README; "
        f"generator produced {len(regenerated)} line(s), the fence holds "
        f"{len(diagram_lines)}"
    )


# --------------------------------------------------------------------------
# surface (5) -- no borrowed authority
# --------------------------------------------------------------------------


@pytest.mark.parametrize("path", [REVIEWER, ADVERSARY], ids=["reviewer", "adversary"])
def test_positioning_paragraph_claims_no_industry_authority(path: Path) -> None:
    """Surface (5). RED until W1-01 (the paragraph must exist to be clean).

    `evidence/research-role-separation-ablations.md` found NO direct
    comparison of reviewer-vs-adversary as separate agents. So the paragraph
    may describe THIS flow's division of labour and must not borrow
    authority it does not have -- intent Proposed outcome 4. Deliberately
    not vacuously green: it resolves the paragraph first, so a missing
    paragraph fails rather than passing for want of banned text.
    """
    para = _positioning_paragraph(path).lower()
    for phrase in BANNED_AUTHORITY_PHRASES:
        assert phrase.lower() not in para, (
            f"{path.relative_to(REPO_ROOT)} positioning paragraph claims "
            f"`{phrase}`; the split is this flow's design assumption, not a "
            "measured industry finding"
        )


# --------------------------------------------------------------------------
# surface (6) -- version bump and changelog
# --------------------------------------------------------------------------


def test_plugin_version_bumped_and_changelog_carries_it() -> None:
    """Surface (6). RED until W1-03.

    Changing skill/agent content without bumping `plugin.json` makes
    `plugin update` a silent no-op for every consumer (repo memory:
    "改 skill 內容的 PR 必須 bump plugin 版本"). Compared as an integer
    tuple, not as a string -- "1.2.10" sorts before "1.2.9" lexically and a
    string compare would wave the wrong bump through.
    """
    version = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))["version"]
    assert _version_tuple(version) > BASELINE_VERSION, (
        f"loom-code plugin.json is still {version}; a contract-text change "
        "must bump past "
        + ".".join(str(n) for n in BASELINE_VERSION)
    )
    changelog = CHANGELOG.read_text(encoding="utf-8")
    assert f"[{version}]" in changelog, (
        f"loom-code CHANGELOG.md has no `[{version}]` entry for the version "
        "plugin.json now declares"
    )
