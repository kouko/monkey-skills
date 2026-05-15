# Protocol — plan

Step 1 of the `legal-research` Agent loop. The LLM parses the user's
`--query=...` free-text legal lookup, emits a structured `plan.md`
search strategy (≥ 3 keywords + ≥ 2 target sites + 法源類型 plan +
budget block), initializes the deterministic `state.json` checkpoint,
prints the plan to stdout, and prompts the user `Plan OK 嗎? Y/n`
(zh-TW exact string, classify-path precedent). Plan-first 半互動 is
mandatory and non-skippable — no fetch budget burns before user
confirms.

## Inputs

- `--query="<NL string>"` — free-text legal lookup question (1-3
  lines typical), e.g. `--query="不完全給付 §227 carve-out 民國 110
  年後判決趨勢"`
- `<cwd>` — the user's invocation working directory (for output path
  resolution)
- `references/webfetch-targets.md` — target site catalogue (read-only)
- `assets/triangulation-config.json` — cap parameters (read-only)

## Outputs

- `<cwd>/legal-outputs/<YYYY-MM-DD-HHmm>-research-<topic>/plan.md` —
  structured plan document (5 sections per `assets/plan-schema.json`)
- `<cwd>/legal-outputs/<YYYY-MM-DD-HHmm>-research-<topic>/state.json` —
  initialized checkpoint
- stdout: full `plan.md` content preview + `Plan OK 嗎? Y/n` prompt

`<topic>` is a slug derived from the query (5-20 zh-TW characters or
ASCII; remove punctuation; truncate at the first §/條/判決/函釋 marker
when present). Example: query `不完全給付 §227 carve-out 民國 110 年後
判決趨勢` → slug `不完全給付-227-carve-out`.

## Procedure

**a. Parse `--query` string.** Trim whitespace; reject empty. Count
characters (UTF-8 codepoints, not bytes) for length check.

**b. Extract candidate keywords.** Scan the query for:

- **法條號碼** — `§\d+(-\d+)?` / `第\s*\d+\s*條` / 法典名 + 條號
  (e.g. `民法 §184` / `個資法 §27`)
- **判決字號** — `\d+[年]?度.+?字第\d+號` (e.g. `110 年度台上字第
  1234 號`) / Romanized 字號 fragments
- **學說用語** — 法律 noun phrases (e.g. `不完全給付` / `表見代理` /
  `善意取得`) — typically 2-4 zh-TW characters with 民/刑/商事法
  semantic weight
- **業務 詞彙** — domain modifiers (e.g. `carve-out` / `民國 110 年後`
  / `判決趨勢`) — narrow the search context

Collect ≥ 3 distinct keywords. If fewer than 3 extractable, halt + ask
user to supply additional keywords (see Halt + ask).

**c. Pick target sites** per `references/webfetch-targets.md`:

| Expected 法源類型 | Primary site | Fallback |
|---|---|---|
| 條文 | `law.moj.gov.tw` (全國法規) | canonical SoT `scripts/canonical/legal-sources.json` |
| 判決 | `judicial.gov.tw` (司法院判決系統) | Google cache → archive.org |
| 函釋 | `mojlaw.moj.gov.tw` (主管法規) / `pdpc.moj.gov.tw` (個資) / 主管機關 site | Google cache |
| 學說 | (cross-site; no single SoT) | skip if not findable; flag as `學說 coverage best-effort` |

Pick ≥ 2 target sites covering at least 2 of the planned 法源類型.

**d. Estimate 法源類型 coverage.** Based on extracted keywords:

- Pure 條文號 query (e.g. `民法 §184 構成要件`) → prioritize 條文 +
  判決 + 學說 (函釋 usually N/A for 民法 § core)
- 判決字號 / 趨勢 query (e.g. `民國 110 年後 不完全給付 carve-out 判決
  趨勢`) → prioritize 判決 + 條文 + 學說
- 主管機關 / 行政 query (e.g. `個資法 §27 適當安全措施 PDPC 函釋`) →
  prioritize 函釋 + 條文 + 判決
- 學說 reference query (e.g. `王澤鑑 不完全給付 通說`) → prioritize
  學說 + 條文 + 判決

Record the prioritized subset as `expected_source_types` in plan.md
`§法源類型 plan` (subset of `{條文, 判決, 函釋, 學說}`).

**e. Read budget config** from
`assets/triangulation-config.json`. Cap parameters MUST match SKILL.md
§Agent loop spec — `max_rounds: 5 / max_fetches: 30 /
early_stop_min_sources: 8 / early_stop_min_types: 2`. Do NOT hardcode
in plan.md; read from the file so v0.5.3 tuning patches propagate.

**f. Compose `plan.md`** with all 5 required sections (per
`assets/plan-schema.json`):

```markdown
# §問題
<1-2 sentence restatement of user query in zh-TW>

# §關鍵字
- <keyword 1 — 法條號碼>
- <keyword 2 — 判決字號 or 學說用語>
- <keyword 3 — 業務 modifier>
- ...

# §目標 site
- <site 1> — <expected 法源類型 covered>
- <site 2> — <expected 法源類型 covered>

# §法源類型 plan
- <type 1> — <priority rationale 1 行>
- <type 2> — <priority rationale 1 行>

# §Budget
- max_rounds: 5
- max_fetches: 30
- early_stop_min_sources: 8
- early_stop_min_types: 2

---

## §Disclaimer
<§6.3 boilerplate — see protocols/cite.md §6.3 Disclaimer text section>
```

