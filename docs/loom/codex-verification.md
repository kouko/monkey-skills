# Codex 0.139.0 verification — repo-wide Codex compat

> **Verified on Codex CLI 0.139.0, 2026-06-30** — live install + skill-discovery
> ritual run against a real `~/.local/bin/codex` instance (`execution = truth`,
> per the loom-code precedent `docs/loom/specs/2026-06-14-codex-compat-completion.md`).
> Verified the Phase-2 branch `feat/codex-compat-phase2-interface` (authored
> interface blocks), which is the state being shipped.

## Install command surface (verified working)

```
codex plugin marketplace add <repo-root>     # registers the repo's .claude-plugin/marketplace.json
codex plugin add <plugin>@monkey-skills      # installs a plugin from that marketplace
codex plugin list                            # shows installed/available + status
codex plugin remove <plugin>                 # uninstall
codex plugin marketplace remove monkey-skills
```

- The marketplace **name is `monkey-skills`** (from `.claude-plugin/marketplace.json`'s
  `name`). `codex plugin marketplace add` has **no `--name` flag** — so adding a second
  source under the same name fails (`'monkey-skills' is already added from a different
  source; remove it before adding this source`). To verify a worktree, remove the existing
  registration first, then re-add.
- Codex reads the **same** `.claude-plugin/marketplace.json` (no separate Codex marketplace).
  It then resolves each plugin's `.codex-plugin/plugin.json` at the marketplace `source` path.

## Enumeration

`codex plugin list` rendered **all 25 marketplace plugins** with no parse error — i.e. the
22 authored `.codex-plugin/plugin.json` manifests (21 Batch-A + loom-code) parse cleanly on
Codex 0.139.0, including the authored `interface` blocks (`capabilities` as a JSON array,
etc.). The 3 plugins without a `.codex-plugin` manifest yet (dev-workflow = Batch B;
collab-toolkit, salesforce-toolkit = Batch C) appear in the marketplace listing (from
marketplace.json) but are not installable until their manifests land.

## Install + skill-discovery — verified sample (6 of 22, chosen for diversity)

| Plugin | Category shape | Result |
|---|---|---|
| research-toolkit | Research, 4 skills | ✅ installed, enabled — 4 skills present in install cache |
| investing-toolkit | Finance, 16 skills (largest) | ✅ installed, enabled — 16 skills present |
| copywriting-toolkit | Writing, 14 skills | ✅ installed, enabled |
| loom-spec | Coding, 2 skills | ✅ installed, enabled |
| ascii-graph-toolkit | Productivity, 1 skill (smallest) | ✅ installed, enabled — 1 skill present |
| briefing-toolkit | read-only (`["Interactive","Read"]`) | ✅ installed, enabled — read-only capabilities accepted |

All 6 → `codex plugin add … @monkey-skills` succeeded; `codex plugin list` shows
`installed, enabled`; the installed plugin root
(`~/.codex/plugins/cache/monkey-skills/<plugin>/<version>/skills/`) carries the plugin's
skills (counts match the source repo). Coverage spans 5 categories + the min/max skill-count
extremes + the read-only-capabilities case.

## Conclusion

The repo-wide Codex-compat Phase-1 engine output + Phase-2 authored interfaces are
**verified loadable + skill-discoverable on Codex 0.139.0**. No manifest failed to parse or
install. Remaining Phase-2 work (Batch B `dev-workflow` hook contract; Batch C
`collab`/`salesforce` MCP) is out of scope here and tracked in
`docs/loom/specs/2026-06-30-codex-compat-all-plugins.md`.
