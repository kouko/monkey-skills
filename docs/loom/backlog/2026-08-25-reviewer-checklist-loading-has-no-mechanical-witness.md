---
name: 2026-08-25-reviewer-checklist-loading-has-no-mechanical-witness
description: a reviewer can emit a correct verdict without ever opening the checklist/rubric its contract says it MUST Read — tool-trace inspection caught a spec-reviewer doing exactly that (1 tool call total), and nothing mechanical witnesses the load
status: open
origin: 2026-08-25 live dispatch tests during the reviewer packet fail-closed arc — valid-packet spec-reviewer PASSed with a single git-show call, checklist never Read; compliance across the session's later dispatches was 2/3
start: a second observed instance of a reviewer verdict shipping without its mandated resource load, or the next arc that touches the reviewer resource-loading contract
---

Candidate mechanism sketched at filing time (not decided): embed a
per-file witness token in each checklist/rubric under `resources`, require
the verdict to echo the tokens of every resource its role mandates, and
have `loom_gate_markers.py` compare echoes against the packet's resource
files — an agent that never opened the file cannot know its token. Judgment
-shaped prose ("you MUST load the checklist") has already been shown weak
in this repo; a token echo converts it to a checkable action.
