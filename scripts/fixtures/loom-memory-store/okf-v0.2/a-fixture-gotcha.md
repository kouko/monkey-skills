---
name: a-fixture-gotcha
description: This is a fixture gotcha lesson used only to exercise the OKF v0.2-compatible validator's happy path from an isolated install.
type: gotcha
sources:
  - resource: "https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/62432a095456147ee71e70ac6e4dc0d2dea3ac30/okf/SPEC.md"
    kind: url
type_note: fixture-only field, not part of the Loom profile schema — exercises REQ-12 (unknown metadata never a profile failure)
---

## Trigger

Whenever `scripts/test_loom_plugin_install_layout.py` copies `loom-memory`
into a clean install root and needs a real bundle to validate.

## Correct path

Point `loom_memory.py validate` at this fixture directory; expect exit 0.

## Why

REQ-22 requires a committed fixture so the isolated-install proof does not
depend on the repository's own live `docs/loom/memory` store.
