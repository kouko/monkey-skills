> Raw output of the 2026-08-06 subagent-latency scan (`scan_subagent_timing.py`), committed verbatim as the durable record referenced by `2026-08-06-subagent-latency-and-cache-research.md` §1. The scan script is appended below as the regeneration appendix.

# Subagent Execution-Time Scan — All Projects

Scanned root: /Users/kouko/.claude/projects
Files scanned: 386
Files with >=1 match: 93
Files failed to parse (skipped): 0
Total subagent-completion matches: 10054
Projects with >=1 match: 13

## Per-Project Summary (sorted by dispatch count desc)

| Project slug | dispatches | median dur (s) | p90 dur (s) | median tool_uses | median tokens | median sec/tool-call | latest activity |
|---|---|---|---|---|---|---|---|
| -Users-kouko-GitHub-monkey-skills | 5287 | 114.8 | 324.7 | 12.0 | 86168 | 10.04 | 2026-08-06 |
| -Users-kouko--supacode-repos-monkey-skills-finacial-analytics-r2 | 3048 | 157.6 | 486.6 | 14.0 | 95313 | 11.20 | 2026-08-06 |
| -Users-kouko-GitHub-kumiko-zaiku-app-icons | 512 | 494.9 | 1143.1 | 27.0 | 120234 | 18.90 | 2026-08-06 |
| -Users-kouko--supacode-repos-monkey-skills-xbrl-tw | 353 | 156.1 | 362.9 | 14.0 | 84145 | 10.74 | 2026-07-25 |
| -Users-kouko-XcodeProjects-komado-Viewfinder | 242 | 211.2 | 440.2 | 14.0 | 77900 | 13.89 | 2026-08-06 |
| -Users-kouko-kouko-obsidian-vault | 238 | 171.5 | 462.0 | 11.0 | 71330 | 15.56 | 2026-08-01 |
| -Users-kouko--supacode-repos-monkey-skills-research-skill-r2 | 212 | 92.2 | 213.8 | 9.0 | 71516 | 10.21 | 2026-07-08 |
| -Users-kouko-GitHub-meeting-emo-transcriber | 90 | 145.1 | 407.7 | 16.0 | 42952 | 8.00 | 2026-08-06 |
| -Users-kouko--supacode-repos-monkey-skills-more-visualization | 39 | 106.9 | 155.6 | 13.0 | 84138 | 6.90 | 2026-07-10 |
| -Users-kouko-GitHub-monkey-skills--worktrees-feat-digest-multiview-synthesis | 12 | 159.2 | 248.7 | 9.0 | 98958 | 17.69 | 2026-07-10 |
| -Users-kouko-DataspellProjects-iCHEF-dbt-pipeline | 9 | 102.8 | 109.0 | 8.0 | 98363 | 12.85 | 2026-07-15 |
| -private-tmp-claude-501--Users-kouko-GitHub-monkey-skills-24e60fa6-46e4-441d-98a7-94af822bc3fa-scratchpad-orch-probe | 8 | 66.1 | 77.4 | 3.0 | 49648 | 20.59 | 2026-07-30 |
| -private-tmp-claude-501--Users-kouko--supacode-repos-monkey-skills-research-skill-r2-5cec19f6-b9d6-4d26-afce-b6f35f849c3f-scratchpad-bakeoff-arm-builtin | 4 | 485.1 | 875.0 | 312.5 | 2644000 | 1.42 | 2026-07-07 |

## Global tool_uses-bucket breakdown (duration hypothesis test)

| tool_uses bucket | n | median duration (s) | p90 duration (s) | median sec/tool-call |
|---|---|---|---|---|
| 0 | 71 | 12.5 | 80.5 | nan |
| 1-5 | 1995 | 41.2 | 137.3 | 15.11 |
| 6-15 | 3886 | 107.2 | 234.4 | 9.98 |
| 16-30 | 2900 | 221.1 | 428.0 | 10.30 |
| >30 | 1202 | 472.5 | 971.0 | 11.15 |

## monkey-skills (current project, called out separately)

- dispatches: 5287
- median duration: 114.8s
- p90 duration: 324.7s

## Outlier check — median sec/tool-call, projects with >=5 dispatches (desc)

