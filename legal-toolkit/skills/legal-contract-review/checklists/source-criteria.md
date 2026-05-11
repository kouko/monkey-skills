# source-criteria — binary all-pass rubric for self-grade.md (source_score)

> **Phase 1 status**: stub — Phase 1.6 will add automated citation verification via `scripts/self_grade.py` (URL fetch / structural check). Phase 1 ships protocol-level instructions for the LLM to self-evaluate citations.

> **Convention** (Harvey BigLaw Bench): document-level citation is the floor; passage-level is not required. Every citation is either `valid` (exists, supports conclusion) / `invalid` (doesn't exist or doesn't support) / `unverifiable` (cannot determine; e.g. private function letter that the LLM cannot access).

---

## Criteria (Phase 1 baseline, N = 6)

| ID | Criterion (zh-TW) | Verification |
|---|---|---|
| **SRC-01** | 引用的法條真實存在 | for each citation of type `statute`, the §number exists in 全國法規資料庫 (LLM can verify on common statutes; flag rare/draft statutes as `unverifiable`) |
| **SRC-02** | 引用的判例編號真實存在 | for each citation of type `case`, the case number (e.g. "最高法院 100 年度台上字第 1166 號") is structurally valid AND the LLM can describe its general holding without inventing it |
| **SRC-03** | 引用支持結論 | for each citation, the citation's actual content (statute text / case holding) supports the CRAC point it's attached to — not just relevant-sounding |
| **SRC-04** | 沒有 hallucinated citation（憑空捏造）| every citation is one the LLM can confirm exists; "unverifiable" is acceptable, "invented" is not. Hallucinated citations are SRC-04 fail |
| **SRC-05** | Citation URL（若有）為主管機關官方來源 | `url` field, when present, points to 全國法規資料庫 / 司法院判決系統 / 主管機關官網 / 公開資訊觀測站 — not third-party blog / aggregator |
| **SRC-06** | Source carve-outs noted | If any citation has a known carve-out / superseded status, the CRAC analysis acknowledges it (e.g. "民法 §X 已於 YYYY 修正，本條於 ZZZ 之後適用") |

---

## Phase 1.6 expansion targets

- SRC-07: passage-level citation verification (LLM extracts the specific statutory paragraph being cited)
- SRC-08: cross-reference 主管機關函釋 numbers (PDPC / 勞動部 / 金管會) against the corresponding function letter database
- SRC-09: 學說 citation — author + year + work + page (e.g. "王澤鑑《債法原理》(2014) p.512")
- SRC-10: Foreign-law citations when jurisdiction != TW — basic structural validity check

---

## How citations are sourced

The LLM's citation pool in Phase 1:

| Source type | Acceptable origin |
|---|---|
| **statute** | 全國法規資料庫 (https://law.moj.gov.tw) is the SoT for TW law; LLM should ground citations to this database's §numbers |
| **case** | 司法院判決系統 (https://judgment.judicial.gov.tw); case-number format is standardised |
| **regulation** | 主管機關官網 (PDPC / 勞動部 / 金管會 / 證交所 / 公平會 / NCC) |
| **authority_letter** | 函釋字號 + 主管機關 (e.g. "個資保護處 109 年 7 月 28 日 法律字第 10903XXX 號") |
| **scholarly** | author + work + year + page; preferred sources: 王澤鑑 / 吳從周 / 王文宇 / 詹森林 |

⚠️ The LLM is not allowed to invent case numbers or function letter numbers. When uncertain, the LLM should:
1. Cite the **general principle** without a specific case (acceptable)
2. OR cite the statute and acknowledge "judicial interpretations have applied this to..." (acceptable)
3. OR mark the citation as `unverifiable` with a note (acceptable)
4. NEVER fabricate a "最高法院 XXX 年度 XXX" pattern just because it sounds plausible (UNACCEPTABLE — SRC-04 fail)

---

## Calibration (Phase 1.6)

Pearson correlation target:
- source_score Pearson ≥ 0.7 across 5-10 dogfood contracts (higher than answer_score because binary citation valid/invalid is more objective)

---

## Anti-patterns the rubric is designed to detect

- **Hallucinated citations** (the catastrophic case): SRC-04 specifically guards this
- **Citation that doesn't support the conclusion** (relevant-sounding but actually about a different issue): SRC-03
- **Outdated statute reference** (民法 §XXX was renumbered in YYYY): SRC-06
- **Citation chains pointing to private function letters** the LLM cannot actually access: should be marked `unverifiable`, not inflated to `valid`

---

## Output (consumed by self-grade.md generator)

For each citation:

```yaml
citation: "民法 §247-1"
type: statute
result: valid / invalid / unverifiable
reason: "<empty if valid>; if invalid: '§247 has no clause 1, this is fabricated'; if unverifiable: 'private function letter, cannot access'"
```

If `source_score.total == 0` (no citations emitted, e.g. mode == nda), record `source_score: 0/0` BUT still emit a note in self-grade.md explaining why (so the user doesn't read "0/0" as a failure mode).
