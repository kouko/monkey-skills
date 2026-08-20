---
name: a-plan-can-cite-a-path-that-does-not-exist-and-pass-review
description: A plan's Acceptance can name a test file that does not exist in the repo and still pass plan-document review, because the reviewer checks that the required field is present and plausible rather than that the path resolves; the guard costs one `ls` per cited path before dispatch
type: process
origin: branch direction-queue-gate (2026-08-20) — Task 8's Acceptance named a shipping-version pin that does not exist in this plugin; found by the implementer, after two rounds of plan review had passed it
---

Task 8's `Acceptance.RED` named `loom-code/scripts/test_plugin_manifest.py` as
the shipping-version pin the bump would redden. No such file exists in that
plugin — the name was carried from memory of a sibling plugin that does have
one. The plan passed two full rounds of plan-document-review with the citation
intact.

The implementer found the real pins only because the bump turned the suite red
and it went looking. Both real pins live in files the plan never named.

**Why:** plan review grades the schema and the reasoning. Check 3 asks whether
`Brief item covered` is filled; the RED/GREEN checks ask whether an acceptance
criterion is specific and falsifiable. A path that is well-formed, plausibly
named, and in the right directory satisfies every one of those without ever
being resolved. The reviewer has no reason to stat the file, and the author has
no signal that they wrote fiction — the sentence reads exactly like a correct
one.

**How to apply:** before dispatching a plan, run `ls` (or a single `for`-loop
over the set) on every filesystem path its Acceptance criteria name. This is
seconds of work and it is mechanical, which is the point: the defect is invisible
to reading and obvious to the shell. When a cited path does not resolve, the
plan is wrong even if the intent is right — fix the citation rather than letting
the implementer rediscover it under a red suite. Related:
[[a-line-cite-fixed-before-its-file-is-edited-goes-stale-again]] (the same
citation class rotting later, rather than being wrong at birth).