| Project slug | dispatches | median sec/tool-call | median dur (s) | median tool_uses |
|---|---|---|---|---|
| -private-tmp-claude-501--Users-kouko-GitHub-monkey-skills-24e60fa6-46e4-441d-98a7-94af822bc3fa-scratchpad-orch-probe | 8 | 20.59 | 66.1 | 3.0 |
| -Users-kouko-GitHub-kumiko-zaiku-app-icons | 512 | 18.90 | 494.9 | 27.0 |
| -Users-kouko-GitHub-monkey-skills--worktrees-feat-digest-multiview-synthesis | 12 | 17.69 | 159.2 | 9.0 |
| -Users-kouko-kouko-obsidian-vault | 238 | 15.56 | 171.5 | 11.0 |
| -Users-kouko-XcodeProjects-komado-Viewfinder | 242 | 13.89 | 211.2 | 14.0 |
| -Users-kouko-DataspellProjects-iCHEF-dbt-pipeline | 9 | 12.85 | 102.8 | 8.0 |
| -Users-kouko--supacode-repos-monkey-skills-finacial-analytics-r2 | 3048 | 11.20 | 157.6 | 14.0 |
| -Users-kouko--supacode-repos-monkey-skills-xbrl-tw | 353 | 10.74 | 156.1 | 14.0 |
| -Users-kouko--supacode-repos-monkey-skills-research-skill-r2 | 212 | 10.21 | 92.2 | 9.0 |
| -Users-kouko-GitHub-monkey-skills | 5287 | 10.04 | 114.8 | 12.0 |
| -Users-kouko-GitHub-meeting-emo-transcriber | 90 | 8.00 | 145.1 | 16.0 |
| -Users-kouko--supacode-repos-monkey-skills-more-visualization | 39 | 6.90 | 106.9 | 13.0 |

## Regeneration appendix — `scan_subagent_timing.py`

