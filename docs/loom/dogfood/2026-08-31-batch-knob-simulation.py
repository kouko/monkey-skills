#!/usr/bin/env python3
"""Read-only simulation: how would two "push toward batching" knobs have
changed reviewer fan-out counts across historical loom plans?

This is an ANALYSIS tool over `docs/loom/plans/*.md` files. It never writes
to any repo. Stdlib only.

Knobs simulated (see task brief for full spec):
  - fanouts_now: current reviewer fan-out (non-mechanical unbatched tasks +
    declared batches).
  - Knob (1) nudge_pairs: ordered dependency pairs A->B, same lane, file
    overlap, not already co-batched -- each is a candidate "you two could
    batch, justify why not" nudge.
  - Knob (2) fanouts_k2 / fanouts_k2_loose: connected-components clustering
    of non-mechanical tasks by (dependency edge, same lane[, file overlap]).

Tolerant parser: plan-format.md defines the strict grammar that
check_review_batches.py enforces for NEW (batch-era) plans; most plans in
this corpus predate that strictness (no Review Batches section, task IDs
that are letters/mixed like "5b"/"F3", dependency clauses with trailing
parenthetical commentary). This parser extracts what it can and records a
`parse_warnings` note per plan rather than hard-failing.
"""

from __future__ import annotations

import csv
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPOS = [
    "monkey-skills",
    "kumiko-zaiku-app-icons",
    "meeting-emo-transcriber",
    "reading-list-summarize-scraper",
    "youtube-summarize-scraper",
    "redshift-comment-mcp",
    "intellij-dbtree",
]
GITHUB_ROOT = Path("/Users/kouko/GitHub")
CAP_KS = (3, 4, 5, 6)

TASK_HEADING = re.compile(r"^##\s*Task\s+([A-Za-z0-9]+)\b[^\n]*$", re.MULTILINE)
REVIEW_BATCH_SECTION = re.compile(r"^##\s*Review Batches\s*$", re.MULTILINE)
BATCH_HEADING = re.compile(r"^###\s*Review Batch:\s*(.+?)\s*$", re.MULTILINE)
H2_HEADING = re.compile(r"^##\s+", re.MULTILINE)

# Tolerant field-line matcher: "- Field:" or "- **Field**:" (allows the
# bold-first-token form seen in a handful of plans: "- **Review-weight: prose**").
FIELD_LINE = re.compile(
    r"^\s*-\s*\*{0,2}(?P<name>[A-Za-z][A-Za-z \-]*?)\*{0,2}\s*:\s*(?P<value>.*)$"
)
MEMBERS_LINE = re.compile(
    r"^\s*-\s*\*{0,2}Members\*{0,2}\s*:\s*(?P<value>.*)$"
)

DEP_TASK_TOKEN = re.compile(r"\bTask[s]?\s+([A-Za-z0-9]+(?:\s*,\s*[A-Za-z0-9]+)*)", re.IGNORECASE)
DEP_IS_PARALLEL = re.compile(r"\bparallel\b", re.IGNORECASE)
DEP_IS_NONE = re.compile(r"^\s*none\b", re.IGNORECASE)


@dataclass
class TaskRec:
    tid: str
    lane: str  # "mechanical" | "prose" | "full"
    files: tuple[str, ...]
    deps: tuple[str, ...]  # dependency task ids (predecessors), any relation
    disposition: str  # "individual" | "batch(<id>)" | "" (absent -> individual)
    module: str  # normalized Module field value, "" if absent


@dataclass
class PlanResult:
    repo: str
    plan: str
    batch_era: bool
    tasks: int
    mechanical: int
    fanouts_now: int
    nudge_pairs: int
    fanouts_k2: int
    fanouts_k2_loose: int
    largest_component: int
    fanouts_k2_cap: dict  # {K: fanouts_k2_cap_K for K in CAP_KS}
    fanouts_a_loose_cap4: int
    fanouts_b_wave_cap4: int
    fanouts_c_module_cap4: int
    fanouts_d_strict_cap6: int
    noshare_a: int
    noshare_b: int
    noshare_c: int
    noshare_d: int
    parse_warnings: str
    # extra (not in CSV header, used for example selection in the report)
    example_edges: list = field(default_factory=list)
    example_components: list = field(default_factory=list)


