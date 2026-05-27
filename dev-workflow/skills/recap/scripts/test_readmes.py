"""
Tests for the tri-language README triplet of the recap skill.

RED check:  test_tri_lang_readmes_consistent MUST FAIL before READMEs exist.
GREEN check: all assertions pass once README.md / README.ja.md / README.zh-TW.md land.
"""
import re
from pathlib import Path

SKILL_ROOT = Path(__file__).parent.parent  # dev-workflow/skills/recap/

README_EN   = SKILL_ROOT / "README.md"
README_JA   = SKILL_ROOT / "README.ja.md"
README_ZHTW = SKILL_ROOT / "README.zh-TW.md"
SKILL_MD    = SKILL_ROOT / "SKILL.md"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _headings(text: str) -> list[str]:
    """Return all ATX heading lines (## or ###) stripped of markers."""
    return [
        re.sub(r"^#+\s*", "", line).strip()
        for line in text.splitlines()
        if re.match(r"^#{1,6}\s", line)
    ]


# ---------------------------------------------------------------------------
# Section-concept matchers — each checks ONE required concept by regex
# so each language can use its own natural phrasing.
# ---------------------------------------------------------------------------

# (a) 4 required heading CONCEPTS per README.
# Each tuple: (concept_label, regex) — regex is tested case-insensitively
# against the full list of heading texts joined by newlines.

REQUIRED_CONCEPTS_EN = [
    ("overview",          r"overview|what.+(this|the)\s+skill|what\s+recap\s+does"),
    ("when-to-use",       r"when\s+to\s+use|vs|built.in"),
    ("example-phrases",   r"example|invocation|trigger|phrases|how\s+to\s+(say|invoke|use)"),
    ("v0.2-deferred",     r"v0\.2|defer|coming|future|not\s+yet|what.s\s+(deferred|next)"),
]

REQUIRED_CONCEPTS_JA = [
    ("overview",          r"概要|このスキルは|recap\s*(と|が)|何をするか|使い方"),
    ("when-to-use",       r"使うとき|vs|使い分け|ビルトイン|組み込み|使わない"),
    ("example-phrases",   r"使い方|フレーズ|例|呼び出し|トリガー|言い方"),
    ("v0.2-deferred",     r"v0\.2|保留|今後|将来|延期|次の"),
]

REQUIRED_CONCEPTS_ZHTW = [
    ("overview",          r"概要|這個\s*skill|recap\s*(是什麼|做什麼|介紹)|簡介"),
    ("when-to-use",       r"何時|使用時機|vs|差異|內建|什麼時候"),
    ("example-phrases",   r"範例|呼叫|觸發|怎麼說|怎麼用|片語|說法"),
    ("v0.2-deferred",     r"v0\.2|延後|未來|下一版|保留|暫不"),
]


def _check_concepts(text: str, concepts: list[tuple[str, str]]) -> list[str]:
    """Return list of concept labels NOT found in the heading texts."""
    headings_block = "\n".join(_headings(text))
    missing = []
    for label, pattern in concepts:
        if not re.search(pattern, headings_block, re.IGNORECASE):
            missing.append(label)
    return missing


# ---------------------------------------------------------------------------
# (c) EN trigger consistency — at least one phrase in README.md example
#     section must appear verbatim in SKILL.md description.
# ---------------------------------------------------------------------------

_EN_TRIGGER_RE = re.compile(
    r"where were we|i.?m lost|recap|bring me back|what are we doing",
    re.IGNORECASE,
)


def _en_readme_has_trigger_phrase(readme_text: str) -> bool:
    return bool(_EN_TRIGGER_RE.search(readme_text))


def _skill_description_contains(skill_text: str, phrase: str) -> bool:
    return phrase.lower() in skill_text.lower()


# ---------------------------------------------------------------------------
# (d) JA / zh-TW trigger phrases — at least 3 language-native triggers
#     that also appear in SKILL.md description.
# ---------------------------------------------------------------------------

JA_TRIGGERS_IN_SKILL = [
    "ちょっと振り返って",
    "今どこだっけ",
    "振り返り",
    "振り返りをして",
    "状況を整理して",
]

