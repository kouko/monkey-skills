#!/usr/bin/env python3
"""Recompute the loom admission-rule mechanism population (concept-model
§11, spec REQ-7) and diff it against docs/loom/evidence/mechanisms.yaml.

Five classes are recomputed straight from repo state: skill, checker-rule,
hook, contract, prose-gate (see mechanisms.yaml's `counting:` field for the
prose paragraph — this module is its executable twin and must not drift
from it). A sixth class, host-hygiene, is declared but never recomputed and
never counted toward the net total -- and, because that is an exemption, it
is spendable only on the ids in HOST_HYGIENE_ALLOWLIST.

Red conditions (class-scoped: R1/R2 compare a mechanism's id within its
declared class, not across classes):
  R0 unknown-class — a mechanism's `class:` is not one of ALL_CLASSES, or it
                      claims `host-hygiene` without being on
                      HOST_HYGIENE_ALLOWLIST (which also leaves it counted
                      and R1-visible: the class launders nothing).
  R1 unregistered  — a recomputed id (for class X) is not registered in the
                      yaml under class X.
  R2 stale         — a yaml id registered under class X was not found by
                      X's recompute; a host-hygiene id must be found in the
                      hook or skill recompute, else it is stale too.
  R3 budget        — the net count rose over --baseline and the CHANGELOG
                      section headed `## [<version>]` / `## <version>`
                      carries no `budget-exception: <mechanism-id> —
                      <reason>` line (no matching section at all is also
                      red, distinctly, and never falls back to a whole-file
                      scan).
  R4 missing-eval   — a mechanism's `eval:` is empty; or points at a path
                      (before `::`) or `cold-read: <path>` that does not
                      exist on disk; or is a bare path that is neither a test
                      file (`test_*.py`, `*.sh` under tests/) nor a
                      `cold-read:` evidence file; or names a `::<node>` that
                      the file does not define and pytest does not collect.
                      An eval that cannot fail is not an eval.
  R4-pending        — a mechanism's `eval:` is the literal
                      `pending — <plan task id>` form: accepted syntax, but
                      always printed red so it is never silently green.
  R5 counting-drift — mechanisms.yaml carries no `counting:` paragraph, or
                      that paragraph does not name every class this module
                      knows: the prose twin has drifted from the code.

`--measure` fails closed: a missing session-start hook, a missing
`session-start-baseline: <sha> <words>` line, or a baseline number its own
sha does not reproduce are each red.

Exit codes: 0 clean, 1 any red finding, 2 internal error (fail-closed).

Usage:
    check_mechanisms.py [--repo PATH] [--baseline REF] [--changelog PATH]
                         [--version X.Y.Z] [--measure]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import yaml

PLUGINS = ("loom-code", "loom-design", "loom-workflow")
RECOMPUTED_CLASSES = ("skill", "checker-rule", "hook", "contract", "prose-gate")
ALL_CLASSES = RECOMPUTED_CLASSES + ("host-hygiene",)

GATE_MARKER_RE = re.compile(r"<!--\s*gate:\s*([A-Za-z0-9._-]+)\s*-->")
BUDGET_EXCEPTION_RE = re.compile(r"budget-exception:\s*(\S+)\s*—\s*(.+)")
QUOTED_TOKEN_RE = re.compile(r'"([^"]+)"|(\S+)')
PENDING_RE = re.compile(r"^pending\s*—\s*(\S.*)$")

# `class: host-hygiene` buys an exemption from the net count and from R1's
# registration gap, so it is spendable only on the named host-infrastructure
# mechanisms -- otherwise any new mechanism launders itself through it (W3
# adversary P10). An id qualifies when one of these names appears in it.
HOST_HYGIENE_ALLOWLIST = ("language-anchor", "lang_detect")

# An eval only earns its name if it can fail. A bare path must be a test
# file (or a `cold-read:` evidence file, handled separately); a `<path>::
# <node>` eval must name a node that file actually defines (W3 adversary
# P02/P12).
TEST_FILE_RE = re.compile(r"(?:^|/)test_[^/]+\.py$")
SHELL_TEST_RE = re.compile(r"(?:^|/)tests/[^/]+\.sh$")
DEF_RE = "(?m)^\\s*(?:async\\s+)?(?:def|class)\\s+{}\\b"


# --------------------------------------------------------------------------
# Manifest / mechanisms.yaml loading
# --------------------------------------------------------------------------

def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_manifest(repo: Path) -> dict:
    path = repo / "loom-code" / "contract" / "manifest.yaml"
    if not path.is_file():
        return {}
    return _load_yaml(path)


def load_mechanisms(repo: Path) -> list[dict]:
    path = repo / "docs" / "loom" / "evidence" / "mechanisms.yaml"
    if not path.is_file():
        return []
    data = _load_yaml(path)
    return list(data.get("mechanisms") or [])


def load_mechanisms_doc(repo: Path) -> dict:
    path = repo / "docs" / "loom" / "evidence" / "mechanisms.yaml"
    if not path.is_file():
        return {}
    return _load_yaml(path)


def _standalone_tool_names(manifest: dict) -> set[str]:
    return {t["name"] for t in manifest.get("tools", []) if t.get("standalone")}


def host_hygiene_allowed(mechanism_id: str) -> bool:
    """True when this id is one of the named host-infrastructure mechanisms
    `class: host-hygiene` exists for."""
    return any(name in mechanism_id for name in HOST_HYGIENE_ALLOWLIST)


def counting_classes(counting: str | None) -> set[str]:
    """The class names the `counting:` paragraph names, as whole words."""
    text = counting or ""
    found = set()
    for cls in ALL_CLASSES:
        if re.search(rf"(?<![\w-]){re.escape(cls)}(?![\w-])", text):
            found.add(cls)
    return found


def is_test_path(relative: str) -> bool:
    return bool(TEST_FILE_RE.search(relative) or SHELL_TEST_RE.search(relative))


def node_is_alive(repo: Path, relative: str, node: str) -> bool:
    """Does `<relative>::<node>` name something that exists?

    Cheap first: the file defines a `def`/`class` for every segment of the
    node id, or carries the node text verbatim. Only when that fails do we
    pay for `pytest --collect-only -q`, which is the authority."""
    try:
        text = (repo / relative).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    segments = [s for s in node.split("::") if s.strip()]
    if segments and all(re.search(DEF_RE.format(re.escape(s)), text) for s in segments):
        return True
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", relative],
        cwd=repo, capture_output=True, text=True,
    )
    return any(node in line for line in proc.stdout.splitlines())


# --------------------------------------------------------------------------
# The five recomputable surfaces
# --------------------------------------------------------------------------

def recompute_skills(repo: Path) -> set[str]:
    manifest = load_manifest(repo)
    standalone = _standalone_tool_names(manifest)
    ids: set[str] = set()
    for plugin in PLUGINS:
        skills_dir = repo / plugin / "skills"
        if not skills_dir.is_dir():
            continue
        for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
            name = skill_md.parent.name
            if name in standalone:
                continue
            ids.add(name)
    return ids


def recompute_checker_rules(repo: Path) -> set[str]:
    script = repo / "loom-code" / "scripts" / "loom_checker.py"
    if not script.is_file():
        return set()
    proc = subprocess.run(
        [sys.executable, str(script), "--list-rules"],
        cwd=repo, capture_output=True, text=True, check=True,
    )
    ids: set[str] = set()
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        ids.add(line.split("\t", 1)[0].strip())
    return ids


def _command_basename(command: str) -> str:
    tokens = [a or b for a, b in QUOTED_TOKEN_RE.findall(command)]
    path_tokens = [t for t in tokens if "/" in t]
    target = path_tokens[-1] if path_tokens else (tokens[-1] if tokens else command)
    return Path(target).name


def recompute_hooks(repo: Path) -> set[str]:
    path = repo / "loom-code" / "hooks" / "hooks.json"
    if not path.is_file():
        return set()
    data = json.loads(path.read_text(encoding="utf-8"))
    ids: set[str] = set()
    for event, entries in (data.get("hooks") or {}).items():
        for entry in entries:
            matcher = entry.get("matcher", "")
            for h in entry.get("hooks", []):
                base = _command_basename(h.get("command", ""))
                ids.add(f"{event}:{matcher}:{base}")
    return ids


def recompute_contract(repo: Path) -> set[str]:
    manifest = load_manifest(repo)
    if not manifest:
        return set()
    ids: set[str] = set()
    for s in manifest.get("stations", []):
        ids.add(f"station:{s['name']}")
    for t in manifest.get("tools", []):
        if t.get("standalone"):
            continue
        ids.add(f"tool:{t['name']}")
    for a in manifest.get("actions", []):
        ids.add(f"action:{a['name']}")
    for name, schema in (manifest.get("artifacts") or {}).items():
        for f in schema.get("fields", []):
            ids.add(f"artifact:{name}.{f['name']}")
    return ids


def recompute_prose_gates(repo: Path) -> set[str]:
    ids: set[str] = set()
    globs = ("skills/**/*.md", "agents/*.md", "references/*.md")
    for plugin in PLUGINS:
        base = repo / plugin
        if not base.is_dir():
            continue
        for glob in globs:
            for path in base.glob(glob):
                text = path.read_text(encoding="utf-8", errors="replace")
                ids.update(GATE_MARKER_RE.findall(text))
    return ids


def recompute_all(repo: Path) -> dict[str, set[str]]:
    return {
        "skill": recompute_skills(repo),
        "checker-rule": recompute_checker_rules(repo),
        "hook": recompute_hooks(repo),
        "contract": recompute_contract(repo),
        "prose-gate": recompute_prose_gates(repo),
    }


# --------------------------------------------------------------------------
# Diff / checks
# --------------------------------------------------------------------------

@dataclass
class Finding:
    rule: str
    mechanism_id: str
    detail: str


@dataclass
class CheckResult:
    exit_code: int
    findings: list[Finding] = field(default_factory=list)
    summary: dict[str, tuple[int, int]] = field(default_factory=dict)  # class -> (recomputed, registered)
    net_total: int = 0
    baseline_total: int | None = None
    baseline_approx: bool = False
    host_hygiene_ids: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def net_count(mechanisms: list[dict]) -> int:
    """Everything except the allowlisted host-hygiene entries. An entry that
    claims host-hygiene without being on the allowlist still counts, so the
    class cannot be used to launder a new mechanism past the budget."""
    return sum(
        1 for m in mechanisms
        if m.get("class") != "host-hygiene"
        or not host_hygiene_allowed(str(m.get("id", "")))
    )


def run_checks(
    repo: Path,
    *,
    baseline_ref: str | None = None,
    baseline_total_override: int | None = None,
    changelog: Path | None = None,
    version: str | None = None,
) -> CheckResult:
    mechanisms = load_mechanisms(repo)
    recomputed = recompute_all(repo)

    findings: list[Finding] = []
    warnings: list[str] = []
    summary: dict[str, tuple[int, int]] = {}

    # R0: class must be one of ALL_CLASSES.
    for m in mechanisms:
        cls = m.get("class")
        mid = m.get("id", "<missing-id>")
        if cls not in ALL_CLASSES:
            findings.append(Finding("R0", mid, f"unknown class {cls!r} (must be one of {ALL_CLASSES})"))
        elif cls == "host-hygiene" and not host_hygiene_allowed(mid):
            findings.append(Finding(
                "R0", mid,
                "class host-hygiene is reserved for host infrastructure "
                f"({', '.join(HOST_HYGIENE_ALLOWLIST)}); this id is none of them, "
                "so it is an ordinary mechanism and owes a class, a net count and an eval",
            ))

    # host-hygiene ids draw from the hook/skill recompute but are registered
    # under a separate class; a *valid* host-hygiene id (one actually found
    # in that recompute) is not a hook/skill-class registration gap, so it
    # must not also trip R1 on the hook/skill class it was drawn from.
    host_hygiene_universe = recomputed["hook"] | recomputed["skill"]
    host_hygiene_ids: list[str] = [
        m["id"] for m in mechanisms
        if m.get("class") == "host-hygiene"
        and m.get("id") in host_hygiene_universe
        and host_hygiene_allowed(str(m.get("id", "")))
    ]

    # R1: a recomputed id for class X not registered in yaml under class X.
    for cls in RECOMPUTED_CLASSES:
        recomputed_ids = recomputed[cls]
        registered_ids = {m["id"] for m in mechanisms if m.get("class") == cls}
        summary[cls] = (len(recomputed_ids), len(registered_ids))
        covered_ids = registered_ids | set(host_hygiene_ids) if cls in ("hook", "skill") else registered_ids
        for mid in sorted(recomputed_ids - covered_ids):
            findings.append(Finding("R1", mid, f"class {cls}: recomputed but not registered in mechanisms.yaml"))

    # R2: a yaml id registered under class X but not found by X's recompute.
    # host-hygiene is exempt from ordinary recompute matching but its id
    # must still be found in the hook or skill recompute (real infra, just
    # outside the loom flow) — otherwise it too is red.
    for m in mechanisms:
        cls = m.get("class")
        mid = m.get("id", "<missing-id>")
        if cls not in ALL_CLASSES:
            continue  # already reported as R0
        if cls == "host-hygiene":
            if not host_hygiene_allowed(mid):
                continue  # already reported as R0
            if mid not in host_hygiene_universe:
                findings.append(Finding("R2", mid, "class host-hygiene: id not found in hook or skill recompute"))
            continue
        if mid not in recomputed[cls]:
            findings.append(Finding("R2", mid, f"class {cls}: registered but not found by recompute"))

    # R4 / R4-pending: eval must be non-empty and resolve, unless it is the
    # literal accepted-but-flagged `pending — <plan task id>` form. This runs
    # over EVERY entry regardless of class -- a host-hygiene mechanism is
    # exempt from R2's ordinary recompute match, but not from having a
    # working eval.
    for m in mechanisms:
        mid = m.get("id", "<missing-id>")
        eval_raw = (m.get("eval") or "").strip()
        if not eval_raw:
            findings.append(Finding("R4", mid, "mechanism has no eval:"))
        elif PENDING_RE.match(eval_raw):
            findings.append(Finding("R4-pending", mid, f"eval not yet landed: {eval_raw}"))
        elif eval_raw.startswith("cold-read:"):
            cold_read_path = eval_raw.split("cold-read:", 1)[1].strip()
            if not (repo / cold_read_path).is_file():
                findings.append(Finding("R4", mid, f"cold-read path does not exist: {cold_read_path}"))
        else:
            file_part, _, node = eval_raw.partition("::")
            file_part, node = file_part.strip(), node.strip()
            if not (repo / file_part).is_file():
                findings.append(Finding("R4", mid, f"eval path does not exist: {file_part}"))
            elif not is_test_path(file_part):
                findings.append(Finding(
                    "R4", mid,
                    f"eval is not a test or cold-read: {file_part} is neither a "
                    "`test_*.py` file, a `*.sh` under tests/, nor a "
                    "`cold-read: <path>` evidence file, so nothing about it can fail",
                ))
            elif node and not node_is_alive(repo, file_part, node):
                findings.append(Finding(
                    "R4", mid,
                    f"eval names a node {file_part} does not define: {node} "
                    "(not defined in the file and not collected by pytest)",
                ))

    # R5: the `counting:` paragraph is this module's prose twin. It must
    # name every class the code knows, so a paragraph that quietly invents an
    # exemption (W3 adversary P15) is red instead of merely misleading.
    counting = load_mechanisms_doc(repo).get("counting")
    if counting is None:
        findings.append(Finding(
            "R5", "<counting>",
            "mechanisms.yaml has no `counting:` paragraph; the prose twin of "
            "this module is what a reader checks the recompute against",
        ))
    else:
        named = counting_classes(counting)
        if named != set(ALL_CLASSES):
            missing = sorted(set(ALL_CLASSES) - named)
            findings.append(Finding(
                "R5", "<counting>",
                f"the `counting:` paragraph does not name every class the "
                f"recompute knows (missing: {', '.join(missing) or 'none'}); "
                "prose and code have drifted",
            ))

    net_total = net_count(mechanisms)
    baseline_total: int | None = None
    baseline_approx = False
    if baseline_total_override is not None:
        baseline_total = baseline_total_override
    elif baseline_ref is not None:
        baseline_total, baseline_approx = compute_baseline_total(repo, baseline_ref)

    if baseline_total is not None and net_total > baseline_total and baseline_approx:
        # The approximation counts SKILL.md files plus hooks.json entries at
        # the ref, which is a different population from the mechanisms.yaml
        # net count -- the ref simply had no mechanisms.yaml to read. A rise
        # between two different quantities is not a budget breach, so it is
        # said out loud and the exit code is left alone.
        warnings.append(
            f"R3 not gated: the baseline ({baseline_total}) was approximated from "
            f"SKILL.md and hooks.json at the ref because it ships no "
            f"docs/loom/evidence/mechanisms.yaml, so the rise to {net_total} "
            "compares two different populations. Re-run against a ref that "
            "carries mechanisms.yaml to gate on it."
        )
    elif baseline_total is not None and net_total > baseline_total:
        changelog_path = changelog or _default_changelog(repo)
        version_str = version or _default_version(repo)
        if not version_str:
            raise ValueError(
                f"cannot resolve plugin version for the R3 CHANGELOG check "
                f"(empty or unparseable {repo / 'loom-code' / '.claude-plugin' / 'plugin.json'})"
            )
        section = _changelog_section(changelog_path, version_str)
        if section is None:
            findings.append(Finding(
                "R3", "<net-count>",
                f"no CHANGELOG section for {version_str} in {changelog_path}",
            ))
        elif not BUDGET_EXCEPTION_RE.search(section):
            findings.append(Finding(
                "R3", "<net-count>",
                f"net mechanism count rose {baseline_total} -> {net_total} and "
                f"{changelog_path} has no `budget-exception:` line for version {version_str}",
            ))

    exit_code = 1 if findings else 0
    return CheckResult(
        exit_code=exit_code,
        findings=findings,
        summary=summary,
        net_total=net_total,
        baseline_total=baseline_total,
        baseline_approx=baseline_approx,
        host_hygiene_ids=host_hygiene_ids,
        warnings=warnings,
    )


# --------------------------------------------------------------------------
# Baseline computation
# --------------------------------------------------------------------------

def _git_show(repo: Path, ref: str, path: str) -> str | None:
    proc = subprocess.run(
        ["git", "-C", str(repo), "show", f"{ref}:{path}"],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout


def _git_ls_tree(repo: Path, ref: str) -> list[str]:
    proc = subprocess.run(
        ["git", "-C", str(repo), "ls-tree", "-r", "--name-only", ref],
        capture_output=True, text=True, check=True,
    )
    return proc.stdout.splitlines()


SKILL_MD_RE = re.compile(r"^(?:loom-code|loom-design|loom-workflow)/skills/[^/]+/SKILL\.md$")


def _count_hooks_json_entries(data: dict) -> int:
    total = 0
    for entries in (data.get("hooks") or {}).values():
        for entry in entries:
            total += len(entry.get("hooks", []))
    return total


def compute_baseline_total(repo: Path, ref: str) -> tuple[int, bool]:
    """Return (total, approximated). Prefers a mechanisms.yaml committed at
    `ref`; falls back to an approximation (SKILL.md count + hooks.json entry
    count at that ref) when none exists, printing that it did so."""
    text = _git_show(repo, ref, "docs/loom/evidence/mechanisms.yaml")
    if text is not None:
        data = yaml.safe_load(text) or {}
        mechs = data.get("mechanisms") or []
        return net_count(mechs), False

    files = _git_ls_tree(repo, ref)
    skill_count = sum(1 for f in files if SKILL_MD_RE.match(f))
    hook_count = 0
    hooks_text = _git_show(repo, ref, "loom-code/hooks/hooks.json")
    if hooks_text is not None:
        try:
            hook_count = _count_hooks_json_entries(json.loads(hooks_text))
        except (json.JSONDecodeError, TypeError):
            hook_count = 0
    return skill_count + hook_count, True


# --------------------------------------------------------------------------
# R3 changelog lookup
# --------------------------------------------------------------------------

def _default_changelog(repo: Path) -> Path:
    return repo / "loom-code" / "CHANGELOG.md"


def _default_version(repo: Path) -> str:
    plugin_json = repo / "loom-code" / ".claude-plugin" / "plugin.json"
    if plugin_json.is_file():
        try:
            return json.loads(plugin_json.read_text(encoding="utf-8")).get("version", "")
        except json.JSONDecodeError:
            return ""
    return ""


def _changelog_section(changelog: Path, version: str) -> str | None:
    """Return the text of the `## [<version>]` or `## <version>` section,
    or None when no such heading exists — R3 reads only that section, never
    a whole-file scan (F7)."""
    if not changelog.is_file():
        return None
    text = changelog.read_text(encoding="utf-8", errors="replace")
    v = re.escape(version)
    heading_re = re.compile(rf"^##\s*(?:\[{v}\]|{v}(?=\s|$))", re.MULTILINE)
    m = heading_re.search(text)
    if not m:
        return None
    next_heading = re.compile(r"^##\s", re.MULTILINE)
    nxt = next_heading.search(text, m.end())
    return text[m.end():nxt.start() if nxt else len(text)]


# --------------------------------------------------------------------------
# --measure
# --------------------------------------------------------------------------

def measure_skill_count(repo: Path) -> int:
    return len(recompute_skills(repo))


def measure_artifact_type_count(repo: Path) -> int:
    manifest = load_manifest(repo)
    return len(manifest.get("artifacts") or {})


def wc_words(data: bytes) -> int:
    """Word count the way KICKOFF-DEFAULTS records it: `LC_ALL=C wc -w`.
    Python's str.split() disagrees with wc on a handful of unicode
    separators, and the recorded baseline is the command's number, not
    Python's. `wc -w` itself disagrees with itself across locales on some
    unicode punctuation (e.g. a circled digit followed by a semicolon, as
    the session-start hook emits), so LC_ALL is pinned to C here rather
    than inherited from the caller's environment -- ASCII-whitespace
    words, identical on macOS and GNU regardless of the ambient LANG."""
    env = {**os.environ, "LC_ALL": "C"}
    proc = subprocess.run(["wc", "-w"], input=data, capture_output=True, env=env)
    return int(proc.stdout.split()[0])


def measure_session_start_words(repo: Path) -> int:
    script = repo / "loom-code" / "hooks" / "session-start"
    if not script.is_file():
        return -1
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        subprocess.run(["git", "-C", str(tmp_path), "init", "-q"], check=True, capture_output=True)
        proc = subprocess.run(
            ["bash", str(script)],
            cwd=tmp_path, input=b"", capture_output=True,
        )
        return wc_words(proc.stdout)


def recompute_baseline_words(repo: Path, sha: str) -> int | None:
    """Re-run the session-start hook AS IT WAS at `sha` and count its words.

    The recorded number is only evidence while the sha that produced it can
    still produce it (W3 adversary P11: raising the number in
    KICKOFF-DEFAULTS.md is otherwise a one-line way past the budget). The
    hook reads sibling files out of its own directory, so the whole
    `loom-code/hooks` tree is extracted at that sha, and it is run with cwd
    set to an empty git repo -- the command KICKOFF-DEFAULTS records.
    Returns None when the sha or the tree cannot be resolved."""
    with tempfile.TemporaryDirectory() as tmp:
        tree = Path(tmp) / "tree"
        tree.mkdir()
        archive = subprocess.run(
            ["git", "-C", str(repo), "archive", sha, "loom-code/hooks"],
            capture_output=True,
        )
        if archive.returncode != 0:
            return None
        untar = subprocess.run(
            ["tar", "-x", "-C", str(tree)], input=archive.stdout, capture_output=True,
        )
        script = tree / "loom-code" / "hooks" / "session-start"
        if untar.returncode != 0 or not script.is_file():
            return None
        empty = Path(tmp) / "empty"
        empty.mkdir()
        subprocess.run(["git", "-C", str(empty), "init", "-q"], check=True, capture_output=True)
        proc = subprocess.run(
            ["bash", str(script)], cwd=empty, input=b"", capture_output=True,
        )
        return wc_words(proc.stdout)


def _session_start_baseline(repo: Path) -> tuple[str, int] | None:
    path = repo / "docs" / "loom" / "KICKOFF-DEFAULTS.md"
    if not path.is_file():
        return None
    m = re.search(r"session-start-baseline:\s*(\S+)\s+(\d+)", path.read_text(encoding="utf-8"))
    if not m:
        return None
    return m.group(1), int(m.group(2))


def run_measure(repo: Path) -> int:
    """Every measurement fails closed: a budget whose evidence is missing is
    not a budget that passed (W3 adversary P04)."""
    skill_count = measure_skill_count(repo)
    artifact_types = measure_artifact_type_count(repo)
    words = measure_session_start_words(repo)

    print(f"skill count (counted): {skill_count}")
    print(f"artifact-type count (manifest): {artifact_types}")
    if skill_count > 18:
        print(f"RED: skill count {skill_count} exceeds the loom budget of 18")
    if artifact_types > 5:
        print(f"RED: artifact-type count {artifact_types} exceeds the per-change budget of 5")
    print(f"session-start word count: {words}")

    exit_code = 1 if (skill_count > 18 or artifact_types > 5) else 0
    if words < 0:
        print("RED: no loom-code/hooks/session-start to measure; the injection "
              "budget cannot be recomputed")
        return 1

    baseline = _session_start_baseline(repo)
    if baseline is None:
        print("RED: docs/loom/KICKOFF-DEFAULTS.md records no "
              "`session-start-baseline: <sha> <words>` line, so there is "
              "nothing to measure against")
        return 1

    sha, baseline_words = baseline
    print(f"session-start-baseline ({sha}): {baseline_words} words")
    recomputed = recompute_baseline_words(repo, sha)
    if recomputed is None:
        print(f"RED: cannot recompute the baseline from sha {sha}: no "
              "loom-code/hooks tree resolves there")
        return 1
    if recomputed != baseline_words:
        print(f"RED: baseline number does not match sha {sha}: it prints "
              f"{recomputed} words, not the recorded {baseline_words}")
        return 1
    print(f"baseline recomputed from {sha}: {recomputed} words (matches)")

    half = baseline_words / 2
    if words > baseline_words:
        print(f"RED: session-start word count {words} exceeds baseline {baseline_words}")
        exit_code = 1
    elif words <= half:
        print(f"info: session-start word count {words} is at or under half the baseline target ({half:.0f})")
    else:
        print(f"info: session-start word count {words} is under baseline but over half target ({half:.0f})")
    return exit_code


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _print_summary(result: CheckResult) -> None:
    print(f"{'class':<14} {'recomputed':>10} {'registered':>10}")
    for cls in RECOMPUTED_CLASSES:
        recomputed_n, registered_n = result.summary.get(cls, (0, 0))
        print(f"{cls:<14} {recomputed_n:>10} {registered_n:>10}")
    print(f"net mechanism count (excl. host-hygiene): {result.net_total}")
    if result.baseline_total is not None:
        approx = " (approximated)" if result.baseline_approx else ""
        print(f"baseline net count: {result.baseline_total}{approx}")
    for mid in result.host_hygiene_ids:
        print(f"exempt from net count: {mid}")
    for warning in result.warnings:
        print(f"WARN {warning}")
    if result.findings:
        print()
        for f in result.findings:
            print(f"RED [{f.rule}] {f.mechanism_id}: {f.detail}")
    else:
        print("all clear")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).parents[2])
    parser.add_argument("--baseline", dest="baseline_ref", default=None)
    parser.add_argument("--changelog", type=Path, default=None)
    parser.add_argument("--version", default=None)
    parser.add_argument("--measure", action="store_true")
    args = parser.parse_args(argv)

    try:
        repo = args.repo.resolve()
        if args.measure:
            return run_measure(repo)
        result = run_checks(
            repo,
            baseline_ref=args.baseline_ref,
            changelog=args.changelog,
            version=args.version,
        )
        _print_summary(result)
        return result.exit_code
    except Exception as exc:  # fail-closed: internal error -> exit 2
        print(f"INTERNAL ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
