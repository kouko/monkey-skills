# Protocol — triangulate

Step 3 of the 4-protocol pipeline. Runs **after** `iterative-search.md`
exits (`state.early_stop=true` OR `state.forced_stop=true`) and
**before** `cite.md`. Validates final triangulation coverage; on
`forced_stop`, prepares the canonical `⚠️ 覆蓋未達 triangulation` block
for `cite.md` to prepend above `§問題` in `research-memo.md`.

## Purpose

Two deterministic responsibilities (no further WebFetch):

1. **Verify final coverage** — cluster `state.sources` by 法源類型,
   apply promotion / demotion rules, compute adjusted count, persist
   to `state.json`.
2. **Prepare ⚠️ block** when `forced_stop` — render the zh-TW warning
   block (see §⚠️ block template) for `cite.md` to prepend.

This protocol does NOT modify `research-memo.md` or
`executive-summary.md` (that is `cite.md`'s job).

## Inputs

- `state.json` — must contain `sources[]`, `types_covered{}`,
  `early_stop`, `forced_stop`, `rounds`, `fetches`
- [`references/triangulation-rules.md`](../references/triangulation-rules.md)
  — 法源類型 classification + promotion / demotion logic

## Outputs

- **`state.json` updates** (in-place write):
  - `final_types_covered_count` (integer ≥ 0) — adjusted count after
    promotion / demotion
  - `triangulation_assessment` (string) — one of `"early_stop met"` /
    `"forced_stop"` / `"coverage degraded"`
- **⚠️ block markdown** — only when assessment ∈ {`forced_stop`,
  `coverage degraded`}; handed to `cite.md` for prepending.

## Procedure

1. **Read** `state.json`. Halt if missing / corrupt (see §Halt + ask).
2. **Cluster** `state.sources` by `type` (`條文 / 判決 / 函釋 / 學說 /
   未通說 / unreachable`). `unreachable` does NOT count.
3. **Apply promotion / demotion** per
   `references/triangulation-rules.md`. Walk each source; on a
   demotion trigger, re-tag `type` to `未通說` **in-memory only** (do
   NOT mutate `state.sources[]`). On a 判決→函釋 binding-cite pattern,
   count 函釋 as a separate captured type even without a standalone
   函釋 fetch.
4. **Compute** `final_types_covered_count` = distinct base types in
   the adjusted cluster (exclude `未通說` + `unreachable`).
5. **Decide** `triangulation_assessment`:
   - `state.forced_stop == true` → `"forced_stop"`
   - `state.early_stop == true` AND `final ≥ 2` AND
     `len(sources) ≥ 8` → `"early_stop met"`
   - `state.early_stop == true` AND `final < 2` →
     `"coverage degraded"`
   - Otherwise → logic bug; halt (see §Halt + ask).
6. **Write** `state.json` with the two new fields.
7. **If** assessment ∈ {`forced_stop`, `coverage degraded`} → render
   the ⚠️ block template with concrete numbers; `cite.md` reads
   `triangulation_assessment` + `final_types_covered_count` from
   `state.json` and reconstructs the same block before prepending.
8. **EXIT** to `cite.md`.

## Type promotion / demotion rules (summary)

Authoritative source:
[`references/triangulation-rules.md`](../references/triangulation-rules.md).

| Trigger | Effect on count |
|---|---|
| 判決 引用 函釋 as binding (cite-pattern in `relevance_snippet`) | 函釋 counts as separate type even without standalone source |
| 判決 > 10 years old AND ≥ 1 學說 反對 entry on same 條文 | 判決 → `未通說`; does NOT count |
| 函釋 marked 已停止適用 by 主管機關 | 函釋 → `未通說`; does NOT count |
| 學說 marked 少數說 / 異說 | 學說 → `未通說`; does NOT count |
| Source unreachable / 404 / archive miss | `unreachable`; does NOT count |
| Otherwise | Source counts toward its captured 法源類型 |

Only the four base types (條文 / 判決 / 函釋 / 學說) satisfy
`early_stop_min_types ≥ 2`.

## ⚠️ block template

Rendered when assessment ∈ {`forced_stop`, `coverage degraded`}.
Substitute `<N>` placeholders with actual `state.json` integers.

```markdown
> ⚠️ **覆蓋未達 triangulation** (forced_stop)
>
> 本研究於 cap 達到時退出 (rounds=<N>/5 或 fetches=<N>/30)，未達 early_stop 條件 (≥ 8 sources + ≥ 2 法源類型)。
>
> 實際覆蓋：<N> sources / <N> 法源類型。
>
> 建議：擴大關鍵字 + 重跑 `/legal-research --query="..."`，或諮詢執業律師補充覆蓋。
```

`cite.md` MUST **prepend** (not append) this block above `§問題`. The
GitHub-flavored blockquote renders distinctly in both Markdown viewers
and plain-text reads.

## Halt + ask fallback

Halts (do NOT proceed to `cite.md`; do NOT mutate `state.json`):

- **`state.json` missing or corrupt JSON** →
  `⚠️ triangulate halt — state.json 讀取失敗。請重跑 /legal-research。`
- **`state.sources` empty** — suspicious; cap should have prevented:
  `⚠️ triangulate halt — 搜尋零結果。建議擴大關鍵字或更換目標 site 後重跑 plan.md。`
- **`early_stop=true` BUT `len(sources) < 8` OR raw
  `len(types_covered) < 2`** — `iterative-search.md` logic bug:
  `⚠️ triangulate halt — early_stop 旗標與實際覆蓋不一致 (sources=<N> / raw types=<N>)。請回報並重跑。`
- **Neither `early_stop` nor `forced_stop` set** — premature invocation:
  `⚠️ triangulate halt — early_stop / forced_stop 均未設定；loop 尚未結束。請回到 iterative-search.md。`

## Worked example (forced_stop)

Input `state.json` (abbreviated):

```json
{
  "rounds": 5, "fetches": 18,
  "sources": [
    {"url_or_cite": "民法 §227", "type": "條文"},
    {"url_or_cite": "110台上1234", "type": "判決"},
    {"url_or_cite": "109台上567",  "type": "判決"},
    {"url_or_cite": "95台上890",   "type": "判決"},
    {"url_or_cite": "92台上111",   "type": "判決"},
    {"url_or_cite": "88台上222",   "type": "判決"}
  ],
  "types_covered": {"條文": 1, "判決": 5},
  "early_stop": false, "forced_stop": true
}
```

Execution:

1. Cluster → `{條文: 1, 判決: 5}`; raw types = 2.
2. 判決 92台上111 + 88台上222 > 10 yrs but no 學說 反對 entry → no
   demotion. No 函釋 binding-cite pattern → no promotion.
3. `final_types_covered_count = 2`.
4. `triangulation_assessment = "forced_stop"` (flag wins regardless of
   count).
5. Write `state.json` with both new fields.
6. Render block: `rounds=5/5`, `fetches=18/30`, `6 sources / 2 法源類型`.
7. Hand off to `cite.md`; it prepends the block above `§問題` and
   emits §Escalation banner in `executive-summary.md` per §6.4
   (forced_stop trigger).

Note: even with `final = 2`, `forced_stop=true` takes precedence —
the user is told 8-source coverage was NOT achieved, confidence
degraded.
