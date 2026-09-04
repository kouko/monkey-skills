# Research: reviewer (reconciliation) vs adversary (executable negative truth) positioning

Date: 2026-09-04. Compiled from web search (EN + JP). Every claim below is tagged
[measured] (empirical data) or [opinion] (practitioner/vendor claim, no measurement).
Where no source was found, this is stated as "insufficient data" rather than guessed.

---

## Q1 — Does the industry already split "reading for reconciliation/consistency" vs "executing for failure"?

**Findings**

- Mäntylä & Lassenius (2009), *"What Types of Defects Are Really Discovered in Code Reviews?"*, IEEE TSE 35(3), 430-448 — classified 388 industrial (C/C++) + 371 student (Java) review-found defects. **75% of defects found in review do not affect visible functionality**; they are "evolvability" defects (readability, maintainability, structure) rather than functional bugs. [measured]
  https://dl.acm.org/doi/abs/10.1109/TSE.2008.71 (also: https://aaltodoc.aalto.fi/bitstreams/cab054e8-0c06-47ab-8754-54bb09a0a6d3/download)
- Bacchelli & Bird (2013), *"Expectations, Outcomes, and Challenges of Modern Code Review"*, ICSE 2013, pp.712-721 (Microsoft study) — reviewers were surveyed/observed and review comments classified. **Finding defects is the stated motivation but is not the dominant actual outcome**; the dominant activity is "code and change understanding" — reviewers spend most effort building a mental model of what changed and why, not executing it. Review also drives knowledge transfer and team awareness. [measured]
  https://www.microsoft.com/en-us/research/publication/expectations-outcomes-and-challenges-of-modern-code-review/
- ISO/IEC/IEEE 29119 series explicitly separates **static testing (reviews, walkthroughs, static analysis)** from **dynamic testing (execution)**: 29119-2's process model covers only dynamic test processes; static testing is deliberately pushed out to the companion standard ISO/IEC 20246, which "complements 29119 with guidance for static testing (reviews and static analysis)." This is a standards-body institutional split of the same reading-vs-executing line. [opinion/standard, not measured — but authoritative]
  https://www.iso.org/obp/ui/en/#!iso:std:81291:en ; https://quality.arc42.org/standards/iso-iec-ieee-29119 (2013/2022)
- Fagan inspection (1976, IBM) vs testing: industry reports (IBM) that structured inspection finds **80-90% of defects** at much lower cost-per-defect than finding the same class of defect in later testing/maintenance (10-100x cost multiplier cited for later-phase fixes). This is a decades-old separate-lane precedent (inspection = reading against a spec; testing = executing). [opinion/practitioner report — original IBM figures are widely cited but the search did not surface a controlled re-measurement]
  https://en.wikipedia.org/wiki/Fagan_inspection
- Security literature: **secure code review** ("dives into logic, architecture, code patterns... finds business-logic flaws, IDORs, auth issues that pattern-matching misses") vs **penetration testing** ("finds exploitable configurations and attack vectors in the running system... weak auth, index-exposure issues only visible at runtime"). Multiple vendor sources agree the two catch different, non-overlapping defect classes and recommend using both, not substituting one for the other. [opinion, consistent across independent vendors, not a controlled study]
  https://www.scnsoft.com/security/web-applications-security-source-code-review-vs-penetration-testing ; https://stonefly.com/blog/secure-code-review-enterprise-sast-dast-iast-guide/
- JP sources converge on the same split informally: review finds typos, logic contradictions, missing edge-case handling, and **spec-interpretation mismatches** ("仕様の解釈違い"), i.e. reconciliation-shaped defects, while execution-based testing is treated as the complementary lane. [opinion]
  https://crexgroup.com/ja/development/project/code-review-checklist/

**Implication for the proposed positioning**: **Supports.** There is a long-standing, cross-domain (SE standards, security, empirical SE research) precedent for splitting verification into a reading/reconciliation lane and an executing/failure lane, and multiple independent measurements agree the two lanes surface substantially different defect classes (evolvability/consistency defects for reading vs functional/exploit defects for execution) — which matches the observed empirical motivation (adversary's 4 findings all executable boundary cases; 4 of the reviewers' 6 findings were non-executable prose/process defects).

---

## Q2 — Is "every review/bug finding becomes a regression test" an established practice?

**Findings**

- Google: "no bug is considered properly fixed without an automated regression test" — described as a near-religious policy that emerged from Google's internal testing-culture turnaround (Mike Bland/Bharat Mediratta), reported via Google Testing Blog history and secondary accounts. [opinion/institutional-policy claim, not an RCT, but a stated organizational rule]
  https://testing.googleblog.com/2011/02/how-google-tests-software-part-three.html ; https://medium.com/@ivan.boklach/from-oh-no-to-go-go-go-the-hilarious-history-of-how-google-learned-to-test-3c0a3360f761
- SQLite: documented practice ("How SQLite Is Tested") states it is "good coding practice when a bug is located and fixed, to record a test that exposes the bug and re-run that test regularly after subsequent changes." SQLite is known for an unusually large regression-test-to-code ratio built substantially this way. [opinion/documented practice, not a controlled study]
  https://www.sqlite.org/testing.html
