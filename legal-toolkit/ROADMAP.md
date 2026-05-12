# legal-toolkit Roadmap (v0.1.0 → v1.0.0)

> **Status**: design phase complete, scaffold in progress
> **Source of design**: `<obsidian-vault>/research/2026-05-09 法務 Agent Skill (legal-toolkit) 整體架構與執行流程設計.md`（1344 行；38+ 鎖定決定見 §11 ledger）
> **Target**: 台灣 SME → 上市櫃 in-house 法務 in-house toolkit（不是 BigLaw 移植 / 不是 general legal assistant）
> **Distribution**: 免費 open-source 工具，非服務（律師法 §48 對工具不適用）

---

## 結論

完整 11 skill 從 0 → GA 估 **~60-80 工作天**（focused mode）或 **6-8 個月** part-time，分 7 個 phase + 1 個 prerequisite research bracket。Phase 4.5（上市櫃 Compliance research）是 critical path 唯一可平行的長尾項，建議 Phase 2 之後就先開頭做。

---

## Timeline 總覽

```
Phase    v0.x.0  天數    Skill 累計   Critical
─────    ──────  ──────  ─────────   ────────
1        0.1.0   8-12d   3            MVP shell                                      ✅ DONE
1.5      0.2.0   5d      3 (補基建)   DSL + ABAC + 8 條 baseline + seed              ✅ DONE
1.6      0.3.0   3-5d    3 (補 eval)  Binary rubric + dogfood baseline               ✅ DONE
1.6.1    0.3.1   1d      3 (patch)    Dogfood-driven: stance-asymmetry + L6 vague    ✅ DONE
1.6.2    0.3.2   1d      3 (patch)    2nd-pass dogfood: asset id + 案號 cleanup      ✅ DONE
1.7      0.3.3   5-7d    3 (架構)     bundled-vs-runtime architecture refactor       ✅ DONE
2        0.4.0   10d     5            Template + Runbook cluster
─────────────────────────────────────  ─── 至此 = 完整合約 + 合規應變
3        0.5.0   8-12d   7            IRAC cluster (諮詢 + 研究)
4        0.6.0   10d     9            Tracker cluster
4.5      ─       10-15d  9 (no skill) ⚠️ Compliance prerequisite research
5        0.9.0   10-15d  11           Compliance cluster
6        1.0.0   ongoing 11 (治理)    Governance mechanics + GA polish
```

---

## 完整 Skill 全景（11 個）

| # | Skill | Cluster | Abstraction | Phase | Status |
|---|---|---|---|---|---|
| 0a | `using-legal-toolkit` | router | Model System | 1 | MVP |
| 0b | `legal-playbook-author` | utility (cross-cluster) | Workflow | 1 | MVP |
| 1 | `legal-contract-review` | 📋 Playbook | playbook (七層 + TW overlay) | 1 | MVP |
| 2 | `legal-document-draft` | 📝 Template | template + playbook override | 2 | planned |
| 3 | `legal-incident-response` | 🚨 Runbook | NIST IR | 2 | planned |
| 4 | `legal-issue-spot` | 🔍 IRAC | issue 矩陣 + 構成要件涵攝 | 3 | planned |
| 5 | `legal-research` | 🔍 IRAC | IRAC + 請求權基礎 + Agent | 3 | planned |
| 6 | `legal-contract-tracker` | 📅 Tracker | 時序 + threshold alert | 4 | planned |
| 7 | `legal-regulation-watch` | 📅 Tracker | RSS poll + LLM 摘要 + Agent | 4 | planned |
| 8 | `legal-corporate-governance` | 🏛️ Compliance | statutory checklist + filing template + deadline tracker | 5 | ⚠️ BLOCKED on 4.5 research |
| 9 | `legal-dd-quickscan` | 🏛️ Compliance | DD checklist 30-50 項 | 5 | ⚠️ BLOCKED on 4.5 research |

---

## Phase 1 — MVP shell（v0.1.0，8-12 天）

**Scope**：3 skill + cold-start fallback。

**Q-lock**（5+1 鎖定決定）：
- Q-A：plugin 初始 version = **v0.1.0**
- Q-B：雛形成熟度 = **(ii)** SKILL.md + protocols 骨架 + assets stub（不含 baseline 8 條完整內容）
- Q-C：Phase 5 兩個 skill **不建任何空殼**；router 識別表標 Phase 5 + 「pending prerequisite research」
- Q-D：visible 三層擁有權設計（`legal-playbook/` + `legal-outputs/` + `.legal-toolkit/`）；不預留 `clauses/` / `templates/`
- Q-E：disclaimer / escalation override 模板放 **各 skill `assets/{disclaimer-block,escalation-override}.md`**，TECH-SPEC 註明三 skill 內容必須 byte-identical
- Q-F：Cold-start fallback ship **4 條 flat baseline**（confidentiality / governing-law-jurisdiction / auto-renewal / termination-and-survival）+ L7 fallback branch + author bootstrap (a)(b)(c) 三選一 + `escalate_to` 佔位字串 + L7 偵測 warning（β 方案）

### 交付物

