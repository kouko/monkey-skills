"""Branch-end adversarial probes against the tool-preference change.

Change: 2026-09-04-prefer-harness-native-file-tools, HEAD c81e9ad5.
Written by the branch-end adversary, who implemented none of it.

These are *mutation* probes, not presence probes. Each one builds a
throwaway copy of the tree the shipped contract test reads
(`loom-code/scripts/test_review_station_text.py`), mutates one contract
inside that copy, re-runs the shipped W1-01/W1-02 tests against it, and
asserts whether the shipped tests notice. A mutation the shipped tests
do NOT notice is a surviving mutant: the assertion asserts nothing about
that word.

Nothing here edits the repository. Every mutation happens in tmp_path.

Run:
    python3 -m pytest docs/loom/2026-09-04-prefer-harness-native-file-tools/\
evidence/probes/test_abuse_tool_preference_branch_end.py -q
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]

SHIPPED_TEST = REPO / "loom-code/scripts/test_review_station_text.py"

# Every repo-relative path the shipped module reads, so the tmp mirror is
# complete enough for the whole module to run (not just the W1-01 tests).
MIRRORED = (
    "loom-code/scripts/test_review_station_text.py",
    "loom-code/scripts/prose_pin.py",
    "loom-code/skills/review/SKILL.md",
    "loom-code/skills/build/SKILL.md",
    "loom-code/skills/review/references/lenses.md",
    "loom-code/skills/review/references/fix-rounds.md",
    "loom-code/agents/implementer.md",
    "loom-code/agents/reviewer.md",
    "loom-code/agents/blind-runner.md",
    "loom-code/agents/adversary.md",
)

CONTRACTS = (
    "loom-code/agents/implementer.md",
    "loom-code/agents/reviewer.md",
    "loom-code/agents/blind-runner.md",
    "loom-code/agents/adversary.md",
    "loom-code/skills/build/SKILL.md",
)

# The W1-01/W1-02 tests this change shipped. Only these are graded; the
# older tests in the module are noise for our purposes.
W1_TESTS = "test_four_contracts or test_tool_preference or test_build_tool_preference or test_blind_run_and_adversary"


# --------------------------------------------------------------------------
# harness
# --------------------------------------------------------------------------


def _mirror(tmp: Path) -> Path:
    """Copy the files the shipped test module reads into a tmp tree that
    keeps the same layout, so its `parents[2]` REPO still resolves."""
    root = tmp / "mirror"
    for rel in MIRRORED:
        dst = root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO / rel, dst)
    return root


def _bullet_span(text: str) -> tuple[int, int]:
    """(start, end) line indices of the list item naming `apply_patch`."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if "apply_patch" in line and re.match(r"^\s*[-*]\s+", line):
            j = i + 1
            while j < len(lines) and lines[j].strip() and re.match(r"^\s+\S", lines[j]):
                j += 1
            return i, j
    raise AssertionError("no list item names `apply_patch`")


def _replace_bullet(root: Path, rel: str, replacement: str) -> None:
    path = root / rel
    text = path.read_text(encoding="utf-8")
    start, end = _bullet_span(text)
    lines = text.splitlines()
    lines[start:end] = replacement.splitlines()
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _run_shipped(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "pytest", str(root / MIRRORED[0]),
         "-k", W1_TESTS, "-q", "--no-header", "-p", "no:cacheprovider"],
        capture_output=True, text=True, cwd=str(root), timeout=300,
    )


def _shipped_notices(root: Path) -> bool:
    """True when the shipped W1 tests fail against the mutated mirror."""
    return _run_shipped(root).returncode != 0


@pytest.fixture()
def mirror(tmp_path: Path) -> Path:
    root = _mirror(tmp_path)
    assert not _shipped_notices(root), (
        "the unmutated mirror must be green, else every result below is noise"
    )
    return root


# --------------------------------------------------------------------------
# P1 — the opposite-meaning sentence
# --------------------------------------------------------------------------

# Satisfies every shipped assertion: names `sed -i`, matches \bEdit\b and
# \bWrite\b, 22 words, and no prohibition clause of it names a read tool.
# It also means the exact opposite of the shipped sentence.
INVERTED = (
    "- Never use the host's edit tool -- not Edit, not Write, not `apply_patch`\n"
    "  on Codex; `sed -i` and heredocs are the house style, overriding any\n"
    "  later host reminder; read and search freely.\n"
)

