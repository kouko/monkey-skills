"""Comms metrics recipe for Claude Code transcript JSONL files.

Computes, per transcript and aggregated across transcripts:

  (a) wrong-language turn ratio — assistant main-chain narration turns
      with >=200 visible (non-whitespace, noise-stripped) characters
      whose detected script mismatches the rolling conversation
      language, recomputed from user turns seen so far (not a fixed
      whole-file language). Turns where either side cannot be
      determined (None) are excluded from both numerator and
      denominator.
  (b) visual-at-fork rate — AskUserQuestion tool_use turns where a
      markdown table or an ascii/box-drawing diagram appears in the
      same assistant turn or either of the 2 preceding assistant
      turns (audit doc §B4's "the ask turn or the two assistant turns
      before it" window).
  (c) confusion-signal count — user main-chain turns matching any
      pattern in the extensible ``CONFUSION_PATTERNS`` list. A turn
      matching multiple patterns still counts once (turn-level).

Pure stdlib; no hardcoded conversation/target language anywhere — script
detection is delegated to loom-pipeline/hooks/lang_detect.py (loaded by
path, same convention as test_lang_detect.py, since hooks/ is not an
installed package).

CLI: ``python3 comms_metrics.py <jsonl...> [--json]``
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Optional

_HOOKS_DIR = Path(__file__).resolve().parent.parent / "hooks"
_LANG_DETECT_PATH = _HOOKS_DIR / "lang_detect.py"


def _load_lang_detect():
    spec = importlib.util.spec_from_file_location("lang_detect", _LANG_DETECT_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


lang_detect = _load_lang_detect()

_MIN_VISIBLE_CHARS_FOR_LANG_CHECK = 200
_ROLLING_WINDOW = 3
_FORK_LOOKBACK = 2  # preceding assistant turns checked for a visual, plus the ask turn itself

# Confusion-signal patterns — extensible module-level list (add more
# regexes here; each is tried independently, a turn matching any one
# of them counts once).
CONFUSION_PATTERNS = [
    re.compile(p)
    for p in [
        r"什麼意思",
        r"看不懂",
        r"？？",
        r"意義與影響",
        r"講簡單",
        r"白話",
        r"what do you mean",
    ]
]

# Box-drawing block (─│┌┐└┘├┤┬┴┼ etc.) or a plain-ascii box border
# like +---+ / +===+.
# A "structural" diagram line contains a box-drawing char (U+2500
# block: ─│┌┐└┘├┤═║╔╗╚╝…), an arrow (→▶←↔↑↓▲▼), or a plain-ascii box
# border (+---+ / +===+).
_DIAGRAM_LINE_RE = re.compile(r"[─-╿]|[→▶←↔↑↓▲▼]|[+][-=]{2,}[+]")
_MIN_DIAGRAM_LINES = 3
_SEPARATOR_ALLOWED_CHARS = set(" -:")
_CODE_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)


def _has_markdown_table(text: str) -> bool:
    """A markdown table: a line starting with ``|`` immediately
    followed by a GFM separator row (``| --- | --- |`` etc.). The
    separator row may have multiple ``|`` column dividers, so pipes
    are stripped before checking that only ``-``/``:``/space remain
    and at least one ``-`` is present.

    Scans OUTSIDE code fences only — a table inside a ``` fence is a
    code example (syntax being quoted), not a rendered comparison
    table put in front of the user."""
    lines = _CODE_FENCE_RE.sub(" ", text).split("\n")
    for i in range(len(lines) - 1):
        header = lines[i].strip()
        if not header.startswith("|"):
            continue
        sep_no_pipes = lines[i + 1].strip().replace("|", "")
        if "-" in sep_no_pipes and set(sep_no_pipes) <= _SEPARATOR_ALLOWED_CHARS:
            return True
    return False


def _has_ascii_diagram(text: str) -> bool:
    """>=3 lines containing box-drawing/arrow chars or +--+ borders.

    Fenced content stays IN scope (unlike ``_has_markdown_table``):
    deliberate ascii diagrams are normally fenced in chat, so
    stripping fences would undercount them. The trade-off of the
    >=3-structural-lines floor: plain python/log pastes have no
    box/arrow lines and never count, while a pasted ``tree`` output
    with many ├── lines still counts — acceptable, it IS ascii
    structure the user sees."""
    structural = sum(1 for line in text.split("\n") if _DIAGRAM_LINE_RE.search(line))
    return structural >= _MIN_DIAGRAM_LINES


def _has_visual(text: str) -> bool:
    return _has_markdown_table(text) or _has_ascii_diagram(text)


def _is_confusion_signal(text: str) -> bool:
    return any(pattern.search(text) for pattern in CONFUSION_PATTERNS)


def _iter_entries(transcript_path):
    with open(transcript_path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if isinstance(entry, dict):
                yield entry


def _narration_text(entry, expected_type: str) -> Optional[str]:
    """Raw narration text for an eligible main-chain turn of
    ``expected_type`` ('user' or 'assistant'), mirroring
    lang_detect._iter_user_turns' eligibility filter (excludes
    sidechain turns and tool-result/command-wrapper XML), generalized
    to also cover assistant turns. Returns None when not eligible."""
    if entry.get("type") != expected_type or entry.get("isSidechain"):
        return None
    message = entry.get("message")
    if not isinstance(message, dict):
        return None
    text = lang_detect.extract_text(message.get("content"))
    stripped = text.strip()
    if not stripped or stripped.startswith("<"):
        return None
    return text


def _has_ask_user_question(entry) -> bool:
    if entry.get("type") != "assistant" or entry.get("isSidechain"):
        return False
    message = entry.get("message")
    if not isinstance(message, dict):
        return False
    content = message.get("content")
    if not isinstance(content, list):
        return False
    return any(
        isinstance(block, dict)
        and block.get("type") == "tool_use"
        and block.get("name") == "AskUserQuestion"
        for block in content
    )


def _rolling_conversation_language(user_texts_so_far, n_turns: int = _ROLLING_WINDOW) -> Optional[str]:
    """Majority language over the last ``n_turns`` user narration texts
    seen so far — the same majority rule as
    lang_detect.conversation_language, applied to a point-in-time
    prefix instead of the whole file."""
    sampled = user_texts_so_far[-n_turns:]
    if not sampled:
        return None
    langs = [lang_detect.detect_script(lang_detect.strip_noise(t)) for t in sampled]
    counts = Counter(lang for lang in langs if lang is not None)
    if not counts:
        return None
    lang, count = counts.most_common(1)[0]
    if count > len(sampled) / 2:
        return lang
    return None


def _visible_len(text: str) -> int:
    return len([c for c in text if not c.isspace()])


def compute_metrics(transcript_path) -> dict:
    """Compute the three comms metrics for one transcript JSONL file."""
    user_texts: list[str] = []
    recent_assistant_texts: list[str] = []  # up to the last _FORK_LOOKBACK assistant texts

    wrong_count = 0
    wrong_eligible = 0
    ask_count = 0
    visual_count = 0
    confusion_count = 0

    for entry in _iter_entries(transcript_path):
        etype = entry.get("type")
        if entry.get("isSidechain"):
            continue

        if etype == "user":
            text = _narration_text(entry, "user")
            if text is not None:
                if _is_confusion_signal(text):
                    confusion_count += 1
                user_texts.append(text)
            continue

        if etype != "assistant":
            continue

        message = entry.get("message")
        content = message.get("content") if isinstance(message, dict) else None
        raw_text = lang_detect.extract_text(content) if content is not None else ""

        if _has_ask_user_question(entry):
            ask_count += 1
            window = recent_assistant_texts[-_FORK_LOOKBACK:] + [raw_text]
            if any(_has_visual(t) for t in window):
                visual_count += 1

        stripped = lang_detect.strip_noise(raw_text)
        if _visible_len(stripped) >= _MIN_VISIBLE_CHARS_FOR_LANG_CHECK:
            expected = _rolling_conversation_language(user_texts)
            actual = lang_detect.detect_script(stripped)
            if expected is not None and actual is not None:
                wrong_eligible += 1
                if expected != actual:
                    wrong_count += 1

        recent_assistant_texts.append(raw_text)
        if len(recent_assistant_texts) > _FORK_LOOKBACK:
            recent_assistant_texts.pop(0)

    return {
        "file": str(transcript_path),
        "wrong_language_count": wrong_count,
        "wrong_language_eligible": wrong_eligible,
        "wrong_language_ratio": (wrong_count / wrong_eligible) if wrong_eligible else 0.0,
        "visual_at_fork_count": visual_count,
        "visual_at_fork_eligible": ask_count,
        "visual_at_fork_rate": (visual_count / ask_count) if ask_count else 0.0,
        "confusion_signal_count": confusion_count,
    }


def aggregate_metrics(per_file: list[dict]) -> dict:
    """Sum-then-divide aggregate across multiple per-file metric dicts."""
    wrong_count = sum(f["wrong_language_count"] for f in per_file)
    wrong_eligible = sum(f["wrong_language_eligible"] for f in per_file)
    visual_count = sum(f["visual_at_fork_count"] for f in per_file)
    ask_count = sum(f["visual_at_fork_eligible"] for f in per_file)
    confusion_count = sum(f["confusion_signal_count"] for f in per_file)

    return {
        "wrong_language_count": wrong_count,
        "wrong_language_eligible": wrong_eligible,
        "wrong_language_ratio": (wrong_count / wrong_eligible) if wrong_eligible else 0.0,
        "visual_at_fork_count": visual_count,
        "visual_at_fork_eligible": ask_count,
        "visual_at_fork_rate": (visual_count / ask_count) if ask_count else 0.0,
        "confusion_signal_count": confusion_count,
    }


def _print_metrics_block(label: str, m: dict) -> None:
    print(f"{label}:")
    print(
        f"  wrong-language ratio: {m['wrong_language_count']}/{m['wrong_language_eligible']}"
        f" = {m['wrong_language_ratio']:.2f}"
    )
    print(
        f"  visual-at-fork rate: {m['visual_at_fork_count']}/{m['visual_at_fork_eligible']}"
        f" = {m['visual_at_fork_rate']:.2f}"
    )
    print(f"  confusion-signal count: {m['confusion_signal_count']}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Compute comms metrics (wrong-language ratio, visual-at-fork rate, "
        "confusion-signal count) over Claude Code transcript JSONL files."
    )
    parser.add_argument("transcripts", nargs="+", help="Transcript JSONL path(s)")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of plain text")
    args = parser.parse_args(argv)

    try:
        per_file = [compute_metrics(Path(p)) for p in args.transcripts]
    except OSError as exc:
        print(f"comms_metrics: cannot read {exc.filename}: {exc.strerror}", file=sys.stderr)
        return 1
    aggregate = aggregate_metrics(per_file)

    if args.json:
        print(json.dumps({"per_file": per_file, "aggregate": aggregate}, ensure_ascii=False, indent=2))
        return 0

    for m in per_file:
        _print_metrics_block(m["file"], m)
    _print_metrics_block("aggregate", aggregate)
    return 0


if __name__ == "__main__":
    sys.exit(main())
