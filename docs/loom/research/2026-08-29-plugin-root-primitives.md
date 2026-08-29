# Plugin-root primitives — cross-plugin resolution: documented surface vs measured mechanism

> Ticket: `docs/loom/maps/family-relocation/tickets/research-plugin-root-primitives.md`
> Method: research-toolkit:deep-deep-research (5 bilingual angles, 22 sources fetched,
> 143 claims extracted, 25 ranked, 3-vote adversarial quorum → 22 confirmed / 3 killed).
> Independence relaxation: each claim's three votes came from ONE verifier context using
> three diversified stances (literal-quote / scope / counter-evidence) — not three
> isolated subagents. Unverified material is explicitly marked "context tier".
> Date: 2026-08-29.

# Research Report

## Summary

Official Claude Code docs (fetched 2026-08-29) now document substantially more of the plugin surface than the feasibility probe assumed, but the probe's core dependency remains internal: installed_plugins.json appears nowhere in official documentation, while the docs DO document the cache location (~/.claude/plugins/cache), its per-version directory layout with a ~14-day orphan grace period, the full CLAUDE_PLUGIN_ROOT placeholder-expansion matrix, an explicit warning that CLAUDE_PLUGIN_ROOT changes on plugin update, a hard guard rejecting component paths that escape the plugin root, and an official plugin-to-plugin dependencies mechanism (auto-install, semver ranges, cross-marketplace allowlist) that is strictly install/enable/version-time — it provides no runtime API for one plugin to locate another plugin's files. A documented persistent-state primitive (CLAUDE_PLUGIN_DATA -> ~/.claude/plugins/data/{id}/) survives updates. Net: cross-plugin script execution is achievable today via the measured internal-registry route, with the officially-documented dependencies field guaranteeing the sibling is installed, but current-version root DISCOVERY at runtime has no documented primitive on Claude Code (verified negative), and Codex-side official docs likewise show none — though the Codex half rests on context-tier (unverified) evidence only.

## Findings

- **CLAUDE_PLUGIN_ROOT expansion is fully documented per component: anywhere in skill/agent content and hook/monitor commands; only command/args/env for MCP stdio; only url/headers/headersHelper for MCP http/sse/ws; also exported as env var to hook and MCP/LSP subprocesses.** *(confidence: high)*
  - <https://code.claude.com/docs/en/plugins-reference>
  - Evidence: Verbatim placeholder-substitution table confirmed 3-0 on claims [0][1][2].
- **CLAUDE_PLUGIN_ROOT is documented as UNSTABLE across plugin updates: it changes when the plugin updates, and the old version directory is explicitly 'ephemeral' — kept only for a grace period.** *(confidence: high)*
  - <https://code.claude.com/docs/en/plugins-reference>
  - Evidence: Claim [3], verbatim sentence confirmed 3-0.
- **Naive cross-plugin file references are officially BLOCKED: a component path resolving outside the plugin's own root (e.g. ../shared-utils) is rejected with a 'path escapes plugin directory' error.** *(confidence: high)*
  - <https://code.claude.com/docs/en/plugins-reference>
  - Evidence: Claim [4], verbatim error text confirmed 3-0; matches this repo's own boundary tests.
- **The plugin cache is now a documented surface: marketplace plugins are copied to ~/.claude/plugins/cache; each installed version is a separate directory grouped by marketplace and plugin, named for the resolved version; old version dirs are swept ~14 days after update/uninstall (grace period for running sessions).** *(confidence: high)*
  - <https://code.claude.com/docs/en/plugins-reference>
  - Evidence: Claims [7][8][10] confirmed 3-0 each.
- **installed_plugins.json is NOT part of the documented surface: neither the plugins-reference page nor the create-plugins guide mentions it anywhere — the probe's resolver reads an internal, undocumented registry.** *(confidence: high)*
  - <https://code.claude.com/docs/en/plugins-reference>
  - <https://code.claude.com/docs/en/plugins.md>
  - Evidence: Negative claims [11][16] survived 3-0 including independent term searches across all page sections.
- **An official plugin-to-plugin dependencies mechanism exists: plugin.json dependencies entries (bare name, or {name, version: semver-range, marketplace}), auto-installed at install time (narrow manual exceptions), cross-marketplace blocked by default behind the root marketplace's allowCrossMarketplaceDependenciesOn allowlist with no trust chaining, versions resolved via {plugin-name}--v{version} git tags; a depended-on plugin gets an explicit enabled=true written.** *(confidence: high)*
  - <https://code.claude.com/docs/en/plugin-dependencies>
  - <https://code.claude.com/docs/en/plugins-reference>
  - Evidence: Claims [19][20][21][22][6] confirmed 3-0 each.
- **The dependencies mechanism is install/enable/version-time ONLY: the page documents no API or field for one plugin's skill/hook/agent to resolve or read another plugin's files, paths, or CLAUDE_PLUGIN_ROOT at runtime.** *(confidence: high)*
  - <https://code.claude.com/docs/en/plugin-dependencies>
  - Evidence: Claim [24], a section-by-section negative sweep whose section list was verified against the page's actual headings, 3-0.
- **A documented persistent-state primitive exists for surviving updates: CLAUDE_PLUGIN_DATA resolves to ~/.claude/plugins/data/{id}/ — distinct from the ephemeral versioned root.** *(confidence: high)*
  - <https://code.claude.com/docs/en/plugins-reference>
  - Evidence: Claim [9] confirmed 3-0.

## Caveats