def _norm_path(p: str) -> str:
    p = p.strip()
    p = p.strip("`")
    p = p.strip()
    # Drop trailing punctuation/parenthetical commentary artifacts.
    p = p.rstrip(".,;")
    return p


def _parse_files(value: str) -> tuple[str, ...]:
    """Tolerant Files touched parser: comma-separated, optionally backtick-wrapped,
    optionally followed by parenthetical commentary we ignore."""
    # Strip a trailing parenthetical note that sometimes follows the list,
    # e.g. "`a.py`, `b.py` (both new)".
    value = value.strip()
    # Split on commas that are not inside backticks/parens (good-enough: this
    # corpus doesn't nest commas inside a single path).
    parts = [p.strip() for p in value.split(",")]
    out = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        # Strip a trailing parenthetical annotation on the last token.
        m = re.match(r"^(.*?)\s*\([^)]*\)\s*$", part)
        if m and m.group(1):
            part = m.group(1).strip()
        part = _norm_path(part)
        if part and part.lower() not in {"n/a", "none"}:
            out.append(part)
    return tuple(out)


def _parse_deps(value: str) -> tuple[str, ...]:
    value = value.strip()
    if DEP_IS_NONE.match(value):
        return ()
    ids: list[str] = []
    for match in DEP_TASK_TOKEN.finditer(value):
        for tok in match.group(1).split(","):
            tok = tok.strip()
            if tok:
                ids.append(tok)
    return tuple(dict.fromkeys(ids))  # de-dup, preserve order


def _field_value(block: str, name_pattern: str) -> str | None:
    """Return the first-line value of the first field whose name matches
    `name_pattern` (case-sensitive substring match against normalized field
    name), or None if absent."""
    for line in block.splitlines():
        m = FIELD_LINE.match(line)
        if not m:
            continue
        fname = m.group("name").strip()
        if fname == name_pattern:
            return m.group("value").strip()
    return None


def _lane_of(block: str) -> str:
    raw = _field_value(block, "Review-weight")
    if raw is None:
        # Tolerate the rare "- **Review-weight: prose**" (bold wraps name+value)
        m = re.search(
            r"Review-weight\*{0,2}\s*:\s*\*{0,2}\s*(mechanical|prose|full)",
            block,
        )
        if m:
            return m.group(1)
        return "full"
    raw = raw.strip()
    for lane in ("mechanical", "prose", "full"):
        if raw.lower().startswith(lane):
            return lane
    return "full"


def _disposition_of(block: str) -> str:
    raw = _field_value(block, "Review disposition")
    if raw is None:
        return ""
    raw = raw.strip()
    m = re.match(r"^(individual|batch\([^)]*\))", raw)
    return m.group(1) if m else ""


