---
title: "wiki-ingest language-policy v3.11.0 — Dogfood Audit"
date: 2026-05-18
branch: wiki-ingest-language-policy
version: v3.11.0
status: dogfood-pass
---

# wiki-ingest language-policy v3.11.0 — Dogfood Audit

**Date**: 2026-05-18
**Branch**: `wiki-ingest-language-policy`
**Version**: v3.11.0 (language-policy SSOT + functional-copy distribution)
**Status**: dogfood-pass

## Scope

MVP verification covers three pillars:

1. Python-layer correctness: `verify-drift.py` + `distribute.py` scripts
2. Test suite green: all test files pass
3. Functional-copy presence: 4 sibling skills carry identical `language-policy.md`

LLM-behavior verification (CC-LL-01..05) is deferred — rationale in §4.

---

## §1 verify-drift.py output capture

Command run:

```
python3 obsidian/scripts/verify-drift.py
```

Literal output:

```
OK: all 4 functional copies match canonical + SSOT header.
Exit: 0
```

All 4 functional copies are byte-for-byte identical to canonical
`obsidian/skills/wiki-ingest/references/language-policy.md` and carry
the required SSOT header block.

---

## §2 pytest output capture

Command run:

```
cd obsidian && PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -v
```

Literal output:

```
============================= test session starts ==============================
platform darwin -- Python 3.12.11, pytest-8.3.4, pluggy-1.6.0 -- /Users/kouko/.conda/envs/dbt-redshift/bin/python3
cachedir: .pytest_cache
rootdir: /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-language-policy/obsidian
configfile: pyproject.toml
testpaths: tests, scripts
plugins: anyio-4.10.0
collecting ... collected 24 items

tests/wiki_ingest/test_select_batch.py::test_select_batch[cc01] PASSED   [  4%]
tests/wiki_ingest/test_select_batch.py::test_select_batch[cc02] PASSED   [  8%]
tests/wiki_ingest/test_select_batch.py::test_select_batch[cc03] PASSED   [ 12%]
tests/wiki_ingest/test_select_batch.py::test_select_batch[cc04] PASSED   [ 16%]
tests/wiki_ingest/test_select_batch.py::test_select_batch[cc05] PASSED   [ 20%]
tests/wiki_ingest/test_select_batch.py::test_select_batch[cc06] PASSED   [ 25%]
tests/wiki_ingest/test_select_batch.py::test_select_batch[cc08] PASSED   [ 29%]
tests/wiki_ingest/test_select_batch.py::test_select_batch[cc09] PASSED   [ 33%]
tests/wiki_ingest/test_select_batch.py::test_select_batch[cc10] PASSED   [ 37%]
tests/wiki_ingest/test_select_batch.py::test_select_batch[cc11] PASSED   [ 41%]
tests/wiki_ingest/test_select_batch.py::test_select_batch[cc12] PASSED   [ 45%]
tests/wiki_ingest/test_select_batch.py::test_select_batch[cc13] PASSED   [ 50%]
tests/wiki_ingest/test_select_batch.py::test_select_batch[cc15] PASSED   [ 54%]
tests/wiki_ingest/test_select_batch.py::test_select_batch_cc07 PASSED    [ 58%]
tests/wiki_ingest/test_select_batch.py::test_select_batch_cc14 PASSED    [ 62%]
tests/wiki_ingest/test_select_batch_smoke.py::test_empty_stdin_returns_valid_json_shape PASSED [ 66%]
tests/wiki_ingest/test_select_batch_smoke.py::test_missing_env_returns_exit_2 PASSED [ 70%]
tests/wiki_ingest/test_select_batch_smoke.py::test_topic_filter_basename_match PASSED [ 75%]
scripts/test_distribute.py::test_distribute_idempotent PASSED            [ 79%]
scripts/test_distribute.py::test_ssot_header_present PASSED              [ 83%]
scripts/test_verify_drift.py::test_help_exits_zero PASSED                [ 87%]
scripts/test_verify_drift.py::test_all_in_sync_exits_zero PASSED         [ 91%]
scripts/test_verify_drift.py::test_drift_exits_nonzero PASSED            [ 95%]
scripts/test_verify_drift.py::test_drift_output_names_path PASSED        [100%]

============================== 24 passed in 0.37s ==============================
Exit: 0
```

24 passed, 0 failed. testpaths now covers both `tests/` and `scripts/`
(pyproject.toml updated in T1), picking up distribute + verify-drift
script tests alongside the core `select_batch` suite.

