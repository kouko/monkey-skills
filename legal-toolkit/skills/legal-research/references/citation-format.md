<!-- [draft — for 法務 review; Phase 4.5 GC outreach validation] -->

# Citation format — Harvey doc-level

Reference file consumed by [`protocols/cite.md`](../protocols/cite.md)
(synthesizes `## §Citations` manifest in `research-memo.md`). Encodes
the **Harvey doc-level citation** convention required by `grade_research.py`
`citation_has_relevance` check.

> **Path A discipline** — Chinese terms throughout (條文 / 判決 / 函釋 /
> 學說); ISO 8601 dates (`2026-05-15` not `2026/5/15`); `民法 §184`
> not `民法 184條` not `Civil Code §184`. Grader fires on English calques
> + date format drift.

> **No inline 條文 text** — defer to canonical
> [`scripts/canonical/legal-sources.json`](../../../scripts/canonical/legal-sources.json)
> for pcode catalog (民法 `B0000001` / 個資法 `I0050021` / 勞基法
> `N0030001` / 性平法 `N0030014` / 公司法 `J0080001` / 證交法 `G0400001`
> / 公平交易法 `J0150002` / 消保法 `J0170001` / 行政程序法 `A0030055`
> / 著作權法 `J0070017` / 營業秘密法 `J0080028` etc.). The full pcode
> set lives in canonical SoT; do NOT duplicate.

---

## 1. Format specification

Every entry in `## §Citations` MUST follow this 3-line shape:

```markdown
N. **<type>**: <full reference: source name + numeric id + 主管機關/court + 日期 + canonical URL or pcode>
   → <1-line relevance: how this source supports/refines/contradicts the §結論 in research-memo.md>
```

**Rules**:

- `N` = sequential integer starting at `1` (no gaps; do not re-number when sources are added late)
- `<type>` ∈ `{條文, 判決, 函釋, 學說}` — exactly one of these four 法源類型 tokens (no English, no synonyms)
- **Full reference** must be unambiguous — a 法務 reader given only this text MUST be able to locate the source (官方來源 + 識別字號 + 引用日期)
- **Relevance line** uses arrow `→` prefix; exactly one sentence; identifies which 論點 in §結論 this citation supports / refines / contradicts
- Bare 字號 / pcode without the `→` line = grader FAIL (`citation_has_relevance` check)

---

## 2. Worked examples — 4 sources, one per type

The following block is a **complete §Citations manifest** that would PASS
the grader. Each entry shows the canonical shape for its 法源類型.

```markdown
1. **條文**: 民法 §184 (中華民國民法; 全國法規資料庫 pcode B0000001; 引用日期 2026-05-15)
   → 本案請求權基礎核心；§184 第一項前段「故意或過失，不法侵害他人之權利」為主要構成要件依據。

2. **判決**: 最高法院 109 年度台上字第 1234 號民事判決 (司法院判決系統; 引用日期 2026-05-15)
   → 「不法侵害他人權利」之 學說 通說採人格權說；本案 §184 涵攝可援引此判決確立的人格權範圍。

3. **函釋**: 法務部 法律字第 11012345 號函 (2024-04-15; 法務部主管法規 mojlaw.moj.gov.tw 引用日期 2026-05-15)
   → 「適當安全措施」§27 之 認定標準；本案 §27 涵攝信心提升至 該當 (參此函釋第三段)。

4. **學說**: 王澤鑑《侵權行為法》第 3 版 (2024) §3.2 第 78 頁
   → 「相當因果關係」之 判定標準採通說；本案 因果關係 涵攝採此 學說 立場。
```

This 4-source manifest covers all 4 法源類型 (early-stop floor:
`types_covered >= 2`; this exceeds the floor at 4).

---

## 3. Per-type field templates

LLM fills these for each citation in `protocols/cite.md` Step 2.

### 3.1 條文 template

