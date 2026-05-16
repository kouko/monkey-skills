# Protocol — iterative-search

Step 2 of the `legal-research` pipeline. **Single-round** Agent loop
body: read `state.json` → check stop conditions → pick next
keyword/site → WebFetch → parse 0-N source candidates → append to
state → write `state.json` → EXIT. The LLM (Claude Code workflow)
re-invokes this protocol once per iteration; `state.json` is the only
persistent state between iterations.

## Inputs

- `<session-dir>/state.json` — loop checkpoint (must exist and be
  parseable; written initially by `protocols/plan.md` Step 1)
- `<session-dir>/plan.md` — search plan with `§關鍵字` (≥ 3 keywords)
  and `§目標 site` (≥ 2 target sites) lists
- `references/webfetch-targets.md` — site URL patterns + fallback
  chain (Google cache → archive.org Wayback) + crawl etiquette

Session dir: `<cwd>/legal-outputs/<YYYY-MM-DD-HHmm>-research-<topic>/`.

## Outputs

Updated `<session-dir>/state.json`. One of three terminal shapes per
invocation:

1. **forced_stop=true** — cap reached OR exhaustion; EXIT to
   `protocols/triangulate.md`
2. **early_stop=true** — coverage met (≥ 8 sources + ≥ 2 types); EXIT
   to `protocols/triangulate.md`
3. **Neither flag set, counters incremented** — EXIT (controller
   workflow re-invokes this protocol)

Sources are **append-only**: never mutate a previously-recorded
source. To revise a source's classification or relevance, append a
new entry and mark the old with `superseded_by: <new url_or_cite>`.

## Stop condition check

Evaluated in this order at the top of every invocation. The **first**
matching row fires; do not evaluate later rows.

| # | Condition | Action |
|---|---|---|
| 1 | `state.rounds >= 5` | set `forced_stop = true`, update `updated_at`, save, EXIT |
| 2 | `state.fetches >= 30` | set `forced_stop = true`, update `updated_at`, save, EXIT |
| 3 | `len(state.sources) >= 8` AND `len(state.types_covered) >= 2` | set `early_stop = true`, update `updated_at`, save, EXIT |
| 4 | All `(keyword × site)` combinations in plan exhausted | set `forced_stop = true`, append note `"計畫關鍵字+site 組合已用盡"` to state, save, EXIT |
| 5 | Otherwise | continue to **Procedure** |

The cap parameters (`5` rounds / `30` fetches / `8` sources / `2`
types) are mirrored verbatim from
`assets/triangulation-config.json` — do **not** hardcode different
values here; if config changes, this protocol changes in the same
commit.

## Procedure

1. **Read `state.json`**. If file missing or JSON unparseable → halt
   + ask (see Halt + ask fallback).
2. **Check stop conditions** per table above. If any of rows 1-4
   fires → write `state.json` with the appropriate flag/note + fresh
   `updated_at` (ISO 8601, e.g. `2026-05-15T14:32:18+08:00`) → EXIT.
3. **Pick next (keyword × site) pair**:
   - Source the candidate space from `plan.md` `§關鍵字` (list of
     keywords) and `§目標 site` (list of target sites)
   - Compute the attempted set from `state.sources[*].captured_at`
     plus an optional `state.attempted_pairs` field if present;
     prefer maintaining `state.attempted_pairs: ["<kw>|<site>", ...]`
     for explicit tracking
   - Choose the lexicographically-first un-attempted pair (stable
     ordering is required for reproducibility)
   - If no un-attempted pair remains → row 4 of stop table fires
     retroactively → mark `forced_stop = true` + exhaustion note → save → EXIT
4. **Construct fetch URL** — fill the site's URL pattern with the
   keyword per `references/webfetch-targets.md`. Examples:
   - `law.moj.gov.tw/LawClass/LawAll.aspx?pcode=<法典code>` (條文 lookup)
   - `judicial.gov.tw/FJUD/default.aspx` + keyword query (判決 search)
   - `mojlaw.moj.gov.tw/LawSearch.aspx?Type=L` + keyword (函釋)
   - `pdpc.gov.tw` (個資 函釋 / 公告)
5. **Call WebFetch** (Claude Code tool) on the constructed URL.
   Declare User-Agent `legal-toolkit/0.5.2 (Claude Code; in-house TW
   legal research)` per SKILL.md §WebFetch crawl etiquette.
6. **Apply fallback chain on failure** — see WebFetch fallback chain
   table below.
