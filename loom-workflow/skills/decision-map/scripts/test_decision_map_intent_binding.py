"""The Map binds a delivery arc to an intent, and to nothing else.

Loom 1.0 deleted the delivery ticket, its Brief, and the backlog store the
old boundary contract governed. These tests pin the replacement contract on
the prose side — the surface a model actually reads — so the vocabulary
cannot drift back.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SKILL_MD = SKILL_DIR / "SKILL.md"
MAP_FORMAT_MD = SKILL_DIR / "references" / "map-format.md"
REPO_ROOT = SKILL_DIR.parents[2]

CONTRACTS = (SKILL_MD, MAP_FORMAT_MD)

# Vocabulary the hard switch deleted. `brief` survives only where the prose
# marks a pre-1.0 ticket as legacy, so the ban is on the live instructions.
DELETED_VOCABULARY = ("seed", "phase ledger", "backlog")


def _flat(text: str) -> str:
    return " ".join(text.split())


def test_start_delivery_writes_an_intent_not_a_brief():
    skill = _flat(SKILL_MD.read_text(encoding="utf-8"))
    assert "docs/loom/intent/<change-id>.md" in skill
    assert "originator: map:<map-id>" in skill
    assert "map: <map-id>" in skill
    assert "start_delivery.py" in skill


def test_delivery_state_derives_from_the_intent_status():
    skill = _flat(SKILL_MD.read_text(encoding="utf-8"))
    assert "Delivery state is derived from the intent's own `status:` field" in skill
    for status in ("`open`", "`confirmed <date>`", "`closed`", "`withdrawn"):
        assert status in skill
    assert "The Map is read-only on intents" in skill
    assert "retired — <reason>" in skill


def test_map_lists_the_change_id_under_its_criterion():
    map_format = _flat(MAP_FORMAT_MD.read_text(encoding="utf-8"))
    assert (
        "`- delivery-intent: DA-<n> | docs/loom/intent/<change-id>.md`" in map_format
    )
    assert "opens no second arc" in map_format
    assert "replacement intent" in map_format


def test_no_delivery_ticket_is_authored_any_more():
    for path in CONTRACTS:
        text = path.read_text(encoding="utf-8")
        assert "Exactly three ticket closure types exist" in text, path
        assert "|delivery>" not in text, path


def test_deleted_vocabulary_is_gone_from_the_live_contract():
    for path in CONTRACTS:
        lowered = path.read_text(encoding="utf-8").lower()
        for word in DELETED_VOCABULARY:
            assert word not in lowered, f"{path} still says {word!r}"


def test_no_reference_to_a_deleted_upstream_skill():
    for path in CONTRACTS:
        text = path.read_text(encoding="utf-8")
        for skill in ("loom-code:writing-plans", "loom-code:brainstorming"):
            assert skill not in text, f"{path} points at deleted {skill}"


def test_citation_checker_scans_loom_workflow():
    """The contract-citation gate covers the loom-workflow plugin tree."""
    checker_path = REPO_ROOT / "loom-code" / "scripts" / "check_contract_citations.py"
    spec = importlib.util.spec_from_file_location("ccc", checker_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert ("loom-workflow/skills", True) in module._SCOPE_DIRS
