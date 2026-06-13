"""Framework completeness-audit: gap-angle schema + prompts + selector.

Lever ① of the deep-deep-research opt-in passes. Where schemas.py's
SCOPE_SCHEMA emits the base research angles, FRAMEWORK_AUDIT_SCHEMA emits
*gap-fill* angles — each tagged with the analytical framework + uncovered
cell that motivated it — so an audit pass can top up the angle set before
the unchanged Stage 2 (Search) consumes it.

The gap items reuse the SCOPE_SCHEMA angle shape (`label` / `query` /
optional `rationale`) so a later dedup+budget-cap step can strip them back
to plain angles and hand Stage 2 the same shape it always sees; `framework`
+ `cell` are the only additions and are dropped before Stage 2.

This module is built incrementally across four tasks (schema → classify
prompt → audit prompt → stdin `select`); the CLI uses subparsers so each
later subcommand slots in beside `schema` without restructuring.

CLI:
  python framework_audit.py schema                    prints FRAMEWORK_AUDIT_SCHEMA as JSON
  python framework_audit.py classify-prompt --question Q  prints the type-classify prompt
  python framework_audit.py audit-prompt --angles A --question Q  prints the cell-walk audit prompt
Exit 0. Unknown/missing subcommand → stderr + exit 1.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# (later tasks add audit-pass constants here)

# ---------------------------------------------------------------------------
# JSON Schema
# ---------------------------------------------------------------------------

FRAMEWORK_AUDIT_SCHEMA = {
    "type": "object",
    "required": ["question", "gaps"],
    "properties": {
        "question": {"type": "string"},
        "gaps": {
            "type": "array",
            "items": {
                "type": "object",
                # label/query mirror the SCOPE_SCHEMA angle shape; framework/
                # cell tag which framework's uncovered cell this gap fills.
                "required": ["label", "query", "framework", "cell"],
                "properties": {
                    "label": {"type": "string"},
                    "query": {"type": "string"},
                    "rationale": {"type": "string"},
                    "framework": {"type": "string"},
                    "cell": {"type": "string"},
                },
            },
        },
    },
}

# ---------------------------------------------------------------------------
# Prompt builders
# ---------------------------------------------------------------------------

# Path to the routing table the agent consults to pick frameworks. Kept as a
# bare relative reference (skill-root relative) so the prompt points at the
# bundled resource without hard-coding an absolute path.
LIBRARY_REF: str = "references/framework-audit-library.md"


def classify_prompt(question: str) -> str:
    """Return the question-type classification prompt with {QUESTION} interpolated.

    Asks the agent to classify the research question's *type* against the
    routing-table 題型 keys in references/framework-audit-library.md, then
    pick the 2–3 audit frameworks that type routes to. Text-only — the agent
    reasons over the bundled routing table, it does not fetch anything.

    Mirrors scope_vs_prompt's structure/tone (Question / Task / Output).
    """
    return f"""\
Classify this research question's TYPE so an audit pass can pick the right
completeness-audit frameworks. This is a text-only reasoning step — no web
search, no retrieval; reason over the bundled routing table only.

## Question
{question}

## Task
1. Read the **routing table (路由表)** in `{LIBRARY_REF}` — its left column
   lists question types (題型 keys, e.g. investment/個股, macro/產業,
   policy/法規, product/UX, risk/安全, or the general 萬用起手 row).
2. Decide which 題型 row this question best matches. If it spans two types,
   name the primary one and note the secondary.
3. From that row's first-line frameworks (走查格子), pick the **2–3** audit
   frameworks that best fit this question. Add one reinforcement framework
   only if the route's cells feel thin.

## Output
- `type` — the routing-table 題型 key you matched (plus any secondary).
- `frameworks` — the 2–3 framework names you picked from that route.
- `why` — one line per framework: why it fits THIS question's gaps.

These 2–3 frameworks feed the next (audit) step; pick for coverage of the
question's likely blind spots, not for prestige.

