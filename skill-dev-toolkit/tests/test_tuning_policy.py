"""Keep human agreement and adoption rules consistent across tuning instructions."""

import importlib.util
from pathlib import Path
import re


SKILL = Path(__file__).resolve().parents[1] / "skills" / "skill-tuning"
spec = importlib.util.spec_from_file_location("tuning_harness", SKILL / "scripts/ab_harness.py")
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)


def affirmative(text, pattern):
    return any(re.search(pattern, sentence) and not re.search(
        r"\b(?:no|not|never|don't|cannot)\b", sentence, re.I
    ) for sentence in re.split(r"(?<=[.!?])\s+", " ".join(text.split())))


def test_human_decision_policy():
    pattern = r"Use .*70%.*agreement"
    assert affirmative("Use at least 70% agreement.", pattern)
    assert not affirmative("Do not Use at least 70% agreement.", pattern)
    for path, heading in (("SKILL.md", "### Phase 3:"),
                          ("references/ab-harness-protocol.md", "## Multi-evaluator")):
        scope = (SKILL / path).read_text().split(heading, 1)[1].split("\n##", 1)[0]
        assert affirmative(scope, pattern)
        assert affirmative(scope, r"Escalate .*2/3")
        assert affirmative(scope, r"Allow .*3/4.*majority")
        assert "⅔" not in scope
    labels = {"A": {"identity": "baseline"}, "B": {"identity": "variant_1"}}
    assert harness.parse_pick("b", labels) == {
        "type": "single", "label": "B", "identity": "variant_1"}
    text = (SKILL / "SKILL.md").read_text()
    adopt = next(row for row in text.splitlines() if "**ADOPT**" in row)
    assert "locked single" in adopt and "Apply" in adopt


def test_ties_never_adopt():
    protocol = (SKILL / "references/ab-harness-protocol.md").read_text()
    fallback = next(row for row in protocol.splitlines() if "All variants picked equally" in row)
    assert "DEFER" in fallback and "record" in fallback and "ADOPT" not in fallback
    atomicity = protocol.split("## Atomicity / lock-in", 1)[1].split("\n##", 1)[0]
    pattern = r"Apply .*only for a locked single non-baseline ADOPT"
    assert affirmative("Apply edit only for a locked single non-baseline ADOPT.", pattern)
    assert not affirmative("Never Apply edit only for a locked single non-baseline ADOPT.", pattern)
    assert affirmative(atomicity, pattern)
    assert "Within that ADOPT branch" in atomicity and "git commit" in atomicity
    assert affirmative(atomicity, r"For DROP, DEFER, REFINE, or ESCALATE, preserve the current skill")
    for path in ("SKILL.md", "references/ab-harness-protocol.md"):
        text = (SKILL / path).read_text()
        row = next(row for row in text.splitlines() if row.startswith("| ") and "DEFER" in row)
        assert "Multiple" in row or '"Both"' in row
    labels = {"A": {"identity": "baseline"}, "B": {"identity": "variant_1"}}
    for raw, kind in (("a+b", "multiple"), ("n", "none"), ("r", "refine")):
        assert harness.parse_pick(raw, labels)["type"] == kind