| 模組 | 檔案 |
|---|---|
| Plugin root | `legal-toolkit/.claude-plugin/plugin.json`（v0.1.0）/ 加入 `.claude-plugin/marketplace.json` / `README.{md,ja.md,zh-TW.md}` |
| Spec | `PRODUCT-SPEC.md`（商業 + 設計，從 design note §1+§2 抽）/ `TECH-SPEC.md`（含 Cold-Start Fallback 章節） |
| router | `skills/using-legal-toolkit/{SKILL.md, README×3}` — 6 cluster 識別表（Phase 2-5 標 not-yet-available） |
| author | `skills/legal-playbook-author/{SKILL.md, protocols/{bootstrap,extend,revise}-mode.md, assets/{stub.flat.md, stub.variant.md, stub._clause.md, disclaimer-block.md, escalation-override.md}, README×3}` |
| review | `skills/legal-contract-review/{SKILL.md, protocols/{L0a,L0b,L1,L2,L3,L4,L5,L6,L6_5,L7}.md, assets/{output-schema-×6, baseline-fallback-×4, disclaimer-block.md, escalation-override.md}, checklists/{answer,source}-criteria.md, README×3}` |

### Quality gate

5 份真合約跑 contract-review（NDA / SaaS MSA / 採購 / 勞動 / DPA），手動評：
- 6 份輸出檔案完整度（issues / redline / memo-legal / memo-business / escalation / self-grade 全有）
- Disclaimer block 100% 出現於檔尾
- Escalation Override 在高風險場景觸發正確（risk_default red / walk_away_triggered / confidence < 0.7）
- Cold-start 4 條 fallback 命中率 ≥ 50%
- 沒有 LLM pipeline 跳步

---

## Phase 1.5 — DSL 基建（v0.2.0） ✅ **DONE 2026-05-12**

**Scope**：補基礎設施，**不新增 skill**。

**完成狀態**（commits 6748333 → 9892690 on `feat/legal-toolkit-v0.1.0`）：
- ✅ JSON Schema 2020-12 for flat / variant-file / _clause shapes
- ✅ discover_playbook.py + validate_schema.py + detect_conflicts.py
- ✅ abac_filter.py + build_baseline.py + seed_baseline.py
- ✅ 8-clause baseline tarball (4 flat + 4 with variant-folders) +
  deterministic build + sha256-pinned manifest
- ✅ bootstrap-mode / extend-mode / revise-mode / L7-evaluate wired
  to invoke the scripts
- ✅ 80+ tests across all components

### 交付物

| 模組 | 檔案 |
|---|---|
| Schema | `skills/legal-playbook-author/assets/schema.json`（flat / `_clause` / variant 三套 JSON schema） |
| Scripts | `legal-playbook-author/scripts/{discover_playbook.py, validate_schema.py, detect_conflicts.py}` — cwd → ancestors → BFS 深度 5 → bundle fallback |
| Scripts | `legal-contract-review/scripts/{abac_filter.py, seed_baseline.py}` — rule-based gate matching + 解壓 baseline archive |
| Baseline | `legal-contract-review/assets/baseline-playbooks.tar.gz` — 8 條完整（含 LoL / Indemnification / DPA 三 variant-folder）+ `seed-manifest.yml` |
| Author 升級 | bootstrap mode 加 (a) 新增「seed 8 條 baseline」選項；偵測「需要 variants」trigger（user 答 walk_away 提到 deal_size / counterparty_type）|

### Quality gate

- ✅ Validator 跑 24 個 hand-crafted broken playbook 抓出 **24/24**（要求 ≥ 22）
- ✅ ABAC filter 對 12 個 deal_context 變項配對 **12/12 正確**（要求 ≥ 11）
- ✅ baseline seed 後立即跑 contract-review 0 error（seed_baseline.py 後所有
  17 檔 schema 驗證 PASS / detect_conflicts.py 0 conflict）

---

## Phase 1.6 — Eval 基建（v0.3.0） ✅ **DONE 2026-05-12** (scaffolding); dogfood calibration pending

**Scope**：定量驗證機制，**不新增 skill**。

**完成狀態**（commits 74cb60b → final on `feat/legal-toolkit-v0.1.0`）：
- ✅ answer-criteria.md 擴充：12 → 20 條（17 deterministic + 3 semantic）
- ✅ source-criteria.md 擴充：6 → 10 條（5 deterministic + 5 semantic）
- ✅ playbook-quality.md 新增：12 條（10 deterministic + 2 semantic）給 author 用
- ✅ self_grade.py：22 deterministic checks（17 ANS + 5 SRC）+ ANS-11 self-consistency
- ✅ 27 unit tests cover golden path + per-criterion mutation + TW vs non-TW branches
- ✅ docs/dogfood-procedure.md：5-10 contract calibration workflow + privacy guidance
- ✅ .gitignore：docs/dogfood-corpus/ never committed (sensitive)

### 交付物

| 模組 | 檔案 |
|---|---|
| Rubric | `legal-contract-review/checklists/answer-criteria.md`（20 條 binary，含 tier）|
| Rubric | `legal-contract-review/checklists/source-criteria.md`（10 條 binary，含 tier）|
| Rubric | `legal-playbook-author/checklists/playbook-quality.md`（12 條 author 用）|
| Eval harness | `legal-contract-review/scripts/self_grade.py` + 27 tests |
| Dogfood procedure | `docs/dogfood-procedure.md` — local-only calibration workflow + cohort table template |

### Quality gate

LLM self-grade 跟 hand-graded reference 在同份 dogfood 上：
- **answer_score** Pearson corr ≥ 0.6 （由 owner 跑 5-10 份合約計算）
- **source_score** Pearson corr ≥ 0.7（source_score 較好驗，binary citation valid/invalid）
- **Hallucinated citation rate = 0**（一條假案號即 hard fail，獨立於 Pearson）

