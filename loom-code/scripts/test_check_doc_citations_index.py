"""Equivalence + boundary tests for W1-02's basename index (check_doc_citations).

Plan acceptance A2: old and new resolution give byte-identical output over
every markdown file CI's "Check doc citations resolve" step scans
(`.github/workflows/loom-code-ci.yml:169`'s file selection), and the indexed
scan finishes well inside CI's wall-clock budget; plus three boundary cases
(`same-basename-two-dirs`, `slash-path-zero-hits`, `bare-name-zero-hits`)
give identical verdicts to the pre-index linear scan.

Equivalence oracle: `_reference_suffix_candidates` below is the pre-W1-02
linear `endswith` scan, pinned verbatim here (not imported from the module),
so this test proves the new code against an independent copy of the old
code rather than against itself.
"""
from __future__ import annotations

import re
import subprocess
import time
from pathlib import Path

import check_doc_citations as cdc


def _reference_suffix_candidates(repo_files: list[str], cited_path: str) -> list[str]:
    """The pre-W1-02 linear scan, copied verbatim as the equivalence oracle."""
    return [f for f in repo_files if f.endswith("/" + cited_path)]


_CI_DOC_SELECTION_RE = re.compile(
    r"^(docs/loom/[^/]+\.md|docs/loom/intent/|"
    r"loom-(code|design|workflow)/(skills|agents|references|contract)/)"
)


def _ci_selected_md_files(repo_root: Path) -> list[str]:
    """Reproduce `.github/workflows/loom-code-ci.yml:169`'s file selection."""
    tracked = subprocess.run(
        ["git", "-C", str(repo_root), "ls-files", "*.md"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()
    return [f for f in tracked if _CI_DOC_SELECTION_RE.search(f)]


def test_index_equivalence_full_repo() -> None:
    """New (indexed) and reference (linear-scan) resolution give identical
    findings/checked/unchecked for every CI-scanned markdown file, and the
    indexed scan finishes well under CI's wall-clock budget."""
    repo_root = cdc.find_repo_root(Path(__file__))
    md_files = _ci_selected_md_files(repo_root)
    assert md_files, "expected the CI doc-citation file selection to be non-empty"
    repo_files = cdc.list_repo_files(repo_root)

    # New: current module code (index-backed `_suffix_candidates`).
    t0 = time.perf_counter()
    new_reports = [
        cdc.check_doc_report(repo_root / f, repo_root, repo_files) for f in md_files
    ]
    elapsed = time.perf_counter() - t0

    # Reference: identical call sites, forced back onto the pre-index linear
    # scan by swapping the module-level helper the three resolvers share.
    original = cdc._suffix_candidates
    cdc._suffix_candidates = _reference_suffix_candidates
    try:
        reference_reports = [
            cdc.check_doc_report(repo_root / f, repo_root, repo_files)
            for f in md_files
        ]
    finally:
        cdc._suffix_candidates = original

    assert [r.findings for r in new_reports] == [
        r.findings for r in reference_reports
    ]
    assert [r.checked for r in new_reports] == [r.checked for r in reference_reports]
    assert [r.unchecked for r in new_reports] == [
        r.unchecked for r in reference_reports
    ]

    # Secondary, timing-sensitive assertion (plan A2: "wall <= 0.4s"). Flagged
    # as such in the message so a slow CI runner reads as an environment
    # fact, never as a correctness regression.
    assert elapsed <= 0.4, (
        f"TIMING-SENSITIVE: indexed scan over {len(md_files)} docs took "
        f"{elapsed:.3f}s (budget 0.4s) -- re-measure before treating this "
        "as a correctness failure"
    )


def test_same_basename_two_dirs_boundary(tmp_path: Path) -> None:
    """Two files sharing a basename in different directories stay ambiguous
    (UNCHECKED) under the index, exactly as under the linear scan."""
    repo_root = tmp_path / "repo"
    (repo_root / "a" / "one").mkdir(parents=True)
    (repo_root / "a" / "two").mkdir(parents=True)
    repo_files = ["a/one/dup.md", "a/two/dup.md"]

    assert cdc.resolve_cited_path(repo_root, "dup.md", repo_files) is None
    assert len(_reference_suffix_candidates(repo_files, "dup.md")) == 2


def test_slash_path_zero_hits_boundary(tmp_path: Path) -> None:
    """An explicit multi-segment path with zero repo-wide matches is a
    finding (not UNCHECKED) — same verdict as the pre-index linear scan."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    repo_files = ["docs/loom/README.md"]

    assert cdc.resolve_cited_path(repo_root, "no/such/path.md", repo_files) is None
    assert (
        cdc._is_explicit_path_citation_with_no_match("no/such/path.md", repo_files)
        is True
    )


def test_bare_name_zero_hits_boundary(tmp_path: Path) -> None:
    """A bare filename with zero repo-wide matches stays UNCHECKED (not a
    finding) — same verdict as the pre-index linear scan."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    repo_files = ["docs/loom/README.md"]

    assert cdc.resolve_cited_path(repo_root, "ghost.md", repo_files) is None
    assert (
        cdc._is_explicit_path_citation_with_no_match("ghost.md", repo_files) is False
    )
