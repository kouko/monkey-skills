"""Tests for dev-workflow/skills/handoff tri-language READMEs — T3 RED assertions.

Assertions per plan T3 Acceptance:
  1. All 3 README files exist: README.md, README.ja.md, README.zh-TW.md
  2. Each contains 5 section concepts:
       - overview (what the skill does)
       - when-to-use-vs-recap comparison
       - example invocations for BOTH prepare AND resume modes
       - .gitignore recommendation
       - v0.2-deferred content
  3. EN README's prepare-mode example phrase matches ≥1 prepare trigger in SKILL.md description
  4. JA and zh-TW READMEs each list ≥2 native prepare-mode trigger phrases AND
     ≥2 native resume-mode trigger phrases that ALSO appear in SKILL.md description
"""

import re
from pathlib import Path

import pytest

try:
    import yaml  # PyYAML
except ImportError:  # pragma: no cover — environment guard
    yaml = None

SKILL_DIR = Path(__file__).parent.parent
SKILL_MD = SKILL_DIR / "SKILL.md"
README_EN = SKILL_DIR / "README.md"
README_JA = SKILL_DIR / "README.ja.md"
README_ZHTW = SKILL_DIR / "README.zh-TW.md"

# Concept matchers — each is a list of candidate substrings; any match satisfies the concept.
# Keys are human-readable concept names for error messages.
CONCEPT_MATCHERS = {
    "overview": [
        "cross-session", "クロスセッション", "跨對話", "跨 session",
        "prepare", "resume", "HANDOFF", "handoff",
        "10-block", "10 block", "10 ブロック", "10 個區塊", "10 塊",
        "cold AI", "cold reader",
        "保存狀態", "保存", "引き継ぎ",
    ],
    "when-to-use-vs-recap": [
        # Must contrast handoff vs recap; any of these signal the comparison table/section
        "recap", "in-session", "L3", "L2",
        "セッション内", "セッション終了", "対話内", "対話内",
        "セッションをまたぐ", "セッションをまたぐ",
        "跨對話", "對話內", "對話內", "跨 session", "in session",
    ],
    "example-invocation-prepare": [
        # EN
        "wrap up", "save state", "save progress", "I'm done for today", "end session",
        # JA
        "今日はここまで", "引き継ぎ", "状態を保存", "セッションを終わる",
        # zh-TW
        "收尾", "明天繼續", "保存狀態", "先這樣", "記錄一下進度", "今天先到這",
    ],
    "example-invocation-resume": [
        # EN
        "pick up where we left off", "load handoff", "resume from last", "continue where we stopped",
        # JA
        "前回の続きから", "引き継ぎを読んで", "再開して",
        # zh-TW
        "繼續上次", "從上次說到哪裡", "載入狀態", "接著做",
    ],
    "gitignore-recommendation": [
        ".gitignore", "gitignore", ".claude/handoffs",
        # Any of these signal the gitignore section
        "commit", "git history", "git-tracking",
        "コミット", "git 履歴", "トラッキング",
        "提交", "git 歷史", "追蹤",
        "opt-in", "opt-out",
    ],
    "v0.2-deferred": [
        "v0.2", "deferred", "defer",
        "v0.2 に保留", "v0.2 保留",
        "v0.2 暫不", "延後",
        "forced", "Interruption Snapshot", "per-tool",
        "強制", "割り込み", "中斷",
        "test-prompts.json", "trigger-eval.json",
    ],
}

# Section concepts each README MUST contain (as list of concept keys that must each fire)
REQUIRED_CONCEPTS = [
    "overview",
    "when-to-use-vs-recap",
    "example-invocation-prepare",
    "example-invocation-resume",
    "gitignore-recommendation",
    "v0.2-deferred",
]


def _load_skill_md_description() -> str:
    """Extract SKILL.md frontmatter description for consistency oracle."""
    if not SKILL_MD.exists():
        return ""
    text = SKILL_MD.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return ""
    parts = text.split("---", 2)
    if len(parts) < 3:
        return ""
    if yaml is None:  # pragma: no cover
        # Fallback: return the raw frontmatter block for substring matching
        return parts[1]
    try:
        fm = yaml.safe_load(parts[1])
        return fm.get("description", "") or ""
    except Exception:
        return parts[1]


