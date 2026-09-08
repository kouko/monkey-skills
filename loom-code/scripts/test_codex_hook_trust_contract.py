"""Contract pins for installed Loom hook trust versus repository hooks."""

from __future__ import annotations

from pathlib import Path


PLUGIN = Path(__file__).resolve().parents[1]
FIRST_CONTACT = PLUGIN / "skills" / "write-plan" / "references" / "codex-first-contact.md"


def test_first_contact_new_worktree_does_not_create_loom_trust_work() -> None:
    text = " ".join(FIRST_CONTACT.read_text(encoding="utf-8").split())

    assert "As observed on Codex 0.153.4, creating another worktree does not create another installed Loom hook identity" in text
    assert "Repository-local hooks are separate host identities" in text
    assert "write-plan.codex-installed-hook-trust-boundary" in text


def test_first_contact_keeps_new_or_modified_hook_review_host_owned() -> None:
    text = " ".join(FIRST_CONTACT.read_text(encoding="utf-8").split())

    assert "new or modified installed definition" in text
    assert "Never edit Codex trust state" in text
    assert "--dangerously-bypass-hook-trust" in text
