# Changelog

All notable changes to the `think-orbit` plugin are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.4] — 2026-08-19

### Fixed

The skill said reasoning must be written silently, and an agent generalised
that into thinking silently — the reasoning was never articulated at all, so
there was nothing to write into the node bodies either. Measured on a real
project (the real-material checkpoint), nodes protected by an interrupt
narrated their upstream 2/2; nodes written silently did so 0/8. Speech now
splits three ways instead of being banned wholesale: progress narration
stays banned, reasoning aloud becomes required — one or two sentences before
the action, naming what is about to be claimed and what it stands on, never
awaiting a reply — and the three interrupts are unchanged. `thinking-session`
also declares itself a deliberate exception to a host-level "be terse, no
narration" preference, which had stacked with the old silence rule to leave
no reason to speak at all. `using-think-orbit` states the same three-way
contract instead of the opposite one, so the two skills in the family no
longer disagree.

### Added

Node bodies now carry a warrant duty: the first paragraph restates in prose
which upstream the step stands on, what the step adds, and what would
collapse it — written even when the same reasoning was just spoken aloud,
because the two faces are equal and neither substitutes for the other. A
branch opens with one CLAIM per path stating that path's position; an
asymmetric fork — one only becoming visible after a path is already under
way — opens the branch retroactively rather than leaving the earlier path
unbranched. Two new `check` rules enforce the mechanical floor:
`input-narration` (a node with load-bearing inputs must name at least one of
their ids in its body) and `branch-has-node` (a branch carrying only
assumptions and no claim is a violation). The four self-describing worked
examples in `thinking-session` are replaced with real ones.

## [0.1.3] — 2026-08-19

### Fixed

The skill text no longer presumes an Obsidian vault. `<root>` intake
described the project directory as one "typically inside their Obsidian
vault", and `node-schema.md` justified the `paragraph-form` rule as
"matching the vault's own writing convention" — a rationale that has no
referent in a project without a vault. The intake ladder and the rule
itself are unchanged; only the borrowed premise is gone.

## [0.1.2] — 2026-08-18

### Fixed

Behavioral dogfood of 0.1.1 found the plugin unreachable in the two
shapes users actually arrive in. `using-think-orbit` now says in its
description that it **owns intake** — invoke it before inspecting any
folder the user names (FINDING-001) — and carries assumption-broke
(FINDING-002), structured-thinking (FINDING-012) and negative
(FINDING-010) cues. `break-assumption` applies whenever a premise
changed, even mid-conversation, resolving `<root>` by the router's own
ladder (FINDING-002), and `thinking-session` sends a direct entry
through that same ladder (FINDING-011).

An assumption's `branch` is now optional: a premise that governs several
branches is filed project-wide, outside every branch's cap of three, and
`render` draws it at the top level (FINDING-005). `dag.py render` prints
`dag view: <relpath>` instead of succeeding silently (FINDING-007).

The sitting protocol gained the rules the dogfood run showed missing:
one `check` per written or edited file rather than per batch, and an
open-question ending among the render milestones (FINDING-003); a GOAL
already stated in the opening message is confirmed in one line, not
asked again (FINDING-004); a FACT body restates its quote while any
"this means…" inference moves to a CLAIM (FINDING-006); and the `status`
enum plus `load_bearing` are explained where a first-time reader meets
them (FINDING-008). The `break` row of `using-think-orbit`'s verb table
now distinguishes `stale` (down a fully load-bearing chain) from
`weakened` (FINDING-009).

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
