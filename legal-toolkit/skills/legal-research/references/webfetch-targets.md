<!-- [draft — for 法務 review; Phase 4.5 GC outreach validation] -->

# webfetch-targets

Target sites + URL patterns + crawl etiquette + fallback chain for the
`legal-research` skill. Consumed by `protocols/plan.md` (target-site
selection at Step 1) and `protocols/iterative-search.md` (URL
construction + fallback dispatch inside the Agent loop).

Scope: **Taiwan in-force law (Path A discipline)** — 條文 / 判決 /
函釋 / 學說. WebFetch is the ONLY resource layer (Q1 locked: no
Python scrapers); this file encodes the dispatcher logic.

---

## 1. Primary target sites (4 categories)

### 1.1 條文 (statutes) — 全國法規資料庫

Host: `law.moj.gov.tw`

- All articles: `https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=<法典pcode>`
- Single article: `https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=<法典pcode>&flno=<條號>`

Common pcode anchors (full catalogue: see
`legal-toolkit/scripts/canonical/legal-sources.json` `statute_sources`
— that file is the SoT, this list is operational shortcut only):

| 法典 | pcode |
|---|---|
| 民法 | `B0000001` |
| 民事訴訟法 | `B0010001` |
| 個人資料保護法 (個資法) | `I0050021` |
| 勞動基準法 (勞基法) | `N0030001` |
| 性別平等工作法 (性平法) | `N0030014` |
| 行政程序法 | `A0030055` |
| 公司法 | `J0080001` |
| 證券交易法 | `G0400001` |
| 公平交易法 | `J0150002` |
| 營業秘密法 | `J0080028` |
| 著作權法 | `J0070017` |
| 消費者保護法 (消保法) | `J0170001` |

**Path A note**: do NOT inline-quote 條文 text in the fetched
citation. The skill records the URL + pinpoint; if the LLM needs
text, it re-fetches at synthesis time. Avoids drift when 條文 amends.

### 1.2 判決 (judgments) — 司法院法學資料檢索

Host: `judicial.gov.tw` (newer: `judgment.judicial.gov.tw`)

- Search: `https://judicial.gov.tw/FJUD/qryresult.aspx?judtype=JUDBOOK&keyword=<keyword>`
- Detail (data view): `https://judicial.gov.tw/FJUD/data.aspx?ty=JD&id=<judgment_id>`
- Newer data endpoint: `https://judgment.judicial.gov.tw/FJUD/data.aspx?ty=JD&id={court_code},{year},{type},{number}`

Caveats:

- Search supports 法院名 + 字第 N 號 patterns
- Full 判決 字號 format: `<法院><年度>年度<字>字第<N>號`
  (e.g. 最高法院 110 年度台上字第 1234 號 民事判決)
- Court codes (subset; full map in `legal-sources.json` `case_sources.default.court_codes`):
  - 最高法院: `TPSV`
  - 最高行政法院: `TPAV`
  - 智慧財產及商業法院: `IPCV`
  - 臺灣高等法院: `TPHV`
  - 臺灣臺北地方法院: `TPDV`
- Result pages render JS-heavy; if WebFetch returns sparse HTML, fall
  back to Google site-restricted search (see §4)

### 1.3 函釋 (administrative interpretations)

Multi-host; pick by 主管機關:

| 主管機關 | Host | Search hint |
|---|---|---|
| 法務部 (主管法規) | `mojlaw.moj.gov.tw` | `https://mojlaw.moj.gov.tw/LawSearch.aspx?Type=L&keyword=<keyword>` |
| 個資保護委員會 (籌備處) | `pdpc.gov.tw` | `https://www.pdpc.gov.tw` (page listing + RSS if available); 籌備處 階段，較舊 函釋 在 `mojlaw.moj.gov.tw` |
| 公平交易委員會 | `ftc.gov.tw` | `https://www.ftc.gov.tw/internet/main/decision/decision_search.aspx` |
| 勞動部 | `mol.gov.tw` | `https://laws.mol.gov.tw/FLAW/FLAWQRY01.aspx` |
| 金融監督管理委員會 | `fsc.gov.tw` | `https://www.fsc.gov.tw/ch/home.jsp?id=200&parentpath=0` |
| 經濟部智慧財產局 | `tipo.gov.tw` | `https://www.tipo.gov.tw` |
| NCC (國家通訊傳播委員會) | `ncc.gov.tw` | site-restricted Google search 通常較可靠 |
| 行政院消費者保護處 | `cpc.ey.gov.tw` | `https://cpc.ey.gov.tw` |

