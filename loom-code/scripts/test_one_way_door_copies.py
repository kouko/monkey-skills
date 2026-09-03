"""W2 F4 — the one-way-door rule lives in three prose copies; pin them together.

`loom-code/skills/write-plan/references/one-way-door.md` is the source of
truth: it names the five classes (a)-(e) and the four gates. Two stations in
`loom-design` cannot read that file at run time — plugins cannot read each
other's files — so each carries its own restatement of the same rule inside
its decision-point step.

Three hand-maintained copies of a rule that decides *what the user is asked*
is exactly the shape that drifts silently: a class renamed in one copy, or a
gate dropped from another, changes which questions reach the user, and no
station's own suite would ever see the other plugin's text. This test reads
the five class titles out of the reference and requires each of them, and
each of the four gate names, to appear in both copies.

Titles are compared with whitespace collapsed and case folded, because the
copies wrap the same sentence differently and start it lower-case mid-list.
Nothing else is normalised: a reworded class title fails here, which is the
point — reword the reference and the copies together, or not at all.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
REFERENCE = REPO / "loom-code" / "skills" / "write-plan" / "references" / "one-way-door.md"
COPIES = [
    REPO / "loom-design" / "skills" / "capture-intent" / "SKILL.md",
    REPO / "loom-design" / "skills" / "write-spec" / "SKILL.md",
]

# The four gates, in the order the reference gives them. The copies write
# them as a running sentence ("check the intent's Acceptance ... measure
# first ... threshold ... merge"), so only the gate word itself is pinned.
GATE_NAMES = ("check", "measure", "threshold", "merge")


def normalise(text: str) -> str:
    """Case-folded, whitespace-collapsed, with markdown emphasis removed."""
    return re.sub(r"\s+", " ", text.replace("*", "")).casefold()


def class_titles() -> dict[str, str]:
    """The five class titles, keyed by letter, read out of the reference.

    A class is a bullet of the shape `- **(a) Hard to swap later** — ...`;
    the title is everything between the letter and the em dash.
    """
    titles = {}
    for line in REFERENCE.read_text(encoding="utf-8").splitlines():
        match = re.match(r"\s*-\s*\*\*\(([a-e])\)\s*(.+?)\*\*\s*—", line)
        if match:
            titles[match.group(1)] = match.group(2).strip()
    return titles


REFERENCE_TITLES = class_titles()


def test_the_reference_still_defines_five_classes():
    assert sorted(REFERENCE_TITLES) == ["a", "b", "c", "d", "e"], (
        f"{REFERENCE.relative_to(REPO)} must define classes (a)-(e); found "
        f"{sorted(REFERENCE_TITLES)}. If a class was added or removed, this "
        "test and both copies move with it."
    )


@pytest.mark.parametrize("copy", COPIES, ids=lambda p: p.parent.name)
@pytest.mark.parametrize("letter", ["a", "b", "c", "d", "e"])
def test_every_copy_carries_the_same_class_title(copy: Path, letter: str):
    title = REFERENCE_TITLES[letter]
    haystack = normalise(copy.read_text(encoding="utf-8"))
    needle = normalise(f"({letter}) {title}")
    assert needle in haystack, (
        f"{copy.relative_to(REPO)} does not carry class ({letter}) under the "
        f"title the reference gives it ({title!r}). The three copies decide "
        "which choices reach the user; a renamed class in one of them is a "
        "silently different rule."
    )


@pytest.mark.parametrize("copy", COPIES, ids=lambda p: p.parent.name)
@pytest.mark.parametrize("gate", GATE_NAMES)
def test_every_copy_names_all_four_gates(copy: Path, gate: str):
    haystack = normalise(copy.read_text(encoding="utf-8"))
    assert gate in haystack, (
        f"{copy.relative_to(REPO)} never names the {gate!r} gate. All four "
        f"gates {GATE_NAMES} decide whether a one-way door is asked at all; a "
        "copy missing one asks the user a question the reference says to skip, "
        "or skips one it says to ask."
    )
