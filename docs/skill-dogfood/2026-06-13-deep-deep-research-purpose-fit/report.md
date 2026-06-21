# Dogfood report — deep-deep-research (purpose-fit lever)

- **Date**: 2026-06-13
- **Skill-under-test**: `research-toolkit/skills/deep-deep-research/` (working tree)
- **Scope**: behavioral dogfood of the newly-added **opt-in purpose-fit relevance-floor** lever (SKILL.md `### Opt-in: Purpose-fit relevance-floor` + `scripts/purpose_fit.py` + `references/purpose-frames.md`). Whole-skill triggering was **unchanged** by this work (no description edit), so Probe A is a light fallback sanity-check; the weight is on Probe B (does the doc drive correct behavior) + Probe C (cold-read of the new subsection).
- **Distractor set**: sibling research-toolkit skills — fact-check / cite-check / deep-read.

## Severity summary

| Severity | Category | Count |
|---|---|---|
| Medium | Workflow-drift / integration | 1 (F1) |
| Low | Cold-start / progressive-disclosure | 2 (F2, F3) |
| — | Positive (behavior verified) | P1 |

No Critical/High. The core eval-validated behavior works end-to-end; findings are doc/integration-precision gaps.

---

## P1 (positive) — core behavior verified end-to-end

Probe B executor (informed) ran the lever as documented on a realistic decision question (macOS MAS-vs-direct, solo dev, app REQUIRES Full Disk Access). Both CLI commands ran clean (exit 0). Blind auditor (Probe B, firewalled) verdict: **Strong** — all 5 contract criteria PASS:
- Inferred purpose + confidence stated ✓
- **never-delete**: all 10 confirmed claims retained across decisive/contextual/not_relevant ✓
- **moot-hoist**: the FDA-incompatibility claim hoisted to a top-level `⚠ MAY SETTLE THE DECISION OUTRIGHT` callout ABOVE the frame ✓
- picked the **right** mooting factor (FDA→MAS ineligible) ✓
- sensible decisive set; no fabrication ✓

→ The SKILL.md prose + `purpose_fit.py` successfully drive the eval-validated behavior (moot-hoist / never-delete / consolidate-when-confident). This is the thing the dogfood most needed to confirm.

## F1 — Medium · Workflow-drift / integration · surfaced blind (Probe C) AND informed (Probe B)

- **Probe / repro**: Probe B executor ran the lever; Probe C cold-reader read the subsection independently.
- **Expected**: the verdict's claim-refs (in `decisive`/`contextual`/`not_relevant`/`mooting_factors`) line up with the claim identifiers in the `confirmed_block` the lever consumes.
- **Actual**: `synthesis.py blocks` emits confirmed claims as `### [0]`, `### [1]`, … (zero-based integer indices — **verified** by running it). But neither the SKILL.md purpose-fit subsection, the `purpose-classify-prompt`, nor `PURPOSE_FIT_SCHEMA` tells the agent that claim-refs must be those `[N]` indices. The executor invented `C1..C10` labels; the cold-reader independently flagged *"'claim-ref' is not defined — claim IDs? text? indices?"*.
- **Transcript evidence**: executor note — *"`synthesis.py blocks` emits headers as `### [0]` … the SKILL.md doesn't pin which scheme the refs must use, leaving a potential mismatch between the rendered block's indices and the verdict's refs."* Cold-reader Q4 — *"'claim-ref' is not defined. Does it mean claim IDs? Claim text strings? Indices?"*
- **Root cause**: the lever consumes `confirmed_block` (an upstream artifact with `[N]` indices) but its prompt/schema/doc describe refs abstractly; the cross-module seam was never exercised against the real `synthesis.py blocks` output.
- **Why static review missed it**: skill-judge reads the file without running it; the per-task + whole-branch code reviews verified the module's *internal* schema↔prompt↔block consistency but never ran the lever against the actual `synthesis.py blocks` output format — the integration seam between two house modules. Only an end-to-end behavioral run surfaces the ref-scheme mismatch (floor-not-ceiling).
- **Location**: `scripts/purpose_fit.py` (`purpose_classify_prompt` instructions) + `SKILL.md` §Opt-in: Purpose-fit (schema-shape paragraph).
- **Suggested fix**: in `purpose_classify_prompt`, add one instruction — *"Refer to each claim by its `[N]` index as printed in the confirmed_block (e.g. `[0]`, `[3]`)."* — and mirror a one-line note in the SKILL.md schema-shape paragraph. Optional defense-in-depth: `purpose_fit.py block` could validate refs against confirmed_block headers. Edit class: add a sentence to the prompt builder + a doc line. (No schema-structure change needed.)
- **DE-CONFOUNDED RE-TEST (2026-06-13)**: re-ran the executor on the **real `[N]`-indexed confirmed_block** (built via `synthesis.py blocks`, no `C1..C10` labels from the probe). Result: the agent **naturally used `[N]` refs** (mooting `["[1]"]`, not_relevant `["[6]","[8]","[9]"]`) — so the original `C1..C10` was partly a **probe confound** (the first probe pre-labeled claims `C1..C10`). The finding still stands, downgraded in trigger-probability: the agent **confirmed it guessed** (schema types refs as bare `array of strings`, "claim-ref" undefined), a schema-valid run could emit full text / made-up labels, and `block` does **pure string pass-through with no ref validation** → a mislabeled verdict yields **silently dangling refs**. Net: real latent bug (unenforced contract + silent-failure), but a capable model defaults to `[N]` when shown the real block; risk is a less-careful run. Severity stays Medium (silent failure) but fires probabilistically, not always.

