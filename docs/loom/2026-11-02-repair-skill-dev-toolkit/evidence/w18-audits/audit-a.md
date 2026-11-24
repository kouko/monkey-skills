# W18 Replay Audit — Source-Grounded Decisions

## Per-Candidate Ratings

### Candidate: read-1.json F1 (W17 preregistered overbreadth case)

| Run | Decision | Rating | Source-Grounded Reason |
|-----|----------|--------|------------------------|
| trial | excluded | **PASS** | The original `why` asserts a disjunctive conflict for any output that is "creative, prose, or non-deterministic." SKILL.md:358–360 excludes "creative / non-deterministic (writing style, prose, design feel)" — prose is a parenthetical example within the creative/non-deterministic category, not a separate universal trigger. equivalence-check-protocol.md:119–123 mirrors this: "non-deterministic / creative output (writing tone, design choices, persuasive copy)." multi-judge-ensemble.md:165–166 says "For any non-deterministic / prose / creative output, run the full ensemble." The slash-separated list in the ensemble file is contrasted with "file transforms, code generation" (deterministic outputs) in lines 154–160; "prose" there means creative/non-deterministic prose, not all prose. A deterministic factual prose report (e.g., a code-generated summary) would not meet the abort exclusion. The original claim overstates the abort scope. Exclusion is correct. |
| run-2 | excluded | **PASS** | Same reasoning as trial. The original's disjunctive "creative, prose, or non-deterministic" treats prose as an independent category, but the governing texts treat prose as an example of creative/non-deterministic output. The counterexample of deterministic prose refutes the asserted universal coverage. |
| run-3 | excluded | **PASS** | Same reasoning. The original elevates prose from a parenthetical example to a separately sufficient abort category. Deterministic prose with exhaustive testable content does not trigger the exclusion; the ensemble's wider run instruction applies without an abort there. |

**Design Question 1 — Did W18 replay reproduce the W17 overbreadth class on read-1.json F1?**
**No.** All three W18 replays correctly **excluded** the overbroad original claim. They kept the parenthetical "prose" within its source-assigned category (example of creative/non-deterministic output) rather than treating it as an independent universal exclusion. The W17 failure (confirming the overbroad claim) is not reproduced.

---

### Candidate: read-1.json F2

| Run | Decision | Rating | Source-Grounded Reason |
|-----|----------|--------|------------------------|
| trial | excluded | **PASS** | The original asserts an overall-verdict conflict: when structural-only skip conditions hold and Layer 1 passes but Q2 is marginal/failing or Q3 violated, the ensemble file assigns PROCEED while SKILL.md requires REJECT/RESHAPE. multi-judge-ensemble.md:3–4 scopes itself to Q1's Layer 2 ("How to spawn 3 independent LLM judges for `skill-refactor` Q1's Layer 2 semantic check"). Its structural-only exception (lines 152–163) says "Layer 1 pass = PROCEED" **for the Q1 check** — documented as `eval_mode: structural_only`. SKILL.md:155–163 defines overall PROCEED as requiring all three checks (Q1, Q2, Q3) to pass strictly; Q2 <5% reduction is REJECT (line 128). The ensemble file's PROCEED is Q1-local, not an overall override. The original's inference of an overall-verdict conflict exceeds the delegated scope. Exclusion is correct. |
| run-2 | confirmed | **FAIL** | Run-2 treats the ensemble file's "Layer 1 pass = PROCEED" as "the entrypoint verdict that applies the candidate," misreading the delegated Q1 scope as an overall verdict. It constructs a witness (zero-reduction deterministic file-transform) where Layer 1 passes Q1 but Q2 fails, and calls the ensemble file's Q1-local PROCEED incompatible with the overall REJECT. This is a semantic defect: the ensemble file does not waive Q2/Q3, nor does it define a separate overall-verdict vocabulary. The trial and run-3 correctly excluded this overread. |
| run-3 | excluded | **PASS** | Same correct reasoning as trial. The reference's skip branch is an explicit exception for Q1's ensemble only, not a delegation to waive Q2/Q3. A zero-reduction round gets Q1 acceptance and overall Q2 rejection consistently. |

**Design Question 2 — read-1.json F2: which direction is a semantic defect?**
The **confirmed** disposition (run-2) is a semantic defect — it misreads a Q1-delegated exception as an overall-verdict override. The **excluded** disposition (trial, run-3) is defensible and correct per the source delegation boundaries.

---

### Candidate: simulate-1.json F1

