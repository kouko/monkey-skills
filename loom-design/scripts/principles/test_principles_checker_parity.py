"""The two counters that decide "is this PRINCIPLES.md ratified" must agree.

`validate_principles_output.py` (authoring side, loom-design) and
`loom_checker.py`'s `unratified_reason()` (gate side, loom-code) recompute
the SAME question — does `## Non-negotiables` carry three substantive,
distinct items — from two codebases that cannot import each other. Byte-
equivalent logic is the intent; this test is what keeps it true, by running
both over one fixture table and comparing verdicts.

Scope: the non-negotiables count only. The authoring validator is stricter
elsewhere on purpose (the five required sections, a real `ratified-by:`
date), so every fixture below is otherwise well-formed and varies only in
the Non-negotiables body.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from validate_principles_output import validate

REPO_ROOT = Path(__file__).resolve().parents[3]
CHECKER = REPO_ROOT / "loom-code" / "scripts" / "loom_checker.py"

INTENT = """# A change
originator: tester
kind: product
needs-design: no — internal only
status: confirmed 2026-09-02

## Problem
People who use the nightly report wait ten minutes and give up.

## Proposed outcome
Make it fast.

## Acceptance
1. After this I can open the report in under a minute.

## Constraints
- Stay inside the existing tool.

## Out of scope
- Everything else.

## Open questions
- None yet.
"""

PRINCIPLES = """# Product principles
{ratified}
## Who
Solo developers tracking personal tasks.
## Non-negotiables (ordered)
{items}## Won't do
- Team features.
## Failure we must avoid
Silent data loss on crash.
## Fixed choices
- CLI only, no GUI planned.
"""

FIXTURES = {
    "three distinct substantive items": [
        "saving works with the network off",
        "never require a sign-up",
        "one plain-text file holds everything",
    ],
    "three identical items": ["it must be fast"] * 3,
    "three items differing only in case and punctuation": [
        "It must be fast.", "it must be fast", "IT MUST BE FAST!",
    ],
    "one-word slogans": ["x", "y", "z"],
    "two-word items": ["be fast", "stay local", "no accounts"],
    "two substantive items": [
        "saving works with the network off",
        "never require a sign-up",
    ],
    "four items, two of them duplicates": [
        "saving works with the network off",
        "saving works with the network off",
        "never require a sign-up",
    ],
    "no items at all": [],
}


SUBSTANTIVE = [
    "saving works with the network off",
    "never require a sign-up",
    "one plain-text file holds everything",
]

# The signature line is the other half of "ratified" (concept-model §8), and
# the two implementations have to agree on it too: a placeholder is not a
# signature, and a date that does not exist is not a date.
RATIFIED_LINES = {
    "a name and a real date": ("ratified-by: kouko 2026-09-03", True),
    "a placeholder instead of a name and date": (
        "ratified-by: pending — kouko to confirm", False,
    ),
    "a date that does not exist": ("ratified-by: kouko 2026-13-45", False),
    "a name with no date": ("ratified-by: kouko", False),
}


def _principles(items: list[str], ratified: str = "ratified-by: Alex Rivera 2026-09-02") -> str:
    return PRINCIPLES.format(
        ratified=ratified, items="".join(f"- {item}\n" for item in items)
    )


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=True)


def _checker_says_ratified(tmp_path: Path, text: str) -> bool:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "T")
    intent = repo / "docs/loom/intent/2026-09-02-a.md"
    intent.parent.mkdir(parents=True, exist_ok=True)
    intent.write_text(INTENT, encoding="utf-8")
    (repo / "PRINCIPLES.md").write_text(text, encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(CHECKER), "standing", str(intent)],
        capture_output=True, text=True, cwd=str(repo),
    )
    assert result.returncode in (0, 1), result.stderr
    return result.returncode == 0


@pytest.mark.parametrize("label", sorted(RATIFIED_LINES))
def test_both_implementations_agree_on_the_signature_line(tmp_path: Path, label: str) -> None:
    line, expected = RATIFIED_LINES[label]
    text = _principles(SUBSTANTIVE, ratified=line)
    path = tmp_path / "PRINCIPLES.md"
    path.write_text(text, encoding="utf-8")
    authoring_ok, problems = validate(path)
    gate_ok = _checker_says_ratified(tmp_path, text)
    assert authoring_ok == gate_ok == expected, (label, problems)


@pytest.mark.parametrize("label", sorted(FIXTURES))
def test_both_implementations_reach_the_same_verdict(tmp_path: Path, label: str) -> None:
    text = _principles(FIXTURES[label])
    path = tmp_path / "PRINCIPLES.md"
    path.write_text(text, encoding="utf-8")
    authoring_ok, problems = validate(path)
    gate_ok = _checker_says_ratified(tmp_path, text)
    assert authoring_ok == gate_ok, (label, problems)


def test_the_table_covers_both_verdicts() -> None:
    """A parity table that only ever expects one answer proves nothing."""
    assert len(FIXTURES) >= 2