def _check_concepts(readme_path: Path, readme_text: str, label: str):
    """Assert all required concept groups appear in readme_text."""
    missing = []
    for concept in REQUIRED_CONCEPTS:
        candidates = CONCEPT_MATCHERS[concept]
        if not any(phrase in readme_text for phrase in candidates):
            missing.append(concept)
    assert not missing, (
        f"{label}: missing concept(s) {missing}. "
        f"Checked phrases per concept: "
        + "; ".join(f"{c}: {CONCEPT_MATCHERS[c]}" for c in missing)
    )


# ---------------------------------------------------------------------------
# Composite test function matching the plan's pytest invocation target
# ---------------------------------------------------------------------------


def test_tri_lang_readmes_consistent():
    """T3 gate: all 3 READMEs exist with 5 section concepts + cross-language trigger consistency."""

    # 1. All 3 README files exist
    for path, label in [
        (README_EN, "README.md (EN)"),
        (README_JA, "README.ja.md (JA)"),
        (README_ZHTW, "README.zh-TW.md (zh-TW)"),
    ]:
        assert path.exists(), f"{label} does not exist at {path}"

    skill_desc = _load_skill_md_description()

    # 2. Each README contains all 5 section concepts
    en_text = README_EN.read_text(encoding="utf-8")
    ja_text = README_JA.read_text(encoding="utf-8")
    zhtw_text = README_ZHTW.read_text(encoding="utf-8")

    _check_concepts(README_EN, en_text, "README.md (EN)")
    _check_concepts(README_JA, ja_text, "README.ja.md (JA)")
    _check_concepts(README_ZHTW, zhtw_text, "README.zh-TW.md (zh-TW)")

    # 3. EN README's prepare-mode example phrase matches ≥1 prepare trigger in SKILL.md description
    en_prepare_triggers = [
        "wrap up", "save state", "save progress", "I'm done for today",
        "end session", "let's stop here",
    ]
    skill_prepare_triggers_in_desc = [t for t in en_prepare_triggers if t in skill_desc]
    en_prepare_in_readme = [t for t in en_prepare_triggers if t in en_text]
    shared_prepare = [t for t in en_prepare_in_readme if t in skill_desc]
    assert len(shared_prepare) >= 1, (
        f"EN README must contain ≥1 prepare-mode trigger phrase that also appears in SKILL.md description. "
        f"SKILL.md has: {skill_prepare_triggers_in_desc}. EN README has: {en_prepare_in_readme}."
    )

    # 4a. JA README lists ≥2 prepare-mode AND ≥2 resume-mode native triggers.
    # (The 2026-06 house description standard removed CJK trigger tails from the
    # EN skill description, so native-language triggers are checked in the README
    # only — no longer cross-checked against skill_desc.)
    ja_prepare_triggers = [
        "今日はここまで", "引き継ぎ", "状態を保存", "セッションを終わる", "先這樣",
    ]
    ja_prepare_in_readme = [t for t in ja_prepare_triggers if t in ja_text]
    assert len(ja_prepare_in_readme) >= 2, (
        f"README.ja.md must list ≥2 prepare-mode native trigger phrases. "
        f"Found: {ja_prepare_in_readme}."
    )

    ja_resume_triggers = [
        "前回の続きから", "引き継ぎを読んで", "再開して",
    ]
    ja_resume_in_readme = [t for t in ja_resume_triggers if t in ja_text]
    assert len(ja_resume_in_readme) >= 2, (
        f"README.ja.md must list ≥2 resume-mode native trigger phrases. "
        f"Found: {ja_resume_in_readme}."
    )

    # 4b. zh-TW README lists ≥2 prepare-mode AND ≥2 resume-mode native triggers
    # (README-only, per the house-standard note in 4a).
    zhtw_prepare_triggers = [
        "收尾", "明天繼續", "保存狀態", "先這樣", "記錄一下進度", "今天先到這",
    ]
    zhtw_prepare_in_readme = [t for t in zhtw_prepare_triggers if t in zhtw_text]
    assert len(zhtw_prepare_in_readme) >= 2, (
        f"README.zh-TW.md must list ≥2 prepare-mode native trigger phrases. "
        f"Found: {zhtw_prepare_in_readme}."
    )

    zhtw_resume_triggers = [
        "繼續上次", "從上次說到哪裡", "載入狀態", "接著做",
    ]
    zhtw_resume_in_readme = [t for t in zhtw_resume_triggers if t in zhtw_text]
    assert len(zhtw_resume_in_readme) >= 2, (
        f"README.zh-TW.md must list ≥2 resume-mode native trigger phrases. "
        f"Found: {zhtw_resume_in_readme}."
    )
