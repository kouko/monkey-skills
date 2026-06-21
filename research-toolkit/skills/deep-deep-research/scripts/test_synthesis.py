"""Tests for synthesis.py — pure synthesis helpers (blocks + stats + render).

RED: synthesis.py does not exist — these tests must fail on import.

Flat imports (NOT deep_research.synthesis) — this module lives in scripts/
and is invoked directly via `python synthesis.py {blocks|report}`.
"""
import json
import subprocess
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent


class TestConfirmedBlock:
    """_confirmed_block emits `### [i] {claim}` + `Vote: {valid-refuted}-{refuted}`."""

    def test_confirmed_block_format(self):
        from synthesis import _confirmed_block

        claim = {
            "claim": "Caffeine delays sleep onset by 30-60 minutes.",
            "sourceUrl": "https://example.com/study1",
            "sourceQuality": "primary",
            "quote": "caffeine ingestion delayed sleep onset significantly.",
        }
        verdicts_per_claim = [
            [
                {"refuted": False, "evidence": "Consistent with pharmacology.", "confidence": "high"},
                {"refuted": False, "evidence": "Backed by RCTs.", "confidence": "medium"},
                {"refuted": False, "evidence": "Well-known effect.", "confidence": "low"},
            ]
        ]
        survived = [True]

        block = _confirmed_block([claim], survived, verdicts_per_claim)

        # `### [i] {claim}` header
        assert "### [0] Caffeine delays sleep onset by 30-60 minutes." in block
        # `Vote: {valid-refuted}-{refuted}` — valid=3, refuted=0 → 3-0
        assert "Vote: 3-0" in block
        # best non-refuting verdict is highest-confidence (high)
        assert "Verifier evidence (high): Consistent with pharmacology." in block

    def test_confirmed_block_picks_best_non_refuting(self):
        from synthesis import _confirmed_block

        claim = {
            "claim": "Coffee disrupts REM sleep.",
            "sourceUrl": "https://example.com/rem",
            "sourceQuality": "secondary",
            "quote": "REM disruption observed.",
        }
        verdicts_per_claim = [
            [
                {"refuted": True, "evidence": "No REM disruption.", "confidence": "high"},
                {"refuted": False, "evidence": "Medium support.", "confidence": "medium"},
                {"refuted": False, "evidence": "Low support.", "confidence": "low"},
            ]
        ]
        survived = [True]

        block = _confirmed_block([claim], survived, verdicts_per_claim)
        # valid=3, refuted=1 → 2-1; best non-refuting = medium
        assert "Vote: 2-1" in block
        assert "Verifier evidence (medium): Medium support." in block


class TestKilledBlock:
    def test_killed_block_lists_refuted(self):
        from synthesis import _killed_block

        claims = [
            {"claim": "Survives.", "sourceUrl": "https://a"},
            {"claim": "One cup of coffee has no effect.", "sourceUrl": "https://b"},
        ]
        survived = [True, False]
        block = _killed_block(claims, survived)
        assert "## Refuted claims (for transparency)" in block
        assert '- "One cup of coffee has no effect." (https://b)' in block
        # surviving claim must NOT appear in the killed block
        assert "Survives." not in block


class TestCollectSources:
    def test_unique_in_insertion_order(self):
        from synthesis import _collect_sources

        claims = [
            {"sourceUrl": "https://a"},
            {"sourceUrl": "https://b"},
            {"sourceUrl": "https://a"},  # dup
            {"sourceUrl": ""},  # empty skipped
        ]
        assert _collect_sources(claims) == ["https://a", "https://b"]


class TestBuildStats:
    def test_agent_calls_formula(self):
        from synthesis import _build_stats

        angles = [{}, {}, {}]  # 3
        sources = ["u1", "u2"]  # 2
        all_claims = [{}, {}]  # 2 extracted
        ranked_claims = [{}, {}]  # 2 verified
        confirmed = [{}]  # 1
        killed = [{}]  # 1

        stats = _build_stats(angles, sources, all_claims, ranked_claims, confirmed, killed)
        # agentCalls = 1 + angles + sources + verified*VOTES_PER_CLAIM(3) + 1
        # = 1 + 3 + 2 + (2*3) + 1 = 13
        assert stats["agentCalls"] == 13
        assert stats["angles"] == 3
        assert stats["sourcesFetched"] == 2
        assert stats["claimsExtracted"] == 2
        assert stats["claimsVerified"] == 2
        assert stats["confirmed"] == 1
        assert stats["killed"] == 1


class TestRenderMarkdown:
    def test_findings_section_emitted(self):
        from synthesis import _render_markdown

        report = {
            "question": "What is the effect of caffeine on sleep?",
            "summary": "Caffeine delays sleep onset.",
            "findings": [
                {
                    "claim": "Caffeine delays sleep onset.",
                    "confidence": "high",
                    "sources": ["https://example.com/study1"],
                }
            ],
        }
        md = _render_markdown(report)
        assert "# What is the effect of caffeine on sleep?" in md
        assert "## Summary" in md
        assert "## Findings" in md
        assert "**Caffeine delays sleep onset.**" in md
        assert "<https://example.com/study1>" in md


class TestBlocksCLI:
    def test_blocks_subcommand(self):
        payload = {
            "ranked_claims": [
                {
                    "claim": "C1.",
                    "sourceUrl": "https://a",
                    "sourceQuality": "primary",
                    "quote": "q1",
                },
                {"claim": "C2.", "sourceUrl": "https://b"},
            ],
            "vote_results": [True, False],
            "verdicts_per_claim": [
                [{"refuted": False, "evidence": "ev", "confidence": "high"}],
                [],
            ],
        }
        out = subprocess.run(
            [sys.executable, "synthesis.py", "blocks"],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            cwd=_SCRIPTS_DIR,
        )
        assert out.returncode == 0, out.stderr
        result = json.loads(out.stdout)
        assert "### [0] C1." in result["confirmed_block"]
        assert "Vote: 1-0" in result["confirmed_block"]
        assert '- "C2." (https://b)' in result["killed_block"]


class TestReportCLI:
    def test_report_subcommand(self):
        payload = {
            "report": {
                "question": "Q?",
                "summary": "s",
                "findings": [
                    {"claim": "F1.", "confidence": "high", "sources": ["https://a"]}
                ],
            },
            "ranked_claims": [{"sourceUrl": "https://a"}, {"sourceUrl": "https://b"}],
            "angles": [{}, {}, {}],
            "all_claims": [{}, {}],
            "confirmed": [{}],
            "killed": [{}],
        }
        out = subprocess.run(
            [sys.executable, "synthesis.py", "report"],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            cwd=_SCRIPTS_DIR,
        )
        assert out.returncode == 0, out.stderr
        result = json.loads(out.stdout)
        # 2 sources collected from ranked_claims
        assert result["stats"]["sourcesFetched"] == 2
        # agentCalls = 1 + 3 + 2 + (2*3) + 1 = 13
        assert result["stats"]["agentCalls"] == 13
        assert "## Findings" in result["markdown"]
        assert "# Q?" in result["markdown"]
