# Research: does separating "reading critic" and "executing tester" into independent agents beat one combined agent?

## Sources checked

### AgentCoder (Huang et al., 2312.13010) — [measured] — https://arxiv.org/abs/2312.13010 (2023/2024)
**Compared**: single agent generating both code AND tests (same conversation) vs. AgentCoder's multi-agent design with a separate Programmer agent and Test Designer agent (plus a Test Executor). Section 4.7 (RQ6), Tables 6-7.
**Measured**: pass@1 and test accuracy on HumanEval and MBPP.
**Result**: Single agent: HumanEval pass@1 71.3%, MBPP 79.4%; test accuracy 61.0% (HumanEval) / 51.8% (MBPP). Multi-agent (separate test designer): HumanEval pass@1 79.9%, MBPP 89.9%; test accuracy 87.8% (HumanEval) / 89.9% (MBPP).
**Interpretation given by authors**: tests written by the same agent that wrote the code inherit that agent's blind spots/logical flaws ("tests... can be biased by the code and lose objectivity"); a same-agent tester is a weaker adversary than an independent one.
**Caveat**: This compares "one agent writes code+tests" vs "two agents, one codes one tests" — both roles here are test-writing/execution ("executing tester"), not a reading-critic vs executing-tester split. It IS a direct, clean ablation on separation itself, just for the tester role, not the reviewer-vs-tester distinction specifically.

### ChatDev (Qian et al., 2307.07924) — [measured, indirect] — https://arxiv.org/abs/2307.07924 (2023)
**Compared**: full chat-chain (with Reviewer and Tester phases/roles) vs. ablations removing phases (e.g., removing the "Code Complete"/testing phase, removing "communicative dehallucination", removing role assignment).
**Measured**: completeness, executability, and other CSC (code statistics) metrics.
**Result**: testing phase is "critical for Executability"; removing role assignment from all agents caused the largest performance drop.
**Caveat**: This is an ablation of *phases/roles present vs absent*, not a controlled comparison of "one agent doing reviewer+tester" vs "two separate agents doing reviewer and tester" — it does not isolate the specific question of merged-vs-separate. Insufficient data on this exact contrast from ChatDev.

### MetaGPT (Hong et al., 2308.00352) — [measured, indirect] — https://arxiv.org/abs/2308.00352 (2023)
**Compared**: presence/absence of the QA Engineer role (which does executable testing) among the 5 roles (PM, Architect, Project Manager, Engineer, QA Engineer).
**Measured**: revisions needed, executability.
**Result**: adding non-Engineer roles (including QA Engineer) "consistently improves both revisions and executability."
**Caveat**: This is role-presence ablation (Engineer alone vs full team), not a merged-vs-separate reviewer/tester comparison. MetaGPT does not appear to have a "Reviewer" role distinct from "QA Engineer" that was ablated against merging them — insufficient data on the specific reading-critic vs executing-tester separation question.

### "Is Self-Repair a Silver Bullet for Code Generation?" (Olausson et al., 2306.09896, ICLR 2024) — [measured] — https://arxiv.org/abs/2306.09896
**Compared**: self-feedback (same model critiques/reads its own code and repairs it) vs. feedback from a separate, stronger model (GPT-4) vs. feedback from a human expert programmer — all three then feed the SAME repair step.
**Measured**: pass rate after repair, accounting for sampling budget.
**Result**: self-repair gains are "often modest" and inconsistent across datasets; substituting a weaker model's self-generated feedback with a stronger model's feedback "significantly improved performance"; human-expert feedback further increased the number of repaired programs passing all unit tests.
**Interpretation**: this is squarely about "same agent reads/critiques its own output" vs "an independent (and/or stronger) agent reads and critiques it" — i.e., separation of the READING/critiquing role from the generator. It found separation (especially with a stronger critic) helps, and that the bottleneck is feedback QUALITY, not the repair step itself.
**Caveat**: This paper's critic is still a "reading" critic (natural-language feedback), not an "executing" one — it doesn't itself contrast reading-critique vs execution-based testing, nor does it test having both a critic AND a tester as two separate agents vs merged.

### Self-Collaboration Code Generation via ChatGPT (Dong et al., 2304.07590) — [insufficient data via this search] 
Not independently re-verified in this pass beyond prior general knowledge; the paper's roles (Analyst/Coder/Tester) are structural but I did not find a specific ablation isolating "Tester merged into Coder" vs "Tester separate" with reported numbers in this search session. Flagging as insufficient data rather than asserting a result.

