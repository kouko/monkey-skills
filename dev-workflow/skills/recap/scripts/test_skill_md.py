"""Tests for dev-workflow/skills/recap/SKILL.md — T2 RED assertions.

Assertions (a-f) per plan T2 Acceptance.RED:
  a) YAML frontmatter parses cleanly with name=recap, version=0.1.0, non-empty description
  b) description contains recap + ≥1 zh-TW trigger + ≥1 ja trigger + ≥1 en trigger
  c) description disambiguates from built-in /recap via away-summary + in-session markers
  d) body references references/seven-block-schema.md (relative path)
  e) body token count ≤6500 (chars/4 proxy)
  f) body cites all 5 共通核心原則 by name
"""

import re
from pathlib import Path

import pytest

try:
    import yaml  # PyYAML
except ImportError:  # pragma: no cover — environment guard
    yaml = None

SKILL_MD = (
    Path(__file__).parent.parent / "SKILL.md"
)

FIVE_PRINCIPLES = [
    "structured-schema",
    "quote-not-paraphrase",
    "all-user-messages",
    "synthesis-check",
    "plain-language",
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
    """All six assertions for T2 acceptance gate."""

    def setup_method(self):
        self.fm, self.body = _parse_skill_md()
        self.description = self.fm.get("description", "") or ""

    def test_a_frontmatter_fields(self):
        """(a) YAML frontmatter: name=recap, version=0.1.0, non-empty description."""
        assert self.fm.get("name") == "recap", "name must be 'recap'"
        assert self.fm.get("version") == "0.1.0", "version must be '0.1.0'"
        assert self.description.strip(), "description must be non-empty"

    def test_b_multilingual_triggers(self):
        """(b) description contains recap + zh-TW trigger + ja trigger + en trigger."""
        desc = self.description
        assert "recap" in desc.lower(), "description must contain 'recap'"
        # zh-TW triggers
        assert any(t in desc for t in ("我們", "剛剛")), (
            "description must contain at least one zh-TW trigger: 我們 or 剛剛"
        )
        # ja triggers
        assert any(t in desc for t in ("振り", "振り返り")), (
            "description must contain at least one ja trigger: 振り or 振り返り"
        )
        # en triggers
        assert any(t in desc for t in ("where were we", "I'm lost")), (
            "description must contain at least one en trigger: 'where were we' or 'I\\'m lost'"
        )

    def test_c_disambiguation_from_builtin(self):
        """(c) description explicitly disambiguates from built-in /recap."""
        desc = self.description
        assert "away-summary" in desc, (
            "description must contain 'away-summary' to distinguish from built-in /recap"
        )
        assert "in-session" in desc, (
            "description must contain 'in-session' to distinguish from built-in /recap"
        )

    def test_d_relative_path_reference(self):
        """(d) body references references/seven-block-schema.md."""
        assert "references/seven-block-schema.md" in self.body, (
            "SKILL.md body must reference 'references/seven-block-schema.md'"
        )

    def test_e_token_budget(self):
        """(e) body token count ≤6500 (chars/4 proxy)."""
        approx_tokens = len(self.body) / 4
        assert approx_tokens <= 6500, (
            f"body token estimate {approx_tokens:.0f} exceeds 6500 (chars={len(self.body)})"
        )

    def test_f_five_principles_named(self):
        """(f) body cites all 5 共通核心原則 by name."""
        missing = [p for p in FIVE_PRINCIPLES if p not in self.body]
        assert not missing, (
            f"SKILL.md body missing 共通核心原則: {missing}"
        )


# Single test function for the plan's pytest invocation target
def test_frontmatter_and_routing():
    """Composite gate: all six assertions a-f must pass."""
    fm, body = _parse_skill_md()
    description = fm.get("description", "") or ""

    # (a)
    assert fm.get("name") == "recap"
    assert fm.get("version") == "0.1.0"
    assert description.strip()

    # (b)
    desc = description
    assert "recap" in desc.lower()
    assert any(t in desc for t in ("我們", "剛剛"))
    assert any(t in desc for t in ("振り", "振り返り"))
    assert any(t in desc for t in ("where were we", "I'm lost"))

    # (c)
    assert "away-summary" in desc
    assert "in-session" in desc

    # (d)
    assert "references/seven-block-schema.md" in body

    # (e)
    approx_tokens = len(body) / 4
    assert approx_tokens <= 6500

    # (f)
    missing = [p for p in FIVE_PRINCIPLES if p not in body]
    assert not missing, f"Missing principles: {missing}"