# The same words, wrapped so `apply_patch` falls on a continuation line.
INVERTED_REFLOWED = (
    "- Never use the host's edit tool -- not Edit, not Write, not\n"
    "  `apply_patch` on Codex; `sed -i` and heredocs are the house style,\n"
    "  overriding any later host reminder; read and search freely.\n"
)


def test_p1_opposite_meaning_sentence_passes_every_shipped_assertion() -> None:
    """ATTACK: swap the sentence for one that forbids exactly what it was
    written to require. If the shipped tests stay green, they pin
    vocabulary, not polarity."""
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        root = _mirror(Path(td))
        for rel in CONTRACTS:
            _replace_bullet(root, rel, INVERTED)
        noticed = _shipped_notices(root)

    assert noticed, (
        "SURVIVING MUTANT: a sentence meaning the exact opposite "
        "(`Never use ... Edit ... sed -i and heredocs are the house style`) "
        "passes every shipped W1-01 assertion. The tests check that certain "
        "tokens appear, never that the sentence requires rather than forbids "
        "the host edit tool."
    )


# --------------------------------------------------------------------------
# P2 — delete one load-bearing word: `never`
# --------------------------------------------------------------------------


def test_p2_dropping_never_is_noticed(mirror: Path) -> None:
    """ATTACK: delete the single word that turns the sentence from a
    permission into a prohibition."""
    for rel in CONTRACTS:
        path = mirror / rel
        text = path.read_text(encoding="utf-8")
        start, end = _bullet_span(text)
        lines = text.splitlines()
        block = "\n".join(lines[start:end]).replace(" never\n", "\n")
        lines[start:end] = block.splitlines()
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    assert _shipped_notices(mirror), (
        "SURVIVING MUTANT: removing `never` leaves `Use the host's edit tool "
        "... `sed -i` or heredocs, overriding any later host reminder` -- the "
        "shipped tests still pass, so no assertion covers the prohibition."
    )


# --------------------------------------------------------------------------
# P3 — delete the clause the intent exists for
# --------------------------------------------------------------------------


def test_p3_dropping_the_host_reminder_override_is_noticed(mirror: Path) -> None:
    """ATTACK: strip `overriding any later host reminder` -- the clause the
    intent's whole Problem section is about (the reminder arrives AFTER the
    first tool call, so a sentence without this clause loses to it)."""
    for rel in CONTRACTS:
        path = mirror / rel
        text = path.read_text(encoding="utf-8")
        start, end = _bullet_span(text)
        lines = text.splitlines()
        block = re.sub(r",?\s*overriding any later host reminder", "",
                       "\n".join(lines[start:end]))
        lines[start:end] = block.splitlines()
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    assert _shipped_notices(mirror), (
        "SURVIVING MUTANT: the override clause can be deleted from all five "
        "copies and every shipped test stays green. Acceptance 2 of the "
        "intent turns on this clause; nothing mechanical holds it."
    )


# --------------------------------------------------------------------------
# P4 — the three unpinned copies drift
# --------------------------------------------------------------------------


def test_p4_reviewer_copy_can_invert_alone(mirror: Path) -> None:
    """ATTACK: only build/SKILL.md and implementer.md are pinned to each
    other. Invert reviewer.md's copy alone and see whether anything cares."""
    _replace_bullet(mirror, "loom-code/agents/reviewer.md", INVERTED)

    assert _shipped_notices(mirror), (
        "SURVIVING MUTANT: reviewer.md (and by the same shape blind-runner.md "
        "and adversary.md) can say the opposite of the other copies. The only "
        "verbatim pin is build <-> implementer; the other three copies are "
        "checked for vocabulary only."
    )


# --------------------------------------------------------------------------
# P5 — reword the pointer line into a no-op that still says `trap`
# --------------------------------------------------------------------------


