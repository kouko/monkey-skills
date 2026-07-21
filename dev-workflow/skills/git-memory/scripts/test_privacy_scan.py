"""test_privacy_scan.py — tests for privacy-scan.py (layer-1 deterministic secrets scan).

Per plan Task 1 acceptance (docs/loom/plans/2026-07-19-closeout-privacy-gate.md):
1. A planted AWS access key / GitHub token / PEM private-key header each yields
   exit 3 + a JSON finding naming the pattern.
2. A clean paragraph (no secret) yields exit 0 + an empty JSON list.
3. Redaction: the full secret literal never appears in stdout.
4. The script also reads from stdin when --text-file is omitted (zero-config CLI).

Per plan Task 2 acceptance (same plan doc) — the OPTIONAL deny-list layer:
5. A term in a --denylist file that appears in the text yields exit 3 + a
   finding with pattern "denylist".
6. `#`-comment lines and blank lines in the deny-list file are ignored (not
   matched as literal terms).
7. No deny-list configured (neither flag nor env) → clean text stays exit 0
   with "denylist: not configured" on stderr; a planted secret is unaffected
   (still exit 3, secrets layer is independent of the deny-list layer).
8. A --denylist path that does not exist does not crash and does not change
   the exit-code contract; stderr notes the file was not found.
9. Redaction applies to deny-list matches too.
"""

from __future__ import annotations

import json
import os
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
SLACK_BOT_TOKEN = "xoxb-EXAMPLE-PLACEHOLDER-notarealslacktokenEXAMPLE"
SLACK_WEBHOOK = "https://hooks.slack.com/services/EXAMPLE/PLACEHOLDER/notarealwebhookEXAMPLE00"
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
            env=_clean_env(),
        )
    text_file = tmp_path / "composed.txt"
    text_file.write_text(text, encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(_SCRIPT), "--text-file", str(text_file)],
        capture_output=True,
        text=True,
        env=_clean_env(),
    )


def _clean_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    """os.environ copy with GIT_MEMORY_DENYLIST scrubbed, so tests never
    inherit a stray value from the ambient shell; `extra` overlays on top."""
    env = os.environ.copy()
    env.pop("GIT_MEMORY_DENYLIST", None)
    if extra:
        env.update(extra)
    return env


