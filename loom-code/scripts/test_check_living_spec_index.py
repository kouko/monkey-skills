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


def _declare_reqs(repo: Path, capability: str, *req_ids: str) -> None:
    """Declare ``req_ids`` under ``docs/loom/spec/<capability>/spec.md``.

    Keeps the namespace non-empty so the structural FAIL lane sees these
    ``@req``s as resolvable — the WARN-lane fixtures exercise drift, not
    dangling tags, so their tagged tests must resolve to stay rc=0.
    """
    spec_dir = repo / "docs" / "loom" / "spec" / capability
    spec_dir.mkdir(parents=True, exist_ok=True)
    body = "".join(f"### Requirement: {r}\n" for r in req_ids)
    (spec_dir / "spec.md").write_text(body, encoding="utf-8")


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


def test_active_coverage():
    # WHY: the hermetic coverage check must enforce the living-spec
    # contract two ways at once. (a) An ACTIVE req with ZERO linked
    # passing tests is an UNCOVERED promise — the gate must surface it as
    # a violation so an active requirement can never sit unverified. (b) A
    # DEFERRED req with zero tests is INTENTIONALLY inspirational, not a
    # defect — it must surface only as advisory (separate list), never as
    # a violation. And a req that HAS ≥1 linked test is covered regardless
    # of status, so it appears in neither list. The function inverts
    # tag_records to req->tests, then partitions namespace reqs by status
    # and link-count.
    checker = _load_checker()

    tag_records = [
        {"test": "t1", "reqs": ["REQ-1"], "invariant_refs": []},
    ]
    namespace = {"REQ-1": "o", "REQ-2": "o", "REQ-3": "o"}
    statuses = {"REQ-2": "deferred", "REQ-3": "active"}
    # REQ-1 defaults active and IS linked (t1) -> neither list.
    # REQ-2 deferred, 0 tests -> surfaced only.
    # REQ-3 active, 0 tests -> violation only.

    violations, surfaced = checker.active_coverage(
        tag_records, namespace, statuses
    )

    # (a) the active+uncovered req IS a violation, naming the id.
    assert any("REQ-3" in v for v in violations), (
        f"active req with 0 tests must be a violation, got: {violations!r}"
    )
    # the linked active req (REQ-1) is NOT a violation.
    assert not any("REQ-1" in v for v in violations), (
        f"a linked active req must not be flagged, got: {violations!r}"
    )
    # the deferred req is NOT a violation (it is inspirational).
    assert not any("REQ-2" in v for v in violations), (
        f"a deferred req must not be a violation, got: {violations!r}"
    )

    # (b) the deferred+uncovered req IS surfaced (advisory).
    assert any("REQ-2" in s for s in surfaced), (
        f"deferred req with 0 tests must be surfaced, got: {surfaced!r}"
    )
    # the active req (REQ-3) is NOT in the advisory list.
    assert not any("REQ-3" in s for s in surfaced), (
        f"an active req must not be in the advisory list, got: {surfaced!r}"
    )
    # the linked req (REQ-1) is NOT surfaced.
    assert not any("REQ-1" in s for s in surfaced), (
        f"a linked req must not be surfaced, got: {surfaced!r}"
    )


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
    # Declare REQ-1 so the structural lane stays clean — this fixture
    # exercises the WARN (drift) lane, not a dangling tag.
    _declare_reqs(repo, "order", "REQ-1")
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
    _declare_reqs(repo, "order", "REQ-1")
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


