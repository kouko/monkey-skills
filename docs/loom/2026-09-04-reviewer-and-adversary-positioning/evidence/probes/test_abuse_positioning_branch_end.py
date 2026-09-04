"""Branch-end adversarial probes for 2026-09-04-reviewer-and-adversary-positioning.

Written at the branch-end checkpoint by a SECOND adversary agent (not the
W0-01 one, and not an implementer of W1-01/W1-02/W1-03), against HEAD
090ecf6643bfac605f440629e0cf88ac38aff7a6. `test_abuse_positioning.py` proves
the shipped text HAS the required properties; this file attacks a different
question: are those proofs vacuous, and did the shipped wording actually
close the LIVE risks the W0-01 adversary left open?

Three families here, none of them present in the W0-01 file:

  (A) MUTATION SENSITIVITY. Each case copies a contract to a tmp file,
      deletes one load-bearing word ("omission", "adversary", "negative",
      "clean tree"), re-points the W0-01 module's own constant at the copy,
      and asserts the W0-01 case goes RED. A text assertion nobody has ever
      seen fail is a test that asserts nothing. One case runs the mutation
      the other way and asserts the W0-01 suite stays GREEN -- that is a
      coverage HOLE, not a success (see `test_fix_rounds_once_is_uncovered`).
  (B) CROSS-FILE CONSISTENCY the W0-01 file did not reach: the six places
      the 1.2.1 stamp lives, and the reviewer.md word cap that W1-03 bumped
      1200 -> 1300 (does the new cap bind, and was the bump even needed?).
  (C) DOCS CLAIMS. Two timing claims in the new README step table are
      grep-checked against build/SKILL.md and review/SKILL.md. A README
      claim the skills do not support is an `incorrect-fact` finding.

Plus one `xfail(strict=True)` case carrying a finding found by cold reading
and then pinned executably: reviewer.md now contradicts itself about
`probes[]`'s `result` field. Strict xfail means the day the wording is
fixed this file goes RED on XPASS, so the marker cannot outlive the bug.

Word counts use `len(str.split())`, never `wc` (BSD/GNU never agree).

## Attack-catalogue classes x the three changed contract files

Six classes attempted against each of reviewer.md, adversary.md,
fix-rounds.md. Cold-read attempts that cannot execute are one line each,
per `docs/loom/2026-09-04-checker-seams/evidence/probes/test_abuse_branch_end.py`:

* forge an artifact the gate trusts
  - reviewer.md: PARTLY CLOSED. W0-01 left this LIVE ("a reader can cite
    `probes[]` it never read"). Shipped wording says "cite an adversary
    probe record's command and result already in `probes[]`" -- `command`
    and "already in" are checkable against the file, so a fabricated
    citation no longer looks identical to a real one. Residue: nothing
    RECOMPUTES the match (no checker rule; per CLAUDE.md unmarked prose is
    not a gate), so the defence is a reader's diligence. Pinned by
    `test_reviewer_citation_points_at_a_checkable_record`.
  - adversary.md: HELD. The paragraph demands evidence that re-runs on a
    clean tree, and `push.probes-adversarial` re-runs probes there.
  - fix-rounds.md: HELD BY ABSENCE. The new block records one probe into
    `probes[]`, which push re-runs; it forges nothing.
* bypass a gate by editing its input
  - all three: NOT APPLICABLE. None of the three new blocks carries a
    `<!-- gate: <id> -->` marker, so none is a gate and there is no gate
    input to edit. This is why every case here is a text/consistency probe.
* replay a stale artifact
  - fix-rounds.md: PARTLY CLOSED. W0-01 asked for "runs it once here"
    explicitly so the single run is a recorded fact; the shipped text says
    it. But NO shipped test pins that word --
    `test_fix_rounds_once_is_uncovered` reproduces the hole by deleting
    "once" and watching the W0-01 case still pass;
    `test_fix_rounds_block_records_a_single_run` closes it.
  - reviewer.md: LIVE, nit. "cite ... result already in `probes[]`" has no
    freshness qualifier: a `probes[]` record from an earlier round, taken
    at an older `sha`, reads as citable. The round's `scope`/`sha` fields
    exist, and the paragraph does not point at them.
  - adversary.md: HELD -- "re-runs on a clean tree" is itself the
    anti-replay clause.
* cross a trust boundary (repo / worktree / process)
  - reviewer.md, adversary.md: HELD. Both paragraphs are portable prose
    citing no `docs/` path (W0-01 surface (1) pins this).
  - fix-rounds.md: NOT APPLICABLE to the text; live only for the concurrent
    4a/4b writers in one tree, which is a build-station concern.
* self-exempt via a prose condition
  - reviewer.md: LIVE, important. "Reconciliation-first, not
    execution-free" is an unbounded grant with no stated ceiling; the only
    thing bounding it is the next clause. Worse, reviewer.md's OWN older
    rule says a dimension resting on evidence you did not run yourself
    scores `PASS_WITH_NOTES`, and the new permission to cite an adversary
    probe never points at that downgrade -- so a reader can cite a probe
    and hand out a clean `PASS`. Pinned as a finding, not a test: the fix
    is one clause, and asserting its absence would be asserting a bug.
  - reviewer.md, softeners: HELD. `test_no_softener_weakens_either_boundary`
    runs -- neither paragraph says "primarily"/"generally"/"usually", so
    "you write no probes yourself" has no "...unless it is quicker" hinge.
  - adversary.md: HELD, with one over-claim. "Every piece of your evidence
    is executable" is absolute, while the file's own `Spec` recipe two
    sections below ("red-team each requirement") and its `findings:` output
    block produce evidence that is not executable. Nit: the trailing clause
    ("...is not a probe") scopes it to probes for a careful reader.
  - fix-rounds.md: HELD. "done inside the fix round, no hand-off" leaves no
    condition under which the round may defer the probe to someone else.
* race a concurrent writer
  - all three: NOT APPLICABLE to contract prose (no shared mutable file is
    described). Live for this checkpoint's own 4a/4b commits, which is why
    every commit here is path-limited -- a build/review station concern.

## Contradiction sweep (reviewer lens class, run here as a cold read)

* reviewer.md vs itself: REPRODUCED, important -- see
  `test_reviewer_result_citation_contradicts_tests_dimension_rule`.
* adversary.md vs itself: nit only (the "every piece of your evidence"
  over-claim above).
* fix-rounds.md vs itself: HELD -- W0-01's
  `test_fix_rounds_still_refuses_to_re_run_existing_probes` is green, and
  the new block says "adds and runs one new probe; it does not re-run
  existing ones" in as many words.
* the three files vs review/SKILL.md: HELD -- SKILL.md §4 already says the
  adversary's findings "enter `findings` like any other finding" and its
  runs "enter `probes[]`", which is the same split the two new paragraphs
  state; no wording in SKILL.md gives the reviewer a probe to write.
"""

