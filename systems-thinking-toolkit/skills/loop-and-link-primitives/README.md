# Loop-and-Link Primitives — R/B Diagnosis + S/O Link Signing

[English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

Sign every causal arrow (S/O) with reversibility plus Sterman ultimate-test fallback, then count Os around a closed loop to classify it R or B.

## When to use

- Building a causal loop diagram and pausing on each arrow asking "is this S or O?"
- A KPI is drifting slowly (NPS, retention, share price) or accelerating non-linearly, and you suspect a feedback loop
- Vicious-cycle / death-spiral / bubble language is in play and you need to diagnose spin direction and flip-trigger
- A variance KPI (target vs actual) has been re-defined and the existing diagram's labels may be silently wrong

## How to invoke

`/systems-thinking-toolkit:link-primitives`

Or via the router: `/systems-thinking-toolkit:stt`

## What you get

- Per-link S or O label, with reversibility / Sterman test logged and uniflow flagged where present
- Per-loop R (even O count, including zero) or B (odd O count) classification, with current spin direction and a named plausible flip-trigger (R) or target plus delay magnitude (B)
- A one-sentence dynamic prediction (e.g. "R-loop in virtuous spin; will compound until trigger X")

## Boundaries

- NOT for one-shot decisions with no closed feedback loop (even-O / odd-O is undefined)
- NOT for statistical correlation labeling (no claimed direction of causation) or DAG causal-inference edges (unsigned by construction)
- Regime-dependent links (sign flips at threshold) hand off to `cld-craft`'s split-fuzzy-variable trick — do NOT pick a single label

See [SKILL.md](SKILL.md) for the full procedure (R/I/A1/A2/E/B sections).

## Source

Dennis Sherwood, *Seeing the Forest for the Trees* (Nicholas Brealey, 2002), Chapters 4, 5, 6, 12.
