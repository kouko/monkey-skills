#!/usr/bin/env python3
"""Tests for the living-spec git-ref drift comparator.

A binding drifts iff the test body's last-touch timestamp is newer
than its ``@req`` binding-line timestamp — i.e. the test changed
after the requirement link was last reaffirmed. These tests pin the
WARN-emission contract: which bindings warn, which stay silent, and
that the input order is preserved.
"""
from __future__ import annotations

from living_spec_drift import find_gitref_drift


def _binding(test, req, body_ref, binding_ref, body_ts, binding_ts):
    return {
        "test": test,
        "req": req,
        "body_ref": body_ref,
        "binding_ref": binding_ref,
        "body_ts": body_ts,
        "binding_ts": binding_ts,
    }


def test_flags_body_newer_than_binding():
    # body_ts (200) > binding_ts (100) => drifted => exactly one WARN
    # that names the test, the req, and both refs.
    bindings = [
        _binding("test_foo", "REQ-1", "bodysha", "bindsha", 200, 100),
    ]
    warns = find_gitref_drift(bindings)
    assert len(warns) == 1
    msg = warns[0]
    assert "test_foo" in msg
    assert "REQ-1" in msg
    assert "bodysha" in msg
    assert "bindsha" in msg


def test_body_not_newer_emits_nothing():
    # body older than binding => silent.
    older = [_binding("test_a", "REQ-2", "b", "k", 50, 100)]
    assert find_gitref_drift(older) == []
    # equal timestamps are NOT drift (rule is strict >).
    equal = [_binding("test_b", "REQ-3", "b", "k", 100, 100)]
    assert find_gitref_drift(equal) == []


def test_mixed_returns_only_drifted_in_input_order():
    bindings = [
        _binding("test_clean", "REQ-1", "b1", "k1", 100, 100),
        _binding("test_drift_a", "REQ-2", "b2", "k2", 300, 100),
        _binding("test_older", "REQ-3", "b3", "k3", 10, 100),
        _binding("test_drift_b", "REQ-4", "b4", "k4", 999, 1),
    ]
    warns = find_gitref_drift(bindings)
    assert len(warns) == 2
    assert "test_drift_a" in warns[0]
    assert "test_drift_b" in warns[1]


def test_empty_input_returns_empty():
    assert find_gitref_drift([]) == []
