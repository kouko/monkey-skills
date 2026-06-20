# Self-Trained Judge Pipeline (H4 Horizon Scaffold)

The skill-tuning preference log accumulates over time. At
sufficient density, it becomes training data for a domain-specific
preference model — a **self-trained judge** that approximates the
user's taste better than any general-purpose LLM judge can.

This document describes the pipeline. **The pipeline is not yet
active** at v1.7.0; it is scaffolded for future activation when
the log accumulates enough data.

## When this activates

| Stage | Threshold | Action |
|---|---|---|
| Phase 0 (now, v1.7.0) | <1000 entries in any single skill's log | Pipeline scaffolded; not deployed; manual scripts in this PR are documentation, not runtime |
| Phase 1 (future) | ≥1000 entries for a single skill | Pipeline activates for *that skill*; trains judge, deploys as Tier 1 pre-filter |
| Phase 2 (further future) | ≥1000 entries × multiple skills | Cross-skill training experiment; per-skill judges initially preferred |
| Phase 3 (long-term) | Ongoing | Continuous re-training as log grows |

The 1000-entry threshold is conservative; literature on
preference-modeling suggests reasonable signals from ~500 paired
preferences but reliable models from ~5000+. We start at 1000 as
a "is this even worth trying" threshold, with re-evaluation at
each milestone.

## Why per-skill, not global

Each skill has its own taste dimensions. A status-report skill's
preferred outputs (warm prose, dense facts) differ from an
inventory-snapshot skill's (terse, exact, list-first). Training
a single global judge across all skills would average these out;
training per-skill captures the actual taste.

The cost: per-skill judges require per-skill data (≥1000 entries
each). For 10 skills × 1000 entries = 10000 manually-judged A/Bs.
That's substantial human investment — only worth it for skills
that get tasted regularly.

## Training methodology

The classic preference-model setup:

```
Input: a preference pair (prompt, output_A, output_B, preferred=A)
Goal: train a model M such that M(prompt, A) > M(prompt, B)
       when A is preferred
Loss: standard pairwise preference loss (Bradley-Terry-style)
       L = -log(sigmoid(M(prompt, preferred) - M(prompt, rejected)))
Architecture: small transformer or fine-tuned existing LLM
              (depends on cost / latency budget)
```

For monkey-skills' use case, the cheapest viable architecture is:

- **Small fine-tuned LLM** (e.g., Llama 3 8B, Qwen 2 7B) on
  preference pairs
- Or: API-based fine-tuning if vendor supports preference-pair
  training

The trained model takes (prompt, output) and returns a scalar
preference score. Higher = more user-preferred.

## Deployment as Tier 1 pre-filter

Once trained, the judge replaces the constitutional-and-blind
A/B's *initial ranking*:

```
Old flow:
  1. Generate variants
  2. Constitutional pre-filter
  3. Show all surviving variants to user
  4. User picks blind

New flow (with trained judge):
  1. Generate variants (more aggressive — generate 5-10 instead of 3)
  2. Constitutional pre-filter
  3. Trained judge ranks remaining variants by predicted preference
  4. Top 3 by judge score shown to user
  5. User still picks blind
  6. User pick logged as new preference data → re-trains judge
```

Benefits:
- Generate more variants cheaply; let judge filter
- User sees the most-promising variants first → less fatigue
- User pick still drives the final decision; judge is advisory pre-filter

The user **always still has final pick** — the trained judge does
not auto-decide. It saves user attention by ranking, not by
replacing.

## Training script outline (`judge_train_stub.py`)

The stub script in `scripts/` documents the interface but fails
fast at v1.7.0:

```python
def train_judge(skill_name, log_path, output_model_path):
    log = load_log(log_path)
    pairs = extract_preference_pairs(log)

    if len(pairs) < 1000:
        raise ValueError(
            f"Insufficient training data for {skill_name}: "
            f"got {len(pairs)} pairs, need ≥1000. "
            "Continue using LLM-as-judge for now; revisit when log denser."
        )

    # When activated:
    # model = load_base_lm(...)
    # optimizer = ...
    # for batch in pairs: ...
    # save_model(output_model_path)

    raise NotImplementedError(
        "Training pipeline scaffolded but not active in v1.7.0. "
        "Activate when ≥1000 pairs available."
    )
```

The full training implementation will land in a future PR (likely
PR-5 or later) once at least one skill has accumulated the
threshold log.

## Evaluation methodology (when active)

When a judge is trained, evaluate before deploying:

1. **Held-out preference pairs** — train on 80%, evaluate on 20%.
   Goal: ≥80% agreement with user picks on held-out set.
2. **A/B against LLM judge** — for new variants, ask both the
   trained judge and a generic LLM judge; compare to actual user
   picks on N=50 fresh examples. Trained judge should outperform.
3. **Confidence calibration** — judge should output not just a
   ranking but a confidence; uncertain picks should escalate to
   user judgment without the pre-filter ranking.

If trained judge underperforms LLM judge: don't deploy; continue
data accumulation; revisit at higher N.

## Privacy / data handling

The training pipeline operates on preference logs. Same privacy
considerations as logs themselves:

- Per-user logs typically; don't merge across users without consent
- Sanitize prompts before training (PII, sensitive context)
- Trained models are themselves derivative of user preferences;
  treat as user-data-equivalent for sharing
- For shared monkey-skills repo case: trained judges are
  per-installation, not committed to the repo; users opt-in to
  sharing aggregate models if desired

## Cross-skill transfer

Speculative: once 2+ skills have trained judges, can the judges
share parameters or knowledge?

Possibilities:
- Multi-task training: one base model with skill-specific heads
- Adapter approach: base LLM + LoRA per skill
- Embedding shared + per-skill scoring head

This is **research territory**, not v1.7.0 scope. The pipeline
documents per-skill training as the v1 path; multi-skill is
out-of-scope until single-skill training proves valuable.

## Failure modes

| Failure | Why | Mitigation |
|---|---|---|
| User taste drifts over time | Preferences from 2 years ago no longer valid | Time-decay weighting; or retrain on recent-N entries only |
| User has multiple "modes" of taste (depending on context) | Single judge averages contexts | Context-conditional judge: take additional context features as input |
| Constitution updates retroactively change what's valid | Old entries against old constitution mismatch new one | `applies_to_constitution_version` filter at training time |
| Judge over-fits to specific examples | Not enough variance in log | Ensure log captures variant diversity (random labeling helps) |
| Judge fails to outperform random | Genuinely hard task; signal too weak | Document; don't deploy; consider whether tuning is the right tool for this skill |

## Cross-references

- `references/preference-log-schema.md` — the data this pipeline
  consumes
- `references/ab-harness-protocol.md` — where the data is
  generated
- `scripts/judge_train_stub.py` — the placeholder script;
  documents the interface
- `dev-workflow/docs/skill-evolution-architecture.md` §6 H4
  horizon — the broader plan this fits into