```
**條文**: <法典中文名稱> §<條號> (中華民國<法典中文名稱>; 全國法規資料庫 pcode <pcode>; 引用日期 <ISO 日期>)
→ <relevance>
```

- `<法典中文名稱>` — canonical short name (e.g. 民法 / 個資法 / 勞基法 / 性平法 / 行政程序法)
- `<條號>` — Arabic numeral, no leading zeros (`184` not `0184`)
- `<pcode>` — 8-char code from `scripts/canonical/legal-sources.json` (e.g. `B0000001`, `I0050021`)
- `<ISO 日期>` — date the WebFetch was run, format `YYYY-MM-DD`

**Common 條文 references** (paired with canonical pcode):

| 法典 | pcode | 高頻 § |
|---|---|---|
| 民法 | `B0000001` | §184 / §227 / §216 / §229 |
| 個資法 | `I0050021` | §5 / §8 / §9 / §27 / §29 |
| 勞基法 | `N0030001` | §11 / §14 / §16 / §17 |
| 性平法 | `N0030014` | §13 |
| 行政程序法 | `A0030055` | §49 / §92 / §96 / §174-1 |
| 公司法 | `J0080001` | §23 / §202 / §223 |
| 證交法 | `G0400001` | §20 / §157-1 / §171 |
| 公平交易法 | `J0150002` | §9 / §20 / §25 |
| 消保法 | `J0170001` | §7 / §51 |
| 著作權法 | `J0070017` | §10 / §44 / §65 |
| 營業秘密法 | `J0080028` | §2 / §10 / §13-1 |

### 3.2 判決 template

```
**判決**: <法院> <年度>年度<字>字第<N>號<案類>判決 (司法院判決系統; 引用日期 <ISO 日期>)
→ <relevance>
```

- `<法院>` — 最高法院 / 最高行政法院 / 臺灣高等法院 / 臺灣高等法院 <分院> / 智慧財產及商業法院 / 臺灣<縣市>地方法院 (use full 中文 form; abbreviations only when 司法院判決系統 uses them)
- `<年度>` — 民國年 (e.g. `109` for 民國 109 年; do NOT convert to 西元)
- `<字>` — common values: `台上` (最高法院民事三審) / `台抗` (最高法院抗告) / `台聲` (最高聲請) / `上` (高等法院民事二審) / `重上` (高等法院重訴二審) / `訴` (地方法院民事訴訟) / `勞訴` (勞動法庭) / `智` (智慧財產法院) / `判` (最高行政法院判決) / `裁` (行政法院裁定)
- `<N>` — case 流水號 (Arabic numeral, no leading zeros)
- `<案類>` — `民事` / `刑事` / `行政` (matches the 字 prefix; e.g. `台上` 字 → 民事)

**Verification rule** — if `WebFetch` returned no match for the 字號, do
**NOT** cite the 判決. Speculative 判決 字號 is a grader-FAIL anti-pattern
(§4.4); fall back to 學說 通說 or 條文 and note the coverage gap in §結論.

### 3.3 函釋 template

```
**函釋**: <主管機關> <字號 prefix>字第<N>號函 (<發文日期 YYYY-MM-DD>; <來源 e.g. mojlaw.moj.gov.tw / ftc.gov.tw>; 引用日期 <ISO 日期>)
→ <relevance>
```

- `<主管機關>` — full 中文 機關名 (e.g. 法務部 / 公平交易委員會 / 勞動部 / 金融監督管理委員會 / 國家通訊傳播委員會)
- `<字號 prefix>` — 機關-specific 字 (see table below)
- `<發文日期>` — 函釋 issuance date in ISO 8601; convert 民國年 → 西元年 ONLY for this field (e.g. 民國 113 年 4 月 15 日 → `2024-04-15`)
- `<來源>` — host of canonical source (e.g. `mojlaw.moj.gov.tw` for 法務部 / `ftc.gov.tw` for 公平會 / `pdpc.gov.tw` for 個資籌備處)
- `<ISO 日期>` — date the WebFetch was run