from __future__ import annotations

import importlib.util
import itertools
import json
import re
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[5]
SIBLING = HERE / "test_abuse_positioning.py"

REVIEWER = REPO_ROOT / "loom-code" / "agents" / "reviewer.md"
ADVERSARY = REPO_ROOT / "loom-code" / "agents" / "adversary.md"
FIX_ROUNDS = (
    REPO_ROOT / "loom-code" / "skills" / "review" / "references" / "fix-rounds.md"
)
LOOM_README = REPO_ROOT / "docs" / "loom" / "README.md"
ROOT_README = REPO_ROOT / "README.md"
CHANGELOG = REPO_ROOT / "loom-code" / "CHANGELOG.md"
PLUGIN_JSON = REPO_ROOT / "loom-code" / ".claude-plugin" / "plugin.json"
CODEX_PLUGIN_JSON = REPO_ROOT / "loom-code" / ".codex-plugin" / "plugin.json"
CODEX_HOOK_SH = REPO_ROOT / ".codex" / "hooks" / "loom-checker"
CODEX_HOOK_PY = REPO_ROOT / ".codex" / "hooks" / "loom_checker.py"
BUILD_SKILL = REPO_ROOT / "loom-code" / "skills" / "build" / "SKILL.md"
REVIEW_SKILL = REPO_ROOT / "loom-code" / "skills" / "review" / "SKILL.md"
SINGLE_CONTRACT_TEST = (
    REPO_ROOT / "loom-code" / "scripts" / "test_reviewer_agent_single_contract.py"
)

REVIEWER_CAP = 1300
PREVIOUS_REVIEWER_CAP = 1200
SOFTENERS = ("primarily", "generally", "usually", "typically", "normally", "mostly")

