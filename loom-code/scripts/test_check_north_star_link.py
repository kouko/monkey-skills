"""Tests for check_north_star_link.py — the betting-moment checker that
every `bet` backlog entry carries a well-formed `serves:` line
against `docs/loom/PURPOSE.md` (grammar SSOT:
`backlog_index._is_well_formed_serves`).

Exercised as a CLI subprocess (the actual interface) — same convention
as `test_check_onramp_choice.py`.

Stdlib only (subprocess + pathlib).
"""

import os
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent / "check_north_star_link.py"

_ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")


def _run(store_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(store_path)],
        capture_output=True,
        text=True,
        env=_ENV,
    )


def _write_entry(store: Path, name: str, status: str, serves: str | None) -> Path:
    store.mkdir(parents=True, exist_ok=True)
    lines = ["---", f"name: {name}", f"status: {status}"]
    if serves is not None:
        lines.append(f"serves: {serves}")
    lines.append("---")
    lines.append("")
    lines.append("body.")
    entry = store / f"{name}.md"
    entry.write_text("\n".join(lines), encoding="utf-8")
    return entry


def test_source_does_not_parse_bold_labels():
    """The brief's Boundary evidence: no label inside PURPOSE.md is
    mechanically enforced — this script must read the file as opaque
    text and never key on any of the four bold sub-labels sketched
    elsewhere. A checker keying on them would break on the second repo
    that adopts a different sub-structure."""
    source = SCRIPT.read_text(encoding="utf-8")
    assert "**Why:**" not in source
    assert "**Done when:**" not in source
    assert "**Goal:**" not in source
    assert "**Success:**" not in source


def test_exit_0_when_every_bet_entry_is_well_formed(tmp_path):
    store = tmp_path / "docs" / "loom" / "backlog"
    store.mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs" / "loom" / "PURPOSE.md").write_text(
        "Some long-horizon purpose.\n", encoding="utf-8"
    )
    _write_entry(store, "entry-a", "bet", "ships the thing")
    _write_entry(store, "entry-b", "open", None)

    result = _run(store)

    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"


def test_exit_0_when_no_bet_entries_and_no_purpose_md(tmp_path):
    """A fresh repo with nothing committed yet must not be blocked —
    the Decision's 'never block a fresh repo with nothing in it yet.'"""
    store = tmp_path / "docs" / "loom" / "backlog"
    _write_entry(store, "entry-a", "open", None)

    result = _run(store)

    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"


def test_exit_1_on_missing_store_path(tmp_path):
    missing = tmp_path / "does" / "not" / "exist"

    result = _run(missing)

    assert result.returncode == 1
    assert str(missing) in result.stderr


def test_bet_entry_without_serves_exits_2(tmp_path):
    """The checker keys on the `bet` status (not the retired
    all-caps literal it used to compare against) — a live `bet` entry
    with no `serves:` line must be caught, not silently skipped as
    nothing-to-check."""
    store = tmp_path / "docs" / "loom" / "backlog"
    store.mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs" / "loom" / "PURPOSE.md").write_text(
        "Some long-horizon purpose.\n", encoding="utf-8"
    )
    _write_entry(store, "entry-c", "bet", None)

    result = _run(store)

    assert result.returncode == 2, f"stdout: {result.stdout}\nstderr: {result.stderr}"
    assert "entry-c" in result.stderr
    assert "serves" in result.stderr


def test_exit_2_asks_for_purpose_md_when_absent_but_entries_exist(tmp_path):
    """Absent PURPOSE.md is no longer a silent exemption — it becomes a
    prompt, and its message must be distinguishable from the
    offending-serves-entry exit 2 (a single ambiguous message is a
    defect per the task brief)."""
    store = tmp_path / "docs" / "loom" / "backlog"
    purpose_path = tmp_path / "docs" / "loom" / "PURPOSE.md"
    _write_entry(store, "entry-a", "bet", "ships the thing")

    result = _run(store)

    assert result.returncode == 2, f"stdout: {result.stdout}\nstderr: {result.stderr}"
    assert str(purpose_path) in result.stderr
    assert "entry-a" not in result.stderr


_TEMPLATE = (Path(__file__).parent / "templates" / "PURPOSE.md").read_text(encoding="utf-8")


def test_retired_status_fails_loudly_instead_of_clean_pass(tmp_path):
    """A store holding only an out-of-vocabulary status (e.g. a retired
    `PARKED` entry) must not be silently dropped as nothing-to-check —
    it must fail loudly, matching `live_bet_names`'s ValueError posture
    over the same bytes (`check_queue_relation.py`), not report a clean
    'OK — no live bet backlog entries to check yet.'"""
    store = tmp_path / "docs" / "loom" / "backlog"
    _write_entry(store, "entry-a", "PARKED", None)

    result = _run(store)

    assert result.returncode == 1, f"stdout: {result.stdout}\nstderr: {result.stderr}"
    assert "entry-a" in result.stderr
    assert "PARKED" in result.stderr