def parse_plan(text: str):
    warnings: list[str] = []
    task_matches = list(TASK_HEADING.finditer(text))
    if not task_matches:
        warnings.append("no Task headings found")
        return [], False, warnings, []

    batch_era = bool(REVIEW_BATCH_SECTION.search(text)) or "Review disposition" in text

    # Determine end of "task region" (before ## Review Batches, if present).
    review_section = REVIEW_BATCH_SECTION.search(text)
    review_start = review_section.start() if review_section else len(text)

    tasks: list[TaskRec] = []
    seen_ids: set[str] = set()
    for i, m in enumerate(task_matches):
        tid = m.group(1)
        start = m.end()
        end = task_matches[i + 1].start() if i + 1 < len(task_matches) else len(text)
        end = min(end, review_start + 1) if review_section and m.start() < review_start else end
        block = text[start:end]

        if tid in seen_ids:
            warnings.append(f"duplicate Task {tid} heading (kept last)")
        seen_ids.add(tid)

        lane = _lane_of(block)

        files_raw = _field_value(block, "Files touched")
        if files_raw is None:
            warnings.append(f"Task {tid}: no Files touched field")
            files = ()
        else:
            files = _parse_files(files_raw)
            if not files:
                warnings.append(f"Task {tid}: Files touched present but unparseable")

        deps_raw = _field_value(block, "Dependencies")
        if deps_raw is None:
            warnings.append(f"Task {tid}: no Dependencies field (treated as none)")
            deps = ()
        else:
            deps = _parse_deps(deps_raw)

        disposition = _disposition_of(block)

        module_raw = _field_value(block, "Module")
        module = _norm_path(module_raw) if module_raw else ""

        tasks.append(
            TaskRec(tid=tid, lane=lane, files=files, deps=deps, disposition=disposition, module=module)
        )

    # Parse declared batches (member task ids), if any.
    declared_batches: list[tuple[str, tuple[str, ...]]] = []
    if review_section:
        batch_body_end_match = H2_HEADING.search(text, review_section.end())
        batch_body_end = batch_body_end_match.start() if batch_body_end_match else len(text)
        batch_body = text[review_section.end():batch_body_end]
        bh_matches = list(BATCH_HEADING.finditer(batch_body))
        for j, bm in enumerate(bh_matches):
            bid = bm.group(1).strip()
            bstart = bm.end()
            bend = bh_matches[j + 1].start() if j + 1 < len(bh_matches) else len(batch_body)
            bblock = batch_body[bstart:bend]
            members_val = None
            for line in bblock.splitlines():
                mm = MEMBERS_LINE.match(line)
                if mm:
                    members_val = mm.group("value").strip()
                    break
            member_ids: tuple[str, ...] = ()
            if members_val:
                member_ids = tuple(
                    tok.strip()
                    for tok in re.findall(r"Task\s+([A-Za-z0-9]+)", members_val)
                )
            declared_batches.append((bid, member_ids))

    # Cross-check: tasks whose disposition says batch(x) but batch section
    # missing / disagreeing is a warning, not a hard failure.
    declared_member_ids = {tid for _, members in declared_batches for tid in members}
    for t in tasks:
        if t.disposition.startswith("batch(") and t.tid not in declared_member_ids and review_section:
            warnings.append(f"Task {t.tid}: batch disposition but not listed under Review Batches")

    return tasks, batch_era, warnings, declared_batches