_COUNTER = itertools.count()


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------


def _load_w0_module():
    """Import `test_abuse_positioning.py` fresh, under a throwaway name.

    Fresh each call so a test can re-point one of its module constants at a
    mutated copy without leaking that into the next case.
    """
    name = f"_w0_probe_{next(_COUNTER)}"
    spec = importlib.util.spec_from_file_location(name, SIBLING)
    assert spec and spec.loader, f"cannot import {SIBLING}"
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _body(text: str) -> str:
    match = re.match(r"^---\n.*?\n---\n", text, re.DOTALL)
    return text[match.end() :] if match else text


def _positioning_paragraph(text: str) -> str:
    blocks = [b for b in re.split(r"\n\s*\n", text) if b.strip()]
    hits = [b for b in blocks if b.lstrip().startswith("You own")]
    assert len(hits) == 1, f"expected exactly one `You own` block, got {len(hits)}"
    return hits[0]


def _fix_round_probe_block(text: str) -> str:
    blocks = [b for b in re.split(r"\n\s*\n", text) if b.strip()]
    hits = [
        b
        for b in blocks
        if "important" in b.lower()
        and "adversary" in b.lower()
        and "probe" in b.lower()
    ]
    assert hits, "fix-rounds.md has no `important` + adversary + probe block"
    return hits[0]


def _mutate_paragraph(path: Path, tmp_path: Path, drop: str) -> Path:
    """Copy `path` to tmp with `drop` deleted from its `You own` paragraph.

    Only the paragraph is touched: deleting the token file-wide would also
    hit unrelated prose and the mutation would no longer be minimal.
    """
    text = path.read_text(encoding="utf-8")
    para = _positioning_paragraph(text)
    assert drop.lower() in para.lower(), (
        f"{path.name} positioning paragraph does not contain {drop!r}; "
        "the mutation would be a no-op and the case vacuous"
    )
    mutated_para = re.sub(re.escape(drop), "", para, count=1, flags=re.IGNORECASE)
    out = tmp_path / path.name
    out.write_text(text.replace(para, mutated_para, 1), encoding="utf-8")
    return out


def _versions() -> dict[str, str]:
    def _plugin(path: Path) -> str:
        return json.loads(path.read_text(encoding="utf-8"))["version"]

    root = ROOT_README.read_text(encoding="utf-8")
    row = re.search(r"\|\s*\[`loom-code`\][^|]*\|\s*([0-9][0-9.]*)\s*\|", root)
    assert row, "root README.md has no `loom-code` plugin-table row with a version"

    changelog = CHANGELOG.read_text(encoding="utf-8")
    top = re.search(r"^##\s*\[([0-9][0-9.]*)\]", changelog, re.MULTILINE)
    assert top, "loom-code/CHANGELOG.md has no `## [x.y.z]` entry"

    def _stamp(path: Path) -> str:
        stamp = re.search(r"#\s*loom-checker\s+([0-9][0-9.]*)", path.read_text("utf-8"))
        assert stamp, f"{path} carries no `# loom-checker <version>` stamp"
        return stamp.group(1)

    return {
        "plugin.json": _plugin(PLUGIN_JSON),
        ".codex-plugin/plugin.json": _plugin(CODEX_PLUGIN_JSON),
        "README.md table row": row.group(1),
        "CHANGELOG top entry": top.group(1),
        ".codex/hooks/loom-checker": _stamp(CODEX_HOOK_SH),
        ".codex/hooks/loom_checker.py": _stamp(CODEX_HOOK_PY),
    }


