"""Tests for Loom agent profiles under dispatch-time resolution.

The four current role contracts carry neither a static model nor effort pin.
Before each host-native spawn, the station resolves the shared portable pair
from current task evidence and host capabilities. The effective result is
retained in active task context only; there is no committed dispatch ledger.

The assertion covers the whole ``agents/`` directory rather than a hand list,
so a new contract cannot silently bypass dispatch-time resolution.
"""
from pathlib import Path

AGENTS_DIR = Path(__file__).resolve().parent.parent / "agents"

ROLES = ["implementer", "reviewer", "blind-runner", "adversary"]


def _frontmatter(agent_name):
    text = (AGENTS_DIR / f"{agent_name}.md").read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{agent_name}.md missing frontmatter opening fence"
    end = text.index("\n---", 4)
    return text[4:end]


def test_the_agent_population_is_the_four_station_roles():
    assert sorted(p.stem for p in AGENTS_DIR.glob("*.md")) == sorted(ROLES)


def test_no_agent_pins_model_or_effort():
    for path in sorted(AGENTS_DIR.glob("*.md")):
        frontmatter = _frontmatter(path.stem)
        for field in ("model:", "effort:"):
            assert field not in frontmatter, (
                f"{path.name} frontmatter must resolve {field[:-1]} at dispatch time"
            )


def test_module_contract_rejects_retired_dispatch_ledger_wording():
    documentation = (__doc__ or "").lower()

    assert "review.json" not in documentation
    assert "dispatch[]" not in documentation
    assert "dispatch-time resolution" in documentation
    assert "active task context only" in documentation
