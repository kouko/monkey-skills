---
name: 2026-08-20-loom-design-scripts-cannot-be-run-as-one-pytest-invocation
description: Four subdirectories under loom-design/scripts/ share test basenames with no __init__.py, so 'pytest loom-design/scripts/' errors at collection; CI runs one job per subdirectory, so nothing catches a dispatch packet that names the whole tree — one did on this arc
status: open
origin: purpose-layer + serves-link arc close-out (2026-08-20)
start: next loom-design CI touch, or the second time a dispatch names a test command that has never worked
---

Recorded at the close of the purpose-layer arc. See
`docs/loom/specs/2026-08-20-north-star-serves-link.md` for the arc's own
framing and `docs/loom/plans/2026-08-20-north-star-serves-link.md` for
where it surfaced.