### Basili & Selby (1987), "Comparing the Effectiveness of Software Testing Strategies" — [measured] — https://www.semanticscholar.org/paper/Comparing-the-Effectiveness-of-Software-Testing-Basili-Selby/3953558e92b1397c778cd450b4ca58da45932bcc (1987)
**Compared**: code reading by stepwise abstraction vs. functional testing vs. structural testing, done by 32 professional programmers + 42 students on 4 unit-sized programs.
**Measured**: fault-detection effectiveness, cost, and fault classes detected — NOT separation of who performs which technique (this is a within-subject/between-subject technique comparison, not an org-design "separate person vs combined person" study).
**Result**: code reading was as effective as (or better than) functional/structural testing for detecting faults, and relative effectiveness depended on program/fault type. This paper is about TECHNIQUE choice (reading vs testing), not about whether the same person/agent should do both vs different people.
**Caveat**: does NOT directly address "separate individuals for reading vs testing" vs "one person does both" — it addresses which technique finds which faults.

### Wood, Roper, Brooks & Miller (1997), "Comparing and Combining Software Defect Detection Techniques" — [measured] — https://link.springer.com/chapter/10.1007/3-540-63531-9_19 (1997)
**Compared**: same three techniques (code reading, functional testing, structural testing) as Basili & Selby, replicated with 47 student subjects.
**Measured**: failures observed, faults found, when techniques applied individually vs. in combination (aggregating results across different applications of the techniques).
**Result**: (a) individual techniques broadly similar effectiveness; (b) relative effectiveness depends on program/fault nature; (c) techniques are "consistently much more effective when used in combination."
**Caveat**: "Combination" here means applying multiple detection techniques (by the same or different subjects) and pooling the faults found — it argues techniques are complementary (found different faults), which is suggestive that a reading-based check and an execution-based check catch different bugs. But like Basili & Selby, this is not a controlled "1 agent doing both roles" vs "2 independent agents/people, one per role" comparison — no experiment condition explicitly varies whether the SAME person did both techniques vs different people did each. Insufficient data on the person-separation question specifically; the paper is about technique complementarity.

### Anthropic — "When to use multi-agent systems (and when not to)" — [opinion/guidance, not measured ablation] — https://claude.com/blog/building-multi-agent-systems-when-and-how-to-use-them (2026)
**Content**: describes a "generator-verifier" pattern (one agent produces, a separate verifier agent checks and can reject with feedback, looping back). States three general conditions where multi-agent beats single-agent: context pollution, parallelizable tasks, tool-selection specialization. Also states multi-agent systems use 3-10x more tokens and are often over-applied where a single well-prompted agent would do as well.
**Tag**: [opinion] — general design guidance, not a controlled ablation of reviewer-vs-tester separation specifically. Does not report a number for "separate reviewer + tester" vs "combined."

## What is actually established
- AgentCoder gives a clean, numeric ablation: an independent test-writing agent beats the same agent writing both code and tests (pass@1 +8.6pp HumanEval, +10.5pp MBPP; test accuracy +26.8pp / +38.1pp) — but this splits code-writer from test-writer, not reviewer from tester.
- Olausson et al. show that an independent (esp. stronger) *critic* that only reads/feeds-back beats self-critique for the repair step — evidence that separating the READING/judging role from the generator specifically helps, because self-critique shares blind spots with self-generation.
- Human-SE literature (Basili & Selby 1987; Wood et al. 1997) establishes that reading-based and execution-based defect-detection TECHNIQUES are complementary, finding different fault classes and being more effective combined.
- ChatDev and MetaGPT ablations show reviewer/tester roles help versus no such role at all, but don't isolate merged-vs-separate.

## What is NOT established
- No source found gives a direct, numeric, controlled comparison of "one agent doing BOTH reading-review AND execution-testing" vs "two independent agents, one reviewing by reading and one testing by executing," holding everything else fixed.
- Human-SE studies compare technique effectiveness, not whether the same person vs different people should apply them — that specific organizational-separation question is not answered by Basili/Selby or Wood et al.
- No LLM-as-judge study was found directly comparing "judge that reads code" vs "judge that reads+runs tests" reliability with numbers in this pass (not found; flagging as insufficient data rather than searched exhaustively).