**Common 主管機關 / 字號 prefix** (TW practice as of 2026-05):

| 主管機關 | 字號 prefix | 領域 |
|---|---|---|
| 法務部 | 法律字 / 法令字 / 法檢字 | 民事 / 行政 / 個資 / 刑事 |
| 個資保護 (PDPC 籌備處) | 法律字 | 個資法 (currently shared with 法務部; PDPC 正式成立後可能改用獨立字號) |
| 公平交易委員會 | 公處字 / 公競字 | 公平法 / 反壟斷 |
| 勞動部 | 勞動條 / 勞動關 / 勞動保 | 勞基法 / 勞退 / 職安 |
| 金管會 | 金管法 / 金管證 / 金管保 | 證交 / 保險 / 銀行 |
| 國家通訊傳播委員會 (NCC) | 通傳 | 電信 / 廣播 |
| 經濟部 | 經商字 / 經智字 | 公司 / 智財 |
| 衛福部 | 衛部醫字 / 衛部食字 | 醫療 / 食安 |

### 3.4 學說 template

```
**學說**: <作者>《<書名 OR 期刊論文標題>》<版次/期數> (<出版年>) <章節/頁數>
→ <relevance>
```

- `<作者>` — 中文 全名 (e.g. 王澤鑑, not WANG Tze-Chien)
- `<書名>` — full title with 《》 quotes for monographs; 〈〉 quotes for journal articles
- `<版次/期數>` — for books: `第 3 版` (西元年版次); for journals: `<刊名> 第 <N> 期`
- `<出版年>` — 西元年 (e.g. `2024`); journal articles use the issue year
- `<章節/頁數>` — pinpoint: `§3.2` for monograph section / `第 78 頁` for page / `頁 78-82` for range

**Common 法務 anchor authors** (TW in-house 法務 通常引用; 法務 SME validation deferred to Phase 4.5):

| 領域 | 通說 / 主流 authors |
|---|---|
| 民法 (一般) | 王澤鑑 / 王文宇 / 黃茂榮 / 鄭玉波 |
| 民法 (侵權) | 王澤鑑 / 詹森林 |
| 民法 (契約) | 邱聰智 / 林誠二 |
| 勞動法 | 邱駿彥 / 林更盛 / 劉志鵬 / 吳姿慧 |
| 個資 / 隱私 | 蔡達智 / 李震山 / 范姜真媺 (PDPC 籌備處 推廣文獻亦可援引) |
| 公司 / 證券 | 王文宇 / 劉連煜 / 易明秋 |
| 行政法 | 翁岳生 / 吳庚 / 林明鏘 |
| 刑事 | 林山田 / 林東茂 / 黃榮堅 |
| 智財 | 謝銘洋 / 章忠信 / 沈宗倫 |

---

## 4. Anti-patterns (grader will FAIL these)

The `grade_research.py` `citation_has_relevance` check + `path_a_antipatterns`
bank fire on the following shapes. Avoid them at draft time, not at review time.

### 4.1 Bare 字號 (no full reference, no relevance line)

```markdown
❌ 1. 民法 §184
```

**Why fail**: missing source attribution (法典中文名稱 + pcode + 引用日期) and missing `→ <relevance>` line. The grader cannot locate the source nor verify it supports the conclusion.

### 4.2 Missing relevance

```markdown
❌ 1. **條文**: 民法 §184 (中華民國民法; 全國法規資料庫 pcode B0000001; 引用日期 2026-05-15)
```

**Why fail**: full reference is correct but no `→ <relevance>` line. Harvey doc-level requires the relevance pinpoint — without it the citation is unanchored to §結論.

### 4.3 Vague relevance

```markdown
❌ 1. **條文**: 民法 §184 (中華民國民法; 全國法規資料庫 pcode B0000001; 引用日期 2026-05-15)
   → 相關。
```