```python
#!/usr/bin/env python3
import re, os, glob, statistics, datetime, sys

PROJ_ROOT = os.path.expanduser("~/.claude/projects")
PATTERN = re.compile(
    r"<subagent_tokens>(\d+)</subagent_tokens><tool_uses>(\d+)</tool_uses><duration_ms>(\d+)</duration_ms>"
)

def pct(sorted_vals, p):
    if not sorted_vals:
        return None
    k = (len(sorted_vals) - 1) * p
    f = int(k)
    c = min(f + 1, len(sorted_vals) - 1)
    if f == c:
        return sorted_vals[f]
    d0 = sorted_vals[f] * (c - k)
    d1 = sorted_vals[c] * (k - f)
    return d0 + d1

def median(vals):
    if not vals:
        return None
    return statistics.median(vals)

def main():
    project_dirs = sorted(glob.glob(os.path.join(PROJ_ROOT, "*")))
    per_project = {}  # slug -> list of (tokens, tool_uses, duration_ms, mtime)
    files_scanned = 0
    files_with_hits = 0
    files_failed = 0
    total_matches = 0

    for pdir in project_dirs:
        if not os.path.isdir(pdir):
            continue
        slug = os.path.basename(pdir)
        jsonl_files = glob.glob(os.path.join(pdir, "*.jsonl"))
        for fpath in jsonl_files:
            files_scanned += 1
            try:
                mtime = os.path.getmtime(fpath)
                hit_in_file = False
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        for m in PATTERN.finditer(line):
                            tokens = int(m.group(1))
                            tool_uses = int(m.group(2))
                            duration_ms = int(m.group(3))
                            per_project.setdefault(slug, []).append(
                                (tokens, tool_uses, duration_ms, mtime)
                            )
                            total_matches += 1
                            hit_in_file = True
                if hit_in_file:
                    files_with_hits += 1
            except Exception as e:
                files_failed += 1
                continue

    # Build report
    lines = []
    lines.append("# Subagent Execution-Time Scan — All Projects")
    lines.append("")
    lines.append(f"Scanned root: {PROJ_ROOT}")
    lines.append(f"Files scanned: {files_scanned}")
    lines.append(f"Files with >=1 match: {files_with_hits}")
    lines.append(f"Files failed to parse (skipped): {files_failed}")
    lines.append(f"Total subagent-completion matches: {total_matches}")
    lines.append(f"Projects with >=1 match: {len(per_project)}")
    lines.append("")

    # Per-project aggregation
    rows = []
    for slug, recs in per_project.items():
        durations = sorted(r[2] for r in recs)
        tool_uses_list = sorted(r[1] for r in recs)
        tokens_list = sorted(r[0] for r in recs)
        n = len(recs)
        med_dur = median(durations)
        p90_dur = pct(durations, 0.90)
        med_tools = median(tool_uses_list)
        med_tokens = median(tokens_list)
        # seconds per tool call (median of per-record ratio, only where tool_uses>0)
        ratios = [r[2] / 1000.0 / r[1] for r in recs if r[1] > 0]
        med_sec_per_tool = median(ratios) if ratios else None
        latest_mtime = max(r[3] for r in recs)
        rows.append({
            "slug": slug,
            "n": n,
            "med_dur_ms": med_dur,
            "p90_dur_ms": p90_dur,
            "med_tool_uses": med_tools,
            "med_tokens": med_tokens,
            "med_sec_per_tool": med_sec_per_tool,
            "latest_mtime": latest_mtime,
        })

    rows.sort(key=lambda r: -r["n"])

    lines.append("## Per-Project Summary (sorted by dispatch count desc)")
    lines.append("")
    lines.append("| Project slug | dispatches | median dur (s) | p90 dur (s) | median tool_uses | median tokens | median sec/tool-call | latest activity |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for r in rows:
        latest_dt = datetime.datetime.fromtimestamp(r["latest_mtime"]).strftime("%Y-%m-%d")
        lines.append(
            f"| {r['slug']} | {r['n']} | {r['med_dur_ms']/1000:.1f} | "
            f"{(r['p90_dur_ms'] or 0)/1000:.1f} | {r['med_tool_uses']:.1f} | "
            f"{r['med_tokens']:.0f} | "
            f"{(r['med_sec_per_tool'] if r['med_sec_per_tool'] is not None else float('nan')):.2f} | "
            f"{latest_dt} |"
        )
    lines.append("")

    # Overall (all projects combined) bucket analysis by tool_uses
    all_recs = []
    for slug, recs in per_project.items():
        all_recs.extend(recs)

    buckets = [
        ("0", lambda t: t == 0),
        ("1-5", lambda t: 1 <= t <= 5),
        ("6-15", lambda t: 6 <= t <= 15),
        ("16-30", lambda t: 16 <= t <= 30),
        (">30", lambda t: t > 30),
    ]
    lines.append("## Global tool_uses-bucket breakdown (duration hypothesis test)")
    lines.append("")
    lines.append("| tool_uses bucket | n | median duration (s) | p90 duration (s) | median sec/tool-call |")
    lines.append("|---|---|---|---|---|")
    for label, pred in buckets:
        sub = [r for r in all_recs if pred(r[1])]
        if not sub:
            lines.append(f"| {label} | 0 | - | - | - |")
            continue
        durs = sorted(r[2] for r in sub)
        med = median(durs) / 1000.0
        p90 = pct(durs, 0.90) / 1000.0
        ratios = [r[2] / 1000.0 / r[1] for r in sub if r[1] > 0]
        med_ratio = median(ratios) if ratios else float('nan')
        lines.append(f"| {label} | {len(sub)} | {med:.1f} | {p90:.1f} | {med_ratio:.2f} |")
    lines.append("")

    # monkey-skills separate callout
    ms_slug = "-Users-kouko-GitHub-monkey-skills"
    if ms_slug in per_project:
        recs = per_project[ms_slug]
        durs = sorted(r[2] for r in recs)
        lines.append("## monkey-skills (current project, called out separately)")
        lines.append("")
        lines.append(f"- dispatches: {len(recs)}")
        lines.append(f"- median duration: {median(durs)/1000:.1f}s")
        lines.append(f"- p90 duration: {pct(durs,0.90)/1000:.1f}s")
        lines.append("")

    # Outlier detection: projects with n>=5, ranked by median sec/tool-call desc
    lines.append("## Outlier check — median sec/tool-call, projects with >=5 dispatches (desc)")
    lines.append("")
    lines.append("| Project slug | dispatches | median sec/tool-call | median dur (s) | median tool_uses |")
    lines.append("|---|---|---|---|---|")
    outlier_rows = [r for r in rows if r["n"] >= 5 and r["med_sec_per_tool"] is not None]
    outlier_rows.sort(key=lambda r: -r["med_sec_per_tool"])
    for r in outlier_rows:
        lines.append(
            f"| {r['slug']} | {r['n']} | {r['med_sec_per_tool']:.2f} | "
            f"{r['med_dur_ms']/1000:.1f} | {r['med_tool_uses']:.1f} |"
        )
    lines.append("")

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "subagent-timing-scan.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Wrote report to {out_path}")
    print(f"files_scanned={files_scanned} files_with_hits={files_with_hits} files_failed={files_failed} total_matches={total_matches} projects={len(per_project)}")

if __name__ == "__main__":
    main()
```
