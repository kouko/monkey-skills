from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


SOURCE_ROOT = Path(__file__).resolve().parents[1]
SOURCE_SCRIPT = Path(__file__).with_name("live_gate_station_receipt.py")

RESOURCE_PATHS = {
    "review_scope": "scripts/review_scope.py",
    "gate_markers": "scripts/loom_gate_markers.py",
    "live_gate_station_receipt": "scripts/live_gate_station_receipt.py",
    "live_gate_adapter_probe": "scripts/live_gate_adapter_probe.py",
    "doc_citation_checker": "scripts/check_doc_citations.py",
    "reviewer_discipline": "scripts/_reviewer-discipline.md",
    "code_reviewer": "agents/code-reviewer.md",
    "docs_reviewer": "agents/docs-reviewer.md",
    "code_review_skill": "skills/requesting-code-review/SKILL.md",
    "docs_review_skill": "skills/requesting-docs-review/SKILL.md",
    "quality_rubric": "skills/subagent-driven-development/rubrics/quality-gate.md",
    "architecture_rubric": "skills/subagent-driven-development/rubrics/arch-gate.md",
    "security_checklist": "skills/subagent-driven-development/checklists/security-checklist.md",
    "spec_consistency_checklist": "skills/subagent-driven-development/checklists/spec-consistency.md",
    "app_security_standard": "skills/subagent-driven-development/standards/app-security-standard.md",
    "character_encoding_security_standard": "skills/subagent-driven-development/standards/character-encoding-security.md",
    "deliberate_simplification_standard": "skills/subagent-driven-development/standards/deliberate-simplification.md",
    "external_surface_grounding_standard": "skills/subagent-driven-development/standards/external-surface-grounding.md",
    "naming_and_functions_standard": "skills/subagent-driven-development/standards/naming-and-functions.md",
    "pragmatic_principles_standard": "skills/subagent-driven-development/standards/pragmatic-principles.md",
    "refactoring_standard": "skills/subagent-driven-development/standards/refactoring-standard.md",
    "solid_principles_standard": "skills/subagent-driven-development/standards/solid-principles.md",
    "tdd_standard": "skills/subagent-driven-development/standards/tdd-standard.md",
}


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _fixture(tmp_path: Path) -> tuple[Path, Path, Path, Path, str]:
    root = tmp_path / "plugin"
    for relative in RESOURCE_PATHS.values():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        source = SOURCE_ROOT / relative
        if relative == "scripts/live_gate_station_receipt.py":
            shutil.copyfile(SOURCE_SCRIPT, target)
        else:
            target.write_text(
                source.read_text(encoding="utf-8") if source.is_file() else "fixture\n",
                encoding="utf-8",
            )
    shutil.copyfile(SOURCE_ROOT / "scripts/review_context.py", root / "scripts/review_context.py")
    manifest = root / ".claude-plugin" / "plugin.json"
    manifest.parent.mkdir()
    manifest.write_text('{"name":"loom-code","version":"test"}\n', encoding="utf-8")

    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "gate@example.test")
    _git(repo, "config", "user.name", "Gate")
    (repo / "README.md").write_text("fixture\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-qm", "fixture")
    reviewed_sha = _git(repo, "rev-parse", "HEAD")
    marker = repo / ".git" / "loom"
    marker.mkdir()
    packet = tmp_path / "packet.json"
    packet.write_text(
        json.dumps(
            {
                "target_repo": str(repo.resolve()),
                "reviewed_sha": reviewed_sha,
                "plugin_version": "test",
                "resources": {
                    key: str((root / relative).resolve())
                    for key, relative in RESOURCE_PATHS.items()
                },
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return root, repo, marker, packet, reviewed_sha


def _command(
    root: Path,
    repo: Path,
    marker: Path,
    packet: Path,
    *,
    station: str = "CODE",
    nonce: str = "a" * 32,
) -> list[str]:
    return [
        sys.executable,
        str(root / "scripts/live_gate_station_receipt.py"),
        "--packet", str(packet),
        "--plugin-root", str(root),
        "--marker-dir", str(marker),
        "--repo", str(repo),
        "--station", station,
        "--nonce", nonce,
    ]


def test_receipt_is_atomic_complete_and_exclusive(tmp_path: Path) -> None:
    root, repo, marker, packet, reviewed_sha = _fixture(tmp_path)
    command = _command(root, repo, marker, packet)

    assert subprocess.run(command, capture_output=True, text=True).returncode == 0
    receipt_path = marker / f"CODE-{'a' * 32}.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    packet_data = json.loads(packet.read_text(encoding="utf-8"))
    packet_digest = hashlib.sha256(
        (json.dumps(packet_data, sort_keys=True, separators=(",", ":")) + "\n").encode()
    ).hexdigest()
    assert receipt == {
        "nonce": "a" * 32,
        "packet_sha256": packet_digest,
        "plugin_root": str(root.resolve()),
        "reviewed_sha": reviewed_sha,
        "station": "CODE",
        "target_repo": str(repo.resolve()),
    }
    assert subprocess.run(command, capture_output=True, text=True).returncode != 0
    assert json.loads(receipt_path.read_text(encoding="utf-8")) == receipt
    assert not tuple(marker.glob(".*.tmp"))


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        (lambda packet: packet.update(extra="field"), "schema"),
        (lambda packet: packet["resources"].pop("review_scope"), "resources"),
        (
            lambda packet: packet["resources"].update(
                review_scope=packet["resources"]["gate_markers"]
            ),
            "resources",
        ),
        (lambda packet: packet.update(reviewed_sha="0" * 40), "sha"),
        (lambda packet: packet.update(plugin_version="wrong"), "version"),
    ],
)
def test_receipt_refuses_incomplete_or_mismatched_packet(
    tmp_path: Path, mutation, expected: str
) -> None:
    root, repo, marker, packet_path, _ = _fixture(tmp_path)
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    mutation(packet)
    packet_path.write_text(json.dumps(packet), encoding="utf-8")

    result = subprocess.run(
        _command(root, repo, marker, packet_path), capture_output=True, text=True
    )

    assert result.returncode != 0
    assert expected in result.stderr.lower()
    assert not tuple(marker.glob("*.json"))


def test_receipt_refuses_wrong_plugin_root_non_marker_destination_and_unsafe_nonce(
    tmp_path: Path,
) -> None:
    root, repo, marker, packet, _ = _fixture(tmp_path)
    other = tmp_path / "other"
    other.mkdir()

    wrong_root = _command(root, repo, marker, packet)
    wrong_root[wrong_root.index("--plugin-root") + 1] = str(other)
    assert subprocess.run(wrong_root, capture_output=True).returncode != 0

    wrong_marker = _command(root, repo, marker, packet)
    wrong_marker[wrong_marker.index("--marker-dir") + 1] = str(tmp_path / "elsewhere")
    assert subprocess.run(wrong_marker, capture_output=True).returncode != 0

    unsafe_nonce = _command(root, repo, marker, packet, nonce="../escape")
    assert subprocess.run(unsafe_nonce, capture_output=True).returncode != 0
    assert not tuple(marker.glob("*.json"))


def test_receipt_refuses_symlink_marker_or_existing_symlink_receipt(tmp_path: Path) -> None:
    root, repo, marker, packet, _ = _fixture(tmp_path)
    real_marker = repo / ".git" / "real-loom"
    real_marker.mkdir()
    marker.rmdir()
    marker.symlink_to(real_marker, target_is_directory=True)
    assert subprocess.run(_command(root, repo, marker, packet), capture_output=True).returncode != 0
    assert not tuple(real_marker.iterdir())

    marker.unlink()
    marker.mkdir()
    outside = tmp_path / "outside.json"
    outside.write_text("keep", encoding="utf-8")
    (marker / f"CODE-{'a' * 32}.json").symlink_to(outside)
    assert subprocess.run(_command(root, repo, marker, packet), capture_output=True).returncode != 0
    assert outside.read_text(encoding="utf-8") == "keep"
