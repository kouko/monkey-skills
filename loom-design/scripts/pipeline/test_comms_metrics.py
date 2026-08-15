"""Tests for loom-pipeline/scripts/comms_metrics.py.

Pure-stdlib recipe that computes three comms metrics over a Claude Code
transcript JSONL (per file + aggregate):
  (a) wrong-language turn ratio — assistant main-chain narration turns
      (>=200 visible chars) whose detected script mismatches the
      rolling conversation language recomputed from user turns up to
      that point (skip when either side is None);
  (b) visual-at-fork rate — AskUserQuestion tool_use turns with a
      markdown table or ascii/box-drawing diagram in the same or 2
      preceding assistant turns;
  (c) confusion-signal count — user turns matching an extensible list
      of regexes.

Imported by path (same pattern as test_lang_detect.py) since the
module lives under scripts/, not an installed package. Fixtures under
fixtures/ have hand-planted, hand-verified counts (see comments below
and the module docstring in fixtures generation).

One test per behavior group (F.I.R.S.T Independent);
``test_three_metrics_on_fixtures`` stays as the thin integration case
the plan's RED/GREEN acceptance names.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO / "loom-pipeline" / "scripts" / "comms_metrics.py"
FIXTURE_A = REPO / "loom-pipeline" / "scripts" / "fixtures" / "fixture_a.jsonl"
FIXTURE_B = REPO / "loom-pipeline" / "scripts" / "fixtures" / "fixture_b.jsonl"


def _load():
    spec = importlib.util.spec_from_file_location("comms_metrics", MODULE_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _write_transcript(path: Path, entries: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        for entry in entries:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _user(text, *, sidechain: bool = False) -> dict:
    return {
        "type": "user",
        "isSidechain": sidechain,
        "message": {"role": "user", "content": text},
    }


def _assistant_text(text, *, sidechain: bool = False) -> dict:
    return {
        "type": "assistant",
        "isSidechain": sidechain,
        "message": {"role": "assistant", "content": [{"type": "text", "text": text}]},
    }


def _assistant_ask(pre_text: str = "") -> dict:
    content = []
    if pre_text:
        content.append({"type": "text", "text": pre_text})
    content.append(
        {
            "type": "tool_use",
            "id": "toolu_x",
            "name": "AskUserQuestion",
            "input": {"questions": [{"question": "?", "header": "H", "options": []}]},
        }
    )
    return {
        "type": "assistant",
        "isSidechain": False,
        "message": {"role": "assistant", "content": content},
    }


EN_LONG = (
    "This is a plain English paragraph written specifically to test the "
    "wrong language detection metric in the comms metrics module, and it "
    "has no real meaning beyond padding the character count comfortably "
    "past the two hundred visible character threshold so the test stays "
    "stable even if the exact counting logic shifts slightly over time."
)
ZH_LONG = (
    "這是一段用來測試錯誤語言偵測的中文內容，內容本身沒有任何實際意義，"
    "純粹是為了湊出足夠長度而重複描述天氣、濕度與氣溫的變化趨勢，"
    "希望這樣的長度足以超過兩百個可見字元的門檻，方便驗證程式邏輯是否正確運作。"
    "再補上幾句話讓長度更保險一些，避免因為門檻計算誤差而導致測試不穩定，"
    "所以我們繼續多寫幾句沒有意義的句子，直到長度確定超過門檻為止，"
    "最後再確認一次總長度是否已經足夠安全，多寫一點總是比較保險，"
    "這樣就能放心地在測試中使用這段固定的文字內容了。"
)


# --- integration: named RED/GREEN acceptance test -----------------------


def test_three_metrics_on_fixtures():
    """fixture_a.jsonl planted counts (hand-verified against lang_detect):
    2 zh user turns -> rolling lang zh; EN_LONG assistant reply mismatches
    (wrong=1); ZH_LONG reply matches (eligible=2); AskUserQuestion turn
    carries its own markdown table (visual=1/1); one user turn contains
    看不懂/白話 (confusion=1, counted once per turn not per pattern).
    """
    mod = _load()
    metrics = mod.compute_metrics(FIXTURE_A)

    assert metrics["wrong_language_count"] == 1
    assert metrics["wrong_language_eligible"] == 2
    assert metrics["wrong_language_ratio"] == 0.5

    assert metrics["visual_at_fork_count"] == 1
    assert metrics["visual_at_fork_eligible"] == 1
    assert metrics["visual_at_fork_rate"] == 1.0

    assert metrics["confusion_signal_count"] == 1


def test_fixture_b_negative_cases():
    """fixture_b.jsonl: rolling lang en (2 en user turns); ZH_LONG reply
    mismatches (wrong=1), EN_LONG2 reply matches (eligible=2);
    AskUserQuestion turn has NO table/diagram in itself or the 2
    preceding assistant turns (visual=0/1); two user turns match
    confusion regexes ("what do you mean", 什麼意思/？？ together on one
    turn still counts once) => confusion=2.
    """
    mod = _load()
    metrics = mod.compute_metrics(FIXTURE_B)

    assert metrics["wrong_language_count"] == 1
    assert metrics["wrong_language_eligible"] == 2
    assert metrics["wrong_language_ratio"] == 0.5

    assert metrics["visual_at_fork_count"] == 0
    assert metrics["visual_at_fork_eligible"] == 1
    assert metrics["visual_at_fork_rate"] == 0.0

    assert metrics["confusion_signal_count"] == 2


def test_aggregate_across_two_fixtures():
    mod = _load()
    per_file = [mod.compute_metrics(FIXTURE_A), mod.compute_metrics(FIXTURE_B)]
    agg = mod.aggregate_metrics(per_file)

    assert agg["wrong_language_count"] == 2
    assert agg["wrong_language_eligible"] == 4
    assert agg["wrong_language_ratio"] == 0.5

    assert agg["visual_at_fork_count"] == 1
    assert agg["visual_at_fork_eligible"] == 2
    assert agg["visual_at_fork_rate"] == 0.5

    assert agg["confusion_signal_count"] == 3


# --- (a) wrong-language: per-behavior tests ------------------------------


def test_wrong_language_skipped_when_conversation_language_undetermined(tmp_path):
    """No user turns at all -> rolling language is always None -> the
    long English assistant turn must be excluded from both numerator
    and denominator, not just the numerator."""
    mod = _load()
    path = tmp_path / "no_lang.jsonl"
    _write_transcript(path, [_assistant_text(EN_LONG)])

    metrics = mod.compute_metrics(path)
    assert metrics["wrong_language_count"] == 0
    assert metrics["wrong_language_eligible"] == 0
    assert metrics["wrong_language_ratio"] == 0.0


def test_wrong_language_ignores_short_assistant_replies(tmp_path):
    """A short (< 200 visible chars) English reply in a zh conversation
    must not count toward the metric at all — the length gate applies
    before the language comparison."""
    mod = _load()
    path = tmp_path / "short_reply.jsonl"
    _write_transcript(
        path,
        [
            _user("請幫我看看今天的天氣預報，我想知道明天是不是還會下雨。"),
            _user("順便查一下濕度和氣溫的變化趨勢，謝謝你的幫忙。"),
            _assistant_text("OK, sure thing."),
        ],
    )

    metrics = mod.compute_metrics(path)
    assert metrics["wrong_language_eligible"] == 0
    assert metrics["wrong_language_count"] == 0


def test_wrong_language_skips_sidechain_assistant_turns(tmp_path):
    """A sidechain assistant turn (isSidechain: true) must never be
    counted even if it is long and in the wrong language."""
    mod = _load()
    path = tmp_path / "sidechain.jsonl"
    _write_transcript(
        path,
        [
            _user("請幫我看看今天的天氣預報，我想知道明天是不是還會下雨。"),
            _user("順便查一下濕度和氣溫的變化趨勢，謝謝你的幫忙。"),
            _assistant_text(EN_LONG, sidechain=True),
        ],
    )

    metrics = mod.compute_metrics(path)
    assert metrics["wrong_language_eligible"] == 0
    assert metrics["wrong_language_count"] == 0


# --- (b) visual-at-fork: per-behavior tests ------------------------------


def test_visual_at_fork_detects_ascii_diagram_two_turns_back(tmp_path):
    mod = _load()
    diagram = "┌────────┐\n│ step 1 │\n└────────┘"
    path = tmp_path / "ascii_two_back.jsonl"
    _write_transcript(
        path,
        [
            _assistant_text(diagram),
            _assistant_text("plain text, no visual here at all."),
            _assistant_ask(""),
        ],
    )

    metrics = mod.compute_metrics(path)
    assert metrics["visual_at_fork_count"] == 1
    assert metrics["visual_at_fork_eligible"] == 1
    assert metrics["visual_at_fork_rate"] == 1.0


def test_visual_at_fork_zero_when_no_table_or_diagram_nearby(tmp_path):
    mod = _load()
    path = tmp_path / "no_visual.jsonl"
    _write_transcript(
        path,
        [
            _assistant_text("plain text turn one, nothing visual."),
            _assistant_text("plain text turn two, still nothing visual."),
            _assistant_ask(""),
        ],
    )

    metrics = mod.compute_metrics(path)
    assert metrics["visual_at_fork_count"] == 0
    assert metrics["visual_at_fork_eligible"] == 1
    assert metrics["visual_at_fork_rate"] == 0.0


def test_has_markdown_table_and_ascii_diagram_direct():
    mod = _load()
    assert mod._has_markdown_table("| a | b |\n| --- | --- |\n| 1 | 2 |") is True
    assert mod._has_markdown_table("just a | pipe character, no table") is False
    assert mod._has_ascii_diagram("┌───┐\n│ x │\n└───┘") is True
    # Plain-ascii +--+ boxes qualify once they contribute >=3 structural lines.
    assert mod._has_ascii_diagram("+----+\n| x  |\n+----+\n| y  |\n+----+") is True
    assert mod._has_ascii_diagram("no diagram characters here") is False


def test_visual_heuristics_vs_code_fences():
    """Fence handling is asymmetric by design (reviewer directive):
    a table INSIDE a fence is a code example, not a rendered
    comparison table -> not a visual; a fenced multi-line box-drawing
    diagram IS a deliberate visual (chat ascii diagrams are normally
    fenced); a fenced python/log paste has no box/arrow lines -> not
    a visual."""
    mod = _load()
    fenced_table = "example syntax:\n```\n| a | b |\n| --- | --- |\n| 1 | 2 |\n```"
    assert mod._has_markdown_table(fenced_table) is False
    assert mod._has_visual(fenced_table) is False

    fenced_diagram = (
        "```\n┌───────┐\n│ start │\n└───┬───┘\n    ▼\n"
        "┌───────┐\n│ done  │\n└───────┘\n```"
    )
    assert mod._has_ascii_diagram(fenced_diagram) is True

    fenced_python = (
        "```python\ndef f(x):\n    return x + 1\n\n"
        "result = [f(i) for i in range(10)]\nprint(result)\n```"
    )
    assert mod._has_ascii_diagram(fenced_python) is False
    assert mod._has_visual(fenced_python) is False


def test_visual_at_fork_not_counted_for_fenced_table_example(tmp_path):
    mod = _load()
    path = tmp_path / "fenced_table.jsonl"
    _write_transcript(
        path,
        [
            _assistant_text(
                "Here is the markdown syntax you asked about:\n"
                "```\n| a | b |\n| --- | --- |\n| 1 | 2 |\n```"
            ),
            _assistant_ask(""),
        ],
    )

    metrics = mod.compute_metrics(path)
    assert metrics["visual_at_fork_count"] == 0
    assert metrics["visual_at_fork_eligible"] == 1


def test_ascii_diagram_requires_three_structural_lines():
    """A stray box char or a 2-line fragment is not a diagram — the
    >=3-structural-lines floor keeps arbitrary pastes out."""
    mod = _load()
    assert mod._has_ascii_diagram("one stray │ pipe in prose") is False
    assert mod._has_ascii_diagram("┌───┐\n└───┘") is False


# --- (c) confusion-signal: per-behavior tests ----------------------------


def test_confusion_signal_count_matches_each_pattern_once_per_turn(tmp_path):
    """Every pattern in the extensible CONFUSION_PATTERNS list is
    individually reachable, and a turn matching two patterns at once
    still counts once (turn-level, not pattern-level)."""
    mod = _load()
    path = tmp_path / "confusion.jsonl"
    _write_transcript(
        path,
        [
            _user("這是什麼意思？"),
            _user("看不懂"),
            _user("？？"),
            _user("意義與影響是什麼"),
            _user("可以講簡單一點嗎"),
            _user("麻煩用白話文說明"),
            _user("what do you mean by this"),
            _user("這裡同時出現看不懂和白話兩個訊號"),  # 2 patterns, 1 turn
            _user("這句話完全沒有訊號"),
        ],
    )

    metrics = mod.compute_metrics(path)
    assert metrics["confusion_signal_count"] == 8


def test_confusion_signal_skips_sidechain_user_turns(tmp_path):
    mod = _load()
    path = tmp_path / "confusion_sidechain.jsonl"
    _write_transcript(path, [_user("看不懂", sidechain=True)])

    metrics = mod.compute_metrics(path)
    assert metrics["confusion_signal_count"] == 0


# --- CLI ------------------------------------------------------------------


def test_cli_json_output_parses():
    result = subprocess.run(
        [sys.executable, str(MODULE_PATH), str(FIXTURE_A), str(FIXTURE_B), "--json"],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert len(payload["per_file"]) == 2
    assert payload["aggregate"]["confusion_signal_count"] == 3


def test_cli_plain_output_prints_per_file_and_aggregate():
    result = subprocess.run(
        [sys.executable, str(MODULE_PATH), str(FIXTURE_A), str(FIXTURE_B)],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "fixture_a.jsonl" in result.stdout
    assert "fixture_b.jsonl" in result.stdout
    assert "aggregate" in result.stdout


def test_cli_unreadable_path_clean_error(tmp_path):
    missing = tmp_path / "does_not_exist.jsonl"
    result = subprocess.run(
        [sys.executable, str(MODULE_PATH), str(missing)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "Traceback" not in result.stderr
    assert str(missing) in result.stderr
    assert len(result.stderr.strip().splitlines()) == 1