7. **Per source candidate extracted from the fetched content**:
   - Classify type per §Source classification rules (條文 / 判決 /
     函釋 / 學說)
   - Capture: `url_or_cite` (canonical reference string) +
     `relevance_snippet` (1-line excerpt, ≤ 200 字, verbatim or
     light paraphrase) + `captured_at` (ISO 8601)
   - Append to `state.sources` (do **not** dedupe destructively; if a
     URL already exists in sources, skip re-append and continue)
   - Increment the corresponding key in `state.types_covered`
     (`{"判決": 3, "條文": 1}` shape)
8. **Update counters**: `state.rounds += 1`; `state.fetches +=
   <actual fetch count this round>` (1 for primary success, 2 if
   one fallback hop, 3 if two fallback hops; minimum 1 even on total
   failure to prevent infinite loop).
9. **Append the attempted pair** to `state.attempted_pairs` (create
   field if absent).
10. **Update `state.updated_at`** to current ISO 8601.
11. **Save `state.json`** atomically (write to temp + rename, or use
    a single write — implementation-dependent; the LLM-controller
    just needs the final disk state to be valid JSON).
12. **EXIT**. Do **not** loop here; the SKILL.md workflow calls this
    protocol again until a stop condition fires.

## WebFetch fallback chain

Applied when the primary URL fetch fails. Each row is tried in order;
move to the next row only when the previous one fails or returns
unusable content (empty / login wall / 403 / 429 / 5xx / total
timeout). **Each hop counts as a separate fetch** for budget purposes.

| # | Source | URL pattern | When |
|---|---|---|---|
| 1 | **Primary target site** | `<target_site_pattern>` filled with keyword | First attempt |
| 2 | **Google cache** | `https://www.google.com/search?q=cache:<URL>` | Primary returns 403 / 429 / anti-bot / empty |
| 3 | **archive.org Wayback** | `https://web.archive.org/web/*/<URL>` (newest snapshot) | Google cache also fails or is stale |
| 4 | **Log + advance** | (no fetch) — append entry to `state.sources` with `type: "unreachable"` + `url_or_cite: <primary URL>` + `relevance_snippet: "primary + 2 fallbacks failed"` | All three fail |

After row 4, **increment `fetches`** as if the hops succeeded (3
fetches consumed) and **increment `rounds` by 1**, then save +
EXIT — do not retry the same (keyword × site) pair on the next
invocation; advance.

Optional: record the unreachable URL in `state.throttled_sites` (a
custom array) so future invocations skip the site entirely if it has
failed ≥ 2 times. This is an optimization, not a requirement.

## Source classification rules

Applied per source candidate extracted from a successful fetch. Use
the URL host + path as the **primary** signal; fall back to content
inspection only if URL is ambiguous (e.g. archive.org Wayback
snapshot of an unknown source).

| 法源類型 | URL / content signal |
|---|---|
| **條文** | URL host = `law.moj.gov.tw` AND path contains `LawClass` (全國法規 statute pages); fallback: content contains `第 <N> 條` header pattern AND is the canonical statute body |
| **判決** | URL host = `judicial.gov.tw` AND path contains `FJUD`; OR content matches 判決字號 regex (e.g. `[北中南高最]院 \d+ 年度 [^\s]+ 字第 \d+ 號 判決`) |
| **函釋** | URL host ∈ {`mojlaw.moj.gov.tw`, `pdpc.gov.tw`, `moea.gov.tw` subdomains for 主管機關 函釋}; OR content title contains `函釋` / `解釋令` / `<機關> 函`; OR explicit 函釋 字號 format (`<機關> <日期> <文號>`) |
| **學說** | Journal-article landing pages (e.g. `airitilibrary.com` / `ndltd.ncl.edu.tw` / university press domains) OR textbook / 月旦法學 / 政大法學評論 citation pattern in content. **Rare via WebFetch** — most 學說 sources are paywalled or PDF-only; if no machine-classifiable signal, set `type: "學說"` only with explicit author + 期刊 + 卷期 cite in the snippet, otherwise omit |
| (fallback) | If no rule fires confidently, set `type: "未分類"` and add the source to sources but do **not** count it in `types_covered`. Triangulate step ignores `未分類`. |

Classification is **best-effort** at fetch time — the triangulation
step (`protocols/triangulate.md`) may re-cluster based on richer
content inspection. Do not block on uncertain classification; record
your best guess + the snippet, and let triangulation refine.

## Halt + ask fallback

Halt and ask the user (do **not** write to `state.json` beyond a
diagnostic note) if **any**:

1. **`state.json` missing** at `<session-dir>/state.json`. Ask:
   「`state.json` 不存在於 `<session-dir>/`，無法繼續搜尋。請先執行
   `protocols/plan.md` 產生 `plan.md` + `state.json` 後再嘗試。」
2. **`state.json` unparseable** (JSON syntax error / required field
   missing per `assets/state-schema.json`). Quote the parse error.
   Ask: 「`state.json` 解析失敗：『<error message>』。建議刪除整個
   session 目錄重新跑 `protocols/plan.md`，或手動修正後重試。」
3. **`plan.md` missing or has empty `§關鍵字` / `§目標 site` lists**.
   Ask: 「`plan.md` 缺少關鍵字或目標 site；無法挑選下一個搜尋。請
   重新執行 `protocols/plan.md` 或手動補上。」

Halt is **not** a failure — once the user resolves the precondition,
the LLM re-invokes this protocol. Exhaustion (row 4 of the stop
table) is **not** a halt; it is a normal `forced_stop` exit that
proceeds to `protocols/triangulate.md`.

## Worked example

**state.json before** (mid-loop, 3rd invocation):

```json
{
  "rounds": 2,
  "fetches": 5,
  "sources": [
    {"url_or_cite": "https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=B0000001", "type": "條文", "captured_at": "2026-05-15T14:20:01+08:00", "relevance_snippet": "民法 §227 不完全給付：因可歸責於債務人之事由，致為不完全給付者..."},
    {"url_or_cite": "最高法院 109 年度 台上字第 2345 號 判決", "type": "判決", "captured_at": "2026-05-15T14:22:14+08:00", "relevance_snippet": "..."},
    {"url_or_cite": "最高法院 110 年度 台上字第 0871 號 判決", "type": "判決", "captured_at": "2026-05-15T14:25:33+08:00", "relevance_snippet": "..."}
  ],
  "types_covered": {"條文": 1, "判決": 2},
  "early_stop": false,
  "forced_stop": false,
  "attempted_pairs": ["不完全給付|law.moj.gov.tw", "carve-out|judicial.gov.tw", "民國 110 年|judicial.gov.tw"],
  "started_at": "2026-05-15T14:18:00+08:00",
  "updated_at": "2026-05-15T14:25:35+08:00"
}
```

**Stop check**: rounds=2 (< 5), fetches=5 (< 30), sources=3 (< 8) →
row 5 fires, continue.

**Pick next pair**: plan.md keywords = `[不完全給付, carve-out, 民國
110 年]`, sites = `[law.moj.gov.tw, judicial.gov.tw, mojlaw.moj.gov.tw]`.
Cartesian product has 9 pairs; 3 attempted; next un-attempted pair
(lex-first): `carve-out|mojlaw.moj.gov.tw`.

**Fetch URL**: `https://mojlaw.moj.gov.tw/LawSearch.aspx?Type=L`
with keyword `carve-out` (構造 per webfetch-targets.md).

**WebFetch result** (hypothetical): 1 函釋 found — 法務部 民國 108
年 法律字第 10803511230 號 函釋, about 不完全給付 carve-out 認定 in
特定契約類型.

**Classify + append**: type=`函釋`, url_or_cite=`法務部 民國 108 年
法律字第 10803511230 號 函釋`, relevance_snippet=`本部認為，於委任
契約之 carve-out 情形，仍應視個案判斷是否該當不完全給付...`,
captured_at=`2026-05-15T14:28:42+08:00`.

**state.json after**:

```json
{
  "rounds": 3,
  "fetches": 6,
  "sources": [
    ... (3 previous entries unchanged) ...,
    {"url_or_cite": "法務部 民國 108 年 法律字第 10803511230 號 函釋", "type": "函釋", "captured_at": "2026-05-15T14:28:42+08:00", "relevance_snippet": "本部認為，於委任契約之 carve-out 情形，仍應視個案判斷是否該當不完全給付..."}
  ],
  "types_covered": {"條文": 1, "判決": 2, "函釋": 1},
  "early_stop": false,
  "forced_stop": false,
  "attempted_pairs": ["不完全給付|law.moj.gov.tw", "carve-out|judicial.gov.tw", "民國 110 年|judicial.gov.tw", "carve-out|mojlaw.moj.gov.tw"],
  "started_at": "2026-05-15T14:18:00+08:00",
  "updated_at": "2026-05-15T14:28:45+08:00"
}
```

EXIT. SKILL.md workflow re-invokes this protocol; next iteration's
stop check sees rounds=3 + sources=4 + types=3 → still continues
(needs sources ≥ 8 for early_stop). Loop proceeds until cap or
coverage met.
