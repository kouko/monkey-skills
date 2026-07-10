"""Headless `claude -p` runner for the L2 e2e harness.

Two pure helpers, no I/O of their own:

- `build_command` assembles the non-interactive `claude` invocation that drives
  a blind Claude Code through `/dbt-wiki:init` -> `/dbt-wiki:pack` -> answering
  each gold question and emitting a final fenced ```json block keyed by trap id.
- `parse_transcript` extracts that inner JSON payload from the run's stdout.

CLI surface grounding (external-surface-grounding): `claude --help` run locally
2026-07-09 confirms `-p, --print` = "Print response and exit... non-interactive
output" and `--output-format <format>` choices `text` / `json` / `stream-json`,
where `json` is documented as "single result"; the same run confirms
`--dangerously-skip-permissions` = "Bypass all permission checks." and
`--add-dir <directories...>` = "Additional directories to allow tool [access]".
A `--output-format json` run
emits ONE outer JSON object whose `result` field carries the final assistant
text; `parse_transcript` unwraps that, then pulls the inner fenced block out of
the text.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

_FENCED_JSON = re.compile(r"```json\s*(.*?)```", re.DOTALL)


def _build_prompt(questions: list[dict[str, Any]]) -> str:
    question_lines = "\n".join(
        f"- {q['trap']}: {q['question'].strip()}" for q in questions
    )
    return (
        "You are a blind analytics teammate. Work only from this dbt project.\n\n"
        "Do these steps in order:\n"
        "1. Run /dbt-wiki:init to scaffold the knowledge base.\n"
        "2. Run /dbt-wiki:pack to package the portable analytics skill.\n"
        "3. Answer each question below by inspecting the project — one numeric "
        "answer per question.\n\n"
        "Questions (each line is `<question_id>: <question>`):\n"
        f"{question_lines}\n\n"
        "Finish your reply with a single fenced ```json code block mapping each "
        "question_id to its numeric answer, e.g.\n"
        "```json\n"
        '{"some_id": 1.23}\n'
        "```\n"
    )


def build_command(
    fixture_dir: Path,
    questions: list[dict[str, Any]],
    skip_permissions: bool = False,
) -> list[str]:
    """Assemble the argv for a headless `claude -p` run over `fixture_dir`.

    The fixture project is passed as an `--add-dir` target so the headless
    agent can read/build it; Task 11's real subprocess call additionally sets
    `cwd=fixture_dir`. `skip_permissions=True` adds `--dangerously-skip-permissions`,
    which the non-interactive run needs so it can execute the two slash commands
    and their tools without blocking on a permission prompt — the caller must opt
    in explicitly (default False) since the flag bypasses every permission gate,
    not just access to `fixture_dir`. Task 11's controlled call site passes
    `skip_permissions=True`.
    """
    cmd = [
        "claude",
        "-p",
        _build_prompt(questions),
        "--output-format",
        "json",
        "--add-dir",
        str(fixture_dir),
    ]
    if skip_permissions:
        cmd.insert(3, "--dangerously-skip-permissions")
    return cmd


def parse_transcript(raw_stdout: str) -> dict[str, Any]:
    """Extract the `{question_id: answer}` payload from `claude -p` stdout.

    `raw_stdout` is the outer `--output-format json` wrapper; its `result`
    field holds the final assistant text, which ends in a fenced ```json block
    carrying the answers. Returns that inner block parsed as a dict.
    """
    result_text = json.loads(raw_stdout)["result"]
    blocks = _FENCED_JSON.findall(result_text)
    if not blocks:
        raise ValueError("no fenced ```json answer block found in transcript result")
    return json.loads(blocks[-1])
