---
name: 2026-08-07-mechanize-loom-memory-prune-pretriage
description: loom-memory prune is fully manual over the whole store; a pre-triage script could rank candidates by origin age
status: open
blocked: waiting on a manual prune pass proving impractically expensive, or the store exceeding 200 entries
origin: 2026-08-07 family complexity audit (docs/loom/audits/2026-08-07-family-complexity-audit.md, item D4)
start: the first full manual prune pass proves impractically expensive, or the store exceeds 200 entries
---

The prune verb (loom-pipeline/skills/loom-memory/SKILL.md:96-119)
requires checking expiry signals for every store file by hand; the store
is at 136 entries / ~53,000 words and growing. A lightweight script
ranking candidates by frontmatter origin age vs git activity on cited
paths would pre-triage the human pass.

Parked because this ADDS machinery — the opposite of the audit's
deletion-first direction — and no manual prune pass has yet been run to
demonstrate the need. Run one honest manual prune first; mechanize only
if it hurts.
