#!/usr/bin/env python3
"""CI gate: structural-violation check for the living-spec index.

Consumes the already-computed slice-1 parser outputs and reports the
structural defects that must FAIL the gate:

- a DANGLING ``@req`` — a test's ``@req`` id that is absent from the
  req-to-capability ``namespace`` (likely a typo or a deleted
  requirement);
- each MALFORMED tag line (a ``@req`` / ``@invariant-ref`` marker
  lacking a usable ``: <id>`` value), passed through verbatim.

``find_structural_violations`` covers the first two; ``main()``
additionally folds ``find_malformed_status`` into the SAME FAIL list,
so a ``### Requirement: <id> [activ]`` with a bad status token (a
syntax defect, RED-safe on every push) also fails ``rc=1``.

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
  on mismatch — the merge-boundary stale-index gate;
- ``--check-coverage [root]`` composes the real-repo inputs and runs the
  hermetic ``active_coverage`` — an UNCOVERED active req fails ``rc=1``
  (stderr), a deferred req with 0 tests is surfaced informationally
  (stdout). The merge-boundary coverage gate (sound because CI runs it
  after the green pytest gate, so a linked test == a passing test).
- ``--next-req-id [root]`` prints ``REQ-<max+1>`` where max is the
  highest ``\\d+`` among ALL id-form ``### Requirement:`` headers found
  by the T7 folded loader across live change-folders + archive + the
  living-spec root (``REQ-1`` when none exist), exit 0 always. LIMIT:
  it scans headers PRESENT, not every id ever minted — a retired
  number (its declaration deleted) is free to be re-minted; this only
  matches the "next unused = highest ever seen + 1" convention while
  no declaration is ever deleted.

The index modes default ``<path>`` to ``docs/loom/INDEX.md`` when
omitted; ``--check-coverage`` and ``--next-req-id`` each take only an
optional trailing ``[root]``.

``build_index(root)`` is the single regeneration path the CLI, the
finishing step, and the CI verify lane all call — composing
``collect_structural_records`` -> ``_load_namespace_all`` ->
``generate_index`` across the source tree into the index markdown
string. The namespace is folded, via ``_namespace_roots(root)``, over
every LIVE change-folder ``docs/loom/<change-id>/specs``, every
ARCHIVED ``docs/loom/archive/<x>/specs``, and the living-spec root
``docs/loom/spec`` (tolerated absent) — not a single hardcoded root.

Alongside the structural FAIL lane, the runner drives an advisory WARN
lane via ``run_drift_lane(root)`` — composing collect -> resolve ->
drift across the source tree to surface git-ref drift on stderr. A
WARN is purely informational: it NEVER fails the build and NEVER
touches the structural FAIL list.

Stdlib only, plus the sibling living-spec modules it composes.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from living_spec_collect import (
    collect_bindings,
    collect_malformed,
    collect_structural_records,
)
from living_spec_drift import find_gitref_drift
from living_spec_gitref import resolve_binding_refs
from living_spec_index import (
    find_malformed_status,
    generate_index,
    load_namespace,
    load_req_paths,
    load_req_status,
)


def _namespace_roots(root: Path) -> list[Path]:
    """Return every ``specs`` dir that contributes to the req namespace.

    In order: every LIVE change-folder ``docs/loom/<change-id>/specs``
    (glob ``docs/loom/*/specs``, existing dirs only), every ARCHIVED
    change-folder ``docs/loom/archive/<x>/specs``, then the living-spec
    root ``docs/loom/spec`` (tolerated absent — the folded loaders below
    already handle a missing dir by globbing nothing). Fixes BI-12: a
    single hardcoded ``docs/loom/spec`` root that usually does not exist
    once requirements live in change-folders instead.
    """
    root = Path(root)
    loom_dir = root / "docs" / "loom"
    roots = [
        p / "specs"
        for p in sorted(loom_dir.glob("*"))
        if p.name != "archive" and (p / "specs").is_dir()
    ]
    archive_dir = loom_dir / "archive"
    if archive_dir.is_dir():
        roots += [
            p / "specs"
            for p in sorted(archive_dir.glob("*"))
            if (p / "specs").is_dir()
        ]
    roots.append(loom_dir / "spec")
    return roots


def _load_namespace_all(root: Path) -> dict[str, str]:
    """Fold ``load_namespace`` over every ``_namespace_roots(root)``.

    Dict merge, later roots overwrite earlier ones on the same key. A
    duplicate id declared under two roots is NOT resolved here — that
    is a namespace-collision violation surfaced elsewhere (T8), not
    silently picked here.
    """
    namespace: dict[str, str] = {}
    for specs_dir in _namespace_roots(root):
        namespace.update(load_namespace(specs_dir))
    return namespace


def _load_req_status_all(root: Path) -> dict[str, str]:
    """Fold ``load_req_status`` over every ``_namespace_roots(root)``."""
    statuses: dict[str, str] = {}
    for specs_dir in _namespace_roots(root):
        statuses.update(load_req_status(specs_dir))
    return statuses


def _find_malformed_status_all(root: Path) -> list[str]:
    """Fold ``find_malformed_status`` over every ``_namespace_roots(root)``."""
    offenders: list[str] = []
    for specs_dir in _namespace_roots(root):
        offenders += find_malformed_status(specs_dir)
    return offenders


def _collect_req_declarations_all(root: Path) -> dict[str, list[Path]]:
    """Map each id-form req id to EVERY spec.md path that declares it.

    Folds over ``_namespace_roots(root)``, walking the same
    ``<specs_dir>/<capability>/spec.md`` files as ``_load_namespace_all``.
    Unlike ``_load_namespace_all`` (a dict merge where the last root wins),
    this collects every declaring path per id, so a duplicate declaration
    across namespace files stays visible instead of being silently
    overwritten.
    """
    declarations: dict[str, list[Path]] = {}
    for specs_dir in _namespace_roots(root):
        for req_id, paths in load_req_paths(specs_dir).items():
            declarations.setdefault(req_id, []).extend(paths)
    return declarations


def find_duplicate_req_declarations(root: Path) -> list[str]:
    """Return one violation per req id declared more than once.

    Two distinct collision shapes, both BI-3 (a merge-boundary collision
    on a change-folder spec.md), reported with distinct wording:

    - CROSS-FILE: two branches each minting the same ``REQ-<n>`` in
      different namespace files collide on the first CI run after both
      merge (or earlier, on rebase). Names the id and every declaring
      path.
    - SAME-FILE: the same ``REQ-<n>`` heading appears twice in ONE
      spec.md (a same-file authoring slip, or two branches appending to
      the same capability spec.md that git merges cleanly line-by-line —
      only this checker catches it post-merge). Names the id, the
      occurrence count, and the single declaring path.

    ``declarations`` (via ``load_req_paths``) carries one path entry per
    DECLARING LINE, repeats included — the distinct-vs-repeated path set
    is what tells the two shapes apart; deduping it would make the
    same-file shape invisible.
    """
    declarations = _collect_req_declarations_all(root)
    violations: list[str] = []
    for req_id in sorted(declarations):
        paths = declarations[req_id]
        distinct_paths = sorted(set(paths))
        if len(distinct_paths) > 1:
            joined = ", ".join(str(p) for p in paths)
            violations.append(
                f"DUPLICATE requirement id {req_id} declared in "
                f"multiple files: {joined}"
            )
        elif len(paths) > 1:
            violations.append(
                f"DUPLICATE requirement id {req_id} declared "
                f"{len(paths)} times in {distinct_paths[0]}"
            )
    return violations


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
    - ``_load_namespace_all(root)`` maps each ``### Requirement: <id>``
      across every namespace root (live change-folders, archive, and
      the living-spec root) to its capability (the subdir name);
    - ``generate_index(records, namespace)`` renders the
      capability > requirement > test markdown tree.

    Over a repo with no namespace roots yet, ``_load_namespace_all``
    returns ``{}`` and the index is near-empty — the valid base case,
    not an error.
    """
    root = Path(root)
    tag_records = collect_structural_records(root)
    namespace = _load_namespace_all(root)
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


def _run_check_coverage(root: Path) -> int:
    """Run the ``--check-coverage`` merge-boundary coverage gate.

    Composes the real-repo inputs and runs the hermetic ``active_coverage``.
    SOUND because CI runs this AFTER the green pytest gate, so a linked
    test == a passing test (0 linked == 0 passing). Deferred reqs with 0
    tests are informational (stdout, never fail); uncovered active reqs
    are violations (stderr, rc=1).
    """
    tag_records = collect_structural_records(root)
    namespace = _load_namespace_all(root)
    statuses = _load_req_status_all(root)
    violations, surfaced = active_coverage(tag_records, namespace, statuses)
    for line in surfaced:
        print(line)
    if violations:
        for entry in violations:
            print(entry, file=sys.stderr)
        print(
            f"\nFAIL: {len(violations)} living-spec coverage "
            f"violation(s).",
            file=sys.stderr,
        )
        return 1
    print("OK: every active living-spec req is covered.")
    return 0


def _run_next_req_id(root: Path) -> int:
    """Run the ``--next-req-id`` mode: print next free ``REQ-<n>``, exit 0.

    Ignores the capability values, parses the trailing ``\\d+`` of every
    id-form key in the T7 folded namespace, and prints the next free
    ``REQ-<n>`` (``REQ-1`` on an empty namespace). Opens no new roots and
    reads no header the structural lane does not already read.

    LIMIT: it scans headers PRESENT, not every id ever minted. A retired
    req id (declaration deleted) is NOT excluded from being re-minted once
    nothing references it any more — the doc's minting rule ("next unused
    = highest ever seen + 1") coincides with this tool's "highest present
    + 1" only while no declaration is ever deleted.
    """
    namespace = _load_namespace_all(root)
    highest = 0
    for req_id in namespace:
        match = re.search(r"\d+", req_id)
        if match:
            highest = max(highest, int(match.group()))
    print(f"REQ-{highest + 1}")
    return 0


def main(argv: list[str] | None = None) -> int:
    # argv shapes:
    #   []                              -> default lanes over cwd
    #   [root]                          -> default lanes over root
    #   [--write-index, [path,] [root]] -> regenerate + WRITE path
    #   [--verify-index, [path,] [root]]-> regenerate + byte-identity gate
    #   [--check-coverage, [root]]      -> active-coverage merge gate
    #   [--next-req-id, [root]]         -> print next free REQ-<n>, exit 0
    # A leading --write-index/--verify-index flag consumes an optional
    # <path> arg (defaulting to docs/loom/INDEX.md); --check-coverage and
    # --next-req-id take no <path>. The trailing positional, if present,
    # still selects the source tree (the WARN-lane tests pass
    # `[str(repo)]` with no flag, so the default path must preserve that
    # behavior).
    args = sys.argv[1:] if argv is None else argv

    mode = None
    if args and args[0] in ("--write-index", "--verify-index"):
        mode = args[0]
        args = args[1:]
        index_path = Path(args[0]) if args else _DEFAULT_INDEX
        if args:
            args = args[1:]
    elif args and args[0] in ("--check-coverage", "--next-req-id"):
        mode = args[0]
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
    if mode == "--check-coverage":
        return _run_check_coverage(root)
    if mode == "--next-req-id":
        return _run_next_req_id(root)

    # WARN lane: advisory only. Print each drift WARN to stderr but NEVER
    # let it fail the build or touch the structural FAIL list below.
    for warn in run_drift_lane(root):
        print(warn, file=sys.stderr)

    # Structural FAIL lane: build tag_records / malformed / namespace from
    # the real source tree at `root` and surface every dangling @req +
    # malformed tag. This is the gate that fails the build (rc=1).
    tag_records = collect_structural_records(root)
    malformed = collect_malformed(root)
    namespace = _load_namespace_all(root)
    violations = find_structural_violations(tag_records, malformed, namespace)
    # Fold the malformed-status check into the SAME FAIL list: a bad status
    # token (`[activ]`) is a syntax defect, RED-safe to gate on every push
    # (not a coverage check) — surface it on stderr and count it toward rc=1.
    violations += _find_malformed_status_all(root)
    # Merge-boundary collision guard (BI-3): the same req id declared in
    # more than one namespace file must fail loud rather than let one
    # declaration silently overwrite the other.
    violations += find_duplicate_req_declarations(root)
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
