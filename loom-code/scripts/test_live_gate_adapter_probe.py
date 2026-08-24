"""Executable contract tests for the package-local live adapter probe."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).with_name("live_gate_adapter_probe.py")


def _run(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *arguments],
        capture_output=True,
        text=True,
    )


def test_loaded_reference_probe_emits_typed_refusal_for_relative_path() -> None:
    result = _run(
        "loaded-reference",
        "--host",
        "codex",
        "--loaded-reference-path",
        "relative/codex-tools.md",
    )

    assert result.returncode == 3
    assert json.loads(result.stdout) == {
        "type": "loom.live-gate.adapter-refusal",
        "case": "invalid-reference",
        "reason": "loaded-reference-path-not-absolute",
    }
    assert result.stderr == ""


def test_loaded_reference_probe_refuses_foreign_absolute_reference(tmp_path: Path) -> None:
    """A matching basename and resolver do not establish loom-code ancestry."""
    foreign = tmp_path / "foreign" / "skills" / "wrong-skill" / "references"
    foreign.mkdir(parents=True)
    reference = foreign / "codex-tools.md"
    reference.write_text("foreign", encoding="utf-8")
    resolver = tmp_path / "foreign" / "scripts" / "review_context.py"
    resolver.parent.mkdir()
    resolver.write_text("foreign", encoding="utf-8")

    result = _run(
        "loaded-reference",
        "--host",
        "codex",
        "--loaded-reference-path",
        str(reference),
    )

    assert result.returncode == 3
    assert json.loads(result.stdout) == {
        "type": "loom.live-gate.adapter-refusal",
        "case": "invalid-reference",
        "reason": "loaded-reference-layout-invalid",
    }


def test_loaded_reference_probe_refuses_symlink_reference(tmp_path: Path) -> None:
    """The source file itself must be a regular installed-plugin artifact."""
    target = tmp_path / "target.md"
    target.write_text("target", encoding="utf-8")
    link = tmp_path / "codex-tools.md"
    link.symlink_to(target)

    result = _run(
        "loaded-reference",
        "--host",
        "codex",
        "--loaded-reference-path",
        str(link),
    )

    assert result.returncode == 3
    assert json.loads(result.stdout) == {
        "type": "loom.live-gate.adapter-refusal",
        "case": "invalid-reference",
        "reason": "loaded-reference-not-regular",
    }


def test_loaded_reference_probe_accepts_canonical_installed_reference() -> None:
    reference = (
        SCRIPT.parents[1]
        / "skills"
        / "using-loom-code"
        / "references"
        / "codex-tools.md"
    )

    result = _run(
        "loaded-reference",
        "--host",
        "codex",
        "--loaded-reference-path",
        str(reference),
    )

    assert result.returncode == 0
    assert json.loads(result.stdout) == {
        "type": "loom.live-gate.adapter-acceptance",
        "case": "valid-reference",
        "reason": "loaded-reference-accepted",
    }


def test_post_fix_probe_emits_typed_refusal_for_unchanged_sha() -> None:
    reviewed_sha = "a" * 40
    result = _run(
        "post-fix-sha",
        "--initial-sha",
        reviewed_sha,
        "--post-fix-sha",
        reviewed_sha,
    )

    assert result.returncode == 3
    assert json.loads(result.stdout) == {
        "type": "loom.live-gate.adapter-refusal",
        "case": "unchanged-post-fix",
        "reason": "post-fix-sha-unchanged",
    }
    assert result.stderr == ""
