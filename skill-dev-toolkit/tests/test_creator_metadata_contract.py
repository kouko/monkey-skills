"""Creator grading instructions share case metadata across run-local results."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1] / "skills/skill-creator-advance"
SCHEMAS = (ROOT / "references/schemas.md").read_text()
METADATA = SCHEMAS.split("## eval_metadata.json\n", 1)[1].split("\n## ", 1)[0]
GRADING = SCHEMAS.split("## grading.json\n", 1)[1].split("\n## ", 1)[0]


def affirmative_source(text):
    return any(
        re.search(r"\breads\b.*explicit.*path.*case.*eval_metadata\.json", sentence)
        and not re.search(r"\b(?:not|never|no|without)\b", sentence, re.I)
        for sentence in re.split(r"(?<=[.!?])\s+(?=[A-Z*])", text)
    )


def test_shared_case_metadata():
    assert "<workspace>/iteration-<N>/eval-<ID>/eval_metadata.json" in METADATA
    grader = (ROOT / "agents/grader.md").read_text()
    assert "Path to eval_metadata.json" in grader
    assert "Load eval_metadata.json from the test case directory" in grader
    assert affirmative_source(GRADING)
    assert affirmative_source(
        "The grader reads assertions from the explicitly supplied path to the case's eval_metadata.json."
    )
    assert not affirmative_source(
        "The grader never reads assertions from the explicitly supplied path to the case's eval_metadata.json."
    )


def test_run_local_metadata_not_required():
    assert "<run-dir>/eval_metadata.json" not in GRADING
    assert "Located at `<run-dir>/grading.json`" in GRADING
    assert re.search(r"shared across.*configurations.*repeat runs", METADATA)
    protocol = (ROOT / "references/eval-protocol.md").read_text()
    assert "Write an `eval_metadata.json` per test case" in protocol
    assert "with_skill/run-<R>/outputs/" in protocol
