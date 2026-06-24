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
inputs. ``main()`` builds ``tag_records`` / ``malformed`` /
``namespace`` from the REAL source tree, fails ``rc=1`` on any
structural violation (dangling ``@req`` / malformed tag), and runs the
advisory WARN lane alongside. ``main()`` also supports two alternate
modes selected from argv:

- ``--write-index <path>`` regenerates via ``build_index(root)`` and
  WRITES ``<path>`` (the finishing-step / once-per-branch regen path);
- ``--verify-index <path>`` regenerates and asserts byte-identity vs
  the committed ``<path>`` (reusing ``index_is_current``), returning 1
  on mismatch — the merge-boundary stale-index gate.

Both default ``<path>`` to ``docs/loom/INDEX.md`` when omitted.

``build_index(root)`` is the single regeneration path the CLI, the
finishing step, and the CI verify lane all call — composing
``collect_structural_records`` -> ``load_namespace`` -> ``generate_index``
across the source tree into the index markdown string.

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

from living_spec_collect import (
    collect_bindings,
    collect_malformed,
    collect_structural_records,
)
from living_spec_drift import find_gitref_drift
from living_spec_gitref import resolve_binding_refs
from living_spec_index import generate_index, load_namespace


def find_structural_violations(
    tag_records: list[dict],
    malformed: list[str],
    namespace: dict[str, str],
) -> list[str]:
    """Return one violation string per structural defect, source order.

    ``tag_records`` is ``extract_tags`` output (one dict per tagged
    test with ``test`` / ``reqs`` / ``invariant_refs``); ``malformed``
    is ``collect_malformed`` output (raw malformed comment lines);
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


def active_coverage(
    tag_records: list[dict],
    namespace: dict[str, str],
    statuses: dict[str, str],
) -> tuple[list[str], list[str]]:
    """Partition namespace reqs by coverage and intent status.

    A hermetic check over in-memory inputs (no filesystem), mirroring
    ``find_structural_violations``' shape:

    - ``tag_records`` is ``collect_structural_records`` output (one dict
      per tagged test with ``test`` / ``reqs`` / ``invariant_refs``);
    - ``namespace`` is ``load_namespace`` output (``{req_id: capability}``);
    - ``statuses`` is ``load_req_status`` output (``{req_id: "active" |
      "deferred"}``); a req absent from ``statuses`` defaults ``"active"``.

    The records are inverted to req -> set-of-tests, then each req in
    ``namespace`` is classified:

    - ``active`` with 0 linked tests -> a coverage ``violation``
      (``"UNCOVERED active req '<id>' (0 passing tests)"``): an active
      promise must never sit unverified;
    - ``deferred`` with 0 linked tests -> ``surfaced`` advisory
      (``"deferred req '<id>' (inspirational, 0 tests)"``): an
      intentionally-aspirational req, never a defect;
    - any req WITH >=1 linked test -> neither list, regardless of status.

    Returns ``(violations, surfaced)``, each sorted by req id. Empty
    ``violations`` == every active req is covered.
    """
    linked: dict[str, set[str]] = {}
    for record in tag_records:
        for req in record["reqs"]:
            linked.setdefault(req, set()).add(record["test"])

    violations: list[str] = []
    surfaced: list[str] = []
    for req in sorted(namespace):
        if linked.get(req):
            continue
        status = statuses.get(req, "active")
        if status == "deferred":
            surfaced.append(
                f"deferred req '{req}' (inspirational, 0 tests)"
            )
        else:
            violations.append(
                f"UNCOVERED active req '{req}' (0 passing tests)"
            )
    return violations, surfaced


def index_is_current(committed_md: str, regenerated_md: str) -> bool:
    """Return True iff a committed INDEX.md matches a fresh regeneration.

    Byte-identity check (the verify-drift pattern): CI regenerates the
    index with ``generate_index(...)`` and compares the result against
    the committed file. Any difference — including a stray trailing
    newline — means the committed file is stale and the gate must fail
    loud, so the index can never silently drift from its source.
    """
    return committed_md == regenerated_md


def build_index(root: Path) -> str:
    """Return the freshly regenerated living-spec index markdown.

    The single regeneration path shared by the CLI, the finishing step,
    and the CI verify lane. Composes the three upstream functions over
    the source tree at ``root``:

    - ``collect_structural_records(root)`` parses every ANCHORED ``@req``
      binding under ``root`` into ``{test, reqs, invariant_refs}``
      records;
    - ``load_namespace(root / "docs/loom/spec")`` maps each
      ``### Requirement: <id>`` to its capability (the subdir name);
    - ``generate_index(records, namespace)`` renders the
      capability > requirement > test markdown tree.

    Over a repo with no ``docs/loom/spec`` tree yet, ``load_namespace``
    returns ``{}`` and the index is near-empty — the valid base case,
    not an error.
    """
    root = Path(root)
    tag_records = collect_structural_records(root)
    namespace = load_namespace(root / "docs" / "loom" / "spec")
    return generate_index(tag_records, namespace)


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

    INTENTIONAL lane asymmetry: this lane collects via ``collect_bindings``
    (anchored regex only), whereas the structural FAIL lane collects via
    ``collect_structural_records`` (additionally ``tokenize``-filtered to
    drop ``@req`` markers sitting inside string literals — e.g. parser
    self-test fixtures). So over a self-hosting tree the two lanes can
    disagree on what counts as a binding: the drift lane may see phantom
    bindings from fixture strings that the structural lane (correctly)
    sees as zero. This is BY DESIGN, not an oversight — string-literal
    awareness was scoped to the FAIL lane (where a false positive blocks
    a merge) and deferred for this ADVISORY lane (a false positive here
    is at worst a spurious WARN that never blocks the build; see the
    design brief's "Residual rot surface" deferred-hardening note). If the
    drift lane is ever promoted to a blocking gate, give it the same
    ``_real_comment_lines`` filter first.
    """
    root = Path(root)
    enriched = [
        resolved
        for binding in collect_bindings(root)
        if (resolved := resolve_binding_refs(binding, root)) is not None
    ]
    return find_gitref_drift(enriched)