ZHTW_TRIGGERS_IN_SKILL = [
    "我們剛剛在幹嘛",
    "剛剛講到哪",
    "我跟丟了",
    "帶我回到",
    "我們在做什麼",
]


def _count_triggers_in_readme(readme_text: str, triggers: list[str]) -> int:
    """Count how many trigger phrases appear in the README body."""
    return sum(1 for t in triggers if t in readme_text)


# ---------------------------------------------------------------------------
# The single test
# ---------------------------------------------------------------------------

def test_tri_lang_readmes_consistent():
    # -----------------------------------------------------------------------
    # (a) All 3 README files exist
    # -----------------------------------------------------------------------
    for path in [README_EN, README_JA, README_ZHTW]:
        assert path.exists(), f"Missing README: {path}"

    en_text   = _read(README_EN)
    ja_text   = _read(README_JA)
    zhtw_text = _read(README_ZHTW)
    skill_text = _read(SKILL_MD)

    # -----------------------------------------------------------------------
    # (b) Each README has 4 required section heading concepts
    # -----------------------------------------------------------------------
    en_missing   = _check_concepts(en_text,   REQUIRED_CONCEPTS_EN)
    ja_missing   = _check_concepts(ja_text,   REQUIRED_CONCEPTS_JA)
    zhtw_missing = _check_concepts(zhtw_text, REQUIRED_CONCEPTS_ZHTW)

    assert not en_missing,   f"EN README missing heading concepts: {en_missing}"
    assert not ja_missing,   f"JA README missing heading concepts: {ja_missing}"
    assert not zhtw_missing, f"zh-TW README missing heading concepts: {zhtw_missing}"

    # -----------------------------------------------------------------------
    # (c) EN README contains >=1 trigger phrase that also appears in SKILL.md
    # -----------------------------------------------------------------------
    assert _en_readme_has_trigger_phrase(en_text), (
        "EN README example section must contain at least one trigger phrase "
        "recognisable in SKILL.md description (e.g. 'where were we', 'I'm lost', "
        "'recap', 'bring me back', 'what are we doing')"
    )
    # Verify at least one of those triggers actually appears in the skill description
    found_in_skill = any(
        _skill_description_contains(skill_text, phrase)
        for phrase in ["where were we", "I'm lost", "recap", "bring me back",
                       "what are we doing"]
    )
    assert found_in_skill, (
        "SKILL.md description does not contain any of the expected EN trigger phrases"
    )

    # -----------------------------------------------------------------------
    # (d) JA README: >=3 language-native triggers also in SKILL.md
    # -----------------------------------------------------------------------
    ja_in_readme = _count_triggers_in_readme(ja_text, JA_TRIGGERS_IN_SKILL)
    assert ja_in_readme >= 3, (
        f"JA README must contain >=3 JA trigger phrases that appear in SKILL.md; "
        f"found {ja_in_readme}: "
        f"{[t for t in JA_TRIGGERS_IN_SKILL if t in ja_text]}"
    )
    # Verify those triggers also appear in skill description
    ja_in_skill = sum(1 for t in JA_TRIGGERS_IN_SKILL if t in skill_text)
    assert ja_in_skill >= 3, (
        f"SKILL.md description does not contain >=3 JA trigger phrases; "
        f"found {ja_in_skill}"
    )

    # -----------------------------------------------------------------------
    # (d) zh-TW README: >=3 language-native triggers also in SKILL.md
    # -----------------------------------------------------------------------
    zhtw_in_readme = _count_triggers_in_readme(zhtw_text, ZHTW_TRIGGERS_IN_SKILL)
    assert zhtw_in_readme >= 3, (
        f"zh-TW README must contain >=3 zh-TW trigger phrases that appear in SKILL.md; "
        f"found {zhtw_in_readme}: "
        f"{[t for t in ZHTW_TRIGGERS_IN_SKILL if t in zhtw_text]}"
    )
    zhtw_in_skill = sum(1 for t in ZHTW_TRIGGERS_IN_SKILL if t in skill_text)
    assert zhtw_in_skill >= 3, (
        f"SKILL.md description does not contain >=3 zh-TW trigger phrases; "
        f"found {zhtw_in_skill}"
    )
