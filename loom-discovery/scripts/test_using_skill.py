"""Structural grep-test guarding the using-loom-discovery entry SKILL.md.

using-loom-discovery is the loom-discovery FAMILY ENTRY (thin router): it
routes "worth doing?" asks to business-value and "what do users need?"
asks to user-insights, but never maps needs or renders a verdict itself.
Mirrors the sibling entry-test shape (test_spec_entry_skill.py,
test_principles_entry_skill.py) — grep on load-bearing PHRASES (intent),
tolerant of wording, stdlib only.

Task 3 acceptance (docs/loom/plans/2026-07-10-loom-discovery-station.md):
  - SKILL.md exists with valid YAML frontmatter (name + description)
  - description renders to <=1536 chars (router listing-eviction budget,
    repo memory: skill-triggering-diagnose-listing-before-text)
  - both references/claude-code-tools.md and references/codex-tools.md exist
  - skill dir is flat (no nested subfolders — repo hook enforces)

Stdlib only (pathlib + re). Resolve paths relative to this test file.
"""

import re
from pathlib import Path

SKILL_DIR = Path(__file__).parents[1] / "skills" / "using-loom-discovery"
SKILL = SKILL_DIR / "SKILL.md"
CC_TOOLS = SKILL_DIR / "references" / "claude-code-tools.md"
CODEX_TOOLS = SKILL_DIR / "references" / "codex-tools.md"

_DESC_CAP = 1536


def _text() -> str:
    assert SKILL.is_file(), f"SKILL.md is absent at {SKILL}"
    return SKILL.read_text(encoding="utf-8")


def _frontmatter(text: str) -> str:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert m, "SKILL.md must open with a YAML frontmatter block (--- ... ---)"
    return m.group(1)


def _description() -> str:
    """YAML-parsed, whitespace-folded description value."""
    front = _frontmatter(_text())
    m = re.search(
        r"description:\s*[|>]?-?\s*\n?(.*?)(?:\nversion:|\Z)", front, re.DOTALL
    )
    assert m and m.group(1).strip(), \
        "frontmatter must carry a non-empty 'description:'"
    return " ".join(m.group(1).split())


# --- existence + frontmatter -------------------------------------------------

def test_skill_file_exists():
    assert SKILL.is_file(), f"using-loom-discovery/SKILL.md must exist at {SKILL}"


def test_yaml_frontmatter_name_and_description():
    front = _frontmatter(_text())
    assert re.search(r"^name:\s*using-loom-discovery\s*$", front, re.MULTILINE), \
        "frontmatter must declare 'name: using-loom-discovery'"
    desc = re.search(r"^description:\s*(\S.*)$", front, re.MULTILINE | re.DOTALL)
    assert desc and desc.group(1).strip(), \
        "frontmatter must carry a non-empty 'description:'"


def test_description_within_router_length_budget():
    """Router descriptions get the 1536-char listing-eviction budget (repo
    memory), not the 250-char house cap for member skills — routers carry
    more surface (both members' triggers + family framing)."""
    desc = _description()
    assert len(desc) <= _DESC_CAP, (
        f"description renders to {len(desc)} chars; router budget is "
        f"{_DESC_CAP} — trim it"
    )


def test_description_is_entry_framed():
    front = _frontmatter(_text()).lower()
    assert "router" in front or "entry" in front, \
        "description must frame this skill as the family entry/router"
    assert "rout" in front, "description must mention routing"


def test_description_carries_plain_language_triggers():
    """Weak-model sessions must be able to decide from the description alone
    (repo memory: skill-triggering-diagnose-listing-before-text) — EN +
    Traditional Chinese + Japanese plain-language trigger phrases."""
    desc = _description()
    assert "需求研究" in desc or "使用者洞察" in desc, \
        "description must carry a Traditional Chinese trigger (需求研究/使用者洞察)"
    assert "值不值得做" in desc, \
        "description must carry the 值不值得做 (worth-doing) trigger"
    assert "ユーザーインサイト" in desc, \
        "description must carry the Japanese ユーザーインサイト trigger"


# --- §Intake ------------------------------------------------------------------

def test_intake_section_present():
    text = _text()
    assert re.search(r"^##\s+§Intake\s*$", text, re.MULTILINE), \
        "SKILL.md must carry a '## §Intake' section"


def test_intake_references_family_reception_ssot_without_copying_rows():
    text = _text()
    assert "family-reception.md" in text, \
        "§Intake must reference loom-pipeline/hooks/family-reception.md (SSOT)"
    # never-copy discipline: the on-ramp table's own column header must not
    # be reproduced verbatim in this router
    assert "| Condition | Recommendation |" not in text, \
        "must not copy the on-ramp table's rows — point to the SSOT instead"


def test_intake_routes_to_both_members_by_verb():
    text = _text()
    low = text.lower()
    assert "business-value" in text, "must name business-value"
    assert "user-insights" in text, "must name user-insights"
    assert "worth" in low, \
        "must state the 'worth doing?' trigger routes to business-value"
    assert "what users need" in low or "what do users need" in low, \
        "must state the 'what users need?' trigger routes to user-insights"


def test_typical_sequence_and_reentrance_documented():
    text = _text()
    low = text.lower()
    assert "user-insights" in text and "business-value" in text
    assert "re-entrant" in low or "reentrant" in low, \
        "must document business-value's re-entrant-after-research nature"
    assert "skip" in low or "skippable" in low, \
        "must document that business-value (assess) is skippable"


def test_professional_isolation_line_present():
    text = _text()
    low = text.lower()
    assert "share no artifact" in low or "shares no artifact" in low, \
        "must state the professional-isolation contract (no shared artifact)"
    assert ("no agent" in low) or ("share no artifact and no agent" in low), \
        "must state the professional-isolation contract (no shared agent)"


# --- references ---------------------------------------------------------------

def test_references_files_exist():
    assert CC_TOOLS.is_file(), f"references/claude-code-tools.md missing at {CC_TOOLS}"
    assert CODEX_TOOLS.is_file(), f"references/codex-tools.md missing at {CODEX_TOOLS}"


def test_skill_folder_is_flat():
    """The skill dir may hold SKILL.md plus single-level subfolders; no
    subfolder may itself contain a subfolder (the repo hook blocks
    otherwise)."""
    assert SKILL_DIR.is_dir(), f"skill dir absent at {SKILL_DIR}"
    for sub in SKILL_DIR.iterdir():
        if sub.is_dir():
            for child in sub.iterdir():
                assert not child.is_dir(), (
                    f"flat-skill violation: nested subdir {child} under "
                    f"{sub} (subfolders must be single-level)"
                )
