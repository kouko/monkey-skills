# Quality Philosophy (Shared Standard)

Foundational beliefs about quality that shape qa-team's approach to test
planning. Referenced by SKILL.md persona and by workers writing TEST-PLAN.md.

## Core Tenet — 品質は工程で作り込む

**Quality is built into the process, not bolted on after.**

This is the foundational principle of post-war Japanese QA, originating in the
TQC (Total Quality Control) movement influenced by Deming, Juran, and Ishikawa.
It rejects the notion that inspection finds defects — it asserts that a good
process does not produce them.

Related concepts:
- **源流管理 (gen-ryū kanri)** — manage at the source
- **次工程はお客様 (next process is the customer)** — each stage serves the next
- **設計レビュー (design review)** — upstream verification as first-class activity

For qa-team this means:
- Test planning begins during requirements/design, not after code exists
- Viewpoint extraction happens before test case writing (see `test-viewpoints-ja.md`)
- Participation in design reviews is a QA activity, not an engineering courtesy
- A TEST-PLAN.md that cannot pass DR is incomplete

## Relationship to Shift-Left (Western framing)

The Western "shift-left" movement, per Carnegie Mellon SEI, means "beginning
testing as early as practical in the lifecycle." It identifies four types:
Traditional, Incremental, Agile/DevOps, and Model-based.

Shift-left and 品質は工程で作り込む are **the same idea, named differently**.
The Japanese framing has ~70 years of institutional history in manufacturing
QA; the Western framing has ~15 years in software. Use whichever term fits
your audience — they are operationally equivalent.

## Observability as Non-Functional Quality

Non-functional testing (performance, reliability, scalability) requires
observability infrastructure to verify. qa-team's non-functional test plans
should reference the three complementary measurement frameworks:

### SLI / SLO / SLA — Google SRE

From *Site Reliability Engineering* (O'Reilly, 2016), Chapter 4:

| Term | Definition |
|------|------------|
| **SLI** (Service Level Indicator) | A quantitative measure of some aspect of service level (latency, error rate, throughput, availability) |
| **SLO** (Service Level Objective) | A target value or range for an SLI over a time window |
| **SLA** (Service Level Agreement) | An explicit contract with users, including consequences of missing SLOs |

Use SLIs/SLOs to define what "passing" means for non-functional acceptance
tests. Example: "P99 latency < 200ms over any 5-minute window" is an SLI+SLO;
"API returns the correct response" is not.

### RED Method — Tom Wilkie (2015)

From the Grafana Labs blog: "his popular talk about the RED Method of
monitoring microservices, which he created in 2015."

Applied to **request-driven services** (HTTP/RPC endpoints):

- **R**ate — requests per second
- **E**rrors — failed requests
- **D**uration — time per request (distribution with percentiles)

### USE Method — Brendan Gregg (2013)

From the 2013 ACM Queue article "Thinking Methodically about Performance."

Applied to **infrastructure resources** (CPUs, memory, disk, network):

- **U**tilization — average time the resource was busy
- **S**aturation — degree of extra work queued beyond current capacity
- **E**rrors — count of error events

Gregg's statement of the method: "For every resource, check utilization,
saturation, and errors."

### How they fit together

```
SLI/SLO/SLA  (user-facing contract)
       ↓
RED  (request-driven service behavior)
       ↓
USE  (resource-level root cause when RED flags a problem)
```

Use SLI/SLO to define what "healthy" means to users. Use RED to measure
service-level behavior. Use USE to diagnose resource bottlenecks when RED
flags a problem. They are **complementary, not competing**.

## Implications for Test Planning

1. **Non-functional test cases must cite an SLI** — not "should be fast" but
   "P99 latency < 200ms over any 5-minute window"
2. **Observability is a prerequisite, not an afterthought** — test plans for
   services with performance SLOs must include RED instrumentation requirements
3. **Infrastructure tests use USE** — capacity planning and bottleneck
   identification reference Gregg's three metrics per resource type

## Sources

### Japanese quality tradition
- [テクノファー — TQM 連載 #10 (工程で品質を作り込む)](https://www.technofer.co.jp/iso/iso-tqm10/)
- [tebiki — 品質の作り込み](https://tebiki.jp/genba/useful/build-quality-method/)
- [ものレボ — 品質は工程で造り込む](https://monorevo.jp/standard/article/quality_built_in_process.html)

### Shift-left (Western framing)
- [Carnegie Mellon SEI — Four Types of Shift Left Testing](https://www.sei.cmu.edu/blog/four-types-of-shift-left-testing/)
- [Qbook — DevOps × シフトレフト](https://www.qbook.jp/column/1460.html) — Japanese-language framing

### Observability primary sources
- [Google SRE Book Ch. 4 — Service Level Objectives](https://sre.google/sre-book/service-level-objectives/)
- [Google Cloud Blog — SRE fundamentals: SLAs vs SLOs vs SLIs](https://cloud.google.com/blog/products/devops-sre/sre-fundamentals-slis-slas-and-slos)
- [Grafana Labs — The RED Method: How to Instrument Your Services (2018)](https://grafana.com/blog/2018/08/02/the-red-method-how-to-instrument-your-services/) — cites "which he created in 2015"
- [GrafanaCon EU 2018 — Tom Wilkie, The RED Method (PDF)](https://grafana.com/files/grafanacon_eu_2018/Tom_Wilkie_GrafanaCon_EU_2018.pdf)
- [Brendan Gregg — The USE Method](https://www.brendangregg.com/usemethod.html)
- [Brendan Gregg — Thinking Methodically about Performance (ACM Queue 2013)](https://queue.acm.org/detail.cfm?id=2413037)