```markdown
❌ 1. **判決**: 最高法院 109 年度台上字第 1234 號民事判決 (司法院判決系統; 引用日期 2026-05-15)
   → 重要參考。
```

**Why fail**: relevance lines like `→ 相關` / `→ 重要參考` / `→ 參考用` do not pinpoint **which 論點 in §結論** this citation supports. Grader keyword check rejects 1-word vague relevance.

### 4.4 Speculative citation (fabricated 字號)

```markdown
❌ 1. **判決**: 最高法院 999 年度台上字第 99999 號民事判決 (司法院判決系統; 引用日期 2026-05-15)
   → 確立人格權範圍。
```

**Why fail**: 判決 字號 fabricated (no WebFetch hit; 999 年度 does not exist; fictitious case number). If `iterative-search.md` returned no match for a 字號, do **NOT** cite it — use 學說 通說 or 條文 instead, and note the coverage gap in §結論 (and let `forced_stop` trigger the ⚠️ block + §Escalation if applicable).

### 4.5 English calques

```markdown
❌ 1. **Statute**: Article 184 Civil Code (Pcode B0000001; Retrieved 2026-05-15)
   → Core basis of claim.
```

**Why fail**: English replacing 中文 法源 vocabulary. Path A discipline requires 條文 / 判決 / 函釋 / 學說 tokens + 中文 法典名 + 中文 relevance line. The grader `path_a_antipatterns` bank fires on Anglo legal terminology in `## §Citations` block.

### 4.6 Date format drift

```markdown
❌ 1. **條文**: 民法 §184 (中華民國民法; 全國法規資料庫 pcode B0000001; 引用日期 2026/5/15)
   → 本案請求權基礎核心。
```

**Why fail**: `2026/5/15` is not ISO 8601. Use `2026-05-15` (zero-padded month + day, hyphen separator). Mixed 民國年 + 西元年 is also a fail mode — only `<發文日期>` of 函釋 may convert 民國 → 西元; all `引用日期` are 西元 ISO 8601.

---

## 5. Multi-citation patterns

### 5.1 Multiple sources of the same type for one 論點

When a §結論 論點 is supported by **multiple sources of the same type**:

- **List each as a separate entry** — do NOT compress into one entry
- Each entry gets its own `→ <relevance>` line (relevance lines may overlap in wording but the entries stay separate)
- This protects the `citation_count_or_warn` check (≥ 8 sources floor)

```markdown
2. **判決**: 最高法院 108 年度台上字第 5678 號民事判決 (司法院判決系統; 引用日期 2026-05-15)
   → 「不完全給付」§227 第一項 carve-out 認定；本案 §227 涵攝可援引此判決之 carve-out 範圍。

3. **判決**: 最高法院 110 年度台上字第 9012 號民事判決 (司法院判決系統; 引用日期 2026-05-15)
   → 「不完全給付」§227 第二項 加害給付 之認定；補充 #2 判決對 carve-out 之 詮釋。
```

### 5.2 判決 cites 函釋 (cross-type reinforcement)

When a 判決 explicitly cites a 函釋 as binding authority:

- Cite **both** separately (each gets its own entry in `## §Citations`)
- 判決's relevance line MAY reference the cited 函釋 by its `## §Citations` number (e.g. `→ 援引上述 §Citations #3 函釋認定 §27 適當性`)
- This produces 2 法源類型 in one 論點, helping early-stop `types_covered >= 2`

```markdown
3. **函釋**: 法務部 法律字第 11012345 號函 (2024-04-15; mojlaw.moj.gov.tw; 引用日期 2026-05-15)
   → 「適當安全措施」§27 之 認定標準；本案 §27 涵攝信心提升至 該當 (參此函釋第三段)。

4. **判決**: 臺灣高等法院 112 年度上字第 345 號民事判決 (司法院判決系統; 引用日期 2026-05-15)
   → 援引上述 §Citations #3 函釋認定 §27 之 適當安全措施 範圍；補強 §結論 對 個資法 §27 該當 之 信心。
```

