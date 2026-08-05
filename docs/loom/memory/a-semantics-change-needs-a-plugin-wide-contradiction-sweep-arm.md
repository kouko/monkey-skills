---
name: a-semantics-change-needs-a-plugin-wide-contradiction-sweep-arm
description: When a branch changes the SEMANTICS of a rule (authorization polarity, a gate's direction) rather than just its text, dispatch one extra review arm that sweeps the WHOLE plugin for restatements of the old semantics — the changed-files arm is structurally blind to unchanged files, and the old meaning survives in README mirrors (×N languages), runtime-loaded reference tables, worked examples, and test fixtures; on the 0.58.0 arc this arm found the only 🔴 (a runtime-loaded table re-teaching the deleted re-ask) plus 7 surfaces the plan's own neighbor sweep missed
type: practice
origin: 2026-08-05 request-derived-authorization arc (loom-code 0.58.0), whole-branch round 1 docs arm B
---

The 0.58.0 arc flipped authorization polarity (publish re-asks deleted;
endpoint-naming requests carry the authorization). The plan swept every
neighbor IN the edited files, three plan-review rounds passed it, and
the changed-files docs arm found only in-file issues. A second docs arm
dispatched with a plugin-wide contradiction mission found the branch's
only 🔴 — `push-trigger-rationalizations.md`, a reference table the
changed flow LOADS AT RUNTIME, still instructed the deleted re-ask —
plus the finishing README in three languages, the top-level README flow
diagrams in three languages, a worked example, and a dogfood fixture
all still teaching the old polarity.

**Why:** a semantics change falsifies every restatement of the old
meaning anywhere in the plugin, but review scope defaults to the
branch's changed files. Unchanged files cannot appear in the diff, so
no changed-files arm — however thorough — can see them. Grep-seeded
sweeps are also insufficient alone: the survivals restate the meaning
in paraphrase and in other languages (再認可／再次授權), so the sweep
arm must read hits in context and hunt synonyms.

**How to apply:** when a branch changes what a rule MEANS (not just
its wording), add one review arm whose scope is the whole plugin (all
READMEs and language mirrors, references/ loaded by the changed flows,
docs/examples, test fixtures and pressure indexes), seeded with the
old semantics' vocabulary in every shipped language, judging each hit
as contradicts-vs-still-true. Runtime-loaded references of the changed
flow are the highest-priority targets — a surviving instruction there
re-teaches the deleted behavior inside the new flow itself.
