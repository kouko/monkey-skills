"""W2-01 — one language sentence per station, six stations.

Each of the six stations that own an artifact under this change's language
policy carries one sentence in its own SKILL.md naming both "English" and
the station's own artifact noun(s). These tests pin the presence and shape
of that sentence per station, mirroring
test_codex_trust_station_text.py's shape: resolve REPO via
`git rev-parse`, read each SKILL.md, split into sentences, and assert one
sentence carries the required facts.

Graduates evidence/probes/test_abuse_language_policy.py's
`test_stations_english_absent` case into the package suite with per-station
granularity and the extra station-specific facts (Conventional Comments
for review, EARS/REQ- for write-spec, "user's language" for capture-intent
and ship) that the looser probe does not check.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

_REPO_RESULT = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"],
    capture_output=True,
    text=True,
    check=True,
)
REPO = Path(_REPO_RESULT.stdout.strip())

WRITE_PLAN_SKILL = REPO / "loom-code" / "skills" / "write-plan" / "SKILL.md"
BUILD_SKILL = REPO / "loom-code" / "skills" / "build" / "SKILL.md"
REVIEW_SKILL = REPO / "loom-code" / "skills" / "review" / "SKILL.md"
SHIP_SKILL = REPO / "loom-code" / "skills" / "ship" / "SKILL.md"
CAPTURE_INTENT_SKILL = REPO / "loom-design" / "skills" / "capture-intent" / "SKILL.md"
WRITE_SPEC_SKILL = REPO / "loom-design" / "skills" / "write-spec" / "SKILL.md"

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def _sentences(text: str) -> list[str]:
    """Split text into sentences after collapsing newlines to spaces —
    same normalization the plan's own probe file uses, so a sentence that
    line-wraps in the SKILL.md source still reads as one unit here."""
    flat = " ".join(text.split())
    return [p for p in _SENTENCE_SPLIT.split(flat) if p.strip()]


def _matching_sentences(path: Path, required_substrings: list[str]) -> list[str]:
    text = path.read_text(encoding="utf-8")
    lowered_required = [s.lower() for s in required_substrings]
    return [
        s for s in _sentences(text)
        if all(req in s.lower() for req in lowered_required)
    ]


def test_writeplan_languageSentence_present() -> None:
    """The write-plan SKILL.md must carry a sentence naming English
    together with 'plan', the station's own artifact noun."""
    hits = _matching_sentences(WRITE_PLAN_SKILL, ["english", "plan"])
    assert hits, "write-plan/SKILL.md has no sentence naming English + plan"


def test_build_languageSentence_present() -> None:
    """The build SKILL.md must carry a sentence naming English together
    with one of its artifact nouns: plan, probe, commit or spec."""
    text = BUILD_SKILL.read_text(encoding="utf-8")
    nouns = ("plan", "probe", "commit", "spec")
    hits = [
        s for s in _sentences(text)
        if "english" in s.lower() and any(n in s.lower() for n in nouns)
    ]
    assert hits, "build/SKILL.md has no sentence naming English + an artifact noun"


def test_review_conventionalCommentsSentence_present() -> None:
    """The review SKILL.md must carry a sentence naming English, one of
    its artifact nouns, and the Conventional Comments label requirement
    on finding text."""
    text = REVIEW_SKILL.read_text(encoding="utf-8")
    nouns = ("review.json", "findings", "evidence", "probe")
    hits = [
        s for s in _sentences(text)
        if "english" in s.lower()
        and "conventional comments" in s.lower()
        and any(n in s.lower() for n in nouns)
    ]
    assert hits, (
        "review/SKILL.md has no sentence naming English + an artifact noun + "
        "Conventional Comments"
    )


def test_ship_userLanguageSentence_present() -> None:
    """The ship SKILL.md must carry a sentence naming English, one of its
    artifact nouns, and the phrase 'user's language' for the artifacts
    that stay untranslated."""
    text = SHIP_SKILL.read_text(encoding="utf-8")
    nouns = ("pr body", "pull-request body", "commit", "report")
    hits = [
        s for s in _sentences(text)
        if "english" in s.lower()
        and "user's language" in s.lower()
        and any(n in s.lower() for n in nouns)
    ]
    assert hits, (
        "ship/SKILL.md has no sentence naming English + an artifact noun + "
        "user's language"
    )


def test_captureintent_userLanguageSentence_present() -> None:
    """The capture-intent SKILL.md must carry a sentence naming English,
    'intent', and the phrase 'user's language'."""
    hits = _matching_sentences(
        CAPTURE_INTENT_SKILL, ["english", "intent", "user's language"]
    )
    assert hits, (
        "capture-intent/SKILL.md has no sentence naming English + intent + "
        "user's language"
    )


def test_writespec_earsSentence_present() -> None:
    """The write-spec SKILL.md must carry a sentence naming English,
    'spec', 'EARS' and 'REQ-'."""
    hits = _matching_sentences(WRITE_SPEC_SKILL, ["english", "spec", "ears", "req-"])
    assert hits, (
        "write-spec/SKILL.md has no sentence naming English + spec + EARS + REQ-"
    )