def compute_plan(repo: str, plan_name: str, text: str) -> PlanResult:
    tasks, batch_era, warnings, declared_batches = parse_plan(text)

    total_tasks = len(tasks)
    mechanical_n = sum(1 for t in tasks if t.lane == "mechanical")
    nonmech = [t for t in tasks if t.lane != "mechanical"]
    by_id = {t.tid: t for t in tasks}

    # --- fanouts_now ---
    # A task counts toward "declared batch" fan-out reduction if EITHER its
    # own disposition field says batch(x), OR (fallback for plans whose task
    # blocks omit the field but whose ## Review Batches section lists it,
    # or vice versa) it appears in a declared batch's Members list.
    batched_task_ids: set[str] = set()
    for t in tasks:
        if t.disposition.startswith("batch("):
            batched_task_ids.add(t.tid)
    for _, members in declared_batches:
        batched_task_ids.update(m for m in members if m in by_id)

    # Count distinct batches actually in play (declared batches that have
    # >=1 recognized member, OR distinct batch(id) tokens from disposition
    # fields when no ## Review Batches section exists).
    batch_ids_in_play: set[str] = set()
    for bid, members in declared_batches:
        if any(m in by_id for m in members):
            batch_ids_in_play.add(bid)
    for t in tasks:
        if t.disposition.startswith("batch("):
            inner = t.disposition[len("batch("):-1]
            batch_ids_in_play.add(inner)

    unbatched_nonmech = [t for t in nonmech if t.tid not in batched_task_ids]
    fanouts_now = len(unbatched_nonmech) + len(batch_ids_in_play)

    # --- knob 1: nudge pairs ---
    # ordered pairs (A -> B): B lists A in Dependencies, same lane (full/prose
    # among non-mechanical), file overlap, not already co-batched.
    def batch_of(tid: str) -> str | None:
        for bid, members in declared_batches:
            if tid in members:
                return bid
        t = by_id.get(tid)
        if t and t.disposition.startswith("batch("):
            return t.disposition[len("batch("):-1]
        return None

    nonmech_ids = {t.tid for t in nonmech}
    nudge_pairs = 0
    for b in nonmech:
        for a_id in b.deps:
            a = by_id.get(a_id)
            if a is None or a.tid not in nonmech_ids:
                continue
            if a.lane != b.lane:
                continue
            if not (set(a.files) & set(b.files)):
                continue
            if batch_of(a.tid) is not None and batch_of(a.tid) == batch_of(b.tid):
                continue
            nudge_pairs += 1

    # --- knob 2: clustering (connected components) ---
    def build_components(require_file_overlap: bool) -> tuple[int, int, dict]:
        parent = {t.tid: t.tid for t in nonmech}

        def find(x: str) -> str:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(x: str, y: str) -> None:
            rx, ry = find(x), find(y)
            if rx != ry:
                parent[rx] = ry

        edges = []
        for t in nonmech:
            for a_id in t.deps:
                a = by_id.get(a_id)
                if a is None or a.tid not in nonmech_ids:
                    continue
                if a.lane != t.lane:
                    continue
                if require_file_overlap and not (set(a.files) & set(t.files)):
                    continue
                union(a.tid, t.tid)
                edges.append((a.tid, t.tid))

        groups: dict[str, list[str]] = {}
        for t in nonmech:
            groups.setdefault(find(t.tid), []).append(t.tid)
        n_components = len(groups)
        largest = max((len(v) for v in groups.values()), default=0)
        return n_components, largest, groups

    fanouts_k2, largest_component, groups_strict = build_components(True)
    fanouts_k2_loose, _, groups_loose = build_components(False)

    def _capped_batches(members: list, K: int) -> list[list[str]]:
        """Split one connected component/group into batches of at most K
        tasks, filling in topological order (in-cluster dependency edges
        only) so a batch may only contain tasks whose in-cluster
        dependencies sit in the same or an earlier batch. Sequential
        chunking of a valid topo order satisfies that constraint by
        construction. Returns the actual batch member-lists (not just a
        count) so callers can inspect batch composition (e.g. the
        no-shared-file proxy)."""
        member_set = set(members)
        indeg = {m: 0 for m in members}
        adj: dict[str, list[str]] = {m: [] for m in members}
        for m in members:
            t = by_id[m]
            for dep_id in t.deps:
                if dep_id in member_set and dep_id != m:
                    adj[dep_id].append(m)
                    indeg[m] += 1
        # Kahn's algorithm, stable tie-break on original member order.
        order_index = {m: i for i, m in enumerate(members)}
        ready = sorted([m for m in members if indeg[m] == 0], key=lambda m: order_index[m])
        topo: list[str] = []
        indeg_work = dict(indeg)
        while ready:
            ready.sort(key=lambda m: order_index[m])
            node = ready.pop(0)
            topo.append(node)
            for nxt in adj[node]:
                indeg_work[nxt] -= 1
                if indeg_work[nxt] == 0:
                    ready.append(nxt)
        if len(topo) != len(members):
            # Cycle (shouldn't happen for a real dependency DAG) -- fall back
            # to original member order rather than dropping tasks.
            topo = list(members)
        return [topo[i:i + K] for i in range(0, len(topo), K)]

    def _batches_for_groups(groups: list, K: int) -> list[list[str]]:
        all_batches: list[list[str]] = []
        for members in groups:
            all_batches.extend(_capped_batches(members, K))
        return all_batches

    def _no_shared_file_batches(batches: list) -> int:
        """Count batches with >=2 members where NO pair shares any touched
        file -- a proxy for "semantically unrelated tasks merged". Singleton
        batches are excluded: there is no pair to be unrelated."""
        count = 0
        for batch in batches:
            if len(batch) < 2:
                continue
            filesets = [set(by_id[m].files) for m in batch]
            any_shared = any(
                filesets[i] & filesets[j]
                for i in range(len(filesets))
                for j in range(i + 1, len(filesets))
            )
            if not any_shared:
                count += 1
        return count

    fanouts_k2_cap: dict[int, int] = {}
    for K in CAP_KS:
        fanouts_k2_cap[K] = len(_batches_for_groups(list(groups_strict.values()), K))

    # --- Variant D: strict (file-gated) clustering, cap=6, for reference ---
    batches_d = _batches_for_groups(list(groups_strict.values()), 6)
    fanouts_d_strict_cap6 = len(batches_d)
    noshare_d = _no_shared_file_batches(batches_d)

    # --- Variant A: loose (dependency edge AND same lane, no file gate), cap=4 ---
    batches_a = _batches_for_groups(list(groups_loose.values()), 4)
    fanouts_a_loose_cap4 = len(batches_a)
    noshare_a = _no_shared_file_batches(batches_a)

    # --- Variant B: wave (same dependency-depth level AND same lane,
    #     regardless of edges/files -- "review each wave as one batch"), cap=4 ---
    # Depth is computed over the FULL dependency graph (any lane, any task --
    # mirrors plan-format.md's own Critical-path-depth definition), then only
    # non-mechanical tasks are bucketed by (depth, lane) for batching.
    depth_cache: dict[str, int] = {}
    visiting: set[str] = set()

    def _depth(tid: str) -> int:
        if tid in depth_cache:
            return depth_cache[tid]
        if tid in visiting:
            depth_cache[tid] = 0  # dependency cycle guard
            return 0
        visiting.add(tid)
        t = by_id.get(tid)
        preds = [d for d in t.deps if d in by_id] if t else []
        d = 1 + max((_depth(p) for p in preds), default=-1) if preds else 0
        visiting.discard(tid)
        depth_cache[tid] = d
        return d

    for t in tasks:
        _depth(t.tid)

    wave_groups: dict[tuple[int, str], list[str]] = {}
    for t in nonmech:
        wave_groups.setdefault((depth_cache[t.tid], t.lane), []).append(t.tid)
    batches_b = _batches_for_groups(list(wave_groups.values()), 4)
    fanouts_b_wave_cap4 = len(batches_b)
    noshare_b = _no_shared_file_batches(batches_b)

    # --- Variant C: same lane AND (dependency edge OR shared Module value),
    #     cap=4 (file gate replaced by Module equality) ---
    parent_c = {t.tid: t.tid for t in nonmech}

    def find_c(x: str) -> str:
        while parent_c[x] != x:
            parent_c[x] = parent_c[parent_c[x]]
            x = parent_c[x]
        return x

    def union_c(x: str, y: str) -> None:
        rx, ry = find_c(x), find_c(y)
        if rx != ry:
            parent_c[rx] = ry

    for t in nonmech:
        for a_id in t.deps:
            a = by_id.get(a_id)
            if a is None or a.tid not in nonmech_ids:
                continue
            if a.lane != t.lane:
                continue
            union_c(a.tid, t.tid)  # dependency edge, no file gate

    module_buckets: dict[tuple[str, str], list[str]] = {}
    for t in nonmech:
        if t.module:
            module_buckets.setdefault((t.lane, t.module), []).append(t.tid)
    for bucket in module_buckets.values():
        for i in range(1, len(bucket)):
            union_c(bucket[0], bucket[i])  # shared Module value, same lane

    groups_module: dict[str, list[str]] = {}
    for t in nonmech:
        groups_module.setdefault(find_c(t.tid), []).append(t.tid)
    batches_c = _batches_for_groups(list(groups_module.values()), 4)
    fanouts_c_module_cap4 = len(batches_c)
    noshare_c = _no_shared_file_batches(batches_c)

    example_components = sorted(
        [g for g in groups_strict.values() if len(g) > 1], key=len, reverse=True
    )

    return PlanResult(
        repo=repo,
        plan=plan_name,
        batch_era=batch_era,
        tasks=total_tasks,
        mechanical=mechanical_n,
        fanouts_now=fanouts_now,
        nudge_pairs=nudge_pairs,
        fanouts_k2=fanouts_k2,
        fanouts_k2_loose=fanouts_k2_loose,
        largest_component=largest_component,
        fanouts_k2_cap=fanouts_k2_cap,
        fanouts_a_loose_cap4=fanouts_a_loose_cap4,
        fanouts_b_wave_cap4=fanouts_b_wave_cap4,
        fanouts_c_module_cap4=fanouts_c_module_cap4,
        fanouts_d_strict_cap6=fanouts_d_strict_cap6,
        noshare_a=noshare_a,
        noshare_b=noshare_b,
        noshare_c=noshare_c,
        noshare_d=noshare_d,
        parse_warnings="; ".join(warnings) if warnings else "",
        example_components=example_components,
    )