## F2 — Low · Cold-start / progressive-disclosure · blind (Probe C)

- **Actual**: the subsection back-references things without restating them: `confirmed_block`'s shape (defined upstream in Stage 6 step 1), the contents of `references/purpose-frames.md` (only named, not characterized → "flying blind in multi-frame mode"), and — if *only* purpose-fit is enabled (no meta-mode) — the base-synthesis command args (Stage 6 step 2). A first-timer must scroll back to assemble the full flow.
- **Why static review missed it**: an informed reader treats these back-references as obvious; only a zero-context cold-reader feels the gap.
- **Location**: `SKILL.md` §Opt-in: Purpose-fit relevance-floor.
- **Suggested fix**: add 2 one-line pointers — *"`confirmed_block` = the markdown from Stage 6 step 1; claim-refs are its `[N]` indices"* (folds in F1) and *"if meta-mode is off, the base synthesis prompt is `prompts.py synthesis` per Stage 6 step 2."* Optionally one line on what a `purpose-frames.md` entry looks like.

## F3 — Low · Cold-start · blind (Probe C)

- **Actual**: the rendered moot-hoist callout format isn't shown in the doc; the cold-reader understood the *intent* (hoist above frames, never delete) but not the rendered shape. The `block` CLI renders it correctly (verified in P1) → doc-only.
- **Suggested fix**: optional — a 3-line rendered example in the subsection. Low priority (the CLI is the source of truth and works).

## Probe A — routing (fallback, fidelity:approximate)

Synthetic-menu routing across deep-deep-research + 3 distractors, 8 queries: **8/8 correct** — deep-research reports → deep-deep-research (3/3); single claim → fact-check; cited-doc audit → cite-check; one book → deep-read; coding & trivial → none. No trigger-miss / over-trigger. (Approximate — not the live `claude -p` harness; triggering was not changed by this work, so the risk surface is unchanged.)

---

## Raw outputs appendix

- **Probe A** routes: q1/2/7→deep-deep-research, q3→fact-check, q4→cite-check, q5→deep-read, q6/8→none (8/8).
- **Probe B executor** verdict JSON: `mode=consolidated`, `mooting_factors=["C2"]`, frame "Channel eligibility under the FDA constraint" decisive=[C2,C8,C4]; both CLI commands exit 0; flagged the `[N]`-vs-`C1` ref-scheme gap (F1).
- **Probe B blind auditor**: Overall **Strong**; 5/5 contract criteria PASS; correct mooting factor; no fabrication.
- **Probe C cold-reader**: never-delete clear ✓; moot-hoist intent clear, rendered shape unclear (F3); `confirmed_block`/`claim-ref`/`purpose-frames.md` back-references (F1/F2).
- **Verification**: `synthesis.py blocks` confirmed to emit `### [0]`, `### [1]` indices (F1 root cause).