Pearson calibration 跟 corpus 從不 commit 進 repo（sensitive contracts）；
owner 跑 `docs/dogfood-procedure.md` 流程，hand-grading 結果本機保存，
cohort summary table 可分享（aggregates only）。

---

## Phase 1.6.1 — Dogfood-driven patches（v0.3.1） ✅ **DONE 2026-05-12**

**Scope**：v0.3.0 dogfood 跑 2 份真實合約（NDA + SaaS reseller）+ 雙 subagent audit 後修補實質問題；**不新增 skill**。

**Trigger**：2026-05-12 dogfood independent audit caught:
1. SRC-09 escape via 營業秘密法 §11-1（fabricated sub-article）— 格式 check 通過但條號實際不存在
2. 個資法 §27 stale citation（2025-11 修法已刪除→§20-1）
3. Stance-asymmetry blind spot — playbook neutral defaults 在 stance-favorable 合約把「該有但沒有」flag 成 risk，redline 反過來主動拱手讓對方
4. False-negative on structural-but-quiet clauses (absent / terse / vague sub-mechanisms) — §2.2/§2.3 deemed-breach, §3.2 unpriced renegotiation, §4.4 audit vagueness 都漏抓
5. Citation over-reach（民法 §247-1 套 1-on-1 negotiated, 公平交易法 §25 缺 market-impact, 民法 §110 用錯方向）
6. Banner spam on all 5 user-facing files including memo-business + redline
7. Editorial parentheticals leaked into operative redline body
8. NDA mode 3-doc spec drift（SKILL.md vs L7 protocol vs self_grade.py）
9. findings.json 沒 schema

### 完成狀態（commits 9f2695a → 17fa0b2 → \<commit-3\> on `feat/legal-toolkit-v0.1.0`）

**commit 1** — protocols（feat/legal-toolkit）：
- L7 Step 1.5 stance-asymmetry pass（Q1+Q2 决定 EXPOSE vs PROTECT；downgrade favorable absences to green/strategic-note）
- L7 Step 9.1 editorial-parenthetical filter（strip amendment-history annotations from proposed_text body）
- L7 Step 9.2 redline split（stance_asymmetry_downgrade → internal_fallback only, not send_now）
- L7 Step 9.3 citation applicability gate（pre-flight check on §247-1 / 公平交易 §25 / §110 / §13-1 / §27→§20-1）
- L7 Step 9.4 headline rule for memo-business（severity ≥ yellow + concrete quantifiable downside + actionable in 30/60/90 days）
- L6 sub-check 4 vagueness scan（per-contract-type dimension table for 7 clause families）
- SKILL.md NDA mode dispatch fix + banner placement scope（memo-legal + escalation only）
- escalation-override.md HTML comment 更新 banner placement 規則

**commit 2** — scripts（feat/legal-toolkit）：
- assets/statute-articles.json — minimum viable blacklist（民法 §11-1 fabricated, 營業秘密法 §11-1 fabricated, 個資法 §27 / 個人資料保護法 §27 deleted 2025-11-11）+ applicability_notes
- self_grade.py SRC-04 tightened：format check + blacklist check（whitespace-tolerant match）
- 7 new SRC-04 blacklist tests → 113 → 120 tests total

**commit 3** — cleanup（chore/legal-toolkit）：
- output-schema-findings.json — new schema documenting the cross-cutting intermediate (consumed by self_grade.py); includes v0.3.1 additions (stance_asymmetry_check / cycle_check.vague_sub_mechanism / top_3_business_impacts shape / favorable_position_notes)
- output-schema-memo-business.json updated for top_3 + favorable_position_notes
- 4 baseline-fallback frontmatters add `statute_verified_at: 2026-05-12`
- plugin.json + marketplace.json + 3 READMEs version bump 0.3.0 → 0.3.1

### Quality gate

- ✅ 120/120 tests pass（27 + 7 new SRC-04 blacklist tests + 86 existing）
- ✅ Pearson calibration target (≥0.6 / ≥0.7) **carries forward to Phase 1.6** — v0.3.1 closes structural escapes but does not change the calibration requirement; owner still runs `docs/dogfood-procedure.md` on 5-10 contracts before Phase 1.6 is fully done

### Deferred to v0.3.3+ / Phase 1.7

- Comprehensive statute whitelist（main article range + sub-articles per statute）vs blacklist
- L6 vagueness scan Python helper (current = protocol reference for LLM)
- Bundled NDA-native fallback baselines（current 4 fallback 偏 SaaS-shaped；NDA §2.2/§2.3 deemed-breach cascade pattern 未涵蓋）
- ANS-21 stance_asymmetry_check 由 self_grade.py 從 protocol-only 升級到 semantic-tier rubric
- SRC-12 cases_verified[] whitelist check（current = protocol-level soft-citation rule, no deterministic enforcement）
- Asset identification pass Python helper / variant-aware asset patterns

---

## Phase 1.6.2 — Second-pass dogfood patches（v0.3.2） ✅ **DONE 2026-05-12**

**Scope**：v0.3.1 dogfood re-run（同樣 NDA + SaaS reseller 兩份合約）+ 雙獨立 audit 後修補剩餘 over-corrections；**不新增 skill**。

**Trigger**：2026-05-12 v0.3.1 verification dogfood，兩份合約 verdict 都 (c)→(b) but identified 3 remaining issues:

