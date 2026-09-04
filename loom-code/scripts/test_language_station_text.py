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


# Round-2 finding (rev-be-codex, branch-end): co-locating keywords in a
# sentence is not discriminating — "The plan is not written in English"
# satisfies a plain substring check on "english" + "plan". A qualifying
# sentence must instead contain an affirmative English form and carry no
# negation anywhere in the sentence; mirrors
# evidence/probes/test_abuse_language_policy.py's `_has_negation` /
# affirmative-sentence pattern.
_NEGATION_RE = re.compile(r"\b(?:not|never|no)\b|n't", re.IGNORECASE)
_ENGLISH_AFFIRM_PHRASES = ("in english", "is english", "are english", "written in english")
_USER_LANGUAGE_AFFIRM_PHRASES = (
    "stays in the user's language",
    "stay in the user's language",
    "in the user's language",
)


def _has_negation(sentence: str) -> bool:
    """True iff `sentence` contains a word-boundary negation token — 'not',
    'never' or 'no' as whole words, or an "n't" contraction. Plain
    substring matching would false-positive on ordinary words ('note',
    'know'), so the regex requires a word boundary on both sides."""
    return bool(_NEGATION_RE.search(sentence))


def _has_affirmative_english(sentence: str) -> bool:
    """True iff `sentence` contains one of the affirmative English forms
    ('in English', 'is English', 'are English', 'written in English') and
    carries no negation anywhere in the sentence."""
    lowered = sentence.lower()
    if not any(phrase in lowered for phrase in _ENGLISH_AFFIRM_PHRASES):
        return False
    return not _has_negation(sentence)


def _has_affirmative_user_language(sentence: str) -> bool:
    """True iff `sentence` contains an affirmative user's-language form
    ('stays/stay in the user's language', or the bare 'in the user's
    language') and carries no negation anywhere in the sentence."""
    lowered = sentence.lower()
    if not any(phrase in lowered for phrase in _USER_LANGUAGE_AFFIRM_PHRASES):
        return False
    return not _has_negation(sentence)


def _matching_sentences(
    path: Path,
    required_substrings: list[str],
    require_affirmative_user_language: bool = False,
) -> list[str]:
    """Sentences that contain every required substring, an affirmative
    English form, and no negation. When `require_affirmative_user_language`
    is set, the same sentence must also carry an affirmative user's-language
    form with no negation."""
    text = path.read_text(encoding="utf-8")
    lowered_required = [s.lower() for s in required_substrings]
    hits = []
    for s in _sentences(text):
        if not all(req in s.lower() for req in lowered_required):
            continue
        if not _has_affirmative_english(s):
            continue
        if require_affirmative_user_language and not _has_affirmative_user_language(s):
            continue
        hits.append(s)
    return hits


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
        and _has_affirmative_english(s)
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
        and _has_affirmative_english(s)
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
        and _has_affirmative_english(s)
        and _has_affirmative_user_language(s)
    ]
    assert hits, (
        "ship/SKILL.md has no sentence naming English + an artifact noun + "
        "user's language"
    )


def test_captureintent_userLanguageSentence_present() -> None:
    """The capture-intent SKILL.md must carry a sentence naming English,
    'intent', and the phrase 'user's language'."""
    hits = _matching_sentences(
        CAPTURE_INTENT_SKILL,
        ["english", "intent", "user's language"],
        require_affirmative_user_language=True,
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


# --- synthetic self-tests for the negation-aware matcher --------------------


def test_matcher_affirmativeSentence_accepted() -> None:
    """A real station sentence — ship's English + user's-language predicate
    — must be accepted by both affirmative-form helpers: the discriminating
    check must not reject real, correctly-written station prose."""
    text = SHIP_SKILL.read_text(encoding="utf-8")
    candidates = [
        s for s in _sentences(text)
        if "english" in s.lower() and "user's language" in s.lower()
    ]
    assert candidates, "expected to find ship's English/user-language sentence"
    assert any(
        _has_affirmative_english(s) and _has_affirmative_user_language(s)
        for s in candidates
    ), "ship's real sentence was rejected by the affirmative-form helpers"


def test_matcher_negatedSentence_rejected() -> None:
    """'The plan is not written in English' co-locates the affirmative
    form 'written in English' with 'plan', but the negation token 'not'
    must reject it — the discriminating case this fix closes."""
    sentence = "The plan is not written in English."
    assert not _has_affirmative_english(sentence)


def test_matcher_shipPredicate_negatedSentence_rejected() -> None:
    """'The report is written in English, never in the user's language'
    satisfies both affirmative-form substring checks in isolation, but
    carries the negation token 'never' in the same sentence — both
    helpers must reject it, mirroring the ship predicate's combined
    check."""
    sentence = "The report is written in English, never in the user's language."
    assert not _has_affirmative_english(sentence)
    assert not _has_affirmative_user_language(sentence)
