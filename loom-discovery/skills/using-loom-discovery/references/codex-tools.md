# Codex CLI — host tool reference for loom-discovery

This plugin's skills phrase host interaction in host-neutral prose. This
file is the concrete Codex re-binding for both member skills reached
through this router.

**Verified 2026-07-05, mixed evidence grain** (same grain as the sibling
`using-loom-spec`/`using-loom-interface-design` references files): Codex
`skill` tool and `web_search` tool are doc-confirmed (OpenAI's official
Codex CLI manual) — not exercised in a live Codex session against this
specific plugin's skills.

## Invoking the member skills

Use the `skill` tool (Codex shape), e.g. request `business-value` or
`user-insights` by name. If the user types `/business-value` or
`/user-insights`, that is an explicit invocation — load it directly, no
routing decision needed from this file.

## Research dispatch (user-insights)

- **Heavyweight** (more than 3 research questions, OR external/user
  evidence is needed): delegate via the `skill` tool to
  `research-toolkit:deep-deep-research` — pass paths + a structured seed
  context, never inline the analysis.
- **Light inline scope** (≤3 questions, no external evidence needed): use
  Codex's `web_search` tool, one call per research question, and write
  findings straight into
  `docs/loom/discovery/<date>-<slug>/research/<question-slug>.md`.

**Codex caveat**: unlike Claude Code's `WebSearch` tool, Codex's
`web_search` availability depends on the current sandbox/network policy
(`~/.codex/config.toml` `[features] web_search`). If disabled, fall back
to the heavyweight delegation path even for small scopes — do not guess
at findings without a live search.

## Business-value delegation

`business-value` never analyzes market sizing, go-to-market, or revenue
inline — that delegates to `domain-teams:planning-team` via the `skill`
tool, paths passed rather than file content.

## Reading prior evidence

Before starting a new discovery pass on an existing slug, read
`docs/loom/discovery/<date>-<slug>/evidence.md` if it already exists (via
Codex's file-read primitive) — the atomic-research model means evidence
outlives any single report; don't re-research a claim already logged
there.
