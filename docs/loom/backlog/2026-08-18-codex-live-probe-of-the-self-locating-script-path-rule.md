---
name: 2026-08-18-codex-live-probe-of-the-self-locating-script-path-rule
description: the adjudication-view invocation contract's self-locating script path rule is argued portable to Codex by structure, but no loom render has ever been executed under Codex to confirm it actually resolves and runs the right script copy
status: open
origin: 2026-08-18 adjudication-render-staleness-visible arc, brief Open Question 0 — recorded rather than made a blocking task because "portable by construction" is an argument, not a measurement
start: the next Codex session that renders an adjudication view, or an explicitly scheduled probe of it
---

- Origin: 2026-08-18 adjudication-render-staleness-visible arc, brief
  Open Question 0 — recorded rather than made a blocking task because
  "portable by construction" is an argument, not a measurement

- Start: the next Codex session that renders an adjudication view,
  or an explicitly scheduled probe of it

- What this is: commit `4754e06b` shipped an invocation contract in the
  adjudication-view protocol that pins which copy of the adjudication
  scripts runs, as a self-locating rule — "the scripts shipped beside
  this protocol file, resolved from its own absolute path as
  `../../../scripts/<script>.py`". The rule's portability to Codex has
  never been live-probed; it has only been argued structurally.

- Why the structural argument looks sound, and why that is still not a
  measurement:
  - The rule names no harness-specific primitive. It deliberately
    avoids `${CLAUDE_PLUGIN_ROOT}`, which Anthropic's docs say is
    substituted only in a SKILL.md body and in `allowed-tools`
    frontmatter — a protocol file opened with the Read tool keeps the
    literal token, which expands to empty in a shell.
  - Codex has BOTH install shapes, per this repo's own onboarding docs
    (`.codex/INSTALL.md`, `docs/loom/codex-verification.md`): a
    marketplace install (`codex plugin add <plugin>@monkey-skills`)
    that lands in a per-version cache tree,
    `~/.codex/plugins/cache/<marketplace>/<plugin>/<version>/` —
    structurally the same shape as the Claude Code per-version-cache
    staleness source this arc's brief describes — and a separate,
    manual git-clone install (`.codex/INSTALL.md` Option B) updated
    with `git pull`. So at least TWO of this arc's three staleness
    classes plausibly exist under Codex, not one: the per-version
    cache tier and the stale clone. The probe must check both.
  - Live datapoint (2026-08-18, this machine): `codex plugin list`'s
    cache holds `~/.codex/plugins/cache/monkey-skills/loom-code/0.83.0/`
    — a per-version directory predating the markdown-it conversion.
    A Codex-rendered adjudication view today would reproduce the
    original bug this arc fixes, confirming the cache tier is not
    just structurally possible but presently stale on a real machine.
  - What remains unverified is narrower than "can Codex go stale" —
    the cache tier and the live datapoint above already answer that.
    What is unverified is whether an executor under Codex resolves
    the self-locating rule correctly and runs the scripts shipped
    beside whichever protocol-file copy it is actually executing —
    marketplace-cached or git-cloned.
  - Nobody has run a loom render under Codex to confirm that.

- Why it matters: this repo has precedent for exactly why a structural
  argument is not enough — a live probe once refuted a documented
  claim about Codex's subagent behaviour (standing-instructions
  auto-spawn) that had been believed on the strength of documentation
  alone (`feedback_codex_multi_agent_spawns_from_standing_instructions`
  in the Claude auto-memory index). "No harness-specific primitive" is
  the same shape of claim, unverified the same way.

- Next step when this fires: drive one real adjudication-render
  invocation from a Codex session against a repo carrying this
  protocol file, and confirm the resolved script path points at the
  scripts shipped beside the protocol file being executed (not a
  stale or wrong copy). Record the result — pass or fail — back into
  this entry or its successor; a failure here would mean the
  invocation contract needs an explicit Codex-side fallback, not just
  the self-locating rule.
