# Host-aware cross-model review language — spec
intent: 2026-09-12-host-aware-cross-model-review-language@f080b1a90d8521db4f54c40048a85bcd86e4d916
confirmed-behavior: 2026-09-12 @acef02e
pre-build-review: required — changes a shared user-facing contract across Codex and Claude Code and corrects cross-provider selection behavior

## Requirements
REQ-1 — Codex excludes its own model family
  WHEN Loom presents a cross-model review option while Codex is the current host, the system shall name an observed runnable CLI from a non-Codex model family and shall not name Codex as the independent reviewer → Acceptance #1

REQ-2 — Claude Code excludes its own model family
  WHEN Loom presents a cross-model review option while Claude Code is the current host, the system shall name an observed runnable CLI from a non-Claude model family and shall not name Claude Code as the independent reviewer → Acceptance #2

REQ-3 — Direct cross-model language
  WHERE Loom describes optional review diversity, the system shall call it an independent review from another model family and shall not call it a second reader → Acceptance #3

REQ-4 — Existing mode behavior remains intact
  WHERE cross-model review behavior is tested, the automated regression suite shall cover Codex-host and Claude-Code-host exclusion across ask, suggest, and fixed modes, including their waiting or opt-in behavior and the no-silent-substitution failure boundaries → Acceptance #4

REQ-5 — Minimal one-column notice
  WHEN Loom presents a non-blocking cross-model review suggestion, the system shall emit two blank lines, one Markdown table with exactly one heading and one descriptive cell, and two trailing blank lines, with raw Markdown that remains understandable without table rendering → Acceptance #5

REQ-6 — Native ask with conservative recommendation
  WHEN ask mode is evaluated, the system shall use the current host's native question interface for a runnable different-model-family tool when available, recommend not using an external reviewer if that interface requires a default, use a blocking plain-language Markdown fallback only when the native interface is unavailable, and otherwise report that no different-model-family review tool is available and continue without asking → Acceptance #6

## Design decision
- user-decided — Present each notice as one one-column Markdown table with a single heading and descriptive cell, surrounded by two blank lines, because stronger multi-column structure and ASCII decoration add content or noise the user did not ask for.
- agent-decided — Resolve the displayed provider from explicit host identity plus the existing runnable-CLI probe, because prose examples must not choose a provider independently of the selection rule.
- agent-decided — Define cross-model independence at the model-family/vendor boundary, not as a second invocation, because another instance of the host family does not provide the requested diversity.
- agent-decided — Keep raw Markdown as the fallback contract, because neither product's documentation guarantees visual table rendering in every Desktop and CLI client.
- user-decided — Use each host's native question interface for ask mode and choose `do not use for this change` whenever the interface requires a recommendation, because the default must not authorize quota use or repository-data egress.
- agent-decided — Fall back to one blocking plain-language Markdown question when a native question tool is unavailable, because Codex exposes its structured input tool only in some modes and Claude Code does not expose AskUserQuestion to subagents.
- agent-decided — When ask mode has no runnable different-model-family candidate, report unavailability and continue without asking, because there is no valid choice to block on and silently substituting the host would defeat the feature.

## Alternatives considered
- Keep the hard-coded Codex question and clarify only the surrounding prose — rejected because Codex would still recommend its own model family.
- Use ASCII separator banners — rejected because the user chose the smaller one-column Markdown table and table markup degrades to readable text.
- Use a two-column status table — rejected because a single notice does not need comparison fields and the user explicitly wants one descriptive cell.
- Detect the host from prose or executable availability — rejected because both tools can be installed at once and availability does not identify the active model family.
- Mark the external reviewer as recommended whenever ask mode appears — rejected because availability alone is not evidence that extra quota use and data egress are warranted.

## Current state evidence
- Forward: `loom-design/skills/capture-intent/references/second-vendor.md` :: `ask one plain sentence` hard-codes Codex at the intent decision point.
- Reverse: `loom-design/skills/capture-intent/SKILL.md` :: `The second-reviewer question` directs the station to repeat the same hard-coded Codex prompt.
- Error: `loom-code/skills/write-plan/references/second-vendor-ask-and-docs-lint.md` :: `Do you want to use Codex as the second reader this time?` is emitted without considering the current host.
- Data: `loom-code/scripts/second_vendor_policy.py` :: `host_vendor` and `usable_vendors` already model host exclusion for suggest mode, while ask mode returns before using that result.
- Boundary: `loom-code/skills/review/SKILL.md` :: `A selected second vendor remains required` consumes the selected CLI; verdict, attestation, and publication behavior stay unchanged.

## UI flows
- Codex host, Claude Code is runnable, ask mode, native input is available → the native question asks whether to use Claude Code for independent review; `這次不使用` is the recommended option and `使用 Claude Code` is the other option; Loom waits for the answer.
- Claude Code host, Codex is runnable, ask mode, AskUserQuestion is available → the native question asks whether to use Codex for independent review with the same two choices and waits for the answer.
- Ask mode without a native question interface → one blocking plain-language Markdown question names the runnable different-model-family tool and offers use or decline without a fabricated recommendation.
- Full-lane suggest mode with an available different model family and no grounded high risk → the table's only cell names the available tool, explains how to opt in before Closing Review, and says work continues without waiting.
- Full-lane suggest mode with grounded high risk → the table heading says the independent cross-model review is recommended, and its only cell names the available tool, gives the grounded reason, explains the opt-in cutoff, and says work continues without waiting.
- Small-lane suggest mode → the table's only cell is informational and says the available different model family can be selected for a future change; the active change gains no reviewer.
- Suggest mode with no runnable different-model-family CLI → no table is shown and Loom continues with the configured lane's normal review behavior.
- Ask mode with no runnable different-model-family CLI → Loom states that no different-model-family review tool is currently available and continues without presenting a choice or waiting.
- A client shows raw Markdown instead of a preview table → the heading, separator row, and one descriptive cell remain understandable in source form with two blank lines separating them from surrounding text.
- A fixed reviewer CLI matches the current host model family or cannot run → Loom reports the existing concrete configuration or availability failure and does not silently select another tool.