Reasoning over the routing table only — no web search, no retrieval."""


# Number of framework-collective blind-spots in the library's meta-check list
# (the「框架自身的集體盲點」section of references/framework-audit-library.md).
# Interpolated into the prompt so the count stays in sync with the library.
BLIND_SPOT_COUNT: int = 12

# Fallback frameworks when the caller doesn't pass --frameworks: the routing
# table's 萬用起手 (general / any-question) first-line frameworks. Lets
# audit-prompt run standalone without first running classify-prompt.
DEFAULT_FRAMEWORKS = ["MECE/issue tree", "5W1H", "PMEST", "SCQA"]


def audit_prompt(question: str, angles, frameworks) -> str:
    """Return the framework completeness-audit prompt.

    Instructs the agent to walk each chosen framework's cells against the
    *existing* angle set and propose gap-fill angles ONLY for uncovered
    cells — each tagged with `framework` + `cell` per FRAMEWORK_AUDIT_SCHEMA.
    The existing `angles` and the chosen `frameworks` are interpolated as
    JSON / a bullet list so the agent dedups against what's already covered.

    Text-only: the agent reasons over the bundled cell-blocks in
    `{LIBRARY_REF}`, it does not fetch anything.

    Mirrors scope_vs_prompt's Question / Task / Output structure.
    """
    import json

    angles_json = json.dumps(angles, ensure_ascii=False, indent=2)
    frameworks_list = "\n".join(f"- {fw}" for fw in frameworks)
    return f"""\
Run a completeness AUDIT over an existing research-angle set. For each chosen
framework, walk its cells one by one against the angles already on the list
and propose gap-fill angles ONLY for the cells nothing covers. This is a
text-only reasoning step — no web search, no retrieval; reason over the
bundled framework cell-blocks only.

## Question
{question}

## Existing angles (already covered — do NOT re-propose these)
{angles_json}

## Chosen frameworks (walk these cells)
{frameworks_list}

## Task
1. **Walk the cells.** For EACH framework above, open its cell-block in
   `{LIBRARY_REF}` and go **cell by cell (一格一格走查格子)**. For every
   cell, decide: does the existing angle list already cover this cell?
   Mark it **covered** or **uncovered**.
2. **Propose gaps for uncovered cells ONLY.** For each uncovered cell, emit
   one gap-fill angle conforming to FRAMEWORK_AUDIT_SCHEMA — tagged with the
   `framework` it came from and the `cell` it fills, plus a `label`, a
   high-signal `query`, and an optional `rationale`. Do NOT emit a gap for a
   cell the existing angles already cover.
3. **Dedup against the existing angles.** Before adding a gap, check it
   against the existing angle set above — if an existing angle already covers
   that cell's concern, the cell is covered; do not re-propose it. Walk a
   cell shared by two frameworks (see the Cross-framework dedup notes) only
   once.
4. **Final meta-check — the {BLIND_SPOT_COUNT} collective blind-spots.**
   After the framework walk, run the
   「框架自身的集體盲點 ({BLIND_SPOT_COUNT} collective blind-spots)」 list at
   the bottom of `{LIBRARY_REF}` — the dimensions ALL frameworks
   structurally miss (time-decay, base rates, second-order, unknown-unknowns,
   …). For each blind-spot your angles don't already cover, add a gap-fill
   angle tagged `framework: "collective-blind-spot"` and the blind-spot name
   as its `cell`.

## Output
Emit JSON conforming to FRAMEWORK_AUDIT_SCHEMA: `{{ "question", "gaps": [...] }}`.
Each gap has:
- `label` — short name for the gap-fill angle
- `query` — a specific, high-signal web search query for the uncovered cell
- `framework` — which framework's walk surfaced this cell (or
  `collective-blind-spot`)
- `cell` — the specific uncovered cell / dimension this angle fills
- `rationale` — (optional) why this cell was uncovered and why it matters

If a framework's cells are all covered, emit no gaps for it — an empty gap
list is a valid, honest result. Propose gaps for genuinely uncovered cells
only; padding the list defeats the audit.