def main() -> int:
    out_dir = Path(__file__).parent
    rows: list[PlanResult] = []
    skipped: list[tuple[str, str, str]] = []

    for repo in REPOS:
        plans_dir = GITHUB_ROOT / repo / "docs" / "loom" / "plans"
        if not plans_dir.is_dir():
            continue
        for path in sorted(plans_dir.glob("*.md")):
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as exc:
                skipped.append((repo, path.name, f"read error: {exc}"))
                continue
            if not TASK_HEADING.search(text):
                skipped.append((repo, path.name, "no Task headings (not a task plan)"))
                continue
            result = compute_plan(repo, path.name, text)
            if result.tasks == 0:
                skipped.append((repo, path.name, "0 tasks parsed"))
                continue
            rows.append(result)

    csv_path = out_dir / "per_plan.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "repo", "plan", "batch_era", "tasks", "mechanical",
                "fanouts_now", "nudge_pairs", "fanouts_k2", "fanouts_k2_loose",
                "largest_component",
                "fanouts_k2_cap3", "fanouts_k2_cap4", "fanouts_k2_cap5", "fanouts_k2_cap6",
                "fanouts_a_loose_cap4", "fanouts_b_wave_cap4", "fanouts_c_module_cap4", "fanouts_d_strict_cap6",
                "noshare_a", "noshare_b", "noshare_c", "noshare_d",
                "parse_warnings",
            ]
        )
        for r in rows:
            writer.writerow(
                [
                    r.repo, r.plan, r.batch_era, r.tasks, r.mechanical,
                    r.fanouts_now, r.nudge_pairs, r.fanouts_k2, r.fanouts_k2_loose,
                    r.largest_component,
                    r.fanouts_k2_cap[3], r.fanouts_k2_cap[4], r.fanouts_k2_cap[5], r.fanouts_k2_cap[6],
                    r.fanouts_a_loose_cap4, r.fanouts_b_wave_cap4, r.fanouts_c_module_cap4, r.fanouts_d_strict_cap6,
                    r.noshare_a, r.noshare_b, r.noshare_c, r.noshare_d,
                    r.parse_warnings,
                ]
            )

    print(f"Parsed {len(rows)} plans; skipped {len(skipped)}.", file=sys.stderr)
    for repo, name, reason in skipped:
        print(f"  SKIP {repo}/{name}: {reason}", file=sys.stderr)
    print(f"Wrote {csv_path}", file=sys.stderr)

    # Stash full objects (with example_components) as a pickle-free simple
    # cache for the report-generation pass, to avoid re-parsing.
    import json
    cache_path = out_dir / "_cache.json"
    cache = [
        {
            "repo": r.repo, "plan": r.plan, "batch_era": r.batch_era,
            "tasks": r.tasks, "mechanical": r.mechanical,
            "fanouts_now": r.fanouts_now, "nudge_pairs": r.nudge_pairs,
            "fanouts_k2": r.fanouts_k2, "fanouts_k2_loose": r.fanouts_k2_loose,
            "largest_component": r.largest_component,
            "fanouts_k2_cap": r.fanouts_k2_cap,
            "fanouts_a_loose_cap4": r.fanouts_a_loose_cap4,
            "fanouts_b_wave_cap4": r.fanouts_b_wave_cap4,
            "fanouts_c_module_cap4": r.fanouts_c_module_cap4,
            "fanouts_d_strict_cap6": r.fanouts_d_strict_cap6,
            "noshare_a": r.noshare_a, "noshare_b": r.noshare_b,
            "noshare_c": r.noshare_c, "noshare_d": r.noshare_d,
            "parse_warnings": r.parse_warnings,
            "example_components": r.example_components,
        }
        for r in rows
    ]
    cache_path.write_text(json.dumps({"rows": cache, "skipped": skipped}, ensure_ascii=False, indent=1))
    print(f"Wrote {cache_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
