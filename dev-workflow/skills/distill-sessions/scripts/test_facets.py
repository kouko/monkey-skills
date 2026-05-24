"""test_facets.py — verifies load_facets + attach_facets_to_events.

Fixture: `fixture_facet.json` in this same directory, one hand-anonymized
record from a real `~/.claude/usage-data/facets/<sid>.json`. The session_id
matches the session in `fixture_sample.jsonl` (T2 fixture) so the join test
exercises a real end-to-end path: ingest JSONL → load facets → attach.

Covers:
- load_facets returns dict[session_id, FacetRecord] for a directory tree,
- load_facets returns empty dict when root is missing,
- load_facets silently skips malformed JSON files,
- attach_facets_to_events joins by event.session,
- attach_facets_to_events leaves event.facet=None when no match,
- FacetRecord field defaults are gracefully None / empty-dict.

Per dev-workflow/skills/distill-sessions Plan Part 1 §Task 3 acceptance.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Allow `from facets import ...` / `from event import Event` /
# `from ingest import ...` when pytest is invoked from the repo root.
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from event import Event  # noqa: E402
from facets import (  # noqa: E402
    FacetRecord,
    attach_facets_to_events,
    load_facets,
)
from ingest import ingest_claude_jsonl  # noqa: E402

FIXTURE_DIR = _HERE
# Same session id as fixture_sample.jsonl (T2) — join target.
EXPECTED_SESSION = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"


def _facets_dir(tmp_path: Path, *json_payloads: dict) -> Path:
    """Write each payload as `<session_id>.json` under tmp_path and return
    that directory for load_facets to walk."""
    for payload in json_payloads:
        sid = payload["session_id"]
        (tmp_path / f"{sid}.json").write_text(
            json.dumps(payload), encoding="utf-8"
        )
    return tmp_path


def test_load_facets_returns_dict_keyed_by_session_id(tmp_path):
    """Two valid facet JSONs in a directory → dict with both session_ids
    as keys, each mapping to a FacetRecord."""
    _facets_dir(
        tmp_path,
        {
            "session_id": "sess-1",
            "underlying_goal": "g1",
            "goal_categories": {"feature": 2},
            "outcome": "fully_achieved",
            "user_satisfaction_counts": {"satisfied": 1},
            "claude_helpfulness": "very_helpful",
            "session_type": "single_task",
            "friction_counts": {},
            "friction_detail": "",
            "primary_success": "good_explanations",
            "brief_summary": "b1",
        },
        {
            "session_id": "sess-2",
            "underlying_goal": "g2",
            "goal_categories": {"bugfix": 1},
            "outcome": "partially_achieved",
            "user_satisfaction_counts": {},
            "claude_helpfulness": "moderately_helpful",
            "session_type": "multi_task",
            "friction_counts": {"buggy_code": 2},
            "friction_detail": "two bugs",
            "primary_success": "multi_file_changes",
            "brief_summary": "b2",
        },
    )

    facets = load_facets(tmp_path)

    assert set(facets.keys()) == {"sess-1", "sess-2"}, (
        f"unexpected keys: {sorted(facets.keys())}"
    )
    assert isinstance(facets["sess-1"], FacetRecord)
    assert facets["sess-1"].outcome == "fully_achieved"
    assert facets["sess-1"].claude_helpfulness == "very_helpful"
    assert facets["sess-1"].goal_categories == {"feature": 2}
    assert facets["sess-2"].friction_counts == {"buggy_code": 2}
    assert facets["sess-2"].primary_success == "multi_file_changes"


def test_load_facets_returns_empty_dict_when_root_missing(tmp_path):
    """A non-existent root path → empty dict (don't crash)."""
    missing = tmp_path / "does-not-exist"
    assert load_facets(missing) == {}


def test_load_facets_silently_skips_malformed_json(tmp_path):
    """Stray non-JSON file in the facets dir → skipped, valid ones still
    parse. Line-by-line resilience like ingest.py."""
    (tmp_path / "broken.json").write_text(
        "this is not json at all", encoding="utf-8"
    )
    (tmp_path / "no-session-id.json").write_text(
        json.dumps({"outcome": "fully_achieved"}),  # missing session_id key
        encoding="utf-8",
    )
    _facets_dir(
        tmp_path,
        {
            "session_id": "sess-ok",
            "underlying_goal": "ok",
            "goal_categories": {},
            "outcome": "fully_achieved",
            "user_satisfaction_counts": {},
            "claude_helpfulness": "very_helpful",
            "session_type": "single_task",
            "friction_counts": {},
            "friction_detail": "",
            "primary_success": "good_explanations",
            "brief_summary": "",
        },
    )

    facets = load_facets(tmp_path)

    assert set(facets.keys()) == {"sess-ok"}, (
        f"malformed JSONs should be skipped silently; got "
        f"{sorted(facets.keys())}"
    )


def test_load_facets_handles_partial_records_with_defaults(tmp_path):
    """Older facets JSONs may be missing newer keys — load_facets should
    populate present keys and leave others at FacetRecord defaults."""
    (tmp_path / "minimal.json").write_text(
        json.dumps(
            {
                "session_id": "sess-min",
                "outcome": "fully_achieved",
                # All other keys absent.
            }
        ),
        encoding="utf-8",
    )

    facets = load_facets(tmp_path)

    rec = facets["sess-min"]
    assert rec.outcome == "fully_achieved"
    # Missing dict fields default to empty dict (NOT None) so callers
    # can do `rec.friction_counts.items()` without a None guard.
    assert rec.friction_counts == {}
    assert rec.goal_categories == {}
    # Missing string fields default to None.
    assert rec.claude_helpfulness is None
    assert rec.primary_success is None


def test_attach_facets_joins_by_session_id(tmp_path):
    """The key new test — load real-shape facet + ingest T2 fixture JSONL,
    attach by session_id, assert events whose session matches get a
    FacetRecord and non-matching ones stay None.

    This exercises the full end-to-end path of T3 (load → attach)."""
    # Copy the committed fixture_facet.json into tmp_path so load_facets
    # has a real-shape JSON to walk. The committed fixture's session_id
    # matches EXPECTED_SESSION (fixture_sample.jsonl's session).
    src = FIXTURE_DIR / "fixture_facet.json"
    assert src.exists(), f"missing committed fixture: {src}"
    payload = json.loads(src.read_text(encoding="utf-8"))
    assert payload["session_id"] == EXPECTED_SESSION, (
        f"committed fixture session_id {payload['session_id']!r} must "
        f"equal fixture_sample.jsonl session {EXPECTED_SESSION!r} for "
        f"the join test to be meaningful"
    )

    # Stage the facets dir with the matching fixture + one non-matching.
    (tmp_path / f"{EXPECTED_SESSION}.json").write_text(
        json.dumps(payload), encoding="utf-8"
    )
    (tmp_path / "00000000-0000-0000-0000-000000000000.json").write_text(
        json.dumps(
            {
                "session_id": "00000000-0000-0000-0000-000000000000",
                "outcome": "failed",
                "goal_categories": {},
                "friction_counts": {},
            }
        ),
        encoding="utf-8",
    )

    facets = load_facets(tmp_path)
    events = list(ingest_claude_jsonl(FIXTURE_DIR))
    assert len(events) > 0, "fixture_sample.jsonl produced no events"

    attached = list(attach_facets_to_events(events, facets))

    # Same count in, same count out — attach must not drop events.
    assert len(attached) == len(events), (
        f"attach changed event count: in={len(events)} out={len(attached)}"
    )

    # Every attached event whose session matches has a FacetRecord; every
    # other event has facet=None.
    matched = [ev for ev in attached if ev.session == EXPECTED_SESSION]
    assert len(matched) > 0, "no matched events — fixture wiring broken"
    for ev in matched:
        assert ev.facet is not None, (
            f"event for matching session {ev.session!r} has facet=None"
        )
        assert isinstance(ev.facet, FacetRecord)
        # The fixture's outcome must round-trip.
        assert ev.facet.outcome == payload["outcome"]

    unmatched = [ev for ev in attached if ev.session != EXPECTED_SESSION]
    for ev in unmatched:
        assert ev.facet is None, (
            f"event for non-matching session {ev.session!r} should have "
            f"facet=None, got {ev.facet!r}"
        )


def test_attach_facets_with_empty_facets_dict_leaves_events_unchanged():
    """Empty facets dict → all events get facet=None, but otherwise pass
    through unchanged (same agent / session / ts / role / text)."""
    events = list(ingest_claude_jsonl(FIXTURE_DIR))
    assert events, "fixture_sample.jsonl produced no events"

    attached = list(attach_facets_to_events(events, {}))

    assert len(attached) == len(events)
    for orig, new in zip(events, attached):
        assert new.facet is None
        # Other fields are preserved (attach must not mutate them).
        assert new.agent == orig.agent
        assert new.session == orig.session
        assert new.ts == orig.ts
        assert new.role == orig.role
        assert new.text == orig.text


def test_attach_facets_is_a_generator():
    """attach_facets_to_events must be a generator (not a list) so a
    multi-GB Event[] stream attaches lazily — same memory discipline as
    ingest_claude_jsonl."""
    events = list(ingest_claude_jsonl(FIXTURE_DIR))
    result = attach_facets_to_events(events, {})
    assert not isinstance(result, list), (
        "attach_facets_to_events must be a generator, got a list — would "
        "OOM on a real multi-GB Event[] stream."
    )
    iter(result)


def test_event_has_facet_field_with_default_none():
    """Event dataclass must carry a `facet` field, defaulting to None so
    attach is optional and existing T2 callers that construct Event(...)
    without `facet=` keep working."""
    ev = Event(
        agent="claude-code",
        session="s",
        ts="2026-05-22T00:00:00Z",
        role="user",
        text="",
    )
    assert hasattr(ev, "facet"), "Event missing facet field"
    assert ev.facet is None, f"Event.facet default should be None, got {ev.facet!r}"