1. **Stance-asymmetry pass under-corrected for EXISTING favorable clauses** — v0.3.0 過 flag 甲方-favorable absences 為 risk；v0.3.1 正確不再 over-flag；但 v0.3.1 把已存在的 favorable clause（如 SaaS §2.3 5-day silence-consent / §1.6 甲方單方訂價 / §4.3 甲方單方退款 / §3.3 末段 wind-down）entirely droped。Auditor 評語：「invisible is worse than over-flagging」。
2. **L6 sub-check 3+4 與 L7 main loop overlap dedup 缺失** — NDA v0.3.0 / v0.3.1 都把 residual-knowledge 同時算入 #1 (confidentiality) + #6 (gap)，cosmetic note 但結構性 dup 仍在。
3. **Bundled fallback 案號 fabrication** — independent verification subagent 2026-05-12 跑了 8 個 case citations 對 https://judgment.judicial.gov.tw + 6law + TIPO + 行政法院裁判選輯 + 律師事務所評論，**7 / 8 likely fabricated**（zero index hits）。bundled assets 本身是 SRC-09 escape source；v0.3.0 NDA run 已 propagate 「智財法院 102 年度民營訴字第 6 號」進 memo-legal output。

### 完成狀態（commits 760d4e2 → 879171f → \<commit-3\> on `feat/legal-toolkit-v0.1.0`）

**commit 1** — protocols（feat/legal-toolkit）：
- L7 Step 0 — **Asset Identification Pass**（only when stance=ours）：scan L2-anatomy clauses for substance-advantages → favorable_position_notes[] + suppress finding emit + include "renewal-time floor" hint. Dual-nature clauses emit BOTH gap finding AND asset note。
- L7 Step 9.3.0 — **Soft case-citation rule**：禁止 LLM 直接 emit "X 年度 Y 字第 N 號" 除非 WebFetch-verified in session OR listed in `assets/statute-articles.json#cases_verified[]`. 鼓勵 softer formulations: 近年實務趨勢 / 司法院判決系統有多則相關案件 / 學者通說.
- L6 Step 2.5 — **Dedup overlap pass**：missing_expected_clause OR vague_sub_mechanism gap 與 L7 main-loop finding 在同 clause_id 重疊時 SUBSUMED into parent finding（不另 emit）.
- SKILL.md 新增 v0.3.2 三個 callout sections
- source-criteria.md SRC-09 rationale 更新

**commit 2** — bundled fallback case cleanup（fix/legal-toolkit）：
- 4 baseline-fallback-*.md 「## 相關判例」section → 「## 相關規範與學說參考」
- 7 fabricated case 全 REMOVED
- 1 unverifiable function letter (消保處 2018 函釋) 註記「請查證後引用」
- 替換為 statute + 王澤鑑 / 王文宇 commentary doctrine pointers
- frontmatter 加 `case_citations_verified_at: 2026-05-12`
- statute-articles.json $schema_version v0.3.1 → v0.3.2 + 新增 `cases_verified[]` placeholder

**commit 3** — version bump（chore/legal-toolkit）：
- plugin.json + marketplace.json + 3 READMEs v0.3.1 → v0.3.2
- ROADMAP §Phase 1.6.2 section + §版本策略 table

### Quality gate

- ✅ 120/120 tests still pass（protocols 為 LLM 規則，runtime-enforced via output；ANS-21 deferred）
- ✅ 0 fabricated case citation 留在 bundled fallback assets
- ✅ Pearson calibration target (≥0.6 / ≥0.7) **carries forward** — owner 跑 `docs/dogfood-procedure.md` 流程 still pending

---

## Phase 1.7 — bundled-vs-runtime architecture refactor（v0.3.3，5-7 天） ✅ **DONE 2026-05-12**

**Status**：✅ DONE 2026-05-12. Pre-Phase-2 architecture cleanup; **不新增 skill**。

### 完成狀態（commits 1c8a6ca → b5df284 → \<commit-5\> on `feat/legal-toolkit-v0.1.0`）

**Q-locks 全 lock**：
- Q-A：TTL with sensible defaults（30d statute / 7d case / 30d 函釋 / 365d applicability_notes）+ per-type override in config.yml
- Q-B：cache-then-fetch-then-LLM-with-warning + `runtime_verified: false` marker；不 silently substitute LLM training-data
- Q-C：main session WebFetch via LLM；Python only managing cache + URL construction
- Q-D：no cross-source conflict resolution；每種 citation 對應自己 source
- Q-E：soft cap 10 unique citations/run；configurable via `.legal-toolkit/config.yml`
- Q-F：scope = statute + case + 函釋 verify only；NO applicability enrichment / NO baseline trim → defer 到 v0.3.4+

**commit 1** — foundation: `assets/legal-sources.json` (12 statutes + 司法院判決 + 7 主管機關) + `assets/output-schema-citation-cache.json` + `scripts/cache_check.py` + 22 tests
**commit 2** — protocol: L7 Step 9.3.1 statute runtime fetch + applicability_caveat carry-through
**commit 3** — protocol: L7 Step 9.3.2 case + Step 9.3.3 function letter verify + `scripts/build_citation_url.py` + 21 tests
**commit 4** — schema: citations[].runtime_verified + cache_path + amendment_note + top-level runtime_fetch_summary + `assets/config.example.yml`
**commit 5** — cleanup: version bump 0.3.2 → 0.3.3 + this ROADMAP section + Timeline update

