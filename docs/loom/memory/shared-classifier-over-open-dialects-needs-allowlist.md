---
name: shared-classifier-over-open-dialects-needs-allowlist
description: A predicate shared across N producers that each emit their own error/metadata dialect must decide by a POSITIVE allowlist of what counts as real data, never a denylist of known error keys — a denylist silently fails toward the dangerous direction the moment an unsampled producer adds a key you did not list
type: gotcha
origin: branch feat-us-sec-narrative-memo-wiring (US SEC narrative→memo wiring, 2026-07-13) — pack_inventory false-presence across 5 markets
---

`pack_inventory._is_failed_section` is ONE predicate consumed by all five
market packs (us/jp/tw/kr/cn) to tell the memo which data is present. A
fix tightened it to "not present if the section carries an error marker",
implemented as a **denylist**: present ⟺ the section has a key OUTSIDE a
`_ERROR_ENVELOPE_KEYS` set. That set was derived from only two of the five
markets (US `run_client` + TW `mops`). The whole-branch reviewer proved by
running the real code that jp/cn emit `_stdout_head` and kr emits
`_partial` on failure — keys absent from the set — so a genuinely
all-failed jp/kr/cn section had a key "outside the denylist" and read
**present: True**. That is FALSE PRESENCE: the inventory then licenses the
memo to cite fundamentals that were never fetched — the exact fabrication
class the inventory exists to prevent, reintroduced for 3 of 5 markets by
a fix that passed its own per-market tests.

The correct shape is a **positive allowlist of DATA**, not a denylist of
errors: present ⟺ the section carries at least one data-bearing value — a
non-empty dict, or a list containing ≥1 dict — with scalars counting only
when their key is not a known diagnostic/skip marker. A merged section
(error marker + a populated `concepts` dict) is present because the data
container is real; a bare error/skip section (only scalar diagnostics like
`error`/`_stdout_head`/`_partial`/`_skipped`) is absent because it has no
data container. This generalizes across every market without enumerating
each one's error vocabulary.

**Why:** the set of error/metadata dialects across N producers is OPEN —
the next producer, or the next error branch, adds a key nobody sampled. A
denylist over an open set fails toward whatever the "unknown key" default
is; here that default was "present" (the dangerous direction for an
anti-fabrication check). An allowlist of what real DATA looks like is a
closed, shape-based question (is there a populated data container?) that
does not grow with the producer count, so an unsampled producer cannot
silently flip a section to the wrong verdict.

**How to apply:** when a single classifier/predicate is shared across
multiple producers that each carry their own error/metadata dialect,
decide by matching the POSITIVE thing you want (real data, by shape:
populated dict / list-of-dict) and treat everything else as its absence —
never by enumerating the negative (known error keys). If you must keep a
scalar-marker set, prove it against ALL N producers' real emissions (read
each one's failure branch), not a sample, and add a per-producer
false-presence regression test so an unsampled dialect cannot silently
reopen the hole. Fail-safe direction for an anti-fabrication check is
"absent unless data is provably present." See also
[[per-task-review-misses-duplicated-fallback-fix]] (a shared shape read at
many sites is exactly what per-task review cannot see) and
[[fixtures-mirror-producer-shape]] (derive shapes from real producers, not
a sample or an assumption).
