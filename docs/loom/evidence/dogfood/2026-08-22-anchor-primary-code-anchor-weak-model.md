# Dogfood record — weak-model code-anchor cold read

Date: 2026-08-22
Model: gpt-5.6-luna (low reasoning)
Scope: anchor-primary author guidance after the code/config clarification

## Prompt boundary

The actor read only `handoff-brief-format.md`'s Current State Evidence
guidance before inspecting one prose, one code, and one configuration target.
The prompt required a repo-relative path plus quoted anchor for each target;
it did not prescribe which code or configuration anchor to choose.

## Response

| Target kind | Citation produced | Result |
| --- | --- | --- |
| Prose | `loom-code/skills/brainstorming/references/handoff-brief-format.md` — `"## Current State Evidence"` | PASS — stable heading exists. |
| Code | `loom-code/scripts/check_doc_citations.py` — `"def resolve_cited_path("` | PASS — distinctive function signature exists. |
| Config | `loom-code/.claude-plugin/plugin.json` — `"description": "Canon-grounded coding-discipline workflow` | PASS — key plus distinctive value fragment exists. |

## Verdict

PASS. The weak model selected an artifact-appropriate anchor for all three
targets without line-only citations or additional coaching. This is a narrow
cold-read probe: it validates selection of prose, code, and config anchors;
it does not claim broad adherence across every citation workflow.
