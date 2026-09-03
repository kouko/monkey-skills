# docs/loom/ — the loom store

Everything a loom change produces lives here. Since loom 1.0
(2026-09-03) the layout is fixed and small: a change is born as an
intent, grows a folder, and leaves evidence behind. Nothing else in
this directory is written by the stations.

## Live layout

| Entry | What it holds | Written by |
|---|---|---|
| [`intent/`](intent/) | One `<change-id>.md` per change — the entry artifact for every change, live or closed. Problem, proposed outcome, acceptance, constraints, open questions; its status line drives what the stations will accept | capture-intent (loom-design) or write-plan (loom-code) |
| `<change-id>/` | The change folder: `spec.md` (only when the change needs design), `plan.md` (the Task DAG), `review.json` (verdicts, dispatch record, probes, open findings), `evidence/` (everything a reviewer, blind runner or adversary produced for THIS change) | write-spec, write-plan, build, review |
| [`evidence/`](evidence/) | Repo-level evidence — the records that outlive one change: [`mechanisms.yaml`](evidence/mechanisms.yaml) (the mechanism inventory the recompute gate diffs against), [`attack-catalogue.md`](evidence/attack-catalogue.md) (the review station's adversarial catalogue), and the seven inherited stores `audits/`, `dogfood/`, `research/`, `references/`, `firing-corpus/`, `task-batch-review/`, `outcome-map-v3/` | review station; anyone recording a measurement |
| [`memory/`](memory/) | Practice-memory store — one distilled fact per file, the knowledge that must travel with the repo. Charter in [`memory/README.md`](memory/README.md) | ship station's memory step |
| [`maps/`](maps/) | Persistent decision maps — `MAP.md` plus tickets per run. A map that wants a slice delivered writes an intent carrying `map:`; it never owns a delivery ticket of its own | [`loom-workflow:decision-map`](../../loom-workflow/skills/decision-map/) |
| [`KICKOFF-DEFAULTS.md`](KICKOFF-DEFAULTS.md) | This repo's standing answers to the questions the stations would otherwise ask every time — second vendor, package-test command, standing-docs waiver, interface surfaces, session-start baseline. One line per key, read by `loom_checker.py` | a human, once per repo |

The artifact type of any path is decided by the mapping in the change's
concept model §6 — `docs/loom/intent/**` is an intent, `**/evidence/**`
is evidence, `docs/loom/memory/**` is memory, `docs/loom/maps/**` is a
map. That mapping is what tells the review station which of the three
verification actions (read / blind run / adversarial) a file owes.

## Frozen stores — read-only history

These are the pre-1.0 stores. loom 1.0 was a hard cutover: old plans,
specs, briefs and backlog entries were archived where they stood and
never converted. Each carries an `ARCHIVED.md` saying so. They stay in
the tree because `git log --grep` and `grep -rn` against historical
decision context is why they were kept in the first place — but no
station reads them, and nothing new should be written into them.

- [`plans/`](plans/) — writing-plans output, 2026-05-18 → 2026-09-01
- [`specs/`](specs/) — brainstorming briefs and OpenSpec-era specs
- [`backlog/`](backlog/) + [`BACKLOG.md`](BACKLOG.md) — the open-item queue store and its former generated index. Open items there are historical; a recurring one comes back as a new intent through the maintain station, not by editing the queue
- [`design/`](design/) — design documents
- [`archive/`](archive/) — closed change folders from the change-folder era
- [`2026-07-12-us-sec-primary-source-layer/`](2026-07-12-us-sec-primary-source-layer/), [`2026-07-19-8k-prose-kpi-intake/`](2026-07-19-8k-prose-kpi-intake/) — two old change folders left where they were

## Where a new change starts

Write `docs/loom/intent/<date>-<slug>.md` (template:
`loom-code/contract/templates/intent.md`), confirm it with the user,
and hand it to the write-plan station. Everything else — the change
folder, the spec if one is needed, the plan, review.json — is created
by the stations from there.
