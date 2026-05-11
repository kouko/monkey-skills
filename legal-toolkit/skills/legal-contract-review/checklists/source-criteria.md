# source-criteria — binary all-pass rubric for self-grade.md (source_score)

> **v0.3.0 (Phase 1.6) status**: full 10-criterion rubric. Consumed by
> `scripts/self_grade.py` (Python structural checks) AND by the LLM at
> session-grade time (substantive verification).

> **Convention** (Harvey BigLaw Bench): document-level citation is the
> floor; passage-level is bonus. Every citation is `valid` (exists,
> supports conclusion) / `invalid` (doesn't exist or doesn't support) /
> `unverifiable` (cannot determine; e.g. private function letter the LLM
> cannot access). Hallucinated citations are catastrophic — SRC-09 fail.

> **Two tiers** (same as answer-criteria): `tier: deterministic` vs
> `tier: semantic`. `self_grade.py` runs the deterministic tier; the
> protocol-driven session runs the semantic tier.

---

## Criteria (N = 10)

### Tier: deterministic (Python-verifiable)

| ID | Criterion (zh-TW) | Verification |
|---|---|---|
| **SRC-01** | citation 結構符合 schema | each citation has `{citation, type, supports}` non-empty; `type ∈ {statute, case, regulation, authority_letter, scholarly}` |
| **SRC-02** | citation 沒有重複 (noise reduction) | no two citations have identical `citation` + `supports` pair |
| **SRC-03** | URL（若有）指向已知主管機關 / 司法院 / 全國法規 domain | `url` if set must match an allowlist (`law.moj.gov.tw` / `judgment.judicial.gov.tw` / `*.gov.tw` / `mops.twse.com.tw`) |
| **SRC-04** | citation 沒有 obvious 結構失敗 + 沒踩 blacklist | `case` matches case-number pattern; `statute` matches `§X-Y` pattern AND not in `assets/statute-articles.json` blacklist (v0.3.1+: known fabricated sub-articles + deprecated articles such as 民法 §11-1, 營業秘密法 §11-1, 個資法 §27 deleted 2025-11-11) |
| **SRC-05** | 每個 verified=true citation 有 supports 欄位非空 | citations with `verified: true` MUST have `supports` describing the CRAC claim it backs |

### Tier: semantic (LLM-judged)

| ID | Criterion (zh-TW) | LLM judgment prompt |
|---|---|---|
| **SRC-06** | 引用的法條真實存在 (非 hallucinated) | "For each `statute` citation, does the §number match the actual statute? Mark unverifiable for rare/draft statutes; mark invalid for fabricated §numbers." |
| **SRC-07** | 引用的判例真實存在 | "For each `case` citation, is the case number structurally valid AND can you describe its general holding without invention? If not, mark unverifiable or invalid." |
| **SRC-08** | citation 支持結論 (非 relevant-sounding-but-off) | "For each citation, does the statute text / case holding actually support the CRAC point it's attached to, not just sound similar?" |
| **SRC-09** | 沒有 hallucinated（憑空捏造）citation | "Across all citations, is every one verifiable, OR explicitly marked unverifiable? Hallucinated = fabricated case number that sounds plausible. This is a hard FAIL." |
| **SRC-10** | 引用 carve-outs / supersession 已標註 | "If any citation has a known carve-out, modification, or has been superseded (e.g. 民法 §X 已於 YYYY 修正), does the CRAC analysis acknowledge it?" |

---

## How citations are sourced

The LLM's citation pool:

| Source type | Acceptable origin |
|---|---|
| **statute** | 全國法規資料庫 (https://law.moj.gov.tw) |
| **case** | 司法院判決系統 (https://judgment.judicial.gov.tw) |
| **regulation** | 主管機關官網 (PDPC / 勞動部 / 金管會 / 證交所 / 公平會 / NCC) |
| **authority_letter** | 函釋字號 + 主管機關 |
| **scholarly** | author + work + year + page (e.g. 王澤鑑 / 吳從周 / 王文宇 / 詹森林) |

⚠️ The LLM is NEVER allowed to invent case numbers / function letter numbers.
When uncertain, the LLM MUST:
1. Cite the **general principle** without a specific case (acceptable)
2. OR cite the statute and acknowledge "judicial interpretations have applied this to..." (acceptable)
3. OR mark the citation as `unverifiable` with a note (acceptable)
4. NEVER fabricate a "最高法院 XXX 年度 XXX" pattern just because it sounds plausible (UNACCEPTABLE — SRC-09 hard FAIL)

---

## Calibration (v0.3.0)

Pearson correlation target:
- **source_score Pearson ≥ 0.7** across 5-10 dogfood contracts (higher
  bar than answer_score because binary citation valid/invalid is more
  objective)
- If Pearson < 0.7: examine the citation type with the worst LLM-vs-hand
  disagreement — typically `scholarly` or `authority_letter` where
  semantic judgment varies more than `statute` / `case`

See `docs/dogfood-procedure.md` for the calibration workflow.

---

## Anti-patterns the rubric is designed to detect

- **Hallucinated citations** (catastrophic) → SRC-04 / SRC-09
- **Citation that doesn't support conclusion** (relevant-sounding but off topic) → SRC-08
- **Outdated statute reference** (民法 §X renumbered in YYYY) → SRC-10
- **Citation chains pointing to private function letters** → should be marked `unverifiable`, not inflated to `valid` → SRC-06 / SRC-07
- **Duplicate citations padding source_score** → SRC-02
- **Random external URL** (not from allowlisted gov domains) → SRC-03

---

## Output (consumed by self-grade.md generator)

For each citation:

```yaml
citation: "民法 §247-1"
type: statute
result: valid / invalid / unverifiable
reason: "<empty if valid>; if invalid: '§247 has no clause 1, this is fabricated'; if unverifiable: 'private function letter, cannot access'"
```

Aggregated:
```yaml
source_score:
  passed: 5
  total: 8
  criteria_results: [...]
failed_criteria:
  - { domain: source, criterion_id: SRC-04, explanation_zh_tw: "案號格式異常" }
```

If `source_score.total == 0` (no citations, e.g. `mode == nda`), record `0/0`
BUT add a note in self-grade.md explaining why — so the user doesn't read
"0/0" as failure.