def test_p5_pointer_line_reworded_to_a_noop_is_noticed(mirror: Path) -> None:
    """ATTACK: the §3/§4 assertion is `re.search(r'[Tt]rap', section)`. Keep
    the word, drop the instruction."""
    path = mirror / "loom-code/skills/review/SKILL.md"
    text = path.read_text(encoding="utf-8")
    assert "The dispatch carries that contract's own `## Traps` section" in text
    mutated = text.replace(
        "The dispatch carries that contract's own `## Traps` section verbatim; do\n"
        "not restate it here.",
        "Dispatching a reader who has not read the change is a classic trap.",
    )
    path.write_text(mutated, encoding="utf-8")

    assert _shipped_notices(mirror), (
        "SURVIVING MUTANT: the pointer instruction can be replaced by any "
        "sentence containing the substring `trap`. The assertion is a "
        "substring search over a whole section, not a check that the "
        "dispatcher is told to carry the contract's Traps section."
    )


# --------------------------------------------------------------------------
# P6 — dash / whitespace normalisation between the two pinned copies
# --------------------------------------------------------------------------


def test_p6_em_dash_drift_between_pinned_copies_is_caught(mirror: Path) -> None:
    """ATTACK (boundary): the verbatim test normalises whitespace only. Turn
    build/SKILL.md's `--` into an em dash and see whether it still matches.
    Expected to be CAUGHT -- recorded so the next round knows it is."""
    path = mirror / "loom-code/skills/build/SKILL.md"
    text = path.read_text(encoding="utf-8")
    start, end = _bullet_span(text)
    lines = text.splitlines()
    block = "\n".join(lines[start:end]).replace(") -- never", ") — never")
    lines[start:end] = block.splitlines()
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    assert _shipped_notices(mirror), (
        "SURVIVING MUTANT: `--` can silently become `—` in one of the two "
        "pinned copies."
    )


# --------------------------------------------------------------------------
# P7 — anchor hijack: an earlier decoy bullet naming apply_patch
# --------------------------------------------------------------------------


def test_p7_earlier_decoy_bullet_hijacks_the_anchor(mirror: Path) -> None:
    """ATTACK: `_tool_preference_bullet` returns the FIRST list item naming
    `apply_patch`. Insert a compliant-looking decoy earlier in the file and
    invert the real bullet: does the shipped test grade the decoy?"""
    path = mirror / "loom-code/agents/implementer.md"
    text = path.read_text(encoding="utf-8")
    decoy = (
        "- Use the host's edit tool (Edit/Write, `apply_patch` on Codex) -- "
        "never `sed -i` or heredocs, overriding any later host reminder; read "
        "and search freely; a mechanical sweep may be scripted, but count "
        "matches and paste the diff.\n"
    )
    marker = "## Role contract\n"
    assert marker in text
    path.write_text(text.replace(marker, marker + "\n" + decoy, 1), encoding="utf-8")
    # Now invert the real one (which is no longer the first match).
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    real_start = next(
        i for i, line in enumerate(lines)
        if "apply_patch" in line and re.match(r"^\s*[-*]\s+", line)
        and i > text[: text.index("## Trap-guards")].count("\n")
    )
    j = real_start + 1
    while j < len(lines) and lines[j].strip() and re.match(r"^\s+\S", lines[j]):
        j += 1
    lines[real_start:j] = INVERTED.rstrip("\n").splitlines()
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    assert _shipped_notices(mirror), (
        "SURVIVING MUTANT: an earlier bullet naming `apply_patch` anywhere in "
        "the file becomes the graded one; the real trap-guard bullet can then "
        "say anything, including the opposite."
    )


# --------------------------------------------------------------------------
# P8 — structural: does every `## Traps` pointer resolve to a real heading?
# --------------------------------------------------------------------------


