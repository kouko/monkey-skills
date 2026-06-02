"""L2 entry point: deep-research CLI.

Usage:
  deep-research "<question>" [--json | --markdown] [--max-fetch N] [--concurrency N]

Builds adapters from env, runs the deep_research() pipeline, then prints
the report.  No network calls in this module — all I/O lives in adapters.
"""
from __future__ import annotations

import argparse
import asyncio
import json
from typing import Any


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="deep-research",
        description="Run a deep multi-source research pipeline on a question.",
    )
    parser.add_argument("question", help="Research question (required)")

    fmt = parser.add_mutually_exclusive_group()
    fmt.add_argument("--json", dest="fmt", action="store_const", const="json",
                     default="json", help="Output report as JSON (default)")
    fmt.add_argument("--markdown", dest="fmt", action="store_const", const="markdown",
                     help="Output report as rendered Markdown")

    parser.add_argument("--max-fetch", type=int, default=None,
                        help="Override MAX_FETCH (number of sources to fetch)")
    parser.add_argument("--concurrency", type=int, default=8,
                        help="Pipeline concurrency (default: 8)")

    return parser.parse_args(argv)


def _render_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = []

    lines.append(f"# {report.get('question', 'Research Report')}\n")

    summary = report.get("summary", "")
    if summary:
        lines.append("## Summary\n")
        lines.append(summary + "\n")

    findings = report.get("findings", [])
    if findings:
        lines.append("## Findings\n")
        for f in findings:
            confidence = f.get("confidence", "")
            claim = f.get("claim", "")
            sources = f.get("sources", [])
            lines.append(f"- **{claim}** *(confidence: {confidence})*")
            for src in sources:
                lines.append(f"  - <{src}>")

    caveats = report.get("caveats", "")
    if caveats:
        lines.append("\n## Caveats\n")
        lines.append(caveats)

    open_qs = report.get("openQuestions", [])
    if open_qs:
        lines.append("\n## Open Questions\n")
        for q in open_qs:
            lines.append(f"- {q}")

    refuted = report.get("refuted", [])
    if refuted:
        lines.append("\n## Refuted Claims\n")
        for r in refuted:
            lines.append(f"- {r.get('claim', '')}")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)

    # Import here so tests can monkeypatch before construction.
    from deep_research import adapters, core

    llm = adapters.AnthropicLLM()
    search = adapters.BraveSearch()
    fetch = adapters.HttpxFetch()

    report = asyncio.run(
        core.deep_research(
            args.question,
            llm,
            search,
            fetch,
            concurrency=args.concurrency,
            max_fetch=args.max_fetch,
        )
    )

    if args.fmt == "markdown":
        print(_render_markdown(report))
    else:
        print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
