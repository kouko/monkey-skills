"""Tests for check_loom_memory_integrity.py — the loom-memory store's integrity gate.

WHY this gate exists: docs/loom/memory/README.md's prose invariants (every body
file indexed, every index line valid, filename == frontmatter name, index
description byte-identical to frontmatter description) already drifted once —
2 orphan files landed via PR #592 with no index line, uncaught, because nothing
mechanical checked it. This mirrors check_version_bump.py's shape: a
validate-only, fail-loud, stdlib-only checker with clear exit codes.

Fixtures build a REAL temporary store directory (README.md + body .md files) so
the script's actual file-parsing behavior is exercised, not a mock of it.
"""

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "check_loom_memory_integrity.py"

README_HEADER = """# fixture store

## Index

"""


def _write(store: Path, rel: str, text: str) -> None:
    path = store / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _body(name: str, description: str) -> str:
    return (
        "---\n"
        f"name: {name}\n"
        f"description: {description}\n"
        "type: practice\n"
        "origin: test fixture\n"
        "---\n\n"
        "The fact.\n"
    )


def _run(store: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--store", str(store)],
        capture_output=True,
        text=True,
    )


def test_clean_store_passes(tmp_path):
    store = tmp_path / "memory"
    store.mkdir()
    desc = "A clean fixture fact used to prove the checker passes valid stores."
    _write(store, "README.md", README_HEADER + f"[clean-fact](clean-fact.md) — {desc}\n")
    _write(store, "clean-fact.md", _body("clean-fact", desc))

    result = _run(store)

    assert result.returncode == 0, result.stdout + result.stderr


def test_orphan_body_file_with_no_index_line_is_a_violation(tmp_path):
    """Invariant (a): the exact PR #592 shape — a body file with no index line."""
    store = tmp_path / "memory"
    store.mkdir()
    desc = "This orphan fact has a file on disk but no index line at all."
    # README's index is empty — orphan-fact.md is never mentioned.
    _write(store, "README.md", README_HEADER)
    _write(store, "orphan-fact.md", _body("orphan-fact", desc))

    result = _run(store)

    assert result.returncode != 0
    assert "orphan-fact.md" in result.stdout
    assert "index" in result.stdout.lower()


def test_index_line_pointing_to_missing_file_is_a_violation(tmp_path):
    """Invariant (b): an index line whose target file does not exist."""
    store = tmp_path / "memory"
    store.mkdir()
    _write(
        store,
        "README.md",
        README_HEADER + "[ghost-fact](ghost-fact.md) — A fact whose file was deleted but the index line stayed.\n",
    )
    # No ghost-fact.md written.

    result = _run(store)

    assert result.returncode != 0
    assert "ghost-fact.md" in result.stdout


def test_filename_frontmatter_name_mismatch_is_a_violation(tmp_path):
    """Invariant (c): filename (minus .md) must equal frontmatter `name`."""
    store = tmp_path / "memory"
    store.mkdir()
    desc = "A fact whose frontmatter name diverges from its own filename."
    _write(store, "README.md", README_HEADER + f"[mismatched-fact](mismatched-fact.md) — {desc}\n")
    _write(store, "mismatched-fact.md", _body("wrong-slug", desc))

    result = _run(store)

    assert result.returncode != 0
    assert "mismatched-fact.md" in result.stdout


def test_description_one_char_mismatch_is_a_violation(tmp_path):
    """Invariant (d): index description must be BYTE-IDENTICAL to frontmatter."""
    store = tmp_path / "memory"
    store.mkdir()
    fm_desc = "A fact whose index description differs by exactly one character."
    index_desc = "A fact whose index description differs by exactly one characteR."
    _write(store, "README.md", README_HEADER + f"[drifted-fact](drifted-fact.md) — {index_desc}\n")
    _write(store, "drifted-fact.md", _body("drifted-fact", fm_desc))

    result = _run(store)

    assert result.returncode != 0
    assert "drifted-fact.md" in result.stdout


def test_index_description_trailing_whitespace_is_not_a_violation(tmp_path):
    """FIX 1: [d] compare must strip BOTH sides. A trailing space on the index
    line (frontmatter side is already `.strip()`ed) must not trip a spurious
    mismatch — it is semantically identical, not drift."""
    store = tmp_path / "memory"
    store.mkdir()
    fm_desc = "A fact whose index line has trailing whitespace only."
    index_desc_with_trailing_space = fm_desc + " "
    _write(
        store,
        "README.md",
        README_HEADER + f"[padded-fact](padded-fact.md) — {index_desc_with_trailing_space}\n",
    )
    _write(store, "padded-fact.md", _body("padded-fact", fm_desc))

    result = _run(store)

    assert result.returncode == 0, result.stdout + result.stderr


def test_description_mismatch_message_shows_repr_of_both_values(tmp_path):
    """FIX 2: a [d] violation message must repr() BOTH the index description and
    the frontmatter description, so invisible byte drift (nbsp, curly quotes,
    em-dash-vs-hyphen) is visible in the failure output, not just "differs"."""
    store = tmp_path / "memory"
    store.mkdir()
    fm_desc = "A fact with a straight quote and a normal space here."
    index_desc = "A fact with a straight quote and a normal space here."  # nbsp
    _write(store, "README.md", README_HEADER + f"[drifted-fact](drifted-fact.md) — {index_desc}\n")
    _write(store, "drifted-fact.md", _body("drifted-fact", fm_desc))

    result = _run(store)

    assert result.returncode != 0
    assert repr(index_desc) in result.stdout
    assert repr(fm_desc) in result.stdout