- "Test-Driven Bug Fixing" (TDB) is a named, widely-written-about practice: write a failing test that reproduces the bug **before** touching the fix, confirm it fails, fix, confirm it passes — explicitly framed as "this becomes your regression test." Multiple independent practitioner write-ups (O'Reilly's TDD book chapter, Evolveum, dev.to) describe the same procedure convergently. [opinion, converging across independent sources, no controlled measurement of value found]
  https://www.oreilly.com/library/view/test-driven-development/9781941222997/f_0132.html ; https://evolveum.com/test-driven-bugfixing/
- Security "detection engineering" runs the identical pattern one layer up: a found vulnerability/finding is turned into a **Semgrep/CodeQL rule** so the same bug class is caught automatically on the next occurrence/component; one case study explicitly evaluates rule quality by testing it against known CVEs (ground truth), i.e., finding → committed, re-runnable check → regression coverage. [measured in the narrow sense of "rule redetects known CVEs", opinion for the general practice]
  https://cc-sw.com/using-codeql-and-semgrep-to-assist-vulnerability-research-part-1-of-6/
- MITRE ATT&CK-based detection engineering: the same "finding becomes a committed, re-runnable check" discipline appears as "detection-as-code" — rules are versioned, code-reviewed, CI-checked, and validated against simulated attacks (e.g., Atomic Red Team), explicitly because "detections you cannot diff, review, or roll back are detections you will eventually break without noticing." This generalizes the graduation path (probe → committed → validated → re-run) beyond unit tests to security detections. [opinion, industry-consensus framing]
  https://www.securityscientist.net/blog/how-to-detection-engineering-2/
- JP sources confirm the same norm in more generic terms: regression testing is run after bug fixes/each test phase, and CI is expected to gate on it ("CIパイプラインで自動テストを通過しない限り本番へは出さないルールにするのが有効"), with "修正をカバーするテストを恒久的に追加することが重要" (permanently adding a test that covers the fix is important). [opinion]
  https://www.ripla.co.jp/blog/system/it-system-bug-fixing-process/

**Implication for the proposed positioning**: **Supports.** "Finding → committed, re-runnable check" is an established, convergent practice across unrelated domains (Google/SQLite unit-test culture, TDD literature, security detection engineering). No source found that treats this graduation path as optional or harmful; the practice generalizes cleanly to "reviewer's important finding gets encoded as an adversary probe in the fix round."

---

## Q3 — In multi-agent LLM coding systems, how are reviewer/critic vs tester/test-designer roles separated?

**Findings**

- **AgentCoder** (arXiv 2312.13010, 2023) uses three explicit agents: Programmer, **Test Designer** (writes test cases independent of the implementation, "to keep objectivity and avoid being biased... by incorrect code"), and **Test Executor** (runs code against the test suite in a sandbox, reports pass/fail). This is a direct precedent for "adversary owns executable truth, independent of the implementer," and the paper's own stated rationale for separating test generation from code generation is bias-avoidance — structurally the same argument as writer≠judge. [measured: reports 96.3%/91.8% pass@1 on HumanEval/MBPP vs baselines' 90.2%/78.9%, though this measures the framework's end result, not the role-separation ablation specifically]
  https://arxiv.org/abs/2312.13010
- **ChatDev** uses a 7-role pipeline CEO→CPO→CTO→Programmer→**Reviewer**→**Tester**→Designer — Reviewer and Tester are already distinct roles in a shipped multi-agent framework. **MetaGPT** similarly assigns a distinct QA Engineer role alongside Architect/Engineer, using structured document exchange (not freeform chat) between roles. [opinion/architecture description, not a role-separation ablation]
  https://smythos.com/developers/agent-comparisons/metagpt-vs-chatdev/ ; https://arxiv.org/html/2308.00352v6
- LLM-as-judge vs execution-based verification literature converges on: **execution-based checks answer functional correctness but miss efficiency/structure/style; LLM-as-judge (reading) covers those broader qualitative dimensions but "most papers agree LLMs struggle to judge if code works without running it."** i.e., the two methods are reported as covering different, non-substitutable ground — reading-based judgment is not a replacement for execution, and vice versa. [measured, per-paper findings synthesized across a benchmarking literature: CodeJudgeBench, "LLM-as-a-Judge for Software Engineering", etc.]
  https://arxiv.org/pdf/2507.10535 ; https://arxiv.org/pdf/2510.24367
- Anthropic's own multi-agent engineering guidance (2026) is the most load-bearing counter-signal here (see Q4): it names "planner → implementer → tester → reviewer" role-splitting **by work type** as an anti-pattern causing coordination overhead ("subagents spent more tokens on coordination than on actual work") and a "telephone game" effect, recommending splitting by **context boundary** instead (the agent that builds a feature should also write its own tests). This is about who writes the *positive* tests (recommends: the implementer, via TDD) — it does not directly address a post-hoc, fresh-context reviewer/adversary checkpoint pair, but it is relevant tension. [opinion, single vendor engineering blog, not a controlled study]
  https://claude.com/blog/building-multi-agent-systems-when-and-how-to-use-them

