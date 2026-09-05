"""Adversarial probes for wave-end:0 of
2026-09-05-artifact-charter-boundaries-and-edit-rights -- attacking states
the up-front adversary's `test_abuse_charter.py` did not cover: a manifest
whose `artifacts:` is missing or the wrong container shape, `goes_to`
matching by exact string only, `signoff` naming a tool instead of a
station, markdown injection through cell text, `--manifest` naming a
directory or an empty file, the mixed gap+good-row exit code, the Codex
mirror rendering identically to the plugin checker, the `charter` rule id
and `--list-rules` count, `contract --require` after the manifest grew,
and the W3-02 repair to `test_probes_complexity_wave_end.py` (the
confirmation-commit-unreachable skip).

Each test is independently re-runnable:
    python3 -m pytest docs/loom/2026-09-05-artifact-charter-boundaries-and-edit-rights/evidence/probes/test_abuse_charter_wave_end.py -q

from the repo root.
"""
from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
import yaml

from _pytest.outcomes import Skipped

REPO = Path(
    subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
)

CHECKER = REPO / "loom-code" / "scripts" / "loom_checker.py"
CODEX_CHECKER = REPO / ".codex" / "hooks" / "loom_checker.py"
PLUGIN_MANIFEST = REPO / "loom-code" / "contract" / "manifest.yaml"
COMPLEXITY_PROBE_MODULE = (
    REPO / "loom-code" / "scripts" / "test_probes_complexity_wave_end.py"
)


def _run_charter(manifest_path, cwd=REPO) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECKER), "charter", "--manifest", str(manifest_path)],
        cwd=str(cwd), capture_output=True, text=True,
    )


def _run(*args, cwd=REPO) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECKER), *args],
        cwd=str(cwd), capture_output=True, text=True,
    )


BASE_TWO_ARTIFACT_MANIFEST = {
    "version": "1.0.0",
    "stations": [{"name": "build"}],
    "artifacts": {
        "intent": {
            "charter": {
                "answers": "x",
                "readers": ["a"],
                "must": ["a"],
                "must_not": [{"kind": "z", "goes_to": "spec"}],
                "signoff": "build",
                "edits_after": ["c"],
            }
        },
        "spec": {
            "charter": {
                "answers": "y",
                "readers": ["a"],
                "must": ["b"],
                "must_not": [{"kind": "z", "goes_to": "intent"}],
                "signoff": "build",
                "edits_after": ["c"],
            }
        },
    },
}


def _write_yaml(tmp_path: Path, doc: dict, name: str = "manifest.yaml") -> Path:
    path = tmp_path / name
    path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# `artifacts:` missing entirely, or present with the wrong container shape.
# ---------------------------------------------------------------------------

