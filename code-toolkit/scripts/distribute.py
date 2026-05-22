#!/usr/bin/env python3
"""Distribute canonical standards / rubrics / checklists from
``domain-teams:code-team`` into ``code-toolkit`` skills as functional copies.

Layout:

    canonical SSOT
      ../domain-teams/skills/code-team/{standards,rubrics,checklists}/<file>

    functional copy (this plugin)
      code-toolkit/skills/<skill>/{standards,rubrics,checklists}/<file>

Each functional copy is *(HTML header)+(canonical bytes)*. The header points
back to the SSOT path and forbids in-place editing. ``verify-drift.py``
regenerates the expected payload and byte-diffs it against what is on disk;
any mismatch fails the CI gate.

Pure stdlib (P1-E). Cross-plugin variant of the ``legal-toolkit/scripts/``
pattern, with the canonical layer living in a sibling plugin instead of in
this plugin's own ``canonical/`` directory.

Workflow
========
1. Land all edits in ``domain-teams/skills/code-team/`` (canonical).
2. In the same commit run ``python3 code-toolkit/scripts/distribute.py``.
3. ``code-toolkit/scripts/verify-drift.py`` runs in CI and fails on byte diff.

Routing table is hand-maintained — there is no auto-skip. Adding or removing
a consuming skill = update ROUTE in the same commit.
"""
from __future__ import annotations

import sys
from pathlib import Path

# code-toolkit/ — parent of scripts/
ROOT = Path(__file__).resolve().parent.parent

# monkey-skills/ repo root — parent of code-toolkit/, sibling of domain-teams/
REPO_ROOT = ROOT.parent

# Canonical knowledge layer in sibling plugin
CODE_TEAM_ROOT = REPO_ROOT / "domain-teams" / "skills" / "code-team"

# Routing table — canonical sub-path (relative to code-team/) → list of
# functional-copy destinations (relative to code-toolkit/).
#
# Update in the SAME commit that adds or removes a consuming skill — there is
# no auto-discovery.
_SDD_STANDARDS_DIR = "skills/subagent-driven-development/standards"
_SDD_RUBRICS_DIR = "skills/subagent-driven-development/rubrics"
_SDD_CHECKLISTS_DIR = "skills/subagent-driven-development/checklists"

ROUTE: dict[str, list[str]] = {
    # tdd-iron-law owns its own functional copy of the TDD standard so the
    # skill can ship without subagent-driven-development. subagent-driven-
    # development keeps its own copy too so the implementer / reviewer
    # subagents can load all seven standards via a single resource path.
    "standards/tdd-standard.md": [
        "skills/tdd-iron-law/standards/tdd-standard.md",
        f"{_SDD_STANDARDS_DIR}/tdd-standard.md",
    ],
    "standards/naming-and-functions.md": [
        f"{_SDD_STANDARDS_DIR}/naming-and-functions.md",
    ],
    "standards/pragmatic-principles.md": [
        f"{_SDD_STANDARDS_DIR}/pragmatic-principles.md",
    ],
    "standards/solid-principles.md": [
        f"{_SDD_STANDARDS_DIR}/solid-principles.md",
    ],
    "standards/refactoring-standard.md": [
        f"{_SDD_STANDARDS_DIR}/refactoring-standard.md",
    ],
    "standards/app-security-standard.md": [
        f"{_SDD_STANDARDS_DIR}/app-security-standard.md",
    ],
    "standards/character-encoding-security.md": [
        f"{_SDD_STANDARDS_DIR}/character-encoding-security.md",
    ],
    "standards/external-surface-grounding.md": [
        f"{_SDD_STANDARDS_DIR}/external-surface-grounding.md",
    ],
    "rubrics/quality-gate.md": [
        f"{_SDD_RUBRICS_DIR}/quality-gate.md",
    ],
    "rubrics/arch-gate.md": [
        f"{_SDD_RUBRICS_DIR}/arch-gate.md",
    ],
    "checklists/security-checklist.md": [
        f"{_SDD_CHECKLISTS_DIR}/security-checklist.md",
    ],
    "checklists/spec-consistency.md": [
        f"{_SDD_CHECKLISTS_DIR}/spec-consistency.md",
    ],
}


def header_for(canonical_subpath: str) -> str:
    """Return the HTML comment header prepended to every functional copy.

    P1-D: the header MUST appear as the first bytes of the functional copy
    and MUST name the canonical SSOT path so a human grepping the copy sees
    where to edit instead.
    """
    return (
        "<!--\n"
        "FUNCTIONAL COPY — DO NOT EDIT IN PLACE\n"
        f"SSOT: domain-teams/skills/code-team/{canonical_subpath}\n"
        "Sync via: code-toolkit/scripts/distribute.py\n"
        "-->\n\n"
    )


def expected_payload(canonical_subpath: str) -> bytes:
    """Return the byte content the functional copy on disk MUST equal."""
    src = CODE_TEAM_ROOT / canonical_subpath
    return header_for(canonical_subpath).encode("utf-8") + src.read_bytes()


