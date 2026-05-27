"""report.py — Stage 5c advisory dispatch-payload generator for distill-sessions.

Reads ``merged.json`` (Stage 4 output from ``main.py``) and emits a JSON
dispatch payload to stdout that the Claude Code orchestrator consumes to
dispatch a Sonnet 4.6 advisory-analyst subagent
(``agents/prompt-advisory-analyst.md``).

Pipeline position: Stage 5c (post-propose.py, independent of apply.py).
Input: merged.json produced by ``main.py`` Stage 4 cluster step.
Output (stdout JSON payload): ``{dispatch_payload, output_path}`` —

- ``dispatch_payload.prompt_path``: relative path to the analyst prompt.
- ``dispatch_payload.model``: ``claude-sonnet-4-6`` (parity with main.py
  Stage 3 per-trajectory subagent — 1M context, semantic clustering
  capable).
- ``dispatch_payload.input``: ``{merged_data, lang, date_str}`` fed to
  the subagent. The subagent performs semantic clustering + 7-section
  narrative rendering in the user's working language and returns the
  finished markdown.
- ``output_path``: where the orchestrator writes the returned markdown
  (default ``docs/skill-mining/<date>-advisory-report.md``).

This script remains **stdlib-only**: it never calls an LLM directly.
The dispatch happens at the orchestrator boundary, mirroring how
``main.py`` emits Stage 3 ``subagent_payload`` JSON to stdout. The
``--lang {zh-TW,en,ja}`` flag is **mandatory** so the analyst's prose
matches the user's working language.

CLI::

    python report.py --input merged.json --lang zh-TW

If ``--output`` is omitted, defaults to
``docs/skill-mining/<today>-advisory-report.md`` relative to the repo
root (resolved as ``<script_dir>/../../../../`` or CWD fallback).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

# Subagent model for v0.5 advisory-analyst dispatch.  Parity with main.py:63
# (Stage 3 per-trajectory subagent also runs on Sonnet 4.6 1M-context).  The
# Claude Code orchestrator dispatches this prompt; report.py only emits the
# dispatch-payload JSON to stdout, no LLM call inside this script.
SUBAGENT_MODEL_ID = "claude-sonnet-4-6"


# ---------------------------------------------------------------------------
# Public API.
# ---------------------------------------------------------------------------


def parse_merged_json(path: str) -> list[dict]:
    """Read merged.json from ``path`` and return the list of entries.

    Each entry has keys: ``session_id``, ``trajectory_id``, ``kind``,
    ``target_skill_path``, ``memory_items`` (list of Memory Item dicts).

    Raises ``ValueError`` if the top-level structure is not a list.
    """
    text = Path(path).read_text(encoding="utf-8")
    data = json.loads(text)
    if not isinstance(data, list):
        raise ValueError(
            f"Expected top-level JSON list in {path}, got {type(data).__name__}"
        )
    return data


def build_dispatch_payload(
    merged_data: list[dict],
    lang: str,
    date_str: str,
    output_path: Path | str,
) -> dict[str, object]:
    """Construct the orchestrator-consumable JSON payload for Sonnet 4.6 advisory dispatch.

    Returns the dict the Claude Code orchestrator reads from this script's
    stdout.  The orchestrator dispatches ``prompt_path`` (Sonnet 4.6) with
    ``input`` and writes the returned markdown to ``output_path``.

    Pure function — no I/O, no side effects.  Pattern parity with
    ``main.py`` Stage 3 dispatch payloads (see ``main.py:312-334``).
    """
    return {
        "dispatch_payload": {
            "prompt_path": "agents/prompt-advisory-analyst.md",
            "model": SUBAGENT_MODEL_ID,
            "input": {
                "merged_data": merged_data,
                "lang": lang,
                "date_str": date_str,
            },
        },
        "output_path": str(output_path),
    }


# ---------------------------------------------------------------------------
# CLI.
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    """Entry point for ``python report.py --input ... --lang ...``."""
    parser = argparse.ArgumentParser(
        prog="report",
        description=(
            "Stage 5c: read distill-sessions Stage 4 merged.json and emit a "
            "dispatch payload for the Sonnet 4.6 advisory-analyst subagent."
        ),
    )
    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Path to merged.json (Stage 4 output from main.py).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help=(
            "Where the orchestrator should write the analyst's returned markdown. "
            "Default: docs/skill-mining/<today>-advisory-report.md "
            "relative to repo root."
        ),
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="Override date string (YYYY-MM-DD); default = today.",
    )
    parser.add_argument(
        "--lang",
        required=True,
        choices=["zh-TW", "en", "ja"],
        help="Locale for advisory-report explanatory prose (mandatory; no default).",
    )
    args = parser.parse_args(argv)

    date_str = args.date or date.today().isoformat()

    merged_data = parse_merged_json(str(args.input))

    output_path: Path
    if args.output is not None:
        output_path = args.output
    else:
        # Default: docs/skill-mining/<date>-advisory-report.md
        # Try to resolve from script location (4 levels up to repo root).
        script_dir = Path(__file__).resolve().parent
        repo_root = script_dir.parents[3]  # scripts/ → distill-sessions/ → skills/ → dev-workflow/ → repo root
        output_path = repo_root / "docs" / "skill-mining" / f"{date_str}-advisory-report.md"

    payload = build_dispatch_payload(
        merged_data=merged_data,
        lang=args.lang,
        date_str=date_str,
        output_path=output_path,
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":  # pragma: no cover  (CLI entrypoint)
    sys.exit(main())