def _run_with_args(
    text: str,
    tmp_path: Path,
    extra_args: list[str],
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    text_file = tmp_path / "composed.txt"
    text_file.write_text(text, encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(_SCRIPT), "--text-file", str(text_file), *extra_args],
        capture_output=True,
        text=True,
        env=_clean_env(env),
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


# ---------------------------------------------------------------------------
# Optional deny-list layer (plan Task 2) — fail-OPEN when absent, composes
# with the mandatory secrets layer when present.


def test_denylist_term_via_flag_exits_3_with_finding(tmp_path: Path) -> None:
    denylist_file = tmp_path / "denylist.txt"
    denylist_file.write_text("AcmeCorp\n", encoding="utf-8")
    result = _run_with_args(
        "Please don't mention AcmeCorp in the changelog.\n",
        tmp_path,
        ["--denylist", str(denylist_file)],
    )
    assert result.returncode == 3, result.stderr
    findings = json.loads(result.stdout)
    assert any(f["pattern"] == "denylist" for f in findings)


def test_denylist_via_env_var_when_no_flag(tmp_path: Path) -> None:
    denylist_file = tmp_path / "denylist.txt"
    denylist_file.write_text("ProjectPhoenix\n", encoding="utf-8")
    result = _run_with_args(
        "Codename ProjectPhoenix ships next quarter.\n",
        tmp_path,
        [],
        env={"GIT_MEMORY_DENYLIST": str(denylist_file)},
    )
    assert result.returncode == 3, result.stderr
    findings = json.loads(result.stdout)
    assert any(f["pattern"] == "denylist" for f in findings)


def test_denylist_comments_and_blanks_ignored(tmp_path: Path) -> None:
    # If the "#" comment line or a blank line were treated as a literal
    # deny-list term, the blank-line term ("") would match every scanned
    # line (substring-of-everything) and the comment's own words ("banana")
    # would trip a false finding. Neither may happen.
    denylist_file = tmp_path / "denylist.txt"
    denylist_file.write_text(
        "# this comment mentions banana, must not be a literal term\n"
        "\n"
        "AcmeCorp\n"
        "\n",
        encoding="utf-8",
    )
    result = _run_with_args(
        "I had a banana for lunch and wrote some ordinary commit prose.\n",
        tmp_path,
        ["--denylist", str(denylist_file)],
    )
    assert result.returncode == 0, result.stderr
    findings = json.loads(result.stdout)
    assert findings == []


def test_no_denylist_configured_clean_text_exit_0_stderr_not_configured(
    tmp_path: Path,
) -> None:
    result = _run_with_args(CLEAN_PARAGRAPH, tmp_path, [])
    assert result.returncode == 0, result.stderr
    findings = json.loads(result.stdout)
    assert findings == []
    assert "denylist: not configured" in result.stderr


def test_no_denylist_configured_secret_still_exits_3(tmp_path: Path) -> None:
    # Absence of a deny-list must never affect the mandatory secrets layer.
    result = _run_with_args(f"AWS_ACCESS_KEY_ID={AWS_KEY}\n", tmp_path, [])
    assert result.returncode == 3, result.stderr
    findings = json.loads(result.stdout)
    assert any(f["pattern"] == "aws_access_key" for f in findings)
    assert "denylist: not configured" in result.stderr


def test_denylist_missing_file_does_not_crash_stderr_notes_not_found(
    tmp_path: Path,
) -> None:
    missing = tmp_path / "does-not-exist-denylist.txt"
    result = _run_with_args(CLEAN_PARAGRAPH, tmp_path, ["--denylist", str(missing)])
    assert result.returncode == 0, result.stderr
    assert "Traceback" not in result.stderr
    assert f"denylist: file not found: {missing}" in result.stderr


def test_denylist_missing_file_secrets_layer_still_works(tmp_path: Path) -> None:
    missing = tmp_path / "does-not-exist-denylist.txt"
    result = _run_with_args(
        f"AWS_ACCESS_KEY_ID={AWS_KEY}\n", tmp_path, ["--denylist", str(missing)]
    )
    assert result.returncode == 3, result.stderr
    findings = json.loads(result.stdout)
    assert any(f["pattern"] == "aws_access_key" for f in findings)


def test_denylist_redaction_never_echoes_full_term(tmp_path: Path) -> None:
    denylist_file = tmp_path / "denylist.txt"
    denylist_file.write_text("SuperSecretCodename\n", encoding="utf-8")
    result = _run_with_args(
        "Referring to SuperSecretCodename in this note.\n",
        tmp_path,
        ["--denylist", str(denylist_file)],
    )
    assert result.returncode == 3, result.stderr
    assert "SuperSecretCodename" not in result.stdout


# ---------------------------------------------------------------------------
# Round-2 review fixes (F1 invalid encoding, F2 short-term redaction,
# F3 flag-vs-env precedence, F4 case-insensitive matching).


def test_denylist_invalid_encoding_fails_open_no_crash(tmp_path: Path) -> None:
    # A deny-list file with a stray invalid-UTF-8 byte (0xFF) must not raise
    # an uncaught UnicodeDecodeError / print a traceback with local paths.
    # It must fail OPEN: clean one-line stderr note, secrets-only scanning
    # continues (exit-code contract unchanged for the secrets layer).
    denylist_file = tmp_path / "denylist.txt"
    denylist_file.write_bytes(b"\xffInvalidUtf8Term\n")
    result = _run_with_args(
        f"AWS_ACCESS_KEY_ID={AWS_KEY}\n", tmp_path, ["--denylist", str(denylist_file)]
    )
    assert "Traceback" not in result.stderr
    assert "denylist" in result.stderr.lower()
    # secrets layer must still catch the planted AWS key despite the
    # unusable deny-list.
    assert result.returncode == 3, result.stderr
    findings = json.loads(result.stdout)
    assert any(f["pattern"] == "aws_access_key" for f in findings)


def test_denylist_short_term_visa_not_revealed_in_full(tmp_path: Path) -> None:
    # "Visa" is 4 chars — the secrets-layer redact() (first 4 chars + "…")
    # would show the ENTIRE term. Deny-list redaction must never reveal a
    # short term in full.
    denylist_file = tmp_path / "denylist.txt"
    denylist_file.write_text("Visa\n", encoding="utf-8")
    result = _run_with_args(
        "We should not mention Visa as a payment partner.\n",
        tmp_path,
        ["--denylist", str(denylist_file)],
    )
    assert result.returncode == 3, result.stderr
    assert "Visa" not in result.stdout


def test_denylist_short_term_ibm_not_revealed_in_full(tmp_path: Path) -> None:
    # "IBM" is 3 chars — shorter than the redact() prefix length (4), so a
    # naive prefix redaction would show the full term plus an ellipsis.
    denylist_file = tmp_path / "denylist.txt"
    denylist_file.write_text("IBM\n", encoding="utf-8")
    result = _run_with_args(
        "Partnering with IBM on the new integration.\n",
        tmp_path,
        ["--denylist", str(denylist_file)],
    )
    assert result.returncode == 3, result.stderr
    assert "IBM" not in result.stdout


def test_denylist_flag_wins_over_env_with_different_terms(tmp_path: Path) -> None:
    # F3: --denylist and GIT_MEMORY_DENYLIST both set, pointing at files with
    # DIFFERENT terms. The flag's file must win entirely — only its term
    # matches; the env file's term must not.
    flag_file = tmp_path / "flag-denylist.txt"
    flag_file.write_text("FlagTerm\n", encoding="utf-8")
    env_file = tmp_path / "env-denylist.txt"
    env_file.write_text("EnvTerm\n", encoding="utf-8")

    result = _run_with_args(
        "This note mentions FlagTerm and EnvTerm both.\n",
        tmp_path,
        ["--denylist", str(flag_file)],
        env={"GIT_MEMORY_DENYLIST": str(env_file)},
    )
    assert result.returncode == 3, result.stderr
    findings = json.loads(result.stdout)
    denylist_findings = [f for f in findings if f["pattern"] == "denylist"]
    assert len(denylist_findings) == 1
    # Neither term's literal should leak via redaction either way, but the
    # key assertion is precedence: env-only term must not have matched at
    # all i.e. exactly one denylist finding (from FlagTerm), not two.


def test_denylist_case_insensitive_match(tmp_path: Path) -> None:
    # F4: deny-list term "AcmeCorp" must catch a differently-cased
    # occurrence in the text ("acmecorp") — case-insensitive matching is
    # the fail-safe default for company/person names in prose.
    denylist_file = tmp_path / "denylist.txt"
    denylist_file.write_text("AcmeCorp\n", encoding="utf-8")
    result = _run_with_args(
        "we should not talk about acmecorp in public.\n",
        tmp_path,
        ["--denylist", str(denylist_file)],
    )
    assert result.returncode == 3, result.stderr
    findings = json.loads(result.stdout)
    assert any(f["pattern"] == "denylist" for f in findings)
