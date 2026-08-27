"""Language-coverage test for the goal-create mechanical lint floor (Task 4).

`goal_lint.py` is a mechanical, syntactic check over goal text. Its field
labels (`Outcome`, `Constraints`, `Verification`, `Stop-when`) are fixed
English, but the field *content* a real user writes is not — this repo's
users write Traditional Chinese, English, and Japanese. A check written
and tested against English content only is language-bound in a way that
fails silently: nothing errors when it is run against Chinese or Japanese
text, it just passes everything (or fails everything) without anyone
noticing the floor stopped doing its job. This test is what makes that
coverage visible: the same structural violation, in each language, must
be judged identically.

No word/marker/phrase list is introduced here. Every fixture below is
judged only by the floor's three structural checks (field presence,
backticked command inside Verification, character count) — never by
matching language-specific vocabulary.
"""

import goal_lint

LANGUAGES = {
    "en": {
        "outcome": "The signup form submits with zero client-side validation errors.",
        "constraints": "Do not touch the payment module.",
        "verification_cmd": "pytest tests/test_signup.py",
        "stopwhen": "The outcome is reached, or stop after 20 turns.",
    },
    "zh-Hant": {
        "outcome": "簽到表單送出時沒有任何前端驗證錯誤。",
        "constraints": "不要更動付款模組。",
        "verification_cmd": "pytest tests/test_signup.py",
        "stopwhen": "達成目標即停止，或跑滿 20 輪後停止。",
    },
    "ja": {
        "outcome": "サインアップフォームがクライアント側の検証エラーなしで送信される。",
        "constraints": "決済モジュールには触れないこと。",
        "verification_cmd": "pytest tests/test_signup.py",
        "stopwhen": "目標達成で終了、または20ターン後に停止。",
    },
}


def _complete_goal(spec):
    return (
        f"Outcome: {spec['outcome']}\n"
        f"Constraints: {spec['constraints']}\n"
        f"Verification: Run `{spec['verification_cmd']}` and paste the output.\n"
        f"Stop-when: {spec['stopwhen']}\n"
    )


def _missing_field_goal(spec):
    # Drop the Stop-when field entirely. The field label itself is fixed
    # English in every language, so this is the exact same structural
    # violation regardless of what language the other fields are in.
    return (
        f"Outcome: {spec['outcome']}\n"
        f"Constraints: {spec['constraints']}\n"
        f"Verification: Run `{spec['verification_cmd']}` and paste the output.\n"
    )


def _no_backtick_goal(spec):
    # Verification content with no backticked command — the second hard
    # failure, in each language.
    return (
        f"Outcome: {spec['outcome']}\n"
        f"Constraints: {spec['constraints']}\n"
        f"Verification: Run {spec['verification_cmd']} and paste the output.\n"
        f"Stop-when: {spec['stopwhen']}\n"
    )


def test_floor_holds_across_zh_en_ja():
    # Structurally complete: identical verdict (no errors) in every language.
    for lang, spec in LANGUAGES.items():
        result = goal_lint.lint_text(_complete_goal(spec))
        assert result.errors == [], f"{lang}: expected no errors, got {result.errors}"
        assert result.exit_code == 0, f"{lang}: expected exit_code 0"

    # Structurally broken (missing field): the same error code fires
    # identically in every language, and no other hard error is dragged in.
    for lang, spec in LANGUAGES.items():
        result = goal_lint.lint_text(_missing_field_goal(spec))
        assert result.exit_code != 0, f"{lang}: expected a hard failure"
        assert any(f.code == "missing-field" for f in result.errors), lang
        assert not any(f.code == "no-backtick-command" for f in result.errors), lang
        assert not any(f.code == "length-limit" for f in result.errors), lang

    # Structurally broken (no backticked command): same code, same shape,
    # in every language.
    for lang, spec in LANGUAGES.items():
        result = goal_lint.lint_text(_no_backtick_goal(spec))
        assert result.exit_code != 0, f"{lang}: expected a hard failure"
        assert any(f.code == "no-backtick-command" for f in result.errors), lang
        assert not any(f.code == "missing-field" for f in result.errors), lang

    # Characters, not bytes: a CJK-heavy goal sitting comfortably under the
    # 4,000-character limit must not trip the limit, even though its UTF-8
    # byte count is far larger than 4,000 (each CJK character is 3 bytes in
    # UTF-8). This is the fixture that would catch a byte-counting
    # regression that an English-only fixture could never distinguish from
    # a correct, character-counting implementation.
    cjk_near_limit = (
        "Outcome: " + ("目" * 3800) + "\n"
        "Constraints: 不要更動付款模組。\n"
        "Verification: Run `pytest tests/test_signup.py` and paste the output.\n"
        "Stop-when: 達成目標即停止，或跑滿 20 輪後停止。\n"
    )
    assert len(cjk_near_limit) <= goal_lint.CHARACTER_LIMIT
    assert len(cjk_near_limit.encode("utf-8")) > goal_lint.CHARACTER_LIMIT * 2
    result = goal_lint.lint_text(cjk_near_limit)
    assert not any(f.code == "length-limit" for f in result.errors)