函釋 字號 patterns (for search keyword construction):

- 法務部: 法律字第 / 法律決字第 / 法檢字第
- 勞動部: 勞動條 X 字第
- 金管會: 金管證X字第 / 金管銀X字第
- 公平會: 公處字第 / 公字第

### 1.4 學說 (academic doctrine)

**Generally NOT directly fetchable via WebFetch.** 教科書 / 期刊論文
typically behind 月旦 / HyRead / 元照 / 政大法學評論 等 paywalls.

Strategy:

- Rely on **training-data knowledge** for well-known doctrine
  (e.g. 王澤鑑「不完全給付」通說 / 史尚寬 / 林誠二 / 黃立 / 邱聰智)
- Cite explicitly as `學說` type in `state.json.sources` with full
  attribution: 作者 + 著作名 + 版次 + 頁碼 + (引用日期 = 當下)
- Do NOT attempt to fetch academic databases (paywalled or
  registration-walled; WebFetch will 403 / login redirect)
- **Edge case**: open-access 月旦法學雜誌 部分 or 法源資訊網 partial
  excerpts may be fetchable — try, but downgrade to training-data
  cite if 403 / paywall

學說 sources do NOT count toward the `early_stop_min_types ≥ 2`
floor by default (they are training-data-derived; lower confidence
than a fetched primary source). See `references/triangulation-rules.md`
for the typing rules.

---

## 2. Crawl etiquette (apply to ALL fetches)

Per `SKILL.md` §WebFetch crawl etiquette + Q1 lock:

- **User-Agent**: identify as `Mozilla/5.0 (compatible;
  legal-toolkit/0.5.2; +https://github.com/kouko/monkey-skills)` when
  WebFetch supports UA override; default Claude WebFetch UA otherwise
  acceptable (the etiquette is the spirit, not the byte form)
- **Rate limit**: 1-2 fetches per second sustained; never burst > 5
  fetches in any rolling second. If a site returns 429, back off
  (skip remainder of round + record host in
  `state.json.throttled_sites`)
- **robots.txt**: respect; if a target path is disallowed → downgrade
  to fallback chain (§3) without retry
- **Content-Type**: prefer HTML; PDF acceptable when a 主管機關
  publishes 函釋 / 判決 as direct PDF link
- **Encoding**: handle UTF-8 + Big-5 (some 法律 sites are Big-5 legacy
  — WebFetch generally auto-decodes; if garbled, treat as soft fail
  and try fallback)
- **No login walls**: if a fetch redirects to a login form, treat as
  unreachable and downgrade

---

## 3. Fallback chain (when primary fetch fails)

Applied per-URL by `protocols/iterative-search.md`:

1. **Primary fetch** at target site (§1 URL pattern)
2. **403 / 429 / anti-bot block / HTML body empty** → **Google cache**:
   `https://webcache.googleusercontent.com/search?q=cache:<URL>`
3. Google cache also fails → **archive.org Wayback Machine**:
   `https://web.archive.org/web/*/<URL>` (or
   `https://web.archive.org/web/2024*/<URL>` to anchor a year)
4. All fallbacks fail → log in `state.json.sources` with
   `type: "unreachable"` + `url` field; increment `fetches`; continue
   to next plan item (do not retry the same URL in this run)
5. **Consecutive failures > 5** within one round → force_stop the
   loop with note `"WebFetch chain unreliable; recommend manual
   research"` (write `state.json.forced_stop = true` + the note in
   `state.json.errors` if the optional schema field exists)

Rationale: the loop's safety net is `forced_stop + ⚠️` marker, NOT
silent under-delivery. Grader (`scripts/grade_research.py`) treats
`forced_stop = true` + ⚠️ block in memo as exit code 2
(`PASS_WITH_NOTES`), not exit 1 (`FAIL`).

---

## 4. Search strategies (for 判決 + 函釋)

### 4.1 判決 search

- 司法院 search: keyword + 法院 + 年度 range
  - e.g. keyword=`不完全給付` + 法院=`最高法院` + 年度=`110-114`
