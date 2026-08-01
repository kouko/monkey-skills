---
name: 2026-07-06-sibling-plugin-skill-md-frontmatter-versions-lag-plugin-json
description: Sibling plugin SKILL.md frontmatter versions lag plugin.json
status: OPEN
origin: PR #490 loom-interface-design agent flag — drift lives in SKILL.md frontmatter, not READMEs, so #490's README pass left it unfixed
start: next version bump of any sibling plugin, or next touch of the manifest-drift tooling (.claude/hooks/check-codex-manifest-drift.sh)
---

- Start: next version bump of any sibling plugin, or next touch of the
  manifest-drift tooling (.claude/hooks/check-codex-manifest-drift.sh)
- Origin: PR #490 loom-interface-design agent flag — drift lives in
  SKILL.md frontmatter, not READMEs, so #490's README pass left it
  unfixed
- What: SKILL.md frontmatter `version:` is stale across all three
  siblings (verified 2026-07-06): loom-interface-design 4× 0.3.0 vs
  plugin.json 0.4.1; loom-product-principles 0.3.0/0.1.0 vs 0.4.0;
  loom-spec 0.2.2/0.2.1/0.1.0 vs 0.4.1. Decide the contract
  (frontmatter tracks plugin version vs deliberate per-skill semver),
  then either sync or add a drift gate next to the codex-manifest one.
  New instance: loom-pipeline shipped loom-memory SKILL.md frontmatter
  `version: 0.1.0` while plugin.json moved to 0.5.0 (2026-07-06,
  followed sibling practice deliberately) — the undecided contract now
  covers loom-pipeline too.