**g. Initialize `state.json`.** Write the following structure to disk
(both timestamps identical at init):

```json
{
  "rounds": 0,
  "fetches": 0,
  "sources": [],
  "types_covered": {},
  "early_stop": false,
  "forced_stop": false,
  "started_at": "<ISO 8601 UTC timestamp>",
  "updated_at": "<ISO 8601 UTC timestamp>"
}
```

Use `datetime.now(timezone.utc).isoformat()` form (e.g.
`2026-05-15T10:30:00+00:00`). Both `started_at` and `updated_at` are
identical at init; `updated_at` advances on every subsequent
`iterative-search.md` write.

**h. Print `plan.md` to stdout** — full content (not a summary). This
is the user's reproducibility checkpoint.

**i. Prompt user** with the exact zh-TW string `Plan OK 嗎? Y/n` (no
variations; router log matches on surface form per SKILL.md §Plan-first
contract). Wait for input.

- **Y** (or `y`) → dispatch to `protocols/iterative-search.md`
- **n** (or any non-Y) → skill exits with `plan.md` + `state.json` on
  disk; user revises query and re-invokes

## Halt + ask fallback

Trigger BEFORE writing any output file. Each halt prints the reason
in zh-TW and exits non-zero.

1. **Query length < 10 characters** (UTF-8 codepoints) →
   ```
   ❌ 查詢字串太短（< 10 字元）。請補充法條號碼、判決字號或學說用語後重試。
   範例: /legal-research --query="不完全給付 §227 carve-out 民國 110 年後判決趨勢"
   ```

2. **Zero legal terms** — no `§` / `條` / `法` / `案號` / `判例` /
   `判決` / `函釋` / `學說` markers anywhere in the query →
   ```
   ⚠️ 此查詢看起來像 fact pattern（事實情境）而非法源查詢；建議改用
   /legal-issue-spot 走 IRAC 構成要件分析。
   確定要繼續走 legal-research（純法源 lookup）嗎？(y/N)
   ```
   Default = N. If user explicitly confirms `y`, proceed; otherwise exit.

3. **Topic slug derivation fails** — query contains 0 extractable
   semantic tokens after punctuation strip (e.g. all-emoji query, or
   `?????`) →
   ```
   ❌ 無法從查詢字串擷取有效的 topic slug。請手動指定 slug:
   /legal-research --query="<NL>" --topic="<5-20 chars slug>"
   ```

In all 3 cases: do NOT create `legal-outputs/` directory yet.

## Worked example

**User invocation**:

```
/legal-research --query="不完全給付 §227 carve-out 民國 110 年後判決趨勢"
```

**Extracted keywords** (4 — exceeds min of 3):

1. `§227` (法條號碼 — 民法)
2. `不完全給付` (學說用語)
3. `carve-out` (業務 modifier — 認定例外範圍)
4. `民國 110 年後` (時間範圍 modifier — 判決趨勢)

**Target sites** (2 — exceeds min of 2):

1. `law.moj.gov.tw` — 條文 (民法 §227 全文)
2. `judicial.gov.tw` — 判決 (民國 110 年後 §227 不完全給付相關判決)

**Prioritized 法源類型**: `[判決, 條文, 學說]` (函釋 N/A for 民法 §
核心 carve-out 認定 — 主管機關 不發 函釋)

**plan.md** (written to
`<cwd>/legal-outputs/2026-05-15-1030-research-不完全給付-227-carve-out/plan.md`):

```markdown
# §問題
查詢民法 §227 不完全給付的 carve-out 認定範圍，聚焦民國 110 年後的判決趨勢。

# §關鍵字
- §227 (民法 — 不完全給付條文)
- 不完全給付 (學說用語)
- carve-out (認定例外)
- 民國 110 年後 (時間範圍)

# §目標 site
- law.moj.gov.tw — 條文 全文
- judicial.gov.tw — 民國 110 年後判決

# §法源類型 plan
- 判決 — 主軸 (民國 110 年後趨勢)
- 條文 — §227 全文 anchor
- 學說 — best-effort (王澤鑑 / 黃立 通說)

# §Budget
- max_rounds: 5
- max_fetches: 30
- early_stop_min_sources: 8
- early_stop_min_types: 2

---

## §Disclaimer
<§6.3 boilerplate>
```

**state.json** (initialized):

```json
{
  "rounds": 0,
  "fetches": 0,
  "sources": [],
  "types_covered": {},
  "early_stop": false,
  "forced_stop": false,
  "started_at": "2026-05-15T10:30:00+00:00",
  "updated_at": "2026-05-15T10:30:00+00:00"
}
```

**Stdout**: full `plan.md` content above + final line:

```
Plan OK 嗎? Y/n
```

User responds `Y` → dispatch to `protocols/iterative-search.md` Step
2 with state.json + plan.md on disk.