# --------------------------------------------------------------------------
# (A) mutation sensitivity -- are the W0-01 text assertions vacuous?
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("path", "drop", "case"),
    [
        (REVIEWER, "omission", "test_reviewer_paragraph_owns_reconciliation_and_writes_no_probes"),
        (REVIEWER, "overclaim", "test_reviewer_paragraph_owns_reconciliation_and_writes_no_probes"),
        (REVIEWER, "contradiction", "test_reviewer_paragraph_owns_reconciliation_and_writes_no_probes"),
        (REVIEWER, "adversary", "test_reviewer_paragraph_owns_reconciliation_and_writes_no_probes"),
        (ADVERSARY, "negative", "test_adversary_paragraph_owns_negative_rerunnable_no_reconciling"),
        (ADVERSARY, "clean tree", "test_adversary_paragraph_owns_negative_rerunnable_no_reconciling"),
        (ADVERSARY, "reconcile", "test_adversary_paragraph_owns_negative_rerunnable_no_reconciling"),
    ],
    ids=[
        "reviewer-omission",
        "reviewer-overclaim",
        "reviewer-contradiction",
        "reviewer-adversary",
        "adversary-negative",
        "adversary-clean-tree",
        "adversary-reconcile",
    ],
)
def test_w0_case_dies_when_one_load_bearing_word_is_deleted(
    tmp_path: Path, path: Path, drop: str, case: str
) -> None:
    """(A) Mutation sensitivity. GREEN = the W0-01 case really tests something.

    Delete exactly one load-bearing word from the positioning paragraph in a
    tmp COPY (the tree is never touched -- an adversary that edits the
    artifact to make an attack land has proved nothing), point the W0-01
    module's constant at the copy, and require its case to raise
    `AssertionError`. A surviving mutant here would mean the W0-01 case
    passes for reasons unrelated to the word it claims to pin.
    """
    mutated = _mutate_paragraph(path, tmp_path, drop)
    module = _load_w0_module()
    setattr(module, "REVIEWER" if path is REVIEWER else "ADVERSARY", mutated)
    with pytest.raises(AssertionError):
        getattr(module, case)()


def test_w0_readme_regeneration_case_dies_when_a_payload_label_is_mutated(
    tmp_path: Path,
) -> None:
    """(A) Mutation sensitivity for the README diagram. GREEN = not vacuous.

    Change one label INSIDE the embedded json payload only (the diagram
    fence above it is left alone), and require the W0-01 regeneration case
    to fail. Without this, "the payload regenerates the diagram" could be
    passing because the comparison itself is loose.
    """
    module = _load_w0_module()
    if not sorted(
        (Path.home() / ".claude" / "plugins" / "cache" / "monkey-skills").glob(
            module.GENERATOR_GLOB
        )
    ):
        pytest.skip("ascii-graph generate.py unavailable on this host")

    text = LOOM_README.read_text(encoding="utf-8")
    needle = '"label": "4a 補攻"'
    assert needle in text, (
        "the README json payload no longer carries the `4a 補攻` label; "
        "this mutation target moved and the case would be vacuous"
    )
    out = tmp_path / "README.md"
    out.write_text(text.replace(needle, '"label": "4a 補攻X"', 1), encoding="utf-8")
    module.README = out
    with pytest.raises(AssertionError):
        module.test_readme_diagram_regenerates_from_its_embedded_payload()


def test_fix_rounds_once_is_uncovered(tmp_path: Path) -> None:
    """(A) The mutation that SURVIVES -- a documented coverage hole.

    W0-01's `replay a stale artifact` line asked W1-01 to say "runs it once
    here" so the single run is a recorded fact. The shipped text says it,
    but no shipped case pins it: delete "once" and W0-01's fix-round case
    still passes. This case asserts the survival (so the hole is a fact, not
    an opinion); `test_fix_rounds_block_records_a_single_run` below is the
    probe that actually closes it.
    """
    text = FIX_ROUNDS.read_text(encoding="utf-8")
    block = _fix_round_probe_block(text)
    mutated = block.replace("once", "", 1)
    assert mutated != block, "the fix-round probe block no longer contains `once`"
    out = tmp_path / "fix-rounds.md"
    out.write_text(text.replace(block, mutated, 1), encoding="utf-8")

    module = _load_w0_module()
    module.FIX_ROUNDS = out
    module.test_fix_rounds_hands_reader_finding_to_adversary_as_probe()
    module.test_fix_rounds_still_refuses_to_re_run_existing_probes()


def test_fix_rounds_block_records_a_single_run() -> None:
    """Closes the hole above. The fix-round block must say the probe is run
    ONCE, here, in this round. Without the count, "the adversary encodes it
    and runs it" reads compatibly with "and keeps re-running the set", which
    is exactly the standing rule the same file spends a section refusing.
    """
    block = _fix_round_probe_block(FIX_ROUNDS.read_text(encoding="utf-8"))
    assert re.search(r"\bonce\b", block), (
        "the fix-round probe block never says the new probe is run `once`; "
        "the single run is implied, not recorded"
    )
    assert re.search(r"does not re-run|not re-run", block), (
        "the fix-round probe block never disclaims re-running the existing "
        "probe set, so it can be read as overriding the standing rule"
    )