def distribute(route: dict[str, list[str]] | None = None) -> int:
    """Copy each canonical file (with SSOT header prepended) to every routed
    destination. Returns the number of files written. Creates parent dirs as
    needed. Raises ``FileNotFoundError`` if a canonical file in ROUTE is
    absent — there is no auto-skip.
    """
    if route is None:
        route = ROUTE

    written = 0
    for canonical_subpath, dests in route.items():
        src = CODE_TEAM_ROOT / canonical_subpath
        if not src.is_file():
            raise FileNotFoundError(
                f"canonical missing: {src.relative_to(REPO_ROOT)}"
            )
        payload = expected_payload(canonical_subpath)
        for rel_dst in dests:
            dst = ROOT / rel_dst
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(payload)
            written += 1
            print(
                f"[deploy] code-team:{canonical_subpath} "
                f"-> code-toolkit/{rel_dst}"
            )
    return written


# ─── Agent in-file injection blocks (P15-12 + reviewer-discipline) ─────────
#
# Plugin-level agent files in ``code-toolkit/agents/`` carry one or more
# canonical text blocks between BEGIN/END markers. The canonical text lives
# once in ``code-toolkit/scripts/_*.md``; ``distribute_agent_injections``
# rewrites each block in every routed agent to match. This is the SSOT-and-
# functional-copy variant for in-file SECTIONS rather than whole files.
#
# Two blocks are routed today:
#
# 1. **baseline-v1** — the 12-rule engineering baseline. Applies to every
#    plugin-level agent (implementer + 3 reviewers).
# 2. **reviewer-discipline-v1** — rules R1+R2 for verdict-producing agents
#    (standards_version stamp + evidence-citation requirement). Applies ONLY
#    to the 3 reviewer agents; implementer does not carry it.

AGENT_BASELINE_SSOT_REL = "scripts/_baseline.md"
AGENT_BASELINE_BEGIN = (
    "<!-- BEGIN baseline-v1 — managed by "
    "code-toolkit/scripts/distribute.py from "
    "code-toolkit/scripts/_baseline.md — do not edit in place -->"
)
AGENT_BASELINE_END = "<!-- END baseline-v1 -->"

# Routing: agent files that embed the baseline block. Add new agent files
# here when promoting them to plugin-level.
#
# v0.5.2 (P15-12 Phase 1): implementer.md (proof-of-mechanism)
# v0.6.0 (P15-12 Phase 2): spec-reviewer.md + code-quality-reviewer.md +
#                           code-reviewer.md (SDD reviewer pair + whole-branch
#                           reviewer from requesting-code-review). systematic-
#                           debugging has no agent directory; no debugger.md
#                           in this batch.
AGENT_BASELINE_TARGETS: list[str] = [
    "agents/implementer.md",
    "agents/spec-reviewer.md",
    "agents/code-quality-reviewer.md",
    "agents/code-reviewer.md",
]

AGENT_REVIEWER_DISCIPLINE_SSOT_REL = "scripts/_reviewer-discipline.md"
AGENT_REVIEWER_DISCIPLINE_BEGIN = (
    "<!-- BEGIN reviewer-discipline-v1 — managed by "
    "code-toolkit/scripts/distribute.py from "
    "code-toolkit/scripts/_reviewer-discipline.md — do not edit in place -->"
)
AGENT_REVIEWER_DISCIPLINE_END = "<!-- END reviewer-discipline-v1 -->"

# Routing: reviewer agents only. Implementer is intentionally excluded — it
# does not produce verdicts and has no `standards_version` / evidence-field
# discipline to apply.
AGENT_REVIEWER_DISCIPLINE_TARGETS: list[str] = [
    "agents/spec-reviewer.md",
    "agents/code-quality-reviewer.md",
    "agents/code-reviewer.md",
]

AGENT_RULE_SHEET_SSOT_REL = "scripts/_rule-sheet.md"
AGENT_RULE_SHEET_BEGIN = (
    "<!-- BEGIN rule-sheet-v1 — managed by "
    "code-toolkit/scripts/distribute.py from "
    "code-toolkit/scripts/_rule-sheet.md — do not edit in place -->"
)
AGENT_RULE_SHEET_END = "<!-- END rule-sheet-v1 -->"
AGENT_RULE_SHEET_TARGETS: list[str] = list(AGENT_BASELINE_TARGETS)
# ^ routes to all 4 agents (implementer + 3 reviewers). Single canonical
#   text — implementer reads same content as reviewers; verdict aggregation
#   rules are informational for implementer (self-check during TDD reduces
#   reviewer NEEDS_REVISION rate).


def expected_baseline_text() -> str:
    """Canonical text of the baseline block (the body of ``_baseline.md``)."""
    src = ROOT / AGENT_BASELINE_SSOT_REL
    return src.read_text(encoding="utf-8").rstrip("\n")


def expected_reviewer_discipline_text() -> str:
    """Canonical text of the reviewer-discipline block (the body of
    ``_reviewer-discipline.md``).
    """
    src = ROOT / AGENT_REVIEWER_DISCIPLINE_SSOT_REL
    return src.read_text(encoding="utf-8").rstrip("\n")


