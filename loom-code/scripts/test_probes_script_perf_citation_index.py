"""Adversarial probes for W1-02 (basename index for citation suffix resolution).

Oracle: the CURRENT `endswith` scan in `check_doc_citations.py`'s three
call sites (`resolve_cited_path` :248, `_is_explicit_path_citation_with_no_match`
:283, `_resolve_snapshot_cited_path` :514) — a 1-line reference is pinned
below as `_reference_resolve` and every probe checks the module's
functions against it directly (never `git show main:...` — CI clones may
be shallow / lack `main`).

Run: `python3 -m pytest loom-code/scripts/test_probes_script_perf_citation_index.py -v`
(needs `loom-code/scripts` on `PYTHONPATH`; conftest below adds it).

RED-today inventory (see bottom of file for the full list as observed):
- `test_basename_index_synthetic_repo_lookup_beats_linear_scan_bound` is
  RED today: the module has no index yet, so the plain `endswith` scan
  measured directly against a hard latency bound overshoots it by 3-10x.
- Every other probe is a differential/equivalence probe. It is GREEN
  today (today's code IS the reference scan) and is a regression pin:
  once W1-02 adds an index, these keep proving the pruning changes
  nothing about *which* files match, only *how fast*.
"""
from __future__ import annotations

import random
import string
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "loom-code" / "scripts"))

import check_doc_citations
from check_doc_citations import (
    _is_explicit_path_citation_with_no_match,
    _resolve_snapshot_cited_path,
    resolve_cited_path,
)


# ---------------------------------------------------------------------------
# Reference: today's semantics, pinned as plain Python (not imported from the
# module under test — this is the oracle the new index-based code must match).
# ---------------------------------------------------------------------------
def _reference_resolve(cited_path: str, repo_files: list[str]) -> list[str]:
    """Today's exact suffix-match scan (copied verbatim from the module)."""
    return [f for f in repo_files if f.endswith("/" + cited_path)]


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True, check=True
    ).stdout


def _init_repo(repo: Path) -> None:
    repo.mkdir(parents=True, exist_ok=True)
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "a@example.com")
    _git(repo, "config", "user.name", "Adversary")


