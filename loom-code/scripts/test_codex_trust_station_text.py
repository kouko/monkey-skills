"""W1-03 — the three stations that touch a Codex hook read `--trusted`
per definition before doing anything else with the hook, and
codex-first-contact.md explains what a trust approval is bound to.

Graduates evidence/probes/test_abuse_hook_trust.py case (8) into the
package suite: that probe only checks that all four words appear
somewhere in each file; these tests pin the load-bearing sentences and
the "What trust is bound to" section by substring, so a rewording that
drops one of the two facts (definition-not-file, path-per-clone) fails
loudly here even if the loose probe still passes.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CODEX_FIRST_CONTACT = (
    REPO / "loom-code" / "skills" / "write-plan" / "references" / "codex-first-contact.md"
)
WRITE_PLAN_SKILL = REPO / "loom-code" / "skills" / "write-plan" / "SKILL.md"
BUILD_SKILL = REPO / "loom-code" / "skills" / "build" / "SKILL.md"
REVIEW_SKILL = REPO / "loom-code" / "skills" / "review" / "SKILL.md"


def test_codex_first_contact_reads_trusted_before_the_push_probe() -> None:
    text = CODEX_FIRST_CONTACT.read_text(encoding="utf-8")
    assert "--trusted" in text
    assert "never" in text.lower()
    assert "/hooks" in text
    assert "stop" in text.lower()


def test_codex_first_contact_explains_what_trust_is_bound_to() -> None:
    text = CODEX_FIRST_CONTACT.read_text(encoding="utf-8")
    assert "What trust is bound to" in text
    # definition, not script content
    assert "needs no re-approval" in text
    # absolute path -> per worktree/clone
    assert "absolute path" in text
    assert "worktree" in text.lower()


def test_codex_first_contact_documents_the_thin_shim() -> None:
    text = CODEX_FIRST_CONTACT.read_text(encoding="utf-8")
    assert "loom_record_fire.py" in text
    assert "Your own hooks" in text
    assert "no evidence of a firing" in text.lower() or "no evidence" in text.lower()


def test_write_plan_step_0b_names_trusted_never_hooks_stop() -> None:
    text = WRITE_PLAN_SKILL.read_text(encoding="utf-8")
    section = text.split("## Step 0b", 1)[1]
    section = section.split("## Step 1", 1)[0]
    assert "--trusted" in section
    assert "never" in section.lower()
    assert "/hooks" in section
    assert "stop" in section.lower()


def test_build_skill_section_0_names_trusted_never_hooks_stop() -> None:
    text = BUILD_SKILL.read_text(encoding="utf-8")
    section = text.split("## 0. Contract check", 1)[1]
    section = section.split("Then locate the change", 1)[0]
    assert "--trusted" in section
    assert "never" in section.lower()
    assert "/hooks" in section
    assert "stop" in section.lower()


def test_review_skill_second_vendor_paragraph_checks_trusted_first() -> None:
    text = REVIEW_SKILL.read_text(encoding="utf-8")
    section = text.split("**Second vendor.**", 1)[1]
    section = section.split("Before dispatching to that tool", 1)[0]
    assert "--trusted" in section
    assert "never" in section.lower()
    assert "/hooks" in section
    assert "stop" in section.lower()