def test_exit_2_when_purpose_md_is_unedited_template(tmp_path):
    """A scaffolded-but-untouched PURPOSE.md must not silently pass — the
    Decision's whole point is that a filled-in placeholder is worse than
    an absent file. Message must name the template state, distinct from
    the absent-file message."""
    store = tmp_path / "docs" / "loom" / "backlog"
    purpose_path = tmp_path / "docs" / "loom" / "PURPOSE.md"
    purpose_path.parent.mkdir(parents=True, exist_ok=True)
    purpose_path.write_text("<!-- scaffolded by loom-init v9.9.9 -->\n" + _TEMPLATE, encoding="utf-8")
    _write_entry(store, "entry-a", "bet", "ships the thing")

    result = _run(store)

    assert result.returncode == 2, f"stdout: {result.stdout}\nstderr: {result.stderr}"
    assert "template" in result.stderr.lower()
    assert "entry-a" not in result.stderr


def test_absent_and_template_messages_are_distinguishable(tmp_path):
    store_a = tmp_path / "a" / "docs" / "loom" / "backlog"
    _write_entry(store_a, "entry-a", "bet", "ships the thing")
    result_absent = _run(store_a)

    store_b = tmp_path / "b" / "docs" / "loom" / "backlog"
    purpose_b = tmp_path / "b" / "docs" / "loom" / "PURPOSE.md"
    purpose_b.parent.mkdir(parents=True, exist_ok=True)
    purpose_b.write_text(_TEMPLATE, encoding="utf-8")
    _write_entry(store_b, "entry-a", "bet", "ships the thing")
    result_template = _run(store_b)

    assert result_absent.returncode == 2
    assert result_template.returncode == 2
    assert result_absent.stderr != result_template.stderr


def test_exit_0_when_purpose_is_not_yet_with_reason(tmp_path):
    store = tmp_path / "docs" / "loom" / "backlog"
    purpose_path = tmp_path / "docs" / "loom" / "PURPOSE.md"
    purpose_path.parent.mkdir(parents=True, exist_ok=True)
    purpose_path.write_text(
        "# Purpose\n\n**Why:** not yet — no product decision yet\n",
        encoding="utf-8",
    )
    _write_entry(store, "entry-a", "bet", "ships the thing")

    result = _run(store)

    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"


def test_bare_not_yet_does_not_resolve(tmp_path):
    store = tmp_path / "docs" / "loom" / "backlog"
    purpose_path = tmp_path / "docs" / "loom" / "PURPOSE.md"
    purpose_path.parent.mkdir(parents=True, exist_ok=True)
    purpose_path.write_text("# Purpose\n\n**Why:** not yet\n", encoding="utf-8")
    _write_entry(store, "entry-a", "bet", "ships the thing")

    result = _run(store)

    assert result.returncode == 2, f"stdout: {result.stdout}\nstderr: {result.stderr}"


def test_exit_0_when_purpose_is_genuinely_written(tmp_path):
    store = tmp_path / "docs" / "loom" / "backlog"
    purpose_path = tmp_path / "docs" / "loom" / "PURPOSE.md"
    purpose_path.parent.mkdir(parents=True, exist_ok=True)
    purpose_path.write_text(
        "# Purpose\n\n**Why:** ship the internal wiki tool for the team.\n"
        "**Done when:** every team member can find a doc in <30s.\n",
        encoding="utf-8",
    )
    _write_entry(store, "entry-a", "bet", "ships the thing")

    result = _run(store)

    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"


def test_exit_0_when_real_template_why_replaced_with_not_yet_reason(tmp_path):
    """Regression: the shipped template's own instructional prose ("if
    the answer is not yet knowable, replace the placeholder below with
    `not yet — <reason>`") must not be mistaken for the user's escape
    hatch. Fixture is the ACTUAL shipped template with only the Why
    placeholder edited, the way a real user edits it — a hand-written
    minimal fixture can't catch a defect that lives in the template's
    own shipped prose."""
    store = tmp_path / "docs" / "loom" / "backlog"
    purpose_path = tmp_path / "docs" / "loom" / "PURPOSE.md"
    purpose_path.parent.mkdir(parents=True, exist_ok=True)
    edited = _TEMPLATE.replace(
        "**Why:** _(one sentence — why this product exists)_",
        "**Why:** not yet — 產品方向還沒決定",
    )
    assert edited != _TEMPLATE  # sanity: the replace actually matched the shipped text
    purpose_path.write_text(edited, encoding="utf-8")
    _write_entry(store, "entry-a", "bet", "ships the thing")

    result = _run(store)

    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"


def test_unreadable_purpose_file_exits_1_not_a_traceback(tmp_path):
    """Round-4 finding (arm B): round 3 guarded the reads in
    `check_queue_relation.py` and its commit message even cited THIS
    file's `is_dir()` guard as the model — but the sweep went one
    direction and did not come back. `determine_purpose_state()`'s own
    `read_text` stayed bare, so an existing-but-unreadable PURPOSE.md
    died on a raw traceback.

    Exit 1, not 2: an unreadable file is a different fact from an absent
    one, and only the absent case is a question for the user."""
    store = tmp_path / "docs" / "loom" / "backlog"
    _write_entry(store, "a-bet", "bet", "the purpose")
    purpose = tmp_path / "docs" / "loom" / "PURPOSE.md"
    purpose.write_text("Ship the thing.\n", encoding="utf-8")
    purpose.chmod(0o000)

    try:
        result = _run(store)
    finally:
        purpose.chmod(0o644)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "Traceback" not in result.stderr
    assert "unreadable" in result.stderr
