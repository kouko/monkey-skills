<!-- [draft — for 法務 review; Phase 4.5 GC outreach validation] -->

# Triangulation Rules

法源類型 classification + ∩ (intersection) coverage rules + type
promotion/demotion logic. Consumed by `protocols/triangulate.md` for
final coverage validation + `state.json.types_covered` accounting.

This file is **operational** — it encodes the decision logic for
classifying a captured source into one of 4 法源類型, deciding whether
the source counts toward `types_covered`, and deciding whether the
loop's early-stop floor has been reached.

## 1. 法源類型 (4 types — exhaustive)

| Type | Definition | Examples |
|---|---|---|
| `條文` | 中華民國現行有效法律 / 命令 / 自治條例 條文 | 民法 §184 / 個資法 §27 / 勞基法 §11 |
| `判決` | 司法院 公開 判決 (最高法院 / 高等法院 / 地方法院) | 109 台上 1234 / 110 上易 567 |
| `函釋` | 主管機關 行政函釋 / 解釋令 | 法務部 法律字第 11012345 號 / 公平會 公處字第 N 號 |
| `學說` | 教科書 / 法學期刊 / 學者論文 (僅當訓練資料或公開文獻可確認時方可採) | 王澤鑑《侵權行為法》§3.2 |

These 4 types are exhaustive for the early-stop counter. Any captured
source that does not fit one of these (or is demoted per §4) is held
in `state.sources` for audit but does NOT increment `types_covered`.

## 2. Early stop criteria

Loop exits via `early_stop=true` IFF **both** conditions hold
simultaneously:

- `len(sources) >= 8` AND
- `len(types_covered) >= 2` (distinct, non-demoted 法源 types)

Worked examples:

| Sources | types_covered | early_stop? | Why |
|---|---|---|---|
| 8 條文 | 1 | NOT | only 1 type |
| 5 條文 + 3 判決 | 2 | YES | 8 sources + 2 types |
| 4 條文 + 3 判決 + 1 函釋 | 3 | YES | 8 sources + 3 types |
| 6 條文 + 1 判決 | 2 | NOT | only 7 sources |
| 3 條文 + 3 判決 + 2 函釋 | 3 | YES | 8 sources + 3 types |
| 7 條文 + 1 學說 (demoted 少數說) | 1 | NOT | 學說 demoted; only 條文 counts |

Both floors are required because they encode independent quality
dimensions: source count (depth of evidence) and type diversity (∩
robustness — a conclusion supported by 條文 + 判決 is harder to refute
than one supported by 8 條文 alone).

## 3. Type promotion rules (separate-counting on citation chains)

When one source cites another, both count separately toward
`types_covered` provided each has its own 識別字號 + 來源 URL captured
in `state.sources`. Do NOT collapse citation chains into the citing
source's type.

- **判決 cites 函釋 as binding** — 判決 stays `type=判決`; 函釋
  separately captured as `type=函釋`. Both count.
- **學說 引用 判決 as 通說** — 學說 stays `type=學說`; 判決
  separately captured IF 學說 引用 a specific 字號 that can be
  WebFetch-verified. If 學說 merely says "依實務見解" without a
  字號, the 判決 is NOT separately captured.
- **判決 cites 學說 as 通說** — both count separately (rare; mostly
  大法官 解釋 / 憲法法庭 判決 + named 學者).
- **條文 explanation 引用 立法理由** — 立法理由 IS NOT separately
  captured as a distinct type (it is meta-data on the 條文 itself).
  Do not promote 立法理由 to 學說.

## 4. Type demotion rules (sources captured but NOT counted toward ∩ floor)

A source is **demoted** when it fails authority / currency tests. A
demoted source is still recorded in `state.sources` (for memo
§搜尋摘要 audit), but it does NOT increment `types_covered`.

- **判決 > 10 years old AND 學說 反對** → demoted to `未通說`. Age
  is measured by 判決 公告日期; "10 years" is ISO-date arithmetic
  against captured_at.
- **判決 已停止援用** — explicit signals: 大法官 解釋 推翻; 後續一致
  改判 (連續 ≥ 3 件 同審級 反向判決); 司法院 公告 不再援用 → demoted
  to `未通說`.
- **函釋 標記 已停止適用** by 主管機關 — explicit signals: 主管機關
  公告 廢止; 主管機關 發布修正版 取代; 法規 修正 致 函釋 前提 失效
  → demoted to `已廢止`.
- **學說 marked 少數說** — explicit signals: 通說 作者 (王澤鑑 / 王
  文宇 / 林誠二 等) 明確標記 「少數見解」; 教科書 章節 標題 含
  「少數說」; 期刊 編者 標註 為 異說 → demoted to `少數說`.

Demoted types live in `state.sources[i].type` as the demoted label
(e.g. `"未通說"`); the counting algorithm in §8 skips them.

## 5. ∩ pattern preferences (advisory; cite.md guidance)

`legal-research` early_stop is satisfied by ≥ 2 types. For higher
quality output (better Harvey doc-level coverage in `cite.md`),
prefer ≥ 3 types from this preference order:

1. **條文** (必含) — statute is the legal basis; without 條文 the memo
   has no grounding.
2. **判決** (通常含) — case law shows current judicial trend; absence
   risks "通說 但 實務不採" gap.
3. **函釋** (含 when 主管機關 has clarified) — regulatory
   interpretation; high authority for 個資 / 公平交易 / 勞工 /
   金融 / 通訊 domains.
4. **學說** (含 when scholarly consensus / controversy is decisive) —
   useful for new 條文 (< 5 years 公告) or contested interpretations.

