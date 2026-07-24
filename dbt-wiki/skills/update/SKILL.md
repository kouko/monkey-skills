---
name: update
description: |
  One-shot update: rescan evidence then, if knowledge pages went stale, gate a redistill — bring the whole .dbt-wiki/ (evidence + semantics) current in one command. Use for 'sync dbt-wiki', 'update the wiki', 'bring wiki up to date', 'model 改了 update everything', '同步 wiki'. Cheap evidence-only→rescan; just re-distill stale→redistill; setup→init.
---

# dbt-wiki — Update Workflow (orchestrator)

Update is the **"just bring my wiki up to date"** path. It runs the cheap
deterministic `rescan` (evidence layer), and **if** that flags any knowledge
pages stale, it stops and asks whether to spend on a `redistill` (semantic
layer). One command, the whole two-layer update, with the expensive half gated
behind an explicit yes.

**Update owns orchestration, not distillation.** It **delegates** to its sibling
skills and never reimplements their logic:

- evidence + stale-flagging → follow `../rescan/SKILL.md`
- LLM re-distillation → follow `../redistill/SKILL.md`

This keeps a single source of truth: rescan owns the cheap half, redistill owns
the LLM half, update just sequences them and owns the gate between.

> **Materiality triage ships** (Step 2.5): cosmetic-only stale pages
> (comment/description/whitespace changes) auto-skip the LLM gate — only
> pages whose evidence changed in *meaning* enter Step 3. Triage consumes the
> `last_rescan_materiality.json` map that rescan Step 2.6 emits; if that map is
> **absent** (a rescan from before this feature, or a first upgrade) update falls
> back to treating **all** stale pages as material (the original Phase-1
> behaviour) — it never blocks on a missing map.

## Args

- `--yes` — auto-confirm both halves (rescan diff-confirm **and** the redistill
  gate). Use for non-interactive / scripted runs.
- `--no-redistill` — run rescan only; never enter the gate (identical to running
  `/dbt-wiki:rescan` directly).
- `--redistill` — pre-answer the gate **yes** (still cheap if nothing is stale).
- `--force-mature`, `--dry-run` — passed through to redistill (Step 3).

## Step 1: Rescan (delegate — always runs, cheap)

Run the **full** rescan workflow by following `../rescan/SKILL.md` end to end
(its Steps 0–8): drift check, evidence diff/rewrite, archive removals,
regenerate index + lineage, and flag stale syntheses + knowledge pages. Honour
its own diff-confirm prompt (or pass its `--yes` when update got `--yes`).

If rescan exits early (no manifest drift), there is nothing to redistill — update
is done. Report and **exit 0**.

## Step 2: Did rescan leave stale knowledge pages?

After rescan, collect the redistill work-list deterministically (no LLM).
`<SKILL_DIR>` = the directory containing this SKILL.md; the redistill helper is
its sibling at `<SKILL_DIR>/../redistill/assets/`. Use the absolute placeholder
path, NOT a bare `../` — rescan's delegation already `cd`'d to the git repo root,
so a relative path would resolve against that, not the skill folder.

```bash
# Resolve the Python runner (same as rescan/redistill Step 0 — uv preferred)
PY_RUNNER=""
if command -v uv >/dev/null 2>&1; then PY_RUNNER="uv run";
elif python3 -c "import yaml" 2>/dev/null; then PY_RUNNER="python3";
else echo "Need uv (recommended) or pip-installed pyyaml."; exit 1; fi

$PY_RUNNER <SKILL_DIR>/../redistill/assets/collect_redistill_worklist.py .dbt-wiki > /tmp/update_worklist.json
```

If `total_selected == 0` and no `--force-mature` target exists: print "Evidence
updated; no stale developing knowledge pages to re-distill." and **exit 0** —
the cheap path was enough.

## Step 2.5: Materiality triage (split material vs cosmetic-only — 0 LLM)

The work-list from Step 2 contains every **stale** developing page. But some
went stale because their evidence changed only cosmetically (a comment /
whitespace / description edit), not in meaning — re-distilling those wastes LLM
budget. Rescan already classified each changed model in its Step 2.6 and emitted
`last_rescan_materiality.json` (`{uid: "material"|"cosmetic"}`). Roll that
per-model verdict up to a per-page verdict here, so only **material** pages enter
the gate. This is **0-LLM** — pure set comparison via the rescan helper.

`<SKILL_DIR>` = the directory containing this SKILL.md; the triage helper is its
own sibling at `<SKILL_DIR>/assets/triage_worklist.py`. Use the absolute
placeholder path, NOT a bare `../` — rescan's delegation already `cd`'d to the
git repo root, so a relative path would resolve against that, not the skill
folder.

