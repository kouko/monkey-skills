# Protocol — risk-grade

Final synthesis step of the 6-protocol pipeline. Reads the four prior
sections of `issues.md` (`§事實摘要` / `§Issue 矩陣` / `§構成要件涵攝` /
`§反事實`), produces the **風險分級** (🔴/🟡/🟢), applies the §6.4
**Escalation Override** logic (hard-wired, not LLM judgement), appends
the §6.3 **Mandatory Disclaimer** footer to BOTH output files, and
synthesizes `business.md` (audience-shaped 業務本位 view).

## Purpose

This is the SYNTHESIS step. Earlier protocols extract / spot / subsume /
counterfactual; this protocol grades + escalates + disclaims +
audience-shapes. The LLM does NOT re-run analysis here — it reads
prior sections, applies the rules table below, and writes outputs.

## Inputs

Read all four sections from `issues.md`:

- `§事實摘要` — for business.md TL;DR + §可以做/不能做/注意點 phrasing
- `§Issue 矩陣` — for cross-statute scope (criminal-law detection)
- `§構成要件涵攝` — for ⚠️ count + 該當/不該當 distribution (drives risk + escalation + handoff)
- `§反事實` — for carve-out flippability (drives 🟡 vs 🟢 boundary)

**Halt + ask fallback** — if any of the four sections is missing or empty:

```
⚠️ risk-grade halt — 缺少必要前置 section：
  - missing: <list of missing section names>
  - 必須先重跑：<該 section 對應的 protocol>
請補齊後再執行 risk-grade.md。
```

Do NOT fabricate missing inputs; halt and report which prior protocol must re-run.

## Outputs

This protocol writes to **multiple destinations** (two files, several sections each):

| File | Section | Source |
|---|---|---|
| `issues.md` | `§風險分級` | risk grade emoji + 1-2 line reasoning |
| `issues.md` | `§Disclaimer` | §6.3 boilerplate (verbatim, see §Disclaimer text below) |
| `business.md` | `# Business 觀點 — <fact pattern 簡述>` | header from §事實摘要 |
| `business.md` | `## §TL;DR` | 1-2 paragraph 業務本位 總結 |
| `business.md` | `## §可以做的部分` | bullets derived from 該當 + carve-out applicable rows |
| `business.md` | `## §不能做的部分` | bullets derived from 不該當 / 該當-無 carve-out rows |
| `business.md` | `## §注意點` | bullets derived from ⚠️ rows + counterfactual flippable carve-outs |
| `business.md` | `## §風險分級` | 同 issues.md, 1-line reasoning |
| `business.md` | `## §建議下一步` | **conditional** — when ≥ 1 ⚠️ in `§構成要件涵攝` |
| `business.md` | `## §Escalation` | **conditional** — when 🔴 OR ≥ 2 ⚠️ OR criminal element |
| `business.md` | `## Disclaimer` | §6.3 boilerplate (verbatim, same as issues.md) |

## Risk-grade rules

Read `§構成要件涵攝` table + `§Issue 矩陣` + `§反事實`. Apply this table top-down (first match wins):

| Condition | Grade |
|---|---|
| 任一 issue 落入 **刑事法** territory (e.g. 刑法 §339 詐欺 / §342 背信 / §201 偽造 / 證交法 §171 / 個資法 §41 五年以下有期徒刑 條款) | 🔴 |
| `§構成要件涵攝` 包含 **≥ 2 ⚠️** (after counterfactual re-grading) | 🔴 |
| 任一 critical 構成要件 = **不該當** 且該結論 reverses 商業期望結果 (i.e. 業務想做的事 因此不能做) | 🔴 |
| `§構成要件涵攝` 包含 **恰好 1 ⚠️** AND 無刑事元素 AND 結論為 conditional (carve-out 取決於事實具體形貌) | 🟡 |
| `§反事實` flagged 一個或多個 flippable carve-outs (微小事實變動 → 結論反轉) AND 無刑事元素 AND 無不該當 reversal | 🟡 |
| 全部 該當 (or 全部 不該當 但符合業務期望) AND 無 ⚠️ AND 無刑事元素 AND `§反事實` 未標記 flippable carve-out | 🟢 |

If multiple rules trigger, **higher severity wins** (🔴 > 🟡 > 🟢).

Output to `issues.md §風險分級`:

```markdown
## §風險分級

🟡 — <1-2 line reasoning citing 構成要件 row + 反事實 carve-out by name>
```

The emoji MUST be exactly one of 🔴 / 🟡 / 🟢 (single character; grader regex checks).

## §6.4 Escalation Override

**Hard-wired logic — NOT LLM judgement.** The LLM does not get to "soften"
or skip this. Trigger conditions (any of):

- 風險分級 = 🔴
- `§構成要件涵攝` contains ≥ 2 ⚠️
- 任一 issue 涉及刑事法 territory

When triggered, `business.md` MUST contain `## §Escalation` section with:

- Explicit 律師 (執業律師 / 外部 counsel) consultation recommendation
- Transparent reasoning (which trigger fired — show user, don't hide)
- Phrasing: "建議於採取行動前諮詢執業律師" (or equivalent zh-TW)

Template:

```markdown
## §Escalation

⚠️ 本案達成 §6.4 升級門檻，**強烈建議於採取任何行動前諮詢執業律師**。

升級觸發原因：
- <list which trigger fired: ≥ 2 ⚠️ / 🔴 grade / 刑事法 issue>
- <1-line elaborate, e.g. "§227 + 個資法 §27 兩個構成要件信心不足，疊加風險">

律師可協助：
- 釐清不確定之構成要件涵攝
- 評估特定案件之判決趨勢與主管機關函釋走向
- 規劃具體 risk mitigation 步驟（書面意見 / 合約條款調整 / 內控程序設計）
```

Rationale (per SKILL.md §6.4 inherited from v0.4.x SoT): when low
confidence intersects high stakes, disclaimer alone is insufficient —
non-lawyer audience needs an explicit "stop and talk to a lawyer" signal.

## §6.3 Disclaimer text

Verbatim boilerplate appended to BOTH `issues.md` and `business.md`. The
text below IS the canonical version for this skill — do NOT paraphrase
when emitting; copy verbatim so grader's `disclaimer_footer` check
passes:

```markdown
---

## Disclaimer

本分析由 AI 工具（legal-toolkit / legal-issue-spot）產出，**不構成正式法律意見**。本工具：

- 僅就現行有效之中華民國法律進行 issue spotting + 構成要件 涵攝；
- 不能取代具有律師資格之專業諮詢；
- 對特定案件之適用性、判決趨勢、最新主管機關函釋未即時涵蓋；
- 不保證內容無誤、完整或最新。

具體案件如涉及訴訟、契約簽訂、刑事責任、跨境議題、或重大金額決策，請諮詢專業律師。
```

Both files end with this block. The leading `---` separator is part of
the boilerplate.

## Cross-skill handoff format

When `§構成要件涵攝` contains **≥ 1 ⚠️** (any low-confidence element),
`business.md` MUST contain `## §建議下一步` section emitting concrete
`/legal-research` query strings — one per ⚠️ row.

Template:

```markdown
## §建議下一步

⚠️ 以下構成要件信心不足，建議跑 research 釐清：

- <Issue 名稱> 的 <構成要件 element name>
  → `/legal-research --query="<具體 NL 查詢字串>"`

- <next ⚠️ row...>
  → `/legal-research --query="..."`
```

**Format constraints** (grader-enforced):

- Query string MUST be wrapped in single backticks
- MUST match regex `` `\`/legal-research --query="[^"]+"\`` ``
- Query content is **opaque** to the grader — write a useful NL query
  (keywords + 法源 + relevant 條文 + scope hint), not a dummy

This is a **soft handoff** — user copies command + invokes themselves;
no auto-dispatch (Q8 locked). Reverse handoff (research → issue-spot)
NOT implemented.

## business.md output template

Skeleton the LLM fills in. Conditional sections only included when their
trigger fires (see Outputs table above):

```markdown
# Business 觀點 — <fact pattern 簡述, ≤ 30 字>

## §TL;DR

<1-2 paragraph 業務本位 總結 — 結論 first, 不堆 jargon, 不重複 issues.md 的法條編號>

## §可以做的部分

- <bullet derived from 該當 + carve-out applicable row>
- <next bullet...>

## §不能做的部分

- <bullet derived from 不該當 / 該當-無 carve-out row>
- <next bullet...>

## §注意點

- <bullet derived from ⚠️ row OR counterfactual flippable carve-out>
- <next bullet...>

## §風險分級

🟡 (or 🔴 / 🟢) — <1-line reasoning, 同 issues.md 但更白話>

[conditional — only if ≥ 1 ⚠️ in §構成要件涵攝]
## §建議下一步

⚠️ 以下構成要件信心不足，建議跑 research 釐清：

- <issue> 的 <element>
  → `/legal-research --query="..."`

[conditional — only if 🔴 OR ≥ 2 ⚠️ OR 刑事元素]
## §Escalation

⚠️ 本案達成 §6.4 升級門檻，**強烈建議於採取任何行動前諮詢執業律師**。

升級觸發原因：
- <which trigger fired>
- <1-line elaborate>

律師可協助：
- <list>

## Disclaimer

<§6.3 boilerplate verbatim>
```

Drafting discipline: zh-TW user-facing strings; do NOT translate
domain terms (構成要件 / 涵攝 / 不完全給付) into English; keep §
references short (`民法 §227`, not the full 條文 quote — canonical SoT
owns that).

## Worked example

Fact pattern (from §事實摘要): "我們想送一份員工生日禮物（500 元蛋糕券）給客戶聯絡人，能不能做？"

`§構成要件涵攝` extract:

| 構成要件 | 涵攝結論 | 信心 |
|---|---|---|
| 民法 §184 侵權行為 - 不法性 | 不該當 | HIGH |
| 個資法 §5 蒐集原則 - 必要性 | 該當 | HIGH |
| 公司治理 利益衝突 - 公務員贈與門檻（非公務員 contact）| ⚠️ | LOW |

`§反事實`: 若聯絡人為公務員 → 公職人員利益衝突迴避法 §15 五百元門檻適用，結論反轉。

**Risk grade** — 1 ⚠️ + carve-out flippable (聯絡人身份) + 無刑事元素 → **🟡**

**Escalation** — 1 ⚠️ < 2 ⚠️ AND grade ≠ 🔴 AND 無刑事元素 → **NOT triggered** (no §Escalation section)

**Handoff** — 1 ⚠️ ≥ 1 → **§建議下一步 REQUIRED**

Snippet of business.md output:

```markdown
## §風險分級

🟡 — 一般客戶聯絡人贈與本身合規，但若聯絡人為公務員身份則觸發利益衝突迴避法門檻，需確認對方身份。

## §建議下一步

⚠️ 以下構成要件信心不足，建議跑 research 釐清：

- 公司治理 利益衝突的「公務員贈與門檻」適用範圍
  → `/legal-research --query="公職人員利益衝突迴避法 §15 五百元門檻 民間企業贈與適用範圍"`

## Disclaimer

<§6.3 boilerplate>
```

End of risk-grade protocol.