- If 司法院 returns < 3 hits or 403: **Google site-restricted**:
  - `site:judgment.judicial.gov.tw <keyword> <字號 prefix>`
  - `site:judicial.gov.tw <keyword>`
- Aim for **判決 字號** as the canonical identifier, not URL alone
  — URL may rot; 字號 is stable

### 4.2 函釋 search

- `mojlaw.moj.gov.tw` LawSearch supports keyword + 主管機關 + 字號
  prefix (e.g. `法律字第`)
- If 主管機關 site is hostile / down: **Google site-restricted**:
  - `site:mojlaw.moj.gov.tw <keyword>`
  - `site:<主管機關 host> <keyword> 函`
- 字號 (e.g. 法律字第 10803507100 號) is the canonical identifier

### 4.3 General fallback

- `site:law.moj.gov.tw <keyword>` for 條文 surface
- `site:judicial.gov.tw <keyword>` for 判決 surface
- 用 Google 取代 site 內 search 是合法的 fallback — site 內 search 引擎
  常有 anti-bot / pagination 問題

---

## 5. Topic-to-site mapping (selection heuristic for protocols/plan.md)

Used by `protocols/plan.md` Step 2 (target-site selection ≥ 2):

| Topic | Primary sites | 法源類型 expected |
|---|---|---|
| 民法 / 民事 / 契約 / 侵權 | `law.moj.gov.tw` (條文) + `judicial.gov.tw` (判決) | 條文 + 判決 + 學說 |
| 個資 / data protection | `law.moj.gov.tw` + `pdpc.gov.tw` + `mojlaw.moj.gov.tw` | 條文 + 函釋 + 判決 |
| 勞動 / 員工 / 解雇 / 工時 | `law.moj.gov.tw` + `judicial.gov.tw` + `mol.gov.tw` (勞動部 函釋) | 條文 + 判決 + 函釋 |
| 刑事 / 詐欺 / 背信 / 業務過失 | `law.moj.gov.tw` + `judicial.gov.tw` (刑事案件 search) | 條文 + 判決 |
| 公司 / 證券 / 商業 | `law.moj.gov.tw` + 公開資訊觀測站 + `fsc.gov.tw` + `ftc.gov.tw` | 條文 + 函釋 |
| 智財 / 著作權 / 營業秘密 / 商標 | `law.moj.gov.tw` + 智財法院 (`IPCV`) + `tipo.gov.tw` | 條文 + 判決 + 函釋 |
| 消費者保護 / 定型化契約 | `law.moj.gov.tw` + `cpc.ey.gov.tw` + `ftc.gov.tw` | 條文 + 函釋 |
| 行政 / 訴願 / 政府採購 | `law.moj.gov.tw` + 最高行政法院 (`TPAV`) + `mojlaw.moj.gov.tw` | 條文 + 判決 + 函釋 |

When the topic crosses domains (e.g. 員工 個資 = 勞動 + 個資),
`plan.md` SHOULD pick ≥ 1 site from each domain row to satisfy
triangulation ≥ 2 法源類型 covered.

---

## 6. Path A discipline reminders

- **即時** reporting language (not 72hr) — Taiwan 個資法 uses 「即時」
- **委託 / 受託** model (not controller / processor) — drop EU GDPR
  二分 vocabulary entirely
- **民法 §12-13 minor age** baseline (not PDPA-specific)
- 條文 text: defer to `legal-sources.json` SoT; do NOT inline-quote
  here

Grader (`grade_research.py` `path_a_antipatterns` check) fires on
GDPR-style phrasing in `plan.md` / `research-memo.md` /
`executive-summary.md`. This reference file is exempt from the
grader scan (operational dispatcher, not output), but its examples
still observe Path A vocabulary to avoid drift into outputs.

---

## 7. Maintenance

- pcode catalogue: SoT is
  `legal-toolkit/scripts/canonical/legal-sources.json` →
  `statute_sources.<法典>.pcode`. Sync this file's §1.1 table when
  SoT amends (drift check: Phase 4.5 GC review item).
- 主管機關 host changes: check `function_letter_sources.*.host` in
  SoT; rare but happens (PDPC 籌備處 → 正式 機關 移轉 pending).
- Fallback chain order (primary → Google cache → archive.org) is
  fixed by `protocols/iterative-search.md`; do NOT reorder here
  without a same-PR protocol patch.