# --------------------------------------------------------------------------
# self-exempt / forge -- executable halves of the cold reads above
# --------------------------------------------------------------------------


@pytest.mark.parametrize("path", [REVIEWER, ADVERSARY], ids=["reviewer", "adversary"])
def test_no_softener_weakens_either_boundary(path: Path) -> None:
    """`self-exempt via a prose condition`, executable half. HELD.

    "You write no probes yourself" and "you do not reconcile" are absolutes.
    A hedge -- "primarily", "generally", "usually" -- turns either into a
    default the actor can decline, and nothing recomputes who wrote a probe.
    """
    para = _positioning_paragraph(path.read_text(encoding="utf-8")).lower()
    hits = [word for word in SOFTENERS if word in para]
    assert not hits, (
        f"{path.name} positioning paragraph hedges its boundary with "
        f"{hits}; the split is stated as absolute or it is not stated"
    )


def test_reviewer_citation_points_at_a_checkable_record() -> None:
    """`forge an artifact the gate trusts`, executable half. HELD (residue).

    W0-01 required the citation permission to name a CHECKABLE artefact
    (`probes[]`, the record's `command`) rather than a judgement call
    ("cite relevant evidence"). A citation naming a `command` that is in
    `probes[]` can be compared against the file; "cite the evidence" cannot.
    """
    para = _positioning_paragraph(REVIEWER.read_text(encoding="utf-8"))
    assert "probes[]" in para, (
        "reviewer positioning paragraph never names `probes[]`, so the "
        "citation permission points at no checkable artefact"
    )
    assert "command" in para.lower(), (
        "reviewer positioning paragraph grants a citation without naming the "
        "`command` field; a fabricated citation would look identical to a "
        "real one"
    )


@pytest.mark.xfail(
    strict=True,
    reason=(
        "FINDING (important): reviewer.md contradicts itself about `result`. "
        "The new paragraph permits citing a probe record's `command and "
        "result`; the older `tests` dimension paragraph in the same file "
        "says the reviewer reads each entry's `command` and `artifact`, "
        "`never its result`. Fix: drop `and result` from the new paragraph "
        "(or scope it explicitly outside the `tests` dimension). This marker "
        "is strict: the day the wording is fixed this case XPASSes and the "
        "suite goes red, forcing the marker's removal."
    ),
)
def test_reviewer_result_citation_contradicts_tests_dimension_rule() -> None:
    """`contradiction with an older paragraph in the same file`. REPRODUCED.

    Two clauses of reviewer.md, both about `probes[]`, disagree on whether
    `result` is readable. A cold reader who reaches the new paragraph first
    scores a `tests` dimension on a field the file later forbids.
    """
    text = REVIEWER.read_text(encoding="utf-8")
    para = _positioning_paragraph(text)
    cites_result = re.search(r"command and result", para) is not None
    forbids_result = re.search(r"never its `result`", text) is not None
    assert not (cites_result and forbids_result), (
        "reviewer.md permits citing a probe record's `result` in the "
        "positioning paragraph while the `tests` dimension paragraph says "
        "`never its result`"
    )


# --------------------------------------------------------------------------
# (B) cross-file consistency the W0-01 file did not reach
# --------------------------------------------------------------------------


def test_every_place_the_version_is_stamped_agrees() -> None:
    """(B) Six stamps, one version. A `plugin update` is driven by
    `plugin.json`; a reader is driven by the README table and the CHANGELOG;
    a Codex host is driven by the two `.codex/hooks` stamps. Any one of them
    left behind is a silently wrong claim about what shipped.
    """
    versions = _versions()
    distinct = sorted(set(versions.values()))
    assert len(distinct) == 1, (
        "the loom-code version is stamped inconsistently: "
        + ", ".join(f"{where} = {ver}" for where, ver in sorted(versions.items()))
    )


