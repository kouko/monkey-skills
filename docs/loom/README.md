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
| [`memory/`](memory/) | Practice-memory store — one distilled fact per file, the knowledge that must travel with the repo. Charter in [`memory/README.md`](memory/README.md) | build station's memory step (before the branch-end checkpoint) |
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

## checkpoint 的三個驗證角色什麼時候被觸發

盲跑者＝`blind-runner`、讀者＝`reviewer`、對抗者＝`adversary`
（另有實作者＝`implementer`）。圖中縮寫：adv／impl／blind／rev x2。
步驟整體先後排列；僅 4a／4b、5 的兩位讀者彼此並行。

```
┌───────┐   ┌─────┐   ┌──────┐   ┌────────┐   ┌───────┐   ┌────────┐
│ build │   │ adv │   │ impl │   │ review │   │ blind │   │ rev x2 │
└───┬───┘   └──┬──┘   └───┬──┘   └────┬───┘   └───┬───┘   └────┬───┘
    │          │          │           │           │            │    
    │          │          │           │           │            │    
    1 探針先寫 │          │           │           │            │    
    │──────────►                                                    
    │       2 實作        │           │           │            │    
    │─────────────────────►                                         
    │          3 checkpoint           │           │            │    
    │─────────────────────────────────►                             
    │          │       4a 補攻        │           │            │    
               ◄──────────────────────│                             
    │          │          │           │ 4b 盲跑   │            │    
                                      │───────────►                 
    │          │          │           │       5 並行讀         │    
                                      │────────────────────────►    
    │          │          │           │       6 verdict        │    
                                      ◄────────────────────────│    
    │          │          │  7 修正   │           │            │    
                          ◄───────────│                             
    │          │      8 編探針        │           │            │    
               ◄──────────────────────│                             
    │          │  9 PASS  │           │           │            │    
    ◄─────────────────────────────────│                             
```

```json
{
  "participants": [
    "build",
    "adv",
    "impl",
    "review",
    "blind",
    "rev x2"
  ],
  "messages": [
    {
      "from": "build",
      "to": "adv",
      "label": "1 探針先寫"
    },
    {
      "from": "build",
      "to": "impl",
      "label": "2 實作"
    },
    {
      "from": "build",
      "to": "review",
      "label": "3 checkpoint"
    },
    {
      "from": "review",
      "to": "adv",
      "label": "4a 補攻"
    },
    {
      "from": "review",
      "to": "blind",
      "label": "4b 盲跑"
    },
    {
      "from": "review",
      "to": "rev x2",
      "label": "5 並行讀"
    },
    {
      "from": "rev x2",
      "to": "review",
      "label": "6 verdict"
    },
    {
      "from": "review",
      "to": "impl",
      "label": "7 修正"
    },
    {
      "from": "review",
      "to": "adv",
      "label": "8 編探針"
    },
    {
      "from": "review",
      "to": "build",
      "label": "9 PASS"
    }
  ]
}
```

重生：JSON 存成 payload.json，`ascii-graph` 的 seq 生成器：
`python3 generate.py seq < payload.json`。

| 步 | 誰派誰 | 內容 | 同步性 |
|---|---|---|---|
| 1 | build→adv | 探針先寫（紅） | 完整車道 code／gate |
| 2 | build→impl | TDD、一 task 一 commit | 同波可並行 |
| 3 | build→review | 套件測試先綠 | 波尾（>8檔/400行）或分支尾 |
| 4a | review→adv | 補攻 ≥3 案例並 commit | 與 4b 同時 |
| 4b | review→blind | 逐條走 Acceptance 並 commit | 與 4a 同時 |
| 5 | review→rev x2 | 兩位讀者判讀 | 等 4a/4b 落地才派、互不可見 |
| 6 | rev x2→review | verdict 綁 sha | 不平均，一票 NEEDS 定案 |
| 7 | review→impl | 一 finding 一 commit | 不計 checkpoint 上限 |
| 8 | review→adv | 讀者 finding 編探針 | 本 intent 新增，寫並跑一次 |
| 9 | review→build | PASS，reviewed_sha→HEAD^ | 下波或 ship 再 push |

4a／4b 同樹並行時只路徑限定 commit、禁 amend；5 的兩位讀者
要等 4a／4b 的 commit 都落地才派，因為 verdict 綁 sha——探針
commit 若晚進樹，讀者就少讀一輪證據。

小車道：跳過 1、4b（Acceptance 為機械條件時），5 只派一位；
4a 不省。

## Where a new change starts

Write `docs/loom/intent/<date>-<slug>.md` (template:
`loom-code/contract/templates/intent.md`), confirm it with the user,
and hand it to the write-plan station. Everything else — the change
folder, the spec if one is needed, the plan, review.json — is created
by the stations from there.
