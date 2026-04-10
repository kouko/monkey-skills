# Risk Assessment (Shared Standard)

Risk-based testing vocabulary and decision criteria for qa-team. Both worker
(when writing risk register) and evaluator (when reviewing) reference this file.

## Default: ISTQB Risk Level = Likelihood × Impact

From ISTQB CTFL v4.0.1 §5.2 Risk-Based Testing:

> **Risk Level = Likelihood × Impact**

This is the standard, two-dimensional formula applicable to all project types.
Each risk item is a tuple:

```
Risk ID | Description | Likelihood | Impact | Risk Level | Mitigation | Test Case Ref
```

### Likelihood Factors

Evidence-based estimation of how likely the risk is to occur:

- **Code complexity** — cyclomatic complexity, nesting depth, coupling
- **Developer familiarity** — first-time contributors, rotated teams
- **Technology novelty** — new frameworks, new language features, new infrastructure
- **Defect history** — prior incidents in this area or similar code
- **Third-party dependencies** — stability, update frequency, community support
- **Change scope** — number of files/modules touched

### Impact Factors

Evidence-based estimation of consequences if the risk materializes:

- **Financial loss** — revenue impact, refund liability, penalty exposure
- **Reputational damage** — user-visible failures, press exposure, trust erosion
- **Safety/compliance** — regulatory violation, physical harm, data breach
- **Users affected** — count, criticality of affected segments
- **Business criticality** — revenue path, core vs auxiliary feature
- **Reversibility** — can the damage be undone?

### Risk Level Matrix (3×3 default)

| | Low Impact | Medium Impact | High Impact |
|---|---|---|---|
| **High Likelihood** | Medium | High | **Critical** |
| **Medium Likelihood** | Low | Medium | High |
| **Low Likelihood** | Low | Low | Medium |

Projects requiring finer resolution may use 5×5. The matrix is **not a formula**
for test effort — it is a prioritization aid. Critical and High risks must have
at least one test case; Medium risks should; Low risks may.

## Opt-in: FMEA RPN for Safety-Critical Systems

For safety-critical, embedded, medical, automotive, or aerospace systems,
ISTQB Advanced Level Test Manager Syllabus §1.3.5 allows an upgrade to FMEA:

> **RPN = Severity × Occurrence × Detectability**

From JSTQB Advanced Level Test Manager Syllabus V3.0.J01 §1.3.5 (verbatim):

> 故障モード影響解析(FMEA)とその派生：品質リスク、その潜在的な原因、および
> 影響する度合いを識別し、重要度、優先度、および検出率を割り当てる。

English gloss: "Failure Mode and Effects Analysis (FMEA) and its derivatives:
identify quality risks, their potential causes, and the degree of impact, and
assign severity, priority, and detection rate."

### FMEA Decision Criteria — When to Upgrade

Use FMEA RPN **instead of** ISTQB L×I when any of these apply:

- Regulatory compliance requires FMEA (ISO 26262, IEC 60812, ISO 13485, DO-178C)
- Safety-of-life consequences are possible
- Hardware/firmware components are involved
- Customer contract explicitly requires FMEA
- Detection difficulty is a primary design concern (e.g., silent data corruption)

For non-safety-critical software (web, mobile, enterprise SaaS), stay with
ISTQB L×I. FMEA adds process overhead without proportional benefit.

## Japanese Context Note

In the Japanese enterprise QA community, FMEA is widely used in manufacturing
(see 機械振興協会 and METI references) but limited in web/enterprise software
QA, which primarily uses JSTQB's qualitative L×I matrix. This matches the
default/opt-in split above.

## Risk Register Format (for TEST-PLAN.md)

```
| ID | Description | L | I | Level | Mitigation (test case) |
|----|-------------|---|---|-------|------------------------|
| R-01 | Payment retry loop may double-charge | H | H | Critical | TC-PAY-003 |
| R-02 | Login rate-limit bypass via header injection | M | H | High | TC-AUTH-012 |
```

Likelihood / Impact abbreviated as H/M/L purely as a shorthand for the
matrix cells — the underlying semantics are ISTQB L×I, **not** self-invented
severity levels.

## Sources

- [ISTQB CTFL Syllabus v4.0.1 §5.2 Risk Management](https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf) — primary source for Risk Level = Likelihood × Impact
- [JSTQB Advanced Level Test Manager Syllabus V3.0.J01 §1.3.5](https://jstqb.jp/dl/JSTQB-Syllabus.Advanced_TM_VersionV30.J01.pdf) — FMEA reference
- [ASTQB — 5.2 Risk Management](https://astqb.org/5-2-risk-management/) — secondary summary
- [IEC 60812 — FMEA standard](https://webstore.iec.ch/publication/26359) — international FMEA standard
- [機械振興協会 FMEA 解説](https://www.jspmi.or.jp/system/l_cont.php?ctid=130402&rid=816) — Japanese manufacturing FMEA context
- [Qbook — リスクベーステスト解説](https://www.qbook.jp/column/1779.html) — Japanese QA community risk-based testing primer
