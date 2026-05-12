[English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

# simulation-modeling

Translate a qualitative CLD into a quantitative stock-and-flow plumbing diagram, then use the resulting simulation for learning — not point forecast.

## When to use

- A CLD is ready for quantification — variables identified, S/O signs verified — and you need numerical magnitudes, not just direction.
- You're suspicious of an exponential trap (compounding small drift) and need the doubling-time-vs-response-delay diagnostic to know whether linear extrapolation is dangerously misleading.
- A model has been built but the team treats its output as forecast — you need to reframe the model as a learning tool.

## How to invoke

`/systems-thinking-toolkit:simulation` or via the router `/systems-thinking-toolkit:stt`.

## What you get

- A stock-and-flow plumbing diagram from the qualitative CLD — variables classified by time-freeze test (stock vs flow), uniflow / biflow detection, lever-to-flow and outcome-to-stock mappings.
- The doubling-time-vs-response-delay diagnostic surfaced for every R-loop, plus an explicit framing of the simulation as a learning artifact (not a forecasting one).

## Boundaries

- NOT for point forecasting — the model exposes structure-driven behavior; if you commit to its numbers as predictions you will be wrong.
- NOT a substitute for an actual simulator — v0.1.0 ships the translation discipline only; numerical execution requires Vensim / iThink / Stella / spreadsheet / Python (companion script deferred to v0.2+).
- NOT for one-shot calibration — the learning loop matters more than the snapshot. Re-run as data refines.

## Reference

- Full skill specification: [SKILL.md](SKILL.md)

## Source

Dennis Sherwood, *Seeing the Forest for the Trees* (Nicholas Brealey, 2002) — Chapter 11 (stock-flow translation) and Chapter 12 (models for learning, not answers). Forrester / Sterman / Meadows lineage on numerical system dynamics.
