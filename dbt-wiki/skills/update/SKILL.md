---
name: update
description: |
  THE maintenance verb for dbt-wiki — one full pass: (optional) ingest new tribal knowledge → rescan evidence → gated redistill of stale knowledge → phantom-column lint gate → review handoff → scorecard. Runs every mechanical step, then hands the human-judgment part to review. Use for 'update dbt-wiki', 'update the wiki', 'bring wiki up to date', 'maintain the wiki', 'sync dbt-wiki', 'model 改了 update everything', '同步 wiki', '更新 wiki', 'wiki 維護'. Cheap evidence-only→rescan; just re-distill stale→redistill; certify pages→review; setup→init.
---

# dbt-wiki — Update Workflow (the maintenance pass)

Update is the **"just bring my wiki up to date"** path — the single maintenance
verb. It runs **every mechanical step to completion**, then stops exactly where
human judgment starts (certifying business meaning) and hands off. One command,
the whole maintenance pass:

```
(0) ingest-front → (1) rescan → (2–4) gated redistill →
(5) phantom-column gate → (6) review handoff → (7) scorecard
```

**Update owns orchestration, not distillation.** It **delegates** to its sibling
skills and never reimplements their logic:

- new tribal knowledge → follow `../ingest/SKILL.md` (Step 0, optional)
- evidence + stale-flagging → follow `../rescan/SKILL.md` (Step 1)
- LLM re-distillation → follow `../redistill/SKILL.md` (Step 4)
- human certification → **hand off** to `/dbt-wiki:review`, never run it (Step 6)

This keeps a single source of truth: each sibling owns its half, update just
sequences them and owns the gates between. `rescan` / `redistill` stay callable
on their own — reach for them directly when you want only the cheap evidence
refresh, or only the LLM half, to save cost.

**One-way discipline**: dbt → wiki, always. Update reads `target/manifest.json`
and the compiled SQL; it never writes to `dbt/`, `target/`, or anywhere outside
`.dbt-wiki/` (+ `CLAUDE.md`), and never runs `dbt parse` / `dbt compile` or
touches a warehouse on your behalf.

> **Materiality triage ships** (Step 2.5): cosmetic-only stale pages
> (comment/description/whitespace changes) auto-skip the LLM gate — only
> pages whose evidence changed in *meaning* enter Step 4. Triage consumes the
> `last_rescan_materiality.json` map that rescan Step 2.6 emits; if that map is
> **absent** (a rescan from before this feature, or a first upgrade) update falls
> back to treating **all** stale pages as material (the original Phase-1
> behaviour) — it never blocks on a missing map.

## Args

- `--yes` — auto-confirm both halves (rescan diff-confirm **and** the redistill
  gate). Use for non-interactive / scripted runs.
- `--no-redistill` — run rescan only; never enter the gate. Steps 5–7 still run
  (they are 0-LLM).
- `--redistill` — pre-answer the gate **yes** (still cheap if nothing is stale).
- `--force-mature`, `--dry-run` — passed through to redistill (Step 4).

## Step 0: Ingest-front (optional — only when the user brought a note)

