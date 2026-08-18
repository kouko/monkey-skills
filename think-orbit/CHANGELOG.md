# Changelog

All notable changes to the `think-orbit` plugin are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] — 2026-08-18

### Changed

The plugin's purpose is **thinking and planning**, not only deciding
(user ruling, 2026-08-18). `skills/decision-session/` is renamed to
`skills/thinking-session/`, and the entry vocabulary of
`using-think-orbit` and `thinking-session` widens to 幫我想 / 想一下 X /
想清楚 / 整理思路 / 規劃 X / 思考 / "think through X" / "plan X" /
"figure out" / "help me think", keeping 我要決定 / 決策推演 /
"help me decide".

A sitting no longer has to end in a `DECISION`: a chain ending in an
open question or a plan outline is a complete record, and a `DECISION`
node is written only when the user actually rules.

## [0.1.0] — 2026-08-18

renamed from working name strategy-dag

### Added

Initial plugin skeleton: `.claude-plugin/plugin.json`, Codex manifest
mirror (`.codex-plugin/plugin.json`), tri-language READMEs, and a stub
`skills/think-orbit/SKILL.md`. The core conversation protocol is not
yet implemented — Part 1, pre-release.

layout: using-think-orbit router + decision-session (renamed to
thinking-session in 0.1.1) + break-assumption;
scripts at plugin level
