---
name: 2026-07-22-loom-memory-store-hardening-deferred-f2-f3-f5-f6
description: loom-memory store hardening — deferred F2/F3/F5/F6
status: open
origin: loom-memory design review (2026-07-22; branch `loom-memory-integrity`). F1 (integrity checker + CI) + F4 (recall staleness caveat) SHIPPED this branch; the review's other findings were triaged DEFER because they are slow-burn or hard to mechanize.
start: at ~150 store entries, on a real recall miss, or next substantive touch of `loom-pipeline/skills/loom-memory/SKILL.md`.
---

- Start: at ~150 store entries, on a real recall miss, or next substantive
  touch of `loom-pipeline/skills/loom-memory/SKILL.md`.
- Origin: loom-memory design review (2026-07-22; branch
  `loom-memory-integrity`). F1 (integrity checker + CI) + F4 (recall
  staleness caveat) SHIPPED this branch; the review's other findings were
  triaged DEFER because they are slow-burn or hard to mechanize.
- What: (a) **F2 size governance** — the store (81 entries, README §Index
  ~33 KB) has no cap / graduation / hot-tier, unlike the sibling auto-memory
  MEMORY.md (24.4 KB soft cap + archive index). Grows unbounded; recall greps
  the whole store. Revisit at ~150 entries. (b) **F3 recall precision** —
  keyword-grep has a false-negative floor (a semantic match with no shared
  keyword is silently missed); the cheap mitigation is a "try alternate
  keyword angles before concluding no-hits" recall nudge (embeddings are YAGNI
  at this scale). (c) **F5 prune trigger** — prune is manual-only with no
  age/size signal that ever wakes it → one-directional accumulation; F4's
  verify-before-act caveat already covers most of the staleness *harm*, so the
  trigger is low-priority. (d) **F6 mirror-hook verification** — the
  auto-memory→loom-store bridge (`.claude/hooks/remind-memory-mirror.sh`) is
  remind-only and hard to mechanize (CI can't see per-machine auto-memory);
  accept, or improve the reminder's specificity.
