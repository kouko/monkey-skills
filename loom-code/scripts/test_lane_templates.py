"""W1-03 — templates and defaults for the user-declared lane
(`lane:` on an intent, `default-lane:` in KICKOFF-DEFAULTS): the intent
template documents the optional field and its switch grammar, the
KICKOFF template documents the repo-wide default, and this repo's own
KICKOFF-DEFAULTS.md declares `default-lane: full`.

Declaring the `default-lane` key as a manifest `kickoff_default` name is
W1-01's job (contract/manifest.yaml `kickoff_defaults`), not this task's
-- see the plan's W1-03 risk note. Until W1-01 lands, adding a
`default-lane:` line to docs/loom/KICKOFF-DEFAULTS.md trips
`test_kickoff_defaults_grammar.py`'s manifest-declared-key check; that
one test is expected to fail here and is skipped with a reason naming
W1-01, per the task's own risk note (do not edit manifest.yaml from
this task).
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
TEMPLATES = REPO / "loom-code" / "contract" / "templates"
CODEX_TEMPLATES = REPO / ".codex" / "hooks" / "contract" / "templates"
MANIFEST = REPO / "loom-code" / "contract" / "manifest.yaml"
KICKOFF_DEFAULTS = REPO / "docs" / "loom" / "KICKOFF-DEFAULTS.md"

INTENT_TEMPLATE = TEMPLATES / "intent.md"
KICKOFF_TEMPLATE = TEMPLATES / "KICKOFF-DEFAULTS.md"

SWITCH_GRAMMAR_RE = re.compile(
    r"lane: <name> — switched <YYYY-MM-DD> by <name>, from "
    r"<wave <n>\|round <n>>"
)


def test_intent_template_carries_a_lane_line() -> None:
    text = INTENT_TEMPLATE.read_text(encoding="utf-8")
    lane_lines = [
        line for line in text.splitlines() if re.search(r"\blane:", line)
    ]
    assert lane_lines, "intent.md template has no lane: line"


def test_intent_template_lane_line_names_both_values() -> None:
    text = INTENT_TEMPLATE.read_text(encoding="utf-8")
    lane_lines = "\n".join(
        line for line in text.splitlines() if re.search(r"\blane:", line)
    )
    assert "express" in lane_lines
    assert "gate-only" in lane_lines


def test_intent_template_lane_line_is_optional() -> None:
    text = INTENT_TEMPLATE.read_text(encoding="utf-8")
    lane_lines = [
        line for line in text.splitlines() if re.search(r"\blane:", line)
    ]
    assert any("optional" in line for line in lane_lines)


def test_intent_template_documents_switch_grammar() -> None:
    text = INTENT_TEMPLATE.read_text(encoding="utf-8")
    assert SWITCH_GRAMMAR_RE.search(text), (
        "intent.md template does not document the switch grammar "
        "`lane: <name> — switched <YYYY-MM-DD> by <name>, from "
        "<wave <n>|round <n>>`"
    )


def test_intent_template_says_last_line_wins() -> None:
    text = INTENT_TEMPLATE.read_text(encoding="utf-8")
    assert "last line wins" in text


def test_intent_template_says_only_the_user_writes_it() -> None:
    text = INTENT_TEMPLATE.read_text(encoding="utf-8")
    assert "only the user writes it" in text


def test_kickoff_template_carries_a_default_lane_line() -> None:
    text = KICKOFF_TEMPLATE.read_text(encoding="utf-8")
    default_lane_lines = [
        line
        for line in text.splitlines()
        if line.strip().startswith("- default-lane:")
    ]
    assert len(default_lane_lines) == 1, (
        "KICKOFF-DEFAULTS.md template has no single `- default-lane:` line"
    )
    line = default_lane_lines[0]
    assert "full" in line
    assert "express" in line
    assert "gate-only" in line


def test_this_repos_kickoff_defaults_declares_default_lane_full() -> None:
    text = KICKOFF_DEFAULTS.read_text(encoding="utf-8")
    default_lane_lines = [
        line
        for line in text.splitlines()
        if line.strip().startswith("- default-lane:")
    ]
    assert len(default_lane_lines) == 1, (
        "docs/loom/KICKOFF-DEFAULTS.md has no single `- default-lane:` line"
    )
    line = default_lane_lines[0]
    assert re.match(
        r"^- default-lane: full — .+ \(\d{4}-\d{2}-\d{2}\)$", line.strip()
    ), line


def test_default_lane_declared_in_manifest_kickoff_defaults() -> None:
    """W1-01 declares `default-lane` in manifest.yaml's `kickoff_defaults`
    with the three lane values; the templates and this repo's KICKOFF rely
    on that declaration."""
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    entries = {entry["name"]: entry for entry in manifest.get("kickoff_defaults", [])}
    assert "default-lane" in entries
    assert entries["default-lane"]["grammar"] == "full | express | gate-only"


def test_codex_mirror_templates_match_loom_code_originals() -> None:
    for name in ("intent.md", "KICKOFF-DEFAULTS.md"):
        original = (TEMPLATES / name).read_text(encoding="utf-8")
        mirror = (CODEX_TEMPLATES / name).read_text(encoding="utf-8")
        assert original == mirror, f"{name} mirror diverges from the original"
