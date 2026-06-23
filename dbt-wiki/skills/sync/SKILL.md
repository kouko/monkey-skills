---
name: sync
description: |
  One-shot update: rescan evidence then, if knowledge pages went stale, gate a redistill — bring the whole .dbt-wiki/ (evidence + semantics) current in one command. Use for 'sync dbt-wiki', 'update the wiki', 'bring wiki up to date', 'model 改了 update everything', '同步 wiki'. Cheap evidence-only→rescan; just re-distill stale→redistill; setup→init.
---

# dbt-wiki — Sync Workflow (orchestrator)

Sync is the **"just bring my wiki up to date"** path. It runs the cheap
deterministic `rescan` (evidence layer), and **if** that flags any knowledge
pages stale, it stops and asks whether to spend on a `redistill` (semantic
layer). One command, the whole two-layer update, with the expensive half gated
behind an explicit yes.

**Sync owns orchestration, not distillation.** It **delegates** to its sibling
skills and never reimplements their logic:

- evidence + stale-flagging → follow `../rescan/SKILL.md`
- LLM re-distillation → follow `../redistill/SKILL.md`

This keeps a single source of truth: rescan owns the cheap half, redistill owns
the LLM half, sync just sequences them and owns the gate between.

> Phase 1 (MVP) has **no materiality triage** — the gate fires whenever rescan
> leaves stale developing pages, even if the change was purely cosmetic
> (comment/description only). Just answer **no** at the gate for cosmetic runs.
> Phase 2 adds triage so cosmetic changes skip the gate automatically.

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
its own diff-confirm prompt (or pass its `--yes` when sync got `--yes`).

If rescan exits early (no manifest drift), there is nothing to redistill — sync
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

$PY_RUNNER <SKILL_DIR>/../redistill/assets/collect_redistill_worklist.py .dbt-wiki > /tmp/sync_worklist.json
```

If `total_selected == 0` and no `--force-mature` target exists: print "Evidence
updated; no stale developing knowledge pages to re-distill." and **exit 0** —
the cheap path was enough.

## Step 3: The gate (interactive, unless pre-answered)

Print the redistill scope table (from the work-list: domains, pages,
`skipped_mature`, fallback flag — same shape as redistill Step 2).

Then decide:

- `--no-redistill` → skip; print how to redistill later (`/dbt-wiki:redistill`)
  and **exit 0**.
- `--yes` or `--redistill` → proceed without asking.
- otherwise **ask**: *"Rescan flagged <N> knowledge page(s) across <D>
  domain(s) stale. Re-distill them now? This calls the LLM. Some may be cosmetic
  — say no to leave them flagged. (yes/no)"*
  - **no** → leave stale flags in place; print `/dbt-wiki:redistill` as the
    follow-up and **exit 0**.
  - **yes** → continue.

**Non-interactive context** (no TTY / scripted, no `--yes`/`--redistill`): treat
the gate as **no** — keep the stale flags, print the follow-up, exit 0. Never
silently spend on the LLM without an explicit yes.

## Step 4: Redistill (delegate — only on yes)

Run the redistill workflow by following `../redistill/SKILL.md` **Steps 3–7**
(skip its Step 0 pre-check and Step 1 collection — sync already did them — and
skip its Step 2 confirm, since sync's gate already confirmed; equivalently,
invoke it with `--yes`, plus any `--force-mature` sync received). Redistill does
the LLM rewrite, clears stale flags on rewritten pages, and runs reconcile +
lint_identifier_fidelity + build_index_knowledge.

## Step 5: Unified summary

```
✓ dbt-wiki sync complete.
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