| Run | Decision | Rating | Source-Grounded Reason |
|-----|----------|--------|------------------------|
| trial | confirmed | **PASS** | The original `why` (narrower than read F1) asserts a conflict for non-deterministic or creative output: self-abort/route-to-skill-tuning vs. run-full-ensemble. SKILL.md:358–360: "Skill output is creative / non-deterministic (writing style, prose, design feel) — equivalence check unreliable; use `skill-tuning`." equivalence-check-protocol.md:119–123: same condition → "The skill self-aborts and recommends `skill-tuning` instead." multi-judge-ensemble.md:165–166: "For any non-deterministic / prose / creative output, run the full ensemble." For a target producing creative persuasive copy (explicitly covered by the protocol's parenthetical), the protocol requires self-abort before Q1, while the ensemble reference requires running Q1's full Layer 2. No precedence or creative-output exception appears in the ensemble file (lines 1–166 searched). The actions are incompatible for this concrete target. Confirmation is correct. |
| run-2 | confirmed | **PASS** | Same correct reasoning. The equivalence protocol specifically orders self-abort because its Layer 2 is unreliable for creative output, while the ensemble protocol specifically orders running that same Layer 2 for any creative/non-deterministic output. The conflict is genuine and category-specific. |
| run-3 | confirmed | **PASS** | Same correct reasoning. The ensemble file's universal instruction explicitly includes the excluded category; treating it merely as the deterministic skip exception cannot remove the opposite instructions. |

**Design Question 2 — simulate-1.json F1: which direction is a semantic defect?**
The **confirmed** disposition is defensible and correct. The conflict is real for the creative/non-deterministic category. An excluded disposition would be the defect (it would require reading an unwritten exception into the ensemble file).

---

### Candidate: simulate-1.json F3

| Run | Decision | Rating | Source-Grounded Reason |
|-----|----------|--------|------------------------|
| trial | excluded | **PASS** | The original claims a structural-only round passing Layer 1 but failing Q2/Q3 receives PROCEED from the ensemble reference and REJECT from SKILL.md. This is the same delegated-scope error as read-1.json F2. multi-judge-ensemble.md:3–4 scopes to Q1's Layer 2; its "Layer 1 pass = PROCEED" (line 162) is Q1-local (`eval_mode: structural_only`). SKILL.md:157–158 defines overall PROCEED as all three checks passing; Q2 <5% is REJECT (line 128). The reference does not waive Q2/Q3. The original's overall-verdict conflict exceeds the reference's Q1 scope. Exclusion is correct. |
| run-2 | confirmed | **FAIL** | Same defect as read-1.json F2 run-2. Run-2 misreads the ensemble file's Q1-local PROCEED as an overall-verdict command, constructs a witness (4% reduction, exhaustive deterministic Layer 1 pass), and calls the resulting Q1-pass/Q2-reject round an incompatible PROCEED-vs-REJECT pair. The ensemble file's exception is only for skipping the ensemble, not for overriding Q2/Q3. |
| run-3 | excluded | **PASS** | Same correct reasoning as trial. The reference's skip branch is an explicit exception for Q1's ensemble only. No incompatible final actions are supported under the delegated scope. |

**Design Question 2 — simulate-1.json F3: which direction is a semantic defect?**
The **confirmed** disposition (run-2) is a semantic defect — identical misreading of delegated scope as read-1.json F2 run-2. The **excluded** disposition (trial, run-3) is defensible and correct.

---

## Summary of Design Question Answers

**Design Question 1** — *Did the W18 replays handle the preregistered W17 failure candidate (`read-1.json F1`) faithfully?*
**Yes.** All three W18 replays excluded the overbroad original claim. They correctly treated "prose" as a parenthetical example within the creative/non-deterministic exclusion category, not as an independent universal trigger. The W17 overbreadth class (confirming the claim) is not reproduced.

**Design Question 2** — *For F2 / simulate F1 / simulate F3, which direction is a semantic defect?*

| Candidate | Defect Direction | Defensible Direction |
|-----------|------------------|----------------------|
| read-1.json F2 | **confirmed** (run-2) — misreads Q1-delegated exception as overall-verdict override | **excluded** (trial, run-3) — respects delegation boundary |
| simulate-1.json F1 | (none — **confirmed** is correct) | **confirmed** — genuine category-specific action conflict |
| simulate-1.json F3 | **confirmed** (run-2) — same delegated-scope misreading as read F2 run-2 | **excluded** (trial, run-3) — respects delegation boundary |

---

## What I Did Not Check

- Did not read any `caller-review.md` files from any replay run directory
- Did not read any W17 evidence files, `grading-spec.md`, session notes, or `*.summary.json` files
- Did not run any detectors, network calls, or spawning of agents
- Did not verify the SHA256 hashes in the decisions.json `sources` objects against the raw detector outputs
- Did not check whether the trial/run-2/run-3 decisions.json files are complete (all candidates from the detector outputs are present)
- Did not evaluate the simulate-1.json F2, F4, F5, F6, F7 candidates (outside the audit scope per the brief)
- Did not assess whether the detector findings themselves are accurate — only whether the caller dispositions are faithful to the governing source texts