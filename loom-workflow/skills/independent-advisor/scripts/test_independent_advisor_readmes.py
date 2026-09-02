"""Tests for loom-workflow/skills/independent-advisor tri-language READMEs — Task 8.

Assertions per plan Task 8 Acceptance:
  1. All 3 README files exist: README.md, README.ja.md, README.zh-TW.md
  2. Each names the skill and states the executor-changes-rather-than-lens
     distinction from the sibling critique skills.
  3. Each documents BOTH modes (`explore` / `audit`).
  4. Each carries the honest-framing caveats (privacy scope is the dispatch
     packet only; agreement between legs reading the same material is weak
     evidence; blindness is a claim about the dispatch packet only, so the
     independence claim is qualified rather than asserted) and never claims
     complete / comprehensive / exhaustive coverage.
  5. JA and zh-TW READMEs each list >=2 native invocation phrases.
"""

import re
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
README_EN = SKILL_DIR / "README.md"
README_JA = SKILL_DIR / "README.ja.md"
README_ZHTW = SKILL_DIR / "README.zh-TW.md"

READMES = [
    (README_EN, "README.md (EN)"),
    (README_JA, "README.ja.md (JA)"),
    (README_ZHTW, "README.zh-TW.md (zh-TW)"),
]

# Concept matchers — each is a list of candidate substrings; any match satisfies
# the concept. Keys are human-readable concept names used in error messages.
CONCEPT_MATCHERS = {
    "skill-name": ["independent-advisor", "Independent Advisor"],
    "executor-not-lens": [
        # EN
        "executor changes", "different executor", "who answers", "not the lens",
        # JA
        "実行者", "誰が答えるか", "観点ではなく",
        # zh-TW
        "執行者", "誰來回答", "不是換視角", "不是換觀點",
    ],
    "sibling-distinction": [
        "critique",
    ],
    "mode-explore": ["explore"],
    "mode-audit": ["audit"],
    "caveat-privacy-scope": [
        "dispatch packet", "派工包", "ディスパッチ",
    ],
    "caveat-agreement-weak": [
        # EN
        "same material", "not a strong signal", "measures the material",
        # JA
        "同じ材料", "強い証拠ではありません", "強い根拠にはなりません",
        # zh-TW
        "同一份材料", "不是強證據", "衡量的是材料",
    ],
    "caveat-qualified-blindness": [
        # EN
        "not the leg", "qualifies the independence claim",
        # JA
        "独立性を断定せず", "渡された範囲",
        # zh-TW
        "不是直接斷定", "授權範圍內",
    ],
    "invocation-phrases": [
        # EN
        "second opinion", "ask a stronger model",
        # JA
        "別のモデル", "セカンドオピニオン",
        # zh-TW
        "換一個模型", "第二意見",
    ],
}

REQUIRED_CONCEPTS = [
    "skill-name",
    "executor-not-lens",
    "sibling-distinction",
    "mode-explore",
    "mode-audit",
    "caveat-privacy-scope",
    "caveat-agreement-weak",
    "caveat-qualified-blindness",
    "invocation-phrases",
]

# Overclaim words the honest framing forbids anywhere in the READMEs.
OVERCLAIM_PATTERN = re.compile(
    r"comprehensive|exhaustive|complete coverage|網羅的|完全な網羅|完整涵蓋|全面涵蓋",
    re.IGNORECASE,
)

JA_PHRASES = [
    "セカンドオピニオン",
    "別のモデル",
    "もっと強いモデル",
    "別のベンダー",
]

ZHTW_PHRASES = [
    "第二意見",
    "換一個模型",
    "更強的模型",
    "換一家廠商",
]


def _check_concepts(readme_text: str, label: str) -> None:
    missing = [
        concept
        for concept in REQUIRED_CONCEPTS
        if not any(phrase in readme_text for phrase in CONCEPT_MATCHERS[concept])
    ]
    assert not missing, (
        f"{label}: missing concept(s) {missing}. Checked phrases per concept: "
        + "; ".join(f"{c}: {CONCEPT_MATCHERS[c]}" for c in missing)
    )


def test_all_three_language_readmes_exist_and_agree():
    """Task 8 gate: three READMEs exist, agree on the contract, and stay honest."""

    for path, label in READMES:
        assert path.exists(), f"{label} does not exist at {path}"

    texts = {label: path.read_text(encoding="utf-8") for path, label in READMES}

    for label, text in texts.items():
        _check_concepts(text, label)
        overclaim = OVERCLAIM_PATTERN.search(text)
        assert overclaim is None, (
            f"{label}: coverage overclaim {overclaim.group(0)!r} — the skill's "
            "honest framing forbids describing coverage as complete."
        )

    ja_found = [p for p in JA_PHRASES if p in texts["README.ja.md (JA)"]]
    assert len(ja_found) >= 2, (
        f"README.ja.md must list >=2 native invocation phrases. Found: {ja_found}."
    )

    zhtw_found = [p for p in ZHTW_PHRASES if p in texts["README.zh-TW.md (zh-TW)"]]
    assert len(zhtw_found) >= 2, (
        f"README.zh-TW.md must list >=2 native invocation phrases. Found: {zhtw_found}."
    )