### Quality gate

- ✅ **163/163 tests pass** (120 從 v0.3.2 + 22 cache_check + 21 build_citation_url)
- ✅ **Zero 新 user-facing breakage** — schema additions all optional / additive
- ✅ **Privacy verified** — WebFetch sends only statute identifier / case number / agency name；NO contract text exfiltrated
- 🟡 **dogfood A/B 待跑** — pre/post Phase 1.7 on same 2 contracts；measure SRC-09 escape rate + latency delta + cache hit rate over multiple runs

### 仍 deferred（v0.3.4+ / Phase 1.8）

- Comprehensive statute whitelist（main range + sub-articles per statute）
- NDA-native fallback baselines（§2.2/§2.3 cascade liability pattern）
- ANS-21 stance_asymmetry_check semantic-tier rubric
- SRC-12 cases_verified[] whitelist deterministic check
- Bundled baseline trim（移走「為什麼這條重要」narrative 到 references/）
- Multi-jurisdiction runtime fetch（HK / CN / JP / US）
- Subagent-mode WebFetch（main-session fine for v0.3.3 scope；reserve for high-volume runs）

---

**Trigger**：2026-05-12 conversation surfaced an architectural question after Phase 1.6.2 case-citation cleanup. v0.3.2 verification subagent found 7 / 8 bundled judicial case citations likely fabricated. Even if every remaining bundled citation is verifiable today, the architecture relies on **bundle-time correctness** that drifts with:

- Legislative amendments (個資法 §27 → §20-1 example, caught manually 2025-11-11)
- Judicial supersession / 解釋 / 變更見解
- Administrative function letter revocation
- Commentary evolution（學者見解 shift）

The bundled approach makes the toolkit **frozen at ship date**. v0.3.1 added `statute_verified_at` + v0.3.2 added `case_citations_verified_at` frontmatter, but those are passive markers — they don't refresh themselves. ROADMAP §Phase 6 plans Q1 drift-check; Phase 1.7 brings the runtime layer forward so Phase 2-5 skills inherit the cleaner architecture from day one.

### Two-tier separation (proposed)

| Content type | Current location | Phase 1.7 target | Why |
|---|---|---|---|
| **Walk-away triggers** | bundled fallback frontmatter | **stay bundled** | Pure policy — no government source can adjudicate red-line opinions |
| **Preferred / Fallback positions** | bundled fallback body | **stay bundled** | Same — company-specific negotiation stance |
| **替代條款文字 (sample substitute clause)** | bundled fallback body | **stay bundled, slim** | Template policy; could be parameterised but offline-runnable today |
| **Statute § number (e.g. 民法 §247-1)** | bundled (+blacklist v0.3.1) | **stay bundled** as reference, **runtime verify** at emit time | § identifier is stable enough; freshness verification at emit-time |
| **Statute internal text** | LLM training-data recall | **runtime fetch** law.moj.gov.tw | Closes wording drift + amendment hidden bugs |
| **Statute applicability** | bundled (applicability_notes v0.3.1) | **stay bundled, expand** | Doctrinal — community-curated; not refetchable per query |
| **Judicial case citations** | bundled (v0.3.0-1 had 7 fabricated; v0.3.2 removed) | **runtime fetch** judgment.judicial.gov.tw at emit + `cases_verified[]` whitelist | Already enforced by v0.3.2 L7 Step 9.3.0 soft-citation rule; Phase 1.7 adds the fetcher |
| **Administrative function letter (函釋)** | bundled (1 unverifiable) | **runtime fetch** if a primary URL exists, else mark `unverifiable` | Similar to case — verify at emit, don't ship plausible-but-stale |
| **「## 為什麼這條重要」 narrative explanation** | bundled fallback body | **move to references/ OR runtime-generate** | Explanatory text changes when commentary evolves; ~20-25% of bundled content |
| **「## 相關規範與學說參考」 references** | bundled fallback body (v0.3.2 cleaned) | **slim further** — keep statute references; commentary author list moves to references/<topic>.md | Loosely coupled — author list / book editions update independently |

### Q-locks (all locked, see Phase 1.7 commits)

- **Q-A** ✅：TTL with sensible defaults — 30d statute / 7d case / 30d 函釋 / 365d applicability_notes；per-type override in config.yml
- **Q-B** ✅：cache-then-fetch-then-LLM-with-warning + `runtime_verified: false` marker；never silently substitute LLM training-data recall as if verified
- **Q-C** ✅：main session WebFetch via LLM；Python only managing cache + URL construction (subagent-mode deferred to v0.3.4+)
- **Q-D** ✅：no cross-source conflict resolution needed — each citation type verifies its own source
- **Q-E** ✅：soft cap 10 unique citations/run；configurable via `.legal-toolkit/config.yml`；overflow → `runtime_fetch_skipped: true`
- **Q-F** ✅：scope = statute + case + 函釋 verify only；NO applicability enrichment / NO baseline trim → defer 到 v0.3.4+

### Tentative deliverables