def test_description_containing_colon_parses_and_compares_correctly(tmp_path):
    """FIX 3(a): a description with a colon (e.g. 'paths:') must not confuse the
    frontmatter `key: value` parser (partition splits on the FIRST colon only)."""
    store = tmp_path / "memory"
    store.mkdir()
    desc = "GitHub Actions " + "paths:" + " filters changed behavior in this fact."
    _write(store, "README.md", README_HEADER + f"[colon-fact](colon-fact.md) — {desc}\n")
    _write(store, "colon-fact.md", _body("colon-fact", desc))

    result = _run(store)

    assert result.returncode == 0, result.stdout + result.stderr


def test_description_containing_em_dash_does_not_mis_split(tmp_path):
    """FIX 3(b): the index-line separator is ' — ' (U+2014), but the description
    itself may ALSO contain an em-dash. The regex must not mis-split on the
    second occurrence — the whole remainder of the line is the description."""
    store = tmp_path / "memory"
    store.mkdir()
    desc = "A fact about caching — including edge cases that surprised us."
    _write(store, "README.md", README_HEADER + f"[emdash-fact](emdash-fact.md) — {desc}\n")
    _write(store, "emdash-fact.md", _body("emdash-fact", desc))

    result = _run(store)

    assert result.returncode == 0, result.stdout + result.stderr


def test_body_file_with_no_frontmatter_is_a_violation_not_a_crash(tmp_path):
    """FIX 3(c): a body file with no `---` frontmatter block at all must be
    reported as a clean violation, never an unhandled exception."""
    store = tmp_path / "memory"
    store.mkdir()
    desc = "This body file forgot its frontmatter block entirely."
    _write(store, "README.md", README_HEADER + f"[bare-fact](bare-fact.md) — {desc}\n")
    _write(store, "bare-fact.md", "No frontmatter here, just prose.\n")

    result = _run(store)

    assert result.returncode != 0
    assert "Traceback" not in result.stderr
    assert "bare-fact.md" in result.stdout


def test_missing_readme_is_a_clear_violation_not_a_crash(tmp_path):
    """FIX 3(d): a store with no README.md at all must be a clear violation
    (every body file reported orphaned), never an unhandled exception."""
    store = tmp_path / "memory"
    store.mkdir()
    _write(store, "lonely-fact.md", _body("lonely-fact", "A fact with nobody to index it."))
    # No README.md written at all.

    result = _run(store)

    assert result.returncode != 0
    assert "Traceback" not in result.stderr
    assert "lonely-fact.md" in result.stdout


def test_body_file_missing_name_key_is_a_violation(tmp_path):
    """FIX 3(e): frontmatter missing the `name` key is reported as a (c)
    violation, not a KeyError/crash."""
    store = tmp_path / "memory"
    store.mkdir()
    desc = "A fact whose frontmatter never declares a name key."
    body = "---\n" f"description: {desc}\n" "type: practice\n" "---\n\nThe fact.\n"
    _write(store, "README.md", README_HEADER + f"[nameless-fact](nameless-fact.md) — {desc}\n")
    _write(store, "nameless-fact.md", body)

    result = _run(store)

    assert result.returncode != 0
    assert "Traceback" not in result.stderr
    assert "nameless-fact.md" in result.stdout
    assert "name" in result.stdout.lower()


def test_body_file_missing_description_key_is_a_violation(tmp_path):
    """FIX 3(e): frontmatter missing the `description` key is reported as a (d)
    violation, not a crash."""
    store = tmp_path / "memory"
    store.mkdir()
    body = "---\nname: descriptionless-fact\ntype: practice\n---\n\nThe fact.\n"
    _write(
        store,
        "README.md",
        README_HEADER + "[descriptionless-fact](descriptionless-fact.md) — Some index text.\n",
    )
    _write(store, "descriptionless-fact.md", body)

    result = _run(store)

    assert result.returncode != 0
    assert "Traceback" not in result.stderr
    assert "descriptionless-fact.md" in result.stdout
    assert "description" in result.stdout.lower()


def test_duplicate_index_entries_for_same_file_is_a_violation(tmp_path):
    """ADD (5th check, [e]): two index lines pointing at the SAME body file (one
    stale, one correct) currently evade every check because `index_by_file`
    keeps only the last entry. Must be flagged, naming the file."""
    store = tmp_path / "memory"
    store.mkdir()
    desc = "The current, correct description for this fact."
    _write(
        store,
        "README.md",
        README_HEADER
        + "[dup-fact-old](dup-fact.md) — A stale description nobody updated.\n"
        + f"[dup-fact](dup-fact.md) — {desc}\n",
    )
    _write(store, "dup-fact.md", _body("dup-fact", desc))

    result = _run(store)

    assert result.returncode != 0
    assert "dup-fact.md" in result.stdout
    assert "2" in result.stdout


def test_multiple_clean_facts_all_pass(tmp_path):
    store = tmp_path / "memory"
    store.mkdir()
    desc_a = "First clean fact for the multi-file clean case."
    desc_b = "Second clean fact for the multi-file clean case."
    _write(
        store,
        "README.md",
        README_HEADER
        + f"[fact-a](fact-a.md) — {desc_a}\n"
        + f"[fact-b](fact-b.md) — {desc_b}\n",
    )
    _write(store, "fact-a.md", _body("fact-a", desc_a))
    _write(store, "fact-b.md", _body("fact-b", desc_b))

    result = _run(store)

    assert result.returncode == 0, result.stdout + result.stderr