# ---------------------------------------------------------------------------
# 1. Equivalence over a hostile file list.
# ---------------------------------------------------------------------------
def test_resolve_cited_path_hostile_suffixes_matches_reference(tmp_path: Path) -> None:
    """`resolve_cited_path` must agree with the reference scan on every hostile input."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    repo_files = [
        "foo/bar_x.md",       # mid-segment suffix must NOT match citation "x.md"
        "foo/x.md",           # exact basename must match
        "a/b/c/dup.md",       # duplicate basename dir 1
        "z/y/dup.md",         # duplicate basename dir 2
        "docs/loom/README.md",
        "docs\\loom\\weird.md",  # literal backslash in a path entry (hostile data)
        "日本語/ファイル.md",       # non-ASCII path
        "trailing/slash/",       # a "file" entry that is itself a directory-like string
    ]
    hostile_citations = [
        "x.md",              # must resolve to foo/x.md only (1 match)
        "bar_x.md",           # must resolve to foo/bar_x.md
        "dup.md",             # 2 matches -> None (ambiguous)
        "./README.md",        # leading ./ never appears in repo_files -> no match
        "../README.md",       # .. traversal attempt -> no match
        "ファイル.md",           # non-ASCII basename -> 1 match
        "",                   # empty citation -> endswith("/") never matches a file entry
        "loom/README.md",     # multi-segment suffix -> 1 match
        "README.md",          # bare -> 1 match (docs/loom/README.md)
        "slash/",             # citation ending in "/" -> matches "trailing/slash/"? endswith("/slash/") -> no (needs "/" + "slash/")
    ]
    for cited in hostile_citations:
        expected_matches = _reference_resolve(cited, repo_files)
        direct = repo_root / cited
        if direct.is_file():
            continue  # direct-hit branch is orthogonal to the suffix index
        expected = repo_root / expected_matches[0] if len(expected_matches) == 1 else None
        actual = resolve_cited_path(repo_root, cited, repo_files)
        assert actual == expected, f"cited={cited!r} expected={expected} actual={actual}"


def test_is_explicit_path_citation_hostile_suffixes_matches_reference() -> None:
    """`_is_explicit_path_citation_with_no_match` must agree with the reference on multi-segment hostile paths."""
    repo_files = [
        "foo/bar_x.md",
        "foo/x.md",
        "a/b/c/dup.md",
        "z/y/dup.md",
        "docs/loom/README.md",
    ]
    hostile = [
        "foo/x.md",            # 1 match -> not a no-match citation
        "nope/x.md",           # 0 matches -> True (no match)
        "b/c/dup.md",          # ambiguous is NOT zero -> reference says 1 match here actually
        "loom/<change-id>.md",  # placeholder grammar -> excluded, always False
        "a/b",                  # no trailing "/name" segment match -> 0 real-file suffix hits
    ]
    for cited in hostile:
        expected_matches = _reference_resolve(cited, repo_files)
        expected = "/" in cited and "<" not in cited and ">" not in cited and len(expected_matches) == 0
        actual = _is_explicit_path_citation_with_no_match(cited, repo_files)
        assert actual == expected, f"cited={cited!r} expected={expected} actual={actual}"


def test_resolve_snapshot_cited_path_hostile_suffixes_matches_reference() -> None:
    """`_resolve_snapshot_cited_path` must agree with the reference on hostile inputs."""
    repo_files = [
        "foo/bar_x.md",
        "foo/x.md",
        "a/b/c/dup.md",
        "z/y/dup.md",
        "docs/loom/README.md",
    ]
    hostile = ["x.md", "bar_x.md", "dup.md", "docs/loom/README.md", "", "nope.md"]
    for cited in hostile:
        if cited in repo_files:
            expected = cited
        else:
            expected_matches = _reference_resolve(cited, repo_files)
            expected = expected_matches[0] if len(expected_matches) == 1 else None
        actual = _resolve_snapshot_cited_path(cited, repo_files)
        assert actual == expected, f"cited={cited!r} expected={expected} actual={actual}"


# ---------------------------------------------------------------------------
# 2. Performance-shaped probe: linear scan cannot meet an index-shaped bound.
# ---------------------------------------------------------------------------
def test_basename_index_synthetic_repo_lookup_beats_linear_scan_bound(tmp_path: Path) -> None:
    """All three resolvers must answer 500 lookups against 50k files well under
    the time a linear `endswith` scan needs — RED today (no index exists yet)."""
    random.seed(20260907)

    def randname(n: int = 8) -> str:
        return "".join(random.choices(string.ascii_lowercase, k=n))

    repo_files: list[str] = []
    for _ in range(50_000):
        depth = random.randint(1, 4)
        parts = [randname() for _ in range(depth)] + [randname() + ".md"]
        repo_files.append("/".join(parts))
    bare_citations = [random.choice(repo_files).split("/")[-1] for _ in range(500)]
    explicit_citations = [
        "/".join(random.choice(repo_files).split("/")[-2:]) for _ in range(500)
    ]

    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    bound_seconds = 0.3  # an index-backed lookup easily clears this; a scan does not

    t0 = time.perf_counter()
    for cited in bare_citations:
        resolve_cited_path(repo_root, cited, repo_files)
    elapsed_resolve = time.perf_counter() - t0

    t0 = time.perf_counter()
    for cited in explicit_citations:
        _is_explicit_path_citation_with_no_match(cited, repo_files)
    elapsed_explicit = time.perf_counter() - t0

    t0 = time.perf_counter()
    for cited in bare_citations:
        _resolve_snapshot_cited_path(cited, repo_files)
    elapsed_snapshot = time.perf_counter() - t0

    assert elapsed_resolve < bound_seconds, (
        f"resolve_cited_path took {elapsed_resolve:.3f}s for 500 lookups over "
        f"50k files (bound {bound_seconds}s) -- no basename index yet"
    )
    assert elapsed_explicit < bound_seconds, (
        f"_is_explicit_path_citation_with_no_match took {elapsed_explicit:.3f}s "
        f"(bound {bound_seconds}s) -- no basename index yet"
    )
    assert elapsed_snapshot < bound_seconds, (
        f"_resolve_snapshot_cited_path took {elapsed_snapshot:.3f}s "
        f"(bound {bound_seconds}s) -- no basename index yet"
    )


# ---------------------------------------------------------------------------
# 3. End-to-end: pin today's observed stdout/stderr/exit code over the three
#    intent sandbox cases (same-basename-two-dirs, slash-path-zero-hits,
#    bare-name-zero-hits).
# ---------------------------------------------------------------------------
def test_end_to_end_intent_sandbox_cases_match_pinned_baseline(tmp_path: Path) -> None:
    """The three intent-listed cases must reproduce byte-identical output to
    what running check_doc_citations.py against them produces TODAY."""
    repo = tmp_path / "repo"
    _init_repo(repo)

    (repo / "a" / "one").mkdir(parents=True)
    (repo / "a" / "one" / "dup.md").write_text("dup one\n", encoding="utf-8")
    (repo / "a" / "two").mkdir(parents=True)
    (repo / "a" / "two" / "dup.md").write_text("dup two\n", encoding="utf-8")

    doc = repo / "citing.md"
    doc.write_text(
        "\n".join(
            [
                "See `dup.md:1` for the same-basename-two-dirs case.",
                "See `no/such/path.md:1` for the slash-path-zero-hits case.",
                "See `ghost.md:1` for the bare-name-zero-hits case.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "seed")

    script = str(
        Path(__file__).resolve().parents[2]
        / "loom-code"
        / "scripts"
        / "check_doc_citations.py"
    )
    result = subprocess.run(
        [sys.executable, script, str(doc)],
        cwd=repo,
        capture_output=True,
        text=True,
    )

    # Pinned after observing today's actual run (2026-09-07, this worktree's
    # HEAD before W1-02's implementation lands): dup.md resolves to neither
    # candidate (ambiguous -> UNCHECKED), the explicit slash-path with zero
    # hits is a finding, and the bare zero-hit name is UNCHECKED.
    assert result.returncode == 1
    assert result.stdout == (
        "checked 1 / unchecked 2 / findings 1\n"
        f"{doc}:2 -> no/such/path.md:1 file not found\n"
    )
    assert result.stderr == ""


# ---------------------------------------------------------------------------
# 4. Cache/mutation contract: repo_files mutated after the index (if any) is
#    built. This documents the observed contract today (a fresh list per
#    call site, always freshly scanned) rather than pinning an unverifiable
#    future contract -- see findings for the reviewer.
# ---------------------------------------------------------------------------
def test_resolve_cited_path_repo_files_mutated_after_call_uses_latest_list(
    tmp_path: Path,
) -> None:
    """Today, `resolve_cited_path` always scans the `repo_files` list passed to
    THIS call -- a file appended to the list before the next call is visible
    on that next call (no cross-call caching of `repo_files` itself)."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    repo_files = ["a/one.md"]

    first = resolve_cited_path(repo_root, "new.md", repo_files)
    assert first is None  # not present yet

    repo_files.append("b/new.md")  # mutate the list in place between calls

    second = resolve_cited_path(repo_root, "new.md", repo_files)
    assert second == repo_root / "b/new.md"  # visible immediately: no stale cache
