"""Contract pins for installed Loom hook trust versus repository hooks."""

from __future__ import annotations

import json
from pathlib import Path


PLUGIN = Path(__file__).resolve().parents[1]
FIRST_CONTACT = PLUGIN / "skills" / "write-plan" / "references" / "codex-first-contact.md"


def test_first_contact_new_worktree_does_not_create_loom_trust_work() -> None:
    text = " ".join(FIRST_CONTACT.read_text(encoding="utf-8").split())

    assert "Creating another worktree does not create another installed Loom hook identity" in text
    assert "Repository-local hooks are separate host identities" in text


def test_first_contact_keeps_new_or_modified_hook_review_host_owned() -> None:
    text = " ".join(FIRST_CONTACT.read_text(encoding="utf-8").split())

    assert "new or modified installed definition" in text
    assert "Never edit Codex trust state" in text
    assert "--dangerously-bypass-hook-trust" in text


def test_loom_code_release_is_2_0_3_on_both_manifests() -> None:
    claude = json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text())
    codex = json.loads((PLUGIN / ".codex-plugin" / "plugin.json").read_text())

    assert claude["version"] == "2.0.3"
    assert codex["version"] == claude["version"]