def expected_rule_sheet_text() -> str:
    """Canonical text of the rule-sheet block (the body of
    ``_rule-sheet.md``).
    """
    src = ROOT / AGENT_RULE_SHEET_SSOT_REL
    return src.read_text(encoding="utf-8").rstrip("\n")


def _rebuild_marker_block(
    content: str,
    agent_rel: str,
    begin_marker: str,
    end_marker: str,
    canonical_text: str,
    label: str,
) -> str:
    """Find ``begin_marker``/``end_marker`` in ``content`` and replace the
    body between them with ``canonical_text``. Returns the rebuilt content.
    Raises ``ValueError`` if either marker is missing or ordered wrong.
    """
    begin_idx = content.find(begin_marker)
    end_idx = content.find(end_marker)
    if begin_idx == -1 or end_idx == -1:
        raise ValueError(
            f"{agent_rel}: missing BEGIN or END {label} marker"
        )
    if begin_idx >= end_idx:
        raise ValueError(
            f"{agent_rel}: BEGIN {label} marker appears at/after END marker"
        )
    before = content[: begin_idx + len(begin_marker)]
    after = content[end_idx:]
    return before + "\n" + canonical_text + "\n" + after


def expected_agent_text(agent_rel: str) -> str:
    """Reconstruct the expected on-disk text of an agent file by rebuilding
    every injection block from SSOT and leaving role-contract / other
    content untouched. Raises ``ValueError`` if a routed agent lacks the
    BEGIN/END markers for any block it should carry.

    Three blocks are rebuilt:
    - baseline-v1 (every routed agent — see ``AGENT_BASELINE_TARGETS``)
    - reviewer-discipline-v1 (reviewer agents only — see
      ``AGENT_REVIEWER_DISCIPLINE_TARGETS``)
    - rule-sheet-v1 (every routed agent — see ``AGENT_RULE_SHEET_TARGETS``,
      same set as baseline)
    """
    dst = ROOT / agent_rel
    content = dst.read_text(encoding="utf-8")

    # Baseline applies to every routed agent.
    content = _rebuild_marker_block(
        content,
        agent_rel,
        AGENT_BASELINE_BEGIN,
        AGENT_BASELINE_END,
        expected_baseline_text(),
        "baseline",
    )

    # Reviewer-discipline applies only to reviewer agents.
    if agent_rel in AGENT_REVIEWER_DISCIPLINE_TARGETS:
        content = _rebuild_marker_block(
            content,
            agent_rel,
            AGENT_REVIEWER_DISCIPLINE_BEGIN,
            AGENT_REVIEWER_DISCIPLINE_END,
            expected_reviewer_discipline_text(),
            "reviewer-discipline",
        )

    # Rule-sheet applies to every routed agent (same routing as baseline).
    content = _rebuild_marker_block(
        content,
        agent_rel,
        AGENT_RULE_SHEET_BEGIN,
        AGENT_RULE_SHEET_END,
        expected_rule_sheet_text(),
        "rule-sheet",
    )

    return content


def distribute_agent_injections() -> int:
    """Rewrite every routed agent's injection blocks (baseline +
    reviewer-discipline where applicable) to match SSOT. Returns the
    number of files actually rewritten (idempotent — no-op if already
    in sync).
    """
    written = 0
    for agent_rel in AGENT_BASELINE_TARGETS:
        dst = ROOT / agent_rel
        if not dst.is_file():
            raise FileNotFoundError(f"agent missing: code-toolkit/{agent_rel}")
        rebuilt = expected_agent_text(agent_rel)
        current = dst.read_text(encoding="utf-8")
        if rebuilt != current:
            dst.write_text(rebuilt, encoding="utf-8")
            written += 1
            tags = ["baseline"]
            if agent_rel in AGENT_REVIEWER_DISCIPLINE_TARGETS:
                tags.append("reviewer-discipline")
            if agent_rel in AGENT_RULE_SHEET_TARGETS:
                tags.append("rule-sheet")
            print(
                f"[deploy-agent-injections] code-toolkit/{agent_rel} "
                f"({' + '.join(tags)})"
            )
    return written


def main() -> int:
    if not CODE_TEAM_ROOT.is_dir():
        print(
            f"ERROR: code-team canonical root not found: "
            f"{CODE_TEAM_ROOT.relative_to(REPO_ROOT)}",
            file=sys.stderr,
        )
        return 2
    try:
        n = distribute()
        b = distribute_agent_injections()
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    print(
        f"\nOK: deployed {n} functional copies from code-team "
        f"+ synced injection blocks into {b} agent file(s) "
        f"(of {len(AGENT_BASELINE_TARGETS)} routed; "
        f"reviewer-discipline applies to {len(AGENT_REVIEWER_DISCIPLINE_TARGETS)} reviewers; "
        f"rule-sheet applies to {len(AGENT_RULE_SHEET_TARGETS)} agents)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