def test_verify_index_mode_fails_on_stale(tmp_path):
    # WHY: the merge-boundary stale-index gate. `--verify-index <path>`
    # regenerates the index from the source tree and asserts byte-identity
    # against the committed file. A committed INDEX.md whose bytes differ
    # from a fresh `build_index` is STALE and must FAIL LOUD (rc=1) so a
    # drifted generated file can never sneak through merge. Against the
    # pre-implementation main() the `--verify-index` flag is unrecognized:
    # argv[0] == "--verify-index" is treated as the source-tree path, which
    # does not exist as a repo => the run does NOT return 1-for-stale-index
    # (it returns 0 or crashes on a bogus root), so this test fails until
    # the mode is wired.
    checker = _load_checker()
    repo = _init_repo(tmp_path)

    # A committed tagged test + matching spec so build_index renders a
    # non-trivial tree (the committed file below is deliberately WRONG).
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
    index_path = repo / "docs" / "loom" / "INDEX.md"
    # A STALE committed index: bytes that differ from a fresh build_index.
    index_path.write_text("# stale — does not match source\n", encoding="utf-8")
    _commit(repo, "tagged test + spec + stale index", date="2026-01-01T00:00:00 +0000")

    # Sanity: the committed file really is stale vs a fresh regeneration.
    assert index_path.read_text(encoding="utf-8") != checker.build_index(repo)

    rc = checker.main(["--verify-index", str(index_path), str(repo)])
    assert rc == 1, (
        f"a stale committed INDEX.md must fail --verify-index, got rc={rc!r}"
    )


def test_write_then_verify_index_round_trips(tmp_path):
    # WHY: `--write-index <path>` regenerates and WRITES the file;
    # `--verify-index <path>` over the same tree must then PASS (rc=0) —
    # the write/verify round-trip is the contract that lets the finishing
    # step regenerate and the CI gate verify against one shared
    # build_index path. A write that verify then rejects would mean the two
    # modes disagree on the canonical bytes.
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
    _commit(repo, "tagged test + spec", date="2026-01-01T00:00:00 +0000")

    index_path = repo / "docs" / "loom" / "INDEX.md"

    # write-index regenerates and writes the file...
    wrc = checker.main(["--write-index", str(index_path), str(repo)])
    assert wrc == 0, f"--write-index must return 0, got rc={wrc!r}"
    assert index_path.read_text(encoding="utf-8") == checker.build_index(repo), (
        "--write-index must write exactly build_index(root)"
    )

    # ...and verify-index over the same tree then passes byte-identity.
    vrc = checker.main(["--verify-index", str(index_path), str(repo)])
    assert vrc == 0, (
        f"--verify-index must pass on a freshly written index, got rc={vrc!r}"
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
    # Declare both reqs (REQ-1 for the committed drift, REQ-2 for the
    # uncommitted working-tree test) so the structural lane stays clean
    # and rc=0 reflects only the WARN/skip behavior under test.
    _declare_reqs(repo, "order", "REQ-1", "REQ-2")
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


# Repo root = three parents up from this test file:
#   .../loom-dogfood/loom-code/scripts/test_check_living_spec_index.py
#   parents[0] scripts  parents[1] loom-code  parents[2] loom-dogfood (root)
# The root is the source tree that contains the committed docs/loom/INDEX.md.
_REPO_ROOT = Path(__file__).resolve().parents[2]


def test_committed_index_is_current():
    # WHY: docs/loom/INDEX.md is the AUTHORED-vs-DERIVED anchor the CI
    # verify step checks against. If anyone changes what build_index
    # produces (a collector, namespace loader, or renderer tweak) without
    # regenerating the committed file, the committed index silently drifts
    # from its source of truth. This guard recomputes build_index over the
    # REAL repo root and asserts byte-identity with the committed file via
    # index_is_current — failing loud the moment the two diverge.
    checker = _load_checker()

    committed = (_REPO_ROOT / "docs" / "loom" / "INDEX.md").read_text(
        encoding="utf-8"
    )
    regenerated = checker.build_index(_REPO_ROOT)

    assert checker.index_is_current(committed, regenerated), (
        "committed docs/loom/INDEX.md is stale vs a fresh build_index over "
        "the repo root; regenerate it with "
        "`check-living-spec-index.py --write-index docs/loom/INDEX.md <root>`"
    )
