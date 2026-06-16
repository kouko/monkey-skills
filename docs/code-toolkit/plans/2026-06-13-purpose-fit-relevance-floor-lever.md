# Plan: purpose-fit relevance-floor lever (end-check, lever ③)

Source brief: docs/code-toolkit/specs/2026-06-13-purpose-fit-relevance-floor-lever.md
Total tasks: 5
Critical-path depth: 4 (T1 → T2 → T3 → T5; T4 parallel) — ≤5
Execution order: parallel-where-possible (T4 ∥ the py chain)
Plan-document-reviewer verdict: PASS (2026-06-13, 14/14; T3 noted upper-bound, atomic single-function unit)

## Notes

- **Template**: `scripts/mode_route.py` + `scripts/test_mode_route.py` are the near-exact analog (schema / classify-prompt / directive-block CLI; block PREPENDs synthesis; own test). Mirror its shape and voice.
- **House code, NOT synced**: `purpose_fit.py` is house code like `mode_route.py`/`framework_audit.py` — do NOT touch `scripts/{schemas,rank,prompts,dedup}.py`; the block PREPENDs the synthesis prompt, base `prompts.py synthesis` stays byte-identical (per `feedback_house_additions_in_new_module_not_synced_ssot`).
- **Same-file serialization**: T1/T2/T3 all edit `scripts/purpose_fit.py` + `scripts/test_purpose_fit.py` → a sequential chain (never `Independent: true` among themselves; shared git index — `feedback_parallel_implementers_one_worktree_interleave_commits`). Only **T4** (references/) is disjoint and parallel-eligible. If T4 runs parallel to the chain, orchestrator commits (implementers don't).
- **English-only**: `references/purpose-frames.md` + all module strings must be CJK-free (the `test_module_source_is_english_only` guard covers scripts/ + references/); the prototyped equity/software frames live in Chinese eval notes → translate. `grep -cP '[\x{4e00}-\x{9fff}]'` = 0 on touched files.
- **Module name** `purpose_fit.py` — safe, not a stdlib shadow (`feedback_select_py_shadows_stdlib_select`).
- **Verification** (Stage 7, not a task): `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q` in scripts/ (current 74 → grows with new tests), sibling suites unchanged (28/41/26), synced-primitive drift empty, CJK 0 on touched files.

## Task 1 — purpose_fit.py: schema + `schema` CLI

- Description: Create `scripts/purpose_fit.py` with `PURPOSE_FIT_SCHEMA` (a JSON-schema dict) and a `schema` CLI subcommand that prints it. Schema shape: `{inferred_purpose: str, confidence: "high|medium|low", mode: "consolidated"|"multi-frame", mooting_factors: [claim-ref...], frames: [{frame: str, decisive: [claim-ref...], contextual: [...], not_relevant: [...]}]}`. Module docstring states it is the purpose-fit (relevance-floor) lever, end-check, mirroring mode_route.py. Add `scripts/test_purpose_fit.py` with the schema test.
- Module: scripts/purpose_fit.py (+ its test)
- Files touched: research-toolkit/skills/deep-deep-research/scripts/purpose_fit.py, research-toolkit/skills/deep-deep-research/scripts/test_purpose_fit.py
- Context paths:
  - research-toolkit/skills/deep-deep-research/scripts/mode_route.py (template: schema dict + `schema` CLI + main dispatch)
  - research-toolkit/skills/deep-deep-research/scripts/test_mode_route.py (test template)
- Acceptance:
  - RED: `test_purpose_fit_schema` asserts the schema dict has the required top-level keys (`inferred_purpose`, `confidence`, `mode`, `mooting_factors`, `frames`) and that `frames` items carry `decisive/contextual/not_relevant` — fails (module/file absent).
  - GREEN: `python purpose_fit.py schema` prints valid JSON with those keys; `pytest -q test_purpose_fit.py` passes; full suite green.
- External surfaces: none (stdlib json/sys/argparse only).
- Dependencies: none
- Independent: false
- Brief item covered: Decision § "`purpose_fit.py schema` → the purpose-fit verdict schema: {inferred_purpose, confidence, mode, mooting_factors, frames…}".

## Task 2 — purpose_fit.py: `purpose-classify-prompt`

- Description: Add `purpose_classify_prompt(question, confirmed_block, frames_ref=...)` + a `purpose-classify-prompt` CLI subcommand to `purpose_fit.py`. The prompt instructs the agent to: (a) infer the decision purpose from the question/context + state it as a visible assumption with a `confidence`; (b) choose `mode` = consolidated (high confidence → foreground one decision-frame) vs multi-frame (low confidence/thin → the question-type's N frames from `references/purpose-frames.md`, evenly); (c) classify each confirmed claim into decisive/contextual/not_relevant **without deleting any** (not_relevant items are kept+labeled); (d) **flag mooting_factors** — claims that could settle the decision outright. Emit per `PURPOSE_FIT_SCHEMA`. Add the prompt-content test.
- Module: scripts/purpose_fit.py (+ its test)
- Files touched: research-toolkit/skills/deep-deep-research/scripts/purpose_fit.py, research-toolkit/skills/deep-deep-research/scripts/test_purpose_fit.py
- Context paths:
  - research-toolkit/skills/deep-deep-research/scripts/mode_route.py (classify_prompt template)
  - docs/code-toolkit/specs/2026-06-13-purpose-fit-relevance-floor-lever.md (Decision § for the four required instructions)
- Acceptance:
  - RED: `test_purpose_classify_prompt` asserts the built prompt contains the four behaviors — infer-purpose+confidence, consolidated-vs-multi-frame, classify-without-deleting (e.g. "not_relevant"/"do not delete"), and mooting-factor flagging ("settle"/"moot") — fails (function absent).
  - GREEN: `python purpose_fit.py purpose-classify-prompt --question Q --confirmed-block CB` prints the prompt with all four; suite green.
- External surfaces: none.
- Dependencies: Task 1 completes first (same module/file; prompt emits per the schema).
- Independent: false
- Brief item covered: Decision § "`purpose-classify-prompt` … (a) infers purpose+confidence, (b) consolidated vs multi-frame, (c) classifies … without deleting, (d) flags mooting factors".

## Task 3 — purpose_fit.py: `block` assembler

- Description: Add `purpose_fit_block(verdict)` + a `block` CLI subcommand that reads the agent's verdict JSON from stdin and emits `{purpose_fit_block: "<directive>"}` — a synthesis-prepend directive (mirroring `mode_route.stance_block`) that: (i) states the inferred purpose + confidence; (ii) **hoists mooting_factors to a top-level "⚠ this may settle the decision outright" callout ABOVE the frames**; (iii) foregrounds the decisive set (consolidated mode) or presents the N frames separately (multi-frame mode); (iv) labels not_relevant honestly. Never deletes (all claim-refs from the verdict appear somewhere). Add tests for both modes + moot-hoist.
- Module: scripts/purpose_fit.py (+ its test)
- Files touched: research-toolkit/skills/deep-deep-research/scripts/purpose_fit.py, research-toolkit/skills/deep-deep-research/scripts/test_purpose_fit.py
- Context paths:
  - research-toolkit/skills/deep-deep-research/scripts/mode_route.py (stance_block + `stance` CLI reading stdin JSON → output JSON)
  - /Users/kouko/kouko-obsidian-vault/projects/2026-06-13 purpose-fit eval — 多目的框架化 vs oracle（三臂 6 seed）.md (why moot-hoist is the load-bearing fix)
- Acceptance:
  - RED: `test_purpose_fit_block_*` — (a) consolidated verdict with mooting_factors → block contains a top-level moot callout ABOVE the frame + foregrounds decisive; (b) multi-frame verdict → block presents each frame separately; (c) no claim-ref present in the verdict is dropped from the block — fails (function absent).
  - GREEN: `echo '<verdict json>' | python purpose_fit.py block` emits the directive with moot-hoist + decisive-foreground + honest not_relevant + all claims retained; suite green.
- External surfaces: none.
- Dependencies: Task 2 completes first (same module/file; consumes the schema/verdict shape).
- Independent: false
- Brief item covered: Decision § "`block` → … (i) states purpose+confidence, (ii) hoists mooting factors to a top-level callout, (iii) foregrounds the decisive few or presents N frames, (iv) labels not-relevant. Never deletes; never edits prompts.py."

## Task 4 — references/purpose-frames.md (decision-frame catalog)

- Description: Create `references/purpose-frames.md` — a decision-frame catalog routed by question type, the input for multi-frame mode. Start with **equity** (entry / trim-exit / income-hold / position-size-risk) and **software-adoption** (velocity / scale-performance / cost-maintenance-burden / lock-in-reversibility), plus a **generic fallback** frame set. Each frame: a short name + the decision it serves + the kind of finding decisive for it. Small N (≤4 per type) per the eval's anti-collapse guard. English-only (translate the prototyped frames from the Chinese eval notes). Mirror `framework-audit-library.md` routing-by-type voice.
- Module: references/purpose-frames.md
- Files touched: research-toolkit/skills/deep-deep-research/references/purpose-frames.md
- Context paths:
  - research-toolkit/skills/deep-deep-research/references/framework-audit-library.md (routing-by-question-type format/voice)
  - /Users/kouko/kouko-obsidian-vault/projects/2026-06-13 purpose-fit eval — 多目的框架化 vs oracle（三臂 6 seed）.md (the prototyped equity/software frame sets)
- Acceptance:
  - RED: `grep -c "equity" references/purpose-frames.md` → 0 (file absent).
  - GREEN: file exists with both question-type families (equity ≤4 frames, software-adoption ≤4 frames) + a generic fallback, each frame named with its decision + decisive-finding kind; `grep -cP '[\x{4e00}-\x{9fff}]' references/purpose-frames.md` = 0.
- External surfaces: none (prose).
- Dependencies: none
- Independent: true   # disjoint file from the py module + SKILL; the prompt (T2) cites its path as a string, no symbol/content coupling
- Brief item covered: Decision § "`references/purpose-frames.md` — decision-frame catalog by question type (equity … / software-adoption …, + generic fallback; small N ≤4)".

## Task 5 — SKILL.md: opt-in subsection + quick-ref

- Description: Add an `### Opt-in: Purpose-fit relevance-floor` subsection to `SKILL.md` (near the meta-mode subsection, in the Stage-6 area), documenting: it operates on Stage-5 confirmed claims; the 3 CLI verbs (`schema` / `purpose-classify-prompt` / `block`); that the `purpose_fit_block` PREPENDs the synthesis prompt ordered **purpose-fit → meta-mode → base synthesis** (base `prompts.py` byte-identical); inference + confidence-gate + multi-frame-fallback + moot-hoist; opt-in/additive (default 360° unchanged). Add the 3 quick-ref table rows. This is the command-surface declaration for the new CLI verbs.
- Module: SKILL.md
- Files touched: research-toolkit/skills/deep-deep-research/SKILL.md
- Context paths:
  - research-toolkit/skills/deep-deep-research/SKILL.md (L422 meta-mode subsection + L522 quick-ref table — mirror the format)
- Acceptance:
  - RED: `grep -c "Opt-in: Purpose-fit" SKILL.md` → 0.
  - GREEN: SKILL.md has the `### Opt-in: Purpose-fit relevance-floor` subsection (states Stage-5-claims input + prepend-ordering purpose-fit→meta-mode→base + moot-hoist + opt-in) AND 3 quick-ref rows for `purpose_fit.py schema|purpose-classify-prompt|block` (command-surface declared); `grep -cP '[\x{4e00}-\x{9fff}]' SKILL.md` = 0.
- External surfaces: none (doc; declares the CLI verbs in the skill's quick-ref command surface).
- Dependencies: Task 3 completes first (doc-mirrors-code — documents the 3 verbs that must exist; depends on the full py module).
- Independent: false
- Brief item covered: Smallest End State "Opt-in SKILL.md subsection" + Decision § placement "purpose-fit-block → meta-mode-stance-block → base synthesis prompt".