| 模組 | 檔案 |
|---|---|
| Runtime fetcher | `legal-contract-review/scripts/fetch_statute.py` (WebFetch + cache + freshness + offline fallback) |
| Runtime fetcher | `legal-contract-review/scripts/verify_case.py` (judgment.judicial.gov.tw search + structural check) |
| Cache | `.legal-toolkit/cache/{statutes,cases,function_letters}/<id>.json` (gitignored at user level; CI ephemeral) |
| Schema | `assets/output-schema-citation-verification.json` — runtime-verified citation shape |
| Protocol update | L7 Step 9.3.0 already references `cases_verified[]`; expand to active runtime-verify; mention `statute_verified_at` carry-through to citation metadata |
| Baseline trim | Move 「## 為什麼這條重要」+「## 相關規範與學說參考」 narrative out of bundled fallback bodies into `references/clause-<id>-context.md`; bundled keeps walk-away + preferred + fallback + substitute text only |
| Skill update | `legal-playbook-author` learns the same fetch protocol (so user-authored playbook entries also benefit) |
| Tests | runtime fetch unit tests + offline fallback + cache behaviour + structural integration test with mocked WebFetch |

### Quality gate

- Pre vs post Phase 1.7 dogfood A/B on same 2 contracts (NDA + SaaS reseller)：
  - **Citation hygiene** (SRC-09 escape rate) — Phase 1.7 should reduce to **0** unverified case / 函釋 citations
  - **Latency** — bounded WebFetch budget; document delta（estimate ≤ +30s per run）
  - **Offline behaviour** — degrade gracefully; emit `runtime_verified: false` markers; do NOT silently substitute training-data recall
- Bundled fallback slimming target：each baseline-fallback-*.md ≤ 60 lines（v0.3.2 average 80-90 lines after case removal）

### Deferred from Phase 1.7 (explicit non-scope, → v0.3.4+ / Phase 1.8)

- **Comprehensive statute whitelist** in `statute-articles.json` — Phase 1.7 closed the bundled-vs-runtime split; the whitelist's article-range enumeration is independent value
- **NDA-native fallback baselines** — orthogonal scope；carries over from Phase 1.6.2 Deferred
- **ANS-21 stance_asymmetry_check semantic rubric** — orthogonal
- **SRC-12 cases_verified[] whitelist** deterministic check (currently soft-citation rule at protocol level)
- **Bundled baseline trim**（移走「為什麼這條重要」narrative 到 references/clause-<id>-context.md）
- **Multi-jurisdiction runtime fetch** (HK / CN / JP / US) — TW-only in Phase 1.7
- **Subagent-mode WebFetch** — main session sufficient for v0.3.3 scope；reserve for high-volume runs

### Risk