This is **advisory** — early_stop logic only enforces ≥ 2. The
preference ordering informs `cite.md` synthesis (which type drives
the §結論 statement) but does not gate the loop.

## 6. Source classification (URL → type mapping)

Used by `protocols/iterative-search.md` to assign `type` field on
each newly captured source. Match by URL host + path prefix.

| URL pattern | Inferred type | Note |
|---|---|---|
| `law.moj.gov.tw/LawClass/LawAll.aspx` | `條文` | 全國法規資料庫 |
| `judicial.gov.tw/FJUD/...` | `判決` | 司法院 法學資料 |
| `mojlaw.moj.gov.tw` | `函釋` | 法務部 主管法規 |
| `pdpc.moj.gov.tw` | `函釋` | 個資 (PDPC 籌備處 官方 函釋) |
| `ftc.gov.tw/law-search` | `函釋` | 公平會 處分書 / 解釋令 |
| `mol.gov.tw/...` | `函釋` | 勞動部 |
| `sfb.gov.tw` / `fsc.gov.tw` | `函釋` | 金管會 / 證期局 |
| `ncc.gov.tw/law` | `函釋` | NCC 通訊傳播委員會 |
| 月旦法學雜誌 / 法令月刊 / 學者個人頁面 | `學說` | only if author + 期刊號 / 篇名 identifiable |
| Other / unclassifiable | `未分類` | does NOT count toward ∩ |

Hosts not in this table are NOT auto-promoted to a 法源 type. The LLM
in `protocols/iterative-search.md` may upgrade `未分類` → an actual
type ONLY when the page content explicitly identifies authority
(e.g. a blog page that quotes 法務部 法律字第 N 號 verbatim with
official 發文日期 — captured as 函釋 with the blog URL as 來源, but
the 識別字號 belongs to 法務部).

## 7. Edge cases

- **大法官 解釋 / 憲法法庭 判決** → classify as `type=判決` (binding
  authority; treat as supreme court of judicial branch).
- **行政函釋 + 立法理由** → `函釋` unless explicit 「立法理由」
  marker → in which case the source is meta-data on a 條文, NOT
  separately counted as 學說 (per §3 promotion rule).
- **PDPC 籌備處 推廣文獻 / 民眾問答 / FAQ** → NOT `函釋` (these are
  not binding interpretations). Classify as `學說` IF authored by a
  named expert with affiliation disclosed; otherwise `未分類`.
- **新聞稿 / 部 內部會議紀錄 / 立法院公報 質詢紀錄** → NOT counted
  (not authoritative legal source). Capture into `state.sources`
  with `type=未分類` for audit; doesn't count toward ∩.
- **WebFetch returned 404 / empty / 403** → do NOT classify as
  anything; log to `state.errors[]` (see `protocols/iterative-search.md`
  state schema); do NOT increment `state.fetches` for failed source
  classification (the fetch itself counts, but the source slot does not).
- **Duplicate 字號 across rounds** — if the same 字號 (e.g. 109 台上
  1234) is captured from two URLs (e.g. judicial.gov.tw + 月旦法學
  cite), dedupe in `state.sources` by 字號 (keep first; merge URLs
  into `alternate_urls`). `types_covered` counts the 字號 once.
- **判決 字號 with 字 + 年 + 數字 disambiguation** — 「最高法院 109
  年度 台上 字 第 1234 號 民事 判決」 and 「109 台上 1234」 are the
  same 字號 — normalize on canonical form 「<court>-<年>-<字>-<號>」
  for dedup key.

## 8. Type counting algorithm

Pseudo-code consumed by `protocols/triangulate.md` (Step 2: read
`state.sources`, compute `types_covered`, decide early_stop /
forced_stop / partial).

```python
DEMOTED = {'未通說', '已廢止', '少數說', '未分類'}

def count_types_covered(sources):
    """
    sources: list of {url, type, captured_at, relevance_snippet, ...}
    returns: (types_dict, types_count)
    types_dict: {type_label: count} — only non-demoted types
    types_count: len(types_dict) — used against early_stop_min_types
    """
    types = {}
    for s in sources:
        if s['type'] in DEMOTED:
            continue  # captured for audit; doesn't count toward ∩
        types[s['type']] = types.get(s['type'], 0) + 1
    return types, len(types)


def is_early_stop(state, cap):
    """
    state: parsed state.json
    cap: {early_stop_min_sources: 8, early_stop_min_types: 2}
    """
    n_sources = len(state['sources'])
    _, n_types = count_types_covered(state['sources'])
    return (n_sources >= cap['early_stop_min_sources']
            and n_types >= cap['early_stop_min_types'])
```

`state.types_covered` (written by `protocols/iterative-search.md` on
every iteration) is the materialized `types_dict` — `triangulate.md`
re-derives from sources to verify consistency (drift check; if they
diverge, trust the sources list and log a warning).

## 9. Triangulate output

`protocols/triangulate.md` reads this file + `state.json`, then
decides one of three exit dispositions for `cite.md` to act on:

- **early_stop** — ≥ 8 sources + ≥ 2 types (non-demoted). Normal
  memo without ⚠️ prefix.
- **forced_stop** — cap reached (≥ 5 rounds OR ≥ 30 fetches) without
  early_stop. Memo gets ⚠️ 覆蓋未達 triangulation block prepended.
- **partial** — neither floor met but plan exhausted (no more
  keyword/site combinations). Treated as `forced_stop=true` for grader
  purposes; memo gets the same ⚠️ block.

The disposition is written back to `state.json` as
`state.disposition` (one of `early_stop` / `forced_stop` / `partial`)
for the grader (`scripts/grade_research.py`).
