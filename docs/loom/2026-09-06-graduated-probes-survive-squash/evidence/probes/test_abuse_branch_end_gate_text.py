"""Executable six-class attack catalogue for the changed skill and mirror gate."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[5]
SKILL = ROOT / "loom-code/skills/build/SKILL.md"
CHECKER = ROOT / "loom-code/scripts/loom_checker.py"
MIRROR = ROOT / ".codex/hooks/loom_checker.py"
TEMPTATIONS = (
    "the diff is one line, proceed?",
    "skip if trivial",
    "the plan says Safety-bearing: no",
    "proceed if the diff is one line",
)
NEGATION = re.compile(r"\b(?:no|not|never|neither|nor|without|cannot|can't|don't|doesn't|isn't|won't)\b", re.I)


def gated_sentence(text: str) -> str:
    start = text.index("<!-- gate: build.rehearsal-before-graduation -->")
    end = text.index("<!-- /gate -->", start)
    gated = " ".join(text[start:end].split())
    sentences = re.split(r"(?<=[.!?])\s+", gated)
    hits = [sentence for sentence in sentences if "squash" in sentence.lower()]
    assert hits
    return hits[0]


def accepts_rule(sentence: str) -> bool:
    """Accept only an affirmative two-shape obligation, not a negated imitation."""
    lowered = sentence.lower()
    required = ("squash", "trunk", "commit")
    affirmative = "runs" in lowered or "rehearses" in lowered
    return affirmative and all(word in lowered for word in required) and not NEGATION.search(sentence)


def test_gate_forgedartifact_refuses(tmp_path: Path) -> None:
    """Forge: a hand-written PASS record cannot replace the sentence's executable two-shape command."""
    forged = tmp_path / "review.json"
    forged.write_text('{"result":"pass","claim":"squashed rehearsal ran"}\n', encoding="utf-8")
    sentence = gated_sentence(SKILL.read_text(encoding="utf-8"))
    assert accepts_rule(sentence)
    assert "rehearse_probes.py" in SKILL.read_text(encoding="utf-8")
    assert forged.read_text(encoding="utf-8") not in sentence


def test_gate_editedinput_refuses(tmp_path: Path) -> None:
    """Bypass: editing the sentence to name only the CI-shaped run must fail the prose matcher."""
    original = gated_sentence(SKILL.read_text(encoding="utf-8"))
    edited = original.replace("the branch squashed to one commit off its trunk", "the CI-shaped clone")
    assert accepts_rule(original)
    assert not accepts_rule(edited)


def test_gate_staleartifact_refuses(tmp_path: Path) -> None:
    """Replay: a stale pre-change sentence must not satisfy the current two-shape obligation."""
    stale = tmp_path / "stale.txt"
    stale.write_text("The rehearsal runs the CI-shaped clone.\n", encoding="utf-8")
    assert accepts_rule(gated_sentence(SKILL.read_text(encoding="utf-8")))
    assert not accepts_rule(stale.read_text(encoding="utf-8"))


def test_gate_trustboundary_matches(tmp_path: Path) -> None:
    """Boundary: the scaffolded checker must remain a byte mirror except for its banner line."""
    source = CHECKER.read_text(encoding="utf-8").splitlines()
    mirror = MIRROR.read_text(encoding="utf-8").splitlines()
    assert mirror[0] == source[0]
    # The banner carries the plugin version -- recompute it rather than pin
    # the value of the day, which goes red at the next bump.
    version = json.loads(
        (CHECKER.parents[1] / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
    )["version"]
    assert mirror[1] == f"# loom-checker {version}"
    assert mirror[2:] == source[1:]


def test_gate_proseexemption_refuses(tmp_path: Path) -> None:
    """Self-exemption: every catalogue temptation is refused verbatim by the affirmative rule."""
    rule = gated_sentence(SKILL.read_text(encoding="utf-8"))
    assert accepts_rule(rule)
    for temptation in TEMPTATIONS:
        attempted = temptation
        assert not accepts_rule(attempted)
        assert temptation not in rule.lower()


def test_gate_concurrentwriter_detects(tmp_path: Path) -> None:
    """Race: interleaved skill snapshots must detect that one writer lost the squashed sentence."""
    path = tmp_path / "SKILL.md"
    current = SKILL.read_text(encoding="utf-8")
    path.write_text(current, encoding="utf-8")
    first = path.read_text(encoding="utf-8")
    second = path.read_text(encoding="utf-8")
    raced = re.sub(
        r"the branch squashed to one commit off\s+its trunk",
        "the CI-shaped clone",
        second,
    )
    path.write_text(raced, encoding="utf-8")
    assert accepts_rule(gated_sentence(first))
    assert not accepts_rule(gated_sentence(path.read_text(encoding="utf-8")))


def test_gate_matcher_selftests_expected(tmp_path: Path) -> None:
    """Synthetic controls prove the matcher accepts affirmation and rejects negation."""
    affirmative = "The rehearsal runs the branch squashed to one commit off its trunk."
    negated = "The rehearsal does not run the branch squashed to one commit off its trunk."
    assert accepts_rule(affirmative)
    assert not accepts_rule(negated)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
