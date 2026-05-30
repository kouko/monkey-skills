"""Tests for dev-workflow/skills/handoff/SKILL.md — T2 RED assertions.

Assertions (a-h) per plan T2 Acceptance.RED:
  a) YAML frontmatter parses with name=handoff, version=0.2.0, non-empty description
  b) description contains 'handoff' + multilingual triggers:
       zh-TW: '收尾' or '明天繼續' or '保存狀態'
       ja: '今日はここまで' or '引き継ぎ'
       en: 'wrap up' or 'save state' or 'pick up where we left off'
  c) description disambiguates from sister recap (cross-session + in-session markers)
     AND from OpenAI-style agent-handoff (cross-session + not-agent-to-agent / not-delegation)
  d) body relative-path references 'references/handoff-schema.md'
  e) body token count ≤6500 (chars/4 proxy)
  f) body cites all 5 共通核心原則 by name (including technical-precision)
  g) body contains BOTH 'prepare' mode AND 'resume' mode language
  h) body contains the literal path '.claude/handoffs/'
"""

import re
from pathlib import Path

import pytest

try:
    import yaml  # PyYAML
except ImportError:  # pragma: no cover — environment guard
    yaml = None

SKILL_MD = Path(__file__).parent.parent / "SKILL.md"

FIVE_PRINCIPLES = [
    "structured-schema",
    "quote-not-paraphrase",
    "all-user-messages",
    "synthesis-check",
    "technical-precision",
]


def _parse_skill_md():
    """Split SKILL.md into frontmatter dict and body string."""
    if yaml is None:  # pragma: no cover — environment guard
        pytest.skip("PyYAML not available")
    text = SKILL_MD.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError("SKILL.md has no YAML frontmatter")
    # Split on the closing --- (second occurrence)
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("SKILL.md frontmatter not closed with ---")
    fm = yaml.safe_load(parts[1])
    body = parts[2]
    return fm, body


class TestFrontmatterAndRouting:
    """All eight assertions for T2 acceptance gate."""

    def setup_method(self):
        self.fm, self.body = _parse_skill_md()
        self.description = self.fm.get("description", "") or ""

    def test_a_frontmatter_fields(self):
        """(a) YAML frontmatter: name=handoff, version=0.2.0, non-empty description."""
        assert self.fm.get("name") == "handoff", "name must be 'handoff'"
        assert self.fm.get("version") == "0.2.0", "version must be '0.2.0'"
        assert self.description.strip(), "description must be non-empty"

    def test_b_multilingual_triggers(self):
        """(b) description contains 'handoff' + zh-TW + ja + en triggers."""
        desc = self.description
        assert "handoff" in desc.lower(), "description must contain 'handoff'"
        # zh-TW triggers
        assert any(t in desc for t in ("收尾", "明天繼續", "保存狀態")), (
            "description must contain at least one zh-TW trigger: 收尾 or 明天繼續 or 保存狀態"
        )
        # ja triggers
        assert any(t in desc for t in ("今日はここまで", "引き継ぎ")), (
            "description must contain at least one ja trigger: 今日はここまで or 引き継ぎ"
        )
        # en triggers
        assert any(t in desc for t in ("wrap up", "save state", "pick up where we left off")), (
            "description must contain at least one en trigger: 'wrap up' or 'save state' or 'pick up where we left off'"
        )

    def test_c_double_disambiguation(self):
        """(c) description disambiguates from sister recap AND from agent-to-agent handoff."""
        desc = self.description
        # Disambiguate from recap: cross-session vs in-session contrast
        assert "cross-session" in desc, (
            "description must contain 'cross-session' to contrast with in-session recap"
        )
        assert "in-session" in desc, (
            "description must contain 'in-session' to contrast with this skill's cross-session scope"
        )
        # Disambiguate from OpenAI agent-to-agent handoff
        assert any(t in desc for t in ("not agent-to-agent", "not delegation", "agent-to-agent")), (
            "description must mention agent-to-agent disambiguation"
        )

    def test_d_relative_path_reference(self):
        """(d) body references references/handoff-schema.md."""
        assert "references/handoff-schema.md" in self.body, (
            "SKILL.md body must reference 'references/handoff-schema.md'"
        )

    def test_e_token_budget(self):
        """(e) body token count ≤6500 (chars/4 proxy)."""
        approx_tokens = len(self.body) / 4
        assert approx_tokens <= 6500, (
            f"body token estimate {approx_tokens:.0f} exceeds 6500 (chars={len(self.body)})"
        )

    def test_f_five_principles_named(self):
        """(f) body cites all 5 共通核心原則 including technical-precision."""
        missing = [p for p in FIVE_PRINCIPLES if p not in self.body]
        assert not missing, (
            f"SKILL.md body missing 共通核心原則: {missing}"
        )

    def test_g_prepare_and_resume_modes(self):
        """(g) body contains BOTH 'prepare' mode AND 'resume' mode language."""
        assert "prepare" in self.body.lower(), (
            "SKILL.md body must contain 'prepare' mode"
        )
        assert "resume" in self.body.lower(), (
            "SKILL.md body must contain 'resume' mode"
        )

    def test_h_handoffs_path(self):
        """(h) body contains literal path '.claude/handoffs/'."""
        assert ".claude/handoffs/" in self.body, (
            "SKILL.md body must contain literal path '.claude/handoffs/' (HARD-GATE)"
        )


# Single test function matching the plan's pytest invocation target
def test_frontmatter_and_routing():
    """Composite gate: all eight assertions a-h must pass."""
    fm, body = _parse_skill_md()
    description = fm.get("description", "") or ""

    # (a)
    assert fm.get("name") == "handoff", "name must be 'handoff'"
    assert fm.get("version") == "0.2.0", "version must be '0.2.0'"
    assert description.strip(), "description must be non-empty"

    # (b)
    desc = description
    assert "handoff" in desc.lower()
    assert any(t in desc for t in ("收尾", "明天繼續", "保存狀態"))
    assert any(t in desc for t in ("今日はここまで", "引き継ぎ"))
    assert any(t in desc for t in ("wrap up", "save state", "pick up where we left off"))

    # (c)
    assert "cross-session" in desc
    assert "in-session" in desc
    assert any(t in desc for t in ("not agent-to-agent", "not delegation", "agent-to-agent"))

    # (d)
    assert "references/handoff-schema.md" in body

    # (e)
    approx_tokens = len(body) / 4
    assert approx_tokens <= 6500, f"body token estimate {approx_tokens:.0f} exceeds 6500"

    # (f)
    missing = [p for p in FIVE_PRINCIPLES if p not in body]
    assert not missing, f"Missing principles: {missing}"

    # (g)
    assert "prepare" in body.lower()
    assert "resume" in body.lower()

    # (h)
    assert ".claude/handoffs/" in body, "Missing literal path '.claude/handoffs/'"
