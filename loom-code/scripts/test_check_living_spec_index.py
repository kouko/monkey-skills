"""Tests for the living-spec structural-violation gate.

`find_structural_violations(tag_records, malformed, namespace)` takes
the already-computed outputs of the slice-1 parser
(`extract_tags` -> `tag_records`, `find_malformed_tags` -> `malformed`)
plus the req-to-capability `namespace` (`load_namespace` output), and
returns one violation string per problem found:

- a DANGLING `@req` — a test's `@req` id absent from `namespace`;
- each MALFORMED tag line (passed through verbatim).

Clean input (every `@req` resolves, no malformed lines) returns `[]`.

The module is loaded by file path because its filename uses a hyphen
(not importable by name) — mirrors `test_check_skill_crossrefs.py`.
Stdlib only.
"""

import importlib.util
import os
import subprocess
from pathlib import Path

_MODULE_PATH = Path(__file__).parent / "check-living-spec-index.py"


def _load_checker():
    spec = importlib.util.spec_from_file_location(
        "check_living_spec_index", _MODULE_PATH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _git(repo: Path, *args: str, env: dict | None = None) -> str:
    """Run a git command in `repo`, return stdout (stripped)."""
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    return result.stdout.strip()


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    return repo


def _commit(repo: Path, message: str, *, date: str) -> str:
    """Stage all + commit with a pinned author/committer date; return SHA."""
    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = date
    env["GIT_COMMITTER_DATE"] = date
    _git(repo, "add", "-A", env=env)
    _git(repo, "commit", "-q", "-m", message, env=env)
    return _git(repo, "rev-parse", "HEAD")


def test_structural_violations():
    # WHY: the gate must FAIL LOUD on two distinct structural defects so
    # a mistagged or half-written tag cannot slip into the living-spec
    # index silently. (a) A test whose @req is not in the namespace is a
    # dangling tag (typo / deleted req); (b) a malformed `# @req:` line
    # never even produced a usable id. Both must surface as violations,
    # and each violation string must name the offending id / line so the
    # author can locate it.
    checker = _load_checker()

    tag_records = [
        {"test": "test_known", "reqs": ["REQ-1"], "invariant_refs": []},
        {"test": "test_dangle", "reqs": ["REQ-UNKNOWN"], "invariant_refs": []},
    ]
    malformed = ["# @req:"]
    namespace = {"REQ-1": "order"}

    violations = checker.find_structural_violations(
        tag_records, malformed, namespace
    )

    # (a) the dangling @req is reported, naming the offending id.
    assert any("REQ-UNKNOWN" in v for v in violations), (
        f"dangling @req must be reported, got: {violations!r}"
    )
    # (b) the malformed line is reported, carrying the raw line.
    assert any("# @req:" in v for v in violations), (
        f"malformed tag must be reported, got: {violations!r}"
    )
    # the resolvable @req (REQ-1) is NOT a violation.
    assert not any("REQ-1" in v for v in violations), (
        f"a resolvable @req must not be flagged, got: {violations!r}"
    )


def test_clean_input_returns_empty():
    # WHY: a clean run (every @req resolves, no malformed lines) must
    # return [] so the gate's __main__ exits 0 — no false positives.
    checker = _load_checker()

    tag_records = [
        {"test": "test_ok", "reqs": ["REQ-1", "REQ-2"], "invariant_refs": []},
    ]
    malformed: list[str] = []
    namespace = {"REQ-1": "order", "REQ-2": "billing"}

    violations = checker.find_structural_violations(
        tag_records, malformed, namespace
    )

    assert violations == [], f"clean input must yield no violations, got: {violations!r}"


def test_index_is_current():
    # WHY: the CI gate must be able to assert that a committed INDEX.md is
    # byte-identical to a fresh `generate_index(...)` (the verify-drift
    # pattern). Anything less than byte-identity — even a stray trailing
    # newline — means the committed file is stale and must fail loud, so
    # the index can never silently drift from its source of truth.
    checker = _load_checker()

    x = "# Living Spec Index\n\n- REQ-1: order\n"

    # identical strings are current.
    assert checker.index_is_current(x, x) is True, (
        "byte-identical strings must be current"
    )
    # a trailing-newline difference is NOT current (byte-identity).
    assert checker.index_is_current(x, x + "\n") is False, (
        "a trailing-newline difference must fail byte-identity"
    )


def test_build_index_renders_tree(tmp_path):
    # WHY: build_index is the single regeneration path the CLI, the
    # finishing step, and the CI verify step all call. It must compose
    # collect_structural_records (anchored @req parsing over the tree),
    # load_namespace (req->capability from docs/loom/spec), and
    # generate_index into one markdown string — so a tagged test under a
    # declared requirement surfaces in the index tree. The output must be
    # byte-equal to driving those three functions by hand over the same
    # tree (no hidden transform).
    import living_spec_collect as LC
    import living_spec_index as LI

    checker = _load_checker()
    repo = _init_repo(tmp_path)

    # A test file carrying a real @req binding.
    (repo / "test_order.py").write_text(
        "def test_places_order():\n"
        "    # @req: REQ-1\n"
        "    assert place() == 1\n",
        encoding="utf-8",
    )
    # A matching spec declaring that requirement under capability `order`.
    spec_dir = repo / "docs" / "loom" / "spec" / "order"
    spec_dir.mkdir(parents=True)
    (spec_dir / "spec.md").write_text(
        "### Requirement: REQ-1\n", encoding="utf-8"
    )
    _commit(repo, "tagged test + spec", date="2026-01-01T00:00:00 +0000")

    index = checker.build_index(repo)

    # The tree renders capability > requirement > test.
    assert "## order" in index
    assert "### REQ-1" in index
    assert "- test_places_order" in index

    # Byte-equal to driving the three composed functions by hand.
    expected = LI.generate_index(
        LC.collect_structural_records(repo),
        LI.load_namespace(repo / "docs" / "loom" / "spec"),
    )
    assert index == expected


def test_run_drift_lane_emits_warn_and_exits_zero(tmp_path, capsys):
    # WHY: the WARN lane composes the three upstream modules
    # (collect -> resolve -> drift) over a real source tree, and a drifted
    # binding must SURFACE as advice WITHOUT failing the build — a WARN is
    # informational, never a gate failure, and must never touch the
    # structural FAIL list. This is the end-to-end seam: collect a tagged
    # test, resolve its body/binding commits, detect body-after-binding
    # drift, print to stderr, and STILL exit 0.
    checker = _load_checker()
    repo = _init_repo(tmp_path)
    src = repo / "test_thing.py"
    # binding_line = 2 (@req), body assertion = line 3 (edited later).
    src.write_text(
        "def test_thing():\n"
        "    # @req: REQ-1\n"
        "    assert compute() == 1\n",
        encoding="utf-8",
    )
    _commit(repo, "initial", date="2026-01-01T00:00:00 +0000")
    # Later commit touches ONLY the body line => body_ts > binding_ts.
    src.write_text(
        "def test_thing():\n"
        "    # @req: REQ-1\n"
        "    assert compute() == 2\n",
        encoding="utf-8",
    )
    _commit(repo, "tweak body", date="2026-02-01T00:00:00 +0000")

    # (1) run_drift_lane returns a non-empty WARN list for the drift.
    warns = checker.run_drift_lane(repo)
    assert warns, f"drifted tagged test must yield a WARN, got: {warns!r}"
    assert any("test_thing" in w for w in warns)

    # (2) main over that root prints the WARN to stderr and returns 0
    # EVEN THOUGH a WARN exists — a WARN never fails the build.
    rc = checker.main([str(repo)])
    assert rc == 0, f"a WARN must not fail the build, got rc={rc!r}"
    captured = capsys.readouterr()
    assert "test_thing" in captured.err, (
        f"WARN must be printed to stderr, got: {captured.err!r}"
    )


def test_run_drift_lane_no_drift_is_silent(tmp_path, capsys):
    # WHY: a clean tree (no body-after-binding drift) must yield [] and a
    # silent, exit-0 main — no false-positive WARNs on stderr.
    checker = _load_checker()
    repo = _init_repo(tmp_path)
    src = repo / "test_thing.py"
    src.write_text(
        "def test_thing():\n"
        "    # @req: REQ-1\n"
        "    assert compute() == 1\n",
        encoding="utf-8",
    )
    _commit(repo, "initial", date="2026-01-01T00:00:00 +0000")

    assert checker.run_drift_lane(repo) == [], "no drift must yield []"

    rc = checker.main([str(repo)])
    assert rc == 0
    captured = capsys.readouterr()
    assert "WARN" not in captured.err, (
        f"a clean tree must emit no WARN, got: {captured.err!r}"
    )


def test_main_structural_lane_fails_on_real_dangling_req(tmp_path, capsys):
    # WHY: main()'s structural lane must read the REAL repo, not an empty
    # stub. A committed test whose `@req: REQ-NOPE` is absent from the
    # namespace declared under docs/loom/spec is a DANGLING binding — the
    # gate must FAIL LOUD (rc=1) and name the offending id on stderr, so a
    # mistagged test cannot slip into the index. Against the empty-inputs
    # stub this test FAILS (the stub ignores real input and returns 0);
    # wiring collect_structural_records / collect_malformed / load_namespace
    # into main() makes it pass.
    checker = _load_checker()
    repo = _init_repo(tmp_path)

    (repo / "test_order.py").write_text(
        "def test_x():\n"
        "    # @req: REQ-NOPE\n"
        "    assert True\n",
        encoding="utf-8",
    )
    spec_dir = repo / "docs" / "loom" / "spec" / "order"
    spec_dir.mkdir(parents=True)
    (spec_dir / "spec.md").write_text(
        "### Requirement: REQ-1\n", encoding="utf-8"
    )
    _commit(repo, "dangling tagged test + spec", date="2026-01-01T00:00:00 +0000")

    rc = checker.main([str(repo)])
    assert rc == 1, (
        f"a real dangling @req must fail the structural lane, got rc={rc!r}"
    )
    captured = capsys.readouterr()
    assert "REQ-NOPE" in captured.err, (
        f"the dangling @req id must be named on stderr, got: {captured.err!r}"
    )


def test_main_structural_lane_passes_on_resolvable_req(tmp_path, capsys):
    # WHY: the structural lane must NOT false-positive. A committed test
    # whose `@req: REQ-1` IS declared in the namespace is structurally
    # clean — main() must print the OK line and return 0.
    checker = _load_checker()
    repo = _init_repo(tmp_path)

    (repo / "test_order.py").write_text(
        "def test_x():\n"
        "    # @req: REQ-1\n"
        "    assert True\n",
        encoding="utf-8",
    )
    spec_dir = repo / "docs" / "loom" / "spec" / "order"
    spec_dir.mkdir(parents=True)
    (spec_dir / "spec.md").write_text(
        "### Requirement: REQ-1\n", encoding="utf-8"
    )
    _commit(repo, "resolvable tagged test + spec", date="2026-01-01T00:00:00 +0000")

    rc = checker.main([str(repo)])
    assert rc == 0, (
        f"a resolvable @req must not fail the structural lane, got rc={rc!r}"
    )


def test_uncommitted_tagged_test_is_skipped_not_fatal(tmp_path, capsys):
    # WHY: the WARN lane must ALWAYS exit 0 and NEVER pre-empt the
    # structural FAIL lane. A net-new @req-tagged test in the WORKING
    # TREE (the everyday local pre-commit workflow) has no committed
    # history, so `git log -L` exits 128. That binding has no committed
    # baseline => it cannot be drift; it must be SKIPPED, not crash the
    # lane. Here a committed+drifted test coexists with an uncommitted
    # tagged test: run_drift_lane must surface the drifted one WITHOUT
    # raising, and main must still return 0 with no traceback.
    checker = _load_checker()
    repo = _init_repo(tmp_path)

    # A committed tagged test that later drifts (body edited after @req).
    drifted = repo / "test_drift.py"
    drifted.write_text(
        "def test_drift():\n"
        "    # @req: REQ-1\n"
        "    assert compute() == 1\n",
        encoding="utf-8",
    )
    _commit(repo, "initial", date="2026-01-01T00:00:00 +0000")
    drifted.write_text(
        "def test_drift():\n"
        "    # @req: REQ-1\n"
        "    assert compute() == 2\n",
        encoding="utf-8",
    )
    _commit(repo, "tweak body", date="2026-02-01T00:00:00 +0000")

    # A NEW tagged test in the working tree, NEVER committed.
    uncommitted = repo / "test_new.py"
    uncommitted.write_text(
        "def test_new():\n"
        "    # @req: REQ-2\n"
        "    assert compute() == 2\n",
        encoding="utf-8",
    )

    # (1) run_drift_lane must NOT raise on the uncommitted binding; it
    # surfaces the committed-drift WARN and skips the uncommitted one.
    warns = checker.run_drift_lane(repo)
    assert any("test_drift" in w for w in warns), (
        f"the committed drift must still surface, got: {warns!r}"
    )
    assert not any("test_new" in w for w in warns), (
        f"the uncommitted test has no baseline => no WARN, got: {warns!r}"
    )

    # (2) main must return 0 (WARN lane never fails the build) and the
    # uncommitted test must not crash it with a traceback.
    rc = checker.main([str(repo)])
    assert rc == 0, f"a WARN/skip must not fail the build, got rc={rc!r}"
