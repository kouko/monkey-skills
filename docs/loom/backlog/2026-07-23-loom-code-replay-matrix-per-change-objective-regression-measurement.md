---
name: 2026-07-23-loom-code-replay-matrix-per-change-objective-regression-measurement
description: loom-code replay matrix — per-change objective regression measurement
status: open
origin: 2026-07-23 discussion (purpose aligned: objective per-change better/worse measurement, not one-shot evaluation); survey + seed inventory in `docs/loom/research/2026-07-23-loom-mechanism-quantitative-eval-methods.md`.
start: user commits to the arc; or the next wave of loom-code skill-text changes where "did this make it worse?" is asked without a measurement to answer it.
---

- Start: user commits to the arc; or the next wave of loom-code skill-text
  changes where "did this make it worse?" is asked without a measurement to
  answer it.
- Origin: 2026-07-23 discussion (purpose aligned: objective per-change
  better/worse measurement, not one-shot evaluation); survey + seed inventory
  in `docs/loom/research/2026-07-23-loom-mechanism-quantitative-eval-methods.md`.
- What: generalize the `principles-replay-matrix` pattern (fixed seed corpus →
  haiku headless replay → mechanical grading from exit codes only → per-seed
  win/loss/tie + pass-rate, n≥2 replicates, eval semantics never CI) to
  loom-code. Scope is smaller than it looks — the corpus raw material already
  exists (~30 seed-grade items): 26 probe rows in
  `docs/loom/audits/2026-07-16-loom-weak-model-behavioral-audit.md`, the
  git-checkable review-quality oracle in
  `docs/loom/dogfood/2026-07-06-g4-sonnet-vs-fable-ab.md`,
  `docs/loom/firing-corpus/*.jsonl` (reuse as-is), the waiver-pressure probe
  (2026-07-20 audit §5), and pipeline-driver F4. Work = normalize probes into
  seed/oracle pairs + copy the replay-matrix workflow + wire loom-code's
  existing mechanical gates as graders. Red/green discipline per change: the
  targeted failure enters the corpus RED first; effectiveness = new seed
  GREEN + zero old-seed regressions + cost delta. Floor-only honesty: this
  measures stability (known failure modes), not output quality — quality
  stays with blind A/B (`skill-tuning`) / rubrics / human read, ratcheting
  the floor via new seeds after each discovered quality failure. Standing
  habit effective immediately (pre-arc): every new dogfood/live failure is
  recorded as a seed+oracle pair in `docs/loom/dogfood/`, so the corpus
  accretes before the harness exists. Cross-ref: the entry above reserves
  promoting the seed-traceability invariant to a family convention when a
  second station ships a seeded mode — this arc shipping fires that trigger.