```python
# Pseudocode — page-level materiality triage. Run via $PY_RUNNER (resolved in
# Step 2). Put the helper's dir on sys.path EXPLICITLY (don't rely on cwd —
# rescan's delegation cd'd to the git root), so `from triage_worklist import …`
# resolves no matter where this block runs. `<SKILL_DIR>` = the dir holding
# THIS SKILL.md; the helper is its sibling at `<SKILL_DIR>/assets/`.
import json, sys
from pathlib import Path
sys.path.insert(0, "<SKILL_DIR>/assets")   # so triage_worklist imports cleanly

worklist = json.loads(Path("/tmp/update_worklist.json").read_text())
groups = worklist["groups"]   # {domain: [page, ...]} from Step 2

mat_path = Path(".dbt-wiki/_internal/last_rescan_materiality.json")

if not mat_path.exists():
    # FALLBACK: rescan ran before this feature (or first upgrade) — no map.
    # Treat ALL stale pages as material (original Phase-1 behaviour). Never
    # block on a missing map. Note the fallback explicitly in the run output.
    material_groups = groups
    cosmetic_pages = []
    print("No materiality map (last_rescan_materiality.json absent) — "
          "treating all stale pages as material (fallback).")
else:
    materiality_map = json.loads(mat_path.read_text())
    from triage_worklist import triage   # <SKILL_DIR>/assets/triage_worklist.py
    partition = triage(groups, materiality_map)
    material_groups = partition["material"]   # {domain: [page, ...]}
    cosmetic_pages = partition["cosmetic"]    # flat [page, ...]

# Surface the cosmetic-only pages — they stay flagged stale, NOT re-distilled.
if cosmetic_pages:
    print(f"Skipped (cosmetic-only): {len(cosmetic_pages)} page(s) — evidence "
          f"changed only cosmetically; left flagged stale, not re-distilled.")

# Only `material_groups` flows into the Step 3 gate. Count material pages:
material_page_count = sum(len(pages) for pages in material_groups.values())
material_domain_count = len(material_groups)
```

If `material_page_count == 0` (every stale page was cosmetic-only) and no
`--force-mature` target exists: print **"Evidence updated; <N> page(s) stale but
all cosmetic — skipped (left flagged stale, not re-distilled)."** and **exit 0**.
The cheap path was enough — do NOT enter the gate, do NOT prompt, do NOT spend on
the LLM.

## Step 3: The gate (interactive, unless pre-answered)

The gate operates on the **material** partition from Step 2.5 only
(`material_groups` / `material_page_count` / `material_domain_count`) — the
cosmetic-only pages were already surfaced and skipped, and never reach here.

Print the redistill scope table for the material pages (domains, pages,
`skipped_mature`, fallback flag — same shape as redistill Step 2).

Then decide:

- `--no-redistill` → skip; print how to redistill later (`/dbt-wiki:redistill`)
  and **exit 0**.
- `--yes` or `--redistill` → proceed without asking.
- otherwise **ask**: *"Rescan flagged <material_page_count> knowledge page(s)
  across <material_domain_count> domain(s) with material evidence changes.
  Re-distill them now? This calls the LLM. (yes/no)"*
  - **no** → leave stale flags in place; print `/dbt-wiki:redistill` as the
    follow-up and **exit 0**.
  - **yes** → continue.

**Non-interactive context** (no TTY / scripted, no `--yes`/`--redistill`): treat
the gate as **no** — keep the stale flags, print the follow-up, exit 0. Never
silently spend on the LLM without an explicit yes.

## Step 4: Redistill (delegate — only on yes)

Run the redistill workflow by following `../redistill/SKILL.md` **Steps 3–7**
(skip its Step 0 pre-check and Step 1 collection — update already did them — and
skip its Step 2 confirm, since update's gate already confirmed; equivalently,
invoke it with `--yes`, plus any `--force-mature` update received). Redistill does
the LLM rewrite, clears stale flags on rewritten pages, and runs reconcile +
lint_identifier_fidelity + build_index_knowledge.

## Step 5: Unified summary

```
✓ dbt-wiki update complete.
  Rescan:    +<a> ~<m> -<r> evidence pages; <S> knowledge pages flagged stale
  Redistill: <ran: N pages across D domains | skipped (gate=no) | not needed>
  Still stale: <mature count> (use --force-mature) · <no-provenance count>
  Next: /dbt-wiki:query "<question>"  ·  /dbt-wiki:review to certify pages mature
```

## Rules

NEVER:
- Reimplement rescan or redistill logic here — always delegate by following the
  sibling SKILL.md (single source of truth).
- Enter the LLM redistill without an explicit yes (gate, `--yes`, or
  `--redistill`). Non-interactive default is **no**.
- Run `dbt parse` / `dbt compile`, or connect to a warehouse.

ALWAYS:
- Run rescan first (cheap, deterministic); it is never skipped.
- Gate the redistill on stale knowledge pages; exit cheap when there are none.
- Surface mature / no-provenance pages left still-stale in the summary.
