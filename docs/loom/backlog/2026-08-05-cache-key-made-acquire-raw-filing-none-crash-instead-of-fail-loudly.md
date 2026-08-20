---
name: 2026-08-05-cache-key-made-acquire-raw-filing-none-crash-instead-of-fail-loudly
description: Task B's cache key made _acquire_raw_filing(None) crash where it used to fail loudly — the root cause is fixed; four call sites remain untraced
status: open
origin: found by Task J's implementer while fixing the same root cause in its own loop; independently reproduced by both of Task J's reviewers (branch `feat-us-quarterly-statement-series`, 2026-08-05).
start: the ROOT CAUSE is fixed; what remains is auditing four call sites nobody has traced — do that before trusting any of them with a producer that can yield None
---

> **ROOT CAUSE FIXED 2026-08-07, on the same branch, before it merged.** A
> whole-branch reviewer objected to the deferral rather than the disclosure: this
> entry's own trigger was "before any live multi-filing run reaches a filer with a
> missing form (Task H's one-off live run is the first that would)" — and that run
> happened on 2026-08-06. The trigger had fired. The fix was moving the cache-key
> computation back INSIDE the existing `try`, which is shorter than this entry.
> Pinned by `test_an_accession_of_none_comes_back_as_a_loud_slot_not_a_traceback`,
> which also asserts the network was never reached — a fix that merely deferred
> the failure into `get_by_accession_number(None)` would satisfy the error-slot
> assertion while spending an SEC round-trip.
>
> **This entry stays OPEN for what the fix did NOT do**: the four untraced call
> sites below. `pack_us._fetch_xval_source_a`'s docstring premise is true again,
> so the confirmed live site is closed — but "no longer crashes" is not "audited".



- Start: the ROOT CAUSE is fixed; what remains is auditing four call sites nobody
  has traced — do that before trusting any of them with a producer that can yield
  None

- ~~Superseded start condition~~ (deliberately NOT written as a struck-through
  `- Start:` bullet: the store's validator matches `^-\s*\**Start\**…:` and
  tolerates `**` but not `~~`, so striking the LABEL makes the field-agreement
  check silently skip rather than pass — this entry did exactly that for one
  round, and reported the resulting green as agreement): ~~before any live
  multi-filing run reaches a filer with a missing form (Task H's one-off live run
  is the first that would), or on the next touch of
  `pack_us._fetch_xval_source_a`. It is a live regression in shipped behaviour,
  not a latent risk.~~ **Superseded 2026-08-07** — that trigger fired (the live
  run happened 2026-08-06) and the root cause was fixed on the same branch.
- Origin: found by Task J's implementer while fixing the same root cause in its
  own loop; independently reproduced by both of Task J's reviewers
  (branch `feat-us-quarterly-statement-series`, 2026-08-05).
- **The root cause**: `_acquire_raw_filing` used to go straight from its identity
  guard into `try: edgar.get_by_accession_number(accession)`, so a `None`
  accession raised INSIDE the try and came back as a loud `{"error": ...}` slot.
  Task B inserted the cache-key computation AHEAD of that `try`, and
  `_accession_nodash` is not defensive:
  `AttributeError: 'NoneType' object has no attribute 'replace'`.
  **Verified 2026-08-05 by executing it** (faked `edgar`, temp cache dir); the
  identity guard does not intercept, because `USER_AGENT` is a compliant constant.
- **The confirmed live site**: `pack_us._fetch_xval_source_a` takes
  `accession = _latest_10k_accession(filings_rows)`, whose signature is
  `str | None` and which returns `None` when no 10-K row exists, then hands it
  straight to `_acquire_raw_filing`. **So a filer with no 10-K in the window now
  aborts memo-fetch with a traceback instead of reporting a wholesale failure.**
  ~~Its own docstring still asserts the expired premise — "which already returns a
  loud resolution error slot ... no separate guard is needed here to avoid a
  crash".~~ **Superseded 2026-08-07**: with the root cause fixed, that docstring's
  premise is TRUE again, so this site is closed. Verified 2026-08-05 by opening both.
  Its test cannot see it: the test mocks the boundary, so nothing exercises the
  real `None` path.
- **What is NOT known**: `_acquire_raw_filing` has six call sites (three in
  `sec_edgar_client.py`, three in `pack_us.py`). Only two have been traced —
  Task J's loop (fixed in that task) and `_fetch_xval_source_a` (this entry).
  **The other four have not been checked for whether their accession can be
  `None`**, and a grep does not answer that; each needs its producer traced.
  Do not treat this entry as a complete inventory.
- ~~Fix shape: make `_acquire_raw_filing` `None`-safe at its own head~~ **DONE
  2026-08-07, by a different means than proposed**: rather than a head guard, the
  cache-key computation moved back INSIDE the existing `try` it had been lifted
  out of — so a `None` accession raises there and returns the loud slot it always
  used to, with no new guard at all. The reasoning below still holds and is why
  the fix went at the shared seam rather than at each call site: one place against
  six unaudited callers. Neither docstring needed correcting; both became true
  again.
- A pre-existing test also asserts the expired premise in prose and cites a line
  range Task B invalidated (`test_data_markets_us.py`, the no-10-K wholesale
  failure test). Task J's round 2 corrected that prose; the underlying test still
  mocks the boundary and so still does not exercise the real path.