### 5.3 學說 反對 通說 (contradicting authority)

When a 學說 explicitly **contradicts** the §結論 立場:

- Still cite it (transparency > advocacy)
- Relevance line states the contradiction: `→ 反對 §結論 立場 ...`
- §結論 should address the contradiction (do not silently drop dissenting 學說)

```markdown
5. **學說**: 黃茂榮《債法總論》第 4 版 (2023) §5.1 第 142 頁
   → 反對 §結論 採之 相當因果關係 通說；主張 條件說 應為 主流。本案 §結論 保留採通說立場，理由見 §法源分析 第 2.3 節。
```

### 5.4 函釋 cites 判決 (回向 reference)

When a 函釋 explicitly references a 判決 as 解釋依據:

- Cite both separately (same as §5.2 reverse)
- 函釋's relevance line references the cited 判決 by `## §Citations` number

---

## 6. Format checklist (self-verify before committing memo)

Before `protocols/cite.md` emits the final `research-memo.md`, walk this
checklist. Each item maps to a `grade_research.py` check; failing any
item triggers exit 1 unless `forced_stop=true` (which downgrades to exit 2).

- [ ] **Every entry has `N. **<type>**:` prefix** — type ∈ {條文, 判決, 函釋, 學說}; no other tokens
- [ ] **Every entry has full reference** unambiguously locating the source (法典名 + § / 法院 + 字號 / 主管機關 + 字號 + 發文日 / 作者 + 書名 + 頁數)
- [ ] **Every entry has `→ <relevance>` line** with exactly one sentence
- [ ] **Relevance is specific to §結論** — names a 論點 / 條文 / 構成要件 element / carve-out; does NOT use vague `→ 相關` / `→ 重要` / `→ 參考`
- [ ] **ISO 8601 date format** for `引用日期` (`YYYY-MM-DD`, hyphen separator, zero-padded)
- [ ] **Sequential numbering** — N starts at 1, no gaps, no duplicates
- [ ] **No bare 字號** — every 判決 / 函釋 字號 ships with full source attribution
- [ ] **No fabricated 字號** — every 判決 / 函釋 cited has a WebFetch trail in `state.json.sources`; if not, dropped and noted as coverage gap
- [ ] **No English calques** — 條文 / 判決 / 函釋 / 學說 + 中文 法典名 + 中文 relevance throughout
- [ ] **Citation count ≥ 8 OR ⚠️ block** — `citation_count_or_warn` check
- [ ] **法源類型 coverage ≥ 2 OR ⚠️ block** — `source_type_coverage` check; counted from distinct `<type>` tokens in §Citations

If any check fails, fix in `protocols/cite.md` Step 2 before writing the
output file. Do not ship a memo with known citation defects — the grader
will catch them and the memo will need to be regenerated, burning fresh
fetch budget.

---

## 7. References

- Consumer protocol: [`protocols/cite.md`](../protocols/cite.md) — synthesizes `## §Citations` from `state.json.sources` using these templates
- Sibling references: [`webfetch-targets.md`](webfetch-targets.md) (target sites + URL patterns) / [`triangulation-rules.md`](triangulation-rules.md) (法源類型 classification + ∩ rules)
- Canonical 條文 SoT: [`scripts/canonical/legal-sources.json`](../../../scripts/canonical/legal-sources.json) — pcode catalog
- Design spec: [`docs/superpowers/specs/2026-05-15-legal-toolkit-phase3-irac-cluster-design.md`](../../../../docs/superpowers/specs/2026-05-15-legal-toolkit-phase3-irac-cluster-design.md) §6.6
- Grader: `scripts/grade_research.py` `citation_has_relevance` / `citation_count_or_warn` / `source_type_coverage` / `path_a_antipatterns` checks
