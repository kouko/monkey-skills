"""Tests for `check_contract_citations.py` — see its module docstring for
the protocol-versus-record exemption rule this checker enforces.

The three pass/fail cases below are built entirely on fixtures under
`tmp_path`, never against the live tree — asserting against the live tree
would measure the repo's current state instead of the checker's logic
(plan `docs/loom/plans/2026-08-22-contracts-cite-only-what-ships.md` Task 1
Acceptance).
"""
from __future__ import annotations

from pathlib import Path

from check_contract_citations import (
    classify_citation,
    evaluate,
    extract_docs_candidates,
    scan_repo,
)


def _write_scoped_file(repo_root: Path, rel_path: str, text: str) -> Path:
    path = repo_root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_a_citation_outside_the_debt_list_fails(tmp_path: Path) -> None:
    _write_scoped_file(
        tmp_path,
        "loom-code/skills/some-skill/SKILL.md",
        "See `docs/loom/specs/2026-08-21-code-as-spec-writing-rule.md` for the rule.\n",
    )
    actual = scan_repo(tmp_path)
    ok, messages = evaluate(set(actual.keys()), frozenset())
    assert not ok
    assert any("some-skill/SKILL.md" in m for m in messages)


def test_a_listed_violator_passes(tmp_path: Path) -> None:
    rel = "loom-code/skills/some-skill/SKILL.md"
    _write_scoped_file(
        tmp_path,
        rel,
        "See `docs/loom/specs/2026-08-21-code-as-spec-writing-rule.md` for the rule.\n",
    )
    actual = scan_repo(tmp_path)
    ok, messages = evaluate(set(actual.keys()), frozenset({rel}))
    assert ok, messages


def test_a_listed_file_that_stopped_violating_also_fails(tmp_path: Path) -> None:
    rel = "loom-code/skills/some-skill/SKILL.md"
    _write_scoped_file(
        tmp_path,
        rel,
        "This contract no longer cites anything under docs/.\n",
    )
    actual = scan_repo(tmp_path)
    ok, messages = evaluate(set(actual.keys()), frozenset({rel}))
    assert not ok
    assert any("STALE" in m and rel in m for m in messages)


def test_checker_exits_0_against_the_current_tree() -> None:
    import subprocess
    import sys

    repo_root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [
            sys.executable,
            str(repo_root / "loom-code/scripts/check_contract_citations.py"),
            "--repo-root",
            str(repo_root),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_agent_contracts_are_not_on_the_debt_list() -> None:
    from check_contract_citations import DEBT_LIST

    agent_files = {
        "loom-code/agents/code-reviewer.md",
        "loom-code/agents/docs-reviewer.md",
        "loom-code/agents/code-quality-reviewer.md",
    }
    assert not (agent_files & DEBT_LIST), agent_files & DEBT_LIST


def test_store_directory_citation_is_exempt() -> None:
    assert classify_citation("docs/loom/plans/") == "exempt"
    assert classify_citation("docs/loom/memory") == "exempt"
    assert classify_citation("docs/loom/spec/") == "exempt"


def test_protocol_filename_citation_is_exempt() -> None:
    assert classify_citation("docs/loom/PRINCIPLES.md") == "exempt"
    assert classify_citation("docs/loom/backlog/README.md") == "exempt"
    assert classify_citation("docs/loom/spec/MODEL.md") == "exempt"
    assert classify_citation("docs/loom/queue-state.json") == "exempt"


def test_placeholder_shape_citation_is_exempt() -> None:
    assert classify_citation("docs/loom/specs/<date>-<topic>.md") == "exempt"
    assert (
        classify_citation("docs/loom/discovery/<date>-<slug>/evidence.md")
        == "exempt"
    )


def test_dated_record_citation_is_banned() -> None:
    assert (
        classify_citation("docs/loom/specs/2026-08-21-code-as-spec-writing-rule.md")
        == "banned"
    )
    assert (
        classify_citation(
            "docs/loom/memory/a-number-in-prose-needs-a-test-that-recomputes-it.md"
        )
        == "banned"
    )


def test_a_bare_text_citation_is_extracted_too() -> None:
    """A citation without backticks counts.

    This test previously asserted the opposite — that only backtick-delimited
    spans were extracted — and so pinned the gate's own blind spot. A
    whole-branch reviewer found a dated record cited in plain prose three
    lines from a backticked one in the live corpus: the gate reported OK while
    a real violation sat in the file. A contributor who omitted backticks
    defeated the whole mechanism.
    """
    text = (
        "bare docs/loom/specs/2026-01-01-x.md counts, "
        "and so does `docs/loom/specs/2026-01-02-y.md`.\n"
    )
    assert extract_docs_candidates(text) == [
        "docs/loom/specs/2026-01-01-x.md",
        "docs/loom/specs/2026-01-02-y.md",
    ]


def test_an_external_url_containing_docs_is_not_a_candidate() -> None:
    """Dropping the backtick constraint must not re-admit external URLs.

    The constraint had been added to exclude them; the prefix filter already
    does, since no URL in this corpus contains `docs/loom`.
    """
    text = "see https://source.android.com/docs/core/display/material and code.claude.com/docs/en/workflows.md\n"
    assert extract_docs_candidates(text) == []


def test_the_rule_is_documented_in_claude_md() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    claude_md = repo_root / "CLAUDE.md"
    # Normalise backticks as well as whitespace. Asserting on raw text made an
    # earlier implementer strip code-span formatting OUT of the document to
    # satisfy the test — the document degraded to fit the assertion, which is
    # the wrong direction. The prose owns its formatting; the test adapts.
    raw = claude_md.read_text(encoding="utf-8").replace("`", "")
    flattened = " ".join(raw.split())
    assert (
        "a runtime prose contract under the loom skill and agent trees "
        "must not cite one of this repository's development records "
        "under docs/"
    ) in flattened
    assert "loom-scaffolded store directories" in flattened
    assert ".py/.sh provenance comments" in flattened


def test_a_dated_directory_citation_is_banned() -> None:
    """A bare directory naming one dated record is not a store.

    The exemption first read "no extension in the basename → exempt", which
    waved through `docs/loom/archive/2026-08-13-some-change` — this
    repository's own history, cited as a folder. A whole-branch reviewer
    probed the predicate directly and found it. No live citation exploited
    the hole, which is why it was dormant rather than a false pass.
    """
    assert classify_citation("docs/loom/archive/2026-08-13-my-change") == "banned"


def test_store_directories_and_placeholder_shapes_stay_exempt() -> None:
    """The dated-segment rule must not catch the shapes it sits beside."""
    for path in (
        "docs/loom/backlog",
        "docs/loom/memory",
        "docs/loom/plans",
        "docs/loom/discovery/<date>-<slug>",
    ):
        assert classify_citation(path) == "exempt", path
