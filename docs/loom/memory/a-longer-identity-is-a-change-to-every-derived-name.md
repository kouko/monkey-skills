---
name: a-longer-identity-is-a-change-to-every-derived-name
description: Making a durable identity string LONGER is a change to every name derived downstream from it — filenames, lock paths, temp paths — and filesystem limits are a constraint no unit test models; a 14-byte digest added to a kpi_id took one filer's series filename from 243 to 257 bytes against a 255-byte limit and aborted its entire ingest while 1084 tests stayed green
type: gotcha
origin: PR arc kpi_id injective identity (feat-kpi-id-consolidation-axis, 2.37.0, 2026-07-26)
---

`derive_kpi_id` gained a 12-hex digest suffix (`__` + 12 = 14 bytes) to make the
id injective. The id was reviewed three times as an IDENTITY change and never as
a LENGTH change. `kpi_store` derives the series filename from that id, and
`_atomic_write` layers a further 19 bytes on top (leading `.`, `.json`,
`.<8-random>.tmp`). JNJ reports revenue across four dimensional axes; its
longest signature produced a 243-byte temp filename before the change and 257
after — against the 255-byte per-component limit on APFS/HFS+/ext4. That filer's
entire ingest aborted with `OSError: [Errno 63] File name too long`.

The offline suite was fully green (1084 passed) and a 47-filer probe reported
every filer healthy, because the probe REPLAYED the selector loop in memory and
never wrote a file. Only running the real producer→store path against a real
filesystem surfaced it.

**Why:** a derived identity is an input to every name built from it, and those
names have limits the identity itself does not. Reviewers asked to judge "is
this id correct" do not measure it; tests that never touch a filesystem cannot
observe a filesystem's limits. The failure is also filer-dependent — it appears
only for the widest signature in the corpus, so a small sample misses it.

**How to apply:**
1. When a durable identity's LENGTH changes, enumerate what is derived from it
   (filenames, lock files, temp files, URL paths, index keys) and budget the
   longest derived form, in BYTES, against its real limit — not the identity's
   own length.
2. Cap the DERIVED name, never the identity, when they conflict. A filename can
   carry a truncated readable stem plus a digest of the FULL raw input (that is
   what `kpi_store._series_key` already did); shortening the identity instead is
   a second one-way-door change.
3. Make truncation a strict no-op below the threshold, or every already-stored
   file becomes an unreachable orphan.
4. Derive the affix budget from the real writer (a test that spies on the actual
   temp-file creation), not from a hand-counted constant a future edit can
   silently invalidate.
5. Related: [[a-data-probe-is-not-a-pipeline-dogfood]] — the probe/dogfood
   distinction is exactly what hid this, and
   [[derived-durable-id-slug-is-a-lossy-one-way-door]].