**Implication for the proposed positioning**: **Partially supports.** AgentCoder is a strong, structurally identical precedent (independent test-designer role, justified by objectivity/bias-avoidance — matching "writer≠judge"). ChatDev/MetaGPT show reviewer and tester already being treated as separate roles in shipped systems, though without an ablation proving separation beats a combined role. The LLM-as-judge-vs-execution literature supports "these two methods catch different things," which is the core empirical claim behind the split. The one piece of friction (Anthropic's anti-pattern warning) is about *who writes positive tests during implementation* (recommends implementer-owns-tests, i.e., TDD — which the proposed design already keeps: "Positive executable checks... belong to the implementer's TDD, not the reviewer"), not about the post-hoc verification checkpoint, so it does not contradict the proposal as scoped — but it does argue against ever asking the *reviewer* to write positive tests, which the proposal already avoids.

---

## Q4 — Counter-evidence: is the split harmful, or should reviewers write tests / adversaries judge design?

**Findings**

- Code review checklists broadly **recommend the reviewer run the code** ("pull the code onto their own machine, run it, interact with the feature, try to break it," "reviewer should run tests when possible, and if a test fails, find out why before approving"). This is in tension with a reviewer role defined as purely reading/reconciling — multiple independent checklist sources treat "run it yourself" as a core reviewer responsibility, not an adversary-only activity. [opinion, convergent across independent checklist authors, no measurement of value-add over reading alone]
  https://onenine.com/code-review-checklist/ ; https://www.michaelagreiler.com/code-review-checklist-2/
- yegor256, *"Does Code Review Involve Testing?"* (practitioner blog) argues the opposite direction from a conflict-of-interest angle: reviewers and testers have **structurally competing incentives** (devs are rewarded for merging, testers for finding defects), so a reviewer should not personally write/run tests but should instead escalate concerns about weak tests and hold the review — i.e., an argument *for* keeping reviewer and tester/adversary roles separated, on incentive grounds rather than skill grounds. [opinion, single practitioner]
  https://www.yegor256.com/2019/12/03/testing-in-code-review.html
- Anthropic's "planner/implementer/tester/reviewer as anti-pattern" (already cited in Q3) is the clearest counter-signal found: splitting verification-adjacent roles **by work type** was measured (in their internal experiment) to burn more tokens on coordination than on task work, and is framed as a "telephone game" that degrades information fidelity across handoffs. Their recommended fix is splitting by context boundary, not eliminating role separation altogether — but it is real evidence that role-splitting has a coordination cost that must be weighed against the diversity-of-defect-class benefit found in Q1–Q3. [opinion, one vendor's internal experiment, not published with methodological detail]
  https://claude.com/blog/building-multi-agent-systems-when-and-how-to-order-them (see Q3 citation)
- No source was found arguing the adversary role should judge design/architecture quality, nor any source arguing reviewers should be barred from ever running code (the checklist consensus is actually the reverse — reviewers are commonly told to run code). **Insufficient data** on any source directly opposing "reviewer does reconciliation, adversary does executable negative truth" as a *conceptual* split; the friction found is about whether the reviewer should also personally execute things, not about whether the two verification jobs should exist as separate roles.

**Implication for the proposed positioning**: **Partially contradicts.** The strongest counter-evidence is (a) mainstream code-review checklists that expect the reviewer to run the code themselves (blurring "reviewer owns reconciliation only, never executes"), and (b) Anthropic's measured coordination-overhead warning about splitting agent roles by work type. Neither source argues the adversary should judge design or that findings shouldn't graduate to tests; both are narrower frictions (reviewer-should-also-run-things; role-splits-have-real-coordination-cost) that the proposed design can absorb — e.g., by treating the reviewer's role as "reconciliation-first, may consult execution evidence the adversary already produced" rather than "must never touch execution."

---

## Bottom line

Q1 and Q2 are well-supported by convergent, partly-measured evidence: reading-based review and execution-based testing/pentesting reliably surface different defect classes (Mäntylä & Lassenius 2009: 75% evolvability, not functional), and "important finding becomes a committed, re-runnable check" is an established cross-domain norm (Google, SQLite, TDD, detection engineering). Q3 has a strong direct LLM-agent precedent (AgentCoder's independent Test Designer, justified by bias-avoidance — structurally identical to writer≠judge) plus corroborating evidence that reading-judgment and execution-based verification are non-substitutable. Q4's real counter-evidence is narrower than a full contradiction: mainstream review checklists expect reviewers to also execute code, and Anthropic reports a measured coordination cost to splitting agent roles by work type — both are absorbable frictions, not refutations of the core split. Net: the proposed positioning is supported by the literature, with two caveats worth naming in the contract text (reviewer may still consult execution evidence; role-splitting has a real coordination cost to be managed, not ignored).
