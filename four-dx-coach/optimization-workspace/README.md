# optimization-workspace — Description-optimization experiment archive

> **Status**: NEGATIVE RESULT (2026-05-01)
>
> Attempted `skill-dev-toolkit:skill-creator-advance` description-optimization loop on all 12 four-dx-coach skills. The loop was unable to produce any improvement over the trim baseline because the trigger-detection mechanism returned `trigger_rate=0.0` for nearly every query across all skills. **Conclusion**: the framework as currently implemented is not suited to conversational coaching skills.

---

## What's in this directory

- **`<skill-name>/trigger-eval.json`** — 12 eval-query sets (20 queries each = 240 total), one per skill. Hand-crafted by parallel workers + spot-checked. Each query has a `should_trigger` label (10 positive / 10 negative per skill, with one xps-evaluation patched 11/9). Adversarial near-miss negatives designed to test cross-skill trigger discrimination.
- **`all-eval-queries-review.md`** — flattened view of all 240 queries for human review.
- **`README.md`** — this file.

What's gitignored (not preserved):
- `_logs/` — subprocess stdout/stderr noise from 12 parallel runs
- `<skill-name>/results/` — full iteration histories (all show same `train=6/12, test=4/8, baseline_won=True` pattern)
- Any `pilot/` dirs from earlier sanity checks

---

## What we found

Across all 12 skills, the optimization loop produced identical results:
- `best_train_score: 6/12` (50% — random performance on 50/50 pos/neg split)
- `best_test_score: 4/8` (50%)
- `baseline_won: True` (best_description == original trim baseline; no proposed improvement beat it)
- `mean trigger_rate: ~0.000` across all queries

**Root cause analysis**:

The `run_eval.py` mechanism creates a slash command from the candidate description and runs `claude -p <query>` as a subprocess, listening for `Skill` or `Read` tool invocations on the candidate skill. For four-dx-coach skills, sonnet-4-6 (the test model) almost never invoked the Skill tool — instead it answered queries directly using its built-in 4DX knowledge (the source book is widely-summarized public material).

This matches the spec's own warning at skill-creator-advance:
> "Claude only consults skills for tasks it can't easily handle on its own — simple queries may not trigger a skill even if the description matches perfectly, because Claude can handle them directly with basic tools."

Conversational coaching skills (where the skill body provides Socratic dialogue patterns rather than novel capabilities) appear to fall under this exemption — Claude is willing to answer 4DX questions directly without consulting the skill.

---

## Why we still keep the eval queries

Even though the optimization framework couldn't validate them, the 240 hand-crafted queries are valuable as:
1. **Hand-curated test cases** — useful for any future trigger-test framework that fixes the conversational-skill issue
2. **Cross-skill boundary documentation** — each negative case names which adjacent skill a near-miss should route to, encoding the routing intuition explicitly
3. **Multilingual coverage examples** — EN / JP / zh-TW phrasings users actually type

If the trigger-test mechanism is later fixed (e.g. by forcing `Skill` invocation as a control variable, or by switching from `claude -p` to direct API trigger evaluation), these eval sets can be re-run.

---

## Future paths if revisiting

1. **Switch eval mechanism** — replace `claude -p` subprocess with direct Anthropic API call + structured trigger-decision prompt; bypasses the "model can answer directly" issue
2. **Force skill consideration** — modify `run_eval.py` to use a system prompt that explicitly requires the model to declare WHICH skill it would consult (even if it could answer directly), reducing the conversational-skill exemption
3. **Try a different test model** — Opus or Haiku may have different invocation thresholds, but root cause is structural (conversational skill nature), not model-specific
4. **Shift to A/B human-judgment evaluation** — `skill-dev-toolkit:skill-tuning` (human-in-the-loop) rather than automated trigger-rate optimization

---

## What we kept (B-trim, not C-optimization)

The 12 SKILL.md `description:` field trims from the **B phase** are preserved in the plugin — those are heuristic-aligned to the 7-pattern rubric (WHAT + about-to-violate WHEN + multilingual triggers + 1-2 negative triggers + ≤500-600 chars). C optimization couldn't validate them empirically, but they remain spec-compliant by construction. See git history at commit `<TBD>` for the trim commit.
