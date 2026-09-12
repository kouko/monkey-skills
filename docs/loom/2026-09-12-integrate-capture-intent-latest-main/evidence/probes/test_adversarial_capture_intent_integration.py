#!/usr/bin/env python3
"""Adversarial checks for the capture-intent integration boundary."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_capture_contract_after_merge_preserves_scope_boundary() -> None:
    capture = read("loom-design/skills/capture-intent/SKILL.md")
    code_only = read("loom-code/skills/write-plan/SKILL.md")
    manifest = read("loom-code/contract/manifest.yaml")

    for text in (capture, code_only):
        assert "altitude pass" in text
        assert "explicit answer" in text
        assert "must remain `open`" in text
    assert "Unsupported product decisions remain open or are deleted" in manifest


def test_capture_contract_after_merge_keeps_retry_fix() -> None:
    resolver = read("loom-code/scripts/dispatch_profile.py")
    assert 'kind == "malformed-response"' in resolver
    assert 'reason="nonconforming-output-redispatch"' in resolver


def test_capture_release_after_merge_advances_current_version() -> None:
    claude = json.loads(read("loom-code/.claude-plugin/plugin.json"))
    codex = json.loads(read("loom-code/.codex-plugin/plugin.json"))
    changelog = read("loom-code/CHANGELOG.md")

    assert claude["version"] == "2.2.2"
    assert codex["version"] == "2.2.2"
    assert "## [2.2.2]" in changelog
    assert "## [2.2.1]" in changelog


if __name__ == "__main__":
    test_capture_contract_after_merge_preserves_scope_boundary()
    test_capture_contract_after_merge_keeps_retry_fix()
    test_capture_release_after_merge_advances_current_version()
