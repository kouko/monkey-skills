---
name: 2026-08-12-protocol-files-carry-no-size-ceiling
description: every word-cap test in the repo targets a SKILL.md, so `<plugin>/skills/*/protocols/*.md` grows unbudgeted even though protocols are loaded at runtime like skill bodies — the adjudication-view protocol grew 1937 → 2069 words in one fix round with nothing to notice
status: OPEN
origin: 2026-08-12 adjudication-view Japanese-support arc, fix round — the implementer adding the §Invocation contract checked for a ceiling before writing and found none, and flagged the gap rather than silently benefiting from it
start: a protocol file crosses ~3000 words, OR a second protocol file lands under any plugin — whichever comes first
---

- Start: a protocol file crosses ~3000 words, OR a second protocol file
  lands under any plugin — whichever comes first

- Origin: 2026-08-12 adjudication-view Japanese-support arc, fix round —
  the implementer adding the §Invocation contract checked for a ceiling
  before writing and found none, and flagged the gap rather than
  silently benefiting from it

- The file it was writing into,
  `loom-code/skills/using-loom-code/protocols/adjudication-view.md`,
  went 1937 → 2069 words in that round with nothing in the repo
  positioned to notice.

- The gap, verified: every word-cap test targets a `SKILL.md`
  (`test_wp_extraction_pointers.py`, `test_rcr_capacity_pointer.py`,
  `test_sdd_mechanical_suite_gate.py`), and
  `scripts/check-skill-structure.py` walks `<plugin>/skills/*/SKILL.md`
  only. `protocols/*.md` is unbudgeted.

- Why it matters: protocols are not references. A reference is read on
  demand by a human or an agent that chose to open it; a protocol is
  loaded and executed at a gate, so its length lands in the same context
  budget the SKILL.md ceilings exist to protect. The repo's own reason
  for capping skill bodies applies to this file class and simply was
  never extended to it.

- Why not now: the arc that surfaced it was a fix round closing two 🔴
  omissions, and adding a new ceiling test mid-round would have been
  scope the review did not ask for. There is also a real design question
  to settle first — whether protocols get their own (probably higher)
  cap, or share the SKILL.md budget of the skill that loads them, since
  a protocol's cost is only paid by the skills that reference it.

- Cheapest shape when it fires: one pin per protocol file with the
  ceiling and its raise-history in the failure message, matching the
  existing SKILL.md ceiling convention — those tests already document
  every deliberate raise inline, which is what makes accretion visible
  instead of merely blocked.
