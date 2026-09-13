---
name: a-fixture-practice
description: This is a fixture practice lesson used only to exercise the OKF v0.2-compatible validator's grouping-by-type behavior from an isolated install.
type: practice
sources:
  - resource: "fixture, authored for scripts/fixtures/loom-memory-store/okf-v0.2/"
---

## Trigger

Whenever a validator test needs more than one memory `type` present in a
single bundle, to prove `index.md` groups lesson links by type.

## Correct path

Regenerate `index.md` and confirm both `## gotcha` and `## practice`
headings appear, each with its own concept underneath.

## Why

REQ-8 requires grouping lesson links by memory type; a single-concept
fixture cannot exercise that.