- **WebFetch rate-limiting on law.moj.gov.tw / judgment.judicial.gov.tw** — fetch budget Q-E mitigates; cache TTL strategy (Q-A) decisive
- **Privacy / data-leak** — runtime fetch only sends statute / case identifiers (no contract text) to external servers; document this clearly in README "Data flow"
- **Network failure mode regression** — Q-B offline behaviour critical; should NOT make the toolkit useless when offline (it's a tool, not a service)
- **Cost** — each /legal-contract-review run becomes more expensive (N × WebFetch latency + token cost for fetched content); document baseline cost delta in dogfood A/B

---

## Phase 2 — Template + Runbook（v0.4.0，10 天）

**Scope**：+2 skill → 累計 **5**。

### 交付物

| Skill | 主要模組 |
|---|---|
| `legal-document-draft` | SKILL.md / 4 mode protocols（privacy / tos / dpa / nda）/ `assets/template-{privacy,tos,dpa,nda}.md`（含 GDPR + 個資法 2025/11 hardcode）/ `checklists/compliance-{pdpc,gdpr}.md` / 跟 `.legal-toolkit/config.yml` profile 整合（公司資訊不重問）|
| `legal-incident-response` | SKILL.md / protocols/{detect,analyze,contain,recover}.md（NIST SP 800-61 r3）/ `assets/template-{pdpc-notification,authority-reply,breach-remedy}.md` / 72hr timer 機制（Claude Code mode 顯示倒數；Cowork mode 用 deadline marker）|
| Router 更新 | `using-legal-toolkit` 識別表 active 標記 + Q2/Q3 dispatch path |

### Quality gate

- draft privacy policy 跑 PDPC 2025/11 checklist ≥ 90% pass
- IR 個資外洩演練從 trigger 到輸出 PDPC 通報文 < 30 秒
- 兩個 skill 都正確讀 `.legal-toolkit/config.yml` profile 不重問

---

## Phase 3 — IRAC cluster（v0.5.0，8-12 天）

**Scope**：+2 skill → 累計 **7**。

### 交付物

| Skill | 主要模組 |
|---|---|
| `legal-issue-spot` | SKILL.md / protocols/{parse-facts,timeline,spot-issues,subsumption,counterfactual,risk-grade}.md / `references/{請求權基礎-民法.md, 構成要件-勞動.md, 構成要件-個資.md}` / `assets/output-schema-issue-matrix.json` |
| `legal-research` | SKILL.md / protocols/{plan,iterative-search,triangulate,cite}.md / Agent 能力（plan-adapt-interact）/ `scripts/fetch_{moj,judicial,authority}.py`（全國法規 / 司法院 / 主管機關 RSS）/ document-level citation 強制 |
| Router 更新 | Q4 dispatch path（fact-driven → issue-spot / 查法源 → research） |

### Quality gate

- issue-spot 拿 5 個已知 case fact pattern 跑出 issue 矩陣 + 構成要件涵攝結論跟資深法務 hand-graded 70% 對齊
- research 對 5 個法律問題跑 iterative search 三角驗證後，引用 ≥ 8 個有效 source 且 source 跟 conclusion 有 supporting relationship

---

## Phase 4 — Tracker cluster（v0.6.0，10 天）

**Scope**：+2 skill → 累計 **9**。

### 交付物

| Skill | 主要模組 |
|---|---|
| `legal-contract-tracker` | SKILL.md / `scripts/{extract_metadata.py, build_db.py, schedule_alerts.py}` / SQLite or YAML 本機 DB / `assets/output-schema-{upcoming-deadlines,obligations-status}.json` / 自動續約日 / 終止 notice / obligations due / 價格調整觸發點 alert |
| `legal-regulation-watch` | SKILL.md / Agent 能力 / `scripts/{rss_poll.py, summarize.py, impact_assess.py}` / 監看 PDPC / 勞動部 / 立院 / 金管會 / 證交所 / cross-ref playbook 變動建議（呼叫 author revise）|
| Router 更新 | Q5 dispatch path |

### Quality gate

- contract-tracker 對 10 份歷史合約 metadata 抽取 accuracy ≥ 85%
- regulation-watch 跑 30 天 RSS poll，false-positive alert（無關變動）< 20%

---

## Phase 4.5 — 上市櫃 Compliance Prerequisite Research（10-15 天，可從 Phase 2 後 parallel）

> ⚠️ **Phase 5 BLOCKER** — design note §9 + research outline `<obsidian-vault>/research/2026-05-09 上市櫃 in-house Compliance 工作流深度研究——大綱與議題清單.md` 已寫成，70-100 工時。

**Scope**：寫獨立 research note（**不**寫 skill 程式），動工後才能 unblock Phase 5。

### 交付物

| 模組 | 內容 |
|---|---|
| Primary interview | 3-5 位上市櫃 in-house GC 訪談（議題：股東會 vs 董事會差別 / 重大訊息揭露決策樹 / 配合 DD 三類場景）|
| Research note | `2026-05-XX 上市櫃 in-house Compliance 工作流深度研究.md`（1500-2000 行，10 個必答核心問題）|
| Sub-research | 重大訊息揭露三層 decision tree + 案例集 / 個資法 2025/11 對 governance template 影響 |

### Quality gate

10 個核心問題每個都有 ≥ 2 個 primary source（GC 訪談 or 公開揭露案例 or 主管機關函釋）+ confidence MEDIUM 以上。

---

## Phase 5 — Compliance cluster（v0.9.0，10-15 天）

**Scope**：+2 skill → 累計 **11**（complete）。

**前置條件**：Phase 4.5 research note 完成。

### 交付物

| Skill | 主要模組 |
|---|---|
| `legal-corporate-governance` | SKILL.md / 3 mode protocols（股東會 / 董事會 / 重大訊息）/ `assets/checklist-{shareholders-meeting,board-meeting,material-disclosure}.md` / `assets/template-{議事手冊,議案模板,揭露文模板}.md` / 公司法 §172 / §192 / 證交法 §36 / TWSE 處理程序 hardcode / 跟 regulation-watch hook（規範變動 → 自動 flag template 更新）|
| `legal-dd-quickscan` | SKILL.md / 3 scenario（IPO / 配合併購 / 配合投資 DD）/ 30-50 項 checklist / 6 大領域 scan（公司結構 / 合約 portfolio / 勞動 / IP / 訴訟 / 稅務內控）/ `assets/output-schema-dd-findings.json` |
| Router 更新 | Q6 dispatch path active |

### Quality gate

- corporate-governance 跑一場真實股東會議事手冊 → 公司法 §172 checklist 100% pass
- dd-quickscan 對 1 家上市櫃公司資訊跑 IPO 場景 → 跟外部律師 DD report 30 項對照 ≥ 25 項一致

---

## Phase 6 — 治理機制（v1.0.0 GA，持續）

**Scope**：不新增 skill，補長期維運機制。

### 交付物

| 模組 | 內容 |
|---|---|
| Drift detection | `scripts/drift_check.py` — 對歷史合約 retro 跑當前 playbook，計算 deviation 數變化趨勢；季度自動跑 |
| Annual reminder | playbook entry `last_updated` > 180 天時 contract-review session start 強制 warn |
| Cross-playbook benchmark | `scripts/benchmark.py` — 個人 playbook vs WorldCC 2024 industry baseline + SpotDraft + ContractKen 對照 |
| Multi-playbook inheritance（v2 schema 預留實作）| 個人 + 公司 + 客戶律所三層 inheritance；schema 已預留 |
| CI gate | drift between bundled fallback / disclaimer / escalation override 三 skill 內容 byte-identical check |
| Docs polish | 完整 3-lang README rewrite / case study × 5 / migration guide / FAQ |

### GA criteria

- 11 skill 全 dogfood pass rate ≥ 80%
- drift detection 抓出 ≥ 1 個真實 stale entry
- marketplace metadata 完整（plugin.json + marketplace.json + 3 lang README）
- 至少 3 個外部 user 跑過完整 flow 回饋

---

## Critical Path & Dependencies

```
                                       ┌──────────────────────┐
                                       │ Phase 4.5 Research   │  parallel
                                       │ (上市櫃 GC interview)│  可從 P2 後起跑
                                       └─────────┬────────────┘
                                                 ↓
P1 (MVP) ─→ P1.5 (DSL) ─→ P1.6 (Eval) ─→ P2 ─→ P3 ─→ P4 ─→ P5 ─→ P6 (GA)
   3 skill    +baseline    +rubric      +2     +2     +2     +2    polish
   8-12d      5d           3-5d         10d    8-12d  10d    10-15d ongoing
```

### 關鍵依賴

- **P1.5 必 after P1**：DSL refactor 需要 working shell
- **P1.6 必 after P1.5**：rubric 需要穩定 schema 才能評
- **P2-P4 之間**理論可平行但建議接力（context switching 成本）
- **P5 必 after P4.5 Research**：design note §9 BLOCKER
- **P6 必 after P5**：drift detection 對 sparse playbook 沒意義

---

## 版本策略

| 版本 | 觸發點 | 對使用者意義 |
|---|---|---|
| v0.1.0 | Phase 1 ship | 「能用，但 playbook 你要自己寫」cold-start fallback 4 條當 demo |
| v0.2.0 | Phase 1.5 ship | 「有 8 條 baseline + ABAC + validator」 |
| v0.3.0 | Phase 1.6 ship | 「我可以自評跟你 hand-grade 對齊」 |
| v0.3.1 | Phase 1.6.1 dogfood patch | 「不會在 stance-favorable 合約把優勢拱手讓人；citation hygiene 更嚴」 |
| v0.3.2 | Phase 1.6.2 second-pass dogfood | 「主動識別合約內 favorable 條款轉成 asset；7 個 fabricated 案號從 bundled fallback 清除；L6/L7 dedup」 |
| v0.3.3 | Phase 1.7 architecture refactor | 「條文 / 案號 / 函釋 runtime fetch + verify；TTL-based cache；offline-graceful；citation drift 不再靠手動 verified_at；163/163 tests」 |
| v0.4.0 | Phase 2 ship | 「合約 + 起草 + 應變」 |
| v0.5.0 | Phase 3 ship | 「+ 諮詢 + 研究」 |
| v0.6.0 | Phase 4 ship | 「+ lifecycle + 法規追蹤」 |
| v0.9.0 | Phase 5 ship | 「+ 公司治理 + DD」(complete features) |
| v1.0.0 | Phase 6 GA | 「全 11 skill + 治理機制 + 3-user 真實驗證」 |

**Semver semantics**：Phase 1.X 內微調 = patch；新 skill = minor bump；schema breaking 在升 v1.0.0 前不算 breaking（pre-GA）。

---

## Risk Callouts

| Risk | 影響 | Mitigation |
|---|---|---|
| Phase 4.5 上市櫃 GC primary interview 約不到人 | Phase 5 永遠 blocked | 用次佳 source（公開揭露案例 + 法律期刊 + GC 公開演講 transcript）退而求其次；接受 confidence LOW 動工 + 後續補訪談 |
| Phase 1.6 rubric Pearson corr 跑不到 0.6 | 無法定量驗 contract-review 品質 → Phase 2-5 都是「感覺對」| 先 ship MVP；rubric 跟 dogfood corpus 邊用邊加，3-5 輪迭代後通常會 converge |
| 個資法 2025/11 新制條文細節未 lock | draft / IR / DPA playbook 都受影響 | Phase 2 動工前再 verify 一次主管機關函釋；draft template 設成可配置欄位 |
| LLM 對中文 instruction following 在 long pipeline 跳步 | contract-review 七層 L1-L7 跑不完整 | 英文骨架 + Q-B 雛形 (ii) 動工後 5 份合約 dogfood A/B 驗證；跳步 > 20% 就回頭把 SKILL.md 寫更英文化 |
| Phase 4 regulation-watch RSS 來源不穩 | false-positive alert 過多 | v1 用 pull-based polling + LLM 去重，避免 push subscription 依賴；v2 才考慮 connector |
| `escalate_to` bundled fallback 佔位符使用者懶得改 | escalation.md 永遠含「[請編輯]」字串 → disclaimer 失效 | Phase 1.6 rubric 加 binary check「escalate_to 是否含 [請編輯]」，failed_criteria 列出來壓 user |

---

## 估時 summary

| 模式 | 估時 |
|---|---|
| Focused mode（每天 6-8 小時專注） | **~60-80 工作天 = 3-4 個月** |
| Part-time（每週 10-15 小時） | **~6-8 個月** |
| Phase 4.5 平行 | 可省 10-15 天 → 約 1.5-2 週 |

---

## 明確排除（不會做的，design note §9）

- ❌ 訴訟策略 / 複雜談判
- ❌ General legal assistant
- ❌ Word add-in
- ❌ 證交所 / 金管會系統整合 / e-mail 打通
- ❌ 收費 / SLA 化變成 service（保持「免費工具」定位 → 不踩律師法 §48）

---

## 相關文件

- **Design note (SoT)**：`<obsidian-vault>/research/2026-05-09 法務 Agent Skill (legal-toolkit) 整體架構與執行流程設計.md`（1344 行）
- **Source research**：
  - `2026-05-07 法務工作流與思考方法論——Agent Skill 設計研究.md`（1570 行）
  - `2026-05-07 Harvey.ai 法務 AI 產品方法論深度研究.md`（586 行）
  - `2026-05-09 法務 Contract Playbook 深度研究——從 BigLaw 到 Agent Skill 的設計原語.md`（1605 行）
- **Phase 5 prerequisite research outline**：`<obsidian-vault>/research/2026-05-09 上市櫃 in-house Compliance 工作流深度研究——大綱與議題清單.md`
- **Repo convention**：`monkey-skills/CLAUDE.md`（skill folder structure / two-layer spec / quality gates）
