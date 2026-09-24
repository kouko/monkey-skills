# skill-consistency-check LLM rewrite — spec
intent: 2026-09-23-skill-consistency-check-llm-rewrite@8c656586a
pre-build-review: not-required — engineering-only skill rewrite; every removal stays in git history, no user data is touched, no public API, and the detection method was already validated by ten rounds of blind experiments

## Requirements
REQ-1 — Contradiction report
  WHEN the check runs on a skill folder, the skill shall produce a list of contradictions, each naming file and line for both sides, a verbatim quote per side, a confidence of high, medium or low, and a one-sentence reason, plus an overall verdict that is "needs revision" only when at least one high-confidence finding exists and "pass" otherwise (carried: "擋 PR：只擋高信心的發現，中低信心的只提示") → Acceptance #1
REQ-2 — Regression corpus
  WHEN the check runs on the imported regression corpus, the planted contradictions found shall be at least two thirds of those in the answer keys, and no high-confidence finding shall be one the answer key marks false → Acceptance #2
REQ-3 — Grouped checking of large skills
  WHEN a skill's total estimated tokens exceed 30,000, the skill shall split it into groups aimed at 25,000 tokens each (flagging any group that ends up larger), put SKILL.md, agents/ files and references directly cited by SKILL.md in every group, distribute the remaining files across groups, offset the read-through grouping from the walk-through grouping, and list in the report every file pair never checked in the same group; at or under 30,000 tokens the whole package is read at once (carried: "3 萬 tokens 以內整包一次讀完；超過就分組，每組不超過 2.5 萬 tokens"; "每組都放 SKILL.md、agent 檔和被直接引用的參考檔，其餘檔案輪流分配到各組"; "兩次執行的分組方式錯開"; "分組時沒放在同一組檢查過的檔案組合要列出來") → Acceptance #3
REQ-4 — Stated limits and model disclosure
  WHEN a report is produced, it shall state the contradiction kinds that may be missed (conditional, multi-step), the model used in this run, and the validation reference (Claude Sonnet, 200k context, packages up to ~25k tokens), and shall warn that accuracy is unvalidated when the run's model differs from the reference → Acceptance #4
REQ-5 — No side effects
  WHEN the check runs, it shall install no package and create or modify no file inside the checked skill folder → Acceptance #5
REQ-6 — Old implementation removed
  WHEN the change lands, the Z3-based scripts, install.sh, the extensionless CLI, the always-pass adversarial probe and the 2026-09-22 attestation shall be absent from the branch → Acceptance #6
REQ-7 — Existing tests
  WHEN the repository package tests run, they shall all pass → Acceptance #7
REQ-8 — Codex parity
  WHEN the check runs on Codex, it shall produce a report in the same format as on Claude Code → Acceptance #8

## Design decision
- agent-decided: detectors are two prompt specs (read-through, execution walk-through) copied from the experiment detector specs, extended with a `file` field; no model name is written; SKILL.md asks for a mid-tier or stronger host model and forbids the smallest tier, because rounds 5–8 showed haiku stopping after 1–3 findings.
- agent-decided: reading order is left unspecified (carried: "讀檔順序：不指定"), because rounds 6, 9 and 10 found no order effect.
- agent-decided: deterministic work (file listing, token estimate, core detection, grouping, never-co-grouped pairs, merge, dedupe, verdict, report rendering) lives in stdlib-only Python scripts so it is testable and identical on Claude Code and Codex; judgment (finding contradictions) stays in the detector agents.
- agent-decided: token estimate = CJK characters counted as one token each plus whitespace-separated words in the remaining text times 1.33; this is the same estimator that produced the agreed 30,000 / 25,000 figures (the validated 13-file package estimates at about 25,000), so thresholds and estimator stay calibrated; no tokenizer dependency, because installs are forbidden.
- agent-decided: "core" = SKILL.md, every file under agents/, and every package file whose relative path appears in SKILL.md text as a whole path (boundary match, not substring); only Markdown files other than README*.md are checked, and the report says so.
- agent-decided: when the core alone exceeds 25,000 tokens, or a single non-core file is larger than the remaining budget (that file then gets its own group with the core), groups still carry the whole core and the report flags the run as over the validated size with a cause-neutral warning.
- agent-decided: two findings are merged when both sides name the same files and each side's lines are within two lines of the other finding's side; the higher confidence is kept.
- agent-decided: reports are written only to an output directory outside the checked skill (default: a new directory under the system temp dir); the merge script refuses an output path inside the target, which turns REQ-5 into a mechanical check.
- agent-decided: fan-out is described abstractly as "dispatch N independent subagents in one message", following research-toolkit fact-check's portable fan-out convention, so the same SKILL.md runs on Codex.
- agent-decided: the regression corpus lives outside the skill folder (nested agents/ and references/ directories would break the flat-skill rule), with answer keys and a scoring helper; the 120k-token filler package is not imported because its filler is copied from other plugins and not needed by REQ-2.

## Alternatives considered
- Keep and repair the Z3 pipeline — rejected: blind runs gave 7/27 recall at ~18% precision; every miss came from natural-language-to-logic extraction.
- Majority vote across repeated same-method runs — rejected for the sonnet-class default: it removed no false findings (there were none) and dropped single-run true catches.
- Aspect-split, CRUD-matrix, pre/post-condition and per-object-index methods — rejected: round 4 showed zero added recall over read-through plus walk-through.
- Candidates-first procedure — rejected: round 7 kept recall flat and dropped precision from 60% to 38%.
- Randomized reading order — rejected: no measurable effect in rounds 6, 9 and 10.
- Always read the whole package — rejected: at ~120k tokens recall fell from 6/6 to 1/6.

## Current state evidence
- Forward: skill-dev-toolkit/skills/skill-consistency-check/skill-consistency-check (extensionless CLI) drives scripts/extract_rules.py → smt_encode.py → generate_report.py.
- Reverse: no other skill, README or plugin manifest references skill-consistency-check (grep over skill-dev-toolkit/README*.md and .claude-plugin/plugin.json).
- Error: scripts/smt_encode.py:204 area auto-installs z3-solver; generate_report.py:217-218 writes reports into the checked folder.
- Data: docs/loom/2026-09-22-skill-consistency-check/attestation.json records passes backed by scripts/adversarial_probe.py, whose body is `sys.exit(0)`.
- Boundary: scripts/check-skill-structure.py CHK-SKL-012 (line 399) rejects install.sh and the extensionless CLI at the skill top level; research-toolkit/skills/fact-check/SKILL.md:53 defines the portable fan-out convention.

## UI flows
N/A — no user interface; the report format is fixed by REQ-1 and REQ-4.
