---
name: a-non-ascii-path-crosses-the-process-boundary-twice
description: A non-ASCII path crosses the process boundary twice, and the two crossings use different encodings from different sources — pipes DECODE with the locale encoding (`locale.getencoding()`), argv ENCODES with the filesystem encoding (`sys.getfilesystemencoding()`, ASCII under an uncoerced C/POSIX locale) — so fixing one says nothing about the other, and only Linux under a C locale exposes the argv half (macOS pins the filesystem encoding to UTF-8), which makes a macOS-green suite no evidence for it; hand argv to git as UTF-8 bytes AND decode its output as UTF-8, and pin the argv half with a platform-independent test
type: gotcha
origin: PR #769 (batch-review-hardening hotfix, 2026-08-31) — #768 merged with `test_packet_seals_non_ascii_path_under_c_locale` failing on the Linux runner (`'ascii' codec can't encode characters in position 45-46`) after the 0.107.0 locale fix had decoded git's output as UTF-8 but left argv on the filesystem encoding; every local run, per-task review and whole-branch review had stayed green
---

`git show <sha>:src/日本.py` raised `UnicodeEncodeError` before git ever
ran. The 0.107.0 fix had made `_run_subprocess` decode stdout with
`encoding="utf-8", errors="surrogateescape"` instead of the
locale-dependent default that `text=True` picks up — and that fix was
correct for the pipe. It did nothing for the argument list: on POSIX,
`subprocess` encodes `str` argv with `os.fsencode` (PEP 383), which is
the filesystem encoding, which is ASCII under an uncoerced C/POSIX
locale. Two crossings, two encoders, two sources of truth.

**Why:** the two halves are invisible to each other. A test that drives
the CLI under `LC_ALL=C` proves the decode side on every platform but the
encode side only where the filesystem encoding actually follows the
locale — Linux. macOS's filesystem encoding is always UTF-8, so the
suite, the per-task triad and the whole-branch review all ran green and
the failure surfaced on the CI runner of the merge commit. "The locale
fix landed" is a statement about one crossing.

**How to apply:** when a path can be non-ASCII and it goes through
`subprocess`, treat output and argv as two separate fixes and ship both:
decode the pipe as UTF-8 (`surrogateescape`), and encode argv to UTF-8
`bytes` yourself (`arg.encode("utf-8", "surrogateescape")`) — git treats
paths as bytes, so UTF-8 bytes match its own model regardless of the
process locale. Pin the argv half with a test that inspects the bytes
handed to `subprocess.run` (the shape of
`test_run_subprocess_hands_git_utf8_bytes_argv` in
`loom-code/scripts/test_batch_review_cli.py`), because a C-locale
end-to-end test can only go red on Linux, and say so in that test's
docstring. When a locale-shaped test is green locally on macOS, the CI
run on the Linux runner is the real GREEN — do not merge ahead of it.
