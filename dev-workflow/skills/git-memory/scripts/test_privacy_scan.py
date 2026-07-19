"""test_privacy_scan.py — tests for privacy-scan.py (layer-1 deterministic secrets scan).

Per plan Task 1 acceptance (docs/loom/plans/2026-07-19-closeout-privacy-gate.md):
1. A planted AWS access key / GitHub token / PEM private-key header each yields
   exit 3 + a JSON finding naming the pattern.
2. A clean paragraph (no secret) yields exit 0 + an empty JSON list.
3. Redaction: the full secret literal never appears in stdout.
4. The script also reads from stdin when --text-file is omitted (zero-config CLI).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

_SCRIPT = Path(__file__).parent / "privacy-scan.py"

# AKIAIOSFODNN7EXAMPLE is AWS's own published documentation example key
# (docs.aws.amazon.com), not a live credential — safe to plant in a test fixture.
AWS_KEY = "AKIAIOSFODNN7EXAMPLE"
GITHUB_TOKEN = "ghp_1234567890abcdefghijklmnopqrstuvwxyzAB"
# Fine-grained PAT shape: github_pat_ + 22 chars + _ + 59 chars (GitHub's
# default PAT format since 2022; classic ghp_/gho_ alone misses this class).
GITHUB_FINE_GRAINED_PAT = (
    "github_pat_" + "A" * 22 + "_" + "B" * 59
)
PEM_HEADER = "-----BEGIN RSA PRIVATE KEY-----"
SLACK_BOT_TOKEN = "xoxb-1234567890-1234567890123-abcdefghijklmnopqrstuvwx"
SLACK_WEBHOOK = "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
CLEAN_PARAGRAPH = (
    "This commit refactors the retry logic in the sync loop and adds "
    "regression tests for the timeout path. No behavior change for callers."
)


def _run(text: str, tmp_path: Path, use_stdin: bool = False) -> subprocess.CompletedProcess:
    if use_stdin:
        return subprocess.run(
            [sys.executable, str(_SCRIPT)],
            input=text,
            capture_output=True,
            text=True,
        )
    text_file = tmp_path / "composed.txt"
    text_file.write_text(text, encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(_SCRIPT), "--text-file", str(text_file)],
        capture_output=True,
        text=True,
    )


def test_planted_aws_key_exits_3_with_finding(tmp_path: Path) -> None:
    result = _run(f"AWS_ACCESS_KEY_ID={AWS_KEY}\n", tmp_path)
    assert result.returncode == 3, result.stderr
    findings = json.loads(result.stdout)
    assert len(findings) >= 1
    assert any(f["pattern"] == "aws_access_key" for f in findings)


def test_planted_github_token_exits_3_with_finding(tmp_path: Path) -> None:
    result = _run(f"token: {GITHUB_TOKEN}\n", tmp_path)
    assert result.returncode == 3, result.stderr
    findings = json.loads(result.stdout)
    assert any(f["pattern"] == "github_token" for f in findings)


def test_planted_github_fine_grained_pat_exits_3_with_finding(tmp_path: Path) -> None:
    # GitHub's default PAT format since 2022 (github_pat_...); classic
    # gh[po]_ regex alone is a false negative for this class.
    result = _run(f"token: {GITHUB_FINE_GRAINED_PAT}\n", tmp_path)
    assert result.returncode == 3, result.stderr
    findings = json.loads(result.stdout)
    assert any(f["pattern"] == "github_token" for f in findings)
    assert GITHUB_FINE_GRAINED_PAT not in result.stdout


def test_planted_slack_bot_token_exits_3_with_finding(tmp_path: Path) -> None:
    result = _run(f"token: {SLACK_BOT_TOKEN}\n", tmp_path)
    assert result.returncode == 3, result.stderr
    findings = json.loads(result.stdout)
    assert any(f["pattern"] == "slack_token" for f in findings)


def test_planted_slack_webhook_exits_3_with_finding(tmp_path: Path) -> None:
    result = _run(f"webhook: {SLACK_WEBHOOK}\n", tmp_path)
    assert result.returncode == 3, result.stderr
    findings = json.loads(result.stdout)
    assert any(f["pattern"] == "slack_webhook" for f in findings)


def test_planted_generic_secret_assignment_exits_3_with_finding(tmp_path: Path) -> None:
    result = _run("SECRET=abcdefghijklmnopqrstuvwxyz\n", tmp_path)
    assert result.returncode == 3, result.stderr
    findings = json.loads(result.stdout)
    assert any(f["pattern"] == "generic_secret_assignment" for f in findings)


def test_short_value_with_token_substring_is_clean(tmp_path: Path) -> None:
    # Pins the length-heuristic boundary: "token" appears as a substring
    # but the assigned value is short (<16 chars) — must NOT trip the
    # generic_secret_assignment heuristic (false-positive boundary check).
    result = _run("session_token=abc123\n", tmp_path)
    assert result.returncode == 0, result.stderr
    findings = json.loads(result.stdout)
    assert findings == []


def test_generic_assignment_boundary_15_chars_is_clean(tmp_path: Path) -> None:
    # Adjacent-to-edge boundary pin: the generic heuristic fires at >=16
    # chars, so a value one below the threshold (15 chars) must stay clean.
    # Paired with test_planted_generic_secret_assignment (26-char value,
    # exit 3), this brackets the exact edge so a threshold regression down
    # to e.g. 10 chars would fail here.
    result = _run("SECRET=abcdefghijklmno\n", tmp_path)  # value is exactly 15 chars
    assert result.returncode == 0, result.stderr
    findings = json.loads(result.stdout)
    assert findings == []


def test_planted_pem_header_exits_3_with_finding(tmp_path: Path) -> None:
    result = _run(f"{PEM_HEADER}\nMIIBogIBAAJ...\n", tmp_path)
    assert result.returncode == 3, result.stderr
    findings = json.loads(result.stdout)
    assert any(f["pattern"] == "pem_private_key" for f in findings)


def test_clean_paragraph_exits_0_with_empty_list(tmp_path: Path) -> None:
    result = _run(CLEAN_PARAGRAPH, tmp_path)
    assert result.returncode == 0, result.stderr
    findings = json.loads(result.stdout)
    assert findings == []


def test_redaction_never_echoes_full_secret(tmp_path: Path) -> None:
    result = _run(f"AWS_ACCESS_KEY_ID={AWS_KEY}\ntoken: {GITHUB_TOKEN}\n", tmp_path)
    assert result.returncode == 3, result.stderr
    assert AWS_KEY not in result.stdout
    assert GITHUB_TOKEN not in result.stdout


def test_stdin_input_when_no_text_file_given(tmp_path: Path) -> None:
    result = _run(f"AWS_ACCESS_KEY_ID={AWS_KEY}\n", tmp_path, use_stdin=True)
    assert result.returncode == 3, result.stderr
    findings = json.loads(result.stdout)
    assert any(f["pattern"] == "aws_access_key" for f in findings)


def test_missing_text_file_exits_1_with_clean_error(tmp_path: Path) -> None:
    missing = tmp_path / "does-not-exist.txt"
    result = subprocess.run(
        [sys.executable, str(_SCRIPT), "--text-file", str(missing)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1, result.stderr
    assert "Traceback" not in result.stderr
    assert result.stderr.strip() != ""
