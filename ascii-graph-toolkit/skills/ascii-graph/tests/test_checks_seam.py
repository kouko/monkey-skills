import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))

from checks_seam import find_issues

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

# CLEAN: boxes sized by display-width; every vertical seam connects.
CLEAN = """\
     ┌──────┐
     │ 開始 │
     └───┬──┘
         │
         ▼
┌──────────────────┐
│ 驗證ユーザー身分 │
└─────────┬────────┘
          │
          ▼
   ┌────────────┐
   │ 權限足夠?  │
   └───┬────┬───┘
       │    │
      是    否
       ▼    ▼
┌────────────┐ ┌──────────────┐
│ 載入畫面   │ │ 顯示エラー   │
└────────────┘ └──────────────┘"""


def test_drifted_fixture_has_violations():
    issues = find_issues(DRIFTED.splitlines())
    assert len(issues) >= 1


def test_clean_fixture_has_no_violations():
    issues = find_issues(CLEAN.splitlines())
    assert issues == []


def test_issue_tuple_shape():
    issues = find_issues(DRIFTED.splitlines())
    ln, col, msg = issues[0]
    assert isinstance(ln, int) and ln >= 1
    assert isinstance(col, int) and col >= 0
    assert isinstance(msg, str) and msg


# Double-line box, width-correct (interior ' 中文 ' = 6 display cells -> 6 ═).
DOUBLE_CLEAN = """\
╔══════╗
║ 中文 ║
╚══════╝"""

# Same double box but the content row is sized by char-count (6 CJK+space chars
# vs 6-cell border) -> the right ║ lands at a column no border reaches.
DOUBLE_CORRUPTED = """\
╔══════╗
║ 中文字測試 ║
╚══════╝"""

# Rounded box, width-correct (interior ' 中文 ' = 6 display cells -> 6 ─).
ROUNDED_CLEAN = """\
╭──────╮
│ 中文 │
╰──────╯"""


def test_double_line_box_clean():
    assert find_issues(DOUBLE_CLEAN.splitlines()) == []


def test_double_line_box_corrupted_caught():
    issues = find_issues(DOUBLE_CORRUPTED.splitlines())
    assert len(issues) >= 1


def test_rounded_box_clean():
    assert find_issues(ROUNDED_CLEAN.splitlines()) == []
