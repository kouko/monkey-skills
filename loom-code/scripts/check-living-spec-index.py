#!/usr/bin/env python3
"""CI gate: structural-violation check for the living-spec index.

Consumes the already-computed slice-1 parser outputs and reports the
structural defects that must FAIL the gate:

- a DANGLING ``@req`` — a test's ``@req`` id that is absent from the
  req-to-capability ``namespace`` (likely a typo or a deleted
  requirement);
- each MALFORMED tag line (a ``@req`` / ``@invariant-ref`` marker
  lacking a usable ``: <id>`` value), passed through verbatim.

Clean input (every ``@req`` resolves, no malformed lines) returns the
empty list.

The importable entry point is
``find_structural_violations(tag_records, malformed, namespace)
-> list[str]`` so it can be tested hermetically against in-memory
inputs. The ``__main__`` block is a thin runner: real-repo wiring
(building ``tag_records`` / ``malformed`` / ``namespace`` from the
source tree) is deferred to a later slice, so it currently runs over
empty inputs and exits 0.

Alongside the structural FAIL lane, the runner drives an advisory WARN
lane via ``run_drift_lane(root)`` — composing collect -> resolve ->
drift across the source tree to surface git-ref drift on stderr. A
WARN is purely informational: it NEVER fails the build and NEVER
touches the structural FAIL list.

Stdlib only, plus the sibling living-spec modules it composes.
"""
from __future__ import annotations

import sys
from pathlib import Path

from living_spec_collect import collect_bindings
from living_spec_drift import find_gitref_drift
from living_spec_gitref import resolve_binding_refs


def find_structural_violations(
    tag_records: list[dict],
    malformed: list[str],
    namespace: dict[str, str],
) -> list[str]:
    """Return one violation string per structural defect, source order.

    ``tag_records`` is ``extract_tags`` output (one dict per tagged
    test with ``test`` / ``reqs`` / ``invariant_refs``); ``malformed``
    is ``find_malformed_tags`` output (raw malformed comment lines);
    ``namespace`` is ``load_namespace`` output (``{req_id: capability}``).

    Two violation kinds are reported:

    - dangling ``@req``: a ``reqs`` entry absent from ``namespace`` ->
      ``"DANGLING @req '<id>' in <test> (not in namespace)"``;
    - malformed tag: each raw line -> ``"MALFORMED tag: <line>"``.

    Empty list == structurally clean.
    """
    violations: list[str] = []
    for record in tag_records:
        test = record["test"]
        for req in record["reqs"]:
            if req not in namespace:
                violations.append(
                    f"DANGLING @req '{req}' in {test} (not in namespace)"
                )
    for line in malformed:
        violations.append(f"MALFORMED tag: {line}")
    return violations


def index_is_current(committed_md: str, regenerated_md: str) -> bool:
    """Return True iff a committed INDEX.md matches a fresh regeneration.

    Byte-identity check (the verify-drift pattern): CI regenerates the
    index with ``generate_index(...)`` and compares the result against
    the committed file. Any difference — including a stray trailing
    newline — means the committed file is stale and the gate must fail
    loud, so the index can never silently drift from its source.
    """
    return committed_md == regenerated_md


def run_drift_lane(root: Path) -> list[str]:
    """Return the git-ref WARN strings for the source tree at ``root``.

    Composes the three upstream modules end-to-end:
    ``collect_bindings(root)`` finds every ``@req`` binding under the
    tree, ``resolve_binding_refs(binding, root)`` enriches each with its
    body + binding-line commit refs/timestamps, and
    ``find_gitref_drift(...)`` emits one WARN per binding whose body
    moved after its ``@req`` line. The empty list means no drift.

    Bindings that resolve as UNRESOLVABLE (``resolve_binding_refs``
    returns ``None`` — a net-new tagged test in the working tree with no
    committed baseline yet, the everyday local pre-commit workflow) are
    SKIPPED: with no prior committed ref they cannot be drift, and the
    lane must never crash. This keeps the advisory lane's promise — it
    NEVER fails the build and is wholly independent of the structural
    FAIL path.
    """
    root = Path(root)
    enriched = [
        resolved
        for binding in collect_bindings(root)
        if (resolved := resolve_binding_refs(binding, root)) is not None
    ]
    return find_gitref_drift(enriched)


def main(argv: list[str] | None = None) -> int:
    # Optional argv path selects the source tree for the WARN lane; the
    # CI invokes this from the repo root, so default to cwd.
    args = sys.argv[1:] if argv is None else argv
    root = Path(args[0]) if args else Path.cwd()

    # WARN lane: advisory only. Print each drift WARN to stderr but NEVER
    # let it fail the build or touch the structural FAIL list below.
    for warn in run_drift_lane(root):
        print(warn, file=sys.stderr)

    # Slice boundary: real-repo wiring (building tag_records / malformed
    # / namespace from the source tree) is deferred. Run over empty
    # inputs for now — the function is exercised by its unit tests.
    violations = find_structural_violations([], [], {})
    if violations:
        for entry in violations:
            print(entry, file=sys.stderr)
        print(
            f"\nFAIL: {len(violations)} living-spec structural "
            f"violation(s).",
            file=sys.stderr,
        )
        return 1
    print("OK: no living-spec structural violations.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