Reasoning over the bundled cell-blocks only — no web search, no retrieval."""


# ---------------------------------------------------------------------------
# Deterministic gap selector
# ---------------------------------------------------------------------------

from dedup import norm_url  # read-only import of the synced SSOT primitive


def _angle_keys(angle: dict) -> tuple[str, str]:
    """Identity keys for dedup: (case-folded label, normalized query).

    Mirrors vs_select.py's `_dedup_key`: a URL-shaped query is normalized via
    `dedup.norm_url`; a plain query is casefold+strip. A gap collides with an
    existing angle (or an earlier gap) if EITHER key matches.
    """
    label = angle.get("label", "").casefold().strip()
    query = angle.get("query", "")
    if "://" in query or query.startswith("//"):
        qkey = norm_url(query)
    else:
        qkey = query.casefold().strip()
    return (label, qkey)


def _strip_angle(gap: dict) -> dict:
    """Reduce a gap to the SCOPE_SCHEMA angle shape {label, query, rationale?}.

    Mirrors vs_select.py's `_strip`: rationale kept only if present; framework
    and cell (the FRAMEWORK_AUDIT_SCHEMA-only tags) are dropped so Stage 2 sees
    the same angle shape it always sees.
    """
    angle = {"label": gap["label"], "query": gap["query"]}
    rationale = gap.get("rationale")
    if rationale:
        angle["rationale"] = rationale
    return angle


def select_gaps(gap_angles, existing_angles, fetch_slots: int) -> list:
    """Dedup gap-fill angles against existing angles, cap to budget, strip.

    Deterministic, stdlib-only. Steps:
      1. Drop any gap whose case-folded label OR normalized query matches an
         existing angle, OR an EARLIER surviving gap (intra-gap dedup).
      2. Cap survivors to `fetch_slots` (remaining MAX_FETCH budget). If
         `fetch_slots <= 0`, return [].
      3. Strip each survivor to {label, query, rationale?} (SCOPE_SCHEMA shape).

    Empty input or all-dropped → [] (a valid, honest result; the caller then
    proceeds with the original angle set unchanged).
    """
    if fetch_slots <= 0:
        return []

    # Seed the seen-set with both keys of every existing angle. A gap collides
    # if EITHER its label OR its query key is already seen, so the two key
    # families are namespaced (("l", ...) / ("q", ...)) to avoid cross-matching.
    seen: set = set()
    for a in existing_angles:
        label_key, query_key = _angle_keys(a)
        seen.add(("l", label_key))
        seen.add(("q", query_key))

    survivors = []
    for gap in gap_angles:
        label_key, query_key = _angle_keys(gap)
        if ("l", label_key) in seen or ("q", query_key) in seen:
            continue
        seen.add(("l", label_key))
        seen.add(("q", query_key))
        survivors.append(gap)

    capped = survivors[:fetch_slots]
    return [_strip_angle(g) for g in capped]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv=None) -> int:
    import argparse
    import json
    import sys

    args = sys.argv[1:] if argv is None else argv

    parser = argparse.ArgumentParser(prog="framework_audit.py", add_help=False)
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("schema", add_help=False)
    p_classify = sub.add_parser("classify-prompt", add_help=False)
    p_classify.add_argument("--question", required=True)
    p_audit = sub.add_parser("audit-prompt", add_help=False)
    p_audit.add_argument("--question", required=True)
    p_audit.add_argument("--angles", required=True)
    # --frameworks is optional JSON; default to the 萬用起手 (general) route's
    # first-line frameworks so the prompt is usable without classify output.
    p_audit.add_argument("--frameworks", default=None)
    # `select` takes no flags — it reads {gap_angles, existing_angles,
    # fetch_slots} from stdin and writes {angles} to stdout (vs_select.py mold).
    sub.add_parser("select", add_help=False)

    # Derive the valid-subcommand list from the registered subparsers so it
    # cannot drift from what's actually wired up (single source of truth).
    valid = ", ".join(sub.choices)

    # Reject an unknown / missing subcommand up front, BEFORE argparse — so a
    # missing-required-arg error on a *known* subcommand isn't mislabeled
    # "unknown subcommand".
    if not args or args[0] not in sub.choices:
        name = args[0] if args else "(none)"
        print(f"unknown subcommand {name!r}; expected one of {{{valid}}}",
              file=sys.stderr)
        return 1

    try:
        ns = parser.parse_args(args)
    except SystemExit:
        # Known subcommand, bad/missing args — argparse already wrote its own
        # specific error to stderr; just normalize the exit code.
        return 1

    if ns.command == "schema":
        print(json.dumps(FRAMEWORK_AUDIT_SCHEMA, indent=2))
        return 0
    if ns.command == "classify-prompt":
        print(classify_prompt(ns.question))
        return 0
    if ns.command == "audit-prompt":
        try:
            angles = json.loads(ns.angles)
        except json.JSONDecodeError as exc:
            print(f"--angles must be valid JSON: {exc}", file=sys.stderr)
            return 1
        if ns.frameworks is None:
            frameworks = DEFAULT_FRAMEWORKS
        else:
            try:
                frameworks = json.loads(ns.frameworks)
            except json.JSONDecodeError as exc:
                print(f"--frameworks must be valid JSON: {exc}", file=sys.stderr)
                return 1
        print(audit_prompt(ns.question, angles, frameworks))
        return 0
    if ns.command == "select":
        payload = json.load(sys.stdin)
        angles = select_gaps(
            payload["gap_angles"],
            payload["existing_angles"],
            payload["fetch_slots"],
        )
        json.dump({"angles": angles}, sys.stdout)
        return 0
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
