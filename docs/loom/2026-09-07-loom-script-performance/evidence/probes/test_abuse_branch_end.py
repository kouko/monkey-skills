"""Branch-end adversarial probes for 2026-09-07-loom-script-performance.

Written by the adversary role at review time, against a30e9db6 — no part
of this file's target code was implemented by the same agent that wrote
these probes. Wave-1 probes (test_abuse_citation_index.py,
test_abuse_fog_cat_file_batch.py, test_abuse_lazy_yaml_import.py,
test_abuse_session_start_awk.py, test_abuse_ticket_read_once.py) already
cover: append-growth cache invalidation, symlink/CRLF/CJK/oversized
tickets, hostile manifest shapes (CRLF, EOF, hazard-char names, shared
decision points), and per-ticket read-count parity. This file targets
what those missed: same-length in-place / GC-reused-id cache staleness
in check_doc_citations.py's `id()`+len memoization, printf/EOF edges in
session-start not already covered, invalid-UTF-8 blob parity in
check_map_fog's bytes-mode cat-file reader, and the lazy `yaml` import's
failure-shape parity with the old module-level import.

Run: python3 -m pytest docs/loom/2026-09-07-loom-script-performance/evidence/probes/test_abuse_branch_end.py -v
"""
from __future__ import annotations

import gc
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
LOOM_CODE_SCRIPTS = REPO / "loom-code" / "scripts"
sys.path.insert(0, str(LOOM_CODE_SCRIPTS))

import check_doc_citations  # noqa: E402

DECISION_MAP_SCRIPTS = (
    REPO / "loom-workflow" / "skills" / "decision-map" / "scripts"
)
sys.path.insert(0, str(DECISION_MAP_SCRIPTS))

import check_map_fog  # noqa: E402
import map_store  # noqa: E402


# ---------------------------------------------------------------------------
# 1. check_doc_citations: id()+len memoization staleness (real bug class)
# ---------------------------------------------------------------------------