def test_reviewer_cap_binds_at_its_new_value_and_the_bump_was_needed() -> None:
    """(B) Does the bumped cap actually bind? RED at 1301, GREEN at 1300.

    W1-03 raised `AGENT_CAPS["reviewer.md"]` 1200 -> 1300. Two ways that
    could be wrong: the file could already be over 1300 (cap not binding),
    or under 1200 (the bump bought nothing and should be reverted). Counted
    with `len(str.split())` over the body, the same oracle the shipped test
    uses -- never `wc`.
    """
    source = SINGLE_CONTRACT_TEST.read_text(encoding="utf-8")
    assert f'"reviewer.md": {REVIEWER_CAP}' in source, (
        f"test_reviewer_agent_single_contract.py no longer caps reviewer.md "
        f"at {REVIEWER_CAP}"
    )
    words = len(_body(REVIEWER.read_text(encoding="utf-8")).split())
    assert words <= REVIEWER_CAP, (
        f"reviewer.md body is {words} words; the declared cap {REVIEWER_CAP} "
        "does not hold"
    )
    assert not words <= words - 1, "arithmetic oracle broken"
    assert words > PREVIOUS_REVIEWER_CAP, (
        f"reviewer.md body is {words} words, still under the OLD cap "
        f"{PREVIOUS_REVIEWER_CAP}; the bump to {REVIEWER_CAP} bought nothing "
        "and should be reverted -- a cap that never bound is not a cap"
    )


# --------------------------------------------------------------------------
# (C) docs claims -- the README step table against the two SKILL.md files
# --------------------------------------------------------------------------


def test_readme_claim_readers_wait_for_the_adversary_and_blind_run() -> None:
    """(C) README claim: step 5's 同步性 is 「等 4a/4b 落地才派」.

    review/SKILL.md must actually say the reviewers are dispatched only
    after the adversary's and blind-runner's commits land. A README that
    invents an ordering the station does not enforce is an incorrect-fact.
    """
    module = _load_w0_module()
    heading, lines = module._role_section(LOOM_README.read_text(encoding="utf-8"))
    body = "\n".join(lines)
    assert "等 4a" in body and "才派" in body, (
        f"README role section ({heading!r}) no longer claims readers wait "
        "for 4a/4b; this case's target moved"
    )
    # Whitespace-normalised: SKILL.md hard-wraps, so a phrase that spans a
    # line break is invisible to a naive `in`. A grep-shaped claim check that
    # can be defeated by reflowing the source is not a check.
    skill = " ".join(REVIEW_SKILL.read_text(encoding="utf-8").split())
    assert "Dispatch in two stages" in skill, (
        "review/SKILL.md does not describe a two-stage dispatch, so the "
        "README's 「等 4a/4b 落地才派」 is unsupported"
    )
    assert "committed before any reviewer starts" in skill, (
        "review/SKILL.md never says the probes and report are committed "
        "before any reviewer starts; the README claim is unsupported"
    )


def test_readme_claim_small_lane_skips_probes_first_blind_run_and_a_reader() -> None:
    """(C) README claim: 「小車道：跳過 1、4b（Acceptance 為機械條件時），
    5 只派一位；4a 不省」. Four sub-claims, each grep-checked at its source.
    """
    module = _load_w0_module()
    heading, lines = module._role_section(LOOM_README.read_text(encoding="utf-8"))
    body = "\n".join(lines)
    assert "小車道" in body, f"README role section ({heading!r}) lost 小車道"

    build = BUILD_SKILL.read_text(encoding="utf-8")
    assert re.search(r"\*\*small lane\*\*[^.]*skips this", build, re.DOTALL), (
        "build/SKILL.md does not say the small lane skips adversary-first, "
        "so the README's 「跳過 1」 is unsupported"
    )

    review = REVIEW_SKILL.read_text(encoding="utf-8")
    small_row = [ln for ln in review.splitlines() if ln.startswith("| `small`")]
    assert small_row, "review/SKILL.md has no `small` lane row"
    row = small_row[0]
    assert "one fresh-context reviewer" in row, (
        "review/SKILL.md's small-lane row does not say one reviewer; the "
        "README's 「5 只派一位」 is unsupported"
    )
    assert "adversarial probes" in row, (
        "review/SKILL.md's small-lane row does not keep the adversarial "
        "pass; the README's 「4a 不省」 is unsupported"
    )
    assert "blind run runs only when" in row and "not mechanical" in row, (
        "review/SKILL.md's small-lane row does not make the blind run "
        "conditional on a non-mechanical Acceptance line; the README's "
        "「跳過 4b（Acceptance 為機械條件時）」 is unsupported"
    )