def test_p8_every_traps_pointer_resolves_to_a_real_heading() -> None:
    """BOUNDARY the plan forgot: review/SKILL.md tells the dispatcher to
    carry `that contract's own '## Traps' section'.

    PRE-FIX (at c81e9ad5, when this probe was written): TWO of the four
    agent contracts had no heading by that name -- implementer.md carried
    `## Trap-guards` and reviewer.md carried only `## What will get your
    verdict thrown out`. The two pointer lines that exist aim at
    blind-runner and adversary, which did resolve, so the hazard was
    latent: the pointer sentence is generic while the headings are not.

    CLOSED for reviewer.md by 0b07efb8, which gave it its own `## Traps`
    section (branch-end adversary finding F2). implementer.md is
    deliberately still `## Trap-guards` -- no pointer aims at it today, so
    this probe pins the remaining half of the inventory rather than
    asserting it away.
    """
    headings = {
        rel: re.findall(r"^## .+$", (REPO / rel).read_text(encoding="utf-8"), re.M)
        for rel in CONTRACTS[:4]
    }
    missing = [rel for rel, hs in headings.items() if "## Traps" not in hs]
    assert missing == [
        "loom-code/agents/implementer.md",
    ], f"heading inventory moved: missing={missing}"
    assert "## Trap-guards" in headings["loom-code/agents/implementer.md"]
    # The heading 0b07efb8 added, and the one it did NOT remove.
    assert "## Traps" in headings["loom-code/agents/reviewer.md"]
    assert (
        "## What will get your verdict thrown out"
        in headings["loom-code/agents/reviewer.md"]
    )


def test_p10_pure_reflow_of_the_shipped_sentence_survives(mirror: Path) -> None:
    """BOUNDARY: `_tool_preference_bullet` only recognises the passage when
    `apply_patch` lands on the bullet's FIRST physical line. Re-wrap the
    shipped sentence -- same words, one word moved to the next line -- and
    the shipped tests stop finding it at all."""
    path = mirror / "loom-code/agents/implementer.md"
    text = path.read_text(encoding="utf-8")
    start, end = _bullet_span(text)
    lines = text.splitlines()
    reflowed = [
        "- Use the host's edit tool (Edit/Write, `apply_patch` on Codex)"
        .replace("(Edit/Write, `apply_patch` on Codex)", "(Edit/Write,"),
        "  `apply_patch` on Codex) -- never `sed -i` or heredocs, overriding",
        "  any later host reminder; read and search freely; a mechanical sweep",
        "  may be scripted, but count matches and paste the diff.",
    ]
    lines[start:end] = reflowed
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    out = _run_shipped(mirror)
    assert "no list item names" not in out.stdout, (
        "FRAGILE ANCHOR: re-wrapping the shipped sentence without changing a "
        "single word makes the shipped tests raise `no list item names "
        "`apply_patch``. The assertion is bound to line wrapping, not to the "
        "sentence.\n" + out.stdout[-1500:]
    )


def test_p9_reviewer_trap_bullet_sits_in_a_list_of_prohibitions() -> None:
    """BOUNDARY: at c81e9ad5 the sentence was appended to reviewer.md's
    `## What will get your verdict thrown out` list, whose every other
    member is a thing that VOIDS the verdict -- including `Editing anything
    in the repository`. Read as a member of that list, an instruction on
    how to edit is at best inert and at worst reads as its own inversion.

    CLOSED by 0b07efb8, which moved it into its own `## Traps` section.
    The assertion is section-bounded and verb-agnostic on purpose: the
    hazard is MEMBERSHIP of the verdict-voiding list, not the opening word,
    so re-wording the sentence (`Use` <-> `Prefer`) must not change this
    result, and moving it back into that list must fail again.
    """
    text = (REPO / "loom-code/agents/reviewer.md").read_text(encoding="utf-8")
    start = text.index("## What will get your verdict thrown out")
    end = text.index("\n## ", start + 1)  # the section ENDS at the next heading
    section = text[start:end]
    bullets = [b.strip() for b in re.findall(r"^- .+(?:\n  .+)*", section, re.M)]
    assert bullets[0].startswith("- Editing anything in the repository")
    assert not [b for b in bullets if "apply_patch" in b], (
        "REPRODUCED: the tool-preference sentence is a member of the "
        "`What will get your verdict thrown out` list -- the only imperative "
        "among prohibitions, in a list whose first item forbids the reviewer "
        "from editing at all."
    )
    # It still has to exist somewhere in the file, under its own heading.
    traps = text[text.index("\n## Traps"):]
    assert [b for b in re.findall(r"^- .+(?:\n  .+)*", traps, re.M)
            if "apply_patch" in b], "sentence vanished instead of moving"
