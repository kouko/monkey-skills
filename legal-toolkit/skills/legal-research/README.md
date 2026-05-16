# legal-research

Read this in: **English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

![version](https://img.shields.io/badge/version-0.1.0-blue) ![license](https://img.shields.io/badge/license-MIT-green) ![phase](https://img.shields.io/badge/phase-3_SP3--b-orange)

> ⚠️ **Not legal advice.** Free open-source utility, not a law firm. Output is 法律意見 (legal opinion) for in-house 法務 internal reference only — escalate to a licensed 律師 (lawyer) for any matter with criminal exposure, regulator-facing risk, cross-border element, or material business impact. Every output ships with the §6.3 Mandatory Disclaimer footer (see below).

IRAC research Agent skill for Taiwan in-house 法務. Takes a free-text legal lookup query (條文號 / 判例編號 / 法律問題) and runs a plan-first 半互動 (semi-interactive) Agent loop — LLM drafts a search plan → user confirms Y/n → autonomous WebFetch + triangulation across 4 法源類型 (條文 statutes / 判決 court judgments / 函釋 administrative interpretations / 學說 academic doctrine) → Harvey doc-level citation memo. No `profile.yml` dependency.

## When to use

- Literal law-text lookup — e.g. 「§227 是什麼？」/「民法 §184 構成要件」/「個資法 §27 適當安全措施」
- 判決 / 判例 趨勢 search — e.g. 「民國 110 年後 不完全給付 carve-out 判決趨勢」
- 函釋 or 學說 reference search — e.g. 「PDPC §27 函釋」/「王澤鑑 不完全給付 通說」

## When NOT to use

- **Fact-pattern analysis** (「我們想做 X，能不能做？」) → use `legal-issue-spot` (v0.5.0)
- **Contract review** (existing contract file or pasted clause text) → use `legal-contract-review`
- **Document drafting** (通知函 / 警示函 / 終止合約信) → use `legal-document-draft`
- **Incident response** (already-happened breach / received 主管機關 letter) → use `legal-incident-response`

## Input format

- **Required at session**: `--query="<NL query>"` — a free-text legal lookup question (typically 1-3 lines)
- **No structured schema** — query string is treated as opaque; `protocols/plan.md` extracts ≥ 3 keywords + ≥ 2 target sites + 法源類型 plan in Step 1
- **No `profile.yml` dependency** — analysis is query-driven, not company-identity-driven (router Q4-law-lookup bypasses the profile prerequisite check used by `legal-document-draft` / `legal-incident-response`)

```bash
/legal-research --query="不完全給付 §227 carve-out 民國 110 年後判決趨勢"
```

## Output format

Per session, writes to `<cwd>/legal-outputs/<YYYY-MM-DD-HHmm>-research-<topic>/`:

| File | Audience | Sections |
|---|---|---|
| `plan.md` | 法務 + 業務 (reproducibility checkpoint) | §問題 / §關鍵字 / §目標 site / §法源類型 plan / §Budget / §Disclaimer |
| `state.json` | machine (grader + LLM loop) | rounds / fetches / sources[] / types_covered{} / early_stop / forced_stop / timestamps |
| `research-memo.md` | 法務 / GC / internal sign-off | §問題 / §搜尋摘要 / §法源分析 / §結論 / §Citations (Harvey doc-level) / §Disclaimer (+ conditional ⚠️ block prepended) |
| `executive-summary.md` | non-法務 (CEO / BD / 業務 / PM) | §問題 / §結論 (✅/⚠️/❌) / §依據 / §風險提示 / §Disclaimer (+ conditional §Escalation) |

Schema validation: `plan.md` / `research-memo.md` / `executive-summary.md` / `state.json` have JSON Schema contracts in `assets/plan-schema.json` / `assets/output-schema-memo.json` / `assets/output-schema-summary.json` / `assets/state-schema.json`, all consumed by `scripts/grade_research.py`.

## Plan-first 半互動 contract

Before any fetch budget burns, the skill emits `plan.md` and asks the user to confirm. This is **mandatory**, non-skippable, and patterned after the v0.4.2 SP3b `classify-path` Y/n precedent:

1. LLM parses `--query=...` and emits `plan.md` to disk
2. LLM prints the full `plan.md` content to stdout as a preview
3. LLM prompts: `Plan OK 嗎? (Y/n)` — exact zh-TW string, no variations
4. **Y** → enter the autonomous Agent loop (`protocols/iterative-search.md`)
5. **n** (or any non-Y) → skill exits with `plan.md` on disk; user revises query and re-invokes

Rationale (Q5 locked): `plan.md` is a cheap reproducibility checkpoint before the expensive 30-fetch budget is committed. User controls token cost; auto-dispatch would silently burn budget on a plan the user might not need.

## Agent loop cap

The loop is LLM-driven with deterministic state tracking via `state.json` (Python only persists state; the LLM re-reads `state.json` at the top of each iteration and decides whether to continue, early-stop, or force-stop).

Cap parameters (centralized in `assets/triangulation-config.json`):

- **Hard cap**: ≤ **5 rounds** OR ≤ **30 fetches** → sets `forced_stop=true`
- **Early-stop**: ≥ **8 sources** AND ≥ **2 法源類型** covered → sets `early_stop=true`
- **Forced-stop ⚠️ marker**: when the cap is hit without early-stop, `protocols/triangulate.md` prepends a `⚠️ 覆蓋未達 triangulation` block above `§問題` in `research-memo.md`. Forced stop is NOT a failure mode — it is the safety net. The grader treats `forced_stop + ⚠️ marker` as exit code 2 (`PASS_WITH_NOTES`), NOT exit 1 (`FAIL`).

## Cross-skill handoff (INBOUND only)

When `legal-issue-spot/business.md` 構成要件 涵攝 (statutory-element subsumption) table contains ≥ 1 ⚠️ (low-confidence), its `§建議下一步` block emits concrete `/legal-research` commands for the user to copy:

```markdown
- §227 不完全給付的 carve-out 認定
  → `/legal-research --query="不完全給付 §227 carve-out 民國 110 年後判決趨勢"`
```

This is a **soft handoff** — the user copies the command and invokes `/legal-research` themselves; no auto-dispatch (Q8 locked). The `--query=...` string is treated as opaque input (no schema validation against issue-spot vocabulary; lets either side evolve independently). **Reverse handoff (research → issue-spot) is intentionally NOT implemented** per Q8 design lock — router Q4 catches misrouted fact-pattern queries upstream.

## §6.3 Disclaimer footer

Every output `.md` file MUST end with the §6.3 Disclaimer footer (canonical text in `protocols/cite.md`). Body covers: AI-tool attribution / not formal legal opinion / current TW in-force law scope / recommendation to consult 律師 for litigation, contract signing, criminal liability, cross-border, or high-stakes decisions. The grader greps for the canonical sentinel substring; missing footer → exit 1 (FAIL). This skill produces 法律意見 — disclaimer is mandatory, not optional.

## §6.4 Escalation Override

When `state.json.forced_stop == true` OR the query domain involves **刑事 / 訴訟 / 跨境 / 重大金額**, `executive-summary.md` MUST contain a `§Escalation` section with an explicit 律師 consultation recommendation. This is **hard-wired**, not an LLM judgement call — `protocols/cite.md` emits the §Escalation banner with fixed-format text; the LLM does not get to soften or skip it. Grader rule: `forced_stop=true` without §Escalation → exit 1 (FAIL).

## References

- Full skill instructions: [`SKILL.md`](SKILL.md)
- Design spec: [`docs/superpowers/specs/2026-05-15-legal-toolkit-phase3-irac-cluster-design.md`](../../../docs/superpowers/specs/2026-05-15-legal-toolkit-phase3-irac-cluster-design.md) §6
- Plugin spec: [`legal-toolkit/PRODUCT-SPEC.md`](../../PRODUCT-SPEC.md) + [`legal-toolkit/TECH-SPEC.md`](../../TECH-SPEC.md)
- ROADMAP: [`legal-toolkit/ROADMAP.md`](../../ROADMAP.md)
