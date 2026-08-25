"""Fail-closed validation gate for immutable review context packets."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


SCRIPT = Path(__file__).resolve().parent / "review_context.py"


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def _target_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "target"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "validate@example.test")
    _git(repo, "config", "user.name", "Packet Validate Test")
    (repo / "README.md").write_text("# Target\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-m", "initial")
    return repo


def _plugin_root(tmp_path: Path, name: str = "plugin") -> Path:
    """Create a minimal plugin installation root (.claude-plugin/plugin.json)."""
    root = tmp_path / name
    (root / ".claude-plugin").mkdir(parents=True)
    (root / ".claude-plugin" / "plugin.json").write_text("{}\n", encoding="utf-8")
    return root


def _well_formed_packet(tmp_path: Path) -> dict[str, object]:
    repo = _target_repo(tmp_path)
    resource = _plugin_root(tmp_path) / "resource.md"
    resource.write_text("resource\n", encoding="utf-8")
    return {
        "target_repo": str(repo),
        "reviewed_sha": _git(repo, "rev-parse", "HEAD"),
        "plugin_version": "0.98.1",
        "resources": {"reviewer_discipline": str(resource)},
    }


def _validate(tmp_path: Path, packet: dict[str, object]) -> subprocess.CompletedProcess[str]:
    packet_path = tmp_path / "packet.json"
    packet_path.write_text(json.dumps(packet), encoding="utf-8")
    # cwd pinned to tmp_path: a relative target_repo must fail on
    # absoluteness itself, not by luck of the validator's cwd.
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--validate", str(packet_path)],
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
    )


def _drop_key(key: str):
    def mutate(packet: dict[str, object], tmp_path: Path) -> None:
        del packet[key]

    return mutate


def _set_sha(sha: str):
    def mutate(packet: dict[str, object], tmp_path: Path) -> None:
        packet["reviewed_sha"] = sha

    return mutate


def _relative_resource(packet: dict[str, object], tmp_path: Path) -> None:
    packet["resources"] = {"reviewer_discipline": "relative/resource.md"}


def _missing_resource(packet: dict[str, object], tmp_path: Path) -> None:
    packet["resources"] = {"reviewer_discipline": str(tmp_path / "does-not-exist.md")}


def _relative_target_repo(packet: dict[str, object], tmp_path: Path) -> None:
    packet["target_repo"] = "target"


def _rootless_resource(packet: dict[str, object], tmp_path: Path) -> None:
    # Absolute and existing, but no .claude-plugin/plugin.json ancestor.
    resource = tmp_path / "rootless.md"
    resource.write_text("resource\n", encoding="utf-8")
    packet["resources"] = {"reviewer_discipline": str(resource)}


def _split_root_resources(packet: dict[str, object], tmp_path: Path) -> None:
    # A second value under a DIFFERENT plugin root than the first.
    extra = _plugin_root(tmp_path, "plugin-b") / "extra.md"
    extra.write_text("resource\n", encoding="utf-8")
    resources = dict(packet["resources"])  # type: ignore[arg-type]
    resources["gate_markers"] = str(extra)
    packet["resources"] = resources


@pytest.mark.parametrize(
    ("mutate", "field"),
    [
        pytest.param(_drop_key("target_repo"), "target_repo", id="missing-target_repo"),
        pytest.param(_drop_key("reviewed_sha"), "reviewed_sha", id="missing-reviewed_sha"),
        pytest.param(_drop_key("plugin_version"), "plugin_version", id="missing-plugin_version"),
        pytest.param(_drop_key("resources"), "resources", id="missing-resources"),
        pytest.param(_set_sha("abc123"), "reviewed_sha", id="short-sha"),
        pytest.param(_set_sha("z" * 40), "reviewed_sha", id="non-hex-sha"),
        pytest.param(_set_sha("0" * 40), "reviewed_sha", id="sha-not-in-repo"),
        pytest.param(_relative_resource, "resources", id="relative-resource-path"),
        pytest.param(_missing_resource, "resources", id="nonexistent-resource-path"),
        pytest.param(_relative_target_repo, "target_repo", id="relative-target_repo"),
        pytest.param(_rootless_resource, "reviewer_discipline", id="resource-outside-plugin-root"),
        pytest.param(_split_root_resources, "gate_markers", id="resources-two-plugin-roots"),
    ],
)
def test_validate_rejects_malformed_packets(tmp_path: Path, mutate, field: str) -> None:
    """A malformed packet must exit nonzero and name the failing field on stderr.

    Reviewers were observed silently self-repairing malformed packets; the
    producer must refuse them mechanically before any reviewer dispatch.
    """
    packet = _well_formed_packet(tmp_path)
    mutate(packet, tmp_path)

    result = _validate(tmp_path, packet)

    assert result.returncode != 0
    assert "PACKET-INVALID:" in result.stderr
    assert field in result.stderr


def test_validate_accepts_well_formed_packet(tmp_path: Path) -> None:
    """A well-formed packet passes the gate with exit 0 and no complaints."""
    result = _validate(tmp_path, _well_formed_packet(tmp_path))

    assert result.returncode == 0, result.stderr
    assert "PACKET-INVALID:" not in result.stderr