_DEFAULT_INDEX = Path("docs") / "loom" / "INDEX.md"


def main(argv: list[str] | None = None) -> int:
    # argv shapes:
    #   []                              -> default lanes over cwd
    #   [root]                          -> default lanes over root
    #   [--write-index, [path,] [root]] -> regenerate + WRITE path
    #   [--verify-index, [path,] [root]]-> regenerate + byte-identity gate
    # A leading --write-index/--verify-index flag consumes an optional
    # <path> arg (defaulting to docs/loom/INDEX.md); the trailing
    # positional, if present, still selects the source tree (the WARN-lane
    # tests pass `[str(repo)]` with no flag, so the default path must
    # preserve that behavior).
    args = sys.argv[1:] if argv is None else argv

    mode = None
    if args and args[0] in ("--write-index", "--verify-index"):
        mode = args[0]
        args = args[1:]
        index_path = Path(args[0]) if args else _DEFAULT_INDEX
        if args:
            args = args[1:]

    root = Path(args[0]) if args else Path.cwd()

    if mode == "--write-index":
        index_path.write_text(build_index(root), encoding="utf-8")
        return 0
    if mode == "--verify-index":
        committed = index_path.read_text(encoding="utf-8")
        if index_is_current(committed, build_index(root)):
            print(f"OK: {index_path} is current.")
            return 0
        print(
            f"FAIL: {index_path} is stale (not byte-identical to a fresh "
            f"build_index). Regenerate with --write-index.",
            file=sys.stderr,
        )
        return 1

    # WARN lane: advisory only. Print each drift WARN to stderr but NEVER
    # let it fail the build or touch the structural FAIL list below.
    for warn in run_drift_lane(root):
        print(warn, file=sys.stderr)

    # Structural FAIL lane: build tag_records / malformed / namespace from
    # the real source tree at `root` and surface every dangling @req +
    # malformed tag. This is the gate that fails the build (rc=1).
    tag_records = collect_structural_records(root)
    malformed = collect_malformed(root)
    namespace = load_namespace(root / "docs" / "loom" / "spec")
    violations = find_structural_violations(tag_records, malformed, namespace)
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
