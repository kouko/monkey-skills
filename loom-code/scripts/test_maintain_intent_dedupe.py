"""W1-05 — the `maintain` station's dedupe rule (SKILL.md step 2, gate
`maintain.dedupe`) as an executable helper: given a directory of intent
fixtures, find the intent this incident already belongs to by filename
slug or by an `evidence:` entry, and never match a withdrawn intent.

Also asserts the shape of loom-code/skills/maintain/SKILL.md itself: the
station summary table is present, the dedupe gate is marked and
registered in mechanisms.yaml, no deleted vocabulary survives, and the
body stays within the 1,500-word cap.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / "loom-code" / "skills" / "maintain" / "SKILL.md"
MECHANISMS = REPO / "docs" / "loom" / "evidence" / "mechanisms.yaml"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
EVIDENCE_RE = re.compile(r"^evidence:\s*\[(.*)\]\s*$", re.M)
STATUS_RE = re.compile(r"^status:\s*(.+)$", re.M)


# --------------------------------------------------------------------------
# The dedupe helper under test (≤40 lines) — a standalone twin of the
# SKILL.md step 2 prose rule, kept here rather than as a shipped script
# because it exists only to prove the rule is executable, not to be
# invoked by an agent at runtime (the agent reads intent files itself).
# --------------------------------------------------------------------------

def find_matching_intent(intent_dir: Path, incident_slug: str, incident_evidence_id: str) -> Path | None:
    """Return the open/confirmed intent that already covers this incident,
    or None. Match iff the intent's filename slug equals incident_slug, or
    its evidence: list already contains incident_evidence_id. Withdrawn
    intents are never matched."""
    for path in sorted(intent_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        m = STATUS_RE.search(text)
        status = m.group(1).strip() if m else "open"
        if status.startswith("withdrawn"):
            continue
        if path.stem == incident_slug:
            return path
        ev_match = EVIDENCE_RE.search(text)
        if ev_match:
            entries = [e.strip().strip("\"'") for e in ev_match.group(1).split(",") if e.strip()]
            if incident_evidence_id in entries:
                return path
    return None


def _write_intent(dir_: Path, slug: str, status: str = "open", evidence: list[str] | None = None) -> Path:
    ev = f"[{', '.join(evidence)}]" if evidence else "[]"
    text = (
        f"# {slug}\n"
        f"originator: maintenance-loop\n"
        f"kind: engineering\n"
        f"needs-design: no — bugfix, no interface change\n"
        f"evidence: {ev}\n"
        f"status: {status}\n\n"
        f"## Problem\nsomething broke\n\n"
        f"## Proposed outcome\nit stops breaking\n\n"
        f"## Acceptance\n1. repro no longer fails\n\n"
        f"## Constraints\n- none\n\n"
        f"## Out of scope\n- none\n\n"
        f"## Open questions\n- none\n"
    )
    path = dir_ / f"{slug}.md"
    path.write_text(text, encoding="utf-8")
    return path


@pytest.fixture
def intent_dir(tmp_path: Path) -> Path:
    d = tmp_path / "intent"
    d.mkdir()
    return d


def test_matches_by_filename_slug(intent_dir):
    target = _write_intent(intent_dir, "ci-flake-login-test")
    found = find_matching_intent(intent_dir, "ci-flake-login-test", "alert-9999")
    assert found == target


def test_matches_by_evidence_entry(intent_dir):
    target = _write_intent(intent_dir, "checkout-500s", evidence=["alert-1234", "docs/loom/evidence/incidents/2026-09-01-checkout-500s.md"])
    found = find_matching_intent(intent_dir, "checkout-500-errors", "alert-1234")
    assert found == target


def test_no_match_returns_none(intent_dir):
    _write_intent(intent_dir, "unrelated-thing", evidence=["alert-0001"])
    found = find_matching_intent(intent_dir, "new-incident-slug", "alert-9999")
    assert found is None


def test_withdrawn_intent_never_matches_by_slug(intent_dir):
    _write_intent(intent_dir, "flaky-upload-test", status="withdrawn — superseded")
    found = find_matching_intent(intent_dir, "flaky-upload-test", "alert-9999")
    assert found is None


def test_withdrawn_intent_never_matches_by_evidence(intent_dir):
    _write_intent(intent_dir, "old-slug", status="withdrawn — superseded", evidence=["alert-7777"])
    found = find_matching_intent(intent_dir, "different-slug", "alert-7777")
    assert found is None


def test_confirmed_intent_still_matches(intent_dir):
    target = _write_intent(intent_dir, "db-timeout", status="confirmed 2026-08-01", evidence=["alert-42"])
    found = find_matching_intent(intent_dir, "db-timeout-again", "alert-42")
    assert found == target


# --------------------------------------------------------------------------
# SKILL.md shape assertions
# --------------------------------------------------------------------------

def _body_text() -> str:
    raw = SKILL.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(raw)
    assert m, "SKILL.md must open with a --- frontmatter block"
    return raw[m.end():]


def test_skill_file_exists():
    assert SKILL.is_file()


def test_frontmatter_name_and_description():
    raw = SKILL.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(raw)
    fm = yaml.safe_load(m.group(1))
    assert fm["name"] == "maintain"
    assert len(fm["description"]) <= 300


def test_summary_table_present():
    body = _body_text()
    assert "| station | artifact | who decides | checker | checkpoint |" in body
    for station in ("capture-intent", "write-spec", "write-plan", "build", "review", "ship", "maintain"):
        assert f"| {station} |" in body, f"missing station row: {station}"


def test_dedupe_gate_marked_in_skill():
    body = _body_text()
    assert "<!-- gate: maintain.dedupe -->" in body


def test_dedupe_gate_registered_in_mechanisms():
    data = yaml.safe_load(MECHANISMS.read_text(encoding="utf-8"))
    ids = {(m["id"], m["class"]) for m in data["mechanisms"]}
    assert ("maintain.dedupe", "prose-gate") in ids


def test_no_deleted_vocabulary():
    body = _body_text().lower()
    for banned in ("brief", "backlog", "seed", "batch", "waiver"):
        assert banned not in body, f"deleted vocabulary present: {banned}"


def test_body_word_count_within_cap():
    body = _body_text()
    assert len(body.split()) <= 1500