If the invocation carries new tribal knowledge that is not in the manifest
(a sort_key rationale, a dialect gotcha, an incident link — e.g. *"update the
wiki, and remember fct_orders is sorted by order_date because of the Tableau
extract"*), attach it **first**, before rescan rewrites evidence pages: run the
ingest workflow by following `../ingest/SKILL.md` end to end.

Ingest writes only the user-owned `## User Notes` section, which rescan
preserves verbatim — so ingesting first is safe and keeps the note in the same
pass.

No note in the invocation → **skip this step silently**. Do not prompt for one.

## Step 1: Rescan (delegate — always runs, cheap)

Run the **full** rescan workflow by following `../rescan/SKILL.md` end to end
(its Steps 0–8): drift check, evidence diff/rewrite, archive removals,
regenerate index + lineage, and flag stale syntheses + knowledge pages. Honour
its own diff-confirm prompt (or pass its `--yes` when update got `--yes`).

If rescan reports **no manifest drift**, there is nothing to redistill: skip
Steps 2–4 and go straight to **Step 5**. Do not exit here — the phantom gate and
the review handoff are 0-LLM and still part of the maintenance pass (pages can
sit un-certified, or cite a phantom column, with no drift at all).

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

If `total_selected == 0` and no `--force-mature` target exists: note "Evidence
updated; no stale developing knowledge pages to re-distill." and **jump to
Step 5** — the cheap path was enough for the knowledge layer, but the pass is
not over.

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
`--force-mature` target exists: note **"Evidence updated; <N> page(s) stale but
all cosmetic — skipped (left flagged stale, not re-distilled)."** and **jump to
Step 5**. Do NOT enter the gate, do NOT prompt, do NOT spend on the LLM.
This skip is **not overridable by flags** — `--yes` / `--redistill` pre-answer
the gate, they do not force cosmetic-only pages INTO it. To re-distill a
cosmetic-stale page anyway, call `/dbt-wiki:redistill` on it directly.

## Step 3: The gate (interactive, unless pre-answered)

The gate operates on the **material** partition from Step 2.5 only
(`material_groups` / `material_page_count` / `material_domain_count`) — the
cosmetic-only pages were already surfaced and skipped, and never reach here.

Print the redistill scope table for the material pages (domains, pages,
`skipped_mature`, fallback flag — same shape as redistill Step 2).

Then decide:

- `--no-redistill` → skip Step 4; note the follow-up (`/dbt-wiki:redistill`) and
  **jump to Step 5**.
- `--yes` or `--redistill` → proceed without asking.
- otherwise **ask**: *"Rescan flagged <material_page_count> knowledge page(s)
  across <material_domain_count> domain(s) with material evidence changes.
  Re-distill them now? This calls the LLM. (yes/no)"*
  - **no** → leave stale flags in place; note `/dbt-wiki:redistill` as the
    follow-up and **jump to Step 5**.
  - **yes** → continue.

**Which context am I in?** A normal chat / agent session **is interactive** —
the user is reachable, so take the "otherwise ask" branch above and actually
ask. **Non-interactive** means specifically that nobody can answer this turn:
a headless run (`claude -p`), a CI job, or a workflow/driver step. There,
with no `--yes`/`--redistill`, treat the gate as **no** — keep the stale
flags, note the follow-up, jump to Step 5. Absence of a terminal is not the
test; absence of a reachable human is. Never silently spend on the LLM
without an explicit yes.

## Step 4: Redistill (delegate — only on yes)

Run the redistill workflow by following `../redistill/SKILL.md` **Steps 3–7**
(skip its Step 0 pre-check and Step 1 collection — update already did them — and
skip its Step 2 confirm, since update's gate already confirmed; equivalently,
invoke it with `--yes`, plus any `--force-mature` update received). Redistill does
the LLM rewrite, clears stale flags on rewritten pages, and runs reconcile +
lint_identifier_fidelity + build_index_knowledge.

## Step 5: Phantom-column gate (mechanical, always runs, 0 LLM)

**Every path above converges here** — including each cheap exit in Steps 1–3.
This is the last *machine-checkable* defect class before a human is asked to
certify anything, so update always runs it, even when nothing was re-distilled.

**What it catches**: a knowledge page citing `model.column` where that model's
manifest-extracted column list has no such column (a paraphrased identifier — a
dropped `__daily` suffix, an invented prefix). Nothing looks wrong on the page;
the SQL a consumer generates from it fails **at execution**. Pages whose model
was extracted `schema_yml_only` / `failed` are reported unverifiable, never as
violations.

```bash
# $PY_RUNNER: reuse the one from Step 2, or resolve it with that same snippet
# if you jumped here from Step 1. The script is in the rebuildable cache
# (rescan Step 0 self-heals it); fall back to <SKILL_DIR>/../init/assets/ if
# .dbt-wiki/_internal/ somehow lacks it.
$PY_RUNNER .dbt-wiki/_internal/lint_identifier_fidelity.py .dbt-wiki --json \
  > /tmp/update_phantom.json
```

Exit codes: **0** = clean · **1** = phantom citations found · **2** = no
`.dbt-wiki/` at that path (cannot happen after Step 1's pre-condition — if it
does, stop and report it; do not carry on with a silent zero).

The JSON carries `refs_checked`, `evidence_models`, `refs_ok`,
`refs_unverifiable`, and `violations: [{page, ref}]`. On exit 1:

- **Do not stop the pass, and do not auto-edit pages.** Update orchestrates; the
  fix is an identifier correction that belongs to redistill or a human edit.
- Group the violations by page and surface them **above** the review handoff —
  they are a mechanical pre-requisite to certification: certifying a page that
  cites a column the model lacks certifies a query that will not run.
- Carry the per-page violation set into Step 6 so each queued page shows whether
  it is blocked, and into the Step 7 scorecard.

Fix path to state, verbatim: correct each cited identifier against the model's
evidence page `columns:` frontmatter (or re-run `/dbt-wiki:redistill` for that
page), then re-run `/dbt-wiki:update`.

## Step 6: Review handoff (present the queue — never run review)

Everything a machine can do is now done. What remains is **certifying business
meaning**, which is a human act: `/dbt-wiki:review` is deliberately a pure
human-in-the-loop skill. Update **presents the queue and stops**.

Build the queue by reading **frontmatter only** across
`.dbt-wiki/{entities,metrics,concepts}/*.md` (same criteria as review Step 1):

| Condition | Meaning |
|---|---|
| `status: developing` | Never certified — LLM-distilled, no human sign-off yet. |
| `status: mature` AND `stale: true` | Re-certification needed — its evidence changed. |

Skip `status: seed` and `status: archived`. Present a compact handoff:

```
Awaiting human certification: <Q> page(s)
  developing (first cert): <d>       stale-mature (re-cert): <s>
  blocked by phantom-column citations: <b>   ← fix these first (Step 5)

  Newly stale this run: <list of page paths, max 10, then "+N more">

  → /dbt-wiki:review   (certifies pages one at a time, with you in the loop)
```

NEVER, in this step:

- run review's Steps 2–6, rank the queue by risk, or open page bodies — that is
  review's job, and loading bodies here burns tokens twice;
- set `status: mature`, stamp `reviewed_by` / `reviewed_at`, or clear a `stale`
  flag — certification without a human is a false certification record;
- demote a page (`mature → developing`).

If the queue is empty, say so plainly: every knowledge page is certified and
not stale (or still `seed`, not yet distilled).

## Step 7: Scorecard

Close with one structured scorecard — **write it in the conversation language**
(translate the labels; keep paths, flags, identifiers and slash-commands
verbatim):

```
✓ dbt-wiki update complete.
  Ingest:      <N note(s) attached to M page(s) | none>
  Rescan:      +<a> ~<m> -<r> evidence pages · <S> knowledge pages flagged stale
  Redistill:   <N pages across D domains | skipped (gate=no) | skipped (all cosmetic: C) | not needed>
  Phantom gate: <✓ clean, R refs checked | ✗ V citation(s) across P page(s)>
  Awaiting review: <Q> page(s) (developing <d> · stale-mature <s>)
  Still stale:  <mature count> (use --force-mature) · <no-provenance count>

  Machine work is done — what's left needs a human:
    1. Fix <V> phantom-column citation(s) listed above   [omit when clean]
    2. /dbt-wiki:review — certify <Q> page(s)            [omit when queue empty]
    3. /dbt-wiki:query "<question>"
```

Every number must come from the step that produced it (rescan's diff, the
triage counts, the lint JSON, the Step 6 queue) — never estimate one, and never
print a count for a step that was skipped: write `skipped` / `not needed`.

## Rules

NEVER:
- Reimplement rescan, redistill, ingest, or review logic here — always delegate
  by following the sibling SKILL.md (single source of truth).
- Enter the LLM redistill without an explicit yes (gate, `--yes`, or
  `--redistill`). Non-interactive default is **no**.
- Auto-run `/dbt-wiki:review` or certify / demote any page — certification is a
  human action; update only presents the queue.
- Auto-edit a knowledge page to silence a phantom-column violation.
- Exit the pass after the cheap half — Steps 5–7 are 0-LLM and always run.
- Write to `dbt/` or `target/`, run `dbt parse` / `dbt compile`, or connect to a
  warehouse. dbt → wiki is one-way.

ALWAYS:
- Run rescan first (cheap, deterministic); it is never skipped.
- Gate the redistill on **material** stale knowledge pages; skip the LLM when
  there are none.
- Run the phantom-column gate before the review handoff, and surface every
  violation as a pre-certification blocker.
- End with the scorecard in the conversation language, and surface mature /
  no-provenance pages left still-stale in it.
- Point at `/dbt-wiki:rescan` or `/dbt-wiki:redistill` when the user wants only
  one half (cheaper than a full pass).
