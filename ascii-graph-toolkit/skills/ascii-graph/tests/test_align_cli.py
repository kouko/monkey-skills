import io
import os
import pathlib
import subprocess
import sys
from contextlib import redirect_stdout

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))

import align

_SCRIPT = (
    pathlib.Path(__file__).resolve().parents[1] / "scripts" / "align.py"
)

# Inline fixtures (self-contained; no /tmp dependency, no nested fixtures/ dir).
# DRIFTED: boxes sized by char-count, so CJK content rows overflow their borders.
DRIFTED = """\
┌──────┐
│ 開始 │
└──┬───┘
   │
   ▼
┌────────┐
│ 驗證ユーザー │
└───┬────┘
    │
    ▼
┌──────────┐
│ 權限足夠? │
└──┬────┬──┘
 是 │    │ 否
   ▼    ▼
┌────────┐ ┌────────┐
│ 載入畫面 │ │ 顯示エラー │
└────────┘ └────────┘"""

# CLEAN: boxes sized by display-width; seam connects, blocks equal-width,
# no kink. Verified to yield zero issues across all three checks.
CLEAN = """\
┌──────────┐
│ 開始處理 │
└────┬─────┘
     │
     ▼
┌──────────┐
│ 完成結束 │
└──────────┘"""


def test_analyze_drifted_has_issues():
    _report, issues = align.analyze(DRIFTED)
    assert len(issues) >= 1


def test_analyze_clean_has_no_issues():
    _report, issues = align.analyze(CLEAN)
    assert issues == []


def test_analyze_report_is_one_line_per_input_line():
    report, _issues = align.analyze(DRIFTED)
    assert len(report.splitlines()) == len(DRIFTED.splitlines())


def test_report_line_numbers_are_1_based_and_match_issue_numbering():
    # Regression for the dogfood F1 bug: the report numbered lines 0-based
    # while drift messages are 1-based, so "fix the flagged line" pointed one
    # line off. The report's first line must be index 1, and an issue's line
    # number must name the same row the report shows.
    report, issues = align.analyze(DRIFTED)
    first = report.splitlines()[0]
    assert first.split()[0] == "1", f"report not 1-based: {first!r}"
    ln = issues[0][0]
    # The issue's 1-based line number must appear as a report row label.
    labels = {line.split()[0] for line in report.splitlines()}
    assert str(ln) in labels


def test_main_drifted_returns_1(tmp_path):
    f = tmp_path / "drifted.txt"
    f.write_text(DRIFTED, encoding="utf-8")
    with redirect_stdout(io.StringIO()):
        rc = align.main([str(f)])
    assert rc == 1


def test_main_clean_returns_0(tmp_path):
    f = tmp_path / "clean.txt"
    f.write_text(CLEAN, encoding="utf-8")
    with redirect_stdout(io.StringIO()):
        rc = align.main([str(f)])
    assert rc == 0


def test_main_clean_prints_no_drift(tmp_path):
    f = tmp_path / "clean.txt"
    f.write_text(CLEAN, encoding="utf-8")
    buf = io.StringIO()
    with redirect_stdout(buf):
        align.main([str(f)])
    assert "no drift" in buf.getvalue()


def test_subprocess_stdin_drifted_exits_1():
    # Run from repo root; script's own dir is sys.path[0] so imports resolve.
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    proc = subprocess.run(
        [sys.executable, str(_SCRIPT)],
        input=DRIFTED,
        capture_output=True,
        text=True,
        env=env,
    )
    assert proc.returncode == 1, proc.stderr
