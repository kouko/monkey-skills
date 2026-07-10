"""Task 10 acceptance test — the `claude -p` headless runner.

`runner.py` builds the non-interactive invocation that drives a blind
headless Claude Code through `/dbt-wiki:init` -> `/dbt-wiki:pack` -> answering
each gold question, and parses that run's stdout back into a
`{question_id: answer}` dict.

CLI surface grounding (external-surface-grounding): `claude --help` run
locally 2026-07-09 confirms `-p, --print` = "Print response and exit... use
-p/--print for non-interactive output" and `--output-format <format>` choices
`text` / `json` / `stream-json`, where `json` is documented as "single
result". A `--output-format json` run emits ONE outer JSON object whose
`result` field holds the final assistant text; the canned fixture below models
exactly that nested shape.

No real subprocess is spawned here — `build_command` is a pure function and
`parse_transcript` runs against a canned transcript string. Task 11 makes the
real `claude -p` call.
"""
from __future__ import annotations

from pathlib import Path

import runner

# A trimmed slice of gold-questions.yml's parsed shape (list of dicts with a
# `trap` id + `question` text) — enough to prove build_command embeds each
# question's id and prompt text.
QUESTIONS = [
    {"trap": "avg_ratio", "question": "What is the overall weighted ratio?"},
    {"trap": "categorical", "question": "How many customers have status 'active'?"},
]

# Canned raw stdout from `claude -p --output-format json`: the OUTER object is
# the run wrapper; its `result` field is the final assistant text, which itself
# ends in a fenced ```json block carrying the {question_id: answer} payload.
# parse_transcript must dig out the INNER block, not the outer wrapper.
CANNED_TRANSCRIPT = """{
  "type": "result",
  "subtype": "success",
  "is_error": false,
  "num_turns": 12,
  "session_id": "abc-123",
  "result": "I ran /dbt-wiki:init then /dbt-wiki:pack, then answered each question by inspecting the project.\\n\\nFinal answers:\\n\\n```json\\n{\\n  \\"avg_ratio\\": 0.0875,\\n  \\"categorical\\": 3\\n}\\n```\\n"
}"""


def test_build_command_targets_headless_claude_at_fixture_dir():
    fixture_dir = Path("/tmp/l2-harness")
    # skip_permissions=True: this test models Task 11's real headless call site,
    # which must opt in explicitly to bypass permission prompts (default is off).
    cmd = runner.build_command(fixture_dir, QUESTIONS, skip_permissions=True)

    assert cmd[0] == "claude"
    # -p / --print: the officially-supported non-interactive mechanism.
    assert "-p" in cmd or "--print" in cmd
    # single-result JSON output.
    assert "--output-format" in cmd
    assert cmd[cmd.index("--output-format") + 1] == "json"
    # The fixture project must be the working root the headless agent operates
    # on (passed as an --add-dir target; Task 11 also sets it as subprocess cwd).
    assert str(fixture_dir) in cmd
    # Opt-in flag must be present when skip_permissions=True is requested.
    assert "--dangerously-skip-permissions" in cmd

    # The prompt must sequence init -> pack and embed every question's id + text.
    prompt_blob = " ".join(cmd)
    assert "/dbt-wiki:init" in prompt_blob
    assert "/dbt-wiki:pack" in prompt_blob
    for q in QUESTIONS:
        assert q["trap"] in prompt_blob
        assert q["question"] in prompt_blob


def test_build_command_defaults_to_not_skipping_permissions():
    fixture_dir = Path("/tmp/l2-harness")
    cmd = runner.build_command(fixture_dir, QUESTIONS)

    assert "--dangerously-skip-permissions" not in cmd


def test_runner_parses_claude_json_output_into_answers():
    answers = runner.parse_transcript(CANNED_TRANSCRIPT)
    assert answers == {"avg_ratio": 0.0875, "categorical": 3}
