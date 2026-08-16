Source: `writing-plans/SKILL.md` §"BLOCKED fallback", §"Plan size ceiling", and §"Consuming a loom-design change-folder" — serves `writing-plans`.

# Design evidence — author-facing, do NOT load at runtime

This file is author-facing: it exists for maintainers reviewing or redesigning this skill's decomposition-pattern citation, depth-ceiling heuristic, and change-folder detection-cascade design. Runtime agents executing `writing-plans` do NOT load this file at runtime — the rules these fragments qualify already stay inline in SKILL.md; only the supporting citations and archaeology live here.

## BLOCKED fallback — Beck Child Test citation (originally §BLOCKED fallback)

The 5-step decomposition process and the anti-pattern warning stay inline in SKILL.md — they are load-bearing. This is the citation + verbatim quote the inline text points to: this is **Kent Beck's "Child Test" pattern (*Test-Driven Development: By Example*, 2002, Part III)** verbatim:

> *"When you are working on a test and it gets too big, write a smaller test that represents the broken part of the bigger test. Get the smaller test working. Then go back to the bigger test."*

## Plan size ceiling — why depth 5 is a heuristic (originally §Plan size ceiling)

The core rule ("critical-path depth >5 = brief too big, route back to brainstorming or split into N briefs") stays inline in SKILL.md — it is load-bearing. This is its supporting rationale: errors **compound** across dependent steps — a depth-5 chain at ~95% per-step reliability succeeds only ~77% of the time — and no universal optimal step count exists. Treat **`5` as a deliberate default, not a measured value**; tune it if your steps are more or less reliable.

## Detecting cascade — industry-precedent survey (originally §Consuming a loom-spec change-folder)

The cascade rule itself (layered, evaluated in order, stop at the first layer that resolves) stays inline in SKILL.md — it is load-bearing and test-pinned. This is its supporting citation: industry precedent — spec-kit, OpenSpec, Jira smart commits — every shipped answer shrinks the candidate pool structurally, none guesses from content. Source: `docs/loom/research/2026-07-10-change-binding-and-lifecycle-research.md` §Resolved decisions.

## Detecting cascade — D8 anchor-pattern precedent (originally §Consuming a loom-spec change-folder)

The anchor rule itself (resolve the target repo's root via `git rev-parse --show-toplevel`, evaluate branch name and folder count against that resolved root, never a relative guess from cwd) stays inline in SKILL.md — it is test-pinned (`test_detection_cascade_anchors_at_target_repo_root`). This is its design precedent: this mirrors `code-reviewer.md`'s D8 "Activation is self-derived" anchor pattern, which fixed the identical bug class (a relative check from cwd false-N/A's from a worktree or nested cwd — here it makes a weak operator run detection against the wrong repo entirely).