Verification-independence relaxation: each claim's three adversarial votes were produced by one verifier context using three diversified voter stances (literal-quote / scope / counter-evidence), not three fully independent subagents.
Only the 25 ranked claims (all from the three official pages) were adversarially verified; GitHub-issue, Codex-official, and Japanese practitioner claims were extracted but not quorum-verified — they are cited as context tier only.
Official docs are live pages; the quoted text reflects 2026-08-29 fetches. The docs carry no versioned changelog for these pages.
Context-tier (unverified) evidence consistently reports registry/cache desync bugs across CLI updates (issues 15642, 48985, 76234, 14061, 35691) — treating even documented cache paths as fully stable would overstate current implementation quality.
3 of 25 ranked claims were killed by the adversarial pass (one fabricated example quote, two interpretive overreaches) and are excluded above.

## Open Questions

- Is there, or will there be, a documented runtime primitive for 'current enabled version root of plugin X' (the one thing installed_plugins.json provides that no documented surface does)?
- Does dependencies auto-install extend to adding the dependency's marketplace on a cold machine, or must the marketplace already be registered?
- Codex side: official skills/plugins docs (context tier) show no placeholder variable and no registry file — is the single-version cache-dir glob the best available mechanism there?
---

## Context tier (extracted, NOT quorum-verified)

### GitHub issues (anthropics/claude-code) — implementation-quality signal
- #24529: hook executor observed not setting CLAUDE_PLUGIN_ROOT env var (doc/impl gap).
- #9354: `${CLAUDE_PLUGIN_ROOT}` expansion historically scoped to JSON configs, not command markdown.
- #59206: stale skills path referencing an old cached version after upgrade.
- #15642: CLAUDE_PLUGIN_ROOT pointing at a stale version after plugin update (cache/registry desync).
- #48985: plugin cache lost across CLI auto-update (2.1.90→2.1.110).
- #76234: cache dirs for manifest-less plugins load under version-string names (layout shifts by manifest presence).
- #14061 / #35691: installed_plugins.json retains stale fields / uninstall leaves cache files — registry and cache are loosely coupled internal state.
- #48864 / #27113: dependency docs gap + project-level dependency feature request — the dependencies feature is newer than most third-party writeups.

### Codex CLI (official docs + community, context tier)
- Official skills/plugins docs (developers.openai.com/codex/{skills,plugins,plugins/build}; github.com/openai/skills): skills live under `~/.codex/skills` / `$CODEX_HOME/skills` / project `.agents/skills`; plugins bundle skills+MCP.
- No CLAUDE_PLUGIN_ROOT-equivalent placeholder and no installed-registry file appear in these docs; nothing addresses one plugin/skill referencing another's files.

### Japanese practitioner corpus (context tier)
- Qiita (yureki_lab) documents CLAUDE_PLUGIN_ROOT ハマりどころ; Zenn (edash) states the placeholder is what makes install-location-independent paths possible. EN/JA sources agree; no substantive disagreement found.

## This repo's measured evidence (from the feasibility probe and boundary tests)

- Probe (ticket `feasibility-cross-plugin-store-access.md`, artifacts at prototype fence commit `2aec80f1`): resolver reads `~/.claude/plugins/installed_plugins.json` (schema `"version": 2`) `installPath`; cold-repo resolution + `map_store.py validate` + a real headless SessionStart hook all PASS; uninstalled plugin → exit 3 graceful N/A; naive same-root version glob AMBIGUOUS (7 dirs loom-workflow / 33 loom-code).
- Boundary tests already enforce what the docs now confirm: raw sibling paths rejected (`scripts/test_check_plugin_boundaries.py`), composition only through plugin-qualified skill names and project-owned docs/loom artifacts (`scripts/test_loom_plugin_composition.py:152`), no mandatory sibling dependency in the marketplace (`test_loom_plugin_composition.py:429`).
- Codex mirror: `.codex/hooks.json` uses literal relative paths; no placeholder variable, no registry analog — single-version cache-dir glob is the only observed resolution route there.

## Implications — measurement baseline for the feasibility ruling

1. **The measured mechanism stands on an internal surface.** `installed_plugins.json` is the only current-enabled-version oracle, and it is absent from every official page (verified negative). The documented cache layout tells you WHERE versions live, not WHICH is current.
2. **What official primitives DO give us**: (a) `dependencies` guarantees the sibling is installed and enabled (install-time); (b) the cache path shape is documented with a ~14-day grace period; (c) `CLAUDE_PLUGIN_DATA` gives durable cross-update state — a documented home for a handshake file a sibling could write for itself.
3. **What no documented primitive gives us**: runtime discovery of a sibling's current root — verified negative on Claude Code; on Codex the same absence is observed but context-tier only (see Open Questions). Claude Code's path-escape guard actively rejects static cross-plugin component paths — cross-plugin composition is by-name delegation or runtime resolution, never static paths (our boundary tests already encode this).
4. **Stability posture for the resolver**: treat `installed_plugins.json` as an internal API — keep the fail-loud guard, re-verify on CLI majors, and note the context-tier desync bugs as the expected failure shape. The officially warned instability of `CLAUDE_PLUGIN_ROOT` across updates means resolved roots must be re-resolved per session, never persisted.
5. **Repo self-imposed constraint now separable from platform constraint**: the marketplace test forbidding mandatory sibling dependencies is OUR policy; the platform now officially supports plugin-to-plugin dependencies (fog F-3's question). Loosening it is a choice, not a platform fight — but auto-install exceptions and cross-marketplace allowlists apply.

## Killed claims (transparency)

Three ranked claims died in the adversarial pass: a dependencies-example quote fabricated by the extractor ("other-plugin" not on the page — structure fact itself true and re-confirmed via the dedicated page), and two interpretive overreaches ("last-writer-wins" framing; "strict resolution" gloss). None affect the findings above.