def test_charter_command_artifacts_key_absent_blocked(tmp_path: Path) -> None:
    """A manifest that carries no `artifacts:` key at all is not a manifest
    that should ever be reported healthy -- `cmd_charter` now checks
    `manifest.get("artifacts")` for falsiness (covering both an absent key
    and an explicit empty mapping) before the row loop, appends a
    `contract.charter-complete` failure naming the gap, renders an empty
    table, and exits 1. Fixed for wave-end:0-01 -- this used to exit 0
    vacuously; it must never again."""
    manifest_path = _write_yaml(tmp_path, {"version": "1.0.0", "stations": []})
    result = _run_charter(manifest_path)
    assert result.returncode == 1, (
        f"expected the missing-artifacts manifest to be blocked (exit 1); "
        f"got {result.returncode}: stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "| artifact |" in result.stdout
    assert "contract.charter-complete" in result.stderr
    assert "no artifacts" in result.stderr or "artifacts" in result.stderr


def test_charter_command_artifacts_empty_mapping_blocked(tmp_path: Path) -> None:
    """The sibling of the absent-key case: `artifacts:` present but an
    explicit empty mapping (`{}`) collapses to the same falsy state and
    must be blocked identically -- not silently accepted as zero rows to
    check."""
    manifest_path = _write_yaml(tmp_path, {"version": "1.0.0", "stations": [], "artifacts": {}})
    result = _run_charter(manifest_path)
    assert result.returncode == 1, (
        f"expected the empty-artifacts manifest to be blocked (exit 1); "
        f"got {result.returncode}: stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "contract.charter-complete" in result.stderr


def test_charter_command_artifacts_as_list_fails_closed(tmp_path: Path) -> None:
    """The opposite shape error -- `artifacts:` present but a YAML sequence
    instead of a mapping -- is NOT silently accepted: `.keys()` on a list
    raises AttributeError, caught by `main`'s blanket except, and reported
    as an internal error at exit 2. Fail-closed, unlike the absent-key
    case above."""
    manifest_path = tmp_path / "manifest.yaml"
    manifest_path.write_text("version: 1.0.0\nstations: []\nartifacts:\n  - foo\n  - bar\n", encoding="utf-8")
    result = _run_charter(manifest_path)
    assert result.returncode == 2, (
        f"expected exit 2 (fail-closed) for a list-shaped artifacts:, got "
        f"{result.returncode}: stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "internal error" in result.stderr


# ---------------------------------------------------------------------------
# `goes_to` string matching, and `signoff` naming a tool.
# ---------------------------------------------------------------------------

def test_charter_row_goes_to_case_and_whitespace_mismatch_blocked(tmp_path: Path) -> None:
    """`goes_to` is matched by exact string membership against
    `all_names` -- there is no case-folding or whitespace-trimming before
    the comparison. `' Spec '` (leading/trailing space, capitalised) does
    NOT resolve to the real artifact `spec`, so this is correctly blocked
    as naming an artifact absent from the table -- confirming the checker
    is strict rather than permissively case-insensitive."""
    doc = {
        "version": "1.0.0",
        "stations": [{"name": "build"}],
        "artifacts": {
            "intent": {
                "charter": {
                    "answers": "x", "readers": ["a"], "must": ["a"],
                    "must_not": [{"kind": "z", "goes_to": " Spec "}],
                    "signoff": "build", "edits_after": ["c"],
                }
            },
            "spec": {
                "charter": {
                    "answers": "y", "readers": ["a"], "must": ["b"],
                    "must_not": [{"kind": "z", "goes_to": "intent"}],
                    "signoff": "build", "edits_after": ["c"],
                }
            },
        },
    }
    manifest_path = _write_yaml(tmp_path, doc)
    result = _run_charter(manifest_path)
    assert result.returncode == 1
    assert "names an artifact absent from the table" in result.stderr
    assert "' Spec '" in result.stderr or "'Spec '" in result.stderr or "Spec" in result.stderr


def test_charter_row_signoff_names_tool_not_station_blocked(tmp_path: Path) -> None:
    """A `signoff` naming a real entry in `tools:` (not `stations:`) is
    rejected -- `stations` is built only from `manifest.get("stations",
    [])`, so a tool name never satisfies membership even though it is a
    legitimate manifest concept elsewhere."""
    doc = {
        "version": "1.0.0",
        "stations": [{"name": "build"}],
        "tools": [{"name": "git-memory"}],
        "artifacts": {
            "intent": {
                "charter": {
                    "answers": "x", "readers": ["a"], "must": ["a"],
                    "must_not": [{"kind": "z", "goes_to": "spec"}],
                    "signoff": "git-memory",
                    "edits_after": ["c"],
                }
            },
            "spec": {
                "charter": {
                    "answers": "y", "readers": ["a"], "must": ["b"],
                    "must_not": [{"kind": "z", "goes_to": "intent"}],
                    "signoff": "build", "edits_after": ["c"],
                }
            },
        },
    }
    manifest_path = _write_yaml(tmp_path, doc)
    result = _run_charter(manifest_path)
    assert result.returncode == 1
    assert "signoff names unknown station 'git-memory'" in result.stderr


# ---------------------------------------------------------------------------
# Markdown injection through cell text.
# ---------------------------------------------------------------------------

def test_render_charter_table_pipe_and_newline_in_cell_corrupts_row(tmp_path: Path) -> None:
    """Neither `_charter_join` nor `render_charter_table` escapes `|` or
    `\\n` in a cell's source text -- a `must` or `must_not.kind` string
    carrying either character is written straight into the markdown row,
    which then renders as MORE table cells and MORE table rows than the
    manifest actually declares (a markdown-injection shape), and the
    command still exits 0 because nothing about this trips
    `contract.charter-complete`'s own checks (they only look at emptiness
    and membership, never at cell content shape)."""
    doc = {
        "version": "1.0.0",
        "stations": [{"name": "build"}],
        "artifacts": {
            "intent": {
                "charter": {
                    "answers": "x", "readers": ["a"],
                    "must": ["a | injected-cell\nand-a-new-row"],
                    "must_not": [{"kind": "z", "goes_to": "spec"}],
                    "signoff": "build", "edits_after": ["c"],
                }
            },
            "spec": {
                "charter": {
                    "answers": "y", "readers": ["a"], "must": ["b"],
                    "must_not": [{"kind": "z", "goes_to": "intent"}],
                    "signoff": "build", "edits_after": ["c"],
                }
            },
        },
    }
    manifest_path = _write_yaml(tmp_path, doc)
    result = _run_charter(manifest_path)
    assert result.returncode == 0, "the injected content trips no rule at all"
    # A well-formed 2-artifact table is exactly 4 physical lines: header,
    # separator, and one row per artifact. The injected `\n` inside a cell
    # splits the `intent` row across two physical lines, so the total
    # physical-line count exceeds 4 even though only 2 artifacts exist.
    physical_lines = result.stdout.splitlines()
    assert len(physical_lines) > 4, (
        "expected the embedded newline to split the intent row across "
        f"extra physical lines; got exactly {len(physical_lines)} lines:\n"
        f"{result.stdout}"
    )
    # Control: the same manifest with the `|`/`\n` stripped out of the
    # `must` string renders the expected clean 4-line, 6-pipe intent row --
    # so the extra line and the extra pipe above are attributable to the
    # injected characters, not to something else about this manifest shape.
    clean_doc = {**doc}
    clean_doc["artifacts"] = {
        "intent": {
            "charter": {
                **doc["artifacts"]["intent"]["charter"],
                "must": ["a injected-cell and-a-new-row"],
            }
        },
        "spec": doc["artifacts"]["spec"],
    }
    clean_manifest = _write_yaml(tmp_path, clean_doc, name="clean_manifest.yaml")
    clean_result = _run_charter(clean_manifest)
    assert clean_result.returncode == 0
    clean_lines = clean_result.stdout.splitlines()
    assert len(clean_lines) == 4, f"control manifest did not render cleanly: {clean_result.stdout!r}"
    assert clean_lines[0].count("|") == result.stdout.splitlines()[0].count("|"), (
        "control and injected runs must share the same header"
    )


# ---------------------------------------------------------------------------
# `--manifest` naming a directory or an empty file.
# ---------------------------------------------------------------------------

def test_charter_command_manifest_path_is_directory_fails_closed(tmp_path: Path) -> None:
    """A directory at the `--manifest` path is rejected by `is_file()`
    before any YAML parsing is attempted -- exit 2, usage error, never a
    parse crash."""
    directory = tmp_path / "a_directory_manifest.yaml"
    directory.mkdir()
    result = _run_charter(directory)
    assert result.returncode == 2
    assert "no contract manifest at" in result.stderr


def test_charter_command_manifest_path_is_empty_file_fails_closed(tmp_path: Path) -> None:
    """An empty file at `--manifest` parses to `None` via `yaml.safe_load`,
    and `manifest.get(...)` on `None` raises AttributeError -- caught by
    `main`'s blanket except and reported as an internal error at exit 2,
    not silently accepted as a manifest with nothing in it."""
    empty = tmp_path / "empty_manifest.yaml"
    empty.write_text("", encoding="utf-8")
    result = _run_charter(empty)
    assert result.returncode == 2
    assert "internal error" in result.stderr


# ---------------------------------------------------------------------------
# Exit code when both a gap and a good row exist.
# ---------------------------------------------------------------------------

def test_charter_command_mixed_manifest_reports_gap_and_good_row_exit_1(tmp_path: Path) -> None:
    """One broken artifact (empty `must_not`) alongside one complete
    artifact in the same manifest: the command still renders BOTH rows
    (the good one complete, the broken one with an empty cell) and still
    exits 1 -- a single failing row is never masked by a passing
    neighbour, and a passing neighbour is never dragged down to omission."""
    doc = {
        "version": "1.0.0",
        "stations": [{"name": "build"}],
        "artifacts": {
            "intent": {
                "charter": {
                    "answers": "x", "readers": ["a"], "must": ["a"],
                    "must_not": [],
                    "signoff": "build", "edits_after": ["c"],
                }
            },
            "spec": {
                "charter": {
                    "answers": "y", "readers": ["a"], "must": ["b"],
                    "must_not": [{"kind": "z", "goes_to": "intent"}],
                    "signoff": "build", "edits_after": ["c"],
                }
            },
        },
    }
    manifest_path = _write_yaml(tmp_path, doc)
    result = _run_charter(manifest_path)
    assert result.returncode == 1
    assert "intent.must_not is empty" in result.stderr
    assert "| spec | b | z → intent | build | c |" in result.stdout


# ---------------------------------------------------------------------------
# Codex mirror renders the same table as the plugin checker.
# ---------------------------------------------------------------------------

def test_codex_mirror_charter_renders_identical_table_to_plugin_checker() -> None:
    """Running `charter` through the Codex-scaffold copy of the checker
    (`.codex/hooks/loom_checker.py`, with no `--manifest` override so it
    resolves its own sibling `contract/manifest.yaml`) produces byte-
    identical stdout to the plugin checker over this repo's real
    manifest -- the two copies have not drifted apart on this artifact
    type."""
    assert CODEX_CHECKER.is_file(), f"{CODEX_CHECKER} does not exist"
    plugin_result = subprocess.run(
        [sys.executable, str(CHECKER), "charter"],
        cwd=str(REPO), capture_output=True, text=True,
    )
    codex_result = subprocess.run(
        [sys.executable, str(CODEX_CHECKER), "charter"],
        cwd=str(REPO), capture_output=True, text=True,
    )
    assert plugin_result.returncode == codex_result.returncode == 0, (
        f"plugin exit {plugin_result.returncode} ({plugin_result.stderr!r}), "
        f"codex exit {codex_result.returncode} ({codex_result.stderr!r})"
    )
    assert plugin_result.stdout == codex_result.stdout, (
        "plugin and Codex-mirror charter tables differ:\n"
        f"--- plugin ---\n{plugin_result.stdout}\n--- codex ---\n{codex_result.stdout}"
    )


# ---------------------------------------------------------------------------
# `--list-rules` count and the `charter` rule id.
# ---------------------------------------------------------------------------

def test_list_rules_count_is_exactly_28_and_charter_id_is_unique() -> None:
    """`--list-rules` names exactly 28 rules, and `contract.charter-
    complete` is the only rule id starting with `contract.charter` --
    it does not collide with any existing `contract.*` prefix (only
    `contract.requires` shares the family, and the two ids differ after
    the dot)."""
    result = _run("--list-rules")
    assert result.returncode == 0
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    assert len(lines) == 28, f"expected exactly 28 rules, got {len(lines)}:\n{result.stdout}"
    rule_ids = [line.split("\t", 1)[0] for line in lines]
    assert rule_ids.count("contract.charter-complete") == 1
    charter_prefixed = [rid for rid in rule_ids if rid.startswith("contract.charter")]
    assert charter_prefixed == ["contract.charter-complete"], (
        f"expected only one contract.charter* id, found {charter_prefixed}"
    )


# ---------------------------------------------------------------------------
# `contract --require` still works after the manifest grew.
# ---------------------------------------------------------------------------

def test_contract_require_still_passes_after_manifest_growth() -> None:
    """`contract --require 1.0` against the real, now-larger (charter-
    carrying) manifest still resolves and passes -- the version check
    reads only `version:`, so growing every artifact's charter block does
    not disturb it."""
    manifest = yaml.safe_load(PLUGIN_MANIFEST.read_text(encoding="utf-8"))
    version = str(manifest.get("version", ""))
    assert version, "the real manifest carries no version at all"
    major_minor = ".".join(version.split(".")[:2])
    result = _run("contract", "--require", major_minor)
    assert result.returncode == 0, (
        f"contract --require {major_minor} failed against the grown manifest: "
        f"{result.stdout!r} {result.stderr!r}"
    )
    assert "satisfies requires-contract" in result.stdout


# ---------------------------------------------------------------------------
# The W3-02 repair: `_confirm_intent_sha()` in
# `test_probes_complexity_wave_end.py` now skips instead of failing when
# the confirmation commit is unreachable.
# ---------------------------------------------------------------------------

def _load_complexity_probe_module():
    spec = importlib.util.spec_from_file_location(
        "_adv_wave_end_complexity_probe", COMPLEXITY_PROBE_MODULE
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def test_confirm_intent_sha_unreachable_skips_with_the_claimed_reason() -> None:
    """`_confirm_intent_sha()`, called against a bare, empty tmp git repo
    where the confirmation commit provably cannot exist, raises pytest's
    `Skipped` with the EXACT reason string the function's own docstring
    claims ("intent-confirmation commit unreachable: branch squash-merged
    and deleted") -- the skip reason is not a generic placeholder, it is
    the specific claim this probe pins."""
    mod = _load_complexity_probe_module()
    tmp = tmp_empty_git_repo_no_matching_commit()
    try:
        mod.REPO = tmp
        with pytest.raises(Skipped) as excinfo:
            mod._confirm_intent_sha()
        assert (
            "intent-confirmation commit unreachable: branch squash-merged and deleted"
            in str(excinfo.value)
        ), f"unexpected skip reason: {excinfo.value!r}"
    finally:
        _cleanup_tmp_repo(tmp)


def test_confirm_intent_sha_reachable_commit_returns_sha_not_skip() -> None:
    """The mirror image of the skip case: when a commit carrying the exact
    confirmation-subject grep target IS reachable (a tmp git repo built
    for this probe, not the real branch), `_confirm_intent_sha()` returns
    that commit's sha and does NOT skip -- the repair only skips on a
    genuine absence, it does not skip unconditionally."""
    mod = _load_complexity_probe_module()
    tmp = tmp_git_repo_with_matching_commit()
    try:
        mod.REPO = tmp
        sha = mod._confirm_intent_sha()
        expected = subprocess.run(
            ["git", "log", "--format=%H", "-1"],
            cwd=str(tmp), capture_output=True, text=True, check=True,
        ).stdout.strip()
        assert sha == expected, f"expected {expected}, got {sha}"
    finally:
        _cleanup_tmp_repo(tmp)


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True)


def tmp_empty_git_repo_no_matching_commit() -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="adv_charter_wave_end_"))
    _git(tmp, "init", "-q")
    _git(tmp, "config", "user.email", "adversary@example.invalid")
    _git(tmp, "config", "user.name", "adversary")
    (tmp / "seed.txt").write_text("seed\n", encoding="utf-8")
    _git(tmp, "add", "seed.txt")
    _git(tmp, "commit", "-q", "-m", "unrelated seed commit")
    return tmp


def tmp_git_repo_with_matching_commit() -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="adv_charter_wave_end_match_"))
    _git(tmp, "init", "-q")
    _git(tmp, "config", "user.email", "adversary@example.invalid")
    _git(tmp, "config", "user.name", "adversary")
    (tmp / "seed.txt").write_text("seed\n", encoding="utf-8")
    _git(tmp, "add", "seed.txt")
    _git(
        tmp, "commit", "-q", "-m",
        "docs(loom): intent 2026-09-05-review-sees-complexity-and-process-cost confirmed",
    )
    return tmp


def _cleanup_tmp_repo(tmp: Path) -> None:
    shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(pytest.main([__file__, "-q"]))
