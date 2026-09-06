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

import subprocess
import sys
from pathlib import Path

import yaml


REPO = Path(
    subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
)

CHECKER = REPO / "loom-code" / "scripts" / "loom_checker.py"
CODEX_CHECKER = REPO / ".codex" / "hooks" / "loom_checker.py"
PLUGIN_MANIFEST = REPO / "loom-code" / "contract" / "manifest.yaml"

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
                "edits_after": [{"id": "c", "text": "c"}],
            }
        },
        "spec": {
            "charter": {
                "answers": "y",
                "readers": ["a"],
                "must": ["b"],
                "must_not": [{"kind": "z", "goes_to": "intent"}],
                "signoff": "build",
                "edits_after": [{"id": "c", "text": "c"}],
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
                    "signoff": "build", "edits_after": [{"id": "c", "text": "c"}],
                }
            },
            "spec": {
                "charter": {
                    "answers": "y", "readers": ["a"], "must": ["b"],
                    "must_not": [{"kind": "z", "goes_to": "intent"}],
                    "signoff": "build", "edits_after": [{"id": "c", "text": "c"}],
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
                    "edits_after": [{"id": "c", "text": "c"}],
                }
            },
            "spec": {
                "charter": {
                    "answers": "y", "readers": ["a"], "must": ["b"],
                    "must_not": [{"kind": "z", "goes_to": "intent"}],
                    "signoff": "build", "edits_after": [{"id": "c", "text": "c"}],
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

def test_render_charter_table_pipe_and_newline_in_cell_blocked(tmp_path: Path) -> None:
    """`check_charter_row` now rejects a `|` or a newline in any charter
    string field -- `must` here -- with a `contract.charter-complete`
    failure naming the artifact and the key, so the command exits 1.
    Fixed for wave-end:0-06 -- previously this markdown-injection shape
    tripped no rule at all and exited 0."""
    doc = {
        "version": "1.0.0",
        "stations": [{"name": "build"}],
        "artifacts": {
            "intent": {
                "charter": {
                    "answers": "x", "readers": ["a"],
                    "must": ["a | injected-cell\nand-a-new-row"],
                    "must_not": [{"kind": "z", "goes_to": "spec"}],
                    "signoff": "build", "edits_after": [{"id": "c", "text": "c"}],
                }
            },
            "spec": {
                "charter": {
                    "answers": "y", "readers": ["a"], "must": ["b"],
                    "must_not": [{"kind": "z", "goes_to": "intent"}],
                    "signoff": "build", "edits_after": [{"id": "c", "text": "c"}],
                }
            },
        },
    }
    manifest_path = _write_yaml(tmp_path, doc)
    result = _run_charter(manifest_path)
    assert result.returncode == 1, (
        f"expected the '|'/newline-carrying must entry to be blocked (exit 1); "
        f"got {result.returncode}: stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "intent.must" in result.stderr
    assert "'|'" in result.stderr or "newline" in result.stderr
    # Control: the same manifest with the `|`/`\n` stripped out of the
    # `must` string is accepted cleanly -- so the block above is
    # attributable to the injected characters, not to something else
    # about this manifest shape.
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
    assert clean_result.returncode == 0, (
        f"control manifest (no '|'/newline) should pass cleanly, got "
        f"{clean_result.returncode}: {clean_result.stderr!r}"
    )
    clean_lines = clean_result.stdout.splitlines()
    assert len(clean_lines) == 4, f"control manifest did not render cleanly: {clean_result.stdout!r}"


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
                    "signoff": "build", "edits_after": [{"id": "c", "text": "c"}],
                }
            },
            "spec": {
                "charter": {
                    "answers": "y", "readers": ["a"], "must": ["b"],
                    "must_not": [{"kind": "z", "goes_to": "intent"}],
                    "signoff": "build", "edits_after": [{"id": "c", "text": "c"}],
                }
            },
        },
    }
    manifest_path = _write_yaml(tmp_path, doc)
    result = _run_charter(manifest_path)
    assert result.returncode == 1
    assert "intent.must_not is empty" in result.stderr
    assert "| spec | y | a | b | z → intent | build | c: c |" in result.stdout


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

def test_list_rules_count_is_exactly_29_and_charter_id_is_unique() -> None:
    """`--list-rules` names exactly 30 rules (28 plus W1-01's
    `plan.field-caps` plus W1-02's `plan.edits-after-commit`, both landed
    after this probe was first written -- count update authorised by
    W1-02's own dispatch packet), and `contract.charter-complete` is the
    only rule id starting with `contract.charter` -- it does not collide
    with any existing `contract.*` prefix (only `contract.requires` shares
    the family, and the two ids differ after the dot). (Count updated
    again to 31 for W1-03's review.round-append-only, same
    authorisation shape.)"""
    result = _run("--list-rules")
    assert result.returncode == 0
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    assert len(lines) == 31, f"expected exactly 31 rules, got {len(lines)}:\n{result.stdout}"
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
