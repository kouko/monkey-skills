"""Tests for cli.py — L2 entry point.

RED: cli.py does not exist — imports will fail.
"""
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


# ---------------------------------------------------------------------------
# Canned report fixture
# ---------------------------------------------------------------------------

_CANNED_REPORT = {
    "question": "my question",
    "summary": "A summary.",
    "findings": [
        {
            "claim": "Fact A.",
            "confidence": "high",
            "sources": ["https://example.com/a"],
            "evidence": "Evidence.",
        }
    ],
    "caveats": "None.",
    "openQuestions": ["Follow up?"],
    "refuted": [],
    "sources": ["https://example.com/a"],
    "stats": {
        "angles": 1,
        "sourcesFetched": 1,
        "claimsExtracted": 1,
        "claimsVerified": 1,
        "confirmed": 1,
        "killed": 0,
        "agentCalls": 5,
    },
}


# ---------------------------------------------------------------------------
# Smoke tests
# ---------------------------------------------------------------------------

class TestCLISmoke:
    def test_cli_smoke_json_output(self, capsys):
        """main(["my question", "--json"]) prints valid JSON report to stdout."""
        with (
            patch("deep_research.adapters.AnthropicLLM") as mock_llm_cls,
            patch("deep_research.adapters.BraveSearch") as mock_search_cls,
            patch("deep_research.adapters.HttpxFetch") as mock_fetch_cls,
            patch("deep_research.core.deep_research", new_callable=AsyncMock) as mock_core,
        ):
            mock_llm_cls.return_value = MagicMock()
            mock_search_cls.return_value = MagicMock()
            mock_fetch_cls.return_value = MagicMock()
            mock_core.return_value = _CANNED_REPORT

            from deep_research.cli import main
            main(["my question", "--json"])

        captured = capsys.readouterr()
        assert captured.out.strip(), "stdout must not be empty"

        parsed = json.loads(captured.out)
        assert parsed["question"] == "my question"
        assert "summary" in parsed

    def test_cli_smoke_no_question_exits_nonzero(self, capsys):
        """main([]) exits non-zero with a usage message on stderr."""
        from deep_research.cli import main

        with pytest.raises(SystemExit) as exc_info:
            main([])

        assert exc_info.value.code != 0, "exit code must be non-zero when question is missing"
        captured = capsys.readouterr()
        assert captured.err.strip(), "stderr must contain usage message when question is missing"

    def test_cli_smoke_markdown_output(self, capsys):
        """main(["my question", "--markdown"]) prints markdown to stdout."""
        with (
            patch("deep_research.adapters.AnthropicLLM") as mock_llm_cls,
            patch("deep_research.adapters.BraveSearch") as mock_search_cls,
            patch("deep_research.adapters.HttpxFetch") as mock_fetch_cls,
            patch("deep_research.core.deep_research", new_callable=AsyncMock) as mock_core,
        ):
            mock_llm_cls.return_value = MagicMock()
            mock_search_cls.return_value = MagicMock()
            mock_fetch_cls.return_value = MagicMock()
            mock_core.return_value = _CANNED_REPORT

            from deep_research.cli import main
            main(["my question", "--markdown"])

        captured = capsys.readouterr()
        assert captured.out.strip(), "stdout must not be empty for --markdown"
        # Markdown output should not be parseable as JSON
        try:
            json.loads(captured.out)
            is_json = True
        except json.JSONDecodeError:
            is_json = False
        assert not is_json, "--markdown output must not be valid JSON"

    def test_cli_max_fetch_forwarded(self):
        """--max-fetch 5 must be forwarded as max_fetch=5 to core.deep_research.

        WHY: Without forwarding the user's budget override is silently dropped.
        """
        with (
            patch("deep_research.adapters.AnthropicLLM") as mock_llm_cls,
            patch("deep_research.adapters.BraveSearch") as mock_search_cls,
            patch("deep_research.adapters.HttpxFetch") as mock_fetch_cls,
            patch("deep_research.core.deep_research", new_callable=AsyncMock) as mock_core,
        ):
            mock_llm_cls.return_value = MagicMock()
            mock_search_cls.return_value = MagicMock()
            mock_fetch_cls.return_value = MagicMock()
            mock_core.return_value = _CANNED_REPORT

            from deep_research.cli import main
            main(["my question", "--max-fetch", "5"])

        called_kwargs = mock_core.call_args.kwargs
        assert called_kwargs.get("max_fetch") == 5, (
            f"core.deep_research must be called with max_fetch=5, got kwargs={called_kwargs}"
        )