---

## §3 Sibling-skill functional-copy sanity check

Four sibling skills each carry a `references/language-policy.md`
functional copy. `ls -la` proof:

```
-rw-r--r--@ 1 kouko  wheel  10915 May 18 07:06 obsidian/skills/wiki-auto-research/references/language-policy.md
-rw-r--r--@ 1 kouko  wheel  10915 May 18 07:23 obsidian/skills/wiki-cross-linker/references/language-policy.md
-rw-r--r--@ 1 kouko  wheel  10915 May 18 07:06 obsidian/skills/wiki-lint/references/language-policy.md
-rw-r--r--@ 1 kouko  wheel  10915 May 18 07:06 obsidian/skills/wiki-query/references/language-policy.md
```

SSOT header (`head -3`) for each copy:

```
=== obsidian/skills/wiki-cross-linker/references/language-policy.md ===
<!-- BEGIN language-policy-v1 — managed by obsidian/scripts/distribute.py from obsidian/skills/wiki-ingest/references/language-policy.md — do not edit in place -->
<!-- This is a functional copy. Edit the canonical source above and re-run distribute.py. -->

=== obsidian/skills/wiki-query/references/language-policy.md ===
<!-- BEGIN language-policy-v1 — managed by obsidian/scripts/distribute.py from obsidian/skills/wiki-ingest/references/language-policy.md — do not edit in place -->
<!-- This is a functional copy. Edit the canonical source above and re-run distribute.py. -->

=== obsidian/skills/wiki-lint/references/language-policy.md ===
<!-- BEGIN language-policy-v1 — managed by obsidian/scripts/distribute.py from obsidian/skills/wiki-ingest/references/language-policy.md — do not edit in place -->
<!-- This is a functional copy. Edit the canonical source above and re-run distribute.py. -->

=== obsidian/skills/wiki-auto-research/references/language-policy.md ===
<!-- BEGIN language-policy-v1 — managed by obsidian/scripts/distribute.py from obsidian/skills/wiki-ingest/references/language-policy.md — do not edit in place -->
<!-- This is a functional copy. Edit the canonical source above and re-run distribute.py. -->
```

All 4 paths confirmed present. All 4 carry identical SSOT headers
pointing to the canonical source in `wiki-ingest/references/`.

---

## §4 LLM-behavior dogfood deferral rationale

CC-LL-01 through CC-LL-05 define the behavioral checks for language
selection correctness: does a real `/wiki-ingest` run on kouko's
Obsidian vault produce Japanese-primary output when
`LANGUAGE_POLICY=enabled` and the input source is Japanese? These
checks are intentionally deferred to post-merge work, not MVP.

The language policy is Claude-prose-enforced: the decision tree in
`language-policy.md` is read by Claude at runtime as part of SKILL.md
context loading. There is no Python resolver that can be unit-tested
against the policy's conditional branches — the enforcement logic lives
inside the LLM's natural language comprehension. A unit test asserting
"given Japanese input, output is Japanese" would require either (a) a
real Claude API call with token cost and non-determinism, or (b) a
Python re-implementation of the decision tree that would immediately
drift from the authoritative prose.

Real-world dogfood requires plugin reload in the user's Claude Code
session, which happens post-merge when the branch lands on `main` and
the plugin is refreshed. Running it against a worktree-local skill
checkout would not exercise the same code path the user's production
session uses.

Phase 2 candidate work: a lightweight LLM-loop test harness (a la
`run_loop.py` in dev-workflow) that sends a fixed Japanese-source
ingest prompt to Claude and asserts the response language via heuristic
classifier, OR a Python policy resolver that mirrors the decision tree
and can be tested deterministically. Either approach is a non-trivial
standalone deliverable and is out of scope for the MVP PR.

---

## §5 Migration strategy proof

80+ existing wiki pages generated before v3.11.0 remain in legacy
format (English-primary with CJK loanwords). No bulk migration is
planned or needed. The policy applies forward-only: when a page's
source document is modified and re-ingested via `/wiki-ingest`, the new
`language-policy.md` decision tree governs the output language for that
re-ingest run. Pages that are not re-ingested are untouched.

This is intentional natural drift — content updates carry the cost of
re-normalization organically. The alternative (`/wiki-relang` bulk
re-processing) is a Phase 2 item and requires an explicit user decision
to accept the vault-wide rewrite surface area. Deferred pending user
confirmation of Phase 2 scope.