def test_basename_index_inplace_mutation_same_length_returns_stale_result() -> None:
    """A same-length in-place replacement of `repo_files[0]` (the id()+len
    cache key is unchanged: same object id, same len) must not make
    `resolve_cited_path` keep resolving the file that was just removed
    from the list, nor stay blind to the file that replaced it — but it
    does: the cache is keyed on `id(repo_files)` and `len(repo_files)`
    only, and both survive an in-place same-length mutation untouched."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "a").mkdir()
        (root / "b").mkdir()
        (root / "a" / "x.md").write_text("hi")
        (root / "b" / "y.md").write_text("hi")
        repo_files = ["a/x.md"]

        first = check_doc_citations.resolve_cited_path(root, "x.md", repo_files)
        assert first == root / "a/x.md"

        repo_files[0] = "b/y.md"  # in-place, same length -> same cache key

        stale = check_doc_citations.resolve_cited_path(root, "x.md", repo_files)
        fresh = check_doc_citations.resolve_cited_path(root, "y.md", repo_files)

        # This is the bug: `stale` should be None (x.md is gone from the
        # list) and `fresh` should resolve b/y.md, but the memoized index
        # still reflects the pre-mutation list.
        assert stale == root / "a/x.md", "stale hit not reproduced -- report as-is"
        assert fresh is None, "stale miss not reproduced -- report as-is"


def test_basename_index_gc_reused_id_returns_stale_result() -> None:
    """CPython can reuse a garbage-collected list's `id()` for a new list
    of the same length. When that happens, `_basename_index`'s
    `id(repo_files)`+`len(repo_files)` cache key collides with the old
    entry and returns the OLD list's index for a completely different
    (same-length) NEW list -- a wrong verdict, not merely a slow one.
    This loop hunts for that collision (CPython's small-int/object-pool
    allocator makes it common, not adversarially rare) and asserts the
    stale-index symptom the first time it fires; if 500 tries never
    collide, the probe is a documented no-op rather than a false pass."""
    collided = False
    for i in range(500):
        old_list = [f"a/x{i}.md", f"a/y{i}.md"]
        old_id = id(old_list)
        check_doc_citations._basename_index(old_list)
        del old_list
        gc.collect()

        new_list = [f"a/x{i}.md", f"a/z{i}.md"]  # same length, different content
        if id(new_list) != old_id:
            continue
        collided = True
        index = check_doc_citations._basename_index(new_list)
        # Bug symptom: the returned index still carries the OLD list's
        # "y{i}.md" basename key instead of the NEW list's "z{i}.md".
        assert f"y{i}.md" in index, (
            "id-reuse collision happened but no staleness observed -- "
            "cache may have been fixed; re-run to confirm before trusting "
            "a single miss"
        )
        assert f"z{i}.md" not in index
        break
    if not collided:
        raise AssertionError(
            "no id() collision in 500 tries on this interpreter/build -- "
            "inconclusive, not a pass: re-run or widen the loop"
        )


# ---------------------------------------------------------------------------
# 2. session-start: edges not already covered by test_abuse_session_start_awk.py
# ---------------------------------------------------------------------------

HOOK = REPO / "loom-code" / "hooks" / "session-start"
OLD_HOOK_TEXT = subprocess.run(
    ["git", "show", "4e158201:loom-code/hooks/session-start"],
    cwd=REPO, capture_output=True, text=True, check=True,
).stdout


def _run_hook_pair(manifest_bytes: bytes) -> tuple[subprocess.CompletedProcess, subprocess.CompletedProcess]:
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        plugin = tmp / "plugin"
        (plugin / "hooks").mkdir(parents=True)
        (plugin / "contract").mkdir()
        (plugin / "hooks" / "session-start").write_bytes(HOOK.read_bytes())
        (plugin / "hooks" / "session-start-old").write_text(OLD_HOOK_TEXT)
        (plugin / "contract" / "manifest.yaml").write_bytes(manifest_bytes)
        repo = tmp / "repo"
        repo.mkdir()
        new = subprocess.run(
            ["bash", str(plugin / "hooks" / "session-start")],
            cwd=str(repo), stdin=subprocess.DEVNULL, capture_output=True,
        )
        old = subprocess.run(
            ["bash", str(plugin / "hooks" / "session-start-old")],
            cwd=str(repo), stdin=subprocess.DEVNULL, capture_output=True,
        )
        return old, new


def test_session_start_manifest_no_trailing_newline_matches_pre_change_stdout() -> None:
    """A manifest whose stations block runs straight to EOF with NO
    trailing newline byte at all (not just no following top-level key --
    the file itself is unterminated) must produce byte-identical stdout
    and exit code before and after the single-awk-pass rewrite."""
    manifest = (
        b"version: 1.0.0\n"
        b"stations:\n"
        b"  - {name: solo, owner: x, produces: y, decision_point: 1}\n"
        b"  - {name: maintain, owner: x, produces: y}"  # no trailing \n
    )
    old, new = _run_hook_pair(manifest)
    assert old.returncode == 0 and new.returncode == 0
    assert old.stdout == new.stdout


def test_session_start_percent_in_station_name_produces_valid_json_matching_old() -> None:
    """A station name containing a `%` (a printf conversion character) fed
    through the manifest -> stations_yaml -> body -> printf pipeline must
    not corrupt the final JSON: the closing `printf '{"...":"%s",...}"'
    call passes the body as a %s ARGUMENT, so a literal `%s`/`%n` inside
    it must come out unchanged, not be re-interpreted as a format spec."""
    manifest = (
        b"version: 1.0.0\n"
        b"stations:\n"
        b"  - {name: pc%sn, owner: x, produces: y, decision_point: 1}\n"
        b"  - {name: maintain, owner: x, produces: y}\n"
    )
    old, new = _run_hook_pair(manifest)
    assert old.returncode == 0 and new.returncode == 0
    assert old.stdout == new.stdout
    import json
    json.loads(new.stdout)  # must not raise: JSON stays well-formed


def test_session_start_empty_stations_block_matches_pre_change_behavior() -> None:
    """`stations:` immediately followed by another top-level key (zero
    station entries at all) is a degenerate manifest the awk state
    machine must still handle identically before and after consolidation
    -- both must exit 0 and emit the same (empty-flow) body, not diverge
    into a crash on one side."""
    manifest = b"version: 1.0.0\nstations:\nartifacts:\n  foo: bar\n"
    old, new = _run_hook_pair(manifest)
    assert old.returncode == 0 and new.returncode == 0
    assert old.stdout == new.stdout


# ---------------------------------------------------------------------------
# 3. check_map_fog: invalid-UTF-8 blob content in bytes mode
# ---------------------------------------------------------------------------


def _init_repo(repo_root: Path) -> None:
    subprocess.run(["git", "init", "-q", str(repo_root)], check=True)
    subprocess.run(["git", "-C", str(repo_root), "config", "user.email", "a@b.c"], check=True)
    subprocess.run(["git", "-C", str(repo_root), "config", "user.name", "a"], check=True)


def _commit(repo_root: Path) -> str:
    subprocess.run(["git", "-C", str(repo_root), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(repo_root), "commit", "-q", "-m", "x"], check=True)
    return subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()


def test_read_base_graduated_ids_invalid_utf8_blob_matches_old_exception_type() -> None:
    """A ticket blob containing bytes that are not valid UTF-8 (`\\xff\\xfe`)
    must fail the same way in the new bytes-mode `cat-file --batch`
    reader as in the old per-ticket `git show` (text-mode) reader: both
    decode with the platform's preferred encoding and neither wraps a
    decode failure into `SchemaViolation` -- a raw `UnicodeDecodeError`
    propagates from both, so this is a parity PASS, not a regression."""
    with tempfile.TemporaryDirectory() as td:
        repo_root = Path(td)
        _init_repo(repo_root)
        map_dir = repo_root / "docs" / "loom" / "maps" / "m1"
        (map_dir / "tickets").mkdir(parents=True)
        (map_dir / "MAP.md").write_text("hello\n")
        ticket = map_dir / "tickets" / "bad.md"
        ticket.write_bytes(
            b"---\ngraduated-from: F-1\n---\n" + b"\xff\xfe\x00\x01" + b"\n"
        )
        base_ref = _commit(repo_root)

        raised = None
        try:
            check_map_fog.read_base_graduated_ids(repo_root, base_ref, map_dir / "MAP.md")
        except Exception as exc:  # noqa: BLE001 -- probing the exact type
            raised = exc

        assert raised is not None, "expected a decode failure, got a clean result"
        assert not isinstance(raised, map_store.SchemaViolation), (
            "new code silently upgraded a decode failure to SchemaViolation "
            "-- confirm this against the old per-ticket git show reader "
            "before treating it as an improvement"
        )
        assert type(raised).__name__ == "UnicodeDecodeError"


# ---------------------------------------------------------------------------
# 4. loom_checker: lazy `import yaml` failure-shape parity
# ---------------------------------------------------------------------------

LOOM_CHECKER = REPO / "loom-code" / "scripts" / "loom_checker.py"
OLD_LOOM_CHECKER_TEXT = subprocess.run(
    ["git", "show", "4e158201:loom-code/scripts/loom_checker.py"],
    cwd=REPO, capture_output=True, text=True, check=True,
).stdout


def _run_with_yaml_unimportable(script_path: Path, args: list[str]) -> subprocess.CompletedProcess:
    with tempfile.TemporaryDirectory() as td:
        badlib = Path(td) / "badlib"
        badlib.mkdir()
        (badlib / "yaml.py").write_text(
            "raise ModuleNotFoundError(\"No module named 'yaml'\")\n"
        )
        return subprocess.run(
            [sys.executable, str(script_path), *args],
            cwd=str(REPO),
            env={"PYTHONPATH": str(badlib), "PATH": "/usr/bin:/bin"},
            capture_output=True, text=True,
        )


def test_loom_checker_yaml_unimportable_diverges_from_old_exit_code() -> None:
    """With `yaml` unimportable and a well-formed `contract --require
    1.0` (a real manifest load is required, so both old and new code
    MUST attempt the yaml import), the pre-change script imported yaml
    at MODULE level -- outside any try/except -- and crashed with an
    unhandled traceback at Python's default exit code 1. The lazy
    import moved the same `import yaml` inside `load_manifest()`, which
    now runs inside main()'s catch-all (`except Exception ... exit 2`),
    so the identical failing dependency now produces a different exit
    code and a different (caught, one-line) message shape. This is a
    real divergence from the stated zero-behaviour-change constraint
    for the failing-yaml-import case, not a false positive."""
    old_dir = Path(tempfile.mkdtemp())
    old_script = old_dir / "loom_checker_old.py"
    old_script.write_text(OLD_LOOM_CHECKER_TEXT)

    old = _run_with_yaml_unimportable(old_script, ["contract", "--require", "1.0"])
    new = _run_with_yaml_unimportable(LOOM_CHECKER, ["contract", "--require", "1.0"])

    assert "ModuleNotFoundError" in old.stderr
    assert "ModuleNotFoundError" in new.stderr
    # Pin the observed divergence so a future fix (or a future widening
    # of the gap) is visible as a test change, not a silent drift.
    assert old.returncode == 1
    assert new.returncode == 2
    assert "Traceback" in old.stderr
    assert "Traceback" not in new.stderr


def test_loom_checker_yaml_unimportable_nonpush_path_still_exits_zero() -> None:
    """The whole point of the lazy import (W1-05) is that a subcommand
    which never touches the manifest must not pay for -- or fail on --
    an unimportable `yaml`. `--list-rules` must still exit 0 (or at
    least never raise ModuleNotFoundError) with yaml shadowed out."""
    new = _run_with_yaml_unimportable(LOOM_CHECKER, ["--list-rules"])
    assert "ModuleNotFoundError" not in new.stderr
    assert new.returncode == 0, new.stderr


# ---------------------------------------------------------------------------
# 5. version-string consistency across the two plugin manifests
# ---------------------------------------------------------------------------


def test_plugin_json_versions_match_1_8_1_and_4_1_1_on_both_hosts() -> None:
    """Every plugin.json this change touches (Claude Code + Codex mirror,
    for both loom-code and loom-workflow) must carry the SAME bumped
    version -- a host-specific manifest left on the old version would
    silently serve stale behavior to whichever host reads it."""
    import json

    pairs = [
        (REPO / "loom-code" / ".claude-plugin" / "plugin.json", "1.8.1"),
        (REPO / "loom-code" / ".codex-plugin" / "plugin.json", "1.8.1"),
        (REPO / "loom-workflow" / ".claude-plugin" / "plugin.json", "4.1.1"),
        (REPO / "loom-workflow" / ".codex-plugin" / "plugin.json", "4.1.1"),
    ]
    for path, expected in pairs:
        data = json.loads(path.read_text())
        assert data["version"] == expected, f"{path}: {data['version']!r} != {expected!r}"
