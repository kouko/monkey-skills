"""Tests for loom-pipeline/hooks/lang_detect.py.

Pure-stdlib language-detection helper: ``detect_script()`` is a
char-heuristic on raw text; ``conversation_language()`` majority-votes
over the last N user main-chain turns of a Claude Code transcript
JSONL file. Imported by path (same pattern as
legal-toolkit/tests/test_classify_path.py) since the module lives
under hooks/, not an installed package.

One test per behavior group (F.I.R.S.T Independent);
``test_detect_and_conversation_language`` stays as the thin
integration case the plan's RED/GREEN acceptance names.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO / "loom-pipeline" / "hooks" / "lang_detect.py"
# Frozen copy of a real session tail (user main-chain turns extracted
# verbatim from a live Traditional-Chinese session's transcript;
# machine-payload turns >2000 chars truncated to their head — the
# injection filters only read the head). Never test against the live,
# still-growing transcript file.
FIXTURE_SESSION_TAIL = (
    REPO / "loom-pipeline" / "scripts" / "fixtures" / "fixture_session_tail.jsonl"
)


def _load():
    spec = importlib.util.spec_from_file_location("lang_detect", MODULE_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _write_transcript(path: Path, entries: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        for entry in entries:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _user_entry(text, *, sidechain: bool = False) -> dict:
    return {
        "type": "user",
        "isSidechain": sidechain,
        "message": {"role": "user", "content": text},
    }


ZH_TEXT = (
    "請幫我看看今天的天氣預報，我想知道明天是不是還會下雨，"
    "順便查一下濕度和氣溫的變化趨勢。"
)
JA_TEXT = (
    "今日はとても良い天気ですね。明日の天気予報も確認してもらえますか、"
    "お願いします。"
)
EN_TEXT = (
    "Could you please check tomorrow's weather forecast and let me "
    "know if it will rain again."
)
ZH_WITH_ENGLISH_TERMS = (
    "這是一個測試，我想要呼叫 API 並解析 JSON 回傳的資料，"
    "看看能不能正常運作，麻煩幫我確認一下。"
)
# Predominantly-English prose quoting a couple of Japanese words —
# must NOT classify 'ja' (code-quality-review finding 1).
EN_QUOTING_JA_WORDS = (
    "The word yoroshiku (よろしく) is used a lot in Japanese business "
    "emails. Another common phrase is otsukaresama (おつかれさま) which "
    "you can say to coworkers at the end of the day."
)
# Unfenced pasted traceback — no triple backticks (finding 2).
UNFENCED_TRACEBACK = (
    "Traceback (most recent call last):\n"
    '  File "app.py", line 10, in <module>\n'
    "    result = process_the_request_data(payload)\n"
    "ValueError: invalid literal for int() with base 10: 'abc'"
)
# A skill invocation's ENTIRE English SKILL.md body arrives as a
# user-role turn beginning with this literal harness-injected prefix —
# machine payload, not the user's language (live repro evidence).
SKILL_BODY_TEXT = (
    "Base directory for this skill: /some/plugin/skills/example\n\n"
    "This skill helps you accomplish a repeatable workflow by walking "
    "through several steps, each described here in plain English prose "
    "so the assistant understands exactly what to do at each stage of "
    "the process before producing any user-facing output at all."
)
INTERRUPTED_TEXT = "[Request interrupted by user]"


# --- detect_script -----------------------------------------------------


def test_detect_script_table():
    mod = _load()
    assert mod.detect_script(JA_TEXT) == "ja"
    assert mod.detect_script(ZH_TEXT) == "zh"
    assert mod.detect_script(EN_TEXT) == "en"
    assert mod.detect_script("hi") is None       # too short
    assert mod.detect_script("") is None
    assert mod.detect_script(None) is None


def test_detect_script_mixed_cjk_with_english_terms():
    mod = _load()
    # Han still dominates the script-bearing chars -> zh
    assert mod.detect_script(ZH_WITH_ENGLISH_TERMS) == "zh"


def test_detect_script_english_quoting_japanese_words():
    """Regression (review finding 1): a few quoted kana words inside a
    predominantly-English turn must not flip the verdict to 'ja'."""
    mod = _load()
    assert mod.detect_script(EN_QUOTING_JA_WORDS) == "en"


# --- noise stripping in conversation_language --------------------------


def test_code_fence_stripping(tmp_path):
    mod = _load()
    # Unstripped, the ascii-heavy code block would tip the vote to 'en'.
    fenced = (
        ZH_TEXT
        + "\n```python\ndef handler(request, response, context):\n"
        "    return process(request)\n```"
    )
    transcript = tmp_path / "fenced.jsonl"
    _write_transcript(transcript, [_user_entry(fenced)] * 3)
    assert mod.conversation_language(transcript, n_turns=3) == "zh"


def test_unfenced_traceback_stripping(tmp_path):
    """Regression (review finding 2): a pasted traceback WITHOUT code
    fences must not outvote the CJK prose around it."""
    mod = _load()
    turn = ZH_TEXT + "\n" + UNFENCED_TRACEBACK
    transcript = tmp_path / "traceback.jsonl"
    _write_transcript(transcript, [_user_entry(turn)] * 3)
    assert mod.conversation_language(transcript, n_turns=3) == "zh"


# --- turn selection ----------------------------------------------------


def test_sidechain_exclusion(tmp_path):
    mod = _load()
    transcript = tmp_path / "sidechain.jsonl"
    _write_transcript(
        transcript,
        [
            _user_entry(EN_TEXT, sidechain=True),
            _user_entry(ZH_TEXT),
            _user_entry(ZH_TEXT),
            _user_entry(ZH_TEXT),
        ],
    )
    assert mod.conversation_language(transcript, n_turns=3) == "zh"


def test_wrapper_turns_skipped(tmp_path):
    # tool-result / system-reminder wrappers (text starts with '<') are
    # skipped and do not count toward the last-n window
    mod = _load()
    transcript = tmp_path / "wrapper.jsonl"
    _write_transcript(
        transcript,
        [
            _user_entry(ZH_TEXT),
            _user_entry(
                "<system-reminder>some english wrapper content</system-reminder>"
            ),
            _user_entry(ZH_TEXT),
            _user_entry(ZH_TEXT),
        ],
    )
    assert mod.conversation_language(transcript, n_turns=3) == "zh"


def test_content_block_lists(tmp_path):
    # message.content as list of blocks: only type:"text" blocks count
    mod = _load()
    transcript = tmp_path / "blocks.jsonl"
    _write_transcript(
        transcript,
        [
            _user_entry(
                [
                    {"type": "tool_result", "text": "irrelevant tool payload"},
                    {"type": "text", "text": ZH_TEXT},
                ]
            )
        ]
        * 3,
    )
    assert mod.conversation_language(transcript, n_turns=3) == "zh"


# --- majority rule ------------------------------------------------------


def test_majority_rule(tmp_path):
    mod = _load()
    transcript = tmp_path / "majority.jsonl"
    _write_transcript(
        transcript,
        [_user_entry(ZH_TEXT), _user_entry(ZH_TEXT), _user_entry(EN_TEXT)],
    )
    assert mod.conversation_language(transcript, n_turns=3) == "zh"


def test_no_majority_tie(tmp_path):
    mod = _load()
    transcript = tmp_path / "tie.jsonl"
    _write_transcript(
        transcript,
        [_user_entry(ZH_TEXT), _user_entry(EN_TEXT), _user_entry(JA_TEXT)],
    )
    assert mod.conversation_language(transcript, n_turns=3) is None


# --- harness-injection filtering (live repro regression) ----------------


def test_harness_injection_turns_excluded_from_vote(tmp_path):
    """A skill-body payload turn (starts with 'Base directory for this
    skill:') and a '[Request interrupted...' marker turn are both
    harness-injected artifacts, not user narration — they must not
    enter the sampled window at all, even though they are English-only
    user-role turns that would otherwise flip the vote away from zh."""
    mod = _load()
    transcript = tmp_path / "harness_injection.jsonl"
    _write_transcript(
        transcript,
        [
            _user_entry(ZH_TEXT),
            _user_entry(ZH_TEXT),
            _user_entry(SKILL_BODY_TEXT),
            _user_entry(INTERRUPTED_TEXT),
            _user_entry(ZH_TEXT),
        ],
    )
    # Unfiltered, the last 3 positional turns would be [SKILL_BODY_TEXT,
    # INTERRUPTED_TEXT, ZH_TEXT] -> majority 'en'; only excluding the
    # two injected turns recovers the true 'zh' signal.
    assert mod.conversation_language(transcript, n_turns=3) == "zh"


def test_short_confirmations_do_not_dilute_vote(tmp_path):
    """Short zh confirmations (<20 visible chars, e.g. '好'/'修') return
    None from detect_script and must be skipped rather than counted as
    an undetermined vote that dilutes the majority — sample the last n
    DETECTABLE turns, not the last n turns positionally. An English
    skill-load turn sits in between and must also be excluded (harness
    injection, not a genuine English turn)."""
    mod = _load()
    transcript = tmp_path / "short_confirmations.jsonl"
    _write_transcript(
        transcript,
        [
            _user_entry(ZH_TEXT),
            _user_entry(ZH_TEXT),
            _user_entry(SKILL_BODY_TEXT),
            _user_entry("好"),
            _user_entry("修"),
        ],
    )
    assert mod.conversation_language(transcript, n_turns=3) == "zh"


def test_harness_injection_filter_does_not_fabricate_zh_in_english_conversation(
    tmp_path,
):
    """An actually-English conversation with one injected skill body
    must stay 'en' — the filter removes noise, it must not invent a
    zh/ja signal out of nothing."""
    mod = _load()
    transcript = tmp_path / "english_with_injection.jsonl"
    _write_transcript(
        transcript,
        [
            _user_entry(EN_TEXT),
            _user_entry(SKILL_BODY_TEXT),
            _user_entry(EN_TEXT),
            _user_entry(EN_TEXT),
        ],
    )
    assert mod.conversation_language(transcript, n_turns=3) == "en"


# --- workflow-invocation echo (third harness-injection shape) -----------


WORKFLOW_ECHO_TEXT = (
    'Run the "deep-research" workflow.\n\n'
    "Deep research harness — fan-out web searches, fetch sources, "
    "adversarially verify claims, synthesize a cited report."
)


def test_workflow_echo_is_harness_injection():
    """Skill/workflow invocation echoes shaped 'Run the "<name>"
    workflow.' are harness-injected (the skill's own description text,
    not user narration) — but a genuine user typing 'Run the tests'
    must NOT be filtered: the match is the full quoted-name shape, not
    a bare 'Run the' prefix."""
    mod = _load()
    assert mod.is_harness_injection(WORKFLOW_ECHO_TEXT) is True
    assert mod.is_harness_injection('Run the "x" workflow. extra prose') is True
    # negative guards: genuine user phrasing stays eligible
    assert mod.is_harness_injection("Run the tests") is False
    assert mod.is_harness_injection("Run the tests and report failures") is False
    assert mod.is_harness_injection('Run the "quoted" thing please') is False


def test_workflow_echo_excluded_from_vote(tmp_path):
    mod = _load()
    transcript = tmp_path / "workflow_echo.jsonl"
    _write_transcript(
        transcript,
        [
            _user_entry(ZH_TEXT),
            _user_entry(ZH_TEXT),
            _user_entry(WORKFLOW_ECHO_TEXT),
            _user_entry(ZH_TEXT),
        ],
    )
    assert mod.conversation_language(transcript, n_turns=3) == "zh"


# --- CJK-aware detectability floor ---------------------------------------


def test_detect_script_short_but_unambiguous_cjk():
    """Short-but-unambiguous CJK turns (<20 visible chars but >=8 CJK
    chars) are the user's dominant real style in live sessions
    (「我合併了 幫我跑跑 comms 稽核」) — they must be detectable, not
    discarded by the ASCII-calibrated 20-char floor."""
    mod = _load()
    assert mod.detect_script("我合併了 幫我跑跑 comms 稽核") == "zh"
    assert mod.detect_script("現在已重置額度了 請繼續") == "zh"
    assert mod.detect_script("すぐに続けてください、お願いします") == "ja"
    # still below BOTH floors -> undetectable
    assert mod.detect_script("修") is None
    assert mod.detect_script("請繼續") is None


def test_detect_script_short_english_with_cjk_fragment_not_flipped():
    """A tiny zh fragment quoted inside an otherwise-English short turn
    (<20 visible, <8 CJK) must not flip the verdict to 'zh' — the CJK
    floor lowers the length gate only for genuinely CJK turns."""
    mod = _load()
    assert mod.detect_script("see 你好嗎 thanks") != "zh"


# --- fail-open ----------------------------------------------------------


def test_fail_open(tmp_path):
    mod = _load()
    # missing file
    assert mod.conversation_language(tmp_path / "does-not-exist.jsonl") is None
    # malformed JSON lines
    malformed = tmp_path / "malformed.jsonl"
    malformed.write_text("not json at all\n{broken", encoding="utf-8")
    assert mod.conversation_language(malformed) is None
    # non-utf8 bytes
    binary_garbage = tmp_path / "binary.jsonl"
    binary_garbage.write_bytes(b"\xff\xfe\x00bad-bytes-not-utf8\x80\x81")
    assert mod.conversation_language(binary_garbage) is None


# --- frozen live-session-tail regression (round-2 acceptance) -----------


def test_session_tail_fixture_detects_zh():
    """Frozen tail of a real Traditional-Chinese session: a workflow
    echo, five skill-body payloads, two English orchestrator wakeup
    prompts (deliberately UNFILTERED — genuine typed turns are
    indistinguishable), an interrupt marker, and a run of short zh
    turns. Combined injection filtering + CJK-aware floor must recover
    'zh'; before the fix this shape returned 'en'/None."""
    mod = _load()
    assert mod.conversation_language(FIXTURE_SESSION_TAIL, n_turns=3) == "zh"


# --- thin integration case (plan's named RED/GREEN reference) -----------


def test_detect_and_conversation_language(tmp_path):
    mod = _load()
    assert mod.detect_script(ZH_TEXT) == "zh"
    transcript = tmp_path / "integration.jsonl"
    _write_transcript(transcript, [_user_entry(ZH_TEXT)] * 3)
    assert mod.conversation_language(transcript, n_turns=3) == "zh"


# --- public wrapper contract (stable cross-module surface) ---------------


def test_public_wrappers_exist_and_delegate():
    """Sibling hooks (language-stop-check.py) consume these PUBLIC names;
    they must exist and behave identically to the private helpers."""
    mod = _load()
    assert mod.is_kana("あ") is True and mod.is_kana("漢") is False
    assert mod.is_han("漢") is True and mod.is_han("あ") is False
    assert mod.extract_text([{"type": "text", "text": "hi"}]) == "hi"
    assert mod.extract_text("plain") == "plain"
    assert "code" not in mod.strip_noise("前置 `code` 後置")
