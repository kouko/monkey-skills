---
name: README
description: Fixture OKF v0.2-compatible Loom memory store used by loom-memory's isolated-install proof (REQ-22).
type: Memory Store Guide
sources:
  - resource: "commit 62432a095456147ee71e70ac6e4dc0d2dea3ac30 (fixture, not a real repository commit)"
---

# loom-memory fixture store

A small, deliberately valid bundle: `loom-workflow/skills/loom-memory/scripts/loom_memory.py
validate` on this directory must exit 0, and running `regenerate-index`
against it twice must produce a byte-identical `index.md` both times.
