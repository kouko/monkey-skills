"""Tests for loom-pipeline/hooks/language-stop-check.py — Stop-event
language-consistency validator.

Subprocess-runs the hook exactly as Claude Code would invoke it: Stop
event JSON (transcript_path, stop_hook_active) on stdin, a
``{"decision": "block", "reason": "..."}`` top-level object (or
nothing) as the effect, exit code 0 always (fail-open). Mirrors
loom-pipeline/scripts/test_language_anchor.py's subprocess-driven
pattern.

The zh/ja block reasons are DIRECTIVE TEXT emitted for a DETECTED
language, not behavior selectors — the hook must never block when the
detected conversation language is 'en' or None.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).resolve().parent.parent / "hooks" / "language-stop-check.py"
HOOKS_JSON = Path(__file__).resolve().parent.parent / "hooks" / "hooks.json"

ZH_USER_TEXT = (
    "請幫我看看今天的天氣預報，我想知道明天是不是還會下雨，"
    "順便查一下濕度和氣溫的變化趨勢。"
)
JA_USER_TEXT = (
    "今日はとても良い天気ですね。明日の天気予報も確認してもらえますか、"
    "お願いします。"
)
EN_USER_TEXT = (
    "Could you please check tomorrow's weather forecast and let me "
    "know if it will rain again."
)

# >=200 visible (non-whitespace) chars, purely ASCII — used as the
# "assistant replied in English" case for a zh/ja session.
EN_REPLY_LONG = (
    "This is a fully English response that explains the implementation in "
    "plain prose without any Chinese or Japanese characters anywhere in "
    "this particular reply block, which is written entirely for testing "
    "purposes today so that the stop hook can correctly flag it as a "
    "language mismatch against the conversation language."
)

# >=200 visible chars, Han ratio ~0.89 even before the code fence is
# added — stays well above the 0.15 block threshold once the fence
# (with its English identifiers) is stripped.
ZH_REPLY_WITH_CODE = (
    "這是一段測試用的中文回覆內容，用來確認即使包含少量英文技術詞彙"
    "像是 API、JSON、CLI 這類名詞，整體仍然應該被視為以中文為主要語言，"
    "不應該被誤判為需要攔截的英文回覆，因為中文字元占了絕大多數的比例。"
    "以下是實作的補充說明，這段文字同樣以繁體中文書寫，並且刻意加長內容，"
    "確保去除程式碼區塊之後剩餘的可見字元數量仍然遠遠超過兩百個字元的門檻，"
    "這樣測試才能穩定通過而不會因為邊界值而偶爾失敗，也能涵蓋更完整的情境。"
    "\n```python\ndef foo():\n    return True  # an english comment too\n```\n"
)

SHORT_REPLY = "This is short."

# Legitimate zh reply DENSE with English identifiers: 377 visible
# chars, 47 Han chars → target-script RATIO 0.125 (< 0.15, blocked by
# the retired ratio rule) but absolute COUNT 47 ≥ max(10, 0.05×377)
# ≈ 19 — must NOT block under the amended count-based rule.
ZH_REPLY_JARGON_DENSE = (
    "這裡的 PostToolUse hook 會先讀 stop_hook_active flag，再用 "
    "conversation_language helper 判斷 expected language；接著 "
    "EventHandler 會把 final assistant message 的 text blocks 串接起來，"
    "經過 strip_noise 與 strip_table_rows 之後才計算 visible chars。"
    "整個 pipeline 依 fail-open convention 處理 malformed stdin，"
    "所以 JSONDecodeError、FileNotFoundError、UnicodeDecodeError "
    "都會直接 exit 0；hooks.json 的 Stop entry 用 command type 註冊，"
    "並透過 CLAUDE_PLUGIN_ROOT variable 解析 hook path。"
)


def _write_transcript(path: Path, user_text: str, assistant_texts, n_user: int = 3) -> None:
    """Write n_user user turns then one assistant turn PER item of
    ``assistant_texts`` (str = single turn) — the hook must evaluate
    only the LAST assistant turn."""
    if isinstance(assistant_texts, str):
        assistant_texts = [assistant_texts]
    with open(path, "w", encoding="utf-8") as fh:
        for _ in range(n_user):
            entry = {
                "type": "user",
                "isSidechain": False,
                "message": {"role": "user", "content": user_text},
            }
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
        for assistant_text in assistant_texts:
            assistant_entry = {
                "type": "assistant",
                "isSidechain": False,
                "message": {
                    "role": "assistant",
                    "content": [{"type": "text", "text": assistant_text}],
                },
            }
            fh.write(json.dumps(assistant_entry, ensure_ascii=False) + "\n")


def run_hook(payload):
    stdin = payload if isinstance(payload, str) else json.dumps(payload)
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=stdin,
        capture_output=True,
        text=True,
    )


def stop_event(transcript_path, stop_hook_active=False):
    return {
        "transcript_path": str(transcript_path),
        "stop_hook_active": stop_hook_active,
    }


def test_blocks_english_reply_in_cjk_session(tmp_path):
    transcript = tmp_path / "zh.jsonl"
    _write_transcript(transcript, ZH_USER_TEXT, EN_REPLY_LONG)
    result = run_hook(stop_event(transcript))
    assert result.returncode == 0
    out = json.loads(result.stdout)
    assert out["decision"] == "block"
    assert "繁體中文" in out["reason"] or "中文" in out["reason"]


def test_zh_reply_with_english_terms_and_code_passes(tmp_path):
    transcript = tmp_path / "zh-code.jsonl"
    _write_transcript(transcript, ZH_USER_TEXT, ZH_REPLY_WITH_CODE)
    result = run_hook(stop_event(transcript))
    assert result.returncode == 0
    assert result.stdout.strip() == ""


def test_en_session_english_reply_never_blocks(tmp_path):
    transcript = tmp_path / "en.jsonl"
    _write_transcript(transcript, EN_USER_TEXT, EN_REPLY_LONG)
    result = run_hook(stop_event(transcript))
    assert result.returncode == 0
    assert result.stdout.strip() == ""


def test_blocks_english_reply_in_ja_session(tmp_path):
    transcript = tmp_path / "ja.jsonl"
    _write_transcript(transcript, JA_USER_TEXT, EN_REPLY_LONG)
    result = run_hook(stop_event(transcript))
    assert result.returncode == 0
    out = json.loads(result.stdout)
    assert out["decision"] == "block"
    assert "日本語" in out["reason"]


def test_stop_hook_active_exits_zero_no_output(tmp_path):
    transcript = tmp_path / "zh.jsonl"
    _write_transcript(transcript, ZH_USER_TEXT, EN_REPLY_LONG)
    result = run_hook(stop_event(transcript, stop_hook_active=True))
    assert result.returncode == 0
    assert result.stdout.strip() == ""


def test_short_reply_passes(tmp_path):
    transcript = tmp_path / "zh-short.jsonl"
    _write_transcript(transcript, ZH_USER_TEXT, SHORT_REPLY)
    result = run_hook(stop_event(transcript))
    assert result.returncode == 0
    assert result.stdout.strip() == ""


def test_jargon_dense_zh_reply_passes(tmp_path):
    """Ratio-based rule false positive (reviewer finding 1): zh prose
    heavy with English identifiers has ratio < 0.15 yet dozens of Han
    chars — genuine drift has near-zero. Count rule must not block."""
    transcript = tmp_path / "zh-jargon.jsonl"
    _write_transcript(transcript, ZH_USER_TEXT, ZH_REPLY_JARGON_DENSE)
    result = run_hook(stop_event(transcript))
    assert result.returncode == 0
    assert result.stdout.strip() == ""


def test_multi_turn_evaluates_last_assistant_only_pass(tmp_path):
    """Earlier English assistant turn + FINAL zh turn → the final turn
    is what the user sees on Stop → must pass."""
    transcript = tmp_path / "zh-multi-pass.jsonl"
    _write_transcript(
        transcript, ZH_USER_TEXT, [EN_REPLY_LONG, ZH_REPLY_JARGON_DENSE]
    )
    result = run_hook(stop_event(transcript))
    assert result.returncode == 0
    assert result.stdout.strip() == ""


def test_multi_turn_evaluates_last_assistant_only_block(tmp_path):
    """Inverse: earlier zh turn + FINAL all-English turn → block."""
    transcript = tmp_path / "zh-multi-block.jsonl"
    _write_transcript(
        transcript, ZH_USER_TEXT, [ZH_REPLY_JARGON_DENSE, EN_REPLY_LONG]
    )
    result = run_hook(stop_event(transcript))
    assert result.returncode == 0
    out = json.loads(result.stdout)
    assert out["decision"] == "block"


def test_malformed_stdin_exits_zero_no_output():
    result = run_hook("not json at all")
    assert result.returncode == 0
    assert result.stdout.strip() == ""


def test_hooks_json_has_all_three_entries():
    data = json.loads(HOOKS_JSON.read_text())
    assert "SessionStart" in data["hooks"]
    assert "PostToolUse" in data["hooks"]

    stop_hooks = data["hooks"]["Stop"]
    assert len(stop_hooks) == 1
    entry = stop_hooks[0]
    hooks = entry["hooks"]
    assert len(hooks) == 1
    assert hooks[0]["type"] == "command"
    assert "language-stop-check.py" in hooks[0]["command"]
