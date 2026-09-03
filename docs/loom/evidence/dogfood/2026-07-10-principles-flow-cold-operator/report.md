# Cold-operator dogfood — product-principles construction flow (post-Task-5)

- **Date**: 2026-07-10
- **Skill under test**: `loom-product-principles:product-principles` SKILL.md @ branch `feat-loom-product-principles-construction-flow` (post-T5 rewrite, commit `e3810a28`)
- **Operator**: fresh-context haiku-tier agent (NOT the instrument/skill author), given ONLY the SKILL.md path + the user's idea; no design docs, no plan, no instrument
- **User**: kouko (real user, live), conversation language zh-TW
- **Product idea**: macOS meeting-recording transcription app — automatic known-speaker identification + custom vocabulary to raise transcription accuracy
- **Artifact produced**: `PRINCIPLES-meeting-transcriber.md` (this folder) — 18 principles (7 Product / 5 Design / 6 Engineering), North Star, consolidated version-pinned Anchors, Open Questions; empty Deviation Ledger correctly OMITTED per omit-when-empty
- **Independent verification (orchestrator, on disk)**: `validate_principles_output.py` exit 0 re-run independently; 18 `— check:` lines counted; section headings confirmed. Operator's claimed validator output matched the real run (no fabrication).

## Success criteria (instrument v0.1 table)

| # | Criterion | Grade | Evidence |
|---|---|---|---|
| 1 | Question-set adequacy | **PASS** | Product Q1-Q8 all asked; when the user answered only the follow-ups + Q3 and skipped Q4/Q5, the operator re-asked them unprompted (B1 coverage self-check exercised, live). No product-shaping dimension surfaced mid-run that the set lacked; the ad-hoc platform question (native vs web) was a reasonable extension, not a set miss. |
| 2 | Candidate breadth | **PARTIAL** | Product: 3 candidates ≥2 traditions + considered-but-rejected named with real reasons (Lean Startup, Design Sprint) ✅. Engineering: 4 candidates + 2 rejected ✅ — but the four mixed AXES (data ownership / code layering / UI pattern / module topology) presented as one exclusive menu; the user was confused and the orchestrator had to disentangle (F1 below). Design round: candidates in two lenses ✅ but considered-but-rejected entirely absent (F2). |
| 3 | Propose-then-react | **PASS** | Thin design stance (「簡單但明確的功能性設計」) → concrete candidates to react to, not a repeated open question. Iteration-vs-robustness confusion → plain-language briefing with worked examples anchored to the user's own Must-be principle (cross-section propagation observed). |
| 4 | Falsifiability | **PASS** | All 18 principles carry `— check:` with observable conditions; read-back killed the non-falsifiable/wrong ones (see F5). 零雲端依賴 hard-wording was softened by the user into a testable offline-inference + model-download split. Note: some check specifics were agent-invented (3-5 focus areas, ≤3 clicks) — falsifiable, user-accepted, but see F4. |
| 5 | Output shape | **PASS** | Version-pinned Anchors ✅; Deviation Ledger omitted-as-empty (contract-correct) ✅; unique principles ✅; per-section + final-total read-backs ✅; validator run by the operator AND independently re-run → exit 0. The 8-principle overshoot (see F3) was corrected in-conversation; the shipped artifact conforms. |

**4 PASS + 1 PARTIAL.**

## Findings

- **F1 (criterion 2, instrument + SKILL.md gap)** — Engineering canon candidates mixed four different axes (where data lives / how code layers / UI pattern / module topology) into one "pick one or mix" menu. The user could not tell what was being decided; the orchestrator had to reframe them as complementary layers. Neither instrument v0.1 nor the shipped SKILL.md states that candidates in one proposal round must be SAME-AXIS alternatives (answers to the same question); different-layer canons belong in Anchors as complements, not on the menu. → fix task.
- **F2 (criterion 2, SKILL.md ambiguity)** — considered-but-rejected was produced for Product and Engineering rounds but skipped for Design. The SKILL.md states the double guard once in the flow description; a weak-tier operator read it as Product-round-scoped. Make it explicitly per-candidate-round. → fix task.
- **F3 (behavior, guardrail latency)** — Operator drafted 8 Product principles, breaching the 3-7 contract it had itself loaded; caught only because the user asked about the count. The validator would have caught it at write time (fail-late), but the flow text could tell the operator to self-check the count at draft time (fail-early). → fold into fix task (one sentence).
- **F4 (behavior, invented specifics)** — Operator invented concrete parameters the user never stated (keyboard-first principle — WRONG, inverted by read-back; "3-5 visual focus areas", "≤3 clicks" — accepted). Read-back caught the load-bearing one (keyboard-first). Acceptable residual: invented-but-falsifiable specifics survive when the user accepts them in read-back. No fix; recorded as known weak-tier behavior that read-back is compensating for, matching the B-findings design.
- **F5 (read-back value, positive)** — Read-back caught two real drifts live: (a) JTBD job definition drift (operator wrote "organize meeting notes / track project progress" as the task; the user's actual task is "audio → speaker-labeled transcript"; downstream uses are not the product's job); (b) keyboard-first inversion (user wants mouse-primary). Both would have poisoned every downstream station. This is the second live confirmation (after the Target-B run) that the read-back gate is load-bearing at weak tier.
- **F6 (behavior, process hygiene, minor)** — Operator merged "revised draft" and "section closed ✅" into one message without awaiting user confirmation of the revision (Design section); and initially dropped the stakes lines when presenting the five Engineering stance questions (recovered in the next round with full background). Also initially swallowed the user's "cannot judge yet" on Q3 cost posture; after prompt, recorded it as a proper Open Question with a re-trigger. All three recovered in-run; none block ship. Candidates for future instrument hardening.
- **F7 (harness, not skill)** — Named persistent agents idle silently: the operator's first turn produced plain text that was never delivered; the orchestrator had to prompt it to route every user-facing message through SendMessage. Known harness gotcha (memory: named Agent dispatch needs SendMessage), not a skill defect.

## Verdict

**FIX-FIRST, then ship.** Criterion 2 is PARTIAL with two concrete, small SKILL.md fixes (F1 same-axis candidate rule, F2 per-round considered-but-rejected, plus F3's one-line draft-time count self-check). All other criteria PASS; the artifact itself is valid and the user signed it off. Fix tasks spawn before Task 7 per the plan's T6 contract.
