---
name: ci-skill-structure-scan-gap-obsidian
description: .github/workflows/skill-structure.yml scans only domain-teams + loom plugins — an obsidian (or other unscanned plugin) SKILL.md CHK-SKL-010 word-cap breach merges silently; check wc -w ≤4,500 before adding text
type: gotcha
origin: feat/digest-multiview-synthesis whole-branch review (2026-07-10)
---

The repo's skill-structure CI (`.github/workflows/skill-structure.yml`) runs
`scripts/check-skill-structure.py` against domain-teams and the loom plugins
only. Every other plugin's SKILL.md — obsidian, dev-workflow, the toolkits —
is NOT covered, so a CHK-SKL-010 breach (>4,500 words / ~6,000 tokens) there
passes CI and merges silently. Live case: feat/digest-multiview-synthesis
pushed `obsidian/skills/daily-news-digest/SKILL.md` from 4,352 to 4,864 words;
only the whole-branch review panel caught it (trimmed back to 4,495).

**Why:** the word cap is a FATAL rule in the repo's own conventions, but for
unscanned plugins the only enforcement is review-time vigilance — a silent gap
that grows one SKILL.md at a time.

**How to apply:** before adding text to any SKILL.md outside domain-teams/loom,
run `wc -w <path>` and budget the delta against 4,500 first (trim-then-add, not
add-then-trim). `obsidian/skills/daily-news-digest/SKILL.md` sits at 4,495/4,500
— any future addition there must start with a trim.
