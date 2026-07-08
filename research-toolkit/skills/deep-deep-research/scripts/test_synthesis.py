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

    def test_confirmed_block_falls_back_to_url_when_sourceurl_missing(self):
        from synthesis import _confirmed_block

        claim = {
            "claim": "Url-keyed claim.",
            "url": "https://example.com/url-keyed",
            "sourceQuality": "primary",
            "quote": "q",
        }
        verdicts_per_claim = [
            [{"refuted": False, "evidence": "ev", "confidence": "high"}]
        ]
        block = _confirmed_block([claim], [True], verdicts_per_claim)
        assert "https://example.com/url-keyed" in block

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

    def test_killed_block_falls_back_to_url_when_sourceurl_missing(self):
        from synthesis import _killed_block

        claims = [{"claim": "Refuted, url-keyed.", "url": "https://c"}]
        block = _killed_block(claims, [False])
        assert '- "Refuted, url-keyed." (https://c)' in block


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

    def test_falls_back_to_url_when_sourceurl_missing(self):
        from synthesis import _collect_sources

        claims = [{"url": "https://d"}, {"sourceUrl": "https://e"}]
        assert _collect_sources(claims) == ["https://d", "https://e"]


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

    def test_caveats_list_is_coerced_to_string(self):
        """LLM sometimes emits caveats as a list, not the schema's plain
        string; the renderer must not crash and must render every item."""
        from synthesis import _render_markdown

        report = {
            "question": "Q?",
            "summary": "s",
            "findings": [],
            "caveats": ["First caveat.", "Second caveat."],
        }
        md = _render_markdown(report)
        assert "## Caveats" in md
        assert "First caveat." in md
        assert "Second caveat." in md

    def test_finding_evidence_is_rendered(self):
        """Every finding's `evidence` field is schema-required but was
        silently dropped by the renderer; it must appear in the output."""
        from synthesis import _render_markdown

        report = {
            "question": "Q?",
            "summary": "s",
            "findings": [
                {
                    "claim": "Caffeine delays sleep onset.",
                    "confidence": "high",
                    "sources": ["https://example.com/study1"],
                    "evidence": "Because of X and Y.",
                }
            ],
        }
        md = _render_markdown(report)
        assert "Because of X and Y." in md


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


class TestKeyFileFlags:
    """--key NAME=FILE / --key-dir NAME=DIR assemble the payload from files.

    Any flag disables stdin; output must equal the stdin-payload run.
    """

    def test_blocks_payload_from_key_files(self, tmp_path):
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
        flags = []
        for name in ("ranked_claims", "vote_results", "verdicts_per_claim"):
            path = tmp_path / f"{name}.json"
            path.write_text(json.dumps(payload[name]), encoding="utf-8")
            flags += ["--key", f"{name}={path}"]

        via_stdin = subprocess.run(
            [sys.executable, "synthesis.py", "blocks"],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            cwd=_SCRIPTS_DIR,
        )
        assert via_stdin.returncode == 0, via_stdin.stderr

        via_flags = subprocess.run(
            [sys.executable, "synthesis.py", "blocks", *flags],
            # deliberately NOT JSON: proves stdin is ignored when flags present
            input="NOT JSON",
            capture_output=True,
            text=True,
            cwd=_SCRIPTS_DIR,
        )
        assert via_flags.returncode == 0, via_flags.stderr
        assert json.loads(via_flags.stdout) == json.loads(via_stdin.stdout)

    def test_report_key_dir_merges_json_arrays_filename_sorted(self, tmp_path):
        claims_dir = tmp_path / "claims"
        claims_dir.mkdir()
        # written out of filename order: merge must be filename-sorted
        (claims_dir / "02-econ.json").write_text(
            json.dumps([{"claim": "B1."}]), encoding="utf-8"
        )
        (claims_dir / "01-health.json").write_text(
            json.dumps([{"claim": "A1."}, {"claim": "A2."}]), encoding="utf-8"
        )
        payload = {
            "report": {"question": "Q?", "summary": "s", "findings": []},
            "ranked_claims": [{"sourceUrl": "https://a"}],
            "angles": [{}, {}],
            "all_claims": [{"claim": "A1."}, {"claim": "A2."}, {"claim": "B1."}],
            "confirmed": [{}],
            "killed": [],
        }
        flags = ["--key-dir", f"all_claims={claims_dir}"]
        for name in ("report", "ranked_claims", "angles", "confirmed", "killed"):
            path = tmp_path / f"{name}.json"
            path.write_text(json.dumps(payload[name]), encoding="utf-8")
            flags += ["--key", f"{name}={path}"]

        via_stdin = subprocess.run(
            [sys.executable, "synthesis.py", "report"],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            cwd=_SCRIPTS_DIR,
        )
        assert via_stdin.returncode == 0, via_stdin.stderr

        via_flags = subprocess.run(
            [sys.executable, "synthesis.py", "report", *flags],
            input="NOT JSON",
            capture_output=True,
            text=True,
            cwd=_SCRIPTS_DIR,
        )
        assert via_flags.returncode == 0, via_flags.stderr
        result = json.loads(via_flags.stdout)
        assert result == json.loads(via_stdin.stdout)
        # 3 claims merged from the two dir files
        assert result["stats"]["claimsExtracted"] == 3


class TestKeyFlagErrors:
    """Every --key / --key-dir error branch exits 1 with a one-line stderr
    message naming the offender (house pattern: rank.py named-offender exits).
    No raw tracebacks may escape to the caller."""

    @staticmethod
    def _run(flags):
        return subprocess.run(
            [sys.executable, "synthesis.py", "blocks", *flags],
            input="",
            capture_output=True,
            text=True,
            cwd=_SCRIPTS_DIR,
        )

    def test_unknown_flag_exits_1_with_message(self):
        out = self._run(["--bogus", "x=y"])
        assert out.returncode == 1
        assert "expected --key NAME=FILE or --key-dir NAME=DIR" in out.stderr
        assert "--bogus" in out.stderr

    def test_malformed_name_path_exits_1_with_message(self):
        out = self._run(["--key", "no-equals-here"])
        assert out.returncode == 1
        assert "malformed" in out.stderr
        assert "NAME=PATH" in out.stderr

    def test_key_dir_non_array_file_exits_1_naming_file(self, tmp_path):
        d = tmp_path / "claims"
        d.mkdir()
        (d / "01-bad.json").write_text(json.dumps({"claim": "obj"}), encoding="utf-8")
        out = self._run(["--key-dir", f"all_claims={d}"])
        assert out.returncode == 1
        assert "not a JSON array" in out.stderr
        assert "01-bad.json" in out.stderr

    def test_key_dir_nonexistent_dir_exits_1_not_silent_empty(self, tmp_path):
        missing = tmp_path / "nope"
        out = self._run(["--key-dir", f"all_claims={missing}"])
        assert out.returncode == 1
        assert "not a directory" in out.stderr
        assert str(missing) in out.stderr

    def test_key_invalid_json_exits_1_naming_path(self, tmp_path):
        bad = tmp_path / "bad.json"
        bad.write_text("{not json", encoding="utf-8")
        out = self._run(["--key", f"ranked_claims={bad}"])
        assert out.returncode == 1
        assert f"--key ranked_claims: {bad}:" in out.stderr
        assert "Traceback" not in out.stderr

    def test_key_missing_file_exits_1_clean_stderr(self, tmp_path):
        missing = tmp_path / "absent.json"
        out = self._run(["--key", f"ranked_claims={missing}"])
        assert out.returncode == 1
        assert str(missing) in out.stderr
        assert "Traceback" not in out.stderr


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
