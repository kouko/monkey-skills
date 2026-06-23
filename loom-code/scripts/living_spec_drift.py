#!/usr/bin/env python3
"""Detect git-ref drift between a living-spec test and its ``@req`` binding.

A *binding* links a test-function to the requirement it covers, with
two committer timestamps: when the test *body* was last touched
(``body_ts``) and when its ``@req`` *binding line* was last touched
(``binding_ts``). When the body moves AFTER the binding, the test's
behavior may have changed without the requirement link being
reaffirmed — the link has DRIFTED and warrants a human look.

The importable entry point is ``find_gitref_drift(bindings)
-> list[str]``, returning one WARN string per drifted binding in
source order. The ``*_ts`` epoch ints are the orderable key; the
``*_ref`` SHAs feed only the human-readable message. Pure stdlib — git
lookup that produces these inputs is a separate (caller's) concern.

Each binding is a dict::

    {"test": str, "req": str, "body_ref": str, "binding_ref": str,
     "body_ts": int, "binding_ts": int}
"""
from __future__ import annotations


def find_gitref_drift(bindings: list[dict]) -> list[str]:
    """Return one WARN string per drifted binding, in input order.

    A binding has DRIFTED iff ``body_ts > binding_ts`` (strict — equal
    timestamps are NOT drift). Each drifted binding yields exactly one
    WARN naming its ``test``, ``req``, and both refs; non-drifted
    bindings yield nothing. An empty / all-clean input returns ``[]``.
    """
    warns: list[str] = []
    for binding in bindings:
        if binding["body_ts"] > binding["binding_ts"]:
            warns.append(
                f"WARN drift: {binding['test']} "
                f"(@req {binding['req']}) — body moved at "
                f"{binding['body_ref']} after binding at "
                f"{binding['binding_ref']}"
            )
    return warns
