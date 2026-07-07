---
name: file-carrier-for-bulk-payloads
description: Bulk data between agent-skill pipeline stages must travel by file path, never as inline JSON in a command or one giant response — a large single response is a reproducible mid-response 5xx killer (proven live 2026-07-07, 2/2 inline failures, success after file hand-off)
type: gotcha
origin: 2026-07-07 research bake-off (docs/loom/dogfood/2026-07-07-research-bakeoff-vs-builtin.md) + fix brief docs/loom/specs/2026-07-07-deep-deep-research-file-carrier.md
---

Bulk data passed between pipeline stages in an agent skill must travel
by file path, never as inline JSON embedded in a command (e.g.
`echo '[<all claims>]'`) or as one giant single response.

**Why:** a large single response is a reproducible mid-response 5xx
killer — the API cuts the response partway through and the stage dies
with nothing recoverable. Proven live 2026-07-07: deep-deep-research's
claims-consolidation stage (88 claims inlined in one `echo`) failed
2/2 unattended runs with "API Error: Server error mid-response", and
succeeded immediately once the payload was written to files
incrementally and handed off by path.

**How to apply:** in any skill that fans out work and re-collects a
large pool (claims, search results, extracted records), each producer
writes its share to a file and passes the path; the collector reads
the files. Never instruct a stage to emit the whole pool inline in a
command argument or a single response. This is the same paths-not-
content convention as agent dispatch, extended to stage-to-stage data
flow.
